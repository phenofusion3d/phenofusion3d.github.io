PhenoFusion3D saved research results — 7 October 2026

Open index.html after extracting the complete folder. Keep its project/ subtree.
Use a short extraction path (for example C:\PF3D_results) on Windows.
If local-file browser restrictions apply, serve this folder with:
  python -m http.server 8878 --bind 127.0.0.1
and open http://127.0.0.1:8878/ . No internet connection is required.

SCOPE
The reports, reviewed geometry, exact measured spectra, evidence photographs,
source-point provenance, current source and built wheel are included.
Original copied report bytes are unchanged. A historical report may describe
its own earlier limitations or source-machine paths; this index and the new
handoffs identify the current status. Original raw RGB-D sequences and full
ENVI cubes are not included. This is a derived-results archive, not a complete
raw-acquisition backup. Keep the raw recordings separately.

CONDITIONS
Unknown physical target pitch and recording units remain gaps. Measured chords
and cloud spans retain conditional scale; they are not final anatomical trait
accuracy. Hyperspectral ratios/indices are exploratory. White-panel reflectance,
confirmed dark reference and independent off-plane spatial/visibility evidence
remain necessary. This archive does not claim calibrated 3D spectral fusion,
perfect surfaces, new-dataset reconstruction generalization or lab certification.

SOURCE AND REPLAY
project/ contains the current source snapshot, including uncommitted changes.
No commit, push or deployment is performed by creating this archive.
The wheel and acceptance checklist are in:
project/generated/research_remaining_20261007/lab_handoff/
Do not replace a working lab environment without its recorded backup and tests.
For saved-cloud report replay, use the portable_workspace_manifest.json beside
the original workspace_manifest.json under research_followthrough_20261007.
The former uses package-relative cloud paths; the original is preserved unchanged.
Copy workspace_endpoints.json from the same folder when importing reviewed picks.
Build into a NEW output folder outside this saved archive.
Full spectral extraction from raw data requires the original cubes and adjusted
configuration paths. The measured derived arrays can be inspected directly.

INTEGRITY
copied_files_manifest.json maps original files to included copies and SHA-256.
checksums.sha256 covers every package file except itself.
The ZIP has a separate SHA-256 sidecar beside it.
verification.json records checks and explicitly distinguishes physical gaps.
