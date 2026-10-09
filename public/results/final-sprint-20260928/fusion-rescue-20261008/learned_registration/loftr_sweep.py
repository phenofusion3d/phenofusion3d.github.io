"""Learned correspondences: frozen configurations, not automatic fusion approval."""
from pathlib import Path
import os,sys,json,hashlib,time,urllib.request,copy,argparse
ROOT=Path(__file__).resolve().parents[3]; ROUND=Path(__file__).resolve().parents[1];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROUND/'vendor'),str(ROOT/'venv/Lib/site-packages'),str(ROOT)]
os.environ['OMP_NUM_THREADS']='2';os.environ['TORCH_HOME']=str(ROUND/'model_cache')
import torch,cv2,numpy as np
torch.set_num_threads(2);cv2.setNumThreads(2)
from kornia.feature import LoFTR,LightGlue,DISK
from processing.research_workspace.spectral_extract import read_envi_source
args=argparse.ArgumentParser();args.add_argument('--weights-only',action='store_true');args.add_argument('--model',default='outdoor');args.add_argument('--method',default='loftr',choices=['loftr','lightglue']);opt=args.parse_args()
weights=ROUND/'model_cache'/f'loftr_{opt.model}.ckpt'
url=f'https://huggingface.co/kornia/loftr/resolve/0fb3b456cf176746709c38fa9cf80695a1c82dac/loftr_{opt.model}.ckpt'
if not weights.exists():
 print('Downloading published pretrained weights',url,flush=True)
 urllib.request.urlretrieve(url,weights)
record={'url':url,'sha256':hashlib.sha256(weights.read_bytes()).hexdigest(),'bytes':weights.stat().st_size,'torch':torch.__version__}
(OUT/f'weights_{opt.model}.json').write_text(json.dumps(record,indent=2)+'\n')
if opt.weights_only:sys.exit(0)
if opt.method=='loftr':
 matcher=LoFTR(pretrained=None).eval();matcher.load_state_dict(torch.load(weights,map_location='cpu',weights_only=True)['state_dict'])
else:
 disk=DISK().eval();disk.load_state_dict(torch.load(ROUND/'model_cache/disk_depth.pth',map_location='cpu',weights_only=True)['extractor'])
 matcher=LightGlue(features=None,input_dim=128,flash=False).eval()
 sd=torch.load(ROUND/'model_cache/disk_lightglue.pth',map_location='cpu',weights_only=True)
 for i in range(9):
  sd={k.replace(f'self_attn.{i}',f'transformers.{i}.self_attn').replace(f'cross_attn.{i}',f'transformers.{i}.cross_attn'):v for k,v in sd.items()}
 missing,unexpected=matcher.load_state_dict(sd,strict=False)
 assert set(unexpected)<= {f'log_assignment.{i}.r' for i in range(9)} and set(missing)<= {'confidence_thresholds'},(missing,unexpected)
 record={'disk_sha256':hashlib.sha256((ROUND/'model_cache/disk_depth.pth').read_bytes()).hexdigest(),'lightglue_sha256':hashlib.sha256((ROUND/'model_cache/disk_lightglue.pth').read_bytes()).hexdigest(),'sources':['https://raw.githubusercontent.com/cvlab-epfl/disk/master/depth-save.pth','https://github.com/cvg/LightGlue/releases/download/v0.1_arxiv/disk_lightglue.pth'],'torch':torch.__version__,'state_compatibility':{'defaulted_buffers':missing,'legacy_unused_assignment_parameters':unexpected,'note':'Kornia constructor also loads these release weights with strict=False; all learned layers present.'}}
rgb=cv2.cvtColor(cv2.imread(str(ROOT/'data/main/test_plant_10-7/test_plant_20260928162354/rgb_1055904.png')),cv2.COLOR_BGR2RGB)
hsi=np.rot90(np.clip(np.load(ROOT/'generated/research_followthrough_20261007/spectral/fx10_display_rgb.npy')*255,0,255).astype('uint8')).copy()
source=read_envi_source(ROOT/'data/main/test_plant_10-7/20260928/003-specim-fx10.hdr')
band_ids=[int(np.argmin(abs(source.wavelength_nm-w))) for w in (450,550,650)]
raw=np.memmap(source.data,mode='r',dtype=source.dtype,offset=source.offset,shape=source.shape)
native=np.stack([np.rot90(np.asarray(raw[:,b,:],dtype=np.float32)) for b in band_ids[::-1]],axis=2)
del raw
probe=json.loads((ROOT/'generated/research_spectral_fusion_20261007/registration_probe/leaf_feature_probe.json').read_text())
clahe=cv2.createCLAHE(2,(4,4))
records=[]
def resize(im,shape):
 h,w=im.shape;ow,oh=shape
 return torch.from_numpy(cv2.resize(im,(ow,oh)).astype('float32')/255)[None,None],np.array([ow/w,oh/h])
def channel(im,ch):
 a=im[:,:,1] if ch=='green' else cv2.cvtColor(im,cv2.COLOR_RGB2GRAY)
 lo,hi=np.percentile(a,[1,99]);a=np.uint8(np.clip((a-lo)/max(float(hi-lo),1)*255,0,255))
 return clahe.apply(a)
def original(pts,scales,origin):return (pts+.5)/scales-.5+origin
for region in probe['regions']:
 name=region['region']; hb=np.array(region['hsi_rotated_bounds']); rb=np.array(region['rgb_bounds'])
 if name=='green_lower':hb=np.array([1735,495,1920,745]);rb=np.array([960,435,1140,580])
 hs=hsi[hb[1]:hb[3],hb[0]:hb[2]];ra=rgb[rb[1]:rb[3],rb[0]:rb[2]]
 held=[c for c in region['candidates'] if c['id'] in ['red_upper_2','red_upper_6','green_lower_0','green_lower_4']]
 hp=np.array([[c['hsi_column_line'][1],1023-c['hsi_column_line'][0]] for c in held]).reshape(-1,2);hq=np.array([c['rgb_xy'] for c in held]).reshape(-1,2)
 for ch in ['gray','green','native_visible']:
  ha=hs if ch!='native_visible' else native[hb[1]:hb[3],hb[0]:hb[2]].copy()
  if ch=='native_visible':
   ha=np.stack([np.clip((ha[:,:,i]-np.percentile(ha[:,:,i],1))/max(float(np.percentile(ha[:,:,i],99)-np.percentile(ha[:,:,i],1)),1)*255,0,255) for i in range(3)],axis=2).astype('uint8')
  a=channel(ha,'green' if ch=='green' else 'gray');b=channel(ra,'green' if ch=='green' else 'gray')
  for anisotropic in [False,True]:
   # Equal canvas aspect is a preprocessing hypothesis; inverse uses pixel centres.
   bw=384;bh=max(64,int(round(ra.shape[0]/ra.shape[1]*bw/8))*8)
   ah=bh if anisotropic else max(64,int(round(hs.shape[0]/hs.shape[1]*bw/8))*8)
   ta,sa=resize(a,(bw,ah));tb,sb=resize(b,(bw,bh));t=time.time()
   with torch.inference_mode():
    if opt.method=='loftr':m=matcher({'image0':ta,'image1':tb})
    else:
     d0=disk(ta.repeat(1,3,1,1),n=1024,pad_if_not_divisible=True)[0];d1=disk(tb.repeat(1,3,1,1),n=1024,pad_if_not_divisible=True)[0]
     f0={'keypoints':d0.keypoints[None],'descriptors':d0.descriptors[None],'image_size':torch.tensor([[ta.shape[3],ta.shape[2]]])};f1={'keypoints':d1.keypoints[None],'descriptors':d1.descriptors[None],'image_size':torch.tensor([[tb.shape[3],tb.shape[2]]])}
     out=matcher({'image0':f0,'image1':f1});pairs=out['matches'][0]
     m={'keypoints0':d0.keypoints[pairs[:,0]],'keypoints1':d1.keypoints[pairs[:,1]],'confidence':out['matching_scores0'][0,pairs[:,0]]}
   pp=original(m['keypoints0'].numpy(),sa,hb[:2]);qq=original(m['keypoints1'].numpy(),sb,rb[:2]);cf=m['confidence'].numpy()
   usable=cf>=.35
   if len(hp):usable&=(np.linalg.norm(pp[:,None]-hp,axis=2).min(axis=1)>10)&(np.linalg.norm(qq[:,None]-hq,axis=2).min(axis=1)>6)
   pp=pp[usable];qq=qq[usable];cf=cf[usable]
   row={'region':name,'channel':ch,'aspect_normalized':anisotropic,'hsi_bounds':hb.tolist(),'rgb_bounds':rb.tolist(),'seconds':time.time()-t,'matches':len(pp),'source':pp.tolist(),'target':qq.tolist(),'confidence':cf.tolist(),'models':[]}
   if len(pp)>=6:
    for kind in ['affine','homography']:
     cv2.setRNGSeed(5817)
     if kind=='affine':A,ii=cv2.estimateAffine2D(pp,qq,method=cv2.RANSAC,ransacReprojThreshold=2.,maxIters=30000,confidence=.999,refineIters=20);H=np.vstack([A,[0,0,1]]) if A is not None else None
     else:H,ii=cv2.findHomography(pp,qq,cv2.USAC_MAGSAC,2.,maxIters=30000,confidence=.999)
     if H is None:continue
     ii=ii.ravel().astype(bool);pred=cv2.perspectiveTransform(pp.reshape(-1,1,2),H).reshape(-1,2)
     errs=np.linalg.norm(pred-qq,axis=1);area=cv2.contourArea(cv2.convexHull(pp[ii].astype('float32')))/np.prod(hb[2:]-hb[:2])
     check=cv2.perspectiveTransform(hp.reshape(-1,1,2),H).reshape(-1,2) if len(hp) else []
     checks=[{'id':c['id'],'observed':q.tolist(),'predicted':p.tolist(),'error_rgb_px':float(np.linalg.norm(p-q))} for c,p,q in zip(held,check,hq)]
     row['models'].append({'kind':kind,'H':H.tolist(),'inliers':int(ii.sum()),'inlier_indices':np.flatnonzero(ii).tolist(),'training_rms':float(np.sqrt(np.mean(errs[ii]**2))),'training_hull_fraction':float(area),'old_exposed_checks':checks,'new_holdout_validation':False})
   records.append(row)
   print(name,ch,anisotropic,len(pp),[(x['kind'],x['inliers'],[round(c['error_rgb_px'],2) for c in x['old_exposed_checks']]) for x in row['models']],flush=True)
   (OUT/f'{opt.method}_{opt.model}.json').write_text(json.dumps({'method':opt.method,'weights':record,'frame':1055904,'control_exclusion':'Exclude features within10nativeHSIpixels or6nativeRGBpixels of old exposed diagnostic controls from fitting. Context still contains controls; this is not an untouched image holdout. New reserved landmarks required.','selection_policy':'Freeze all variants; rank fit by inlier support and spatial spread, never old check error. No physical accuracy or dense assignment accepted.','records':records},indent=2)+'\n')
