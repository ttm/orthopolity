"""Append the retrospective measured-data diagnosis, preserving prior records."""
import json
from pathlib import Path

from orthopolity.run_registry import archive_reference, file_reference, register_run, verify_registry
from verify_chemostat_capacity import verify

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = Path('results/chemostat-capacity-followup-2026-10-10')


def main():
    directory = ROOT/DIRECTORY
    checked = verify(directory)
    recorded = json.loads((directory/'verification.json').read_text())
    if recorded != checked:
        raise ValueError('Retained verification differs from independent recomputation')
    execution = json.loads((directory/'execution.json').read_text())
    summary = json.loads((directory/'summary.json').read_text())
    config = 'configs/chemostat_capacity_followup_2026-10-10.json'
    sources = [r['path'] for r in execution['sources'] if r['path'] != config]
    sources += ['experiments/verify_chemostat_capacity.py', 'experiments/plot_chemostat_capacity.py',
                'experiments/register_chemostat_capacity.py', 'tests/test_chemostat_capacity_verification.py',
                'docs/chemostat-capacity-followup-results-2026-10-11.md']
    entry = dict(schema_version=1, run_id=summary['run_id'], evidence_kind='actual_measurement',
        resources=[dict(name='Transferred algal nitrogen and carbon requirements',
            units='Elemental density in pmol per cubic micrometre; normalized nitrogen shares and TV dimensionless',
            definition='Measured main-vessel biovolumes converted using separate preliminary-culture assays; finite algal groups, no size-spectrum neutrality claim')],
        data_inputs=[file_reference(ROOT, r['path'], role='Previously exposed published measurements') for r in execution['inputs']],
        configs=[archive_reference(ROOT, config)],
        algorithms=[dict(name='Frozen conditional TV upper bound and dual lower certificate, independently verified by geometric enumeration',
                         sources=[archive_reference(ROOT, p) for p in sources])],
        artifacts=[file_reference(ROOT, p.relative_to(ROOT).as_posix()) for p in sorted(directory.iterdir()) if p.is_file()],
        generated_seeds=dict(generated_empirical_data=False, randomized_analysis=False),
        hardware_metadata=dict(runtime=execution, cpu_model=None, total_ram_bytes=None, runtime_thread_count_verified=False),
        relationships=[dict(run_id='chemostat-resource-response-2026-10-02', type='retrospective_failure_diagnosis_of')],
        summary=dict(result=summary, freeze_commit=execution['freeze_commit'],
            analysis_design='Retrospective conditional diagnostic; already exposed outcomes, not independent confirmation',
            inference_scope='Excludes fixed opportunities, the two-resource family and transferred point quotas jointly in eight primary vessels. No statistical rejection, assay uncertainty or proof of alternative mechanism. Original forecast preserved.'))
    print(json.dumps(register_run(ROOT, entry), indent=2))
    print(json.dumps(verify_registry(ROOT), indent=2))


if __name__ == '__main__':
    main()
