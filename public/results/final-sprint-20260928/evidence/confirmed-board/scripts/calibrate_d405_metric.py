"""Recompute metric board poses and trajectory from the supplied print dimensions.

No plant reference is used. Prior results and application files stay untouched.
"""
from pathlib import Path
import hashlib, json, csv
import cv2
import numpy as np
from scipy.spatial.transform import Rotation

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
SRC=ROOT/'generated/research_20260928_readiness_20261007/checkerboard_calibration'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v): p.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def stats(x):
 x=np.asarray(x);return dict(n=len(x),rms=float(np.sqrt(np.mean(x*x))),median=float(np.median(x)),p95=float(np.quantile(x,.95)),max=float(x.max()))
def robust(X,Y):
 w=np.ones(len(X))
 for _ in range(15):
  b=np.linalg.lstsq(X*np.sqrt(w[:,None]),Y*np.sqrt(w[:,None]),rcond=None)[0]
  rr=np.linalg.norm(Y-X@b,axis=1); med=np.median(rr); mad=np.median(abs(rr-med))
  w=np.minimum(1,max(med+2.5*1.4826*mad,.000025)/np.maximum(rr,1e-12))
 return b,Y-X@b,w

def main():
 OUT.mkdir(exist_ok=True,parents=True)
 confirmation=dict(source='Saswat email text supplied directly by the user in this conversation on 2026-10-07',
  square_length_m=.025,marker_length_m=.018,marker_square_ratio=.72,squares_x=7,squares_y=10,dictionary='DICT_4X4_50',
  physical_size_previously_unknown=True,dimension_uncertainty_not_provided=True,
  exact_user_supplied_text='The printed ChArUco board uses a square size of 25 mm × 25 mm. The embedded ArUco markers are 18 mm × 18 mm, and the board layout is 7 × 10 squares using the DICT_4X4_50 dictionary. In the calibration code, these dimensions are recorded in metres: square length 0.025 m; marker length 0.018 m. The values 127/76 may refer to pixel measurements from an image rather than physical dimensions.')
 save(OUT/'board_confirmation.json',confirmation)
 original=json.loads((SRC/'corner_observations.json').read_text())['observations']
 model=json.loads((SRC/'calibration_experiment.json').read_text());K=np.array(model['factory_K']);dist=np.array(model['factory_distortion'])
 old_transfer=json.loads((ROOT/'generated/research_20260928_processing_20261007/calibration_transfer.json').read_text())
 metric=[];projection_errors=[];pose_deltas=[]
 for o in original:
  obj=np.asarray(o['object_points_board_squares'],float)*.025; img=np.asarray(o['image_points_pixels'],float)
  r=np.array(o['factory_pose_rotation_rvec'],float);t=np.array(o['factory_pose_translation_board_squares'],float)*.025
  oldp=cv2.projectPoints(obj,r,t,K,dist)[0].reshape(-1,2)
  ok,rr,tt=cv2.solvePnP(obj,img,K,dist,r.copy(),t.copy(),True,flags=cv2.SOLVEPNP_ITERATIVE)
  assert ok
  projected=cv2.projectPoints(obj,rr,tt,K,dist)[0].reshape(-1,2)
  delta=np.max(abs(projected-oldp)); assert delta<.002,delta
  projection_errors.extend(np.linalg.norm(projected-img,axis=1));pose_deltas.append(float(delta))
  metric.append(dict(frame=o['frame'],frame_id=o['frame_id'],sample_index=o['sample_index'],sheet=o['sheet'],image_sha256=o['image_sha256'],
   rvec=rr.reshape(-1).tolist(),tvec_m=tt.reshape(-1).tolist(),corners=len(obj),reprojection_px=stats(np.linalg.norm(projected-img,axis=1))))
 sheets=sorted({o['sheet'] for o in metric});pos=np.array([o['frame_id']/1e6 for o in metric]);centre=float(pos.mean())
 X=np.column_stack([np.array([o['sheet']==s for o in metric],float) for s in sheets]+[pos-centre]);Y=np.array([o['tvec_m'] for o in metric])
 b,res,w=robust(X,Y); motion=-b[-1]; factor=np.linalg.norm(motion);direction=motion/factor
 per=[];board_models=[]
 for si,s in enumerate(sheets):
  ids=np.array([i for i,o in enumerate(metric) if o['sheet']==s]);p=pos[ids];xx=np.column_stack([np.ones(len(ids)),p-p.mean()]);bb,rr,ww=robust(xx,Y[ids])
  f=np.linalg.norm(bb[-1]);per.append(dict(sheet=s,observations=len(ids),metres_per_previous_filename_unit=float(f),change_percent=float((f-1)*100),residual_m=stats(np.linalg.norm(rr,axis=1))))
  R=Rotation.from_rotvec(np.array([metric[i]['rvec'] for i in ids])).mean().as_matrix()
  t0=b[si]-b[-1]*centre
  board_models.append(dict(sheet=s,R_board_to_reference=R.tolist(),t_board_to_reference_m=t0.tolist(),reference='calibration camera at filename coordinate zero under fixed-mount shared-linear-motion fit',
   uncertainty='Approximate fit; small orientation variation, paper warp and mount/pose error are not removed. Not yet transferred to plant bundle reference.'))
 splits=[]
 for fold in range(4):
  held=np.array([o['sample_index']%4==fold for o in metric]);train=~held
  bb,_,_=robust(X[train],Y[train]);splits.append(dict(fold=fold,train_observations=int(train.sum()),held_observations=int(held.sum()),factor=float(np.linalg.norm(bb[-1])),held_pose_translation_residual_m=stats(np.linalg.norm(Y[held]-X[held]@bb,axis=1))))
 report=dict(status='metric_board_pose_and_gantry_scale_recomputed',dimension_source='board_confirmation.json',
  physical_square_m=.025,physical_marker_m=.018,marker_ratio=.72,corner_observations=len(metric),corners=sum(o['corners'] for o in metric),
  intrinsics_changed=False,selected_K=K.tolist(),selected_distortion=dist.tolist(),
  pose_method='Refit solvePnP with actual 25mm square object coordinates, original refined image corners and retained factory intrinsics.',
  calibration_reprojection_px=stats(projection_errors),max_reprojection_change_from_unit_square_pose_px=max(pose_deltas),
  metric_motion_vector_m_per_previous_filename_unit=motion.tolist(),metres_per_previous_filename_unit=float(factor),linear_length_change_percent=float((factor-1)*100),
  area_change_percent=float((factor**2-1)*100),volume_change_percent=float((factor**3-1)*100),
  motion_direction=direction.tolist(),old_motion_direction=old_transfer['positive_gantry_direction_camera_xyz'],
  angle_to_old_motion_deg=float(np.degrees(np.arccos(np.clip(direction@np.array(old_transfer['positive_gantry_direction_camera_xyz']),-1,1)))),
  joint_translation_residual_m=stats(np.linalg.norm(res,axis=1)),per_sheet=per,whole_frame_holdouts=splits,
  board_models=board_models,model='Shared linear camera motion with a separate intercept for each physical sheet, robust translation residual weighting.',
  method_boundary='Board pose/trajectory residuals are model consistency diagnostics. Print dimensions are supplied, not independently remeasured here; uncertainty unavailable. Same-rig transfer to the plant scan is user-confirmed but model-dependent.',
  old_filename_unit_interpretation='Previously frame_id/1e6 was treated as metres. Here its physical displacement is estimated from known-size board poses.',
  use_for_reconstruction='Establishes D405 RGB geometry scale. Do not apply this factor blindly to L515 sensor depth or fused geometry; evaluate sensor units and refit cross-camera registration separately.',
  no_new_surfaces=True,manual_traits_used=False,plant_reconstruction_updated=False,
  source_hashes={str(p.relative_to(ROOT)):sha(p) for p in [SRC/'corner_observations.json',SRC/'calibration_experiment.json',ROOT/'generated/research_20260928_processing_20261007/calibration_transfer.json',Path(__file__)]})
 save(OUT/'d405_metric_calibration.json',report);save(OUT/'d405_board_poses_metres.json',dict(coordinate_units='metres',observations=metric))
 print(json.dumps({k:report[k] for k in ['status','metres_per_previous_filename_unit','linear_length_change_percent','area_change_percent','angle_to_old_motion_deg','joint_translation_residual_m']}))
if __name__=='__main__':main()
