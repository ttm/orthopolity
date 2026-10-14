"""Register synthetic design qualification; preserve all empirical run records."""
import hashlib
import json
from pathlib import Path

from orthopolity.run_registry import archive_reference, file_reference, register_run, verify_registry
from verify_saltation_qualification import verify_result

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = 'results/saltation-qualification-2026-10-14'
CONFIG = 'configs/saltation_qualification_2026-10-14.json'


def main():
    directory = ROOT/DIRECTORY
    result = json.loads((directory/'result.json').read_text())
    execution = json.loads((directory/'execution.json').read_text())
    checked = verify_result(directory/'result.json', ROOT/CONFIG)
    if not checked['verified'] or checked != json.loads((directory/'verification.json').read_text()):
        raise ValueError('Independent verification differs')
    for item in execution['sources']:
        if hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest() != item['sha256']:
            raise ValueError('Changed executed source '+item['path'])
    registry = ROOT/'results/run-registry.jsonl'
    prior = registry.read_bytes()
    if any(json.loads(line)['run_id']==result['run_id'] for line in prior.decode().splitlines()):
        print(json.dumps(dict(appended=False,audit=verify_registry(ROOT)),indent=2))
        return
    algorithms = [e['path'] for e in execution['sources'] if not e['path'].startswith('data/') and e['path']!=CONFIG]
    algorithms += ['experiments/verify_saltation_qualification.py','experiments/plot_saltation_qualification.py',
                   'experiments/register_saltation_qualification.py','docs/saltation-qualification-results-2026-10-14.md']
    entry = dict(schema_version=1,run_id=result['run_id'],evidence_kind='simulation',
        resources=[dict(name='Wind momentum-throughput budget with synthetic sand transport',units='Pa and arbitrary common flux units',
            definition='Day-balanced observation measure; neither log-orthopolic nor linear-orthopolic size allocation tested')],
        data_inputs=[file_reference(ROOT,e['path'],role='Publisher source or predictor-only audit; numerical sand responses unused')
                     for e in execution['sources'] if e['path'].startswith('data/')],
        configs=[archive_reference(ROOT,CONFIG)],
        algorithms=[dict(name='Chronological two-law discrimination; active-set fitting and independent least-squares verification',
                         sources=[archive_reference(ROOT,p) for p in algorithms])],
        artifacts=[file_reference(ROOT,p.relative_to(ROOT).as_posix()) for p in sorted(directory.iterdir()) if p.is_file()],
        generated_seeds=dict(seed=20261014,generator='NumPy default_rng PCG64',
                             streams='Configuration order; common factors across truth/threshold within each noise level',generated_empirical_data=False),
        hardware_metadata=dict(python=execution['python'],runtime_thread_count_verified=False),relationships=[],
        summary=dict(freeze_commit=execution['freeze_commit'],gate=result['gate'],
                     scenarios=24,replicates_per_scenario=500,real_response_values_read=False,
                     conclusion='Frozen design fails selection gate under declared variability; real-response fitting stopped; neither physical law nor general allocation tested'))
    print(json.dumps(register_run(ROOT,entry),indent=2))
    if not registry.read_bytes().startswith(prior):
        raise ValueError('Earlier registry bytes changed')
    print(json.dumps(verify_registry(ROOT),indent=2))


if __name__=='__main__':
    main()
