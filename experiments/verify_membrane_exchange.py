"""Independent qualification checks for the frozen membrane-exchange study.

This module imports neither the primary analysis nor its source reader. Its
reader can decode optical standards, calibration trajectories and target
baselines only; there is deliberately no option to decode later target values.
Real source access must wait for the committed protocol. Merely importing the
module reads no files. Pure calculation functions also accept synthetic inputs.
"""

import argparse
import csv
from decimal import Decimal, localcontext
import hashlib
import io
import json
import math
from pathlib import Path
from zipfile import ZipFile

import numpy as np
from scipy.integrate import solve_ivp
from scipy.stats import f as f_distribution
from scipy.stats import t as t_distribution


ROOT = Path(__file__).resolve().parents[1]
RUNS = ('20250505', '20250603')
TIMES = {
    RUNS[0]: tuple(range(0, 67, 6)),
    RUNS[1]: (0, 4, 21.3, 24, 27.5, 45.6, 48, 69.6),
}
SAMPLES = {
    RUNS[0]: 'Diffusion Testing/Sample Data/20250505_ot2_PES_PEG25_AO_metadata.csv',
    RUNS[1]: 'Diffusion Testing/Sample Data/20250603_manual_PES_PEG25_AO_metadata.csv',
}
STANDARDS = {
    RUNS[0]: 'Diffusion Testing/UV_Vis_Calibration_Curves/20250505_ot2_calibration_AO.csv',
    RUNS[1]: 'Diffusion Testing/UV_Vis_Calibration_Curves/20250603_manual_calibration_AO.csv',
}


def dec(value):
    result = Decimal(str(value))
    if not result.is_finite():
        raise ValueError('Nonfinite authorized source value')
    return result


def _csv_rows(archive, member, required):
    with archive.open(member) as binary:
        with io.TextIOWrapper(binary, encoding='utf-8-sig', newline='') as stream:
            reader = csv.DictReader(stream, strict=True)
            header = reader.fieldnames
            if (not header or len(header) != len(set(header))
                    or not set(required).issubset(header)):
                raise ValueError('Invalid source CSV schema')
            for row in reader:
                if None in row or any(v is None for v in row.values()):
                    raise ValueError('Malformed source CSV row')
                yield row


def read_qualification_source(path, expected_sha256):
    """Decode the authorized source partition, never later target responses."""
    if (not isinstance(expected_sha256, str) or len(expected_sha256) != 64
            or any(c not in '0123456789abcdef' for c in expected_sha256)):
        raise ValueError('A pinned lowercase SHA-256 is required')
    raw = Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected_sha256:
        raise ValueError('Source SHA-256 mismatch')
    result = {'archive_sha256': expected_sha256, 'runs': {}}
    with ZipFile(io.BytesIO(raw)) as archive:
        names = archive.namelist()
        for name in (*SAMPLES.values(), *STANDARDS.values()):
            if names.count(name) != 1:
                raise ValueError('Missing or duplicate required ZIP member')
        for run_index, run in enumerate(RUNS):
            standards = [
                (dec(row['C_uM']), dec(row['Abs_raw']))
                for row in _csv_rows(archive, STANDARDS[run], ('C_uM', 'Abs_raw'))
            ]
            concentrations = [row[0] for row in standards]
            if (len(standards) != 5 or len(set(concentrations)) != 5
                    or min(concentrations) < 0):
                raise ValueError('Invalid optical-standard identities')
            first_sample = 1 + 4 * run_index
            expected = {
                (f'PES_PEG25_AO_S{first_sample + pair - 1}',
                 f'H{pair}_C{chamber}', dec(time))
                for pair in range(1, 5) for chamber in (1, 2)
                for time in TIMES[run]
            }
            seen, observations = set(), {}
            for row in _csv_rows(archive, SAMPLES[run], ('Sample', 'Hcell', 'Time', 'Abs_raw')):
                key = (row['Sample'], row['Hcell'], dec(row['Time']))
                if key not in expected or key in seen:
                    raise ValueError('Unexpected or duplicate chamber/time identity')
                seen.add(key)
                # Do not access, parse, convert or return positive-time target Abs_raw.
                if run_index == 0 or key[2] == 0:
                    observations[key] = dec(row['Abs_raw'])
            if seen != expected:
                raise ValueError('Missing chamber/time identity')
            pairs = []
            for pair in range(1, 5):
                sample = f'PES_PEG25_AO_S{first_sample + pair - 1}'
                allowed_times = TIMES[run] if run_index == 0 else (0,)
                pairs.append({
                    'sample': sample,
                    'times_hours': tuple(dec(t) for t in allowed_times),
                    'donor': tuple(observations[(sample, f'H{pair}_C1', dec(t))]
                                   for t in allowed_times),
                    'acceptor': tuple(observations[(sample, f'H{pair}_C2', dec(t))]
                                      for t in allowed_times),
                })
            result['runs'][run] = {'standards': tuple(sorted(standards)), 'pairs': pairs}
    return result


def optical_fit(standards, alpha=0.01):
    """Affine optical OLS using centered Decimal sums, not a matrix solver."""
    with localcontext() as context:
        context.prec = 80
        x, y = zip(*[(dec(a), dec(b)) for a, b in standards])
        n = len(x)
        if n != 5 or len(set(x)) != n or min(x) < 0:
            raise ValueError('Expected five distinct nonnegative optical standards')
        mx, my = sum(x) / n, sum(y) / n
        xx = sum((v - mx) ** 2 for v in x)
        xy = sum((a - mx) * (b - my) for a, b in zip(x, y))
        slope = xy / xx
        intercept = my - slope * mx
        residuals = [b - slope * a - intercept for a, b in zip(x, y)]
        rss = sum(v * v for v in residuals)
        variance = rss / (n - 2)
        numerical_zero_limit = 100 * (Decimal(2) ** -52) ** 2 * max(Decimal(1), sum(v * v for v in y))
        h = ((1 / xx, -mx / xx), (-mx / xx, Decimal(1) / n + mx * mx / xx))
        # These weights separately express the fitted intercept in terms of
        # the five original optical observations. They drive the G covariance.
        intercept_weights = [Decimal(1) / n - mx * (a - mx) / xx for a in x]
        critical = dec(t_distribution.ppf(1 - alpha / 2, n - 2))
        margin = critical * (variance * h[0][0]).sqrt()
        yy = sum((v - my) ** 2 for v in y)
        return {
            'slope': float(slope), 'intercept': float(intercept),
            'variance': float(variance), 'df': n - 2, 'n': n,
            'rss': float(rss), 'H': [[float(v) for v in row] for row in h],
            'residuals': [float(v) for v in residuals],
            'coefficient_covariance': [[float(variance * v) for v in row] for row in h],
            'numerical_zero_limit': float(numerical_zero_limit),
            'intercept_weights': [float(v) for v in intercept_weights],
            'slope_interval': [float(slope - margin), float(slope + margin)],
            'r_squared': float(1 - rss / yy) if yy else None,
            'concentration_range_uM': [float(min(x)), float(max(x))],
            'passed': bool(rss > numerical_zero_limit and slope - margin > 0),
        }


def _trim(poly):
    result = list(poly)
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result


def _add(a, b, multiplier=Decimal(1)):
    result = [Decimal(0)] * max(len(a), len(b))
    for i, value in enumerate(a):
        result[i] += value
    for i, value in enumerate(b):
        result[i] += multiplier * value
    return _trim(result)


def _multiply(a, b):
    result = [Decimal(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            result[i + j] += x * y
    return _trim(result)


def _differentiate(a):
    return [i * v for i, v in enumerate(a)][1:] or [Decimal(0)]


def _evaluate(poly, point):
    value = Decimal(0)
    for coefficient in reversed(poly):
        value = value * point + coefficient
    return value


def _bernstein_split(coefficients):
    row = list(coefficients)
    left, right = [row[0]], [row[-1]]
    while len(row) > 1:
        row = [(a + b) / 2 for a, b in zip(row, row[1:])]
        left.append(row[0])
        right.append(row[-1])
    return left, list(reversed(right))


def _variations(coefficients):
    signs = [v > 0 for v in coefficients if v != 0]
    return sum(a != b for a, b in zip(signs, signs[1:]))


def polynomial_unit_roots(coefficients, width=Decimal('1e-18')):
    """Isolate all unit-interval real roots using Bernstein sign variation.

    Unlike a sampled objective grid, subdivision cannot skip a narrow sign
    change. Multiple roots closer than ``width`` are returned as one cluster.
    An identically zero polynomial is reported separately by its caller.
    """
    with localcontext() as context:
        context.prec = 80
        poly = _trim([dec(v) for v in coefficients])
        if len(poly) == 1:
            return []
        exact_endpoints = ([Decimal(0)] if poly[0] == 0 else [])
        if _evaluate(poly, Decimal(1)) == 0:
            exact_endpoints.append(Decimal(1))
        n = len(poly) - 1
        scale = max(abs(v) for v in poly)
        poly = [v / scale for v in poly]
        bernstein = [sum(poly[i] * Decimal(math.comb(k, i)) / math.comb(n, i)
                         for i in range(k + 1)) for k in range(n + 1)]
        stack = [(Decimal(0), Decimal(1), bernstein)]
        roots, nodes = exact_endpoints, 0
        while stack:
            lower, upper, coefficients = stack.pop()
            nodes += 1
            if nodes > 100000:
                raise ArithmeticError('Polynomial root isolation did not resolve')
            if coefficients[0] == 0:
                roots.append(lower)
            if coefficients[-1] == 0:
                roots.append(upper)
            if not _variations(coefficients):
                continue
            midpoint = (lower + upper) / 2
            if upper - lower <= width:
                roots.append(midpoint)
                continue
            left, right = _bernstein_split(coefficients)
            stack.extend(((lower, midpoint, left), (midpoint, upper, right)))
        distinct = []
        for root in sorted(roots):
            if not distinct or root - distinct[-1] > 4 * width:
                distinct.append(root)
        return distinct


def profile_fit(times_hours, differences, retention_fraction, variance,
                alpha=0.01, variance_df=3, volume_ml=11, reference_time_hours=6):
    """Independent global profile fit and absolute-RSS confidence set.

    For this frozen equal-spacing design, phi_j=(f*z)^j. Its profiled RSS
    is T-N(z)^2/D(z). Polynomial stationary points and confidence boundaries
    are isolated in high precision; the primary grid/refinement is not reused.
    """
    with localcontext() as context:
        context.prec = 80
        times = [dec(t) for t in times_hours]
        d = [dec(value) for value in differences]
        n = len(d)
        if n != 12 or times != [dec(reference_time_hours) * j for j in range(n)]:
            raise ValueError('Independent polynomial check requires the frozen 12-point grid')
        f = dec(retention_fraction)
        if not 0 < f <= 1 or variance < 0:
            raise ValueError('Invalid sampling retention or variance')
        numerator = [value * f ** j for j, value in enumerate(d)]
        denominator = [Decimal(0)] * (2 * n - 1)
        for j in range(n):
            denominator[2 * j] = f ** (2 * j)
        total = sum(value * value for value in d)

        def at(z):
            # Direct residual accumulation avoids subtracting two close sums.
            phi = [(f * z) ** j if j else Decimal(1) for j in range(n)]
            amplitude = sum(v * y for v, y in zip(phi, d)) / sum(v * v for v in phi)
            rss = sum((y - amplitude * v) ** 2 for y, v in zip(d, phi))
            return amplitude, rss, [amplitude * v for v in phi]

        stationary = _add(
            [2 * v for v in _multiply(_differentiate(numerator), denominator)],
            _multiply(numerator, _differentiate(denominator)), Decimal(-1))
        roots = polynomial_unit_roots(_multiply(numerator, stationary))
        candidates = sorted(set([Decimal(0), Decimal(1), *roots]))
        z = min(candidates, key=lambda candidate: (at(candidate)[1], candidate))
        amplitude, rss, curve = at(z)
        threshold = (2 * (n - 1) * dec(variance)
                     * dec(f_distribution.ppf(1 - alpha, n - 1, variance_df)))
        boundary_polynomial = _add(
            [(total - threshold) * v for v in denominator],
            _multiply(numerator, numerator), Decimal(-1))
        boundaries = polynomial_unit_roots(boundary_polynomial)
        cuts = sorted(set([Decimal(0), Decimal(1), *boundaries]))
        intervals = []
        for lower, upper in zip(cuts, cuts[1:]):
            if at((lower + upper) / 2)[1] <= threshold:
                intervals.append([float(lower), float(upper)])
        # Record isolated accepted points (e.g. exact zero-variance synthetic data).
        for point in cuts:
            if at(point)[1] <= threshold and not any(a <= float(point) <= b for a, b in intervals):
                intervals.append([float(point), float(point)])
        intervals.sort()
        merged = []
        for interval in intervals:
            if merged and abs(interval[0] - merged[-1][1]) <= 1e-15:
                merged[-1][1] = interval[1]
            else:
                merged.append(interval)
        accepted_zero = at(Decimal(0))[1] <= threshold
        accepted_one = at(Decimal(1))[1] <= threshold
        acceptable = rss <= threshold
        finite_interior_set = bool(merged) and not accepted_zero and not accepted_one
        rate = -float(z.ln()) / reference_time_hours if z > 0 else None
        return {
            'z': float(z), 'amplitude': float(amplitude), 'rss': float(rss),
            'threshold': float(threshold), 'fitted_curve': [float(v) for v in curve],
            'acceptance_intervals_z': merged,
            'accepts_z_zero': bool(accepted_zero), 'accepts_z_one': bool(accepted_one),
            'fit_accepted': bool(acceptable), 'amplitude_positive': bool(amplitude > 0),
            'finite_interior_set': bool(finite_interior_set),
            'lambda_per_hour': rate,
            'conductance_ml_per_hour': rate * volume_ml / 2 if rate is not None else None,
            'passed': bool(acceptable and amplitude > 0 and finite_interior_set),
            'stationary_candidates_checked': len(candidates),
            'endpoint_rss': [float(at(Decimal(0))[1]), float(at(Decimal(1))[1])],
        }


def integrated_pair(times_hours, initial, conductance, volume_ml=11,
                    withdrawal_ml=0.020):
    """Numerically integrate edge balances and PRE-sampling observations."""
    times = np.asarray(times_hours, dtype=float)
    if len(times) == 0 or times[0] != 0 or np.any(np.diff(times) <= 0):
        raise ValueError('Expected an increasing schedule starting at zero')
    if (not all(math.isfinite(float(v)) for v in (volume_ml, withdrawal_ml, conductance))
            or volume_ml <= 0 or not 0 <= withdrawal_ml < volume_ml or conductance < 0):
        raise ValueError('Invalid physical integration input')
    state = np.asarray(initial, dtype=float)
    if state.shape != (2,) or not np.all(np.isfinite(state)):
        raise ValueError('Invalid initial pair')
    predicted = [state.copy()]
    retained = 1 - withdrawal_ml / volume_ml

    def flux(_time, concentrations):
        exchange = conductance * (concentrations[0] - concentrations[1]) / volume_ml
        return [-exchange, exchange]

    for previous, current in zip(times, times[1:]):
        state = state * retained
        solved = solve_ivp(flux, (previous, current), state, method='DOP853',
                           rtol=2e-12, atol=2e-13)
        if not solved.success:
            raise ArithmeticError('Independent edge-balance integration failed')
        state = solved.y[:, -1]
        predicted.append(state.copy())
    return np.asarray(predicted)


def baseline_check(pairs, optics, alpha=0.01, family_size=16):
    limit = float(t_distribution.ppf(1 - alpha / family_size, optics['df'])
                  * math.sqrt(optics['variance'] * (1 + optics['H'][1][1])))
    details = []
    for pair in pairs:
        donor, acceptor = float(pair['donor'][0]), float(pair['acceptor'][0])
        b = optics['intercept']
        total, contrast = donor + acceptor - 2 * b, donor - acceptor
        corrected = [donor - b, acceptor - b]
        details.append({
            'sample': pair['sample'], 'sum_corrected_raw': total, 'difference_raw': contrast,
            'donor_raw': donor, 'recipient_raw': acceptor,
            'corrected_raw': corrected, 'sum_positive': total > 0,
            'difference_positive': contrast > 0,
            'nonnegative_within_limit': all(value >= -limit for value in corrected),
        })
    return {'negative_tolerance_raw': limit,
            't_critical': float(t_distribution.ppf(1 - alpha / family_size, optics['df'])),
            'pairs': details,
            'passed': all(p['sum_positive'] and p['difference_positive']
                          and p['nonnegative_within_limit'] for p in details)}


def total_stock_check(pairs, optics, retention_fraction, alpha=0.01):
    """Construct covariance via an observation-error map G, independently.

    Columns 0..95 correspond to original chamber absorbances; the last five
    are independent original standard absorbances. Therefore Q=G G' accounts
    for repeated baselines AND the common fitted intercept without reusing
    the primary compact covariance expression.
    """
    n = len(pairs[0]['donor'])
    if len(pairs) != 4 or n != 12 or any(len(p['donor']) != n or len(p['acceptor']) != n for p in pairs):
        raise ValueError('Expected four complete calibration pairs')
    m = len(pairs) * (n - 1)
    g = np.zeros((m, 2 * n * len(pairs) + 5))
    residuals = []
    row_index = 0
    for pair_index, pair in enumerate(pairs):
        first_total = float(pair['donor'][0] + pair['acceptor'][0])
        for j in range(1, n):
            retained = retention_fraction ** j
            residuals.append(float(pair['donor'][j] + pair['acceptor'][j])
                             - retained * first_total - 2 * (1 - retained) * optics['intercept'])
            base = 2 * n * pair_index
            g[row_index, base + 2 * j:base + 2 * j + 2] = 1
            g[row_index, base:base + 2] = -retained
            g[row_index, -5:] = -2 * (1 - retained) * np.asarray(optics['intercept_weights'])
            row_index += 1
    q = g @ g.T
    r = np.asarray(residuals)
    # Cholesky whitening, not the primary expression or inverse multiplication.
    whitened = np.linalg.solve(np.linalg.cholesky(q), r)
    quadratic = float(whitened @ whitened)
    statistic = quadratic / (m * optics['variance']) if optics['variance'] > 0 else None
    p_value = float(f_distribution.sf(statistic, m, optics['df'])) if statistic is not None else None
    return {'residuals': residuals, 'Q': q.tolist(), 'quadratic_form': quadratic,
            'statistic': statistic, 'numerator_df': m, 'denominator_df': optics['df'],
            'p_value': p_value, 'passed': p_value is not None and p_value >= alpha}


def independent_qualification(source, *, alpha=0.01, retention_fraction=549 / 550,
                              volume_ml=11, reference_time_hours=6, baseline_family_size=16):
    optics, baselines, rates = {}, {}, []
    for run in RUNS:
        data = source['runs'][run]
        optics[run] = optical_fit(data['standards'], alpha)
    if not all(v['passed'] for v in optics.values()):
        return {'passed': False, 'optics': optics, 'baselines': {}, 'rates': [],
                'total_stock': None, 'later_target_responses_decoded': False}
    for run in RUNS:
        data = source['runs'][run]
        baselines[run] = baseline_check(data['pairs'], optics[run], alpha, baseline_family_size)
    calibration = source['runs'][RUNS[0]]['pairs']
    for pair in calibration:
        fit = profile_fit(pair['times_hours'],
                          [a - b for a, b in zip(pair['donor'], pair['acceptor'])],
                          retention_fraction, optics[RUNS[0]]['variance'], alpha,
                          optics[RUNS[0]]['df'], volume_ml, reference_time_hours)
        fit['sample'] = pair['sample']
        if fit['conductance_ml_per_hour'] is not None:
            integrated = integrated_pair(pair['times_hours'], [fit['amplitude'], 0],
                                         fit['conductance_ml_per_hour'], volume_ml,
                                         volume_ml * (1 - retention_fraction))
            difference = integrated[:, 0] - integrated[:, 1]
            fit['integration_max_abs_difference'] = float(np.max(np.abs(
                difference - np.asarray(fit['fitted_curve']))))
            if not np.allclose(difference, fit['fitted_curve'], atol=2e-10, rtol=2e-10):
                raise ArithmeticError('Physical integration and polynomial fit disagree')
        rates.append(fit)
    total = total_stock_check(calibration, optics[RUNS[0]], retention_fraction, alpha)
    passed = (all(v['passed'] for v in optics.values())
              and all(v['passed'] for v in baselines.values())
              and all(v['passed'] for v in rates) and total['passed'])
    return {'passed': passed, 'optics': optics, 'baselines': baselines,
            'rates': rates, 'total_stock': total,
            'later_target_responses_decoded': False}


def source_payload(source):
    """Reconstruct the primary reader's public payload without importing it."""
    def standards(run):
        return [{'concentration_uM': float(x), 'absorbance': float(y)}
                for x, y in source['runs'][run]['standards']]

    def observations(run):
        result = []
        for k, pair in enumerate(source['runs'][run]['pairs'], 1):
            for chamber, field in ((1, 'donor'), (2, 'acceptor')):
                result.extend({'time_hours': float(time), 'sample': pair['sample'],
                               'chamber': f'H{k}_C{chamber}', 'absorbance': float(value)}
                              for time, value in zip(pair['times_hours'], pair[field]))
        return result

    design = [{'time_hours': float(time), 'sample': f'PES_PEG25_AO_S{k + 4}',
               'chamber': f'H{k}_C{chamber}'}
              for k in range(1, 5) for chamber in (1, 2) for time in TIMES[RUNS[1]]]
    return {'archive_sha256': source['archive_sha256'],
            'calibration_standards': standards(RUNS[0]),
            'target_standards': standards(RUNS[1]),
            'calibration_observations': observations(RUNS[0]),
            'target_baselines': observations(RUNS[1]),
            'target_design': design, 'target_observations': None}


def _optical_reasons(optics):
    reasons = []
    if optics['rss'] <= optics['numerical_zero_limit']:
        reasons.append('unresolved_optical_variance')
    if optics['slope_interval'][0] <= 0:
        reasons.append('optical_slope_not_identified_positive')
    return reasons


def _baseline_reasons(pair):
    reasons = []
    if not pair['sum_positive']:
        reasons.append('nonpositive_corrected_baseline_total')
    if not pair['difference_positive']:
        reasons.append('nonpositive_baseline_contrast')
    if not pair['nonnegative_within_limit']:
        reasons.append('baseline_below_observation_compatibility_bound')
    return reasons


def _rate_reasons(rate):
    reasons = []
    if not rate['acceptance_intervals_z']:
        reasons.append('empty_rate_confidence_set')
    if rate['accepts_z_zero']:
        reasons.append('instantaneous_exchange_not_excluded')
    if rate['accepts_z_one']:
        reasons.append('no_exchange_not_excluded')
    if not rate['amplitude_positive']:
        reasons.append('nonpositive_fitted_amplitude')
    return reasons


def verify(document, config=None, *, root=ROOT):
    """Verify a qualification artifact; no later-target decoding is possible."""
    root = Path(root)
    if config is None:
        config = json.loads((root / 'configs/membrane_exchange_2026-10-20.json').read_text())
    count, max_difference = 0, 0.0

    def check(actual, expected, path, *, atol=3e-12, rtol=3e-9):
        nonlocal count, max_difference
        if isinstance(expected, dict):
            if not isinstance(actual, dict) or set(actual) != set(expected):
                raise ValueError('Field mismatch: ' + path)
            for key, value in expected.items():
                check(actual[key], value, path + '.' + key, atol=atol, rtol=rtol)
        elif isinstance(expected, (list, tuple)):
            if not isinstance(actual, (list, tuple)) or len(actual) != len(expected):
                raise ValueError('Sequence mismatch: ' + path)
            for i, (value, expected_value) in enumerate(zip(actual, expected)):
                check(value, expected_value, path + f'[{i}]', atol=atol, rtol=rtol)
        elif isinstance(expected, (int, float, Decimal)) and not isinstance(expected, bool):
            if isinstance(actual, bool) or not isinstance(actual, (int, float, Decimal)):
                raise ValueError('Numeric type mismatch: ' + path)
            a, e = float(actual), float(expected)
            if not math.isfinite(a) or not math.isfinite(e):
                raise ValueError('Nonfinite comparison: ' + path)
            difference = abs(a - e)
            count += 1
            max_difference = max(max_difference, difference)
            if difference > atol + rtol * abs(e):
                raise ValueError('Numeric mismatch: ' + path)
        elif actual != expected or type(actual) is not type(expected):
            raise ValueError('Value mismatch: ' + path)

    check(document['config'], config, 'config', atol=0, rtol=0)
    check(document['study'], config['study'], 'study')
    check(document['source_sha256'], config['source_sha256'], 'source_sha256')
    check(document['withheld_target_response_count'], 56, 'withheld_count', atol=0, rtol=0)
    check(document['target_later_responses_decoded'], False, 'target_decoding')
    commit = document['design_commit']
    if not isinstance(commit, str) or len(commit) != 40 or any(c not in '0123456789abcdef' for c in commit):
        raise ValueError('Invalid design commit identifier')
    if config['calibration_run'] != RUNS[0] or config['target_run'] != RUNS[1]:
        raise ValueError('Unexpected source cohort split')
    path = (root / config['source']).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('Source path must remain under the project root')
    source = read_qualification_source(path, config['source_sha256'])
    check(document['inputs'], source_payload(source), 'inputs', atol=2e-15, rtol=2e-15)
    retained = 1 - config['withdrawal_mL'] / config['volume_mL']
    independent = independent_qualification(
        source, alpha=config['alpha'], retention_fraction=retained,
        volume_ml=config['volume_mL'], reference_time_hours=config['reference_time_hours'],
        baseline_family_size=config['baseline_family_size'])
    reported = document['qualification']
    check(reported['retention_fraction'], retained, 'retention_fraction')
    check(reported['passed'], independent['passed'], 'passed')
    check(reported['assumptions'], [
        'Nominal optical-standard concentrations are known without error.',
        'Raw absorbance errors are independent Gaussian with a common variance '
        'for standards and chamber samples within each run.',
        'Five standards do not establish linearity, temporal stability, matrix '
        'equivalence, Gaussian errors, or equal variances.',
        'Sampling removes and replaces 0.02 mL simultaneously in both 11 mL chambers; '
        'observations precede collection.',
        'The reference measure is compartment volume, neither log-orthopolic nor '
        'linear-orthopolic size allocation.',
    ], 'assumptions')
    if set(reported['optics']) != set(RUNS):
        raise ValueError('Unexpected optical calibration run identities')
    stop_reasons = []
    for run in RUNS:
        actual, expected = reported['optics'][run], independent['optics'][run]
        fields = {'n': expected['n'], 'df': expected['df'], 'slope': expected['slope'],
                  'intercept': expected['intercept'], 'sse': expected['rss'],
                  'variance': expected['variance'], 'inverse_xtx': expected['H'],
                  'coefficient_covariance': expected['coefficient_covariance'],
                  'slope_ci': expected['slope_interval'], 'residuals': expected['residuals'],
                  'concentration_support': expected['concentration_range_uM'],
                  'numerical_zero_sse_threshold': expected['numerical_zero_limit'],
                  'concentrations_uM': [float(x) for x, _ in source['runs'][run]['standards']],
                  'absorbances': [float(y) for _, y in source['runs'][run]['standards']],
                  'passed': expected['passed'], 'stop_reasons': _optical_reasons(expected)}
        for key, value in fields.items():
            check(actual[key], value, f'optics.{run}.{key}', atol=3e-15, rtol=3e-9)
        stop_reasons.extend(f'{run}:{reason}' for reason in fields['stop_reasons'])
    if not independent['baselines']:
        check(reported['baselines'], {}, 'baselines')
        check(reported['rates'], [], 'rates')
        check(reported['total_stock'], None, 'total_stock')
        check(reported['stop_reasons'], stop_reasons, 'stop_reasons')
        return {'numeric_checks': count, 'max_abs_diff': max_difference,
                'source_sha256': config['source_sha256'],
                'target_later_responses_decoded': False, 'qualification_passed': False,
                'dependent_checks_skipped_for_optics': True}

    if set(reported['baselines']) != set(RUNS):
        raise ValueError('Unexpected baseline run identities')
    for run in RUNS:
        actual, expected = reported['baselines'][run], independent['baselines'][run]
        check(actual['negative_limit'], -expected['negative_tolerance_raw'], f'baselines.{run}.negative_limit')
        check(actual['t_critical'], expected['t_critical'], f'baselines.{run}.t_critical')
        check(actual['passed'], expected['passed'], f'baselines.{run}.passed')
        if len(actual['pairs']) != 4:
            raise ValueError('Wrong baseline pair count')
        run_reasons = []
        for i, (a, e) in enumerate(zip(actual['pairs'], expected['pairs']), 1):
            reasons = _baseline_reasons(e)
            check(a, {'sample': e['sample'], 'donor_chamber': f'H{i}_C1',
                      'recipient_chamber': f'H{i}_C2', 'donor_raw': e['donor_raw'],
                      'recipient_raw': e['recipient_raw'],
                      'donor_minus_intercept': e['corrected_raw'][0],
                      'recipient_minus_intercept': e['corrected_raw'][1],
                      'sum_minus_2_intercept': e['sum_corrected_raw'],
                      'difference': e['difference_raw'], 'passed': not reasons,
                      'stop_reasons': reasons}, f'baselines.{run}.pairs[{i - 1}]')
            run_reasons.extend(f"{e['sample']}:{reason}" for reason in reasons)
        check(actual['stop_reasons'], run_reasons, f'baselines.{run}.stop_reasons')
        stop_reasons.extend(f'{run}:{reason}' for reason in run_reasons)

    if len(reported['rates']) != 4:
        raise ValueError('Wrong calibration rate count')
    max_integration_difference = 0.0
    for i, (actual, expected, pair) in enumerate(zip(
            reported['rates'], independent['rates'], source['runs'][RUNS[0]]['pairs']), 1):
        label = f'rates[{i - 1}]'
        reasons = _rate_reasons(expected)
        for key, value in {'sample': pair['sample'], 'donor_chamber': f'H{i}_C1',
                           'recipient_chamber': f'H{i}_C2', 'n': 12, 'df': 11,
                           'times_hours': [float(t) for t in pair['times_hours']],
                           'differences': [float(a - b) for a, b in zip(pair['donor'], pair['acceptor'])],
                           'threshold': expected['threshold'], 'passed': expected['passed'],
                           'stop_reasons': reasons}.items():
            check(actual[key], value, label + '.' + key)
        check(actual['rss'], expected['rss'], label + '.rss', atol=3e-13, rtol=3e-8)
        check(actual['fitted_differences'], expected['fitted_curve'], label + '.fitted_differences',
              atol=3e-8, rtol=3e-7)
        check(actual['amplitude'], expected['amplitude'], label + '.amplitude', atol=3e-8, rtol=3e-7)
        z = float(actual['z'])
        if not math.isfinite(z) or not 0 <= z <= 1:
            raise ValueError('Out-of-domain fitted rate parameter')
        rate = -math.log(z) / config['reference_time_hours'] if z > 0 else None
        check(actual['lambda_per_hour'], rate, label + '.lambda_per_hour')
        conductance = rate * config['volume_mL'] / 2 if rate is not None else None
        check(actual['g_ml_per_hour'], conductance, label + '.g_ml_per_hour')
        check(actual['boundary'], 'instantaneous' if z == 0 else 'no_exchange' if z == 1 else None,
              label + '.boundary')
        # Verify that the reported optimizer parameter really produces the
        # reported curve, separately from agreement on the best objective.
        if conductance is not None:
            integrated = integrated_pair(pair['times_hours'], [actual['amplitude'], 0],
                                         conductance, config['volume_mL'], config['withdrawal_mL'])
            curve = integrated[:, 0] - integrated[:, 1]
        else:
            curve = np.array([actual['amplitude']] + [0.0] * 11)
        check(actual['fitted_differences'], curve.tolist(), label + '.integrated_differences',
              atol=3e-10, rtol=3e-10)
        max_integration_difference = max(max_integration_difference,
            float(np.max(np.abs(curve - np.asarray(actual['fitted_differences'])))))
        intervals = expected['acceptance_intervals_z']
        check(actual['confidence_intervals_z'], intervals, label + '.confidence_intervals_z',
              atol=3e-10, rtol=3e-9)
        lambda_intervals = [[-math.log(hi) / config['reference_time_hours'],
                             -math.log(lo) / config['reference_time_hours'] if lo > 0 else None]
                            for lo, hi in intervals]
        g_intervals = [[v * config['volume_mL'] / 2 if v is not None else None for v in interval]
                       for interval in lambda_intervals]
        check(actual['confidence_intervals_lambda_per_hour'], lambda_intervals,
              label + '.confidence_intervals_lambda_per_hour', atol=3e-9, rtol=3e-8)
        check(actual['confidence_intervals_g_ml_per_hour'], g_intervals,
              label + '.confidence_intervals_g_ml_per_hour', atol=3e-9, rtol=3e-8)
        for endpoint, rss, accepted in zip(('z0', 'z1'), expected['endpoint_rss'],
                (expected['accepts_z_zero'], expected['accepts_z_one'])):
            statistic = rss / (22 * independent['optics'][RUNS[0]]['variance'])
            check(actual['endpoint_tests'][endpoint],
                  {'rss': rss, 'statistic': statistic,
                   'p_value': float(f_distribution.sf(statistic, 11, 3)), 'accepted': accepted},
                  label + '.endpoint_tests.' + endpoint)
        stop_reasons.extend(f"{pair['sample']}:{reason}" for reason in reasons)

    actual, expected = reported['total_stock'], independent['total_stock']
    identities, totals, expected_totals = [], [], []
    b = independent['optics'][RUNS[0]]['intercept']
    for i, pair in enumerate(source['runs'][RUNS[0]]['pairs'], 1):
        initial = float(pair['donor'][0] + pair['acceptor'][0])
        for j, time in enumerate(pair['times_hours'][1:], 1):
            identities.append({'sample': pair['sample'], 'donor_chamber': f'H{i}_C1',
                               'recipient_chamber': f'H{i}_C2', 'time_hours': float(time),
                               'sampling_index': j})
            totals.append(float(pair['donor'][j] + pair['acceptor'][j]))
            expected_totals.append(retained ** j * initial + 2 * (1 - retained ** j) * b)
    stock_reasons = [] if expected['passed'] else ['total_stock_model_incompatible']
    check(actual, {'n': 44, 'df_numerator': 44, 'df_denominator': 3,
                   'residuals': expected['residuals'], 'covariance_q': expected['Q'],
                   'identities': identities, 'raw_totals': totals,
                   'expected_raw_totals': expected_totals, 'statistic': expected['statistic'],
                   'threshold': float(f_distribution.ppf(1 - config['alpha'], 44, 3)),
                   'p_value': expected['p_value'], 'passed': expected['passed'],
                   'stop_reasons': stock_reasons}, 'total_stock')
    stop_reasons.extend(stock_reasons)
    check(reported['stop_reasons'], stop_reasons, 'stop_reasons')
    return {'numeric_checks': count, 'max_abs_diff': max_difference,
            'integration_max_abs_diff': max_integration_difference,
            'source_sha256': config['source_sha256'],
            'target_later_responses_decoded': False,
            'qualification_passed': independent['passed'],
            'dependent_checks_skipped_for_optics': False,
            'rate_confidence_method': '80-digit Bernstein polynomial root isolation',
            'total_covariance_method': 'Independent raw-observation error design G G-transpose'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qualification', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--config', type=Path, default=ROOT / 'configs/membrane_exchange_2026-10-20.json')
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    raw = args.qualification.read_bytes()
    config = json.loads(args.config.read_text())
    report = verify(json.loads(raw), config)
    report['qualification_sha256'] = hashlib.sha256(raw).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as stream:
        json.dump(report, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')
    print(json.dumps(report, sort_keys=True))


if __name__ == '__main__':
    main()
