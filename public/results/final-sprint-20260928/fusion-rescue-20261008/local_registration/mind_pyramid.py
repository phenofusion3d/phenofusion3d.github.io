"""Coarse-to-fine MIND with a training-only bounded translation initialization."""
from mind_registration import *

foreground_only=os.environ.get('MIND_FOREGROUND','0')=='1'
name='pyramid_mind_foreground' if foreground_only else 'pyramid_mind_rgb'
if foreground_only:
 # Exclude visible white-board/background pixels in the initially warped source.
 # This mask is derived from image chromaticity, never correspondence checks.
 hsv=cv2.cvtColor(source,cv2.COLOR_RGB2HSV)
 foreground=((hsv[:,:,0]>=28)&(hsv[:,:,0]<=100)&(hsv[:,:,1]>=45)&(hsv[:,:,2]>=30)).astype(np.uint8)*255
 foreground=cv2.erode(foreground,np.ones((7,7),np.uint8))
 mask=cv2.bitwise_and(mask,foreground)
 cv2.imwrite(str(OUT/'source_foreground_mask.png'),foreground)

# Larger exclusions cover the descriptor footprint at quarter resolution.
for c in checks:
 for k in ['prediction','observed']:
  cv2.circle(mask,tuple(np.rint(np.array(c[k])-[x0,y0]).astype(int)),30,0,-1)
trainmask=torch.from_numpy((mask>0).astype(np.float32))[None,None]
cv2.imwrite(str(OUT/f'{name}_training_mask.png'),mask)
aff=torch.zeros((2,3),requires_grad=True)
mat=torch.cat([normxy,torch.ones((1,H,W,1))],-1)
history=[]
for scale in [4,2,1]:
 smallsrc=cv2.resize(source,(W//scale,H//scale),interpolation=cv2.INTER_AREA)
 smalldst=cv2.resize(target,(W//scale,H//scale),interpolation=cv2.INTER_AREA)
 ds=F.interpolate(mind(smallsrc,'rgb'),size=(H,W),mode='bilinear',align_corners=True)
 dt=F.interpolate(mind(smalldst,'rgb'),size=(H,W),mode='bilinear',align_corners=True)
 if scale==4:
  options=[]
  with torch.no_grad():
   for dy in range(-18,19,3):
    for dx in range(-18,19,3):
     pred=sample(dt,base+torch.tensor([dx,dy]))
     val=(F.smooth_l1_loss(pred,ds,reduction='none',beta=.15)*trainmask).sum()/(trainmask.sum()*ds.shape[1])
     options.append((float(val),dx,dy))
   options.sort();_,dx,dy=options[0];aff[:,2]=torch.tensor([dx,dy])
  history.append({'scale':4,'training_translation_grid_best':options[:8]})
 opt=torch.optim.Adam([aff],lr=.10 if scale>1 else .03)
 for it in range(220):
  opt.zero_grad();disp=mat@aff.T;pred=sample(dt,base+disp)
  data=(F.smooth_l1_loss(pred,ds,reduction='none',beta=.15)*trainmask).sum()/(trainmask.sum()*ds.shape[1])
  reg=.00005*aff[:,:2].square().mean()+.000001*disp.square().mean()
  loss=data+reg;loss.backward();opt.step()
 history.append({'scale':scale,'training_loss':float(data.detach()),'affine_residual':aff.detach().tolist()})
 print('scale',scale,float(data.detach()),aff.detach().tolist(),flush=True)

fixed=(mat@aff.detach().T).detach()
coarse=torch.zeros((1,2,5,7),requires_grad=True)
opt=torch.optim.Adam([coarse],lr=.04)
for it in range(280):
 opt.zero_grad();local=F.interpolate(coarse,size=(H,W),mode='bicubic',align_corners=True).permute(0,2,3,1)
 disp=fixed+local;pred=sample(dt,base+disp)
 data=(F.smooth_l1_loss(pred,ds,reduction='none',beta=.15)*trainmask).sum()/(trainmask.sum()*ds.shape[1])
 smooth=(coarse[:,:,1:,:]-coarse[:,:,:-1,:]).square().mean()+(coarse[:,:,:,1:]-coarse[:,:,:,:-1]).square().mean()
 reg=.002*smooth+.00003*local.square().mean();loss=data+reg;loss.backward();opt.step()
disp=(fixed+F.interpolate(coarse,size=(H,W),mode='bicubic',align_corners=True).permute(0,2,3,1)).detach()[0].numpy()
jac=(1+np.gradient(disp[:,:,0],axis=1))*(1+np.gradient(disp[:,:,1],axis=0))-np.gradient(disp[:,:,0],axis=0)*np.gradient(disp[:,:,1],axis=1)
dpath=OUT/f'{name}.npz'
np.savez_compressed(dpath,initial_HSI_rotated_to_native_RGB=A,source_crop_xyxy=np.array([x0,y0,x1,y1]),forward_displacement_rgb_px=disp,coarse_controls=coarse.detach().numpy(),affine_residual=aff.detach().numpy(),training_mask=mask)
result={'name':name,'status':'FROZEN_FOR_BLIND_AUDIT','method':'Three-scale MIND 4/2/1 + bounded coarse translation grid chosen by training loss + residual affine + regularized5x7bicubic displacement',
 'training_pixels':int((mask>0).sum()),'training_loss':float(data.detach()),'training_objective':float(loss.detach()),'history':history,'holdout_policy':'30px exclusion disks; no holdout errors inspected before freezing','source_foreground_only':foreground_only,
 'jacobian_min':float(jac[mask>0].min()),'jacobian_max':float(jac[mask>0].max()),'folded_training_pixels':int((jac[mask>0]<=0).sum()),'maximum_training_displacement_rgb_px':float(np.linalg.norm(disp[mask>0],axis=1).max()),'artifact':dpath.name,'sha256':hashlib.sha256(dpath.read_bytes()).hexdigest(),
 'scope':'Single green P5 leaf in RGBframe1055904. Appearance hypothesis only; no metric surface assignments.'}
(OUT/f'{name}.json').write_text(json.dumps(result,indent=2)+'\n')
q=base[0].numpy()+disp;aligned=cv2.remap(target,q[:,:,0],q[:,:,1],cv2.INTER_LINEAR)
cv2.imwrite(str(OUT/f'{name}_pair.jpg'),cv2.cvtColor(cv2.resize(np.hstack([source,aligned]),(1440,525)),cv2.COLOR_RGB2BGR))
print(json.dumps(result),flush=True)
