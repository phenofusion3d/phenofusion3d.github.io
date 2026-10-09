"""Bounded isolated Linux check; no existing environment or hardware changes."""
from pathlib import Path
import hashlib
import importlib.metadata as metadata
import importlib.util
import json
import os
import platform
import shutil
import subprocess
import sys
import time
import tomllib
import xml.etree.ElementTree as ET

OUT = Path(__file__).resolve().parent
SOURCE = OUT / "source_snapshot"
ENV = OUT / "isolated_linux_env"
CACHE = OUT / "pip_cache"
TEMP = OUT / "pytest_temp"
RESULT = OUT / "verification.json"
TESTS = ["test_analysis_ui.py", "test_analysis_workflow.py", "test_gantry_offline.py",
         "test_hyperspectral.py", "test_realsense_runtime.py", "test_reference_traits.py",
         "test_research_spectral_extract.py", "test_research_spectral_mapping.py",
         "test_research_workspace.py", "test_research_workspace_review.py", "test_ros_runtime.py"]


def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def run(args, name, timeout, *, env=None, cwd=OUT):
    start = time.monotonic()
    with (OUT / (name + ".log")).open("w", encoding="utf-8") as stream:
        result = subprocess.run(list(map(str, args)), cwd=cwd, env=env, stdout=stream,
                                stderr=subprocess.STDOUT, timeout=timeout)
    return dict(command=list(map(str, args)), exit_code=result.returncode,
                elapsed_seconds=round(time.monotonic() - start, 3), log=name + ".log")


def main():
    provenance = json.loads((OUT / "source_provenance.json").read_text())
    record = dict(status="started", commit=provenance["commit"], source=str(SOURCE),
                  platform=platform.platform(), machine=platform.machine(), python=sys.version,
                  existing_environment_changed=False, existing_checkouts_changed=False,
                  hardware_contacted=False, system_packages_changed=False,
                  new_environment=str(ENV), full_offline_selection=TESTS)
    required = ["numpy", "scipy", "open3d", "cv2", "PyQt5", "pytest", "natsort"]
    base = Path("/home/adithyarama/projects/PhenoFusion3D")
    initial = dict(executable=sys.executable, version=sys.version,
                   modules={name: bool(importlib.util.find_spec(name)) for name in required},
                   project_root=str(base), project_children=sorted(p.name for p in base.iterdir()) if base.exists() else [],
                   venv_module=bool(importlib.util.find_spec("venv")),
                   ensurepip_module=bool(importlib.util.find_spec("ensurepip")), uv=shutil.which("uv"))
    save("existing_environment.json", initial)
    record["missing_existing_dependencies"] = [name for name, present in initial["modules"].items() if not present]
    save("verification.json", record)
    try:
        assert not ENV.exists(), "Environment must be fresh; preserve earlier results"
        print("Creating a separate Linux test environment", flush=True)
        record["create_environment"] = run([sys.executable, "-m", "venv", ENV], "create_environment", 60)
        assert record["create_environment"]["exit_code"] == 0, "Isolated venv creation failed"
        interpreter = ENV / "bin/python"
        settings = tomllib.loads((SOURCE / "pyproject.toml").read_text())
        requirements = settings["project"]["dependencies"] + ["scipy>=1.10.0", "pytest>=7.4.0"]
        assert not any("realsense" in value.lower() or "rospy" in value.lower() for value in requirements)
        (OUT / "test_requirements.txt").write_text("\n".join(requirements) + "\n")
        env = {**os.environ, "PIP_DISABLE_PIP_VERSION_CHECK": "1", "PIP_NO_INPUT": "1",
               "PIP_CACHE_DIR": str(CACHE), "PYTHONDONTWRITEBYTECODE": "1",
               "PYTHONPATH": str(SOURCE), "QT_QPA_PLATFORM": "offscreen",
               "OMP_NUM_THREADS": "4", "OPENBLAS_NUM_THREADS": "4", "PYTHONUNBUFFERED": "1"}
        print("Installing binary test dependencies into the new environment only", flush=True)
        record["install_dependencies"] = run([interpreter, "-m", "pip", "install", "--only-binary=:all:",
                                                "--index-url", "https://pypi.org/simple", "-r", OUT / "test_requirements.txt"],
                                               "install_dependencies", 480, env=env)
        save("verification.json", record)
        assert record["install_dependencies"]["exit_code"] == 0, "Binary dependency installation failed"
        record["new_environment_dependencies_installed"] = True
        record["freeze"] = run([interpreter, "-m", "pip", "freeze"], "environment_freeze", 30, env=env)
        probe = "import importlib,json,sys; names=['numpy','scipy','open3d','cv2','PyQt5','pytest','processing.research_workspace.workflow','processing.research_workspace.spectral_extract','processing.research_workspace.spectral_mapping']; print(json.dumps({n:{'path':getattr(importlib.import_module(n),'__file__',None),'version':getattr(importlib.import_module(n),'__version__',None)} for n in names},indent=2)); assert not any(n=='capture' or n.startswith('capture.') for n in sys.modules)"
        record["import_probe"] = run([interpreter, "-c", probe], "import_probe", 60, env=env)
        assert record["import_probe"]["exit_code"] == 0, "Installed dependencies cannot import; inspect import_probe.log"
        imports = json.loads((OUT / "import_probe.log").read_text())
        assert all(Path(value["path"]).resolve().is_relative_to(SOURCE) for name, value in imports.items() if name.startswith("processing."))
        record["source_module_origins"] = {name: value["path"] for name, value in imports.items() if name.startswith("processing.")}
        print("Running the current-commit offline selection once, with offscreen Qt", flush=True)
        args = [interpreter, "-m", "pytest", *[SOURCE / "tests" / name for name in TESTS], "-q",
                "-p", "no:cacheprovider", "--basetemp", TEMP, "--junitxml", OUT / "tests.xml"]
        record["tests"] = run(args, "tests", 300, env=env)
        if (OUT / "tests.xml").exists():
            xml = ET.parse(OUT / "tests.xml").getroot()
            suites = list(xml.iter("testsuite"))
            record["test_counts"] = {key: sum(int(s.get(key, 0)) for s in suites) for key in ("tests", "failures", "errors", "skipped")}
            record["skips"] = [dict(test=case.get("name"), reason=skip.get("message")) for case in xml.iter("testcase") for skip in case.findall("skipped")]
        assert record["tests"]["exit_code"] == 0, "Offline suite failed; inspect tests.log and tests.xml"
        record["status"] = "passed_isolated_linux_offline_selection"
        record["limitations"] = ["WSL2 compatibility only; native lab host and physical hardware remain untested.",
                                 "Only the recorded offline test selection was run, not arbitrary GUI workflows.",
                                 "Source snapshot omits local datasets; optional real-recording parity can be skipped.",
                                 "This test environment is new and separate; existing system/lab environments were not upgraded."]
    except BaseException as error:
        record["status"] = "incomplete_or_failed_linux_compatibility_check"
        record["error"] = f"{type(error).__name__}: {error}"
        raise
    finally:
        changed = [name for name, expected in provenance["file_sha256"].items()
                   if hashlib.sha256((SOURCE / name).read_bytes()).hexdigest() != expected]
        record["source_snapshot_files_changed"] = changed
        record["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        save("verification.json", record)
        print(json.dumps({key: record.get(key) for key in ("status", "commit", "test_counts", "error", "source_snapshot_files_changed")}), flush=True)


if __name__ == "__main__":
    main()
