"""Reproduce the frozen metric board-derived seed without changing it."""
from pathlib import Path
import hashlib,json
import numpy as np

ROOT=Path.cwd();BASE=ROOT/'generated/research_confirmed_board_20261007';OUT=BASE/'cross_camera'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fit(a,b):
 ca=a.mean(0);cb=b.mean(0);u,s,vh=np.linalg.svd((a-ca).T@(b-cb));R=vh.T@u.T
 if np.linalg.det(R)<0:vh[-1]*=-1;R=vh.T@u.T
 T=np.eye(4);T[:3,:3]=R;T[:3,3]=cb-R@ca;return T
def points(models):
 corners=np.array([[x,y,0.] for y in range(1,10) for x in range(1,7)])*.025
 return {m['sheet']:corners@np.array(m['R_board_to_reference']).T+np.array(m['t_board_to_reference_m']) for m in models}
def main():
 dp=BASE/'d405_metric_calibration.json';lp=BASE/'l515/board_models_metric.json';sp=OUT/'board_seed.json'
 d=points(read(dp)['board_models']);l=points(read(lp)['board_models']);sheets=sorted(d);assert sheets==sorted(l)
 D=np.concatenate([d[s] for s in sheets]);L=np.concatenate([l[s] for s in sheets]);T=fit(L,D);seed=read(sp)
 err=float(abs(T-np.array(seed['T_D405_reference_from_L515_reference'])).max());assert err<1e-10,err
 held=[]
 for s in sheets:
  train=[q for q in sheets if q!=s];t=fit(np.concatenate([l[q] for q in train]),np.concatenate([d[q] for q in train]));ref=next(q for q in seed['whole_sheet_holdouts'] if q['heldout_sheet']==s);delta=float(abs(t-np.array(ref['T'])).max());assert delta<1e-10;held.append(dict(sheet=s,max_transform_difference=delta))
 report=dict(status='pass',method='Unweighted proper rigid Kabsch fit, 54 actual-size inner corners for each of three separately identified sheets; no scale fit.',supplied_square_m=.025,corner_pairs=162,max_seed_transform_difference=err,whole_sheet_holdouts=held,seed_unchanged=True,source_hashes={str(p.relative_to(ROOT)):sha(p) for p in [dp,lp,sp,Path(__file__)]},physical_accuracy=False)
 (OUT/'board_seed_reproduction.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
