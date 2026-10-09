"""Download/extract one official library locally, then run the offline suite."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import xml.etree.ElementTree as ET

import run_linux_check as audit

out = Path(__file__).resolve().parent
record = json.loads((out / "verification.json").read_text())
native = json.loads((out / "native_paths.json").read_text())
root = Path(native["native_root"])
source = Path(native["source"])
interpreter = Path(native["environment"]) / "bin/python"
assert root.parent == Path("/tmp") and root.name.startswith("phenofusion3d-validation-")
for name in ("verification.json", "import_probe.log"):
    shutil.copyfile(out / name, out / ("before_runtime_overlay_" + name))
downloads = root / "downloaded_runtime"
overlay = root / "runtime_overlay"
downloads.mkdir(); overlay.mkdir()
package = "libusb-1.0-0=2:1.0.27-1"
details = subprocess.check_output(["apt-cache", "show", package], text=True)
fields = dict(line.split(": ", 1) for line in details.splitlines() if ": " in line and not line.startswith(" "))
uri = subprocess.check_output(["apt-get", "--print-uris", "download", package], text=True)
assert "archive.ubuntu.com/ubuntu" in uri
record["runtime_download"] = audit.run(["apt-get", "download", package], "runtime_download", 90, cwd=downloads)
assert record["runtime_download"]["exit_code"] == 0
deb, = downloads.glob("*.deb")
fingerprint = hashlib.sha256(deb.read_bytes()).hexdigest()
assert fingerprint == fields["SHA256"]
record["runtime_extract"] = audit.run(["dpkg-deb", "--extract", deb, overlay], "runtime_extract", 30)
assert record["runtime_extract"]["exit_code"] == 0
lib = overlay / "usr/lib/x86_64-linux-gnu"
assert (lib / "libusb-1.0.so.0").exists()
runtime_record = dict(package=fields["Package"], version=fields["Version"], architecture=fields["Architecture"],
                      archive_uri=uri.strip(), archive_sha256=fingerprint, metadata_sha256=fields["SHA256"],
                      archive_path=str(deb), extracted_to=str(overlay), ld_library_path=str(lib),
                      apt_update_run=False, apt_install_run=False, system_files_changed=False,
                      postinstall_scripts_run=False, sdk_installed=False, device_access_performed=False)
audit.save("runtime_overlay.json", runtime_record)
record["runtime_overlay"] = runtime_record
env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONPATH": str(source),
       "QT_QPA_PLATFORM": "offscreen", "OMP_NUM_THREADS": "4", "OPENBLAS_NUM_THREADS": "4",
       "LD_LIBRARY_PATH": str(lib) + (":" + os.environ["LD_LIBRARY_PATH"] if os.environ.get("LD_LIBRARY_PATH") else "")}
try:
    print("Testing imports with the isolated official libusb overlay", flush=True)
    probe = "import importlib,json,sys; names=['numpy','scipy','open3d','cv2','PyQt5','pytest','processing.research_workspace.workflow','processing.research_workspace.spectral_extract','processing.research_workspace.spectral_mapping']; print(json.dumps({n:{'path':getattr(importlib.import_module(n),'__file__',None),'version':getattr(importlib.import_module(n),'__version__',None)} for n in names},indent=2)); assert not any(n=='capture' or n.startswith('capture.') for n in sys.modules)"
    record["import_probe"] = audit.run([interpreter, "-c", probe], "import_probe", 60, env=env)
    assert record["import_probe"]["exit_code"] == 0, "Import still fails; no further system changes attempted"
    imports = json.loads((out / "import_probe.log").read_text())
    assert all(Path(v["path"]).resolve().is_relative_to(source) for n, v in imports.items() if n.startswith("processing."))
    record["source_module_origins"] = {n: v["path"] for n, v in imports.items() if n.startswith("processing.")}
    print("Running the full requested offline selection once", flush=True)
    args = [interpreter, "-m", "pytest", *[source / "tests" / name for name in audit.TESTS], "-q",
            "-p", "no:cacheprovider", "--basetemp", root / "pytest_temp", "--junitxml", out / "tests.xml"]
    record["tests"] = audit.run(args, "tests", 300, env=env)
    record["full_selection_executed"] = True
    if (out / "tests.xml").exists():
        xml = ET.parse(out / "tests.xml").getroot(); suites = list(xml.iter("testsuite"))
        record["test_counts"] = {key: sum(int(s.get(key, 0)) for s in suites) for key in ("tests", "failures", "errors", "skipped")}
        record["skips"] = [dict(test=case.get("name"), reason=skip.get("message")) for case in xml.iter("testcase") for skip in case.findall("skipped")]
    assert record["tests"]["exit_code"] == 0, "Offline selection failed; inspect tests.log and tests.xml"
    record.pop("error", None)
    record["status"] = "passed_isolated_linux_offline_selection_with_local_runtime_overlay"
except BaseException as error:
    record["status"] = "incomplete_or_failed_linux_compatibility_with_local_runtime_overlay"
    record["error"] = f"{type(error).__name__}: {error}"
    raise
finally:
    provenance = json.loads((out / "source_provenance.json").read_text())
    record["source_snapshot_files_changed"] = [name for name, expected in provenance["file_sha256"].items()
        if hashlib.sha256((source / name).read_bytes()).hexdigest() != expected]
    audit.save("verification.json", record)
    print(json.dumps({k: record.get(k) for k in ("status", "test_counts", "error", "source_snapshot_files_changed")}), flush=True)
