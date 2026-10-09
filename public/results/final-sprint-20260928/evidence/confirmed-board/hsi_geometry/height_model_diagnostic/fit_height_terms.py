"""Three existing P5 features: conditional model diagnostic, never dense fusion."""
from pathlib import Path
import hashlib,json
import numpy as np
HERE=Path(__file__).resolve().parent;BASE=HERE.parents[1];ROOT=BASE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 paths={'plane':HERE.parent/'shared_plane_calibration.json','transfer':HERE.parent/'scan_transfer_v1/scan_transfer.json','bridge':HERE.parent/'rgb_bridge_review/independent_review.json','metric':BASE/'d405_metric_calibration.json','associations':ROOT/'generated/research_spectral_extension_20261007/result/associations.json'}
 d={k:json.loads(p.read_text()) for k,p in paths.items()};s=d['metric']['metres_per_previous_filename_unit'];T=np.array(d['bridge']['T_plant_reference_from_calibration_zero']);origin=np.array(d['plane']['plane_origin_reference_m']);basis=np.array(d['plane']['plane_basis_columns_reference']);normal=np.array(d['plane']['plane_normal_reference']);rows=d['associations']['associations']
 def plane_coordinates(points,T=T):
  # T maps calibration->plant; inverse for existing plant points.
  cal=(points-T[:3,3])@T[:3,:3];return np.column_stack([(cal-origin)@basis,(cal-origin)@normal])
 def fit_and_predict(xyz,uv,params,train):
  xy=xyz[:,:2];h=xyz[:,2];v=np.column_stack([xy,np.ones(len(xy))]);N=v@np.array(params['column_numerator_XY1']);D=1+xy@np.array(params['column_denominator_XY_plus_one']);L=v@np.array(params['line_XY1'])
  k=float(np.linalg.lstsq(h[train,None],(uv[:,1]-L)[train],rcond=None)[0][0])
  A=np.column_stack([h,-uv[:,0]*h]);target=uv[:,0]*D-N
  ab=np.linalg.lstsq(A[train],target[train],rcond=None)[0];den=D+ab[1]*h
  pred=np.column_stack([(N+ab[0]*h)/den,L+k*h]);sv=np.linalg.svd(A[train]/np.linalg.norm(A[train],axis=0),compute_uv=False)
  return pred,{'line_height_coefficient_px_per_m':k,'column_numerator_height_coefficient_px_per_m':float(ab[0]),'column_denominator_height_coefficient_per_m':float(ab[1]),'column_height_fit_normalized_singular_values':sv.tolist(),'column_height_fit_normalized_condition_number':float(sv[0]/sv[-1]),'rank':int(np.linalg.matrix_rank(A[train])),'denominator_at_three_points':den.tolist(),'input_height_m':h.tolist(),'input_cross_plane_xy_m':xy.tolist()}
 result={'status':'three_P5_control_conditional_height_model_diagnostic_not_accepted_camera_calibration','equations':{'signed_h':'normal dot (calibration_xyz-plane_origin); negative toward camera above table','line':'L_plane(X,Y)+k*h','column':'(N_plane(X,Y)+a*h)/(D_plane(X,Y)+b*h)','unknowns':['k','a','b']},'source_3D_coordinates':'Existing independently localized D405 RGB feature positions multiplied by confirmed scale factor, then inverse provisional RGB paper bridge. Not remapped cleanup vertices or independently surveyed control locations.','heldout_policy':'For each fold, exactly two existing P5 feature correspondences estimate the three height terms; the third observation is used only to score the prediction. Planar coefficients remain fixed. No spectral values are assigned by this model.','parameter_count':3,'per_sensor':{},'source_hashes':{str(p.relative_to(ROOT)):sha(p) for p in [*paths.values(),Path(__file__)]},'limitations':['Three points on one plant do not establish a general 3D camera model.','Column terms are exactly solvable from two distinct columns and nonzero heights; exact training fit is algebraic, not validation.','The two red controls have very similar heights and nearby columns, making extrapolation to green potentially unstable.','The RGB frame bridge uses a narrow paper strip and has material fold variation; it is approximate.','Source correspondence centroids and D405 depth localization have no independent physical ground truth.','Perturbations are explicit sensitivity scenarios, not calibrated confidence intervals.','FX17 correspondences were composed through FX10 and are not independent validation of the FX10 material identities.','No dense surface propagation, occlusion interpretation, plant-health score or calibrated reflectance is produced.']}
 for camera in ['fx10','fx17']:
  controls=[r for r in rows if r['sensor_id']==camera];P=np.array([r['localized_reference_xyz'] for r in controls])*s;uv3=np.array([r['native_hsi_subpixel_column_line'] for r in controls]);translation=np.array(d['transfer']['per_sensor'][camera]['translation_column_line_px']);uv=uv3-translation;xyz=plane_coordinates(P)
  model=next(m for m in d['plane']['per_sensor'][camera]['best_models'] if m['model']=='pushbroom_plane');params=model['fit'];folds=[]
  for held in range(3):
   train=np.arange(3)!=held;pred,fit=fit_and_predict(xyz,uv,params,train);error=pred[held]-uv[held]
   scenarios=[]
   # Bridge leave-frame-out scenarios: all retain untouched held spectral observation.
   for b in d['bridge']['leave_frame_out']:
    pred_b,fit_b=fit_and_predict(plane_coordinates(P,np.array(b['T_plant_reference_from_calibration_zero'])),uv,params,train)
    scenarios.append({'kind':'RGB_bridge_leave_frame_out','held_RGB_frame':b['held_frame'],'prediction_003_column_line':(pred_b[held]+translation).tolist(),'change_from_baseline_px':float(np.linalg.norm(pred_b[held]-pred[held])),'held_error_px':float(np.linalg.norm(pred_b[held]-uv[held]))})
   for b in model['leave_one_sheet_out']:
    pred_b,fit_b=fit_and_predict(xyz,uv,b['fit'],train)
    scenarios.append({'kind':'calibration_plane_leave_sheet_out','held_sheet':b['held_sheet'],'prediction_003_column_line':(pred_b[held]+translation).tolist(),'change_from_baseline_px':float(np.linalg.norm(pred_b[held]-pred[held])),'held_error_px':float(np.linalg.norm(pred_b[held]-uv[held]))})
   for control in range(3):
    for axis in range(3):
     for sign in [-1,1]:
      pert=P.copy();pert[control,axis]+=sign*.001;pred_b,fit_b=fit_and_predict(plane_coordinates(pert),uv,params,train)
      scenarios.append({'kind':'single_coordinate_1mm_stress','control':controls[control]['id'],'axis':axis,'sign':sign,'prediction_003_column_line':(pred_b[held]+translation).tolist(),'change_from_baseline_px':float(np.linalg.norm(pred_b[held]-pred[held])),'held_error_px':float(np.linalg.norm(pred_b[held]-uv[held]))})
   for control in np.flatnonzero(train):
    for axis in range(2):
     for sign in [-1,1]:
      pert=uv.copy();pert[control,axis]+=sign;pred_b,fit_b=fit_and_predict(xyz,pert,params,train)
      scenarios.append({'kind':'training_correspondence_1px_stress','control':controls[control]['id'],'axis':axis,'sign':sign,'prediction_003_column_line':(pred_b[held]+translation).tolist(),'change_from_baseline_px':float(np.linalg.norm(pred_b[held]-pred[held])),'held_error_px':float(np.linalg.norm(pred_b[held]-uv[held]))})
   folds.append({'held_out_id':controls[held]['id'],'training_ids':[controls[i]['id'] for i in np.flatnonzero(train)],'observed_003_column_line':uv3[held].tolist(),'predicted_003_column_line':(pred[held]+translation).tolist(),'held_out_residual_column_line':error.tolist(),'held_out_vector_error_px':float(np.linalg.norm(error)),'training_residuals_column_line':(pred[train]-uv[train]).tolist(),'fit':fit,'sensitivity_scenarios':scenarios,'max_prediction_shift_by_scenario':{k:max(r['change_from_baseline_px'] for r in scenarios if r['kind']==k) for k in sorted({r['kind'] for r in scenarios})}})
  predall,fitall=fit_and_predict(xyz,uv,params,np.ones(3,bool));result['per_sensor'][camera]={'controls':[{'id':r['id'],'original_D405_localization':r['localized_reference_xyz'],'metric_plant_xyz':P[i].tolist(),'plane_XYh':xyz[i].tolist(),'source_003_column_line':uv3[i].tolist()} for i,r in enumerate(controls)],'folds':folds,'all_three_fit_for_diagnostics_only':{'fit':fitall,'residual_column_line':(predall-uv).tolist()},'worst_held_out_error_px':max(f['held_out_vector_error_px'] for f in folds)}
 (HERE/'height_diagnostic.json').write_text(json.dumps(result,indent=2)+'\n')
 summary={c:{'worst_held_out_error_px':v['worst_held_out_error_px'],'folds':[{'held_id':f['held_out_id'],'error_px':f['held_out_vector_error_px'],'condition':f['fit']['column_height_fit_normalized_condition_number'],'max_sensitivity':f['max_prediction_shift_by_scenario']} for f in v['folds']]} for c,v in result['per_sensor'].items()}
 (HERE/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
