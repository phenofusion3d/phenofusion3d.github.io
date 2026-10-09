"""Prepare an isolated repeat of the frozen trait review on confirmed-board results."""
from pathlib import Path
import shutil

ROOT = Path.cwd()
BASE = ROOT / 'generated/research_confirmed_board_20261007'
OUT = BASE / 'traits_metric'
OUT.mkdir(exist_ok=True)
old = ROOT / 'generated/research_followthrough_20261007/traits'
target = OUT / 'build_metric_trait_review.py'
if target.exists():
    raise SystemExit('Refusing to replace prepared builder')
shutil.copy2(old / 'annotations.json', OUT / 'annotations.json')
s = (old / 'build_trait_review.py').read_text(encoding='utf-8')
s = s.replace("F=ROOT/'generated/research_d405_l515_fusion_20261007/v1'", "F=ROOT/'generated/research_confirmed_board_20261007/fusion_v1'")
s = s.replace("C=ROOT/'generated/research_plant_cleanup_20261007/v1/result'", "C=ROOT/'generated/research_confirmed_board_20261007/cleanup_v1/result'\nM=ROOT/'generated/research_confirmed_board_20261007/d405_metric'\nSCALE=1.0288746669066682")
s = s.replace("D/'result/icp_diagnostics.json'", "M/'icp_diagnostics_reexpressed.json'")
s = s.replace("z=dep['depth'][ij2[:,1],ij2[:,0]]", "z=dep['depth'][ij2[:,1],ij2[:,0]]*SCALE")
s = s.replace("for j in range(1,6):\n    pid", "for j in range(1,6):\n    cache.clear()\n    pid")
s = s.replace('conditional_m', 'm')
s = s.replace('conditional_cm', 'cm')
s = s.replace("'conditional metre coordinates; recording units and physical ChArUco scale unavailable'", "'Board-referenced metres from supplied 25 mm square / 18 mm marker; D405 metric gauge and empirical L515 board gain; anatomical accuracy unvalidated'")
s = s.replace("'Physical ChArUco square/marker size explicitly unavailable.'", "'Board dimensions supplied by operator: 25 mm square, 18 mm marker, 7 by 10 DICT_4X4_50; independent printed-size uncertainty unavailable.'")
s = s.replace("'Recorded depth and gantry/encoder units explicitly unavailable; metre coordinates remain conditional.'", "'D405 metric gauge re-expressed from supplied board pitch; L515 effective depth gain is empirically fitted, not a confirmed native device unit; cross-camera transform is a research estimate.'")
s = s.replace("status='first_stage_observed_geometry_and_correspondence_not_physical_validation'", "status='confirmed_board_observed_geometry_and_correspondence_not_anatomical_validation'")
s = s.replace("created_date='2026-10-07'", "created_date='2026-10-08'")
s = s.replace('conditional projected occupancy/hull descriptors only.', 'board-referenced projected occupancy/hull descriptors only.')
s = s.replace('tolerances remain scale-conditional.', 'tolerances remain physical 10 mm / 12 mm after gauge correction.')
s = s.replace("units_independently_confirmed=False", "units_independently_confirmed=False,board_dimensions_operator_confirmed=True,coordinate_unit='board-referenced metre'")
s = s.replace("inputs=[F/", "inputs=[ROOT/'generated/research_confirmed_board_20261007/board_confirmation.json',ROOT/'generated/research_confirmed_board_20261007/d405_metric_calibration.json',ROOT/'generated/research_confirmed_board_20261007/cross_camera/selection.json',F/")
s = s.replace('"""Read-only first-stage audit; all output stays beside this script."""', '"""Repeat frozen source review on new metric fusion/cleanup; originals are read-only."""')
target.write_text(s, encoding='utf-8')
print(target)
