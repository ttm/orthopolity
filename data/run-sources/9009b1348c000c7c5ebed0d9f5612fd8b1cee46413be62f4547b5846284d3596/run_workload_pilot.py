"""Calibrate, freeze, execute, and analyse actual resource-quota workloads.

Each stage leaves a file-backed record. Existing measurement and freeze files
are resumed, never silently regenerated; use a new directory for a new study.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
WORKER = ROOT / 'experiments/workload_worker.py'


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def plain(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {str(k): plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [plain(v) for v in value]
    return value


def write_json(path, value):
    Path(path).write_text(json.dumps(plain(value), indent=2, allow_nan=False) + '\n')


def read_rows(path):
    if not Path(path).exists():
        return []
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line]


def append_row(path, row):
    with Path(path).open('a') as handle:
        handle.write(json.dumps(plain(row), allow_nan=False) + '\n')
        handle.flush()


def measurement_sources():
    return {str(path.relative_to(ROOT)): digest(path) for path in (
        WORKER, ROOT / 'src/orthopolity/workload.py',
        ROOT / 'src/orthopolity/workload_prediction.py',
        ROOT / 'src/orthopolity/workload_analysis.py', Path(__file__),
    )}


def worker(config, size, *, memory_budget=None, cpu_budget=None):
    command = [sys.executable, str(WORKER), '--size', str(size),
               '--repeats', str(config['matrix_repeats']),
               '--warmup-size', str(config['warmup_size'])]
    if memory_budget is not None:
        command.extend(['--memory-budget-bytes', str(int(memory_budget))])
    if cpu_budget is not None:
        command.extend(['--cpu-budget-seconds', str(float(cpu_budget))])
    environment = os.environ.copy()
    environment.update(config['thread_environment'])
    environment['PYTHONPATH'] = str(ROOT / 'src')
    result = subprocess.run(command, env=environment, text=True, capture_output=True,
                            timeout=config['worker_timeout_seconds'], check=True)
    measurement = json.loads(result.stdout)
    if measurement['peak_rss_bytes'] > config['maximum_total_worker_memory_bytes']:
        raise RuntimeError('Measured worker memory exceeds declared pilot bound')
    return measurement


def audit_calibration(config, rows):
    from orthopolity.workload_prediction import calibration_profiles
    expected={(block,size) for block in range(config['calibration_blocks']) for size in config['sizes']}
    actual={(row['block_id'],row['size']) for row in rows}
    if actual!=expected or len(rows)!=len(expected):
        raise ValueError('Calibration must retain every planned block and size exactly once')
    for row in rows:
        if not row['completed'] or not row['numerical_valid'] or row['status']!='completed':
            raise ValueError('A retained calibration task failed; start a new study after inspection')
        if row['cpu_seconds']>config['maximum_calibration_cpu_seconds'] or row['peak_rss_bytes']>config['maximum_total_worker_memory_bytes']:
            raise ValueError('A retained calibration task exceeds the declared pilot bound')
    return calibration_profiles(rows,config['sizes'])


def calibrate(config, config_path, directory):
    path = directory / 'calibration.jsonl'
    manifest_path = directory / 'calibration-manifest.json'
    current_sources = measurement_sources()
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        if manifest['config_sha256'] != digest(config_path) or manifest['source_sha256'] != current_sources:
            raise ValueError('Configuration/source changed: start a new study directory')
        if manifest['calibration_sha256'] != digest(path):
            raise ValueError('Calibration measurements changed after completion')
        rows=read_rows(path)
        audit_calibration(config,rows)
        return rows
    marker_path = directory / 'study-specification.json'
    specification = dict(config=config, config_sha256=digest(config_path),
                         source_sha256=current_sources)
    if marker_path.exists():
        existing = json.loads(marker_path.read_text())
        if any(existing[key] != value for key, value in specification.items()):
            raise ValueError('An incomplete study has a different specification')
    else:
        write_json(marker_path, dict(specification, started_utc=utc_now()))
    rows = read_rows(path)
    done = {(row['block_id'], row['size']) for row in rows}
    expected = config['calibration_blocks'] * len(config['sizes'])
    for block in range(config['calibration_blocks']):
        rng = np.random.default_rng(np.random.SeedSequence([config['seed'], 1, block]))
        for position, size in enumerate(rng.permutation(config['sizes'])):
            if (block, int(size)) in done:
                continue
            measurement = worker(config, int(size))
            row = dict(split='calibration', block_id=block, order_in_block=position,
                       measured_utc=utc_now(), **measurement)
            append_row(path, row)
            rows.append(row)
            if not row['completed'] or not row['numerical_valid']:
                raise RuntimeError('Calibration task failed; preserve record and inspect')
            if row['cpu_seconds'] > config['maximum_calibration_cpu_seconds']:
                raise RuntimeError('Calibration cost exceeds declared pilot bound')
        print(f'Calibration block {block + 1}/{config["calibration_blocks"]} retained', flush=True)
    audit_calibration(config,rows)
    blas=np.__config__.CONFIG.get('Build Dependencies',{}).get('blas',{})
    write_json(manifest_path, dict(config_sha256=digest(config_path),
        source_sha256=current_sources, calibration_sha256=digest(path),
        completed_utc=utc_now(), rows=len(rows),
        environment=dict(python=platform.python_version(), numpy=np.__version__,
            system=platform.system(), architecture=platform.machine(),
            logical_cpu_count=os.cpu_count(), thread_environment=config['thread_environment'],
            blas_name=blas.get('name','unavailable'),
            runtime_thread_count_verified=False),
        interpretation='Actual fresh-process measurements; serial randomized calibration blocks'))
    return rows


def budget_levels(median, config, *, integer=False):
    median = np.asarray(median, dtype=float)
    levels = np.r_[median[0] * config['lowest_budget_factor'],
                   (median[:-1] + median[1:]) / 2,
                   median[-1] * config['highest_budget_factor']]
    return np.rint(levels).astype(np.int64) if integer else levels


def freeze(config, config_path, directory):
    from orthopolity.workload_prediction import calibration_profiles, forecast_largest
    path = directory / 'frozen-plan.json'
    if path.exists():
        plan = json.loads(path.read_text())
        if plan['config_sha256'] != digest(config_path) or plan['calibration_sha256'] != digest(directory / 'calibration.jsonl') or plan['source_sha256'] != measurement_sources():
            raise ValueError('Frozen plan inputs changed; use a new study')
        return plan
    if (directory / 'validation.jsonl').exists():
        raise ValueError('Validation exists before prediction freeze')
    manifest_path=directory/'calibration-manifest.json'
    if not manifest_path.exists():
        raise ValueError('Complete the full declared calibration before freezing predictions')
    manifest=json.loads(manifest_path.read_text())
    if manifest['config_sha256']!=digest(config_path) or manifest['source_sha256']!=measurement_sources() or manifest['calibration_sha256']!=digest(directory/'calibration.jsonl'):
        raise ValueError('Calibration manifest inputs changed')
    profile = audit_calibration(config,read_rows(directory / 'calibration.jsonl'))
    memory = budget_levels(profile['median_memory_bytes'], config, integer=True)
    cpu = budget_levels(profile['median_cpu_seconds'], config)
    n = len(memory)
    conditions = {}
    for condition in config['conditions']:
        permutation = np.arange(n)
        if condition == 'opposed':
            permutation = permutation[::-1]
        elif condition == 'permuted':
            permutation = np.roll(permutation, config['permutation_shift'])
        elif condition not in ('aligned', 'cpu_tightened'):
            raise ValueError('Unknown budget condition')
        paired_cpu = cpu[permutation]
        if condition == 'cpu_tightened':
            paired_cpu = paired_cpu * config['cpu_tightening_factor']
        forecasts = {mode: forecast_largest(profile, memory, paired_cpu, mode=mode)
                     for mode in ['joint', 'median', 'memory_only', 'cpu_only', 'resource_independent']}
        forecasts['budget_independent'] = forecast_largest(
            profile, np.repeat(memory, n), np.tile(paired_cpu, n), mode='joint')
        conditions[condition] = dict(memory_budgets_bytes=memory, cpu_budgets_seconds=paired_cpu,
                                    cpu_level_permutation=permutation, forecasts=forecasts)
    plan = dict(frozen_utc=utc_now(), config_sha256=digest(config_path),
                calibration_sha256=digest(directory / 'calibration.jsonl'),
                source_sha256=measurement_sources(), config=config,
                calibrated_profile=profile, conditions=conditions,
                budget_strata=n, validation_blocks=n*config['validation_repetitions_per_budget_stratum'])
    plan['design'] = design_simulation(plan)
    write_json(path, plan)
    print(f'Predictions frozen for {plan["validation_blocks"]} blocks and {len(conditions)} conditions', flush=True)
    return json.loads(path.read_text())


def design_simulation(plan):
    """Conditional calibration-replay design, completed before validation."""
    config = plan['config']
    profile = plan['calibrated_profile']
    memory_cost = np.asarray(profile['memory_costs'])
    cpu_cost = np.asarray(profile['cpu_costs'])
    sizes = np.asarray(config['sizes'])
    rng = np.random.default_rng(np.random.SeedSequence([config['seed'], 3]))
    nblocks = plan['validation_blocks']
    strata = np.tile(np.arange(plan['budget_strata']), config['validation_repetitions_per_budget_stratum'])
    traces = rng.integers(0, len(memory_cost), size=(config['design_simulations'], nblocks))
    output = {}
    baseline_modes = ['memory_only', 'cpu_only', 'budget_independent']
    for name, condition in plan['conditions'].items():
        memory_budget = np.asarray(condition['memory_budgets_bytes'])[strata]
        cpu_budget = np.asarray(condition['cpu_budgets_seconds'])[strata]
        success = ((memory_cost[traces] <= memory_budget[None, :, None]) &
                   (cpu_cost[traces] <= cpu_budget[None, :, None]))
        largest = np.max(np.where(success, sizes, 0), axis=-1)
        survival = np.mean(largest[:, :, None] >= sizes, axis=1)
        main = np.asarray(condition['forecasts']['joint']['survival_at_sizes'])
        errors = np.max(np.abs(survival-main), axis=1)
        tolerance = float(np.quantile(errors, config['nominal_interval_level']))
        gains = {}
        for mode in baseline_modes:
            baseline = np.asarray(condition['forecasts'][mode]['survival_at_sizes'])
            improvement = np.mean((survival-baseline)**2,axis=1)-np.mean((survival-main)**2,axis=1)
            gains[mode] = dict(mean_squared_profile_error_improvement=float(improvement.mean()),
                              positive_improvement_fraction=float(np.mean(improvement>0)))
        output[name] = dict(absolute_profile_error_tolerance=tolerance,
                            comparator_design=gains)
    return dict(method='Draw whole measured calibration cost profiles; balanced budget strata; conditional on this calibration sample',
                simulations=config['design_simulations'], nominal_level=config['nominal_interval_level'],
                tolerance_rule='Quantile of max absolute survival error; allow one observation quantum 1/n to avoid a zero tolerance',
                conditions={name:dict(row, absolute_profile_error_tolerance=max(row['absolute_profile_error_tolerance'],1/nblocks))
                            for name,row in output.items()},
                limitation='Conditional design calculation without a guaranteed false-positive rate; does not propagate unknown hardware drift')


def validate(config, directory, plan):
    path = directory / 'validation.jsonl'
    freeze_sha = digest(directory / 'frozen-plan.json')
    if plan['source_sha256'] != measurement_sources():
        raise ValueError('Measurement sources changed after prediction freeze')
    rows = read_rows(path)
    if any(row['frozen_plan_sha256'] != freeze_sha for row in rows):
        raise ValueError('Validation references a different frozen plan')
    done = {(row['block_id'], row['condition'], row['size']) for row in rows}
    conditions = list(plan['conditions'])
    for block in range(plan['validation_blocks']):
        stratum = block % plan['budget_strata']
        tasks = [(condition, size) for condition in conditions for size in config['sizes']]
        rng = np.random.default_rng(np.random.SeedSequence([config['seed'], 4, block]))
        for order, position in enumerate(rng.permutation(len(tasks))):
            condition, size = tasks[position]
            if (block, condition, size) in done:
                continue
            settings = plan['conditions'][condition]
            memory_budget = settings['memory_budgets_bytes'][stratum]
            cpu_budget = settings['cpu_budgets_seconds'][stratum]
            measurement = worker(config, size, memory_budget=memory_budget, cpu_budget=cpu_budget)
            row = dict(split='validation', block_id=block, budget_stratum=stratum,
                       condition=condition, order_in_block=order,
                       measured_utc=utc_now(), frozen_plan_sha256=freeze_sha,
                       **measurement)
            append_row(path, row)
            rows.append(row)
        print(f'Validation block {block+1}/{plan["validation_blocks"]} retained', flush=True)
    expected = plan['validation_blocks']*len(conditions)*len(config['sizes'])
    if len(rows) != expected:
        raise ValueError('Validation grid incomplete or duplicated')
    return rows


def analyse(config, directory, plan, output):
    from orthopolity.workload_analysis import analyse_pilot, pilot_figures
    result = analyse_pilot(plan, read_rows(directory/'validation.jsonl'))
    result.update(calibration_sha256=digest(directory/'calibration.jsonl'),
                  validation_sha256=digest(directory/'validation.jsonl'),
                  frozen_plan_sha256=digest(directory/'frozen-plan.json'),
                  analysed_utc=utc_now(), environment=json.loads((directory/'calibration-manifest.json').read_text())['environment'])
    output.mkdir(parents=True, exist_ok=True)
    write_json(output/'study.json', result)
    with (output/'opportunities.csv').open('w',newline='') as handle:
        columns=['block_id','budget_stratum','condition','memory_budget_bytes','cpu_budget_seconds','largest_completed_size','zero_completion','upper_censored','nonmonotone_success_pattern']
        writer=csv.DictWriter(handle,fieldnames=columns,lineterminator='\n')
        writer.writeheader()
        writer.writerows(result['opportunities'])
    pilot_figures(result, output)
    print(json.dumps(result['summary'],indent=2),flush=True)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,default=ROOT/'configs/workload_pilot_2026-10-01.json')
    parser.add_argument('--directory',type=Path,default=ROOT/'data/workload-pilot/2026-10-01')
    parser.add_argument('--output',type=Path,default=ROOT/'results/workload-pilot')
    parser.add_argument('--stage',choices=['calibrate','freeze','validate','analyse','all'],default='all')
    args=parser.parse_args()
    config=json.loads(args.config.read_text())
    if config['sizes']!=sorted(set(config['sizes'])) or min(config['sizes'])<2 or max(config['sizes'])>2048:
        raise ValueError('Declared grid must be unique, increasing, and within the bounded pilot size domain')
    args.directory.mkdir(parents=True,exist_ok=True)
    started=time.perf_counter()
    if args.stage in ('calibrate','all'):
        calibrate(config,args.config,args.directory)
    if args.stage in ('freeze','all'):
        freeze(config,args.config,args.directory)
    if args.stage in ('validate','analyse','all'):
        plan=freeze(config,args.config,args.directory)
        if args.stage in ('validate','all'):
            validate(config,args.directory,plan)
        if args.stage in ('analyse','all'):
            analyse(config,args.directory,plan,args.output)
    print(f'Completed {args.stage} stage in {time.perf_counter()-started:.2f}s',flush=True)


if __name__=='__main__':
    main()
