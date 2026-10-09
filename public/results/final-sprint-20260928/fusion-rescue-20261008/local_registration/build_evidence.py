"""Compact failure evidence; does not create a spectral surface display."""
from pathlib import Path
import json,cv2,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path.cwd();OUT=Path(__file__).resolve().parent
rows=json.loads((OUT/'old_control_checks.json').read_text())['rows']
rgb=cv2.cvtColor(cv2.imread(str(ROOT/'data/main/test_plant_10-7/test_plant_20260928162354/rgb_1055904.png')),cv2.COLOR_BGR2RGB)
fig,axes=plt.subplots(2,3,figsize=(13,9.8),constrained_layout=True)
fig.set_constrained_layout_pads(h_pad=.13,w_pad=.04,hspace=.07,wspace=.03)
for ax,r in zip(axes.flat,rows):
 ax.imshow(rgb); ax.set_xlim(980,1135);ax.set_ylim(575,450)
 for c in r['old_checks']:
  x,y=c['previous_observed_native_rgb'];px,py=c['predicted_native_rgb']
  ax.plot(x,y,'+',color='#00d5ff',markersize=11,markeredgewidth=2)
  ax.plot(px,py,'x',color='#ff7100',markersize=8,markeredgewidth=2)
  ax.plot([x,px],[y,py],color='#ffe044',linewidth=1.3)
 ax.set_title(r['candidate'].replace('_',' ')+'\n'+', '.join(f"{c['error_native_rgb_px']:.2f} px" for c in r['old_checks']),fontsize=10)
 ax.set_xlabel('Native RGB x (px)',fontsize=9);ax.set_ylabel('Native RGB y (px)',fontsize=9);ax.tick_params(labelsize=8)
fig.suptitle('Post-freeze registration checks: every candidate fails the prior 3 px screen\nCyan + = saved observed feature; orange × = candidate prediction; all controls remain provisional',fontsize=13)
fig.savefig(OUT/'registration_check_evidence.png',dpi=150);plt.close(fig)
print(OUT/'registration_check_evidence.png')
