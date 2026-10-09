from pathlib import Path
import hashlib,importlib.util,json
import cv2,numpy as np
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
source=ROOT/'generated/research_20260928_processing_20261007/spectral_geometry/extract_raw_board_observations.py'
spec=importlib.util.spec_from_file_location('board_reader',source);reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
sources=[]
for camera,targets in [('fx10',[661,970]),('fx17',[1301,970])]:
    panels=[]
    for target in targets:
        views=[]
        for run in ['002','003']:
            header=ROOT/f'data/main/test_plant_10-7/20260928/{run}-specim-{camera}.hdr'
            plane,meta=reader.load_plane(header,target);meta['header_relative_path']=str(header.relative_to(ROOT));sources.append(meta)
            np.savez_compressed(HERE/f'{run}_{camera}_{target}_first450.npz',raw_DN=plane[:450],first_line=0,source_band=meta['band_zero_based'],wavelength_nm=meta['actual_wavelength_nm'])
            lo,hi=np.percentile(plane[:450],[1,99]);display=np.uint8(np.clip((plane.astype(float)-lo)/(hi-lo),0,1)*255)
            cv2.imwrite(str(HERE/f'{run}_{camera}_{target}_display.png'),display)
            crop=cv2.cvtColor(display[:450],cv2.COLOR_GRAY2BGR);cv2.putText(crop,f'{run} {camera} {meta["actual_wavelength_nm"]} nm',(12,24),cv2.FONT_HERSHEY_SIMPLEX,.6,(20,180,255),2)
            views.append(crop)
        row=np.hstack(views);panels.append(row)
    cv2.imwrite(str(HERE/f'{camera}_source_start_pairs.png'),np.vstack(panels))
(HERE/'sources.json').write_text(json.dumps({'selected_band_reads':sources,'source_reader_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'scope':'Two recorded bands per sensor and run; memory-map full selected planes only, save first 450 native raw lines. Display percentile scaling does not alter raw arrays.'},indent=2)+'\n')
print(HERE)
