"""Publish current board-referenced traits, preserving every frozen manual exclusion."""
from pathlib import Path
import csv, copy, hashlib, html, json, shutil, sys
import numpy as np
from scipy.spatial.distance import cdist

ROOT=Path.cwd(); BASE=ROOT/'generated/research_confirmed_board_20261007'
TRAITS=BASE/'traits_metric'; OUT=BASE/'website/traits'; F=BASE/'fusion_v1'; C=BASE/'cleanup_v1/result'
OLD=ROOT/'generated/final_sprint_website_20261007/traits_site'
OLDTRAIT=ROOT/'generated/research_followthrough_20261007/traits'
SCALE=1.0288746669066682
sys.path.insert(0,str(ROOT/'generated/research_20260928_processing_20261007'))
from extract_P5_review_candidate import read_vertices,xyz
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v):Path(p).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()
def rel(p):return Path(p).relative_to(ROOT).as_posix()
def csvwrite(p,rows):
    with Path(p).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader()
        w.writerows({k:json.dumps(v) if isinstance(v,(dict,list)) else v for k,v in a.items()} for a in rows)
if OUT.exists() and any(OUT.iterdir()) and '--resume-generated-output' not in sys.argv:raise SystemExit('Refusing existing current website output')
OUT.mkdir(parents=True,exist_ok=True)
old=load(OLD/'website_tables.json'); new=copy.deepcopy(old); review=load(TRAITS/'traits_review.json')
inputs=[F/'fused_review_reference.ply',F/'fused_point_provenance.npz',C/'point_classification.npz',C/'summary.json',TRAITS/'traits_review.json',OLD/'website_tables.json',OLDTRAIT/'provisional_chords.json',OLDTRAIT/'chord_endpoint_indices.npz']
oldF=ROOT/'generated/research_d405_l515_fusion_20261007/v1'
inputs += [oldF/'fused_point_provenance.npz']
input_hashes={rel(p):sha(p) for p in inputs}
prov=np.load(F/'fused_point_provenance.npz'); oldprov=np.load(oldF/'fused_point_provenance.npz')
points=xyz(read_vertices(F/'fused_review_reference.ply'),slice(None)); cl=np.load(C/'point_classification.npz')
# D405 IDs are unchanged across gauge conversion; L515 IDs are not interchangeable.
did=np.flatnonzero(prov['camera_id']==0)
inverse=np.full(8265080,-1,dtype=np.int64); inverse[prov['original_point_index'][did]]=did
frozen=np.load(OLDTRAIT/'chord_endpoint_indices.npz'); remapped={}; pool_audit={}
for key in frozen.files:
    idx=frozen[key]
    retained=idx[oldprov['camera_id'][idx]==0]
    mapped=inverse[oldprov['original_point_index'][retained]]
    assert np.all(mapped>=0), 'Frozen D405 endpoint candidate absent from new fusion'
    remapped[key]=mapped
    pool_audit[key]=dict(historical_count=len(idx),exact_d405_remap_count=len(mapped),old_l515_not_remappable_count=int((oldprov['camera_id'][idx]!=0).sum()),current_cleanup_plant_counts={str(k):int(v) for k,v in zip(*np.unique(cl['plant_id'][mapped],return_counts=True))},policy='No reuse of old L515 vertex IDs in the rebuilt L515 cloud; unmappable historical points excluded from current candidate sensitivity.')
np.savez_compressed(TRAITS/'chord_endpoint_indices.npz',**remapped)
rawchords=load(OLDTRAIT/'provisional_chords.json'); chordmap={}
for a in rawchords:
    a['historical_chord_cm']=a.pop('conditional_chord_cm',None)
    a.pop('chord_conditional_m',None)
    a['scale_status']='Board-referenced metres from supplied 25 mm checker pitch; same observed D405 endpoints; anatomical and reference accuracy remain unvalidated.'
    a['endpoint_selection_policy']='Exact preserved camera=0/source-point ID and frozen source-image click; no closest-geometry rematching or manual-value tuning.'
    for e in a['endpoints']:
        if 'fused_point_index' not in e:continue
        oi=e['fused_point_index']; assert e['camera_id']==0
        ni=int(inverse[e['original_point_index']]); assert ni>=0
        e['historical_fused_point_index']=oi;e['fused_point_index']=ni
        before=np.array(e.pop('reference_xyz_conditional_m'))
        assert np.allclose(points[ni],before*SCALE,rtol=0,atol=1e-12)
        e['reference_xyz_m']=points[ni].tolist()
        e['current_cleaned_plant_id']=int(cl['plant_id'][ni]);e['current_cleanup_reason']=int(cl['reason'][ni])
        e['current_candidate_pool_audit']=pool_audit[e['candidate_index_key']]
    valid=all('fused_point_index' in e for e in a['endpoints'])
    if valid:
        ends=[e['fused_point_index'] for e in a['endpoints']]
        a['chord_m']=float(np.linalg.norm(points[ends[0]]-points[ends[1]]));a['chord_cm']=a['chord_m']*100
        keys=[e['candidate_index_key'] for e in a['endpoints']]
        ds=cdist(points[remapped[keys[0]]],points[remapped[keys[1]]])
        a['endpoint_pixel_disk_sensitivity_m']=[float(ds.min()),float(ds.max())]
        cleanpools=[remapped[k][cl['plant_id'][remapped[k]]==a['plant']] for k in keys]
        cds=cdist(points[cleanpools[0]],points[cleanpools[1]])
        a['current_cleaned_endpoint_pool_sensitivity_m']=[float(cds.min()),float(cds.max())]
        a['sensitivity_scope']='Exact remapped historical D405 source-disk pool in full fusion; cleanup membership counts are explicit. Separate cleaned-only range supplied. One old P5 L515 candidate is not remappable and excluded.'
        a.pop('endpoint_pixel_disk_sensitivity_conditional_m',None)
    else:a['chord_m']=None;a['chord_cm']=None
    for projection in a.get('projections',[]):
        ds=projection.pop('point_minus_stereo_depth_conditional_m',None)
        if ds is not None:projection['point_minus_stereo_depth_m']=[x*SCALE if x is not None else None for x in ds]
    a['signed_difference_from_operator_annotation_cm']=a['chord_cm']-a['reference_annotation_cm'] if a['id']=='P3.O03.blade_chord' else None
    a['physical_accuracy_validated']=False;a['included_in_physical_accuracy_statistics']=False
    chordmap[a['id']]=a
save(TRAITS/'provisional_chords.json',rawchords)
save(TRAITS/'chord_pool_remap_audit.json',pool_audit)
csvwrite(TRAITS/'provisional_chords.csv',[dict(id=a['id'],manual_dimension_id=a['manual_dimension_id'],chord_cm=a['chord_cm'],annotation_cm=a['reference_annotation_cm'],signed_difference_from_operator_annotation_cm=a['signed_difference_from_operator_annotation_cm'],physical_accuracy_validated=False,scope=a['scope'],limitation=a['limitation']) for a in rawchords])

# Current evidence folder; original manual photographs remain byte-identical.
shutil.copytree(OLD/'manual_reference',OUT/'manual_reference',dirs_exist_ok=True)
shutil.copytree(TRAITS/'assets',OUT/'assets',dirs_exist_ok=True)
for p in OLDTRAIT.glob('P*_manual_overview.jpg'):shutil.copy2(p,OUT/'assets'/p.name)
for p in OLDTRAIT.glob('assets/P*.O*.jpg'):shutil.copy2(p,OUT/'assets'/p.name)
for p in TRAITS.iterdir():
    if p.suffix in ('.json','.csv','.npz'):shutil.copy2(p,OUT/p.name)
# Old linked reports remain available only inside an explicit historical archive.
shutil.copytree(OLD,OUT/'archive/pre_confirmed_board',dirs_exist_ok=True)
banner='<aside style="position:relative;background:#8b290d;color:white;padding:18px;font:18px sans-serif"><strong>HISTORICAL PRE-CONFIRMED-BOARD REPORT.</strong> Its old coordinates, counts, scale gap and conditional comparisons have been superseded. Source-image/ruler evidence is retained for traceability. <a style="color:white" href="../../../../index.html">Open current traits</a></aside>'
for p in (OUT/'archive/pre_confirmed_board/reports').glob('*/index.html'):
    s=p.read_text(encoding='utf-8');pos=s.find('>',s.find('<body'))+1
    if pos>0:s=s[:pos]+banner+s[pos:]
    else:s=banner+s
    p.write_text(s,encoding='utf-8')
new.update(schema_version=2,audit_date='2026-10-08',paths_relative_to='website/traits',status='current_confirmed_board_observed_geometry_not_validated_anatomical_traits')
new['labels'].update(observed_span_cm='Observed X / Y / display-Z span (board-referenced cm; not anatomical height)',observed_p01_p99_span_cm='Observed 1st–99th percentile span (board-referenced cm)',hull_cm2='Observed XY convex-hull area (board-referenced cm²; not leaf area)',estimate_cm='Provisional source-endpoint chord (board-referenced cm; not validated leaf length)')
new['assumptions'].update(coordinate_unit='board_referenced_m',website_length_unit='board_referenced_cm',website_area_unit='board_referenced_cm2',length_conversion='100 times board-referenced distance in metres',area_conversion='10000 times board-referenced XY area in square metres',physical_scale_verified=False,board_dimensions_operator_confirmed=True,board_square_mm=25,board_marker_mm=18,board_design='7 x 10 DICT_4X4_50',d405_metric_scale_factor=SCALE,independent_print_size_uncertainty_available=False,source_coordinates_modified=True,coordinate_update='D405 coordinates/pose translations multiplied by board-derived gauge factor; L515 rebuilt with empirically board-fitted depth gain then rigidly aligned; final fusion/cleanup thresholds remain physical.',source_percentile_definition='First through 99th percentile of the current retained plant subset; not anatomical extrema.')
new['metrics']['provisional_difference_policy']='Only P3.O03: 7.691100957 board-referenced cm minus operator-only 7.5 cm = +0.191100957 cm. This is arithmetic, not validation, a physical error estimate or a percent score.'
new['missing_deliverables']=[m for m in new['missing_deliverables'] if m['id']!='physical_scale']
new['resolved_gaps']=[dict(id='board_dimensions',status='operator_confirmed',value='25 mm square / 18 mm marker; 7 by 10 DICT_4X4_50',effect='Metric gauge is now anchored to supplied checker pitch. Anatomical endpoints, manual references and camera-geometry accuracy are not thereby validated.')]
new['missing_deliverables'].insert(0,dict(id='metric_accuracy',status='not_independently_validated',missing='Independent printed-size uncertainty, native L515 unit confirmation and untouched geometric accuracy controls',impact='Board-referenced dimensions are available; they are not certified anatomical accuracy.'))
def image_path(s):
    return s.replace('reports/trait_review/assets/','assets/').replace('reports/trait_review/P','assets/P') if isinstance(s,str) else s
for row in new['manual_dimensions']:
    row['estimate_unit']='board-referenced cm; anatomical validation unavailable'
    row['board_dimensions_operator_confirmed']=True;row['units_independently_confirmed']=False
    row['historical_exclusion_reason']=row['reason']
    for k in ('annotation_photo','ruler_photos','ruler_photo_thumbnails'):
        if isinstance(row.get(k),list):row[k]=[image_path(x) for x in row[k]]
        elif k in row:row[k]=image_path(row[k])
    if row['conditional_comparison_id']:
        c=chordmap[row['conditional_comparison_id']]
        row['estimate_cm']=c['chord_cm'];row['signed_difference_from_operator_annotation_cm']=c['signed_difference_from_operator_annotation_cm']
        row['reason']='Same frozen D405 source endpoints after board gauge correction. The source-supported chord is provisional; anatomical base convention remains tentative and the 7.5 cm reference is operator annotation only. No eligible validation pair.'
    row['comparison_id']=row.pop('conditional_comparison_id')
rowmap={a['id']:a for a in new['manual_dimensions']}
for a in new['chords']:
    c=chordmap[a['id']];a['historical_estimate_cm']=a['estimate_cm'];a['estimate_cm']=c['chord_cm']
    a['endpoint_disk_sensitivity_cm']=[x*100 for x in c['endpoint_pixel_disk_sensitivity_m']] if 'endpoint_pixel_disk_sensitivity_m' in c else None
    a['endpoints']=c['endpoints'];a['signed_difference_from_operator_annotation_cm']=c['signed_difference_from_operator_annotation_cm']
    a['source_view_figures']=[image_path(x) for x in a['source_view_figures']]
    if a['id']=='P3.O03.blade_chord':a['status']='Provisional same-endpoint chord; operator-only difference +0.191100957 cm; not anatomical accuracy validation.'
    a['coordinate_unit']='board-referenced cm'
    a['sensitivity_scope']=c.get('sensitivity_scope','No supported endpoint pair; current missing-tip search remains empty.')
    a['current_cleaned_endpoint_pool_sensitivity_cm']=[x*100 for x in c['current_cleaned_endpoint_pool_sensitivity_m']] if 'current_cleaned_endpoint_pool_sensitivity_m' in c else None
before_after=[]
for p,prior,calc in zip(new['plants'],old['plants'],review['plants']):
    assert p['id']==calc['specimen_id']
    p.update(points=calc['point_count'],core_points=calc['multi_view_core_count'],d405_points=calc['d405_count'],l515_points=calc['l515_count'],observed_span_cm=[x*100 for x in calc['full_axis_spans_m']],observed_p01_p99_span_cm=[x*100 for x in calc['p01_p99_axis_spans_m']],hull_cm2=calc['xy_convex_hull_area_m2']*10000,core_hull_cm2=calc['xy_core_hull_area_m2']*10000,source_cloud=rel(C/f"{p['id']}_reference.ply"),source_cloud_sha256=sha(C/f"{p['id']}_reference.ply"),source_provenance=rel(C/f"{p['id']}_provenance.npz"),photo=f"assets/{p['id']}_source_review.jpg",source_photo=f"assets/{p['id']}_source_raw.jpg",manual_overview=f"assets/{p['id']}_manual_overview.jpg",report='index.html',readiness_report='archive/pre_confirmed_board/reports/measurement_readiness/index.html')
    p.pop('occupied_cell_areas_cm2_by_conditional_grid_m',None)
    p['occupied_cell_areas_cm2_by_physical_grid_m']={k:v*10000 for k,v in calc['xy_occupied_cell_area_m2_by_grid_m'].items()}
    p['notes'][0]=calc['unit_status'];p['dimensions']=[rowmap[a['id']] for a in p['dimensions']]
    p['notes'].append('The photographed base disk and highest observed surface are review candidates, not accepted anatomical endpoints. Confirmed board pitch does not resolve this distinction.')
    before_after.append(dict(plant_id=p['id'],old_points=prior['points'],new_points=p['points'],change_points=p['points']-prior['points'],old_core_points=prior['core_points'],new_core_points=p['core_points'],old_l515_points=prior['l515_points'],new_l515_points=p['l515_points'],old_observed_span_conditional_cm=prior['observed_span_cm'],new_observed_span_board_cm=p['observed_span_cm'],old_xy_hull_conditional_cm2=prior['hull_cm2'],new_xy_hull_board_cm2=p['hull_cm2'],height_estimate_cm=None))
for im in new['manual_original_images']:im['thumbnail']=image_path(im['thumbnail'])
new['reports']=dict(trait_review='index.html',measurement_readiness='archive/pre_confirmed_board/reports/measurement_readiness/index.html',canopy_csv='canopy_descriptors.csv',manual_dimensions_csv='manual_dimension_disposition.csv',organs_csv='organ_correspondences.csv',chords_csv='provisional_chords.csv',before_after='before_vs_after.json',historical_trait_review='archive/pre_confirmed_board/reports/trait_review/index.html')
# Update current prose references while keeping verbatim historical exclusions.
text_replacements={'5.643':f"{chordmap['P1.O03.observed_blade_extent']['chord_cm']:.3f}",'12.149':f"{chordmap['P5.O04.terminal_lamina_chord']['chord_cm']:.3f}",'existing partial':'current partial','this explicitly conditional comparison':'this explicitly provisional comparison'}
def current_text(value,key=''):
    if key.startswith('historical'):return value
    if isinstance(value,dict):return {k:current_text(v,k) for k,v in value.items()}
    if isinstance(value,list):return [current_text(v,key) for v in value]
    if isinstance(value,str):
        for a,b in text_replacements.items():value=value.replace(a,b)
    return value
new=current_text(new)
change=dict(status='descriptive_recheck_not_proof_all_metrics_improved',old_coordinate_status='Conditional pre-confirmed-board metres; historical model',new_coordinate_status='Board-referenced metres; supplied 25 mm pitch and empirical selected L515 gain',model_changes=['D405 uniform metric gauge factor 1.0288746669066682, no new stereo surfaces','L515 rebuilt from selected board-gain candidate with new source-point IDs','New cross-camera empirical rigid alignment','Frozen image masks unchanged; native physical fusion/cleanup thresholds unchanged; soil coordinates scaled before unchanged 15/25 mm offsets'],comparison_limit='Counts and observed extents describe different retained subsets; more points, greater extent or closer operator agreement is not by itself greater accuracy.',plants=before_after,p3_operator_comparison=dict(old_chord_conditional_cm=7.475255446013435,new_chord_board_cm=chordmap['P3.O03.blade_chord']['chord_cm'],operator_annotation_cm=7.5,old_difference_cm=-.024744553986565,new_difference_cm=chordmap['P3.O03.blade_chord']['signed_difference_from_operator_annotation_cm'],physical_accuracy_validated=False,interpretation='The old near-agreement did not establish accuracy; fixing the independently supplied board gauge moves the same observed-endpoint chord away from that annotation.'))
save(OUT/'before_vs_after.json',change);save(TRAITS/'before_vs_after.json',change)
save(OUT/'website_tables.json',new)
csvwrite(OUT/'manual_dimensions_website.csv',new['manual_dimensions'])
save(OUT/'provenance.json',dict(input_sha256=input_hashes,source_coordinate_policy=new['assumptions']['coordinate_update'],source_identity_remap='D405 camera0 and original full-cloud point index only; no nearest-point matching',historical_report_rewrites='Archive report index.html files receive a prominent historical banner and link to current report. Original source folders are untouched.',manual_photos_byte_identical=all(sha(OUT/a['path'])==a['sha256'] for a in new['manual_original_images'])))
assert len(new['manual_dimensions'])==47 and len(new['plants'])==5
assert all(not a['eligible_for_accuracy_statistics'] for a in new['manual_dimensions'])
assert all(sha(ROOT/k)==v for k,v in input_hashes.items())
assert sum(len(p['dimensions']) for p in new['plants'])==47

def e(x):return html.escape(str(x))
def num(x,n=2):return 'Unavailable' if x is None else f'{x:.{n}f}'
parts=['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Five-plant traits — confirmed board</title><style>body{margin:0;background:#091a24;color:#e4edf2;font:16px/1.55 system-ui}main{max-width:1250px;margin:auto;padding:32px}h1,h2,h3{line-height:1.2}a{color:#84dfdd}.banner{padding:20px;background:#184149;border-left:5px solid #72dbce;border-radius:8px}section{margin:34px 0}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}.card{padding:16px;background:#102c3b;border:1px solid #33505f;border-radius:10px}img{width:100%;border-radius:5px}table{border-collapse:collapse;width:100%;font-size:14px}th,td{text-align:left;padding:10px;border-bottom:1px solid #355160;vertical-align:top}th{background:#183c4b}.scroll{overflow:auto}small,.muted{color:#b4c8d2}details{padding:12px;background:#112d3b;margin:10px 0}summary{cursor:pointer;font-weight:650}.pill{display:inline-block;background:#6b4d14;border-radius:4px;padding:2px 7px}code{font-size:13px}</style><main><h1>Five-plant traits after confirmed-board calibration</h1><p>28 September 2026 dataset · Current recalculation: 8 October 2026</p><div class="banner"><strong>Board dimensions resolved:</strong> Saswat supplied 25 mm checker squares and 18 mm markers on the 7 × 10 DICT_4X4_50 target. Current dimensions use this metric reference. <strong>Anatomical validation remains incomplete:</strong> 47 manual records are retained, with zero eligible independent accuracy pairs. No plant-height, complete-leaf-length or width accuracy score is reported.</div><p>The reconstruction contains observed surfaces only. Display-Z span is not stem-base-to-tip height; projected XY hull is not leaf area. Image masks were reused unchanged. Geometry cleanup uses the same physical tolerances after recalibration.</p><p><a href="website_tables.json">Complete table JSON</a> · <a href="canopy_descriptors.csv">Observed geometry CSV</a> · <a href="manual_dimensions_website.csv">All 47 manual records</a> · <a href="before_vs_after.json">Before / after recheck</a> · <a href="provenance.json">Provenance</a></p><section><h2>Current observed geometry</h2><div class="scroll"><table><tr><th>Plant</th><th>Retained points</th><th>D405 / L515</th><th>Observed X / Y / display-Z (cm)</th><th>XY hull (cm²)</th><th>Manual height annotation (cm)</th><th>Accepted height</th></tr>']
for p in new['plants']:parts.append(f"<tr><td>{p['id']}</td><td>{p['points']:,}</td><td>{p['d405_points']:,} / {p['l515_points']:,}</td><td>{' / '.join(num(x) for x in p['observed_span_cm'])}</td><td>{num(p['hull_cm2'])}</td><td>{num(p['manual_height_cm'])}</td><td>Unavailable</td></tr>")
parts.append('</table></div><p class="muted">Metre/cm coordinates are referenced to the supplied board pitch. Printed-size uncertainty, empirical L515 gain, alignment error and missing anatomy still limit physical interpretation. Fitted-board display normal is not independently verified gravity.</p></section><section><h2>What changed, and what did not</h2><p>D405 lengths increased by 2.8875% under the board-derived scale correction. L515 was rebuilt and aligned again. Re-running the same physical cleanup rules retained 430,060 points, versus 435,917 historically. This count reduction is not a quality score. No missing surface was filled.</p><div class="scroll"><table><tr><th>Plant</th><th>Historical points</th><th>Current points</th><th>Historical XY hull (conditional cm²)</th><th>Current XY hull (board cm²)</th></tr>')
for a in before_after:parts.append(f"<tr><td>{a['plant_id']}</td><td>{a['old_points']:,}</td><td>{a['new_points']:,}</td><td>{num(a['old_xy_hull_conditional_cm2'])}</td><td>{num(a['new_xy_hull_board_cm2'])}</td></tr>")
parts.append('</table></div></section><section><h2>Three observed chords; two unsupported endpoint attempts</h2><p>Frozen source-image clicks and exact original D405 point IDs were retained. Candidate endpoints were not selected again to improve agreement. Four-pixel-disk ranges describe endpoint sensitivity, not confidence intervals.</p><div class="scroll"><table><tr><th>Observed structure</th><th>Chord (cm)</th><th>Endpoint sensitivity range (cm)</th><th>Scope / limitation</th></tr>')
for a in new['chords']:parts.append(f"<tr><td>{e(a['id'])}</td><td>{num(a['estimate_cm'],4)}</td><td>{' – '.join(num(x,3) for x in a['endpoint_disk_sensitivity_cm']) if a['endpoint_disk_sensitivity_cm'] else 'No supported pair'}</td><td>{e(a['scope'])}<br><small>{e(a['limitation'])}</small></td></tr>")
parts.append('</table></div><p>All six selected endpoints of the three numerical chords survive as current plant core points. P3’s historical base candidate pool has one point now marked uncertain; the full-fusion source-disk range is retained explicitly, with a separate cleaned-only range in JSON. One old L515 point in P5’s tip pool cannot map to the rebuilt cloud and is excluded; the other 73 candidates map exactly. The two missing-tip searches were repeated on the current cleaned cloud and still found zero candidates. <a href="chord_pool_remap_audit.json">Pool membership audit</a> · <a href="missing_endpoint_recheck.json">Missing-tip recheck</a></p><p class="banner">P3.O03 moved from <strong>7.4753 conditional cm to 7.6911 board-referenced cm</strong>. Against the operator-only 7.5 cm annotation, the arithmetic difference changed from −0.0247 to +0.1911 cm. The former near-match was not evidence of accuracy. The base definition remains tentative, and no validation metric is calculated.</p></section>')
for p in new['plants']:
    parts.append(f"<section id='{p['id']}'><h2>{p['id']} — source evidence and manual records</h2><div class='cards'><div class='card'><a href='{p['photo']}'><img src='{p['photo']}' loading='lazy'></a><p>Current projection: observed top and base-region candidates, neither accepted as a true anatomical endpoint.</p></div><div class='card'><a href='{p['manual_overview']}'><img src='{p['manual_overview']}' loading='lazy'></a><p>Frozen operator annotation; values and ambiguities remain unchanged.</p></div></div><p>{e(p['identity_evidence'])}</p><p><strong>Height exclusion:</strong> {e(p['height_reason'])}</p><div class='scroll'><table><tr><th>Record</th><th>Annotation (cm)</th><th>Photo candidate (cm)</th><th>Geometry (cm)</th><th>Status and exclusion</th><th>Evidence</th></tr>")
    for a in p['dimensions']:
        links=[f"<a href='{e(a['annotation_photo'])}'>Annotation</a>"]+[f"<a href='{e(x)}'>Ruler {j+1}</a>" for j,x in enumerate(a['ruler_photos'])]
        parts.append(f"<tr><td>{e(a['id'])}<br><small>{e(a['organ_kind'])}</small></td><td>{num(a['annotation_cm'])}</td><td>{num(a['ruler_cm'])}</td><td>{num(a['estimate_cm'],4)}</td><td><span class='pill'>{e(a['status'])}</span><br>{e(a['reason'])}<br><small>{e(a['photo_evidence_limit'])}</small></td><td>{'<br>'.join(links)}</td></tr>")
    parts.append('</table></div></section>')
parts.append('<section><h2>Remaining scientific gaps</h2><ul>')
for m in new['missing_deliverables']:parts.append(f"<li><strong>{e(m['missing'])}.</strong> {e(m['impact'])}</li>")
parts.append('</ul><p>Manual P1.O03 width remains 9 cm as originally annotated; the photograph suggests about 0.8 cm (0.6–1.0 cm). This conflict is not silently corrected. P4 organ identity and P1 ear-versus-leaf distinctions remain explicit. Photos of a changed plant cannot retrospectively validate its earlier scan.</p></section><section><h2>Historical evidence archive</h2><p>The following frozen reports include old scale assumptions and superseded point counts. Their image/ruler evidence is retained, with a prominent archive banner. Use current tables above for geometry.</p><p><a href="archive/pre_confirmed_board/reports/trait_review/index.html">Historical trait review</a> · <a href="archive/pre_confirmed_board/reports/measurement_readiness/index.html">Historical measurement readiness</a></p></section></main></html>')
(OUT/'index.html').write_text(''.join(parts),encoding='utf-8')
save(OUT/'verification.json',dict(plants=5,manual_dimensions=47,source_unchanged=True,manual_photos_original=True,source_point_identity_remap=True,all_selected_endpoints_d405=True,all_current_endpoint_pools_d405=True,excluded_historical_l515_pool_points=1,eligible_accuracy_pairs=0,board_dimensions_operator_confirmed=True,physical_accuracy_validated=False,current_cleanup_points=sum(p['points'] for p in new['plants']),trait_source=rel(TRAITS),site=rel(OUT)))
print(json.dumps({'site':rel(OUT),'points':[p['points'] for p in new['plants']],'spans_cm':[p['observed_span_cm'] for p in new['plants']],'hulls_cm2':[p['hull_cm2'] for p in new['plants']],'p3_chord_cm':chordmap['P3.O03.blade_chord']['chord_cm']},indent=2))
