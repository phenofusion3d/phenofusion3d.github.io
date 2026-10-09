# Independent D405 metric audit

Numeric checks passed. Existing surfaces and identities were preserved; scale is referenced to the supplied checkerboard pitch, not an independent physical accuracy assessment.

The within-sheet-centered regression independently gives 1.0288746669067 m per old coordinate unit, matching the exported factor to 8.88e-16. There are 57 board observations from 32 frames and 3,067 corners. Reprojection RMS is 0.220402 px. Held-out folds keep whole frames together.

All coordinates and non-coordinate fields were checked for both clouds (8,265,080 full-scene and 1,719,001 inspection vertices). Bundle and final ICP translations were scaled exactly while rotations stayed unchanged. An additional 86,310 in-frame projections using final ICP and lens distortion changed by at most 1.08e-11 pixels.

P3.O03 selected endpoints are both D405: old fused indices 1,221,511 and 944,608 map exactly to original D405 vertices 5,799,835 and 4,949,838. The updated chord is 7.691100957 cm; the arithmetic difference from the operator-only 7.5 cm is +0.191100957 cm. This remains provisional; basal convention and reference readability remain unresolved. No validated MAE/MAPE follows.

Scope limits:

- The supplied 25 mm square and 18 mm marker resolve the formerly unknown design dimensions. Printed-size measurement uncertainty was not supplied.
- The scalar is metres per old frame_id/1e6 coordinate unit. It follows a fixed-mount linear-motion model, retained factory RGB intrinsics and user-confirmed unchanged settings between scans.
- Small pose residuals and reprojection invariance are internal consistency checks, not independently measured physical accuracy or reconstructed surface completeness.
- This is uniform scale re-expression of an existing RGB reconstruction. No new stereo, bundle, ICP, filtering or 1 mm-threshold run took place; inherited thresholds are multiplied by the factor.
- The new best-fit motion direction differs by about 0.0097 degrees. The export intentionally retains existing rotations and direction; it applies the scalar only.
- D405 input depth PNGs and cached synthetic depth arrays are not re-expressed by this script. Consumers must not mix them with scaled cloud/poses without explicit corresponding unit handling.
- The full mixed D405/L515 cloud cannot be multiplied by this D405 factor. L515 depth/rig registration and any mixed-cloud descriptors require separate recomputation.
- The 128,000 comparison root check used bundle poses and an inspection subset despite a full-scene comment. This audit additionally tests original and scaled points with final accepted ICP transforms and lens distortion.
- Correcting board scale does not recover anatomical bases/tips, match ruler sections, resolve leaf-versus-pod identity, or make manual photos independent ground truth.
- The existing marker-edge image ratio is approximately 0.670 rather than 0.720; low-resolution edge localization is not independent physical verification of marker width. Metric scaling here is based on checker-corner pitch, not fitted marker-edge width.
