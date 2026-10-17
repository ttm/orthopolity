"""Freeze information-capacity forecasts before decoding non-IE durations."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess

from orthopolity.speech_capacity import FAMILIES, MODELS, read_rows, fit_models, predict, score

ROOT = Path(__file__).resolve().parents[1]
CONFIG = 'configs/speech_capacity_2026-10-17.json'
FROZEN = [CONFIG, 'src/orthopolity/speech_capacity.py', 'experiments/run_speech_capacity.py',
    'experiments/verify_speech_capacity.py', 'tests/test_speech_capacity.py',
    'docs/speech-capacity-protocol-2026-10-17.md',
    'data/human-candidates/2026-10-17/speech/acquisition.json',
    'data/human-candidates/2026-10-17/speech/predictor-audit.json',
    'data/human-candidates/2026-10-17/speech/publisher-crosscheck.json']


def encode(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+'\n').encode()


def freeze(ref, paths):
    full = subprocess.check_output(['git', 'rev-parse', ref], cwd=ROOT, text=True).strip()
    for name in paths:
        if subprocess.check_output(['git', 'show', f'{full}:{name}'], cwd=ROOT) != (ROOT/name).read_bytes():
            raise ValueError('Frozen file changed: '+name)
    return full


def verify_sources():
    cfg = json.loads((ROOT/CONFIG).read_text())
    base = (ROOT/cfg['source']).parent
    for item in json.loads((base/'acquisition.json').read_text())['files']:
        if hashlib.sha256((base/item['file']).read_bytes()).hexdigest() != item['sha256']:
            raise ValueError('Source changed: '+item['file'])
    if hashlib.sha256((ROOT/cfg['source']).read_bytes()).hexdigest() != cfg['source_sha256']:
        raise ValueError('Data changed')
    return cfg


def qualify(rows, cfg):
    if len(rows) != cfg['expected_rows'] or {r['language'] for r in rows} != set(FAMILIES):
        raise ValueError('Cohort identity or size changed')
    for lang in FAMILIES:
        subset = [r for r in rows if r['language'] == lang]
        if len({r['speaker'] for r in subset}) != 10 or len({r['text'] for r in subset}) != 15:
            raise ValueError('Speaker or text coverage changed')
    train = [r for r in rows if r['family'] == 'Indo-European']
    targets = [r for r in rows if r['family'] != 'Indo-European']
    if len(train) != 789 or len(targets) != 1499:
        raise ValueError('Split sizes changed')
    return train, targets


def forecast(design):
    cfg = verify_sources()
    train, targets = qualify(read_rows(ROOT/cfg['source'], 'calibration'), cfg)
    fits = fit_models(train)
    for name, fit in fits.items():
        fit['log_forecasts'] = predict(name, fit, targets).tolist()
        fit['calibration_score'] = score(predict(name, fit, train), train)
    lo, hi = min(r['id'] for r in train), max(r['id'] for r in train)
    return dict(study=cfg['study'], config=cfg, design_commit=design, training=train,
        targets=targets, fits=fits, target_numerical_durations_decoded=False,
        calibration_id_range=[lo, hi], target_languages_outside_id_support=sorted({
            r['language'] for r in targets if not lo <= r['id'] <= hi}))


def evaluate(predictions, sealed):
    cfg = verify_sources()
    _, outcomes = qualify(read_rows(ROOT/cfg['source'], 'evaluation'), cfg)
    scores = {m: score(predictions['fits'][m]['log_forecasts'], outcomes) for m in MODELS}
    key = 'family_balanced_language_log_mae'
    error = scores['conditional'][key]
    gains = {m: (1-error/scores[m][key]) if scores[m][key] > 0 else None
             for m in MODELS if m != 'conditional'}
    accuracy = error <= math.log(cfg['maximum_average_factor'])
    gain = gains['syllabic'] is not None and gains['syllabic'] >= cfg['minimum_syllabic_gain']
    best = min(scores[m][key] for m in ('unigram', 'power', 'same_text'))
    competitive = error <= cfg['maximum_best_benchmark_ratio']*best
    return dict(study=cfg['study'], config=cfg, design_commit=predictions['design_commit'],
        prediction_commit=sealed, outcomes=outcomes, scores=scores, gains=gains,
        decision=dict(accuracy=accuracy, syllabic_advantage=gain, competitive=competitive,
            joint_rule=accuracy and gain and competitive,
            contextual_advantage=gains['unigram'] is not None and gains['unigram'] >= cfg['minimum_context_gain']),
        target_languages_outside_id_support=predictions['target_languages_outside_id_support'])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--stage', required=True, choices=['verify', 'predict', 'evaluate'])
    p.add_argument('--freeze-commit')
    p.add_argument('--prediction-commit')
    p.add_argument('--predictions', type=Path)
    p.add_argument('--output', type=Path)
    a = p.parse_args()
    verify_sources()
    if a.stage == 'verify':
        print('Speech original bytes verified; no durations numerically decoded.'); return
    design = freeze(a.freeze_commit, FROZEN)
    if a.stage == 'predict':
        result, filename = forecast(design), 'predictions.json'
    else:
        if a.predictions is None or a.prediction_commit is None:
            p.error('Evaluation requires a committed prediction file')
        name = a.predictions.resolve().relative_to(ROOT).as_posix()
        sealed = freeze(a.prediction_commit, [name])
        if a.predictions.read_bytes() != encode(forecast(design)):
            raise ValueError('Forecast replay differs')
        result, filename = evaluate(json.loads(a.predictions.read_text()), sealed), 'result.json'
    a.output.mkdir(parents=True, exist_ok=False)
    (a.output/filename).write_bytes(encode(result))
    print(json.dumps(dict(stage=a.stage, path=str(a.output/filename))))


if __name__ == '__main__':
    main()
