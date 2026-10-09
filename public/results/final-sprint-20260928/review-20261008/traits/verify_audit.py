from pathlib import Path
import json,sys,hashlib,collections
import numpy as np,cv2
O=Path(__file__).resolve().parent;ROOT=Path.cwd();B=ROOT/'generated/research_confirmed_board_20261007';T=B/'traits_metric';D=ROOT/'generated/research_20260928_improvement_20261007/short_dense_v3';load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sys.path.insert(0,str(ROOT/'generated/research_20260928_processing_20261007'))
from extract_P5_review_candidate import read_vertices,xyz
p=xyz(read_vertices(B/'fusion_v1/fused_review_reference.ply'),slice(None));prov=np.load(B/'fusion_v1/fused_point_provenance.npz');cl=np.load(B/'cleanup_v1/result/point_classification.npz');rows=load(O/'conditional_comparisons.json');attempts=load(O/'batch_endpoint_probes.json')+load(O/'revision_endpoint_probes.json');lookup={a['id']:a for a in attempts};K=np.array(load(D/'profile.json')['K']);poses={a['frame']:np.array(a['transform']) for a in load(B/'d405_metric/icp_diagnostics_reexpressed.json') if a['icp_accepted']};checks=[]
for r in rows:
 a=lookup[r['endpoint_evidence']];ids=np.array(r['fused_point_indices']);ref=float(np.linalg.norm(p[ids[1]]-p[ids[0]])*100);assert abs(ref-r['estimate_cm'])<1e-10
 assert np.all(cl['plant_id'][ids]==int(r['specimen_id'][1]));assert prov['original_point_index'][ids].tolist()==r['source_point_ids'];assert prov['camera_id'][ids].tolist()==r['camera_ids']
 support=[];details=[]
 for fr in [a['frame']]+a['secondary']:
  t=poses[fr];pc=(p[ids]-t[:3,3])@t[:3,:3];ideal=pc[:,:2]/pc[:,2,None]*[K[0,0],K[1,1]]+[K[0,2],K[1,2]];ij=np.rint(ideal).astype(int);de=np.load(D/f'rgb/depth_{fr}.npz');z=de['depth'][ij[:,1],ij[:,0]]*1.0288746669066682;votes=de['votes'][ij[:,1],ij[:,0]];delta=pc[:,2]-z;ok=np.isfinite(z)&(z>0)&(votes>=2)&(np.abs(delta)<=.012);support.append(ok);details.append(dict(frame=fr,point_minus_stereo_mm=[float(v*1000) if np.isfinite(v) else None for v in delta],votes=votes.tolist(),supported=ok.tolist()))
 counts=np.sum(support,axis=0);assert np.all(counts>=2);checks.append(dict(id=r['id'],chord_recomputed_cm=ref,original_vertex_identity_exact=True,current_cleaned_plant_identity_exact=True,endpoint_supporting_view_counts=counts.tolist(),depth_checks=details))
old=load(T/'traits_review.json');sources=[]
for rel,expected in old['source_sha256'].items():
 if '/fusion_v1/' in rel or '/cleanup_v1/result/' in rel or rel.endswith('icp_diagnostics_reexpressed.json') or '/manual_validation_5-plants_28-09/' in rel:
  path=ROOT/rel;actual=hashlib.file_digest(path.open('rb'),'sha256').hexdigest();assert actual==expected; sources.append(rel)
ver=load(O/'verification.json');ver.update(exact_geometry_provenance_and_chord_checks=checks,all_accepted_endpoints_two_view_depth_supported=True,existing_result_and_manual_source_hashes_unchanged=True,unchanged_source_count=len(sources),checked_source_paths=sources,maximum_chord_recomputation_error_cm=max(abs(a['chord_recomputed_cm']-b['estimate_cm']) for a,b in zip(checks,rows)))
(O/'verification.json').write_text(json.dumps(ver,indent=2,allow_nan=False)+'\n')
review=[];accepted={r['endpoint_evidence'] for r in rows}
for a in attempts:
 if a['id'] in accepted:status='conditional_comparison_in_curated_table';reason='Visually reviewed in three views; exact geometry and two-view stereo support verified. Definitions and held-ruler pose remain conditional.'
 elif a['chord_cm'] is None:status='rejected_missing_endpoint_support';reason='At least one endpoint lacks current retained source support; no distance published as a manual comparison.'
 elif a['manual_dimension_id'] in ['P3.O01.length','P3.O05.length','P5.O04.length']:status='rejected_anatomical_origin_or_partial_lamina';reason='Crossing stem or partial visible lamina origin does not match full ruler length.'
 elif a['manual_dimension_id'].startswith('P5.O02.'):status='superseded_after_venation_axis_review';reason='First batch axis interpretation was wrong; revised length provided, revised width abstains.'
 else:status='descriptive_only_reference_section_mismatch';reason='Visible chord is not matched to the ruler section; P1 also has unresolved annotation-unit discrepancy.'
 review.append(dict(id=a['id'],measurement_id=a['manual_dimension_id'],status=status,reason=reason,attempt_chord_cm=a['chord_cm']))
(O/'attempt_review.json').write_text(json.dumps(review,indent=2)+'\n')
h=(O/'index.html').read_text(encoding='utf-8');h=h.replace('<h2>Three-view endpoint review</h2>','<h2>Three-view endpoint review</h2><p><strong>These sheets preserve every initial numerical attempt, including rejected ones.</strong> Only the 13 rows in the curated table are accepted for conditional comparison. Crossing-stem matches, partial sections and the initial P5.O02 axis interpretation are not accepted. See <a href="attempt_review.json">attempt review</a> and <a href="verification.json">numerical/provenance checks</a>.</p>');(O/'index.html').write_text(h,encoding='utf-8')
print('Verified',len(rows),'comparisons;',len(sources),'existing input hashes unchanged; all26 endpoints have >=2 view stereo support.')
