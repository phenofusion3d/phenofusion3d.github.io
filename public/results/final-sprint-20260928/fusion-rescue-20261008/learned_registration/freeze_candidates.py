"""Freeze candidate maps using learned-fit evidence, without new test landmarks."""
from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'venv/Lib/site-packages')]
import cv2,numpy as np
from scipy.spatial import Delaunay
from scipy.interpolate import RBFInterpolator
records=[]
for file in [OUT/'loftr_outdoor.json',OUT/'lightglue_outdoor.json']:
 if file.exists():
  a=json.loads(file.read_text())
  records += [(file.stem,r) for r in a['records']]
names=sorted(set(r['region'] for _,r in records));export=[]
rgb=cv2.cvtColor(cv2.imread(str(ROOT/'data/main/test_plant_10-7/test_plant_20260928162354/rgb_1055904.png')),cv2.COLOR_BGR2RGB)
hsi=np.rot90(np.clip(np.load(ROOT/'generated/research_followthrough_20261007/spectral/fx10_display_rgb.npy')*255,0,255).astype('uint8')).copy()
dest=OUT/'frozen';dest.mkdir(exist_ok=True)
for name in names:
 candidates=[]
 for method,r in records:
  if r['region']!=name:continue
  for m in r['models']:
   # Explicit pre-test ranking. Inlier fit quality cannot establish true correspondence.
   if m['inliers']<8 or m['training_hull_fraction']<.05:continue
   score=m['inliers']*np.sqrt(m['training_hull_fraction'])/(1+m['training_rms'])
   candidates.append((score,method,r,m))
 if not candidates:continue
 score,method,r,m=max(candidates,key=lambda c:c[0]);H=np.array(m['H']);src=np.array(r['source']);tgt=np.array(r['target']);ii=m['inlier_indices'];p=src[ii];q=tgt[ii]
 hb=np.array(r['hsi_bounds']);rb=np.array(r['rgb_bounds']);yy,xx=np.mgrid[hb[1]:hb[3],hb[0]:hb[2]];grid=np.c_[xx.ravel(),yy.ravel()].astype('float64')
 hull=Delaunay(p);valid=hull.find_simplex(grid)>=0
 def project(x):return cv2.perspectiveTransform(x.reshape(-1,1,2),H).reshape(-1,2)
 base=project(grid);res=q-project(p)
 modes=[('projective' if m['kind']=='homography' else 'affine',None)]
 if len(p)>=12:modes += [('thin_plate_residual',s) for s in [1.,4.,16.]]
 for kind,smoothing in modes:
  mapped=base.copy()
  if smoothing is not None:mapped += RBFInterpolator(p,res,kernel='thin_plate_spline',smoothing=smoothing,degree=1)(grid)
  mapped[~valid]=np.nan
  key=f'{name}_{method}_{kind}'+(f'_s{smoothing:g}' if smoothing is not None else '')
  np.savez_compressed(dest/f'{key}.npz',hsi_origin=hb[:2],rgb_xy=mapped.reshape(*xx.shape,2).astype('float32'),supported_hull=valid.reshape(xx.shape))
  entry={'id':key,'region':name,'method':method,'channel':r['channel'],'aspect_normalized':r['aspect_normalized'],'selection_score':float(score),'training_inliers':len(p),'training_hull_fraction':m['training_hull_fraction'],'kind':kind,'smoothing':smoothing,'H':H.tolist(),'hsi_bounds':hb.tolist(),'rgb_bounds':rb.tolist(),'training_source':p.tolist(),'training_target':q.tolist(),'map_npz':str((dest/f'{key}.npz').relative_to(OUT)),'accepted':False}
  export.append(entry)
 # Match panel for the selected source model; no independent check markers shown.
 panel=np.ones((570,1000,3),dtype='uint8')*245
 ha=hsi[hb[1]:hb[3],hb[0]:hb[2]];ra=rgb[rb[1]:rb[3],rb[0]:rb[2]]
 panel[60:540,10:490]=cv2.resize(ha,(480,480));panel[60:540,510:990]=cv2.resize(ra,(480,480))
 cv2.putText(panel,f'{name} | {method} | {len(p)} learned inliers - NOT validated',(15,28),cv2.FONT_HERSHEY_SIMPLEX,.65,(20,20,20),2)
 for n,(a,b) in enumerate(zip(p,q)):
  x=(a-hb[:2])*480/(hb[2:]-hb[:2])+[10,60];y=(b-rb[:2])*480/(rb[2:]-rb[:2])+[510,60];color=(int((n*71)%200),int((n*113)%220),int((n*139)%200))
  cv2.circle(panel,tuple(x.astype(int)),3,color,1);cv2.circle(panel,tuple(y.astype(int)),3,color,1)
  if n%3==0:cv2.line(panel,tuple(x.astype(int)),tuple(y.astype(int)),color,1)
 cv2.imwrite(str(dest/f'{name}_matches.jpg'),cv2.cvtColor(panel,cv2.COLOR_RGB2BGR))
output={'policy':'Source model selected using inliers*sqrt(hull fraction)/(1+training RMS), independent of new check coordinates and old diagnostic errors. Residual TPS variants frozen before checking. Dense maps valid only within learned inlier convex hull; no whole-leaf guarantee.','frame':1055904,'candidates':export,'inputs':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in [OUT/'loftr_outdoor.json',OUT/'lightglue_outdoor.json'] if f.exists()}}
(OUT/'frozen_candidates.json').write_text(json.dumps(output,indent=2)+'\n')
print([(e['id'],e['training_inliers']) for e in export])
