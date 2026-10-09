# Local multimodal registration rescue — 8 October 2026

This directory contains six executed, frozen image-registration experiments on the lower green P5 leaf, using the recorded FX10 display and D405 RGB frame 1055904. It contains **no accepted new dense 3D assignments** and does not modify reconstruction, spectral samples, original recordings, capture software or earlier results.

## What was newly attempted

Previous attempts used SIFT, simple image warps, grayscale ECC and Lucas–Kanade tracking. These experiments instead use:

1. Directional local self-similarity descriptors (MIND-style), normalized independently at each image location. A residual affine fit is followed by a smooth bicubic 5 × 7 control field. RGB, grayscale and stronger-regularization variants were executed.
2. A coarse-to-fine MIND fit at quarter, half and full resolution. A bounded translation grid supplies the initialization using only the image-training objective. The fit then estimates affine and smooth local corrections.
3. Smoothed joint-intensity normalized mutual information, using a 32-bin joint histogram, three training-selected starts and bounded affine correction.
4. A foreground-restricted repetition of the MIND pyramid. This removes white-board pixels visible inside the initially warped source, using eroded source chromaticity, while preserving the same deformation settings.

The shared initialization is the previously recorded six manually proposed outline/vein correspondences. Several proposals are uncertain and are **initialization hypotheses**, not certified material landmarks. No new point correspondences were hand-fitted in this directory.

## Controls and evaluation

The previously reviewed central features `green_lower_0` and `green_lower_4` were excluded from the fitting objective. Exclusion radii cover the descriptor footprint: 18 pixels for single-scale MIND, 30 pixels for the pyramid, and 20 pixels for mutual information. Those coordinates enter exclusion masks only; their error is not an optimization target. Candidate fields were saved and hashed before evaluating their errors. A separate auditor withheld fresh anatomical check coordinates from this fitting process.

All runs are reported. The minimum observed check error is not used to choose a new “validated” model. The prior three-pixel screen is retained as an image-registration screen, not physical ground-truth accuracy: the old annotations and newly reviewed anatomical landmarks have nonzero localization and identity uncertainty.

| Frozen candidate | Old check 0 (native RGB px) | Old check 4 (native RGB px) | Prior 3 px screen |
|---|---:|---:|---|
| Primary RGB MIND | 6.3181 | 7.7559 | Fail |
| Stronger smoothing | 6.4533 | 7.8416 | Fail |
| Grayscale MIND | 6.3511 | 7.8216 | Fail |
| Coarse-to-fine RGB MIND | 5.6371 | 7.3447 | Fail |
| Mutual-information affine | 13.7992 | 16.0362 | Fail |
| Foreground-only MIND pyramid | 10.3187 | 12.3429 | Fail |

The initial affine errors were 7.0353 and 8.2446 pixels. The coarse-to-fine MIND result reduces both, but still fails the declared screen. Smooth fields have positive local Jacobians in their training regions (no detected folds); this does not prove anatomical correspondence. The materially different foreground-restricted solution also demonstrates sensitivity to the pixels supplied to the objective.

The blind auditor froze three additional image labels before evaluating the fields, without giving their coordinates to this fitting process. The label-file hash is `a80f090c375c8a2736faf37e366283201da7664692faaa5c78f286aa760ca19e`. Results are saved separately in `../control_audit/blind_local_registration_evaluation.json`.

| Frozen candidate | Basal notch (px) | Basal vein (px; low confidence) | Distal vein (px) |
|---|---:|---:|---:|
| Primary RGB MIND | 2.03 | 21.32 | 1.95 |
| Coarse-to-fine RGB MIND | 11.88 | 29.23 | 11.59 |
| Mutual-information affine | 25.03 | 38.87 | 21.59 |
| Foreground-only MIND pyramid | 9.77 | 18.92 | 12.69 |

The basal notch and distal vein were rated low-medium confidence; the basal vein was already rated low confidence before evaluation because its repetitive anatomy is ambiguous. All three have subjective image-localization uncertainty, with transformed worst-direction bounds approximately 6.7–8.4 RGB pixels across these models. Those bounds are not confidence intervals. The ambiguous basal-vein match cannot independently veto a model. Conversely, two close predictions for the primary map do not certify precise dense mapping: the original affine already gave 1.81 and 1.57 pixels at those two features, and the primary MIND field largely retains that initialization. The broader deformations reduce some old check errors while worsening these fresh checks. No model is promoted on that evidence, and no independent physical accuracy is claimed.

## Saved evidence

- `old_control_checks.json`: post-freeze errors, every model's hash and the no-selection policy.
- `registration_check_evidence.png`: all six check results on the same recorded RGB crop, without spectral colour projection.
- `frozen_experiments.json`: the first three runs, initialization policy and original input hashes.
- `primary_mind_rgb.json`, `sensitivity_stiff.json`, `sensitivity_gray.json`, `pyramid_mind_rgb.json`, `mutual_information_affine.json`, `pyramid_mind_foreground.json`: optimization settings, training objectives and frozen-field hashes.
- Corresponding `.npz` files: exact forward displacement fields for independent checks.
- `*_pair.jpg`: source image and target resampled through each hypothesis. These are alignment diagnostics, not fused plant results.
- Saved training masks make the source support and control exclusions inspectable.

## Forward-map convention

For a native FX10 pixel `(column, line)`, form rotated display position `(line, 1023 − column)`. Apply `initial_HSI_rotated_to_native_RGB` to obtain the initial native RGB position `p`. Subtract `source_crop_xyxy[:2]` to index `forward_displacement_rgb_px` bilinearly. The candidate native RGB coordinate is `p + displacement(p)`. This map is defined over the saved crop only; extrapolation or clipping outside it is not supported.

The native RGB crop is `[930, 430, 1170, 605]`. These fields do not by themselves identify a correct existing 3D vertex. Passing source depth, surface proximity or reprojection checks would still not repair an incorrect spectral material-point correspondence.

## Reproduction and limits

The scripts run in the repository's existing `venv` with NumPy, OpenCV, SciPy and CPU PyTorch. Threads are limited to two. Run `mind_registration.py`, `mind_pyramid.py`, `mutual_information.py`, then run `mind_pyramid.py` with `MIND_FOREGROUND=1`. The evaluation is separate in `evaluate_frozen.py`; it does not fit or change models. Earlier frozen results should be preserved before a new replay.

The FX10 input is the existing 661.10/550.91/471.26 nm three-band display, not a calibrated camera RGB response. One green leaf and one RGB viewpoint do not establish full-plant or cross-dataset generalization. No claim is made that every possible registration method has been exhausted. These bounded experiments provide additional measured failure evidence and a modest reduction in two old image-coordinate errors, not completed dense spectral fusion.
