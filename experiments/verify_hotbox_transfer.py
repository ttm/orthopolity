"""Independently verify sealed hotbox forecasts without opening the archive.

The supplied input summaries are the only numerical observations consumed.
This checks summary-to-forecast arithmetic and qualification, not extraction of
the summaries from the original data. Exact decimal-rational corner arithmetic,
pairwise interval-order feasibility and a separate convex-combination envelope
avoid importing the production runner. No target interior values are read.
"""

import argparse
from fractions import Fraction
import hashlib
import itertools
import json
import math
from pathlib import Path


SUMMARY_FIELDS = {'case', 'position', 'sensor', 'mean_c', 'min_c', 'max_c', 'drift_c'}
ROW_FIELDS = {
    'case', 'position', 'sensor', 'calibration_beta', 'calibration_beta_interval',
    'calibration_monotone', 'geometry_beta', 'geometry_prediction_c',
    'transfer_prediction_c', 'persistence_prediction_c', 'additive_prediction_c',
    'transfer_observation_interval_c', 'geometry_observation_interval_c',
    'input_qualified',
}


class Checks:
    def __init__(self):
        self.numeric = 0
        self.logical = 0
        self.maximum = 0.0

    def equal(self, actual, expected, label):
        if isinstance(expected, (list, tuple)):
            if not isinstance(actual, (list, tuple)) or len(actual) != len(expected):
                raise ValueError('Wrong array shape: ' + label)
            for i, (a, b) in enumerate(zip(actual, expected)):
                self.equal(a, b, f'{label}[{i}]')
        elif isinstance(expected, (int, float, Fraction)) and not isinstance(expected, bool):
            if isinstance(actual, bool) or not isinstance(actual, (int, float)):
                raise ValueError('Wrong numeric type: ' + label)
            a, b = float(actual), float(expected)
            if not math.isfinite(a) or not math.isfinite(b):
                raise ValueError('Nonfinite number: ' + label)
            difference = abs(a-b)
            self.numeric += 1
            self.maximum = max(self.maximum, difference)
            if difference > 1e-10 + 1e-11*abs(b):
                raise ValueError('Independent numerical mismatch: ' + label)
        else:
            self.logical += 1
            if type(actual) is not type(expected) or actual != expected:
                raise ValueError('Independent logical mismatch: ' + label)


def rational(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError('Expected a finite numeric input')
    return Fraction(str(value))


def valid_hash(value, length):
    return (isinstance(value, str) and len(value) == length
            and all(c in '0123456789abcdef' for c in value))


def order_feasible(means, radius):
    """Pairwise characterization, independent of the runner's greedy witness.

For descending intervals, feasibility fails exactly when a later interval's
lower endpoint exceeds an earlier interval's upper endpoint.
"""
    return all(means[j]-radius <= means[i]+radius
               for i in range(len(means)) for j in range(i+1, len(means)))


def calibrated_fraction_bounds(hot, cold, interior, radius):
    """Linear-fractional extrema over a box with positive denominator.

Each coordinate is fractional-linear with derivative of constant sign while
the others are fixed, so a minimum and maximum occur among the eight corners.
The physical [0, 1] restriction is imposed only on the interval, never the
unclipped nominal point forecast.
"""
    corners = []
    for signs in itertools.product((-1, 1), repeat=3):
        a, b, m = (v+s*radius for v, s in zip((hot, cold, interior), signs))
        if a <= b:
            raise ValueError('Unqualified calibration denominator')
        corners.append((m-b)/(a-b))
    low, high = max(Fraction(0), min(corners)), min(Fraction(1), max(corners))
    return (low, high) if low <= high else None


def predicted_observation_bounds(hot, cold, beta, radius):
    """Convexity reduces eight prediction corners to two nominal mixtures.

For beta in [0, 1], the bounded two-anchor error contributes exactly radius;
the independently observed target adds another radius. No assumption about
independence or a reduction by sample count is made.
"""
    if beta is None:
        return None
    endpoints = [cold+b*(hot-cold) for b in beta]
    return [min(endpoints)-2*radius, max(endpoints)+2*radius]


def verify(prediction):
    checks = Checks()
    cfg = prediction['config']
    # This verifier is specific to the registered split and sensor map. A
    # changed design requires explicit review rather than silently accepting a
    # configuration that uses target channels as calibration inputs.
    fixed = {
        'calibration_case': 6, 'control_case': 7,
        'target_cases': [1, 2, 3, 4, 5], 'positions': list(range(1, 16)),
        'anchors': ['c', 'g'], 'interior': ['d', 'e', 'f'],
        'sensor_error_c': 0.15, 'internal_calibration_range_c': [-10, 50],
        'maximum_window_drift_c': 0.30, 'expected_rows': 181,
        'expected_columns': 136, 'drift_window_rows': 60,
        'time_step_seconds': 60,
    }
    for key, value in fixed.items():
        checks.equal(cfg[key], value, 'config.'+key)
    for sensor, millimetres in zip('cdefg', (69, 125, 182, 239, 296)):
        checks.equal(cfg['depth_m'][sensor], Fraction(millimetres, 1000), 'depth.'+sensor)
    if set(cfg['depth_m']) != set('cdefg'):
        raise ValueError('Unexpected depth map')
    if not valid_hash(cfg['source_sha256'], 64):
        raise ValueError('Invalid source SHA-256')
    if not valid_hash(prediction['design_commit'], 40):
        raise ValueError('Invalid frozen design commit')
    checks.equal(prediction['target_interior_temperatures_decoded'], False,
                 'target_interior_temperatures_decoded')

    expected_inputs = {(case, p, s) for case in (6, 7) for p in range(1, 16) for s in 'cdefg'}
    expected_inputs.update((case, p, s) for case in range(1, 6)
                           for p in range(1, 16) for s in 'cg')
    inputs = {}
    for row in prediction['input_summary']:
        if not isinstance(row, dict) or set(row) != SUMMARY_FIELDS:
            raise ValueError('Unexpected input-summary fields')
        if type(row['case']) is not int or type(row['position']) is not int:
            raise ValueError('Input identifiers must be integers')
        key = row['case'], row['position'], row['sensor']
        if key not in expected_inputs or key in inputs:
            raise ValueError('Unexpected or duplicate input identity')
        for name in ('mean_c', 'min_c', 'max_c', 'drift_c'):
            rational(row[name])
        if not row['min_c'] <= row['mean_c'] <= row['max_c']:
            raise ValueError('Input mean outside reported range')
        if abs(row['drift_c']) > row['max_c']-row['min_c']+1e-10:
            raise ValueError('Input window drift exceeds the full range')
        inputs[key] = row
    if set(inputs) != expected_inputs:
        raise ValueError('Incomplete permitted-input partition')
    checks.equal(prediction['numeric_temperature_cells'], 300*181,
                 'numeric_temperature_cells')

    def qualified(row):
        low, high = cfg['internal_calibration_range_c']
        radius = cfg['sensor_error_c']
        return (row['min_c']-radius >= low and row['max_c']+radius <= high
                and abs(row['drift_c']) <= cfg['maximum_window_drift_c'])

    rows = prediction['predictions']
    identities = [(case, p, s) for case in range(1, 6)
                  for p in range(1, 16) for s in 'def']
    if len(rows) != len(identities):
        raise ValueError('Expected 225 complete target forecasts')
    radius = rational(cfg['sensor_error_c'])
    for row, identity in zip(rows, identities):
        if not isinstance(row, dict) or set(row) != ROW_FIELDS:
            raise ValueError('Unexpected forecast fields')
        case, p, sensor = identity
        label = f'forecast[{case},{p},{sensor}]'
        for name, expected in zip(('case', 'position', 'sensor'), identity):
            checks.equal(row[name], expected, label+'.'+name)
        cal = [inputs[(6, p, s)] for s in 'cdefg']
        means = [r['mean_c'] for r in cal]
        if means[0]-means[-1] <= 2*cfg['sensor_error_c']:
            raise ValueError('Calibration denominator should have stopped the forecast')
        monotone = order_feasible(means, cfg['sensor_error_c'])
        hot0, cold0 = rational(means[0]), rational(means[-1])
        interior0 = rational(inputs[(6, p, sensor)]['mean_c'])
        hotrow, coldrow = inputs[(case, p, 'c')], inputs[(case, p, 'g')]
        hot, cold = rational(hotrow['mean_c']), rational(coldrow['mean_c'])
        beta = (interior0-cold0)/(hot0-cold0)
        fraction = calibrated_fraction_bounds(hot0, cold0, interior0, radius) if monotone else None
        # Integer millimetres express the geometry independently of decimal
        # subtraction of the production depth map.
        geometry = Fraction({'d': 171, 'e': 114, 'f': 57}[sensor], 227)
        geometric_prediction = cold+geometry*(hot-cold)
        additive_prediction = (geometric_prediction+interior0
                               -cold0-geometry*(hot0-cold0))
        expected = {
            'calibration_beta': beta,
            'calibration_beta_interval': fraction,
            'calibration_monotone': monotone,
            'geometry_beta': geometry,
            'geometry_prediction_c': geometric_prediction,
            'transfer_prediction_c': cold+beta*(hot-cold),
            'persistence_prediction_c': interior0,
            'additive_prediction_c': additive_prediction,
            'transfer_observation_interval_c': predicted_observation_bounds(hot, cold, fraction, radius),
            'geometry_observation_interval_c': [geometric_prediction-2*radius,
                                                geometric_prediction+2*radius],
            'input_qualified': monotone and all(qualified(r) for r in cal+[hotrow, coldrow]),
        }
        for name, value in expected.items():
            checks.equal(row[name], value, label+'.'+name)
    return {
        'numeric_checks': checks.numeric,
        'logical_checks': checks.logical,
        'maximum_absolute_difference': checks.maximum,
        'source_sha256': cfg['source_sha256'],
        'input_summaries_checked': len(inputs),
        'prediction_rows_checked': len(rows),
        'source_archive_opened': False,
        'target_interior_temperatures_decoded': False,
        'input_summary_extraction_independently_verified': False,
        'independent_methods': ['Exact decimal-rational calibration-box vertices',
                                'Pairwise interval-order feasibility',
                                'Integer-millimetre geometry',
                                'Convex anchor-error envelope'],
        'scope': 'Summary-to-forecast arithmetic and qualification; marginal conditional bounds only',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prediction', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    raw = args.prediction.read_bytes()
    report = verify(json.loads(raw))
    report['prediction_sha256'] = hashlib.sha256(raw).hexdigest()
    report['verification_source_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as stream:
        json.dump(report, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')
    print(json.dumps(report, sort_keys=True))


if __name__ == '__main__':
    main()
