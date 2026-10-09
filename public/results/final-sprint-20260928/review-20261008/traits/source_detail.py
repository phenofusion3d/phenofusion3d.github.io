from pathlib import Path
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=Path('generated/research_sprint_review_20261008/traits_audit')
for plant,xlim,ylim in [('P3',(425,735),(600,290)),('P5',(325,730),(610,185))]:
 im=Image.open(f'generated/research_confirmed_board_20261007/traits_metric/assets/{plant}_source_raw.jpg')
 fig,ax=plt.subplots(figsize=(14,13));ax.imshow(im,interpolation='nearest');ax.set_xlim(*xlim);ax.set_ylim(*ylim);ax.set_xticks(range((xlim[0]//20)*20,xlim[1]+1,20));ax.set_yticks(range((ylim[1]//20)*20,ylim[0]+1,20));ax.grid(alpha=.35);fig.savefig(p/f'{plant}_source_detail.png',dpi=120);plt.close(fig)
