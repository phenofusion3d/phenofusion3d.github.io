"""Reviewable local template displacements of static calibration/plant controls."""
from pathlib import Path
import json,hashlib,importlib.util
import cv2,numpy as np
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
reader_path=ROOT/'generated/research_20260928_processing_20261007/spectral_geometry/extract_raw_board_observations.py'
spec=importlib.util.spec_from_file_location('board_reader',reader_path);reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
plane=json.loads((HERE.parent/'shared_plane_calibration.json').read_text())
# Fixed source locations chosen on visible static supports/grid; no plant matches.
anchors=[('panel_left_corner','start_fit',145,162),('panel_right_corner','start_fit',908,160),('left_support_a','start_fit',251,179),('left_support_b','start_fit',318,178),('right_support_a','start_fit',759,176),('right_support_b','start_fit',811,178),('table_start_corner','start_holdout',99,204),('ink_top_cross','start_holdout',224,216),('left_grid_615','long_holdout',223,615),('left_grid_914','long_holdout',223,914),('left_grid_1420','long_holdout',223,1420),('left_grid_1920','long_holdout',223,1920),('end_cross_left','long_holdout',366,2020),('end_cross_middle','long_holdout',524,2020),('end_cross_right','long_holdout',670,2020)]
a10=np.array(plane['per_sensor']['fx10']['best_models'][0]['fit']['coefficient_XY1_to_column_line']);a17=np.array(plane['per_sensor']['fx17']['best_models'][0]['fit']['coefficient_XY1_to_column_line'])
def convert(p):return (np.array(p)-a10[2])@np.linalg.inv(a10[:2])@a17[:2]+a17[2]
def gray(p):return cv2.imread(str(p),cv2.IMREAD_GRAYSCALE)
def local_match(A,B,xy,half=18,search=12):
    x,y=np.rint(xy).astype(int);tpl=A[y-half:y+half+1,x-half:x+half+1]
    roi=B[y-half-search:y+half+search+1,x-half-search:x+half+search+1]
    if tpl.shape!=(2*half+1,2*half+1) or roi.shape!=(2*(half+search)+1,2*(half+search)+1):return None
    score=cv2.matchTemplate(roi,tpl,cv2.TM_CCOEFF_NORMED);_,maximum,_,p=cv2.minMaxLoc(score);peak=np.array(p,dtype=float)
    for dim in range(2):
        px,py=p
        if 0<p[dim]<score.shape[1-dim]-1:
            vals=score[py,px-1:px+2] if dim==0 else score[py-1:py+2,px]
            denom=vals[0]-2*vals[1]+vals[2]
            if denom<0:peak[dim]+=.5*(vals[0]-vals[2])/denom
    dxdy=peak-search
    gx=cv2.Sobel(tpl.astype(np.float32),cv2.CV_32F,1,0,ksize=3);gy=cv2.Sobel(tpl.astype(np.float32),cv2.CV_32F,0,1,ksize=3)
    eig=np.linalg.eigvalsh(np.array([[np.sum(gx*gx),np.sum(gx*gy)],[np.sum(gx*gy),np.sum(gy*gy)]]))
    away=score.copy();away[max(0,p[1]-3):p[1]+4,max(0,p[0]-3):p[0]+4]=-1
    return {'source_xy':[int(x),int(y)],'target_xy':(np.array([x,y])+dxdy).tolist(),'shift_column_line':dxdy.tolist(),'NCC':float(maximum),'peak_margin_outside_3px':float(maximum-away.max()),'gradient_eigenvalue_ratio':float(eig[0]/max(eig[1],1e-12)),'search_radius_px':search,'template_width_px':2*half+1,'at_search_border':bool(min(p)==0 or max(p)==2*search)}
out={'status':'static_source_features_local_translation_probe_not_physical_camera_calibration','coordinate_convention':'Native zero-based detector column, acquisition line. All source feature coordinates fixed before testing. Search restricted to ±12 pixels because visual source comparison shows nearly aligned static background; this is not a wide-range independent retrieval test.','candidates':[]}
for camera,bands in [('fx10',[661,970]),('fx17',[1301,970])]:
    panels=[]
    for band in bands:
        Adis=gray(HERE/f'002_{camera}_{band}_display.png');Bdis=gray(HERE/f'003_{camera}_{band}_display.png');crops=[]
        A,metaA=reader.load_plane(ROOT/f'data/main/test_plant_10-7/20260928/002-specim-{camera}.hdr',band)
        B,metaB=reader.load_plane(ROOT/f'data/main/test_plant_10-7/20260928/003-specim-{camera}.hdr',band)
        A=A.astype(np.float32);B=B.astype(np.float32)
        for name,group,x,y in anchors:
            xy=(x,y) if camera=='fx10' else convert((x,y))
            record=local_match(A,B,xy)
            if record is None:continue
            record.update(sensor=camera,nominal_band_nm=band,actual_wavelength_nm=metaA['actual_wavelength_nm'],feature=name,split=group,measurement='Raw DN float32 templates; no display rescaling, clipping or interpolation before matching',source_selected_plane_sha256=metaA['selected_plane_sha256_little_endian_uint16_row_major'],target_selected_plane_sha256=metaB['selected_plane_sha256_little_endian_uint16_row_major'])
            record['passes_numeric_candidate_gate']=record['NCC']>=.85 and record['peak_margin_outside_3px']>=.025 and record['gradient_eigenvalue_ratio']>=.015 and not record['at_search_border']
            out['candidates'].append(record)
            canvas=np.full((102,250,3),235,np.uint8)
            for col,(im,point) in enumerate([(Adis,record['source_xy']),(Bdis,record['target_xy'])]):
                crop=cv2.getRectSubPix(im,(65,65),tuple(float(v) for v in point));crop=cv2.cvtColor(crop,cv2.COLOR_GRAY2BGR);cv2.drawMarker(crop,(32,32),(0,80,255),cv2.MARKER_CROSS,10,1)
                canvas[23:88,col*125+30:col*125+95]=crop
            colour=(20,110,20) if record['passes_numeric_candidate_gate'] else (20,20,180)
            cv2.putText(canvas,f'{name} {band}',(4,15),cv2.FONT_HERSHEY_SIMPLEX,.36,colour,1)
            cv2.putText(canvas,f'NCC {record["NCC"]:.3f} d {record["shift_column_line"][0]:.2f},{record["shift_column_line"][1]:.2f}',(4,98),cv2.FONT_HERSHEY_SIMPLEX,.34,colour,1)
            crops.append(canvas)
        panels.append(np.vstack(crops))
    cv2.imwrite(str(HERE/f'{camera}_static_feature_crops.png'),np.hstack(panels))
(HERE/'static_feature_candidates.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps([dict(sensor=r['sensor'],band=r['nominal_band_nm'],feature=r['feature'],shift=r['shift_column_line'],NCC=r['NCC'],gate=r['passes_numeric_candidate_gate']) for r in out['candidates']],indent=2))
