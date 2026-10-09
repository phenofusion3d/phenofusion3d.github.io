"""Prepare and run an isolated L515 reconstruction using the known-board scale and board-only empirical depth gain."""
from pathlib import Path
import hashlib, importlib.util, json, shutil
from types import SimpleNamespace
import numpy as np

ROOT=Path.cwd()
BASE=ROOT/'generated/research_l515_20261007/l515_sensor_v1'
CAL=ROOT/'generated/research_confirmed_board_20261007/l515/metric_calibration.json'
OUT=ROOT/'generated/research_confirmed_board_20261007/l515_metric_boardgain_v1'
SCRIPT=ROOT/'generated/research_l515_20261007/reconstruct_sensor.py'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def save(p,v):Path(p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')

def main():
 if (OUT/'result/summary.json').exists():raise ValueError('Completed new reconstruction already exists; preserved.')
 OUT.mkdir(exist_ok=True,parents=True);(OUT/'bundle').mkdir(exist_ok=True)
 metric=read(CAL);scale=metric['metres_per_previous_filename_unit'];sensor_unit=metric['actual_size_board_effective_depth_unit_m_per_count']
 assert abs(scale-1.0296675588864626)<1e-10
 cfg=read(BASE/'profile.json');poses=read(BASE/'bundle/poses.json')
 for row in poses['frames']:
  T=np.array(row['transform'],float);T[:3,3]*=scale;row['transform']=T.tolist()
 poses['metric_reexpression']=dict(scale=scale,scale_source=str(CAL),scale_sha256=sha(CAL),rotations_changed=False,translation_scaled=True,new_RGB_bundle_optimization=False,projection_equivalence='Scaling all RGB points and camera translations equally leaves RGB reprojections unchanged. Raw sensor depth receives the independent board-only empirical conversion; not a confirmed recorded device unit.')
 save(OUT/'bundle/poses.json',poses)
 lm=np.load(BASE/'bundle/landmarks.npz');updated={k:lm[k].copy() for k in lm.files};updated['points']*=scale
 np.savez_compressed(OUT/'bundle/landmarks.npz',**updated)
 frozen=read(BASE/'calibration_frozen.json');frozen.update(confirmed_physical_square_mm=25.,physical_marker_mm=18.,actual_marker_square_ratio=.72,metres_per_previous_filename_unit=scale,metric_calibration_source=str(CAL),metric_calibration_sha256=sha(CAL),candidate_depth_metres_per_count_for_reconstruction=sensor_unit,status='known_board_metric_RGB_trajectory_empirical_board_depth_gain_trial_not_device_unit_confirmation')
 save(OUT/'calibration_frozen.json',frozen)
 shutil.copyfile(BASE/'native_keep_mask.png',OUT/'native_keep_mask.png')
 cfg['calibration']=str(OUT/'calibration_frozen.json');cfg['calibration_sha256']=sha(OUT/'calibration_frozen.json');cfg['native_feature_keep_mask']=str(OUT/'native_keep_mask.png')
 cfg['metric_scale_status']='RGB trajectory anchored to supplied 25mm printed squares; board-derived effective depth conversion; empirical correction, not recorded device setting'
 cfg['sensor_unit_m']=sensor_unit;cfg['depth_scale']=1/sensor_unit;cfg['voxel']=.002;cfg['trunc']=.010;cfg['tolerance']=.008
 for row in cfg['frames']:
  T=np.array(row['transform'],float);T[:3,3]*=scale;row['transform']=T.tolist()
 cfg['metric_RGB_translation_factor']=scale;cfg['new_sensor_ICP_TSDF_required']=True
 save(OUT/'profile.json',cfg)
 provenance=dict(status='prepared_known_board_empirical_depth_gain_trial',script_sha256=sha(__file__),reconstruction_script=str(SCRIPT),reconstruction_script_sha256=sha(SCRIPT),board_calibration=str(CAL),board_calibration_sha256=sha(CAL),
  old_source_hashes={str(p.relative_to(ROOT)):sha(p) for p in [BASE/'profile.json',BASE/'bundle/poses.json',BASE/'bundle/landmarks.npz',BASE/'native_keep_mask.png',BASE/'calibration_frozen.json']},
  sensor_unit_changed=True,sensor_gain_or_offset_applied=True,empirical_depth_gain_over_native_candidate=sensor_unit/.00025,offset_m=0.,device_depth_unit_confirmed=False,physical_thresholds_unchanged=True,old_cloud_scaled=False,old_cloud_overwritten=False,new_ICP_TSDF_and_support=True,
  vertex_indices='New TSDF extraction creates new point identities. Do not copy old cleanup/spectral vertex indices.',
  geometry_axes='L515 reference colour-camera axes; no cross-camera alignment yet.',
  image_selection='Exact same 64 source frames and frozen housing mask as previous L515 result.',
  manual_traits_used=False)
 save(OUT/'provenance.json',provenance)
 print('PREPARED '+str(OUT)+' factor '+str(scale),flush=True)
 spec=importlib.util.spec_from_file_location('old_l515_sensor_replay',SCRIPT);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 m.fuse(SimpleNamespace(output=str(OUT)))
 # Supplement historical implementation's generic summary wording with exact
 # new provenance without changing any frozen output from the previous run.
 summary=read(OUT/'result/summary.json');summary['board_pitch_mm']=25.;summary['physical_marker_mm']=18.;summary['RGB_translation_factor_from_known_board']=scale
 summary['scale_status']=cfg['metric_scale_status'];summary['old_point_indices_reusable']=False;summary['raw_sensor_depth_gain_or_offset_applied']=True;summary['empirical_depth_gain_over_native_candidate']=sensor_unit/.00025;summary['device_depth_unit_confirmed']=False
 save(OUT/'result/summary.json',summary)
 provenance['status']='completed_known_board_empirical_depth_gain_trial';provenance['result_summary_sha256']=sha(OUT/'result/summary.json');save(OUT/'provenance.json',provenance)
 print('COMPLETE '+str(OUT),flush=True)

if __name__=='__main__':main()
