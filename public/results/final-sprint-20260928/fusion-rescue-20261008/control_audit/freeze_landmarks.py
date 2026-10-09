from pathlib import Path
import numpy as np,cv2,json,sys,hashlib
from scipy.spatial import cKDTree
from PIL import Image,ImageDraw
R=Path.cwd();O=Path(__file__).resolve().parent;B=R/'generated/research_confirmed_board_20261007';D=R/'generated/research_20260928_improvement_20261007/short_dense_v3';RGB=R/'data/main/test_plant_10-7/test_plant_20260928162354';load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sys.path.insert(0,str(R/'generated/research_20260928_processing_20261007'));from extract_P5_review_candidate import read_vertices,xyz
p=xyz(read_vertices(B/'cleanup_v1/result/P5_reference.ply'),slice(None));tree=cKDTree(p);pr=load(D/'profile.json');K=np.array(pr['K']);dist=np.array(pr['dist']);poses={a['frame']:np.array(a['transform']) for a in load(B/'d405_metric/icp_diagnostics_reexpressed.json') if a['icp_accepted']};T=poses[1055904];dep=np.load(D/'rgb/depth_1055904.npz');S=1.0288746669066682
specs=[
 dict(id='audit_red_pale_island_terminal',role='new_provisional_training',hsi_rotated_xy=[1600.0,97.0],native_RGB_xy=[810.0,276.0],hsi_uncertainty_radius_px=3,RGB_uncertainty_radius_px=2,confidence='medium',feature='Terminal lower point of leftmost long pale island in upper red leaf; a material colour-patch extremity, not blade silhouette.'),
 dict(id='audit_red_midvein_lower_junction',role='new_provisional_training',hsi_rotated_xy=[1684.0,86.0],native_RGB_xy=[874.0,266.0],hsi_uncertainty_radius_px=4,RGB_uncertainty_radius_px=3,confidence='low-medium',feature='Lower main-vein branch neighbourhood in upper red leaf; visible vein is broad and modality dependent.'),
 dict(id='reserved_red_right_notch',role='reserved_evaluation',hsi_rotated_xy=[1705.0,57.0],native_RGB_xy=[899.0,255.0],hsi_uncertainty_radius_px=4,RGB_uncertainty_radius_px=3,confidence='medium',feature='Deep upper-right lobe notch on red blade; distinctive boundary topology, potentially viewpoint dependent.'),
 dict(id='reserved_red_distal_tip',role='reserved_evaluation',hsi_rotated_xy=[1663.0,216.0],native_RGB_xy=[853.0,326.0],hsi_uncertainty_radius_px=4,RGB_uncertainty_radius_px=3,confidence='medium',feature='Lowest distal lobe tip on upper red blade; isolated silhouette tip, potentially viewpoint dependent.'),
 dict(id='reserved_green_basal_notch',role='reserved_evaluation',hsi_rotated_xy=[1822.0,508.0],native_RGB_xy=[995.0,460.0],hsi_uncertainty_radius_px=5,RGB_uncertainty_radius_px=3,confidence='low-medium',feature='Notch between two basal lobes on lower green blade; shadow/foreshortening makes extent uncertain.'),
 dict(id='reserved_green_basal_vein',role='reserved_evaluation',hsi_rotated_xy=[1827.0,575.0],native_RGB_xy=[1012.0,478.0],hsi_uncertainty_radius_px=5,RGB_uncertainty_radius_px=3,confidence='low',feature='Basal main-vein/side-vein fork candidate; assignment uncertain because several similar vein junctions and dark HSI region. Exploratory falsification only.'),
 dict(id='reserved_green_distal_vein',role='reserved_evaluation',hsi_rotated_xy=[1836.0,704.0],native_RGB_xy=[1082.0,559.0],hsi_uncertainty_radius_px=5,RGB_uncertainty_radius_px=3,confidence='low-medium',feature='Distal main-vein branch before blade tip; two closely spaced branches and mild blur limit exact material-centre localization.')]
for a in specs:
 a['native_hsi_column_line']=[1023-a['hsi_rotated_xy'][1],a['hsi_rotated_xy'][0]];a['RGB_frame']=1055904;a['selection_policy']='Visually specified from native source grids before evaluating any candidate warp; not adjusted to model predictions. Radiometric pseudoRGB colours are not calibrated reflectance.';a['independent_operator_ground_truth']=False;a['uncertainty_note']='Subjective localization radius, not a calibrated confidence interval; do not use strict3px gate for these landmarks.'
 und=cv2.undistortPoints(np.array(a['native_RGB_xy'],float).reshape(1,1,2),K,dist,P=K).reshape(2);u,v=np.rint(und).astype(int);d=float(dep['depth'][v,u])*S;a['depth_votes']=int(dep['votes'][v,u]);a['sampled_undistorted_pixel_xy']=[int(u),int(v)];a['depth_m']=d
 if d>0 and np.isfinite(d):
  pc=np.array([(u-K[0,2])*d/K[0,0],(v-K[1,2])*d/K[1,1],d]);ref=pc@T[:3,:3].T+T[:3,3];ds,ix=tree.query(ref);a['nearest_P5_distance_m']=float(ds);a['point_index']=int(ix);a['reference_xyz_m']=p[ix].tolist();a['depth_lift_reference_xyz_m']=ref.tolist();a['reference_frame']='D405_short_dense_v3_metric_reference';a['source_geometry_supported']=bool(ds<=.003 and a['depth_votes']>=2)
  ps=[]
  for fr in [1055904,1445026,1884421]:
   if fr not in poses:continue
   tt=poses[fr];cc=(p[ix]-tt[:3,3])@tt[:3,:3];uv=cv2.projectPoints(cc.reshape(1,3),np.zeros(3),np.zeros(3),K,dist)[0].reshape(2);ps.append(dict(frame=fr,native_RGB_xy=uv.tolist()))
  a['projections']=ps
 else:a['source_geometry_supported']=False
(O/'fresh_landmark_specs_frozen.json').write_text(json.dumps(dict(status='frozen_before_model_evaluation',records=specs),indent=2)+'\n',encoding='utf-8')
(O/'new_provisional_training.json').write_text(json.dumps([a for a in specs if a['role']=='new_provisional_training'],indent=2)+'\n',encoding='utf-8')
(O/'reserved_evaluation_private.json').write_text(json.dumps([a for a in specs if a['role']=='reserved_evaluation'],indent=2)+'\n',encoding='utf-8')
h=np.rot90(np.clip(np.load(R/'generated/research_followthrough_20261007/spectral/fx10_display_rgb.npy')*255,0,255).astype('uint8'));im=Image.fromarray(h);dr=ImageDraw.Draw(im);rgb=Image.open(RGB/'rgb_1055904.png').convert('RGB');dg=ImageDraw.Draw(rgb)
for i,a in enumerate(specs):
 for d,xy in [(dr,a['hsi_rotated_xy']),(dg,a['native_RGB_xy'])]:x,y=xy;d.ellipse([x-4,y-4,x+4,y+4],outline='yellow',width=1);d.text((x+6,y+4),str(i),fill='yellow')
im.save(O/'new_source_hsi.png');rgb.save(O/'new_source_RGB.png')
for a in specs:
 print(a['id'],a.get('source_geometry_supported'),a.get('nearest_P5_distance_m'),a.get('depth_votes'))
print('Frozen SHA',hashlib.sha256((O/'fresh_landmark_specs_frozen.json').read_bytes()).hexdigest())
