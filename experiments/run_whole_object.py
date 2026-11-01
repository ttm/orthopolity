"""Analytic forecasts and later kinetic checks for whole-object assembly.

The forecast uses direct integer enumeration and rational detailed-balance
weights. Kinetic state discovery, linear solves and event simulation are in a
separate module. Simulation checks mathematical implementation, not nature.
"""
import argparse
from fractions import Fraction
import hashlib
import json
from math import factorial, log, sqrt
from pathlib import Path

import numpy as np
from scipy.linalg import expm

from orthopolity.whole_object_kinetics import generator, generator_stationary

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / 'configs/whole_object_2026-10-31.json'
SOURCES = ['experiments/run_whole_object.py', 'src/orthopolity/whole_object_kinetics.py']


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def analytic_law(budget, mechanism, forward=(1, 1), reverse=(1, 1)):
    """Stationary law from reaction-wise detailed balance, with exact weights."""
    if isinstance(budget, bool) or not isinstance(budget, int) or budget <= 0:
        raise ValueError('Budget must be a positive integer')
    if mechanism not in ('channel', 'mass_action'):
        raise ValueError('Unknown mechanism')
    for values in (forward, reverse):
        if (len(values) != 2 or any(isinstance(x, (bool, np.bool_)) for x in values)
                or not np.isfinite(values).all() or min(values) <= 0):
            raise ValueError('Two positive finite rates are required in each direction')
    ratios = [Fraction(str(a)) / Fraction(str(b)) for a, b in zip(forward, reverse)]
    # Direct lattice enumeration, independent of kinetic graph traversal.
    states = sorted((budget - 2*d - 4*t, d, t)
                    for t in range(budget // 4 + 1)
                    for d in range((budget - 4*t) // 2 + 1))
    weights = []
    for mono, dimer, tetramer in states:
        value = ratios[0] ** (dimer + 2*tetramer) * ratios[1] ** tetramer
        if mechanism == 'mass_action':
            value /= factorial(mono) * factorial(dimer) * factorial(tetramer)
        weights.append(value)
    total = sum(weights)
    probabilities = [value / total for value in weights]
    means = [sum(p*n[j] for p, n in zip(probabilities, states)) for j in range(3)]
    shares = [means[j]*q/budget for j, q in enumerate((1, 2, 4))]
    second = [[sum(p*Fraction(n[i]*qi*n[j]*qj, budget**2)
                   for p, n in zip(probabilities, states))
               for j, qj in enumerate((1, 2, 4))] for i, qi in enumerate((1, 2, 4))]
    covariance = [[second[i][j] - shares[i]*shares[j] for j in range(3)] for i in range(3)]
    return states, probabilities, means, shares, covariance


def moments(states, probabilities, budget):
    shares = np.asarray(states, dtype=float) * np.array([1, 2, 4]) / budget
    p = np.asarray(probabilities, dtype=float)
    mean = p @ shares
    centered = shares - mean
    return mean, (centered.T * p) @ centered


def forecast(config_path):
    config = json.loads(Path(config_path).read_text())
    budget = config['budget']
    if config['costs'] != [1, 2, 4]:
        raise ValueError('This reaction network has fixed costs 1, 2, 4')
    cases = []
    for case in config['cases']:
        mechanism, forward, reverse = case['mechanism'], case['forward'], case['reverse']
        states, exact, counts, shares, covariance = analytic_law(budget, mechanism, forward, reverse)
        kinetic_states, matrix = generator(budget, mechanism, forward, reverse)
        if list(map(tuple, kinetic_states)) != states:
            raise AssertionError('Independent state enumerations disagree')
        _, initial, _, _, _ = analytic_law(budget, mechanism)
        p0 = np.array([float(p) for p in initial])
        endpoint = expm(matrix * config['duration']) @ p0
        if abs(endpoint.sum() - 1) > 1e-11 or endpoint.min() < -1e-13:
            raise AssertionError('Invalid finite-time probability prediction')
        mean, cov = moments(states, endpoint, budget)
        cases.append({
            **case, 'state_count': len(states), 'states': states,
            'stationary_probabilities': [float(p) for p in exact],
            'stationary_mean_counts': [float(x) for x in counts],
            'stationary_exact_mean_shares': [str(x) for x in shares],
            'stationary_mean_shares': [float(x) for x in shares],
            'stationary_share_covariance': [[float(x) for x in row] for row in covariance],
            'initial_probabilities': p0.tolist(),
            'finite_time_probabilities': endpoint.tolist(),
            'finite_time_mean_shares': mean.tolist(),
            'finite_time_share_covariance': cov.tolist(),
        })
    asymptotic = []
    for b in config['asymptotic_budgets']:
        if b % 4:
            raise ValueError('Closed-form comparison budgets must be multiples of four')
        states, _, _, shares, covariance = analytic_law(b, 'channel')
        m = b // 4
        formula = [Fraction(1, 3) + Fraction(1, 12*(m+1))] * 2
        formula.append(Fraction(1, 3) - Fraction(1, 6*(m+1)))
        if len(states) != (m+1)**2 or shares != formula:
            raise AssertionError('Enumeration disagrees with independent finite-budget formula')
        asymptotic.append({'budget': b, 'states': len(states),
                           'mean_shares': [float(x) for x in shares],
                           'share_covariance': [[float(x) for x in row] for row in covariance]})
    dimension = 3 * len(cases)
    bound = sqrt(log(2*dimension/config['family_error_bound']) / (2*config['replicates']))
    return {
        'kind': config['kind'], 'config_sha256': sha256(config_path),
        'source_sha256': {name: sha256(ROOT / name) for name in SOURCES},
        'reference_measure': config['reference_measure'],
        'budget': budget, 'duration': config['duration'], 'replicates': config['replicates'],
        'seed': config['seed'], 'initialization': config['initialization'],
        'family_error_bound': config['family_error_bound'],
        'simultaneous_mean_absolute_tolerance': bound,
        'tolerance_basis': 'Hoeffding union bound over all case/class bounded share means; independence across replicates, not across classes',
        'asymptotic_channel': asymptotic,
        'limiting_share_covariance': [[1/18 if i == j else -1/36 for j in range(3)] for i in range(3)],
        'cases': cases,
    }


def verify(prediction_path, config_path):
    """Independent generator checks plus Gillespie paths, after forecast freeze."""
    from orthopolity.whole_object_kinetics import gillespie_endpoints

    prediction = json.loads(Path(prediction_path).read_text())
    if prediction['config_sha256'] != sha256(config_path):
        raise AssertionError('Configuration differs from frozen prediction')
    for name, expected_hash in prediction['source_sha256'].items():
        if sha256(ROOT / name) != expected_hash:
            raise AssertionError(f'Implementation differs from frozen prediction: {name}')
    budget, duration = prediction['budget'], prediction['duration']
    replicates = prediction['replicates']
    children = np.random.SeedSequence(prediction['seed']).spawn(len(prediction['cases']))
    records = []
    for case, seed in zip(prediction['cases'], children):
        states, matrix = generator(budget, case['mechanism'], case['forward'], case['reverse'])
        expected = np.array(case['stationary_probabilities'])
        if list(map(tuple, states)) != list(map(tuple, case['states'])):
            raise AssertionError('Frozen state indexing differs')
        solved = generator_stationary(matrix)
        flux = matrix * expected[None, :]
        balance_error = float(abs(flux - flux.T).max())
        stationary_error = float(abs(solved - expected).max())
        if balance_error > 1e-11 or stationary_error > 1e-11:
            raise AssertionError('Analytic law disagrees with kinetic generator')
        rng = np.random.default_rng(seed)
        initial_indices = rng.choice(len(states), size=replicates, p=case['initial_probabilities'])
        initial = np.array(states)[initial_indices]
        final, events = gillespie_endpoints(initial, duration, case['mechanism'],
                                            case['forward'], case['reverse'], rng=rng)
        if not np.all(final @ np.array([1, 2, 4]) == budget):
            raise AssertionError('Whole-object trajectories lost resource')
        observed = final.mean(axis=0) * np.array([1, 2, 4]) / budget
        errors = abs(observed - case['finite_time_mean_shares'])
        lookup = {tuple(s): j for j, s in enumerate(states)}
        histogram = np.bincount([lookup[tuple(n)] for n in final], minlength=len(states))/replicates
        state_tv = float(.5 * abs(histogram - case['finite_time_probabilities']).sum())
        passed = bool(np.all(errors <= prediction['simultaneous_mean_absolute_tolerance']))
        records.append({'name': case['name'], 'replicates': replicates,
                        'events': int(np.sum(events)), 'maximum_events_per_replicate': int(np.max(events)),
                        'observed_mean_shares': observed.tolist(),
                        'absolute_mean_errors': errors.tolist(),
                        'whole_state_total_variation_descriptive': state_tv,
                        'maximum_detailed_balance_error': balance_error,
                        'maximum_stationary_linear_solve_error': stationary_error,
                        'frozen_mean_bound_passed': passed})

    # The clock control concerns the whole probability law, not only the endpoint mean.
    states, base = generator(budget, 'channel', [1, 2], [1, 1])
    _, faster = generator(budget, 'channel', [3, 6], [3, 3])
    rate_error = float(abs(faster - 3*base).max())
    clock_error = float(abs(expm(faster*duration) - expm(base*(3*duration))).max())
    if rate_error > 1e-13 or clock_error > 1e-12:
        raise AssertionError('Common clock scaling failed')
    return {'kind': 'Verification of constructed model predictions; not empirical evidence',
            'prediction_sha256': sha256(prediction_path), 'config_sha256': sha256(config_path),
            'reference_measure': prediction['reference_measure'],
            'simultaneous_mean_absolute_tolerance': prediction['simultaneous_mean_absolute_tolerance'],
            'family_error_bound': prediction['family_error_bound'],
            'clock_control_generator_error': rate_error, 'clock_control_transition_error': clock_error,
            'total_trajectories': replicates * len(records),
            'total_events': sum(row['events'] for row in records),
            'all_frozen_mean_bounds_passed': all(row['frozen_mean_bound_passed'] for row in records),
            'cases': records}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=['forecast', 'verify'], required=True)
    parser.add_argument('--config', type=Path, default=DEFAULT_CONFIG)
    parser.add_argument('--prediction', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.stage == 'verify' and args.prediction is None:
        parser.error('--prediction is required for verification')
    result = forecast(args.config) if args.stage == 'forecast' else verify(args.prediction, args.config)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'stage': args.stage, 'output': str(args.output),
                      'cases': len(result['cases'])}, sort_keys=True))
    if args.stage == 'verify' and not result['all_frozen_mean_bounds_passed']:
        raise SystemExit('Frozen mean bound failed; all case results retained in output')


if __name__ == '__main__':
    main()
