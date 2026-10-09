"""Predefined 16-pair LoFTR extension to P1--P4; no fusion promotion."""
from pathlib import Path
import os,sys,json,hashlib,time
ROOT=Path.cwd();ROUND=ROOT/'generated/research_fusion_rescue_20261008';OUT=Path(__file__).resolve().parent
os.environ['OMP_NUM_THREADS']='2';os.environ['MKL_NUM_THREADS']='2';os.environ['TORCH_HOME']=str(ROUND/'model_cache')
sys.path[:0]=[str(ROUND/'vendor'),str(ROOT/'venv/Lib/site-packages'),str(ROOT)]
import torch,cv2,numpy as np,open3d as o3d
from scipy.spatial import cKDTree
from kornia.feature import LoFTR
torch.set_num_threads(2);cv2.setNumThreads(2)

D=ROOT/'generated/research_20260928_improvement_20261007/short_dense_v3'
C=ROOT/'generated/research_confirmed_board_20261007/cleanup_v1/result'
profile=json.loads((D/'profile.json').read_text());K=np.array(profile['K']);dist=np.array(profile['dist'])
poses=[r for r in json.loads((D/'result/icp_diagnostics.json').read_text()) if r['icp_accepted']]
scale=1.0288746669066682
rgbroot=Path(profile['dataset'])
hsip=ROOT/'generated/research_followthrough_20261007/spectral/fx10_display_rgb.npy'
hsi=np.rot90(np.clip(np.load(hsip)*255,0,255).astype('uint8')).copy()
spectral=json.loads((ROOT/'generated/research_followthrough_20261007/spectral/fx10_summary.json').read_text())
windows={1:(180,550),2:(550,880),3:(880,1230),4:(1230,1550)}
allpoint={i:np.asarray(o3d.io.read_point_cloud(str(C/f'P{i}_reference.ply')).points) for i in range(1,5)}
cache={}
def projection(i,pose,full=False):
 xyz=allpoint[i] if full else allpoint[i][::3]
 T=np.array(pose['transform']);T[:3,3]*=scale
 pc=(xyz-T[:3,3])@T[:3,:3]
 uv=cv2.projectPoints(pc,np.zeros(3),np.zeros(3),K,dist)[0][:,0]
 good=(pc[:,2]>0)&np.isfinite(uv).all(1)&(uv[:,0]>=5)&(uv[:,0]<1275)&(uv[:,1]>=5)&(uv[:,1]<715)
 ids=np.flatnonzero(good)
 if len(ids)==0:return uv,np.zeros(len(xyz),bool),dict(inside_fraction=0.,supported_fraction=0.,occupied_pixels=0,score=0.)
 fr=pose['frame']
 if fr not in cache:
  zz=np.load(D/f'rgb/depth_{fr}.npz');cache[fr]=(zz['depth']*scale,zz['votes'])
 dep,votes=cache[fr]
 ideal=pc[ids,:2]/pc[ids,2,None]*[K[0,0],K[1,1]]+[K[0,2],K[1,2]]
 pix=np.rint(ideal).astype(int);inside=(pix[:,0]>=0)&(pix[:,0]<1280)&(pix[:,1]>=0)&(pix[:,1]<720)
 ids=ids[inside];pix=pix[inside]
 z=dep[pix[:,1],pix[:,0]];v=votes[pix[:,1],pix[:,0]]
 support=np.isfinite(z)&(z>0)&(v>=2)&(abs(pc[ids,2]-z)<=.015)
 supported=np.zeros(len(xyz),bool);supported[ids[support]]=True
 occ=len(np.unique(np.rint(uv[supported]).astype(int),axis=0))
 score=occ*good.mean()
 return uv,supported,dict(inside_fraction=float(good.mean()),supported_fraction=float(supported.mean()),occupied_pixels=occ,score=float(score))

selections=[]
for i in range(1,5):
 ranking=[]
 for k,p in enumerate(poses):
  _,_,r=projection(i,p);ranking.append(dict(frame=p['frame'],pose_index=k,**r))
 ranking.sort(key=lambda r:r['score'],reverse=True);best=ranking[0]
 adjacent=[r for r in ranking if abs(r['pose_index']-best['pose_index'])==1]
 selected=[best,max(adjacent,key=lambda r:r['score'])]
 sel={'plant_id':i,'identity_scope':f'Provisional scan-order region R{i} to existing RGB-D plant P{i}; whole-plant identity alone does not establish same-organ pixel correspondence.',
  'view_selection':'Highest depth-supported projected pixel occupancy times in-frame fraction; adjacent accepted view chosen by same geometry score. No HSI match results used.',
  'selected_views':selected,'ranking':ranking}
 selections.append(sel);print('selected',i,[(r['frame'],r['score']) for r in selected],flush=True)
(OUT/'frozen_view_selection.json').write_text(json.dumps({'predefined_runs':16,'selections':selections},indent=2)+'\n')
cache.clear()
weights=ROUND/'model_cache/loftr_outdoor.ckpt'
matcher=LoFTR(pretrained=None).eval();matcher.load_state_dict(torch.load(weights,map_location='cpu',weights_only=True)['state_dict'])
clahe=cv2.createCLAHE(2.,(4,4))
records=[];inputs=[hsip,weights,D/'profile.json',D/'result/icp_diagnostics.json']

def mono(im,ch):
 a=im[:,:,1] if ch=='green' else cv2.cvtColor(im,cv2.COLOR_RGB2GRAY)
 lo,hi=np.percentile(a,[1,99]);return clahe.apply(np.uint8(np.clip((a-lo)/max(float(hi-lo),1)*255,0,255)))
def resize(im,wh):
 hh,ww=im.shape;ow,oh=wh
 return torch.from_numpy(cv2.resize(im,(ow,oh)).astype('float32')/255)[None,None],np.array([ow/ww,oh/hh])
def original(p,sc,origin):return (p+.5)/sc-.5+origin

for sel in selections:
 i=sel['plant_id']; a,b=windows[i];hb=np.array([a,23,b,943])
 hs=hsi[hb[1]:hb[3],hb[0]:hb[2]]
 patches=[p for p in spectral['patches'] if p['region_id']==i]
 roimap=np.zeros(hsi.shape[:2],np.uint8)
 for p in patches:
  poly=np.array(p['polygon_column_line']);rot=np.c_[poly[:,1],1023-poly[:,0]]
  cv2.fillPoly(roimap,[rot.astype(int)],p['patch_id'])
 for view in sel['selected_views']:
  fr=view['frame'];pose=poses[view['pose_index']]
  uv,supported,q=projection(i,pose,full=True)
  if supported.sum()<6:raise RuntimeError(f'Insufficient geometry support for selected P{i} frame{fr}')
  supportids=np.flatnonzero(supported);tree=cKDTree(uv[supported])
  lo=np.maximum(np.floor(np.quantile(uv[supported],.005,axis=0))-18,[0,0]).astype(int)
  hi=np.minimum(np.ceil(np.quantile(uv[supported],.995,axis=0))+18,[1280,720]).astype(int)
  rb=np.r_[lo,hi];rp=rgbroot/f'rgb_{fr}.png';inputs.extend([rp,C/f'P{i}_reference.ply',D/f'rgb/depth_{fr}.npz'])
  rgb=cv2.cvtColor(cv2.imread(str(rp)),cv2.COLOR_BGR2RGB);ra=rgb[rb[1]:rb[3],rb[0]:rb[2]]
  # Same rectangular canvas is one declared anisotropic preprocessing hypothesis.
  bh=384;bw=int(np.clip(round(ra.shape[1]/ra.shape[0]*bh/8)*8,160,384));shape=(bw,bh)
  for ch in ['gray','green']:
   ta,sa=resize(mono(hs,ch),shape);tb,sb=resize(mono(ra,ch),shape);started=time.time()
   with torch.inference_mode():m=matcher({'image0':ta,'image1':tb})
   pp=original(m['keypoints0'].numpy(),sa,hb[:2]);qq=original(m['keypoints1'].numpy(),sb,rb[:2]);cf=m['confidence'].numpy()
   keep=cf>=.35;pp,qq,cf=pp[keep],qq[keep],cf[keep]
   hh=np.rint(pp).astype(int);valid=(hh[:,0]>=0)&(hh[:,0]<hsi.shape[1])&(hh[:,1]>=0)&(hh[:,1]<hsi.shape[0])
   patchids=np.zeros(len(pp),int);patchids[valid]=roimap[hh[valid,1],hh[valid,0]]
   if len(qq):distance,nearest=tree.query(qq)
   else:distance=np.array([]);nearest=np.array([],int)
   domain=(patchids>0)&(distance<=6.)
   row={'plant_id':i,'hsi_scan_region':i,'frame':fr,'channel':ch,'hsi_bounds':hb.tolist(),'rgb_bounds':rb.tolist(),'canvas_wh':list(shape),'inference_seconds':time.time()-started,
    'raw_confident_matches':len(pp),'reviewed_hsi_roi_matches':int((patchids>0).sum()),'plant_geometry_near_matches':int((distance<=6).sum()),'joint_domain_matches':int(domain.sum()),
    'source_HSI_rotated_xy':pp.tolist(),'target_native_RGB_xy':qq.tolist(),'confidence':cf.tolist(),'hsi_patch_ids':patchids.tolist(),'nearest_supported_plant_pixel_distance':distance.tolist(),
    'nearest_current_plant_vertex_index':supportids[nearest].tolist(),'joint_domain_indices':np.flatnonzero(domain).tolist(),'patch_models':[]}
   for pat in patches:
    ids=np.flatnonzero(domain&(patchids==pat['patch_id']));src=pp[ids];dst=qq[ids]
    if len(ids)<6:continue
    for kind in ['affine','homography']:
     cv2.setRNGSeed(5817)
     if kind=='affine':AA,ii=cv2.estimateAffine2D(src,dst,method=cv2.RANSAC,ransacReprojThreshold=2,maxIters=30000,confidence=.999,refineIters=20);M=np.vstack([AA,[0,0,1]]) if AA is not None else None
     else:M,ii=cv2.findHomography(src,dst,cv2.USAC_MAGSAC,2,maxIters=30000,confidence=.999)
     if M is None:continue
     ii=ii.ravel().astype(bool);pred=cv2.perspectiveTransform(src.reshape(-1,1,2),M)[:,0];err=np.linalg.norm(pred-dst,axis=1)
     hull=cv2.contourArea(cv2.convexHull(src[ii].astype(np.float32))) if ii.sum()>=3 else 0
     model={'patch_id':pat['patch_id'],'patch_name':pat['name'],'kind':kind,'H_HSIrotated_to_nativeRGB':M.tolist(),'inlier_global_indices':ids[ii].tolist(),'inlier_count':int(ii.sum()),
      'training_rms_rgb_px':float(np.sqrt(np.mean(err[ii]**2))) if ii.any() else None,'training_hull_over_reviewed_patch_area':float(hull/pat['mask_pixels']),
      'independent_checks':0,'accepted_for_3d_assignment':False,'reason':'Learned appearance fit only; no independently established same-organ endpoints in this HSI/RGB pair.'}
     row['patch_models'].append(model)
   records.append(row)
   # Show every joint-domain proposal up to 35 highest-confidence pairs; no 3D colour map.
   ah,aw=420,400
   panel=np.full((ah+70,aw*2+40,3),25,np.uint8)
   panel[60:480,:aw]=cv2.resize(hs,(aw,ah));panel[60:480,aw+40:]=cv2.resize(ra,(aw,ah))
   shown=np.flatnonzero(domain);shown=shown[np.argsort(cf[shown])[::-1]][:35]
   for k,ix in enumerate(shown):
    p0=(int((pp[ix,0]-hb[0])*aw/(hb[2]-hb[0])),60+int((pp[ix,1]-hb[1])*ah/(hb[3]-hb[1])))
    p1=(aw+40+int((qq[ix,0]-rb[0])*aw/(rb[2]-rb[0])),60+int((qq[ix,1]-rb[1])*ah/(rb[3]-rb[1])))
    color=(60+int(k*57)%180,230,100+int(k*41)%155)
    cv2.circle(panel,p0,3,color,-1);cv2.circle(panel,p1,3,color,-1);cv2.line(panel,p0,p1,color,1)
   cv2.putText(panel,f'P{i} / HSI R{i}, RGB {fr}, {ch}: {int(domain.sum())} domain proposals',(8,23),cv2.FONT_HERSHEY_SIMPLEX,.53,(255,255,255),1)
   cv2.putText(panel,'UNVALIDATED APPEARANCE MATCHES. No spectral 3D assignments.',(8,47),cv2.FONT_HERSHEY_SIMPLEX,.50,(255,200,50),1)
   name=f'P{i}_{fr}_{ch}';cv2.imwrite(str(OUT/f'{name}.jpg'),cv2.cvtColor(panel,cv2.COLOR_RGB2BGR))
   print(name,'matches',len(pp),'joint',int(domain.sum()),'fits',[(r['patch_id'],r['kind'],r['inlier_count'],round(r['training_rms_rgb_px'],2)) for r in row['patch_models']],flush=True)
   (OUT/'learned_other_plants.json').write_text(json.dumps({'status':'EXPLORATORY_ONLY_NO_DENSE_PROMOTION','selection_frozen_before_matching':True,'method':'Cached pretrained LoFTR outdoor; two geometry-selected views and two channels perplant; native coordinate inverse accounts for pixel centers',
    'domain_policy':'Source inside previously reviewed HSI tissue polygon; target within6nativeRGBpx of recorded depth-supported plant projection. This is proximity support, not proof of correct material correspondence.',
    'identity_policy':'R1–R4 are assistant-reviewed scan-order region hypotheses paired to P1–P4. Printed region labels and scene order support coarse association; no automatic organ equivalence assumed.',
    'accepted_new_dense_assignments':0,'records':records},indent=2)+'\n')

hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in set(inputs)}
(OUT/'input_hashes.json').write_text(json.dumps(hashes,indent=2)+'\n')
print('COMPLETE',len(records),'runs',sum(r['joint_domain_matches'] for r in records),'domain proposals, zero accepted assignments',flush=True)
