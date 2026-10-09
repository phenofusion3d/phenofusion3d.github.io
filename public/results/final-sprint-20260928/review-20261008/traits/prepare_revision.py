from pathlib import Path
import json
O=Path('generated/research_sprint_review_20261008/traits_audit')
r=json.loads((O/'batch_frozen_endpoint_specs.json').read_text())
rev=[]
for mid,pts,why in [('P5.O02.length',[[533,404],[589,413]],'Three-view venation review showed the first batch axes were reversed; this is basal lamina to true terminal margin.'),('P5.O02.width',[[545,378],[549,432]],'Three-view venation review showed the first batch axes were reversed; this is the opposing side-margin chord across the midrib.'),('P3.O01.length',[[655,477],[717,499]],'Original basal click lay on the crossing flowering stalk; new frozen click is at first visible lamina junction on the correct leaf. This may omit hidden basal tissue.')]:
 a=next(q for q in r if q['manual_dimension_id']==mid).copy();a['id']=mid+'_revision';a['points']=pts;a['scope']=why;rev.append(a)
(O/'revision_frozen_endpoint_specs.json').write_text(json.dumps(rev,indent=2)+'\n')
s=(O/'batch_endpoints.py').read_text().replace("batch_frozen_endpoint_specs.json","revision_frozen_endpoint_specs.json").replace("batch_endpoint_probes.json","revision_endpoint_probes.json").replace("batch_endpoint_candidates.npz","revision_endpoint_candidates.npz")
(O/'revision_endpoints.py').write_text(s)
