from pathlib import Path
import json,numpy as np,cv2,hashlib
from scipy.spatial import Delaunay
R=Path.cwd();O=Path(__file__).resolve().parent;L=R/'generated/research_fusion_rescue_20261008/learned_registration';P=R/'generated/research_fusion_rescue_20261008/physical_model';load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
initial=load(O/'reserved_evaluation_private.json');extra=load(O/'supplemental_reserved_landmarks_private.json')
for a in initial:a['region']='red_upper' if a['id'].startswith('reserved_red') else 'green_lower'
rows=initial+extra;models=load(L/'frozen_candidates.json');out=[]
for m in models['candidates']:
 path=L/m['map_npz'];a=np.load(path);mp=a['rgb_xy'];ori=a['hsi_origin'];hull=Delaunay(np.array(m['training_source']));rec=[]
 for r in rows:
  if r['region']!=m['region']:continue
  q=np.array(r['hsi_rotated_xy'],float);z=q-ori;indomain=bool(hull.find_simplex(q)>=0);gridinside=bool(0<=z[0]<mp.shape[1]-1 and 0<=z[1]<mp.shape[0]-1);pred=None
  if gridinside:
   v=mp[int(z[1]),int(z[0])] if np.allclose(z,np.rint(z)) else cv2.remap(mp,np.array([[z[0]]],np.float32),np.array([[z[1]]],np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=float('nan'))[0,0]
   if np.isfinite(v).all():pred=v
  H=np.array(m['H']);hp=H@np.r_[q,1];globalv=hp[:2]/hp[2]
  rec.append(dict(id=r['id'],confidence=r['confidence'],inside_learned_inlier_hull=indomain,map_sample_supported=pred is not None,prediction_native_RGB_xy=pred.tolist() if pred is not None else None,error_RGB_px=float(np.linalg.norm(pred-r['native_RGB_xy'])) if pred is not None else None,global_only_extrapolation_error_RGB_px=float(np.linalg.norm(globalv-r['native_RGB_xy'])) if not indomain else None,extrapolation_does_not_validate_interpolation=not indomain,HSI_localization_radius_px=r['hsi_uncertainty_radius_px'],RGB_localization_radius_px=r['RGB_uncertainty_radius_px'],eligible_for_strict_accuracy_gate=False))
 out.append(dict(id=m['id'],region=m['region'],map_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),checks=rec))
report=dict(model_freeze_sha256=hashlib.sha256((L/'frozen_candidates.json').read_bytes()).hexdigest(),policy='All frozen variants scored. Missing predictions outside convex hull are out of domain, not failed interpolation. These manually proposed controls are independent of model fitting but not independently verified physical landmark truth.',results=out)
(O/'blind_learned_evaluation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
for m in out:print(m['id'],[(r['id'],r['inside_learned_inlier_hull'],r['error_RGB_px'],r['global_only_extrapolation_error_RGB_px']) for r in m['checks']])
phy=load(P/'frozen_candidates.json');pp=[]
for m in phy['models']:
 c=m['coordinates'];T=np.array(c['T_plant_reference_from_calibration']);origin=np.array(c['origin_calibration_reference_m']);basis=np.array(c['basis_columns']);tr=np.array(c['scan_002_to_003_column_line_translation']);ay,ah,a0,by,bh,lx,ly,lh,l0=m['parameters'];rec=[]
 for r in initial:
  fields={}
  for field in ['depth_lift_reference_xyz_m','reference_xyz_m']:
   xyz=(np.array(r[field])-T[:3,3])@T[:3,:3];x,y,z=(xyz-origin)@basis;uv=np.array([(ay*y+ah*z+a0)/(1+by*y+bh*z),lx*x+ly*y+lh*z+l0])+tr;fields[field]=dict(predicted_column_line=uv.tolist(),residual_column_line=(uv-r['native_hsi_column_line']).tolist(),error_HSI_px=float(np.linalg.norm(uv-r['native_hsi_column_line'])))
  rec.append(dict(id=r['id'],confidence=r['confidence'],preferred_3D_field=m['input_3d_field_for_new_controls'],depth_vs_vertex_prediction_displacement_HSI_px=float(np.linalg.norm(np.array(fields['reference_xyz_m']['predicted_column_line'])-fields['depth_lift_reference_xyz_m']['predicted_column_line'])),localization_sensitivity=fields,eligible_for_strict_accuracy_gate=False))
 pp.append(dict(id=m['id'],primary_candidate=m['primary_candidate'],checks=rec))
(O/'blind_physical_evaluation_private.json').write_text(json.dumps(dict(model_freeze_sha256=hashlib.sha256((P/'frozen_candidates.json').read_bytes()).hexdigest(),results=pp),indent=2)+'\n',encoding='utf-8')
print('physical',[(m['id'],[(r['id'],r['localization_sensitivity'][r['preferred_3D_field']]['error_HSI_px']) for r in m['checks']]) for m in pp])

