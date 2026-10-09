from pathlib import Path
O=Path(__file__).resolve().parent
src=(O/'evaluate_frozen_models.py').read_text(encoding='utf-8').split("phy=load(P/")[0];src=src.replace('rows=initial+extra;models=',"rows=load(O/'round2_interior_landmarks_frozen.json')['records'];models=");src=src.replace('blind_learned_evaluation.json','blind_round2_learned_evaluation.json');exec(compile(src,str(O/'evaluate_round2.py'),'exec'))
