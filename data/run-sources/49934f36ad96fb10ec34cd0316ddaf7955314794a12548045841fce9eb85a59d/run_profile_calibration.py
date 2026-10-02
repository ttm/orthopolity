"""Freeze and evaluate complete-profile decisions under declared sampling models."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import time
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import scipy
from scipy.optimize import brentq

from orthopolity.figures import save_figure
from orthopolity.interventions import wilson_interval
from orthopolity.profile_calibration import (
    METHODS, batch_profile_decisions, normalized_profile,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ['experiments/run_profile_calibration.py', 'src/orthopolity/profile_calibration.py',
           'src/orthopolity/goodness_of_fit.py', 'src/orthopolity/interventions.py',
           'src/orthopolity/figures.py']
DECISIONS = ['equivalent', 'departure', 'unresolved']


def utc():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_bundle():
    return {name: digest(ROOT/name) for name in SOURCES}


def write_json_new(path, value):
    with Path(path).open('x') as stream:
        stream.write(json.dumps(value, indent=2, allow_nan=False)+'\n')


def profiles(config):
    widths = np.asarray(config['log_widths'], dtype=float)
    centers = np.cumsum(widths)-widths/2
    margin = np.log(config['factor'])
    result = []
    for specification in config['profile_shapes']:
        shape = specification['shape']
        if shape == 'flat':
            phi = np.ones(len(widths))
        elif shape == 'zero':
            phi = np.ones(len(widths)); phi[2] = 0
            phi *= widths.sum()/np.dot(widths, phi)
        else:
            h = centers-centers.mean() if shape == 'gradient' else np.cos(2*np.pi*centers/widths.sum())
            h /= np.max(np.abs(h))
            target = specification['departure_margin_multiple']*margin
            def candidate(amplitude):
                values = np.exp(amplitude*h)
                return values*widths.sum()/np.dot(widths, values)
            amplitude = brentq(lambda value: np.max(np.abs(np.log(candidate(value))))-target,
                                0, 10, xtol=1e-14)
            phi = candidate(amplitude)
        with np.errstate(divide='ignore'):
            log_phi = np.log(phi)
        delta = float(np.max(np.abs(log_phi)))
        if shape == 'zero':
            relation = 'outside'
        elif specification['departure_margin_multiple'] == 1:
            relation = 'boundary'
        else:
            relation = 'inside' if delta < margin else 'outside'
        result.append(dict(name=specification['name'], phi=phi.tolist(),
            log_phi=[float(value) if np.isfinite(value) else None for value in log_phi],
            max_abs_log_departure=delta if np.isfinite(delta) else None,
            departure_infinite=not np.isfinite(delta), truth_relation=relation))
    return result


def generate_blocks(config, population, family, n_blocks, replicates, rng):
    widths = np.asarray(config['log_widths']); phi = np.asarray(population['phi'])
    mean = widths*phi
    kind = family['kind']; bounds = None
    if kind in ('bounded', 'detection'):
        half = family['noise_half_width']
        blocks = mean*rng.uniform(1-half, 1+half, size=(replicates, n_blocks, len(widths)))
        bounds = config['known_bound_base_multiplier']*widths
        if kind == 'detection':
            inclusion = np.asarray(family['inclusion_probabilities'])
            blocks *= rng.random(blocks.shape) < inclusion
            if family['inverse_probability_correction']:
                blocks /= inclusion; bounds = bounds/inclusion
    elif kind == 'compound_pareto':
        shape = family['pareto_shape']; cost_mean = shape/(shape-1)
        rate = family['expected_resource_scale']*mean/cost_mean
        counts = rng.poisson(rate, size=(replicates, n_blocks, len(widths)))
        identifiers = np.repeat(np.arange(counts.size), counts.ravel())
        costs = 1+rng.pareto(shape, size=len(identifiers))
        blocks = np.bincount(identifiers, weights=costs, minlength=counts.size).reshape(counts.shape)
    elif kind == 'ar_lognormal':
        rho, sigma = family['ar_correlation'], family['log_sd']
        z = np.empty((replicates, n_blocks, len(widths)))
        z[:, 0] = rng.standard_normal((replicates, len(widths)))
        for index in range(1, n_blocks):
            z[:, index] = rho*z[:, index-1]+np.sqrt(1-rho*rho)*rng.standard_normal((replicates, len(widths)))
        blocks = mean*np.exp(sigma*z-sigma*sigma/2)
    else:
        raise ValueError('Unknown frozen observation family')
    return blocks, bounds


def case_list(config, populations):
    cases = []
    for ni, n in enumerate(config['block_counts']):
        for pi, population in enumerate(populations):
            for fi, family in enumerate(config['observation_families']):
                cases.append(dict(index=len(cases), n_index=ni, n_blocks=n, profile_index=pi,
                    profile=population['name'], family_index=fi, family=family['name'],
                    paired_seed_family_index=3 if family['kind'] == 'detection' else fi))
    return cases


def stage_audit(directory, stage, config_path):
    manifest = json.loads((directory/f'{stage}-manifest.json').read_text())
    if manifest['config_sha256'] != digest(config_path):
        raise ValueError('Recorded configuration changed; use a separate run directory')
    if manifest['source_sha256'] != source_bundle():
        if stage != 'development':
            raise ValueError('Recorded evaluation algorithms changed')
        # Development precedes the final source freeze. Its original source
        # snapshot remains authoritative when output-audit code is hardened.
        for name, sha in manifest['source_sha256'].items():
            snapshot = directory/'development-source-snapshot'/name
            if not snapshot.exists() or digest(snapshot) != sha:
                raise ValueError('Original development algorithm snapshot is unavailable or changed')
    for item in manifest['artifacts']:
        if digest(ROOT/item['path']) != item['sha256']:
            raise ValueError('Recorded simulation statistics failed integrity verification')
    return manifest


def collect(config, config_path, directory, stage):
    manifest_path = directory/f'{stage}-manifest.json'
    if manifest_path.exists():
        return stage_audit(directory, stage, config_path)
    stage_directory = directory/stage
    if stage_directory.exists() and any(stage_directory.iterdir()):
        raise ValueError('Retain interrupted collection and use a new run directory; partial files cannot be overwritten')
    stage_directory.mkdir(parents=True, exist_ok=True)
    populations = profiles(config); cases = case_list(config, populations)
    development = stage == 'development'
    stage_index = 0 if development else 1
    seed = config['development_seed'] if development else config['evaluation_seed']
    replicates = config['development_replicates'] if development else config['evaluation_replicates']
    started = utc(); sources = source_bundle(); artifacts = []
    for case in cases:
        ni, pi, fi = case['n_index'], case['profile_index'], case['family_index']
        seed_family = case['paired_seed_family_index']
        data_seed = [seed, ni, pi, seed_family]
        bootstrap_seed = [config['bootstrap_seed'], stage_index, ni, pi, seed_family]
        family = config['observation_families'][fi]
        blocks, bounds = generate_blocks(config, populations[pi], family, case['n_blocks'], replicates,
                                         np.random.default_rng(np.random.SeedSequence(data_seed)))
        statistics = batch_profile_decisions(blocks, config['log_widths'], factor=config['factor'],
            alpha=config['alpha'], bootstrap_replicates=config['bootstrap_replicates'],
            chunk=config['bootstrap_chunk'], resource_upper_bounds=bounds,
            rng=np.random.default_rng(np.random.SeedSequence(bootstrap_seed)))
        method_lower = np.full((len(METHODS), replicates), np.nan)
        method_upper = np.full_like(method_lower, np.nan)
        method_log_lower = np.full((len(METHODS), replicates, blocks.shape[-1]), np.nan)
        method_log_upper = np.full_like(method_log_lower, np.nan)
        decisions = np.full((len(METHODS), replicates), -1, dtype=np.int8)
        available = np.zeros(len(METHODS), dtype=bool)
        for mi, name in enumerate(METHODS):
            if name not in statistics['methods']:
                continue
            result = statistics['methods'][name]; available[mi] = True
            method_lower[mi], method_upper[mi] = result['departure_lower'], result['departure_upper']
            decisions[mi] = np.array([DECISIONS.index(value) for value in result['decision']], dtype=np.int8)
            if 'log_lower' in result:
                method_log_lower[mi], method_log_upper[mi] = result['log_lower'], result['log_upper']
        path = stage_directory/f"scenario-{case['index']:03d}.npz"
        with path.open('xb') as stream:
            np.savez_compressed(stream, resource_means=blocks.mean(axis=1), point_log=statistics['point_log'],
                point_delta=statistics['point_delta'], radius=statistics['radius'],
                zero_total=statistics['zero_total'], zero_bootstrap_profiles=statistics['zero_bootstrap_profiles'],
                method_lower=method_lower, method_upper=method_upper,
                method_log_lower=method_log_lower, method_log_upper=method_log_upper,
                decisions=decisions, method_available=available,
                historical_percentile_equivalent=statistics['historical_percentile_equivalent'],
                example_resource_blocks=blocks[:config['raw_input_examples_per_scenario']],
                known_resource_upper_bounds=bounds if bounds is not None else np.array([]))
        artifacts.append(dict(path=str(path.relative_to(ROOT)), sha256=digest(path), **case,
                              data_seed=data_seed, bootstrap_seed=bootstrap_seed))
        if (case['index']+1) % len(config['observation_families']) == 0:
            print(f"{stage}: n={case['n_blocks']} {case['profile']} complete ({case['index']+1}/{len(cases)} scenarios)", flush=True)
    if sources != source_bundle():
        raise ValueError('Algorithms changed during collection')
    manifest = dict(stage=stage, completed=True, started_utc=started, completed_utc=utc(),
        run_id=config['run_id'], replicates=replicates, config_sha256=digest(config_path),
        source_sha256=sources, artifacts=artifacts, methods=METHODS, decision_codes=DECISIONS,
        retention='All outer means, profile bounds, decisions, bootstrap radii and zero flags; first eight full block-vector inputs per scenario. Remaining generated inputs reconstruct exactly from frozen source, NumPy version and recorded SeedSequence recipes. Inner bootstrap indices are regenerated, not retained.')
    write_json_new(manifest_path, manifest)
    return manifest


def freeze(config, config_path, directory):
    development = stage_audit(directory, 'development', config_path)
    path = directory/'frozen-plan.json'
    if path.exists():
        plan = json.loads(path.read_text())
        if plan['source_sha256'] != source_bundle() or plan['config_reference']['sha256'] != digest(config_path):
            raise ValueError('Frozen configuration or algorithms changed')
        if plan['environment']['numpy'] != np.__version__:
            raise ValueError('The recorded NumPy sampling implementation must be retained')
        return plan
    if (directory/'evaluation-manifest.json').exists():
        raise ValueError('Final evaluation cannot precede its prediction/method freeze')
    plan = dict(run_id=config['run_id'], frozen_utc=utc(), config=config,
        config_reference=dict(path=str(config_path.relative_to(ROOT)), sha256=digest(config_path)),
        sources=[dict(path=name, sha256=sha) for name, sha in source_bundle().items()],
        source_sha256=source_bundle(), environment=dict(python=platform.python_version(), numpy=np.__version__,
            scipy=scipy.__version__, matplotlib=matplotlib.__version__, architecture=platform.machine(),
            system=platform.system(), system_release=platform.release(), logical_cpus=os.cpu_count(),
            input_dtype='float64', random_bit_generator='PCG64'),
        seeds=dict(development=config['development_seed'], evaluation=config['evaluation_seed'],
            bootstrap=config['bootstrap_seed'], recipe=config['stream_recipe']),
        development_manifest_sha256=digest(directory/'development-manifest.json'),
        development_source_sha256=development['source_sha256'],
        development_source_note='Exact original development source snapshots retained; final runner adds completion/output-integrity guards before evaluation. Generation, bootstrap methods, observations, scenarios, margins and decision criteria unchanged.',
        development_role='Separate implementation/development sample, retained before final evaluation. No interval multiplier, scenario, margin, eligibility criterion or tuning parameter selected from evaluation.',
        populations=profiles(config), scenarios=case_list(config, profiles(config)),
        methods=METHODS, complete_profile_target='phi_j = (sum widths)*E[R_j]/(width_j*sum E[R]); Delta=max abs log phi. Structural zero target has infinite Delta.')
    write_json_new(path, plan)
    return plan


def rate(values, level):
    values = np.asarray(values, dtype=bool); count = int(values.sum()); total = len(values)
    return dict(rate=float(count/total), successes=count, trials=total,
                monte_carlo_interval=list(wilson_interval(count, total, level)))


def summaries(config, populations, manifest):
    rows = []; historical = []; level = config['monte_carlo_interval_level']
    for artifact in manifest['artifacts']:
        values = np.load(ROOT/artifact['path']); population = populations[artifact['profile_index']]
        target_log = np.array([-np.inf if value is None else value for value in population['log_phi']])
        delta = np.inf if population['departure_infinite'] else population['max_abs_log_departure']
        relation = population['truth_relation']
        historical.append(dict(family=artifact['family'], n_blocks=artifact['n_blocks'], profile=artifact['profile'],
            equivalent=rate(values['historical_percentile_equivalent'], level),
            false_equivalence=rate(values['historical_percentile_equivalent'] & (relation != 'inside'), level),
            upper_departure_coverage=rate(delta <= values['method_upper'][1], level)))
        for mi, name in enumerate(METHODS):
            if not values['method_available'][mi]:
                continue
            decision = values['decisions'][mi]
            lower, upper = values['method_lower'][mi], values['method_upper'][mi]
            delta_coverage = (lower <= delta) & (delta <= upper)
            if name == 'percentile_delta_extension':
                coverage = delta_coverage; coverage_target = 'Delta interval, not a simultaneous complete-vector band'
            else:
                coverage = np.all((values['method_log_lower'][mi] <= target_log) &
                                  (target_log <= values['method_log_upper'][mi]), axis=-1)
                coverage_target = 'simultaneous complete normalized log-resource vector'
            rows.append(dict(family=artifact['family'], n_blocks=artifact['n_blocks'], profile=artifact['profile'],
                truth_relation=relation, method=name, coverage_target=coverage_target,
                coverage=rate(coverage, level), departure_interval_coverage=rate(delta_coverage, level),
                false_equivalence=rate((decision == 0) & (relation != 'inside'), level),
                false_departure=rate((decision == 1) & (relation != 'outside'), level),
                decisions={label: rate(decision == index, level) for index, label in enumerate(DECISIONS)},
                unbounded_upper_fraction=float(np.mean(~np.isfinite(upper))),
                mean_zero_observed_bins=float(np.mean(np.sum(~np.isfinite(values['point_log']), axis=-1))),
                mean_zero_bootstrap_profiles=float(values['zero_bootstrap_profiles'].mean())))
    return rows, historical


def eligibility(config, rows):
    gates = []
    for family in config['observation_families']:
        for n in config['block_counts']:
            for method in METHODS:
                subset = [row for row in rows if row['family'] == family['name'] and row['n_blocks'] == n and row['method'] == method]
                failures = [row['profile'] for row in subset
                    if row['coverage']['monte_carlo_interval'][0] < config['eligibility']['minimum_coverage_mc_lower']
                    or row['false_equivalence']['monte_carlo_interval'][1] > config['eligibility']['maximum_false_decision_mc_upper']
                    or row['false_departure']['monte_carlo_interval'][1] > config['eligibility']['maximum_false_decision_mc_upper']]
                assumptions = bool(family['independent_blocks'] and family['correct_observation'])
                gates.append(dict(family=family['name'], n_blocks=n, method=method,
                    available=bool(subset), passes=bool(subset and not failures and assumptions),
                    operating_characteristics_pass=bool(subset and not failures), failed_profile_shapes=failures,
                    coverage_target=subset[0]['coverage_target'] if subset else None,
                    assumptions_satisfied_in_simulation=assumptions,
                    interpretation='Conditional on this exact simulated observation family; no automatic eligibility for twelve real seasonal months.'))
    return gates


def output_audit(output):
    manifest = json.loads((output/'output-manifest.json').read_text())
    for item in manifest['artifacts']:
        if digest(ROOT/item['path']) != item['sha256']:
            raise ValueError('Completed output artifact failed integrity verification')
    return manifest


def analyse(config, config_path, plan, directory, output):
    development = stage_audit(directory, 'development', config_path)
    evaluation = stage_audit(directory, 'evaluation', config_path)
    hashes = {name: digest(directory/name) for name in ['frozen-plan.json', 'development-manifest.json', 'evaluation-manifest.json']}
    result_path = output/'study.json'
    if (output/'output-manifest.json').exists():
        output_audit(output)
        previous = json.loads(result_path.read_text())
        if previous['data_sha256'] != hashes:
            raise ValueError('Existing results cannot be overwritten after changed inputs')
        return previous
    if output.exists() and any(output.iterdir()):
        raise ValueError('Retain interrupted output artifacts and use a new output directory; completion manifest missing')
    rows, historical = summaries(config, plan['populations'], evaluation)
    dev_rows, _ = summaries(config, plan['populations'], development)
    result = dict(status='complete', run_id=config['run_id'], config=config, data_sha256=hashes,
        frozen_plan_sha256=hashes['frozen-plan.json'], source_sha256=plan['source_sha256'], environment=plan['environment'],
        populations=plan['populations'], scenarios=rows, historical_percentile_max=historical,
        development_scenarios=dev_rows, eligibility=eligibility(config, rows),
        evaluation_outer_datasets=len(evaluation['artifacts'])*config['evaluation_replicates'],
        development_outer_datasets=len(development['artifacts'])*config['development_replicates'],
        monte_carlo_intervals='Wilson binomial intervals over independent outer datasets within each scenario; bootstrap draws are internal, not independent validation trials. Detection-corrected/misspecified scenarios share paired latent inputs.',
        retention=evaluation['retention'], inference='Simultaneous centered-vector bootstrap is approximate. Known-bound ratio reference is distribution-free only under true independent bounded blocks and correct observation weights. Percentile Delta lower extension is not the historical method.',
        solar_preread_gate='Independent exchangeable calendar months, adequate tail regularity and physical block-fluence bounds are not established. Solar robust primary verdict remains unresolved; approximate bootstrap classification is conditional exploratory.',
        interpretation=config['interpretation'])
    output.mkdir(parents=True, exist_ok=True)
    figures(config, result, output)
    # The completed report and manifest are published only after figures
    # succeed. Interrupted files are retained and never treated as complete.
    write_json_new(result_path, result)
    write_json_new(output/'output-manifest.json', dict(status='complete', run_id=config['run_id'],
        completed_utc=utc(), artifacts=[dict(path=str(path.relative_to(ROOT)), sha256=digest(path))
            for path in [result_path, output/'calibration.png', output/'calibration.svg']]))
    return result


def figures(config, result, output):
    rows = result['scenarios']; counts = config['block_counts']
    colors = ['#28669b', '#ba5c22', '#6a4c93', '#238b68', '#ad3e50']
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'svg.fonttype': 'none'})
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), layout='constrained')
    names = ['Centered log-vector', 'Percentile Delta extension', 'Known-bound reference']
    for method, label, color in zip(METHODS, names, colors):
        subset = [row for row in rows if row['family'] == 'iid_bounded_dense' and row['profile'] == 'flat' and row['method'] == method]
        axes[0, 0].plot([row['n_blocks'] for row in subset], [row['coverage']['rate'] for row in subset], 'o-', label=label, color=color)
    axes[0, 0].set(xlabel='Independent blocks', ylabel='Coverage', ylim=(-.02, 1.02), title='Flat bounded population: direct Delta bootstrap is biased')
    for family, color in zip(config['observation_families'], colors):
        values = [min(row['coverage']['rate'] for row in rows if row['family'] == family['name'] and row['n_blocks'] == n and row['method'] == 'centered_bootstrap') for n in counts]
        axes[0, 1].plot(counts, values, 'o-', color=color, label=family['name'].replace('_', ' '))
    axes[0, 1].set(xlabel='Sampling blocks', ylabel='Minimum full-vector coverage over shapes', ylim=(-.02, 1.02), title='Centered bands: observation process governs validity')
    for ax in axes[0]:
        ax.axhline(config['eligibility']['minimum_coverage_mc_lower'], color='gray', ls=':', lw=1)
    labels = [family['name'].replace('iid_', '').replace('_', '\n') for family in config['observation_families']]
    x = np.arange(len(labels)); width = .35
    for key, offset, color, label in [('false_equivalence', -width/2, '#28669b', 'False equivalence'), ('false_departure', width/2, '#ba5c22', 'False departure')]:
        values = [max(row[key]['rate'] for row in rows if row['family'] == family['name'] and row['n_blocks'] == 12 and row['method'] == 'centered_bootstrap') for family in config['observation_families']]
        axes[1, 0].bar(x+offset, values, width, color=color, label=label)
    axes[1, 0].axhline(config['eligibility']['maximum_false_decision_mc_upper'], color='gray', ls=':', lw=1)
    axes[1, 0].set(xticks=x, xticklabels=labels, ylabel='Maximum wrong-decision rate over shapes', title='Twelve blocks: wrong decisions can be systematic')
    bottom = np.zeros(len(labels))
    for decision, color in zip(DECISIONS, ['#28669b', '#ba5c22', '#9ca5ae']):
        values = np.array([next(row['decisions'][decision]['rate'] for row in rows if row['family'] == family['name'] and row['n_blocks'] == 12 and row['method'] == 'centered_bootstrap' and row['profile'] == 'flat') for family in config['observation_families']])
        axes[1, 1].bar(x, values, bottom=bottom, color=color, label=decision); bottom += values
    axes[1, 1].set(xticks=x, xticklabels=labels, ylabel='Decision fraction under a flat true resource target', ylim=(0, 1.02), title='Retaining an unresolved outcome is useful')
    for ax in axes.flat:
        ax.legend(fontsize=7, frameon=False); ax.grid(axis='y', alpha=.2); ax.spines[['top', 'right']].set_visible(False)
    fig.suptitle('Complete-profile decisions need a validated observation model\n2,000 outer datasets per condition; 499 bootstrap draws are internal', fontsize=11)
    for suffix in ('png', 'svg'):
        save_figure(fig, output/f'calibration.{suffix}', dpi=180)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=['development', 'freeze', 'evaluate', 'analyse', 'all'], default='all')
    parser.add_argument('--config', type=Path, default=ROOT/'configs/profile_calibration_2026-10-02.json')
    parser.add_argument('--directory', type=Path, default=ROOT/'data/profile-calibration/2026-10-02')
    parser.add_argument('--output', type=Path, default=ROOT/'results/profile-calibration')
    args = parser.parse_args(); config_path = args.config.resolve(); config = json.loads(config_path.read_text())
    args.directory.mkdir(parents=True, exist_ok=True); started = time.perf_counter()
    if args.stage in ('development', 'all'):
        collect(config, config_path, args.directory, 'development')
    if args.stage != 'development':
        plan = freeze(config, config_path, args.directory)
        if args.stage in ('evaluate', 'all'):
            collect(config, config_path, args.directory, 'evaluation')
        if args.stage in ('analyse', 'all'):
            result = analyse(config, config_path, plan, args.directory, args.output)
            for gate in result['eligibility']:
                if gate['available']:
                    print(f"{gate['family']} n={gate['n_blocks']} {gate['method']}: {'passes' if gate['passes'] else 'fails'}", flush=True)
    print(f'Completed {args.stage} in {time.perf_counter()-started:.2f} s', flush=True)


if __name__ == '__main__':
    main()
