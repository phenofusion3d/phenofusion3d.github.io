"""Save exact native spectra for a visibly labelled partial registration hypothesis."""
from pathlib import Path
import sys, json, hashlib, csv, shutil
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'venv/Lib/site-packages'),str(ROOT)]
import numpy as np
from processing.research_workspace.spectral_extract import extract_reviewed_spectra,read_envi_source
from processing.research_workspace.spectral_viewer import build_spectral_review,load_spectral_result
from processing.research_workspace.spectral_fusion_viewer import write_viewer
from processing.research_workspace.workflow import cloud_record
HERE=Path(__file__).resolve().parent; BASE=HERE/'partial_surface'; OUT=BASE/'result'
WARNING=('PARTIAL EXPLORATORY FUSION: measured spectra projected onto parts of two upper leaves of Plant 5. '
 'Local image alignment is approximate; point-wise physical correspondence is not validated. '
 'This is not complete five-plant fusion. Native FX10 and FX17 measurements remain separate. '
 'Outside the measured white-reference columns, normalized values and indices are unavailable; raw DN remains inspectable. '
 'The dark reference and panel reflectance are unconfirmed, so valid Q/Q0 values are exploratory signals, not calibrated reflectance.')
def save(p,a):p.write_text(json.dumps(a,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
def main():
 if OUT.exists():raise ValueError('Output already exists; preserve it and choose a new version.')
 z=np.load(BASE/'projection_hypothesis.npz');pix=z['fx10_column_line'];pid=z['current_P5_point_index'];region=z['region_id'];n=len(pix)
 metric=ROOT/'generated/research_confirmed_board_20261007';cp=metric/'cleanup_v1/result/P5_reference.ply';pp=metric/'cleanup_v1/result/P5_provenance.npz';prov=np.load(pp)
 R=np.array(json.loads((metric/'spectral_metric_v1/metric_fusion_config.json').read_text())['upright_R'])
 rec=cloud_record({'id':'P5','label':'Unchanged metric P5 geometry','cloud':str(cp)},ROOT,np.eye(3));original=rec['points'].copy();rec['points']=original@R.T
 assert np.array_equal(original[pid],z['reference_xyz'])
 tracks={};candidates=[];sources=[BASE/'projection_hypothesis.npz',BASE/'evidence.json',cp,pp]
 for rid,name in [(1,'upper_green'),(2,'upper_red')]:
  tp=HERE/f'physical_model/cross_sensor_upper/{name}_native_tracks.npz';t=np.load(tp);tracks[rid]=t;sources.append(tp)
  lookup={tuple(p):j for j,p in enumerate(t['fx10_column_line']) if t['valid_tracking'][j]}
  for i in np.flatnonzero(region==rid):
   j=lookup.get(tuple(pix[i]))
   if j is not None:candidates.append((int(i),j,float(t['cross_band_max_radius_fx17_px'][j])))
 candidates.sort(key=lambda r:(r[2],r[0]));seen_pixel=set();seen_point=set();fx17=[]
 for i,j,radius in candidates:
  target=tracks[int(region[i])]['fx17_integer_column_line'][j];key=tuple(target)
  if key in seen_pixel or int(pid[i]) in seen_point:continue
  seen_pixel.add(key);seen_point.add(int(pid[i]));fx17.append((i,j,target))
 selectors={'fx10':[(i,None,pix[i])for i in range(n)],'fx17':fx17}
 assert len(fx17)>0
 OUT.mkdir();(OUT/'inputs').mkdir();(OUT/'clouds').mkdir();(OUT/'evidence').mkdir()
 save(OUT/'run_status.json',{'complete':False,'status':'running'})
 shutil.copyfile(cp,OUT/'clouds/P5_reference.ply');shutil.copyfile(pp,OUT/'clouds/P5_provenance.npz');rec['packaged_cloud']='clouds/P5_reference.ply'
 evidence_links=[]
 for p in [BASE/'projection_hypothesis.npz',BASE/'evidence.json',HERE/'learned_registration/frozen_candidates.json',HERE/'control_audit/blind_learned_evaluation.json',HERE/'control_audit/blind_round2_learned_evaluation.json']:
  dest=OUT/'evidence'/p.name;shutil.copyfile(p,dest);evidence_links.append({'id':p.stem.replace('_',' '),'packaged_path':'evidence/'+p.name});sources.append(p)
 for name in ['upper_green','upper_red']:
  for suffix in ['registration.json','tracking_summary.json','registration.png','native_tracks.npz']:
   p=HERE/f'physical_model/cross_sensor_upper/{name}_{suffix}';shutil.copyfile(p,OUT/'evidence'/p.name);sources.append(p)
   evidence_links.append({'id':p.stem.replace('_',' '),'packaged_path':'evidence/'+p.name})
 arrays_by_sensor={};result_dirs={};rows=[];products={};validation={};extract_summaries={}
 for sensor,entries in selectors.items():
  configpath=ROOT/f'generated/research_spectral_extension_20261007/full_spectral_review/sensors/{sensor}/input_config.json';config=json.loads(configpath.read_text());sources.append(configpath)
  config.pop('source_config_provenance',None);config['dataset_label']=f'20260928 {sensor}: partial upper-leaf projection hypothesis';config['sampling']={'line_step':1,'column_step':1}
  mask=np.zeros((2127,1024 if sensor=='fx10' else 640),np.uint16)
  for i,j,(c,l)in entries:mask[l,c]=region[i]
  maskpath=OUT/'inputs'/f'{sensor}_pixels.npy';np.save(maskpath,mask)
  config['selection']={'review_status':'assistant_reviewed','provenance':WARNING+' Coordinates selected by frozen learned maps plus geometric and overlap-band checks; not independently surveyed correspondence.','label_mask_npy':str(maskpath),'label_names':{'1':'P5 upper green partial hypothesis','2':'P5 upper red partial hypothesis'}}
  cfg=OUT/'inputs'/f'{sensor}.json';save(cfg,config)
  es=extract_reviewed_spectra(cfg,OUT/'extractions'/sensor,progress=lambda t:print(sensor,t,flush=True));extract_summaries[sensor]=es
  result=OUT/'extractions'/sensor/'result';result_dirs[sensor]=result;arrays,_=load_spectral_result(result);arrays_by_sensor[sensor]=arrays
  source=read_envi_source(config['header'],config['data']);m=np.memmap(source.data,mode='r',dtype=source.dtype,offset=source.offset,shape=source.shape)
  raw=np.asarray(m[arrays['scan_line'],:,arrays['detector_column']]).copy();del m
  assert np.array_equal(raw,arrays['raw_DN'])
  refs=np.load(result/'reference_profiles.npz');xx=arrays['detector_column'];W=refs['W_board'][:,xx].T;D=refs['D_dark'][:,xx].T;valid=(arrays['band_quality_flags']&31)==0
  q=np.full(raw.shape,np.nan,np.float32);q0=q.copy();np.divide(raw.astype('float32')-D,W-D,out=q,where=valid);np.divide(raw,W,out=q0,where=valid)
  assert np.array_equal(q,arrays['Q_assumed_or_confirmed_dark'],equal_nan=True)and np.array_equal(q0,arrays['Q_zero_offset'],equal_nan=True)
  validation[sensor]={'samples':len(entries),'bands':source.shape[1],'source_DN_reread_exact':True,'Q_Q0_recomputed_exact':True,'all_band_normalization_valid_samples':int(valid.all(axis=1).sum()),'every_invalid_normalized_value_NaN':bool(np.isnan(q[~valid]).all()and np.isnan(q0[~valid]).all())}
  lookup={(int(c),int(l)):j for j,(c,l)in enumerate(zip(arrays['detector_column'],arrays['scan_line']))}
  local=[]
  for i,j,(c,l)in entries:
   k=lookup[(int(c),int(l))];point=int(pid[i]);rid=int(region[i]);row={'id':f'{sensor}_upper_{k:06d}','sensor_id':sensor,'sample_index':k,'cloud_id':'P5','point_index':point,'source_scan_line':int(l),'source_detector_column':int(c),'source_patch_id':rid,'mapping_input_row':i,'source_camera_id':int(prov['camera_id'][point]),'original_camera_point_index':int(prov['original_point_index'][point]),'fused_point_index':int(prov['fused_point_index'][point]),'source_cloud_sha256':rec['sha256'],'xyz_reference':original[point].tolist(),'xyz_upright':rec['points'][point].tolist(),'coordinate_unit':'m','status':'exploratory_partial_surface_not_physically_validated','feature_description':('Upper green'if rid==1 else'Upper red')+' leaf: approximate frozen image map; measured source spectrum; unknown point-wise association error.','vertex_distance':float(z['vertex_distance_m'][i]),'supporting_rgb_pairs':int(z['supporting_rgb_pairs'][i]),'mapping_error_rgb_px':None,'physical_registration_validated':False,'calibrated_reflectance':False,'fx10_linked_source_column_line':pix[i].tolist()}
   if j is not None:
    t=tracks[rid];row.update(fx17_tracking_row=int(j),fx17_passing_overlap_bands=int(t['passing_bands'][j]),fx17_cross_band_max_radius_px=float(t['cross_band_max_radius_fx17_px'][j]),fx17_subpixel_column_line=t['fx17_subpixel_column_line'][j].tolist())
   rows.append(row);local.append(row)
  local.sort(key=lambda r:r['sample_index']);assert [r['sample_index']for r in local]==list(range(len(entries)))
  export=dict(arrays);export.update(current_P5_point_index=np.array([r['point_index']for r in local],np.int64),mapping_input_row=np.array([r['mapping_input_row']for r in local],np.int64),source_camera_id=np.array([r['source_camera_id']for r in local],np.uint8),original_camera_point_index=np.array([r['original_camera_point_index']for r in local],np.int64),fused_point_index=np.array([r['fused_point_index']for r in local],np.int64),xyz_reference=np.array([r['xyz_reference']for r in local]),xyz_upright=np.array([r['xyz_upright']for r in local]),WARNING=np.array(WARNING))
  products[sensor]=f'assigned_spectra_{sensor}.npz';np.savez_compressed(OUT/products[sensor],**export)
 build_spectral_review(result_dirs,OUT/'spectra',progress=lambda t:print(t,flush=True))
 save(OUT/'associations.json',{'warning':WARNING,'associations':rows})
 fields=['id','sensor_id','sample_index','point_index','source_patch_id','source_scan_line','source_detector_column','mapping_input_row','vertex_distance','supporting_rgb_pairs','mapping_error_rgb_px','status']
 with(OUT/'associations.csv').open('w',newline='',encoding='utf-8')as f:w=csv.DictWriter(f,fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
 with(OUT/'assigned_points_reference.ply').open('w',encoding='ascii',newline='\n')as f:
  f.write(f'ply\nformat ascii 1.0\ncomment Exploratory associations; unchanged original vertices\nelement vertex {len(rows)}\nproperty double x\nproperty double y\nproperty double z\nend_header\n')
  for row in rows:f.write(' '.join(format(v,'.17g')for v in row['xyz_reference'])+'\n')
 summary={'status':'partial_exploratory_dense_surface_not_physically_validated','title':'Partial spectral surface · two upper leaves','warning':WARNING,'coordinate_unit':'m','sensor_counts':{s:len(v)for s,v in selectors.items()},'region_counts':{s:{'upper_green':sum(int(region[i])==1 for i,j,p in v),'upper_red':sum(int(region[i])==2 for i,j,p in v)}for s,v in selectors.items()},'context_points':len(original),'unique_geometry_points':len(set(r['point_index']for r in rows)),'sensor_products':products,'evidence':evidence_links,'physical_registration_validated':False,'accepted_for_measurement':False,'all_five_plants_complete':False,'full_leaf_coverage_claimed':False,'calibrated_reflectance':False,'spectral_interpolation':False,'cross_sensor_spectrum_concatenation':False,'geometry_positions_modified':False,'upright_R':R.tolist(),'FX17_intersections_before_duplicate_suppression':len(candidates),'FX17_duplicate_policy':'Smallest overlap-band tracking disagreement; one native pixel and one original vertex per sensor.','raw_measurements_are_exact':True,'mapping_uncertainty':'Sparse uncertain manual check disagreement does not define per-point error bounds. Residuals mix annotation uncertainty with model error.','display_region_selection_post_hoc':True,'inputs_sha256':{str(p.relative_to(ROOT)):sha(p)for p in sources},'numeric_validation':validation,'normalization':{s:v['normalization']for s,v in extract_summaries.items()}}
 write_viewer(OUT,{'P5':rec},rows,arrays_by_sensor,summary)
 page=(OUT/'index.html').read_text(encoding='utf-8')
 changes={'Interactive sparse spectral associations on recorded 3D geometry':'Partial exploratory spectral surface on unchanged 3D geometry','click an enlarged spectral marker.':'click a coloured spectral point.','Marker size is for inspection and does not represent a measured spectral footprint.':'Point size is for display; exact physical correspondence remains unvalidated.','Reviewed association':'Provisional mapped pixel','Show annotation markers through geometry':'Show spectral points through geometry (inspection only)','id="overlay" checked':'id="overlay"','id="rgb">':'id="rgb" checked>','Sparse existing vertices':'Existing mapped vertices',' sparse associations':' provisional surface points',' sparse provisional associations':' provisional surface points','gl.uniform1f(loc.size,13*ratio)':'gl.uniform1f(loc.size,2.5*ratio)','gl.uniform1f(loc.size,19*ratio)':'gl.uniform1f(loc.size,5*ratio)','best=225':'best=36','Physical units remain conditional.':'Coordinates use the confirmed-board metric reference; independent physical accuracy is unverified.','Status: provisional; independently unvalidated.':'Status: partial exploratory surface; point-wise accuracy unvalidated.','<header>':'<header><a href="../../index.html">← Experiment results and evidence</a>'}
 for a,b in changes.items():page=page.replace(a,b)
 page=page.replace('<button id="side">Side view</button>','<button id="side">Side view</button><button id="focus">Focus spectral leaves</button>')
 page=page.replace("$('sensor').onchange=changeSensor;", "$('focus').onclick=()=>{if(!filtered.length)return;const a=axes(),p=filtered.map(r=>r.xyz_display),dot=(x,v)=>x.reduce((s,t,j)=>s+t*v[j],0),xs=p.map(q=>dot(q,a.r)),ys=p.map(q=>dot(q,a.u)),loX=Math.min(...xs),hiX=Math.max(...xs),loY=Math.min(...ys),hiY=Math.max(...ys),w=canvas.clientWidth,h=canvas.clientHeight;zoom=Math.min(10,.46*1.22/Math.max((hiX-loX)*Math.min(h/w,1),(hiY-loY)*Math.min(w/h,1),.001));pan=[-(loX+hiX)*zoom/1.22*Math.min(h/w,1),-(loY+hiY)*zoom/1.22*Math.min(w/h,1)];};$('sensor').onchange=changeSensor;")
 (OUT/'index.html').write_text(page,encoding='utf-8');save(OUT/'summary.json',summary);save(OUT/'numeric_validation.json',validation)
 for p,h in [(ROOT/p,h)for p,h in summary['inputs_sha256'].items()]:assert sha(p)==h
 save(OUT/'verification.json',{'source_hashes_stable':True,'exact_native_spectra_reread':True,'unchanged_geometry_exact_identity':True,'unique_source_pixel_and_vertex_per_sensor':True,'invalid_normalization_preserved':True,'spatial_accuracy_certified':False})
 save(OUT/'run_status.json',{'complete':True,'status':summary['status']})
 print(json.dumps({'output':str(OUT),'sensor_counts':summary['sensor_counts'],'region_counts':summary['region_counts'],'validation':validation},indent=2),flush=True)
if __name__=='__main__':main()
