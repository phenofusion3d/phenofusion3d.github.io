# Recorded-data spectral mapping investigation

7 October 2026. **Saved outcome: no defensible 3D-to-HSI calibration was established by this bounded investigation. No fit was attempted and physical fusion remains null.** New work was confined to this directory; earlier spectra, reconstruction outputs and software were preserved.

This review went beyond the earlier missing-calibration inventory: it compared the recorded broad-leaf P3/R3 and P5/R5 appearances, inspected six P5 same-leaf candidate windows and sampled their saved RGB multi-view depth with the correct distortion convention. Five windows have useful recovered-depth support. The specific missing step is a sufficiently distributed set of exact cross-sensor physical-point identities with independently reserved off-plane validation, not merely an unknown millimetre scale.

## What the recorded images support

- The FX10 R5 region and D405 frame 1055904 show a recognizable arrangement of broad leaves, including red upper/lower leaves, two broad green leaves and a variegated right leaf. The six windows are same-leaf candidates, not accepted point correspondences or verified specimen labels.
- The paired zooms show different viewpoint, apparent shape, spatial sampling and contrast. Veins provide promising future annotation features, but the chosen window centres do not identify one independently verified identical vein junction. It would be unsound to fit them as if they did. No independent repeat-localization error or held-out raised landmark set was established.
- The FX17 SWIR display also preserves recognizable broad-leaf arrangement and venation. It is a separate view with different band contrast and sampling, so FX10 point identity cannot simply be transferred through the previous plane-only registration. No FX17 point controls were accepted in this review.
- P3/R3 is less promising for immediate exact-point matching: narrow leaves and overlapping branches/petioles make local ownership and junction identity ambiguous in the compared view. Prior source review likewise records P3/P4 and P4/P5 overlap. No automatic feature pairing or label transfer was used.
- Visible blue/background grid features are planar. The pot is identifiable, but its unmarked circular rim has view-dependent silhouette/extrema; those are not persistent physical material points. No distinctive marked, depth-supported pot feature was established as a shared control in these inspected crops.

## Measured depth at candidate windows

The native RGB centres were undistorted with the saved D405 intrinsics before querying the undistorted recovered-depth raster. Frame 1055904 has an accepted saved reconstruction transform. The depth is recovered from RGB multi-view pairs; it is not an HSI ray calibration or independent physical ground truth.

| Review window | Pair votes at centre | Local pixels with at least 2 votes | Camera depth, original reconstruction units | Accepted control |
|---|---:|---:|---:|---|
| P5_red_upper | 6 | 49/49 | 0.543145 | No |
| P5_green_upper | 3 | 49/49 | 0.519755 | No |
| P5_green_lower | 3 | 49/49 | 0.504554 | No |
| P5_red_lower | 5 | 49/49 | 0.530824 | No |
| P5_variegated_right | 1 | 0/49 | 0.585784 | No |
| P5_green_central | 5 | 49/49 | 0.476024 | No |

Five windows have all 49 local pixels supported by at least two pairs. The right variegated window has only one pair at its centre and no such supported local pixels. Vote counts and local depth spread are consistency diagnostics, not uncertainty bounds. The depths are camera-axis distances, **not heights above the table**. Different depth values alone do not establish a well-conditioned noncoplanar control set.

The JSON retains native and undistorted pixels, individual pair values, local depth quantiles and conditional reference-frame XYZ at the RGB review pixel. Those XYZ values are diagnostic only and are explicitly not assigned to the HSI review-window centre. This preserves the measured evidence without manufacturing correspondences.

## Existing controls and why a fit was not run

The earlier geometry evidence contains 205 per-sensor marker observations and 101 shared FX10/FX17 marker pairs from empty-board run 002. Held-out-sheet affine errors were 0.56–0.81 pixels RMS in that plane. Those controls do not measure raised-leaf response, and the prior extraction did not incorporate D405 pixels or XYZ poses. The plant cubes are run 003; a run-start relationship also requires validation. Repeated marker IDs are qualified by physical sheet.

This investigation accepted **0 exact 3D-to-HSI training controls and 0 independent off-plane holdout controls**. Six plausible same-leaf regions are not a substitute for these observations. Fitting arbitrary centres, assigning nominal leaf heights, or using planar registration on raised leaves would add unsupported information. The existing API requires at least 12 noncoplanar training controls, four independent off-plane holdout points and numeric pixel-error thresholds. No model was created, and no spectral values were assigned to the plant surface.

This is a bounded assessment of the available reviewed evidence, not proof that expert annotation or recovered lab records could never yield a useful exploratory fit. Exact vein-junction annotation across additional views is the most plausible existing-data route, if identities, depth quality and independent holdouts can actually be established. No calibrated HSI spatial intrinsics, fixed extrinsics or per-line/run-start records were newly located by this review; the earlier metadata audit remains the relevant inventory.

## Saved next steps

The [capture specification](calibration_capture_specification.md) and [machine-readable specification](calibration_capture_specification.json) list target layout, shared-frame fields, exact control records, independent holdout policy, numerical residual gates, run transfer and visibility requirements. Recover existing calibration/logs first; otherwise record a rigid measured multi-height target spanning the plant volume. Unknown ChArUco size and recording translation units remain separate physical-scale gaps. A consistent shared arbitrary frame is sufficient in principle for independently pixel-validated mapping.

The previously saved measured DN and exploratory Q/Q0 descriptors remain available. Fixed exposure and intended white-board use are recorded; panel spectral reflectance and the final-tail shutter state remain unknown. No reflectance, physiology or health interpretation is added here.

## Evidence files

- [Three-sensor P5 appearance comparison](R5_three_sensor_appearance.png)
- [Six candidate leaf windows](P5_candidate_landmark_windows.png)
- [P3/R3 comparison](R3_candidate_comparison.png) and [P5/R5 comparison](R5_candidate_comparison.png)
- [Full measured candidate audit](candidate_control_audit.json) and [availability CSV](candidate_availability.csv)
- [Earlier planar holdout evidence](../../research_20260928_processing_20261007/spectral_geometry/pushbroom_feasibility_and_holdout.md)
- [Earlier mapping workspace](../../research_followthrough_20261007/spectral/mapping_workspace/mapping_config.json)
- [Saved measured spectra](../../research_followthrough_20261007/spectral/index.html)

Comparison images use existing three-band display arrays: FX10 target bands 660/550/470 nm and FX17 1600/1300/1050 nm. They are contrast-adjusted recorded-data displays for identifying appearance; no geometric warp or synthetic image generation was used. `inspect_controls.py` and `audit_candidate_controls.py` reproduce this investigation from the saved source products. Full 35 GB raw cubes were not hashed or reloaded for this bounded spatial audit; the input hashes name the exact images, saved depth, calibration/pose and display products that were used.
