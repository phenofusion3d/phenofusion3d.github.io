"""Check the supplied marker/square ratio against recorded D405 marker edges."""
from pathlib import Path
import json, hashlib
import cv2, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent/'marker_ratio_check'
SRC=ROOT/'generated/research_20260928_readiness_20261007/checkerboard_calibration'
DATA=ROOT/'data/main/test_plant_10-7/test_plant_20260928143911'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 OUT.mkdir(exist_ok=True,parents=True)
 saved=json.loads((SRC/'corner_observations.json').read_text());cal=json.loads((SRC/'calibration_experiment.json').read_text());K=np.array(cal['factory_K']);D=np.array(cal['factory_distortion'])
 dictionary=cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
 params=cv2.aruco.DetectorParameters();params.cornerRefinementMethod=cv2.aruco.CORNER_REFINE_SUBPIX
 detector=cv2.aruco.ArucoDetector(dictionary,params)
 board=cv2.aruco.CharucoBoard((7,10),1.,.72,dictionary); models=dict(zip(board.getIds().ravel().tolist(),board.getObjPoints()))
 old=cv2.aruco.CharucoBoard((7,10),1.,.6,dictionary);oldmodels=dict(zip(old.getIds().ravel().tolist(),old.getObjPoints()))
 rows=[];sources={}
 for o in saved['observations']:
  if o['sample_index'] not in [0,6,13,19,25,31]:continue
  p=DATA/o['frame'];sources[str(p.relative_to(ROOT))]=sha(p);im=cv2.imread(str(p));x0,y0,x1,y1=o['crop_xyxy'];gray=cv2.cvtColor(im[y0:y1,x0:x1],cv2.COLOR_BGR2GRAY);gray=cv2.resize(gray,None,fx=3,fy=3,interpolation=cv2.INTER_CUBIC)
  corners,ids,_=detector.detectMarkers(gray)
  if ids is None:continue
  r=np.array(o['factory_pose_rotation_rvec']);R=cv2.Rodrigues(r)[0];t=np.array(o['factory_pose_translation_board_squares'])
  for c,mid in zip(corners,ids.ravel()):
   if int(mid) not in models:continue
   uv=c.reshape(-1,2)/3+[x0,y0]
   predict=cv2.projectPoints(models[int(mid)],r,t,K,D)[0].reshape(-1,2)
   # Repeated IDs on other physical sheets never qualify merely by marker ID.
   if np.linalg.norm(uv.mean(0)-predict.mean(0))>2:continue
   rays=np.c_[cv2.undistortPoints(uv.astype(float).reshape(-1,1,2),K,D).reshape(-1,2),np.ones(4)]
   scale=(R[:,2]@t)/(rays@R[:,2]);points=(rays*scale[:,None]-t)@R
   edges=np.linalg.norm(points-np.roll(points,1,axis=0),axis=1)
   prior=cv2.projectPoints(oldmodels[int(mid)],r,t,K,D)[0].reshape(-1,2)
   rows.append(dict(frame=o['frame'],sheet=o['sheet'],marker_id=int(mid),observed_corners_xy=uv.tolist(),edge_ratios=edges.tolist(),median_edge_ratio=float(np.median(edges)),new_072_corner_rms_px=float(np.sqrt(np.mean(np.sum((uv-predict)**2,axis=1)))),old_060_corner_rms_px=float(np.sqrt(np.mean(np.sum((uv-prior)**2,axis=1))))))
 ratios=np.array([r['median_edge_ratio'] for r in rows]);assert len(ratios)>10
 summary=dict(status='recorded_marker_edge_check',expected_ratio=.72,marker_m=.018,square_m=.025,observations=len(rows),
  distinct_frames=len({r['frame'] for r in rows}),median_measured_edge_ratio=float(np.median(ratios)),p10_p90_measured_ratio=np.quantile(ratios,[.1,.9]).tolist(),
  median_new_corner_rms_px=float(np.median([r['new_072_corner_rms_px'] for r in rows])),median_old_corner_rms_px=float(np.median([r['old_060_corner_rms_px'] for r in rows])),
  explanation='Marker edges were re-detected in six sampled frames, backprojected onto each independently saved unit-square board pose. Ratio is an image-based consistency check, not a ruler calibration. Repeated physical sheets and low pixel resolution introduce correlated localization effects. Marker centres and final refined checker corners do not depend on the old 0.6 seed ratio.',
  sources=sources,observations_detail=rows,script_sha256=sha(Path(__file__)))
 (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 fig,ax=plt.subplots(figsize=(7.5,4.5));ax.hist(ratios,bins=20,color='#287d77',alpha=.85);ax.axvline(.72,color='#9d3d28',label='Confirmed 18/25 = 0.72');ax.axvline(.6,color='gray',ls='--',label='Earlier seed-only ratio 0.60');ax.set(xlabel='Marker edge / square edge (image-derived)',ylabel='Marker observations',title='Recorded marker size: consistency with the supplied design');ax.legend();fig.tight_layout();fig.savefig(OUT/'marker_ratio.png',dpi=170);fig.savefig(OUT/'marker_ratio.pdf');plt.close(fig)
 print(json.dumps({k:v for k,v in summary.items() if k not in ['observations_detail','sources','explanation']}))
if __name__=='__main__':main()
