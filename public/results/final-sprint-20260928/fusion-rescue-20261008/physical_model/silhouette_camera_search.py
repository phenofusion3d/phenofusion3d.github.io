"""Coarse colour-class silhouette scan-camera search; no reserved labels consumed."""
import sys
import cv2,numpy as np
from scipy.ndimage import distance_transform_edt
from scipy.optimize import minimize
from fit_physical_models import HERE,ROOT,BASE,read,save,predict,camera_values
sys.path.insert(0,str(ROOT))
from processing.research_workspace.workflow import cloud_record

def classes(a):
    r,g,b=np.moveaxis(a,-1,0);z=np.zeros(r.shape,np.uint8)
    z[(g>1.1*r)&(g>1.05*b)&(g>.15)]=1
    z[(r>1.3*g)&(r>1.2*b)&(r>.15)]=2
    return z
def main():
    frozen=read(HERE/'frozen_candidates.json');seed=next(x for x in frozen['models'] if x['primary_candidate']);p0=np.array(seed['parameters']);coords=seed['coordinates'];T=np.array(coords['T_plant_reference_from_calibration']);O=np.array(coords['origin_calibration_reference_m']);B=np.array(coords['basis_columns']);tr=np.array(coords['scan_002_to_003_column_line_translation'])
    entry=cloud_record({'id':'P5','label':'P5','cloud':str(BASE/'cleanup_v1/result/P5_reference.ply')},ROOT,np.eye(3));xyz=entry['points'];rgb=entry['colours'];cls=classes(rgb);keep=np.flatnonzero(cls>0)[::3];q=((xyz[keep]-T[:3,3])@T[:3,:3]-O)@B;labels=cls[keep]
    img=np.load(ROOT/'generated/research_followthrough_20261007/spectral/fx10_display_rgb.npy');native_cls=classes(img);roi=np.zeros(native_cls.shape,bool);roi[1510:2010,240:]=True;native_cls[~roi]=0
    # Class masks are a heuristic image-registration objective, not labelled tissue truth.
    fields={k:distance_transform_edt(native_cls!=k).astype(np.float32) for k in [1,2]}
    baseline_uv=predict(p0,q)+tr
    baseline_visible={k:float(np.mean((baseline_uv[labels==k,0]>=240)&(baseline_uv[labels==k,0]<1024)&(baseline_uv[labels==k,1]>=1510)&(baseline_uv[labels==k,1]<2010))) for k in [1,2]}
    def objective(x,detail=False):
        p=p0.copy();p[[1,4,7]]=x*[500,1,100];uv=predict(p,q)+tr;losses=[];fractions=[];visibility=[];vis_penalty=0.
        for k in [1,2]:
            pp=uv[labels==k].astype(np.float32);visible=(pp[:,0]>=240)&(pp[:,0]<1024)&(pp[:,1]>=1510)&(pp[:,1]<2010);visibility.append(float(visible.mean()));vis_penalty+=max(0,.85*baseline_visible[k]-visible.mean())**2*10000.;pp=pp[visible];sample=cv2.remap(fields[k],pp[:,0,None],pp[:,1,None],cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=100).ravel();losses.append(float(np.mean(np.minimum(sample,40)**2)));fractions.append(float(np.mean(sample<=3)))
        cam=camera_values(p);prior=((cam['near_orthogonal_scan_principal_column_px']-511.5)/80)**2+(p[7]/250)**2
        score=float(np.mean(losses)+prior+vis_penalty)
        return {'score':score,'class_mean_clipped_squared_distance':losses,'within_3px_fraction':fractions,'visible_fraction':visibility,'visibility_penalty':vis_penalty,'camera':cam} if detail else score
    bounds=[(.5,1.8),(.5,1.6),(-2,2)];runs=[]
    for delta in [0.,-.2,.2]:
        init=p0[[1,4,7]]/[500,1,100];init[1]+=delta;init=np.clip(init,np.array(bounds)[:,0],np.array(bounds)[:,1]);f=minimize(objective,init,method='Powell',bounds=bounds,options={'maxiter':75,'maxfev':1500,'xtol':1e-4,'ftol':1e-5});p=p0.copy();p[[1,4,7]]=f.x*[500,1,100];r={'id':f'colour_class_geometry_seed_{delta:+g}','parameters':p.tolist(),'nfev':f.nfev,'success':bool(f.success),'objective':objective(f.x,True),'coordinates':coords,'sensor':'fx10','parameter_order':seed['parameter_order'],'input_3d_field_for_new_controls':'depth_lift_reference_xyz_m','prediction_recipe':seed['prediction_recipe'],'no_reserved_labels_consumed':True};runs.append(r);print(r['id'],r['objective'],flush=True)
    best=min(runs,key=lambda r:r['objective']['score']);best['primary_candidate']=True
    result={'status':'FROZEN_SILHOUETTE_CAMERA_SELECTION_CANDIDATES','version':2,'correction_from_v1':'Out-of-FOV points are censored, not punished for lacking image evidence. V1 incorrectly penalized genuinely out-of-view right leaf points, favoring shrinkage. Both versions retained. Visibility cannot fall below 85% of initial per-class visibility without a quadratic penalty; sensitivity assumption, not measured coverage.','primary_selection':'Lowest colour-class distance objective, before reserved material-point scores.','source_points':len(q),'class_names':['green','red'],'limitations':['Colour thresholds are heuristic and modality/illumination dependent.','Incomplete geometry and occlusions can bias silhouette objectives.','Symmetric pixel coverage is not guaranteed; score is projected-source-to-observed-class distance.','Near-colour agreement does not prove exact material correspondence.','No native spectral data assigned; this is camera-model search only.','Reserved label coordinates and errors were not consumed; labels share this recorded imagery, not independent physical acquisition.'],'class_thresholds':{'green':'g>1.1r and g>1.05b and g>.15','red':'r>1.3g and r>1.2b and r>.15'},'native_roi':[240,1510,1024,2010],'varied_parameters':['ah','bh','lh'],'bounds_normalized':bounds,'normalization':[500,1,100],'initial':{'parameters':p0.tolist(),'objective':objective(p0[[1,4,7]]/[500,1,100],True)},'models':runs};save(HERE/'frozen_silhouette_candidates_v2.json',result)
    # Visualize geometry projections over the unmodified native pseudoRGB crop.
    panels=[]
    for title,pp in [('Initial five-control model',p0),('Colour-class objective minimum',np.array(best['parameters']))]:
        a=np.uint8(np.clip(img[1510:2010]*255,0,255));uv=predict(pp,q)+tr
        for k,col in [(1,(0,255,255)),(2,(255,0,255))]:
            kk=uv[labels==k];valid=(kk[:,0]>=0)&(kk[:,0]<1024)&(kk[:,1]>=1510)&(kk[:,1]<2010);kk=np.round(kk[valid]).astype(int);kk[:,0]=np.clip(kk[:,0],0,1023);kk[:,1]=np.clip(kk[:,1]-1510,0,499);a[kk[:,1],kk[:,0]]=np.array(col)
        panel=np.full((550,1024,3),245,np.uint8);panel[50:]=a;cv2.putText(panel,title+'; cyan=green XYZ, magenta=red XYZ',(10,29),cv2.FONT_HERSHEY_SIMPLEX,.6,(20,20,20),1);panels.append(panel)
    cv2.imwrite(str(HERE/'silhouette_projection_comparison_v2.jpg'),cv2.cvtColor(np.vstack(panels),cv2.COLOR_RGB2BGR))
if __name__=='__main__':main()
