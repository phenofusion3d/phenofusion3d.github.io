# Website operations

## Runtime and build

The application uses Next.js 14, React 18, Three.js and a static export. `next.config.js` enables `output: "export"`, trailing slashes and unoptimised static images. Node.js 22 matches the deployment workflow; `package.json` selects pnpm 9.15.0. Use the checked-in lockfile.

```sh
pnpm install --frozen-lockfile
pnpm build
python3 scripts/check-spectral-publication.py
python3 scripts/check-dashboard.py --out
```

The scripts verify packaged assets, decoded archive hashes, spectral rows, catalogue destinations, local links and the repository's conservative 950,000,000-byte export budget. They do not establish new scientific accuracy, physical laboratory operation or stakeholder acceptance.

## Local and offline viewing

```sh
python3 scripts/serve-results.py --port 8880
```

Open http://127.0.0.1:8880/results/all/ . The server exposes `out/` and maps `/__research_data__/` to the repository's `research-assets/` folder. This mapping is required: serving only `out/` with a generic file server will leave archived scientific files unavailable. Use an HTTP URL rather than double-clicking HTML files.

For disconnected viewing, deliver the complete source/data checkout and an already-built `out/` export, with Python available. Do dependency installation and build before disconnecting. Keep `research-assets/` alongside `out/` under the same repository root. Use a modern browser with gzip `DecompressionStream` support.

The local archive removes the large-data dependency on GitHub for the mapped assets. It does not guarantee that every external video, font or linked page works offline. Test each agreed report, 3D model, FX10/FX17 spectrum and download with the network disconnected and record exceptions. The YouTube pitch requires network access unless an authorised local MP4 copy is delivered separately.

## GitHub Pages deployment

1. Confirm the target is `phenofusion3d/phenofusion3d.github.io`, not a personal fork.
2. An administrator confirms **Settings > Pages > Build and deployment > Source: GitHub Actions**.
3. Submit source changes for review. `.github/workflows/check-publication.yml` builds and checks pull requests to main/master using a frozen lockfile.
4. After merge, `.github/workflows/deploy-pages.yml` builds, verifies and uploads `out/`, then deploys using the `github-pages` environment.
5. Confirm the deployment run and inspect the live homepage, dashboard, spectral values and one large model/download.

The deployment currently uses `pnpm install`; the pull-request check uses `pnpm install --frozen-lockfile`. Preserve the lockfile and review dependency changes deliberately.

Do not switch Pages to build the repository source root as a shortcut. This can publish the README instead of the intended Next.js export. If you lack Pages settings access, have the administrator check the source and the active deployment. Re-run the known workflow or redeploy a known-good export through the authorised publishing process; do not create competing deployment sources without agreement.

## Scientific archive maintenance

`public/research-assets.js` contains the mapping and immutable public data commit. Large data load from `raw.githubusercontent.com/phenofusion3d/phenofusion3d.github.io/<commit>/research-assets/` in public viewing. On localhost the loader uses `/__research_data__/` unless the page has the `remoteData` query parameter.

Keep the manifest, loader and chunks consistent. The server-side verification scripts check SHA-256; the browser loader verifies decoded byte length. A correct browser file size alone does not replace the archive checksum check.

When adding scientific data:

1. Preserve originals and record the producing code revision, input, parameters, units and limitations.
2. Create lossless content-addressed chunks and update the data manifest and loader through the existing publication process.
3. Ensure the immutable data commit is available in the publishing repository before making the loader depend on it.
4. Run both publication checks and inspect representative spectrum/model downloads in the browser.
5. Retain the previous source and data revisions for rollback. Remove duplicate copies only after verifying the retained bytes and links.

An HTTP-only mirror of `out/` is not a complete backup. Preserve `research-assets/`, manifests, source and the producing repository history, plus the separate full research archive.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| Homepage displays a plain README | Pages source and active deployment; ensure the workflow deploys `out/` |
| Reports open but spectra/models fail | Archive chunks, immutable data commit, browser console and access to raw.githubusercontent.com |
| Local spectra/models return 404 | Start `scripts/serve-results.py`; check `research-assets/` is present |
| Spectrum values do not change | Selected recorded pixel/band, scene loading and actual CSV output; do not rely only on colour |
| Build or link checker fails | First failing path, manifest consistency, lockfile and export size |
| Deployment has unexpected content | Compare accepted source SHA, workflow run and active Pages artifact |

For recovery, identify the last known-good source and matching data revision, rebuild/check it, then redeploy through the same reviewed workflow. Do not delete historical data commits referenced by a published loader.
