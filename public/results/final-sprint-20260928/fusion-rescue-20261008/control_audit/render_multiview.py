from pathlib import Path
import json,numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont
R=Path.cwd();O=Path(__file__).resolve().parent;B=R/'generated/research_confirmed_board_20261007';D=R/'generated/research_20260928_improvement_20261007/short_dense_v3';RGB=R/'data/main/test_plant_10-7/test_plant_20260928162354';load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
pr=load(D/'profile.json');K=np.array(pr['K']);dist=np.array(pr['dist']);poses={a['frame']:np.array(a['transform']) for a in load(B/'d405_metric/icp_diagnostics_reexpressed.json') if a['icp_accepted']};rows=load(O/'new_provisional_training.json')+load(O/'reserved_evaluation_private.json');h=np.rot90(np.clip(np.load(R/'generated/research_followthrough_20261007/spectral/fx10_display_rgb.npy')*255,0,255).astype('uint8'));h=Image.fromarray(h)
canvas=Image.new('RGB',(1200,230*len(rows)),'white');dr=ImageDraw.Draw(canvas)
for i,a in enumerate(rows):
 y0=i*230;dr.text((8,y0+6),a['id']+' | '+a['confidence']+' | observations remain provisional',fill='black')
 for j,fr in enumerate(['hsi',1055904,1445026,1884421]):
  if fr=='hsi':im=h;u,v=a['hsi_rotated_xy'];label='FX10 rotated';rad=35
  elif fr in poses:
   im=Image.open(RGB/f'rgb_{fr}.png').convert('RGB');T=poses[fr];pc=(np.array(a['reference_xyz_m'])-T[:3,3])@T[:3,:3];u,v=cv2.projectPoints(pc.reshape(1,3),np.zeros(3),np.zeros(3),K,dist)[0].reshape(2);label='RGB '+str(fr);rad=40
  else:continue
  crop=im.crop((int(u)-rad,int(v)-rad,int(u)+rad,int(v)+rad)).resize((190,190));dd=ImageDraw.Draw(crop);dd.line((88,95,102,95),fill='yellow',width=1);dd.line((95,88,95,102),fill='yellow',width=1);canvas.paste(crop,(j*300+10,y0+36));dr.text((j*300+10,y0+22),label,fill='black')
canvas.save(O/'control_multiview_support.jpg',quality=95)
