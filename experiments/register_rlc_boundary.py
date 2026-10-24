"""Archive the independently specified circuit forecast and qualified result."""
import hashlib
import json
from pathlib import Path
import platform
import sys

import numpy as np

from orthopolity.run_registry import archive_reference, file_reference, register_run, verify_registry
from run_rlc_boundary import CONFIG, FROZEN, freeze, verify_sources
from verify_rlc_boundary import verify_prediction, verify_result

ROOT = Path(__file__).resolve().parents[1]
FORECAST = 'results/rlc-boundary-forecast-2026-10-25'
RESULT = 'results/rlc-boundary-2026-10-25'


def main():
    prediction_path = ROOT/FORECAST/'predictions.json'
    prediction_bytes = prediction_path.read_bytes()
    prediction = json.loads(prediction_bytes)
    result = json.loads((ROOT/RESULT/'result.json').read_text())
    cfg = prediction['config']
    freeze(prediction['design_commit'], FROZEN)
    freeze(result['forecast_commit'], [FORECAST+'/predictions.json', FORECAST+'/verification.json'])
    source = verify_sources(cfg)
    stats = dict(numerical_comparisons=0, maximum_absolute_difference=0.)
    verify_prediction(prediction, stats)
    verify_result(result, prediction, prediction_bytes, stats)
    verification = json.loads((ROOT/RESULT/'verification.json').read_text())
    for key, value in stats.items():
        if verification[key] != value:
            raise ValueError('Independent verification differs: '+key)
    result_hash = hashlib.sha256((ROOT/RESULT/'result.json').read_bytes()).hexdigest()
    if verification['result_sha256'] != result_hash:
        raise ValueError('Result changed')
    audit = json.loads((ROOT/RESULT/'source-audit.json').read_text())
    if not audit['passed'] or audit['result_sha256'] != result_hash:
        raise ValueError('Source audit does not cover result')
    registry = ROOT/'results/run-registry.jsonl'
    prior = registry.read_bytes()
    if any(json.loads(line)['run_id'] == cfg['study'] for line in prior.decode().splitlines()):
        print(json.dumps(dict(appended=False, audit=verify_registry(ROOT)), indent=2))
        return
    sources = [name for name in FROZEN if name != CONFIG and not name.startswith('data/')]
    sources += ['experiments/audit_rlc_source.py', 'experiments/plot_rlc_boundary.py',
                'experiments/register_rlc_boundary.py', 'docs/rlc-boundary-results-2026-10-25.md']
    entry = dict(schema_version=1, run_id=cfg['study'], evidence_kind='actual_measurement',
        resources=[dict(name='Charge increments and electric/magnetic storage in a driven circuit',
            units='ohm; Hz; F; H; incremental charge C V; stored energy (C V^2 + L I_L^2)/2',
            definition=cfg['reference_measure'])],
        data_inputs=[file_reference(ROOT, p.relative_to(ROOT).as_posix(), role='Public original or acquisition/design receipt')
                     for p in sorted(source.iterdir()) if p.is_file()],
        configs=[archive_reference(ROOT, CONFIG)],
        algorithms=[dict(name='Independent component forecast, passive RC error lower bound and separate state/source verification',
                         sources=[archive_reference(ROOT, name) for name in sources])],
        artifacts=[file_reference(ROOT, p.relative_to(ROOT).as_posix())
                   for directory in (FORECAST, RESULT)
                   for p in sorted((ROOT/directory).iterdir()) if p.is_file()],
        generated_seeds=dict(generated_empirical_data=False, randomized_analysis=False),
        hardware_metadata=dict(python=sys.version, numpy=np.__version__, platform=platform.platform(),
                               runtime_thread_count_verified=False),
        relationships=[],
        summary=dict(design_commit=result['design_commit'], forecast_commit=result['forecast_commit'],
            original_observations=81, locally_unexposed_primary_observations=80,
            previously_exposed_rows=[0], primary=result['primary'],
            crossing_hz_interval=prediction['crossing_hz_interval'],
            independent_numeric_checks=stats['numerical_comparisons'],
            qualifications=[
                'One fabricated driven circuit; no independent-circuit replication or instrument-error model',
                'Published fitted component values and qualitative response known; first raw string exposed and excluded before other access',
                'Conditional component envelope overlaps observed bracket; nominal crossover itself is below that bracket',
                'Conflicting printed resistance units handled by fixed primary and sensitivity; resistance uncertainty unspecified',
                'Deterministic comparison against collocated passive RC class, not statistical rejection or unique law confirmation',
                cfg['reference_measure']],
            conclusion='Independent standard RLC forecast beats a lower bound for every collocated passive RC network on the released spectrum; magnetic storage extends the restricted exchange mechanism',
            registration_scope='Locally frozen retrospective reanalysis of public actual measurements, not new collection or external preregistration'))
    print(json.dumps(register_run(ROOT, entry), indent=2))
    if not registry.read_bytes().startswith(prior):
        raise ValueError('Earlier registry bytes changed')
    print(json.dumps(verify_registry(ROOT), indent=2))


if __name__ == '__main__':
    main()
