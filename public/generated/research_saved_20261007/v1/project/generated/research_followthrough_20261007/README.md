# Five-plant research continuation — 7 October 2026

Open `index.html` for the assembled results. This separate folder preserves the earlier camera reconstructions, RGB-D fusion and cleanup results through links; those source products are not overwritten.

## Completed with the available evidence

| Stage | Saved result | Interpretation |
|---|---|---|
| Specimen/organ review | `traits/index.html` | Five specimen identities; 12 supported, three tentative and six unresolved organ matches. |
| Manual evidence disposition | `traits/manual_dimension_disposition.csv` | All 47 dimensions retained with evidence class, conflicts and exclusion reasons. |
| Observed geometry | `workspace_v2/observed_descriptors.json` | Distribution of retained tissue points for five plants; not anatomical height or complete area/volume. |
| Exact observed distances | `workspace_v2/measurements.json` | Three source-indexed chords: P1 partial blade, P3 candidate blade and P5 terminal lamina. All use conditional coordinate units. |
| Hyperspectral review | `spectral/index.html` | 13,343 measured source-pixel spectra across 224 bands, 24 reviewed patches and quality flags. Scan-order regions are not confirmed 3D plant/organ identities. |
| Spectral projection preparation | `spectral/mapping_workspace/` | 205 existing planar observations, explicit missing calibration and a blank shared-3D-control template. |
| Offline software | Repository `processing/research_workspace/` and `app/analysis_dialog.py` | Configurable saved-cloud report, exact-point endpoint review, measured spectra processing and guarded report launch. No AI service required to execute these tools. Reviewed selections remain inputs. |
| Reusable spectral replay | `spectral_extraction_v1/fx10/result/index.html` and `spectral_extraction_v1/fx17/result/index.html` | Tracked offline extractor exactly reproduced all 13,343 full spectra, Q/Q0 and quality flags, plus all six available FX10 descriptors. |

`workspace_manifest.json` links the preserved geometry and research stages. `workspace_endpoints.json` imports the three source-supported observed distances. Rebuild into a fresh folder; the frozen `workspace_v1` development report is superseded by `workspace_v2` for presentation, with the same scientific measurements. A saved manifest snapshot uses absolute local paths and cloud hashes so it can be rerun on this machine. Reports are not self-contained portable bundles: keep their linked inputs or adjust paths explicitly on another machine.

## Still unresolved

The user cannot currently supply the printed ChArUco pitch or independent recording units. These are recorded in `gaps.json` and the tracked repository ledger `docs/RESEARCH_GAPS_20260928.md`; no guessed pitch is silently accepted. Scale is not fitted to the plant validation measurements.

True stem bases/highest tips and several organ boundaries remain obscured or incompletely reconstructed. There are **no eligible final physical accuracy pairs**. P3's close match to an operator-only 7.5 cm note is explicitly provisional: endpoint sensitivity spans about 6.71–8.42 cm, and the anatomical boundary convention remains tentative. It is not an accuracy result.

The white-board spectrum and shutter-closed dark reference are unknown. Normalized spectra and indices are exploratory. Table-plane agreement does not identify height-dependent HSI projection; off-plane spatial/rig evidence, line linkage and visibility validation are still missing. **Calibrated 3D spectral surface fusion has not been achieved.** No spectra are fabricated on unmapped leaves.

Whole-plant gap-free coverage, arbitrary-dataset automation and physical lab operation are not established by these software checks. Additional capture or independent evidence is needed for those claims.

## Verification

- `release_tests.xml`: **141 passing tests**, zero failures/errors/skips in the final combined run.
- `release_verification.json`: final source hashes, protected-file check, package discovery, browser/Qt checks and remaining physical limitations.
- `spectral_extraction_v1/parity_validation.json`: exact full-data replay comparisons for both HSI cameras.
- `test_results.xml`: 128 passing relevant offline tests at the assembled-workspace checkpoint.
- `final_changed_tests.xml`: subsequent focused checks after the viewer and presentation changes.
- `browser_endpoint_verification.json`: real browser selection/export, original source-hash verification and unreviewed measurement calculation. These arbitrary UI test picks are not scientific trait observations.
- `integration_audit/final_workspace_v2_verification.json`: report assets, input hashes, package discovery and protected-file checks.
- `traits/verification.json`, `spectral/deliverable_validation.json`: scientific-product verification.

The code changes are local. This continuation does not push, deploy or certify lab hardware operation.
