"""Verify lossless archive, catalogue coverage and local report links."""
from pathlib import Path
from urllib.parse import urlsplit,unquote
from html.parser import HTMLParser
import gzip,hashlib,json,sys

SITE=Path(__file__).resolve().parents[1]
ROOT=SITE/('out' if '--out' in sys.argv else 'public')
mapping=json.loads((SITE/'docs/dashboard-data-manifest.json').read_text())
def read_asset(url):
    item=mapping[url]
    data=b''.join((SITE/'research-assets'/p).read_bytes() for p in item['chunks'])
    if item['encoding']=='gzip':data=gzip.decompress(data)
    assert len(data)==item['bytes'] and hashlib.sha256(data).hexdigest()==item['sha256'],url
    return data
verified=set()
for url,item in mapping.items():
    if item['sha256'] not in verified:
        data=read_asset(url);verified.add(item['sha256'])
    original=SITE/'public'/url.lstrip('/')
    if original.is_file():assert hashlib.sha256(original.read_bytes()).hexdigest()==item['sha256'],url

def exists(path):
    path=path.resolve()
    assert path.is_relative_to(ROOT.resolve()),path
    url='/'+path.relative_to(ROOT.resolve()).as_posix()
    return path.exists() or url in mapping
catalog=json.loads((ROOT/'results/all/catalog.json').read_text())
for item in catalog:
    url=urlsplit(item['url']);p=ROOT/unquote(url.path).lstrip('/')
    if url.path.endswith('/'):p=p/'index.html'
    # The Next study HTML is produced at build time.
    if '--out' not in sys.argv and ((SITE/'src/app'/url.path.strip('/')/'page.tsx').is_file() or url.path=='/index.html'):continue
    assert exists(p),item['url']
class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        for k,v in attrs:
            if k in {'href','src','poster'} and v:self.links.append(v)
missing=[];count=0
for html in ROOT.rglob('*.html'):
    parser=Links();parser.feed(html.read_text(errors='replace'))
    for href in parser.links:
        u=urlsplit(href)
        if u.scheme or u.netloc or not u.path:continue
        p=ROOT/unquote(u.path).lstrip('/') if u.path.startswith('/') else html.parent/unquote(u.path)
        if not exists(p):missing.append((str(html.relative_to(ROOT)),href))
        count+=1
if '--out' in sys.argv:
    assert not missing, json.dumps(missing[:40])
size=sum(p.stat().st_size for p in ROOT.rglob('*') if p.is_file())
if '--out' in sys.argv:assert size<950_000_000,size
print(json.dumps({'archive_urls':len(mapping),'unique_verified_data_files':len(verified),'catalogue_destinations':len(catalog),'html_links_checked':count,'missing_before_build':missing[:30],'bytes':size,'passed':True},indent=2))
