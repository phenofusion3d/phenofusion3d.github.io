# Manual reference inventory — 28 September 2026 capture

Inspected and transcribed on **7 October 2026 (Australia/Sydney)**. These are source measurements and readiness findings, not reconstruction results or validated error scores.

## Evidence and provenance

The evidence is under `data/main/test_plant_10-7/manual_validation_5-plants_28-09/`: **74 images**, consisting of **9 annotated overview images and 65 supporting photographs**. There are **5 annotated heights and 21 organ length/width pairs**, giving **47 numeric measurements**. No original spreadsheet, CSV, or written measurement protocol was found in that directory.

`manual_reference_inventory.json` records every source image's relative path, byte count, pixel dimensions and SHA256. Paths in the JSON are relative to `data/main/test_plant_10-7/`. Its annotation identifiers such as `P3.O01` are stable transcription IDs; they do not assert that a particular numbered leaf folder or reconstructed component has already been matched.

The source image for plant 1 is `plant-1_measurements.jpeg`. For plants 2–5, organ annotations are in `plant-N_measurements_01.png`, and whole heights are in `plant-N_measurements_02.png`. Supporting photograph counts by folder are 10, 9, 18, 14 and 14. Plants 2–5 have supporting whole-height ruler photographs. Individual ruler photographs and overview arrows provide evidence for future physical leaf matching.

## Values transcribed verbatim

All numbers below retain the **cm units shown in the annotated images**. The order of organ pairs matches the stable IDs in the JSON, not automatic segmentation order.

| Source specimen | Whole height, cm | Organ length × width, cm |
| --- | ---: | --- |
| plant-1 | 53.5 | 12.5 × 1; 10.9 × 1; 7.3 × **9**; ear 6.5 × 1.6 |
| plant-2 | 51.7 | 5 × 2.7; 3.9 × 3.4 |
| plant-3 | 52.8 | 7.4 × 5.5; 9.8 × 7.6; 7.5 × 5.7; 11 × 8.7; 9.2 × 7.7; 7.5 × 6.3 |
| plant-4 | 52.3 | 3 × 0.2; 2.8 × 0.5; 2.9 × 0.3; 2.9 × 0.4 |
| plant-5 | 31.8 | 12 × 9.9; 8 × 4.8; 11.9 × 11.7; 12.9 × 9; 13.2 × 7.8 |

## User clarification about height and units

The user clarified that whole height was measured **from the stem base to the very tip of the plant**, using **two rulers**. Their phrase "step base" is interpreted here as stem base. The user also states that the annotations are in **centimetres**, not millimetres. All five recorded heights and all original organ numbers remain unchanged. The height endpoint convention is therefore recorded as user-specified; the two-ruler joining/offset and measurement uncertainty have not been independently reconstructed.

This clarification does not apply a factor-of-ten conversion to any measurement. The specific P1 width conflict described below remains unresolved.

## Ambiguities requiring resolution

1. **P1.O03 upper blade width:** the overview says `Width:9cm`, and the user states the annotations are in centimetres. The original ruler photograph `plant-1/Media (6).jpeg` was re-inspected at original resolution. Its major labels **1, 2 and 3 are centimetres**, with ten small millimetre subdivisions between adjacent centimetre marks. The blade above the ruler spans approximately **one major centimetre interval**, rather than nine such intervals. That is visual evidence of a conflict for this particular width; it does not imply that all annotations were in millimetres. **0.9 cm remains a proposed explanation only**: the exact correction and whether the photographed section represents maximum width are unconfirmed. The JSON preserves **9 cm**, marks the issue `needs_confirmation`, and explicitly excludes this width from numeric accuracy statistics until resolved.
2. **P1.O04 is a cereal ear**, so its 6.5 × 1.6 cm measurement belongs to a separate organ trait rather than ordinary leaf statistics.
3. **P4.O01–P4.O04 have uncertain organ identity.** The folders are named `Leaf-1` through `Leaf-4`, but close-up photographs show very narrow structures among flowers and pods; several resemble pods. Preserve the source values while reviewing their botanical identity. No exact correspondence from those folder numbers to overview-arrow IDs is asserted here.
4. **Whole-height endpoints have now been clarified by the user:** stem base to the very tip of the plant, using two rulers. This is separate from the P1 leaf-width issue. The original centimetre values remain 53.5, 51.7, 52.8, 52.3 and 31.8. Two-ruler joining/offset, measurement uncertainty and exact endpoint correspondence in each reconstructed plant still need to be documented for reproducible scoring.
5. **Length and width definitions are unknown.** Record whether length is straight base-to-tip, curved surface length, or a flattened manual measurement, and how maximum width was selected. Some photographs show leaves held beside a ruler, which can change their shape relative to the capture.
6. **Physical matching is unfinished.** Match specimen identity and each measured organ to particular RGB views and reconstructed points. Do not compare arbitrary leaf ordering, largest leaves, or automatically assigned component numbers against the manual folder order.

## Tentative D405 correspondence

The sampled D405 plant recording contains the same five distinctive specimen morphologies along the scan: cereal, two taller broad-leaf specimens, yellow-flowering specimen, then the shorter broad/brown-leaf specimen. The following are **candidate review frames only**; multiple plants may appear in a frame, and no leaf-to-component matching is established.

| Reference specimen | Candidate frame in `test_plant_20260928162354/` |
| --- | --- |
| plant-1 | `rgb_0.png` |
| plant-2 | `rgb_425109.png` |
| plant-3 | `rgb_631832.png` |
| plant-4 | `rgb_1034629.png` |
| plant-5 | `rgb_1441230.png` |

Candidate frame hashes are stored in the JSON. Species names have not been confirmed from this inventory.

## Independent validation policy

**All manual measurements are held out from camera calibration, depth-scale estimation, reconstruction tuning and spectral-registration tuning.** First establish calibration from independent targets and capture metadata, freeze processing choices and the measurement convention, then use these manual values for comparison.

Record unresolved units, uncertain organ type, occlusion, missing endpoints and unmatched identity as explicit exclusions with reasons. Do not invent geometry or endpoints to obtain a complete score table. Once matching is defensible, report individual errors and specimen-level summaries; correlated leaves from one plant should not be treated as independent plants.

The photographs provide useful ruler evidence, but no repeat-measurement protocol or uncertainty record is supplied. Five plants support a descriptive assessment of this batch; they do not by themselves demonstrate generalisation across species or datasets.

The raw images and application source were left unchanged. This inventory is reproducible against the recorded hashes and remains separate from the unresolved physical checkerboard dimensions.
