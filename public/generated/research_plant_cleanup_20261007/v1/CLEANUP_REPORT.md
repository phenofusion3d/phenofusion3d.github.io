# D405 + L515: reversible plant cleanup candidate

Recordings: 28 September 2026. Processing: 7 October 2026.

## Result and status

The existing fusion has been separated into five specimen selections, an uncertain review pool and remaining scene context. The primary plant candidates contain **435,917 observed points**. **603,740 points** remain in the uncertainty pool and **692,833** in the scene-context output. These three disjoint outputs account for all **1,732,490 input points**.

This is an assistant source-reviewed research segmentation candidate. It is not confirmed tissue ground truth, a complete plant, or a validated trait mask. A cleaner appearance does not establish greater dimensional accuracy. True basal tissue, poorly seen edges and overlapping leaves may be absent from the primary selection and remain in the other outputs.

[Open the interactive comparison](review/index.html) · [All 15 annotated source views](review/source_review.html) · [Machine-readable summary](result/summary.json) · [Independent verification](qa/INDEPENDENT_CLEANUP_QA.md)

| Specimen | Selected points | Multiple-view core | One-view nearby edge | D405 origin | L515 origin |
|---|---:|---:|---:|---:|---:|
| P1 | 21,891 | 12,089 | 9,802 | 21,891 | 0 |
| P2 | 74,306 | 50,252 | 24,054 | 74,240 | 66 |
| P3 | 113,901 | 85,055 | 28,846 | 113,061 | 840 |
| P4 | 69,634 | 41,137 | 28,497 | 69,560 | 74 |
| P5 | 156,185 | 121,810 | 34,375 | 154,991 | 1,194 |

Point counts describe selection and sampling density, not percentage completeness or biological accuracy. The edge category is lower-confidence than the multiple-view core.

## Source evidence and classification

1. Start with the frozen `fused_review_reference.ply` from the separate fusion run. D405 geometry and selected, rigidly aligned L515 additions have already been fused. Cleanup does not recalculate alignment, average camera coordinates or generate geometry.
2. Review three recorded native D405 RGB images for each specimen (15 specimen-view records; 14 distinct frames). Save visible plant-envelope polygons, small exposed nonplant examples and explicit ambiguity polygons. Traced clear-tissue polygons can resolve a broad ambiguity envelope only for narrowly identifiable stems or petals. These masks are approximate and dataset-specific, not operator-confirmed ground truth. Pale, dry, red/brown and yellow tissue is eligible; there is no green-only filter.
3. Project existing points using the **final accepted per-frame ICP camera-to-reference transformations**, the recorded camera matrix and native distortion. Guard the calibrated ray domain before distortion so off-axis rays cannot fold into the image. Source-mask authors checked the exact bundle frames; classification uses their corresponding final ICP transformations without pose interpolation.
4. A full fused-cloud depth buffer, with a one-pixel neighbourhood and 10 mm depth tolerance, suppresses self-occluded points. Supported stereo depths from the same exact frames provide an additional 12 mm occlusion check. Native distorted mask coordinates and undistorted stereo-raster coordinates are computed separately. Missing depth abstains; it does not establish absence. A nonplant veto additionally requires supported stereo depth agreement within 12 mm. These distances inherit the conditional scale and are algorithm thresholds, not measured errors.
5. Primary core points need at least two visible positive masks for one specimen, no explicit nonplant veto, no positive evidence for another specimen and a position above that specimen's approximate basal band. Two clear observations can resolve an ambiguous envelope in another view; ambiguity alone does not prove another specimen's identity. A two-pixel exterior mask boundary remains uncertain.
6. An existing point with at least one positive mask may join the same specimen if it is within 4 mm of its primary core, above the basal band and has no competing clear assignment or nonplant veto. This is a one-step selection of existing vertices, not interpolation, hole filling or recursive expansion. No largest-cluster rule or small-component deletion is used.
7. All remaining points with positive or uncertain source-mask evidence stay in the separate uncertainty pool. The rest are scene context; unreviewed context is not asserted to be noise. No original point is discarded from the complete partition.

## Basal boundary and research limits

Reviewed soil-patch seeds identify neighbourhoods; they are not measured stem bases. The provisional upright cut is soil-seed Z +15 mm for P2–P5 and +25 mm for P1. An independent P1 source-labelled soil check showed that +15 mm retained soil. The final cut values are saved in `result/summary.json`. Source-supported points below the cuts remain uncertain. **Do not measure plant height from these cuts.** No manually measured height, leaf length or width was used to choose geometry or scale.

Masks trace photographs from a translating camera and do not certify hidden undersides or a full 360-degree surface. Thin stems, motion, occlusion, projection uncertainty and prior fusion coverage cause gaps. The input itself is a review-region crop; this cleanup cannot recover surfaces excluded earlier or never recorded. Broader masks can contain internal background gaps even after the visible-source checks.

Physical checkerboard dimensions and absolute camera scale remain unverified. The earlier D405/L515 alignment was an empirical rigid surface alignment, not a certified physical camera extrinsic. L515-only additions inherit their previous evidence limits. For paper-ready traits, confirm specimen/organ correspondence, actual stem-base/tip definitions, physical calibration and the manual measurements independently. Do not use the manual measurements to tune segmentation or rescale the reconstruction and then present them as held-out validation.

## Files and coordinates

- `result/P1_reference.ply` through `P5_reference.ply`: exact original binary vertex records selected for each specimen, in the D405 reference camera frame. Positions, colours and any normals are copied without modification.
- `result/plants_cleaned_reference.ply`, `uncertain_reference.ply`, `scene_context_reference.ply`: the full disjoint partition. Every file has a matching provenance archive with original fused index, camera ID and original camera-cloud index.
- `result/point_classification.npz`: all input points in original order, final specimen ID, reason code, positive/uncertain/nonplant/visible-view counts, camera ID and original point index. Camera 0 is D405; camera 1 is L515.
- `review/*_upright.ply`: viewer/download copies rotated into the same saved upright coordinate frame, with no translation or scale change. The orange uncertainty overlay intentionally replaces colours for visual review only; original RGB remains in `result/uncertain_reference.ply`.
- `review/index.html`: full-resolution offline WebGL viewer. Before/after and uncertainty share a display centre and scale. Individual specimens are fitted more closely for display; downloads still use the common upright frame. Point-size and brightness controls change appearance only.
- `source_review/`: native-image annotations, editable polygon coordinates and the evidence used to select them. `input_hashes.json`, `output_hashes.json` and `review_provenance.json` provide reproducibility records.

## Verification and reproducibility

The independent audit checks exact vertex-record preservation, complete disjoint partition, per-plant union, camera/original-index mapping, unique clear ownership, selection thresholds and input/output hashes. Its current results are in `qa/INDEPENDENT_CLEANUP_QA.md`. Viewer packaging and HTTP/browser behaviour are checked separately. These are computational checks, not physical or biological validation.

Run from the repository root with the existing research Python environment and NumPy, SciPy, OpenCV and Open3D available:

```text
python generated/research_plant_cleanup_20261007/cleanup.py
python generated/research_plant_cleanup_20261007/package_review.py
python generated/research_plant_cleanup_20261007/write_report.py
python generated/research_plant_cleanup_20261007/v1/qa/audit_partition.py
```

The scripts only write under this separate research directory. Reproduction uses these reviewed masks and dataset paths; **this cleanup has not been integrated into the offline general-purpose application**. Working capture, gantry control and `main.py` are untouched. Original D405, L515 and fusion results remain available separately. Hyperspectral mapping and trait validation are subsequent stages.
