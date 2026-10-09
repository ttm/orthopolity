"""Replicate old forecasts on original quotas, with prospective recalibration.

The original measurement/analysis source and data are retained. This driver
adds a separately hashed replication specification, comparison freeze, and
registry entry rather than changing historical algorithms or measurements.
"""
from __future__ import annotations

import argparse
import csv
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import time

import numpy as np

from orthopolity.workload_transfer import analyse_transfer, transfer_figures, transfer_plan
from orthopolity.run_registry import collect_hardware_metadata, file_reference, archive_reference, register_run

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('preserved_workload_pilot',ROOT/'experiments/run_workload_pilot.py')
legacy=importlib.util.module_from_spec(spec)
spec.loader.exec_module(legacy)


def replication_sources():
    sources=legacy.measurement_sources()
    sources.update({str(path.relative_to(ROOT)):legacy.digest(path) for path in (
        Path(__file__),ROOT/'src/orthopolity/workload_transfer.py',ROOT/'src/orthopolity/run_registry.py')})
    return sources


def check_reference(config):
    directory=ROOT/config['reference_directory']
    plan=json.loads((directory/'frozen-plan.json').read_text())
    manifest=json.loads((directory/'calibration-manifest.json').read_text())
    result=json.loads((ROOT/config['reference_results']).read_text())
    if plan['source_sha256']!=legacy.measurement_sources():
        raise ValueError('Original algorithm files changed; restore the recorded version before transfer')
    if legacy.digest(directory/'calibration.jsonl')!=plan['calibration_sha256'] or manifest['calibration_sha256']!=plan['calibration_sha256']:
        raise ValueError('Original calibration archive changed')
    if legacy.digest(directory/'frozen-plan.json')!=result['frozen_plan_sha256'] or legacy.digest(directory/'validation.jsonl')!=result['validation_sha256']:
        raise ValueError('Original prediction or validation archive changed')
    if np.__version__!=manifest['environment']['numpy']:
        raise ValueError('Use the original recorded NumPy version for unchanged matrix inputs')
    return plan,dict(reference_run_id=config['reference_run_id'],
        reference_plan=file_reference(ROOT,str((directory/'frozen-plan.json').relative_to(ROOT))),
        reference_calibration=file_reference(ROOT,str((directory/'calibration.jsonl').relative_to(ROOT))),
        reference_validation=file_reference(ROOT,str((directory/'validation.jsonl').relative_to(ROOT))),
        reference_result=file_reference(ROOT,config['reference_results']))


def prepare(config, config_path, directory):
    reference,lineage=check_reference(config)
    sources=replication_sources()
    path=directory/'transfer-specification.json'
    specification=dict(config=config,config_sha256=legacy.digest(config_path),source_sha256=sources,lineage=lineage)
    metadata_path=directory/'hardware-metadata.json'
    if metadata_path.exists():
        specification['hardware_metadata_reference']=file_reference(ROOT,str(metadata_path.relative_to(ROOT)))
    if path.exists():
        existing=json.loads(path.read_text())
        if any(existing[key]!=value for key,value in specification.items()):
            raise ValueError('A recorded replication has different inputs; use a new directory')
        return reference,existing
    if (directory/'validation.jsonl').exists() or (directory/'calibration.jsonl').exists():
        raise ValueError('Specify replication provenance before collecting its measurements')
    specification.update(started_utc=legacy.utc_now(),
        hardware_metadata=(json.loads(metadata_path.read_text()) if metadata_path.exists()
                           else collect_hardware_metadata(config['thread_environment'])),
        run_id='workload-transfer-'+directory.name,
        qualification='Later software launches on the same date/machine; no distinct-day or different-hardware claim')
    legacy.write_json(path,specification)
    return reference,json.loads(path.read_text())


def freeze(config,config_path,directory):
    reference,specification=prepare(config,config_path,directory)
    path=directory/'frozen-plan.json'
    if path.exists():
        plan=json.loads(path.read_text())
        if plan['replication_source_sha256']!=replication_sources() or plan['config_sha256']!=legacy.digest(config_path) or plan['calibration_sha256']!=legacy.digest(directory/'calibration.jsonl'):
            raise ValueError('Comparison freeze inputs changed')
        return plan
    if (directory/'validation.jsonl').exists():
        raise ValueError('Validation cannot precede the comparison freeze')
    # Preserved runner audits completed full calibration and its manifest.
    rows=legacy.calibrate(config,config_path,directory)
    plan=transfer_plan(reference,config,rows)
    plan.update(frozen_utc=legacy.utc_now(),config_sha256=legacy.digest(config_path),
        calibration_sha256=legacy.digest(directory/'calibration.jsonl'),
        source_sha256=legacy.measurement_sources(),replication_source_sha256=replication_sources(),
        lineage=specification['lineage'],hardware_metadata=specification['hardware_metadata'],
        run_id=specification['run_id'])
    legacy.write_json(path,plan)
    print('Original and local forecasts frozen against exactly the original quotas',flush=True)
    return json.loads(path.read_text())


def analyse(config,directory,plan,output):
    existing_path=output/'study.json'
    if existing_path.exists():
        existing=json.loads(existing_path.read_text())
        expected=dict(new_calibration_sha256=legacy.digest(directory/'calibration.jsonl'),
            new_validation_sha256=legacy.digest(directory/'validation.jsonl'),
            comparison_plan_sha256=legacy.digest(directory/'frozen-plan.json'),
            replication_source_sha256=plan['replication_source_sha256'])
        if any(existing.get(key)!=value for key,value in expected.items()):
            raise ValueError('Retained analysis differs from this run; use a new output directory')
        print('Retaining existing comparison outputs without overwriting their recorded bytes',flush=True)
        return existing
    result=analyse_transfer(plan,legacy.read_rows(directory/'validation.jsonl'))
    result.update(run_id=plan['run_id'],hardware_metadata=plan['hardware_metadata'],lineage=plan['lineage'],
        new_calibration_sha256=legacy.digest(directory/'calibration.jsonl'),
        new_validation_sha256=legacy.digest(directory/'validation.jsonl'),
        comparison_plan_sha256=legacy.digest(directory/'frozen-plan.json'),
        analysed_utc=legacy.utc_now(),replication_source_sha256=plan['replication_source_sha256'])
    output.mkdir(parents=True,exist_ok=True)
    legacy.write_json(output/'study.json',result)
    with (output/'comparison.csv').open('w',newline='') as handle:
        writer=csv.writer(handle,lineterminator='\n')
        writer.writerow(['condition','size','observed_survival','original_survival','local_survival','original_tolerance'])
        for name,row in result['conditions'].items():
            for i,size in enumerate(config['sizes']):
                writer.writerow([name,size,row['observed']['survival_at_sizes'][i],
                    row['original_forecasts']['joint']['survival_at_sizes'][i],
                    row['local_forecasts']['joint']['survival_at_sizes'][i],row['original_tolerance']])
    with (output/'opportunities.csv').open('w',newline='') as handle:
        fields=list(result['opportunities'][0])
        writer=csv.DictWriter(handle,fieldnames=fields,lineterminator='\n')
        writer.writeheader();writer.writerows(result['opportunities'])
    transfer_figures(result,output)
    print(json.dumps(result['summary'],indent=2),flush=True)
    return result


def register(config,config_path,directory,output,result):
    algorithms=[]
    for path in result['replication_source_sha256']:
        algorithms.append(dict(name=path,sources=[archive_reference(ROOT,path)]))
    paths=['transfer-specification.json','study-specification.json','calibration-manifest.json',
           'calibration.jsonl','frozen-plan.json','validation.jsonl']
    if (directory/'hardware-metadata.json').exists(): paths.append('hardware-metadata.json')
    entry=dict(schema_version=1,run_id=result['run_id'],evidence_kind='actual_measurement',
        resources=[dict(name='peak resident memory',definition=config['memory_resource'],units='bytes'),
                   dict(name='workload processor time',definition=config['cpu_resource'],units='CPU seconds')],
        data_inputs=[file_reference(ROOT,str((directory/path).relative_to(ROOT))) for path in paths]
                    +[result['lineage'][key] for key in ('reference_plan','reference_calibration','reference_validation')],
        generated_seeds=dict(ordering_and_bootstrap_seed=config['seed'],matrix_seed_rule='SeedSequence([1729,size])',probe_seed_rule='SeedSequence([1730,size])'),
        algorithms=algorithms,configs=[archive_reference(ROOT,str(config_path.relative_to(ROOT)))],
        artifacts=[file_reference(ROOT,str(path.relative_to(ROOT))) for path in sorted(output.glob('*')) if path.is_file()],
        relationships=[dict(run_id=config['reference_run_id'],type='transfer_replication')],
        summary=result['summary'],hardware_metadata=result['hardware_metadata'])
    legacy.write_json(directory/'registry-entry.json',entry)
    print(json.dumps(register_run(ROOT,entry)),flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,default=ROOT/'configs/workload_transfer_2026-10-01.json')
    parser.add_argument('--directory',type=Path,default=ROOT/'data/workload-transfer/2026-10-01b')
    parser.add_argument('--output',type=Path,default=ROOT/'results/workload-transfer')
    parser.add_argument('--stage',choices=['calibrate','freeze','validate','analyse','register','all'],default='all')
    args=parser.parse_args();config=json.loads(args.config.read_text())
    args.directory=args.directory.resolve();args.output=args.output.resolve();args.config=args.config.resolve()
    args.directory.mkdir(parents=True,exist_ok=True)
    started=time.perf_counter()
    prepare(config,args.config,args.directory)
    if args.stage in ('calibrate','all'):legacy.calibrate(config,args.config,args.directory)
    if args.stage in ('freeze','validate','analyse','register','all'):plan=freeze(config,args.config,args.directory)
    if args.stage in ('validate','all'):legacy.validate(config,args.directory,plan)
    if args.stage in ('analyse','all'):result=analyse(config,args.directory,plan,args.output)
    if args.stage=='register':result=json.loads((args.output/'study.json').read_text())
    if args.stage in ('register','all'):register(config,args.config,args.directory,args.output,result)
    print(f'Completed {args.stage} in {time.perf_counter()-started:.2f}s',flush=True)


if __name__=='__main__':main()
