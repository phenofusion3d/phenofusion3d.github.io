# D405 + L515: empirical surface fusion, version 1

Completed 7 October 2026. [Open the fusion comparison](review/index.html). D405, L515 and the fusion are separately labelled and preserved. This is a conditional research candidate, not a gap-free plant model, certified camera calibration or validated trait result.

## What was combined

The primary D405 result is the existing 64-view RGB-stereo reconstruction with corrected filtering and closer camera pairs. The separate L515 result uses 64 RGB-refined sensor-depth views, followed by bounded ICP, TSDF and multi-view support checks. Both original full scenes remain unchanged.

This fusion operates on the established D405 upright inspection region: x 0–1.80 m, y -0.40–0.40 m, z -0.79–-0.10 m. These coordinates retain the reference-camera origin and conditional scale. The region includes pots and may omit outlying plant parts; it is not a biological segmentation or height datum.

| Inspection-region product | Points |
|---|---:|
| Preserved D405 | 1,719,001 |
| Rigidly aligned L515 | 175,708 |
| Accepted additional L515 surfaces | 13,489 |
| Fused candidate | 1,732,490 |

Most L515 observations overlap geometry D405 already recovered. The additional point count is modest and is not a plant-completeness score. Plant 1 and unobserved thin or hidden surfaces remain incomplete.

[Independent computational QA passed](qa/INDEPENDENT_FUSION_QA.md): exact source-coordinate/colour mappings, every classification decision, 74 input hashes and 10 output hashes were checked. A separate implementation recomputed 579 candidate points across 64 D405 views (37,056 point/view checks), with no support or conflict mismatches. This verifies recorded computation, not physical accuracy.

## Why this alignment was selected

The recorded boards gave a consistent starting rigid transform. However, one rigid fit to distant gantry features did not reconcile the two frozen RGB bundles across the scan. A camera-trajectory correction improved those far image residuals, but remained poorer at near-plant sensor geometry; it was not used in this fusion.

A bounded rigid surface registration used the P1/P3/P5 pot/soil regions, with memberships frozen before fitting. P2/P4 regions and all foliage were held out. It improved the held-out pot nearest-surface median from 6.05 to 2.24 mm and the held-out foliage symmetric median summary from 6.47 to 3.36 mm. Occlusion and incomplete coverage leave substantial tails.

An additional source-image test used **65 matched P2/P4 soil features**, excluded from fitting and reviewed in source photographs. Of these, 62 had sufficient valid L515 depth. Applying the proposed transform to those measured rays with the saved L515 final ICP poses gave:

| Matched soil 3D diagnostic | Board starting transform | Selected empirical surface transform |
|---|---:|---:|
| Median disagreement | 10.968 mm | 3.411 mm |
| 90th percentile disagreement | 14.223 mm | 7.415 mm |

For the selected transform, 51/62 correspondences were within 5 mm and 58/62 within 10 mm; maximum disagreement remained 22.506 mm. These observations share camera models and gantry-conditioned geometry, so they are not independent physical ground truth. Soil-plane orientation ambiguity remains: reversing training and validation pots changes the fitted rotation. The transform is an **empirical alignment of measured surfaces**, compensating some combined errors; it must not be exported as a verified physical colour-camera extrinsic.

See [the full cross-camera review](../../research_l515_20261007/cross_camera/CROSS_CAMERA_REVIEW.md), [rigid probe](../../research_l515_20261007/cross_camera/pot_rigid_probe/pot_rigid_alignment.json), and [matched-soil evidence](../../research_l515_20261007/cross_camera/near_static_holdouts/near_sensor_alignment_comparison.json). `alignment_selection.json` preserves the decision and evidence hashes.

## Fusion rules and provenance

Every D405 point in the inspection region retains its original coordinates and colour. L515 points receive the one declared rigid transform; scale and reconstructed camera trajectories are unchanged. The fusion is an observed-point union: it does not average the cameras into new surfaces or invent missing geometry.

L515 observations within 4 mm of existing D405 geometry are suppressed as near-duplicates. Remaining candidates are projected into the 64 accepted D405 stereo depth maps, with an 8 mm agreement tolerance and a 16 mm free-space margin. Excessive free-space contradictions are withheld. Points 4–12 mm from existing D405 geometry with fewer than two agreeing D405 maps are also withheld as uncertain overlapping layers. These thresholds are processing choices, not accuracy guarantees.

The **exclusive** decision partition is:

| Decision | L515 points |
|---|---:|
| Near-duplicate suppressed | 140,434 |
| Nonduplicate free-space contradiction | 3,823 |
| Nonduplicate uncertain overlap | 17,962 |
| Added with at least two agreeing D405 depth maps | 8,330 |
| Added with fewer than two D405 agreement votes | 5,159 |
| Total | 175,708 |

The last group is explicitly a **L515-only complementary candidate**. Its original L515 multi-view evidence is retained, but absence of a D405 contradiction is not cross-camera confirmation. Distinct map votes also share source images and systematic errors; they are not independent statistical trials. The 21,785 withheld nonduplicate points remain available as a separate viewer selection and file.

The viewer offers the fused candidate, preserved D405, aligned L515, a camera-source colour overlay, L515 additions alone and withheld overlaps. Blue in the source overlay denotes D405; amber denotes added L515. The original RGB files remain separate from that display overlay. Every selector uses the same crop, display scale, angle and sampling stride; native point spacing differs between the two reconstructions.

## Remaining research limits

L515's 0.00025 m/count conversion remains conditional. Its board/motion and RGB-landmark diagnostics do not identify a unique scale or axial-bias correction; no such correction was applied. The printed board dimensions still need confirmation. The fixed depth-alignment interpretation follows the saved colour-sized raster and current exporter, without a recording-specific metadata manifest.

The source L515 images contain a persistent missing-depth region and other holes. Both captures provide limited viewing directions. Fusion cannot recover surfaces never observed reliably by either camera. Sparse fragments, boundary colour bleeding, biological motion and local registration error remain possible. Manual plant dimensions were not used to fit geometry, scale or alignment.

This result is suitable for comparative inspection and further validation. Organ-level measurements and hyperspectral mapping require their own evidence and acceptance checks.

## Files and reproduction

- `fused_review_reference.ply`: primary fused inspection region, D405 reference-camera coordinates.
- `d405_review_reference.ply`, `l515_aligned_review_reference.ply`: separate sources in the same coordinates.
- `l515_additions_reference.ply`, `l515_excluded_reference.ply`: added and withheld contributions.
- `fused_source_colours_reference.ply`: identical fused geometry with camera-source colours.
- `fused_point_provenance.npz`: exact camera ID and original full-cloud point index for every fused point.
- `l515_fusion_decisions.npz`: distances, cross-view votes, exclusive decision codes and source evidence for every reviewed L515 point.
- `input_hashes.json`, `output_hashes.json`, `summary.json`: frozen processing inputs and outputs.
- `review/review_provenance.json`: exact upright transforms, crop mappings and browser buffers.
- `qa/`: independent computational checks, distinct from physical calibration validation.

Reproduce using `generated/research_l515_20261007/fuse_cameras.py` with `fusion_v1_config.json`, then `pack_review.py` with this directory's `review_config.json`. Use a new output directory for changed settings. Keep the viewer HTML and cloud scripts together for offline use.

Separate L515 research files: [reconstruction report](../../research_l515_20261007/l515_sensor_v1/RECONSTRUCTION_REPORT.md). Preserved D405 comparison: [open viewer](../../research_20260928_improvement_20261007/comparison/index.html). Raw recordings and the lab acquisition, camera and gantry software were not changed.
