"""Freeze physical candidates before the independent agent scores reserved points."""
import hashlib,json
import numpy as np
from scipy.optimize import least_squares
from fit_physical_models import HERE,ROOT,BASE,read,save,predict,camera_values,stats

def main():
    old=read(HERE/'physical_model_results.json');plane=read(BASE/'hsi_geometry/shared_plane_calibration.json');height=read(BASE/'hsi_geometry/height_model_diagnostic/height_diagnostic.json');bridge=read(BASE/'hsi_geometry/rgb_bridge_review/independent_review.json');transfer=read(BASE/'hsi_geometry/scan_transfer_v1/scan_transfer.json');path=HERE.parent/'control_audit/new_provisional_training.json';new=read(path)
    B=np.array(old['audit']['basis']);O=np.array(old['audit']['origin_m']);T=np.array(bridge['T_plant_reference_from_calibration_zero']);camera='fx10';source=plane['per_sensor'][camera]['source_controls'];q=(np.array([r['reference_xyz_m'] for r in source])-O)@B;u=np.array([r['column_line_px'] for r in source]);tr=np.array(transfer['per_sensor'][camera]['translation_column_line_px']);controls=height['per_sensor'][camera]['controls'];initial=np.array(old['per_sensor'][camera]['models'][1]['full_selection_fit']['parameters'])
    models=[]
    for xyz_kind in ['depth_lift_reference_xyz_m','reference_xyz_m']:
        P=np.vstack([np.array([r['metric_plant_xyz'] for r in controls]),[r[xyz_kind] for r in new]]);uv=np.vstack([np.array([r['source_003_column_line'] for r in controls]),[r['native_hsi_column_line'] for r in new]])-tr;ep=((P-T[:3,3])@T[:3,:3]-O)@B
        for principal_sigma,line_sigma in [(51.2,250.),(25.6,130.),(10.24,65.)]:
            def residual(p):
                vals=camera_values(p)
                return np.r_[((predict(p,q)-u)/.75).ravel(),((predict(p,ep)-uv)/4.).ravel(),(vals['near_orthogonal_scan_principal_column_px']-511.5)/principal_sigma,p[7]/line_sigma]
            bounds=([-5000,-5000,-3000,-.5,.2,900,-300,-750,500],[0,5000,3000,.5,2.,1700,300,750,1700]);f=least_squares(residual,initial,bounds=bounds,x_scale=[1000,500,500,.05,1,1000,100,100,1000],max_nfev=1000,xtol=1e-11,gtol=1e-11,ftol=1e-11)
            models.append({'id':f'physical_fx10_{xyz_kind}_principal{principal_sigma:g}','sensor':'fx10','input_3d_field_for_new_controls':xyz_kind,'primary_candidate':xyz_kind=='depth_lift_reference_xyz_m' and principal_sigma==51.2,'principal_column_prior_mean_sigma':[511.5,principal_sigma],'line_height_prior_mean_sigma':[0,line_sigma],'HSI_training_sigma_px':4.,'parameters':f.x.tolist(),'optimizer_success':bool(f.success),'plane_fit':stats(predict(f.x,q)-u),'exposed_training_fit':stats(predict(f.x,ep)-uv),'camera_interpretation':camera_values(f.x),'coordinates':{'origin_calibration_reference_m':O.tolist(),'basis_columns':B.tolist(),'T_plant_reference_from_calibration':T.tolist(),'scan_002_to_003_column_line_translation':tr.tolist()},'training_ids':[r['id'] for r in controls]+[r['id'] for r in new],'prediction_recipe':'cal=(P_plant_m-T[:3,3])@T[:3,:3]; XYZ=(cal-origin)@basis; column=(ay*Y+ah*Z+a0)/(1+by*Y+bh*Z); line=lx*X+ly*Y+lh*Z+l0; add scan translation to obtain native003 column,line.','parameter_order':old['model_equations']['parameters']})
    result={'status':'FROZEN_BEFORE_RESERVED_CONTROL_SCORES','reserved_coordinates_consumed':False,'all_models_retained':True,'primary_selection_rule':'Weak optical prior, direct pixel depth-lift coordinate to avoid nearest-vertex shift; fixed before reserved scores. Alternatives are explicit sensitivity checks, not independent validation repetitions.','new_training_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'reserved_ids_only':['reserved_red_right_notch','reserved_red_distal_tip','reserved_green_basal_notch','reserved_green_basal_vein','reserved_green_distal_vein'],'models':models};save(HERE/'frozen_candidates.json',result)
    print(json.dumps([{'id':r['id'],'primary':r['primary_candidate'],'trainingRMS':r['exposed_training_fit']['rms_px'],'planeRMS':r['plane_fit']['rms_px']} for r in models],indent=2))
if __name__=='__main__':main()
