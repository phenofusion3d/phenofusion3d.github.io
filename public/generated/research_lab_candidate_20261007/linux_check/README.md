# Linux / WSL compatibility evidence

Status: linux offline run completed with one existing test timing failure.
Commit: `920a577958a22e10998d24935265c77e2296d867`.
Platform: Linux-6.6.87.2-microsoft-standard-WSL2-x86_64-with-glibc2.39.
Python: 3.12.3 (main, Aug 31 2026, 10:18:26) [GCC 13.3.0].

Offline selection: 142 tests; 140 passed;
1 skipped; 1 failures;
0 errors. See `tests.xml` and `tests.log` for actual scope.

Existing Python lacked open3d, cv2, PyQt5, pytest, natsort.
The authorized fresh environment is `/tmp/phenofusion3d-validation-u6bcgpn1/environment`.
The checked source is `/tmp/phenofusion3d-validation-u6bcgpn1/source`; all 208 tracked
file hashes were checked against the current-commit archive.

Finding: Existing gantry test checks an error list before queued Qt delivery: the start-thread sentinel is cleared before error emission. In a separate 20-iteration mock-only diagnostic, immediate assertion failed in 10 iterations; bounded event waiting delivered the expected error in all 20, with nonblocking start and retryability preserved. Recommended fix is a bounded wait for the expected error in the test, not an acquisition implementation change.

## Reproduction evidence

`run_linux_native_check.py` creates a fresh unique native Linux directory and
extracts `committed_source.tar` before invoking the bounded runner. The runner
records exact commands in `verification.json`; `test_requirements.txt` lists the
requested constraints and `environment_freeze.log` records resolved versions.
After the recorded missing-libUSB import failure, `resume_with_libusb.py`
downloaded the exact official package, verified its repository SHA-256, extracted
it locally and ran the selection with a subprocess-only library path. Its package
source, version, fingerprint and paths are retained in `runtime_overlay.json`.
Run only in an authorized new environment; no existing environment needs changing.

## Limits

- This is Ubuntu on WSL2 compatibility evidence, not a native lab-host or camera/gantry acceptance test.
- No RealSense SDK, ROS, apt/system package or existing Python environment was installed or upgraded.
- The newly authorized test environment uses binary packages from PyPI and is separate from system/lab environments.
- Open3D initially required missing libusb-1.0.so.0. The official Ubuntu libusb package was downloaded and extracted only under the temporary directory; LD_LIBRARY_PATH was set only for test subprocesses. No apt update/install or package post-install script was run.
- The initial venv creation on the Windows mount timed out before dependency installation. A single native /tmp retry was used; no orphaned setup process remained.
- All checked project modules resolve to the committed source snapshot. The existing website checkouts were not edited.
- Local recordings are absent from the committed snapshot; any real-data fixture skip is listed separately and is not counted as a pass.
- Temporary Linux paths may not survive cleanup/restart. Preserve this source snapshot, exact versions and logs for reproduction.
- Synthetic/numerical software tests do not establish physical scale, completeness, plant identity, radiometric calibration or 3D spectral fusion.
