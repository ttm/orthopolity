"""Verify retained public source bytes without decoding response data."""
import hashlib
import json
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1] / 'data/physics-candidates/2026-10-23/topology'
    receipt = json.loads((root / 'acquisition.json').read_text())
    for record in receipt['files']:
        path = root / record['file']
        if path.parent != root:
            raise ValueError('Expected a source basename')
        data = path.read_bytes()
        if len(data) != record['bytes'] or hashlib.sha256(data).hexdigest() != record['sha256']:
            raise ValueError(f'Source bytes changed: {path}')
    print(json.dumps(dict(verified_source_files=len(receipt['files']),
                         numerical_response_arrays_decoded=False), indent=2))


if __name__ == '__main__':
    main()
