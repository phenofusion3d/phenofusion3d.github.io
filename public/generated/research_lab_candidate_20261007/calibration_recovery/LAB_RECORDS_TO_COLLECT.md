# Exact lab records to recover

7 October 2026. These records were not recovered in the bounded saved-file audit. No camera was opened or physical action performed. Recover originals first; do not substitute current device defaults or historical analysis constants.

1. **printed board scale** — Original ChArUco design/PDF with dictionary, rows/columns, square and marker dimensions; print settings and a dated ruler/caliper check of the actual three September28 sheets.

   Reason: The available 600px four-marker design does not specify the physical September28 board pitch.

2. **D405 and L515 depth units** — September28 camera/session export or original .bag/device-settings record containing camera serial, firmware, depth_units/get_depth_scale value, stream formats/resolutions, alignment/filter settings and acquisition time for all four named RGB-D folders.

   Reason: K/dist/dimensions were saved, but the queried depth scale was not serialized. Present device defaults are not proof of past settings.

3. **gantry units and exporter** — Exact executed September28 capture script/commit and ROS driver config; joint-state position unit/conversion; dated encoder calibration or independent travel check; associated ROS bag/position log.

   Reason: Filename=position*1e6 is recoverable source convention. Current driver scale and exact executed version are not preserved.

4. **HSI line timing and start** — Acquisition-computer sidecars 002-specim-fx10.json, 002-specim-fx17.json, 003-specim-fx10.json and 003-specim-fx17.json if retained; matching SCM/hypercam session/event logs, timestamp units/timebase, dropped-frame counters, per-line encoder/trigger relationship and run-start fiducial observations.

   Reason: August28 sidecars show frame IDs/timestamp/system_time fields and one FX17 missing frame. September28 headers alone cannot supply these records; acquisition time must not be assumed to mean first line.

5. **HSI spatial geometry** — Per-sensor serial and lens/focus identifier; spatial column-to-ray/lens/keystone calibration; measured fixed rig transforms in a stated shared frame; applicability/change log proving the geometry applies to September28.

   Reason: Historical homographies and specimen ICP transforms are not calibrated camera intrinsics/extrinsics.

6. **independent offplane validation** — Exact noncoplanar shared XYZ-to-HSI control records and independently reserved elevated holdouts, repeat-localization evidence and numeric residual thresholds; otherwise follow the saved multi-height capture specification.

   Reason: Metadata recovery alone cannot certify raised-leaf mapping or visibility.

7. **radiometric reference** — Matching white-panel spectral reflectance/certificate and exposure/gain records; confirmed shutter-closed dark capture and timing; usable reference spatial support.

   Reason: Fixed exposure/intended white use are recorded but panel reflectance and shutter-tail state remain unknown.
