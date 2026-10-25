"""Serve the built website and local scientific archive on localhost only."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit
import argparse

ROOT = Path(__file__).resolve().parents[1]


class ResultsHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        decoded = unquote(urlsplit(path).path)
        if decoded.startswith('/__research_data__/'):
            archive = (ROOT / 'research-assets').resolve()
            target = (archive / decoded[len('/__research_data__/'):]).resolve()
            if not target.is_relative_to(archive):
                return str(archive / '__invalid_path__')
            return str(target)
        return super().translate_path(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8880)
    args = parser.parse_args()
    export = ROOT / 'out'
    if not export.is_dir() or not (ROOT / 'research-assets').is_dir():
        parser.error('Build out/ first and provide the complete research-assets/ folder.')
    handler = partial(ResultsHandler, directory=str(export))
    with ThreadingHTTPServer(('127.0.0.1', args.port), handler) as server:
        print(f'Open http://127.0.0.1:{args.port}/results/all/', flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()
