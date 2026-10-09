# Independent cleanup QA — 7 October 2026

**Computational audit: PASS.** The final cleanup is a reversible, source-reviewed candidate. This audit does **not** certify every retained point as plant tissue, plant completeness, accepted trait segmentation, or physical measurement accuracy.

The audited classification is `../result/point_classification.npz`, SHA-256 `ca2af9922994117cc8068169ac8bdf91b0b84d7792b7f75bb6dc0df628789fcb`.

## Complete point and provenance checks

All 1,732,490 original fused input points are assigned to exactly one output pool:

| Pool | Points |
| --- | ---: |
| Primary plant candidates | 435,917 |
| Uncertain review pool | 603,740 |
| Unassigned scene context | 692,833 |
| Total | 1,732,490 |

Primary candidates contain P1 21,891; P2 74,306; P3 113,901; P4 69,634; and P5 156,185 points. The five plant sets are disjoint and their union exactly equals the primary pool.

All 67 integrity checks pass. The audit compared **every binary vertex record** in each reference-coordinate output with its indexed original fused record, including coordinates, normals, and RGB values. No vertex was moved, recoloured, or fabricated in these reference outputs. Every per-output fused index, camera identifier, and original point index matches its original provenance. The original fusion hash still matches the recorded input. All 39 input-manifest entries, 19 output-manifest entries, and the 15 reviewed source-image hashes match.

No assigned point has competing clear-positive evidence for multiple plants. No assigned point has a source nonplant veto, lies below its own recorded basal floor, or lacks a positive source observation. Each core point has at least two clear-positive observations. Every extension is within the recorded 4 mm distance of its own unambiguous core, has positive source evidence, and has no competing plant positives. No extension resolves a multiple-core ownership conflict.

These checks apply to the reference-coordinate outputs. The separate upright and orange uncertainty display products deliberately transform coordinates or override display colours; they are not the byte-preserved reference outputs.

## Projection and visibility replay

A separate audit used inverse world-to-camera matrices and direct OpenCV projections without the cleanup projection helper. Full-cloud depth buffers were rebuilt for the 15 reviewed views. A deterministic sample of 29,596 points was stratified by camera origin, output reason, and plant label.

The replay exactly matches saved positive, uncertain, nonplant, and visible vote counts for every sampled point: **zero mismatches in all four arrays**. All selected exact ICP rotations pass rigidity checks. Native distorted RGB coordinates are used for polygons; ideal pinhole coordinates separately query the cached undistorted stereo depth. Behind-surface evidence is removed from positive/negative voting, and explicit negative evidence additionally requires stereo-depth agreement.

The implementation intentionally permits a source-envelope-positive, depth-buffer-visible point without stereo-depth agreement in that view. The sample contains 9,953 such observations out of 37,075 positive point-view observations; these are observations, not unique points. Missing or disagreeing stereo support therefore does not itself certify material identity. This remains a semantic limitation rather than a projection-replay failure.

## Source and decision review

The independent visual review covered all P3/P4 annotated views, the P1/P2 six-view contact and full-size spot checks, all three P5 raw source images and overlays, and the final narrow-tissue overlays for P1/P2/P3/P4. P5's two small central-junction overrides were checked against enlarged raw crops. No gross plant-identity swap or systematic exclusion of pale, brown, or yellow organs was found in that scope.

The review caught a P3 pot-exclusion polygon overlapping green tissue. Its corrected replacement was checked against the original image. A tiny ambiguous second P3 exclusion was removed. The draft extension rule could assign four points with two qualifying plant cores; the final classifier now withholds every point with clear-positive observations for multiple plants before both core selection and extension. All final clear-positive cross-plant assignments are zero.

Narrow `clear_tissue_polygons` override only their own view's broad uncertainty; they do not override explicit nonplant evidence. Broad uncertain-envelope hits may be resolved by clearer observations elsewhere. This is appropriate because those broad regions include overlapping projections, but it does not establish complete anatomical ownership. P5's pale left foliage and P4 overlap remain explicitly uncertain. Source annotations use observed pixels, not manual trait dimensions, colour-only segmentation, or morphological completion.

The original, cleaned, uncertainty-overlay, and P5 static front previews were inspected. The primary preview visibly separates much of the pot/scene geometry and retains differently coloured foliage, but it remains incomplete and contains disconnected fragments. The uncertainty overlay contains both possible plant tissue and nonplant surfaces. Those pools must accompany any interpretation of missing or ambiguous structures. Static front views do not validate all surfaces or quantify segmentation accuracy.

## Evidence and scope

- `partition_audit_final.json`: complete-record integrity checks and final manifests.
- `projection_audit_final.json`: sampled independent projection/vote replay and per-view observations.
- `projection_audit_final_sample.npz`: reproducible sampled fused indices and replayed vote arrays.
- `audit_partition.py` and `audit_projection.py`: reusable audit programs; outputs are confined to this QA directory.
- `../../source_review/p5/P5_source_review.json`: P5 coordinates, exact-frame/source hashes, masks, and known limitations.

This evidence establishes point preservation, exact partitioning, provenance consistency, implemented visibility conventions, and the stated decision invariants. It does not establish ground-truth tissue purity, complete leaves/stems, independently calibrated metric scale, or validated physical traits. No unrelated reconstruction was rerun for this audit.
