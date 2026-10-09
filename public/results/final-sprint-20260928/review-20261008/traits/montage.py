from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
O=Path('generated/research_sprint_review_20261008/traits_audit');rows=json.loads((O/'batch_endpoint_probes.json').read_text());RGB=Path('data/main/test_plant_10-7/test_plant_20260928162354')
accepted={r['endpoint_evidence'] for r in json.loads((O/'conditional_comparisons.json').read_text())}
for plant in [1,3,5]:
 rs=[r for r in rows if r['plant']==plant and r['chord_cm'] is not None]
 for page in range((len(rs)+3)//4):
  subset=rs[page*4:(page+1)*4];fig,axes=plt.subplots(len(subset),3,figsize=(16,len(subset)*3.7),squeeze=False)
  for row,(a,axs) in enumerate(zip(subset,axes)):
   for ax,pr in zip(axs,a['projections']):
    im=Image.open(RGB/f'rgb_{pr["frame"]}.png');uv=pr['pixel_xy'];xs=[t[0] for t in uv];ys=[t[1] for t in uv];cx=sum(xs)/2;cy=sum(ys)/2;sz=max(max(xs)-min(xs),max(ys)-min(ys),90)/2+30
    ax.imshow(im,interpolation='nearest');ax.set_xlim(cx-sz,cx+sz);ax.set_ylim(cy+sz*.7,cy-sz*.7);ax.plot(xs,ys,'y-o',markersize=4);[ax.text(x+3,y+3,str(i+1),color='magenta') for i,(x,y) in enumerate(uv)];ax.set_title(('CONDITIONAL: ' if a['id'] in accepted else 'NOT ACCEPTED: ')+f'{a["id"]} / {pr["frame"]} / {a["chord_cm"]:.2f}cm',fontsize=9);ax.axis('off')
  fig.tight_layout();fig.savefig(O/f'P{plant}_three_view_candidates_{page+1}.png',dpi=110);plt.close(fig)

