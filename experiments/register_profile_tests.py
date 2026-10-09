"""Register retained solar and simulation tests without rerunning their data.

The aquatic driver handles its own registration. The first simulation's exact
source snapshots survive its plotting correction; the final replay is labelled
as the same numerical realization, rather than new independent evidence.
"""
from __future__ import annotations

import json
from pathlib import Path

from orthopolity.run_registry import archive_reference,file_reference,register_run,verify_registry


ROOT=Path(__file__).resolve().parents[1]


def retained_sources(expected, snapshot=None):
    result=[]
    for logical,digest in expected.items():
        path=logical if snapshot is None else str(snapshot/logical)
        ref=archive_reference(ROOT,path)
        if ref['sha256']!=digest:raise ValueError(f'Frozen source no longer matches: {path}')
        ref['original_path']=logical
        result.append(ref)
    return result


def references(directory):
    return [file_reference(ROOT,str(path.relative_to(ROOT))) for path in sorted((ROOT/directory).iterdir())
            if path.is_file() and path.name!='registry-entry.json']


def save_entry(directory,entry):
    path=ROOT/directory/'registry-entry.json'
    encoded=json.dumps(entry,indent=2,allow_nan=False)+'\n'
    if path.exists() and path.read_text()!=encoded:raise ValueError('Retained registration differs')
    if not path.exists():path.write_text(encoded)
    return register_run(ROOT,entry)


def environment(versions):
    return dict(recording_scope='Recorded numerical execution versions; additional host facts not recorded',
                recorded_environment=versions,cpu_model=None,total_ram_bytes=None)


def register_solar():
    directory=Path('data/solar-resource-transfer/2026-10-01');output=Path('results/solar-resource-transfer')
    plan=json.loads((ROOT/directory/'frozen-plan.json').read_text())
    result=json.loads((ROOT/output/'study.json').read_text())
    assert file_reference(ROOT,str(directory/'frozen-plan.json'))==result['frozen_plan']
    expected={ref['path']:ref['sha256'] for ref in plan['sources']}
    config_ref=archive_reference(ROOT,plan['config_reference']['path'])
    assert config_ref['sha256']==plan['config_reference']['sha256']
    for ref in plan['data_inputs']:
        assert file_reference(ROOT,ref['path'])==ref
    primary=result['results']['integrated_irrad_peak']
    entry=dict(schema_version=1,run_id=plan['run_id'],evidence_kind='actual_measurement',
        resources=[dict(name='rise-window fluence',definition='Supplied start-to-peak XRS integrated irradiance at the observer, without additional background subtraction',units='J/m²'),
                   dict(name='end-window fluence',definition='Supplied start-to-end XRS integrated irradiance; complete-case sensitivity with missingness retained',units='J/m²')],
        data_inputs=plan['data_inputs']+references(directory),
        generated_seeds=dict(base_seed=plan['config']['seed'],bootstrap_replicates=plan['config']['bootstrap_replicates'],
            algorithm='Paired month-block resampling stratified within each calendar year, as specified in archived source'),
        algorithms=[dict(name='Measured-cost full-profile temporal forecast',sources=retained_sources(expected))],
        configs=[config_ref],artifacts=references(output),
        relationships=[dict(run_id='models-2026-10-01',type='empirical_full_profile_test')],
        hardware_metadata=environment(plan['environment']),
        summary=dict(new_observations_collected=0,training_events=primary['training_complete_n'],heldout_events=primary['evaluation_complete_n'],
            primary_count_scores=primary['scores'],paired_cross_entropy=primary['paired_cross_entropy_differences'],
            scope=result['scope']))
    return save_entry(directory,entry)


def register_identification(final):
    suffix='2026-10-01-final' if final else '2026-10-01'
    directory=Path('data/resource-identification')/suffix
    output=Path('results/resource-identification') if final else directory/'interrupted-results'
    plan=json.loads((ROOT/directory/'frozen-plan.json').read_text())
    result=json.loads((ROOT/output/'study.json').read_text())
    assert result['frozen_plan_sha256']==file_reference(ROOT,str(directory/'frozen-plan.json'))['sha256']
    snapshot=None if final else directory/'frozen-sources'
    config_path=plan['config_path'] if final else str(snapshot/plan['config_path'])
    config_ref=archive_reference(ROOT,config_path)
    assert config_ref['sha256']==plan['config_sha256']
    config_ref['original_path']=plan['config_path']
    parents=([dict(run_id='resource-identification-2026-10-01',type='same_seed_computational_replay_after_plot_fix')]
             if final else [dict(run_id='models-2026-10-01',type='exponent_sufficiency_test')])
    entry=dict(schema_version=1,run_id=plan['run_id'],evidence_kind='simulation',
        resources=[plan['config']['resource']],data_inputs=references(directory),
        generated_seeds=dict(base_seed=plan['config']['seed'],streams=plan['config']['streams']),
        algorithms=[dict(name='Stationary growth/removal populations and independently calibrated rank tests',
            sources=retained_sources(plan['source_sha256'],snapshot))],
        configs=[config_ref],artifacts=references(output),relationships=parents,
        hardware_metadata=environment(plan['versions']),
        summary=dict(rendering_status='complete' if final else 'interrupted_after_numerical_completion',
            independent_numerical_realization=not final,calibration_cohorts=36000,heldout_cohorts=18000,
            operating_characteristics=result['operating_characteristics'],interpretation=result['interpretation']))
    if final:
        import numpy as np
        for filename in ('calibration.npz','validation.npz'):
            with np.load(ROOT/'data/resource-identification/2026-10-01'/filename) as original,np.load(ROOT/directory/filename) as replay:
                assert original.files==replay.files
                assert all(np.array_equal(original[key],replay[key]) for key in original.files)
    return save_entry(directory,entry)


def main():
    print(json.dumps([register_solar(),register_identification(False),register_identification(True)],indent=2))
    print(json.dumps(verify_registry(ROOT),indent=2))


if __name__=='__main__':main()
