"""Known-size L515 board trajectory and depth audit; historical results untouched."""
from pathlib import Path
import hashlib, json
import cv2
import numpy as np

ROOT=Path.cwd()
OUT=ROOT/'generated/research_confirmed_board_20261007/l515'
OLD=ROOT/'generated/research_l515_20261007/calibration'
CAL=ROOT/'data/main/test_plant_10-7/test_plant_20260928144647_L515'

def read(p):return json.loads(Path(p).read_text())
def save(p,v):Path(p).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def stats(a):
 a=np.asarray(a);return dict(n=len(a),median=float(np.median(a)),rms=float(np.sqrt(np.mean(a*a))),p10=float(np.quantile(a,.1)),p90=float(np.quantile(a,.9)),min=float(a.min()),max=float(a.max()))
def errors(a):
 a=np.asarray(a);return dict(n=len(a),median_signed_m=float(np.median(a)),median_absolute_m=float(np.median(abs(a))),p90_absolute_m=float(np.quantile(abs(a),.9)),rms_m=float(np.sqrt(np.mean(a*a))))
def robust(X,Y):
 w=np.ones(len(X))
 for _ in range(15):
  b=np.linalg.lstsq(X*np.sqrt(w[:,None]),Y*np.sqrt(w[:,None]),rcond=None)[0]
  rr=np.linalg.norm(Y-X@b,axis=1);m=np.median(rr);mad=np.median(abs(rr-m))
  w=np.minimum(1,max(m+2.5*1.4826*mad,.000025)/np.maximum(rr,1e-12))
 return b,Y-X@b,w
def robust_scalar(x,y,kind):
 if kind=='native':return np.array([1.,0.])
 A={'offset':np.ones((len(x),1)),'scale':x[:,None],'affine':np.column_stack((x,np.ones(len(x))))}[kind]
 target=y-x if kind=='offset' else y;w=np.ones(len(x))
 for _ in range(12):
  b=np.linalg.lstsq(A*np.sqrt(w[:,None]),target*np.sqrt(w),rcond=None)[0]
  r=A@b-target;s=max(1.4826*np.median(abs(r-np.median(r))),.001)
  w=np.minimum(1,1.345*s/np.maximum(abs(r),1e-12))
 return np.array([1.,b[0]]) if kind=='offset' else np.array([b[0],0.]) if kind=='scale' else b

def main():
 OUT.mkdir(exist_ok=True,parents=True);cv2.setNumThreads(2)
 original=read(OLD/'corner_observations.json')['observations'];old=read(OLD/'calibration_transfer.json')
 K=np.array(old['K']);dist=np.array(old['dist']);sheet_names=sorted({o['sheet'] for o in original})
 poses=[];reproj=[];changes=[];depth=[];samples=[];source_files=[OLD/'corner_observations.json',OLD/'calibration_transfer.json',OLD/'depth_unit_diagnostics.json',OUT.parent/'board_confirmation.json',Path(__file__)]
 for o in original:
  obj=np.asarray(o['object_points_board_squares'],float)*.025;img=np.asarray(o['image_points_pixels'],float)
  r=np.asarray(o['factory_pose_rotation_rvec'],float);t=np.asarray(o['factory_pose_translation_board_squares'],float)*.025
  before=cv2.projectPoints(obj,r,t,K,dist)[0].reshape(-1,2)
  ok,rr,tt=cv2.solvePnP(obj,img,K,dist,r.copy(),t.copy(),True,flags=cv2.SOLVEPNP_ITERATIVE);assert ok
  after=cv2.projectPoints(obj,rr,tt,K,dist)[0].reshape(-1,2)
  delta=float(abs(after-before).max());assert delta<.002
  changes.append(delta);reproj.extend(np.linalg.norm(before-img,axis=1))
  # Scale-equivalent original PnP translations keep numerical optimizer jitter
  # separate from the physical-size update; the refit is a verification only.
  poses.append(dict(frame_id=o['frame_id'],sample_index=o['sample_index'],sheet=o['sheet'],rvec=r.tolist(),tvec_m=t.tolist(),refit_rvec=rr.reshape(-1).tolist(),refit_tvec_m=tt.reshape(-1).tolist(),max_refit_projection_change_px=delta,image_sha256=o['image_sha256']))
  path=CAL/f"depth_{o['frame_id']}.png";raw=cv2.imread(str(path),cv2.IMREAD_UNCHANGED);source_files.append(path)
  outline=np.float32([[.3,.3,0],[6.7,.3,0],[6.7,9.7,0],[.3,9.7,0]])*.025
  poly=cv2.projectPoints(outline,r,t,K,dist)[0].reshape(-1,2);mask=np.zeros(raw.shape,np.uint8)
  cv2.fillConvexPoly(mask,np.rint(poly).astype(int),1);mask=cv2.erode(mask,np.ones((5,5),np.uint8))>0
  yy,xx=np.nonzero(mask);valid=(raw[yy,xx]>0)&(raw[yy,xx]<65535);take=valid&((xx%2)==0)&((yy%2)==0)
  px=np.column_stack((xx[take],yy[take])).astype(float);rays=np.column_stack((cv2.undistortPoints(px[:,None],K,dist).reshape(-1,2),np.ones(len(px))))
  counts=raw[yy[take],xx[take]].astype(float);n=cv2.Rodrigues(r)[0][:,2];z=(n@t)/(rays@n);ratio=z/counts
  depth.append(dict(frame_id=o['frame_id'],sample_index=o['sample_index'],sheet=o['sheet'],depth_sha256=sha(path),sampled_pixels=len(counts),valid_fraction=float(valid.mean()),board_axial_Z_m=stats(z),raw_counts=stats(counts),effective_m_per_count=stats(ratio),native_sensor_minus_board_m=errors(counts*.00025-z)))
  samples.append(np.column_stack((np.full(len(counts),len(depth)-1),px,counts,z)))
 sheets=sheet_names;pos=np.array([o['frame_id']/1e6 for o in poses]);centre=float(pos.mean())
 X=np.column_stack([np.array([o['sheet']==s for o in poses],float) for s in sheets]+[pos-centre]);Y=np.array([o['tvec_m'] for o in poses])
 b,res,w=robust(X,Y);motion=-b[-1];factor=float(np.linalg.norm(motion));direction=motion/factor
 per=[]
 for s in sheets:
  ix=np.array([o['sheet']==s for o in poses]);p=pos[ix];xx=np.column_stack((np.ones(ix.sum()),p-p.mean()));bb,rr,ww=robust(xx,Y[ix]);sf=float(np.linalg.norm(bb[-1]))
  per.append(dict(sheet=s,observations=int(ix.sum()),metres_per_previous_filename_unit=sf,translation_residual_m=stats(np.linalg.norm(rr,axis=1))))
 folds=[]
 for f in range(4):
  held=np.array([o['sample_index']%4==f for o in poses]);fit,_,_=robust(X[~held],Y[~held]);folds.append(dict(fold=f,train_observations=int((~held).sum()),held_observations=int(held.sum()),factor=float(np.linalg.norm(fit[-1])),held_translation_residual_m=stats(np.linalg.norm(Y[held]-X[held]@fit,axis=1))))
 ratios=np.array([d['effective_m_per_count']['median'] for d in depth]);board_unit=float(np.median(ratios))
 unit_difference_percent=float((board_unit/.00025-1)*100)
 report=dict(status='known_25mm_board_metric_trajectory_and_depth_rechecked',physical_square_m=.025,physical_marker_m=.018,marker_square_ratio=.72,dictionary='DICT_4X4_50',grid_squares=[7,10],dimension_source='../board_confirmation.json',
  dimension_provenance='User supplied Saswat statement; actual printed dimensions reported, no measurement uncertainty supplied.',
  observations=len(poses),unique_frames=len({p['frame_id'] for p in poses}),corners=sum(len(o['corner_ids']) for o in original),
  K=K.tolist(),dist=dist.tolist(),intrinsics_changed=False,
  pose_method='Original refined intersections with 25mm square object coordinates. Original unit-square poses are metrically equivalent; solvePnP refits verify negligible pixel change.',
  calibration_reprojection_px=stats(reproj),max_refit_projection_change_px=max(changes),
  metres_per_previous_filename_unit=factor,linear_length_change_percent=(factor-1)*100,metric_motion_vector_m_per_previous_filename_unit=motion.tolist(),motion_direction=direction.tolist(),
  angle_to_old_direction_deg=float(np.degrees(np.arccos(np.clip(direction@np.array(old['positive_gantry_direction_camera_xyz']),-1,1)))),
  joint_translation_residual_m=stats(np.linalg.norm(res,axis=1)),per_sheet=per,whole_frame_holdouts=folds,
  recorded_sensor_depth_unit_m_per_count=None,retained_sensor_unit_candidate_m_per_count=.00025,
  actual_size_board_effective_depth_unit_m_per_count=board_unit,board_frame_unit_medians=stats(ratios),board_gain_over_retained_native_candidate=board_unit/.00025,board_gain_percent=unit_difference_percent,
  current_reconstruction_decision='Rerun raw L515 sensor-depth ICP/TSDF at unchanged .00025 m/count with RGB camera translations multiplied by this independently board-derived metric factor. Do not scale the old sensor cloud or mixed fusion.',
  depth_gain_decision='The actual-size board effective gain remains diagnostic: native sensor setting was not recorded and limited-depth board data cannot distinguish multiplicative unit error from axial bias, alignment or model error. No fitted gain/offset selected from the board.',
  reconstruction_thresholds='Retain physical .002 m voxel, .010 m truncation and .008 m support tolerance; recompute ICP/TSDF/support since trajectory and measured rays no longer share a global scale.',
  no_manual_traits_used=True,source_hashes={str(p.relative_to(ROOT)):sha(p) for p in sorted(set(source_files))},
  remaining_limits=['Supplied print dimensions lack tolerance or independent print-scale measurement.','Fixed factory model and aligned-depth interpretation remain assumptions.','Board observations have limited depth and plane-normal diversity.','Frame/landmark holdouts are correlated internal checks, not external physical truth.','New sensor reconstruction changes point identities; old cleanup/spectral vertex IDs cannot be transferred by index.'])
 save(OUT/'metric_calibration.json',report);save(OUT/'board_poses_metres.json',dict(observations=poses,units='metres'))
 save(OUT/'board_depth_diagnostics.json',dict(unit_candidate=.00025,board_gain_diagnostic_only=board_unit/.00025,observations=depth,median_of_frame_unit_medians=board_unit))
 np.savez_compressed(OUT/'board_depth_samples.npz',samples=np.concatenate(samples),columns=np.array(['observation_index','native_x','native_y','raw_count','board_axial_Z_m']))
 # Independent-of-board plant-scan RGB depth audit. Freeze the original cohort,
 # IDs and heldout folds; rescale RGB depths/translation, leave raw counts alone.
 lp=OLD/'landmark_depth_check/landmark_samples.npz';a=np.load(lp);tracks=a['landmarks'];x=tracks[:,4]*.00025;y=tracks[:,3]*factor;models={}
 for kind in ['native','board_gain','offset','scale','affine']:
  coef=np.array([board_unit/.00025,0.]) if kind=='board_gain' else robust_scalar(x,y,kind)
  held=np.zeros(len(x));ff=[]
  for f in range(5):
   test=tracks[:,0].astype(int)%5==f;fit=coef if kind in ['native','board_gain'] else robust_scalar(x[~test],y[~test],kind)
   held[test]=x[test]*fit[0]+fit[1]-y[test];ff.append(dict(fold=f,gain=float(fit[0]),offset_m=float(fit[1]),held=errors(held[test])))
  models[kind]=dict(gain=float(coef[0]),offset_m=float(coef[1]),equivalent_unit_m_per_count=float(coef[0]*.00025),all=errors(x*coef[0]+coef[1]-y),heldout=errors(held),folds=ff)
 bins=[]
 for lo,hi in zip([.2,.4,.6,.8,1.,1.3],[.4,.6,.8,1.,1.3,1.7]):
  q=(y>=lo)&(y<hi)
  if q.any():bins.append(dict(metric_RGB_interval_m=[lo,hi],landmarks=int(q.sum()),native=errors(x[q]-y[q]),board_gain=errors(x[q]*board_unit/.00025-y[q])))
 diag=dict(status='diagnostic_only_no_gain_or_offset_applied',native_unit=.00025,RGB_metric_scale_factor=factor,cohort='Same 3733 distinct smooth multi-view landmarks and original ID folds. Gates frozen before sensor-vs-RGB residuals; no newly selected points.',
  models=models,depth_strata=bins,source_hashes={str(lp.relative_to(ROOT)):sha(lp),str((OLD/'landmark_depth_check/landmark_depth_review.json').relative_to(ROOT)):sha(OLD/'landmark_depth_check/landmark_depth_review.json')},
  physical_accuracy=False,limits=['RGB landmark depths use this board-derived motion scale; no plant trait dimensions were used.','This plant scan is distinct from calibration board images, but camera intrinsics and geometry assumptions are shared.','Smooth broad surfaces dominate; no thin-leaf or nearest-range accuracy guarantee.','All tails retained; ID folds share images and are not independent trials.'])
 save(OUT/'metric_landmark_depth_diagnostics.json',diag)
 print(json.dumps({'factor':factor,'direction':direction.tolist(),'board_effective_unit':board_unit,'board_gain_percent':unit_difference_percent,'landmark_models':{k:v['heldout'] for k,v in models.items()}},indent=2),flush=True)

if __name__=='__main__':main()
