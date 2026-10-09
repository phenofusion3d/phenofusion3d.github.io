# Five-plant reconstruction: gaps and controlled improvements

Research review, 7 October 2026. Dataset: D405 plant recording `test_plant_20260928162354`.

The gaps in the earlier viewer are real gaps in the reconstructed surface. They are not simply an upside-down display or a poor choice of viewing angle. The earlier result should not be treated as the best reconstruction achievable from these data. This review found a reproducible filtering defect and complementary stereo evidence. None of the candidates establishes a complete, metrically validated 360-degree plant.

## What was found

The RGB reconstruction was using raw sensor-depth validity to decide which RGB-derived depths could count as foreground support. A surface with repeatable RGB depth could therefore be rejected when the sensor had a hole at the same pixel. Across the original 32 dense views, this veto removed **491,839 of 4,995,895** otherwise repeated, in-range RGB pixel-view candidates: **9.845%**. These counts include pots and background, repeated observations of the same surface and possibly incorrect depths. They are not a percentage of missing plant geometry.

The effect occurs principally during support checking. The original TSDF integration already used a wide dilation around the masks. Removing the veto adds only 4,192 depth pixels to TSDF integration, while restoring many more potential support votes. It would be incorrect to say all 491,839 discarded candidates were absent from TSDF.

The original stereo view selection also used a whole-scene representative distance. Closer view pairs provide better local evidence for some exposed stems and arches. They are not universally better: one isolated P4 bud has stronger conditional depth evidence in the original pair set. Replacing all original pairs without checking those losses would discard useful observations.

The standalone sensor-depth audit does not solve the gaps. P1 remains disconnected under strict consistency checks. The isolated P4 bud has zero sensor depth at its annotated centre in all three checked images. Nearby flower junctions have some repeatable sensor support. Sensor candidates are retained separately and have not been blended into the presented RGB clouds.

A second confirmed software loss occurs during generic statistical outlier removal. Eight supported points near the conditional P4 bud landmark pass three supporting views with zero conflicts, survive TSDF, and have projections consistent with the pale bud in the source photographs. The statistical filter removes all eight. Their nearest conditional-landmark distance changes from 0.578 mm before cleanup to 8.013 mm after it. This is source-correlated evidence for a real small patch, not an independent accuracy measurement. The exact rejected indices and source projections are saved in [the stage trace](sensor_audit/p4_stereo_stage_trace/original32_roi.md).

P1 has a different failure. In one frozen green-attachment sample, there are 13 finite depth estimates but zero pixels with the required two-pair agreement, so that local gap already exists before fusion. In the adjacent dry-strip sample, 124 original stereo observations pass the multi-view gate and all have a supported surface neighbour within 6 mm. However, only 30 of those 124 reproject into the other frozen strip sample even with its uncertainty band (21 inside its primary mask). They cannot all be called recovered strip geometry; background or other surfaces may contribute. Disabling cleanup alone cannot reconstruct the missing attachment.

## Controlled results

Four scene reconstructions and two preserved processing checkpoints are compared using identical camera orientation, upright transform, review bounds, display scale, sampling stride and point size:

1. **Earlier result:** 32 original dense views, original pair selection and sensor-dependent mask.
2. **Filtering fix only:** exactly the same 32 depth maps, RGB arrays, pair votes and saved accepted ICP transforms. Only the sensor-dependent mask is replaced by the valid RGB image footprint with the existing depth-range and pair-vote checks.
3. **Filtering fix: before cleanup:** the filtering fix's checkpoint before statistical outlier removal. It retains every surface fragment that passed the same multi-view support and conflict checks. This helps inspect what generic cleanup removes, and may include noise.
4. **Closer-view trial:** all 64 frozen bundle camera poses become dense anchors, each with six nearby translated views and the corrected mask. ICP is rerun and checked using the existing acceptance rules.
5. **Combined pairs: after cleanup:** all 32 original anchors use the reviewed conservative complementary-pair rule described below, followed by the same saved camera alignment, fusion and statistical cleanup. All old image-valid accepted depths are preserved, with 408,864 added whole-frame candidate pixels. Shared pair maps match exactly and duplicate targets count once.
6. **Combined pairs: fine fragments retained:** the combined result before statistical cleanup. This is an inspectable research candidate, preserving small supported fragments rather than deleting them solely because of their local density. It also retains potentially incorrect fragments and does not establish every new connection as plant tissue.

All retain the same 1 mm TSDF voxel, 5 mm truncation, minimum three distinct supporting anchors, 6 mm visibility agreement and original free-space conflict rule. All except the explicitly labelled checkpoints also apply the same statistical cleanup. Component-size deletion is disabled throughout. No manual plant dimensions, learned shape completion or invented surfaces are used.

| Result | Dense anchors | Full scene points | Common review crop points |
| --- | ---: | ---: | ---: |
| Earlier result | 32 | 3,468,158 | 924,874 |
| Filtering fix only | 32 | 3,960,257 | 1,026,440 |
| Filtering fix: before cleanup | 32 | 4,092,685 | 1,061,410 |
| Closer-view trial | 64 | 8,265,080 | 1,719,001 |
| Combined pairs: after cleanup | 32 | 4,159,263 | 1,104,454 |
| Combined pairs: fine fragments retained | 32 | 4,303,406 | 1,143,063 |

The common crop contains pots and background. The 64-view result also gives denser observations of already represented surfaces; its larger point count is not a completeness percentage. The interactive viewer displays every second vertex from each crop, with the same scale and point size. Downloads retain every crop point; the fixed-source audits use full source clouds.

The viewer opens on **Closer-view trial** as the preferred candidate for inspection after reviewing all completed results. Its 64 views produce more continuous visible stem/leaf fragments, particularly in P4, than either the earlier result or the conservative 32-view combination. All 64 camera alignments passed the existing acceptance gate; retained points have at least three supporting views (median seven). Substantial gaps and uncertain/background fragments remain. This preference is not a claim of globally superior accuracy, complete organ connectivity or an optimum over all methods. The other five outputs remain selectable at the identical camera view.

The full 64-view result recovers the conditional P4 bud despite the single-anchor counterexample in the preliminary pair probe: it has 22 points within 5 mm of that landmark, with nearest distance 0.196 mm. The other two conditional P4 landmark nearest distances are 3.987 and 0.561 mm. These are shared-camera agreement checks, not physical-accuracy scores. They show why a local pair-set regression must be evaluated in the complete multi-anchor result before selecting a final candidate.

The combined result has ten supported points within 2 mm of the conditional P4 bud landmark, with three to five supporting anchors and zero conflicts. Its statistical derivative deletes all ten; the nearest-point distance changes from 0.499 mm to 8.014 mm. The precise removal is verified in `combined_v5/conditional_landmark_stage_review.json`. Those distances are conditional agreement values, not measured reconstruction accuracy.

Review crops include pots and some background; they are not complete specimen segmentations. More scene points or a denser rendering does not establish better plant geometry. Distinct supporting camera IDs are not statistically independent trials because the stereo maps reuse images.

## Local source-image checks

The source reviewer froze 37 annotations across 10 exact camera views before reviewing the new outputs. Five trial anchors contain 15 plant-surface samples and five bare-board controls. Native image masks were remapped using the factory distortion model; uncertain boundaries were excluded from primary counts.

On 8,444 fixed plant-sample pixels, repeated-stereo candidate occupancy was 84.66% for the original gated maps, 87.22% after removing only the sensor veto, 87.73% with shorter pairs but the old veto, and 90.94% with shorter pairs and image validity. Broad, already complete leaves dominate this pooled number. It is **not plant completeness** and does not establish correct depth for each occupied pixel.

Examples with encouraging local depth distributions are the P1 ear, P2 upper curved stem and P4 arch. The P1 dry strip does not gain from shorter pairs alone. P3's lower-stem sample gains a farther-depth tail, so some added pixels may represent background. Bare-board occupancy is reported separately; legitimate board points are not a false-positive rate.

Three source-reviewed P4 landmarks provide conditional depth comparisons. They share camera calibration, pose and scale with reconstruction, and their intervals cover only pixel annotation uncertainty. They are not independent metric ground truth. Ambiguous repeated grains and occluded junctions were excluded instead of choosing whichever correspondence agreed with the output.

## Why P5 looks better, and why some gaps remain

P5 has broad visible leaf surfaces that yield many mutually supporting pixels. The other plants include thinner, low-contrast and partially hidden structures. The source review finds recoverable-looking exposed fragments but cannot establish a continuous visible path through every stem junction. Fine awns, narrow dry threads and some petal edges have too little reliable image evidence for the current matcher and fusion settings.

The camera poses and photographs show predominantly overhead lateral views. The fitted 64 camera centres span about 1.642 m along their main direction, with only about 1.08 mm and 0.43 mm along the other principal directions; the maximum fitted optical-axis difference is 0.326 degrees. These conditional, model-derived values describe an almost straight pass, not a camera orbit. They are not independent metrology, and optical-axis variation is not the full angular range of rays to each plant. See `capture_geometry.json`.

Rotating a 3D viewer exposes areas those cameras did not observe, especially reverse leaf surfaces and hidden junctions. ICP aligns the available geometry; it cannot measure a surface that has no usable observations. Filling such gaps to make a closed model would introduce a shape assumption that must be labelled separately from measurements.

The matcher and TSDF remain possible sources of recoverable loss. The complementary-pair experiment tests one conservative way to use more of the recorded evidence. Simply lowering all consistency thresholds or filling every hole would mix weak and contradictory surfaces into a visually fuller model. These experiments do not establish an optimum over every possible reconstruction method.

A bounded complementary-pair probe preserves old accepted depths exactly and fills only previously empty pixels with at least three distinct agreeing pair observations and no competing mode with at least two pairs more than 10 mm away. It deduplicates target camera IDs. This retains the old bud observation while improving some sampled ear/stem regions. The corrected version passed 37 independent integrity checks; an earlier tied-mode prototype was caught in peer review, preserved as superseded, and not used for a scene result. P1's sampled dry strip gains only five pixels and its attachment remains missing. See [the combined-pair probe review](visual_audit/combined_probe/v2/COMBINED_PROBE_REVIEW.md).

## Better recording for the next experiment

For complete surface coverage, capture each plant from overlapping oblique views around it and at more than one elevation, including views of lower stems and leaf undersides. Keep the plant stationary and control airflow during each sequence. Use sharp frames, stable diffuse lighting and sufficient overlap. This recommendation follows the observed missing directions in this dataset and the general acquisition principles in the [COLMAP tutorial](https://colmap.github.io/tutorial.html): textured images, consistent illumination, overlapping observations and translated viewpoints.

Plan camera-to-surface distances across the whole plant, not only its top. RealSense lists the D405's ideal operating interval as **7–50 cm**; this is an operating-range specification, not a guarantee of millimetre accuracy for every surface. Several deeper scene regions in this recording lie beyond that interval under the current conditional scale. RGB stereo can still produce estimates there, but it does not validate the sensor depths. See the [official D405 specification](https://www.realsenseai.com/products/d405-series/).

Record and verify the printed calibration cell size, camera serials, intrinsics, depth units, colour/depth alignment and actual scan positions. Include a scale object and independent checks distributed through the working volume. For trait validation, retain explicit plant/leaf identifiers and stem-base-to-tip definitions. These checks should evaluate the reconstruction rather than being used to force it to the expected dimensions.

## Evidence and reproducibility

- [Same-view interactive comparison](comparison/index.html)
- [Stage-loss audit](stage_audit/stage_loss_audit.md)
- [Four-way fixed-source stereo comparison](stage_audit/probe_comparison.md)
- [Final-cloud source and landmark checks](final_cloud_audit/final_cloud_comparison.md)
- [Source annotation protocol](visual_audit/README.md)
- [Separate sensor-depth conclusion](sensor_audit/SENSOR_REVIEW_CONCLUSION.md)

All experiments are versioned under `generated/research_20260928_improvement_20261007/`. The previous result is preserved. The application, lab acquisition, camera controls, gantry code, original recordings and manual measurements are unchanged. Metric scale and physical trait accuracy remain provisional.
