# PhenoFusion3D website

This repository publishes the PhenoFusion3D project website and interactive research results. The desktop application and acquisition software live in the separate [PhenoFusion3D software repository](https://github.com/PhenoFusion-3D/PhenoFusion3D).

- Website: https://phenofusion3d.github.io/
- All research results: https://phenofusion3d.github.io/results/all/
- Whole-plant spectral explorer: https://phenofusion3d.github.io/results/whole-plant-spectral-20260928/
- Publishing repository: https://github.com/phenofusion3d/phenofusion3d.github.io

## Start here

| Task | Guide |
| --- | --- |
| Take over access, releases and maintenance | [Website handover](docs/WEBSITE_HANDOVER.md) |
| Build, preview, deploy and recover | [Website operations](docs/WEBSITE_OPERATIONS.md) |
| Understand the results dashboard and archived data | [Dashboard publication](docs/dashboard-publication.md) |
| Understand the spectral viewer package | [Spectral publication](docs/spectral-publication.md) |

## Build and preview

Use Node.js 22, pnpm 9.15.0 (declared in `package.json`) and Python 3.10 or later for the verification and preview scripts. Install dependencies while online:

```sh
pnpm install --frozen-lockfile
pnpm build
python3 scripts/check-spectral-publication.py
python3 scripts/check-dashboard.py --out
python3 scripts/serve-results.py --port 8880
```

Open http://127.0.0.1:8880/results/all/ . The preview serves the built `out/` folder and the local scientific archive. Keep the server bound to localhost. Stop it with Ctrl+C.

`pnpm dev` is useful for interface development. For a complete report and scientific-data check, use the production export and preview command above. This is a static export; `pnpm start` is not the deployment method.

## Repository structure

| Path | Purpose |
| --- | --- |
| `src/app/` | Next.js pages and layouts |
| `src/components/` | Shared interface and scientific viewers |
| `public/` | Static reports, figures, scripts and viewer assets |
| `public/results/all/catalog.json` | Dashboard destinations |
| `research-assets/` | Lossless content-addressed scientific data chunks |
| `public/research-assets.js` | Maps original data URLs to archive chunks |
| `docs/dashboard-data-manifest.json` | Original byte lengths and SHA-256 checksums |
| `scripts/` | Publication verification and local preview |
| `.github/workflows/` | Pull request checks and GitHub Pages deployment |
| `out/` | Generated static export; rebuilt from source |

## Research interpretation

The August demonstration includes experimental spectral values associated with a 3D surface. The September whole-plant explorer provides recorded 2D spectra across both sensors, with tentative RGB context. These are different results. Preserve the dataset dates, provisional trait qualifications, raw-DN/reflectance distinctions and fusion limits when editing the site.

This website is a presentation and inspection package, not a complete archive of every original recording and research intermediate. The separate delivered dataset/results inventory must identify those materials and their institutional storage location.

## Publication and ownership

The deployment workflow builds `out/` and deploys it using GitHub Actions. A maintainer must confirm **Settings > Pages > Source: GitHub Actions** in the publishing repository. A push to a personal fork does not update the public site. Public large-file loading also depends on `raw.githubusercontent.com`; see the operations guide for offline preview and recovery.

Record the accepted website commit, named administrator and archive custodian at handover. A working website does not itself prove that repository administration or all research data have been transferred.
