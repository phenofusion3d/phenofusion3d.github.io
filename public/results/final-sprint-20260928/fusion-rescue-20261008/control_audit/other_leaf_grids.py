from pathlib import Path
import numpy as np, json
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path.cwd();O=Path(__file__).resolve().parent
h=np.rot90(np.clip(np.load(R/'generated/research_followthrough_20261007/spectral/fx10_display_rgb.npy')*255,0,255).astype('uint8'));r=np.array(Image.open(R/'data/main/test_plant_10-7/test_plant_20260928162354/rgb_1055904.png'))
for name,hl,rl in [('green_central',(1630,1815,435,205),(875,1020,438,330)),('variegated_right',(1850,2040,590,230),(1040,1210,480,340)),('red_lower',(1565,1780,820,530),(800,966,610,465)),('green_upper',(1720,1880,255,0),(920,1090,338,185))]:
 for typ,im,lim in [('hsi',h,hl),('rgb',r,rl)]:
  fig,ax=plt.subplots(figsize=(12,13));ax.imshow(im,interpolation='nearest');ax.set_xlim(lim[:2]);ax.set_ylim(lim[2:]);ax.set_xticks(np.arange((lim[0]//10)*10,lim[1]+1,10));ax.set_yticks(np.arange((lim[3]//10)*10,lim[2]+1,10));ax.tick_params(axis='x',rotation=90);ax.grid(alpha=.25);fig.tight_layout();fig.savefig(O/f'{name}_{typ}.png',dpi=100);plt.close(fig)
