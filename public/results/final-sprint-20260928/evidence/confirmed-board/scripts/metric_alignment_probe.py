"""Rigid scene alignment after board-anchored scale correction.

Inherited pot-region policy is frozen before fitting. New TSDF vertices have
new identities; the semantic split is preserved, not falsely old vertex IDs.
"""
from pathlib import Path
import argparse,importlib.util,json,hashlib
import numpy as np
import open3d as o3d
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[1]
OLD=ROOT/'generated/research_l515_20261007/cross_camera/pot_rigid_probe'
spec=importlib.util.spec_from_file_location('original_rigid_probe',OLD/'run_probe.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def save(p,v):p.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def main(variant):
 lroot=BASE/('l515_metric_v1' if variant=='native' else 'l515_metric_boardgain_v1')
 out=BASE/'cross_camera'/variant;out.mkdir(parents=True,exist_ok=True)
 assert not (out/'alignment.json').exists(),'Preserve completed alignment'
 D=BASE/'d405_metric/full_scene_reference.ply';L=lroot/'result/l515_supported_reference.ply'
 assert D.exists() and L.exists()
 scale=json.loads((BASE/'d405_metric_calibration.json').read_text())['metres_per_previous_filename_unit']
 R=np.array(json.loads((ROOT/'generated/research_20260928_processing_20261007/calibration_transfer.json').read_text())['upright_export_R_reference_camera_to_xyz_z_up'])
 U=np.eye(4);U[:3,:3]=R;seed=json.loads((BASE/'cross_camera/board_seed.json').read_text());T=np.array(seed['T_D405_reference_from_L515_reference'])
 limits=np.array([[0,-.4,-.78],[1.8,.4,-.1]])*scale
 arrays=[]
 for path,M in [(D,U),(L,U@T)]:
  v=m.ply(path);p=np.column_stack([v[k] for k in ['x','y','z']]);p=m.transform(p,M);mask=np.all((p>=limits[0])&(p<=limits[1]),axis=1)
  arrays.append((p[mask],np.flatnonzero(mask)))
 d,di=arrays[0];l,li=arrays[1]
 boxes=np.array(m.POT_BOXES)*scale;zlim=np.array([-.78,-.695])*scale
 def labels(p):
  lab=np.full(len(p),-1,np.int8)
  for i,(x0,x1,y0,y1) in enumerate(boxes):lab[(p[:,0]>=x0)&(p[:,0]<=x1)&(p[:,1]>=y0)&(p[:,1]<=y1)&(p[:,2]>=zlim[0])&(p[:,2]<=zlim[1])]=i
  return lab
 dl=labels(d);ll=labels(l);seeds=np.array(json.loads((OLD/'inputs.json').read_text())['seed_upright_xyz'])*scale
 results={}
 for name,train in [('odd',[0,2,4]),('even_stability',[1,3])]:
  delta,fit=m.fit(d[np.isin(dl,train)],l[np.isin(ll,train)]);info=m.parameter_info(delta,seeds)
  results[name]=dict(delta=delta.tolist(),fit=fit,parameters=info)
 delta=np.array(results['odd']['delta']);reverse=np.array(results['even_stability']['delta']);candidate=np.linalg.inv(U)@delta@U@T
 regions={f'P{i+1}':(dl==i,ll==i) for i in range(5)};regions['heldout_P2_P4']=(np.isin(dl,[1,3]),np.isin(ll,[1,3]));regions['all_foliage_heldout']=(d[:,2]>-.68*scale,l[:,2]>-.68*scale)
 metrics={}
 for name,(a,b) in regions.items():
  assert a.any() and b.any(),name
  metrics[name]=dict(before=m.bidirectional(d[a],l[b],np.eye(4)),after=m.bidirectional(d[a],l[b],delta),reverse_stability=m.bidirectional(d[a],l[b],reverse))
  print(variant,name,metrics[name]['after']['equal_direction_mean_median_mm'],flush=True)
 q=metrics['heldout_P2_P4'];f=metrics['all_foliage_heldout'];info=results['odd']['parameters']
 gates=dict(rotation_bounded=info['rotation_degrees']<=.75,seed_movement_bounded=info['max_seed_movement_mm']<=25,translation_bounded=info['translation_norm_mm']<=30,
  heldout_median_improves_10pct=q['after']['equal_direction_mean_median_mm']<=.9*q['before']['equal_direction_mean_median_mm'],
  heldout_p90_not_worse_10pct=q['after']['equal_direction_mean_p90_mm']<=1.1*q['before']['equal_direction_mean_p90_mm'],
  foliage_median_not_worse_10pct=f['after']['equal_direction_mean_median_mm']<=1.1*f['before']['equal_direction_mean_median_mm'],
  foliage_p90_not_worse_10pct=f['after']['equal_direction_mean_p90_mm']<=1.1*f['before']['equal_direction_mean_p90_mm'])
 for plant in ['P2','P4']:
  p=metrics[plant];gates[plant+'_median_not_worse_10pct']=p['after']['equal_direction_mean_median_mm']<=1.1*p['before']['equal_direction_mean_median_mm']
 np.savez_compressed(out/'memberships.npz',D405_source_indices=di,L515_source_indices=li,D405_pot_labels=dl,L515_pot_labels=ll)
 report=dict(status='passes_surface_gates_pending_fixed_soil_feature_check' if all(gates.values()) else 'fails_predeclared_surface_gates',variant=variant,
  T_D405_reference_from_L515_reference=candidate.tolist(),board_seed=T.tolist(),acceptance_checks=gates,results=results,metrics=metrics,
  region_policy=dict(source=str(OLD/'frozen_parameters.json'),old_boxes_scaled_by_board_factor=scale,pot_boxes=boxes.tolist(),pot_z=zlim.tolist(),train=['P1','P3','P5'],holdout=['P2','P4','all foliage'],memberships_frozen_before_fit=True,old_vertex_ids_reused=False),
  board_square_m=.025,rigid_only=True,scale_fitted_to_plants=False,manual_traits_used=False,
  limits=['Nearest-surface agreement is not point correspondence or physical accuracy.','This alignment is empirical for these scans, not a certified rigid sensor extrinsic.','The board-gain trial is an empirical range correction, not confirmation of the saved device depth unit.','Fixed matched-soil source feature validation remains required before selecting a fusion.'],
  source_hashes={str(p.relative_to(ROOT)):m.sha(p) for p in [D,L,BASE/'cross_camera/board_seed.json',BASE/'d405_metric_calibration.json',OLD/'run_probe.py',Path(__file__)]})
 save(out/'alignment.json',report);print(json.dumps(dict(variant=variant,status=report['status'],gates=gates)))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('variant',choices=['native','boardgain']);main(p.parse_args().variant)
