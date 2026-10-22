"""Check released membrane values against original CSV cells independently.

This post-release provenance audit imports no production reader or analysis.
It opens only the chosen later-run sample CSV and optical-standard CSV. All
56 later absorbances must already have been released after the forecast seal.
Source-derived concentrations and unrelated archive members are not inspected.
"""

import argparse
import csv
from decimal import Decimal
import hashlib
import io
import json
import math
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
CONFIG = 'configs/membrane_exchange_2026-10-20.json'
QUALIFICATION = 'results/membrane-exchange-qualification-2026-10-20/qualification.json'
PREDICTION = 'results/membrane-exchange-forecast-2026-10-22/predictions.json'
RESULT = 'results/membrane-exchange-transfer-2026-10-22/result.json'
SAMPLE_MEMBER = 'Diffusion Testing/Sample Data/20250603_manual_PES_PEG25_AO_metadata.csv'
STANDARD_MEMBER = 'Diffusion Testing/UV_Vis_Calibration_Curves/20250603_manual_calibration_AO.csv'
EXPECTED_SOURCE_SHA256 = 'b50871afca499ae8d74873260a35cff5338388d1c4e6d52c4c3b53eace697c07'
TIMES = (0.0, 4.0, 21.3, 24.0, 27.5, 45.6, 48.0, 69.6)


def number(text):
    decimal = Decimal(str(text))
    value = float(decimal)
    if not decimal.is_finite() or not math.isfinite(value):
        raise ValueError('Nonfinite selected source value')
    return value


def rows(archive, member, required):
    if archive.namelist().count(member) != 1:
        raise ValueError('Missing or duplicate selected archive member')
    with archive.open(member) as binary:
        with io.TextIOWrapper(binary, encoding='utf-8-sig', newline='') as stream:
            reader = csv.DictReader(stream, strict=True)
            if (not reader.fieldnames or len(set(reader.fieldnames)) != len(reader.fieldnames)
                    or not set(required).issubset(reader.fieldnames)):
                raise ValueError('Unexpected selected CSV schema')
            for row in reader:
                if None in row or any(value is None for value in row.values()):
                    raise ValueError('Malformed selected CSV row')
                yield row


def audit(root=ROOT):
    root = Path(root)
    cfg = json.loads((root / CONFIG).read_text())
    documents = {}
    digests = {}
    for label, path in [('qualification', QUALIFICATION), ('prediction', PREDICTION), ('result', RESULT)]:
        raw = (root / path).read_bytes()
        documents[label] = json.loads(raw)
        digests[label + '_sha256'] = hashlib.sha256(raw).hexdigest()
    qualification, prediction, result = [documents[name] for name in ('qualification', 'prediction', 'result')]
    if (result['target_later_responses_decoded'] is not True
            or result['evaluation']['target_later_responses_decoded'] is not True):
        raise ValueError('This audit is authorized only after target release')
    if (result['prediction_sha256'] != digests['prediction_sha256']
            or result['qualification_sha256'] != digests['qualification_sha256']
            or prediction['qualification_sha256'] != digests['qualification_sha256']):
        raise ValueError('Released artifacts do not share the recorded sealed inputs')
    source_path = (root / cfg['source']).resolve()
    if not source_path.is_relative_to(root.resolve()):
        raise ValueError('Source must remain under the repository root')
    source_bytes = source_path.read_bytes()
    source_hash = hashlib.sha256(source_bytes).hexdigest()
    if (source_hash != EXPECTED_SOURCE_SHA256 or source_hash != cfg['source_sha256']
            or source_hash != qualification['source_sha256'] or source_hash != prediction['source_sha256']):
        raise ValueError('Source archive hash differs')
    selected = {}
    with ZipFile(io.BytesIO(source_bytes)) as archive:
        for row in rows(archive, SAMPLE_MEMBER, ('Sample', 'Hcell', 'Time', 'Abs_raw')):
            identity = (row['Sample'], row['Hcell'], number(row['Time']))
            if identity in selected:
                raise ValueError('Duplicate source sample identity')
            selected[identity] = number(row['Abs_raw'])
        standards = sorted((number(row['C_uM']), number(row['Abs_raw']))
                           for row in rows(archive, STANDARD_MEMBER, ('C_uM', 'Abs_raw')))
    expected_grid = {(f'PES_PEG25_AO_S{pair + 4}', f'H{pair}_C{chamber}', time)
                     for pair in range(1, 5) for chamber in (1, 2) for time in TIMES}
    if set(selected) != expected_grid or len(standards) != 5 or len({c for c, _ in standards}) != 5:
        raise ValueError('Selected source identity grid or standard set differs')

    def indexed(records):
        values = {}
        for row in records:
            identity = (row['sample'], row['chamber'], row['time_hours'])
            if identity in values:
                raise ValueError('Duplicate artifact identity')
            values[identity] = row['absorbance']
        return values

    source_later = {key: value for key, value in selected.items() if key[2] > 0}
    source_baselines = {key: value for key, value in selected.items() if key[2] == 0}
    if indexed(result['evaluation']['observations']) != source_later:
        raise ValueError('A released later absorbance differs from its original CSV cell')
    if indexed(qualification['inputs']['target_baselines']) != source_baselines:
        raise ValueError('A qualification baseline differs from its original CSV cell')
    forecast_baselines = {(row['sample'], row[chamber], 0.0): row[value]
                          for row in prediction['forecasts']['baseline_pairs']
                          for chamber, value in [('donor_chamber', 'donor_raw'),
                                                 ('recipient_chamber', 'recipient_raw')]}
    if forecast_baselines != source_baselines:
        raise ValueError('A forecast baseline differs from its original CSV cell')
    recorded_standards = sorted((row['concentration_uM'], row['absorbance'])
                                for row in qualification['inputs']['target_standards'])
    if recorded_standards != standards:
        raise ValueError('A target optical standard differs from its original CSV cells')
    return dict(
        source_sha256=source_hash, **digests,
        design_commit=result['design_commit'], implementation_commit=result['implementation_commit'],
        prediction_commit=result['prediction_commit'], selected_members=[SAMPLE_MEMBER, STANDARD_MEMBER],
        later_observation_records=len(source_later), baseline_records=len(source_baselines),
        optical_standard_records=len(standards), unique_selected_numeric_values=74,
        forecast_baseline_values_rechecked=8, exact_binary_float_matches=True,
        maximum_absolute_difference=0.0, production_reader_imported=False,
        source_derived_values_used=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    report = audit()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as stream:
        json.dump(report, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps(report, sort_keys=True))


if __name__ == '__main__':
    main()
