"""Append the cantilever forecast audit while preserving all earlier records."""
import json
from pathlib import Path

from orthopolity.run_registry import archive_reference, file_reference, register_run, verify_registry
from verify_cantilever import verify

ROOT = Path(__file__).resolve().parents[1]
BASE = 'data/cantilever/2026-10-13'
DIRECTORY = 'results/cantilever-transfer-2026-10-13'
FORECAST = 'results/cantilever-forecast-2026-10-13'


def main():
    directory = ROOT / DIRECTORY
    result = json.loads((directory / 'result.json').read_text())
    execution = json.loads((directory / 'execution.json').read_text())
    if verify(directory) != json.loads((directory / 'verification.json').read_text()):
        raise ValueError('Independent verification differs')
    registry = ROOT / 'results/run-registry.jsonl'
    if any(json.loads(line)['run_id'] == result['run_id'] for line in registry.read_text().splitlines()):
        print(json.dumps(dict(run_id=result['run_id'], appended=False, audit=verify_registry(ROOT)),indent=2))
        return
    config = 'configs/cantilever_2026-10-13.json'
    sources = [item['path'] for item in execution['sources'] if item['path'] != config]
    sources += ['experiments/verify_cantilever.py', 'experiments/register_cantilever.py',
                'experiments/plot_cantilever.py', 'tests/test_cantilever_verification.py',
                'docs/cantilever-results-2026-10-13.md']
    entry = dict(schema_version=1,run_id=result['run_id'],evidence_kind='actual_measurement',
        resources=[dict(name='Mean harmonic energy of specified mechanical modes',
            units='Fluctuation temperature K; potential energy per coordinate k_B T_fluc/2',
            definition='Finite mode counting measure; conditional nonequilibrium transfer, inherited equilibrium normalization')],
        data_inputs=[file_reference(ROOT,p.relative_to(ROOT).as_posix(),role='Retained original source or predictor-only audit')
                     for p in sorted((ROOT/BASE).iterdir()) if p.is_file()],
        configs=[archive_reference(ROOT,config)],
        algorithms=[dict(name='Cold-to-hot quadratic local-loss inversion, positivity gate and independent spatial integration',
                         sources=[archive_reference(ROOT,p) for p in sources])],
        artifacts=[file_reference(ROOT,p.relative_to(ROOT).as_posix()) for d in [FORECAST,DIRECTORY]
                   for p in sorted((ROOT/d).iterdir()) if p.is_file()],
        generated_seeds=dict(generated_empirical_data=False,randomized_analysis=False),
        hardware_metadata=dict(python=execution['python'],runtime_thread_count_verified=False),
        relationships=[],
        summary=dict(freeze_commit=execution['freeze_commit'],prediction_commit=execution['prediction_commit'],
            analyses={a['name']:a['summary'] for a in result['analyses']},
            source_qualifications=['Paper295K/archive300K baseline discrepancy identified before fit',
                'Archived C30C flexural3 last response is below published plotting range; retained unchanged',
                'Shared spectra, baseline and thermometry; no joint covariance',
                'C30 and C30C are preparations of the same cantilever, not independent specimens'],
            conclusion='Modest conditional average gain with one primary physical-model failure and large mode-specific errors; no universal or prospective confirmation'))
    print(json.dumps(register_run(ROOT,entry),indent=2))
    print(json.dumps(verify_registry(ROOT),indent=2))


if __name__=='__main__': main()
