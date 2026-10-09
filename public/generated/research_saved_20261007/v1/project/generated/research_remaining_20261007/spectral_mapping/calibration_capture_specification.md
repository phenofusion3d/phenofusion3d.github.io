# Calibration capture specification

This is a practical recording specification, not a completed calibration. Recover existing lab spatial calibration and acquisition logs first: FX10/FX17 lens and spatial calibration, fixed rig geometry, per-line motion/timestamps and scan-start transfer. If those records exist, they may reduce the new capture required, but still need independent elevated validation.

## Target and coordinate records

Use a rigid stepped or otherwise noncoplanar coded target whose points have independently measured XYZ coordinates. Cover the column, scan-line and height volume occupied by the intended plants. Choose actual height spacings after measuring that volume; no plant heights are assumed here. Record target dimensions, measurement uncertainty, coordinate origin/axes and units. Shared arbitrary units can support pixel validation; millimetre traits separately require verified physical scale.

Plan roughly 24 well-distributed training controls and 12 independently reserved elevated controls per sensor. These are planning counts, not a sufficiency guarantee. The existing offline fit API has a minimum of 12 training and four independent off-plane validation controls. Include at least two genuinely different measured training heights, preferably three or more, and reserve a whole elevated target/height group or spatial section before fitting. Distinct IDs attached to duplicated XYZ coordinates are not independent observations.

Record exact physical point identities: coded marker corners/centres or unambiguous measured intersections, with a photograph of each location. Do not use a leaf's apparent centre, pot-rim ellipse extrema, or a projected grid prediction as an observed control. Keep independent repeat annotations to quantify image localization variability. Retain raw native coordinates, source band, wavelength, camera distortion convention, depth evidence and XYZ uncertainty.

## Recording procedure

1. Keep the rig rigid and record each sensor's lens/focus, exposure/gain, scan direction and working geometry. Save native cubes/headers and RGB-D calibration.
2. Record per-line encoder position and timestamps, or independently validate displacement per line and motion stability. Include persistent rigid start/end fiducials in calibration and plant captures.
3. Acquire the distributed target at all planned measured heights and capture the separately reserved validation geometry without changing the optics. Check movement/rigidity and do not silently pool different setups.
4. Record true shutter-closed dark data and a white panel at matching settings; record the panel's spectral reflectance and usable spatial coverage if calibrated reflectance is required. These references are separate from geometric calibration.
5. Produce one source-linked control record per physical point and sensor. Keep whole-target/height holdout identities fixed before selecting the model.

## Acceptance before assignment to plant surfaces

Choose numeric column/line and combined RMS, P95 and maximum error limits from the intended leaf-region footprint and measured repeat-localization error before viewing final holdout results. The JSON deliberately leaves thresholds null because the desired spectral footprint has not been measured; null or a boolean cannot certify a calibration.

Check rank/conditioning and independent off-plane residuals over height, location and wavelength. Validate run-start/motion transfer to the plant recording. Restrict projection to positive depth, observed image bounds and the supported 3D control volume. A final surface mapper also needs first-visible ray intersections and explicit occlusion/footprint/uncertainty masks; a good pixel fit alone does not implement visibility.

The existing `processing.research_workspace.spectral_mapping.fit_pushbroom_controls` can fit and assess properly supplied controls offline. It rejects plane-only controls and missing/invalid holdout thresholds. It does not turn the present candidate review windows into controls and does not yet constitute a visibility-aware full-cube mapper. Continue to preserve DN, source band/line/column and all quality masks; current Q/Q0 signals are not calibrated reflectance or validated physiological traits.
