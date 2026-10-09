"""Finish site-only labels, separate diagnostic routes and audit exact numeric files."""
from pathlib import Path
import hashlib,json,re,subprocess
from urllib.parse import urlsplit,unquote
import numpy as np
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
SITE=BASE/'website/spectral'
OUT=BASE/'spectral_metric_v1'
OLD=ROOT/'generated/final_sprint_website_20261007/spectral_site'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n',encoding='utf-8')

src=(SITE/'diagnostics').resolve();dst=(SITE/'geometry-diagnostics').resolve()
assert src.parent==SITE.resolve() and dst.parent==SITE.resolve()
if src.exists() and not dst.exists():src.rename(dst)
assert dst.is_dir()
for rel in ['index.html','fusion/index.html']:
 p=SITE/rel;t=p.read_text(encoding='utf-8');t=t.replace('href="diagnostics/index.html"','href="geometry-diagnostics/index.html"').replace('href="../diagnostics/index.html"','href="../geometry-diagnostics/index.html"')
 if rel=='index.html':
  t=t.replace('all five original RGB plants','all five plants in the current metric RGB geometry').replace('compare bands or saved FX10 descriptors.','compare bands, six FX10 descriptors or the exploratory FX17 signal ratio.')
  t=t.replace('FX10 can calculate its six saved descriptors there.','FX10 can calculate its six saved descriptors there; FX17 supplies one separately derived signal ratio.')
  t=t.replace('<a href="geometry-diagnostics/index.html">Radiometric quality and sensitivity</a>','<a href="diagnostics/index.html">Radiometric quality and sensitivity</a>')
  if 'Radiometric quality and sensitivity' not in t:t=t.replace('<a href="geometry-diagnostics/index.html">Calibration and failed-height diagnostic</a>','<a href="geometry-diagnostics/index.html">Calibration and failed-height diagnostic</a> · <a href="diagnostics/index.html">Radiometric quality and sensitivity</a>')
 else:
  native=(OUT/'result/index.html').read_text(encoding='utf-8')
  pattern=r'(<h2>Correspondence evidence</h2><ul>)[\s\S]*?(</ul>)'
  native_evidence=re.search(pattern,native).group(0)
  t,n=re.subn(pattern,lambda m:native_evidence,t);assert n==1
 p.write_text(t,encoding='utf-8')

# Correct the reproducible builder as well, without rerunning or overwriting results.
p=BASE/'build_metric_spectral_site.py';t=p.read_text(encoding='utf-8')
t=t.replace("(site/'diagnostics')","(site/'geometry-diagnostics')").replace("(site/'diagnostics/index.html')","(site/'geometry-diagnostics/index.html')").replace('href="../diagnostics/index.html"','href="../geometry-diagnostics/index.html"').replace('href="diagnostics/index.html"','href="geometry-diagnostics/index.html"')
p.write_text(t,encoding='utf-8')

inventory=json.loads((SITE/'measurement_inventory.json').read_text(encoding='utf-8'))
inventory['limitations']=[('R1-R5 are scan-order regions, not verified 3D specimen identities.' if x.startswith('R1') else x) for x in inventory['limitations']]
p=SITE/'samples/fx17_signal_ratio.js';ratio=json.loads(p.read_text(encoding='utf-8').removeprefix('const FX17_SIGNAL_RATIO=').strip().removesuffix(';'))
inventory['sensors']['fx17']['additional_separately_derived_descriptors']=[dict(name=ratio['name'],finite_Q=sum(v is not None for v in ratio['q']),finite_Q0=sum(v is not None for v in ratio['q0']),formula=ratio['formula'],actual_wavelength_nm=ratio['actual_wavelength_nm'],scope=ratio['scope'])]
dump(SITE/'measurement_inventory.json',inventory)

exact=[]
for p in sorted((OLD/'samples/sensors').rglob('*')):
 if p.is_file():
  q=SITE/'samples'/p.relative_to(OLD/'samples');assert sha(p)==sha(q),q
  exact.append(dict(path=q.relative_to(SITE).as_posix(),sha256=sha(q)))
for where in [OUT/'identity_remap_validation.json',SITE/'site_adaptation.json']:
 d=json.loads(where.read_text());d['full_camera_space_sample_files_byte_identical_before_ui_adaptation']=d.pop('full_camera_space_sample_files_byte_identical',25)
 d['final_camera_space_sensor_files_byte_identical']=len(exact);d['final_camera_space_sensor_hashes']=exact
 d['fx17_signal_ratio']='Additional separately derived strict-flag descriptor; original NPZ/CSV/browser numeric payloads remain unchanged.'
 d['builder_final_sha256']=sha(BASE/'build_metric_spectral_site.py');dump(where,d)

for parent in [SITE/'samples',SITE/'fusion/spectra']:
 d=json.loads((parent/'checksums.json').read_text());d.update({p.relative_to(parent).as_posix():sha(p) for p in parent.rglob('*') if p.is_file() and p!=parent/'checksums.json'});dump(parent/'checksums.json',d)

# Adapt the prior bounded DOM behavior check to the new exact geometry and ratio.
t=(ROOT/'generated/final_sprint_website_20261007/audit_spectra/validate_site_runtime.cjs').read_text(encoding='utf-8')
t=t.replace("path.resolve(__dirname,'../spectral_site')","path.resolve(__dirname,'../website/spectral')").replace(',435917)',',430060)').replace(',74306)',',72786)').replace(',156185)',',154648)')
t=t.replace("s.run('data.index_names.length'),0)","s.run('data.index_names.length'),1)").replace("f.run('D.sensors[sensor].index_names.length'),0)","f.run('D.sensors[sensor].index_names.length'),1)")
t=t.replace("checks.push('All-five", """f.e('mode').value='indices_dark';f.e('mode').onchange();
f.e('point').onchange({target:{value:'2'}});assert(f.e('detail').textContent.includes('SR_1301.56_1449.68_signal_ratio / Q'));
assert(Math.abs(f.run('modeValue(filtered[2])')-4.8306622675896245)<1e-12);assert(f.e('detail').textContent.includes('Descriptor flags: 0'));
f.e('point').onchange({target:{value:'0'}});assert.equal(f.run('modeValue(filtered[0])'),null);assert(f.e('detail').textContent.includes('Descriptor flags: 21'));
const sparse=runtime(path.join(stage,'fusion/spectra/index.html'));sparse.e('sensor').value='fx17';sparse.e('sensor').onchange();
sparse.e('sample').value='2';sparse.e('selectSample').onclick();sparse.e('mode').value='index_dark_0';sparse.e('mode').onchange();
assert(sparse.e('selected').textContent.includes('scan line 1718'));assert(sparse.e('selected').textContent.includes('detector column 235'));
assert(sparse.e('value').textContent.startsWith('SR_1301.56_1449.68_signal_ratio'));assert(Math.abs(sparse.run('values()[2]')-4.8306622675896245)<1e-12);
assert(sparse.e('quality').textContent.includes('Descriptor flags 0'));assert.equal(sparse.e('band').disabled,true);
checks.push('Strict FX17 ratio displayed at exact green source pixel and marker; red missing value and flags remain explicit');
checks.push('All-five""")
(OUT/'validate_site_runtime.cjs').write_text(t,encoding='utf-8')
subprocess.run(['node',str(OUT/'validate_site_runtime.cjs')],check=True)
syntax=[]
for p in sorted(SITE.rglob('*.html')):
 for n,s in enumerate(re.findall(r'<script(?:\s[^>]*)?>([\s\S]*?)</script>',p.read_text(encoding='utf-8'))):
  if not s.strip():continue
  tmp=OUT/(p.relative_to(SITE).as_posix().replace('/','_')+f'.{n}.js');tmp.write_text(s,encoding='utf-8');r=subprocess.run(['node','--check',str(tmp)],capture_output=True,text=True);assert r.returncode==0,r.stderr;syntax.append(p.relative_to(SITE).as_posix())
links=[];pending=[]
for p in sorted(SITE.rglob('*.html')):
 for href in re.findall(r'(?:href|src)="([^"]+)"',p.read_text(encoding='utf-8')):
  parts=urlsplit(href)
  if parts.scheme or parts.netloc or not parts.path or any(x in parts.path for x in ["'+",'${']):continue
  target=(p.parent/unquote(parts.path)).resolve()
  item=dict(page=p.relative_to(SITE).as_posix(),href=href,exists=target.exists())
  if not target.exists():
   assert target.is_relative_to((BASE/'website/evidence/confirmed-board').resolve()) or target==(SITE/'diagnostics/index.html').resolve(),item
   pending.append(item)
  else:links.append(item)
result=dict(status='pass_with_parent_report_copy_pending' if pending else 'pass',numeric_sensor_files_exact=len(exact),original_scientific_values_changed=False,geometry_points=430060,associations=6,unique_locations=3,inline_javascript_syntax=syntax,existing_local_links=len(links),pending_parent_owned_report_links=pending,runtime_validation=json.loads((OUT/'runtime_validation.json').read_text()),browser_visual_test='Parent handles browser and WebGL validation separately',script_sha256=sha(Path(__file__)))
dump(OUT/'final_site_validation.json',result)
dump(SITE/'checksums.json',{p.relative_to(SITE).as_posix():sha(p) for p in sorted(SITE.rglob('*')) if p.is_file() and p!=SITE/'checksums.json'})
print(json.dumps(result,indent=2))
