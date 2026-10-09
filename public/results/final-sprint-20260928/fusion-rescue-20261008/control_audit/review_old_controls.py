from pathlib import Path
import json,numpy as np
from PIL import Image,ImageDraw
R=Path.cwd();O=Path(__file__).resolve().parent;src=R/'generated/research_spectral_fusion_20261007/registration_probe';load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));a=load(src/'localized_candidate_associations.json');q=[r for r in a['candidates'] if r['id'] in ['green_lower_0','green_lower_4','red_upper_6']];print(json.dumps(q,indent=2))
h=Image.fromarray(np.rot90(np.clip(np.load(R/'generated/research_followthrough_20261007/spectral/fx10_display_rgb.npy')*255,0,255).astype('uint8')));rgb=Image.open(R/'data/main/test_plant_10-7/test_plant_20260928162354/rgb_1055904.png').convert('RGB');canvas=Image.new('RGB',(1400,480*len(q)),'white');dr=ImageDraw.Draw(canvas)
for i,r in enumerate(q):
 for j,(im,xy) in enumerate([(h,[r['hsi_column_line'][1],1023-r['hsi_column_line'][0]]),(rgb,r['native_rgb_subpixel_xy'])]):
  x,y=xy;rad=45 if j==0 else 30;box=(int(x)-rad,int(y)-rad,int(x)+rad,int(y)+rad);crop=im.crop(box).resize((450,450),Image.Resampling.NEAREST);dd=ImageDraw.Draw(crop);cx=(x-box[0])*450/(2*rad);cy=(y-box[1])*450/(2*rad);dd.line((cx-12,cy,cx+12,cy),fill='yellow',width=2);dd.line((cx,cy-12,cx,cy+12),fill='yellow',width=2);canvas.paste(crop,(j*700+20,i*480+25));dr.text((j*700+20,i*480+5),r['id']+' '+('HSI' if j==0 else 'RGB'),fill='black')
canvas.save(O/'old_control_material_review.png')
