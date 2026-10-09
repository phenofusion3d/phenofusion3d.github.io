"""Plot actual retained landmark diagnostics; no point selection by residual."""
from pathlib import Path
import hashlib,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path.cwd();OUT=ROOT/'generated/research_confirmed_board_20261007/l515'
SOURCE=ROOT/'generated/research_l515_20261007/calibration/landmark_depth_check/landmark_samples.npz'
cal=json.loads((OUT/'metric_calibration.json').read_text());review=json.loads((OUT/'metric_landmark_depth_diagnostics.json').read_text())
track=np.load(SOURCE)['landmarks'];native=track[:,4]*.00025;rgb=track[:,3]*cal['metres_per_previous_filename_unit'];gain=cal['board_gain_over_retained_native_candidate']
residuals={'Native conversion':(native-rgb)*1000,'Board-only gain':(native*gain-rgb)*1000}
fig,axes=plt.subplots(1,2,figsize=(12,5.3),layout='constrained');colours=['#276a90','#a25a26']
for (name,res),c in zip(residuals.items(),colours):
 x=np.sort(abs(res));p=np.arange(1,len(x)+1)/len(x)
 axes[0].step(x,p,where='post',label=name,color=c)
axes[0].set_xscale('log');axes[0].set_xlim(.01,max(abs(v).max() for v in residuals.values())*1.05)
axes[0].set_ylim(0,1.01);axes[0].set_xlabel('Absolute axial disagreement / mm (log scale)');axes[0].set_ylabel('Fraction of retained landmarks');axes[0].grid(alpha=.2);axes[0].legend(loc='lower right',fontsize=9)
bins=review['depth_strata'];xs=np.arange(len(bins));w=.34
for j,(label,key,c) in enumerate([('Native conversion','native',colours[0]),('Board-only gain','board_gain',colours[1])]):
 y=[b[key]['median_signed_m']*1000 for b in bins];axes[1].bar(xs+(j-.5)*w,y,w,label=label,color=c)
axes[1].axhline(0,color='#555',lw=.7);axes[1].set_xticks(xs,[f"{b['metric_RGB_interval_m'][0]:g}–{b['metric_RGB_interval_m'][1]:g}\n(n={b['landmarks']})" for b in bins]);axes[1].set_xlabel('Metric RGB-predicted axial depth / m');axes[1].set_ylabel('Median sensor minus RGB-predicted depth / mm');axes[1].grid(axis='y',alpha=.2)
axes[0].set_title('All 3,733 landmarks; all residual tails retained',fontsize=11)
axes[1].set_title('The gain does not remove depth-dependent differences',fontsize=11)
fig.suptitle('L515 depth check after confirming 25 mm board squares',fontsize=14)
for ext in ['png','pdf','svg']:fig.savefig(OUT/f'metric_depth_diagnostic.{ext}',dpi=180)
plt.close(fig)
caption=("L515 diagnostics for the frozen cohort of 3,733 smooth multiview RGB landmarks. RGB depths use the independently board-derived camera-motion factor 1.0296675588864626. The native candidate is 0.00025 m/count; the board-only empirical gain is 1.0134562282967752, estimated exclusively from actual-size board images. The plant-scan landmark cohort was not used to fit that gain. The empirical CDF includes every absolute residual, with a logarithmic horizontal axis; bars show signed medians in the newly metric depth strata. Native versus board-gain median absolute disagreement is 15.642 versus 5.496 mm, P90 24.360 versus 12.450 mm, and RMS 43.193 versus 41.709 mm. These are internal cross-modal consistency diagnostics, not independent sensor accuracy. Shared intrinsics and motion assumptions, correlated observations, broad-surface selection, unresolved thin structures and missing recording-time depth units remain. Neither curve establishes a universal camera correction.\n")
(OUT/'metric_depth_diagnostic.caption.txt').write_text(caption,encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
provenance={'source_hashes':{str(p.relative_to(ROOT)):sha(p) for p in [SOURCE,OUT/'metric_calibration.json',OUT/'metric_landmark_depth_diagnostics.json',Path(__file__)]},'landmark_count':len(track),'same_frozen_landmark_ids':True,'residual_gate_or_trimming':False,'point_interpolation':False,'plots':{f'metric_depth_diagnostic.{e}':sha(OUT/f'metric_depth_diagnostic.{e}') for e in ['png','pdf','svg']}}
(OUT/'metric_depth_diagnostic.provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
print(caption)
