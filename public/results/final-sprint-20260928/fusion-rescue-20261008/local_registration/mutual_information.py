"""Bounded affine registration by smoothed joint-intensity mutual information."""
from mind_registration import *
from scipy.optimize import minimize
from scipy.ndimage import gaussian_filter

for c in checks:
 for k in ['prediction','observed']:
  cv2.circle(mask,tuple(np.rint(np.array(c[k])-[x0,y0]).astype(int)),20,0,-1)
ys,xs=np.nonzero(mask); xy=np.c_[xs,ys].astype(np.float32)
cent=np.array([W/2,H/2],np.float32)
s=cv2.cvtColor(source,cv2.COLOR_RGB2GRAY).astype(np.float32)/255
t=cv2.cvtColor(target,cv2.COLOR_RGB2GRAY).astype(np.float32)/255
s=cv2.GaussianBlur(s,(0,0),1);t=cv2.GaussianBlur(t,(0,0),1)
sv=s[ys,xs]
def transform(par,p):
 lin=np.array([[1+par[0],par[1]],[par[2],1+par[3]]]);return ((p-cent)@lin.T+cent+par[4:6]).astype(np.float32)
def score(par):
 q=transform(par,xy)
 tv=cv2.remap(t,q[:,0].reshape(-1,1),q[:,1].reshape(-1,1),cv2.INTER_LINEAR).ravel()
 # Robust contrast changes are allowed; geometry has a small bounded affine correction.
 joint=np.histogram2d(sv,tv,bins=32,range=[[0,1],[0,1]])[0]
 joint=gaussian_filter(joint,.7)+1e-10;joint/=joint.sum()
 pa=joint.sum(1);pb=joint.sum(0);mi=np.sum(joint*np.log(joint/(pa[:,None]*pb[None,:])))
 entropy=-np.sum(pa*np.log(pa))-np.sum(pb*np.log(pb))
 nmi=2*mi/entropy
 penalty=.03*np.sum(np.array(par[:4])**2)+.000003*np.sum(np.array(par[4:6])**2)
 return -nmi+penalty
options=[]
for dy in range(-18,19,3):
 for dx in range(-18,19,3):
  p=[0,0,0,0,dx,dy];options.append((score(p),p))
options.sort(key=lambda x:x[0]);fits=[]
for _,p in options[:3]:
 result=minimize(score,np.array(p,float),method='Powell',bounds=[(-.15,.15)]*4+[(-22,22)]*2,options={'maxiter':70,'xtol':.0004,'ftol':1e-7})
 fits.append({'objective':float(result.fun),'parameters':result.x.tolist(),'success':bool(result.success),'nfev':int(result.nfev),'start':p})
fits.sort(key=lambda x:x['objective']);chosen=fits[0];par=chosen['parameters']
q=transform(par,base[0].numpy());disp=q-base[0].numpy()
name='mutual_information_affine';dpath=OUT/f'{name}.npz'
np.savez_compressed(dpath,initial_HSI_rotated_to_native_RGB=A,source_crop_xyxy=np.array([x0,y0,x1,y1]),forward_displacement_rgb_px=disp,training_mask=mask,residual_parameters=np.array(par))
record={'name':name,'status':'FROZEN_FOR_BLIND_AUDIT','method':'32bin smoothed joint-intensity normalized mutual information with bounded affine residual; top3 training-only translation grid starts',
 'training_pixels':len(xs),'training_objective':chosen['objective'],'fits':fits,'training_translation_grid_best':options[:8],
 'holdout_policy':'20px exclusion around old observed/predicted features; no exact control positions fit or used for selection. New checks kept private by separate auditor.',
 'artifact':dpath.name,'sha256':hashlib.sha256(dpath.read_bytes()).hexdigest(),'scope':'Appearance hypothesis only; no 3D spectral assignments.'}
(OUT/f'{name}.json').write_text(json.dumps(record,indent=2)+'\n')
aligned=cv2.remap(target,q[:,:,0],q[:,:,1],cv2.INTER_LINEAR)
cv2.imwrite(str(OUT/f'{name}_pair.jpg'),cv2.cvtColor(cv2.resize(np.hstack([source,aligned]),(1440,525)),cv2.COLOR_RGB2BGR))
print(json.dumps(record),flush=True)
