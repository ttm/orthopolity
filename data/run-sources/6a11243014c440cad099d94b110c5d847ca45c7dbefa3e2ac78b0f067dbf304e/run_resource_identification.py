"""Freeze, simulate, and audit an exponent-sufficiency counterexample."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import time
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import scipy

from orthopolity.figures import save_figure
from orthopolity.interventions import monte_carlo_rank_pvalue, wilson_interval
from orthopolity.resource_identification import (
    binned_deviance, coordinate_prediction, curvature, hazard_extrema,
    inverse_cdf_table, log_density, matched_curvature, population_summary,
    removal_hazard, sample_cohorts,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ['experiments/run_resource_identification.py',
           'src/orthopolity/resource_identification.py',
           'src/orthopolity/interventions.py', 'src/orthopolity/figures.py']
NAMES = ['neutral', 'curved_same_exponent', 'shifted_power']


def utc():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_bundle():
    return {name: digest(ROOT/name) for name in SOURCES}


def write_json_new(path, value):
    with Path(path).open('x') as stream:
        stream.write(json.dumps(value, indent=2, allow_nan=False)+'\n')


def freeze(config_path, directory):
    config = json.loads(config_path.read_text())
    path = directory/'frozen-plan.json'
    if path.exists():
        plan = json.loads(path.read_text())
        if plan['config_sha256'] != digest(config_path) or plan['source_sha256'] != source_bundle():
            raise ValueError('Frozen configuration or algorithms changed; use a separate run directory')
        if plan['versions']['numpy'] != np.__version__:
            raise ValueError('The frozen random-number implementation requires the recorded NumPy version')
        return plan
    if any((directory/name).exists() for name in ('calibration.npz', 'validation.npz')):
        raise ValueError('Samples cannot precede the prospective prediction freeze')
    lo, hi = config['domain']
    if lo != 1 or hi <= lo:
        raise ValueError('This explicit construction requires the domain [1, upper], upper>1')
    width = float(np.log(hi))
    d = config['resource']['cost_exponent']
    if d <= 0 or config['log_growth_rate'] <= 0 or not 0 < config['alpha'] < 1:
        raise ValueError('Positive physical cost dimension, growth, and valid alpha required')
    model = matched_curvature(width, d)
    specifications = [(model, 0.), (model, config['curvature_amplitude']),
                      (matched_curvature(width, config['shifted_removal_rate']/config['log_growth_rate']), 0.)]
    populations = []
    for name, (parameters, amplitude) in zip(NAMES, specifications):
        hazard = hazard_extrema(parameters, amplitude, config['log_growth_rate'])
        if hazard['minimum'] <= 0:
            raise ValueError('The specified removal intervention must have a positive hazard throughout the domain')
        table = inverse_cdf_table(parameters, amplitude, config['inverse_cdf_grid_points'])
        if table['maximum_midpoint_cdf_error'] > config['maximum_audited_cdf_interpolation_error']:
            raise ValueError('Inverse-CDF midpoint error exceeds the frozen numerical tolerance')
        summary = population_summary(parameters, amplitude, d, config['log_bins'])
        populations.append(dict(name=name, parameters=parameters, amplitude=float(amplitude),
            hazard_extrema=hazard, numerical_sampling_audit=dict(
                knots=config['inverse_cdf_grid_points'],
                maximum_midpoint_cdf_error=table['maximum_midpoint_cdf_error'],
                interpretation='Numerical error at table midpoints, not a certified global error bound'),
            **summary))
    if abs(populations[0]['population_bounded_power_mle']-populations[1]['population_bounded_power_mle']) > 1e-10:
        raise ValueError('The independently audited population exponents must match')
    plan = dict(run_id=config['run_id'], frozen_utc=utc(), config=config,
        config_path=str(config_path.relative_to(ROOT)), config_sha256=digest(config_path),
        source_sha256=source_bundle(), populations=populations,
        log_bin_edges=np.linspace(0, width, config['log_bins']+1).tolist(),
        primary_null_exponent=float(d+1),
        mechanism='Stationary solution g*d(n)/du=-h(u)*n(u), external entry at u=0 and exit at u=L; removal hazard and growth are specified before simulation.',
        stage_order='prediction freeze, independent null calibration, held-out stationary cross sections, analysis',
        versions=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__, matplotlib=matplotlib.__version__))
    directory.mkdir(parents=True, exist_ok=True)
    write_json_new(path, plan)
    return plan


def audit_stage(directory, stage):
    manifest = json.loads((directory/f'{stage}-manifest.json').read_text())
    if manifest['data_sha256'] != digest(directory/f'{stage}.npz') or manifest['frozen_plan_sha256'] != digest(directory/'frozen-plan.json'):
        raise ValueError(f'{stage} data do not match the frozen provenance record')
    return manifest


def collect(plan, directory, stage):
    config = plan['config']
    if plan['source_sha256'] != source_bundle():
        raise ValueError('Frozen algorithms changed')
    path = directory/f'{stage}.npz'
    manifest_path = directory/f'{stage}-manifest.json'
    plan_hash = digest(directory/'frozen-plan.json')
    if path.exists() or manifest_path.exists():
        audit_stage(directory, stage)
        return
    is_calibration = stage == 'calibration'
    stage_stream = 10 if is_calibration else 20
    replicates = config['null_calibration_replicates'] if is_calibration else config['heldout_replicates']
    all_counts, all_log_sums, all_exponents, all_resource = [], [], [], []
    for n_index, n in enumerate(config['sample_sizes']):
        counts, sums, exponents, resource = [], [], [], []
        for scenario_index, population in enumerate(plan['populations']):
            model, amplitude = population['parameters'], population['amplitude']
            table = inverse_cdf_table(model, amplitude, config['inverse_cdf_grid_points']) if amplitude else None
            rng = np.random.default_rng(np.random.SeedSequence([config['seed'], stage_stream, n_index, scenario_index]))
            samples = sample_cohorts(model, amplitude, n, replicates, config['log_bins'], rng, table=table,
                                     resource_exponent=config['resource']['cost_exponent'])
            counts.append(samples['counts']); sums.append(samples['log_sums']); exponents.append(samples['exponent'])
            resource.append(samples['resource_bin_totals'])
        all_counts.append(counts); all_log_sums.append(sums); all_exponents.append(exponents)
        all_resource.append(resource)
        print(f'{stage}: {replicates} cohorts per condition at n={n}', flush=True)
    with path.open('xb') as stream:
        np.savez_compressed(stream, counts=np.asarray(all_counts), log_sums=np.asarray(all_log_sums),
                            exponents=np.asarray(all_exponents), resource_bin_totals=np.asarray(all_resource))
    write_json_new(manifest_path, dict(stage=stage, completed_utc=utc(), data_sha256=digest(path),
        frozen_plan_sha256=plan_hash, shape_order=['sample_size', 'scenario', 'replicate', 'bin'],
        scenarios=NAMES, sample_sizes=config['sample_sizes'], replicates=replicates,
        streams=[[config['seed'], stage_stream, ni, si]
                 for ni in range(len(config['sample_sizes'])) for si in range(len(NAMES))],
        retained_statistics='Exact continuous log sums and all bin counts reconstruct MLE and deviance; exact per-bin physical resource totals are retained; individual log sizes are not retained.'))


def rate(values, level):
    values = np.asarray(values, dtype=bool)
    n, k = len(values), int(values.sum())
    return dict(rate=float(k/n), successes=k, replicates=n,
                monte_carlo_interval=list(wilson_interval(k, n, level)))


def analyse(plan, directory, output):
    for stage in ('calibration', 'validation'):
        audit_stage(directory, stage)
    hashes = {name: digest(directory/name) for name in [
        'frozen-plan.json', 'calibration.npz', 'calibration-manifest.json',
        'validation.npz', 'validation-manifest.json']}
    study_path = output/'study.json'
    if study_path.exists():
        previous = json.loads(study_path.read_text())
        if previous['data_sha256'] != hashes:
            raise ValueError('Registered-style outputs cannot be overwritten after input changes')
        return previous
    config = plan['config']; alpha = config['alpha']; level = config['monte_carlo_interval_level']
    cal = np.load(directory/'calibration.npz'); val = np.load(directory/'validation.npz')
    p0 = np.asarray(plan['populations'][0]['object_bin_probabilities'])
    rows = []
    pvalues = np.empty((len(config['sample_sizes']), len(NAMES), config['heldout_replicates'], 3))
    for ni, n in enumerate(config['sample_sizes']):
        exponent_null = np.abs(cal['exponents'][ni, 0]-plan['primary_null_exponent'])
        profile_null = binned_deviance(cal['counts'][ni, 0], p0)
        for si, population in enumerate(plan['populations']):
            exponent_p = monte_carlo_rank_pvalue(np.abs(val['exponents'][ni, si]-plan['primary_null_exponent']), exponent_null)
            profile_p = monte_carlo_rank_pvalue(binned_deviance(val['counts'][ni, si], p0), profile_null)
            mechanism_p = monte_carlo_rank_pvalue(
                binned_deviance(val['counts'][ni, si], population['object_bin_probabilities']),
                binned_deviance(cal['counts'][ni, si], population['object_bin_probabilities']))
            pvalues[ni, si] = np.stack([exponent_p, profile_p, mechanism_p], axis=-1)
            mle = val['exponents'][ni, si]
            counts = val['counts'][ni, si]
            resource = val['resource_bin_totals'][ni, si]
            observed_resource_probability = resource/resource.sum(axis=-1, keepdims=True)
            true_resource = np.asarray(population['resource_per_log_bin'])
            true_resource_probability = true_resource/true_resource.sum()
            resource_error = .5*np.abs(observed_resource_probability-true_resource_probability).sum(axis=-1)
            rows.append(dict(scenario=population['name'], sample_size=n,
                exponent_compatibility=rate(exponent_p > alpha, level),
                frozen_neutral_profile_rejection=rate(profile_p <= alpha, level),
                frozen_mechanism_profile_rejection=rate(mechanism_p <= alpha, level),
                exponent_compatible_but_neutral_profile_rejected=rate((exponent_p > alpha) & (profile_p <= alpha), level),
                observed_exponent=dict(mean=float(mle.mean()), sd=float(mle.std(ddof=1)),
                    quantile_025=float(np.quantile(mle, .025)), quantile_975=float(np.quantile(mle, .975))),
                mean_zero_count_bins=float(np.mean((counts == 0).sum(axis=-1))),
                physical_mass_profile_total_variation=dict(mean=float(resource_error.mean()),
                    quantile_90=float(np.quantile(resource_error, .9))),
                population_exponent=population['population_bounded_power_mle'],
                population_resource_max_log_departure=population['binned_max_log_departure']))
    coordinates = {population['name']: [coordinate_prediction(population['population_bounded_power_mle'],
                    config['resource']['cost_exponent'], c) for c in config['coordinate_powers']]
                   for population in plan['populations']}
    result = dict(run_id=plan['run_id'], config=config, frozen_plan_sha256=hashes['frozen-plan.json'],
        data_sha256=hashes, source_sha256=plan['source_sha256'], populations=plan['populations'],
        operating_characteristics=rows, coordinate_transformations=coordinates,
        calibration='Independent finite-sample Monte Carlo upper-tail rank p=(1+#calibration>=observed)/(R+1), ties conservative. Tests target different properties and are reported separately; no combined familywise claim.',
        monte_carlo_intervals='Wilson binomial intervals conditional on the frozen calibration realization. They quantify outer sampling uncertainty, not physical-model uncertainty or an exact interval for resources.',
        interpretation=config['interpretation'])
    output.mkdir(parents=True, exist_ok=True)
    with (output/'pvalues.npz').open('xb') as stream:
        np.savez_compressed(stream, pvalues=pvalues)
    write_json_new(study_path, result)
    with (output/'decisions.csv').open('x', newline='') as stream:
        fields = ['scenario', 'sample_size', 'exponent_compatibility', 'neutral_profile_rejection',
                  'mechanism_profile_rejection', 'exponent_compatible_profile_rejected', 'observed_exponent_mean']
        writer = csv.DictWriter(stream, fieldnames=fields); writer.writeheader()
        for row in rows:
            writer.writerow(dict(scenario=row['scenario'], sample_size=row['sample_size'],
                exponent_compatibility=row['exponent_compatibility']['rate'],
                neutral_profile_rejection=row['frozen_neutral_profile_rejection']['rate'],
                mechanism_profile_rejection=row['frozen_mechanism_profile_rejection']['rate'],
                exponent_compatible_profile_rejected=row['exponent_compatible_but_neutral_profile_rejected']['rate'],
                observed_exponent_mean=row['observed_exponent']['mean']))
    figures(plan, result, output)
    return result


def figures(plan, result, output):
    config = plan['config']; width = np.log(config['domain'][1]); d = config['resource']['cost_exponent']
    u = np.linspace(0, width, 1001); x = np.exp(u)
    colors = ['#28669b', '#ba5c22', '#6a4c93']
    labels = ['Neutral reference', 'Curvature, same population MLE', 'Changed constant removal']
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'svg.fonttype': 'none'})
    fig, axes = plt.subplots(2, 2, figsize=(11.5, 8), layout='constrained')
    for si, (population, color, label) in enumerate(zip(plan['populations'], colors, labels)):
        model, amp = population['parameters'], population['amplitude']
        resource = np.exp(d*u)*log_density(u, model, amp)
        # Exact population average across equal-width log bins supplies the normalizer.
        resource /= np.mean(population['resource_per_log_bin'])
        axes[0, 0].plot(x, resource, color=color, label=label)
        axes[0, 1].plot(x, removal_hazard(u, model, amp, config['log_growth_rate']), color=color, label=label)
        subset = [row for row in result['operating_characteristics'] if row['scenario'] == population['name']]
        for ax, key in [(axes[1, 0], 'exponent_compatibility'), (axes[1, 1], 'frozen_neutral_profile_rejection')]:
            xs = [row['sample_size'] for row in subset]
            values = np.array([row[key]['rate'] for row in subset])
            intervals = np.array([row[key]['monte_carlo_interval'] for row in subset])
            # At rates exactly zero or one, floating-point Wilson endpoints
            # can exceed the point estimate by <3e-16. Plot distances stay
            # nonnegative; the recorded numerical intervals remain untouched.
            errors = np.maximum(np.stack([values-intervals[:, 0], intervals[:, 1]-values]), 0)
            ax.errorbar(xs, values, yerr=errors,
                        color=color, fmt='o-', capsize=3, label=label, lw=1.3)
    axes[0, 0].axhline(1, color='gray', ls=':', lw=1)
    axes[0, 0].set(xscale='log', xlabel='Mass x (fixed units)', ylabel='Normalized mass per log size',
                   title='Same measured resource; different complete profiles')
    axes[0, 1].set(xscale='log', xlabel='Mass x (fixed units)', ylabel='Removal hazard per time unit',
                   title='Positive growth/removal mechanisms frozen before sampling')
    axes[1, 0].set(xscale='log', xlabel='Independent objects in each cohort', ylabel='Exponent compatibility fraction',
                   ylim=(-.02, 1.02), title='Exponent-only test: non-rejection supplies limited information')
    axes[1, 1].set(xscale='log', xlabel='Independent objects in each cohort', ylabel='Frozen neutral profile rejected',
                   ylim=(-.02, 1.02), title='Complete bin probabilities reveal the departure')
    axes[1, 0].axhline(1-config['alpha'], color='gray', ls=':', lw=1)
    axes[1, 1].axhline(config['alpha'], color='gray', ls=':', lw=1)
    for ax in axes.flat:
        ax.legend(fontsize=7, frameon=False); ax.grid(alpha=.2); ax.spines[['top', 'right']].set_visible(False)
    fig.suptitle('An exponent does not identify resource neutrality\n2,000 held-out cohorts per point; intervals show conditional Monte Carlo uncertainty', fontsize=11)
    for suffix in ('png', 'svg'):
        save_figure(fig, output/f'identification.{suffix}', dpi=180)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=['freeze', 'calibrate', 'validate', 'analyse', 'all'], default='all')
    parser.add_argument('--config', type=Path, default=ROOT/'configs/resource_identification_2026-10-01.json')
    parser.add_argument('--directory', type=Path, default=ROOT/'data/resource-identification/2026-10-01-final')
    parser.add_argument('--output', type=Path, default=ROOT/'results/resource-identification')
    args = parser.parse_args(); started = time.perf_counter()
    plan = freeze(args.config.resolve(), args.directory)
    if args.stage in ('calibrate', 'all'):
        collect(plan, args.directory, 'calibration')
    if args.stage in ('validate', 'all'):
        if not (args.directory/'calibration-manifest.json').exists():
            raise ValueError('The independently frozen null calibration must precede validation')
        audit_stage(args.directory, 'calibration')
        collect(plan, args.directory, 'validation')
    if args.stage in ('analyse', 'all'):
        result = analyse(plan, args.directory, args.output)
        for row in result['operating_characteristics']:
            print(f"{row['scenario']} n={row['sample_size']}: exponent compatible {row['exponent_compatibility']['rate']:.4f}, neutral profile rejected {row['frozen_neutral_profile_rejection']['rate']:.4f}")
    print(f'Completed {args.stage} in {time.perf_counter()-started:.2f} s', flush=True)


if __name__ == '__main__':
    main()
