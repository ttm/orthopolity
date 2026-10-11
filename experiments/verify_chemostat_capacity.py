"""Independent finite-geometry audit; does not import the analysis or an LP solver."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import subprocess

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(path.read_text())


def check(condition, message):
    if not condition:
        raise ValueError(message)


def close(first, second, message):
    check(np.allclose(first, second, atol=2e-10, rtol=1e-10), message)


def geometric_minimum(first, second):
    """TV is affine in each cell of the zero-residual line arrangement.

    Its minimum on the unit square occurs at a vertex of that arrangement.
    Include all four corners even when residual lines are constant or parallel.
    """
    first, second = np.asarray(first), np.asarray(second)
    delta = first[0]-second[0]
    direction = np.column_stack((first[1]-first[0], second[0]-second[1]))
    lines = [(np.array([1., 0.]), 0.), (np.array([1., 0.]), 1.),
             (np.array([0., 1.]), 0.), (np.array([0., 1.]), 1.)]
    lines += [(row, -value) for row, value in zip(direction, delta)]
    candidates = [np.array(p) for p in itertools.product((0., 1.), repeat=2)]
    for (a, b), (c, d) in itertools.combinations(lines, 2):
        matrix = np.array([a, c])
        # Exactly parallel/zero lines need no additional vertices.
        if np.linalg.det(matrix) == 0:
            continue
        point = np.linalg.solve(matrix, [b, d])
        if np.all(point >= -1e-12) and np.all(point <= 1+1e-12):
            candidates.append(np.clip(point, 0., 1.))
    return min(float(np.abs(delta+direction@p).sum()/2) for p in candidates)


def corner_price_bound(initial, final):
    """Enumerate ratio endpoints and pure C / pure N prices at both times.

    Each pairwise multiplier ratio is monotone in each independent price ratio
    and constituent ratio, so its extrema occur at these corners.
    """
    span = 1.
    for r0 in itertools.product(*initial):
        for rt in itertools.product(*final):
            for numerator in (np.ones(len(r0)), np.array(r0)):
                for denominator in (np.ones(len(rt)), np.array(rt)):
                    factor = numerator/denominator
                    span = max(span, float(max(factor)/min(factor)))
    return span, (np.sqrt(span)-1)/(np.sqrt(span)+1)


def shares(volumes, density):
    result = []
    for pool in density[2:]:
        amounts = np.asarray(volumes)*[density[0], density[1], pool]
        result.append(amounts/amounts.sum())
    return np.array(result)


def verify(directory):
    execution = read(directory/'execution.json')
    for source in execution['sources']:
        actual = (ROOT/source['path']).read_bytes()
        frozen = subprocess.check_output(['git', 'show', execution['freeze_commit']+':'+source['path']], cwd=ROOT)
        check(actual == frozen, 'Source differs from freeze: '+source['path'])
        check(hashlib.sha256(actual).hexdigest() == source['sha256'], 'Source hash changed')
    inputs = []
    for source in execution['inputs']:
        raw = (ROOT/source['path']).read_bytes()
        check(len(raw) == source['size_bytes'] and hashlib.sha256(raw).hexdigest() == source['sha256'], 'Input changed')
        inputs.append(json.loads(raw))
    config = read(ROOT/'configs/chemostat_capacity_followup_2026-10-10.json')
    check(config['inputs'] == execution['inputs'], 'Input configuration mismatch')
    species = ['Cr', 'Ca', 'Mo', 'Co']
    quotas = {(r['Algae'], r['Time standardised to pulse [days]']):
              np.array([r['N [pmol/cell]'], r['C [pmol/cell]']])/r['Cell volume [µm³]']
              for r in inputs[0]['rows']}
    check(len(quotas) == len(inputs[0]['rows']) == 20, 'Preliminary row count')
    baseline = np.array([(quotas[s, -4]+quotas[s, 0])/2 for s in species])
    density = {day: np.array([quotas[s, day] for s in species]) for day in (1, 2, 3)}
    calibration = read(directory/'quota-calibration.json')
    close(calibration['initial']['nitrogen'], baseline[:, 0], 'N calibration')
    close(calibration['initial']['carbon'], baseline[:, 1], 'C calibration')
    for day in (1, 2, 3):
        close(calibration['final'][str(day)]['nitrogen'], density[day][:, 0], 'Target N')
        close(calibration['final'][str(day)]['carbon'], density[day][:, 1], 'Target C')
    records = inputs[1]['main']+inputs[2]
    by_row = {r['source_row']: r for r in records}
    check(len(by_row) == len(records) == 456, 'Main source row count')
    bounds = {(r['mode'], r['day']): r for r in read(directory/'bounds.json')}
    for (mode, day), bound in bounds.items():
        final = baseline if mode == 'fixed_prepulse_densities' else density[day]
        intervals = []
        for costs in (baseline, final):
            ratios = costs[:, 1]/costs[:, 0]
            intervals.append([[ratios[0]]*2, [ratios[1]]*2, [min(ratios[2:]), max(ratios[2:])]])
        close(bound['initial_ratio_intervals'], intervals[0], 'Initial ratios')
        close(bound['final_ratio_intervals'], intervals[1], 'Final ratios')
        span, upper = corner_price_bound(*intervals)
        close(bound['multiplier_span_upper'], span, 'Price-corner span')
        close(bound['tv_upper'], upper, 'Price-corner TV')
    ledger = read(directory/'ledger.json')
    summary = read(directory/'summary.json')
    expected = {(mode, day, str(r['chemostat'])) for mode in config['modes']
                for day in (1, 2, 3) for r in records}
    check(len(ledger) == 144 and len(bounds) == 6, 'Output sizes')
    check({(r['mode'], r['day'], r['vessel']) for r in ledger} == expected, 'Ledger coverage')
    max_difference = 0.
    for row in ledger:
        # Every retained row in this completed run is usable; assert rather than skip.
        check(row['status'] == 'scored', 'Unexpected unscored row in complete retained run')
        initial = by_row[row['baseline_source_row']]
        final = by_row[row['target_source_row']]
        for source, day in ((initial, 0), (final, row['day'])):
            check(str(source['chemostat']) == row['vessel'] and source['time'] == day
                  and source['category'] == row['category'] and source['treatment'] == row['treatment'], 'Row identity')
        costs = baseline if row['mode'] == 'fixed_prepulse_densities' else density[row['day']]
        first = shares(initial['biovolumes'], baseline[:, 0])
        second = shares(final['biovolumes'], costs[:, 0])
        close(row['initial_share_segment'], first, 'Initial shares')
        close(row['final_share_segment'], second, 'Target shares')
        minimum = geometric_minimum(first, second)
        observation = row['observed_tv']
        close(observation['minimum'], minimum, 'Independent minimum')
        max_difference = max(max_difference, abs(minimum-observation['minimum']))
        maximum = max(float(np.abs(a-b).sum()/2) for a in first for b in second)
        close(observation['maximum'], maximum, 'Maximum TV')
        dual = np.array(observation['minimum_dual_vector'])
        check(np.all(abs(dual) <= .5), 'Dual infeasible')
        lower = max(0., float(dual@(first[0]-second[0])
                    +min(0., dual@(first[1]-first[0]))+min(0., dual@(second[0]-second[1])))-1e-12)
        close(observation['minimum_lower_bound'], lower, 'Dual lower bound')
        check(lower <= minimum+1e-10 and minimum-lower < 1e-8, 'Dual gap')
        bound = bounds[row['mode'], row['day']]['tv_upper']
        close(row['tv_upper'], bound, 'Row upper bound')
        close(row['minimum_excess_over_bound'], lower-bound, 'Excess')
        check(row['conditional_bound_exceeded'] == (lower-bound > config['numerical_tolerance']), 'Verdict')
    for comparison in summary['comparisons']:
        chosen = [r for r in ledger if r['mode'] == comparison['mode'] and r['category'] == comparison['category']]
        exceeding = [r for r in chosen if r['conditional_bound_exceeded']]
        check(comparison['n_rows'] == comparison['n_scored'] == len(chosen) == 36
              and comparison['n_unscored'] == 0, 'Summary row counts')
        check(comparison['n_rows_exceeding'] == len(exceeding), 'Summary exceedance count')
        vessels = sorted({r['vessel'] for r in exceeding})
        check(comparison['vessels_exceeding'] == vessels and comparison['n_vessels_exceeding'] == len(vessels), 'Summary vessels')
    primary = next(s for s in summary['comparisons'] if s['mode'] == config['primary_mode'] and s['category'] == config['primary_category'])
    check(summary['primary'] == primary and summary['n_main_records'] == 456, 'Primary summary')
    check(summary['verdict'] == 'conditional bound exceeded in recorded primary observations'
          and primary['n_rows_exceeding'] > 0, 'Primary verdict')
    return dict(verified=True, ledger_rows=len(ledger), independent_minimum_max_error=max_difference,
                method='Zero-residual line-arrangement vertices and extreme-price enumeration; no LP solver',
                freeze_commit=execution['freeze_commit'], primary=primary,
                artifact_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in sorted(directory.glob('*.json')) if p.name != 'verification.json'})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, required=True)
    args = parser.parse_args()
    result = verify(args.directory)
    (args.directory/'verification.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result, indent=2))
