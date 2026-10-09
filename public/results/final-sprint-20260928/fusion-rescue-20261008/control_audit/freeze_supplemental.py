from pathlib import Path
import json,hashlib
O=Path(__file__).resolve().parent
rows=[
('reserved_central_distal_tip','green_central',[1674,399],[925,432],4,3,'medium','Terminal lower-left lobe tip; unique outline, but folded margin can shift with view.'),
('reserved_central_distal_notch','green_central',[1701,376],[944,425],5,3,'low-medium','Deep notch between two distal lobes; foreshortened narrow valley.'),
('reserved_variegated_basal_notch','variegated_right',[1920,300],[1085,380],5,3,'medium','Distinct notch between the two upper variegated lobes.'),
('reserved_variegated_curled_tip','variegated_right',[2000,330],[1184,379],4,3,'medium','Isolated narrow upper-right curled lobe tip; view dependence possible.'),
('reserved_upper_green_mainfork','green_upper',[1803,121],[994,287],4,3,'medium','Broad main-vein/left-side-vein fork in lower half; material interior feature but broad junction.'),
('reserved_upper_green_distal_notch','green_upper',[1797,198],[986,316],4,3,'medium','Deep bottom inter-lobe notch; unique topology, potentially viewpoint dependent.'),
('reserved_lower_red_notch','red_lower',[1710,628],[917,520],4,3,'medium','Distinct right-side inward notch between middle lobes.'),
('reserved_lower_red_mainfork','red_lower',[1681,670],[879,540],5,3,'low-medium','Main vein meets left branch near centre; diffuse bright HSI patch limits exact centre.')]
res=[dict(id=id,region=reg,hsi_rotated_xy=hs,native_hsi_column_line=[1023-hs[1],hs[0]],native_RGB_xy=rgb,hsi_uncertainty_radius_px=uh,RGB_uncertainty_radius_px=ur,confidence=co,feature=feat,role='reserved_evaluation',RGB_frame=1055904,selection_policy='Manually specified from original full-native gridded source images without seeing candidate transforms or predictions; anatomical correspondence provisional, not independent operator ground truth.',uncertainty_note='Subjective localization radius, not calibrated confidence interval; no strict3pxaccuracygate') for id,reg,hs,rgb,uh,ur,co,feat in rows]
p=O/'supplemental_reserved_landmarks_private.json';p.write_text(json.dumps(res,indent=2)+'\n',encoding='utf-8');print(hashlib.sha256(p.read_bytes()).hexdigest())
