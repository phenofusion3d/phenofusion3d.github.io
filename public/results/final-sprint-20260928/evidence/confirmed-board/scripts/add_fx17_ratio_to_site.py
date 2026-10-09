"""Add a separately derived, strictly gated FX17 signal ratio to fresh viewers."""
from pathlib import Path
import csv,hashlib,json
import numpy as np
ROOT=Path(__file__).resolve().parents[2];BASE=Path(__file__).resolve().parent
SITE=BASE/'website/spectral';DIAG=ROOT/'generated/final_sprint_website_20261007/spectral_diagnostics'
NAME='SR_1301.56_1449.68_signal_ratio'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def replace(t,a,b):
 assert t.count(a)==1,(t.count(a),a[:80]);return t.replace(a,b)
def ratios(folder):
 with np.load(folder/'measured_spectra.npz',allow_pickle=False) as z:a={k:z[k].copy() for k in z.files}
 summary=json.loads((folder/'summary.json').read_text());bands=[105,147];assert np.array_equal(a['wavelength_nm'][bands],[1301.56,1449.68])
 result={}
 for field,key in [('Q_assumed_or_confirmed_dark','q'),('Q_zero_offset','q0')]:
  parts=a[field][:,bands].astype(float);ff=a['band_quality_flags'][:,bands];stable=parts[:,1]>.01;value=np.full(len(parts),np.nan);np.divide(parts[:,0],parts[:,1],out=value,where=stable);flags=np.zeros(len(parts),np.uint8);reference=np.zeros(len(parts),bool)
  for roi in ['white_roi','dark_roi']:
   lo,hi,_,_=summary['normalization'][roi];reference|=(a['scan_line']>=lo)&(a['scan_line']<hi)
  for bit,mask in [(1,np.any((ff&31)!=0,axis=1)),(2,np.any((ff&32)!=0,axis=1)),(4,~stable),(8,reference),(16,~np.isfinite(value))]:flags[mask]|=bit
  value[flags!=0]=np.nan;result[key]=value;result['flags_'+key]=flags
 result.update(sample_id=np.arange(len(a['raw_DN']),dtype=np.int32),scan_line=a['scan_line'],detector_column=a['detector_column'],patch_id=a['patch_id'])
 return result
def payload(r,source):
 p={k:([float(x) if np.isfinite(x) else None for x in a] if a.dtype.kind=='f' else a.tolist()) for k,a in r.items()}
 p.update(name=NAME,formula='Q1301.56/Q1449.68; Q0 separately',source_band_zero_based=[105,147],actual_wavelength_nm=[1301.56,1449.68],source_measured_npz_sha256=sha(source/'measured_spectra.npz'),scope='Exploratory reference-relative signal ratio. Not calibrated reflectance, water content, stress or health. Both bands require zero quality flags; denominator must exceed 0.01 Q units.')
 return p
def inspector(folder,p):
 (folder/'fx17_signal_ratio.js').write_text('const FX17_SIGNAL_RATIO='+json.dumps(p,separators=(',',':'),allow_nan=False)+';\n',encoding='utf-8')
 t=(folder/'index.html').read_text(encoding='utf-8');t=replace(t,'<script>const M=','<script src="fx17_signal_ratio.js"></script><script>const M=')
 t=replace(t,"current=0;band=0;mode='raw_DN';", "appendSignalRatio(d,A);current=0;band=0;mode='raw_DN';")
 func="""function appendSignalRatio(d,a){if(d.sensor!=='fx17')return;const r=FX17_SIGNAL_RATIO;if(d.summary.sample_count!==r.sample_id.length)throw Error('Ratio sample count mismatch');for(let i=0;i<r.sample_id.length;i++)if(r.sample_id[i]!==i||a.scan_line[i]!==r.scan_line[i]||a.detector_column[i]!==r.detector_column[i]||a.patch_id[i]!==r.patch_id[i])throw Error('Ratio source identity mismatch');d.index_names=[r.name];a.indices_dark=Float64Array.from(r.q,x=>x===null?NaN:x);a.indices_zero=Float64Array.from(r.q0,x=>x===null?NaN:x);a.index_flags_dark=Uint8Array.from(r.flags_q);a.index_flags_zero=Uint8Array.from(r.flags_q0);d.additional_descriptor={formula:r.formula,scope:r.scope,source_measured_npz_sha256:r.source_measured_npz_sha256};}
"""
 t=replace(t,'function values(){',func+'function values(){')
 t=replace(t,'method:data.summary}', 'method:data.summary,additional_descriptor:data.additional_descriptor||null}')
 t=replace(t,'<h1>Measured spectra explorer</h1>', '<h1>Measured spectra explorer</h1><p>FX17 also includes the separately derived <strong>1301.56/1449.68 signal ratio</strong> with strict quality masks. This is exploratory Q/Q0, not reflectance or a biological water/health score. <a href="fx17_signal_ratio.csv">Exact ratio values and flags</a></p>')
 (folder/'index.html').write_text(t,encoding='utf-8')
 with (folder/'fx17_signal_ratio.csv').open('w',newline='') as stream:
  fields=['sample_id','scan_line','detector_column','patch_id','q','q0','flags_q','flags_q0'];w=csv.writer(stream);w.writerow(fields)
  for i in range(len(p['sample_id'])):w.writerow([p[k][i] for k in fields])
 (folder/'source_checksums_before_signal_ratio.json').write_bytes((folder/'checksums.json').read_bytes())
 checks=json.loads((folder/'checksums.json').read_text());checks.update({n:sha(folder/n) for n in ['index.html','fx17_signal_ratio.js','fx17_signal_ratio.csv']});dump(folder/'checksums.json',checks)
def main():
 full_source=SITE/'samples/sensors/fx17';full=ratios(full_source)
 with np.load(DIAG/'fx17_ratio_samples.npz',allow_pickle=False) as prior:
  for k,v in full.items():assert np.array_equal(prior[k],v,equal_nan=True),(k,'derived value differs from verified diagnostics')
  assert str(prior['source_measured_npz_sha256'])==sha(full_source/'measured_spectra.npz')
 with (DIAG/'fx17_ratio_samples.csv').open(newline='') as stream:
  rows=list(csv.DictReader(stream));assert len(rows)==len(full['q'])
  for i,r in enumerate(rows):
   assert int(r['sample_id'])==i and int(r['scan_line'])==full['scan_line'][i] and int(r['detector_column'])==full['detector_column'][i]
   for k,c in [('q','Q1301_56_div_Q1449_68'),('q0','Q0_1301_56_div_Q0_1449_68')]:assert (not r[c] and np.isnan(full[k][i])) or float(r[c])==full[k][i]
 inspector(SITE/'samples',payload(full,full_source))
 sparse_source=SITE/'fusion/spectra/sensors/fx17';sparse=ratios(sparse_source);p=payload(sparse,sparse_source);inspector(SITE/'fusion/spectra',p)
 (SITE/'fusion/fx17_signal_ratio.js').write_text('const FX17_ASSOCIATION_RATIO='+json.dumps(p,separators=(',',':'),allow_nan=False)+';\n',encoding='utf-8')
 t=(SITE/'fusion/index.html').read_text(encoding='utf-8');t=replace(t,'<script src="fusion_data.js"></script>','<script src="fusion_data.js"></script><script src="fx17_signal_ratio.js"></script>')
 t=replace(t,'const $=id=>document.getElementById(id),D=FUSION,all=D.associations;',"""const $=id=>document.getElementById(id),D=FUSION,all=D.associations;
const ratio=FX17_ASSOCIATION_RATIO;D.sensors.fx17.index_names=[ratio.name];for(const row of all.filter(r=>r.sensor_id==='fx17')){const i=row.sample_index;if(row.source_scan_line!==ratio.scan_line[i]||row.source_detector_column!==ratio.detector_column[i])throw Error('Ratio association source identity mismatch');row.indices_dark=[ratio.q[i]];row.indices_zero=[ratio.q0[i]];row.index_flags_dark=[ratio.flags_q[i]];row.index_flags_zero=[ratio.flags_q0[i]];}
""")
 t=t.replace('<p>Original RGB colours show recorded geometry context,','<p>FX17’s 1301.56/1449.68 ratio is an exploratory reference-relative signal descriptor; it does not measure water content or health.</p><p>Original RGB colours show recorded geometry context,')
 (SITE/'fusion/index.html').write_text(t,encoding='utf-8')
 t=(SITE/'index.html').read_text(encoding='utf-8');t=t.replace('No saved descriptor is supported by the required wavelength set; missing wavelengths are never borrowed from FX10.','A separate exploratory Q1301.56/Q1449.68 signal ratio (and Q0 version) is available with strict flags. It is not calibrated reflectance or a water/health score. The six visible/NIR descriptors are unavailable; missing wavelengths are never borrowed from FX10.');(SITE/'index.html').write_text(t,encoding='utf-8')
 inventory=json.loads((SITE/'measurement_inventory.json').read_text());inventory['limitations']=[x for x in inventory['limitations'] if x!='FX17 has no supported saved descriptors; missing wavelengths are never borrowed from FX10.'];inventory['limitations'].append('FX17 has one separately derived exploratory Q/Q0 signal ratio; it is not a physiological measurement. The original visible/NIR descriptor set is unavailable.');inventory['fx17_additional_signal_ratio']={k:p[k] for k in ['name','formula','source_band_zero_based','actual_wavelength_nm','scope']};dump(SITE/'measurement_inventory.json',inventory)
 receipt={'status':'pass','source_full_csv_sha256':sha(DIAG/'fx17_ratio_samples.csv'),'source_full_npz_sha256':sha(DIAG/'fx17_ratio_samples.npz'),'source_methods_sha256':sha(DIAG/'methods_and_sources.json'),'full_sample_ids_verified':len(full['q']),'full_ratios_and_flags_exactly_match_saved_diagnostics':True,'sparse_pixel_ratios_computed_from_their_own_exact_spectra':p,'underlying_raw_and_Q_arrays_modified':False,'script_sha256':sha(Path(__file__))}
 dump(BASE/'spectral_metric_v1/fx17_ratio_viewer_validation.json',receipt);dump(SITE/'fx17_ratio_viewer_validation.json',receipt)
 dump(SITE/'checksums.json',{p.relative_to(SITE).as_posix():sha(p) for p in sorted(SITE.rglob('*')) if p.is_file() and p!=SITE/'checksums.json'})
 print(json.dumps({'full_samples':len(full['q']),'sparse_q':p['q'],'sparse_q0':p['q0'],'sparse_flags':p['flags_q']}))
if __name__=='__main__':main()
