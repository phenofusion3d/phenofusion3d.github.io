# Independent fusion QA

**PASS: declared algorithm, coordinate preservation and provenance. This is an exploratory research union, not verified physical extrinsics or absolute accuracy.**

- D405: 1,719,001 points in the declared scene crop are unchanged, with exact source coordinates, colours and indices. 6,546,079 original points outside the crop are not included; the original full source file remains unchanged.
- L515: 13,489 additions retain their original colours and indices, with only the declared rigid transform applied. Maximum saved-coordinate difference from independent matrix transformation: 0 m.
- Union: 1,732,490 points, exact source concatenation. No averaging, deformation, synthetic completion or manual-trait scaling.
- Every nearest-distance gate, classification flag, source-evidence gate, exclusive decision code and count was checked. All 74 recorded input hashes and 10 recorded output hashes match; inputs still match after QA.
- Independently recomputed 579 stratified candidates across all 64 D405 views (37,056 point/view checks): zero support or free-space-conflict mismatches. The verifier does not import the fusion implementation or its visibility helper.
- Tracked checkout is clean and the tracked `main.py`, capture and processing diff is empty.

| Exclusive decision | Points |
|---|---:|
| Near duplicate suppressed | 140,434 |
| Nonduplicate free-space contradiction | 3,823 |
| Nonduplicate uncertain overlap | 17,962 |
| Added, at least two D405 agreeing views | 8,330 |
| Added, fewer than two D405 agreeing views | 5,159 |

The last group contains 4,875 points with zero D405 votes and 284 with one. They retain L515 same-camera multi-view evidence. Missing or occluded D405 observations abstain; absence of contradiction is not independent confirmation.

The separate held-out P2/P4 soil correspondences support an empirical rigid alignment (median 3.411 mm, P90 7.415 mm, maximum 22.506 mm in the recorded 62-match quality cohort). They were not used to fit the P1/P3/P5 surface transform. This near-planar evidence does not establish true camera extrinsics, elevated-leaf accuracy or hidden-surface completeness. Units, alignment of exported colour/depth rasters and the camera/gantry model remain conditional. Pots are included in the review crop, so the union is not an organ segmentation or direct trait measurement.

See `independent_fusion_qa.json` for measured checks and hashes, and `independent_sampled_cross_view_votes.npz` for per-view sampled evidence. This verification reads generated source clouds/depth caches; the earlier sensor QA, not this run, performed the full raw-image-manifest rehash.
