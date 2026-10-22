"""Fixed membrane-pair forecasts and scores; this module performs no file I/O.

The reference measure is compartment volume, neither log-orthopolic nor
linear-orthopolic size allocation. Rates come only from the qualified earlier
cohort; target baselines set amplitudes. All target measurements must be supplied
explicitly to ``evaluate`` by a caller that has checked the committed forecasts.
"""

from copy import deepcopy
import math

import numpy as np

from .membrane_exchange import total_stock_test
from .membrane_exchange_source import TARGET_RUN, TARGET_TIMES


MODELS = ('exchange', 'persistence', 'instant_mixing', 'empirical')
TIMING_SHIFTS = {'minus_10_minutes': -1 / 6, 'plus_10_minutes': 1 / 6}


def _concentration(total, contrast, retained, kernel, sign):
    return retained * (total + sign * kernel * contrast) / 2


def forecast(qualification_document):
    """Generate all fixed forecasts from qualified inputs, without targets.

    Prediction order is pair, positive time, donor then recipient. The complete
    covariance matrix uses exactly this order. Its ten inputs are slope,
    intercept, then the eight independent raw baseline readings, donor first
    within each pair. Optical coefficient covariance remains a full 2x2 block.
    Rate-set, between-calibrator and timing diagnostics remain separate from
    this conditional optical/baseline covariance.
    """
    qdoc = qualification_document
    result, cfg = qdoc['qualification'], qdoc['config']
    if (result['passed'] is not True or result['stop_reasons']
            or qdoc['target_later_responses_decoded'] is not False
            or qdoc['inputs']['target_observations'] is not None):
        raise ValueError('Forecasts require passing qualification with targets withheld')
    optics = result['optics'][TARGET_RUN]
    a, b = optics['slope'], optics['intercept']
    dilution, retained = cfg['dilution_factor'], result['retention_fraction']
    rates = result['rates']
    pairs = result['baselines'][TARGET_RUN]['pairs']
    if len(rates) != 4 or len(pairs) != 4 or not all(r['passed'] for r in rates):
        raise ValueError('Expected four qualified rates and four target baseline pairs')
    pairs = sorted(pairs, key=lambda p: p['sample'])
    rates = sorted(rates, key=lambda r: r['sample'])
    reference = cfg['reference_time_hours']
    calibrators = [{key: deepcopy(r[key]) for key in
                   ('sample', 'z', 'lambda_per_hour', 'g_ml_per_hour', 'confidence_intervals_z')}
                  for r in rates]
    calibration_times = np.asarray(rates[0]['times_hours'])
    empirical_values = np.mean([
        np.asarray(r['differences']) /
        (r['differences'][0] * retained ** np.arange(len(calibration_times)))
        for r in rates], axis=0)

    def mean_kernel(time):
        return float(np.mean([r['z'] ** (time / reference) for r in rates]))

    kernels = []
    for j, time in enumerate(TARGET_TIMES):
        individual = [r['z'] ** (time / reference) for r in rates]
        limits = []
        for rate in rates:
            intervals = rate['confidence_intervals_z']
            if not intervals:
                raise ValueError('Empty accepted rate set cannot produce forecasts')
            limits.append((min(lo ** (time / reference) for lo, _ in intervals),
                           max(hi ** (time / reference) for _, hi in intervals)))
        kernels.append(dict(
            time_hours=time, sampling_index=j,
            models=dict(exchange=float(np.mean(individual)), persistence=1.0,
                        instant_mixing=1.0 if j == 0 else 0.0,
                        empirical=float(np.interp(time, calibration_times, empirical_values))),
            single_calibrator=individual,
            rate_envelope=[float(np.mean([lo for lo, _ in limits])),
                           float(np.mean([hi for _, hi in limits]))],
            timing_sensitivity={name: mean_kernel(max(0.0, time + shift))
                                for name, shift in TIMING_SHIFTS.items()}))

    baselines, predictions, jacobian = [], [], []
    order = ['slope', 'intercept']
    for k, pair in enumerate(pairs):
        donor, recipient = pair['donor_raw'], pair['recipient_raw']
        total_raw, contrast_raw = donor + recipient - 2 * b, donor - recipient
        total, contrast = dilution * total_raw / a, dilution * contrast_raw / a
        if total <= 0 or contrast <= 0:
            raise ValueError('Target baseline total and contrast must remain positive')
        baseline = dict(
            sample=pair['sample'], donor_chamber=pair['donor_chamber'],
            recipient_chamber=pair['recipient_chamber'], donor_raw=donor, recipient_raw=recipient,
            donor_uM=dilution * (donor - b) / a,
            recipient_uM=dilution * (recipient - b) / a,
            total_uM=total, contrast_uM=contrast,
            total_corrected_raw=total_raw, contrast_raw=contrast_raw)
        baselines.append(baseline)
        order.extend(f"{pair['sample']}:{pair[field]}"
                     for field in ('donor_chamber', 'recipient_chamber'))
        for kernel in kernels[1:]:
            j, time = kernel['sampling_index'], kernel['time_hours']
            f = retained ** j
            for chamber, sign in ((pair['donor_chamber'], 1), (pair['recipient_chamber'], -1)):
                values = {name: _concentration(total, contrast, f, value, sign)
                          for name, value in kernel['models'].items()}
                individual = [_concentration(total, contrast, f, value, sign)
                              for value in kernel['single_calibrator']]
                value = values['exchange']
                predictions.append(dict(
                    sample=pair['sample'], chamber=chamber, time_hours=time, sampling_index=j,
                    concentration_uM=value, raw_absorbance_prediction=b + a * value / dilution,
                    model_concentrations_uM=values,
                    rate_envelope_uM=sorted(_concentration(total, contrast, f, v, sign)
                                           for v in kernel['rate_envelope']),
                    between_calibrator_range_uM=[min(individual), max(individual)],
                    single_calibrator_concentrations_uM=individual,
                    timing_sensitivity_uM={name: _concentration(total, contrast, f, v, sign)
                                           for name, v in kernel['timing_sensitivity'].items()}))
                row = np.zeros(10)
                row[0], row[1] = -value / a, -dilution * f / a
                K = kernel['models']['exchange']
                row[2 + 2 * k] = dilution * f * (1 + sign * K) / (2 * a)
                row[3 + 2 * k] = dilution * f * (1 - sign * K) / (2 * a)
                jacobian.append(row)
    input_covariance = np.zeros((10, 10))
    input_covariance[:2, :2] = optics['coefficient_covariance']
    input_covariance[2:, 2:] = np.eye(8) * optics['variance']
    jacobian = np.asarray(jacobian)
    covariance = jacobian @ input_covariance @ jacobian.T
    for row, variance in zip(predictions, covariance.diagonal()):
        row['optical_baseline_sd_uM'] = math.sqrt(float(variance))
    expected_design = {(p['sample'], p['chamber'], p['time_hours']) for p in predictions}
    input_design = {(p['sample'], p['chamber'], p['time_hours'])
                    for p in qdoc['inputs']['target_design'] if p['time_hours'] > 0}
    if len(predictions) != 56 or expected_design != input_design:
        raise ValueError('Forecast identities differ from the frozen target grid')
    return dict(
        config=deepcopy(cfg), design_commit=qdoc['design_commit'],
        source_sha256=qdoc['source_sha256'], reference_measure=cfg['reference_measure'],
        optics=deepcopy(optics), retention_fraction=retained, calibrators=calibrators,
        baseline_pairs=baselines, kernels=kernels, predictions=predictions,
        empirical_calibration=dict(times_hours=calibration_times.tolist(),
                                   normalized_contrast=empirical_values.tolist()),
        conditional_uncertainty=dict(
            input_order=order, input_covariance=input_covariance.tolist(),
            jacobian=jacobian.tolist(), prediction_covariance_uM2=covariance.tolist()),
        uncertainty_scope='Conditional optical and baseline uncertainty excludes rate uncertainty, '
                          'new-membrane variation and unmodelled observation errors; separate '
                          'rate-set, between-calibrator and timing sensitivities are not population prediction intervals.',
        target_later_responses_decoded=False)


def evaluate(forecasts, target_observations):
    """Score all 56 supplied target rows against the previously sealed forecasts.

    The caller controls the chronological source-release guarantee. This pure
    function validates identities and finite raw values, retains negative
    readings, fits no target parameter, and evaluates stock independently of
    the kinetic comparison. Target rows are ordinary dictionaries.
    """
    if forecasts['target_later_responses_decoded'] is not False:
        raise ValueError('Expected a target-withheld forecast payload')
    expected = {(p['sample'], p['chamber'], p['time_hours']): p
                for p in forecasts['predictions']}
    observed = {}
    for row in target_observations:
        identity = (row['sample'], row['chamber'], row['time_hours'])
        if identity in observed or identity not in expected:
            raise ValueError('Unexpected or duplicate target identity')
        if not math.isfinite(float(row['absorbance'])):
            raise ValueError('Nonfinite target absorbance')
        observed[identity] = float(row['absorbance'])
    if set(observed) != set(expected) or len(observed) != 56:
        raise ValueError('Expected every frozen later target chamber observation')
    optics, cfg = forecasts['optics'], forecasts['config']
    a, b, dilution = optics['slope'], optics['intercept'], cfg['dilution_factor']
    retained = forecasts['retention_fraction']
    pair_outputs, stock_pairs = [], []
    pair_scores = {name: [] for name in MODELS}
    for baseline in forecasts['baseline_pairs']:
        sample, total0 = baseline['sample'], baseline['total_uM']
        donor, recipient = baseline['donor_chamber'], baseline['recipient_chamber']
        points, raw_donor, raw_recipient = [], [baseline['donor_raw']], [baseline['recipient_raw']]
        for j, time in enumerate(TARGET_TIMES[1:], 1):
            identity_d, identity_a = (sample, donor, time), (sample, recipient, time)
            D, A = observed[identity_d], observed[identity_a]
            cd, ca = dilution * (D - b) / a, dilution * (A - b) / a
            total, contrast = cd + ca, cd - ca
            raw_donor.append(D)
            raw_recipient.append(A)
            models = {}
            for name in MODELS:
                pd = expected[identity_d]['model_concentrations_uM'][name]
                pa = expected[identity_a]['model_concentrations_uM'][name]
                ed, ea = (pd - cd) / total0, (pa - ca) / total0
                models[name] = dict(
                    donor_uM=pd, recipient_uM=pa, contrast_uM=pd - pa,
                    normalized_contrast=(pd - pa) / total0,
                    normalized_contrast_error=(pd - pa - contrast) / total0,
                    normalized_total_error=(pd + pa - total) / total0,
                    normalized_joint_chamber_absolute_error=(abs(ed) + abs(ea)) / 2,
                    normalized_joint_chamber_squared_error=(ed * ed + ea * ea) / 2)
            expected_total = retained ** j * total0
            points.append(dict(
                time_hours=time, sampling_index=j, donor_raw=D, recipient_raw=A,
                donor_uM=cd, recipient_uM=ca, contrast_uM=contrast, total_uM=total,
                normalized_contrast=contrast / total0, expected_total_uM=expected_total,
                total_recovery_ratio=total / expected_total, models=models))
        pair_outputs.append(dict(sample=sample, baseline_total_uM=total0, points=points))
        stock_pairs.append(dict(sample=sample, donor_chamber=donor, recipient_chamber=recipient,
                                times_hours=list(TARGET_TIMES), donor=raw_donor, recipient=raw_recipient))
        for name in MODELS:
            errors = [point['models'][name] for point in points]
            pair_scores[name].append(dict(
                sample=sample,
                primary_contrast_mae=float(np.mean([abs(e['normalized_contrast_error']) for e in errors])),
                normalized_total_mae=float(np.mean([abs(e['normalized_total_error']) for e in errors])),
                normalized_joint_chamber_mae=float(np.mean([
                    e['normalized_joint_chamber_absolute_error'] for e in errors])),
                normalized_joint_chamber_rmse=math.sqrt(float(np.mean([
                    e['normalized_joint_chamber_squared_error'] for e in errors])))))
    scores = {}
    for name, rows in pair_scores.items():
        scores[name] = {metric: float(np.mean([row[metric] for row in rows])) for metric in
                        ('primary_contrast_mae', 'normalized_total_mae', 'normalized_joint_chamber_mae')}
        scores[name]['normalized_joint_chamber_rmse'] = math.sqrt(float(np.mean([
            row['normalized_joint_chamber_rmse'] ** 2 for row in rows])))
        scores[name]['per_pair'] = rows
    gains = {}
    for name in MODELS[1:]:
        baseline_error = scores[name]['primary_contrast_mae']
        improvement = baseline_error - scores['exchange']['primary_contrast_mae']
        pair_improvements = []
        for model_row, exchange_row in zip(pair_scores[name], pair_scores['exchange']):
            gain = model_row['primary_contrast_mae'] - exchange_row['primary_contrast_mae']
            pair_improvements.append(dict(
                sample=model_row['sample'], absolute_difference=gain,
                relative_gain=gain / model_row['primary_contrast_mae']
                if model_row['primary_contrast_mae'] > 0 else None))
        gains[name] = dict(
            absolute_difference=improvement,
            relative_gain=improvement / baseline_error if baseline_error > 0 else None,
            per_pair=pair_improvements,
            pairs_with_positive_difference=sum(row['absolute_difference'] > 0 for row in pair_improvements))
    stock = total_stock_test(stock_pairs, optics, retention_fraction=retained, alpha=cfg['alpha'])
    observations, outside, concentrations = [], [], []
    lower, upper = optics['concentration_support']
    for identity, prediction in expected.items():
        sample, chamber, time = identity
        raw = observed[identity]
        observations.append(dict(sample=sample, chamber=chamber, time_hours=time, absorbance=raw))
        concentration = (raw - b) / a
        concentrations.append(concentration)
        if not lower <= concentration <= upper:
            outside.append(dict(sample=sample, chamber=chamber, time_hours=time,
                                aliquot_concentration_uM=concentration,
                                chamber_concentration_uM=dilution * concentration))
    beats = {name: value['absolute_difference'] > 0 for name, value in gains.items()}
    return dict(
        observations=observations, pairs=pair_outputs, scores=scores, gains=gains,
        total_stock=stock,
        extrapolation=dict(input_count=56, outside_support_count=len(outside),
                           aliquot_concentration_range_uM=[min(concentrations), max(concentrations)],
                           outside_support=outside),
        decision=dict(exchange_beats_each_benchmark=beats,
                      exchange_beats_all_benchmarks=all(beats.values()),
                      target_stock_compatible=stock['passed'], comparison_boundary=0.0),
        target_later_responses_decoded=True)
