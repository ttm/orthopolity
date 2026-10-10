"""Verify pinned candidate sources offline; --restore retrieves only missing files."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT/'data/seismic-candidates/2026-10-10/acquisition.json'


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def verify(restore=False):
    manifest = json.loads(MANIFEST.read_text())
    for item in manifest['files']:
        path = ROOT/item['path']
        if not path.exists():
            if not restore:
                raise FileNotFoundError(f'{path}: restore the pinned public source with --restore')
            path.parent.mkdir(parents=True, exist_ok=True)
            part = path.with_name(path.name+'.part')
            subprocess.run(['curl', '--fail', '--location', '--retry', '2', '--connect-timeout',
                            '30', '--max-time', '600', '--output', str(part), item['url']], check=True)
            if part.stat().st_size != item['bytes'] or digest(part) != item['sha256']:
                raise ValueError('Publisher source changed; partial file retained, snapshot not replaced')
            part.replace(path)
        if path.stat().st_size != item['bytes'] or digest(path) != item['sha256']:
            raise ValueError(f'Changed source bytes: {path}')
    return dict(files=len(manifest['files']), valid=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--restore', action='store_true')
    print(json.dumps(verify(parser.parse_args().restore), indent=2))
