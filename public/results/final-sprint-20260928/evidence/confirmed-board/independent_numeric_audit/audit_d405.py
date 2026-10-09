"""Independent read-only numeric audit of the board-scale re-expression."""
from pathlib import Path
import hashlib
import json
import numpy as np
import cv2

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "generated/research_confirmed_board_20261007"
OUT = Path(__file__).resolve().parent
OLD = ROOT / "generated/research_20260928_improvement_20261007/short_dense_v3"
FUSED = ROOT / "generated/research_d405_l515_fusion_20261007/v1"
TRAITS = ROOT / "generated/research_followthrough_20261007/traits"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(2**20), b""):
            h.update(b)
    return h.hexdigest()


def ply(path):
    with path.open("rb") as f:
        properties, vertices, active = [], None, False
        while True:
            line = f.readline()
            if not line:
                raise ValueError("Unterminated PLY header")
            fields = line.decode("ascii").split()
            if fields[:2] == ["format", "binary_little_endian"]:
                binary = True
            if fields[:1] == ["element"]:
                active = fields[1] == "vertex"
                if active:
                    vertices = int(fields[2])
            if fields[:1] == ["property"] and active:
                assert fields[1] != "list"
                code = {"double": "<f8", "float": "<f4", "uchar": "u1", "uint": "<u4", "int": "<i4"}[fields[1]]
                properties.append((fields[2], code))
            if fields == ["end_header"]:
                offset = f.tell(); break
    assert binary and vertices is not None
    return np.memmap(path, mode="r", dtype=np.dtype(properties), offset=offset, shape=(vertices,))


def xyz(points, ids):
    return np.column_stack([points[k][ids] for k in "xyz"])


def fit_shared_motion(position, translation, sheets, robust=True):
    # Eliminate sheet intercepts with weighted within-sheet centering, rather
    # than reusing the original script's matrix regression implementation.
    weights = np.ones(len(position))
    for iteration in range(15 if robust else 1):
        means, dx, dy = {}, np.empty_like(position), np.empty_like(translation)
        for sheet in set(sheets):
            use = sheets == sheet
            xbar = np.average(position[use], weights=weights[use])
            ybar = np.average(translation[use], weights=weights[use], axis=0)
            dx[use] = position[use] - xbar; dy[use] = translation[use] - ybar
            means[sheet] = (xbar, ybar)
        slope = np.sum(weights[:, None] * dx[:, None] * dy, axis=0) / np.sum(weights * dx**2)
        predicted = np.vstack([means[s][1] + (x - means[s][0]) * slope for x, s in zip(position, sheets)])
        residual = np.linalg.norm(translation - predicted, axis=1)
        threshold = max(np.median(residual) + 2.5 * 1.4826 * np.median(abs(residual - np.median(residual))), .000025)
        weights = np.minimum(1, threshold / np.maximum(residual, 1e-12))
    return slope, residual


def main():
    if (OUT / "audit.json").exists():
        raise FileExistsError("Preserve completed independent audit")
    calibration = read(BASE / "d405_metric_calibration.json")
    summary = read(BASE / "d405_metric/summary.json")
    factor = calibration["metres_per_previous_filename_unit"]
    input_paths = [BASE / "calibrate_d405_metric.py", BASE / "reexpress_d405_metric.py", BASE / "board_confirmation.json",
                   BASE / "d405_metric_calibration.json", BASE / "d405_board_poses_metres.json", BASE / "d405_metric/summary.json",
                   TRAITS / "provisional_chords.json", TRAITS / "chord_endpoint_indices.npz", FUSED / "fused_point_provenance.npz"]
    hashes = {str(p.relative_to(ROOT)): sha(p) for p in input_paths}
    old_obs = read(ROOT / "generated/research_20260928_readiness_20261007/checkerboard_calibration/corner_observations.json")["observations"]
    metric = read(BASE / "d405_board_poses_metres.json")["observations"]
    assert len(old_obs) == len(metric) == 57
    assert all((a["frame_id"], a["sheet"]) == (b["frame_id"], b["sheet"]) for a, b in zip(old_obs, metric))
    K, distortion = np.array(calibration["selected_K"]), np.array(calibration["selected_distortion"])
    errors, integer_grid = [], True
    for before, after in zip(old_obs, metric):
        obj = np.array(before["object_points_board_squares"], float)
        integer_grid &= bool(np.allclose(obj, np.rint(obj), atol=1e-12))
        projected = cv2.projectPoints(obj * .025, np.array(after["rvec"]), np.array(after["tvec_m"]), K, distortion)[0].reshape(-1, 2)
        errors.extend(np.linalg.norm(projected - np.array(before["image_points_pixels"]), axis=1))
    position = np.array([r["frame_id"] / 1e6 for r in metric])
    translation = np.array([r["tvec_m"] for r in metric])
    sheets = np.array([r["sheet"] for r in metric])
    slope, residual = fit_shared_motion(position, translation, sheets)
    slope_unweighted, _ = fit_shared_motion(position, translation, sheets, robust=False)
    independent_factor = np.linalg.norm(slope)
    assert abs(independent_factor - factor) < 1e-10
    assert np.max(abs(-slope - calibration["metric_motion_vector_m_per_previous_filename_unit"])) < 1e-10
    assert abs(float(np.sqrt(np.mean(np.array(errors)**2))) - calibration["calibration_reprojection_px"]["rms"]) < 1e-10
    frame_folds = {}
    for r in old_obs:
        frame_folds.setdefault(r["frame_id"], set()).add(r["sample_index"] % 4)
    assert all(len(v) == 1 for v in frame_folds.values())

    exports = []
    for entry in summary["export_files"]:
        old_path = ROOT / entry["source"]
        new_path = BASE / "d405_metric" / entry["file"]
        old, new = ply(old_path), ply(new_path)
        assert old.shape == new.shape and old.dtype == new.dtype
        all_equal = True
        for start in range(0, len(old), 200_000):
            stop = min(start + 200_000, len(old))
            for key in old.dtype.names:
                expected = old[key][start:stop] * factor if key in "xyz" else old[key][start:stop]
                all_equal &= bool(np.array_equal(new[key][start:stop], expected))
        assert all_equal
        old_sha, new_sha = sha(old_path), sha(new_path)
        assert old_sha == entry["source_sha256"] and new_sha == entry["sha256"]
        exports.append({"file": entry["file"], "points": len(old), "every_coordinate_exactly_scaled": True,
                        "all_non_coordinate_fields_exactly_preserved": True, "source_sha256": old_sha, "output_sha256": new_sha})

    transform_results = []
    for old_path, new_path, kind in [(OLD / "bundle/poses.json", BASE / "d405_metric/poses.json", "bundle"),
                                    (OLD / "result/icp_diagnostics.json", BASE / "d405_metric/icp_diagnostics_reexpressed.json", "final_icp")]:
        before, after = read(old_path), read(new_path)
        if kind == "bundle":
            before, after = before["frames"], after["frames"]
        assert len(before) == len(after)
        for a, b in zip(before, after):
            assert a["frame"] == b["frame"]
            A, B = np.array(a["transform"]), np.array(b["transform"])
            assert np.array_equal(A[:3, :3], B[:3, :3])
            assert np.array_equal(A[:3, 3] * factor, B[:3, 3])
            assert np.array_equal(A[3], B[3])
        transform_results.append({"type": kind, "transforms": len(before), "rotations_unchanged": True, "translations_exactly_scaled": True})
    assert sha(OLD / "result/point_evidence.npz") == sha(BASE / "d405_metric/point_evidence.npz")
    with np.load(BASE / "d405_metric/point_evidence.npz") as evidence:
        evidence_fields = {k: {"shape": list(evidence[k].shape), "dtype": str(evidence[k].dtype)} for k in evidence.files}
        assert set(evidence.files) == {"support_views", "contradicting_views"}

    # Independent covariance check uses actual old and new points and final ICP,
    # including lens distortion. The root check used scaled points and bundle poses.
    old_points = ply(OLD / "result/plant_rgb_icp.ply")
    new_points = ply(BASE / "d405_metric/full_scene_reference.ply")
    ids = np.random.default_rng(28405).choice(len(old_points), 2048, replace=False)
    old_xyz, new_xyz = xyz(old_points, ids), xyz(new_points, ids)
    old_icp = read(OLD / "result/icp_diagnostics.json")
    new_icp = read(BASE / "d405_metric/icp_diagnostics_reexpressed.json")
    pixel_changes = []
    for a, b in zip(old_icp, new_icp):
        if not a.get("integrated"):
            continue
        A, B = np.array(a["transform"]), np.array(b["transform"])
        pa = (old_xyz - A[:3, 3]) @ A[:3, :3]
        pb = (new_xyz - B[:3, 3]) @ B[:3, :3]
        front = (pa[:, 2] > .01) & (pb[:, 2] > .01 * factor)
        u = cv2.projectPoints(pa[front], np.zeros(3), np.zeros(3), K, distortion)[0].reshape(-1, 2)
        v = cv2.projectPoints(pb[front], np.zeros(3), np.zeros(3), K, distortion)[0].reshape(-1, 2)
        in_frame = (u[:, 0] >= 0) & (u[:, 0] < 1280) & (u[:, 1] >= 0) & (u[:, 1] < 720)
        pixel_changes.extend(np.linalg.norm(u[in_frame] - v[in_frame], axis=1))
    assert len(pixel_changes) and max(pixel_changes) < 1e-8

    fused_points = ply(FUSED / "fused_review_reference.ply")
    with np.load(FUSED / "fused_point_provenance.npz") as saved:
        camera, original_index = saved["camera_id"], saved["original_point_index"]
    candidates = np.load(TRAITS / "chord_endpoint_indices.npz")
    chord_updates = []
    for chord in read(TRAITS / "provisional_chords.json"):
        entries = []
        for endpoint in chord["endpoints"]:
            if endpoint.get("fused_point_index") is None:
                entries.append({"role": endpoint["role"], "status": "no_supported_endpoint"}); continue
            idx = endpoint["fused_point_index"]
            oi = int(original_index[idx]); cam = int(camera[idx])
            assert oi == endpoint["original_point_index"] and cam == endpoint["camera_id"]
            assert np.array_equal(xyz(fused_points, [idx])[0], np.array(endpoint["reference_xyz_conditional_m"]))
            assert cam == 0
            assert np.array_equal(xyz(old_points, [oi])[0], xyz(fused_points, [idx])[0])
            pool = candidates[endpoint["candidate_index_key"]]
            entries.append({"role": endpoint["role"], "fused_index": idx, "camera_id": cam,
                            "D405_original_index": oi, "old_xyz": xyz(old_points, [oi])[0].tolist(),
                            "board_scaled_xyz_m": xyz(new_points, [oi])[0].tolist(),
                            "candidate_count": len(pool), "candidate_camera_counts": {str(k): int((camera[pool] == k).sum()) for k in np.unique(camera[pool])},
                            "all_candidates_D405": bool(np.all(camera[pool] == 0))})
        value = chord.get("conditional_chord_cm")
        record = {"id": chord["id"], "endpoints": entries, "old_conditional_chord_cm": value,
                  "board_scaled_chord_cm": None, "scale_factor": factor,
                  "reference_annotation_cm": chord["reference_annotation_cm"],
                  "eligible_for_physical_accuracy_statistics": False,
                  "geometry_or_manual_definition_exclusions": chord["limitation"],
                  "original_result_preserved": True}
        if value is not None:
            coords = np.array([e["board_scaled_xyz_m"] for e in entries])
            new_length_cm = float(np.linalg.norm(coords[1] - coords[0]) * 100)
            assert abs(new_length_cm - value * factor) < 1e-10
            record["board_scaled_chord_cm"] = new_length_cm
            all_pools_D405 = all(e["all_candidates_D405"] for e in entries)
            record["endpoint_disk_range_can_be_scaled_without_mixing_cameras"] = all_pools_D405
            if all_pools_D405:
                record["board_scaled_endpoint_disk_sensitivity_cm"] = [100 * factor * v for v in chord["endpoint_pixel_disk_sensitivity_conditional_m"]]
            if chord["id"] == "P3.O03.blade_chord":
                record["provisional_difference_from_operator_cm"] = new_length_cm - chord["reference_annotation_cm"]
                record["comparison_status"] = "Board-referenced metric chord; operator-only comparison still provisional. No MAE/MAPE or physical accuracy claim."
            else:
                record["provisional_difference_from_operator_cm"] = None
                record["comparison_status"] = "Partial extent; not homologous to whole-organ ruler length. No residual."
        chord_updates.append(record)

    caveats = [
        "The supplied 25 mm square and 18 mm marker resolve the formerly unknown design dimensions. Printed-size measurement uncertainty was not supplied.",
        "The scalar is metres per old frame_id/1e6 coordinate unit. It follows a fixed-mount linear-motion model, retained factory RGB intrinsics and user-confirmed unchanged settings between scans.",
        "Small pose residuals and reprojection invariance are internal consistency checks, not independently measured physical accuracy or reconstructed surface completeness.",
        "This is uniform scale re-expression of an existing RGB reconstruction. No new stereo, bundle, ICP, filtering or 1 mm-threshold run took place; inherited thresholds are multiplied by the factor.",
        "The new best-fit motion direction differs by about 0.0097 degrees. The export intentionally retains existing rotations and direction; it applies the scalar only.",
        "D405 input depth PNGs and cached synthetic depth arrays are not re-expressed by this script. Consumers must not mix them with scaled cloud/poses without explicit corresponding unit handling.",
        "The full mixed D405/L515 cloud cannot be multiplied by this D405 factor. L515 depth/rig registration and any mixed-cloud descriptors require separate recomputation.",
        "The 128,000 comparison root check used bundle poses and an inspection subset despite a full-scene comment. This audit additionally tests original and scaled points with final accepted ICP transforms and lens distortion.",
        "Correcting board scale does not recover anatomical bases/tips, match ruler sections, resolve leaf-versus-pod identity, or make manual photos independent ground truth.",
        "The existing marker-edge image ratio is approximately 0.670 rather than 0.720; low-resolution edge localization is not independent physical verification of marker width. Metric scaling here is based on checker-corner pitch, not fitted marker-edge width.",
    ]
    report = {"status": "numeric_consistency_passed_with_recorded_scope_limits", "date": "2026-10-07",
              "source_hashes": hashes, "old_conditional_unit": "frame_id/1e6", "new_coordinate_unit": "metres referenced to supplied 25 mm checker pitch",
              "scale_factor": factor, "independent_factor_from_within_sheet_centered_regression": float(independent_factor),
              "unweighted_fit_factor_sensitivity": float(np.linalg.norm(slope_unweighted)),
              "factor_absolute_difference": float(abs(independent_factor - factor)),
              "integer_checker_corner_grid_confirmed": integer_grid,
              "board_observations": len(metric), "board_unique_frames": len(frame_folds), "checker_corners": len(errors),
              "recomputed_reprojection_rms_px": float(np.sqrt(np.mean(np.array(errors)**2))),
              "no_frame_leakage_across_reported_holdout_folds": True,
              "independent_translation_fit_rms_m": float(np.sqrt(np.mean(residual**2))),
              "exports": exports, "pose_checks": transform_results, "support_evidence_unchanged": True, "support_evidence_fields": evidence_fields,
              "independent_final_ICP_distorted_reprojection_check": {"in_frame_comparisons": len(pixel_changes), "max_pixel_change": float(max(pixel_changes))},
              "provisional_chord_updates": chord_updates, "caveats": caveats,
              "new_physical_accuracy_claim": False, "source_geometry_or_manual_evidence_modified": False}
    after = {name: sha(ROOT / name) for name in hashes}
    assert hashes == after
    report["source_hashes_unchanged_after_audit"] = True
    (OUT / "audit.json").write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    p3 = next(x for x in chord_updates if x["id"] == "P3.O03.blade_chord")
    lines = ["# Independent D405 metric audit", "", "Numeric checks passed. Existing surfaces and identities were preserved; scale is referenced to the supplied checkerboard pitch, not an independent physical accuracy assessment.", "",
             f"The within-sheet-centered regression independently gives {independent_factor:.13f} m per old coordinate unit, matching the exported factor to {abs(independent_factor-factor):.3g}. There are 57 board observations from 32 frames and 3,067 corners. Reprojection RMS is {np.sqrt(np.mean(np.array(errors)**2)):.6f} px. Held-out folds keep whole frames together.", "",
             f"All coordinates and non-coordinate fields were checked for both clouds (8,265,080 full-scene and 1,719,001 inspection vertices). Bundle and final ICP translations were scaled exactly while rotations stayed unchanged. An additional {len(pixel_changes):,} in-frame projections using final ICP and lens distortion changed by at most {max(pixel_changes):.3g} pixels.", "",
             f"P3.O03 selected endpoints are both D405: old fused indices 1,221,511 and 944,608 map exactly to original D405 vertices 5,799,835 and 4,949,838. The updated chord is {p3['board_scaled_chord_cm']:.9f} cm; the arithmetic difference from the operator-only 7.5 cm is {p3['provisional_difference_from_operator_cm']:+.9f} cm. This remains provisional; basal convention and reference readability remain unresolved. No validated MAE/MAPE follows.", "",
             "Scope limits:", ""] + ["- " + c for c in caveats]
    (OUT / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "factor": factor, "p3_chord": p3,
                      "reprojection": report["independent_final_ICP_distorted_reprojection_check"]}, indent=2))


if __name__ == "__main__":
    main()
