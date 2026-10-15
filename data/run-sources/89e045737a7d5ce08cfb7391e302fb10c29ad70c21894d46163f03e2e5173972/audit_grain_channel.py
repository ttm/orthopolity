"""Verify/restore the public source archive and rebuild its predictor-only audit."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import ssl
import urllib.request

from orthopolity.grain_channel import read_predictors

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'data/grain-channel/2026-10-15'


def encode(obj):
    return (json.dumps(obj, indent=2, sort_keys=True, allow_nan=False)+'\n').encode()


def verify_sources(base=BASE, restore=False):
    receipt = json.loads((base/'acquisition.json').read_text())
    for item in receipt['files']:
        path = base/item['name']
        if restore and not path.exists():
            with urllib.request.urlopen(item['requested_url'], timeout=60,
                    context=ssl.create_default_context(cafile='/etc/ssl/cert.pem')) as response:
                data = response.read(item['bytes']+1)
            if hashlib.sha256(data).hexdigest() != item['sha256']:
                raise ValueError('Changed remote source: '+item['name'])
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        data = path.read_bytes()
        if len(data) != item['bytes'] or hashlib.sha256(data).hexdigest() != item['sha256']:
            raise ValueError('Changed source: '+item['name'])
    checksums = dict(re.findall(r'Filename/Fichier: (.*?)\s*\nSHA256 Checksum/Sommes de contrôle: ([0-9a-f]{64})',
                               (base/'frdr-dfdr-checksums.txt').read_text()))
    checked = 0
    for item in receipt['files']:
        name = item['name']
        if name == 'frdr-dfdr-checksums.txt':
            continue
        if checksums.get(name) != item['sha256']:
            raise ValueError('Publisher checksum mismatch: '+name)
        checked += 1
    return dict(sources=len(receipt['files']), publisher_checksums=checked)


def audit():
    data = read_predictors(BASE)
    data.update(reference_measure='equal grain cohort, then equal run; neither log-orthopolic nor linear-orthopolic size allocation',
                numerical_transport_columns_converted=False,
                prior_exposure=dict(published_qualitative_outcomes=True,
                    wide_target_count=1, wide_target='S1 row 2 / gb_5_01',
                    wide_mass_flux_kg_s='0.0115909333333333',
                    explanation='Accidental first-data-row display in a separate metadata audit; all nine targets retained.'))
    return data


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--stage', choices=['audit','verify','restore'], default='verify')
    args = p.parse_args()
    result = verify_sources(restore=args.stage == 'restore')
    content = encode(audit())
    dest = BASE/'predictor-audit.json'
    if args.stage == 'audit':
        dest.write_bytes(content)
    elif content != dest.read_bytes():
        raise ValueError('Predictor audit changed')
    print(json.dumps(dict(verified=True, **result, numerical_transport_columns_converted=False)))
