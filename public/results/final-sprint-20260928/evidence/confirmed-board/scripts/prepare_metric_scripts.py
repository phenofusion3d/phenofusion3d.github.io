"""Create isolated, inspectable successors of the frozen research builders."""
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]


def replace_once(text, before, after):
    assert text.count(before) == 1, before
    return text.replace(before, after)


def main():
    target = BASE / "fuse_metric_cameras.py"
    assert not target.exists(), "Existing prepared builder preserved"
    text = (ROOT / "generated/research_l515_20261007/fuse_cameras.py").read_text(encoding="utf-8")
    text = replace_once(text, 'sys.path.insert(0,str(Path(__file__).resolve().parent))',
                        'BASE=Path(__file__).resolve().parent\nsys.path.insert(0,str(ROOT/"generated/research_l515_20261007"))')
    text = replace_once(text, 'def main(config):\n    cfg=json.loads(Path(config).read_text())\n    out=Path(cfg[\'output\'])', '''def main(config, output):
    config=Path(config).resolve()
    selection=json.loads(config.read_text(encoding='utf-8'))
    if selection.get('selected_for_fusion') is not True:raise ValueError('An explicit reviewed selection is required')
    variant=selection['variant']
    if variant not in ('native','boardgain'):raise ValueError('Unknown L515 variant')
    frozen_path=ROOT/'generated/research_l515_20261007/fusion_v1_config.json'
    frozen=json.loads(frozen_path.read_text(encoding='utf-8'))
    cal_path=BASE/'d405_metric_calibration.json'
    scale=json.loads(cal_path.read_text(encoding='utf-8'))['metres_per_previous_filename_unit']
    cfg=dict(frozen)
    cfg.update(T_D405_reference_from_L515_reference=selection['T_D405_reference_from_L515_reference'],
        bounds_min_upright=(np.array(frozen['bounds_min_upright'])*scale).tolist(),
        bounds_max_upright=(np.array(frozen['bounds_max_upright'])*scale).tolist(),
        alignment_evidence=selection['alignment_evidence'],
        status='board_referenced_metric_fusion_empirical_rigid_alignment',
        limits=selection.get('limits',[])+[
            '25mm checker pitch is operator-confirmed; print-size uncertainty is unavailable.',
            'Cross-camera alignment is empirical and not a certified physical rig extrinsic.',
            'D405 metric scale transfers under the stated fixed-rig acquisition assumptions.',
            'L515 board-gain trial is an empirical range correction, not confirmation of device units.' if variant=='boardgain' else 'L515 uses the native assumed sensor scale; depth-unit metadata remains incomplete.'])
    out=Path(output).resolve()
    if not out.is_relative_to(BASE):raise ValueError('Output must remain in confirmed-board research directory')
    if out.exists() and any(out.iterdir()):raise ValueError('Existing output is preserved')''')
    text = replace_once(text, "    dpath=droot/'result/plant_rgb_icp.ply';lpath=lroot/'result/l515_supported_reference.ply'", "    lroot=BASE/('l515_metric_v1' if variant=='native' else 'l515_metric_boardgain_v1')\n    dpath=BASE/'d405_metric/full_scene_reference.ply';lpath=lroot/'result/l515_supported_reference.ply'\n    dposes=BASE/'d405_metric/icp_diagnostics_reexpressed.json'")
    text = text.replace("droot/'result/icp_diagnostics.json'", 'dposes')
    text = replace_once(text, "        Path(cfg['alignment_evidence'])]", "        ROOT/Path(cfg['alignment_evidence']),ROOT/Path(selection['soil_validation_evidence']),frozen_path,cal_path,\n        BASE/'d405_metric/summary.json',lroot/'profile.json',lroot/'result/summary.json']")
    text = replace_once(text, "Path(__file__).with_name('reconstruct_sensor.py')", "ROOT/'generated/research_l515_20261007/reconstruct_sensor.py'")
    text = replace_once(text, "z=a['depth'].copy();valid", "z=a['depth'].astype(np.float64)*scale;valid")
    text = replace_once(text, "    summary=dict(status=cfg['status'],d405_points=len(di),l515_review_points=len(li),", "    summary=dict(status=cfg['status'],l515_variant=variant,coordinate_units='metres referenced to supplied 25mm checker pitch; empirical cross-camera alignment',\n        d405_scale_factor=scale,old_stereo_depth_scaled_at_read=True,\n        physical_thresholds_unchanged_from_frozen_config=True,\n        spatial_region_scaled_from_frozen_config=True,\n        source_point_id_policy='camera_id 0 indexes d405_metric/full_scene_reference.ply; camera_id 1 indexes the selected NEW L515 supported reconstruction, never old L515 vertex IDs',\n        source_clouds={'0':dict(path=str(dpath.relative_to(ROOT)),sha256=sha(dpath)),\n                       '1':dict(path=str(lpath.relative_to(ROOT)),sha256=sha(lpath))},\n        selection_config=str(config.relative_to(ROOT)),soil_validation_evidence=selection['soil_validation_evidence'],\n        d405_points=len(di),l515_review_points=len(li),")
    text = replace_once(text, "    assert input_hashes=={str(p):sha(p) for p in input_files},'Input changed during fusion'", '''    # Check source identity/colour and exact ordering after writing the union.
    verify=o3d.io.read_point_cloud(str(out/'fused_review_reference.ply'))
    expected=np.vstack((dx,lx[add]))
    assert np.array_equal(np.asarray(verify.points),expected)
    assert np.array_equal(np.rint(np.asarray(verify.colors)*255).astype(np.uint8),np.rint(np.asarray(fused.colors)*255).astype(np.uint8))
    assert len(np.unique(di))==len(di) and len(np.unique(li[add]))==int(add.sum())
    summary['written_union_exact_coordinate_and_source_order_check']=True
    save(out/'resolved_config.json',cfg)
    assert input_hashes=={str(p):sha(p) for p in input_files},'Input changed during fusion' ''')
    text = replace_once(text, "p.add_argument('config');a=p.parse_args();main(a.config)", "p.add_argument('config');p.add_argument('--output',required=True);a=p.parse_args();main(a.config,a.output)")
    text = text.replace('Evidence-preserving D405/L515 fusion in a declared inspection region.',
                        'Confirmed-board successor of the frozen D405/L515 observed-point union.\n\nPhysical thresholds are copied from the actual previous run; only frozen spatial\nregions and cached D405 stereo depth are converted with the board-derived scale.')
    compile(text, str(target), "exec");target.write_text(text, encoding="utf-8")

    target = BASE / "cleanup_metric.py"
    assert not target.exists(), "Existing prepared builder preserved"
    text = (ROOT / "generated/research_plant_cleanup_20261007/cleanup.py").read_text(encoding="utf-8")
    text = replace_once(text, "FUSION = ROOT/'generated/research_d405_l515_fusion_20261007/v1'", "FUSION = None\nORIGINAL_CLEANUP=ROOT/'generated/research_plant_cleanup_20261007'")
    text = replace_once(text, 'def run(out):\n    out.mkdir(parents=True,exist_ok=True)', '''def run(out, fusion):
    global FUSION
    FUSION=Path(fusion).resolve()
    if not FUSION.is_relative_to(HERE):raise ValueError('Expected new confirmed-board fusion')
    if out.exists() and any(out.iterdir()):raise ValueError('Existing cleanup output preserved')
    out.mkdir(parents=True,exist_ok=True)
    metric_calibration=HERE/'d405_metric_calibration.json'
    scale=read(metric_calibration)['metres_per_previous_filename_unit']
    pose_path=HERE/'d405_metric/icp_diagnostics_reexpressed.json' ''')
    text = text.replace("DENSE/'result/icp_diagnostics.json'", 'pose_path')
    text = text.replace("HERE/'source_review/", "ORIGINAL_CLEANUP/'source_review/")
    text = replace_once(text, "    seeds=np.asarray(read(seeds_path)['seed_upright_xyz'])", "    seeds=np.asarray(read(seeds_path)['seed_upright_xyz'])*scale")
    # Soil coordinates convert; the deliberate 15/25 mm basal exclusion offsets
    # are fixed physical thresholds. They are not anatomical stem-base positions.
    text = replace_once(text, "seeds_path,basal_audit,*masks,Path(__file__)]", "seeds_path,basal_audit,*masks,metric_calibration,ORIGINAL_CLEANUP/'cleanup.py',Path(__file__)]")
    text = replace_once(text, "dep=d['depth'][ij[:,1],ij[:,0]]", "dep=d['depth'][ij[:,1],ij[:,0]].astype(np.float64)*scale")
    text = replace_once(text, "        input_points=n,counts={k:len(v) for k,v in selections.items()},", "        coordinate_units='metres referenced to confirmed 25mm checker pitch; empirical cross-camera alignment',\n        d405_scale_factor=scale,physical_cleanup_thresholds_unchanged=True,\n        source_image_polygons_reused_without_edits=True,old_stereo_depth_scaled_at_read=True,\n        input_points=n,counts={k:len(v) for k,v in selections.items()},")
    text = replace_once(text, "            basal_floor_policy='Reviewed soil seed Z + 15mm (P1 +25mm after source-labelled soil audit) is an approximate exclusion band, not measured stem-base height. Every source-positive point below it remains in uncertain pool.'),", "            basal_floor_policy='Frozen reviewed soil coordinates multiplied by the D405 board factor, then physical 15mm (P1 25mm) offsets applied unchanged. This is an approximate exclusion band, not stem-base height. Positive points below it remain uncertain.'),")
    text = replace_once(text, "          'Independent calibration and physical trait validation remain outstanding. Metric scale is conditional.',", "          'Checker pitch is now operator-confirmed. Print uncertainty, empirical cross-camera alignment and anatomical trait validation remain unresolved.',")
    text = replace_once(text, "    save(out/'summary.json',summary);save(out/'input_hashes.json',hashes)", '''    assert sum(summary['counts'][k] for k in ('plants_cleaned','uncertain','scene_context'))==n
    assert sum(summary['per_plant'][k]['total'] for k in summary['per_plant'])==summary['counts']['plants_cleaned']
    for name,idx in selections.items():
        if len(idx):
            check=read_vertices(out/(name+'_reference.ply'))
            assert np.array_equal(check,vertices[idx]),name
    summary['exact_source_records_and_complete_partition_verified']=True
    save(out/'summary.json',summary);save(out/'input_hashes.json',hashes)''')
    text = replace_once(text, "parser=argparse.ArgumentParser();parser.add_argument('--output',default=str(HERE/'v1/result'))", "parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);parser.add_argument('--fusion',required=True)")
    text = replace_once(text, "    run(out)", "    run(out,args.fusion)")
    text = text.replace('Reproducible, reversible source-reviewed selection of existing fusion vertices.',
                        'Confirmed-board cleanup using exactly the frozen source polygons.\n\nCoordinates and cached stereo depths are converted consistently. Native physical\nvisibility/edge/basal-offset thresholds are unchanged; original sources stay intact.')
    compile(text, str(target), "exec");target.write_text(text, encoding="utf-8")
    print('Prepared fuse_metric_cameras.py and cleanup_metric.py; not executed.')


if __name__ == '__main__':
    main()
