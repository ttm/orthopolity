"""Verify all pinned basin archives; --restore retrieves missing files only."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--restore', action='store_true')
    args = parser.parse_args()
    manifest = json.loads((ROOT/'data/hydrobasins/2026-10-09/acquisition.json').read_text())
    for item in manifest['archives']:
        path = ROOT/item['path']
        if not path.exists():
            if not args.restore:
                parser.error('Missing basin archive; use --restore for publisher download')
            path.parent.mkdir(parents=True, exist_ok=True)
            part = path.with_suffix('.zip.part')
            subprocess.run(['curl', '--fail', '--location', '--retry', '2', '--connect-timeout',
                            '30', '--max-time', '180', '--output', str(part), item['url']], check=True)
            if part.stat().st_size != item['bytes'] or hashlib.sha256(part.read_bytes()).hexdigest() != item['sha256']:
                raise ValueError('Publisher source changed; partial file retained')
            part.replace(path)
        if path.stat().st_size != item['bytes'] or hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
            raise ValueError(f'Altered basin archive: {path.name}')
        with zipfile.ZipFile(path) as archive:
            if archive.testzip() is not None:
                raise ValueError(f'Failed ZIP integrity: {path.name}')
    print(json.dumps(dict(archives=len(manifest['archives']), verification='all SHA256, size and ZIP CRC checks pass')))


if __name__ == '__main__':
    main()
