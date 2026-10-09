"""Independent per-leaf FX10/FX17 overlap-band fits; no spectra or 3D edits."""
from pathlib import Path
import json,hashlib
import cv2,numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];PREV=ROOT/'generated/research_spectral_extension_20261007/fx17_probe'
A=np.rot90(np.uint8(np.clip(np.load(PREV/'fx10_overlap_display.npy')*255,0,255)));B=np.rot90(np.uint8(np.clip(np.load(PREV/'fx17_overlap_display.npy')*255,0,255)));A=cv2.resize(A,(A.shape[1],640),interpolation=cv2.INTER_LINEAR)
prior=json.loads((PREV/'exact_feature_tracking.json').read_text());known=[x for x in prior['candidates']if x['prior_fx10_id'] in ['red_upper_2','red_upper_6']]
clahe=cv2.createCLAHE(2.5,(4,4));sift=cv2.SIFT_create(nfeatures=2500,contrastThreshold=.004,edgeThreshold=16);bf=cv2.BFMatcher()
def native_a(p):return np.c_[1023-((p[:,1]+.5)/.625-.5),p[:,0]+1450]
def native_b(p):return np.c_[639-p[:,1],p[:,0]+1350]
def stats(a):return {'n':len(a),'rms_px':float(np.sqrt(np.mean(a*a))),'median_px':float(np.median(a)),'max_px':float(np.max(a)),'errors_px':a.tolist()}
def fit(src,dst,kind):
 cv2.setRNGSeed(10517)
 if kind=='affine':
  M,ii=cv2.estimateAffine2D(src,dst,method=cv2.RANSAC,ransacReprojThreshold=2.,maxIters=30000,confidence=.999,refineIters=20);H=np.vstack([M,[0,0,1]])if M is not None else None
 else:H,ii=cv2.findHomography(src,dst,cv2.RANSAC,2.,maxIters=30000,confidence=.999)
 return H,ii.ravel().astype(bool) if ii is not None else None
def predict(H,p):return cv2.perspectiveTransform(p.reshape(-1,1,2).astype(float),H).reshape(-1,2)
for region,aroi,broi in [('upper_red',[105,0,305,129],[90,0,300,175]),('upper_green',[285,0,430,150],[260,0,445,190])]:
 raw=[];ax0,ay0,ax1,ay1=aroi;bx0,by0,bx1,by1=broi
 for band in range(4):
  a=clahe.apply(A[ay0:ay1,ax0:ax1,band]);b=clahe.apply(B[by0:by1,bx0:bx1,band]);kt,dt=sift.detectAndCompute(b,None)
  for sx in [.9,1.,1.1]:
   for sy in [.9,1.,1.1]:
    aa=cv2.resize(a,None,fx=sx,fy=sy);ks,ds=sift.detectAndCompute(aa,None)
    if ds is None or dt is None or min(len(ds),len(dt))<2:continue
    fm=bf.knnMatch(ds,dt,k=2);bm=bf.knnMatch(dt,ds,k=2);rev={(m.trainIdx,m.queryIdx)for m,n in bm if m.distance<.76*n.distance}
    for m,n in fm:
     if m.distance>=.76*n.distance or (m.queryIdx,m.trainIdx)not in rev:continue
     p=(np.array(ks[m.queryIdx].pt)+.5)/[sx,sy]-.5+[ax0,ay0];q=np.array(kt[m.trainIdx].pt)+[bx0,by0];raw.append({'p':p,'q':q,'ratio':m.distance/n.distance,'config':(band,sx,sy)})
 clusters=[]
 for r in sorted(raw,key=lambda x:x['ratio']):
  c=next((c for c in clusters if np.linalg.norm(c[0]['p']-r['p'])<2.5 and np.linalg.norm(c[0]['q']-r['q'])<2.5),None)
  if c is None:clusters.append([r])
  else:c.append(r)
 records=[]
 for i,c in enumerate(clusters):
  p=np.median([r['p']for r in c],axis=0);q=np.median([r['q']for r in c],axis=0);cfg=len(set(r['config']for r in c));bands=sorted(set(r['config'][0]for r in c));na=native_a(p[None])[0];nb=native_b(q[None])[0]
  if cfg<4 or len(bands)<2:continue
  excluded=region=='upper_red' and any(np.linalg.norm((na-np.array(k['native_fx10_anchor_column_line']))*[.625,1])<10 or np.linalg.norm(nb-np.array(k['native_fx17_subpixel_column_line']))<10 for k in known)
  records.append({'id':i,'fx10_column_line':na.tolist(),'fx17_column_line':nb.tolist(),'repeat_configs':cfg,'bands':bands,'excluded_old_anchor_neighbourhood':bool(excluded)})
 train=[r for r in records if not r['excluded_old_anchor_neighbourhood']];src=np.array([r['fx10_column_line']for r in train]);dst=np.array([r['fx17_column_line']for r in train]);models=[]
 if len(train)>=8:
  for kind in ['affine','homography']:
   H,ii=fit(src,dst,kind)
   if H is None:continue
   e=np.linalg.norm(predict(H,src)-dst,axis=1);folds=[];groups=np.digitize(src[:,1],np.quantile(src[:,1],[1/3,2/3]))
   for g in range(3):
    m=groups!=g;HH,jj=fit(src[m],dst[m],kind)
    if HH is None:folds.append({'held_source_line_third':g,'fit_failed':True});continue
    er=np.linalg.norm(predict(HH,src[~m])-dst[~m],axis=1);folds.append({'held_source_line_third':g,'held_ids':[r['id']for r,k in zip(train,~m)if k],'errors':stats(er)})
   anchors=[]
   if region=='upper_red':
    for k in known:
     err=np.linalg.norm(predict(H,np.array(k['native_fx10_anchor_column_line'])[None])[0]-k['native_fx17_subpixel_column_line']);anchors.append({'id':k['prior_fx10_id'],'error_native_fx17_px':float(err)})
   models.append({'kind':kind,'H_native_fx10_column_line_to_native_fx17_column_line':H.tolist(),'inlier_count':int(ii.sum()),'training_inlier_stats':stats(e[ii]),'all_training_candidate_stats':stats(e),'inlier_ids':[r['id']for r,k in zip(train,ii)if k],'inlier_source_hull_native':cv2.convexHull(src[ii].astype(np.float32)).reshape(-1,2).tolist(),'spatial_folds':folds,'excluded_old_anchors':anchors})
 result={'region':region,'status':'per_leaf_cross_sensor_registration_candidate_not_physical_validation','A_resized_ROI':aroi,'B_native_rotated_ROI':broi,'FX10_original_rotated_bounds':[ax0+1450,0,ax1+1450,205 if region=='upper_red' else 240],'raw_matches':len(raw),'candidate_clusters':len(clusters),'repeatable_candidates':records,'training_candidates':len(train),'models':models,'policy':'Independent per-leaf fit. Existing red anchor neighbourhoods excluded. Complete source-line thirds held out without pre-filtering by full-fit inliers. Multiband/repeated observations correlated. No new independently surveyed physical controls.','source_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in [PREV/'fx10_overlap_display.npy',PREV/'fx17_overlap_display.npy']}}
 (HERE/f'{region}_registration.json').write_text(json.dumps(result,indent=2)+'\n');print(region,'matches',len(train),[(m['kind'],m['inlier_count'],m['training_inlier_stats']['rms_px'],m['excluded_old_anchors'])for m in models],flush=True)
 canvas=np.zeros((490,960,3),np.uint8);canvas[55:455,:450]=cv2.resize(A[ay0:ay1,ax0:ax1,1],(450,400))[:,:,None];canvas[55:455,510:]=cv2.resize(B[by0:by1,bx0:bx1,1],(450,400))[:,:,None]
 cv2.putText(canvas,f'{region}: independent overlap-band matches; numbers are candidate IDs',(8,27),cv2.FONT_HERSHEY_SIMPLEX,.65,(255,255,255),1)
 for r in train:
  col=tuple(int(x)for x in np.random.default_rng(r['id']).integers(80,255,3))
  for sensor in [10,17]:
   c,l=r[f'fx{sensor}_column_line'];px=l-(1450 if sensor==10 else 1350);py=(1023-c+.5)*.625-.5 if sensor==10 else 639-c;roi=aroi if sensor==10 else broi;pt=(int((px-roi[0])*450/(roi[2]-roi[0]))+(0 if sensor==10 else 510),int((py-roi[1])*400/(roi[3]-roi[1]))+55);cv2.circle(canvas,pt,3,col,1);cv2.putText(canvas,str(r['id']),pt,cv2.FONT_HERSHEY_SIMPLEX,.36,col,1)
 cv2.imwrite(str(HERE/f'{region}_registration.png'),canvas)
