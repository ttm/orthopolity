"""Seal membrane forecasts before the first numerical later-cohort access."""

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

from orthopolity.membrane_exchange_source import read_membrane_archive
from orthopolity.membrane_exchange_transfer import forecast, evaluate
from run_membrane_exchange import encode, frozen_commit, qualification_document, verify_sources
from verify_membrane_exchange import verify as verify_qualification
from verify_membrane_transfer import verify_predictions


ROOT = Path(__file__).resolve().parents[1]
QUALIFICATION = 'results/membrane-exchange-qualification-2026-10-20'
FROZEN = [
    'src/orthopolity/membrane_exchange_transfer.py',
    'experiments/run_membrane_transfer.py',
    'experiments/verify_membrane_transfer.py',
    'tests/test_membrane_exchange_transfer.py',
    'tests/test_membrane_transfer_verification.py',
    'tests/test_membrane_transfer_staging.py',
    *(QUALIFICATION + '/' + name for name in
      ('qualification.json', 'verification.json', 'execution.json')),
]


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def freeze(ref, paths):
    if not ref:
        raise ValueError('A committed implementation/forecast reference is required')
    full = subprocess.check_output(['git', 'rev-parse', ref], cwd=ROOT, text=True).strip()
    for name in paths:
        committed = subprocess.check_output(['git', 'show', f'{full}:{name}'], cwd=ROOT)
        if committed != (ROOT / name).read_bytes():
            raise ValueError('Frozen file changed: ' + name)
    return full


def ancestor(earlier, later):
    subprocess.run(['git', 'merge-base', '--is-ancestor', earlier, later], cwd=ROOT, check=True)


def checked_qualification():
    cfg = verify_sources()
    raw = (ROOT / QUALIFICATION / 'qualification.json').read_bytes()
    doc = json.loads(raw)
    design = frozen_commit(doc['design_commit'])
    if not doc['qualification']['passed'] or doc['target_later_responses_decoded'] is not False:
        raise ValueError('The original qualification did not authorize transfer')
    if encode(qualification_document(design)) != raw:
        raise ValueError('Qualification replay differs')
    checked = verify_qualification(doc, cfg)
    checked['qualification_sha256'] = digest(raw)
    if checked != json.loads((ROOT / QUALIFICATION / 'verification.json').read_text()):
        raise ValueError('Independent qualification verification differs')
    return doc, raw


def prediction_document(implementation, qualification, raw):
    return dict(
        study=qualification['study'], design_commit=qualification['design_commit'],
        implementation_commit=implementation, qualification_sha256=digest(raw),
        source_sha256=qualification['source_sha256'], target_later_responses_decoded=False,
        forecasts=forecast(qualification))


def checked_prediction(implementation, qualification, raw, path, reference):
    name = path.resolve().relative_to(ROOT).as_posix()
    verification_path = path.with_name('verification.json')
    verification_name = verification_path.resolve().relative_to(ROOT).as_posix()
    sealed = freeze(reference, [name, verification_name])
    ancestor(implementation, sealed)
    saved = path.read_bytes()
    document = prediction_document(implementation, qualification, raw)
    if encode(document) != saved:
        raise ValueError('Committed forecast replay differs')
    verified = verify_predictions(document, qualification)
    verified['prediction_sha256'] = digest(saved)
    if verified != json.loads(verification_path.read_text()):
        raise ValueError('Committed independent prediction verification differs')
    return document, saved, sealed


def evaluate_document(prediction, raw_prediction, sealed, qualification):
    # The only positive-time target decoder in this driver is deliberately
    # downstream of all qualification, code-freeze, seal and replay checks.
    source = read_membrane_archive(ROOT / qualification['config']['source'], allow_target=True)
    rows = [asdict(row) for row in source.target_observations]
    if len(rows) != qualification['config']['withheld_target_observations']:
        raise ValueError('Unexpected numerical target count')
    return dict(
        study=prediction['study'], design_commit=prediction['design_commit'],
        implementation_commit=prediction['implementation_commit'], prediction_commit=sealed,
        prediction_sha256=digest(raw_prediction), qualification_sha256=prediction['qualification_sha256'],
        target_later_responses_decoded=True,
        evaluation=evaluate(prediction['forecasts'], rows))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=['predict', 'evaluate'], required=True)
    parser.add_argument('--freeze-commit', required=True)
    parser.add_argument('--prediction-commit')
    parser.add_argument('--predictions', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    implementation = freeze(args.freeze_commit, FROZEN)
    qualification, raw = checked_qualification()
    ancestor(qualification['design_commit'], implementation)
    if args.output.exists():
        raise FileExistsError(args.output)
    if args.stage == 'evaluate':
        if args.predictions is None or args.prediction_commit is None:
            parser.error('Evaluation requires committed and independently verified predictions')
        prediction, raw_prediction, sealed = checked_prediction(
            implementation, qualification, raw, args.predictions, args.prediction_commit)
    args.output.mkdir(parents=True, exist_ok=False)
    started = datetime.now(timezone.utc).isoformat()
    if args.stage == 'predict':
        result = prediction_document(implementation, qualification, raw)
        filename, count = 'predictions.json', 0
    else:
        result = evaluate_document(prediction, raw_prediction, sealed, qualification)
        filename, count = 'result.json', 56
    encoded = encode(result)
    (args.output / filename).write_bytes(encoded)
    receipt = dict(stage=args.stage, started_utc=started,
                   completed_utc=datetime.now(timezone.utc).isoformat(),
                   design_commit=qualification['design_commit'], implementation_commit=implementation,
                   artifact_sha256=digest(encoded), later_target_observations_decoded=count)
    if args.stage == 'evaluate':
        receipt['prediction_commit'] = sealed
    (args.output / 'execution.json').write_bytes(encode(receipt))
    print(json.dumps(dict(stage=args.stage, output=str(args.output / filename),
                          later_target_observations_decoded=count)))


if __name__ == '__main__':
    main()
