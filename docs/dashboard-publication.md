# Complete research dashboard

Public endpoint: `/results/all/`. The original localhost hash is accepted: `#view=%2Fgenerated%2Fresearch_whole_plant_spectral_20261008%2Findex.html` opens the published spectral explorer inside the same sidebar.

All 25 catalogue destinations are preserved, including the current five-plant report, calibration, camera models, traits, spectral scenes, partial surface overlay, fusion experiments, diagnostics, presentations, laboratory handover and labelled earlier studies. The current study is rebuilt from its source components; standalone reports retain their original scientific content.

## Large scientific assets

The linked reports contain multiple gigabytes, exceeding GitHub Pages' 1 GB published-site limit. Pages therefore serves the interface, reports, images and scripts; large binary files load from immutable GitHub commit URLs. `docs/dashboard-data-manifest.json` maps each original URL to lossless content-addressed chunks under `research-assets/`. Identical files share chunks. Gzip compression changes storage only, never measured values; chunks are at most 32 MB. The loader restores original bytes before supplying them to viewers or downloads. Original public copies are removed only after archive hashes and loading tests pass. No source research files are deleted.

`public/research-assets.js` records the immutable data commit. It intercepts only mapped same-origin GETs and data-download links; other requests pass through. Local preview can serve `research-assets/` at `/__research_data__/`. Public viewing needs network access to raw.githubusercontent.com as well as the website. GitHub's service availability and bandwidth policies still apply; this is not an institutional long-term research repository.

Run `pnpm build`, `python3 scripts/check-spectral-publication.py` and `python3 scripts/check-dashboard.py --out`. Verification checks lossless hashes, every spectral scan row, previews, all catalogue destinations, report links and the conservative 950 MB site budget. No camera acquisition, reconstruction, gantry or calibration code is changed. Publication does not establish new scientific validation.
