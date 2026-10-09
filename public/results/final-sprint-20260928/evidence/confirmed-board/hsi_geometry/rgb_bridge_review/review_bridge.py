from pathlib import Path
import hashlib,json
import cv2,numpy as np
from scipy.optimize import least_squares
HERE=Path(__file__).resolve().parent;BASE=HERE.parents[1];ROOT=BASE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def stat(e):
 r=np.linalg.norm(e,axis=1);return {'n':len(r),'rms_px':float(np.sqrt(np.mean(r*r))),'median_px':float(np.median(r)),'p95_px':float(np.quantile(r,.95)),'max_px':float(r.max())}
def main():
 source=BASE/'rgb_run_transfer_paper_v2/summary.json';d=json.loads(source.read_text());metric=json.loads((BASE/'d405_metric_calibration.json').read_text());poses={r['frame']:np.array(r['transform']) for r in json.loads((BASE/'d405_metric/icp_diagnostics_reexpressed.json').read_text())};K=np.array(metric['selected_K']);D=np.array(metric['selected_distortion'])
 points=[];pixels=[];camera=[];groups=[];audit=[]
 for g,r in enumerate(d['records']):
  if 'calibration_pixels' not in r:continue
  keys=np.round(np.column_stack([r['calibration_pixels'],r['plant_pixels']]),4);_,ix=np.unique(keys,axis=0,return_index=True);ix.sort()
  points.extend(np.array(r['calibration_plane_points_m'])[ix]);pixels.extend(np.array(r['plant_pixels'])[ix]);camera.extend([poses[r['frame']]]*len(ix));groups.extend([g]*len(ix))
  audit.append({'frame':r['frame'],'original_candidates':len(keys),'unique_pixel_pairs':len(ix),'source_images_visually_reviewed':True,'observation':'Matches lie on repeated handwritten paper text/grid; no obvious gantry support matches in the inspected revised panels. Exact feature locations are still automatic subpixel estimates.'})
 P=np.array(points);U=np.array(pixels);T=np.array(camera);groups=np.array(groups)
 def residual(par):
  R=cv2.Rodrigues(par[:3])[0];q=P@R.T+par[3:];pc=np.einsum('nj,njk->nk',q-T[:,:3,3],T[:,:3,:3]);uv=cv2.projectPoints(pc,np.zeros(3),np.zeros(3),K,D)[0].reshape(-1,2);return uv-U
 def matrix(par):
  t=np.eye(4);t[:3,:3]=cv2.Rodrigues(par[:3])[0];t[:3,3]=par[3:];return t
 f=least_squares(lambda x:residual(x).ravel(),np.zeros(6),loss='soft_l1',f_scale=1.,max_nfev=300,xtol=1e-12,ftol=1e-12,gtol=1e-12)
 J=np.column_stack([(residual(f.x+np.eye(6)[j]*1e-6)-residual(f.x-np.eye(6)[j]*1e-6)).ravel()/2e-6 for j in range(6)])
 scale=np.linalg.norm(J,axis=0);s=np.linalg.svd(J/scale,compute_uv=False)
 held=[]
 for g in np.unique(groups):
  test=groups==g;fg=least_squares(lambda x:residual(x)[~test].ravel(),np.zeros(6),loss='soft_l1',f_scale=1.,max_nfev=300,xtol=1e-12,ftol=1e-12,gtol=1e-12)
  held.append({'held_frame':audit[int(g)]['frame'],'test_unique_pairs':int(test.sum()),'errors':stat(residual(fg.x)[test]),'T_plant_reference_from_calibration_zero':matrix(fg.x).tolist(),'fit_parameters':fg.x.tolist()})
 matrices=np.array([x['T_plant_reference_from_calibration_zero'] for x in held]);xyzcentre=np.array([1.25,0.,.55]);pred=np.einsum('nij,j->ni',matrices[:,:3,:3],xyzcentre)+matrices[:,:3,3];spread=np.linalg.norm(pred-pred.mean(0),axis=1)
 result={'status':'provisional_paper_plane_RGB_frame_bridge_for_bounded_diagnostics_only','original_feature_records':d['matches'],'unique_pixel_pairs':len(P),'deduplication':'Rounded (calibration u,v,plant u,v) at 1e-4 pixels within each frame; duplicate SIFT orientations do not count as independent features.','visual_review':audit,'T_plant_reference_from_calibration_zero':matrix(f.x).tolist(),'fit_parameters':f.x.tolist(),'identity_errors':stat(residual(np.zeros(6))),'fit_errors':stat(residual(f.x)),'leave_frame_out':held,'conditioning':{'jacobian_parameter_units':'first3 radians, last3 metres','jacobian_columns_l2_norm':scale.tolist(),'column_normalized_singular_values':s.tolist(),'column_normalized_condition_number':float(s[0]/s[-1]),'column_normalized_rank':int(np.linalg.matrix_rank(J/scale)),'limit':'Full rank does not establish ground-truth camera accuracy; paper-strip coverage is narrow and geometry/pose errors are correlated.'},'illustrative_P5_region_point_fold_spread':{'calibration_xyz_m':xyzcentre.tolist(),'fold_mapped_points':pred.tolist(),'max_distance_from_fold_mean_m':float(spread.max()),'meaning':'Leave-frame-out model variation at a representative height; not physical confidence interval.'},'limitations':['All controls are a narrow lower paper strip; the bridge is approximate and model-dependent.','Revised masks exclude off-plane gantry areas present in rejected first probe.','RANSAC selects within each image pair before this bridge fit; test-frame feature correspondence filtering uses that pair, but held-out pixels never enter the bridge fit.','Coplanarity of paper with the boards is assumed; no independent elevated calibration exists.','Use only as one sensitivity scenario for a bounded three-point height-model diagnostic; not a production dense-fusion transform.'],'source_hashes':{str(p.relative_to(ROOT)):sha(p) for p in [source,BASE/'d405_metric_calibration.json',BASE/'d405_metric/icp_diagnostics_reexpressed.json',Path(__file__)]}}
 (HERE/'independent_review.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ['original_feature_records','unique_pixel_pairs','fit_errors','conditioning','illustrative_P5_region_point_fold_spread']},indent=2))
if __name__=='__main__':main()
