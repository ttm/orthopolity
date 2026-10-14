"""Append the chemistry transfer while preserving all earlier study records."""
import json
from pathlib import Path

from orthopolity.run_registry import archive_reference, file_reference, register_run, verify_registry
from verify_adsorption import verify_result
from audit_adsorption_coverage import audit

ROOT = Path(__file__).resolve().parents[1]
BASE = 'data/adsorption/2026-10-13'
DIRECTORY = 'results/adsorption-transfer-2026-10-13'
FORECAST = 'results/adsorption-forecast-2026-10-13'
CONFIG = 'configs/adsorption_2026-10-13.json'


def main():
    directory = ROOT/DIRECTORY
    result = json.loads((directory/'result.json').read_text())
    execution = json.loads((directory/'execution.json').read_text())
    checked = verify_result(directory/'result.json',ROOT/FORECAST/'predictions.json',ROOT/CONFIG)
    if not checked['verified'] or checked != json.loads((directory/'verification.json').read_text()):
        raise ValueError('Independent verification differs')
    if audit(ROOT/FORECAST/'predictions.json') != json.loads((directory/'coverage-audit.json').read_text()):
        raise ValueError('Post-response coverage audit differs')
    registry = ROOT/'results/run-registry.jsonl'
    prior = registry.read_bytes()
    if any(json.loads(line)['run_id']==result['run_id'] for line in prior.decode().splitlines()):
        print(json.dumps(dict(run_id=result['run_id'],appended=False,audit=verify_registry(ROOT)),indent=2))
        return
    sources = [item['path'] for item in execution['sources'] if item['path']!=CONFIG]
    sources += ['experiments/verify_adsorption.py','experiments/audit_adsorption_coverage.py',
        'experiments/plot_adsorption.py','experiments/register_adsorption.py',
        'tests/test_adsorption_verification.py','docs/adsorption-results-2026-10-13.md']
    entry = dict(schema_version=1,run_id=result['run_id'],evidence_kind='actual_measurement',
        resources=[dict(name='Effective common adsorption capacity within each temperature',units='mmol/g',
            definition='Counting measure over two species and vacancies; pure-calibrated affinities constrain finite-site allocation')],
        data_inputs=[file_reference(ROOT,p.relative_to(ROOT).as_posix(),role='Retained publisher original, methods source or predictor-only audit')
                     for p in sorted((ROOT/BASE).iterdir()) if p.is_file()],
        configs=[archive_reference(ROOT,CONFIG)],
        algorithms=[dict(name='Pure-calibrated competitive Langmuir, ablation and IAST; independent Gibbs/variable-projection/composition-root verification',
                         sources=[archive_reference(ROOT,p) for p in sources])],
        artifacts=[file_reference(ROOT,p.relative_to(ROOT).as_posix()) for d in [FORECAST,DIRECTORY]
                   for p in sorted((ROOT/d).iterdir()) if p.is_file()],
        generated_seeds=dict(generated_empirical_data=False,randomized_analysis=False),
        hardware_metadata=dict(python=execution['python'],runtime_thread_count_verified=False),relationships=[],
        summary=dict(freeze_commit=execution['freeze_commit'],prediction_commit=execution['prediction_commit'],
            analyses={a['name']:a['summary'] for a in result['analyses']},
            source_qualifications=['Published qualitative outcomes known before local freeze',
                'Equilibrium composition and uptake derived through related density/mass-balance measurements; covariance unavailable',
                'Temperature-specific effective capacities, not independently measured invariant site counts',
                '29 upper IAST extrapolations; post-response audit adds 12 lower mixture and 11 lower IAST CO2 conditions',
                'Engineering tolerance relative to pure maxima; only 39 of 90 primary predictions within reported observation U'],
            conclusion='Substantial gain over omitting competition and declared finite-accuracy transfer pass; IAST slightly better; no demonstrated new predictive advantage or universal-neutrality evidence'))
    print(json.dumps(register_run(ROOT,entry),indent=2))
    if not registry.read_bytes().startswith(prior):
        raise ValueError('Earlier registry bytes changed')
    print(json.dumps(verify_registry(ROOT),indent=2))


if __name__ == '__main__':
    main()
