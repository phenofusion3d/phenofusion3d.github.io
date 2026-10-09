"""Transparent comparison selection, not a final independent accuracy test."""
from pathlib import Path
import hashlib,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path.cwd();BASE=ROOT/'generated/research_confirmed_board_20261007';OUT=BASE/'cross_camera'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 native=read(OUT/'native/alignment.json');gain=read(OUT/'boardgain/alignment.json');soil=read(OUT/'matched_soil_metric_comparison.json')
 assert all(native['acceptance_checks'].values()) and all(gain['acceptance_checks'].values())
 comparisons={}
 for region in ['heldout_P2_P4','all_foliage_heldout']:
  for metric in ['equal_direction_mean_median_mm','equal_direction_mean_p90_mm']:
   key=f'{region}.{metric}';n=native['metrics'][region]['after'][metric];g=gain['metrics'][region]['after'][metric]
   comparisons[key]=dict(native=n,boardgain=g,boardgain_improves=g<n)
 for metric in ['median_mm','p90_mm','rms_mm','max_mm']:
  n=soil['variants']['native']['aggregate']['pot_rigid']['median5x5'][metric];g=soil['variants']['boardgain']['aggregate']['pot_rigid']['median5x5'][metric]
  comparisons[f'fixed_soil.{metric}']=dict(native=n,boardgain=g,boardgain_improves=g<n)
 assert all(v['boardgain_improves'] for v in comparisons.values())
 run=BASE/'l515_metric_boardgain_v1';source=run/'result/l515_supported_reference.ply';Ts=np.array(gain['T_D405_reference_from_L515_reference']);assert np.allclose(Ts[:3,:3]@Ts[:3,:3].T,np.eye(3),atol=1e-10) and np.linalg.det(Ts[:3,:3])>0
 evidence=[OUT/'native/alignment.json',OUT/'boardgain/alignment.json',OUT/'matched_soil_metric_comparison.json',BASE/'l515/metric_calibration.json',BASE/'l515/metric_landmark_depth_diagnostics.json',BASE/'l515/replay_validation_native.json',BASE/'l515/replay_validation_board_gain.json',source,run/'result/icp_diagnostics.json',Path(__file__)]
 report=dict(status='selected_board_gain_empirical_research_candidate_for_new_fusion',chosen_variant='boardgain',selected_variant='boardgain',
  l515_run=str(run),l515_source=str(source),l515_source_path=str(source),l515_source_sha256=sha(source),l515_point_evidence=str(run/'result/point_evidence.npz'),l515_icp_poses=str(run/'result/icp_diagnostics.json'),
  d405_source=str(BASE/'d405_metric/full_scene_reference.ply'),T_D405_reference_from_L515_reference=Ts.tolist(),
  calibration_board_square_m=.025,empirical_depth_conversion_m_per_count=.0002533640570741938,confirmed_device_depth_unit=False,
  rigid_only_cross_camera_alignment=True,plant_scale_fitted=False,manual_traits_used=False,
  selection_reason='Both variants pass the inherited bounded rigid surface gates. The board-only depth-gain variant improves heldout-pot and all-foliage median/P90 proximity, and all fixed-soil median/P90/RMS/max correspondence distances relative to the newly metric native baseline. Separate plant-scan RGB landmark depth diagnostics also improve. Select it as a better-supported empirical candidate while retaining both complete results.',
  surface_alignment_file=str(OUT/'boardgain/alignment.json'),fixed_soil_evidence_file=str(OUT/'matched_soil_metric_comparison.json'),comparisons=comparisons,
  fixed_soil_selected=soil['variants']['boardgain']['aggregate']['pot_rigid']['median5x5'],
  fixed_soil_selected_per_plant=soil['variants']['boardgain']['per_specimen'],
  selection_data_reused=True,final_untouched_independent_test=False,physical_accuracy_validated=False,
  fusion_conditions=['Keep the predeclared physical duplicate/support/conflict thresholds; do not relax them to force overlap.','D405 stereo depths and poses use its independently board-derived factor; L515 uses the new depth conversion and new final ICP poses.','Camera-source provenance must identify new per-camera point IDs; old L515 point IDs cannot be reused.','Recompute source-reviewed cleanup membership against the new fused geometry.','Treat L515-only additions and uncertain overlap separately.'],
  limits=['Held-out regions/soil observations were excluded from rigid fitting but used here for variant selection. They are not a final untouched validation dataset.','The rigid transform is an empirical alignment of reconstructed surfaces, not a certified physical sensor extrinsic.','The board-based depth gain is supported on this dataset, not a universal device calibration.','P4 soil median remains7.43mm and maximum26.04mm; foliage proximity P90 remains52.38mm, affected by occlusion and incomplete coverage.','Historical conditional-scale scores are not directly comparable to the new physically anchored quantities. The old soil median3.411mm does not imply better physical truth.','No gap-free360-degree completeness or biological trait accuracy is established.'],
  source_hashes={str(p.relative_to(ROOT)):sha(p) for p in evidence})
 (OUT/'selection.json').write_text(json.dumps(report,indent=2)+'\n')
 rows=soil['variants']['native']['rows'];other=soil['variants']['boardgain']['rows'];assert [(r['frame'],r['point_id']) for r in rows]==[(r['frame'],r['point_id']) for r in other]
 fig,axes=plt.subplots(1,2,figsize=(12,5),layout='constrained')
 for ax,plant in zip(axes,['P2','P4']):
  keep=[i for i,r in enumerate(rows) if r['quality_cohort'] and r['specimen']==plant]
  vals=np.array([[rows[i]['methods']['pot_rigid']['median5x5']['distance_m'],other[i]['methods']['pot_rigid']['median5x5']['distance_m']] for i in keep])*1000
  for y in vals:ax.plot([0,1],y,color='#c0c5c8',alpha=.6,lw=.8)
  ax.scatter(np.zeros(len(vals)),vals[:,0],s=18,c='#276a90',zorder=3);ax.scatter(np.ones(len(vals)),vals[:,1],s=18,c='#a25a26',zorder=3)
  ax.set_xticks([0,1],['Native conversion','Board-only gain']);ax.set_ylabel('Matched soil 3D disagreement / mm');ax.set_title(f'{plant}: {len(vals)} original quality-passing observations');ax.set_xlim(-.25,1.25);ax.set_ylim(bottom=0);ax.grid(axis='y',alpha=.2)
 fig.suptitle('Same matched soil features; new metric reconstructions and rigid alignment',fontsize=14)
 for e in ['png','pdf','svg']:fig.savefig(OUT/f'matched_soil_comparison.{e}',dpi=180)
 plt.close(fig)
 caption='The exact original62quality-passing matched-soil observations from65source matches are compared without residual trimming. Lines connect the same source feature in the native-depth and board-gain variants after each inherited P1/P3/P5 pot-only rigid alignment. P2/P4 were excluded from the rigid fit, but these observations are now used for variant selection, so the plot is not a final untouched validation result. D405 targets are exact original RGB-bundle landmarks expressed at the supplied25mm board scale; L515 uses recorded raw source pixels with each new final sensor ICP trajectory. Shared camera models and acquisition assumptions remain. The gain is empirical and does not confirm the missing recording-time device depth unit.\n'
 (OUT/'matched_soil_comparison.caption.txt').write_text(caption,encoding='utf-8')
 (OUT/'matched_soil_comparison.provenance.json').write_text(json.dumps(dict(source_sha256=sha(OUT/'matched_soil_metric_comparison.json'),all_original_cohort_preserved=True,plots={f'matched_soil_comparison.{e}':sha(OUT/f'matched_soil_comparison.{e}') for e in ['png','pdf','svg']}),indent=2)+'\n')
 print(json.dumps({k:report[k] for k in ['status','chosen_variant','l515_source','T_D405_reference_from_L515_reference','comparisons']},indent=2))
if __name__=='__main__':main()
