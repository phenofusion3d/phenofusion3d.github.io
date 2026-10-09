# Lab acceptance handoff — research workspace

Prepared 7 October 2026. This is a local software handoff. Camera acquisition,
gantry motion, physical calibration and measurement accuracy have not been tested
in this work. Leave the lab checks below unmarked until an operator records an
actual result on the rig.

## What is already checked

- The saved release XML contains **141 tests, zero failures, zero errors and zero
  skips**. All eight listed release software files still match its recorded
  SHA-256 values. This audit rechecked that evidence without rerunning the suite.
- All **26 protected acquisition, controller, main-window, reconstruction and
  installation files** match the pre-integration baseline. `main.py`, capture,
  RealSense, ROS, gantry implementation and existing dependency pins are unchanged.
- Both new command-line help entry points and workspace template creation ran
  successfully in the current Python environment.
- A workspace was built from the earlier `integration_109_final/reviewed_result`
  upright cloud, sourced from recording `20260901122109`: **1,266,476 source
  points**, **422,159 displayed points**, stride **3**. Source files remained
  unchanged. Units were deliberately recorded as `unknown`, with no endpoint
  measurements; anatomical height, leaf area, volume and empty comparison scores
  remain null. This checks supplied-cloud input reuse only. It is not a new
  reconstruction, segmentation benchmark, trait validation or generalization test.
- The previous bounded offscreen UI check showed that all Research workspace
  controls fit at 850×760. The dedicated research viewer's static fallback was
  readable, used its research banner, followed a local HTML link and returned home.
  Those checks do not demonstrate WebEngine or hardware behavior on the lab rig.

## Preconditions to record on the lab machine

- [ ] Record operator, date, machine, source revision or source hashes, Python
  executable, and chosen output directory. Keep the protected-file comparison.
- [ ] Use the existing lab Python environment and existing ROS distribution,
  catkin workspace, camera USB/SDK configuration and device-selection settings.
  This handoff performs no installation. Keep the existing
  `pyrealsense2==2.54.2.5684` pin and all acquisition settings.
- [ ] Check required packages are available in that environment: NumPy and
  Open3D for workspace clouds; NumPy for extraction; OpenCV for polygon regions;
  PyQt5 for the desktop UI. Optional PyQtWebEngine enables interactive in-app
  reports. A local WebGL-capable browser can supply interactive point review.
- [ ] Record whether WebEngine is available. It is absent in the verified
  Windows audit runtime, which used the static report fallback. `rospy` is also
  absent there; that is not evidence about the configured Linux lab ROS runtime.
  Presence of a RealSense Python module is not a successful camera connection.
- [ ] Confirm the output parent is writable and outside recording/source
  directories. Each CLI output must be new or empty. Keep source clouds, source
  ENVI files, setup JSON, reviewed regions and any linked reports available.
- [ ] Use the normal checkout launch (`python main.py`) from the repository root
  or the existing lab launcher. Do not leave `QT_QPA_PLATFORM=offscreen` set for an
  interactive operator session; that setting was only used for headless tests.

The audited runtime used Python 3.12 with the existing local dependency overlay,
not a newly installed environment. Package versions and availability are saved
in `runtime_preconditions.json`. Fresh installation and Linux hardware acceptance
remain separate from these software checks.

## Desktop software checks on the rig

- [ ] **Open Analysis.** Start the normal application, then choose
  **Analysis → Offline reconstruction, traits and hyperspectral fusion... →
  Research workspace**. Confirm the original **Data Capture** and **Gantry
  Control** panels remain present. No analysis action should request camera
  selection, begin capture or command gantry motion.
- [ ] **Create a setup.** Choose **New results parent folder**, then **Create
  workspace setup template**. Expect a new timestamped run containing
  `workspace_template.json` and `result/index.html`. The setup field should point
  to the new JSON and the old optional endpoint field should be cleared. Edit
  the template with actual saved PLY paths and protected input roots before build.
- [ ] **Build a saved-cloud report.** Select **Workspace setup JSON**, leave
  endpoints empty initially, and choose **Build / check research workspace**.
  Expect `run_status.json` with `complete_candidate_workspace`, a manifest
  snapshot, observed descriptors, empty measurements, and `result/index.html`.
  Coordinate-unit declarations must not rescale the source cloud.
- [ ] **Open the right report.** Use **Open latest result** or **Saved workspace
  report (index.html) → Open saved workspace report in software**. Expect the
  **RESEARCH REVIEW** banner. Confirm the saved report, local links and **Report
  home** work. If only the static view is available, use **Open in browser** for
  interactive points; record this limitation.
- [ ] **Review source-index points.** In the point reviewer choose specimen,
  displayed cloud and quantity. Use **Mark first point**, double-click an actual
  visible vertex, repeat for **Mark second point**, then **Keep endpoint pair**
  and **Download endpoint JSON**. Verify cloud ID/hash and zero-based source
  indices are exported. Unsampled or missing anatomical endpoints must remain
  missing. A partial visible chord is not a complete leaf length.
- [ ] **Rebuild annotations.** Select the exported JSON in **Reviewed landmark
  JSON (optional)** and build a fresh run. Exported records begin unreviewed.
  Expect source-index validation, provisional values and no physical-accuracy
  claim. Unknown units and empty eligible reference sets must retain null scores.
- [ ] **Extract a saved spectrum.** Select **Spectral extraction setup JSON**
  and **Extract measured spectra from reviewed regions**. Use a configuration
  reviewed for that exact recording. Expect `run_status.json` with `complete`,
  `result/index.html`, actual raw-DN spectra, source line/column/band identities,
  quality flags, mask, CSV and metadata. Q/Q0, reference profiles and descriptors
  appear only when their explicit inputs and wavelength requirements are met.
- [ ] **Check incomplete output.** Start a sufficiently long offline job and
  select **Cancel processing**. Expect the process to stop, status `cancelled`,
  and no completed latest result. A CLI interruption can leave `running` or
  partial files; accept completion only from a successful exit and complete
  status. Reusing a nonempty output folder should be rejected.
- [ ] **Keep historical HSI separate.** Confirm **Hyperspectral / fusion ·
  experimental** still describes its reviewed 28 August dataset. New September
  or other recording extraction belongs to the new reviewed-region action.

## Acquisition acceptance — pending a lab operator

Use the existing rig acceptance procedure and operator-approved movement bounds.
These checks are not performed by this handoff and do not introduce new capture
settings or motion recipes.

- [ ] **Camera-only behavior.** In **Data Capture**, select **RealSense Only**
  for the existing camera-only acceptance run. Confirm device selection, Capture,
  Stop, completion and **Open captured folder** behave as before. Saving must
  finish after acquisition stops; verify matched RGB/depth frame names and
  camera-intrinsic/session records using the existing capture procedure.
- [ ] **ROS/gantry behavior.** With the normal lab runtime available, verify the
  existing **Auto / ROS + Gantry** backend behavior and live position read-back.
  Check the existing **<< Jog**, **Jog >>**, release-to-stop, **Go**, **Go Home**
  and **STOP** controls using the rig's established safe procedure. The analysis
  integration must not change command topics, sign convention, units, limits,
  stop behavior or session frame-to-position recording.
- [ ] **Capture takes priority.** During the approved capture acceptance run,
  attempts to launch analysis or open its saved viewer should report **Processing
  busy**. Starting capture while offline work is active must cancel that offline
  job and leave partial results unaccepted. This interaction passed simulated
  worker tests; actual rig behavior still needs operator evidence.
- [ ] **Other worker guards.** While reconstruction, quality checking or
  post-processing is active, analysis should refuse to start. Close the Analysis
  window during an offline job and confirm its child process stops without
  changing capture/gantry settings. Record logs for any failure.
- [ ] **Final preservation check.** Compare the protected 26 hashes after the
  acceptance session; preserve run statuses, logs, source fingerprints and
  operator observations. Hardware acceptance does not resolve plant-scale,
  organ-identity, radiometric or cross-sensor calibration gaps.

## Command-line equivalents

Run from the repository root in the application's existing Python environment.
The example output names must be changed if previously used. Replace setup and
annotation paths with actual reviewed inputs.

```text
python main.py
python -m processing.research_workspace --help
python -m processing.research_workspace template --output generated/lab_acceptance/workspace_setup
python -m processing.research_workspace build --manifest generated/lab_acceptance/workspace_setup/workspace_template.json --output generated/lab_acceptance/workspace_01
python -m processing.research_workspace build --manifest generated/lab_acceptance/workspace_setup/workspace_template.json --annotations reviewed_endpoints.json --output generated/lab_acceptance/workspace_02
python -m processing.research_workspace.spectral_extract --help
python -m processing.research_workspace.spectral_extract --config reviewed_spectral_config.json --output generated/lab_acceptance/spectra_01
python -m app.research_report generated/lab_acceptance/workspace_01/result/index.html
```

For the saved 28 September FX10 example only, when its original local recording
is available, `docs/examples/research_spectral_20260928_fx10.json` is a valid
configuration path. Its polygons and reference assumptions are dataset-specific.
Use `docs/examples/research_spectral_template.json` as a starting structure for
another recording; it must be edited and reviewed first.

The recorded 141-test selection can be repeated without hardware using the
following command. Set `QT_QPA_PLATFORM=offscreen`, `OMP_NUM_THREADS=4`,
`OPENBLAS_NUM_THREADS=4` and `PYTHONDONTWRITEBYTECODE=1` in that test session.
Choose a fresh short temporary path; long Windows paths can affect Open3D file
loading. Optional real-recording fixtures can be skipped if those local files
are absent, so record actual counts rather than assuming 141 passes elsewhere.

```text
python -m pytest tests/test_analysis_ui.py tests/test_analysis_workflow.py tests/test_gantry_offline.py tests/test_hyperspectral.py tests/test_realsense_runtime.py tests/test_reference_traits.py tests/test_research_spectral_extract.py tests/test_research_spectral_mapping.py tests/test_research_workspace.py tests/test_research_workspace_review.py tests/test_ros_runtime.py -q --basetemp generated/lab_test_tmp --junitxml generated/lab_acceptance/tests.xml
```

## Packaging correction and evidence

The audit found that the declared `phenofusion3d = main:main` console entry point
did not include `main.py` in wheel module selection. The correction adds only
`py-modules = ["main"]` under `[tool.setuptools]` in `pyproject.toml`. The existing
main module and dependency declarations are unchanged. `wheel_verification.json`
records the wheel archive check, exact included source hashes and isolated
source-cloud build. Building and inspecting a wheel does not install it or test
camera/gantry hardware.

The original workspace output links its original local inputs; it is not a
self-contained data bundle. Rebuilding requires those files. Any separately
prepared portable review bundle has its own inventory and verification; this
handoff does not assume a package location or infer completeness from copying
only `result/`.

Record acceptance decision, unresolved issues, operator and date separately.
Keep `physical_accuracy_validated=false` and calibrated 3D fusion unclaimed
unless a distinct, documented physical validation study establishes them.
