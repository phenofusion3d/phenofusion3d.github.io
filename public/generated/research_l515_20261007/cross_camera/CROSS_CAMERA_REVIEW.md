# D405–L515 cross-camera alignment review

The best tested **empirical surface alignment** is the bounded pot/soil rigid transform in `pot_rigid_probe/pot_rigid_alignment.json`. Fresh source-image matches on held-out P2/P4 soil support it more strongly than the independent checkerboard seed or the far-static camera-trajectory correction. This does not establish true camera extrinsics, traceable metric accuracy, or perfect plant fusion.

All work here is generated research evidence. Raw recordings, the main/lab application and existing D405/L515 reconstruction outputs were preserved. No manual plant measurements, biological size targets, sensor-unit adjustment, or plant deformation were used.

## Evidence and comparison

The source-only near check contains 65 observed soil-texture correspondences, covering 59 distinct D405 RGB-bundle landmarks in L515 frames 417039, 828961 and 1243159. Four native-image polygons select clear soil interiors on P2 and P4. Leaves are excluded by source-image review. All three polygon panels and all 65 D405/L515 source patch pairs were visually inspected. Mutual SIFT matches require a descriptor ratio below 0.65 and support for the same landmark from at least two D405 source frames. These remain assistant-reviewed candidates, with operator confirmation pending.

The pot alignment was fitted using P1/P3/P5; these P2/P4 correspondence checks were held out. Their image masks, measured pixels and landmark associations were frozen before numerical comparison and were never used to tune the transforms. The 62-point quality cohort requires a positive centre-depth sample and at least 20 positive samples in its 5×5 patch, regardless of agreement with a transform. The other three records remain in the evidence file.

The following distances compare each **physically matched D405 RGB landmark** with its L515 raw-depth observation, using the L515 **final accepted sensor ICP camera pose**. They are not nearest-neighbour cloud distances. The 5×5 median is a local reading, not an exact ground-truth point. Centre readings give the same 3.411 mm median for the pot transform.

| Fixed mapping | Qualified readings | Median matched distance | P90 | Maximum | Within 5 mm |
|---|---:|---:|---:|---:|---:|
| Independent board seed + final L515 ICP | 62 | 10.968 mm | 14.223 mm | 23.033 mm | 0 |
| Bounded pot rigid + final L515 ICP | 62 | **3.411 mm** | **7.415 mm** | 22.506 mm | **51** |
| Far-static camera-trajectory correction, diagnostic | 62 | 12.709 mm | 15.062 mm | 18.011 mm | 0 |

For the pot transform, 58/62 readings are within 10 mm. P2 median/P90 are 3.095/4.176 mm; P4 are 3.777/8.667 mm. The large tail remains, especially at the later P4 view. No readings were removed for having poor residuals. Raw samples, ray coordinates, per-reading residual vectors, source camera poses and hashes are preserved in `near_static_holdouts/near_sensor_alignment_comparison.json`.

## Why colour-camera alignment and surface alignment differ

An initial image-only test matched fixed gantry rails and metal slats to the D405 bundle's existing 3D landmarks. Individual L515 view poses have plausible static correspondences, but one shared rigid transform over the two frozen RGB bundles leaves horizontal drift across the scan. The rejected trimmed joint fit retains only 73 of 196 training observations and passes only 5 of 41 held-out descriptor candidates at 2 pixels. It must not be used as an accepted fusion transform.

An independent calibration route keeps left, middle and right physical ChArUco sheets distinct despite their repeated marker IDs. Its board-conditioned rigid seed gives internal board correspondence median 0.416 mm and maximum 0.748 mm at fixed conditional square pitch 24.303 mm. Those values measure internal consistency of the board/gantry model, not physical accuracy. Projecting plant-scan static landmarks with the frozen bundles still gives increasing median residuals from 2.33 to 13.27 pixels. The calibration-to-plant transfer therefore needs more than attractive visual overlap.

A bounded seven-parameter diagnostic fits one global rigid extrinsic and one extra camera-translation slope along the measured L515 rail direction. It changes source camera poses only. It does **not** warp an existing point cloud or fit raw sensor units. Alternating sampled views and the original landmark-ID hold-outs are excluded from fitting. The estimated slope is −0.01470 m/m, amounting to 24.128 mm at the full scan endpoint.

This camera-motion model improves held-out far-static RGB matches: the frozen local-consistent subset has median/P90 0.970/1.863 pixels, compared with 3.005/7.292 pixels for the untrimmed rigid baseline. There are 100/109 such matches within 2 pixels. All 149 held-out descriptor candidates are also reported, including mismatches: their median is 1.190 pixels and P90 is 53.654 pixels. There is no static validation beyond frame 1243159; the final portion would be an extrapolation.

However, the fresh **near-soil** RGB check has median/P90 4.726/5.729 pixels under that far-only model. The per-view medians are 1.872, 2.451 and 5.401 pixels, and its raw-depth matched distances remain about 12.7 mm. Thus good far-scene image reprojection does not establish correct nearby plant geometry. The camera-motion model is preserved as a diagnostic and is not recommended over the pot transform for the current sensor-cloud review.

The pot transform empirically aligns measured depth surfaces and can partly absorb depth bias or trajectory errors. It is therefore inappropriate to treat its inverse as a newly certified colour-camera extrinsic and reject it solely on image projection. The source-depth 3D correspondence comparison above is the relevant independent check for this purpose.

## Important limits for fusion and research claims

- Both reconstructions use conditional encoder-based metric scale. Physical checkerboard pitch and session metadata remain incompletely established.
- L515 depth is interpreted on the saved colour-sized raster using factory colour rays and a candidate unit of 0.00025 m/count. Exporter code and image dimensions support this interpretation, but no per-session alignment flag/extrinsics were saved. Pixel correspondence does not independently certify depth registration.
- The independent L515 audit finds range-dependent raw-depth versus RGB-geometry bias. A single fitted rigid transform cannot correct every range or surface orientation.
- The near test is confined to soil on two pots around 0.75–0.78 m camera depth. It does not validate all leaves, thin stems, the scan ends, occluded structures or other datasets.
- Repeated observations and neighbouring soil keypoints are correlated. Sixty-five matches are not sixty-five independent physical ground-truth measurements.
- The reference points are D405 pre-ICP RGB-bundle landmarks, not external metrology. Bundle, calibration, association, local soil roughness and raw-depth uncertainty remain.
- The reverse pot-partition stability fit exceeds the declared 0.75-degree rotation bound (1.321 degrees). The current transform is a bounded candidate, not a uniquely established extrinsic.
- Keep disagreements and unobserved regions explicit. Any later combined result should preserve camera/source provenance, original separate reconstructions, and uncertain/disagreeing geometry. These results do not justify hole filling or a completeness claim.

## Reproducible artifacts

- `static_rgb_alignment.py` and `static_correspondences_<frame>.json`: image-only fixed-scene matches, per-view PnP, hold-out IDs, native pixels and raw-depth patch samples.
- `refine_static_rigid_seed.py` and `joint_static_rigid_alignment.json`: rejected shared rigid RGB fit, kept for audit.
- `check_board_transfer_seed.py` and `board_transfer_alignment_check.json`: separately identified physical-board rigid seed and plant-scan checks.
- `test_trajectory_correction.py`, `trajectory_correction.json`, and `corrected_L515_camera_poses_D405_reference.json`: bounded camera-motion diagnostic, withheld-view results, leave-one-training-view-out sensitivity, and explicit late-scan extrapolation labels.
- `near_static_holdouts/near_static_correspondences.json`: frozen source-only soil candidates and polygons, never fitted.
- `near_static_holdouts/near_static_visual_review.json`: completed visual review and raw source-image/depth hashes. The original candidate file retains its pre-review status; this separate review record supersedes that status without changing candidate coordinates.
- `near_static_holdouts/near_static_validation.json`: independent image reprojection comparison.
- `near_static_holdouts/near_sensor_alignment_comparison.json`: independent matched raw-depth 3D comparison using final L515 ICP poses, including every reading and full residuals.
- `near_static_holdouts/near_roi_*.jpg` and `near_patch_pairs_*.jpg`: source review panels.

No full fusion was performed by this audit. The parent task selected the pot rigid transform for a separate **conditional empirical fusion** under `generated/research_d405_l515_fusion_20261007/v1`, retaining the original separate reconstructions. The parent task owns that fusion and its presentation; this review does not certify its later output or imply that every admitted point is correct. The frozen pot transform has not been edited by this audit.
