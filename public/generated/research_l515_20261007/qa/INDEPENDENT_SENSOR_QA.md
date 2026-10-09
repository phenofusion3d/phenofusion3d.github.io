# Independent L515 reconstruction verification

PASS: saved computational products and provenance checks; not physical accuracy certification

Verified 64 distinct integrated frames, 1,598,977 supported points and 1,562,246 points in the optional statistically filtered derivative. The pre-SOR supported result remains separate.

All 192 initial/bundle/ICP transforms are rigid. Every saved ICP acceptance decision matches its declared gate. Every supported point has at least 3 supporting views and passes `conflict <= max(1,0.3*support)`; median support is 9.

Independently recomputed votes and colour choices for 480 sampled points against all 64 source frames, applying the saved native housing mask and undistortion. Support, conflict, source-view index and RGB mismatches: **0 / 0 / 0 / 0**. This check did not call the reconstruction's visibility function.

Filtered-source indices reproduce the saved filtered coordinates and colours (maximum coordinate error 0 m). Upright coordinates equal the source cloud multiplied by the saved board-up rotation, with maximum error 2.22e-16 m. Point order and colours are preserved; no translation or scale adjustment occurs.

All 7 recorded output SHA256 checks pass. Both complete replacement L515 PNG inventories were rehashed: 5,136 files, matching original bytes, file sets and SHA256. All four intrinsic files are unchanged.

Original RGB reconstruction module hashes match the preexisting reference; capture-module hashes match the earlier audit. The research bundle copy contains exactly the declared mask and import changes. The tracked checkout is clean, and `git diff HEAD -- main.py capture processing` is empty. HEAD: `3b15fdf15c0b2668a1e5c890507c9b9362c2ca42`.

## Interpretation limits

- Pass establishes recorded computation, index mapping and data preservation, not physical trait accuracy or complete plant geometry.
- Depth units and registration remain conditional on calibration analysis. Broad0.2–1.6m is a scene envelope, not a sensor-accuracy range or biological segmentation.
- Projection support uses one vote per view but neighbouring pixels may supply depth agreement; RGB is taken at the centre pixel, allowing colour bleeding at depth boundaries.
- TSDF averages observations and can omit thin surfaces; statistical derivative may delete small supported organs. Supported product is preserved separately.
- The first-camera origin is retained. Board-up rotation supplies orientation, not soil height or a specimen base datum.

Detailed counts, source hashes and individual camera checks: `independent_sensor_QA.json`. The sampled point indices and independently recomputed evidence are retained in `sampled_vote_checks.npz`. `verify_sensor_reconstruction.py` reproduces this read-only audit. No reconstruction was rerun and no raw/application file was modified.
