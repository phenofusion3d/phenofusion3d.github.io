# Frozen source visibility review

This review uses original RGB images only. It does not use manual ruler dimensions, reconstruction output, new probe scores, or trait-based crops to choose samples. These are assistant annotations awaiting operator confirmation, not human-confirmed ground truth.

`source_visibility_review.json` contains 37 small annotations across 10 exact accepted bundle frames: **27 visible plant-surface samples and 10 neighboring board samples**. All five requested dense probe anchors are included: 275384, 487431, 799028, 1055904 and 1420709. Individual and aggregate PNG masks are native distorted 1280×720 RGB pixels, with source hashes and a separate ±3-pixel boundary-localization band. Use nearest-neighbor remapping for masks when comparing undistorted stereo caches. Zero label means unassessed, not background.

The original views and every source/trace pair were inspected. The `P1` through `P5_mask_source_QA.jpg` sheets show source crops beside traces. Larger original-view annotations and coordinate crops are also saved. Samples are deliberately small visible interiors/centrelines; they do not define whole plants, leaf endpoints, maximum widths or hidden surfaces. The P4 flower sample regions include a little adjacent green pedicel tissue: interpret them as floral plant-surface samples, not petal-only masks.

## Visible targets and acquisition limits

| Specimen | Source evidence worth recovering | Limits |
| --- | --- | --- |
| P1 | Textured ear body and pale dry strips across 197108, 222952, 249551 and 275384 | Fine awns are blurred and very thin. Repeated grains make precise point identity difficult. Hidden stem/soil junctions and back surfaces are unobserved. |
| P2 | Exposed curved upper stem and broad/narrow leaf faces at 487431; neighboring source views 433466 and 459309 were also visually checked | Lower tangled canopy is partly occluded; complete branch ownership is not established. |
| P3 | Exposed lower main stem and separated leaf faces at 799028; source views 696431 and 721510 also show these kinds of structures | Leaf backs and covered junctions cannot be inferred from the overhead sweep. |
| P4 | Upper arched branch and upright flower stalk clearly track through 1003470, 1030829 and 1055904; several distinct buds/flowers are visible | Thin crossing stems, petals and hidden bases remain difficult; some apparent junctions become occluded. |
| P5 | Textured green and brown leaf controls plus an exposed stem above the pot at 1420709 | Whole-plant separation and overlap ownership remain unconfirmed. |

Neighboring reviewed P1 views span about 25.4–26.6 mm camera translation per step; the P4 sequence spans about 25.4–28.1 mm per step according to the existing bundle. These are conditional bundle-derived distances, not ruler-validated calibration. The repeated visible ear/branch structures make those short baselines useful tests of matching and support. Visibility in RGB alone does not guarantee recoverable metric geometry.

## Depth-aware conditional landmarks

`conditional_landmark_depth_review.json` freezes six candidate tracks with native image coordinates and ±3 px localization uncertainty. Three P4 tracks are accepted only as **conditional evaluation landmarks**. They use the frozen factory colour intrinsics/distortion and exact bundle poses; poses and scale were not optimized. Two-view triangulation predicts the held-out third view. All three source patches for each accepted landmark were visually checked in saved panels.

| Accepted P4 landmark | Frame 1055904 native pixel | Conditional camera depth | Pixel-only 95% interval | Largest held-out error |
| --- | --- | ---: | ---: | ---: |
| Isolated hanging bud | (637,342) | 0.19418 m | 0.18911–0.19941 m | 3.46 px |
| Left yellow flower petal junction | (483,464) | 0.20579 m | 0.20018–0.21154 m | 2.23 px |
| Right yellow flower petal junction | (661,485) | 0.25235 m | 0.24381–0.26140 m | 1.56 px |

The JSON includes central reference-frame 3D coordinates, per-frame depth intervals, full sampled extrema, reprojection errors and source hashes. Intervals come from 2,000 uniform pixel perturbations. They **exclude** pose, distortion, motion and scale errors and share the camera model with reconstruction; they are not independent metric ground truth.

Three candidates are excluded from primary depth-aware scoring despite numerical fits: the P1 pale grain has repeated-structure ambiguity, the P4 side-leaf tip overlaps the upper branch in the last view, and its junction is partly obscured by the hanging bud. These excluded records and panels remain as evidence; no correspondence was forced to satisfy the requested count.

## Fair old/new comparison

Keep these masks fixed for both outputs, using the same raster, projection, visibility and splat policy. Report foreground samples and board samples separately. Exclude the uncertain boundary band from primary counts and retain its sensitivity separately.

Projected occupancy on a stem pixel is not enough: a board behind the missing stem can occupy the same ray. Conversely, a board point is correct in a full-scene reconstruction and is not a false surface merely because it projects into a background mask. The accepted landmark depths can distinguish nearby plant surfaces from far background locally; do not extend one landmark's depth across an entire ROI.

These annotations support coverage and consistency comparisons. They do not establish absolute reconstruction accuracy, complete 360-degree coverage, a gap-free plant, accepted trait validation or a proven specimen segmentation. Original sensor data and application files remain unchanged.
