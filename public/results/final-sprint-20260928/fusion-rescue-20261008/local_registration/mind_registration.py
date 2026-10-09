"""Frozen local MIND-style multimodal registration experiment.

The output is an image registration hypothesis, not measured 3D fusion.
No previously withheld landmark is fitted or used to select parameters.
"""
from pathlib import Path
import os
os.environ['OMP_NUM_THREADS']='2'
os.environ['MKL_NUM_THREADS']='2'
import json, hashlib, time
import cv2, numpy as np, torch
import torch.nn.functional as F

torch.set_num_threads(2); cv2.setNumThreads(2)
ROOT=Path.cwd(); OUT=Path(__file__).resolve().parent
PREV=ROOT/'generated/research_sprint_review_20261008/multiview_probe'
INIT=json.loads((PREV/'manual_init/manual_affine.json').read_text())
A=np.array(INIT['matrix'],np.float32)
hsip=ROOT/'generated/research_followthrough_20261007/spectral/fx10_display_rgb.npy'
rgbp=ROOT/'data/main/test_plant_10-7/test_plant_20260928162354/rgb_1055904.png'
h=np.rot90(np.clip(np.load(hsip)*255,0,255).astype('uint8')).copy()
rgb=cv2.cvtColor(cv2.imread(str(rgbp)),cv2.COLOR_BGR2RGB)
x0,y0,x1,y1=930,430,1170,605; H,W=y1-y0,x1-x0
source=cv2.warpAffine(h,A,(1280,720))[y0:y1,x0:x1].copy()
target=rgb[y0:y1,x0:x1].copy()
poly=np.array([[963,458],[990,468],[1000,452],[1028,470],[1080,468],[1110,489],[1113,512],[1132,532],[1130,562],[1090,570],[1060,556],[1040,540],[1010,539],[990,522],[985,499],[968,497]])-[x0,y0]
mask=np.zeros((H,W),np.uint8);cv2.fillPoly(mask,[poly],255)
mask=cv2.erode(mask,np.ones((11,11),np.uint8))
checks=INIT['heldout_checks']
for c in checks:
 for k in ['prediction','observed']:
  cv2.circle(mask,tuple(np.rint(np.array(c[k])-[x0,y0]).astype(int)),18,0,-1)
cv2.imwrite(str(OUT/'training_mask.png'),mask)
cv2.imwrite(str(OUT/'initial_pair.jpg'),cv2.cvtColor(np.hstack([cv2.resize(source,(720,525)),cv2.resize(target,(720,525))]),cv2.COLOR_RGB2BGR))

def mind(im, mode):
 # Self-similarity of local patches, normalized independently at every pixel.
 # Directional offsets are evaluated after the frozen anisotropic initial warp.
 if mode=='gray': im=cv2.cvtColor(im,cv2.COLOR_RGB2GRAY)[:,:,None]
 a=torch.from_numpy(im.astype(np.float32)/255).permute(2,0,1)[None]
 # Reduce sensor noise while preserving leaf veins.
 a=F.avg_pool2d(F.pad(a,(1,1,1,1),mode='reflect'),3,1)
 distances=[]
 offsets=[(2,0),(-2,0),(0,2),(0,-2),(4,0),(-4,0),(0,4),(0,-4),(3,3),(-3,3),(3,-3),(-3,-3)]
 for dx,dy in offsets:
  b=torch.roll(a,(dy,dx),dims=(2,3))
  sq=(a-b).square().mean(1,keepdim=True)
  distances.append(F.avg_pool2d(F.pad(sq,(1,1,1,1),mode='reflect'),3,1))
 d=torch.cat(distances,1);d=d-d.min(1,keepdim=True)[0]
 v=d.mean(1,keepdim=True);lo=v.mean()*.03;hi=v.mean()*20
 desc=torch.exp(-d/v.clamp(lo,hi).clamp_min(1e-7))
 return desc

yy,xx=torch.meshgrid(torch.arange(H),torch.arange(W),indexing='ij')
base=torch.stack([xx,yy],-1).float()[None]
normalizer=torch.tensor([W-1,H-1]).float()
trainmask=torch.from_numpy((mask>0).astype(np.float32))[None,None]
normxy=(base-torch.tensor([W/2,H/2]))/100.

def sample(tensor,xy):return F.grid_sample(tensor,2*xy/normalizer-1,align_corners=True,padding_mode='border')
def fit(mode,grid,penalty,name):
 ds=mind(source,mode);dt=mind(target,mode)
 # Stage 1 fits a small global residual. Stage 2 is a coarse smooth field.
 aff=torch.zeros((2,3),requires_grad=True)
 mat=torch.cat([normxy,torch.ones((1,H,W,1))],-1)
 opt=torch.optim.Adam([aff],lr=.06)
 history=[]
 for it in range(240):
  opt.zero_grad();disp=mat@aff.T;pred=sample(dt,base+disp)
  data=(F.smooth_l1_loss(pred,ds,reduction='none',beta=.15)*trainmask).sum()/(trainmask.sum()*ds.shape[1])
  reg=.0002*aff[:,:2].square().mean()+.00001*disp.square().mean()
  loss=data+reg;loss.backward();opt.step()
  if it%80==0:history.append({'stage':'affine','iteration':it,'data':float(data),'penalty':float(reg)})
 aff=aff.detach(); fixed=(mat@aff.T).detach()
 coarse=torch.zeros((1,2,grid[0],grid[1]),requires_grad=True)
 opt=torch.optim.Adam([coarse],lr=.07)
 for it in range(360):
  opt.zero_grad();local=F.interpolate(coarse,size=(H,W),mode='bicubic',align_corners=True).permute(0,2,3,1)
  disp=fixed+local;pred=sample(dt,base+disp)
  data=(F.smooth_l1_loss(pred,ds,reduction='none',beta=.15)*trainmask).sum()/(trainmask.sum()*ds.shape[1])
  # Coarse neighboring-control regularization plus a weak zero-deformation prior.
  smooth=(coarse[:,:,1:,:]-coarse[:,:,:-1,:]).square().mean()+(coarse[:,:,:,1:]-coarse[:,:,:,:-1]).square().mean()
  reg=penalty*smooth+.00003*local.square().mean()
  loss=data+reg;loss.backward();opt.step()
  if it%120==0:history.append({'stage':'smooth','iteration':it,'data':float(data),'penalty':float(reg)})
 disp=(fixed+F.interpolate(coarse,size=(H,W),mode='bicubic',align_corners=True).permute(0,2,3,1)).detach()[0].numpy()
 dxdu=np.gradient(disp[:,:,0],axis=1);dxdv=np.gradient(disp[:,:,0],axis=0)
 dydu=np.gradient(disp[:,:,1],axis=1);dydv=np.gradient(disp[:,:,1],axis=0)
 jac=(1+dxdu)*(1+dydv)-dxdv*dydu
 valid=mask>0
 dpath=OUT/f'{name}.npz'
 np.savez_compressed(dpath,initial_HSI_rotated_to_native_RGB=A,source_crop_xyxy=np.array([x0,y0,x1,y1]),forward_displacement_rgb_px=disp,coarse_controls=coarse.detach().numpy(),affine_residual=aff.numpy(),training_mask=mask)
 # Forward source-coordinate field allows third-party landmark evaluation without refitting.
 result={'name':name,'descriptor':mode,'grid':list(grid),'smoothness_weight':penalty,'initial_affine':A.tolist(),'crop':[x0,y0,x1,y1],
  'training_pixels':int(valid.sum()),'training_loss':float(data),'training_objective':float(loss),'deformation_max_rgb_px':float(np.linalg.norm(disp[valid],axis=1).max()),
  'jacobian_min_in_training':float(jac[valid].min()),'jacobian_max_in_training':float(jac[valid].max()),'folded_training_pixels':int((jac[valid]<=0).sum()),
  'history':history,'artifact':dpath.name,'sha256':hashlib.sha256(dpath.read_bytes()).hexdigest()}
 # Compare source with target sampled along forward map; never synthesize a spectral 3D output.
 q=base[0].numpy()+disp
 aligned=cv2.remap(target,q[:,:,0],q[:,:,1],cv2.INTER_LINEAR)
 show=np.hstack([source,aligned]);show=cv2.resize(show,(1440,525))
 cv2.imwrite(str(OUT/f'{name}_pair.jpg'),cv2.cvtColor(show,cv2.COLOR_RGB2BGR))
 (OUT/f'{name}.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result),flush=True)
 return result

if __name__=='__main__':
 runs=[]
 for name,mode,grid,penalty in [('primary_mind_rgb','rgb',(5,7),.002),('sensitivity_stiff','rgb',(5,7),.008),('sensitivity_gray','gray',(5,7),.002)]:
  runs.append(fit(mode,grid,penalty,name))
 record={'status':'FROZEN_IMAGE_HYPOTHESES_FOR_INDEPENDENT_AUDIT','primary_candidate':'primary_mind_rgb','selection':'Primary descriptor/grid/regularization fixed before execution and before new audit coordinates; sensitivity variants are reported without selecting by holdout error.',
  'method':'MIND-style directional local self-similarity; residual affine then bicubic coarse smooth displacement. Forward mapping from initial warped HSI positions to native RGB frame1055904.',
  'heldout_exclusion':'18px disks around the two old heldout predictions and observed positions; larger than descriptor footprint. Neither old nor newly audited control coordinates enter the fit.',
  'initialization':'Six previously declared manual hypotheses only, frozen affine from previous turn; some silhouette/vein hypotheses uncertain. No learned feature network and no metric 3D assignment.',
  'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [hsip,rgbp,PREV/'manual_init/manual_affine.json']},'runs':runs,
  'limits':['Loss minimization and smooth positive Jacobians do not certify anatomical correspondence.','Three-band display is a visualization, not radiometrically calibrated RGB.','Mask comes from prior reviewed leaf outline.','No 3D points modified and no spectra mapped to surface here.']}
 (OUT/'frozen_experiments.json').write_text(json.dumps(record,indent=2)+'\n')
 