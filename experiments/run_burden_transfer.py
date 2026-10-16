"""Freeze an assay-to-cell prediction before opening new-protein outcomes."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np
from orthopolity.burden_transfer import read_inputs, read_outcomes, fit_models, predict, score

ROOT = Path(__file__).resolve().parents[1]
CONFIG = 'configs/burden_transfer_2026-10-16.json'
FROZEN = ['src/orthopolity/burden_transfer.py', 'experiments/run_burden_transfer.py',
          'experiments/verify_burden_transfer.py', 'tests/test_burden_transfer.py', CONFIG,
          'docs/burden-transfer-protocol-2026-10-16.md',
          'data/biology-candidates/2026-10-16/borkowski2018/acquisition.json']


def encode(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n').encode()


def freeze(ref, files):
    full = subprocess.check_output(['git', 'rev-parse', ref], cwd=ROOT, text=True).strip()
    for name in files:
        if subprocess.check_output(['git', 'show', f'{full}:{name}'], cwd=ROOT) != (ROOT/name).read_bytes():
            raise ValueError('Frozen file changed: '+name)
    return full


def verify_sources():
    cfg = json.loads((ROOT/CONFIG).read_text())
    base = (ROOT/cfg['source']).parent
    receipt = json.loads((base/'acquisition.json').read_text())
    for item in receipt['files']:
        if hashlib.sha256((base/item['name']).read_bytes()).hexdigest() != item['sha256']:
            raise ValueError('Source hash mismatch: '+item['name'])
    if hashlib.sha256((ROOT/cfg['source']).read_bytes()).hexdigest() != cfg['source_sha256']:
        raise ValueError('Workbook changed')
    return cfg


def forecast(design):
    cfg = verify_sources()
    inputs = read_inputs(ROOT/cfg['source'])
    train, new = inputs['training'], inputs['targets']
    assert len(train) == cfg['required_calibration_n'] and len(new) == cfg['required_target_n']
    assert len({r['family'] for r in new}) == cfg['required_family_n']
    fits = fit_models([r['assay'] for r in train], [r['cell'] for r in train])
    for model, fit in fits.items():
        fit['forecasts'] = predict(model, [r['assay'] for r in new], fit['parameters']).tolist()
    return dict(study=cfg['study'], config=cfg, design_commit=design, inputs=inputs,
                fits=fits, numerical_target_values_decoded=False,
                target_assays_outside_training_support=[r['id'] for r in new if
                    r['assay'] < min(t['assay'] for t in train) or
                    r['assay'] > max(t['assay'] for t in train)])


def evaluate(predictions, prediction_commit):
    cfg = verify_sources()
    outcomes = read_outcomes(ROOT/cfg['source'])
    scores = {m: score(f['forecasts'], outcomes) for m, f in predictions['fits'].items()}
    primary = scores['pool']['family_balanced_mae']
    gains = {m: 1-primary/scores[m]['family_balanced_mae']
             if scores[m]['family_balanced_mae'] > 0 else None for m in cfg['primary_comparators']}
    accuracy = primary <= cfg['maximum_family_balanced_mae']
    advantages = {m: gains[m] is not None and gains[m] >= cfg['minimum_relative_gain'] for m in gains}
    spread = [{'id': o['id'], 'reported_minus_recomputed_mean': o['reported_mean']-o['observed'],
               'reported_minus_sample_sd': o['reported_spread']-o['sample_sd'],
               'reported_minus_sem': o['reported_spread']-o['sample_sd']/np.sqrt(3)} for o in outcomes]
    return dict(study=cfg['study'], design_commit=predictions['design_commit'],
        prediction_commit=prediction_commit, config=cfg, outcomes=outcomes,
        scores=scores, gains=gains, source_summary_checks=spread,
        decision=dict(absolute_accuracy=accuracy, relative_advantages=advantages,
                      joint_rule=accuracy and all(advantages.values())),
        target_assays_outside_training_support=predictions['target_assays_outside_training_support'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=['verify', 'predict', 'evaluate'], required=True)
    parser.add_argument('--freeze-commit')
    parser.add_argument('--prediction-commit')
    parser.add_argument('--predictions', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    verify_sources()
    if args.stage == 'verify':
        print('Biological source checksums verified; no numerical outcomes decoded.')
        return
    design = freeze(args.freeze_commit, FROZEN)
    if args.stage == 'predict':
        result, filename = forecast(design), 'predictions.json'
    else:
        if args.predictions is None or args.prediction_commit is None:
            parser.error('Evaluation requires sealed predictions and their commit')
        prediction_file = args.predictions.resolve().relative_to(ROOT).as_posix()
        sealed = freeze(args.prediction_commit, [prediction_file])
        predictions = json.loads(args.predictions.read_text())
        if predictions['design_commit'] != design:
            raise ValueError('Prediction design mismatch')
        if encode(forecast(design)) != args.predictions.read_bytes():
            raise ValueError('Forecast replay changed before outcome evaluation')
        result, filename = evaluate(predictions, sealed), 'result.json'
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output/filename).write_bytes(encode(result))
    print(json.dumps(dict(path=str(args.output/filename), stage=args.stage)))


if __name__ == '__main__':
    main()
