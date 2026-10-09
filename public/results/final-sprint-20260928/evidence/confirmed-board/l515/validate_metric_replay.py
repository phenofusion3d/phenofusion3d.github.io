"""Fresh-read computational checks of one completed new L515 replay."""
from pathlib import Path
import argparse,hashlib,json
import cv2,numpy as np

ROOT=Path.cwd();OUT=ROOT/'generated/research_confirmed_board_20261007'
OLD=ROOT/'generated/research_l515_20261007/l515_sensor_v1'
def read(p):return json.loads(p.read_text())
def save(p,v):p.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def ply(p):
 with p.open('rb') as f:
  n=None
  while True:
   s=f.readline().decode().strip()
   if s.startswith('element vertex'):n=int(s.split()[-1])
   if s=='end_header':break
  offset=f.tell()
 dtype=np.dtype([('x','<f8'),('y','<f8'),('z','<f8'),('r','u1'),('g','u1'),('b','u1')])
 assert p.stat().st_size==offset+n*dtype.itemsize
 return np.memmap(p,mode='r',dtype=dtype,offset=offset,shape=(n,))
def xyz(a):return np.column_stack([a[k] for k in 'xyz'])

def main():
 ap=argparse.ArgumentParser();ap.add_argument('variant',choices=['native','board_gain']);args=ap.parse_args()
 run=OUT/('l515_metric_v1' if args.variant=='native' else 'l515_metric_boardgain_v1');result=run/'result'
 assert (result/'summary.json').exists(),'Replay not complete yet'
 assert read(run/'provenance.json')['status'].startswith('completed_'),'Replay wrapper not finalized'
 cfg=read(run/'profile.json');summary=read(result/'summary.json');poses=read(run/'bundle/poses.json');icp=read(result/'icp_diagnostics.json')
 a=ply(result/'l515_supported_reference.ply');ev=np.load(result/'point_evidence.npz');selected=np.linspace(0,len(a)-1,min(len(a),768)).round().astype(int)
 points=xyz(a[selected]);colors=np.column_stack([a[k][selected] for k in ['r','g','b']]);n=len(selected)
 supp=np.zeros(n,int);conf=np.zeros(n,int);best=np.full(n,np.inf);expected_rgb=np.zeros((n,3),np.uint8);best_view=np.full(n,-1,int)
 K=np.array(cfg['K']);dist=np.array(cfg['dist']);maps=cv2.initUndistortRectifyMap(K,dist,None,K,(1280,720),cv2.CV_32FC1)
 keep=cv2.remap(cv2.imread(cfg['native_feature_keep_mask'],0),*maps,cv2.INTER_NEAREST)>0
 by_frame={r['frame']:r for r in poses['frames']};sources={};integrated=[r for r in icp if r['integrated']]
 cv2.setNumThreads(2)
 for vi,row in enumerate(integrated):
  frame=by_frame[row['frame']];rawp=Path(frame['depth']);rgbp=Path(frame['rgb']);sources[str(rawp.relative_to(ROOT))]=sha(rawp);sources[str(rgbp.relative_to(ROOT))]=sha(rgbp)
  z=cv2.remap(cv2.imread(str(rawp),-1),*maps,cv2.INTER_NEAREST).astype(np.float32)*cfg['sensor_unit_m'];image=cv2.remap(cv2.imread(str(rgbp)),*maps,cv2.INTER_LINEAR)
  valid=keep&(z>cfg['near'])&(z<cfg['far'])&(z<65535*cfg['sensor_unit_m'])
  inv=np.linalg.inv(np.array(row['transform']));p=points@inv[:3,:3].T+inv[:3,3];uv=np.rint(p[:,:2]/p[:,2,None]*[K[0,0],K[1,1]]+[K[0,2],K[1,2]]).astype(int)
  xx,yy=uv.T;in_frame=np.flatnonzero((xx>=1)&(xx<1279)&(yy>=1)&(yy<719)&(p[:,2]>0));x=xx[in_frame];y=yy[in_frame]
  neighbors=np.column_stack([z[y+dy,x+dx] for dx,dy in [(0,0),(-1,0),(1,0),(0,-1),(0,1)]])
  good=np.column_stack([valid[y+dy,x+dx] for dx,dy in [(0,0),(-1,0),(1,0),(0,-1),(0,1)]])
  distances=np.where(good,abs(neighbors-p[in_frame,2,None]),np.inf).min(1);nearest=np.where(good,neighbors,np.inf).min(1)
  agree=distances<cfg['tolerance'];free=np.isfinite(nearest)&(p[in_frame,2]<nearest-2*cfg['tolerance']);supp[in_frame]+=agree;conf[in_frame]+=free
  better=agree&(distances<best[in_frame]);q=in_frame[better];best[q]=distances[better];expected_rgb[q]=image[y[better],x[better],::-1];best_view[q]=vi
 assert np.array_equal(supp,ev['support_views'][selected])
 assert np.array_equal(conf,ev['contradicting_views'][selected])
 assert np.array_equal(best_view,ev['colour_source_view_index'][selected])
 assert np.array_equal(colors,expected_rgb)
 assert np.array_equal(ev['frame_ids'],np.array([r['frame'] for r in integrated]))
 assert len(a)==summary['points']==len(ev['support_views'])
 assert np.all(ev['support_views']>=3)
 assert np.all(ev['contradicting_views']<=np.maximum(1,.3*ev['support_views']))
 filtered=ply(result/'l515_filtered_reference.ply');fi=np.load(result/'filtered_source_indices.npz')['source_indices'];assert np.array_equal(filtered,a[fi])
 for row in icp:
  accepted=row['fitness_after']>.65 and row['median_displacement_m']<.006 and row['rotation_degrees']<.5 and row['rmse_after_m']<=row['rmse_before_m']*1.05
  assert accepted==row['icp_accepted'];assert row['integrated']==(accepted or (row['fitness_before']>.65 and row['rmse_before_m']<.006))
 oldlm=np.load(OLD/'bundle/landmarks.npz');newlm=np.load(run/'bundle/landmarks.npz');scale=cfg['metric_RGB_translation_factor'];oldposes=read(OLD/'bundle/poses.json')['frames']
 assert np.array_equal(oldlm['observations'],newlm['observations'])
 assert np.array_equal(oldlm['residual_px'],newlm['residual_px'])
 assert np.array_equal(newlm['points'],oldlm['points']*scale)
 maxerr=0.;obs=oldlm['observations'];compared=0
 for ci,(old,new) in enumerate(zip(oldposes,poses['frames'])):
  ids=obs[obs[:,0].astype(int)==ci,1].astype(int)
  ot=np.array(old['transform']);nt=np.array(new['transform']);assert np.array_equal(ot[:3,:3],nt[:3,:3]);assert np.array_equal(ot[:3,3]*scale,nt[:3,3])
  oi=np.linalg.inv(ot);ni=np.linalg.inv(nt);op=oldlm['points'][ids]@oi[:3,:3].T+oi[:3,3];np_=newlm['points'][ids]@ni[:3,:3].T+ni[:3,3]
  ou=op[:,:2]/op[:,2,None]*[K[0,0],K[1,1]]+[K[0,2],K[1,2]];nu=np_[:,:2]/np_[:,2,None]*[K[0,0],K[1,1]]+[K[0,2],K[1,2]]
  maxerr=max(maxerr,float(abs(ou-nu).max()));compared+=len(ids)
 assert maxerr<1e-8
 provenance=read(run/'provenance.json')
 for p,h in provenance['old_source_hashes'].items():assert sha(ROOT/p)==h
 assert sha(Path(cfg['calibration']))==cfg['calibration_sha256']
 assert sha(Path(cfg['native_feature_keep_mask']))==sha(OLD/'native_keep_mask.png')
 # The wrapper adds known-board provenance after the unchanged reconstruction
 # implementation writes its generic summary. Refresh the NEW result manifest.
 save(result/'output_hashes.json',{p.name:sha(p) for p in result.iterdir() if p.is_file() and p.name!='output_hashes.json'})
 report=dict(status='pass',variant=args.variant,points=len(a),filtered_points=len(filtered),frames=len(integrated),icp_accepted=sum(r['icp_accepted'] for r in icp),
  sensor_conversion_m_per_count=cfg['sensor_unit_m'],RGB_translation_factor=scale,voxel_m=cfg['voxel'],truncation_m=cfg['trunc'],support_tolerance_m=cfg['tolerance'],
  fresh_raw_visibility_check=dict(points=n,views=len(integrated),point_view_checks=n*len(integrated),support_exact=True,conflict_exact=True,RGB_exact=True,colour_source_view_exact=True,selected_new_cloud_indices=selected.tolist()),
  RGB_bundle_projection_equivalence=dict(observations=compared,max_difference_px=maxerr,landmarks_exactly_scaled=True,rotations_unchanged=True,original_residuals_unchanged=True),
  filtered_cloud_exact_subset=True,old_input_hashes_unchanged=True,raw_source_hashes=sources,
  result_manifest_refreshed_after_summary_provenance_annotation=True,script_sha256=sha(Path(__file__)),output_hashes=read(result/'output_hashes.json'),
  limits=['Computational reproducibility only; not independent physical accuracy.','Native device depth units remain absent. Board-gain version is an empirical correction, not device-unit confirmation.','New point identities require new fusion and source-reviewed cleanup; do not reuse old per-vertex labels.'])
 save(OUT/'l515'/f'replay_validation_{args.variant}.json',report)
 print(json.dumps({k:report[k] for k in ['status','variant','points','filtered_points','frames','icp_accepted','sensor_conversion_m_per_count','RGB_bundle_projection_equivalence']},indent=2))

if __name__=='__main__':main()
