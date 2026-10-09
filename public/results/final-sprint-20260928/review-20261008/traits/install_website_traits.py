"""Install only the owned trait component/table and additive review assets."""
from pathlib import Path
import json,shutil,hashlib
O=Path(__file__).resolve().parent;STAGE=O.parent;SITE=Path('/home/adithyarama/projects/PhenoFusion3D/phenofusion3d.github.io');PUBLIC=SITE/'public/results/final-sprint-20260928';target=PUBLIC/'review-20261008/traits'
assert str(SITE).startswith('/home/adithyarama/projects/PhenoFusion3D/')
assert target.is_relative_to(PUBLIC)
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
old=PUBLIC/'traits/website_tables.json';oldhash=sha(old)
component=SITE/'src/components/final-sprint/StudyTraits.tsx';shutil.copyfile(STAGE/'website_additions/StudyTraits.tsx',component)
shutil.copyfile(STAGE/'website_additions/website_tables_v3.json',PUBLIC/'traits/website_tables_v3.json')
shutil.copytree(O,target,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
assert sha(old)==oldhash
obj=json.loads((PUBLIC/'traits/website_tables_v3.json').read_text());dims=[d for p in obj['plants'] for d in p['dimensions']];comp=[d for d in dims if d['signed_difference_from_operator_annotation_cm'] is not None]
assert len(dims)==47 and len(comp)==13 and len({d['organ_id'] for d in comp})==8
assert (target/'index.html').is_file();assert sum(p.read_text(encoding='utf-8').count('class="table-scroll"') for p in [target/'index.html'])==3
files=[p for p in target.rglob('*') if p.is_file()]
receipt=dict(dimensions=47,conditional_comparisons=13,compared_organs=8,trait_artifact_files=len(files),trait_artifact_bytes=sum(p.stat().st_size for p in files),old_website_tables_sha256_unchanged=oldhash,component=str(component),new_table=str(PUBLIC/'traits/website_tables_v3.json'),review=str(target/'index.html'),new_table_sha256=sha(PUBLIC/'traits/website_tables_v3.json'))
(STAGE/'website_additions/trait_install_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
