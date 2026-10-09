# Raw D405 depth: repeatability and additional-surface audit

**Conditional depth scale 0.0001 m/count; assumed depth-to-colour alignment. Internal repeatability, not absolute accuracy or confirmed stems.**

Eight dense anchors use the exact 32-view final ICP pose set. Poses are RGB-derived estimates, not externally measured truth. Original sensor values are neither smoothed nor rescaled. The output is separate from the RGB result.

## Repeatability gate

At least 3 distinct raw-depth views including source, zero free-space conflicts among compared valid views, >=.06 m supported camera-position span. Nearest projected pixel, no neighbourhood match search.

max(.003,.01*z_predicted_m**2): 3 mm near/within most ideal range, 10 mm at 1 m. Heuristic repeatability gate, not manufacturer accuracy. Also report twice-tolerance support counts without relaxing final acceptance.

Another sensor view sees farther than predicted point + gate; a closer measurement is classed as occlusion, not contradiction. Zero/out-of-range samples are missing, not support.

An additional colour check is recorded separately: At least 2 geometrically agreeing other views with L1 normalized RGB chromaticity distance <=.22. This heuristic cannot establish leaf identity or remove all colour bleeding.

## Per-frame results

| Frame | Candidate pixels | >=3 agreeing views | Strict (no free-space conflict) | Strict + colour | Sensor zero fraction, full frame |
|---|---:|---:|---:|---:|---:|
| 58790 | 31568 | 5918 | 3061 | 3055 | 0.203 |
| 170514 | 59141 | 16219 | 8003 | 7917 | 0.240 |
| 328592 | 104141 | 39433 | 19383 | 19135 | 0.242 |
| 433466 | 123788 | 60630 | 35456 | 35352 | 0.255 |
| 696431 | 179299 | 102272 | 58570 | 58492 | 0.237 |
| 799028 | 181181 | 87076 | 49758 | 49540 | 0.248 |
| 952549 | 140733 | 79314 | 41200 | 40711 | 0.280 |
| 1055904 | 106895 | 53401 | 30454 | 30393 | 0.289 |

## Separate depth ranges

The camera's ideal operating interval ends at 0.5 m; this audit starts at 0.15 m. The 0.5–1.0 m group is deliberately retained separately as outside-ideal-range evidence, never certified by a range filter. Counts below follow 1.5-mm voxel representative selection.

| Source-depth group | Strict representatives | Strict + colour | Strict + colour >6 mm from previous RGB |
|---|---:|---:|---:|
| ideal_range_source_depth_le_0p5m | 39580 | 39356 | 6198 |
| outside_ideal_source_depth_gt_0p5m | 23194 | 23154 | 3605 |

## Alignment, noise and colour limits

Assume supplied raw depth already aligns to native colour grid; undistort both using saved colour K/dist, nearest neighbour for depth. Verified exact equality to cached sensor maps. Capture code supports align-to-colour but recording-specific confirmation is absent.

Per-frame 2-pixel-grid shifts over +/-8 pixels compare raw depth with repeated RGB stereo without applying any correction. Scores and nominal/best offsets are saved. This is a diagnostic, not a recovered factory depth-to-colour calibration. Edge occlusion, stereo error and raw-depth bias can also change the best shift.

Distinct views are not statistically independent: the rig trajectory and scene are shared, and persistent mismatches can repeat. Texture painted onto a depth ghost can appear plausible. Colour agreement reduces some mismatches but pale structures and similarly coloured background remain ambiguous. Strict filtering can remove genuine one-pixel stems; rejected candidates are preserved for diagnosis rather than filled.

## Additional-surface interpretation

9803 strict colour-supported voxel representatives are more than 6 mm from the previous RGB cloud. These are candidates for inspection, not proven rescued stems. They must be inspected in original RGB/depth views and compared with the improved RGB reconstruction before any fusion. The present PLY crop includes background and neighbouring foliage; no per-plant completeness or trait accuracy is claimed.

## Selection and output coordinates

P1-P4 loose station bands by midpoint between previously reviewed soil seeds; x [0,1.22], abs(y)<=.4, at least .02 m above nearest displaced soil-patch height and upright z<=-.1. Not specimen segmentation, stem bases or trait heights.

Choose strongest original measured observation per 1.5-mm voxel; never average, interpolate, scale-fit, close holes or build triangles.

PLY exports use the current recorded-board upright rotation and retain the first-camera origin. Point i in sensor_strict_original_observations_upright.ply matches evidence row i. Other PLYs are explicit colour-support/distance subsets, whose flags can be reproduced from the aligned evidence. No unobserved surfaces are synthesized.

- `sensor_depth_audit.json`: all thresholds, results, provenance and per-frame diagnostics.
- `sensor_strict_evidence.npz`: original source pixel/frame/depth, support bitmasks, colour agreement, baseline distance and coordinates.
- `frame_*_candidate_evidence.npz`: rejected as well as accepted candidate support evidence.
- `frame_*_sensor_audit.png`: source RGB, raw depth, RGB-stereo difference, agreement/contradiction maps.
- `sensor_candidate_overview.png`: upright sensor-only geometry and discrepancy colouring.
- Three explicitly named sensor-only PLY files; none replaces or blends the RGB reconstruction.

`audit_sensor_support.py` reproduces this bounded cache audit. Original capture files and application source remain unchanged. See the existing official camera specification audit for manufacturer conditions; the adaptive gates here are analysis choices, not those specifications.
