"""Joint metric scan-camera / RGB run-bridge fit, retaining all exposed failures."""
from pathlib import Path
import json
import cv2,numpy as np
from scipy.optimize import least_squares
from fit_physical_models import HERE,ROOT,BASE,read,save,predict,camera_values,stats

def main():
    physical=read(HERE/'physical_model_results.json');plane=read(BASE/'hsi_geometry/shared_plane_calibration.json');metric=read(BASE/'d405_metric_calibration.json');height=read(BASE/'hsi_geometry/height_model_diagnostic/height_diagnostic.json');bridge=read(BASE/'hsi_geometry/rgb_bridge_review/independent_review.json');paper=read(BASE/'rgb_run_transfer_paper_v2/summary.json');transfer=read(BASE/'hsi_geometry/scan_transfer_v1/scan_transfer.json');poses={r['frame']:np.array(r['transform']) for r in read(BASE/'d405_metric/icp_diagnostics_reexpressed.json')}
    basis=np.array(physical['audit']['basis']);origin=np.array(physical['audit']['origin_m']);K=np.array(metric['selected_K']);D=np.array(metric['selected_distortion']);T0=np.array(bridge['T_plant_reference_from_calibration_zero']);p0=cv2.Rodrigues(T0[:3,:3])[0].ravel();p0=np.r_[p0,T0[:3,3]]
    points=[];pixels=[];cameras=[]
    for r in paper['records']:
        if 'calibration_pixels' not in r:continue
        keys=np.round(np.c_[r['calibration_pixels'],r['plant_pixels']],4);_,ix=np.unique(keys,axis=0,return_index=True);ix.sort();points.extend(np.array(r['calibration_plane_points_m'])[ix]);pixels.extend(np.array(r['plant_pixels'])[ix]);cameras.extend([poses[r['frame']]]*len(ix))
    P=np.array(points);U=np.array(pixels);C=np.array(cameras)
    board={};elev={};names=[];initial=[]
    for sensor in ['fx10','fx17']:
        r=plane['per_sensor'][sensor]['source_controls'];board[sensor]=((np.array([x['reference_xyz_m'] for x in r])-origin)@basis,np.array([x['column_line_px'] for x in r]));r=height['per_sensor'][sensor]['controls'];elev[sensor]=(np.array([x['metric_plant_xyz'] for x in r]),np.array([x['source_003_column_line'] for x in r])-transfer['per_sensor'][sensor]['translation_column_line_px']);initial.extend(physical['per_sensor'][sensor]['models'][1]['full_selection_fit']['parameters'])
        names=[x['id'] for x in r]
    initial=np.r_[initial,p0]
    def reproject(bp):
        R=cv2.Rodrigues(bp[:3])[0];q=P@R.T+bp[3:];pc=np.einsum('nj,njk->nk',q-C[:,:3,3],C[:,:3,:3]);return cv2.projectPoints(pc,np.zeros(3),np.zeros(3),K,D)[0].reshape(-1,2)-U
    def elev_coords(sensor,bp):
        R=cv2.Rodrigues(bp[:3])[0];return ((elev[sensor][0]-bp[3:])@R-origin)@basis
    camera_lo=[-5000,-5000,-3000,-.5,.2,900,-300,-750,500];camera_hi=[0,5000,3000,.5,2.,1700,300,750,1700];lower=np.r_[camera_lo,camera_lo,p0[:3]-.0873,p0[3:]-.03];upper=np.r_[camera_hi,camera_hi,p0[:3]+.0873,p0[3:]+.03];scale=np.r_[[1000,500,500,.05,1,1000,100,100,1000]*2,[.01,.01,.01,.01,.01,.01]]
    results=[]
    for rgb_sigma in [1.,2.,5.]:
        for held in [-1,0,1,2]:
            selected=np.ones(3,bool) if held<0 else np.arange(3)!=held
            def residual(p):
                pieces=[(reproject(p[18:])/rgb_sigma).ravel()]
                for si,sensor in enumerate(['fx10','fx17']):
                    pp=p[si*9:(si+1)*9];q,u=board[sensor];pieces.extend([((predict(pp,q)-u)/(.75 if si==0 else .5)).ravel(),((predict(pp,elev_coords(sensor,p[18:]))-elev[sensor][1])[selected]/4.).ravel()]);values=camera_values(pp);pieces.append(np.array([(values['near_orthogonal_scan_principal_column_px']-(511.5 if si==0 else 319.5))/(51.2 if si==0 else 32.),pp[7]/250.]))
                return np.concatenate(pieces)
            f=least_squares(residual,initial,bounds=(lower,upper),x_scale=scale,max_nfev=800,ftol=1e-10,xtol=1e-10,gtol=1e-10)
            rr={'RGB_paper_sigma_px':rgb_sigma,'HSI_exposed_control_sigma_px':4.,'held_old_control_index':held,'selection_status':'No new reserved controls; previously exposed features only. FX17 tracks are correlated with FX10.','optimizer_success':bool(f.success),'nfev':f.nfev,'paper_residual':stats(reproject(f.x[18:])),'bridge_parameters':f.x[18:].tolist(),'bridge_delta_rotation_degrees':float(np.linalg.norm(f.x[18:21]-p0[:3])*180/np.pi),'bridge_delta_translation_m':(f.x[21:]-p0[3:]).tolist(),'per_sensor':{}}
            for si,sensor in enumerate(['fx10','fx17']):
                pp=f.x[si*9:(si+1)*9];q,u=board[sensor];er=predict(pp,elev_coords(sensor,f.x[18:]))-elev[sensor][1];rr['per_sensor'][sensor]={'parameters':pp.tolist(),'camera_interpretation':camera_values(pp),'plane':stats(predict(pp,q)-u),'all_exposed_controls':stats(er),'held_old_control_error_px':float(np.linalg.norm(er[held])) if held>=0 else None,'predictions_calibration_column_line':predict(pp,elev_coords(sensor,f.x[18:])).tolist()}
            results.append(rr)
            print(json.dumps({'rgb_sigma':rgb_sigma,'held':held,'paper_rms':rr['paper_residual']['rms_px'],'elevated':[rr['per_sensor'][s]['held_old_control_error_px'] if held>=0 else rr['per_sensor'][s]['all_exposed_controls']['rms_px'] for s in ['fx10','fx17']]}),flush=True)
    save(HERE/'joint_bridge_results.json',{'status':'joint_bridge_physical_model_selection_only','paper_unique_pairs':len(P),'method':'Original paper pixels, fixed accepted metric RGB poses/intrinsics, two gantry-invariant rational scan cameras, jointly optimized six-DOF calibration-to-plant bridge; sigma5 RGB case is stress relaxation, not accepted uncertainty.','results':results})
if __name__=='__main__':main()
