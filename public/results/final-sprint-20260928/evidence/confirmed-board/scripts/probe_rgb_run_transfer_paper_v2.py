"""Bounded candidate transfer from recurring bare-paper features across RGB runs.

Uses the confirmed board plane, never foliage or repeated ChArUco IDs.
Correspondences require visual review; no production projection is replaced.
"""
from pathlib import Path
import json,hashlib
import cv2,numpy as np
from scipy.optimize import least_squares
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2];BASE=Path(__file__).resolve().parent;OUT=BASE/'rgb_run_transfer_paper_v2'
CAL=ROOT/'data/main/test_plant_10-7/test_plant_20260928143911';PLANT=ROOT/'data/main/test_plant_10-7/test_plant_20260928162354'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def stat(a):
 a=np.asarray(a);return dict(n=len(a),median_px=float(np.median(a)),rms_px=float(np.sqrt(np.mean(a*a))),p95_px=float(np.quantile(a,.95)),max_px=float(a.max()))
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 c=json.loads((BASE/'d405_metric_calibration.json').read_text());K=np.array(c['selected_K']);D=np.array(c['selected_distortion']);motion=np.array(c['metric_motion_vector_m_per_previous_filename_unit'])
 models=c['board_models'];normal=np.mean([np.array(b['R_board_to_reference'])[:,2] for b in models],axis=0);normal/=np.linalg.norm(normal)
 centres=np.array([np.array(b['R_board_to_reference'])@np.array([.0875,.125,0])+np.array(b['t_board_to_reference_m']) for b in models]);plane_d=float(np.median(centres@normal))
 frames=json.loads((BASE/'d405_metric/icp_diagnostics_reexpressed.json').read_text());chosen=[frames[i] for i in [0,12,25,38,50,63]]
 calibration_files=sorted(CAL.glob('rgb_*.png'),key=lambda p:int(p.stem[4:]));calids=np.array([int(p.stem[4:]) for p in calibration_files]);sift=cv2.SIFT_create(nfeatures=5000,contrastThreshold=.008)
 points=[];pixels=[];camera=[];groups=[];records=[];sources={}
 for gi,f in enumerate(chosen):
  fid=f['frame'];cp=calibration_files[np.argmin(abs(calids-fid))];cid=int(cp.stem[4:]);pp=PLANT/f'rgb_{fid}.png';a=cv2.imread(str(cp));b=cv2.imread(str(pp));sources[str(cp.relative_to(ROOT))]=sha(cp);sources[str(pp.relative_to(ROOT))]=sha(pp)
  def paper_mask(frame_id):
   h,w=a.shape[:2];yy,xx=np.mgrid[0:h,0:w];uv=np.column_stack([xx.ravel(),yy.ravel()]).astype(float)
   rays=cv2.undistortPoints(uv.reshape(-1,1,2),K,D).reshape(-1,2);rays=np.c_[rays,np.ones(len(rays))];origin=motion*frame_id/1e6
   depth=(plane_d-normal@origin)/(rays@normal);world=origin+rays*depth[:,None]
   good=(world[:,0]>.17)&(world[:,0]<1.66)&(world[:,1]>.235)&(world[:,1]<.340)&(uv[:,1]>=540)&(uv[:,1]<615)
   return (good.reshape(h,w)*255).astype(np.uint8)
  maska=paper_mask(cid);maskb=paper_mask(fid)
  ka,da=sift.detectAndCompute(cv2.cvtColor(a,cv2.COLOR_BGR2GRAY),maska);kb,db=sift.detectAndCompute(cv2.cvtColor(b,cv2.COLOR_BGR2GRAY),maskb)
  if da is None or db is None:continue
  matcher=cv2.BFMatcher();ab=[m for pair in matcher.knnMatch(da,db,k=2) if len(pair)==2 for m,n in [pair] if m.distance<.7*n.distance];ba={m.queryIdx:m.trainIdx for pair in matcher.knnMatch(db,da,k=2) if len(pair)==2 for m,n in [pair] if m.distance<.7*n.distance};matches=[m for m in ab if ba.get(m.trainIdx)==m.queryIdx]
  if len(matches)<6:records.append(dict(frame=fid,calibration_frame=cid,mutual_matches=len(matches),reason='too_few_matches'));continue
  ua=np.array([ka[m.queryIdx].pt for m in matches]);ub=np.array([kb[m.trainIdx].pt for m in matches]);H,keep=cv2.findHomography(ua,ub,cv2.RANSAC,1.2);keep=keep.ravel().astype(bool) if keep is not None else np.zeros(len(matches),bool);aa,bb=ua[keep],ub[keep]
  if len(aa)<6:records.append(dict(frame=fid,calibration_frame=cid,mutual_matches=len(matches),inliers=int(keep.sum()),reason='too_few_planar_candidates'));continue
  rays=np.c_[cv2.undistortPoints(aa.reshape(-1,1,2),K,D).reshape(-1,2),np.ones(len(aa))];origin=motion*cid/1e6;t=(plane_d-normal@origin)/(rays@normal);world=origin+rays*t[:,None]
  points.extend(world);pixels.extend(bb);camera.extend([f['transform']]*len(aa));groups.extend([gi]*len(aa))
  records.append(dict(frame=fid,calibration_frame=cid,mutual_matches=len(matches),planar_candidates=len(aa),calibration_pixels=aa.tolist(),plant_pixels=bb.tolist(),calibration_plane_points_m=world.tolist(),paper_mask_policy='frozen calibration-reference rectangle X0.17..1.66m,Y0.235..0.340m intersect imageY540..615; excludes gantry and white-panel support',homography=H.tolist()))
  fig,ax=plt.subplots(figsize=(13,3.5));combined=np.concatenate([a[510:650],b[510:650]],axis=1);ax.imshow(cv2.cvtColor(combined,cv2.COLOR_BGR2RGB))
  for j,(u,v) in enumerate(zip(aa,bb)):
   ax.plot([u[0],v[0]+1280],[u[1]-510,v[1]-510],lw=.35,alpha=.55);ax.text(u[0],u[1]-510,str(j),fontsize=6,color='red');ax.text(v[0]+1280,v[1]-510,str(j),fontsize=6,color='red')
  ax.set_title(f'Candidate paper matches: empty {cid} → plants {fid}; IDs need visual review');ax.axis('off');fig.tight_layout();fig.savefig(OUT/f'matches_{fid}.png',dpi=150);plt.close(fig)
 report=dict(status='candidate_image_transfer_probe_not_accepted_calibration',matches=sum('planar_candidates' in r and r['planar_candidates'] or 0 for r in records),records=records,source_hashes=sources,
  plane_normal=normal.tolist(),plane_distance_from_calibration_zero_camera_m=plane_d,visual_review_pending=True,limitations=['Features are descriptor/homography candidates until actual image identity is reviewed.','The first wide-strip probe included off-plane gantry points and is not accepted. This revised rectangle excludes those areas based on source inspection.','The lower paper strip is assumed coplanar with the board; warp, stacked paper and marker localization can contribute.','This is an RGB run-frame bridge, not HSI line timing or elevated-plant registration.'])
 if len(points)>=12 and len(set(groups))>=3:
  P=np.array(points);U=np.array(pixels);T=np.array(camera);groups=np.array(groups)
  def residual(par):
   R=cv2.Rodrigues(par[:3])[0];q=P@R.T+par[3:];pc=np.einsum('nj,njk->nk',q-T[:,:3,3],T[:,:3,:3]);uv=cv2.projectPoints(pc,np.zeros(3),np.zeros(3),K,D)[0].reshape(-1,2);return uv-U
  fit=least_squares(lambda x:residual(x).ravel(),np.zeros(6),loss='soft_l1',f_scale=1.,max_nfev=100)
  checks=[]
  for group in np.unique(groups):
   test=groups==group;fitg=least_squares(lambda x:residual(x)[~test].ravel(),np.zeros(6),loss='soft_l1',f_scale=1.,max_nfev=100);checks.append(dict(heldout_group=int(group),errors=stat(np.linalg.norm(residual(fitg.x)[test],axis=1))))
  M=np.eye(4);M[:3,:3]=cv2.Rodrigues(fit.x[:3])[0];M[:3,3]=fit.x[3:]
  report.update(T_plant_reference_from_calibration_zero_candidate=M.tolist(),identity_frame_errors=stat(np.linalg.norm(residual(np.zeros(6)),axis=1)),fitted_errors=stat(np.linalg.norm(residual(fit.x),axis=1)),leave_frame_out=checks,rotation_deg=float(np.linalg.norm(fit.x[:3])*180/np.pi),translation_m=fit.x[3:].tolist())
 (OUT/'summary.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['records','source_hashes','limitations']}))
if __name__=='__main__':main()
