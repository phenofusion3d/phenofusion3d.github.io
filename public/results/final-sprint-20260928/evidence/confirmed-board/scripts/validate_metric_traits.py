"""Local integrity and portability checks for current scientific trait outputs."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json,hashlib,sys
import numpy as np
ROOT=Path.cwd();BASE=ROOT/'generated/research_confirmed_board_20261007';OUT=BASE/'website/traits'
def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[]
    def handle_starttag(self,t,attrs):
        for k,v in attrs:
            if k in ('src','href') and v:self.links.append(v)
broken=[];escaped=[];checked=0
for p in OUT.rglob('*.html'):
    parser=Links();parser.feed(p.read_text(encoding='utf-8'))
    for href in parser.links:
        u=urlsplit(href)
        if u.scheme or u.netloc or not u.path:continue
        target=(p.parent/unquote(u.path)).resolve();checked+=1
        if not target.is_relative_to(OUT.resolve()):escaped.append([str(p.relative_to(OUT)),href])
        if not target.exists():broken.append([str(p.relative_to(OUT)),href])
data=load(OUT/'website_tables.json');manual=data['manual_dimensions'];old=load(ROOT/'generated/final_sprint_website_20261007/traits_site/website_tables.json')
assert len(manual)==47 and len({a['id'] for a in manual})==47
assert all(not a['eligible_for_accuracy_statistics'] for a in manual)
assert [(a['id'],a['annotation_cm'],a['ruler_cm']) for a in manual]==[(a['id'],a['annotation_cm'],a['ruler_cm']) for a in old['manual_dimensions']]
assert all(p['estimated_height_cm'] is None for p in data['plants'])
assert sum(p['points'] for p in data['plants'])==430060
assert data['metrics']['mae'] is None and data['metrics']['rmse'] is None and data['metrics']['mape'] is None
assert all(sha(OUT/a['path'])==a['sha256'] for a in data['manual_original_images'])
chords=load(OUT/'provisional_chords.json');counts=[]
for a in chords:
    if a['chord_cm'] is not None:
        assert all(e['current_cleaned_plant_id']==a['plant'] and e['current_cleanup_reason']==1 for e in a['endpoints'])
        counts.append(a['id'])
assert len(counts)==3
assert all(a['current_cleaned_visible_candidates']==0 for a in load(OUT/'missing_endpoint_recheck.json'))
for p in data['plants']:
    for key in ('photo','source_photo','manual_overview'):
        assert (OUT/p[key]).is_file(),(p['id'],key)
assert not broken and not escaped,(broken,escaped)
result=dict(status='passed',html_local_links_checked=checked,broken_links=broken,escaped_links=escaped,current_plants=5,current_points=430060,manual_dimensions=47,original_manual_annotations_and_ruler_candidates_unchanged=True,original_manual_images_verified=len(data['manual_original_images']),numerical_chords=counts,all_six_selected_chord_endpoints_retained_in_current_multiview_plant_core=True,two_missing_tip_searches_still_empty=True,accuracy_metric_count=0,physical_accuracy_validated=False)
(OUT/'portability_and_scientific_checks.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
