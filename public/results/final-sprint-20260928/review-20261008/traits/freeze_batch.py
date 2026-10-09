from pathlib import Path
import json
O=Path('generated/research_sprint_review_20261008/traits_audit')
# Frozen against original colour images, before numerical reconstruction; no manual target enters selection.
specs=[]
def add(oid,frame,length,width,scope,secondary,kind='leaf'):
 for dim,points in [('length',length),('width',width)]:
  specs.append(dict(id=oid+'.'+dim+'_candidate',manual_dimension_id=oid+'.'+dim,plant=int(oid[1]),frame=frame,points=points,roles=['basal margin candidate','terminal margin candidate'] if dim=='length' else ['first opposite margin candidate','second opposite margin candidate'],secondary=secondary,scope=scope,organ_kind=kind))
add('P1.O03',459309,[[240,401],[149,379]],[[193,386],[191,394]],'Upper narrow blade; length excludes fine dry tip so partial only; width is visible green-blade section.',[143152,302754])
add('P1.O04',459309,[[232,412],[157,469]],[[201,430],[211,440]],'Ear body excluding awns; not a leaf.',[143152,302754],'ear')
add('P3.O01',824869,[[639,471],[717,499]],[[686,451],[682,507]],'Lateral lobed blade; selected basal junction and terminal margin, plus opposite lateral lobes.',[618150,1055904])
add('P3.O02',824869,[[651,416],[698,324]],[[636,364],[723,365]],'Lobed blade with basal hole; basal margin and terminal lobe, plus opposite lateral margins.',[618150,1055904])
add('P3.O03',824869,[[594,424],[590,326]],[[563,372],[633,375]],'Oval terminal blade including small basal lobes; base convention tentative; width is visible opposing side margins.',[618150,1055904])
add('P3.O04',824869,[[550,388],[506,318]],[[492,365],[563,346]],'Lobed blade; basal lobe boundary and terminal lamina candidate; opposite lateral lobes.',[618150,1055904])
add('P3.O05',824869,[[540,485],[431,479]],[[510,431],[516,521]],'Lobed blade; basal lamina margin revised from visibly crossing-stem candidate, not adjusted to reference; visible terminal and side lobes.',[618150,1055904])
add('P5.O01',1445026,[[523,334],[548,202]],[[473,290],[574,304]],'Green damaged lobed blade; lowest basal-lamina lobe extent to terminal margin; widest opposing basal lobes.',[1030829,1639585])
add('P5.O02',1445026,[[532,416],[547,378]],[[533,404],[590,411]],'Small central green blade; basal lamina to terminal tip; side-margin chord. Ruler mapping conditional.',[1030829,1639585])
add('P5.O03',1445026,[[603,420],[708,433]],[[659,363],[639,496]],'Rust-brown damaged blade; lamina base to distal curled terminal margin; side lobes. Curl differs from held ruler pose.',[1030829,1639585])
add('P5.O04',1445026,[[529,449],[548,583]],[[493,514],[596,509]],'Green broad blade; lowest basal side-lobe origin candidate to distal margin; terminal-lamina side margins, possibly different ruler section.',[1030829,1639585])
add('P5.O05',1445026,[[476,407],[343,437]],[[430,344],[448,451]],'Left-facing green lobed blade; basal lamina to distal tip; opposite side lobes.',[1030829,1639585])
(O/'batch_frozen_endpoint_specs.json').write_text(json.dumps(specs,indent=2)+'\n')
