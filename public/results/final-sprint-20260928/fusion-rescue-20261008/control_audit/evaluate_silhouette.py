from pathlib import Path
import json,numpy as np,hashlib
O=Path(__file__).resolve().parent;P=O.parent/'physical_model';load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));ph=load(P/'frozen_silhouette_candidates_v2.json');print(ph.keys());models=ph.get('models',ph.get('candidates'));rows=load(O/'reserved_evaluation_private.json');out=[]
for m in models:
 c=m['coordinates'];T=np.array(c['T_plant_reference_from_calibration']);origin=np.array(c['origin_calibration_reference_m']);basis=np.array(c['basis_columns']);tr=np.array(c['scan_002_to_003_column_line_translation']);ay,ah,a0,by,bh,lx,ly,lh,l0=m['parameters'];rec=[]
 for r in rows:
  fields={}
  for field in ['depth_lift_reference_xyz_m','reference_xyz_m']:
   xyz=(np.array(r[field])-T[:3,3])@T[:3,:3];x,y,z=(xyz-origin)@basis;uv=np.array([(ay*y+ah*z+a0)/(1+by*y+bh*z),lx*x+ly*y+lh*z+l0])+tr;fields[field]=dict(predicted_column_line=uv.tolist(),error_HSI_px=float(np.linalg.norm(uv-r['native_hsi_column_line'])))
  rec.append(dict(id=r['id'],confidence=r['confidence'],preferred_3D_field=m['input_3d_field_for_new_controls'],localization_sensitivity=fields,eligible_for_strict_accuracy_gate=False))
 out.append(dict(id=m['id'],primary_candidate=m.get('primary_candidate',False),checks=rec));print(m['id'],[(r['id'],round(r['localization_sensitivity'][r['preferred_3D_field']]['error_HSI_px'],3)) for r in rec])
(O/'blind_silhouette_v2_evaluation.json').write_text(json.dumps(dict(model_freeze_sha256=hashlib.sha256((P/'frozen_silhouette_candidates_v2.json').read_bytes()).hexdigest(),results=out),indent=2)+'\n',encoding='utf-8')
