# Final-cloud comparison on fixed source samples

Descriptive fixed-source audit; not independent metric validation.

Same original bundle cameras, native annotations remapped to undistorted raster, nearest positive-Z point at each rounded pixel, no dilation or increased splat footprint. Frozen boundaries excluded. All points, not viewer subsamples.

## Conditional P4 landmarks

Distance is to the nearest point anywhere in the final scene; it is descriptive agreement with shared-camera triangulation, not accuracy.

| Variant | Landmark | Nearest surface (mm) | Points within 5 mm |
| --- | --- | ---: | ---: |
| earlier | P4_single_hanging_bud | 8.417 | 0 |
| earlier | P4_left_yellow_flower_junction | 3.720 | 57 |
| earlier | P4_right_yellow_flower_junction | 0.540 | 139 |
| roi_only | P4_single_hanging_bud | 8.013 | 0 |
| roi_only | P4_left_yellow_flower_junction | 3.720 | 57 |
| roi_only | P4_right_yellow_flower_junction | 0.540 | 143 |
| roi_supported | P4_single_hanging_bud | 0.578 | 8 |
| roi_supported | P4_left_yellow_flower_junction | 3.720 | 58 |
| roi_supported | P4_right_yellow_flower_junction | 0.540 | 144 |
| short_dense | P4_single_hanging_bud | 0.196 | 22 |
| short_dense | P4_left_yellow_flower_junction | 3.987 | 98 |
| short_dense | P4_right_yellow_flower_junction | 0.561 | 147 |
| combined | P4_single_hanging_bud | 8.014 | 0 |
| combined | P4_left_yellow_flower_junction | 3.710 | 66 |
| combined | P4_right_yellow_flower_junction | 0.540 | 144 |
| combined_supported | P4_single_hanging_bud | 0.499 | 10 |
| combined_supported | P4_left_yellow_flower_junction | 3.710 | 69 |
| combined_supported | P4_right_yellow_flower_junction | 0.540 | 144 |

Full source-sample depth distributions and per-view depth-interval checks are in `final_cloud_comparison.json`.

## Limits

- Point occupancy can be background behind a missing plant part.
- Three P4 landmarks share camera model, poses and scale with reconstruction.
- Landmark intervals contain pixel annotation perturbation only, not camera or scale uncertainty.
- Nearest-neighbour distance describes agreement and is not an accuracy score.
- All source samples are localized assistant-reviewed annotations, not full-plant masks.
