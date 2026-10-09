from pathlib import Path
import json,numpy as np,cv2
R=Path.cwd();B=R/'generated/research_confirmed_board_20261007';D=R/'generated/research_20260928_improvement_20261007/short_dense_v3';load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
a=next(x for x in load(R/'generated/research_sprint_review_20261008/traits_audit/batch_endpoint_probes.json') if x['id']=='P5.O04.length_candidate');p=np.array([x['xyz_m'] for x in a['endpoints']]);T=np.array(next(x['transform'] for x in load(B/'d405_metric/icp_diagnostics_reexpressed.json') if x['frame']==1055904));pr=load(D/'profile.json');K=np.array(pr['K']);ds=np.array(pr['dist']);pc=(p-T[:3,3])@T[:3,:3];uv=cv2.projectPoints(pc,np.zeros(3),np.zeros(3),K,ds)[0].reshape(-1,2);print('P5O04sourceorigin questionable, tip:',uv.tolist())
