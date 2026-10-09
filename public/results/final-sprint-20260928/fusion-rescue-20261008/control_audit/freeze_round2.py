from pathlib import Path
import json,hashlib
O=Path(__file__).resolve().parent
spec=[
('round2_red_pale_island_upper_tip','red_upper',[1609,54],[812,256],3,2,'medium','Upper narrow end of long pale island left of old red2; same material patch, nearby support is correlated with old training feature.'),
('round2_red_midvein_branch_middle','red_upper',[1678,69],[869,259],4,3,'low-medium','Middle midrib branch, between prior red6 and lower training junction; broad vein crossing.'),
('round2_red_midvein_branch_lower','red_upper',[1688,115],[881,281],4,3,'medium','Lower main-vein intersection with long leftward vein extending to rounded lower lobe.'),
('round2_red_midvein_bottom','red_upper',[1689,132],[883,290],5,3,'low','Near lower branch subdivision; green/red spectral intensity boundary makes exact fork ambiguous.'),
('round2_upper_green_fork_high','green_upper',[1811,83],[1011,265],4,3,'medium','Main-vein junction below upper lobe; small lateral branch leads left across dark region.'),
('round2_upper_green_fork_middle','green_upper',[1808,99],[1004,276],4,3,'medium','Next main-vein branch below high junction and above already-frozen lower mainfork.'),
('round2_upper_green_fork_low','green_upper',[1798,153],[985,300],5,3,'low-medium','Lower mainvein region before distal lobes divide; foreshortening and broad vein make exact centre uncertain.')]
rows=[dict(id=id,region=reg,hsi_rotated_xy=hs,native_hsi_column_line=[1023-hs[1],hs[0]],native_RGB_xy=rgb,hsi_uncertainty_radius_px=uh,RGB_uncertainty_radius_px=ur,confidence=co,feature=feat,role='second_round_reserved_evaluation',RGB_frame=1055904,selection_policy='Raw source grids only; no predicted point overlay or fitted warp was viewed to select/adjust coordinates. All7 attempts retained. Leaves chosen after first-round results, so this is adaptive second-round evidence; models unchanged.',independent_operator_ground_truth=False) for id,reg,hs,rgb,uh,ur,co,feat in spec]
p=O/'round2_interior_landmarks_frozen.json';p.write_text(json.dumps(dict(records=rows,unselected_attempts=[dict(region='green_upper',feature='pale lateral edge patches',reason='not unique across spectral channels, no reliable material landmark identified'),dict(region='red_upper',feature='small red/pale interior islands to left of mainrib',reason='several visually similar patches; no unique peak identity without tuning')]),indent=2)+'\n',encoding='utf-8');print(hashlib.sha256(p.read_bytes()).hexdigest())
