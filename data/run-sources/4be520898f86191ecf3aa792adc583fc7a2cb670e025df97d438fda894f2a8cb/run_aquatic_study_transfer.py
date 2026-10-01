"""Run a retrospective study-excluded aquatic slope forecast on frozen data."""
from __future__ import annotations

import argparse
import csv
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path

import numpy as np
import scipy

from orthopolity.aquatic_study_transfer import analyse,select_rows
from orthopolity.run_registry import archive_reference,collect_hardware_metadata,file_reference,register_run


ROOT=Path(__file__).resolve().parents[1]


def utc_now():return datetime.now(timezone.utc).isoformat()


def write_json(path,value):
    encoded=json.dumps(value,indent=2,allow_nan=False)+'\n'
    if path.exists() and path.read_text()!=encoded:
        raise ValueError(f'Retained file differs; use a new run directory: {path}')
    if not path.exists():path.write_text(encoded)


def sources():
    paths=[Path(__file__),ROOT/'src/orthopolity/aquatic_study_transfer.py',
           ROOT/'src/orthopolity/run_registry.py',ROOT/'src/orthopolity/figures.py']
    return {str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}


def figure(result,output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from orthopolity.figures import save_figure
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'svg.fonttype':'none'})
    fig,axes=plt.subplots(1,2,figsize=(11,5),layout='constrained')
    colors=['#28669b','#b75f29'];panels=[('primary','Direct reported SE'),('ci_assumption_sensitivity','CI-augmented sensitivity (assumed 95% CI)')]
    for ax,(key,title) in zip(axes,panels):
        folds=result[key]['folds'];delta=[f['fixed_minus_training_location_log_score'] for f in folds]
        y=np.arange(len(folds));ax.barh(y,delta,color=[colors[0] if d>=0 else colors[1] for d in delta])
        ax.set_yticks(y,labels=[f["held_study"].replace('StudyID_','')+f" (n={f['held_rows']})" for f in folds])
        ax.axvline(0,color='gray',lw=.8);ax.set(xlabel='Fixed −1 minus training-center log score',ylabel='Entire held-out study',title=title)
        ax.spines[['top','right']].set_visible(False)
    fig.suptitle('Aquatic location prediction across studies\nPositive bars favor −1; shared scatter fitted only to other studies; retrospective reanalysis')
    for suffix in ('png','svg'):save_figure(fig,output/f'study-transfer.{suffix}',dpi=180)
    plt.close(fig)


def register(config,config_path,directory,output,result):
    entry=dict(schema_version=1,run_id=config['run_id'],evidence_kind='actual_measurement',
        resources=[dict(name='reported biomass',definition=config['resource'],units='Source-specific reported biomass units; compared via dimensionless slopes')],
        data_inputs=[file_reference(ROOT,config['input'])]+[file_reference(ROOT,str(p.relative_to(ROOT))) for p in sorted(directory.glob('*')) if p.is_file() and p.name!='registry-entry.json'],
        generated_seeds=dict(status=config['randomness']),
        algorithms=[dict(name='Study-excluded weighted-moment slope prediction',sources=[archive_reference(ROOT,path) for path in result['source_sha256']])],
        configs=[archive_reference(ROOT,str(config_path.relative_to(ROOT)))],
        artifacts=[file_reference(ROOT,str(p.relative_to(ROOT))) for p in sorted(output.glob('*')) if p.is_file()],
        relationships=[dict(run_id='models-2026-10-01',type='empirical_test_of_fixed_cost_prediction')],
        hardware_metadata=result['hardware_metadata'],summary=result['summary'])
    write_json(directory/'registry-entry.json',entry)
    return register_run(ROOT,entry)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,default=ROOT/'configs/aquatic_study_transfer_2026-10-01.json')
    parser.add_argument('--directory',type=Path,default=ROOT/'data/aquatic-study-transfer/2026-10-01')
    parser.add_argument('--output',type=Path,default=ROOT/'results/aquatic-study-transfer')
    parser.add_argument('--register',action='store_true')
    args=parser.parse_args();args.config=args.config.resolve();args.directory=args.directory.resolve();args.output=args.output.resolve()
    config=json.loads(args.config.read_text());args.directory.mkdir(parents=True,exist_ok=True);args.output.mkdir(parents=True,exist_ok=True)
    checksum=json.loads((ROOT/'data/snapshot_checksums.json').read_text())
    expected=next(r['sha256'] for r in checksum if r['file']==Path(config['input']).name)
    input_ref=file_reference(ROOT,config['input']);assert input_ref['sha256']==expected,'Source snapshot changed'
    specification=dict(config=config,config_sha256=hashlib.sha256(args.config.read_bytes()).hexdigest(),
        input=input_ref,source_sha256=sources(),assessment_status='Retrospective reanalysis, held-out by fitting only; source results already inspected')
    spec_path=args.directory/'study-specification.json'
    if spec_path.exists():
        existing=json.loads(spec_path.read_text())
        if any(existing[key]!=value for key,value in specification.items()):raise ValueError('Inputs changed; use a new run')
        specification=existing
    else:
        specification.update(specified_utc=utc_now(),hardware_metadata=collect_hardware_metadata(),
                             numerical_versions=dict(numpy=np.__version__,scipy=scipy.__version__))
        write_json(spec_path,specification)
    result_path=args.output/'study.json'
    if result_path.exists():
        result=json.loads(result_path.read_text())
        if result['source_sha256']!=sources() or result['specification_sha256']!=hashlib.sha256(spec_path.read_bytes()).hexdigest():
            raise ValueError('Output does not belong to this specification')
        print('Reusing retained results without overwriting recorded bytes')
    else:
        rows,membership=select_rows(ROOT/config['input'],config)
        write_json(args.directory/'selected-records.json',rows)
        write_json(args.directory/'membership.json',membership)
        result=analyse(rows,config)
        result.update(run_id=config['run_id'],source_sha256=sources(),completed_utc=utc_now(),
            specification_sha256=hashlib.sha256(spec_path.read_bytes()).hexdigest(),hardware_metadata=specification['hardware_metadata'],
            numerical_versions=specification['numerical_versions'])
        result['summary']=dict(new_observations_collected=0,primary_records=result['primary']['rows'],primary_studies=result['primary']['studies'],
            primary_equal_study_fixed_minus_training_log_score=result['primary']['comparison']['equal_study_mean_fixed_minus_training_log_score'],
            ci_sensitivity_records=result['ci_assumption_sensitivity']['rows'],ci_sensitivity_studies=result['ci_assumption_sensitivity']['studies'],
            ci_sensitivity_fixed_minus_training_log_score=result['ci_assumption_sensitivity']['comparison']['equal_study_mean_fixed_minus_training_log_score'],
            strict_measurement_only_mean_log_score=result['primary']['models']['fixed_neutral_measurement_only']['equal_study_mean_log_score'],
            inference=config['inference'])
        write_json(result_path,result)
        with (args.output/'folds.csv').open('w',newline='') as handle:
            columns=['analysis','held_study','held_rows','training_mean','training_tau','fixed_minus_training_log_score','fixed_log_score','training_log_score','measurement_only_log_score']
            writer=csv.DictWriter(handle,fieldnames=columns,lineterminator='\n');writer.writeheader()
            for key in ('primary','ci_assumption_sensitivity'):
                for fold in result[key]['folds']:
                    writer.writerow(dict(analysis=key,held_study=fold['held_study'],held_rows=fold['held_rows'],training_mean=fold['training']['mean'],
                        training_tau=np.sqrt(fold['training']['tau_squared']),fixed_minus_training_log_score=fold['fixed_minus_training_location_log_score'],
                        fixed_log_score=fold['models']['fixed_neutral_shared_scatter']['mean_log_predictive_density'],
                        training_log_score=fold['models']['training_location_shared_scatter']['mean_log_predictive_density'],
                        measurement_only_log_score=fold['models']['fixed_neutral_measurement_only']['mean_log_predictive_density']))
        figure(result,args.output)
    print(json.dumps(result['summary'],indent=2))
    if args.register:print(register(config,args.config,args.directory,args.output,result))


if __name__=='__main__':main()
