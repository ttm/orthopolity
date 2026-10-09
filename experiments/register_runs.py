"""Register existing fixed studies or a supplied run entry without rerunning them.

Historical source hashes are labelled retrospective unless an original frozen
manifest supplies them. Hardware recorded by the original run is retained;
current host facts are never substituted for missing historical metadata.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from orthopolity.run_registry import (
    archive_reference, collect_hardware_metadata, file_reference, hash_file,
    register_run, verify_registry,
)


ROOT = Path(__file__).resolve().parents[1]


def resource(name, definition, units):
    return dict(name=name, definition=definition, units=units)


CATALOGUE = [
    dict(run_id='models-2026-10-01', directory='models', result='model-study.json',
         config='model_study_2026-10-01.json', runner='run_models.py',
         modules=['models.py', 'spectrum.py'], kind='simulation', parents=[],
         resources=[
             resource('continuous model cost', 'Declared scenario q(x)=x^d or x^2(1+b*x); exponent and coefficients fixed in each scenario', 'normalized model cost units'),
             resource('edge incidences', 'q(k)=k undirected edge incidences per vertex', 'edge incidences'),
             resource('centered wedges', 'q(k)=k(k-1)/2 unordered neighbor pairs centered on each vertex', 'centered wedges'),
             resource('money or size', 'q(x)=x of exchanged wealth, growth size, or realized feasibility capacity; normalized within each model', 'normalized units of the declared model resource'),
             resource('transported power', 'Packet/ray flux through spheres or a fixed angular cap', 'normalized power units'),
         ]),
    dict(run_id='dependence-2026-10-01', directory='dependence', result='dependence-study.json',
         config='dependence_study_2026-10-01.json', runner='run_dependence.py',
         modules=['dependence.py', 'models.py'], kind='simulation', parents=['models-2026-10-01'],
         resources=[resource('realized capacity', 'K=min_a X_a; q(K)=K with fixed unit-Pareto marginal capacities', 'normalized capacity units')]),
    dict(run_id='attachment-2026-10-01', directory='attachment', result='attachment-study.json',
         config='attachment_study_2026-10-01.json', runner='run_attachment.py',
         modules=['attachment.py'], kind='simulation', parents=['models-2026-10-01'],
         resources=[resource('centered wedges', 'q(k)=k(k-1)/2; fixed structural resource across all attachment kernels and graph sizes', 'centered wedges')]),
    dict(run_id='restrictions-2026-10-01', directory='restrictions', result='study.json',
         config='restriction_study_2026-10-01.json', runner='run_restrictions.py',
         modules=['restrictions.py'], kind='constructed_prediction', parents=[],
         resources=[resource('primary cost', 'q1(k)=k^2 at fixed logarithmic class centers', 'normalized primary cost units'),
                    resource('auxiliary cost', 'q2(k)=k^3 at the same class centers', 'normalized auxiliary cost units')]),
    dict(run_id='competition-2026-10-01', directory='competition', result='competition-study.json',
         config='competition_study_2026-10-01.json', runner='run_competition.py',
         modules=['competition.py', 'dependence.py'], kind='simulation', parents=['dependence-2026-10-01'],
         resources=[resource('realized capacity', 'K=min(X1,X2); q(K)=K, unchanged across Gaussian copula couplings', 'normalized capacity units')]),
    dict(run_id='forecast-2026-10-01', directory='forecast', result='forecast-study.json',
         config='forecast_study_2026-10-01.json', runner='run_forecast.py',
         modules=['forecast.py', 'dependence.py'], kind='simulation', parents=['dependence-2026-10-01'],
         resources=[resource('realized capacity', 'K=min(X1,X2); fixed q(K)=K with independently generated training, selection, and output cohorts', 'normalized capacity units')]),
    dict(run_id='interventions-2026-10-01', directory='interventions', result='study.json',
         config='intervention_study_2026-10-01.json', runner='run_interventions.py',
         modules=['interventions.py', 'restrictions.py'], kind='simulation', parents=['restrictions-2026-10-01'],
         resources=[resource('primary cost', 'q1(k)=k^2; measured sampled resource per object differs from normalized object counts', 'normalized primary cost units'),
                    resource('auxiliary cost', 'q2(k)=k^3; intervention changes auxiliary budget 12 to 8 and separate declared cases add measurement error', 'normalized auxiliary cost units')]),
]


def historical_metadata(result):
    recorded = result.get('environment', result.get('versions', {}))
    return dict(recording_scope='Historical environment fields copied from the original result; additional hardware not recorded',
                recorded_environment=recorded, cpu_model=None, total_ram_bytes=None,
                os_version_or_build=None,
                runtime_thread_count_verified=bool(recorded.get('runtime_thread_count_verified', False)))


def existing_study_entry(repo_root, specification):
    directory = Path('results') / specification['directory']
    result_path = (directory / specification['result']).as_posix()
    config_path = 'configs/' + specification['config']
    result = json.loads((repo_root / result_path).read_text())
    config = json.loads((repo_root / config_path).read_text())
    if result.get('config', result.get('configuration')) != config:
        raise ValueError(f'Historical result configuration differs from {config_path}')
    if 'config_sha256' in result and result['config_sha256'] != hash_file(repo_root, config_path):
        raise ValueError(f'Historical config digest differs from {config_path}')
    sources = ['experiments/' + specification['runner']] + [
        'src/orthopolity/' + name for name in specification['modules']] + ['src/orthopolity/figures.py']
    artifacts = [file_reference(repo_root, path.relative_to(repo_root).as_posix())
                 for path in sorted((repo_root / directory).iterdir()) if path.is_file()]
    description = result.get('kind', result.get('interpretation', config.get('description', '')))
    return dict(schema_version=1, run_id=specification['run_id'], evidence_kind=specification['kind'],
        resources=specification['resources'], data_inputs=[],
        generated_seeds=(dict(base_seed=config['seed'], derivation='Scenario/stage/replicate derivation is defined in the archived runner')
                         if 'seed' in config else dict(status='Deterministic construction; no random seed')),
        algorithms=[dict(name=specification['directory'] + ' study',
                         sources=[archive_reference(repo_root, path) for path in sources],
                         source_provenance='Retrospective current-source snapshots; original execution did not retain a source digest. These hashes do not establish the original executed source version.')],
        configs=[archive_reference(repo_root, config_path)], artifacts=artifacts,
        relationships=[dict(run_id=parent, type='conceptual_extension') for parent in specification['parents']],
        hardware_metadata=historical_metadata(result),
        summary=dict(interpretation=description, scenario_count=len(result.get('scenarios', result.get('cases', []))),
                     registration_scope='Retrospective catalogue registration of existing retained output; no rerun or external preregistration'))


def baseline_pilot_entry(repo_root):
    directory = Path('data/workload-pilot/2026-10-01')
    manifest = json.loads((repo_root / directory / 'calibration-manifest.json').read_text())
    result = json.loads((repo_root / 'results/workload-pilot/study.json').read_text())
    config_path = 'configs/workload_pilot_2026-10-01.json'
    if manifest['config_sha256'] != hash_file(repo_root, config_path):
        raise ValueError('Baseline pilot config no longer matches its original frozen manifest')
    sources = []
    for path, digest in manifest['source_sha256'].items():
        archived = archive_reference(repo_root, path)
        if archived['sha256'] != digest:
            raise ValueError(f'Baseline pilot source changed since original freeze: {path}')
        sources.append(archived)
    inputs = [file_reference(repo_root, path.relative_to(repo_root).as_posix())
              for path in sorted((repo_root / directory).iterdir()) if path.is_file()]
    expected = [('calibration.jsonl', manifest['calibration_sha256']),
                ('validation.jsonl', result['validation_sha256']),
                ('frozen-plan.json', result['frozen_plan_sha256'])]
    for name, digest in expected:
        if hash_file(repo_root, (directory / name).as_posix()) != digest:
            raise ValueError(f'Baseline pilot retained input changed: {name}')
    artifacts = [file_reference(repo_root, path.relative_to(repo_root).as_posix())
                 for path in sorted((repo_root / 'results/workload-pilot').iterdir()) if path.is_file()]
    config = result['config']
    return dict(schema_version=1, run_id='workload-pilot-2026-10-01', evidence_kind='actual_measurement',
        resources=[resource('peak resident memory', config['memory_resource'], 'bytes'),
                   resource('task CPU', config['cpu_resource'], 'CPU seconds')],
        data_inputs=inputs,
        generated_seeds=dict(schedule_and_analysis_base_seed=config['seed'],
                             workload_input_base_seed=1729, independent_probe_base_seed=1730,
                             derivation='Task inputs and probes use [base_seed,size]; stage/block scheduling is defined in archived runner'),
        algorithms=[dict(name='Fresh-child measured matrix work and frozen cost-profile replay', sources=sources,
                         source_provenance='All digests matched the original pre-validation frozen source manifest')],
        configs=[archive_reference(repo_root, config_path)], artifacts=artifacts, relationships=[],
        hardware_metadata=historical_metadata(result),
        summary=dict(result['summary'], evidence_scope=config['interpretation'],
                     registration_scope='Retrospective registration of a prospective frozen-prediction experiment; original records preserved'))


def register_catalogue(repo_root, registry_path):
    results = [register_run(repo_root, existing_study_entry(repo_root, specification), registry_path)
               for specification in CATALOGUE]
    results.append(register_run(repo_root, baseline_pilot_entry(repo_root), registry_path))
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', type=Path, default=ROOT)
    parser.add_argument('--registry', default='results/run-registry.jsonl')
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--catalogue', action='store_true', help='Register seven established model studies and the measured baseline pilot')
    action.add_argument('--entry', type=Path, help='Register a supplied schema_version=1 entry')
    action.add_argument('--verify', action='store_true', help='Audit all registry entries and file digests')
    action.add_argument('--hardware', action='store_true', help='Print current privacy-limited host/software metadata without registering it')
    args = parser.parse_args()
    root = args.repo_root.resolve()
    if args.catalogue:
        result = register_catalogue(root, args.registry)
    elif args.entry:
        result = register_run(root, json.loads(args.entry.read_text()), args.registry)
    elif args.verify:
        result = verify_registry(root, args.registry)
    else:
        result = collect_hardware_metadata()
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == '__main__': main()
