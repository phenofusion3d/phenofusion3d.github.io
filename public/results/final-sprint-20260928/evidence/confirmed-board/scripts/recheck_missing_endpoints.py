"""Repeat the two frozen missing-tip searches in current metric cleaned geometry."""
from pathlib import Path
import sys,json
import cv2,numpy as np
ROOT=Path.cwd();BASE=ROOT/'generated/research_confirmed_board_20261007';D=ROOT/'generated/research_20260928_improvement_20261007/short_dense_v3';S=1.0288746669066682
sys.path.insert(0,str(ROOT/'generated/research_20260928_processing_20261007'))
from extract_P5_review_candidate import read_vertices,xyz
def load(p):return json.loads(p.read_text(encoding='utf-8'))
p=xyz(read_vertices(BASE/'fusion_v1/fused_review_reference.ply'),slice(None));cl=np.load(BASE/'cleanup_v1/result/point_classification.npz')
profile=load(D/'profile.json');K=np.array(profile['K']);dist=np.array(profile['dist']);poses={a['frame']:np.array(a['transform']) for a in load(BASE/'d405_metric/icp_diagnostics_reexpressed.json') if a['icp_accepted']}
out=[]
for key,frame,pixel in [('P1.O03.true_tip_attempt',143152,[983,354]),('P1.O04.ear_body_chord',459309,[157,469])]:
    T=poses[frame];pc=(p-T[:3,3])@T[:3,:3];uv=cv2.projectPoints(pc,np.zeros(3),np.zeros(3),K,dist)[0].reshape(-1,2)
    good=(pc[:,2]>0)&np.isfinite(uv).all(axis=1)&(uv[:,0]>=0)&(uv[:,0]<1279.5)&(uv[:,1]>=0)&(uv[:,1]<719.5)
    ids=np.flatnonzero(good);ij=np.rint(uv[ids]).astype(int);pix=ij[:,1]*1280+ij[:,0];zb=np.full(1280*720,np.inf,np.float32);np.minimum.at(zb,pix,pc[ids,2]);zb=cv2.erode(zb.reshape(720,1280),np.ones((3,3),np.uint8)).ravel()
    visible=np.zeros(len(p),bool);visible[ids]=pc[ids,2]<=zb[pix]+.010
    ideal=pc[ids,:2]/pc[ids,2,None]*[K[0,0],K[1,1]]+[K[0,2],K[1,2]]
    inside=(ideal[:,0]>=0)&(ideal[:,0]<1279.5)&(ideal[:,1]>=0)&(ideal[:,1]<719.5);iq=np.flatnonzero(inside);ij2=np.rint(ideal[iq]).astype(int)
    with np.load(D/f'rgb/depth_{frame}.npz') as de:
        dz=de['depth'][ij2[:,1],ij2[:,0]]*S;valid=np.isfinite(dz)&(dz>0)&(de['votes'][ij2[:,1],ij2[:,0]]>=2)
    visible[ids[iq[valid&(pc[ids[iq],2]>dz+.012)]]]=False
    near=np.flatnonzero(visible&(cl['plant_id']==1)&(np.linalg.norm(uv-pixel,axis=1)<=4))
    out.append(dict(id=key,frame=frame,pixel=pixel,radius_px=4,current_cleaned_visible_candidates=len(near),source_fused_indices=near.tolist(),new_endpoint_selected=False,policy='Frozen click; current full-cloud occlusion plus scaled stereo depth and current P1 membership. No farther point substituted.'))
(BASE/'traits_metric/missing_endpoint_recheck.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(out)
