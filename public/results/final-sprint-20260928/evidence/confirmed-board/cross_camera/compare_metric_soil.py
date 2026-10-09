"""Re-evaluate the exact frozen soil keypoints for both metric L515 variants."""
from pathlib import Path
import hashlib,json
import cv2,numpy as np

ROOT=Path.cwd();BASE=ROOT/'generated/research_confirmed_board_20261007';OUT=BASE/'cross_camera'
OLD=ROOT/'generated/research_l515_20261007/cross_camera/near_static_holdouts'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def stats(v):
 v=np.asarray(v);return dict(count=len(v),median_mm=float(np.median(v)*1000),p90_mm=float(np.quantile(v,.9)*1000),p95_mm=float(np.quantile(v,.95)*1000),max_mm=float(v.max()*1000),rms_mm=float(np.sqrt(np.mean(v*v))*1000),within_3mm=int((v<=.003).sum()),within_5mm=int((v<=.005).sum()),within_10mm=int((v<=.010).sum()))
def main():
 previous=read(OLD/'near_sensor_alignment_comparison.json');matches=read(OLD/'near_static_correspondences.json')
 oldrows=previous['rows'];assert len(oldrows)==65 and sum(r['quality_cohort'] for r in oldrows)==62
 dscale=read(BASE/'d405_metric_calibration.json')['metres_per_previous_filename_unit'];seed=np.array(read(OUT/'board_seed.json')['T_D405_reference_from_L515_reference'])
 bymatch={(f['frame'],m['point_id']):m for f in matches['frames'] for m in f['matches']}
 outputs={};sources=[OLD/'near_sensor_alignment_comparison.json',OLD/'near_static_correspondences.json',BASE/'d405_metric_calibration.json',OUT/'board_seed.json',Path(__file__)]
 for variant,runname in [('native','l515_metric_v1'),('boardgain','l515_metric_boardgain_v1')]:
  run=BASE/runname;alignment=read(OUT/variant/'alignment.json');cfg=read(run/'profile.json');icp={r['frame']:np.array(r['transform']) for r in read(run/'result/icp_diagnostics.json') if r['integrated']};poses={r['frame']:r for r in read(run/'bundle/poses.json')['frames']}
  K=np.array(cfg['K']);unit=cfg['sensor_unit_m'];T=np.array(alignment['T_D405_reference_from_L515_reference']);raws={};rows=[]
  sources.extend([OUT/variant/'alignment.json',run/'profile.json',run/'result/icp_diagnostics.json',run/'bundle/poses.json'])
  for old in oldrows:
   frame=old['frame'];pid=old['point_id'];m=bymatch[(frame,pid)];u=np.array(m['L515_uv_undistorted']);ray=np.r_[(u-[K[0,2],K[1,2]])/[K[0,0],K[1,1]],1.]
   assert np.max(abs(ray-np.array(old['L515_ray_colour_camera'])))<1e-14
   if frame not in raws:
    p=Path(poses[frame]['depth']);raws[frame]=cv2.imread(str(p),cv2.IMREAD_UNCHANGED);sources.append(p)
   raw=raws[frame];x,y=np.rint(old['L515_uv_native']).astype(int);patch=raw[y-2:y+3,x-2:x+3];vv=patch[patch>0];centre=int(raw[y,x]);median=float(np.median(vv)) if len(vv) else None
   assert centre==old['depth_centre_count'];assert median==old['depth_5x5_median_count'];assert len(vv)==old['patch_valid_count'];assert (len(vv)>=20 and centre>0)==old['quality_cohort']
   target=np.array(old['D405_landmark'])*dscale
   assert np.allclose(np.array(m['D405_point_reference'])*dscale,target,atol=1e-14)
   r=dict(frame=frame,point_id=pid,specimen=old['specimen'],quality_cohort=old['quality_cohort'],L515_uv_native=old['L515_uv_native'],L515_ray=ray.tolist(),D405_metric_target=target.tolist(),depth_centre_count=centre,depth_5x5_median_count=median,patch_valid_count=len(vv),methods={})
   for method,R in [('board_seed',seed),('pot_rigid',T)]:
    pose=R@icp[frame];entry={}
    for name,count in [('centre',centre),('median5x5',median)]:
     if count:
      point=pose[:3,:3]@(ray*count*unit)+pose[:3,3];res=point-target;entry[name]=dict(point_D405_reference=point.tolist(),residual_xyz_m=res.tolist(),distance_m=float(np.linalg.norm(res)))
     else:entry[name]=None
    r['methods'][method]=entry
   rows.append(r)
  aggregate={method:{name:stats([r['methods'][method][name]['distance_m'] for r in rows if r['quality_cohort']]) for name in ['centre','median5x5']} for method in ['board_seed','pot_rigid']}
  per={p:{method:stats([r['methods'][method]['median5x5']['distance_m'] for r in rows if r['quality_cohort'] and r['specimen']==p]) for method in ['board_seed','pot_rigid']} for p in ['P2','P4']}
  outputs[variant]=dict(sensor_conversion_m_per_count=unit,source_points=read(run/'result/summary.json')['points'],surface_status=alignment['status'],surface_gates=alignment['acceptance_checks'],aggregate=aggregate,per_specimen=per,rows=rows)
 report=dict(status='frozen_soil_cohort_recomputed_for_metric_camera_candidates',original_matches=65,fixed_quality_cohort=62,unique_D405_landmark_ids=len({r['point_id'] for r in oldrows}),
  cohort_identical=True,raw_patch_counts_identical=True,new_correspondences_added=False,manual_trait_values_used=False,
  D405_target_method='Exact original pre-ICP RGB-bundle physical-keypoint landmark multiplied by confirmed-board D405 factor; no nearest-cloud substitution.',D405_metric_factor=dscale,
  L515_method='Exact original native source pixel/ray and raw depth centre or5x5median; use new final sensor ICP poses and per-variant conversion.',
  fitting_exclusion='P2/P4 soil point identities and source pixels were withheld from pot rigid fitting. These diagnostics are now used to select among variants and thus are not a final untouched test set.',
  variants=outputs,source_hashes={str(p.relative_to(ROOT)):sha(p) for p in sorted(set(sources))},
  limits=['Correspondences share factory camera models, scale transfer and source images; not independent physical ground truth.','Repeat observations of soil features are correlated.','Surface proximity metrics are separate from these physical-keypoint distances.','The new board-gain conversion is an empirical correction; original device unit was not saved.','Tails and all original quality-passing correspondences are retained.'])
 (OUT/'matched_soil_metric_comparison.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
 print(json.dumps({k:dict(surface_status=v['surface_status'],soil=v['aggregate'],per_specimen=v['per_specimen']) for k,v in outputs.items()},indent=2))
if __name__=='__main__':main()
