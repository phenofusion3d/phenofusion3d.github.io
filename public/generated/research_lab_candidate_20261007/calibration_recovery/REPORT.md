# Saved calibration record recovery

7 October 2026. **No new applicable physical calibration or verified metric scale was recovered.** The audit found specific acquisition-record recovery leads and preserved their provenance. No geometry, spectra, software or earlier report was modified; no raw HSI cube or camera device was opened.

## Current recording evidence

| Current folder | Files | Types |
|---|---:|---|
| `20260928` | 8 | .bil: 4, .hdr: 4 |
| `manual_validation_5-plants_28-09` | 74 | .jpeg: 66, .png: 8 |
| `test_plant_20260928143911` | 2542 | .png: 2540, .txt: 2 |
| `test_plant_20260928144647_L515` | 2582 | .png: 2580, .txt: 2 |
| `test_plant_20260928162111_L515` | 2558 | .png: 2556, .txt: 2 |
| `test_plant_20260928162354` | 2416 | .png: 2414, .txt: 2 |

The four RGB-D runs each contain image pairs and two intrinsics files. All eight intrinsics documents contain only `K`, `dist`, `height`, `width`; they omit depth scale, device serial, firmware and rigid extrinsics. The HSI directory contains four BIL cubes and four ENVI headers, with no JSON sidecars, encoder/session files or logs. The extensionless `order_of_scan` note says `1. calibration, hyperspec, d405 and l515 (002-specim-fx10)`; it supports run ordering, not numerical synchronization or physical dimensions. These 13 small current metadata documents are hashed in the inventory.

Representative RGB/depth PNG containers from each RGB-D run were also inspected without decoding pixels. Their chunk inventory and dimensions are saved; this sample is not an exhaustive assertion about every image. Filename tokens and matching-pair counts were enumerated without treating filename differences as elapsed time.

## Recovered source conventions, with limits

The main and reference `rospy_thread_fin_1.py` sources obtain `depth_sensor.get_depth_scale()` (line 52) but omit the value from their saved intrinsics dictionaries (lines 47–98). Thus the source explains how units could be lost; it cannot reconstruct the runtime numeric value. The same source writes `int(position * 10**6)` into frame names (line 129), using `message.position[0]` (line 142). This is useful exporter-convention evidence, but the exact September 28 executed revision, driver-unit conversion and independent travel check are absent. Reference and current scripts even have different stop endpoints (0.78 and 1.65).

The September 1 `data/main/20260901122109/session.json` explicitly records a ROS session, 30 FPS, velocity 0.038 m/s, endpoint 1.65 m and 1309 frame-position entries. The May 11 session records camera-only capture and timestamps. Both are historical captures; neither supplies September 28 frame positions, depth units or HSI timing. The August 28 profile uses depth divisor 10000, explicitly for that older dataset. These processing values and generic 1000 defaults are not camera readbacks and were not transferred.

## Neighbouring repository: useful acquisition-sidecar leads

`../3d_hyperspec_ai/data/20260828/001-specim-fx10.json` and `001-specim-fx17.json` preserve `bil_hdr`, `frames[]` and `info`. Each frame has `frame_id`, `frame_start_offset`, `system_time`, `timestamp`. FX10 has 2127 frame records; FX17 has 2126 and lacks frame ID 946, with `n_failures=1`. This demonstrates why original per-line records matter and identifies the analogous run 002/003 sidecars to request from the acquisition computer.

The sidecars explicitly belong to August 28, run 001. Their time/offset units are not declared. Initial device timestamp increments are 62500000, but no September 28 line rate is inferred. If system_time is interpreted as Unix nanoseconds, the header's acquisition time lies near the historical final frame; that interpretation is unverified and is not used to establish scan start. The current run003 headers share `2026-09-28T06:19:41Z`, but a single timestamp does not encode line timing or RGB-D synchronization.

No serial/lens, spatial intrinsics, rigid extrinsics, encoder positions or trigger relationship occur in those historical JSONs. The historical ROS YAML has `target_velocity:0.025`, whereas the capture source has 0.038. These are distinct unproven configurations, not competing estimates from which to choose a current speed.

## Board and geometric calibration recovery

The neighbouring `notebooks/aruco_markers.ipynb` designs four standalone DICT_4X4_50 markers (IDs0–3), each 600 pixels. It contains no physical print dimensions, and it is not a design specification for the current three ChArUco sheets. Pixel design size cannot determine printed square pitch. No actual September 28 board drawing, print-scale certificate or measured square dimension was recovered.

The historical Coleus fusion metrics contain a plant-local SIFT/RANSAC image homography with an explicit planar/parallax limitation. Historical global-placement matrices are specimen-to-scene ICP transforms and explicitly do not recover the missing 95-frame trajectory. Neither is an HSI lens calibration or a fixed RGB-D-to-HSI rig transform. No applicable HSI spatial calibration was found within this bounded search.

## Gaps and next records

All physical-scale and raised-leaf projection gaps remain open. A shared arbitrary frame can in principle support independently pixel-validated mapping; absolute millimetres are a separate requirement. This audit does not repeat the completed leaf-landmark review or manufacture new controls. Physical fusion remains null.

1. **printed board scale** — Original ChArUco design/PDF with dictionary, rows/columns, square and marker dimensions; print settings and a dated ruler/caliper check of the actual three September 28 sheets.

   Reason: The available 600px four-marker design does not specify the physical September 28 board pitch.

2. **D405 and L515 depth units** — September 28 camera/session export or original .bag/device-settings record containing camera serial, firmware, depth_units/get_depth_scale value, stream formats/resolutions, alignment/filter settings and acquisition time for all four named RGB-D folders.

   Reason: K/dist/dimensions were saved, but the queried depth scale was not serialized. Present device defaults are not proof of past settings.

3. **gantry units and exporter** — Exact executed September 28 capture script/commit and ROS driver config; joint-state position unit/conversion; dated encoder calibration or independent travel check; associated ROS bag/position log.

   Reason: Filename=position*1e6 is recoverable source convention. Current driver scale and exact executed version are not preserved.

4. **HSI line timing and start** — Acquisition-computer sidecars 002-specim-fx10.json, 002-specim-fx17.json, 003-specim-fx10.json and 003-specim-fx17.json if retained; matching SCM/hypercam session/event logs, timestamp units/timebase, dropped-frame counters, per-line encoder/trigger relationship and run-start fiducial observations.

   Reason: August 28 sidecars show frame IDs/timestamp/system_time fields and one FX17 missing frame. September 28 headers alone cannot supply these records; acquisition time must not be assumed to mean first line.

5. **HSI spatial geometry** — Per-sensor serial and lens/focus identifier; spatial column-to-ray/lens/keystone calibration; measured fixed rig transforms in a stated shared frame; applicability/change log proving the geometry applies to September 28.

   Reason: Historical homographies and specimen ICP transforms are not calibrated camera intrinsics/extrinsics.

6. **independent offplane validation** — Exact noncoplanar shared XYZ-to-HSI control records and independently reserved elevated holdouts, repeat-localization evidence and numeric residual thresholds; otherwise follow the saved multi-height capture specification.

   Reason: Metadata recovery alone cannot certify raised-leaf mapping or visibility.

7. **radiometric reference** — Matching white-panel spectral reflectance/certificate and exposure/gain records; confirmed shutter-closed dark capture and timing; usable reference spatial support.

   Reason: Fixed exposure/intended white use are recorded but panel reflectance and shutter-tail state remain unknown.

## Files and verification

`evidence_inventory.json` and `.csv` contain exact paths, file sizes, SHA-256, observations, line references and applicability. `lab_records_to_collect.json` is an explicit recovery list. `audit_saved_metadata.py` reproduces the metadata-only inventory and rechecks every source hash at completion. No full hyperspectral payload hash is claimed. Search scope was limited to this recording tree, related saved acquisition files and exact neighbouring calibration/configuration sources; absence here is not proof the lab computer has no such records.
