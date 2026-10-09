"""Confirmed-board HSI/D405 common-plane controls; no plant projection."""
from pathlib import Path
import csv
import hashlib
import itertools
import json
import numpy as np
import cv2
from scipy.optimize import least_squares
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
METRIC=HERE.parent/'d405_metric_calibration.json'
OBS=ROOT/'generated/research_20260928_processing_20261007/spectral_geometry/raw_calibration_marker_observations.json'
IMAGES=[ROOT/'generated/research_20260928_processing_20261007/spectral_geometry/002_fx10_marker_observations.png',ROOT/'generated/research_20260928_readiness_20261007/checkerboard_calibration/corners_sample_13.png']

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def stats(error):
    length=np.linalg.norm(error,axis=1)
    return dict(n=len(length),rms_px=float(np.sqrt(np.mean(length**2))),median_px=float(np.median(length)),p95_px=float(np.quantile(length,.95)),max_px=float(length.max()),rms_column_px=float(np.sqrt(np.mean(error[:,0]**2))),rms_line_px=float(np.sqrt(np.mean(error[:,1]**2))))
def fit(xy,uv,kind):
    v=np.column_stack([xy,np.ones(len(xy))])
    if kind=='affine':
        coef=np.linalg.lstsq(v,uv,rcond=None)[0]
        return lambda x:np.column_stack([x,np.ones(len(x))])@coef,{'coefficient_XY1_to_column_line':coef.tolist()}
    if kind=='homography':
        H,_=cv2.findHomography(xy.astype(np.float64),uv.astype(np.float64),0)
        assert H is not None
        return lambda x:cv2.perspectiveTransform(x[None].astype(np.float64),H)[0],{'homography_XY1_to_column_line':H.tolist()}
    line=np.linalg.lstsq(v,uv[:,1],rcond=None)[0]
    u=uv[:,0]
    initial=np.linalg.lstsq(np.column_stack([v,-u[:,None]*xy]),u,rcond=None)[0]
    predict=lambda p,x:(np.column_stack([x,np.ones(len(x))])@p[:3])/(1+x@p[3:])
    result=least_squares(lambda p:predict(p,xy)-u,initial,max_nfev=1000,xtol=1e-12,ftol=1e-12,gtol=1e-12)
    return lambda x:np.column_stack([predict(result.x,x),np.column_stack([x,np.ones(len(x))])@line]),{'line_XY1':line.tolist(),'column_numerator_XY1':result.x[:3].tolist(),'column_denominator_XY_plus_one':result.x[3:].tolist(),'optimizer_success':bool(result.success)}

def main():
    metric=json.loads(METRIC.read_text());observations=json.loads(OBS.read_text())
    board=cv2.aruco.CharucoBoard((7,10),.025,.018,cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50))
    # Exact nominal marker centres: ratio does not alter a marker's cell centre.
    centers={int(i):np.round(np.asarray(p,dtype=np.float64).mean(0)/.025*2)/2*.025 for i,p in zip(board.getIds().flatten(),board.getObjPoints())}
    models={m['sheet']:m for m in metric['board_models']}
    allworld=np.array([np.asarray(m['R_board_to_reference'])@p+np.asarray(m['t_board_to_reference_m']) for m in models.values() for p in centers.values()])
    origin=allworld.mean(0);_,singular,V=np.linalg.svd(allworld-origin,full_matrices=False)
    normal=V[2];normal*=np.sign(normal[2])
    motion=np.asarray(metric['metric_motion_vector_m_per_previous_filename_unit'])
    axisx=motion-normal*(normal@motion);axisx/=np.linalg.norm(axisx)
    axisy=np.cross(normal,axisx);basis=np.column_stack([axisx,axisy])
    plane_height=(allworld-origin)@normal
    mapping_order=['top','middle_rotated','bottom'];sheets=['left_sheet','middle_sheet','right_sheet']
    output={'status':'shared_metric_calibration_plane_diagnostics_not_leaf_projection','board_square_m':.025,'board_marker_m':.018,'coordinate_frame':'D405 calibration camera at filename coordinate zero under fixed-mount shared-linear-motion fit; not the plant bundle reference frame','plane_origin_reference_m':origin.tolist(),'plane_basis_columns_reference':basis.tolist(),'plane_normal_reference':normal.tolist(),'plane_singular_values':singular.tolist(),'control_height_about_best_plane_m':{'min':float(plane_height.min()),'max':float(plane_height.max()),'rms':float(np.sqrt(np.mean(plane_height**2)))},'observation_policy':'All saved decoded marker centres with nominal board positions; no prior inlier filtering. Sheet IDs qualify repeated marker IDs. Image observations are unchanged. Marker centres are derived from nominal cell centres; 18/25 ratio confirms physical design but does not alter centres.','visual_sheet_identity':{'mapping':dict(zip(mapping_order,sheets)),'evidence':['White reference board lies adjacent to HSI top and D405 left sheet in the inspected images.','Distinctive rotated central sheet matches HSI middle_rotated and D405 middle_sheet.','Outer sheets have opposite decoded marker orientations, consistent with the remaining bottom-to-right ordering.'],'status':'assistant visual review plus permutation diagnostics; not independent operator-confirmed physical labels','images':[str(p.relative_to(ROOT)) for p in IMAGES]},'per_sensor':{},'limitations':['Fits describe calibration-table marker centres at one selected wavelength per sensor.','No controls or maps are transferred to the plant run or optimized plant reference frame here.','Whole-sheet held-outs assess this plane and selected-band geometry, not elevated leaves or independent final model validation.','Small apparent departures from a common plane include paper warp and D405 pose uncertainty; they are not independent multi-height calibration evidence.','Physical units now use confirmed 25 mm cells, but board pose and marker-centre measurement uncertainty remain.','No calibrated reflectance, dense fusion or health claim follows from these fits.']}
    controls_all=[];fig,axes=plt.subplots(2,2,figsize=(13,9),layout='constrained')
    for si,sensor in enumerate(observations['sensors']):
        camera=sensor['camera'];candidates=[]
        for perm in itertools.permutations(sheets):
            mapping=dict(zip(mapping_order,perm));controls=[]
            for sheet in sensor['sheets']:
                target=models[mapping[sheet['physical_sheet_key']]];R=np.asarray(target['R_board_to_reference']);t=np.asarray(target['t_board_to_reference_m'])
                for m in sheet['marker_observations']:
                    if 'model_centre_board_square_xy' not in m:continue
                    marker_id=m['marker_id'];obj=centers[marker_id];assert np.max(np.abs(obj[:2]-.025*np.array(m['model_centre_board_square_xy'])))<1e-7
                    xyz=R@obj+t;xy=(xyz-origin)@basis
                    controls.append(dict(sensor=camera,hsi_sheet=sheet['physical_sheet_key'],d405_sheet=mapping[sheet['physical_sheet_key']],marker_id=marker_id,board_xyz_m=obj.tolist(),reference_xyz_m=xyz.tolist(),plane_xy_m=xy.tolist(),column_line_px=m['centre_column_line_px'],old_grid_inlier=m['grid_homography_inlier']))
            xy=np.array([c['plane_xy_m'] for c in controls]);uv=np.array([c['column_line_px'] for c in controls]);keys=np.array([c['hsi_sheet'] for c in controls]);ids=np.array([c['marker_id'] for c in controls])
            diagnostics=[]
            for kind in ['affine','pushbroom_plane','homography']:
                predictor,params=fit(xy,uv,kind);holdouts=[]
                for held in mapping_order:
                    test=keys==held;pred,fit_params=fit(xy[~test],uv[~test],kind)
                    holdouts.append(dict(held_sheet=held,train_count=int((~test).sum()),test_count=int(test.sum()),train=stats(pred(xy[~test])-uv[~test]),held_out=stats(pred(xy[test])-uv[test]),held_marker_ids=ids[test].tolist(),predicted_column_line=pred(xy[test]).tolist(),residual_column_line=(pred(xy[test])-uv[test]).tolist(),fit=fit_params))
                diagnostics.append(dict(model=kind,full_fit=stats(predictor(xy)-uv),fit=params,leave_one_sheet_out=holdouts,held_out_pooled_rms_px=float(np.sqrt(np.mean(np.concatenate([np.array(h['residual_column_line']) for h in holdouts])**2)*2))))
            candidates.append(dict(mapping=mapping,models=diagnostics))
            if list(perm)==sheets:
                best_controls=controls;best_xy=xy;best_uv=uv;best_keys=keys
        candidates.sort(key=lambda x:x['models'][0]['full_fit']['rms_px'])
        assert candidates[0]['mapping']==dict(zip(mapping_order,sheets)), candidates[0]['mapping']
        best=candidates[0];models_out=best['models'];controls_all+=best_controls
        output['per_sensor'][camera]={'source':sensor['source'],'controls':len(best_controls),'selected_mapping':best['mapping'],'all_six_permutations':candidates,'best_models':models_out,'source_controls':best_controls,'model_selection_status':'Mapping and model diagnostics use the listed controls/holdouts; no independent final validation set.'}
        pred,_=fit(best_xy,best_uv,'affine');error=pred(best_xy)-best_uv
        palette={'top':'#2678a0','middle_rotated':'#ba6834','bottom':'#268368'}
        for sheet in mapping_order:
            mask=best_keys==sheet
            axes[si,0].scatter(best_xy[mask,0],best_xy[mask,1],s=16,label=sheet,color=palette[sheet])
            axes[si,1].quiver(best_uv[mask,0],best_uv[mask,1],error[mask,0],error[mask,1],angles='xy',scale_units='xy',scale=.3,color=palette[sheet],width=.003)
        axes[si,0].set(title=f'{camera.upper()}: shared metric table controls',xlabel='Along gantry / m',ylabel='Across table / m');axes[si,0].axis('equal');axes[si,0].legend(fontsize=8)
        axes[si,1].set(title=f'{camera.upper()}: affine training residuals × 3.33',xlabel='Recorded detector column',ylabel='Recorded scan line');axes[si,1].invert_yaxis()
    fig.suptitle('Confirmed 25 mm board: table-plane controls only; no elevated-leaf projection',fontsize=14);fig.savefig(HERE/'shared_plane_diagnostics.png',dpi=150);plt.close(fig)
    inputs=[METRIC,OBS,Path(__file__),*IMAGES,HERE.parent/'board_confirmation.json']
    output['source_hashes']=[dict(path=str(p.relative_to(ROOT)),sha256=sha(p)) for p in inputs]
    (HERE/'shared_plane_calibration.json').write_text(json.dumps(output,indent=2)+'\n')
    with (HERE/'shared_metric_controls.csv').open('w',newline='') as stream:
        fields=['sensor','hsi_sheet','d405_sheet','marker_id','reference_x_m','reference_y_m','reference_z_m','plane_x_m','plane_y_m','detector_column_px','scan_line_px','old_grid_inlier']
        w=csv.DictWriter(stream,fieldnames=fields);w.writeheader()
        for c in controls_all:
            row={k:c[k] for k in ['sensor','hsi_sheet','d405_sheet','marker_id','old_grid_inlier']};row.update(dict(zip(fields[4:11],c['reference_xyz_m']+c['plane_xy_m']+c['column_line_px'])));w.writerow(row)
    compact={cam:{'controls':v['controls'],'mapping':v['selected_mapping'],'models':[{'model':x['model'],'fit_rms':x['full_fit']['rms_px'],'pooled_holdout_rms':x['held_out_pooled_rms_px'],'heldouts':[{k:h[k] for k in ['held_sheet','held_out']} for h in x['leave_one_sheet_out']]} for x in v['best_models']],'wrong_mapping_best_fit_rms':min(c['models'][0]['full_fit']['rms_px'] for c in v['all_six_permutations'][1:])} for cam,v in output['per_sensor'].items()}
    (HERE/'summary.json').write_text(json.dumps(compact,indent=2)+'\n');print(json.dumps(compact,indent=2))

if __name__=='__main__':main()
