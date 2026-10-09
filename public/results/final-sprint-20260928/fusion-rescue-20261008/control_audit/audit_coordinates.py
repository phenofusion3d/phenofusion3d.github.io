from pathlib import Path
import numpy as np, cv2, json, sys, hashlib
from PIL import Image,ImageDraw
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path.cwd();O=Path(__file__).resolve().parent; B=R/'generated/research_confirmed_board_20261007'; D=R/'generated/research_20260928_improvement_20261007/short_dense_v3';RGB=R/'data/main/test_plant_10-7/test_plant_20260928162354'
load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sys.path.insert(0,str(R/'generated/research_20260928_processing_20261007'))
from extract_P5_review_candidate import read_vertices,xyz
p=xyz(read_vertices(B/'cleanup_v1/result/P5_reference.ply'),slice(None));cfg=load(B/'spectral_metric_v1/metric_fusion_config.json');old=load(R/'generated/research_spectral_fusion_20261007/registration_probe/localized_candidate_associations.json');loc={a['id']:a for a in old['candidates']};pr=load(D/'profile.json');K=np.array(pr['K']);dist=np.array(pr['dist']);T={a['frame']:np.array(a['transform']) for a in load(B/'d405_metric/icp_diagnostics_reexpressed.json') if a['icp_accepted']}[1055904];To={a['frame']:np.array(a['transform']) for a in load(D/'result/icp_diagnostics.json') if a['icp_accepted']}[1055904]
s=1.0288746669066682
rows=[]
for a in cfg['associations']:
 id=a['id']; orig=id.removeprefix('fx17_track_');q=loc[orig];pt=p[a['point_index']];pc=(pt-T[:3,3])@T[:3,:3];uv=cv2.projectPoints(pc.reshape(1,3),np.zeros(3),np.zeros(3),K,dist)[0].reshape(2);ui=pc[:2]/pc[2]*[K[0,0],K[1,1]]+[K[0,2],K[1,2]]; po=np.array(q['nearest_cleaned_p5_reference_xyz']);pco=(po-To[:3,3])@To[:3,:3];uvo=cv2.projectPoints(pco.reshape(1,3),np.zeros(3),np.zeros(3),K,dist)[0].reshape(2)
 rows.append(dict(id=id,role='existing_exposed_selection_control_not_independent_validation',sensor='fx17' if id.startswith('fx17') else 'fx10',native_hsi_column_line=a['native_hsi_subpixel_column_line'],reference_xyz_m=pt.tolist(),reference_frame='D405_short_dense_v3_metric_reference',source_original_index=a['original_D405_full_scene_point_index'],new_P5_row=a['point_index'],native_RGB_mark_xy=q['native_rgb_subpixel_xy'],native_RGB_projection_xy=uv.tolist(),undistorted_RGB_projection_xy=ui.tolist(),native_RGB_reprojection_error_px=float(np.linalg.norm(uv-q['native_rgb_subpixel_xy'])),distortion_displacement_px=float(np.linalg.norm(uv-ui)),old_to_new_reprojection_change_px=float(np.linalg.norm(uv-uvo)),metric_point_error_vs_old_scaled_m=float(np.linalg.norm(pt-po*s)),visual_note=q['visual_review_note'],point_localization_is_not_physical_correspondence_proof=True))
h=np.load(R/'generated/research_followthrough_20261007/spectral/fx10_display_rgb.npy');hr=np.rot90(h); native=np.array([[0,0],[1023,0],[20,1444],[1023,h.shape[0]-1]],int);rt=[]
for c,l in native:rt.append(bool(np.array_equal(h[l,c],hr[1023-c,l])))
out=dict(native_hsi_shape=list(h.shape),rotated_hsi_shape=list(hr.shape),rotation_rule='rotated_xy=[native_line, 1023-native_column], exact integer pixel-centre permutation; no half-pixel correction',roundtrip_checks=rt,records=rows,resize_note='Historical feature detector inverted cv2 resize as dst/scale. Pixel-centre-aware inverse differs by 0.5/scale-0.5; at tested sy=0.4..0.7 this is +0.214..+0.75 source HSI px; sx=0.75..1.25 gives -0.1..+0.167 source HSI px. This cannot by itself explain several-pixel native RGB residuals. Re-running detection needed before altering any old coordinate.',training_status='Previously exposed selections only; not fresh ground truth')
(O/'coordinate_audit.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');(O/'exposed_training_controls.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
arr=np.clip(hr*255,0,255).astype('uint8');rgb=np.array(Image.open(RGB/'rgb_1055904.png'))
for name,im,lim,ids in [('red_hsi',arr,(1510,1770,240,0),['red_upper_2','red_upper_6']),('red_rgb',rgb,(760,940,340,175),['red_upper_2','red_upper_6']),('whole_hsi',arr,(0,arr.shape[1],arr.shape[0],0),[]),('whole_rgb',rgb,(0,1280,720,0),[])]:
 fig,ax=plt.subplots(figsize=(14,11 if name.startswith('red') else 6));ax.imshow(im,interpolation='nearest');ax.set_xlim(lim[0],lim[1]);ax.set_ylim(lim[2],lim[3]);ax.grid(alpha=.2)
 if name.startswith('red'):ax.set_xticks(np.arange((lim[0]//10)*10,lim[1]+1,10));ax.set_yticks(np.arange(0 if name.endswith('hsi') else 180,lim[2]+1,10));ax.tick_params(axis='x',rotation=90)
 for id in ids:
  q=loc[id];x,y=([q['hsi_column_line'][1],1023-q['hsi_column_line'][0]] if name.endswith('hsi') else q['native_rgb_subpixel_xy']);ax.plot(x,y,'+',color='cyan',ms=12);ax.annotate(id,(x,y),color='cyan',xytext=(8,8),textcoords='offset points')
 fig.tight_layout();fig.savefig(O/(name+'.png'),dpi=120);plt.close(fig)
print(json.dumps(out,indent=2))
