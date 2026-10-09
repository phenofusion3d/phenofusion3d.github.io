"""Rebuild six exact source associations on new metric cleanup; preserve old results."""
from pathlib import Path
import argparse,base64,copy,hashlib,importlib.util,json,re,shutil,subprocess
import numpy as np
from processing.research_workspace.spectral_fusion import build
from reexpress_d405_metric import ply_read
ROOT=Path(__file__).resolve().parents[2];BASE=Path(__file__).resolve().parent
OLD=ROOT/'generated/research_spectral_extension_20261007'
UI=ROOT/'generated/final_sprint_website_20261007/spectral_site'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def replace(t,a,b):
 assert t.count(a)==1,(t.count(a),a[:100]);return t.replace(a,b)
def arrays_equal(a,b):return a.dtype==b.dtype and a.shape==b.shape and (np.array_equal(a,b,equal_nan=True) if a.dtype.kind in 'fc' else np.array_equal(a,b))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--cleanup',required=True);args=ap.parse_args();cleanup=Path(args.cleanup).resolve()
 clean=json.loads((cleanup/'summary.json').read_text());metric=json.loads((BASE/'d405_metric_calibration.json').read_text());s=metric['metres_per_previous_filename_unit'];R=np.asarray(clean['upright_R'])
 output=BASE/'spectral_metric_v1';site=BASE/'website/spectral'
 assert not output.exists() and not site.exists(),'Fresh metric result and website spectral directories are required'
 output.mkdir();site.parent.mkdir(parents=True,exist_ok=True)
 oldprovpath=ROOT/'generated/research_plant_cleanup_20261007/v1/result/P5_provenance.npz';oldprov=np.load(oldprovpath,allow_pickle=False);newprov=np.load(cleanup/'P5_provenance.npz',allow_pickle=False)
 config=json.loads((OLD/'reproduce_two_camera_fusion.json').read_text());config['frame_id']='D405_short_dense_v3_metric_reference';config['coordinate_unit']='m';config['upright_R']=R.tolist();config['title']='Five plants in metric RGB context; FX10 and FX17 at three provisional Plant 5 locations'
 for entry in config['sensors']:entry['result_dir']=str((OLD/entry['result_dir']).resolve())
 for entry in config['evidence']:entry['path']=str((OLD/entry['path']).resolve())
 config['clouds']=[dict(id=f'P{i}',label=f'Plant {i} — current metric cleaned tissue',cloud=str(cleanup/f'P{i}_reference.ply'),sha256=sha(cleanup/f'P{i}_reference.ply')) for i in range(1,6)]
 extra=[('confirmed_board',BASE/'board_confirmation.json'),('metric_calibration',BASE/'d405_metric_calibration.json'),('metric_cleanup',cleanup/'summary.json'),('old_P5_source_identity',oldprovpath),('new_P5_source_identity',cleanup/'P5_provenance.npz'),('shared_calibration_plane',BASE/'hsi_geometry/shared_plane_calibration.json'),('measured_scan_transfer',BASE/'hsi_geometry/scan_transfer_v1/scan_transfer.json'),('failed_height_model_diagnostic',BASE/'hsi_geometry/height_model_diagnostic/height_diagnostic.json')]
 config['evidence'] += [dict(id=k,path=str(p),sha256=sha(p)) for k,p in extra]
 remaps=[]
 for row in config['associations']:
  before=row['point_index'];camera=int(oldprov['camera_id'][before]);sourceid=int(oldprov['original_point_index'][before]);assert camera==0,'This remap expects original D405 features'
  ids=np.flatnonzero((newprov['camera_id']==camera)&(newprov['original_point_index']==sourceid));assert len(ids)==1,(row['id'],camera,sourceid,len(ids))
  after=int(ids[0]);row['point_index']=after;row['localized_reference_xyz']=(np.array(row['localized_reference_xyz'])*s).tolist();row['maximum_vertex_distance']*=s
  row.update(prior_cleanup_point_index=before,source_camera='D405',original_D405_full_scene_point_index=sourceid,source_identity_remap='Exact source camera + original full-scene point index; no spatial nearest-neighbour mapping',new_cleanup_provenance_sha256=sha(cleanup/'P5_provenance.npz'),metric_scale_factor=s,height_model_status='Three-control generalization test failed; existing association remains provisional and is not a calibrated projection')
  row['evidence_ids'] += [k for k,p in extra]
  remaps.append(dict(id=row['id'],source_camera_id=camera,original_D405_full_scene_point_index=sourceid,old_P5_row=before,new_P5_row=after))
 dump(output/'metric_fusion_config.json',config)
 scientific=output/'result';build(output/'metric_fusion_config.json',scientific,progress=lambda v:print(v,flush=True))
 scientific_summary=json.loads((scientific/'summary.json').read_text());scientific_summary.update(metric_scale_status='Operator-confirmed 25 mm cells; source print measurement uncertainty was not provided',board_dimensions_resolved=True,absolute_metric_scale_independently_remeasured=False,source_identity_remapping=remaps)
 dump(scientific/'summary.json',scientific_summary)
 # All spectral values and identities remain exactly the previously saved values.
 for camera in ['fx10','fx17']:
  with np.load(OLD/f'result/assigned_spectra_{camera}.npz',allow_pickle=False) as a,np.load(scientific/f'assigned_spectra_{camera}.npz',allow_pickle=False) as b:
   for k in a.files:
    if k in ['source_point_index','xyz_reference','xyz_upright']:continue
    assert arrays_equal(a[k],b[k]),(camera,k)
   # Metric D405 points have exactly the same original source IDs, not scaled mixed-cloud rows.
   assert np.max(np.abs(b['xyz_reference']-a['xyz_reference']*s))<1e-12
 shutil.copytree(scientific,site/'fusion');shutil.copytree(UI/'samples',site/'samples')
 for name in ['index.html','measurement_inventory.json']:
  shutil.copy2(UI/name,site/name)
 # Adapt only the fresh public copy of the scientific viewer.
 t=(UI/'fusion/index.html').read_text(encoding='utf-8')
 t=t.replace('href="clouds/cloud_0.ply">Plant 5','href="clouds/cloud_4.ply">Plant 5')
 t=t.replace('Physical units remain conditional.','Physical units now use the operator-confirmed 25 mm board. Spatial spectral correspondence remains provisional.')
 t=replace(t,'<p class="coverage"', '<p style="padding:12px 26px;background:#354b39;margin:0"><strong>Confirmed-board update:</strong> 25 mm cells, 18 mm markers. The shared calibration plane and scan transfer are supported; the three-point height model failed held-out prediction. <a href="../geometry-diagnostics/index.html">Calibration evidence and limits</a></p><p class="coverage"')
 (site/'fusion/index.html').write_text(t,encoding='utf-8')
 context=site/'fusion/context';context.mkdir()
 xyzs=[];rgbs=[];items={};offset=0
 for i in range(1,6):
  label=f'P{i}';src=cleanup/f'{label}_reference.ply';header,rec=ply_read(src);xyz=np.column_stack([rec[k] for k in 'xyz'])@R.T;rgb=np.column_stack([rec[k] for k in ['red','green','blue']]);xyzs.append(xyz);rgbs.append(rgb)
  shutil.copy2(src,context/src.name);items[label]=dict(offset=offset,count=len(xyz),centre=((xyz.min(0)+xyz.max(0))/2).tolist(),scale=float(np.ptp(xyz,axis=0).max()),source=str(src.relative_to(ROOT)),source_sha256=sha(src),download='context/'+src.name,spectral_associations=6 if i==5 else 0);offset+=len(xyz)
 XYZ=np.concatenate(xyzs);RGB=np.concatenate(rgbs)
 payload=dict(plants=items,all=dict(offset=0,count=len(XYZ),centre=((XYZ.min(0)+XYZ.max(0))/2).tolist(),scale=float(np.ptp(XYZ,axis=0).max())),xyz_upright_float64=base64.b64encode(XYZ.astype('<f8').tobytes()).decode(),rgb_uint8=base64.b64encode(RGB.tobytes()).decode(),upright_R=R.tolist(),frame_id=config['frame_id'],coordinate_unit='m')
 (context/'context_data.js').write_text('const PLANT_CONTEXT='+json.dumps(payload,separators=(',',':'))+';\n',encoding='utf-8')
 dump(context/'provenance.json',{k:v for k,v in payload.items() if k not in ['xyz_upright_float64','rgb_uint8']})
 t=(site/'index.html').read_text(encoding='utf-8')
 t=t.replace('Physical scale and calibration-board dimensions also remain unresolved.','The board dimensions are now confirmed: 25 mm cells and 18 mm markers. The D405 geometry has been expressed in that metric scale. A shared table-plane calibration and static scan transfer are saved; the three-control height model failed its untouched-point tests, so dense spectral projection is not accepted.')
 t=t.replace('<p>PHENOFUSION3D · 28 SEPTEMBER 2026 DATA · FINAL SPRINT</p>','<p>PHENOFUSION3D · 28 SEPTEMBER 2026 DATA · CONFIRMED-BOARD RESULTS</p>')
 t=t.replace('<a href="site_adaptation.json">','<a href="geometry-diagnostics/index.html">Calibration and failed-height diagnostic</a> · <a href="site_adaptation.json">')
 (site/'index.html').write_text(t,encoding='utf-8')
 inventory=json.loads((site/'measurement_inventory.json').read_text());inventory['limitations']=[x for x in inventory['limitations'] if not x.startswith('Board pitch')];inventory['limitations']+=['Confirmed 25 mm board supplies metric scale; independent print dimension uncertainty is not provided.','The three-point height-dependent model failed held-out prediction and is not used for dense spectral mapping.'];inventory['unique_existing_vertices']=[dict(cloud='P5',vertex=v) for v in sorted({r['new_P5_row'] for r in remaps})];inventory['geometry_context_count']=len(XYZ);dump(site/'measurement_inventory.json',inventory)
 # Root can supplement this local guide with complete diagnostic folders without changing paths.
 (site/'geometry-diagnostics').mkdir();(site/'geometry-diagnostics/index.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Spectral calibration evidence</title><style>body{font:17px/1.6 system-ui;max-width:950px;margin:40px auto;padding:20px;color:#173443}a{color:#006a82}</style><p><a href="../index.html">Spectral results</a></p><h1>What the new calibration establishes</h1><p>The operator-confirmed 25 mm cells connect the three physical targets to a common metric calibration plane. Withheld-sheet tests and static background controls support the table-plane and calibration-to-plant scan-coordinate transfers.</p><p><strong>The three-point height model fails held-out prediction.</strong> Its untouched-point errors reach 174.70 pixels for FX10 and 123.43 pixels for FX17. It is not used to colour or assign spectra to additional plant points.</p><ul><li><a href="../../evidence/confirmed-board/hsi_geometry/index.html">Shared metric plane, exact controls and whole-sheet tests</a></li><li><a href="../../evidence/confirmed-board/hsi_geometry/scan_transfer_v1/index.html">Actual static source images and measured scan transfer</a></li><li><a href="../../evidence/confirmed-board/hsi_geometry/height_model_diagnostic/index.html">Failed height-model diagnostic and sensitivity tests</a></li></ul><p>Three sparse Plant 5 locations retain their existing provisional source-feature associations. Raw spectra stay unchanged. Plants 1–4 have no accepted 3D spectral association. Radiometric reference gaps remain separate from geometry.</p></html>''',encoding='utf-8')
 changes={};numeric_files=0
 for p in (UI/'samples').rglob('*'):
  if p.is_file():assert sha(p)==sha(site/'samples'/p.relative_to(UI/'samples'));numeric_files+=1
 output_manifest={'status':'new_metric_context_with_exact_source_identity_spectral_remap','script_sha256':sha(Path(__file__)),'prior_results_preserved':True,'all_prior_spectral_arrays_exact':True,'full_camera_space_sample_files_byte_identical':numeric_files,'unique_source_locations':3,'associations':6,'remappings':remaps,'geometry_source':str(cleanup.relative_to(ROOT)),'geometry_source_summary_sha256':sha(cleanup/'summary.json'),'geometry_context_points':len(XYZ),'per_plant_counts':{k:v['count'] for k,v in items.items()},'board_dimensions_resolved':True,'dense_spectral_projection':False,'height_diagnostic_decision':'failed held-out prediction; not applied','scientific_result':str(scientific.relative_to(ROOT)),'scientific_result_summary_sha256':sha(scientific/'summary.json')}
 dump(output/'identity_remap_validation.json',output_manifest);dump(site/'site_adaptation.json',output_manifest)
 jschecks=[]
 for p in site.rglob('*.html'):
  for n,script in enumerate(re.findall(r'<script(?:\s[^>]*)?>([\s\S]*?)</script>',p.read_text(encoding='utf-8'))):
   if not script.strip():continue
   temp=output/(p.relative_to(site).as_posix().replace('/','_')+f'.{n}.js');temp.write_text(script,encoding='utf-8');r=subprocess.run(['node','--check',str(temp)],text=True,capture_output=True);assert r.returncode==0,r.stderr;jschecks.append(p.relative_to(site).as_posix())
 dump(output/'site_validation.json',{'status':'pass','numeric_identity':output_manifest,'inline_javascript_syntax':jschecks,'browser_visual_test':'pending root','external_report_links':'Root copies confirmed-board evidence to website/evidence/confirmed-board/'})
 dump(site/'checksums.json',{p.relative_to(site).as_posix():sha(p) for p in sorted(site.rglob('*')) if p.is_file() and p!=site/'checksums.json'})
 print(json.dumps(output_manifest,indent=2))
if __name__=='__main__':main()
