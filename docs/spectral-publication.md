# Whole-plant spectral explorer publication

The standalone page at `/results/whole-plant-spectral-20260928/` is the local 8 October explorer, with the same interactive HTML, CSS, JavaScript and measured data. Home and results navigation link to it. Both complete 28 September scans are included: 2,178,048 FX10 pixels and 1,361,280 FX17 pixels, each with 224 bands. There is no external data service or new runtime dependency.

These are measured raw camera signals and provisional board-relative values, not validated reflectance. RGB context and existing partial matches retain their original qualifications. Publication does not establish full spectral-to-3D fusion.

## Storage cleanup

All active historical studies remain available. Six byte-identical validation images now share the canonical copies used by the experimental report; validation image links were updated. Source scripts, NumPy mask intermediates, obsolete UI backups and audit screenshots are not part of the public export. The original research files are untouched. Exact omitted and consolidated paths and byte savings are recorded in `spectral-publication-manifest.json`.

The manifest records SHA-256 for every packaged viewer asset. Run `python3 scripts/check-spectral-publication.py` after `pnpm build` to verify hashes, all line/band assets, static HTML links, and the published site size. The checker enforces a conservative 950 MB site budget below GitHub Pages' 1 GB limit.

## Publication

The PR targets `phenofusion3d/phenofusion3d.github.io:main`, the publishing repository. Pushing to a personal fork alone does not update the public website. The page becomes public after merge and successful Pages deployment. No laboratory capture, reconstruction, calibration or gantry code is changed.
