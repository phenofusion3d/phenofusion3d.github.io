# L515: separate reconstruction of the 28 September plants

Completed on 7 October 2026. This result uses the replacement L515 plant recording and remains separate from every D405 result. It is a research reconstruction with conditional metric scale, not validated plant traits or a complete 360-degree model.

## Result

| Quantity | Result |
|---|---:|
| Available paired source frames | 1,278 |
| Selected, refined and registered views | 64 |
| RGB bundle landmarks / observations | 5,334 / 63,664 |
| RGB reprojection median / 90th percentile | 0.236 / 0.641 pixels |
| Accepted bounded sensor ICP corrections | 64 / 64 |
| TSDF points before support checks | 2,272,210 |
| Supported scene points, before optional cleanup | 1,598,977 |
| Points after optional statistical cleanup | 1,562,246 |
| Minimum / median supporting views | 3 / 9 |

These are scene-processing and internal-agreement counts, not percentages of plant completeness or physical accuracy. The full cloud includes support surfaces and rig as well as plants and pots. [Open the separate L515 viewer](review/index.html). Its labelled review crop is reversible, has saved source indices, and must not be treated as a specimen segmentation mask.

[Independent computational verification passed](../qa/INDEPENDENT_SENSOR_QA.md): 480 sampled points checked across all 64 raw views reproduced the saved support, conflict and colour evidence exactly. All source PNGs and intrinsic files were rehashed unchanged. This verifies the computation and preservation of data, not physical plant accuracy.

## Method and calibration

Recorded ChArUco observations establish camera-motion direction and an upright basis using the saved colour calibration. Camera translation scale is conditional on the filename keys representing calibrated gantry metres. The 61 accepted board observations across three separately tracked sheets give conditional square pitches around 24.27–24.31 mm; these are not ruler measurements of the print. See [calibration evidence](../calibration/CALIBRATION_REVIEW.md).

The working depth conversion is **0.00025 m/count**, a candidate supported by the board/motion audit, not recovered recording metadata. The board-derived ratio is approximately 0.000246124 m/count, leaving an unresolved difference of about 1.57%. There is no universal L515 unit asserted here. Factory geometry, axial depth bias, gantry scale and alignment can contribute. A separate [RGB landmark versus sensor-depth diagnostic](../calibration/landmark_depth_check/README.md) found depth-dependent discrepancies; no fitted correction from that diagnostic was applied to this reconstruction.

The source's native depth intrinsic file describes 1024 × 768, while exported depth is 1280 × 720. This pipeline uses the colour grid, consistent with the present exporter's alignment-to-colour behavior. Actual recording-specific alignment provenance is absent. An RGB/depth edge audit did not justify one global image translation.

The visible camera housing is excluded with a documented native-grid mask. The mask and depth are remapped using nearest-neighbour interpolation; RGB uses bilinear interpolation. Zero or out-of-range depths stay missing. RGB features refine 64 camera poses with gantry priors. Sensor ICP compares each view with frozen neighbouring bundle clouds, using a 12 mm correspondence gate, a 6 mm maximum median correction and a 0.5-degree rotation bound. Targets do not accumulate earlier corrections.

TSDF fusion uses a 2 mm voxel and 10 mm truncation. The broad 0.20–1.60 m processing envelope retains static surroundings for scene registration; it is not an accuracy specification or plant mask. Retained points require at least three distinct supporting sensor views within 8 mm and limited free-space contradictions. These tolerances describe processing choices, not guaranteed precision. Different views can share systematic errors.

The primary output preserves every point passing the support checks. Optional statistical cleanup is saved separately, with source indices. No small-component deletion, depth-hole interpolation or unseen-surface completion is applied. Colour is sampled at the projected centre pixel even when an adjacent pixel supplies depth agreement, so colour can bleed at boundaries.

## Observed limitations

The sensor audit found approximately 21–32% missing raw depth outside the housing in sampled frames, including a persistent left strip with about 93–97% zeros. Plant 1 remains very incomplete in the reconstruction. Some stems and leaves in other plants are useful candidates for complementary coverage; cross-camera registration must establish whether they can be fused with D405. More points do not establish better geometry.

Matching the clouds must preserve disagreement for inspection. Manual plant dimensions were not used to set scale, shape or crop bounds. Physical square size, metric accuracy, specimen/organ identity and manual trait validation remain separate issues.

## Preserved files

- `result/l515_supported_reference.ply`: primary supported scene, first L515 camera coordinates.
- `result/l515_supported_upright.ply`: the same geometry rotated using the recorded boards, with no plant-base translation.
- `result/l515_filtered_reference.ply`: optional statistical-cleanup comparison.
- `result/point_evidence.npz`: aligned support/conflict counts and colour-source view indices.
- `result/filtered_source_indices.npz`: mapping from cleanup output to primary supported points.
- `result/icp_diagnostics.json`, `summary.json`, `output_hashes.json`: registration, method and file integrity evidence.
- `bundle/poses.json`, `landmarks.npz`, `bundle_masked.py`: refined camera geometry and the documented research-only feature-mask adaptation.
- `profile.json`, `calibration_frozen.json`, `provenance.json`: frozen configuration, calibration snapshot and source hashes.
- `review/review_provenance.json`: crop bounds, transforms, source hashes and display normalization.

Reproduce with `../reconstruct_sensor.py` stages `prepare`, `bundle`, `fuse`, then `../pack_review.py` using `review_config.json`. Use a new output directory for another reconstruction. Keep viewer HTML and local cloud scripts together for offline use.

Raw inputs, D405 results and the working lab application's source, camera capture and gantry controls were not changed.
