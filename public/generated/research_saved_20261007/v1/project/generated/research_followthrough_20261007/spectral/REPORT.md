# Measured hyperspectral follow-through: 28 September plant run 003

**Completed:** 13,343 source-pixel spectra, each with all 224 recorded bands, from 24 independently reviewed tissue patches across five scan-order specimen regions in each camera. FX10 supplies 7,982 spectra and FX17 supplies 5,361. These are 2,988,832 measured DN values, with exact source line, detector column, source band and wavelength. The cameras remain separate. **Actual 3D spectral fusion remains underdetermined and is not claimed.**

The full spectral vectors now preserve raw DN, provisional Q=(DN-D_tail)/(W_board-D_tail), zero-offset sensitivity Q0=DN/W_board, and every per-band quality flag. Invalid Q is NaN. Negative and above-one finite Q are retained. No clipped measurement is reconstructed. All 224 source bands are present even when some normalized values are invalid; this is not a 224-band-valid reflectance claim.

## Tissue evidence and scope

The review uses recorded run-003 imagery: FX10 661.10/550.91/471.26 nm and FX17 approximately 1598.8/1301.56/1050.0 nm. Polygon interiors were chosen manually on those images before examining index values, avoiding a vegetation-index selection rule that would preselect its own reported measurements. The overlay figures make every polygon reviewable. The five R labels mean scan-order specimen-region candidates; they are not operator-verified P identities, organ labels, complete masks, or points matched to the RGB-D cloud. Thin leaves and neighbouring foliage can overlap. The selected interiors have visible tissue support, but mixed pixels and human-review errors remain possible.

Sampling keeps every even scan line and even detector column inside these polygons. It is deterministic and spatially correlated, not a random biological sample. Each camera has an explicit outer-leaf patch outside its white-reference columns. Its raw DN is retained while its board-relative signal remains missing. Reference coverage is FX10 columns [180,850) and FX17 [90,520); no extrapolation fills the outer foliage.

## Actual coverage and clipping

Counts below concern sampled reviewed patches, not all leaves or whole plants. Clipping counts mean one or more bands reached the observed 65520 ceiling. Missing-reference counts and clipping can overlap. “All bands Q-valid” means passing normalization flags, including clipping/reference support; low-signal advisory flags remain separately available and invalidate required index inputs.

| Camera | Patch | Region | Sample pixels | Any-band suspected clipping | No white-column support | All 224 bands Q-valid |
|---|---:|---|---:|---:|---:|---:|
| FX10 | 1 | R1 | 240 | 148 | 0 | 92 |
| FX10 | 2 | R1 | 106 | 0 | 0 | 106 |
| FX10 | 3 | R2 | 954 | 64 | 0 | 890 |
| FX10 | 4 | R2 | 436 | 312 | 0 | 124 |
| FX10 | 5 | R3 | 621 | 32 | 0 | 589 |
| FX10 | 6 | R3 | 674 | 0 | 0 | 674 |
| FX10 | 7 | R3 | 621 | 0 | 0 | 621 |
| FX10 | 8 | R4 | 375 | 4 | 0 | 371 |
| FX10 | 9 | R4 | 417 | 291 | 0 | 126 |
| FX10 | 10 | R5 | 1749 | 458 | 0 | 1291 |
| FX10 | 11 | R5 | 1096 | 645 | 0 | 451 |
| FX10 | 12 | R5 | 693 | 378 | 693 | 0 |
| FX17 | 1 | R1 | 81 | 0 | 0 | 81 |
| FX17 | 2 | R1 | 50 | 0 | 0 | 50 |
| FX17 | 3 | R2 | 541 | 0 | 0 | 541 |
| FX17 | 4 | R2 | 265 | 145 | 0 | 120 |
| FX17 | 5 | R3 | 336 | 0 | 0 | 336 |
| FX17 | 6 | R3 | 430 | 0 | 0 | 430 |
| FX17 | 7 | R3 | 551 | 0 | 0 | 551 |
| FX17 | 8 | R4 | 254 | 0 | 0 | 254 |
| FX17 | 9 | R4 | 274 | 183 | 0 | 91 |
| FX17 | 10 | R5 | 1325 | 15 | 0 | 1310 |
| FX17 | 11 | R5 | 638 | 7 | 0 | 631 |
| FX17 | 12 | R5 | 616 | 0 | 616 | 0 |

## Bands, descriptors and offset sensitivity

The full-resolution patch masks and `*_all_patch_pixels_selected_bands.npz` retain selected raw/relative bands at every polygon pixel, plus all six FX10 descriptors and their flags. `fx10_patch_indices.npz` retains those same descriptors at the sampled full-spectrum pixels. Actual bands and explicit formulas are carried in sidecars and prior provenance; all values match the previous saved products exactly at every queried pixel. Descriptor names are NDVI_800_680, NDRE_790_720, GNDVI_800_550, PRI_531_570, PSRI_678_500_750 and SIPI_800_445_680. SIPI keeps its difference denominator. No cross-camera index is computed.

The white start board and fixed exposure are user-confirmed. The board's spectral reflectance is unknown, and a closed shutter during the final tail is unconfirmed. Q and Q0 compare an assumed tail correction with zero offset; neither is verified reflectance. Per-patch CSV files report valid count at every band. Plotted medians can use different valid pixel subsets at different wavelengths because clipping and other invalid values are omitted; compare their counts, not just smooth curves. Raw-DN medians retain clipped samples. Patch variation, illumination, unknown board response and offset assumptions prevent physiological interpretation.

## Why no new 3D spectral cloud is produced

The supplied geometry evidence has 101 sheet-qualified shared FX10/FX17 marker correspondences. Independent held-out-sheet affine errors are approximately 0.56–0.81 pixels RMS on the table plane. These observations establish useful plane registration diagnostics but not height-dependent pushbroom rays or raised-leaf correspondences. Headers do not supply spatial intrinsics/extrinsics, per-line positions/timing, or a measured plant-scan start transfer. Foliage extends off the reference plane and can occlude other surfaces. A planar warp onto those leaves would hide this missing information.

The exported mapping workspace contains 205 measured individual sensor/target observations and a deliberately blank shared-3D-control template. Its configuration retains unknown optical/motion parameters and numeric validation limits as null. The reusable offline module now fits/project-checks future noncoplanar controls, rejects plane-only/rank-deficient or failed held-out fits, and restricts supported projection to positive projective depth, image coverage and the training control volume. A supplied physical straight-scan model has a separate positive-optical-depth projection path. Both remain fit/project tools: surface visibility and final cube-to-surface mapping are unfinished stages requiring real evidence.

Unknown physical ChArUco pitch and recording translation units are recorded gaps. A common arbitrary coordinate unit can still support numeric pixel reprojection validation; verified millimetres are a separate requirement for physical traits. No shared 3D HSI control frame has yet been established for this recording, so the current configuration reports `blocked_missing_calibration` and `physical_fusion: null`.

## Verification and reproduction

All saved sample raw DN, Q and quality values agree exactly with the previously validated selected-plane products. Every six-descriptor sample also agrees exactly. A separate fresh source read checked all 224 raw bands at 500 deterministic samples per camera. Invalid-value and reference-coverage assertions passed. Full input cubes were never loaded into RAM; reads used read-only memory maps, bounded reference windows and explicit sample lines. Source files and earlier outputs remain untouched.

Run `inspect_regions.py`, then `prepare_followthrough.py`, `build_mapping_workspace.py` and `build_report.py` with the documented Python environment to reproduce these outputs in this folder. The scripts and source hashes are retained. The reusable fit/project module has synthetic nonplanar, planar, numerical-holdout, source-independence, volume, detector and positive-depth tests; synthetic checks validate software behaviour, not this plant recording's physical accuracy.

See `mapping_workspace_README.md` and `mapping_workspace/mapping_config.json` for the concrete missing-control pathway. Prior reference/geometry reports remain the authoritative detailed source audit in `generated/research_20260928_processing_20261007`.
