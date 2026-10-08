# Whole recorded plant scenes: spectral presentation

Created 8 October 2026 from the 28 September run003 FX10 and FX17 recordings.

Start with `rgb_context/presentation.html` for the illustrated eight-part walkthrough, then `index.html` for live exploration. Both are served by the existing local results server:

- https://phenofusion3d.github.io/results/whole-plant-spectral-20260928/index.html
- https://phenofusion3d.github.io/results/whole-plant-spectral-20260928/rgb_context/presentation.html

## What is complete

The complete camera-visible scenes are available, not only the twelve small historical tissue patches. FX10 has 2,178,048 source pixels; FX17 has 1,361,280. Every one of these 3,539,328 pixels retains all 224 recorded bands. Background, pots and reference strips are intentionally retained for context and can also be inspected.

The viewer provides:

- Five scan-region selectors and the complete original scene for each camera.
- Full-scene three-band composites and 224 wavelength previews per sensor.
- Zoom, pan, exact native pixel selection and the full measured spectrum.
- Original RGB photographs beside the spectral scene, with provisional plant identity and selected earlier candidate matches.
- Pixel CSV export, up to four labelled sample curves for comparison, optional candidate tissue overlays, and regional raw-signal mean CSV exports.
- Explicit clipping, low-signal, missing-reference and descriptor-quality information.

FX10 records 397.66–1003.81 nm; FX17 records 935.61–1720.23 nm. Their signals remain separate. They have different wavelengths, sampling and views; raw DN values are not directly comparable across the two cameras. FX17 does not contain the visible/red bands required for the six existing vegetation descriptors.

## Demonstration

### Pixel-selection viewer correction — 8 October 2026

Every native recorded pixel remains available in both cameras. Selection is not restricted to the old three-location baseline or the optional RGB candidate examples. Click the spectral scan, not the ordinary RGB photograph. The wavelength slider changes the displayed band across the scene; clicking changes the source pixel whose full 224-band curve is shown.

The selected-pixel spectrum now sits beside the scan on wide screens and directly after it on narrow screens. An immediate readout below the scan shows the source coordinates and raw DN at the chosen band. The RGB photograph and old match examples are in an optional expandable section. The regional average is explicitly labelled as a separate summary that stays unchanged for clicks within the same region.

Selecting a new pixel clears the previous graph immediately. Loading or failure of optional RGB context no longer delays or blocks spectral readout. The latest selection wins if requests complete out of order. Arrow keys move the selection by one source pixel; Shift + arrow moves ten. A click outside the recorded image shows a message rather than silently retaining the previous selection.

Raw DN remains available outside white-reference coverage. In provisional Q mode, a button returns to raw DN when normalization is missing or incomplete. Nearby pixels can legitimately have similar spectra or the same clipped band value; a different source coordinate does not guarantee a different numerical value at every band.

Verification: `audit/selection_regression.json` records 12 passing checks, including all 224 DN values for 84 pixels, stale-graph clearing, request races, delayed/failed RGB and raw data outside Q support. `audit/actual_viewer_numerical_verification.json` rechecks raw values, normalization, flags and indices against independent source fixtures. `audit/selection_browser_checks.json` records real canvas clicks and one-pixel moves in all five regions of both cameras. These UI corrections do not modify spectra, calibration or 3D associations.

1. Start with the complete FX10 composite. Point out all five pots and their visible foliage.
2. Choose R3 or R5 to enlarge a plant region, then click a visible leaf. Read its 224-band curve below the image.
3. Move the wavelength slider. It shows the entire scene at that band; the crosshair stays on the selected source pixel and its exact number updates below.
4. Select an RGB reference view to recognise the broad plant/leaf context. Use the candidate-location menu to demonstrate available tentative matches.
5. Repeat with FX17. Explain that it measures a different part of the spectrum and has its own image coordinates.
6. Show the optional regional average and its clipping count. Explain the mask and quality limits before interpreting any difference.

Reproducible example: FX10, line352, column786, band0 (397.66 nm) is 4,880 DN. A provisional RGB candidate can be demonstrated at FX10 line1600, column923 on an upper P5 leaf. Its Q is unavailable because this detector column lies outside the reviewed white-reference support.

## RGB context and correspondence

R1–R5 identify scan-order windows, provisionally associated with RGB P1–P5 using pot order and morphology. They are not operator-confirmed manual-validation specimen identities. Region boundaries are navigation aids, not exclusive leaf/plant masks; leaning foliage can cross them.

The RGB context package contains nine original-frame views and exact source hashes. It also reuses thirteen earlier candidate feature links across P2–P4. For P5 it retains the existing 2,338 FX10 and 862 FX17 partial-surface candidates, only at the exact recorded pixels already present in that result. No nearest-neighbour filling or extension to other leaves is performed. The viewer can display these hypotheses, but does not convert them into independently verified same-tissue correspondence or a new dense 3D fusion result.

## Measurement and display are separate

Numerical spectra are lossless uint16 values from the native BIL files. Per-line files store column differences modulo65536, shuffled into low/high byte planes, then gzip-compressed. The browser reverses this exactly. One click fetches one native scan line, not the entire cube.

All 448 wavelength previews preserve native spatial dimensions, but use an 8-bit 1st/99th percentile intensity stretch and JPEG quality90. Preview colours are approximate and independently stretched by band. No numerical measurement is recovered from image colours. The three-band composites similarly use independent display stretches; FX17 colours are false colour.

Coordinates are zero-based: display x = native scan line; display y = detector-column-count − 1 − native column. Data axes in the raw source are line, band, column. All transformations and source SHA-256 hashes are recorded in `manifest.json`.

## Normalization and scientific limits

Raw DN is measured camera signal, not calibrated reflectance or a health diagnosis. Q = (DN − D)/(W − D) reuses the reviewed white-board and assumed dark-tail profiles. The user confirmed a white board and fixed exposure, but its spectral reflectance and shutter closure at the tail are unknown. Gain is not independently established.

Q is supported only where the reviewed reference columns and quality guards allow it: FX10 columns180–849 and FX17 columns90–519, with additional per-band clipping/contrast exclusions. Values outside support remain unavailable. Low-signal flags are advisory for Q and exclude required bands from descriptors. Reference scan lines are excluded from descriptors. No values are extrapolated, painted across leaves, or filled into missing bands.

Candidate tissue means depend on an appearance-based mask. Dry R1 foliage is often missed, and some shadows/background remain uncertain. The mean including all candidates and the mean excluding zero/suspected-clipped samples are both shown; contributing counts can change with wavelength. FX10 has substantial clipping in some regions/bands. These are not unbiased whole-plant reflectance or physiological traits.

“Whole plant” here means the entire recorded visible scene is accessible. It does not mean every leaf surface was observed, leaves have anatomically verified IDs, or complete 360-degree spectral coverage was achieved.

## Verification

- `export_verification.json`: every exported row decoded and compared exactly to its original uint16 source values; both source files unchanged during export.
- `audit/qa_receipt.json`: independent numerical and export-layout review, including all4,254 rows and448 previews.
- `audit/actual_viewer_numerical_verification.json`: actual browser-decoder/Q/descriptor functions tested on84 pixels, including support boundaries and reference lines.18,816 DN values and flags match exactly. Q and descriptors agree within expected float precision, not necessarily bit-for-bit with historical float32 arrays.
- `masks/export_integration_verification.json`:3,727,360 independently decoded DN values, image orientation and reference-array checks.
- `masks/verification.json`, `masks/quality_audit.json`: mask-coordinate, mean and quality checks. These validate arithmetic, not anatomical segmentation accuracy.
- `rgb_context/asset_validation.json`: RGB/presentation assets and browser checks.
- `browser_verification.json`: controls, exported CSV and page checks from the final interactive review.

## Saved result and portability

All new files are isolated in this folder. Original recordings, reconstruction, camera capture and gantry control were not changed. No repository commit or public deployment was made for this new presentation.

The exact rows plus wavelength previews occupy about710 MiB, with additional RGB context, masks and audit files. This complete numerical viewer is saved separately from the existing website rather than silently adding the large dataset to its publication bundle.

To use it after restarting the existing server, open a terminal in this folder and run:

```text
python -m http.server 8882 --bind 127.0.0.1
```

Then open http://127.0.0.1:8882/index.html. A local HTTP server is needed because the browser loads data files; opening the HTML directly as a file will not work reliably. After serving this folder, no external CDN, AI service or Internet connection is required for inspection. The raw source cubes and research Python environment are needed only to regenerate the result with `export_full_scans.py` and the helper scripts in the subfolders.


## Website package

The website retains every recorded spectrum and all viewer assets. Source-only Python/Node scripts, NumPy mask intermediates, browser screenshots and previous UI backups stay in the research workspace and are not deployed. The numerical verification receipts remain under `audit/`. The interactive HTML, CSS and JavaScript are copied without changes.
