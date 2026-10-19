"""Append the fixed cross-family information-capacity comparison."""
import hashlib
import json
from pathlib import Path
import platform
import sys

import numpy as np

from run_speech_capacity import verify_sources
from verify_speech_capacity import verify
from orthopolity.run_registry import archive_reference, file_reference, register_run, verify_registry

ROOT = Path(__file__).resolve().parents[1]
FORECAST = 'results/speech-capacity-forecast-2026-10-17'
RESULT = 'results/speech-capacity-2026-10-17'


def main():
    cfg = verify_sources()
    fp, rp = ROOT/FORECAST/'predictions.json', ROOT/RESULT/'result.json'
    prediction, result = json.loads(fp.read_text()), json.loads(rp.read_text())
    verified = verify(prediction, result)
    verified.update(prediction_sha256=hashlib.sha256(fp.read_bytes()).hexdigest(),
                    result_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
    if verified != json.loads((ROOT/RESULT/'verification.json').read_text()):
        raise ValueError('Independent verification differs')
    registry = ROOT/'results/run-registry.jsonl'
    prior = registry.read_bytes()
    if any(json.loads(line)['run_id'] == cfg['study'] for line in prior.decode().splitlines()):
        print(json.dumps(dict(appended=False, audit=verify_registry(ROOT)))); return
    sources = ['src/orthopolity/speech_capacity.py', 'experiments/run_speech_capacity.py',
        'experiments/verify_speech_capacity.py', 'experiments/plot_speech_capacity.py',
        'experiments/register_speech_capacity.py', 'tests/test_speech_capacity.py',
        'docs/speech-capacity-protocol-2026-10-17.md', 'docs/speech-capacity-results-2026-10-17.md',
        'docs/human-source-qualification-2026-10-17.md']
    entry = dict(schema_version=1, run_id=cfg['study'], evidence_kind='actual_measurement',
        resources=[dict(name='Syllable information and inferred processing capacity',
            units='bits per canonical syllable; pause-filtered seconds; inferred bits/second',
            definition=cfg['reference_measure'])],
        data_inputs=[file_reference(ROOT, p.relative_to(ROOT).as_posix(), role='Original source or qualification receipt')
                     for directory in ('data/human-candidates/2026-10-17/speech',
                                       'data/human-candidates/2026-10-19/speech-notices')
                     for p in sorted((ROOT/directory).iterdir()) if p.is_file()],
        configs=[archive_reference(ROOT, 'configs/speech_capacity_2026-10-17.json')],
        algorithms=[dict(name='Fixed information-capacity transfer and independent Decimal verification',
                         sources=[archive_reference(ROOT, p) for p in sources])],
        artifacts=[file_reference(ROOT, p.relative_to(ROOT).as_posix()) for d in (FORECAST, RESULT)
                   for p in sorted((ROOT/d).iterdir()) if p.is_file()],
        generated_seeds=dict(generated_empirical_data=False, randomized_analysis=False),
        hardware_metadata=dict(python=sys.version,numpy=np.__version__,platform=platform.platform(),
                               runtime_thread_count_verified=False),
        relationships=[], summary=dict(design_commit=result['design_commit'],prediction_commit=result['prediction_commit'],
            calibration_readings=789,calibration_languages=7,target_readings=1499,target_languages=10,target_families=8,
            primary_errors={m:s['family_balanced_language_log_mae'] for m,s in result['scores'].items()},
            gains=result['gains'],decision=result['decision'],
            qualifications=['Published equal-information-rate hypothesis and aggregate outcomes known',
                'Geometric language means, not individual reading accuracy or size allocation',
                'Independent entropy predictors; absolute capacity inferred and entropy uncertainty unpropagated',
                'Four target languages extrapolate; calibration has more missing text cells',
                'Publisher and GitHub agree on 2288 rows, versus unexplained article count 2265'],
            conclusion='Known information-capacity account transfers and beats all declared benchmarks in this cohort; not a unique orthopolity mechanism or universal allocation confirmation'))
    print(json.dumps(register_run(ROOT, entry), indent=2))
    if not registry.read_bytes().startswith(prior):
        raise ValueError('Earlier registry entries changed')
    print(json.dumps(verify_registry(ROOT), indent=2))


if __name__ == '__main__': main()
