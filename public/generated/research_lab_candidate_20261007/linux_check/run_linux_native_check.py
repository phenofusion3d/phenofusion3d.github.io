"""One authorized retry on a fresh native Linux filesystem directory."""
from pathlib import Path
import hashlib
import json
import shutil
import tarfile
import tempfile

import run_linux_check as audit

out = Path(__file__).resolve().parent
for name in ("verification.json", "create_environment.log"):
    if (out / name).exists():
        shutil.copyfile(out / name, out / ("ntfs_attempt_" + name))
native = Path(tempfile.mkdtemp(prefix="phenofusion3d-validation-", dir="/tmp"))
assert native.parent == Path("/tmp") and native.name.startswith("phenofusion3d-validation-")
source = native / "source"
source.mkdir()
with tarfile.open(out / "committed_source.tar") as archive:
    archive.extractall(source, filter="data")
provenance = json.loads((out / "source_provenance.json").read_text())
assert all(hashlib.sha256((source / name).read_bytes()).hexdigest() == expected
           for name, expected in provenance["file_sha256"].items())
(out / "native_paths.json").write_text(json.dumps(dict(native_root=str(native), source=str(source),
    environment=str(native / "environment"), commit=provenance["commit"],
    source_files_verified=len(provenance["file_sha256"]), existing_checkouts_modified=False), indent=2) + "\n")
audit.SOURCE = source
audit.ENV = native / "environment"
audit.CACHE = native / "pip_cache"
audit.TEMP = native / "pytest_temp"
audit.main()
