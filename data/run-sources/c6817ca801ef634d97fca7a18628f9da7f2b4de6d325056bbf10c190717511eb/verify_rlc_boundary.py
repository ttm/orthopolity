"""Independent RLC forecast/result verifier; never reads original responses.

Forecasts are checked by solving physical two-state harmonic equations,
crossings by roots of admittance susceptance, and errors by explicit
log-frequency trapezoids. No production analysis functions are imported.
The optional result file must have been released by the frozen workflow.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import brentq


ROOT = Path(__file__).resolve().parents[1]


def impedance(frequency, resistance, inductance, capacitance):
    """Solve C Vdot=Iin-IL; L ILdot=V-R IL, with unit port current."""
    omega = 2*math.pi*frequency
    system = np.array([[1j*omega*capacitance, 1.],
                       [-1., resistance+1j*omega*inductance]], dtype=complex)
    voltage, inductor_current = np.linalg.solve(system, [1., 0.])
    residual = system @ np.array([voltage, inductor_current]) - np.array([1., 0.])
    if np.max(np.abs(residual)) > 1e-10:
        raise AssertionError('Two-state harmonic equations not satisfied')
    return complex(voltage)


def admittance_crossing(resistance, inductance, capacitance):
    def divided_susceptance(omega):
        if omega == 0:
            return capacitance - inductance/resistance**2
        admittance = 1/(resistance+1j*omega*inductance) + 1j*omega*capacitance
        return admittance.imag/omega
    if divided_susceptance(0) >= 0:
        raise AssertionError('No strictly positive inductive band')
    root = brentq(divided_susceptance, 0., 2/math.sqrt(inductance*capacitance),
                  xtol=1e-11, rtol=1e-14)
    return root/(2*math.pi)


def component_ranges(config):
    l = config['inductance_henry']
    c = config['capacitance_farad']
    dl = config['inductance_fractional_tolerance']
    dc = config['capacitance_fractional_tolerance']
    return (l*(1-dl), l*(1+dl)), (c*(1-dc), c*(1+dc))


def crossing_envelope(config, resistance):
    lr, cr = component_ranges(config)
    # d(f_cross²)/dL<0 exactly when L>2R²C; d/dC is always negative.
    if lr[0] <= 2*resistance**2*cr[1]:
        raise AssertionError('Advertised corner monotonicity does not hold')
    corners = [admittance_crossing(resistance, l, c) for l in lr for c in cr]
    low, high = min(corners), max(corners)
    for i in range(17):
        for j in range(17):
            l = lr[0]+(lr[1]-lr[0])*i/16
            c = cr[0]+(cr[1]-cr[0])*j/16
            f = admittance_crossing(resistance, l, c)
            if not low-1e-9 <= f <= high+1e-9:
                raise AssertionError('Interior crossing outside corner envelope')
    return [low, high]


def separated_sign(frequency, interval):
    if frequency < interval[0]:
        return 1
    if frequency > interval[1]:
        return -1
    return 0


def check_numeric(actual, expected, stats, label):
    if not math.isclose(float(actual), float(expected), rel_tol=1e-10, abs_tol=1e-9):
        raise AssertionError(f'Independent check failed: {label}')
    stats['numerical_comparisons'] += 1
    stats['maximum_absolute_difference'] = max(
        stats['maximum_absolute_difference'], abs(float(actual)-float(expected)))


def verify_prediction(prediction, stats):
    config = prediction['config']
    resistance = config['resistance_ohm']
    inductance = config['inductance_henry']
    capacitance = config['capacitance_farad']
    nominal = admittance_crossing(resistance, inductance, capacitance)
    envelope = crossing_envelope(config, resistance)
    alternative = crossing_envelope(config, config['alternative_resistance_ohm'])
    union = [min(envelope[0], alternative[0]), max(envelope[1], alternative[1])]
    check_numeric(nominal, prediction['crossing_hz_nominal'], stats, 'nominal crossing')
    for name, expected in [('crossing_hz_interval', envelope),
                           ('crossing_hz_unit_union', union)]:
        if len(prediction[name]) != 2:
            raise AssertionError('Unexpected interval length')
        for i in range(2):
            check_numeric(expected[i], prediction[name][i], stats, f'{name}[{i}]')
    rows = prediction['rows']
    if len(rows) != config['expected_rows'] or sorted(row['row'] for row in rows) != list(range(len(rows))):
        raise AssertionError('Forecast row inventory differs')
    frequencies = [row['frequency_hz'] for row in rows]
    if len(set(frequencies)) != len(frequencies) or any(f <= 0 or not math.isfinite(f) for f in frequencies):
        raise AssertionError('Invalid forecast frequencies')
    for observed, expected in zip([min(frequencies), max(frequencies)], config['frequency_range_hz']):
        if abs(observed/expected-1) > config['frequency_relative_tolerance']:
            raise AssertionError('Unexpected frequency range')
    for row in rows:
        value = impedance(row['frequency_hz'], resistance, inductance, capacitance)
        check_numeric(value.real, row['real_ohm'], stats, f'row {row["row"]} real')
        check_numeric(value.imag, row['imag_ohm'], stats, f'row {row["row"]} imaginary')
        for name, interval in [('sign_table_s3', envelope), ('sign_unit_union', union)]:
            if row[name] != separated_sign(row['frequency_hz'], interval):
                raise AssertionError(f'Independent sign classification differs: {name}')
    return envelope, union


def integrated_squared(values, frequencies):
    """Unnormalized trapezoid integral; its common normalization cancels."""
    terms = []
    for i in range(len(values)-1):
        dx = math.log(frequencies[i+1])-math.log(frequencies[i])
        if dx <= 0:
            raise AssertionError('Integration frequencies not strictly increasing')
        terms.append(.5*dx*(values[i]+values[i+1]))
    return math.fsum(terms)


def independent_scores(observations, config):
    ordered = sorted(observations, key=lambda row: row['frequency_hz'])
    frequencies = [row['frequency_hz'] for row in ordered]
    observed = [complex(row['real_ohm'], row['imag_ohm']) for row in ordered]
    if len(observed) < 2:
        raise AssertionError('Too few observations for quadrature')
    denominator = integrated_squared([abs(value)**2 for value in observed], frequencies)
    if denominator <= 0:
        raise AssertionError('Zero observed impedance norm')
    numerators = {'rc_relative_rms_lower_bound': [max(value.imag, 0)**2 for value in observed]}
    for name, resistance in [('rlc_relative_rms', config['resistance_ohm']),
                             ('alternative_resistance_relative_rms', config['alternative_resistance_ohm'])]:
        predicted = [impedance(f, resistance, config['inductance_henry'], config['capacitance_farad'])
                     for f in frequencies]
        numerators[name] = [abs(a-b)**2 for a, b in zip(predicted, observed)]
    return {name: math.sqrt(integrated_squared(values, frequencies)/denominator)
            for name, values in numerators.items()}


def independent_signs(observations, interval):
    ordered = sorted(observations, key=lambda row: row['frequency_hz'])
    actual = [1 if row['imag_ohm'] > 0 else -1 if row['imag_ohm'] < 0 else 0
              for row in ordered]
    predicted = [separated_sign(row['frequency_hz'], interval) for row in ordered]
    errors = [row['row'] for row, a, p in zip(ordered, actual, predicted) if p and a != p]
    brackets = []
    for left, right, a, b in zip(ordered[:-1], ordered[1:], actual[:-1], actual[1:]):
        if a*b == -1:
            brackets.append(dict(low_hz=left['frequency_hz'], high_hz=right['frequency_hz'],
                                 from_sign=a, to_sign=b))
    zeros = [row['frequency_hz'] for row, sign in zip(ordered, actual) if not sign]
    compatible = False
    if len(brackets) == 1 and not zeros:
        bracket = brackets[0]
        compatible = (bracket['from_sign'] == 1 and bracket['to_sign'] == -1
                      and max(bracket['low_hz'], interval[0]) <= min(bracket['high_hz'], interval[1]))
    classified = sum(p != 0 for p in predicted)
    return dict(classified=classified, unclassified=len(ordered)-classified,
                agreements=classified-len(errors), disagreement_rows=errors,
                all_classified_signs_agree=not errors, brackets=brackets,
                exact_zero_hz=zeros, single_crossing_bracket_intersects_interval=compatible)


def verify_result(result, prediction, prediction_bytes, stats):
    if result['forecast_sha256'] != hashlib.sha256(prediction_bytes).hexdigest():
        raise AssertionError('Result references a different forecast')
    observations = result['observations']
    forecasts = {row['row']: row for row in prediction['rows']}
    if len(observations) != len(forecasts) or set(row['row'] for row in observations) != set(forecasts):
        raise AssertionError('Released observation inventory differs')
    for row in observations:
        check_numeric(row['frequency_hz'], forecasts[row['row']]['frequency_hz'], stats,
                      f'observation frequency {row["row"]}')
        if any(not math.isfinite(row[key]) for key in ('real_ohm', 'imag_ohm')):
            raise AssertionError('Nonfinite released impedance')
    excluded = set(prediction['config']['previously_exposed_zero_based_rows'])
    subsets = {'primary': [row for row in observations if row['row'] not in excluded],
               'all_rows': observations}
    for label, subset in subsets.items():
        scores = independent_scores(subset, prediction['config'])
        for name, value in scores.items():
            check_numeric(value, result[label][name], stats, f'{label}.{name}')
        ordered = sorted(subset, key=lambda row: row['frequency_hz'])
        positive = [row['imag_ohm'] for row in subset if row['imag_ohm'] > 0]
        expected = dict(count=len(subset), row_indices=[row['row'] for row in ordered],
            positive_imaginary_count=len(positive),
            positive_imaginary_fraction=len(positive)/len(subset),
            positive_imaginary_range_ohm=[min(positive), max(positive)] if positive else None,
            rlc_error_below_rc_lower_bound=scores['rlc_relative_rms'] < scores['rc_relative_rms_lower_bound'])
        for key, value in expected.items():
            if result[label][key] != value:
                raise AssertionError(f'Independent report differs: {label}.{key}')
        for name, interval in [('table_s3', prediction['crossing_hz_interval']),
                               ('unit_union', prediction['crossing_hz_unit_union'])]:
            if result[label]['signs'][name] != independent_signs(subset, interval):
                raise AssertionError(f'Independent sign report differs: {label}.{name}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prediction', type=Path, required=True)
    parser.add_argument('--result', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    prediction_bytes = args.prediction.read_bytes()
    prediction = json.loads(prediction_bytes)
    stats = {'numerical_comparisons': 0, 'maximum_absolute_difference': 0.}
    envelope, union = verify_prediction(prediction, stats)
    result = None
    if args.result is not None:
        result = json.loads(args.result.read_text())
        verify_result(result, prediction, prediction_bytes, stats)
    output = {'passed': True, 'stage': 'result' if result is not None else 'prediction',
              'design_commit': prediction['design_commit'],
              'forecast_sha256': hashlib.sha256(prediction_bytes).hexdigest(),
              'raw_source_files_read': False, 'production_analysis_imported': False,
              'forecast_method': 'two-state harmonic linear solve',
              'crossing_method': 'admittance susceptance roots; monotonicity and 17x17 interior checks',
              'error_method': 'explicit log-frequency trapezoid loops',
              'relative_tolerance': 1e-10, 'absolute_tolerance': 1e-9,
              'crossing_hz_interval': envelope, 'crossing_hz_unit_union': union, **stats}
    if args.result is not None:
        output['result_sha256'] = hashlib.sha256(args.result.read_bytes()).hexdigest()
        output['forecast_commit'] = result['forecast_commit']
    serialized = json.dumps(output, indent=2, allow_nan=False)+'\n'
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized)
    print(serialized, end='')


if __name__ == '__main__':
    main()
