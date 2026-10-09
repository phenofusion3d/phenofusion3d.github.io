"""Selection-only physical scan-camera diagnostics; old evidence is immutable.

Fixed direction v implies detector column invariant under P -> P + t*v.
Column is rational in the two transverse coordinates; line is affine in XYZ.
The existing three exposed P5 features are selection controls, not new holdouts.
"""
from pathlib import Path
import csv, hashlib, json
import numpy as np
from scipy.optimize import least_squares

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
BASE=ROOT/'generated/research_confirmed_board_20261007'
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def stats(e):
    d=np.linalg.norm(e,axis=1)
    return {'n':len(d),'rms_px':float(np.sqrt(np.mean(d*d))),'max_px':float(d.max()),'median_px':float(np.median(d)),'residuals_column_line':e.tolist()}
def save(p,d): p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def predict(p,q):
    x,y,z=q.T
    return np.c_[(p[0]*y+p[1]*z+p[2])/(1+p[3]*y+p[4]*z),p[5]*x+p[6]*y+p[7]*z+p[8]]
def camera_values(p):
    n=np.array(p[:2]);d=np.array(p[3:5]);cx=float(n@d/(d@d))
    center=np.linalg.solve(np.array([n,d]),[-p[2],-1])
    return {'near_orthogonal_scan_principal_column_px':cx,'near_orthogonal_scan_focal_pixels':float(np.linalg.norm(n-cx*d)/np.linalg.norm(d)),'cross_section_camera_yz_m':center.tolist(),'line_height_tilt_degrees':float(np.degrees(np.arctan2(p[7],np.hypot(p[5],p[6]))))}

def main():
    paths={
      'metric':BASE/'d405_metric_calibration.json',
      'plane':BASE/'hsi_geometry/shared_plane_calibration.json',
      'height':BASE/'hsi_geometry/height_model_diagnostic/height_diagnostic.json',
      'bridge':BASE/'hsi_geometry/rgb_bridge_review/independent_review.json',
      'transfer':BASE/'hsi_geometry/scan_transfer_v1/scan_transfer.json',
      'static':BASE/'hsi_geometry/scan_transfer_v1/static_controls.csv'}
    d={k:read(p) for k,p in paths.items() if k!='static'}
    metric,plane,height,bridge,transfer=(d[k] for k in ('metric','plane','height','bridge','transfer'))
    origin=np.array(plane['plane_origin_reference_m']);normal=np.array(plane['plane_normal_reference']);oldbasis=np.array(plane['plane_basis_columns_reference']);v=np.array(metric['metric_motion_vector_m_per_previous_filename_unit']);v/=np.linalg.norm(v)
    # Use the measured full 3D motion, not its projected table direction.
    ey=oldbasis[:,1];ey-=v*(v@ey);ey/=np.linalg.norm(ey);ez=np.cross(v,ey);ez*=np.sign(ez@normal);basis=np.c_[v,ey,ez]
    T=np.array(bridge['T_plant_reference_from_calibration_zero'])
    result={'status':'physical_model_selection_diagnostics_no_new_independent_holdout','model_equations':{'column':'(ay*Y+ah*Z+a0)/(1+by*Y+bh*Z)','line':'lx*X+ly*Y+lh*Z+l0','parameters':['ay','ah','a0','by','bh','lx','ly','lh','l0'],'coordinates':'Calibration-zero metric frame, origin at recorded mean board plane; X parallel full 3D measured gantry motion.'},'selection_policy':'All old three P5 points and old board sheets have been inspected in prior work. Leave-one-feature/sheet diagnostics here are model-selection checks, not a new final validation set. No new reserved controls consumed.','source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths.values()},'audit':{'basis_orthonormal_max_error':float(np.max(np.abs(basis.T@basis-np.eye(3)))),'bridge_rotation_orthonormal_max_error':float(np.max(np.abs(T[:3,:3].T@T[:3,:3]-np.eye(3)))),'metres_per_previous_unit':metric['metres_per_previous_filename_unit'],'table_normal_motion_component':float(v@normal),'basis':basis.tolist(),'origin_m':origin.tolist(),'row_vector_inverse_bridge_formula':'calibration_xyz = (plant_xyz - T_translation) @ T_rotation','scale_policy':'Original old-unit localized reference XYZ scaled exactly once; calibration controls and bridge translations already metric.'},'per_sensor':{}}
    static=list(csv.DictReader(paths['static'].open(encoding='utf-8')))
    for sensor in ['fx10','fx17']:
        source=plane['per_sensor'][sensor]['source_controls'];xyz=np.array([r['reference_xyz_m'] for r in source]);q=(xyz-origin)@basis;uv=np.array([r['column_line_px'] for r in source]);sheets=np.array([r['hsi_sheet'] for r in source]);controls=height['per_sensor'][sensor]['controls'];P=np.array([r['metric_plant_xyz'] for r in controls]);cal=(P-T[:3,3])@T[:3,:3];eq=(cal-origin)@basis;eu=np.array([r['source_003_column_line'] for r in controls]);translation=np.array(transfer['per_sensor'][sensor]['translation_column_line_px']);eu-=translation
        cx=511.5 if sensor=='fx10' else 319.5
        plane_fit=next(x for x in plane['per_sensor'][sensor]['best_models'] if x['model']=='pushbroom_plane')['fit'];a=plane_fit['column_numerator_XY1'];b=plane_fit['column_denominator_XY_plus_one'];l=plane_fit['line_XY1'];initial=np.array([a[1],cx,a[2],b[1],1.,l[0],l[1],0.,l[2]])
        width=1024 if sensor=='fx10' else 640
        configs=[{'id':'joint_translating_rational','principal_sigma':None,'height_line_sigma':None}, {'id':'weak_optical_prior','principal_sigma':.05*width,'height_line_sigma':250.}, {'id':'moderate_optical_prior','principal_sigma':.025*width,'height_line_sigma':130.}, {'id':'near_nadir_optical_prior','principal_sigma':.01*width,'height_line_sigma':65.}]
        def fit(qtrain,utrain,etrain,config):
            qs=np.vstack([qtrain,eq[etrain]]);us=np.vstack([utrain,eu[etrain]]);sigma=np.r_[np.full(len(qtrain),.75 if sensor=='fx10' else .5),np.full(np.count_nonzero(etrain),2.)]
            def residual(p):
                rr=((predict(p,qs)-us)/sigma[:,None]).ravel();prior=[]
                if config['principal_sigma'] is not None:
                    vals=camera_values(p);prior.extend([(vals['near_orthogonal_scan_principal_column_px']-cx)/config['principal_sigma'],p[7]/config['height_line_sigma']])
                # Denominator must be positive at supplied points; bounds avoid camera below the lowest leaf.
                return np.r_[rr,prior]
            lo=np.array([-5000,-5000,-3000,-.5,.2,900,-300,-750,500]);hi=np.array([0,5000,3000,.5,2.,1700,300,750,1700]);sc=np.array([1000,500,500,.05,1,1000,100,100,1000])
            f=least_squares(residual,initial,bounds=(lo,hi),x_scale=sc,loss='linear',max_nfev=1500,ftol=1e-11,xtol=1e-11,gtol=1e-11)
            norms=np.linalg.norm(f.jac,axis=0);sv=np.linalg.svd(f.jac/np.maximum(norms,1e-15),compute_uv=False)
            return f.x,{'optimizer_success':bool(f.success),'nfev':f.nfev,'normalized_jacobian_condition':float(sv[0]/sv[-1]),'parameters':f.x.tolist(),'camera_interpretation':camera_values(f.x),'data_weighting':'board sigma 0.75 FX10 / 0.5 FX17 pixel; elevated sigma 2 pixels, linear loss','bounds':{'lower':lo.tolist(),'upper':hi.tolist()},'minimum_elevated_denominator':float(np.min(1+eq[:,1]*f.x[3]+eq[:,2]*f.x[4]))}
        runs=[]
        for config in configs:
            p,details=fit(q,uv,np.ones(3,bool),config);item={'config':config,'full_selection_fit':details,'plane_residual':stats(predict(p,q)-uv),'all_exposed_elevated_fit':stats(predict(p,eq)-eu),'leave_one_exposed_feature_out':[],'leave_one_sheet_out':[]}
            for held in range(3):
                train=np.arange(3)!=held;pf,fd=fit(q,uv,train,config);pred=predict(pf,eq);item['leave_one_exposed_feature_out'].append({'held_id':controls[held]['id'],'training_ids':[controls[i]['id'] for i in np.flatnonzero(train)],'error_px':float(np.linalg.norm(pred[held]-eu[held])),'residual_column_line':(pred[held]-eu[held]).tolist(),'prediction_plant_column_line':(pred[held]+translation).tolist(),'fit':fd})
            for sheet in sorted(set(sheets)):
                test=sheets==sheet;pf,fd=fit(q[~test],uv[~test],np.ones(3,bool),config);item['leave_one_sheet_out'].append({'held_sheet':sheet,'held':stats(predict(pf,q[test])-uv[test]),'fit':fd})
            runs.append(item)
        # Static scan drift learned from previously exposed controls: explicitly not a fresh validation set.
        rows=[r for r in static if r['sensor']==sensor and r['accepted_numeric_and_visual']=='True' and abs(float(r['band_nm'])-(661.1 if sensor=='fx10' else 1301.42))<3]
        sq=np.array([[float(r['source_column']),float(r['source_line'])] for r in rows]);delta=np.array([[float(r['delta_column']),float(r['delta_line'])] for r in rows]);scan=[]
        for degree in [1,2]:
            sx=(sq[:,1]-1063.5)/1063.5;V=np.vander(sx,degree+1,increasing=True);co=np.linalg.lstsq(V,delta,rcond=None)[0];els=np.vander((eu[:,1]-1063.5)/1063.5,degree+1,increasing=True)@co
            leave=[]
            for i in range(len(sq)):
                z=np.arange(len(sq))!=i;c=np.linalg.lstsq(V[z],delta[z],rcond=None)[0];leave.append(V[i]@c-delta[i])
            scan.append({'degree':degree,'features':[r['feature'] for r in rows],'coefficients':co.tolist(),'leave_one_previously_exposed_feature_out':stats(np.array(leave)),'predicted_delta_at_elevated_controls':els.tolist(),'delta_line_difference_red_pair':float(els[1,1]-els[0,1]),'baseline_start_median_translation':translation.tolist()})
        plane_pred=np.c_[eq[:,:2],np.ones(3)]@np.array(next(x for x in plane['per_sensor'][sensor]['best_models'] if x['model']=='affine')['fit']['coefficient_XY1_to_column_line'])
        difference=(eu[1,1]-eu[0,1])-(plane_pred[1,1]-plane_pred[0,1]);dz=float(eq[1,2]-eq[0,2]);result['per_sensor'][sensor]={'controls':[dict(id=c['id'],motion_frame_xyz=eq[i].tolist(),native_plant_column_line=(eu[i]+translation).tolist()) for i,c in enumerate(controls)],'red_pair_line_conflict':{'observed_separation_px':float(eu[1,1]-eu[0,1]),'plane_predicted_separation_px':float(plane_pred[1,1]-plane_pred[0,1]),'difference_px':float(difference),'height_difference_m':dz,'required_height_coefficient_if_other_coefficients_fixed_px_per_m':float(difference/dz),'required_scan_plane_tilt_degrees':float(np.degrees(np.arctan2(abs(difference/dz),l[0])))},'models':runs,'scan_transfer_model_selection':scan}
    save(HERE/'physical_model_results.json',result)
    summary={s:{'red_pair':v['red_pair_line_conflict'],'models':[{'id':x['config']['id'],'plane_rms':x['plane_residual']['rms_px'],'exposed_elevated_fit_rms':x['all_exposed_elevated_fit']['rms_px'],'leave_one_exposed_errors':[r['error_px'] for r in x['leave_one_exposed_feature_out']],'whole_sheet_rms':[r['held']['rms_px'] for r in x['leave_one_sheet_out']]} for x in v['models']],'scan_red_pair_delta':[x['delta_line_difference_red_pair'] for x in v['scan_transfer_model_selection']]} for s,v in result['per_sensor'].items()};save(HERE/'summary.json',summary);print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
