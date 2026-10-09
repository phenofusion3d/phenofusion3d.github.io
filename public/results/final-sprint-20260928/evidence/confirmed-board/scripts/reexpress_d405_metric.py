"""Apply the recovered metric gauge to unchanged D405 RGB geometry and poses.

This is a similarity re-expression, not new surface recovery or a rerun at fixed
metric thresholds. All old processing distances acquire their actual scale.
"""
from pathlib import Path
import json,hashlib,shutil
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
BASE=Path(__file__).resolve().parent
OUT=BASE/'d405_metric'
OLD=ROOT/'generated/research_20260928_improvement_20261007/short_dense_v3'

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def ply_read(p):
 with p.open('rb') as f:
  lines=[]
  while True:
   line=f.readline();lines.append(line)
   if line==b'end_header\n':break
  assert b'format binary_little_endian 1.0\n' in lines
  props=[];n=None;mp={'double':'<f8','float':'<f4','uchar':'u1','uint':'<u4','int':'<i4'}
  for line in lines:
   vals=line.decode().strip().split()
   if vals[:2]==['element','vertex']:n=int(vals[2])
   if vals[:1]==['property']:props.append((vals[2],mp[vals[1]]))
  d=np.fromfile(f,dtype=np.dtype(props),count=n);assert len(d)==n
 return b''.join(lines),d

def main():
 assert not OUT.exists(),'Existing metric export preserved; use a new version'
 OUT.mkdir()
 cal=json.loads((BASE/'d405_metric_calibration.json').read_text());s=cal['metres_per_previous_filename_unit']
 exports=[]
 inputs=[(OLD/'result/plant_rgb_icp.ply','full_scene_reference.ply'),(ROOT/'generated/research_d405_l515_fusion_20261007/v1/d405_review_reference.ply','inspection_region_reference.ply')]
 for src,name in inputs:
  header,old=ply_read(src);new=old.copy()
  for k in 'xyz':new[k]=old[k]*s
  dest=OUT/name
  with dest.open('wb') as f:f.write(header);new.tofile(f)
  hh,check=ply_read(dest)
  assert hh==header and check.dtype==old.dtype and len(check)==len(old)
  for k in old.dtype.names:assert np.array_equal(check[k],old[k]*s if k in 'xyz' else old[k]),k
  exports.append(dict(file=name,points=len(old),source=str(src.relative_to(ROOT)),source_sha256=sha(src),sha256=sha(dest),every_coordinate_verified=True,colour_and_order_unchanged=True))
  print(name,len(old),flush=True)
  del old,new,check
 poses=json.loads((OLD/'bundle/poses.json').read_text())
 for row in poses['frames']:
  T=np.array(row['transform']);T[:3,3]*=s;row['transform']=T.tolist()
 poses['metric_reexpression']=dict(scale=s,source=str((OLD/'bundle/poses.json').relative_to(ROOT)),source_sha256=sha(OLD/'bundle/poses.json'),no_new_bundle_fit=True)
 save(OUT/'poses.json',poses)
 icp=json.loads((OLD/'result/icp_diagnostics.json').read_text())
 for row in icp:
  T=np.array(row['transform']);T[:3,3]*=s;row['transform']=T.tolist()
  for k in ['rmse_before_m','rmse_after_m','median_displacement_m']:row[k]*=s
 save(OUT/'icp_diagnostics_reexpressed.json',icp)
 shutil.copyfile(OLD/'result/point_evidence.npz',OUT/'point_evidence.npz')
 # Scale covariance of projection: compare actual full-scene vertices in all
 # saved camera frames, using unchanged K and s-scaled translations.
 _,points=ply_read(OUT/'inspection_region_reference.ply');ids=np.linspace(0,len(points)-1,2000,dtype=int)
 q=np.column_stack([points[k][ids] for k in 'xyz']);p=q/s
 oldposes=json.loads((OLD/'bundle/poses.json').read_text())['frames'];err=[]
 K=np.array(cal['selected_K'])
 for a,b in zip(oldposes,poses['frames']):
  A=np.array(a['transform']);B=np.array(b['transform']);pa=(p-A[:3,3])@A[:3,:3];pb=(q-B[:3,3])@B[:3,:3]
  ok=(pa[:,2]>.01)&(pb[:,2]>.01);ua=pa[ok]@K.T;ub=pb[ok]@K.T
  err.extend(np.linalg.norm(ua[:,:2]/ua[:,2,None]-ub[:,:2]/ub[:,2,None],axis=1))
 assert max(err)<1e-8
 summary=dict(status='D405_RGB_geometry_metric_reexpression_from_confirmed_25mm_board',scale_factor=s,
  export_files=exports,physical_length_change_percent=(s-1)*100,
  old_conditional_voxel_m=.001,actual_inherited_voxel_m=.001*s,actual_inherited_truncation_m=.005*s,
  actual_inherited_pair_tolerance_m=.01*s,actual_inherited_visibility_tolerance_m=.006*s,
  reprojection_invariance=dict(comparisons=len(err),max_pixel_change=float(max(err))),
  anchors=len(poses['frames']),new_points=0,surface_topology_changed=False,new_stereo_or_icp_run=False,
  note='Known board dimensions determine the metric gauge of an otherwise identical monocular RGB reconstruction. Existing observations, disparity solutions, point identities and support remain unchanged. Values formerly labelled metres were conditional filename units. Original thresholds are re-expressed here, not silently claimed to have been rerun at 1mm.',
  caveats=['Print size is operator-confirmed without stated measurement uncertainty.','D405 factory intrinsics retained; board pose/model residuals remain.','Fixed rig and identical scan settings supplied by user; calibration-to-plant scale transfer remains a model assumption.','L515 sensor depth requires its own scale evaluation; the old mixed cloud is not rescaled by this operation.'],
  source_hashes={str(p.relative_to(ROOT)):sha(p) for p in [BASE/'d405_metric_calibration.json',OLD/'bundle/poses.json',OLD/'result/icp_diagnostics.json',OLD/'result/point_evidence.npz',Path(__file__)]})
 save(OUT/'summary.json',summary);print(json.dumps(summary['reprojection_invariance']),flush=True)
if __name__=='__main__':main()
