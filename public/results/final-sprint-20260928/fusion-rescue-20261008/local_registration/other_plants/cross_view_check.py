"""Check frozen appearance proposals across adjacent views, without refitting."""
from pathlib import Path
import os
os.environ['OMP_NUM_THREADS']='2'
import json,numpy as np,open3d as o3d,cv2
from scipy.spatial import cKDTree
ROOT=Path.cwd();OUT=Path(__file__).resolve().parent
report=json.loads((OUT/'learned_other_plants.json').read_text());records=report['records']
D=ROOT/'generated/research_20260928_improvement_20261007/short_dense_v3'
p=json.loads((D/'profile.json').read_text());K=np.array(p['K']);dist=np.array(p['dist'])
poses={r['frame']:np.array(r['transform']) for r in json.loads((D/'result/icp_diagnostics.json').read_text()) if r['icp_accepted']}
for T in poses.values():T[:3,3]*=1.0288746669066682
def collect(plant,frame):
 vals=[]
 for r in records:
  if r['plant_id']!=plant or r['frame']!=frame:continue
  for ix in r['joint_domain_indices']:
   vals.append({'source':r['source_HSI_rotated_xy'][ix],'target':r['target_native_RGB_xy'][ix],'patch':r['hsi_patch_ids'][ix],'vertex':r['nearest_current_plant_vertex_index'][ix],'confidence':r['confidence'][ix],'channels':[r['channel']]})
 dedup=[]
 for v in sorted(vals,key=lambda x:-x['confidence']):
  match=next((w for w in dedup if np.linalg.norm(np.array(v['source'])-w['source'])<=2 and np.linalg.norm(np.array(v['target'])-w['target'])<=2 and w['patch']==v['patch']),None)
  if match is None:dedup.append(v)
  else:match['channels']=sorted(set(match['channels']+v['channels']))
 return dedup
rows=[]
for plant in range(1,5):
 frames=sorted({r['frame'] for r in records if r['plant_id']==plant})
 a,b=[collect(plant,f) for f in frames]
 xyz=np.asarray(o3d.io.read_point_cloud(str(ROOT/f'generated/research_confirmed_board_20261007/cleanup_v1/result/P{plant}_reference.ply')).points)
 checks=[]
 if a and b:
  sa=np.array([r['source'] for r in a]);sb=np.array([r['source'] for r in b]);dab,j=cKDTree(sb).query(sa);_,back=cKDTree(sa).query(sb)
  for ix,(dd,jx) in enumerate(zip(dab,j)):
   if dd>3 or back[jx]!=ix or a[ix]['patch']!=b[jx]['patch']:continue
   va,vb=a[ix],b[jx];X=xyz[va['vertex']];Y=xyz[vb['vertex']];T=poses[frames[1]]
   camera=(X-T[:3,3])@T[:3,:3];pred=cv2.projectPoints(camera.reshape(1,3),np.zeros(3),np.zeros(3),K,dist)[0][0,0]
   checks.append({'patch':va['patch'],'source_a':va['source'],'source_b':vb['source'],'hsi_localization_difference_px':float(dd),'view_a':va,'view_b':vb,
    'nearest_vertex_separation_m':float(np.linalg.norm(X-Y)),'view_a_vertex_reprojection_to_b_error_rgb_px':float(np.linalg.norm(pred-vb['target'])),
    'passes_geometric_consistency_screen':bool(np.linalg.norm(X-Y)<=.010 and np.linalg.norm(pred-vb['target'])<=3.)})
 rows.append({'plant_id':plant,'frames':frames,'unique_domain_proposals_by_view':[len(a),len(b)],'matched_source_proposals':len(checks),'geometrically_consistent_proposals':sum(c['passes_geometric_consistency_screen'] for c in checks),'checks':checks})
result={'status':'POST_FREEZE_CONSISTENCY_SCREEN_ONLY','policy':'Gray/green duplicate proposals merged within2HSI/2RGBpx; mutual nearest source coordinates across frames within3nativeHSIpx and same reviewed patch. Screen: existing-vertex separation<=10mm and forward reprojection<=3RGBpx. Thresholds fixed before evaluating results.',
 'limits':['Matching-confidence and multiview consistency are necessary support, not independent same-material truth.','Nearest observed vertices may lie on same nearby patch without proving exact spectral localization.','No blind anatomical control has been established for these P1–P4 pairs.','No dense surface assignment created.'],
 'accepted_new_dense_assignments':0,'plants':rows}
(OUT/'cross_view_consistency.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
