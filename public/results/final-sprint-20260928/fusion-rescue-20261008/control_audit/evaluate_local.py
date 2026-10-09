from pathlib import Path
import json, numpy as np, cv2, hashlib
from PIL import Image,ImageDraw
R=Path.cwd();O=Path(__file__).resolve().parent;L=R/'generated/research_fusion_rescue_20261008/local_registration';rows=json.loads((O/'reserved_evaluation_private.json').read_text(encoding='utf-8'));results=[]
for name in ['primary_mind_rgb','pyramid_mind_rgb','mutual_information_affine','pyramid_mind_foreground']:
 p=L/(name+'.npz');a=np.load(p);print(name,a.files);A=a['initial_HSI_rotated_to_native_RGB'];crop=a['source_crop_xyxy'];f=a['forward_displacement_rgb_px'];rec=[]
 def predict(q):
  z=A@np.r_[q,1];v=z-crop[:2];disp=cv2.remap(f,np.array([[v[0]]],np.float32),np.array([[v[1]]],np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=float('nan'))[0,0];return z+disp
 for r in rows:
  if not r['id'].startswith('reserved_green'):continue
  q=np.array(r['hsi_rotated_xy']);pred=predict(q);initial=A@np.r_[q,1];J=np.column_stack([predict(q+[1,0])-predict(q-[1,0]),predict(q+[0,1])-predict(q-[0,1])])/2;bound=float(np.linalg.norm(J,2)*r['hsi_uncertainty_radius_px']+r['RGB_uncertainty_radius_px']);err=float(np.linalg.norm(pred-r['native_RGB_xy']))
  rec.append(dict(id=r['id'],prediction_native_RGB_xy=pred.tolist(),error_RGB_px=err,initial_error_RGB_px=float(np.linalg.norm(initial-r['native_RGB_xy'])),subjective_worst_direction_uncertainty_bound_RGB_px=bound,error_exceeds_subjective_bound=bool(err>bound),confidence=r['confidence'],eligible_for_strict_accuracy_gate=False,interpretation='Exploratory image correspondence check only; uncertainty is subjective, not a confidence interval.'))
 results.append(dict(candidate=name,path=str(p.relative_to(R)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),checks=rec))
(O/'blind_local_registration_evaluation.json').write_text(json.dumps(dict(evaluation_labels_frozen_sha256=hashlib.sha256((O/'fresh_landmark_specs_frozen.json').read_bytes()).hexdigest(),results=results),indent=2)+'\n',encoding='utf-8')
print(json.dumps(results,indent=2))

