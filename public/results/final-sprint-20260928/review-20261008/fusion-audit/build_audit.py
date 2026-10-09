"""Audit existing results without changing them; freeze compact source evidence."""
from pathlib import Path
import hashlib,json,subprocess
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).resolve().parent
NEW=ROOT/'generated/research_confirmed_board_20261007';files=[]
def read(p):
 p=Path(p);files.append(p);return json.loads(p.read_text())
identity=read(NEW/'spectral_metric_v1/identity_remap_validation.json')
fusion=read(NEW/'fusion_v1/summary.json');summary=read(NEW/'spectral_metric_v1/result/summary.json')
plane=read(NEW/'hsi_geometry/summary.json');height=read(NEW/'hsi_geometry/height_model_diagnostic/summary.json')
local=read(OUT.parent/'fusion_candidates/local_warp_probe.json')
# Public historical assets are read from the actual WSL website repository.
wsroot='/home/adithyarama/projects/PhenoFusion3D/phenofusion3d.github.io/public/experimental-results/viewer'
code="from pathlib import Path;import json,hashlib;r=Path("+repr(wsroot)+");print(json.dumps([{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'data':json.loads(p.read_text())} for p in sorted(r.glob('fusion/*/fusion_metrics.json'))]))"
old=json.loads(subprocess.check_output(['wsl.exe','-d','Ubuntu','--','python3','-c',code],text=True))
oldbrief=[]
for row in old:
 d=row['data'];r=d['registration'];oldbrief.append({'plant':d['plant'],'source':row['path'],'sha256':row['sha256'],'mapped_points':d['coverage']['points_with_valid_depth'],'registration_model':r['selected_model'],'plant_training_inliers':r['plant_inliers'],'plant_training_rmse_rgb_px':r['plant_reprojection_rmse_px'],'ecc_correlation':r['ecc_correlation'],'ecc_residual_affine':r['ecc_residual_affine'],'depth_search_radius_px':4,'surface_filter_mm':20})
actual=[]
for sensor in ('fx10','fx17'):
 p=NEW/f'spectral_metric_v1/result/assigned_spectra_{sensor}.npz';files.append(p)
 with np.load(p,allow_pickle=False) as z:
  actual.append({'sensor':sensor,'array_shapes':{k:list(z[k].shape) for k in z.files},'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
headers=[]
for p in sorted((ROOT/'data/main/test_plant_10-7/20260928').glob('*.hdr')):
 files.append(p);txt=p.read_text();keys=[line.split('=',1)[0].strip() for line in txt.splitlines() if '=' in line]
 headers.append({'file':str(p.relative_to(ROOT)),'metadata_keys':keys,'recorded_spatial_intrinsics':False,'per_line_timing_or_encoder':False})
evidence={'audit_date':'2026-10-08','scope':'Historical dense prototype versus current sparse September result; new local-warp experiment only. Other concurrent experiments saved separately.','historical_site':{'url':'https://phenofusion3d.github.io/results/experimental/','dataset':'20260828','total_points':sum(x['mapped_points'] for x in oldbrief),'bands_in_processed_merged_product':427,'spatial_stride':4,'plants':oldbrief,'caveat':'427-band product uses spatially resampled/registered FX17 after gain/offset correction, not 427 untouched same-pixel detector bands. Training image residuals and geometry overlap are not independent HSI material-point accuracy.'},'current_sparse':{'unique_geometry_locations':identity['unique_source_locations'],'spectral_observations':identity['associations'],'sensor_counts':summary['sensor_counts'],'all_in_plant':'P5','context_points':identity['geometry_context_points'],'unassigned_context_count':identity['geometry_context_points']-identity['unique_source_locations'],'arrays':actual,'physical_registration_validated':False,'dense_surface_fusion':False},'geometry_fusion':{k:fusion[k] for k in ('d405_points','l515_added_points','fused_points','decision_counts','method','duplicate_distance_m','uncertain_overlap_distance_m','cross_view_agreement_m','free_space_margin_m','geometry_averaged_between_cameras','shape_completion')},'current_plane_holdouts':{s:next(x for x in plane[s]['models'] if x['model']=='affine') for s in ('fx10','fx17')},'rejected_height_model':height,'new_local_warp_screen':{'source':'../fusion_candidates/local_warp_probe.json','passes':sum(m['passes_screen'] for r in local['regions'] for m in r['models']),'candidate_models':sum(len(r['models']) for r in local['regions']),'regions':[{k:v for k,v in r.items() if k not in ('training_candidates','heldouts')} for r in local['regions']]},'raw_header_inventory':headers,'remaining_gap':'No identified omitted current HSI cube or spatial lens/rig/timing sidecar; all 002 and 003 paired cubes were used. This is a current-record audit, not a proof that no additional lab records or image-feature evidence can be recovered.','source_checksums':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
(OUT/'evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
# A figure for explaining the two distinct uses of fusion.
fig,ax=plt.subplots(figsize=(15,8.5),dpi=150);fig.patch.set_facecolor('#f6fafb');ax.set_facecolor('#f6fafb');ax.set_xlim(0,15);ax.set_ylim(0,8.5);ax.axis('off')
ax.text(.4,8.05,'Two different fusion steps',fontsize=25,weight='bold',color='#102e3c')
ax.text(.4,7.61,'Saved v1 checkpoint for the September 28 study; new local-leaf experiments are reported separately.',fontsize=12,color='#315360')
def box(x,y,w,h,title,body,col):
 ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.15',facecolor=col,edgecolor='#b6cbd5',linewidth=1))
 ax.text(x+.15,y+h-.34,title,fontsize=14,weight='bold',color='#133440')
 ax.text(x+.15,y+h-.72,body,fontsize=11,color='#244b5b',va='top',linespacing=1.5)
def arrow(x,y,xx,yy):ax.add_patch(FancyArrowPatch((x,y),(xx,yy),arrowstyle='-|>',mutation_scale=15,color='#3f7789',linewidth=2))
ax.text(.4,7.03,'1   D405 + L515: combine observed geometry',fontsize=16,weight='bold',color='#145c71')
box(.5,4.92,3.8,1.65,'Reconstruct each camera','D405: primary geometry\nL515: complementary observations\n25 mm board gives metric reference','#e7f3f5')
box(5.15,4.92,4.0,1.65,'Align and check','Rigid alignment in a shared frame\nSuppress duplicates and conflicts\nKeep each original point identity','#e7f3f5')
box(10.0,4.92,4.3,1.65,'Observed-point union','1,719,001 D405 + 21,672 L515\nThen separate plants and scene\n430,060 retained plant points','#e7f3f5')
arrow(4.45,5.72,4.97,5.72);arrow(9.3,5.72,9.82,5.72)
ax.text(.4,4.31,'2   FX10 + FX17: associate spectra with surface locations',fontsize=16,weight='bold',color='#865923')
box(.5,2.17,3.8,1.65,'Read measured spectra','13,343 sampled image locations\nTwo separate sensors, 224 bands each\nRaw DN and qualified Q / Q0','#fff3df')
box(5.15,2.17,4.0,1.65,'Identify the same material','Review HSI ↔ RGB features\nUse supported depth + saved pose\nMatch original 3D point identity','#fff3df')
box(10.0,2.17,4.3,1.65,'Existing sparse result','3 unique P5 locations\n3 FX10 + 3 FX17 observations\nColour changes only at these markers','#fff3df')
arrow(4.45,2.97,4.97,2.97);arrow(9.3,2.97,9.82,2.97)
ax.text(.55,1.35,'Why the full plant is not spectral-coloured yet',fontsize=15,weight='bold',color='#8d3527')
ax.text(.55,.96,'The table-plane map is supported; its extension to raised leaves failed held-out tests.\nA local visible-leaf mapping may still work, but must pass separate correspondence checks before export.',fontsize=12,color='#4a4e4f',linespacing=1.6,va='top')
fig.savefig(OUT/'fusion_process.png',bbox_inches='tight');fig.savefig(OUT/'fusion_process.svg',bbox_inches='tight');plt.close(fig)
print(json.dumps({'historical_points':evidence['historical_site']['total_points'],'current_unique_points':identity['unique_source_locations'],'new_local_models':evidence['new_local_warp_screen']['candidate_models'],'new_local_passes':evidence['new_local_warp_screen']['passes']}))
