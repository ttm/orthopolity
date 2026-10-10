"""Independently verify source joins with Python's CSV reader, without fitting."""
import argparse
from collections import Counter
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'data/seismic-candidates/2026-10-10'


def identifier(text):
    return int(float(text)) if text and text.strip() and text.strip() not in ('0', 'NULL') else None


def horus_ids(archive, member, id_index):
    result, duplicates = {}, set()
    with archive.open(member) as raw, io.TextIOWrapper(raw) as stream:
        rows = csv.reader(stream, delimiter='\t')
        next(rows)
        for row in rows:
            key = identifier(row[id_index].strip())
            if key is None:
                continue
            if key in result:
                duplicates.add(key)
            result[key] = [value.strip() for value in row]
    for key in duplicates:
        del result[key]
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, default=BASE/'audit')
    args = parser.parse_args()
    result = json.loads((args.directory/'audit.json').read_text())
    with gzip.open(BASE/'raw/CLASS1.0_full.csv.gz', 'rt') as stream:
        class_rows = list(csv.DictReader(stream, delimiter=';'))
    class_ids = Counter(identifier(row['id_class']) for row in class_rows)
    ingv_ids = Counter(identifier(row['id_ingv']) for row in class_rows)
    with zipfile.ZipFile(BASE/'raw/HORUS_Ita_Catalog.zip') as archive:
        catalogue = horus_ids(archive, 'HORUS_Ita_Catalog_o.txt', 14)
        origin = horus_ids(archive, 'HORUS_Ita_DataOrigin_o.txt', 32)
    statuses, direct, proxy, missing_provenance = Counter(), 0, 0, 0
    with gzip.open(args.directory/'class-horus-crosswalk.csv.gz','rt') as stream:
        ledger = csv.DictReader(stream)
        for index, source in enumerate(class_rows, start=2):
            row = next(ledger)
            assert int(row['class_source_row']) == index
            key = identifier(source['id_ingv'])
            cid = identifier(source['id_class'])
            assert identifier(row['id_class']) == cid and identifier(row['id_ingv']) == key
            if key is None:
                status = 'missing_ingv_id'
            elif class_ids[cid] > 1 or ingv_ids[key] > 1:
                status = 'ambiguous_class_identifiers'
            elif key not in catalogue:
                status = 'no_unique_horus_match'
            elif key not in origin:
                status = 'no_unique_provenance_match'
            else:
                status = 'matched_catalogue_and_provenance'
                cat, prov = catalogue[key], origin[key]
                assert abs(float(row['horus_mw'])-float(cat[9])) < 1e-9
                assert abs(float(row['horus_sigma_mw'])-float(cat[10])) < 1e-9
                assert row['final_source'] == prov[27]
                is_direct = bool(prov[21] and prov[22] and prov[27].startswith('Mw '))
                assert (row['has_direct_mt_provenance'] == 'True') == is_direct
                direct += int(is_direct)
                proxy += int(bool(prov[27]) and not is_direct)
                missing_provenance += int(not prov[27])
            statuses[status] += 1
            assert status == row['join_status']
        assert next(ledger, None) is None
    expected = result['crosswalk']
    assert dict(statuses) == expected['status_counts']
    assert direct == expected['n_direct_mt_provenance']
    assert proxy == expected['n_proxy_provenance']
    assert missing_provenance == expected['n_missing_magnitude_provenance']
    assert direct//200 == expected['direct_mt_maximum_disjoint_200_event_groups']
    nocal_count, nocal_errors, nocal_ids, negative_depth = 0, 0, set(), 0
    with gzip.open(BASE/'raw/NCAeqDD.v202112.1.gz','rt') as stream:
        for line in stream:
            fields = line.split()
            if len(fields) != 15 or not fields[0].isdigit():
                continue
            nocal_count += 1
            nocal_ids.add(int(fields[-1]))
            nocal_errors += int(all(float(fields[i]) > 0 for i in [9,10,12]))
            negative_depth += int(float(fields[8]) < 0)
    nocal = result['northern_california']
    assert nocal_count == len(nocal_ids) == nocal['n_rows']
    assert nocal_errors == nocal['n_all_positive_finite_relative_error_fields']
    assert negative_depth == nocal['n_negative_depth']
    lookups = json.loads((BASE/'identity-lookups.json').read_text())['files']
    with (args.directory/'class-horus-time-discrepancies.csv').open() as stream:
        differences = {int(row['id_ingv']): row for row in csv.DictReader(stream)}
    assert set(differences) == {item['event_id'] for item in lookups}
    from datetime import datetime
    for item in lookups:
        path = ROOT/item['path']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item['sha256']
        row = list(csv.DictReader(path.read_text().splitlines(), delimiter='|'))[0]
        assert int(row['#EventID']) == item['event_id'] and row['EventType'] == item['event_type']
        official = datetime.fromisoformat(row['Time'])
        horus = datetime.fromisoformat(differences[item['event_id']]['horus_time']).replace(tzinfo=None)
        assert official == horus
    verification = dict(class_rows_independently_checked=len(class_rows),
        status_counts=dict(sorted(statuses.items())), direct_mt_provenance=direct,
        northern_california_rows_independently_checked=nocal_count,
        official_identity_lookups_matching_horus=len(lookups),
        quarry_blasts_among_time_discrepancies=sum(item['event_type']=='quarry blast' for item in lookups),
        response_estimators_called=False, valid=True)
    (args.directory/'verification.json').write_text(json.dumps(verification,indent=2)+'\n')
    print(json.dumps(verification,indent=2))


if __name__ == '__main__':
    main()
