"""Acquire and verify the small published saltation archive; never inspect flux."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import datetime as dt
import hashlib
import json
from pathlib import Path
import ssl
import urllib.request

from orthopolity.saltation import read_wind, eligible

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'data/saltation/2026-10-14'
URLS = {
    'record.json': 'https://zenodo.org/api/records/291798',
    'SaltationWind_ThreeSites_30minute.xlsx': 'https://zenodo.org/api/records/291798/files/SaltationWind_ThreeSites_30minute.xlsx/content',
    'paper.xml': 'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC5462498/fullTextXML',
}


def encode(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n').encode()


def audit():
    config = json.loads((ROOT/'configs/saltation_qualification_2026-10-14.json').read_text())
    rows = read_wind(BASE/'SaltationWind_ThreeSites_30minute.xlsx')
    sites = {}
    for name in sorted({r['site'] for r in rows}):
        source = [r for r in rows if r['site'] == name]
        dates = sorted({r['date'] for r in source})
        days = []
        for day in dates:
            group = [r for r in source if r['date'] == day]
            good = [r for r in group if eligible(r, config)]
            stress = [r['tau'] for r in good]
            days.append(dict(date=day, source_intervals=len(group), eligible_intervals=len(good),
                             stress_range_Pa=[min(stress), max(stress)] if stress else None))
        sites[name] = dict(source_intervals=len(source), recorded_dates=len(dates), days=days)
    return dict(numerical_response_columns_read=False, numeric_columns_read='A:I only',
                sites=sites, rows=rows)


def verify():
    receipt = json.loads((BASE/'acquisition.json').read_text())
    if not receipt['complete'] or {e['name'] for e in receipt['files']} != set(URLS):
        raise ValueError('Incomplete source inventory')
    for item in receipt['files']:
        data = (BASE/item['name']).read_bytes()
        if len(data) != item['bytes'] or hashlib.sha256(data).hexdigest() != item['sha256']:
            raise ValueError('Changed source: '+item['name'])
    record = json.loads((BASE/'record.json').read_text())
    if str(record['id']) != '291798' or len(record['files']) != 1:
        raise ValueError('Wrong source record')
    item = record['files'][0]
    data = (BASE/item['key']).read_bytes()
    if item['checksum'] != 'md5:'+hashlib.md5(data).hexdigest() or len(data) != item['size']:
        raise ValueError('Publisher checksum mismatch')
    if encode(audit()) != (BASE/'predictor-audit.json').read_bytes():
        raise ValueError('Changed predictor audit')
    return dict(verified=True, sources=len(URLS), real_response_values_read=False)


def acquire():
    BASE.mkdir(parents=True, exist_ok=True)
    if (BASE/'acquisition.json').exists():
        return verify()
    def fetch(item):
        name, url = item
        start = dt.datetime.now(dt.timezone.utc).isoformat()
        request = urllib.request.Request(url, headers={'User-Agent':'OrthopolityResearch/1.0'})
        with urllib.request.urlopen(request, context=ssl.create_default_context(cafile='/etc/ssl/cert.pem'), timeout=90) as response:
            data = response.read(2_000_001)
            if len(data) > 2_000_000:
                raise ValueError('Unexpected source size')
            receipt = dict(name=name, requested_url=url, final_url=response.url,
                retrieval_started_utc=start, retrieval_completed_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
                bytes=len(data), sha256=hashlib.sha256(data).hexdigest(), http_status=response.status,
                tls_certificate_verification=True, headers=dict(response.headers))
        path = BASE/name
        if path.exists() and path.read_bytes() != data:
            raise ValueError('Refusing changed source overwrite')
        path.write_bytes(data)
        return receipt
    with ThreadPoolExecutor(max_workers=3) as pool:
        receipts = list(pool.map(fetch, URLS.items()))
    (BASE/'predictor-audit.json').write_bytes(encode(audit()))
    (BASE/'acquisition.json').write_bytes(encode(dict(complete=True,files=receipts)))
    return verify()


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--stage', choices=['acquire','verify'], default='verify')
    args = p.parse_args()
    print(json.dumps(acquire() if args.stage == 'acquire' else verify(), indent=2))
