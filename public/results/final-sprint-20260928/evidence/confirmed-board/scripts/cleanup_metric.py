"""Confirmed-board cleanup using exactly the frozen source polygons.

Coordinates and cached stereo depths are converted consistently. Native physical
visibility/edge/basal-offset thresholds are unchanged; original sources stay intact.

Research candidate only: the masks are assistant-reviewed, not ground truth.
No acquisition/application files, raw inputs, or prior results are modified.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys
import cv2
import numpy as np
from scipy.spatial import cKDTree

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FUSION = None
ORIGINAL_CLEANUP=ROOT/'generated/research_plant_cleanup_20261007'
DENSE = ROOT/'generated/research_20260928_improvement_20261007/short_dense_v3'
sys.path.insert(0, str(ROOT/'generated/research_20260928_processing_20261007'))
from extract_P5_review_candidate import read_vertices, xyz, project


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(4*1024*1024), b''): h.update(b)
    return h.hexdigest()


def read(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def save(path, obj):
    path = Path(path).resolve()
    if not path.is_relative_to(HERE): raise ValueError('Output escapes cleanup directory')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def mask(polygons, w, h):
    a = np.zeros((h,w), np.uint8)
    for polygon in polygons:
        cv2.fillPoly(a, [np.rint(polygon).astype(np.int32)], 1)
    return a.astype(bool)


def write_vertices(path, vertices, indices):
    # Copy original binary vertex records verbatim, including normals and colours.
    source = FUSION/'fused_review_reference.ply'
    with source.open('rb') as f:
        header = []
        while True:
            line = f.readline()
            if line.startswith(b'element vertex '): line = f'element vertex {len(indices)}\n'.encode()
            header.append(line)
            if line.strip() == b'end_header': break
    with Path(path).open('wb') as f:
        f.write(b''.join(header))
        for start in range(0,len(indices),200000): vertices[indices[start:start+200000]].tofile(f)


def run(out, fusion):
    global FUSION
    FUSION=Path(fusion).resolve()
    if not FUSION.is_relative_to(HERE):raise ValueError('Expected new confirmed-board fusion')
    if out.exists() and any(out.iterdir()):raise ValueError('Existing cleanup output preserved')
    out.mkdir(parents=True,exist_ok=True)
    metric_calibration=HERE/'d405_metric_calibration.json'
    scale=read(metric_calibration)['metres_per_previous_filename_unit']
    pose_path=HERE/'d405_metric/icp_diagnostics_reexpressed.json' 
    source=FUSION/'fused_review_reference.ply'; vertices=read_vertices(source)
    p=xyz(vertices,slice(None)); n=len(p)
    R=np.asarray(read(FUSION/'summary.json')['upright_R'])
    upright=p@R.T
    profile=read(DENSE/'profile.json'); K=np.asarray(profile['K']); dist=np.asarray(profile['dist'])
    w,h=profile['width'],profile['height']
    poses={int(r['frame']):np.asarray(r['transform']) for r in read(pose_path) if r['icp_accepted']}
    masks=[ORIGINAL_CLEANUP/'source_review/p1_p2/P1_P2_multiview_polygon_review.json',
           ORIGINAL_CLEANUP/'source_review/p3_p4/source_review_p3_p4.json',ORIGINAL_CLEANUP/'source_review/p5/P5_source_review.json']
    records={r['id']:r for path in masks for r in read(path)['plants']}
    seeds_path=ROOT/'generated/research_l515_20261007/cross_camera/pot_rigid_probe/inputs.json'
    seeds=np.asarray(read(seeds_path)['seed_upright_xyz'])*scale
    # Deliberately approximate basal review band, never a true stem-base origin.
    # A source-visible point below this is retained as uncertain, not deleted.
    floor=seeds[:,2]+np.array([.025,.015,.015,.015,.015])
    basal_audit=ORIGINAL_CLEANUP/'source_review/p1_p2/P1_P2_basal_nonplant_depth_support.json'
    positive=np.zeros((n,5),np.uint8); ambiguous=np.zeros_like(positive)
    negative=np.zeros_like(positive); seen=np.zeros_like(positive)
    hashes={str(v.relative_to(ROOT)):sha(v) for v in [source,FUSION/'fused_point_provenance.npz',FUSION/'summary.json',DENSE/'profile.json',pose_path,seeds_path,basal_audit,*masks,metric_calibration,ORIGINAL_CLEANUP/'cleanup.py',Path(__file__)]}
    diagnostics=[]
    kernel=np.ones((3,3),np.uint8)
    for j in range(5):
        plant=records['P'+str(j+1)]
        for view in plant['views']:
            frame=int(view['frame']); T=poses[frame]
            rgb_path=ROOT/view['image_relative_to_repo']
            hashes[str(rgb_path.relative_to(ROOT))]=sha(rgb_path)
            for key in ('source_sha256','image_sha256','rgb_sha256'):
                if key in view and sha(rgb_path)!=view[key]: raise ValueError('Reviewed source changed')
            depth_path=DENSE/f'rgb/depth_{frame}.npz'
            hashes[str(depth_path.relative_to(ROOT))]=sha(depth_path)
            ids,pixels,z=project(vertices,slice(None),T,K,dist,w,h)
            zb=np.full(w*h,np.inf,np.float32); np.minimum.at(zb,pixels,z)
            # A one-pixel neighbourhood covers point rasterisation uncertainty.
            zb=cv2.erode(zb.reshape(h,w),kernel).ravel()
            visible=z<=zb[pixels]+.010
            # Native RGB pixel projection is separate from ideal stereo raster.
            pc=(p[ids]-T[:3,3])@T[:3,:3]
            uv=pc[:,:2]/pc[:,2,None]
            uv=uv*np.array([K[0,0],K[1,1]])+np.array([K[0,2],K[1,2]])
            inside=(uv[:,0]>=0)&(uv[:,0]<w-.5)&(uv[:,1]>=0)&(uv[:,1]<h-.5)
            q=np.flatnonzero(inside); ij=np.rint(uv[q]).astype(np.int32)
            with np.load(depth_path) as d:
                dep=d['depth'][ij[:,1],ij[:,0]].astype(np.float64)*scale
                valid=np.isfinite(dep)&(dep>0)&(d['votes'][ij[:,1],ij[:,0]]>=2)
            visible[q[valid & (z[q]>dep+.012)]]=False
            depth_agrees=np.zeros(len(ids),bool)
            depth_agrees[q[valid & (np.abs(z[q]-dep)<=.012)]]=True
            tissue=mask(view.get('clear_tissue_polygons',[]),w,h)
            pos=mask(view.get('plant_envelopes',[]),w,h)|tissue
            unc=mask(view.get('uncertain_polygons',[]),w,h)&~tissue
            neg=mask(view.get('nonplant_polygons',[]),w,h)
            boundary=cv2.dilate(pos.astype(np.uint8),np.ones((5,5),np.uint8)).astype(bool)&~pos
            clear=(pos&~unc&~neg).ravel()[pixels]&visible
            unclear=((unc|boundary)&~neg).ravel()[pixels]&visible
            bad=neg.ravel()[pixels]&visible&depth_agrees
            positive[ids[clear],j]+=1;ambiguous[ids[unclear],j]+=1
            negative[ids[bad],j]+=1;seen[ids[visible],j]+=1
            diagnostics.append(dict(plant=plant['id'],frame=frame,projected=len(ids),visible=int(visible.sum()),positive=int(clear.sum()),uncertain=int(unclear.sum()),nonplant=int(bad.sum())))
            print(diagnostics[-1],flush=True)
    # Each plant has its own reviewed views. Explicit nonplant evidence can veto
    # a primary assignment even when annotated while reviewing another plant.
    any_negative=negative.max(axis=1)>0
    above=upright[:,2,None]>floor[None,:]
    conflicting_ownership=(positive>0).sum(axis=1)>1
    core=(positive>=2)&above&~any_negative[:,None]&~conflicting_ownership[:,None]
    unique=core.sum(axis=1)==1
    labels=np.zeros(n,np.uint8); reason=np.zeros(n,np.uint8)
    for j in range(5):
        use=unique&core[:,j]; labels[use]=j+1;reason[use]=1
    # Preserve source-supported thin edges close to an unambiguous core. This
    # selects measured points only: no interpolation or point generation.
    extension=np.zeros((n,5),bool)
    for j in range(5):
        base=labels==j+1
        candidate=(labels==0)&(core.sum(axis=1)==0)&(positive[:,j]>=1)&above[:,j]&~any_negative&~conflicting_ownership
        idx=np.flatnonzero(candidate)
        if base.any() and len(idx):
            near=cKDTree(p[base]).query(p[idx],workers=4)[0]<=.004
            extension[idx[near],j]=True
    ext_unique=extension.sum(axis=1)==1
    for j in range(5):
        use=ext_unique&extension[:,j];labels[use]=j+1;reason[use]=2
    # Remaining positive/uncertain image evidence is retained in a review pool.
    # Outside all annotated polygons is unknown scene, not proof of background.
    review=(labels==0)&((positive+ambiguous).max(axis=1)>0)
    reason[review]=3
    reason[(labels==0)&~review&any_negative]=4
    provenance=np.load(FUSION/'fused_point_provenance.npz')
    np.savez_compressed(out/'point_classification.npz',fused_point_index=np.arange(n,dtype=np.uint32),
        plant_id=labels,reason=reason,positive_views=positive,uncertain_views=ambiguous,
        nonplant_views=negative,visible_review_views=seen,
        camera_id=provenance['camera_id'],original_point_index=provenance['original_point_index'])
    selections={**{'P'+str(j+1):np.flatnonzero(labels==j+1) for j in range(5)},
        'plants_cleaned':np.flatnonzero(labels>0),'uncertain':np.flatnonzero(review),
        'scene_context':np.flatnonzero((labels==0)&~review)}
    for name,idx in selections.items():
        write_vertices(out/(name+'_reference.ply'),vertices,idx)
        np.savez_compressed(out/(name+'_provenance.npz'),fused_point_index=idx,
            camera_id=provenance['camera_id'][idx],original_point_index=provenance['original_point_index'][idx])
    summary=dict(status='source_reviewed_plant_cleanup_candidate_not_validated_trait_segmentation',
        coordinate_units='metres referenced to confirmed 25mm checker pitch; empirical cross-camera alignment',
        d405_scale_factor=scale,physical_cleanup_thresholds_unchanged=True,
        source_image_polygons_reused_without_edits=True,old_stereo_depth_scaled_at_read=True,
        input_points=n,counts={k:len(v) for k,v in selections.items()},
        per_plant={f'P{j+1}':dict(total=int((labels==j+1).sum()),
            multi_view_core=int(((labels==j+1)&(reason==1)).sum()),
            one_view_near_core_edge=int(((labels==j+1)&(reason==2)).sum()),
            d405=int(((labels==j+1)&(provenance['camera_id']==0)).sum()),
            l515=int(((labels==j+1)&(provenance['camera_id']==1)).sum())) for j in range(5)},
        reason_codes={0:'Unassigned scene context; not asserted noise',1:'At least two visible positive source masks; above basal band; no competing clear positive assignment',2:'One or more visible positive masks and <=4mm from that plants core; no competing clear positive assignment',3:'Uncertain evidence, basal region, ownership, contradiction or insufficient views',4:'Explicit source nonplant evidence without positive or ambiguous source mask'},
        parameters=dict(mask_boundary_margin_px=2,self_occlusion_tolerance_m=.010,
            stereo_occlusion_tolerance_m=.012,negative_requires_stereo_agreement_m=.012,
            primary_min_positive_views=2,edge_extension_radius_m=.004,
            basal_floor_upright_z_m=floor.tolist(),soil_seed_upright=seeds.tolist(),
            basal_floor_policy='Frozen reviewed soil coordinates multiplied by the D405 board factor, then physical 15mm (P1 25mm) offsets applied unchanged. This is an approximate exclusion band, not stem-base height. Positive points below it remain uncertain.'),
        upright_R=R.tolist(),vertices_moved=False,vertices_created=False,manual_trait_dimensions_used=False,
        original_fusion_unchanged=(sha(source)==hashes[str(source.relative_to(ROOT))]),
        views=diagnostics,
        limits=['Assistant source polygons are approximate and dataset-specific, not accepted ground truth.',
          'Unknown pixels abstain. Broad plant polygons may contain background; unseen/back surfaces remain unlabelled.',
          'The approximate basal band and sparse review can omit true tissue from primary output; uncertain pool is essential.',
          'Checker pitch is now operator-confirmed. Print uncertainty, empirical cross-camera alignment and anatomical trait validation remain unresolved.',
          'Input was a fused review-region crop. This cleanup cannot recover previously omitted or never-observed surfaces.'])
    for name,expected in hashes.items():
        if sha(ROOT/name)!=expected:raise ValueError('Input changed during classification: '+name)
    assert sum(summary['counts'][k] for k in ('plants_cleaned','uncertain','scene_context'))==n
    assert sum(summary['per_plant'][k]['total'] for k in summary['per_plant'])==summary['counts']['plants_cleaned']
    for name,idx in selections.items():
        if len(idx):
            check=read_vertices(out/(name+'_reference.ply'))
            assert np.array_equal(check,vertices[idx]),name
    summary['exact_source_records_and_complete_partition_verified']=True
    save(out/'summary.json',summary);save(out/'input_hashes.json',hashes)
    save(out/'output_hashes.json',{p.name:sha(p) for p in sorted(out.iterdir()) if p.is_file() and p.name!='output_hashes.json'})
    print(json.dumps(summary['counts']),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);parser.add_argument('--fusion',required=True)
    args=parser.parse_args();out=Path(args.output).resolve()
    if not out.is_relative_to(HERE):raise ValueError('Output must be under research cleanup directory')
    run(out,args.fusion)
