from pathlib import Path
import hashlib,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 d=json.loads((HERE/'height_diagnostic.json').read_text());fig,axes=plt.subplots(1,2,figsize=(12,4.8),layout='constrained');rows=[]
 for i,(camera,s) in enumerate(d['per_sensor'].items()):
  labels=[f['held_out_id'].replace('fx17_track_','') for f in s['folds']];errors=[f['held_out_vector_error_px'] for f in s['folds']]
  axes[i].bar(labels,errors,color=['#b87048','#b87048','#a83735']);axes[i].set(title=camera.upper(),ylabel='Held-out source-pixel error (column + line)',ylim=(0,190));axes[i].tick_params(axis='x',labelsize=9)
  for j,e in enumerate(errors):axes[i].text(j,e+3,f'{e:.2f} px',ha='center')
  for f in s['folds']:
   r=f['held_out_residual_column_line'];rows.append(f'<tr><td>{camera.upper()}</td><td>{f["held_out_id"]}</td><td>{f["held_out_vector_error_px"]:.2f}</td><td>{r[0]:+.2f}, {r[1]:+.2f}</td><td>{f["fit"]["column_height_fit_normalized_condition_number"]:.1f}</td></tr>')
 fig.suptitle('Two P5 controls cannot predict the untouched third reliably: dense height projection rejected');fig.savefig(HERE/'held_out_failure.png',dpi=150);plt.close(fig)
 text='''BOUNDED HEIGHT-MODEL DIAGNOSTIC: FAILED GENERALIZATION

The known 25 mm board supports shared metric table-plane geometry. Static panel and paper controls support a small calibration-to-plant HSI scan-coordinate transfer. A separately reviewed, deduplicated paper-only RGB bridge provides an approximate calibration-camera-zero to plant-reference transform, with material conditioning and fold variation.

We tested whether these advances plus the three existing P5 feature correspondences could determine the three remaining height coefficients of a general linear pushbroom model. The plane model stays fixed. Each fold uses two P5 points to fit one line-height coefficient and two column-height coefficients, then predicts the untouched third point. Existing D405-localized points are scaled by the confirmed metric factor. Spectral source coordinates stay unchanged.

The model fails this test. FX10 held-out errors are 10.08, 14.48 and 174.70 pixels. FX17 errors are 7.24, 12.28 and 123.43 pixels. The two similar-height red points provide a poorly conditioned basis for predicting the distant green point: normalized condition numbers are 145.0 and 143.6. A single-coordinate 1 mm stress changes the green prediction by as much as 34.26 px for FX10 or 20.48 px for FX17. These stresses are explicit scenarios, not physical confidence bounds.

This is not fixed by claiming a small training error: two column-height coefficients can exactly fit two columns algebraically. It is also not evidence that a denser warp is justified. The available plane/frame assumptions, three source-feature correspondences and reconstructed point locations do not support this height model sufficiently. The test cannot uniquely attribute the failure to one element of that chain. It does not validate the previously provisional material identities.

DECISION
Do not use this fitted model to distribute spectra over the plant surface. Keep the six real source-pixel spectra at three manually/assistant-reviewed provisional P5 associations with their existing uncertainty labels. No new spectral point assignments or interpolated texture are created. The successful table-plane and scan-transfer diagnostics remain useful independent results.

NEXT EVIDENCE
Recover spatial camera intrinsics/rig geometry and/or record independently measured elevated controls spanning the plant volume and detector width. Establish calibration-to-plant frame transfer with broader or independently surveyed controls. Hold out whole heights or independent spatial groups. Verify feature identities and triangulated positions independently, especially beyond one plant. Use a physically constrained model and visibility checks before claiming dense 3D spectral fusion.

SAVED DETAILS
height_diagnostic.json retains every unchanged observed third point, prediction, residual vector, training identities, fitted coefficients, normalized singular values, and 35 sensitivity scenarios per fold: six RGB-frame variants, three plane-sheet variants, eighteen single-coordinate 1 mm stresses and eight training-pixel 1 px stresses. Six P5 folds were evaluated across both cameras. These are conditional geometry tests, not calibrated reflectance or physiology.
'''
 (HERE/'REPORT.txt').write_text(text,encoding='utf-8')
 page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Height-dependent spectral mapping: failed held-out diagnostic</title><style>body{font:16px/1.6 system-ui;background:#f2f4f5;color:#182c38}main{max-width:1100px;margin:auto;padding:24px}section{background:white;border-radius:10px;padding:22px;margin:20px 0}.stop{background:#ffeddf;border-left:5px solid #a63d29}img{width:100%;height:auto}table{border-collapse:collapse;width:100%;font-size:14px}th,td{padding:8px;text-align:left;border-bottom:1px solid #d0dade}pre{white-space:pre-wrap;font:14px/1.6 system-ui}a{color:#076c87}.scroll{overflow:auto}</style><main><p><a href="../index.html">Shared metric calibration plane</a> · <a href="../scan_transfer_v1/index.html">Measured scan transfer</a></p><h1>Can three existing P5 features recover the missing height model?</h1><section class="stop"><strong>The held-out test fails. Dense surface projection is not supported.</strong><p>Two controls were used to fit the three missing height terms, while the third measured correspondence was left untouched for prediction. The errors reach 174.70 pixels for FX10 and 123.43 pixels for FX17.</p></section><section><img src="held_out_failure.png" alt="Held-out errors for all three points of each hyperspectral camera"><div class="scroll"><table><thead><tr><th>Sensor</th><th>Untouched point</th><th>Error px</th><th>Column, line residual px</th><th>Normalized condition</th></tr></thead><tbody>'''+''.join(rows)+'''</tbody></table></div><p>The source spectra remain real recorded measurements. Their sparse spatial associations remain provisional; this failure prevents expanding them into a dense height-based spectral map.</p></section><section><h2>Evidence and interpretation</h2><p><a href="height_diagnostic.json">All controls, folds and sensitivity scenarios</a> · <a href="summary.json">Compact numeric results</a> · <a href="validation.json">Independent arithmetic checks</a></p><pre>'''+text.replace('&','&amp;').replace('<','&lt;')+'''</pre></section></main></html>'''
 (HERE/'index.html').write_text(page,encoding='utf-8')
 checks=[]
 for cam,s in d['per_sensor'].items():
  for f in s['folds']:
   a=np.array(f['predicted_003_column_line']);b=np.array(f['observed_003_column_line']);assert np.allclose(a-b,f['held_out_residual_column_line'],rtol=0,atol=1e-10)
   assert abs(np.linalg.norm(a-b)-f['held_out_vector_error_px'])<1e-10
   assert f['held_out_id'] not in f['training_ids'] and len(f['training_ids'])==2
   assert len(f['sensitivity_scenarios'])==35
  checks.append({'camera':cam,'all_three_folds_checked':True,'third_identity_not_in_training':True,'scenario_count_per_fold':35})
 (HERE/'validation.json').write_text(json.dumps({'status':'pass_for_computation_not_model_acceptance','checks':checks,'scientific_decision':'Model fails held-out prediction; no dense projection accepted.'},indent=2)+'\n')
 (HERE/'checksums.json').write_text(json.dumps({p.name:sha(p) for p in HERE.iterdir() if p.is_file() and p.name!='checksums.json'},indent=2)+'\n');print('Reports saved; six held-out predictions and 210 scenarios checked')
if __name__=='__main__':main()
