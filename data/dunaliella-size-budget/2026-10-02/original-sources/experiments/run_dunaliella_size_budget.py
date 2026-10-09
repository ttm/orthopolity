#!/usr/bin/env python3
"""Size-law transfer and restoration forecasts for size-selected Dunaliella lineages.

Stages run in order, after the protocol commit:
  forecast  fit each fold on its development lineages and retain parameters
            and size-based forecasts; held-out lineages enter only through
            their measured cell volumes
  evaluate  verify and replay the forecasts, then score held-out lineages
  audit     replay forecasts and evaluation offline

Existing public measurements only (Malerba et al. 2018); no new observations.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from orthopolity.rdata_reader import data_frame, load_rdata  # noqa: E402
from orthopolity.size_budget import (  # noqa: E402
    absolute_errors, carrying_capacity, pairwise_verdict, restoration_forecasts, size_law_forecasts,
)

CONFIG = ROOT / 'configs/dunaliella_size_budget_2026-10-02.json'
AMENDMENT = ROOT / 'configs/dunaliella_size_budget_2026-10-02_amendment-1.json'
PARTITION = ROOT / 'configs/dunaliella_size_budget_2026-10-02_partition.json'
SOURCES = ROOT / 'data/dunaliella-sources/2026-10-02'
BUNDLE = SOURCES / 'extracted/Codes and analysis'
GROWTH = BUNDLE / 'Analysis of demographic rates/All analysis Fig. 3/All raw data.RData'
SIZES = BUNDLE / 'Analysis of demographic rates/All analysis Fig. 3/SummaryData.RData'
SIZES_CHECK = BUNDLE / 'Analysis of cell size/SummaryData.RData'
ASSIGNED = ROOT / 'data/archived-cost-transfer/2026-10-02/calibration.json'
ASSIGNED_ENTRY = ROOT / 'data/archived-cost-transfer/2026-10-02/registry-entry.json'
DATA = ROOT / 'data/dunaliella-size-budget/2026-10-02'
RESULTS = ROOT / 'results/dunaliella-size-budget'
SOURCE_PATHS = [Path('experiments/run_dunaliella_size_budget.py'), Path('src/orthopolity/size_budget.py'),
                Path('src/orthopolity/rdata_reader.py')]
HISTORIES = ['Replete', 'N-Deplete', 'P-Deplete']
SIZE_LABELS = {'Nfull': 'Replete', 'Nfree': 'N-Deplete', 'Pfree': 'P-Deplete'}
OUTCOMES = {'biovolume': 'BiovolUL', 'optical_density': 'OD_BC_man'}
TREATMENT_CODES = {'Small': 'S', 'Control': 'C', 'Large': 'L'}
ASSIGNED_RESOURCES = {'assigned_carbon_cost': 'QC', 'assigned_nitrogen_cost': 'QN'}


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def ref(path):
    return dict(path=Path(path).relative_to(ROOT).as_posix(), sha256=digest(path))


def read_json(path):
    return json.loads(Path(path).read_text())


def save_json(path, value):
    path = Path(path)
    content = (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + '\n').encode()
    if path.exists():
        if path.read_bytes() != content:
            raise RuntimeError(f'Refusing to overwrite changed retained artifact: {path}')
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def verify_reference(reference):
    if digest(ROOT / reference['path']) != reference['sha256']:
        raise RuntimeError(f'Frozen reference changed: {reference["path"]}')


def verify_inputs():
    members = {item['path']: item['sha256'] for item in read_json(SOURCES / 'archive-members.json')}
    references = {}
    for key, path in (('growth', GROWTH), ('sizes', SIZES), ('sizes_check', SIZES_CHECK)):
        reference = ref(path)
        if members.get(reference['path']) != reference['sha256']:
            raise RuntimeError(f'Input differs from the retained archive inventory: {reference["path"]}')
        references[key] = reference
    registered = {item['path']: item['sha256'] for item in read_json(ASSIGNED_ENTRY)['data_inputs']}
    assigned = ref(ASSIGNED)
    if registered.get(assigned['path']) != assigned['sha256']:
        raise RuntimeError('Assigned exponents differ from the registered cost-transfer calibration')
    references['assigned_exponents'] = assigned
    for name in ('acquisition.json', 'archive-members.json', 'bundle-schema.json'):
        references[name] = ref(SOURCES / name)
    return references


def assigned_slopes():
    fitted = read_json(ASSIGNED)['fitted']
    return {name: 1.-fitted[resource]['models']['pooled_free_power']['coefficient']/3.
            for name, resource in ASSIGNED_RESOURCES.items()}


def read_sizes():
    """Log mean prolate-spheroid volume, (pi/6) L W^2, per (lineage, history).

    The second summary repeats every shape column exactly but computes volume
    as (4 pi/3) L W^2 from full axes, exactly 8 times larger (amendment 1);
    both facts are verified rather than assumed.
    """
    frame = data_frame(load_rdata(SIZES)['SummaryData'])
    check = data_frame(load_rdata(SIZES_CHECK)['SummaryData'])
    shape = ('Size', 'Major', 'Minor', 'Perim', 'Circ')
    rows = list(zip(frame['Treat'].factor_labels(), frame['Rep'].decode(), frame['Media'].factor_labels(),
                    frame['Vol'].decode(), *(frame[column].decode() for column in shape)))
    other = {(treat, int(rep), SIZE_LABELS[media]): (volume, values) for treat, rep, media, volume, *values in
             zip(check['Treat'].factor_labels(), check['Rep'].decode(), check['Media'].factor_labels(),
                 check['Vol'].decode(), *(check[column].decode() for column in shape))}
    sizes = {}
    for treat, rep, media, volume, *values in rows:
        key = (f'{TREATMENT_CODES[treat]}.{int(rep)}', media)
        if key in sizes or not (math.isfinite(volume) and volume > 0):
            raise ValueError(f'Duplicate or invalid size summary: {key}')
        repeated = other.get((treat, int(rep), media))
        if repeated is None or repeated[1] != values or not math.isclose(repeated[0], 8.*volume, rel_tol=1e-12):
            raise ValueError(f'Cell-size summaries are not the documented factor-8 pair: {key}')
        sizes[key] = math.log(volume)
    if len(other) != len(sizes):
        raise ValueError('Cell-size summaries cover different lineages')
    return sizes


def read_growth():
    """Per (lineage, history, plate): {day: log outcome} for both outcomes."""
    frame = data_frame(load_rdata(GROWTH)['AllData'])
    treat, media, sample, plate = (frame[name].factor_labels() for name in ('Treat', 'Media', 'Sample', 'Plate'))
    day = frame['Day'].decode()
    wells = {outcome: defaultdict(dict) for outcome in OUTCOMES}
    for outcome, column in OUTCOMES.items():
        values = frame[column].decode()
        for index, value in enumerate(values):
            if sample[index].split('.')[0] != TREATMENT_CODES[treat[index]]:
                raise ValueError(f'Sample and treatment disagree at row {index}')
            key = (sample[index], media[index], plate[index])
            if day[index] in wells[outcome][key]:
                raise ValueError(f'Duplicate reading: {key} day {day[index]}')
            wells[outcome][key][float(day[index])] = math.log(value) if math.isfinite(value) and value > 0 else math.nan
    return wells


def capacities(wells):
    grouped = defaultdict(dict)
    for (lineage, history, plate), readings in wells.items():
        grouped[(lineage, history)][plate] = readings
    return {key: carrying_capacity(plates) for key, plates in grouped.items()}


def lineage_treatment(lineage):
    return {code: name for name, code in TREATMENT_CODES.items()}[lineage.split('.')[0]]


def forecast_computation(k, sizes, config, partition, slopes):
    """Retained forecasts; depends on held-out lineages only through cell volume."""
    lineages = sorted({lineage for lineage, _ in sizes} | {lineage for lineage, _ in k})
    result = {}
    for fold, members in sorted(partition['folds'].items()):
        development = [lineage for lineage in lineages if lineage_treatment(lineage) in members['development']]
        held = [lineage for lineage in lineages if lineage_treatment(lineage) in members['evaluation']]
        if set(development) & set(held) or not development or not held:
            raise ValueError(f'Fold {fold} needs disjoint nonempty development and evaluation lineages')
        dev_units = {lineage: dict(log_volume=sizes[(lineage, 'Replete')], log_k=k[(lineage, 'Replete')])
                     for lineage in development
                     if (lineage, 'Replete') in sizes and k.get((lineage, 'Replete')) is not None}
        held_units = {lineage: dict(log_volume=sizes[(lineage, 'Replete')])
                      for lineage in held if (lineage, 'Replete') in sizes}
        size_law = size_law_forecasts(dev_units, held_units, slopes)
        restoration = {}
        for history in config['endpoints']['E2_restoration']['histories']:
            dev = {lineage: dict(log_k=k[(lineage, history)], replete_log_k=k[(lineage, 'Replete')],
                                 log_volume=sizes[(lineage, history)])
                   for lineage in development
                   if (lineage, history) in sizes and k.get((lineage, history)) is not None
                   and k.get((lineage, 'Replete')) is not None}
            held_volume = {lineage: dict(log_volume=sizes[(lineage, history)])
                           for lineage in held if (lineage, history) in sizes}
            fitted = restoration_forecasts(dev, held_volume)
            restoration[history] = dict(
                parameters=fitted['parameters'], development_units=fitted['development_units'],
                forecasts={name: values for name, values in fitted['forecasts'].items()
                           if name in ('size_law_history', 'constant_history')},
                anchored_rules=dict(full_restoration='observed replete log K of the same lineage',
                                    history_offset=f'observed replete log K + {fitted["parameters"]["development_mean_deficit"]!r}'),
                eligible_units=sorted(held_volume),
                excluded_units=sorted(set(held)-set(held_volume)))
        result[fold] = dict(development_lineages=development, evaluation_lineages=held,
                            size_law=size_law, restoration=restoration,
                            excluded_size_law_units=sorted(set(held)-set(held_units)))
    return result


def evaluation_computation(frozen, k, config):
    endpoints = config['endpoints']
    margin = config['decision_rule']['practical_margin_log']
    folds = sorted(frozen)
    e1_errors, e2_errors, summary = [], [], {}
    for fold in folds:
        item = frozen[fold]
        observed = {lineage: k.get((lineage, 'Replete')) for lineage in item['evaluation_lineages']}
        errors, units = absolute_errors(item['size_law']['forecasts'], observed)
        e1_errors.append(errors)
        forecasts, observed2 = defaultdict(dict), {}
        for history, part in item['restoration'].items():
            deficit = part['parameters']['development_mean_deficit']
            for lineage in part['eligible_units']:
                unit = f'{lineage}|{history}'
                replete = k.get((lineage, 'Replete'))
                observed2[unit] = k.get((lineage, history))
                if replete is not None:
                    forecasts['full_restoration'][unit] = replete
                    forecasts['history_offset'][unit] = replete+deficit
                for name in ('size_law_history', 'constant_history'):
                    forecasts[name][unit] = part['forecasts'][name][lineage]
        errors2, units2 = absolute_errors(dict(forecasts), observed2)
        e2_errors.append(errors2)
        summary[fold] = dict(
            E1=dict(scored_units=units, mean_absolute_log_error={model: float(np.mean(list(values.values())))
                                                                  for model, values in errors.items()},
                    errors=errors, observed=observed),
            E2=dict(scored_units=units2, mean_absolute_log_error={model: float(np.mean(list(values.values())))
                                                                  for model, values in errors2.items()},
                    errors=errors2, observed=observed2))
    verdicts = dict(
        E1=[pairwise_verdict(e1_errors, first, second, margin) for first, second in endpoints['E1_size_law_transfer']['pairs']],
        E2=[pairwise_verdict(e2_errors, first, second, margin) for first, second in endpoints['E2_restoration']['pairs']])
    return dict(folds=summary, verdicts=verdicts)


def computation(config, partition):
    sizes, wells, slopes = read_sizes(), read_growth(), assigned_slopes()
    k = {outcome: capacities(wells[outcome]) for outcome in OUTCOMES}
    return sizes, k, slopes


def serial_capacities(k):
    return {outcome: {f'{lineage}|{history}': value for (lineage, history), value in sorted(values.items())}
            for outcome, values in k.items()}


def forecast():
    target = DATA / 'frozen-forecasts.json'
    if target.exists():
        verify_forecasts()
        return
    if (RESULTS / 'study.json').exists():
        raise RuntimeError('Cannot forecast after evaluation outputs exist')
    config, partition = read_json(CONFIG), read_json(PARTITION)
    if config['run_id'] != partition['run_id']:
        raise RuntimeError('Configuration and partition belong to different runs')
    inputs = verify_inputs()
    sizes, k, slopes = computation(config, partition)
    frozen = {outcome: forecast_computation(k[outcome], sizes, config, partition, slopes) for outcome in OUTCOMES}
    sources, snapshots = [], []
    for source in SOURCE_PATHS:
        snapshot = DATA / 'original-sources' / source
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        if not snapshot.exists():
            snapshot.write_bytes((ROOT / source).read_bytes())
        sources.append(ref(ROOT / source))
        snapshots.append(ref(snapshot))
        if sources[-1]['sha256'] != snapshots[-1]['sha256']:
            raise RuntimeError(f'Source snapshot differs: {source}')
    save_json(target, dict(
        run_id=config['run_id'], status='forecasts_retained_before_scoring', frozen_utc=now(),
        config_reference=ref(CONFIG), partition_reference=ref(PARTITION), amendment_reference=ref(AMENDMENT),
        input_references=inputs,
        source_references=sources, source_snapshot_references=snapshots,
        assigned_slopes=slopes, size_log_volumes={f'{lineage}|{history}': value for (lineage, history), value in sorted(sizes.items())},
        git_head_at_forecast=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        environment=dict(python=sys.version, numpy=np.__version__, platform=platform.platform()),
        separation=('The protocol commit precedes any decoding of small- or large-selected outcomes. Folds are cross-fitted, '
                    'so held-out values of one fold are development values of the other; every retained forecast depends on '
                    'held-out lineages only through their cell volumes, and anchored restoration forecasts apply frozen '
                    'development offsets to observed replete capacities at evaluation.'),
        forecasts=frozen))


def verify_forecasts():
    frozen = read_json(DATA / 'frozen-forecasts.json')
    for reference in [frozen['config_reference'], frozen['partition_reference'], frozen['amendment_reference'],
                      *frozen['input_references'].values(),
                      *frozen['source_references'], *frozen['source_snapshot_references']]:
        verify_reference(reference)
    return frozen


def replay_forecasts(frozen):
    config, partition = read_json(CONFIG), read_json(PARTITION)
    sizes, k, slopes = computation(config, partition)
    replay = {outcome: forecast_computation(k[outcome], sizes, config, partition, slopes) for outcome in OUTCOMES}
    if json.loads(json.dumps(replay)) != frozen['forecasts'] or slopes != frozen['assigned_slopes']:
        raise RuntimeError('Forecast replay differs from the retained forecasts')
    return config, k


def evaluate():
    if (RESULTS / 'study.json').exists():
        audit()
        return
    frozen = verify_forecasts()
    config, k = replay_forecasts(frozen)
    started = now()
    if started <= frozen['frozen_utc']:
        raise RuntimeError('Evaluation would precede the retained forecasts')
    save_json(DATA / 'capacities.json', serial_capacities(k))
    evaluation = {outcome: evaluation_computation(frozen['forecasts'][outcome], k[outcome], config) for outcome in OUTCOMES}
    report = dict(run_id=config['run_id'], status='complete', kind='retrospective_size_selected_lineage_budget_law',
                  evaluation_started_utc=started, frozen_forecasts=ref(DATA / 'frozen-forecasts.json'),
                  capacities_reference=ref(DATA / 'capacities.json'), config_reference=frozen['config_reference'],
                  partition_reference=frozen['partition_reference'],
                  git_head_at_evaluation=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                  evaluation=json.loads(json.dumps(evaluation)),
                  interpretation=('Separately grown size-selected lineages share one medium, so carrying capacity tests the budget '
                                  'closure N q(V) = R and its implied size law. Cost dimensions are development-fitted or assigned '
                                  'cross-taxon, not measured quotas; the lineages are not a coexisting size spectrum.'),
                  statistical_scope=config['statistical_scope'])
    save_json(RESULTS / 'study.json', report)
    save_json(RESULTS / 'output-manifest.json', dict(run_id=config['run_id'], artifacts=[ref(RESULTS / 'study.json')],
                                                   capacities=ref(DATA / 'capacities.json')))


def audit():
    frozen = verify_forecasts()
    config, k = replay_forecasts(frozen)
    report = read_json(RESULTS / 'study.json')
    for key in ('frozen_forecasts', 'capacities_reference'):
        verify_reference(report[key])
    manifest = read_json(RESULTS / 'output-manifest.json')
    for reference in manifest['artifacts'] + [manifest['capacities']]:
        verify_reference(reference)
    if serial_capacities(k) != read_json(DATA / 'capacities.json'):
        raise RuntimeError('Capacity replay differs')
    evaluation = {outcome: evaluation_computation(frozen['forecasts'][outcome], k[outcome], config) for outcome in OUTCOMES}
    if json.loads(json.dumps(evaluation)) != report['evaluation']:
        raise RuntimeError('Evaluation replay differs from the retained report')
    return dict(status='verified_offline', run_id=config['run_id'])


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--stage', choices=['forecast', 'evaluate', 'audit'], required=True)
    stage = parser.parse_args().stage
    {'forecast': forecast, 'evaluate': evaluate, 'audit': audit}[stage]()
    print(json.dumps(dict(stage=stage, status='complete', run_id=read_json(CONFIG)['run_id'])))


if __name__ == '__main__':
    main()
