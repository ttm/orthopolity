"""Independent arithmetic and optimization for the grain/channel transfer.

No production model is imported. The helper functions can be checked on
synthetic data before the source responses are opened. Real verification is
performed only after the design and forecasts have been frozen.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import brentq, least_squares


ROOT = Path(__file__).resolve().parents[1]


def independent_wall(width, depth, slope, discharge, diameter):
    """Reconstruct Guo with a normalized real-algebra branch.

    The negative-radicand expression is the real part of the complete
    published expression, without taking a complex square root or clipping.
    Vanoni's Lambert-W term is independently found from log(w) + w = log(z).
    """
    values = (width, depth, slope, discharge, diameter)
    if not all(math.isfinite(v) and v > 0 for v in values):
        raise ValueError("Nonpositive or nonfinite hydraulic primitive")
    aspect = width / depth
    radius = 1 / (1 / depth + 2 / width)
    speed = discharge / depth / width
    friction = 9.81 * radius * slope / speed ** 2
    roughness = 15 * depth / diameter
    phi = math.exp(-math.sqrt((aspect / math.pi) ** 3))
    beta = (3 / 4 - math.pi ** -2) / .41
    psi = math.sqrt(2 / aspect) * (
        (math.log(roughness) - 1 - (1 + phi) ** 3 / 12) / .41
        + (1 + math.sqrt(phi)) * (1 + math.sin(math.pi * phi)
                                  / (math.pi * (1 + phi))) / 2)
    norm2 = beta ** 2 + psi ** 2
    scale = norm2 * (1 + aspect / 2) * friction
    b, p = beta / math.sqrt(norm2), psi / math.sqrt(norm2)
    radicand = scale - 1
    numerator = ((b - p * math.sqrt(radicand)) ** 2 if radicand >= 0
                 else b * b + p * p * radicand)
    guo = 1 - numerator / scale
    reynolds = radius * speed / 1e-6
    log_argument = math.log(.224072094) + (math.log(reynolds) - math.log(friction)) / 3
    root = brentq(lambda w: math.log(w) + w - log_argument,
                  1e-100, max(1., log_argument + 1.), xtol=5e-15, rtol=1e-14)
    wall_friction = .018409368 / root ** 2
    return dict(alpha=aspect, radius=radius, velocity=speed,
                friction=friction, reynolds=reynolds,
                relative_roughness=roughness, radicand=radicand, guo=guo,
                radius_factor=1 / (1 + 2 / aspect),
                vanoni_brooks=1 - wall_friction / friction / (1 + aspect / 2))


def independent_shape(corey, settling, sphere_settling, repose_degrees,
                      bed_gradient, density, fluid_density, volume):
    """Compute each drag coefficient from force balance before taking its ratio."""
    if (min(corey, settling, sphere_settling, fluid_density, volume) <= 0
            or density <= fluid_density):
        raise ValueError("Invalid independent grain primitives")
    diameter = (6 * volume / math.pi) ** (1 / 3)
    submerged_force = (density - fluid_density) * volume * 9.81
    projected_area = math.pi * diameter * diameter / 4
    cd = submerged_force / (.5 * fluid_density * projected_area * settling ** 2)
    co = submerged_force / (.5 * fluid_density * projected_area * sphere_settling ** 2)
    mu = math.tan(repose_degrees * math.pi / 180)
    mu0 = math.tan(24 * math.pi / 180)
    if bed_gradient >= min(mu, mu0):
        raise ValueError("Nonpositive resistance to downslope motion")
    cstar = corey * cd / co
    mustar = (mu - bed_gradient) / (mu0 - bed_gradient)
    return dict(cstar=cstar, mustar=mustar, shape=cstar / mustar)


def independent_transport(stress, amplitude, threshold):
    stress = np.asarray(stress, dtype=float)
    excess = np.clip(stress - threshold, 0, None)
    return amplitude * excess * np.sqrt(excess)


def independent_fit(stress, response, weights):
    """Bounded two-parameter least squares from many deterministic starts.

    Scaling keeps numerical tolerances independent of physical flux units.
    Both amplitude and threshold remain optimization variables, unlike the
    production profile search. Return all distinct near-optimal solutions so
    agreement of the objective cannot hide non-identifiable forecasts.
    """
    x, y, w = (np.asarray(a, dtype=float) for a in (stress, response, weights))
    if (x.ndim != 1 or y.shape != x.shape or w.shape != x.shape or len(x) < 3
            or not all(np.isfinite(a).all() for a in (x, y, w))
            or np.any(x <= 0) or np.any(y < 0) or np.any(w <= 0)
            or not np.any(y > 0)):
        raise ValueError("Invalid independent calibration inputs")
    w = w / w.sum()
    xscale, yscale = float(x.max()), float(y.max())
    xn, yn, sw = x / xscale, y / yscale, np.sqrt(w)

    def residual(parameters):
        return sw * (independent_transport(xn, *parameters) - yn)

    def jacobian(parameters):
        a, t = parameters
        excess = np.clip(xn - t, 0, None)
        root = np.sqrt(excess)
        return sw[:, None] * np.column_stack((excess * root, -1.5 * a * root))

    knots = np.unique(np.r_[0., xn])
    starts = np.unique(np.r_[np.linspace(0, .999, 25),
                             knots[:-1], (knots[:-1] + knots[1:]) / 2])
    candidates = []
    for threshold in starts:
        h = independent_transport(xn, 1., threshold)
        norm = float(np.dot(w, h * h))
        amplitude = float(np.dot(w, h * yn)) / norm if norm else 1.
        for multiplier in (.5, 2.):
            fit = least_squares(residual, (max(amplitude * multiplier, 1e-12), threshold),
                                jac=jacobian, bounds=((0., 0.), (np.inf, 1.)),
                                x_scale='jac', ftol=2e-13, xtol=2e-13,
                                gtol=2e-13, max_nfev=3000)
            if not fit.success:
                continue
            a = float(fit.x[0]) * yscale / xscale ** 1.5
            t = float(fit.x[1]) * xscale
            error = independent_transport(x, a, t) - y
            mse = float(np.dot(w, error * error))
            candidates.append(dict(amplitude=a, threshold=t, mse=mse))
    # Treat the constrained zero-threshold solution exactly, rather than
    # relying on a trust-region optimizer's small positive boundary value.
    h0 = independent_transport(xn, 1., 0.)
    a0 = float(np.dot(w, h0 * yn) / np.dot(w, h0 * h0)) * yscale / xscale ** 1.5
    error0 = independent_transport(x, a0, 0.) - y
    candidates.append(dict(amplitude=a0, threshold=0., mse=float(np.dot(w, error0 ** 2))))
    best = min(candidates, key=lambda fit: (fit['mse'], fit['threshold']))
    tolerance = 1e-10 * yscale ** 2
    near = [fit for fit in candidates if fit['mse'] <= best['mse'] + tolerance]
    return {**best, 'starts': len(starts) * 2,
            'successful_fits': len(candidates) - 1,
            'near_optimal_threshold_range': [min(f['threshold'] for f in near),
                                             max(f['threshold'] for f in near)],
            'near_optimal_amplitude_range': [min(f['amplitude'] for f in near),
                                             max(f['amplitude'] for f in near)],
            'active_calibration_count': int(np.count_nonzero(x > best['threshold'])),
            'near_optimal_solutions': near}


def independent_weights(rows):
    kinds = sorted(set(row['grain'] for row in rows))
    counts = {kind: sum(row['grain'] == kind for row in rows) for kind in kinds}
    return np.array([1 / len(kinds) / counts[row['grain']] for row in rows])


def compare_number(actual, expected, comparisons, name, *, rtol=2e-7, atol=2e-11):
    actual, expected = float(actual), float(expected)
    if not all(math.isfinite(v) for v in (actual, expected)):
        raise ValueError(f"Nonfinite verification value: {name}")
    difference = abs(actual - expected)
    if difference > atol + rtol * abs(expected):
        raise ValueError(f"Independent mismatch at {name}: {actual} versus {expected}")
    comparisons.append(dict(path=name, absolute=difference,
                            relative=difference / max(abs(expected), 1e-30)))


def read_csv(path):
    with open(path, newline='') as stream:
        return list(csv.DictReader(stream))


def independent_stress(row, model):
    wall = row['wall']['guo'] if model.startswith('guo') else (
        row['wall']['radius_factor'] if model.startswith('radius') else 1.)
    correction = row['shape'] if model.endswith('shape') else 1.
    return row['H'] * row['S'] / row['rf'] / row['D'] * wall * correction


def check_predictors(rows, base, comparisons):
    """Read grain assays, then recompute all audit arithmetic independently."""
    raw = base / '02_data/source_data'
    batches = {}
    for cohort, suffix in (('narrow', ''), ('wide', '_WF')):
        batches[cohort] = {
            key: {record['']: record for record in read_csv(raw / (key + suffix + '.csv'))}
            for key in ('1_var_density', '2_var_shape', '3_var_ARS',
                        '4_var_settling_velocities', '5_var_VES_settling_velocity')}
    output = []
    for row in rows:
        name, kind = row['id'], 'gb' if row['grain'] == 'sphere' else 'ng'
        batch = batches[row['cohort']]
        density = float(batch['1_var_density'][kind]['total_grain_ro'])
        compare_number(row['density'], density, comparisons, name + '.density')
        compare_number(row['rf'], density / row['fluid_density'] - 1,
                       comparisons, name + '.submerged_density_ratio')
        compare_number(row['D'], float(batch['2_var_shape'][kind]['dn']),
                       comparisons, name + '.diameter')
        hydraulic = independent_wall(*(row[key] for key in ('W', 'H', 'S', 'Q', 'D')))
        for key, value in hydraulic.items():
            compare_number(row['wall'][key], value, comparisons, name + '.wall.' + key)
        shape = independent_shape(
            float(batch['2_var_shape'][kind]['CSF']),
            float(batch['4_var_settling_velocities'][kind]['vel_mean']),
            float(batch['5_var_VES_settling_velocity'][kind]['ws_sphere']),
            float(batch['3_var_ARS'][kind]['mean_angle']), row['bed_gradient'],
            density, row['fluid_density'], float(batch['1_var_density'][kind]['grain_vol']))
        for key, value in shape.items():
            compare_number(row[key], value, comparisons, name + '.' + key)
        scale = density * row['W'] * row['D'] * math.sqrt(9.81 * row['rf'] * row['D'])
        compare_number(row['mass_per_dimensionless_flux'], scale, comparisons, name + '.mass_scale')
        compare_number(row['stress_depth'], row['H'] * row['S'] / row['rf'] / row['D'],
                       comparisons, name + '.stress_depth')
        qualified = hydraulic['radicand'] >= 0 and hydraulic['radius_factor'] <= hydraulic['guo'] <= 1
        if row['qualified_hydraulics'] is not qualified:
            raise ValueError('Independent hydraulic qualification disagrees: ' + name)
        output.append({**row, **shape, 'wall': hydraulic, 'mass_per_dimensionless_flux': scale})
    return output


def independent_observations(rows, base):
    """Read numerical flux only for the explicit row list supplied by the caller."""
    cache, output = {}, []
    for row in rows:
        path = base / '02_data/source_data' / row['raw_file']
        if path not in cache:
            cache[path] = read_csv(path)
        source = cache[path][row['raw_row'] - 2]
        identity_key = 'names' if row['cohort'] == 'narrow' else 'name'
        if source[identity_key] != row['id']:
            raise ValueError('Independent response identity mismatch')
        mass = float(source['mass_flux'])
        if not math.isfinite(mass) or mass < 0:
            raise ValueError('Invalid response; independent verifier never removes rows')
        output.append(dict(id=row['id'], mass_flux=mass,
                           dimensionless_flux=mass / row['mass_per_dimensionless_flux']))
    return output


def check_response_records(actual, expected, comparisons, path):
    if [r['id'] for r in actual] != [r['id'] for r in expected]:
        raise ValueError('Changed response membership: ' + path)
    for a, e in zip(actual, expected):
        for key in ('mass_flux', 'dimensionless_flux'):
            compare_number(a[key], e[key], comparisons, path + '.' + a['id'] + '.' + key)


def check_fit(fit, calibration, model, response_map, new, comparisons, path):
    if fit['calibration_ids'] != [row['id'] for row in calibration]:
        raise ValueError('Changed calibration membership: ' + path)
    x = np.array([independent_stress(row, model) for row in calibration])
    y = np.array([response_map[row['id']] for row in calibration])
    w = independent_weights(calibration)
    for key, values in (('calibration_stress', x), ('calibration_flux', y), ('weights', w)):
        if len(fit[key]) != len(values):
            raise ValueError('Changed fit array length: ' + path + '.' + key)
        for index, (a, e) in enumerate(zip(fit[key], values)):
            compare_number(a, e, comparisons, f'{path}.{key}[{index}]')
    independent = independent_fit(x, y, w)
    for key in ('amplitude', 'threshold'):
        compare_number(fit[key], independent[key], comparisons, path + '.' + key,
                       rtol=2e-5, atol=2e-8)
    compare_number(fit['mse'], independent['mse'], comparisons, path + '.mse',
                   rtol=1e-7, atol=1e-12 * max(float(y.max()) ** 2, 1e-30))
    if 'calibration_rmse' in fit:
        compare_number(fit['calibration_rmse'], math.sqrt(independent['mse']),
                       comparisons, path + '.calibration_rmse')
    if 'active_calibration_count' in fit and fit['active_calibration_count'] != independent['active_calibration_count']:
        raise ValueError('Changed active calibration count: ' + path)
    compare_tree(fit['stress_range'], [float(x.min()), float(x.max())], comparisons,
                 path + '.stress_range')
    if fit['threshold_at_zero'] != (fit['threshold'] == 0.):
        raise ValueError('Incorrect threshold boundary indicator: ' + path)
    profile_locations = sorted(set(max(0., min(float(x.max()), fit['threshold'] + offset * .01 * float(np.ptp(x))))
                                   for offset in (-1., 0., 1.)))
    if len(fit['threshold_profile']) != len(profile_locations):
        raise ValueError('Changed threshold profile locations: ' + path)
    for index, (point, threshold) in enumerate(zip(fit['threshold_profile'], profile_locations)):
        compare_number(point['threshold'], threshold, comparisons, f'{path}.threshold_profile[{index}].threshold')
        column = independent_transport(x, 1., threshold) * np.sqrt(w)
        a = (max(0., float(np.linalg.lstsq(column[:, None], y * np.sqrt(w), rcond=None)[0][0]))
             if np.any(column) else 0.)
        residual = independent_transport(x, a, threshold) - y
        mse = math.fsum(float(weight * error * error) for weight, error in zip(w, residual))
        compare_number(point['amplitude'], a, comparisons, f'{path}.threshold_profile[{index}].amplitude')
        compare_number(point['mse'], mse, comparisons, f'{path}.threshold_profile[{index}].mse')
    xp = np.array([independent_stress(row, model) for row in new])
    near = np.array([independent_transport(xp, item['amplitude'], item['threshold'])
                     for item in independent.pop('near_optimal_solutions')])
    independent['maximum_near_optimal_forecast_spread'] = float(np.ptp(near, axis=0).max()) if len(xp) else 0.
    independent['maximum_near_optimal_forecast_spread_over_calibration_max'] = (
        independent['maximum_near_optimal_forecast_spread'] / float(y.max()))
    return independent


def check_forecasts(actual, new, model, fit_for_row, comparisons, path):
    if [r['id'] for r in actual] != [r['id'] for r in new]:
        raise ValueError('Changed forecast membership: ' + path)
    output = []
    for forecast, row in zip(actual, new):
        fit = fit_for_row(row)
        x = independent_stress(row, model)
        value = float(independent_transport(x, fit['amplitude'], fit['threshold']))
        expected = dict(id=row['id'], grain=row['grain'], stress=x,
                        dimensionless_flux=value, mass_flux=value * row['mass_per_dimensionless_flux'],
                        extrapolates=x < min(fit['calibration_stress']) or x > max(fit['calibration_stress']))
        for key in ('id', 'grain', 'extrapolates'):
            if forecast[key] != expected[key]:
                raise ValueError('Changed forecast field: ' + path + '.' + key)
        for key in ('stress', 'dimensionless_flux', 'mass_flux'):
            compare_number(forecast[key], expected[key], comparisons,
                           path + '.' + row['id'] + '.' + key)
        output.append(expected)
    return output


def independent_score(forecasts, observations, normalization):
    observed = {row['id']: row for row in observations}
    rows = []
    for forecast in forecasts:
        obs = observed[forecast['id']]
        rows.append({**forecast, 'observed_flux': obs['dimensionless_flux'],
                     'observed_mass_flux': obs['mass_flux'],
                     'error': forecast['dimensionless_flux'] - obs['dimensionless_flux'],
                     'mass_error': forecast['mass_flux'] - obs['mass_flux']})
    groups = {}
    for grain in ('sphere', 'gravel'):
        group = [row for row in rows if row['grain'] == grain]
        n = len(group)
        mae = math.fsum(abs(row['error']) for row in group) / n
        groups[grain] = dict(n=n, mae=mae, normalized_mae=mae / normalization,
                             bias=math.fsum(row['error'] for row in group) / n,
                             mass_mae=math.fsum(abs(row['mass_error']) for row in group) / n)
    return dict(rows=rows, groups=groups,
                balanced_mae=math.fsum(group['mae'] for group in groups.values()) / len(groups))


def compare_tree(actual, expected, comparisons, path='result'):
    if isinstance(expected, dict):
        if not isinstance(actual, dict) or set(actual) != set(expected):
            raise ValueError('Changed result fields: ' + path)
        for key, value in expected.items():
            compare_tree(actual[key], value, comparisons, path + '.' + key)
    elif isinstance(expected, list):
        if not isinstance(actual, list) or len(actual) != len(expected):
            raise ValueError('Changed result list: ' + path)
        for index, value in enumerate(expected):
            compare_tree(actual[index], value, comparisons, f'{path}[{index}]')
    elif isinstance(expected, (float, np.floating)):
        compare_number(actual, expected, comparisons, path)
    elif actual != expected:
        raise ValueError('Changed result category: ' + path)


def verify(predictions, base, result=None):
    comparisons = []
    models = {'guo_shape', 'guo_unity', 'radius_shape', 'depth_shape'}
    if (set(predictions['fits']) != {'sphere', 'pooled'}
            or any(set(fits) != models for fits in predictions['fits'].values())
            or set(predictions['material_label']['fits']) != {'sphere', 'gravel'}):
        raise ValueError('Changed declared model/calibration families')
    rows = check_predictors(predictions['predictor_audit']['rows'], base, comparisons)
    old = [row for row in rows if row['cohort'] == 'narrow']
    new = [row for row in rows if row['cohort'] == 'wide']
    observed_old = independent_observations(old, base)
    check_response_records(predictions['calibration_responses'], observed_old, comparisons, 'calibration')
    responses = {row['id']: row['dimensionless_flux'] for row in observed_old}
    normalized_by = max(responses[row['id']] for row in old if row['grain'] == 'sphere')
    compare_number(predictions['normalization'], normalized_by, comparisons, 'normalization')
    diagnostics, forecasts = {}, {}
    for family in ('sphere', 'pooled'):
        calibration = [row for row in old if family == 'pooled' or row['grain'] == 'sphere']
        diagnostics[family], forecasts[family] = {}, {}
        for model, fit in predictions['fits'][family].items():
            diagnostics[family][model] = check_fit(fit, calibration, model, responses, new,
                                                  comparisons, family + '.' + model)
            forecasts[family][model] = check_forecasts(fit['forecasts'], new, model, lambda row: fit,
                                                      comparisons, family + '.' + model + '.forecasts')
    diagnostics['material_label'] = {}
    for grain, fit in predictions['material_label']['fits'].items():
        diagnostics['material_label'][grain] = check_fit(
            fit, [row for row in old if row['grain'] == grain], 'guo_unity', responses,
            [row for row in new if row['grain'] == grain], comparisons, 'material_label.' + grain)
    label_forecasts = check_forecasts(
        predictions['material_label']['forecasts'], new, 'guo_unity',
        lambda row: predictions['material_label']['fits'][row['grain']], comparisons, 'material_label.forecasts')
    decision = None
    if result is not None:
        if any(result[key] != predictions[key] for key in ('study', 'design_commit')):
            raise ValueError('Result and forecast provenance disagree')
        compare_number(result['normalization'], normalized_by, comparisons, 'result.normalization')
        observed_new = independent_observations(new, base)
        check_response_records(result['observations'], observed_new, comparisons, 'observations')
        scores = {family: {model: independent_score(values, observed_new, normalized_by)
                           for model, values in model_values.items()}
                  for family, model_values in forecasts.items()}
        scores['material_label'] = independent_score(label_forecasts, observed_new, normalized_by)
        compare_tree(result['scores'], scores, comparisons, 'scores')
        full = scores['sphere']['guo_shape']
        gains = {model: 1 - full['balanced_mae'] / score['balanced_mae'] if score['balanced_mae'] else None
                 for model, score in scores['sphere'].items() if model != 'guo_shape'}
        compare_tree(result['primary_relative_gains'], gains, comparisons, 'primary_relative_gains')
        config = predictions['config']
        primary_fit = diagnostics['sphere']['guo_shape']
        adequate = (primary_fit['active_calibration_count'] >= 3
                    and math.sqrt(primary_fit['mse']) / normalized_by <= config['maximum_normalized_mae'])
        accurate = adequate and all(group['normalized_mae'] <= config['maximum_normalized_mae']
                                    for group in full['groups'].values())
        decision = dict(calibration_adequate=adequate, pragmatic_accuracy=accurate,
                        shape_advantage=accurate and gains['guo_unity'] is not None
                            and gains['guo_unity'] >= config['minimum_relative_gain'],
                        geometry_advantage=accurate and gains['radius_shape'] is not None
                            and gains['radius_shape'] >= config['minimum_relative_gain'])
        compare_tree(result['decision'], decision, comparisons, 'decision')
    return dict(study='grain-channel-independent-verification-2026-10-15',
                status='passed', checked_numbers=len(comparisons),
                maximum_absolute_difference=max(item['absolute'] for item in comparisons),
                maximum_relative_difference=max(item['relative'] for item in comparisons),
                optimization_diagnostics=diagnostics, decision=decision,
                scope='Independent real-algebra hydraulics, force-balance drag ratio, multi-start two-parameter fitting, forecasts and optional source-response scores. Archived sphere-settling speed is a frozen input, not independently rederived.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--predictions', type=Path, required=True)
    parser.add_argument('--result', type=Path)
    parser.add_argument('--base', type=Path, default=ROOT / 'data/grain-channel/2026-10-15')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    predictions = json.loads(args.predictions.read_text())
    result = json.loads(args.result.read_text()) if args.result else None
    prediction_sha = hashlib.sha256(args.predictions.read_bytes()).hexdigest()
    if result is not None and result.get('prediction_sha256') != prediction_sha:
        raise ValueError('Evaluated prediction hash differs from supplied forecast file')
    verified = verify(predictions, args.base, result)
    verified['prediction_sha256'] = prediction_sha
    if args.result:
        verified['result_sha256'] = hashlib.sha256(args.result.read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(verified, indent=2, sort_keys=True, allow_nan=False) + '\n')
    print(json.dumps({key: verified[key] for key in ('status', 'checked_numbers', 'maximum_relative_difference')}))
