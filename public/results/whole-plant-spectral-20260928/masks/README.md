# Optional visible-tissue candidates

These outputs assist full-scene spectral browsing. **The full scan must remain visible and clickable when the mask is disabled.** The mask does not define all available measurements or prove all leaves have been detected.

Each camera was processed independently in native scan-line / detector-column coordinates. The five broad scan-order browsing windows follow the earlier reviewed regions. They are not an operator-certified specimen identity map, and leaning foliage can cross a window boundary.

## Method

`build_candidate_masks.py` reads the run003 ENVI recordings using the existing validated reader and a read-only memory map. Twelve historical tissue-interior polygons provide positive examples; explicit table, rail and soil rectangles provide negative examples. A fixed-seed random forest uses a small set of measured spectral bands, per-pixel spectral shape, brightness and the existing three-band display. A tree-vote score of at least 0.75 marks candidates; 0.30–0.75 is uncertain. This score is not a calibrated probability or independently measured segmentation confidence. There is no filling, dilation, invented geometry, or spectral interpolation.

The broad candidate highlighting was visually inspected beside the original images in both camera contact sheets. Many coloured-leaf silhouettes are included. R1's dry, narrow foliage is poorly represented by the old interior examples and is often excluded. Background shadows and labels can be uncertain or falsely included. Bright streaks and saturated regions are present in the recorded input. There is no independent anatomical ground truth for precision, recall or complete-leaf coverage.

## Files and coordinates

- `{sensor}_candidate_labels.npy`: uint8, `[native_scan_line, native_detector_column]`; 0 = unselected/background candidate, 1–5 = candidate in R1–R5, 255 = uncertain.
- `{sensor}_region_windows.npy`: the broad R1–R5 windows without tissue selection.
- `{sensor}_tissue_vote.npy`: float16 appearance score, not correctness probability.
- `{sensor}_candidate_overlay.png`: transparent native-coordinate highlight.
- `{sensor}_rotated_overlay.png` and `{sensor}_rotated_labels.png`: same arrays rotated 90 degrees counter-clockwise; viewer x = native scan line, viewer y = detector width minus 1 minus native detector column.
- `{sensor}_candidate_contact.jpg`: source and optional highlight for all five regions.
- `{sensor}_independent_flags.npz`: suspected clipping in any band, zero in any band, and reference-column support. These remain separate from tissue labels.
- `{sensor}_summary.json`: exact selection method, region counts, coverage caveats and source metadata.
- `{sensor}_candidate_mean_spectra.json`: 224-band candidate-pixel means of raw DN, plus means excluding zero and suspected-clipped readings, counts and clipping counts per band.

These means are **conditional on this spectral appearance selection**. They are not unbiased whole-plant spectra, calibrated reflectance, physiological trait estimates, leaf areas, or an FX10/FX17 merged spectrum. Values above the suspected-clipping threshold are shown in the all-reading mean and explicitly counted; the separately named unclipped mean changes the contributing tissue across wavelengths. White/dark correction is not applied to these means.

## Verification

`verification.json` records exact label rotation, all old patches lying within their expected broad region, independently recomputed native-plane mean/count checks, and 300 independent all-band clipping/zero checks per camera. These check storage and arithmetic; they do not validate anatomical segmentation.

Reproduction: run `build_candidate_masks.py`, `render_contact.py`, `finish_browser_assets.py`, then `verify_masks.py` with the project scientific Python dependencies. No source cube, old result, hardware path, or application file is modified.
