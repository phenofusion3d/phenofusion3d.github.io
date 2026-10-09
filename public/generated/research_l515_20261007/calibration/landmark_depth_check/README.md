# L515 RGB-landmark versus raw-depth diagnostic

diagnostic_only_no_scale_or_bias_correction_applied.

35,215 smooth valid low-reprojection observations yielded 3,733 distinct landmarks with at least 3 depth observations and 80 mm camera span. Native candidate 0.00025000 m/count is unchanged. Bundle residuals reproduced to 1.03e-12 px.

## Depth-stratified native residuals

| RGB Z bin (m) | Landmarks | Median sensor minus RGB (mm) | P90 absolute difference (mm) | Median inferred m/count |
| --- | ---: | ---: | ---: | ---: |
| [0.4, 0.6] | 912 | 11.094 | 17.952 | 0.000245034 |
| [0.6, 0.8] | 1838 | 6.585 | 10.528 | 0.000247852 |
| [0.8, 1.0] | 877 | 8.500 | 12.595 | 0.000247708 |
| [1.0, 1.3] | 13 | -14.706 | 343.894 | 0.000253708 |
| [1.3, 1.6] | 93 | -15.069 | 36.750 | 0.000252643 |

## Diagnostic models, never applied

| Model | Gain | Offset (mm) | Held-out median absolute error (mm) | Held-out P90 absolute error (mm) |
| --- | ---: | ---: | ---: | ---: |
| native | 1.000000 | 0.000 | 7.884 | 14.563 |
| offset | 1.000000 | -7.767 | 2.863 | 8.384 |
| scale | 0.990537 | 0.000 | 2.962 | 10.157 |
| affine | 1.016430 | -20.134 | 2.727 | 7.205 |

Low reprojection, validity, smoothness and camera-span gates were chosen before inspecting the residuals. No sensor-vs-RGB agreement gate was used. A five-by-five smoothness window does not repair missing depth or validate thin structures. Model comparisons are conditional diagnostics with correlated observations; they do not identify a unique physical source of disagreement.

## Limitations

- RGB landmarks are estimated without sensor depth, but share factory K and gantry-conditioned metric priors; this is not independent physical validation.
- Tracks may contain correspondence/material-motion error. Smooth valid regions preferentially sample broad surfaces and background rather than difficult thin plant edges.
- Fit each model on per-landmark medians. Five held-out ID folds avoid counting each repeated observation as an independent training datum, but landmarks/images remain correlated.
- Offset and scale models are diagnostic candidates, not a device calibration. No fitted correction is applied to the reconstruction or main software.
- No manual plant dimensions, observed trait values or expected plant morphology enter selection or models.

## Interpretation and decision

The common 0.4-1.0 m RGB-depth strata show positive sensor-minus-RGB axial differences of approximately 6.6-11.1 mm. Their variation is not a clean monotonic scale-error signature.

An offset-only diagnostic and a scale-only diagnostic give very similar held-out median errors (2.86 and 2.96 mm). The affine diagnostic reaches 2.73 mm but cannot uniquely identify device bias, scale, shared geometric model error or correspondence error.

Held-out RMS remains approximately 41 mm after fitted diagnostic corrections. These retained tails must accompany the small robust medians; no sensor-agreement selection was used to hide them.

Only 13 landmarks occur at 1.0-1.3 m and 93 at 1.3-1.6 m; their reversed signed bias is not sufficient evidence for a distance correction. No accepted landmarks occur at 0.2-0.4 m, so this diagnostic does not characterize the nearest plant structures.

Samples are not semantically classified as plant, pot or rig. Smooth full-patch validity favors broad surfaces. The result does not establish depth accuracy for thin leaves, grain heads or occlusion boundaries.

Retain 0.00025 m/count as the explicitly conditional reconstruction candidate. Do not apply any fitted gain or offset to the frozen sensor reconstruction or combine cameras under a claim of verified absolute metric accuracy.
