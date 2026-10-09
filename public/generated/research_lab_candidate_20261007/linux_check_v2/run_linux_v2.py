"""Verify one test-only patch using the existing isolated Linux runtime."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import time
import xml.etree.ElementTree as ET

OUT = Path(__file__).resolve().parent
OLD = OUT.parent / "linux_check"
provenance = json.loads((OUT / "source_provenance.json").read_text())
native = json.loads((OLD / "native_paths.json").read_text())
overlay = json.loads((OLD / "runtime_overlay.json").read_text())
ROOT = Path(native["native_root"])
SOURCE = ROOT / "source_v2"
PYTHON = Path(native["environment"]) / "bin/python"
TESTS = json.loads((OLD / "verification.json").read_text())["full_offline_selection"]


def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2) + "\n")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(command, name, timeout, env):
    start = time.monotonic()
    with (OUT / (name + ".log")).open("w") as log:
        process = subprocess.run(list(map(str, command)), cwd=ROOT, env=env,
                                 stdout=log, stderr=subprocess.STDOUT, timeout=timeout)
    return dict(command=list(map(str, command)), exit_code=process.returncode,
                elapsed_seconds=round(time.monotonic() - start, 3), log=name + ".log")


def xml_counts(name):
    xml = ET.parse(OUT / name).getroot()
    suites = list(xml.iter("testsuite"))
    counts = {key: sum(int(s.get(key, 0)) for s in suites) for key in ("tests", "failures", "errors", "skipped")}
    skips = [dict(test=case.get("name"), reason=skip.get("message")) for case in xml.iter("testcase") for skip in case.findall("skipped")]
    return counts, skips


def main():
    assert ROOT.parent == Path("/tmp") and ROOT.name.startswith("phenofusion3d-validation-")
    assert not SOURCE.exists(), "Preserve prior snapshots; v2 source must be fresh"
    shutil.copytree(Path(native["source"]), SOURCE)
    changed = "tests/test_gantry_offline.py"
    shutil.copyfile(OUT / "source_snapshot" / changed, SOURCE / changed)
    assert sha(SOURCE / changed) == provenance["test_lf_sha256"]
    assert all(sha(SOURCE / name) == value for name, value in provenance["file_sha256"].items())
    old_provenance = json.loads((OLD / "source_provenance.json").read_text())
    assert all(sha(Path(native["source"]) / name) == value for name, value in old_provenance["file_sha256"].items())
    env = {**os.environ, "PYTHONPATH": str(SOURCE), "PYTHONDONTWRITEBYTECODE": "1",
           "QT_QPA_PLATFORM": "offscreen", "OMP_NUM_THREADS": "4", "OPENBLAS_NUM_THREADS": "4",
           "LD_LIBRARY_PATH": overlay["ld_library_path"]}
    record = dict(status="running", base_commit=provenance["base_commit"], patch_uncommitted=True,
                  patch_sha256=provenance["patch_sha256"], test_lf_sha256=provenance["test_lf_sha256"],
                  source=str(SOURCE), python=str(PYTHON), runtime_overlay=overlay,
                  existing_environment_reused=True, new_dependencies_installed=False,
                  system_packages_changed=False, production_source_changed=False,
                  hardware_contacted=False, other_committed_files_unchanged=207,
                  protected_file_count=26, protected_files_changed=[])
    save("verification.json", record)
    try:
        probe = "import json,sys,importlib; names=['numpy','scipy','open3d','cv2','PyQt5','pytest','processing.research_workspace.workflow','processing.research_workspace.spectral_extract']; print(json.dumps({n:{'origin':getattr(importlib.import_module(n),'__file__',None),'version':getattr(importlib.import_module(n),'__version__',None)} for n in names},indent=2))"
        record["import_probe"] = run([PYTHON, "-c", probe], "import_probe", 40, env)
        assert record["import_probe"]["exit_code"] == 0
        origins = json.loads((OUT / "import_probe.log").read_text())
        assert all(Path(value["origin"]).resolve().is_relative_to(SOURCE) for name, value in origins.items() if name.startswith("processing."))
        record["module_origins"] = origins
        print("Running the same full Linux offline selection on the isolated test-only snapshot", flush=True)
        command = [PYTHON, "-m", "pytest", *[SOURCE / "tests" / name for name in TESTS], "-q",
                   "-p", "no:cacheprovider", "--basetemp", ROOT / "v2_pytest_temp", "--junitxml", OUT / "tests.xml"]
        record["full_suite"] = run(command, "tests", 300, env)
        record["test_counts"], record["skips"] = xml_counts("tests.xml")
        assert record["full_suite"]["exit_code"] == 0, "Full offline selection failed"
        repeat = ROOT / "repeat_v2"
        repeat.mkdir()
        wrapper = repeat / "test_changed_gantry_repeat.py"
        wrapper.write_text('''import importlib.util
from pathlib import Path
import pytest
from PyQt5.QtWidgets import QApplication

target=Path(''' + repr(str(SOURCE / changed)) + ''')
spec=importlib.util.spec_from_file_location("changed_gantry_test_subject",target)
subject=importlib.util.module_from_spec(spec);spec.loader.exec_module(subject)

@pytest.fixture(scope="module")
def application():
    return QApplication.instance() or QApplication(["mock-only-repeat"])

@pytest.mark.parametrize("iteration",range(20))
def test_changed_gantry_error_delivery(iteration,application,monkeypatch):
    subject.test_connection_failure_is_nonblocking_and_retryable(application,monkeypatch)
''')
        print("Repeating only the changed mock-only test twenty times to check the former race", flush=True)
        record["changed_test_repeat"] = run([PYTHON, "-m", "pytest", wrapper, "-q", "-p", "no:cacheprovider",
                                              "--basetemp", ROOT / "v2_repeat_temp", "--junitxml", OUT / "repeat_tests.xml"],
                                             "repeat_tests", 90, env)
        record["repeat_counts"], _ = xml_counts("repeat_tests.xml")
        assert record["changed_test_repeat"]["exit_code"] == 0
        assert record["repeat_counts"] == dict(tests=20, failures=0, errors=0, skipped=0)
        record["status"] = "passed_linux_offline_selection_and_changed_test_repeats"
        record["full_suite_passed"] = True
    except BaseException as error:
        record["status"] = "failed_linux_v2_verification"
        record["error"] = f"{type(error).__name__}: {error}"
        raise
    finally:
        record["v2_snapshot_files_changed_during_tests"] = [name for name, expected in provenance["file_sha256"].items() if sha(SOURCE / name) != expected]
        record["prior_snapshot_files_changed"] = [name for name, expected in old_provenance["file_sha256"].items() if sha(Path(native["source"]) / name) != expected]
        record["frozen_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        save("verification.json", record)
        save("status.json", {key: record.get(key) for key in ("status", "base_commit", "patch_uncommitted", "patch_sha256", "test_lf_sha256", "test_counts", "repeat_counts", "full_suite_passed", "production_source_changed", "hardware_contacted", "error")})
        print(json.dumps({key: record.get(key) for key in ("status", "test_counts", "repeat_counts", "error")}), flush=True)


if __name__ == "__main__":
    main()
