"""Independent checks of sealed membrane transfer predictions and scores.

This module never imports the production transfer code or reads a source ZIP.
Prediction checks use the already qualified earlier cohort and target baselines.
Outcome checks require an explicitly supplied released result document. Optical
OLS uses centered sums, and joint uncertainty uses complex-step differentiation
of a separately expressed raw-baseline forecast, not production derivatives.
"""

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp
from scipy.stats import f as f_distribution


ROOT = Path(__file__).resolve().parents[1]
MODELS = ('exchange', 'persistence', 'instant_mixing', 'empirical')


def canonical_hash(document):
    return hashlib.sha256((json.dumps(document, indent=2, sort_keys=True,
                                      allow_nan=False) + '\n').encode()).hexdigest()


class Checks:
    def __init__(self):
        self.count = 0
        self.maximum = 0.0

    def check(self, actual, expected, path='', *, atol=3e-10, rtol=3e-9):
        if isinstance(expected, dict):
            if not isinstance(actual, dict) or set(actual) != set(expected):
                raise ValueError('Object fields differ: ' + path)
            for key in expected:
                self.check(actual[key], expected[key], path + '.' + key, atol=atol, rtol=rtol)
        elif isinstance(expected, (list, tuple, np.ndarray)):
            if not isinstance(actual, (list, tuple, np.ndarray)) or len(actual) != len(expected):
                raise ValueError('Array length differs: ' + path)
            for i, (a, e) in enumerate(zip(actual, expected)):
                self.check(a, e, path + '[' + str(i) + ']', atol=atol, rtol=rtol)
        elif isinstance(expected, (int, float, np.number)) and not isinstance(expected, (bool, np.bool_)):
            if isinstance(actual, (bool, np.bool_)) or not isinstance(actual, (int, float, np.number)):
                raise ValueError('Wrong numeric type: ' + path)
            a, e = float(actual), float(expected)
            if not math.isfinite(a) or not math.isfinite(e):
                raise ValueError('Nonfinite comparison: ' + path)
            self.count += 1
            difference = abs(a - e)
            self.maximum = max(self.maximum, difference)
            if difference > atol + rtol * abs(e):
                raise ValueError('Numeric mismatch: ' + path)
        elif actual != expected or type(actual) is not type(expected):
            raise ValueError('Value mismatch: ' + path)

    def report(self):
        return {'numeric_checks': self.count, 'max_abs_diff': self.maximum}


def optical_fit(standards):
    x = np.array([row['concentration_uM'] for row in standards], dtype=float)
    y = np.array([row['absorbance'] for row in standards], dtype=float)
    xc, yc = x - x.mean(), y - y.mean()
    xx = xc @ xc
    a = float(xc @ yc / xx)
    b = float(y.mean() - a * x.mean())
    residuals = y - (a * x + b)
    variance = float(residuals @ residuals / (len(x) - 2))
    h = np.array([[1 / xx, -x.mean() / xx],
                  [-x.mean() / xx, 1 / len(x) + x.mean() ** 2 / xx]])
    weights = 1 / len(x) - x.mean() * xc / xx
    return {'a': a, 'b': b, 'variance': variance, 'H': h,
            'covariance': variance * h, 'intercept_weights': weights}


def parameterization(qualification):
    if not qualification['qualification']['passed'] or qualification['qualification']['stop_reasons']:
        raise ValueError('A passed qualification is required')
    if qualification['target_later_responses_decoded']:
        raise ValueError('Qualification must precede later target access')
    if qualification['inputs']['target_observations'] is not None:
        raise ValueError('Qualification contains later target outcomes')
    config = qualification['config']
    optics = optical_fit(qualification['inputs']['target_standards'])
    baseline = qualification['inputs']['target_baselines']
    pairs = []
    for sample in sorted({row['sample'] for row in baseline}):
        rows = sorted((row for row in baseline if row['sample'] == sample),
                      key=lambda row: row['chamber'])
        if len(rows) != 2 or any(row['time_hours'] != 0 for row in rows):
            raise ValueError('Wrong baseline partition')
        pairs.append((sample, rows))
    if len(pairs) != 4:
        raise ValueError('Expected four target pairs')
    theta = np.array([optics['a'], optics['b'],
                      *[row['absorbance'] for _, rows in pairs for row in rows]], dtype=float)
    covariance = np.zeros((10, 10))
    covariance[:2, :2] = optics['covariance']
    covariance[2:, 2:] = np.eye(8) * optics['variance']
    times = sorted({row['time_hours'] for row in qualification['inputs']['target_design']})
    f = 1 - config['withdrawal_mL'] / config['volume_mL']
    return config, optics, pairs, theta, covariance, np.array(times), f


def raw_prediction(theta, pair_index, j, kernel, f, dilution):
    """Separately written forecast from affine coefficients and raw baselines."""
    a, b = theta[:2]
    donor, recipient = theta[2 + 2 * pair_index:4 + 2 * pair_index]
    # Mixing matrix applied before conversion avoids copying the production
    # total/contrast Jacobian expressions.
    mix = np.array([[(1 + kernel) / 2, (1 - kernel) / 2],
                    [(1 - kernel) / 2, (1 + kernel) / 2]])
    return (f ** j) * dilution * (mix @ np.array([donor - b, recipient - b])) / a


def complex_step_jacobian(function, theta):
    base = np.asarray(function(theta), dtype=float)
    jacobian = np.empty((base.size, len(theta)))
    for column in range(len(theta)):
        perturbed = np.asarray(theta, dtype=complex)
        perturbed[column] += 1e-25j
        jacobian[:, column] = np.asarray(function(perturbed)).imag.reshape(-1) / 1e-25
    return jacobian


def kernels(qualification, times, f):
    rates = qualification['qualification']['rates']
    reference = qualification['config']['reference_time_hours']
    z = np.array([row['z'] for row in rates])
    each = z[None, :] ** (times[:, None] / reference)
    each[times == 0] = 1
    lower_z = np.array([min(interval[0] for interval in row['confidence_intervals_z']) for row in rates])
    upper_z = np.array([max(interval[1] for interval in row['confidence_intervals_z']) for row in rates])
    lower = np.mean(lower_z[None, :] ** (times[:, None] / reference), axis=1)
    upper = np.mean(upper_z[None, :] ** (times[:, None] / reference), axis=1)
    empirical_times = np.asarray(rates[0]['times_hours'])
    empirical_each = [np.array(row['differences']) /
                      (row['differences'][0] * f ** np.arange(len(empirical_times))) for row in rates]
    empirical = np.interp(times, empirical_times, np.mean(empirical_each, axis=0))
    timing = {name: np.mean(z[None, :] ** (np.maximum(0, times + offset)[:, None] / reference), axis=1)
              for name, offset in [('minus_10_minutes', -1 / 6), ('plus_10_minutes', 1 / 6)]}
    return {'exchange': each.mean(axis=1), 'persistence': np.ones(len(times)),
            'instant_mixing': (times == 0).astype(float), 'empirical': empirical}, each, lower, upper, timing


def integrated_prediction(initial, times, conductance, config):
    """Direct edge-balance ODE with collection impulses, independent of K(t)."""
    state = np.asarray(initial, dtype=float)
    result = [state.copy()]
    f = 1 - config['withdrawal_mL'] / config['volume_mL']
    volume = config['volume_mL']
    for left, right in zip(times, times[1:]):
        state = state * f
        def derivative(_time, concentration):
            transfer = conductance * (concentration[0] - concentration[1]) / volume
            return [-transfer, transfer]
        solution = solve_ivp(derivative, (left, right), state, method='DOP853',
                             rtol=2e-12, atol=2e-12)
        if not solution.success:
            raise ArithmeticError('ODE verification failed')
        state = solution.y[:, -1]
        result.append(state.copy())
    return np.asarray(result)


def _verify_forecasts(forecasts, qualification, checks):
    config, optics, pairs, theta, covariance, times, f = parameterization(qualification)
    model_kernels, each, lower, upper, timing = kernels(qualification, times, f)
    checks.check(forecasts['config'], config, 'config')
    checks.check(forecasts['design_commit'], qualification['design_commit'], 'design_commit')
    checks.check(forecasts['source_sha256'], qualification['source_sha256'], 'source_sha256')
    checks.check(forecasts['reference_measure'], config['reference_measure'], 'reference_measure')
    checks.check(forecasts['target_later_responses_decoded'], False, 'target_decoding')
    checks.check(forecasts['retention_fraction'], f, 'retention_fraction')
    checks.check(forecasts['optics'], qualification['qualification']['optics'][config['target_run']], 'optics')
    checks.check(forecasts['optics']['slope'], optics['a'], 'independent_slope')
    checks.check(forecasts['optics']['intercept'], optics['b'], 'independent_intercept')
    checks.check(forecasts['optics']['variance'], optics['variance'], 'independent_variance')
    checks.check(forecasts['optics']['coefficient_covariance'], optics['covariance'], 'independent_covariance')
    checks.check(forecasts['calibrators'], [
        {key: row[key] for key in ('sample', 'z', 'lambda_per_hour', 'g_ml_per_hour', 'confidence_intervals_z')}
        for row in qualification['qualification']['rates']], 'calibrators')
    baseline_pairs = []
    expected_rows = []
    input_order = ['slope', 'intercept']
    dilution = config['dilution_factor']
    ode_discrepancy = 0.0
    for k, (sample, rows) in enumerate(pairs):
        initial = dilution * (theta[2 + 2 * k:4 + 2 * k] - theta[1]) / theta[0]
        initial_raw = theta[2 + 2 * k:4 + 2 * k]
        baseline_pairs.append({
            'sample': sample, 'donor_chamber': rows[0]['chamber'],
            'recipient_chamber': rows[1]['chamber'], 'donor_raw': float(initial_raw[0]),
            'recipient_raw': float(initial_raw[1]), 'donor_uM': float(initial[0]),
            'recipient_uM': float(initial[1]), 'total_uM': float(sum(initial)),
            'contrast_uM': float(initial[0] - initial[1]),
            'total_corrected_raw': float(sum(initial_raw) - 2 * theta[1]),
            'contrast_raw': float(initial_raw[0] - initial_raw[1]),
        })
        input_order.extend(f"{sample}:{row['chamber']}" for row in rows)
        integrated = np.mean([integrated_prediction(initial, times, row['g_ml_per_hour'], config)
                              for row in qualification['qualification']['rates']], axis=0)
        for j, time in enumerate(times[1:], 1):
            values = {name: raw_prediction(theta, k, j, kernel[j], f, dilution)
                      for name, kernel in model_kernels.items()}
            interval = [raw_prediction(theta, k, j, boundary[j], f, dilution) for boundary in (lower, upper)]
            singles = [raw_prediction(theta, k, j, kernel, f, dilution) for kernel in each[j]]
            shifted = {name: raw_prediction(theta, k, j, kernel[j], f, dilution)
                       for name, kernel in timing.items()}
            ode_discrepancy = max(ode_discrepancy, float(np.max(abs(integrated[j] - values['exchange']))))
            checks.check(values['exchange'], integrated[j], f'ode_pair[{k}][{j}]', atol=2e-8, rtol=2e-10)
            for chamber_index, source in enumerate(rows):
                predicted = float(values['exchange'][chamber_index])
                expected_rows.append({
                    'sample': sample, 'chamber': source['chamber'], 'time_hours': float(time),
                    'sampling_index': j, 'concentration_uM': predicted,
                    'raw_absorbance_prediction': float(theta[0] * predicted / dilution + theta[1]),
                    'model_concentrations_uM': {name: float(value[chamber_index]) for name, value in values.items()},
                    'rate_envelope_uM': sorted(float(value[chamber_index]) for value in interval),
                    'between_calibrator_range_uM': [float(min(value[chamber_index] for value in singles)),
                                                   float(max(value[chamber_index] for value in singles))],
                    'single_calibrator_concentrations_uM': [float(value[chamber_index]) for value in singles],
                    'timing_sensitivity_uM': {name: float(value[chamber_index]) for name, value in shifted.items()},
                })
    checks.check(forecasts['baseline_pairs'], baseline_pairs, 'baseline_pairs')
    expected_kernels = [{
        'time_hours': float(time), 'sampling_index': j,
        'models': {name: float(value[j]) for name, value in model_kernels.items()},
        'single_calibrator': each[j].tolist(), 'rate_envelope': [float(lower[j]), float(upper[j])],
        'timing_sensitivity': {name: float(value[j]) for name, value in timing.items()},
    } for j, time in enumerate(times)]
    checks.check(forecasts['kernels'], expected_kernels, 'kernels')
    calibration_rates = qualification['qualification']['rates']
    calibration_times = np.asarray(calibration_rates[0]['times_hours'])
    normalized = np.mean([np.asarray(row['differences']) /
                          (row['differences'][0] * f ** np.arange(len(calibration_times)))
                          for row in calibration_rates], axis=0)
    checks.check(forecasts['empirical_calibration'], {
        'times_hours': calibration_times.tolist(), 'normalized_contrast': normalized.tolist()},
        'empirical_calibration')
    checks.check(forecasts['uncertainty_scope'],
        'Conditional optical and baseline uncertainty excludes rate uncertainty, '
        'new-membrane variation and unmodelled observation errors; separate '
        'rate-set, between-calibrator and timing sensitivities are not population prediction intervals.',
        'uncertainty_scope')

    def point_vector(parameters):
        return np.concatenate([raw_prediction(parameters, k, j, model_kernels['exchange'][j], f, dilution)
                               for k in range(4) for j in range(1, len(times))])

    jacobian = complex_step_jacobian(point_vector, theta)
    prediction_covariance = jacobian @ covariance @ jacobian.T
    uncertainty = forecasts['conditional_uncertainty']
    checks.check(uncertainty['input_order'], input_order, 'uncertainty.input_order')
    checks.check(uncertainty['input_covariance'], covariance, 'uncertainty.input_covariance')
    checks.check(uncertainty['jacobian'], jacobian, 'uncertainty.jacobian')
    checks.check(uncertainty['prediction_covariance_uM2'], prediction_covariance, 'uncertainty.prediction_covariance')
    for index, row in enumerate(expected_rows):
        row['optical_baseline_sd_uM'] = math.sqrt(prediction_covariance[index, index])
    checks.check(forecasts['predictions'], expected_rows, 'predictions')
    return ode_discrepancy


def verify_predictions(document, qualification):
    checks = Checks()
    checks.check(document['study'], qualification['study'], 'study')
    checks.check(document['design_commit'], qualification['design_commit'], 'design_commit')
    checks.check(document['source_sha256'], qualification['source_sha256'], 'source_sha256')
    checks.check(document['qualification_sha256'], canonical_hash(qualification), 'qualification_sha256')
    checks.check(document['target_later_responses_decoded'], False, 'target_later_responses_decoded')
    implementation = document['implementation_commit']
    if not isinstance(implementation, str) or len(implementation) != 40 or any(c not in '0123456789abcdef' for c in implementation):
        raise ValueError('Invalid implementation commit identifier')
    ode_difference = _verify_forecasts(document['forecasts'], qualification, checks)
    return {**checks.report(), 'qualification_sha256': canonical_hash(qualification),
            'prediction_sha256': canonical_hash(document),
            'target_later_responses_decoded': False,
            'integration_max_abs_diff': ode_difference,
            'uncertainty_method': 'Complex-step derivatives of an independent raw-baseline mixing matrix'}


def _verify_evaluation(evaluation, forecasts, qualification, checks):
    config, optics, pairs, theta, covariance, times, f = parameterization(qualification)
    rows = evaluation['observations']
    predictions = forecasts['predictions']
    if len(rows) != 56:
        raise ValueError('Wrong target observation count')
    identities = ('sample', 'chamber', 'time_hours')
    for index, (row, prediction) in enumerate(zip(rows, predictions)):
        if set(row) != {*identities, 'absorbance'}:
            raise ValueError('Unexpected target row fields')
        checks.check([row[key] for key in identities], [prediction[key] for key in identities],
                     f'observation_identity[{index}]')
    raw = np.asarray([row['absorbance'] for row in rows], dtype=float).reshape(4, 7, 2)
    if not np.isfinite(raw).all():
        raise ValueError('Nonfinite target observation')
    measured = (raw - theta[1]) * config['dilution_factor'] / theta[0]
    initial = (theta[2:].reshape(4, 2) - theta[1]) * config['dilution_factor'] / theta[0]
    totals0 = initial.sum(axis=1)
    observed_total, observed_contrast = measured.sum(axis=2), measured[:, :, 0] - measured[:, :, 1]
    predicted_by_model = {name: np.asarray([p['model_concentrations_uM'][name] for p in predictions]).reshape(4, 7, 2)
                          for name in MODELS}
    metrics, model_details = {}, {}
    for name, prediction in predicted_by_model.items():
        errors = (prediction - measured) / totals0[:, None, None]
        contrast_error = errors[:, :, 0] - errors[:, :, 1]
        total_error = errors.sum(axis=2)
        joint_absolute, joint_squared = np.abs(errors).mean(axis=2), (errors ** 2).mean(axis=2)
        model_details[name] = (contrast_error, total_error, joint_absolute, joint_squared)
        pair_metrics = np.column_stack((np.abs(contrast_error).mean(axis=1), np.abs(total_error).mean(axis=1),
                                        joint_absolute.mean(axis=1), np.sqrt(joint_squared.mean(axis=1))))
        metric_names = ('primary_contrast_mae', 'normalized_total_mae',
                        'normalized_joint_chamber_mae', 'normalized_joint_chamber_rmse')
        aggregate = np.r_[pair_metrics[:, :3].mean(axis=0), np.sqrt(joint_squared.mean())]
        metrics[name] = {key: float(value) for key, value in zip(metric_names, aggregate)}
        metrics[name]['per_pair'] = [dict(sample=pairs[k][0], **{
            key: float(value) for key, value in zip(metric_names, pair_metrics[k])}) for k in range(4)]
    expected_pairs = []
    for k, (sample, baseline) in enumerate(pairs):
        points = []
        for index, time in enumerate(times[1:]):
            j = index + 1
            model_points = {}
            for name, prediction in predicted_by_model.items():
                contrast_error, total_error, joint_absolute, joint_squared = model_details[name]
                model_points[name] = {
                    'donor_uM': float(prediction[k, index, 0]), 'recipient_uM': float(prediction[k, index, 1]),
                    'contrast_uM': float(prediction[k, index, 0] - prediction[k, index, 1]),
                    'normalized_contrast': float((prediction[k, index, 0] - prediction[k, index, 1]) / totals0[k]),
                    'normalized_contrast_error': float(contrast_error[k, index]),
                    'normalized_total_error': float(total_error[k, index]),
                    'normalized_joint_chamber_absolute_error': float(joint_absolute[k, index]),
                    'normalized_joint_chamber_squared_error': float(joint_squared[k, index]),
                }
            points.append({
                'time_hours': float(time), 'sampling_index': j,
                'donor_raw': float(raw[k, index, 0]), 'recipient_raw': float(raw[k, index, 1]),
                'donor_uM': float(measured[k, index, 0]), 'recipient_uM': float(measured[k, index, 1]),
                'contrast_uM': float(observed_contrast[k, index]), 'total_uM': float(observed_total[k, index]),
                'normalized_contrast': float(observed_contrast[k, index] / totals0[k]),
                'expected_total_uM': float(f ** j * totals0[k]),
                'total_recovery_ratio': float(observed_total[k, index] / (f ** j * totals0[k])),
                'models': model_points,
            })
        expected_pairs.append({'sample': sample, 'baseline_total_uM': float(totals0[k]), 'points': points})
    checks.check(evaluation['pairs'], expected_pairs, 'evaluation.pairs')
    checks.check(evaluation['scores'], metrics, 'evaluation.scores')
    gains = {}
    for name in MODELS[1:]:
        error = metrics[name]['primary_contrast_mae']
        difference = error - metrics['exchange']['primary_contrast_mae']
        pair_gains = []
        for model, exchange in zip(metrics[name]['per_pair'], metrics['exchange']['per_pair']):
            gain = model['primary_contrast_mae'] - exchange['primary_contrast_mae']
            pair_gains.append({'sample': model['sample'], 'absolute_difference': gain,
                               'relative_gain': gain / model['primary_contrast_mae']
                               if model['primary_contrast_mae'] > 0 else None})
        gains[name] = {'absolute_difference': difference, 'relative_gain': difference / error if error > 0 else None,
                       'per_pair': pair_gains, 'pairs_with_positive_difference': sum(p['absolute_difference'] > 0 for p in pair_gains)}
    checks.check(evaluation['gains'], gains, 'evaluation.gains')
    # Original independent observations: eight baselines, 56 later readings,
    # and five standards. The fitted-intercept column weights preserve all
    # shared standard uncertainty without using the compact Q expression.
    g = np.zeros((28, 69))
    residuals, total_raw, expected_raw, stock_identities = [], [], [], []
    for k, (sample, baseline) in enumerate(pairs):
        for j, time in enumerate(times[1:], 1):
            index = k * 7 + j - 1
            retained = f ** j
            g[index, 2 * k:2 * k + 2] = -retained
            g[index, 8 + 2 * index:10 + 2 * index] = 1
            g[index, 64:] = -2 * (1 - retained) * optics['intercept_weights']
            total = float(raw[k, j - 1].sum())
            expected = retained * theta[2 + 2 * k:4 + 2 * k].sum() + 2 * (1 - retained) * theta[1]
            residuals.append(total - expected)
            total_raw.append(total)
            expected_raw.append(float(expected))
            stock_identities.append({'sample': sample, 'donor_chamber': baseline[0]['chamber'],
                                     'recipient_chamber': baseline[1]['chamber'], 'time_hours': float(time), 'sampling_index': j})
    q = g @ g.T
    whitened = np.linalg.solve(np.linalg.cholesky(q), residuals)
    statistic = float(whitened @ whitened / (28 * optics['variance']))
    probability = float(f_distribution.sf(statistic, 28, 3))
    passed = probability >= config['alpha']
    stock = {'n': 28, 'df_numerator': 28, 'df_denominator': 3, 'residuals': residuals,
             'covariance_q': q.tolist(), 'identities': stock_identities, 'raw_totals': total_raw,
             'expected_raw_totals': expected_raw, 'statistic': statistic,
             'threshold': float(f_distribution.ppf(1 - config['alpha'], 28, 3)),
             'p_value': probability, 'passed': passed,
             'stop_reasons': [] if passed else ['total_stock_model_incompatible']}
    checks.check(evaluation['total_stock'], stock, 'evaluation.total_stock')
    lower, upper = forecasts['optics']['concentration_support']
    outside, concentrations = [], []
    for row in rows:
        value = (row['absorbance'] - theta[1]) / theta[0]
        concentrations.append(value)
        if not lower <= value <= upper:
            outside.append({**{key: row[key] for key in identities}, 'aliquot_concentration_uM': value,
                            'chamber_concentration_uM': config['dilution_factor'] * value})
    checks.check(evaluation['extrapolation'], {
        'input_count': 56, 'outside_support_count': len(outside),
        'aliquot_concentration_range_uM': [min(concentrations), max(concentrations)],
        'outside_support': outside}, 'evaluation.extrapolation')
    beats = {name: gain['absolute_difference'] > 0 for name, gain in gains.items()}
    checks.check(evaluation['decision'], {'exchange_beats_each_benchmark': beats,
                 'exchange_beats_all_benchmarks': all(beats.values()),
                 'target_stock_compatible': passed, 'comparison_boundary': 0.0}, 'evaluation.decision')
    checks.check(evaluation['target_later_responses_decoded'], True, 'evaluation.target_decoding')


def verify_result(result, prediction, qualification):
    prediction_report = verify_predictions(prediction, qualification)
    checks = Checks()
    checks.count = prediction_report['numeric_checks']
    checks.maximum = prediction_report['max_abs_diff']
    for field in ('study', 'design_commit', 'implementation_commit', 'qualification_sha256'):
        checks.check(result[field], prediction[field], 'result.' + field)
    checks.check(result['prediction_sha256'], canonical_hash(prediction), 'result.prediction_sha256')
    checks.check(result['qualification_sha256'], canonical_hash(qualification), 'result.qualification_sha256')
    checks.check(result['target_later_responses_decoded'], True, 'result.target_decoding')
    commit = result['prediction_commit']
    if not isinstance(commit, str) or len(commit) != 40 or any(c not in '0123456789abcdef' for c in commit):
        raise ValueError('Invalid prediction commit identifier')
    _verify_evaluation(result['evaluation'], prediction['forecasts'], qualification, checks)
    return {**checks.report(), 'qualification_sha256': canonical_hash(qualification),
            'prediction_sha256': canonical_hash(prediction), 'result_sha256': canonical_hash(result),
            'target_later_responses_decoded': True,
            'stock_covariance_method': 'Independent original-observation error map G G-transpose',
            'uncertainty_method': 'Complex-step derivatives of an independent raw-baseline mixing matrix'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qualification', type=Path, required=True)
    parser.add_argument('--predictions', type=Path, required=True)
    parser.add_argument('--result', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    qualification = json.loads(args.qualification.read_text())
    prediction = json.loads(args.predictions.read_text())
    report = (verify_result(json.loads(args.result.read_text()), prediction, qualification)
              if args.result else verify_predictions(prediction, qualification))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as stream:
        json.dump(report, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')
    print(json.dumps(report, sort_keys=True))


if __name__ == '__main__':
    main()
