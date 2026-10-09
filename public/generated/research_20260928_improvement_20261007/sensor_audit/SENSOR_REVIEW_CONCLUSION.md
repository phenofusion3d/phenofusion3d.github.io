# D405 sensor-depth review: incomplete thin-structure support

The recorded D405 depth supplies repeatable local surface candidates, especially larger leaves and some flower junctions. This bounded audit does **not** establish complete recovery of the missing P1 or P4 structures. Keep the sensor-only candidate separate and compare it with the improved RGB reconstruction before considering a validated merge.

All distances remain conditional on **0.0001 m/count**, the assumed recorded depth-to-colour alignment, saved factory intrinsics, and the frozen RGB-derived camera poses. Internal repeatability is not absolute accuracy. No missing depth was filled, no points were scaled to manual traits, and no application or raw capture files were changed.

## What was tested

Eight sampled source anchors were compared against up to six neighbouring accepted cameras in the frozen 32-view pose set. The strict gate requires at least three distinct sensor views, zero observed free-space contradictions, and at least 6 cm of supporting camera-position span. Its adaptive tolerance is `max(0.003, 0.01*z_predicted**2)` metres. This is an analysis threshold, not a manufacturer precision guarantee. Original depth observations are preserved; the 1.5 mm voxel step selects one original observation without averaging.

`SENSOR_DEPTH_AUDIT.md` and `sensor_depth_audit.json` contain the full method, source hashes, thresholds, alignment diagnostic and depth-range split. `sensor_strict_evidence.npz` records original source pixels and support evidence. Mechanical checks confirm finite points, at least three distinct support bits and the required supporting span.

## Visual findings

- **P1:** the source RGB shows narrow dry stems and leaves. Many apparent sensor strands have either fewer than three agreeing views or at least one other view that sees farther through the proposed surface. The zero-conflict gate removes these contradictory strands. The retained cyan points cover only sparse, disconnected pieces; they do not recover a continuous P1 structure. See `P1_sensor_support_detail.png`.
- **P4:** some larger leaves, flower regions and stem segments have repeatable sensor support. Many thin sections remain absent or contradictory. The retained geometry is incomplete, and the broad review region also includes neighbouring foliage. See `P4_sensor_support_detail.png`.
- Colour support alone is weak discrimination here: 62,510 of 62,774 strict voxel representatives pass the additional chromaticity test. Similarly coloured neighbouring surfaces and depth-colour bleeding can pass. A plausible colour does not establish that a proposed thin surface is real.
- The small alignment search found no consistent gross pixel displacement. Some frames improve slightly at a 2-pixel offset; no correction was applied. This comparison against RGB stereo cannot distinguish sensor alignment error from occlusion, depth bias or stereo error and does not certify registration.

## Where the retained points lie

These are loose spatial station bands, **not specimen segmentations**. Counts are original observations selected per voxel; neither point count nor density is a completeness score.

| Review band | Strict representatives | Also colour supported | Colour supported and >6 mm from previous RGB |
|---|---:|---:|---:|
| P1 region | 5,979 | 5,974 | 1,749 |
| P2 region | 20,006 | 19,914 | 4,298 |
| P3 region | 25,778 | 25,720 | 2,266 |
| P4 region | 11,011 | 10,902 | 1,490 |

Most retained points lie in the P2/P3 regions. Of 9,803 colour-supported discrepancy candidates, 6,198 originate within the audited 0.15–0.5 m source-depth interval and 3,605 beyond 0.5 m. The latter are outside the manufacturer's ideal D405 range and remain explicitly separate in the evidence. Distance from the previous RGB cloud means disagreement or additional coverage; it does not prove a newly recovered plant surface. The new shorter-baseline RGB run may already recover some of these locations.

## Conditional P4 landmark checks

The independent visual audit selected these RGB landmarks before comparison with this sensor result. It triangulated them using the same factory intrinsics and RGB-derived pose family. Its uncertainty interval accounts for pixel perturbation only and excludes calibration, pose and identity errors. Consequently, the checks below are conditional consistency tests, **not independent metric ground truth**. Ambiguous/rejected landmarks were excluded.

Full evidence, source-frame depth hashes and per-view comparisons are in `sensor_landmark_comparison.json`. The source landmark file is `../visual_audit/conditional_landmark_depth_review.json`.

| Landmark | Nearest strict sensor point | Strict points within 5 / 10 / 20 mm | Interpretation |
|---|---:|---:|---|
| Isolated hanging bud | 8.54 mm | 0 / 11 / 121 | No strict local candidate supports the actual marked bud centre. Nearby surface points must not be relabelled as the bud. |
| Left yellow-flower junction | 2.56 mm | 14 / 214 / 435 | Some nearby geometry is supported; raw centre depths differ from the conditional RGB estimate. |
| Right yellow-flower junction | 1.78 mm | 54 / 191 / 275 | Positive local example of repeatable sensor geometry compatible with the conditional RGB location. |

For the **bud**, native RGB centres are `(814,339)` in frame 1003470, `(723,341)` in frame 1030829 and `(637,342)` in frame 1055904. The raw centre depth is **zero in all three**. The first two 7x7 neighbourhoods contain no nonzero depth. The final neighbourhood has 13 nonzero samples at approximately 0.1929–0.1930 m, compatible with the conditional RGB estimate of 0.19418 m and its pixel-only interval. However, **none of those local samples passes the strict multi-view gate**. Their existence does not justify filling the bud or connecting its stalk.

For the **left junction**, the three centre readings are 0.1982, 0.1971 and 0.1967 m, compared with a final-view conditional RGB estimate of approximately 0.20579 m. Local patches still contain compatible observations, including 13 strict compatible samples in the final-view patch. This supports nearby flower-region geometry but cautions against treating the centre reading as precise truth.

For the **right junction**, centre readings are 0.2509, 0.2504 and 0.2502 m, compared with a final-view conditional RGB estimate of approximately 0.25235 m. All 49 samples in each 7x7 patch are compatible with that view's pixel-only interval expanded by the audit's 3 mm near-range gate; 49 final-view local samples also pass the strict gate. This is a useful positive control, not a validation of all P4 geometry.

## Decision

Preserve the stricter sensor candidate as a separately inspectable diagnostic. Do not relax the zero-conflict rule globally to make stems appear continuous. A point supported by three views can still be contradicted by other visible views, and thin structures can also fail because of genuine occlusion, one-pixel sampling, pose or alignment error. The present data do not distinguish every such case.

The next safe comparison is against the improved shorter-baseline RGB result at the same frozen poses, followed by source-view inspection of the remaining sensor-only patches. Only individually supported additions should be considered for fusion. Missing bud/stem samples remain missing; they are not evidence that an interpolated surface is valid.

Reproduction: `audit_sensor_support.py` creates the bounded sensor audit; `review_sensor_landmarks.py` creates the conditional landmark comparison and the two detail figures. Numerical evidence and PLY candidates remain in this folder and have not been blended into the RGB result.
