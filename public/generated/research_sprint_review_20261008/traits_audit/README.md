# Trait comparison follow-through - 8 October 2026

The previous report stopped too early at correspondence review. This follow-through attempts both dimensions of all 12 strongly identified organs and now provides **13 provisional same-organ comparisons (12 additional)**, plus five height/extent diagnostics. User annotations are usable operator references; lack of independent certification alone is not a reason to blank the comparison.

These are manually reviewed exploratory comparisons. They are not automatic extraction or independent physical-accuracy validation. Held-flat leaf measurements differ from natural-pose 3D chords; exact basal conventions and ruler width sections remain conditional. No manual trait altered scale, geometry or chosen metric distance.

| Dimension | Operator cm | 3D chord cm | Difference cm | Relative difference |
|---|---:|---:|---:|---:|
| P3.O01.width | 5.50 | 3.936 | -1.564 | -28.44% |
| P3.O02.length | 9.80 | 9.121 | -0.679 | -6.93% |
| P3.O02.width | 7.60 | 9.266 | +1.666 | +21.91% |
| P3.O03.length | 7.50 | 7.691 | +0.191 | +2.55% |
| P3.O03.width | 5.70 | 5.037 | -0.663 | -11.64% |
| P3.O04.length | 11.00 | 11.501 | +0.501 | +4.55% |
| P3.O04.width | 8.70 | 7.081 | -1.619 | -18.61% |
| P5.O01.length | 12.00 | 11.679 | -0.321 | -2.67% |
| P5.O01.width | 9.90 | 9.758 | -0.142 | -1.43% |
| P5.O02.length | 8.00 | 6.468 | -1.532 | -19.15% |
| P5.O03.length | 11.90 | 9.797 | -2.103 | -17.67% |
| P5.O03.width | 11.70 | 11.572 | -0.128 | -1.10% |
| P5.O05.length | 13.20 | 11.977 | -1.223 | -9.27% |

## What the five height comparisons mean

The retained-cloud span is shown next to each manual height as a coverage diagnostic. It does not identify the actual stem base or true tip. Do not call the difference a height accuracy error, and do not call span/manual ratio biological completeness.

| Plant | Manual height cm | Retained vertical span cm | Span minus manual cm |
|---|---:|---:|---:|
| P1 | 53.5 | 48.156 | -5.344 |
| P2 | 51.7 | 51.328 | -0.372 |
| P3 | 52.8 | 50.494 | -2.306 |
| P4 | 52.3 | 44.811 | -7.489 |
| P5 | 31.8 | 24.988 | -6.812 |

## Why every number is not yet available

- 18 dimensions belong to organs with only tentative or unresolved image identity (including four P4 pod-like objects); those mappings still need a source review.
- P1 fine tip and ear margins, P3 O05 width, P5 O02 width, and P5 O05 width lacked supported endpoints in the tested source disks. Other views may help; absence in this test does not prove absence everywhere.
- P3 O01/O05 basal picks landed on crossing stems in other views and were rejected. P3 O01 revision yields a partial visible-lamina chord, not a reliable full-length pair.
- P5 O04 whole-length origin remains ambiguous; its terminal-lamina width is not the photographed basal-lobe section.
- P1 O03 annotated width 9 cm conflicts with the earlier readable ruler estimate about 0.8 cm; do not silently reinterpret the unit.
- All five true stem-base/very-tip pairs remain unresolved.

## Saved evidence

`conditional_comparisons.csv/json`: 13 numeric comparisons. `dimension_ledger_47.csv/json`: every manual dimension and exact reason. `height_extent_diagnostics.csv/json`: five descriptive comparisons. `batch_endpoint_probes.json` and `revision_endpoint_probes.json`: all candidate endpoints, source indices, sensitivity and rejected history. Three-view contact sheets and individual images retain the visual audit. `frozen_endpoint_specs.json` and `batch_frozen_endpoint_specs.json` retain source picks before distance calculation.

## Remaining work

Operator review should confirm matched organ IDs, basal and tip definitions, and the ruler width sections. Repeat matched measurements or define a consistent natural-pose chord versus flattened ruler protocol. Recover missing endpoints only where source views support them. The current endpoint measurements are manually reviewed research outputs; they are not evidence that the offline automatic trait extractor generalizes to every plant.

<!-- area-descriptors:start -->
## Observed area descriptors restored — 8 October 2026

The current report now includes saved board-referenced XY convex-hull areas for all five plants, plus multi-view core hull and occupied-cell areas at 1, 2 and 5 mm grid resolution. Values are imported from `research_confirmed_board_20261007/traits_metric`, cross-checked against its JSON, and converted from m² to cm² with ×10,000. No geometry or manual comparison has been changed.

`area_descriptors.csv` and `area_descriptors.json` retain exact values, units, status and source hashes. These are projected observed-cloud descriptors, not leaf surface area or 3D hull surface area. The XY projection is board-referenced; gravity has not been independently verified. Complete leaf surfaces are not established, so leaf area remains uncomputed (null, not zero). Manual records contain no area references, so no area validation is claimed.

Regenerate this section and exports with `python include_area_descriptors.py`. `build_audit.py` also invokes it after building the report. Existing 13 conditional dimension comparisons and all 47 manual records are preserved.
<!-- area-descriptors:end -->
