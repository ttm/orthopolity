"""Frozen membrane-pair qualification, using raw affine optical measurements.

No files are read here. ``qualify`` consumes the gated reader's calibration
payload and never accesses later positive-time target observations. The finite
sample tests condition on nominal standard concentrations and independent,
homoscedastic Gaussian errors shared by standards and samples within each run.
Five standards do not establish these assumptions. The reference measure is
compartment volume, neither log-orthopolic nor linear-orthopolic size allocation.
"""

import math

import numpy as np
from scipy.optimize import brentq, minimize_scalar
from scipy.stats import f as f_distribution
from scipy.stats import t as t_distribution

from .membrane_exchange_source import CALIBRATION_RUN, CALIBRATION_TIMES, TARGET_RUN


ASSUMPTIONS = (
    'Nominal optical-standard concentrations are known without error.',
    'Raw absorbance errors are independent Gaussian with a common variance '
    'for standards and chamber samples within each run.',
    'Five standards do not establish linearity, temporal stability, matrix '
    'equivalence, Gaussian errors, or equal variances.',
    'Sampling removes and replaces 0.02 mL simultaneously in both 11 mL chambers; '
    'observations precede collection.',
    'The reference measure is compartment volume, neither log-orthopolic nor '
    'linear-orthopolic size allocation.',
)


def _array(values, name):
    result = np.asarray(values, dtype=float)
    if result.ndim != 1 or not np.isfinite(result).all():
        raise ValueError(f'{name} must be a finite one-dimensional sequence')
    return result


def _alpha(alpha):
    alpha = float(alpha)
    if not math.isfinite(alpha) or not 0 < alpha < 1:
        raise ValueError('alpha must lie strictly between zero and one')
    return alpha


def fit_optics(standards, alpha=0.01):
    """Fit ``Abs_raw = slope * concentration_uM + intercept`` by OLS.

    ``inverse_xtx`` and ``coefficient_covariance`` use slope, intercept order.
    Invalid optical uncertainty stops qualification; it is never replaced by
    a variance floor. Standards' raw measurements and residuals are retained.
    """
    alpha = _alpha(alpha)
    concentrations = _array([row.concentration_uM for row in standards], 'standards')
    absorbances = _array([row.absorbance for row in standards], 'absorbances')
    n = len(concentrations)
    result = {
        'n': n, 'df': n - 2, 'slope': None, 'intercept': None, 'sse': None,
        'variance': None, 'inverse_xtx': None, 'coefficient_covariance': None,
        'slope_ci': None, 'residuals': None,
        'numerical_zero_sse_threshold': float(
            100 * np.finfo(float).eps ** 2 * max(1.0, float(absorbances @ absorbances))),
        'concentration_support': ([float(min(concentrations)), float(max(concentrations))]
                                  if n else None),
        'concentrations_uM': concentrations.tolist(),
        'absorbances': absorbances.tolist(), 'passed': False, 'stop_reasons': [],
    }
    if n <= 2 or len(set(concentrations)) != n:
        result['stop_reasons'].append('singular_or_insufficient_optical_standards')
        return result
    design = np.column_stack((concentrations, np.ones(n)))
    try:
        inverse = np.linalg.inv(design.T @ design)
        coefficients = np.linalg.lstsq(design, absorbances, rcond=None)[0]
    except np.linalg.LinAlgError:
        result['stop_reasons'].append('singular_optical_calibration')
        return result
    residuals = absorbances - design @ coefficients
    sse = float(residuals @ residuals)
    variance = sse / (n - 2)
    if not (np.isfinite(inverse).all() and np.isfinite(coefficients).all()
            and math.isfinite(variance)):
        result['stop_reasons'].append('nonfinite_optical_calibration')
        return result
    slope, intercept = map(float, coefficients)
    covariance = variance * inverse
    result.update(slope=slope, intercept=intercept, sse=sse, variance=variance,
                  inverse_xtx=inverse.tolist(), coefficient_covariance=covariance.tolist(),
                  residuals=residuals.tolist())
    if sse <= result['numerical_zero_sse_threshold']:
        result['stop_reasons'].append('unresolved_optical_variance')
    if inverse[0, 0] <= 0:
        result['stop_reasons'].append('singular_optical_calibration')
        return result
    half_width = float(t_distribution.ppf(1 - alpha / 2, n - 2)
                       * math.sqrt(variance * inverse[0, 0]))
    result['slope_ci'] = [slope - half_width, slope + half_width]
    if result['slope_ci'][0] <= 0:
        result['stop_reasons'].append('optical_slope_not_identified_positive')
    result['passed'] = not result['stop_reasons']
    return result


def _rates(z, volume_ml, reference_time_hours):
    if z == 0:
        return None, None
    rate = -math.log(z) / reference_time_hours
    return rate, volume_ml * rate / 2


def _accepted_intervals(objective, points, threshold):
    """Find all detected closed components, retaining refined narrow minima."""
    points = sorted(set(map(float, points)))
    values = [objective(point) - threshold for point in points]
    roots = [point for point, value in zip(points, values) if value == 0]
    for left, right, lo, hi in zip(points, points[1:], values, values[1:]):
        if (lo < 0 < hi) or (hi < 0 < lo):
            roots.append(float(brentq(lambda z: objective(z) - threshold,
                                      left, right, xtol=5e-324,
                                      rtol=4 * np.finfo(float).eps)))
    boundaries = sorted(set([0.0, 1.0, *roots]))
    intervals = []
    for left, right in zip(boundaries, boundaries[1:]):
        if objective((left + right) / 2) <= threshold:
            if intervals and intervals[-1][1] == left:
                intervals[-1][1] = right
            else:
                intervals.append([left, right])
    # A tangent confidence boundary may be an isolated accepted point.
    for point in roots + [0.0, 1.0]:
        if (objective(point) <= threshold
                and not any(left <= point <= right for left, right in intervals)):
            intervals.append([point, point])
    return sorted(intervals)


def profile_rate(times_hours, differences, *, retention_fraction, variance,
                 variance_df=3, volume_ml=11.0, reference_time_hours=6.0,
                 alpha=0.01, grid_points=4097):
    """Profile an unconstrained contrast amplitude over the full z interval.

    The accepted set inverts the absolute RSS F test, not an RSS-increment
    approximation. A dense grid and refinement of every detected minimum and
    maximum provide brackets; refined minima also seed the confidence search.
    ``None`` represents the infinite rate at z=0 in JSON-safe output.
    """
    alpha = _alpha(alpha)
    times = _array(times_hours, 'times_hours')
    differences = _array(differences, 'differences')
    if (len(times) != len(differences) or len(times) < 2 or times[0] != 0
            or not np.all(np.diff(times) > 0)):
        raise ValueError('Rate design requires paired, increasing times beginning at zero')
    parameters = (retention_fraction, variance, variance_df, volume_ml, reference_time_hours)
    if not all(math.isfinite(float(value)) and value > 0 for value in parameters):
        raise ValueError('Rate parameters must be finite and positive')
    if retention_fraction > 1 or type(grid_points) is not int or grid_points < 3:
        raise ValueError('Invalid retention fraction or rate grid size')
    n = len(times)
    sampling = retention_fraction ** np.arange(n)
    powers = times / reference_time_hours

    def profile(z):
        phi = sampling * np.power(float(z), powers)
        phi[0] = 1.0
        amplitude = float(phi @ differences / (phi @ phi))
        residuals = differences - amplitude * phi
        return float(residuals @ residuals), amplitude, phi

    def objective(z):
        return profile(z)[0]

    def derivative(z):
        _, amplitude, phi = profile(z)
        gradient = np.zeros(n)
        gradient[1:] = (sampling[1:] * powers[1:]
                        * np.power(float(z), powers[1:] - 1))
        return float(-2 * amplitude * (gradient @ (differences - amplitude * phi)))

    grid = np.linspace(0.0, 1.0, grid_points)
    values = np.array([objective(z) for z in grid])
    candidates = [0.0, 1.0]
    search_points = grid.tolist()
    brackets = [(float(grid[0]), float(grid[1]), 1),
                (float(grid[-2]), float(grid[-1]), 1)]
    for i in range(1, grid_points - 1):
        middle, left, right = values[i], values[i - 1], values[i + 1]
        minimum = middle <= left and middle <= right and (middle < left or middle < right)
        maximum = middle >= left and middle >= right and (middle > left or middle > right)
        if minimum or maximum:
            brackets.append((float(grid[i - 1]), float(grid[i + 1]), 1 if minimum else -1))
            if minimum:
                candidates.append(float(grid[i]))
    for left, right, sign in brackets:
        optimum = minimize_scalar(lambda z: sign * objective(z), bounds=(left, right),
                                  method='bounded', options={'xatol': 1e-15})
        point = float(optimum.x)
        # Refine a derivative sign bracket as well: bounded minimization's
        # stopping rule alone loses precision for exceptionally narrow sets.
        derivative_left = max(left, np.finfo(float).tiny)
        dl, dr = derivative(derivative_left), derivative(right)
        if math.isfinite(dl) and math.isfinite(dr) and dl * dr < 0:
            point = float(brentq(derivative, derivative_left, right, xtol=5e-324,
                                 rtol=4 * np.finfo(float).eps))
        search_points.append(point)
        if sign == 1:
            candidates.append(point)
    z = min(candidates, key=lambda point: (objective(point), point))
    rss, amplitude, phi = profile(z)
    threshold = float(2 * (n - 1) * variance
                      * f_distribution.ppf(1 - alpha, n - 1, variance_df))
    intervals = _accepted_intervals(objective, [*search_points, z], threshold)
    endpoint_tests = {}
    for label, point in (('z0', 0.0), ('z1', 1.0)):
        endpoint_rss = objective(point)
        statistic = endpoint_rss / (2 * (n - 1) * variance)
        endpoint_tests[label] = {
            'rss': endpoint_rss, 'statistic': float(statistic),
            'p_value': float(f_distribution.sf(statistic, n - 1, variance_df)),
            'accepted': bool(endpoint_rss <= threshold),
        }
    reasons = []
    if not intervals:
        reasons.append('empty_rate_confidence_set')
    if endpoint_tests['z0']['accepted']:
        reasons.append('instantaneous_exchange_not_excluded')
    if endpoint_tests['z1']['accepted']:
        reasons.append('no_exchange_not_excluded')
    if amplitude <= 0:
        reasons.append('nonpositive_fitted_amplitude')
    rate, conductance = _rates(z, volume_ml, reference_time_hours)
    return {
        'n': n, 'df': n - 1, 'z': z, 'lambda_per_hour': rate,
        'g_ml_per_hour': conductance,
        'boundary': 'instantaneous' if z == 0 else 'no_exchange' if z == 1 else None,
        'amplitude': amplitude, 'rss': rss, 'threshold': threshold,
        'confidence_intervals_z': intervals,
        'confidence_intervals_g_ml_per_hour': [
            [_rates(right, volume_ml, reference_time_hours)[1],
             _rates(left, volume_ml, reference_time_hours)[1]] for left, right in intervals],
        'confidence_intervals_lambda_per_hour': [
            [_rates(right, volume_ml, reference_time_hours)[0],
             _rates(left, volume_ml, reference_time_hours)[0]] for left, right in intervals],
        'endpoint_tests': endpoint_tests, 'times_hours': times.tolist(),
        'differences': differences.tolist(), 'fitted_differences': (amplitude * phi).tolist(),
        'passed': not reasons, 'stop_reasons': reasons,
    }


def _pairs(observations):
    """Group complete paired observations without accessing any target rows."""
    grouped = {}
    for row in observations:
        if not math.isfinite(row.time_hours) or not math.isfinite(row.absorbance):
            raise ValueError('Nonfinite chamber observation')
        if not row.chamber.endswith(('_C1', '_C2')):
            raise ValueError('Unknown donor/recipient chamber')
        cells = grouped.setdefault(row.sample, {})
        identity = (row.time_hours, row.chamber)
        if identity in cells:
            raise ValueError('Duplicate chamber observation')
        cells[identity] = row.absorbance
    result = []
    for sample in sorted(grouped):
        cells = grouped[sample]
        chambers = sorted({chamber for _, chamber in cells})
        if (len(chambers) != 2 or not chambers[0].endswith('_C1')
                or chambers[1] != chambers[0][:-1] + '2'):
            raise ValueError('Each sample needs matching donor and recipient chambers')
        times = sorted({time for time, _ in cells})
        if not times or times[0] != 0 or len(cells) != 2 * len(times):
            raise ValueError('Missing paired chamber observations or baseline')
        result.append({
            'sample': sample, 'donor_chamber': chambers[0], 'recipient_chamber': chambers[1],
            'times_hours': times,
            'donor': [cells[(time, chambers[0])] for time in times],
            'recipient': [cells[(time, chambers[1])] for time in times],
        })
    return result


def qualify_baselines(pairs, optics, *, alpha=0.01, family_size=16):
    """Check corrected baseline sums/contrasts and a one-sided family bound."""
    critical = float(t_distribution.ppf(1 - _alpha(alpha) / family_size, optics['df']))
    negative_limit = -critical * math.sqrt(
        optics['variance'] * (1 + optics['inverse_xtx'][1][1]))
    intercept = optics['intercept']
    outputs = []
    for pair in pairs:
        donor, recipient = pair['donor'][0], pair['recipient'][0]
        total, difference = donor + recipient - 2 * intercept, donor - recipient
        reasons = []
        if total <= 0:
            reasons.append('nonpositive_corrected_baseline_total')
        if difference <= 0:
            reasons.append('nonpositive_baseline_contrast')
        if donor - intercept < negative_limit or recipient - intercept < negative_limit:
            reasons.append('baseline_below_observation_compatibility_bound')
        outputs.append({
            **{key: pair[key] for key in ('sample', 'donor_chamber', 'recipient_chamber')},
            'donor_raw': donor, 'recipient_raw': recipient,
            'donor_minus_intercept': donor - intercept,
            'recipient_minus_intercept': recipient - intercept,
            'sum_minus_2_intercept': total, 'difference': difference,
            'passed': not reasons, 'stop_reasons': reasons,
        })
    return {'pairs': outputs, 'negative_limit': negative_limit, 't_critical': critical,
            'passed': all(pair['passed'] for pair in outputs),
            'stop_reasons': [f"{pair['sample']}:{reason}" for pair in outputs
                             for reason in pair['stop_reasons']]}


def total_stock_test(pairs, optics, *, retention_fraction, alpha=0.01):
    """Test all positive-time raw totals with shared baseline/intercept errors."""
    residuals, baseline_rows, u, identities, totals, expected_totals = [], [], [], [], [], []
    for k, pair in enumerate(pairs):
        initial = pair['donor'][0] + pair['recipient'][0]
        for j, time in enumerate(pair['times_hours'][1:], start=1):
            retained = retention_fraction ** j
            total = pair['donor'][j] + pair['recipient'][j]
            expected = retained * initial + 2 * (1 - retained) * optics['intercept']
            residuals.append(total - expected)
            totals.append(total)
            expected_totals.append(expected)
            baseline_rows.append([retained if column == k else 0 for column in range(len(pairs))])
            u.append(1 - retained)
            identities.append({
                **{key: pair[key] for key in ('sample', 'donor_chamber', 'recipient_chamber')},
                'time_hours': time, 'sampling_index': j,
            })
    m = len(residuals)
    if not m:
        raise ValueError('Stock test requires positive-time observations')
    residuals, baseline, u = np.array(residuals), np.array(baseline_rows), np.array(u)
    covariance = (2 * np.eye(m) + 2 * baseline @ baseline.T
                  + 4 * optics['inverse_xtx'][1][1] * np.outer(u, u))
    statistic = float(residuals @ np.linalg.solve(covariance, residuals)
                      / (m * optics['variance']))
    probability = float(f_distribution.sf(statistic, m, optics['df']))
    passed = probability >= _alpha(alpha)
    return {
        'n': m, 'df_numerator': m, 'df_denominator': optics['df'],
        'residuals': residuals.tolist(), 'covariance_q': covariance.tolist(),
        'identities': identities, 'raw_totals': totals, 'expected_raw_totals': expected_totals,
        'statistic': statistic,
        'threshold': float(f_distribution.ppf(1 - alpha, m, optics['df'])),
        'p_value': probability, 'passed': passed,
        'stop_reasons': [] if passed else ['total_stock_model_incompatible'],
    }


def qualify(source, config):
    """Return JSON-ready qualification, with no access to target follow-ups.

    Configuration uses the protocol's ``volume_mL``, ``withdrawal_mL``,
    ``reference_time_hours``, ``alpha``, ``baseline_family_size`` and
    ``rate_grid_points`` keys. The stock gate always runs after valid optics,
    including when baseline or rate identification fails. Invalid optics stop
    the dependent calculations and retain their explicit reasons.
    """
    volume = float(config.get('volume_mL', 11.0))
    withdrawal = float(config.get('withdrawal_mL', 0.02))
    reference = float(config.get('reference_time_hours', 6.0))
    dilution = float(config.get('dilution_factor', 10.0))
    alpha = _alpha(config.get('alpha', 0.01))
    family = config.get('baseline_family_size', 16)
    grid = config.get('rate_grid_points', 4097)
    if not (math.isfinite(volume) and math.isfinite(withdrawal)
            and volume > 0 and 0 < withdrawal < volume and reference > 0
            and math.isfinite(reference) and math.isfinite(dilution) and dilution > 0
            and type(family) is int and family > 0):
        raise ValueError('Invalid membrane qualification configuration')
    retention = 1 - withdrawal / volume
    optics = {
        CALIBRATION_RUN: fit_optics(source.calibration_standards, alpha),
        TARGET_RUN: fit_optics(source.target_standards, alpha),
    }
    result = {
        'passed': False, 'stop_reasons': [], 'assumptions': list(ASSUMPTIONS),
        'retention_fraction': retention, 'optics': optics,
        'baselines': {}, 'rates': [], 'total_stock': None,
    }
    for run, optical in optics.items():
        result['stop_reasons'].extend(f'{run}:{reason}' for reason in optical['stop_reasons'])
    if result['stop_reasons']:
        return result
    calibration = _pairs(source.calibration_observations)
    target = _pairs(source.target_baselines)
    if len(calibration) != 4 or len(target) != 4:
        raise ValueError('Qualification requires four calibration and four target pairs')
    if (any(tuple(pair['times_hours']) != CALIBRATION_TIMES for pair in calibration)
            or any(pair['times_hours'] != [0.0] for pair in target)):
        raise ValueError('Qualification observations do not match the frozen time design')
    for run, observations in ((CALIBRATION_RUN, source.calibration_observations),
                              (TARGET_RUN, source.target_baselines)):
        optical = optics[run]
        lower, upper = optical['concentration_support']
        concentrations, outside = [], []
        for row in observations:
            concentration = (row.absorbance - optical['intercept']) / optical['slope']
            concentrations.append(concentration)
            if not lower <= concentration <= upper:
                outside.append({'sample': row.sample, 'chamber': row.chamber,
                                'time_hours': row.time_hours,
                                'aliquot_concentration_uM': concentration,
                                'chamber_concentration_uM': dilution * concentration})
        optical['sample_extrapolation'] = {
            'input_count': len(concentrations), 'outside_support_count': len(outside),
            'aliquot_concentration_range_uM': [min(concentrations), max(concentrations)],
            'outside_support': outside,
        }
    for run, pairs in ((CALIBRATION_RUN, calibration), (TARGET_RUN, target)):
        baselines = qualify_baselines(pairs, optics[run], alpha=alpha, family_size=family)
        result['baselines'][run] = baselines
        result['stop_reasons'].extend(f'{run}:{reason}' for reason in baselines['stop_reasons'])
    for pair in calibration:
        rate = profile_rate(
            pair['times_hours'], np.array(pair['donor']) - np.array(pair['recipient']),
            retention_fraction=retention, variance=optics[CALIBRATION_RUN]['variance'],
            variance_df=optics[CALIBRATION_RUN]['df'], volume_ml=volume,
            reference_time_hours=reference, alpha=alpha, grid_points=grid)
        rate.update({key: pair[key] for key in ('sample', 'donor_chamber', 'recipient_chamber')})
        result['rates'].append(rate)
        result['stop_reasons'].extend(f"{pair['sample']}:{reason}" for reason in rate['stop_reasons'])
    stock = total_stock_test(calibration, optics[CALIBRATION_RUN],
                             retention_fraction=retention, alpha=alpha)
    result['total_stock'] = stock
    result['stop_reasons'].extend(stock['stop_reasons'])
    result['passed'] = not result['stop_reasons']
    return result
