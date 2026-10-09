"""Verify the self-contained static publication, using only Python's stdlib."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import gzip, hashlib, json

site = Path(__file__).resolve().parents[1]
out = site / 'out'
root = out / 'results/whole-plant-spectral-20260928'
receipt = json.loads((site / 'docs/spectral-publication-manifest.json').read_text())
assert out.is_dir(), 'Run pnpm build first'
mapping = json.loads((site / 'docs/dashboard-data-manifest.json').read_text())
def present(p):
    return p.exists() or '/'+p.relative_to(out).as_posix() in mapping
def read(p):
    if p.is_file(): return p.read_bytes()
    item = mapping['/'+p.relative_to(out).as_posix()]
    data = b''.join((site/'research-assets'/chunk).read_bytes() for chunk in item['chunks'])
    if item['encoding'] == 'gzip': data = gzip.decompress(data)
    assert hashlib.sha256(data).hexdigest() == item['sha256']
    return data
for rel, expected in receipt['files'].items():
    p = root / rel
    assert present(p), f'Missing published asset: {rel}'
    assert hashlib.sha256(read(p)).hexdigest() == expected, f'Changed asset: {rel}'

manifest = json.loads((root / 'manifest.json').read_text())
rows = previews = pixels = 0
for name, sensor in manifest['sensors'].items():
    assert len(sensor['wavelength_nm']) == sensor['bands'] == 224
    pixels += sensor['pixel_count']
    assert (root / sensor['composite']).is_file()
    refs = gzip.decompress(read(root / sensor['references']))
    assert len(refs) == sensor['columns'] * sensor['bands'] * 4 * 4
    for line in range(sensor['lines']):
        rel = sensor['row_template'].replace('{line}', f'{line:04d}')
        raw = gzip.decompress(read(root / rel))
        assert len(raw) == sensor['columns'] * sensor['bands'] * 2, rel
        rows += 1
    for band in sensor['band_previews']:
        assert (root / band['file']).stat().st_size == band['bytes'], band['file']
        previews += 1
assert pixels == 3539328

class Links(HTMLParser):
    def __init__(self): super().__init__(); self.links = []
    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in {'href', 'src'} and value:
                self.links.append(value)

pages = list(root.rglob('*.html')) + [out / 'experimental-results/viewer/rgbd_icp/validation/validation_report.html']
links = 0
for page in pages:
    parser = Links(); parser.feed(page.read_text())
    for href in parser.links:
        url = urlsplit(href)
        if url.scheme or url.netloc or not url.path:
            continue
        path = unquote(url.path)
        target = (out / path.lstrip('/')) if path.startswith('/') else page.parent / path
        assert target.resolve().is_relative_to(out.resolve()), (page, href)
        assert present(target), f'Broken link in {page.relative_to(out)}: {href}'
        links += 1

for entry in receipt['historical_duplicates_removed']:
    assert not (site / entry['removed']).exists()
    assert (site / entry['retained']).exists()
files = [p for p in out.rglob('*') if p.is_file()]
size = sum(p.stat().st_size for p in files)
assert size < 950_000_000, f'Static site exceeds 950 MB safety budget: {size}'
assert max(p.stat().st_size for p in files) < 100_000_000
print(json.dumps({'status':'passed', 'hashed_assets':len(receipt['files']), 'rows':rows,
    'band_previews':previews, 'pixels':pixels, 'checked_static_links':links,
    'site_bytes':size, 'site_files':len(files), 'budget_bytes':950_000_000,
    'duplicate_bytes_saved':receipt['duplicate_bytes_saved'],
    'intermediate_bytes_not_deployed':receipt['intermediate_bytes_not_deployed']}, indent=2))
