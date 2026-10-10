"""Append the completed synthetic magnitude gate without changing empirical runs."""
import hashlib
import json
from pathlib import Path

from orthopolity.run_registry import archive_reference, file_reference, register_run, verify_registry

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = Path('results/italian-magnitude-validation-2026-10-10')
CONFIG = 'configs/italian_magnitude_validation_2026-10-10.json'


def main():
    summary = json.loads((ROOT/DIRECTORY/'summary.json').read_text())
    execution = json.loads((ROOT/DIRECTORY/'execution.json').read_text())
    verified = json.loads((ROOT/DIRECTORY/'verification.json').read_text())
    if not verified['verified'] or verified['failed_gate_cells'] != summary['n_failed_gate_cells']:
        raise ValueError('Independent verification missing or disagrees')
    if (ROOT/CONFIG).read_bytes() != (ROOT/DIRECTORY/'config.json').read_bytes():
        raise ValueError('Configuration changed after execution')
    for path, expected in execution['source_sha256'].items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest() != expected:
            raise ValueError(f'Executed source changed: {path}')
    for path, expected in execution['artifact_sha256'].items():
        if hashlib.sha256((ROOT/DIRECTORY/path).read_bytes()).hexdigest() != expected:
            raise ValueError(f'Executed artifact changed: {path}')
    cfg = json.loads((ROOT/CONFIG).read_text())
    if hashlib.sha256((ROOT/cfg['source']['path']).read_bytes()).hexdigest() != execution['methods_pdf_sha256']:
        raise ValueError('Methods PDF changed')
    sources = list(execution['source_sha256']) + [
        'experiments/verify_italian_magnitudes.py',
        'experiments/plot_italian_magnitudes.py',
        'experiments/register_italian_magnitudes.py',
        'docs/italian-magnitude-validation-results-2026-10-10.md']
    entry = dict(schema_version=1, run_id=cfg['run_id'], evidence_kind='simulation',
        resources=[dict(name='Synthetic magnitude observation for rupture-territory comparison',
                        units='Moment magnitude and dimensionless b',
                        definition='Magnitude marginals b=1 and 1.5 of log-orthopolic rupture territory b=D2/2 versus b=1; no real resource or D2 measurement')],
        data_inputs=[file_reference(ROOT,cfg['source']['path'],role='Published observation-model coefficients, not earthquake rows')],
        configs=[archive_reference(ROOT,CONFIG)],
        algorithms=[dict(name='Frozen source-bin conversion, original magnitude estimator and independent population/runner checks',
                         sources=[archive_reference(ROOT,p) for p in sources])],
        artifacts=[file_reference(ROOT,p.relative_to(ROOT).as_posix())
                   for p in sorted((ROOT/DIRECTORY).iterdir()) if p.is_file()],
        generated_seeds=dict(base_seed=cfg['seed'],
            streams='SeedSequence([base_seed, model_index, true_b_index, lower_support_index, replicate])',
            generator='NumPy default_rng; fixed configuration order'),
        hardware_metadata=dict(runtime=execution, cpu_model=None,total_ram_bytes=None,
                               runtime_thread_count_verified=False),
        relationships=[dict(run_id='seismic-qualification-2026-10-10',type='subsequent_candidate_method_validation')],
        summary=dict(passes_gate=summary['passes_gate'],failed_cells=summary['n_failed_gate_cells'],
                     required_cells=summary['n_gate_cells'],total_simulated_cells=len(summary['cells']),
                     replicates=verified['replicates'],protocol_commit='ab14b6b',
                     executed_commit=execution['git_commit'],
                     real_italian_sequence_or_response_fit=False,
                     inference_scope='Synthetic failure of a necessary estimator gate under declared scenarios. Neither physical hypothesis tested or favoured. Original empirical records preserved.'))
    print(json.dumps(register_run(ROOT,entry),indent=2))
    print(json.dumps(verify_registry(ROOT),indent=2))


if __name__=='__main__':
    main()
