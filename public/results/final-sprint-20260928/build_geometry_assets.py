"""Read frozen results and create review-only website derivatives; never reconstruct.

Run from the repository root with the existing NumPy/Matplotlib environment.
"""
from pathlib import Path
import gzip
import hashlib
import json
import shutil
import struct
import numpy as np

ROOT = Path.cwd()
BASE = ROOT / 'generated/research_confirmed_board_20261007'
OUT = BASE / 'website/geometry'
AUDIT = OUT / 'validation'
FUSION = BASE / 'fusion_v1'
CLEAN = BASE / 'cleanup_v1'
D405 = BASE / 'd405_metric'
L515 = BASE / 'l515_metric_boardgain_v1'
DTYPE = np.dtype([('x','<f8'),('y','<f8'),('z','<f8'),('r','u1'),('g','u1'),('b','u1')])
WEB_DTYPE = np.dtype([('x','<f4'),('y','<f4'),('z','<f4'),('r','u1'),('g','u1'),('b','u1')])


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1024*1024), b''):
            h.update(b)
    return h.hexdigest()


def rel(path):
    return Path(path).relative_to(ROOT).as_posix()


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def read_ply(path):
    # All selected frozen clouds have the same six-property binary record layout.
    with Path(path).open('rb') as f:
        lines = []
        while True:
            line = f.readline().decode('ascii').strip()
            lines.append(line)
            if line == 'end_header':
                break
        assert 'format binary_little_endian 1.0' in lines
        props = [s for s in lines if s.startswith('property ')]
        assert props == ['property double x','property double y','property double z',
                         'property uchar red','property uchar green','property uchar blue'], props
        count = int(next(s for s in lines if s.startswith('element vertex ')).split()[-1])
        offset = f.tell()
    assert Path(path).stat().st_size == offset + count * DTYPE.itemsize
    return np.memmap(path, dtype=DTYPE, mode='r', offset=offset, shape=(count,))


def xyz(records):
    return np.column_stack([records[k] for k in ('x','y','z')])


def rgb(records):
    return np.column_stack([records[k] for k in ('r','g','b')])


for child in ['clouds','provenance','downloads','figures']:
    (OUT/child).mkdir(parents=True, exist_ok=True)
AUDIT.mkdir(parents=True, exist_ok=True)

cleanup = read_json(CLEAN/'result/summary.json')
fusion = read_json(FUSION/'summary.json')
calibration_path = ROOT/'generated/research_20260928_processing_20261007/calibration_transfer.json'
calibration = read_json(calibration_path)
metric_calibration = read_json(BASE/'d405_metric_calibration.json')
metric_scale = metric_calibration['metres_per_previous_filename_unit']
R = np.asarray(cleanup['upright_R'])
assert np.array_equal(R, np.asarray(fusion['upright_R']))
assert np.array_equal(R, np.asarray(calibration['upright_export_R_reference_camera_to_xyz_z_up']))
# The old research viewers use board Z-up. The new Three.js viewer uses Y-up.
Y_FROM_Z = np.array([[1.,0.,0.],[0.,0.,1.],[0.,-1.,0.]])
DISPLAY_R = Y_FROM_Z @ R
assert np.allclose(DISPLAY_R @ DISPLAY_R.T, np.eye(3), atol=1e-12)
assert np.isclose(np.linalg.det(DISPLAY_R), 1., atol=1e-12)

fp = np.load(FUSION/'fused_point_provenance.npz')
ld = np.load(FUSION/'l515_fusion_decisions.npz')
clean_prov = np.load(CLEAN/'result/plants_cleaned_provenance.npz')
stages = {
    'd405': {'path': FUSION/'d405_review_reference.ply', 'label': 'D405',
             'old': ROOT/'generated/research_d405_l515_fusion_20261007/v1/review/d405_review_upright.ply',
             'description': 'Preserved 64-view D405 RGB stereo geometry expressed at the supplied 25mm board scale. Point identities, RGB and topology unchanged; inherited voxel spacing is 1.028875mm.',
             'camera_id': fp['camera_id'][:fusion['d405_points']],
             'original_point_index': fp['original_point_index'][:fusion['d405_points']],
             'fused_point_index': np.arange(fusion['d405_points'],dtype=np.int64)},
    'l515': {'path': FUSION/'l515_aligned_review_reference.ply', 'label': 'L515 aligned',
             'old': None,
             'description': 'New 64-view L515 sensor ICP/TSDF with board-based empirical depth adjustment, rigidly aligned to metric D405; all reviewed L515 points before fusion filtering. Device depth units are not independently confirmed.',
             'camera_id': np.ones(fusion['l515_review_points'],dtype=np.uint8),
             'original_point_index': ld['l515_source_indices']},
    'fused': {'path': FUSION/'fused_review_reference.ply', 'label': 'D405 + L515 before cleanup',
              'old': None,
              'description': f"Observed-point union: every D405 inspection-region point retained plus {fusion['l515_added_points']:,} selected L515 points. No shape completion.",
              'camera_id': fp['camera_id'], 'original_point_index': fp['original_point_index'],
              'fused_point_index': np.arange(fusion['fused_points'],dtype=np.int64)},
    'cleaned': {'path': CLEAN/'result/plants_cleaned_reference.ply', 'label': 'Cleaned candidate',
                'old': None,
                'description': 'Exact saved source-reviewed candidate plant subset; uncertain points and scene context remain separately preserved.',
                **{k:clean_prov[k] for k in clean_prov.files}},
}
full_source_paths = {
    '0': D405/'full_scene_reference.ply',
    '1': L515/'result/l515_supported_reference.ply',
}
full_records = {k:read_ply(p) for k,p in full_source_paths.items()}
T = np.asarray(fusion['T_D405_reference_from_L515_reference'])
input_files = {BASE/'d405_metric_calibration.json', BASE/'board_confirmation.json', BASE/'cross_camera/selection.json', calibration_path, CLEAN/'result/summary.json', FUSION/'summary.json',
               FUSION/'fused_point_provenance.npz',FUSION/'l515_fusion_decisions.npz',
               CLEAN/'result/plants_cleaned_provenance.npz',*full_source_paths.values()}
for v in stages.values():
    input_files.add(v['path'])
    if v['old'] is not None: input_files.add(v['old'])
    v['records'] = read_ply(v['path'])
    v['upright'] = xyz(v['records']) @ R.T
    v['display'] = v['upright'] @ Y_FROM_Z.T

# Crop policy is explicitly a new display ROI, not biological membership.
# Identical boxes are applied to the three pre-cleanup stage clouds.
crops = {}
plant_records = {}
for i in range(1,6):
    plant = f'P{i}'
    p = CLEAN/'result'/f'{plant}_reference.ply'
    pp = CLEAN/'result'/f'{plant}_provenance.npz'
    old = None
    input_files.update((p,pp))
    a = read_ply(p)
    u = xyz(a) @ R.T
    seed = np.asarray(cleanup['parameters']['soil_seed_upright'][i-1])
    lo = np.minimum(u.min(0) - np.array([.02,.02,0]), seed - np.array([.09,.09,0]))
    hi = np.maximum(u.max(0) + np.array([.02,.02,0]), seed + np.array([.09,.09,0]))
    lo[2], hi[2] = fusion['bounds_min_upright'][2], fusion['bounds_max_upright'][2]
    lo = np.maximum(lo, np.array(fusion['bounds_min_upright']))
    hi = np.minimum(hi, np.array(fusion['bounds_max_upright']))
    crops[plant] = {'min':lo.tolist(),'max':hi.tolist()}
    plant_records[plant] = {'path':p,'records':a,'provenance_path':pp,
                            'old':old,'upright':u,'display':u @ Y_FROM_Z.T}

inputs_before = {rel(p):sha(p) for p in sorted(input_files)}
source_identity_checks = []
orientation_checks = []
for stage, v in stages.items():
    a = v['records']
    assert len(a) == len(v['camera_id']) == len(v['original_point_index'])
    maxerr = 0.
    for camera in (0,1):
        which = np.flatnonzero(v['camera_id']==camera)
        if not len(which):
            continue
        original = full_records[str(camera)][v['original_point_index'][which]]
        expected = xyz(original)
        if camera == 1:
            expected = expected @ T[:3,:3].T + T[:3,3]
        error = float(np.max(np.abs(xyz(a[which]) - expected)))
        maxerr = max(maxerr,error)
        assert error < 1e-12, (stage,camera,error)
        assert np.array_equal(rgb(a[which]),rgb(original))
    source_identity_checks.append({'stage':stage,'points':len(a),'max_reference_coordinate_error':maxerr,'rgb_exact':True})
    if v['old'] is not None:
        prior = read_ply(v['old'])
        assert len(prior)==len(a)
        err = float(np.max(np.abs(xyz(prior)*metric_scale-v['upright'])))
        assert err < 1e-12
        assert np.array_equal(rgb(prior),rgb(a))
        orientation_checks.append({'stage':stage,'old_viewer_ply':rel(v['old']),'points':len(a),'old_viewer_coordinates_scaled_by':metric_scale,'max_z_up_error':err})
    else:
        orientation_checks.append({'stage':stage,'old_vertex_identity_not_reused':True,'proper_common_rotation_checked':True,'basis_same_as_verified_D405':True})

download_cache = {}
def download(path):
    if path in download_cache:
        return download_cache[path]
    name = path.name + '.gz'
    target = OUT/'downloads'/name
    with path.open('rb') as src, target.open('wb') as dst:
        with gzip.GzipFile(filename='', mode='wb', fileobj=dst,mtime=0,compresslevel=6) as gz:
            shutil.copyfileobj(src,gz,1024*1024)
    # Verify decompression returns the original file byte-for-byte by hash.
    h = hashlib.sha256()
    with gzip.open(target,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):
            h.update(b)
    assert h.hexdigest()==inputs_before[rel(path)]
    item = {'download':target.relative_to(OUT).as_posix(),
            'downloadSha256':sha(target),'downloadBytes':target.stat().st_size,
            'downloadOriginalSha256':h.hexdigest(),'downloadFormat':'gzip-compressed original binary PLY',
            'downloadCoordinateFrame':'D405 reference camera; unmodified source, not display Y-up'}
    download_cache[path] = item
    return item


def crop_download(model_id, records):
    """Write exact selected binary records, not float32 browser coordinates."""
    header = (f'ply\nformat binary_little_endian 1.0\ncomment Display-only spatial crop; includes context; exact source records\nelement vertex {len(records)}\n'
              'property double x\nproperty double y\nproperty double z\nproperty uchar red\nproperty uchar green\nproperty uchar blue\nend_header\n').encode('ascii')
    body = records.tobytes()
    h = hashlib.sha256(header+body).hexdigest()
    target = OUT/'downloads'/f'{model_id}_reference_spatial_crop.ply.gz'
    with target.open('wb') as dst:
        with gzip.GzipFile(filename='',mode='wb',fileobj=dst,mtime=0,compresslevel=6) as gz:
            gz.write(header);gz.write(body)
    with gzip.open(target,'rb') as src:
        assert hashlib.sha256(src.read()).hexdigest()==h
    return {'download':target.relative_to(OUT).as_posix(),'downloadSha256':sha(target),
            'downloadBytes':target.stat().st_size,'downloadOriginalSha256':h,
            'downloadFormat':'gzip-compressed binary PLY; exact selected source records',
            'downloadCoordinateFrame':'D405 reference camera; exact source records, not display Y-up'}

models = []
web_checks = []
for stage,v in stages.items():
    for plant in ['all','P1','P2','P3','P4','P5']:
        model_id = f'{stage}_{plant}'
        source = v
        is_roi = plant != 'all' and stage != 'cleaned'
        if stage=='cleaned' and plant!='all':
            source = plant_records[plant]
            saved = np.load(source['provenance_path'])
            provenance = {k:saved[k] for k in saved.files}
            selected = np.arange(len(source['records']),dtype=np.uint32)
            fused_indices = provenance['fused_point_index']
            assert np.array_equal(source['records'],stages['fused']['records'][fused_indices])
            assert np.array_equal(R, np.asarray(cleanup['upright_R']))
        else:
            if is_roi:
                box = crops[plant]
                mask = np.all((v['upright']>=box['min'])&(v['upright']<=box['max']),axis=1)
                selected = np.flatnonzero(mask).astype(np.uint32)
            else:
                selected = np.arange(len(v['records']),dtype=np.uint32)
            provenance = {k:v[k][selected] for k in ['camera_id','original_point_index','fused_point_index'] if k in v}
        records = source['records'][selected]
        positions = source['display'][selected]
        count = len(records)
        assert count>0 and np.isfinite(positions).all()
        payload = np.empty(count,dtype=WEB_DTYPE)
        for j,k in enumerate(('x','y','z')):
            payload[k] = positions[:,j]
        for k in ('r','g','b'):
            payload[k] = records[k]
        cloud = OUT/'clouds'/f'{model_id}.bin'
        with cloud.open('wb') as f:
            f.write(b'PF3D'+struct.pack('<I',count))
            payload.tofile(f)
        prov_path = OUT/'provenance'/f'{model_id}_source_indices.npz'
        np.savez_compressed(prov_path,source_vertex_index=selected,**provenance)
        assert cloud.stat().st_size==8+15*count
        with cloud.open('rb') as f:
            assert f.read(8)==b'PF3D'+struct.pack('<I',count)
            check = np.fromfile(f,dtype=WEB_DTYPE,count=count)
        assert np.array_equal(payload,check)
        err = float(np.max(np.abs(xyz(check)-positions)))
        assert err <= 1.2e-7
        suffix = ('all five plants - inspection region' if plant=='all' else f'{plant} - spatial crop, includes context' if is_roi else f'{plant} - source-reviewed candidate')
        desc = v['description']
        if is_roi:
            desc += ' New spatial display crop only: may include pot, background and neighbouring foliage; may omit outlying tissue. This is not a biological segmentation.'
        if stage=='cleaned':
            desc += ' Approximate source masks and basal exclusions can omit true tissue; not a validated trait mask.'
        item = {
            'id':model_id,'label':f"{v['label']} / {suffix}",'stage':stage,'plant':plant,
            'file':cloud.relative_to(OUT).as_posix(),'pointCount':count,'sourcePointCount':len(source['records']),
            'description':desc,'bounds':{'min':positions.min(0).tolist(),'max':positions.max(0).tolist()},
            'sourcePath':rel(source['path']),'sourceSha256':inputs_before[rel(source['path'])],
            'sha256':sha(cloud),'bytes':cloud.stat().st_size,
            'provenance':prov_path.relative_to(OUT).as_posix(),'provenanceSha256':sha(prov_path),
            'selection':'spatial_crop_includes_context' if is_roi else 'saved_source_reviewed_candidate_subset' if stage=='cleaned' else 'preserved_inspection_region',
            'sourceIndexMeaning':'source_vertex_index is zero-based in sourcePath; camera_id 0=D405,1=L515; original_point_index indexes the original full camera cloud; fused_point_index when present indexes the preserved fused cloud.',
            'decimated':False,'coordinates':'common board-derived Y-up display frame; metres anchored to supplied 25mm squares, with empirical L515 correction',
            'float32MaxCoordinateRounding':err,
            'cameraCounts':{str(c):int(np.count_nonzero(provenance['camera_id']==c)) for c in (0,1)},
            **(crop_download(model_id,records) if is_roi else download(source['path'])),
            'downloadScope':'displayed_spatial_crop' if is_roi else 'displayed_source_cloud',
            'downloadLabel':'Selected spatial crop PLY (.gz), includes context' if is_roi else 'Original reference-frame PLY (.gz)',
        }
        if is_roi:
            item['cropBoundsBoardZUp'] = crops[plant]
            parent = download(source['path'])
            item['parentSourceDownload'] = parent['download']
            item['parentSourceDownloadSha256'] = parent['downloadSha256']
        if stage=='cleaned':
            item['cleanupEvidence'] = cleanup['per_plant'].get(plant, {'total':cleanup['counts']['plants_cleaned']})
        models.append(item)
        web_checks.append({'id':model_id,'points':count,'payload_bytes':cloud.stat().st_size,'header_valid':True,'rgb_exact':True,'source_indices_valid':True,'max_float32_rounding':err})
        print(model_id,count,flush=True)

manifest = {
    'schemaVersion':1,'title':'28 September 2026 - five-plant geometry stages',
    'status':'board-anchored metric research candidates; not complete 360-degree models or validated physical accuracy',
    'physicalSquareMetres':0.025,'markerMetres':0.018,'dictionary':'DICT_4X4_50',
    'format':{'magic':'PF3D','headerBytes':8,'count':'uint32 little endian at byte 4',
              'recordBytes':15,'record':'x,y,z float32 little endian then r,g,b uint8; unpadded'},
    'models':models,
    'coordinateFrame':{
        'displayUp':'Y','reference':'first D405 plant camera; no soil/table height zero',
        'units':'metres anchored to supplied 25mm square pitch; print tolerance and residual camera-model uncertainty remain',
        'boardZUpFromD405Reference':R.tolist(),'displayYUpFromBoardZUp':Y_FROM_Z.tolist(),
        'displayYUpFromD405Reference':DISPLAY_R.tolist(),
        'formula':'column vectors: display = displayYUpFromD405Reference @ reference; no translation or scale',
        'l515TransformAlreadyApplied':True,
        'l515ToD405EmpiricalTransform':T.tolist(),
        'orientationEvidence':rel(calibration_path),'orientationEvidenceSha256':inputs_before[rel(calibration_path)],
    },
    'cropPolicy':{
        'status':'new display-only spatial boxes, identical for D405, aligned L515 and fused stages',
        'method':f"For each plant, union saved clean-cloud XY bounds expanded 0.02m with soil-seed XY +/-0.09m; retain entire metric inspection-region Z {fusion['bounds_min_upright'][2]:.9f} to {fusion['bounds_max_upright'][2]:.9f}m; clip to original inspection bounds.",
        'purpose':'Allow honest per-plant stage inspection where no saved earlier biological segmentation exists.',
        'limitations':['Boxes may overlap; counts across per-plant raw views are not a partition.',
                       'Includes context, neighbouring leaves and possible outliers; can omit outlying or never-recovered tissue.',
                       'The clean candidate extent guides display framing only; no new plant labels are assigned.'],
        'boundsBoardZUp':crops,
    },
    'originalFullCameraClouds':{k:{'path':rel(p),'sha256':inputs_before[rel(p)],'points':len(full_records[k]),
                                 'includedInWebsite':False,'reason':'Full scene retained locally; website uses established inspection region.'} for k,p in full_source_paths.items()},
    'sourceHashManifest':'provenance/input_hashes.json',
    'fullResolutionForEverySelection':True,
    'physicalAccuracyValidated':False,'manualTraitDimensionsUsedToFitGeometry':False,
    'limits':['Point counts are not completeness scores. No unseen surfaces or new vertices are invented.',
              'D405 is RGB stereo reconstruction; L515 uses recorded depth. Their source point spacings differ.',
              'Camera-to-camera transform is empirical surface alignment, not independently validated physical extrinsics.',
              'Board pitch is supplied as 25mm; it anchors the recovered RGB geometry scale. Print tolerance is unavailable. L515 device depth units remain unrecorded; the selected gain is empirical.',
              'Cleanup is reversible source-reviewed candidate selection, not accepted biological ground truth.',
              'Original downloads retain reference-camera orientation; only PF3D display geometry is rotated Y-up.'],
}
write_json(OUT/'provenance/input_hashes.json',inputs_before)
write_json(OUT/'manifest.json',manifest)
assert {rel(p):sha(p) for p in sorted(input_files)}==inputs_before
validation = {'status':'pass','models':len(models),'web_records':sum(m['pointCount'] for m in models),
              'cloud_bytes':sum(m['bytes'] for m in models),'download_bytes':sum(p.stat().st_size for p in (OUT/'downloads').glob('*.gz')),
              'all_source_hashes_unchanged':True,'source_files_checked':len(input_files),
              'source_identity':source_identity_checks,'old_viewer_orientation':orientation_checks,
              'rotation_determinant':float(np.linalg.det(DISPLAY_R)),
              'web_checks':web_checks,'downloads_roundtrip_exact':True,
              'no_physical_accuracy_or_biological_completeness_claim':True}
write_json(AUDIT/'geometry_asset_validation.json',validation)
write_json(BASE/'geometry_asset_validation.json',validation)
print(json.dumps({k:validation[k] for k in ['status','models','cloud_bytes','download_bytes']},indent=2),flush=True)

# Small static preview: downsample only for the overview graphic, never web assets.
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig,axes = plt.subplots(2,2,figsize=(14,7.6),sharex=True,sharey=True,layout='constrained')
preview = []
for ax,(stage,v) in zip(axes.flat,stages.items()):
    step = max(1,int(np.ceil(len(v['records'])/230000)))
    pos = v['display'][::step]
    colours = rgb(v['records'][::step])/255
    ax.set_facecolor('#092b3b')
    ax.scatter(pos[:,0],pos[:,1],c=colours,s=.23,linewidths=0,rasterized=True)
    ax.set_title(f"{v['label']} - {len(v['records']):,} points",fontsize=11)
    ax.set_xlim(fusion['bounds_min_upright'][0],fusion['bounds_max_upright'][0]);ax.set_ylim(fusion['bounds_min_upright'][2],fusion['bounds_max_upright'][2]);ax.set_aspect('equal')
    ax.set_xlabel('Gantry direction / m (board anchored)')
    ax.set_ylabel('Board-derived up / m (board anchored)')
    preview.append({'stage':stage,'source_points':len(v['records']),'plot_stride':step,'plotted_points':len(pos)})
fig.suptitle('Preserved geometry stages in one upright frame',fontsize=16)
fig.savefig(OUT/'figures/stages_front.png',dpi=180)
plt.close(fig)
write_json(OUT/'figures/stages_front.provenance.json',{'source':'manifest.json','plot':'orthographic X/Y projection; no interpolation','preview_sampling':preview,'png_sha256':sha(OUT/'figures/stages_front.png'),'limitation':'Static overview uses a documented point stride for file size. Interactive PF3D clouds contain every selected point.'})
