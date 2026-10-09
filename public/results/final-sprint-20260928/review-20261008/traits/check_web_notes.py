from pathlib import Path
import json
p=Path('generated/research_sprint_review_20261008/website_additions/website_tables_v3.json');d=json.loads(p.read_text());
for a in d['plants']:
 print(a['id']);print('\n'.join(a['notes'])); print('example',list(a['dimensions'][0]))
