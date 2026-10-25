# Website handover

The incoming maintainer should be able to build the website, open the results, recover the deployment and retrieve its scientific assets without the original developer's laptop. Use this record with the project's software, data and results handover register.

## Record at the handover

| Item | Record and demonstrate |
| --- | --- |
| Publishing repository | `phenofusion3d/phenofusion3d.github.io`; confirm recipient access |
| Accepted source release | Exact commit SHA and any release tag agreed by the team |
| Site administrator | Named person who can inspect Actions, Pages settings and repository access |
| Deployment configuration | Confirm Pages Source is GitHub Actions and the deploy workflow succeeds |
| Website data | Complete `research-assets/`, both data/publication manifests and matching loader |
| Original datasets and intermediates | Institutional storage link, inventory, size/checksum report and recipient restore receipt |
| Backup and recovery | Retained previous source/data revision, retrieval method and rollback reviewer |
| Ongoing responsibility | Maintainer, issue-reporting route and agreed support end date |

Do not put passwords, access tokens or private credentials into this record. Transfer access through the institution's account and repository controls.

## Demonstrate receipt

1. Have the recipient open the repository under their own account and locate the source, documentation and Actions history.
2. From the accepted release, build and run both publication verification scripts using [Website operations](WEBSITE_OPERATIONS.md).
3. Open the homepage, results dashboard, five-plant study and a labelled historical study.
4. In the spectral explorer, select FX10 and FX17, click different recorded pixels, change wavelength and download one spectrum CSV.
5. Open a 3D model and confirm the large scientific assets load. Record the dataset and actual browser result; a successful HTML response is insufficient.
6. Run the local preview with the network disconnected and repeat the agreed viewer/download checks. Record any external-resource exceptions.
7. Have the recipient retrieve a selected original dataset and intermediate result from the separate archive, compare checksums and open them.
8. Record acceptance, or named conditions with owners and due dates. Keep the transfer open until receipt is confirmed.

## What the website archive contains

`docs/dashboard-data-manifest.json` maps original scientific URLs to lossless chunks in `research-assets/`. `docs/spectral-publication-manifest.json` records the viewer package and omitted source-only files. The publication deliberately omits some analysis scripts, masks, screenshots and source-only intermediates; preserve them in the complete project archive.

Do not treat GitHub Pages, its compressed chunks, or a screenshot of a viewer as the sole long-term research archive. The project handover promises original datasets and intermediate as well as final results.

## Research descriptions to preserve

- Label August experimental 3D spectral fusion separately from September 2D spectral inspection and partial association experiments.
- Retain the source recording, wavelength, pixel index and units when moving scientific data.
- Keep conditional trait comparisons and exclusion reasons visible; display appearance is not an accuracy certificate.
- Spectral indices are exploratory indicators. Do not relabel raw digital numbers or provisional normalisation as validated reflectance or a plant-health diagnosis.

## Closure evidence

Save the accepted commit, build/check output, deployment URL/run, recipient access confirmation, disconnected-preview findings and archive restore receipt together. Stakeholder software access and a working lab application are valuable evidence but do not automatically establish website administrator access or custody of excluded research files.
