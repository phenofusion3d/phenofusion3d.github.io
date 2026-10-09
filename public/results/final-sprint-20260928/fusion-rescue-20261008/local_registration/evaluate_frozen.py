"""Post-freeze check only: no fitting, model selection or parameter updates."""
from pathlib import Path
import json,hashlib,cv2,numpy as np
OUT=Path(__file__).resolve().parent;ROOT=Path.cwd()
init=json.loads((ROOT/'generated/research_sprint_review_20261008/multiview_probe/manual_init/manual_affine.json').read_text())
rows=[]
for name in ['primary_mind_rgb','sensitivity_stiff','sensitivity_gray','pyramid_mind_rgb','mutual_information_affine','pyramid_mind_foreground']:
 p=OUT/f'{name}.npz';z=np.load(p);D=z['forward_displacement_rgb_px'];crop=z['source_crop_xyxy']
 checks=[]
 for c in init['heldout_checks']:
  q=np.array(c['prediction'],np.float32);local=q-crop[:2]
  delta=cv2.remap(D,local[:1].astype(np.float32).reshape(1,1),local[1:].astype(np.float32).reshape(1,1),cv2.INTER_LINEAR)[0,0]
  predicted=q+delta;checks.append({'id':c['id'],'predicted_native_rgb':predicted.tolist(),'previous_observed_native_rgb':c['observed'],'error_native_rgb_px':float(np.linalg.norm(predicted-c['observed']))})
 rows.append({'candidate':name,'frozen_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'old_checks':checks,'passes_prior_3px_screen':all(c['error_native_rgb_px']<=3 for c in checks)})
record={'status':'POST_FREEZE_EVALUATION','policy':'Old controls previously available but excluded from fitting; parameters and candidate files frozen before errors computed. These are not newly independent physical ground truth; blind new checks are evaluated by separate auditor.',
 'rows':rows,'accepted_dense_3d_assignments':0,'geometry_modified':False,'not_a_selection_rule':'Report every run; do not choose the lowest heldout error as a new validated model.'}
(OUT/'old_control_checks.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
