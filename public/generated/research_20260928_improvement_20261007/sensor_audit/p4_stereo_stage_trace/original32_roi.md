# P4 RGB stereo stage trace: original32_roi

Conditional stage diagnosis, no geometric or trait ground truth

Existing RGB stereo samples within20 mm of accepted P4 conditional landmarks, with exact saved integrated ICP transforms. No depth recomputed or thresholds changed.

Counts below are source observations within a sphere around a conditional landmark. Nearby samples can belong to other structures. The central landmark is not independent metric ground truth.

| Landmark | Source samples within2 /5 /10 /20 mm | Passing original visibility policy before TSDF | Nearest source / passing sample, mm | Nearest supported checkpoint / final cloud, mm |
|---|---|---|---|---|
| P4_single_hanging_bud | [148, 177, 503, 2335] | [138, 151, 347, 1673] | 0.158 / 0.158 | 0.578 / 8.013 |
| P4_left_yellow_flower_junction | [0, 810, 5894, 12727] | [0, 801, 5624, 12197] | 3.081 / 3.081 | 3.720 / 3.720 |
| P4_right_yellow_flower_junction | [396, 2294, 5295, 6598] | [396, 2287, 5098, 6080] | 0.205 / 0.205 | 0.540 / 0.540 |

The existing policy is at least3 supporting anchors,6 mm depth agreement using the unchanged5-pixel neighbourhood, and conflict <= max(1,0.3*support). No acceptance threshold was relaxed. Original32 uses the corrected RGB-footprint mask; v3 uses its actually saved masks and final integrated ICP transforms.

Landmarks share factory camera calibration and original RGB bundle poses; they are conditional and not independent metric truth. Saved ICP can move the local camera coordinates slightly.
Sphere samples can belong to nearby plant parts; counts are source observations, including repeats, not distinct reconstructed surfaces.
Passing pre-TSDF source points establishes policy support for some nearby samples, not guaranteed survival of voxel-centre TSDF extraction.
A gap between source support and supported_cloud can arise during TSDF integration/extraction or visibility retesting at new surface coordinates; this audit does not isolate those two without a raw TSDF checkpoint.
Absence within2 or5 mm must be interpreted with the landmarks pixel-only uncertainty and unmeasured pose/calibration errors.

No source or application files changed. NPZ files preserve each examined source sample, source pixel/frame and visibility counts. Complete provenance and per-frame diagnostics are in the JSON.
