"""Read-only static-export link and asset audit for the new study route."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse,unquote
import argparse,json,hashlib
class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        for name,value in attrs:
            if value and name in ('href','src') and tag in ('a','img','script','link','iframe','source'):
                self.links.append((tag,value))
def main(root):
    root=Path(root).resolve();route=root/'results/final-sprint-20260928'
    errors=[];checked=0;external=set()
    for p in route.rglob('*.html'):
        parser=Links();parser.feed(p.read_text(encoding='utf-8'))
        for tag,url in parser.links:
            u=urlparse(url)
            if u.scheme or u.netloc:external.add(url);continue
            if not u.path or u.path.startswith('data:'):continue
            if '{' in u.path:continue
            target=(root/unquote(u.path).lstrip('/') if u.path.startswith('/') else p.parent/unquote(u.path)).resolve()
            if target.is_dir():target=target/'index.html'
            checked+=1
            if not target.is_file():errors.append(dict(page=str(p.relative_to(root)),tag=tag,url=url,resolved=str(target)))
    manifest=json.loads((route/'geometry/manifest.json').read_text())
    assert len(manifest['models'])==24
    for row in manifest['models']:
        for field in ['file','download','provenance']:
            p=route/'geometry'/row[field]
            assert p.exists(),str(p)
        p=route/'geometry'/row['file']
        assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
    result=dict(status='pass' if not errors else 'fail',html_pages=len(list(route.rglob('*.html'))),local_references_checked=checked,external_reference_count=len(external),geometry_models_verified=24,errors=errors)
    output=Path(__file__).resolve().parent/'website_link_validation.json';output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2));assert not errors,'Broken exported links'
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('root');main(parser.parse_args().root)
