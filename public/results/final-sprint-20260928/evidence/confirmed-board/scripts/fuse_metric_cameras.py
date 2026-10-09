"""Confirmed-board successor of the frozen D405/L515 observed-point union.

Physical thresholds are copied from the actual previous run; only frozen spatial
regions and cached D405 stereo depth are converted with the board-derived scale.

Requires an explicitly reviewed rigid transform. D405 points remain unchanged;
additional L515 points retain exact source coordinates and source indices.
"""
from pathlib import Path
import argparse
import json
import sys
import numpy as np
import open3d as o3d
from scipy.spatial import cKDTree

ROOT=Path(__file__).resolve().parents[2]
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/"generated/research_l515_20261007"))
from reconstruct_sensor import sha,save,visibility


def main(config, output):
    config=Path(config).resolve()
    selection=json.loads(config.read_text(encoding='utf-8'))
    if selection.get('selected_for_fusion') is not True and not selection.get('status','').startswith('selected_'):raise ValueError('An explicit reviewed selection is required')
    variant=selection.get('variant',selection.get('chosen_variant'))
    if variant not in ('native','boardgain'):raise ValueError('Unknown L515 variant')
    frozen_path=ROOT/'generated/research_l515_20261007/fusion_v1_config.json'
    frozen=json.loads(frozen_path.read_text(encoding='utf-8'))
    cal_path=BASE/'d405_metric_calibration.json'
    scale=json.loads(cal_path.read_text(encoding='utf-8'))['metres_per_previous_filename_unit']
    cfg=dict(frozen)
    cfg.update(T_D405_reference_from_L515_reference=selection['T_D405_reference_from_L515_reference'],
        bounds_min_upright=(np.array(frozen['bounds_min_upright'])*scale).tolist(),
        bounds_max_upright=(np.array(frozen['bounds_max_upright'])*scale).tolist(),
        alignment_evidence=selection.get('alignment_evidence',selection.get('surface_alignment_file')),
        status='board_referenced_metric_fusion_empirical_rigid_alignment',
        limits=selection.get('limits',[])+[
            '25mm checker pitch is operator-confirmed; print-size uncertainty is unavailable.',
            'Cross-camera alignment is empirical and not a certified physical rig extrinsic.',
            'D405 metric scale transfers under the stated fixed-rig acquisition assumptions.',
            'L515 board-gain trial is an empirical range correction, not confirmation of device units.' if variant=='boardgain' else 'L515 uses the native assumed sensor scale; depth-unit metadata remains incomplete.'])
    out=Path(output).resolve()
    cfg['output']=str(out)
    soil_evidence=selection.get('soil_validation_evidence',selection.get('fixed_soil_evidence_file'))
    if not cfg['alignment_evidence'] or not soil_evidence:raise ValueError('Alignment and soil evidence must both be recorded')
    for source,expected in selection.get('source_hashes',{}).items():
        if sha(ROOT/source)!=expected:raise ValueError('Selected source evidence changed: '+source)
    if not out.is_relative_to(BASE):raise ValueError('Output must remain in confirmed-board research directory')
    if out.exists() and any(out.iterdir()):raise ValueError('Existing output is preserved')
    if (out/'summary.json').exists():raise ValueError('Completed fusion preserved.')
    out.mkdir(parents=True,exist_ok=True)
    droot=ROOT/'generated/research_20260928_improvement_20261007/short_dense_v3'
    lroot=BASE/('l515_metric_v1' if variant=='native' else 'l515_metric_boardgain_v1')
    dpath=BASE/'d405_metric/full_scene_reference.ply';lpath=lroot/'result/l515_supported_reference.ply'
    assert lpath.resolve()==Path(selection['l515_source']).resolve()
    assert sha(lpath)==selection['l515_source_sha256']
    dposes=BASE/'d405_metric/icp_diagnostics_reexpressed.json'
    T=np.asarray(cfg['T_D405_reference_from_L515_reference'])
    assert T.shape==(4,4) and np.isfinite(T).all()
    assert np.allclose(T[3],[0,0,0,1]) and np.allclose(T[:3,:3].T@T[:3,:3],np.eye(3),atol=1e-6)
    assert np.isclose(np.linalg.det(T[:3,:3]),1)
    alignment=json.loads((ROOT/Path(cfg['alignment_evidence'])).read_text(encoding='utf-8'))
    assert np.allclose(T,np.array(alignment['T_D405_reference_from_L515_reference']),atol=1e-12)
    input_files=[dpath,lpath,Path(config),Path(__file__),ROOT/'generated/research_l515_20261007/reconstruct_sensor.py',
        droot/'profile.json',dposes,lroot/'result/point_evidence.npz',
        ROOT/'generated/research_20260928_processing_20261007/calibration_transfer.json',
        ROOT/Path(cfg['alignment_evidence']),ROOT/Path(soil_evidence),frozen_path,cal_path,
        BASE/'d405_metric/summary.json',lroot/'profile.json',lroot/'result/summary.json']
    recorded_camera=json.loads((dposes).read_text())
    input_files += [droot/f'rgb/depth_{r["frame"]}.npz' for r in recorded_camera if r['integrated']]
    input_hashes={str(p):sha(p) for p in input_files}
    save(out/'input_hashes.json',input_hashes)
    R=np.array(json.loads((ROOT/'generated/research_20260928_processing_20261007/calibration_transfer.json').read_text())['upright_export_R_reference_camera_to_xyz_z_up'])
    lo,hi=np.array(cfg['bounds_min_upright']),np.array(cfg['bounds_max_upright'])
    clouds=[];indices=[]
    for source,transform in [(dpath,np.eye(4)),(lpath,T)]:
        p=o3d.io.read_point_cloud(str(source));p.transform(transform)
        assert len(p.points)>0 and np.isfinite(np.asarray(p.points)).all()
        x=np.asarray(p.points)@R.T
        ids=np.flatnonzero(((x>=lo)&(x<=hi)).all(axis=1))
        clouds.append(p.select_by_index(ids));indices.append(ids)
        assert len(ids)>0
    d,l=clouds;di,li=indices
    dx,lx=np.asarray(d.points),np.asarray(l.points)
    distance,nearest=cKDTree(dx).query(lx,workers=4)
    dc=json.loads((droot/'profile.json').read_text())
    camera=json.loads((dposes).read_text())
    frames=[]
    for row in camera:
        if not row['integrated']:continue
        with np.load(droot/f'rgb/depth_{row["frame"]}.npz') as a:
            z=a['depth'].astype(np.float64)*scale;valid=a['mask']&np.isfinite(z)&(a['votes']>=2)
            frames.append(dict(frame=row['frame'],T=np.array(row['transform']),z=z,
                               rgb=a['rgb'].copy(),mask=valid))
    cross_support,cross_conflict,_,_=visibility(lx,frames,np.array(dc['K']),cfg['cross_tolerance_m'])
    duplicate=distance<=cfg['duplicate_distance_m']
    contradicted=cross_conflict>np.maximum(1,cross_support*.3)
    # Near-overlapping, unsupported layers remain separate for review. This
    # conservative band prevents mildly misaligned surfaces becoming thickness.
    uncertain=(distance<cfg['uncertain_overlap_distance_m'])&(cross_support<2)&~duplicate
    add=~duplicate&~contradicted&~uncertain
    reason=np.full(len(li),4,np.uint8)
    reason[duplicate]=0
    reason[~duplicate&contradicted]=1
    reason[~duplicate&~contradicted&uncertain]=2
    reason[add&(cross_support>=2)]=3
    assert np.all((reason>=3)==add)
    additions=l.select_by_index(np.flatnonzero(add))
    fused=d+additions
    for name,p in [('d405_review_reference.ply',d),('l515_aligned_review_reference.ply',l),
                   ('l515_additions_reference.ply',additions),('fused_review_reference.ply',fused),
                   ('l515_excluded_reference.ply',l.select_by_index(np.flatnonzero(~duplicate&~add)))]:
        if len(p.points)>0 and not o3d.io.write_point_cloud(str(out/name),p):
            raise IOError(f'Point-cloud write failed: {name}')
    provenance=o3d.geometry.PointCloud(fused)
    provenance.colors=o3d.utility.Vector3dVector(np.vstack((np.tile([.1,.65,1.],(len(d.points),1)),np.tile([1.,.65,.05],(int(add.sum()),1)))))
    assert o3d.io.write_point_cloud(str(out/'fused_source_colours_reference.ply'),provenance)
    with np.load(lroot/'result/point_evidence.npz') as lev:
        assert len(lev['support_views'])==len(o3d.io.read_point_cloud(str(lpath)).points)
        assert np.all(lev['support_views']>=3)
        assert np.all(lev['contradicting_views']<=np.maximum(1,.3*lev['support_views']))
        np.savez_compressed(out/'l515_fusion_decisions.npz',l515_source_indices=li,
            nearest_d405_source_indices=di[nearest],nearest_d405_distance_m=distance,
            l515_support_views=lev['support_views'][li],l515_conflict_views=lev['contradicting_views'][li],
            d405_support_views=cross_support,d405_conflict_views=cross_conflict,
            duplicate=duplicate,contradicted=contradicted,uncertain_overlap=uncertain,added=add,
            decision_code=reason,added_sensor_only=add&(cross_support<2),
            added_with_cross_view_support=add&(cross_support>=2))
    np.savez_compressed(out/'fused_point_provenance.npz',camera_id=np.r_[np.zeros(len(di),np.uint8),np.ones(int(add.sum()),np.uint8)],
        original_point_index=np.r_[di,li[add]])
    summary=dict(status=cfg['status'],l515_variant=variant,coordinate_units='metres referenced to supplied 25mm checker pitch; empirical cross-camera alignment',
        d405_scale_factor=scale,old_stereo_depth_scaled_at_read=True,
        physical_thresholds_unchanged_from_frozen_config=True,
        spatial_region_scaled_from_frozen_config=True,
        source_point_id_policy='camera_id 0 indexes d405_metric/full_scene_reference.ply; camera_id 1 indexes the selected NEW L515 supported reconstruction, never old L515 vertex IDs',
        source_clouds={'0':dict(path=str(dpath.relative_to(ROOT)),sha256=sha(dpath)),
                       '1':dict(path=str(lpath.relative_to(ROOT)),sha256=sha(lpath))},
        selection_config=str(config.relative_to(ROOT)),soil_validation_evidence=soil_evidence,
        d405_points=len(di),l515_review_points=len(li),
        l515_added_points=int(add.sum()),fused_points=len(fused.points),duplicates_suppressed=int(duplicate.sum()),
        all_l515_contradicted=int(contradicted.sum()),all_l515_uncertain_overlap=int(uncertain.sum()),
        nonduplicate_excluded=int((~duplicate&~add).sum()),
        decision_codes={'0':'near duplicate suppressed','1':'nonduplicate free-space contradiction',
            '2':'nonduplicate uncertain overlap','3':'added with at least two D405 stereo-view votes',
            '4':'added L515-only complementary candidate'},
        decision_counts={str(k):int((reason==k).sum()) for k in range(5)},
        T_D405_reference_from_L515_reference=T.tolist(),upright_R=R.tolist(),
        bounds_min_upright=lo.tolist(),bounds_max_upright=hi.tolist(),
        method='Observed-point union; preserve D405, suppress near-duplicates, add supported L515 surfaces after cross-view conflict/overlap checks.',
        duplicate_distance_m=cfg['duplicate_distance_m'],uncertain_overlap_distance_m=cfg['uncertain_overlap_distance_m'],
        cross_view_agreement_m=cfg['cross_tolerance_m'],free_space_margin_m=2*cfg['cross_tolerance_m'],
        nearest_distance_quantiles_m=np.quantile(distance,[0,.1,.5,.9,1]).tolist(),
        geometry_averaged_between_cameras=False,shape_completion=False,manual_traits_used=False,
        source_hashes=input_hashes,
        alignment_evidence=cfg['alignment_evidence'],
        limits=cfg['limits']+['Fusion region includes pots and is not an organ/trait segmentation.',
            'Added points are measured by L515; lack of a D405 contradiction is not independent confirmation.',
            'Distance and view checks do not prove physical accuracy or complete hidden-surface coverage.'])
    # Check source identity/colour and exact ordering after writing the union.
    verify=o3d.io.read_point_cloud(str(out/'fused_review_reference.ply'))
    expected=np.vstack((dx,lx[add]))
    assert np.array_equal(np.asarray(verify.points),expected)
    assert np.array_equal(np.rint(np.asarray(verify.colors)*255).astype(np.uint8),np.rint(np.asarray(fused.colors)*255).astype(np.uint8))
    assert len(np.unique(di))==len(di) and len(np.unique(li[add]))==int(add.sum())
    summary['written_union_exact_coordinate_and_source_order_check']=True
    save(out/'resolved_config.json',cfg)
    assert input_hashes=={str(p):sha(p) for p in input_files},'Input changed during fusion' 
    save(out/'summary.json',summary)
    save(out/'output_hashes.json',{p.name:sha(p) for p in out.iterdir() if p.is_file() and p.name!='output_hashes.json'})
    print(json.dumps(summary,indent=2),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('config');p.add_argument('--output',required=True);a=p.parse_args();main(a.config,a.output)
