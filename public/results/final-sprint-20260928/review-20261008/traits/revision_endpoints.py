"""Source-picked current metric endpoint probes; writes only traits_audit."""
from pathlib import Path
import sys,json,hashlib
import numpy as np,cv2
from PIL import Image,ImageDraw
ROOT=Path.cwd(); OUT=Path(__file__).resolve().parent
B=ROOT/'generated/research_confirmed_board_20261007';F=B/'fusion_v1';C=B/'cleanup_v1/result';D=ROOT/'generated/research_20260928_improvement_20261007/short_dense_v3';RGB=ROOT/'data/main/test_plant_10-7/test_plant_20260928162354'
sys.path.insert(0,str(ROOT/'generated/research_20260928_processing_20261007'))
from extract_P5_review_candidate import read_vertices,xyz
load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
p=xyz(read_vertices(F/'fused_review_reference.ply'),slice(None));cl=np.load(C/'point_classification.npz');prov=np.load(F/'fused_point_provenance.npz');profile=load(D/'profile.json');K=np.array(profile['K']);dist=np.array(profile['dist']);poses={a['frame']:np.array(a['transform']) for a in load(B/'d405_metric/icp_diagnostics_reexpressed.json') if a['icp_accepted']}
SCALE=1.0288746669066682
specs=load(OUT/'revision_frozen_endpoint_specs.json')
def projection(points,frame):
 T=poses[frame];pc=(points-T[:3,3])@T[:3,:3];uv=cv2.projectPoints(pc,np.zeros(3),np.zeros(3),K,dist)[0].reshape(-1,2);return uv,pc
arrays={};result=[]
for a in specs:
 uv,pc=projection(p,a['frame']);good=(pc[:,2]>0)&(uv[:,0]>=0)&(uv[:,0]<1279.5)&(uv[:,1]>=0)&(uv[:,1]<719.5);ids=np.flatnonzero(good);ij=np.rint(uv[ids]).astype(int);pix=ij[:,1]*1280+ij[:,0]
 zb=np.full(1280*720,np.inf,np.float32);np.minimum.at(zb,pix,pc[ids,2]);zb=cv2.erode(zb.reshape(720,1280),np.ones((3,3),np.uint8)).ravel();visible=np.zeros(len(p),bool);visible[ids]=pc[ids,2]<=zb[pix]+.010
 ideal=pc[ids,:2]/pc[ids,2,None]*[K[0,0],K[1,1]]+[K[0,2],K[1,2]];inside=(ideal[:,0]>=0)&(ideal[:,0]<1279.5)&(ideal[:,1]>=0)&(ideal[:,1]<719.5);iq=np.flatnonzero(inside);ij2=np.rint(ideal[iq]).astype(int)
 with np.load(D/f'rgb/depth_{a["frame"]}.npz') as de:
  dz=de['depth'][ij2[:,1],ij2[:,0]]*SCALE;valid=np.isfinite(dz)&(dz>0)&(de['votes'][ij2[:,1],ij2[:,0]]>=2)
 visible[ids[iq[valid&(pc[ids[iq],2]>dz+.012)]]]=False
 ep=[]
 for i,click in enumerate(a['points']):
  d=np.linalg.norm(uv-click,axis=1);near=np.flatnonzero(visible&(cl['plant_id']==a['plant'])&(d<=4));key=a['id'].replace('.','_')+f'_{i}';arrays[key]=near
  if not len(near):ep.append(dict(role=a['roles'][i],source_pixel_xy=click,candidate_count=0));continue
  original_near=near.copy()
  checks=[]
  for fr in [a['frame']]+a['secondary']:
   pu,pcand=projection(p[near],fr);uvideal=pcand[:,:2]/pcand[:,2,None]*[K[0,0],K[1,1]]+[K[0,2],K[1,2]];ijc=np.rint(uvideal).astype(int);ok=(ijc[:,0]>=0)&(ijc[:,0]<1280)&(ijc[:,1]>=0)&(ijc[:,1]<720);support=np.zeros(len(near),bool)
   with np.load(D/f'rgb/depth_{fr}.npz') as de:
    iok=np.flatnonzero(ok);zs=de['depth'][ijc[iok,1],ijc[iok,0]]*SCALE;vs=de['votes'][ijc[iok,1],ijc[iok,0]];support[iok]=np.isfinite(zs)&(zs>0)&(vs>=2)&(np.abs(zs-pcand[iok,2])<=.012)
   checks.append(support)
  support_counts=np.sum(checks,axis=0);near=near[support_counts>=2];arrays[key]=near
  if not len(near):ep.append(dict(role=a['roles'][i],source_pixel_xy=click,candidate_count=0,projected_candidates_before_two_view_depth_check=len(original_near),rejection='No candidate consistent with stereo depth in at least two of three inspected views.'));continue
  chosen=int(near[np.argmin(d[near])]);ep.append(dict(role=a['roles'][i],source_pixel_xy=click,candidate_count=len(near),fused_point_index=chosen,camera_id=int(prov['camera_id'][chosen]),original_point_index=int(prov['original_point_index'][chosen]),xyz_m=p[chosen].tolist(),reprojection_pixel_xy=uv[chosen].tolist(),source_click_distance_px=float(d[chosen]),candidate_key=key))
 a['endpoints']=ep;a['manual_used_for_scale_or_endpoint_selection']=False;a['physical_accuracy_validated']=False
 if all('fused_point_index' in e for e in ep):
  selected=p[[e['fused_point_index'] for e in ep]];a['chord_cm']=float(np.linalg.norm(selected[1]-selected[0])*100)
  b,t=[arrays[e['candidate_key']] for e in ep];ds=np.linalg.norm(p[b,None,:]-p[t][None,:,:],axis=2)*100;a['four_pixel_disk_sensitivity_cm']=[float(ds.min()),float(ds.max())];a['sensitivity_note']='All candidate endpoint pairs, not a confidence interval.'
  prs=[]
  for fr in [a['frame']]+a['secondary']:
   u,c=projection(selected,fr);prs.append(dict(frame=fr,pixel_xy=u.tolist()));im=Image.open(RGB/f'rgb_{fr}.png').convert('RGB');dr=ImageDraw.Draw(im)
   for i,(x,y) in enumerate(u):dr.ellipse((x-7,y-7,x+7,y+7),outline='magenta',width=3);dr.text((x+9,y+5),str(i+1),fill='magenta')
   dr.line([tuple(x) for x in u],fill='yellow',width=2);dr.text((10,10),a['id']+' | observed endpoints; anatomy candidate',fill='yellow');im.save(OUT/f'{a["id"]}_{fr}.jpg',quality=95)
  a['projections']=prs
 else:a['chord_cm']=None;a['status']='No current source-supported endpoint within 4px disk.'
 result.append(a);print(a['id'],a['chord_cm'],[(e['candidate_count'],e.get('source_click_distance_px')) for e in ep])
(OUT/'revision_endpoint_probes.json').write_text(json.dumps(result,indent=2)+'\n');np.savez_compressed(OUT/'revision_endpoint_candidates.npz',**arrays)
