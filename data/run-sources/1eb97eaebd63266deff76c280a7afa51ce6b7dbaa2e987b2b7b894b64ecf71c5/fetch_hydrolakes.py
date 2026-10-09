"""Verify the retained HydroLAKES source; --restore downloads missing bytes.

The 820 MB archive and 1.5 GB extraction are deliberately excluded from Git.
Existing altered files cause failure rather than being silently overwritten.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile
import zlib

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/hydrolakes/2026-10-09'


def file_crc(path):
    crc = 0
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            crc = zlib.crc32(chunk, crc)
    return f'{crc:08x}'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--restore', action='store_true')
    args = parser.parse_args(argv)
    manifest = json.loads((DATA / 'acquisition.json').read_text())
    archive = DATA / 'HydroLAKES_polys_v10_shp.zip'
    if not archive.exists():
        if not args.restore:
            parser.error('Archive absent. Run with --restore to download the registered public source.')
        part = archive.with_suffix('.zip.part')
        subprocess.run(['curl', '--fail', '--location', '--retry', '2',
                        '--connect-timeout', '30', '--max-time', '1800',
                        '--output', str(part), manifest['url']], check=True)
        with part.open('rb') as handle:
            digest = hashlib.file_digest(handle, 'sha256').hexdigest()
        if part.stat().st_size != manifest['bytes'] or digest != manifest['sha256']:
            raise ValueError('Downloaded bytes changed; partial file retained for inspection')
        part.rename(archive)
    with archive.open('rb') as handle:
        digest = hashlib.file_digest(handle, 'sha256').hexdigest()
    if archive.stat().st_size != manifest['bytes'] or digest != manifest['sha256']:
        raise ValueError('Local archive differs from the registered source')
    extraction = DATA / 'extracted'
    with zipfile.ZipFile(archive) as zipped:
        for member in manifest['members']:
            if member['name'].endswith('/'):
                continue
            path = extraction / member['name']
            if not path.resolve().is_relative_to(extraction.resolve()):
                raise ValueError('Archive member escapes the extraction directory')
            if not path.exists():
                if not args.restore:
                    parser.error('Extracted member absent; --restore recreates missing members.')
                zipped.extract(member['name'], extraction)
            if path.stat().st_size != member['bytes'] or file_crc(path) != member['crc32']:
                raise ValueError(f'Extracted source altered: {member["name"]}')
    print(json.dumps({'archive_sha256': digest, 'archive_bytes': archive.stat().st_size,
                      'extracted_file_checks': 'all pass'}, indent=2))


if __name__ == '__main__':
    main()
