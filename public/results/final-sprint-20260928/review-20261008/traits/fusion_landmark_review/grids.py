from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
R=Path.cwd();O=Path(__file__).resolve().parent
h=np.rot90(np.clip(np.load(R/'generated/research_followthrough_20261007/spectral/fx10_display_rgb.npy')*255,0,255).astype('uint8'));fig,ax=plt.subplots(figsize=(12,14));ax.imshow(h,interpolation='nearest');ax.set_xlim(1710,1910);ax.set_ylim(755,435);ax.set_xticks(range(1710,1911,10));ax.set_yticks(range(440,756,10));ax.grid(alpha=.3);fig.tight_layout();fig.savefig(O/'HSI_full_leaf_grid.png',dpi=110);plt.close(fig)
r=Image.open(R/'data/main/test_plant_10-7/test_plant_20260928162354/rgb_1055904.png');fig,ax=plt.subplots(figsize=(14,11));ax.imshow(r,interpolation='nearest');ax.set_xlim(945,1150);ax.set_ylim(585,435);ax.set_xticks(range(950,1151,10));ax.set_yticks(range(440,586,10));ax.grid(alpha=.3);fig.tight_layout();fig.savefig(O/'RGB_full_leaf_grid.png',dpi=110);plt.close(fig)
