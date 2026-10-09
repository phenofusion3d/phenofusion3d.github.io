# Offline spectral mapping workspace

`mapping_workspace/mapping_config.json` records actual missing inputs as null. `observed_planar_controls.csv` contains the already measured, sheet-qualified HSI target centres. `shared_3d_controls_template.csv` intentionally contains only headings because shared noncoplanar 3D controls were not supplied. Do not copy local sheet XY coordinates into a single world plane and call that a height calibration.

The workspace is ready to receive recovered lab calibration and logs. Numeric acceptance limits must be chosen from the intended leaf-region size and spectral footprint before judging held-out observations; this analysis has not invented universal error limits. Operator-confirmed control IDs, shared frame/units and independent elevated-target observations are required. A consistent arbitrary shared length unit can support pixel reprojection validation. Actual printed ChArUco size and recording units remain necessary to independently verify millimetre-scale traits, but their absence is not itself a mathematical prohibition on shared-frame pixel mapping.

The reusable `processing.research_workspace.spectral_mapping` module supports:

1. `fit_pushbroom_controls`: noncoplanar 3D controls to scan-line/column projection, rejecting deficient or ill-conditioned fits, reused holdouts and failed independent off-plane pixel residuals. Explicit `PixelThresholds(rms, p95, maximum)` cannot be replaced by a pass boolean.
2. `project_control_model`: queries restricted to positive fitted projective depth, the recorded image, and the training-control convex hull. The fitted denominator is not claimed as calibrated optical depth. This is empirical projection only, with no ray model or visibility certification.
3. `project_physical_pushbroom`: projects using an independently supplied straight-motion slit-camera model, requiring positive optical depth. Merely supplying parameters does not validate them.
4. `mapping_readiness`: keeps physical fusion null while required evidence is absent.

None of these functions produces a cube-to-surface fusion. That final stage still needs a physically validated ray model, first-visible surface intersections, a justified footprint/occlusion rule, scan transfer, and per-band radiometric validity. The ready control-fitting path reduces future implementation work while preserving the current evidence boundary. Do not substitute a planar homography, nearest 3D neighbour, or arbitrary focal length for these controls.

For independent validation, retain complete elevated targets or spatial sections as holdouts, record source images and measurement provenance, and report column/line errors as well as vector RMS/P95/max. Verify that plant heights and detector positions lie within the accepted calibration support. Do not tune the model against the final holdout. Cross-camera alignment must also be checked at usable wavelengths before combining their spectra.
