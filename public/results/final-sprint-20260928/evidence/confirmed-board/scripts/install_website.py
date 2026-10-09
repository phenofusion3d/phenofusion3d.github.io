"""Run in the requested WSL checkout; local copy only, no push/deployment."""
from pathlib import Path
import hashlib,json,shutil,subprocess
BASE=Path(__file__).resolve().parent
SITE=Path('/home/adithyarama/projects/PhenoFusion3D/phenofusion3d.github.io').resolve()
assert SITE.is_dir() and (SITE/'.git').exists()
assert json.loads((SITE/'package.json').read_text())['name']=='phenofusion3d-site'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
before={str(p.relative_to(SITE)):digest(p) for p in [SITE/'src/components/Navbar.tsx',SITE/'src/components/ResultsNavigation.tsx']}
src=BASE/'site_src';assets=BASE/'website'
assert (assets/'website_provenance.json').exists()
route=SITE/'src/app/results/final-sprint-20260928'
components=SITE/'src/components/final-sprint'
public=SITE/'public/results/final-sprint-20260928'
for p in [route,components,public]:p.mkdir(parents=True,exist_ok=True)
for name in ['page.tsx','study.css','study-data.json']:shutil.copy2(src/name,route/name)
for name in ['StudyGeometryViewer.tsx','StudyInspectors.tsx','StudyTraits.tsx']:shutil.copy2(src/name,components/name)
shutil.copytree(assets,public,dirs_exist_ok=True)
navigation=SITE/'src/components/ResultsNavigation.tsx';text=navigation.read_text()
if '/results/final-sprint-20260928/' not in text:
    text=text.replace('  ["/", "Home"],','  ["/", "Home"],\n  ["/results/final-sprint-20260928/", "Five-plant final sprint"],')
    navigation.write_text(text)
navbar=SITE/'src/components/Navbar.tsx';text=navbar.read_text()
if '/results/final-sprint-20260928/' not in text:
    text=text.replace('const navLinks = [','const navLinks = [\n  { href: `${process.env.NEXT_PUBLIC_BASE_PATH ?? ""}/results/final-sprint-20260928/`, label: "Five plants" },')
    # Keep the full menu readable at intermediate desktop sizes.
    text=text.replace('xl:flex','2xl:flex').replace('xl:hidden','2xl:hidden')
    navbar.write_text(text)
manifest=json.loads((assets/'website_provenance.json').read_text())
for row in manifest['files']:
    target=public/row['path'];assert target.exists() and digest(target)==row['sha256'],row['path']
assert digest(assets/'website_provenance.json')==digest(public/'website_provenance.json')
receipt=dict(site=str(SITE),route='/results/final-sprint-20260928/',asset_count=len(manifest['files'])+1,all_copied_asset_hashes_match=True,prior_navigation_hashes=before,
    new_navigation_hashes={str(p.relative_to(SITE)):digest(p) for p in [navigation,navbar]},pushed=False,source_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=SITE,text=True).strip())
(BASE/'website_install_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
(SITE/'FINAL_SPRINT_20260928.md').write_text('''# Five-plant final-sprint results

Route: `/results/final-sprint-20260928/`.

This is the confirmed-board edition of the 28 September 2026 capture. Saswat
confirmed 25 mm squares, 18 mm markers, a 7 x 10 layout and DICT_4X4_50.
The old result pages remain available as historical work.

The page includes 24 full-resolution geometry selections (D405, aligned L515,
fused and cleaned; all plants and P1-P5 individually), compressed PLY downloads,
point provenance, all 47 manual-reference dispositions, both hyperspectral
camera inspectors and all-sample quality/index diagnostics. Six provisional
spectra refer to three P5 vertices; this is not dense spectral fusion across
the plants. The attempted height model failed held-out prediction and is
documented rather than used to manufacture assignments.

`public/results/final-sprint-20260928/website_provenance.json` records asset
hashes. `study_requirements.json` separates completed outputs from unresolved
scientific requirements. The evidence directory includes calibration,
cross-camera selection, cleanup and numerical checks. Cloud display is Y-up;
downloaded PLY coordinates retain the documented D405 reference frame.

The new scale anchors lengths to the supplied board, but print tolerance,
device metadata, anatomical endpoint correspondence, calibrated reflectance,
hidden surfaces and independent physical accuracy remain limited. The source
recordings and full-scene research runs remain in the PhenoFusion3D research
workspace. Protected lab capture/gantry source was not changed for this page.

Build locally with `pnpm build`; the static export is `out/`. The usual
NEXT_PUBLIC_BASE_PATH setting is respected. This task prepares a local result;
it does not push, deploy or establish live publication. Review and push through
the existing GitHub Pages workflow when ready.
''',encoding='utf-8')
print(json.dumps(receipt,indent=2))
