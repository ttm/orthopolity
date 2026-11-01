"""Independent scalar-rate audit of the whole-object analytic forecast.

No project model or driver is imported. States are enumerated by the first
two counts, reaction rates are reconstructed individually, and a numerical
nullspace solve is compared with the product weights and frozen forecasts.
No Gillespie paths or empirical observations are generated.
"""
import argparse
from fractions import Fraction
import hashlib
import json
from math import fsum, lgamma, log, sqrt
from pathlib import Path

import numpy as np
from scipy.linalg import expm


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PREDICTION = ROOT / 'results/whole-object-assembly-2026-10-31/predictions.json'
COSTS = (1, 2, 4)
TOLERANCE = 1e-11


def lattice_states(budget):
    """Fix monomer and dimer counts, then test the remaining tetramer mass."""
    if isinstance(budget, bool) or not isinstance(budget, int) or budget <= 0:
        raise ValueError('A positive integer material budget is required')
    return [(a, b, (budget-a-2*b)//4)
            for a in range(budget+1)
            for b in range((budget-a)//2+1)
            if (budget-a-2*b) % 4 == 0]


def scalar_generator(states, mechanism, forward, reverse):
    """Construct each feasible physical reaction separately; columns are sources."""
    if mechanism not in ('channel', 'mass_action'):
        raise ValueError('Unknown mechanism')
    if len(forward) != 2 or len(reverse) != 2:
        raise ValueError('Two forward and two reverse constants are required')
    if any(not np.isfinite(v) or v <= 0 for v in (*forward, *reverse)):
        raise ValueError('Rate constants must be positive and finite')
    index = {state: i for i, state in enumerate(states)}
    matrix = np.zeros((len(states), len(states)))
    transitions = 0
    for source, (a, b, c) in enumerate(states):
        channels = []
        if a >= 2:
            rate = forward[0] * (a*(a-1) if mechanism == 'mass_action' else 1)
            channels.append(((a-2, b+1, c), rate))
        if b >= 1:
            rate = reverse[0] * (b if mechanism == 'mass_action' else 1)
            channels.append(((a+2, b-1, c), rate))
        if b >= 2:
            rate = forward[1] * (b*(b-1) if mechanism == 'mass_action' else 1)
            channels.append(((a, b-2, c+1), rate))
        if c >= 1:
            rate = reverse[1] * (c if mechanism == 'mass_action' else 1)
            channels.append(((a, b+2, c-1), rate))
        for target, rate in channels:
            if min(target) < 0 or sum(q*n for q, n in zip(COSTS, target)) != a+2*b+4*c:
                raise AssertionError('Reaction does not conserve integer material')
            matrix[index[target], source] += rate
            matrix[source, source] -= rate
            transitions += 1
    return matrix, transitions


def product_probability(states, mechanism, forward=(1, 1), reverse=(1, 1)):
    """Logarithmic product weights, independent of the rational forecast code."""
    log_dimer = log(forward[0]/reverse[0])
    log_tetramer = 2*log_dimer + log(forward[1]/reverse[1])
    weights = np.array([b*log_dimer + c*log_tetramer
                        - (fsum(lgamma(n+1) for n in (a, b, c))
                           if mechanism == 'mass_action' else 0.)
                        for a, b, c in states])
    weights = np.exp(weights - weights.max())
    return weights / fsum(weights)


def scalar_moments(states, probability, budget):
    counts = [fsum(float(p)*state[j] for p, state in zip(probability, states))
              for j in range(3)]
    mean = [counts[j]*COSTS[j]/budget for j in range(3)]
    covariance = [[fsum(float(p)*(state[i]*COSTS[i]/budget-mean[i])
                       *(state[j]*COSTS[j]/budget-mean[j])
                       for p, state in zip(probability, states))
                   for j in range(3)] for i in range(3)]
    return counts, mean, covariance


def audit(path):
    raw = Path(path).read_bytes()
    prediction = json.loads(raw)
    budget = prediction['budget']
    states = lattice_states(budget)
    duration = prediction['duration']
    if not np.isfinite(duration) or duration < 0:
        raise ValueError('Invalid observation duration')
    compared = 0
    errors = {}

    def compare(label, actual, expected):
        nonlocal compared
        a, b = np.asarray(actual, dtype=float), np.asarray(expected, dtype=float)
        if a.shape != b.shape or not np.isfinite(a).all() or not np.isfinite(b).all():
            raise AssertionError(f'{label}: invalid array shape or finite values')
        error = float(np.max(np.abs(a-b)))
        compared += a.size
        errors[label] = max(errors.get(label, 0.), error)
        if error > TOLERANCE:
            raise AssertionError(f'{label}: {error} exceeds {TOLERANCE}')

    transitions = 0
    generators = {}
    for case in prediction['cases']:
        if list(map(tuple, case['states'])) != states or case['state_count'] != len(states):
            raise AssertionError('Independent lattice enumeration differs')
        if any(sum(q*n for q, n in zip(COSTS, state)) != budget for state in states):
            raise AssertionError('State budget differs')
        mechanism = case['mechanism']
        matrix, edge_count = scalar_generator(states, mechanism, case['forward'], case['reverse'])
        transitions += edge_count
        generators[case['name']] = matrix
        compare('generator_column_sum', matrix.sum(axis=0), np.zeros(len(states)))
        product = product_probability(states, mechanism, case['forward'], case['reverse'])
        compare('stationary_product', product, case['stationary_probabilities'])
        compare('stationary_residual', matrix @ product, np.zeros(len(states)))
        flux = matrix * product[None, :]
        compare('edge_detailed_balance', flux, flux.T)
        # Nullspace via SVD, not the model's normalized square linear solve.
        _, singular, vectors = np.linalg.svd(matrix)
        if singular[-2] <= 1e-12 or singular[-1] > 1e-11:
            raise AssertionError('Expected one-dimensional stationary nullspace')
        null = vectors[-1]
        null = null / fsum(null)
        compare('stationary_svd', null, case['stationary_probabilities'])
        counts, mean, covariance = scalar_moments(states, null, budget)
        compare('stationary_mean_counts', counts, case['stationary_mean_counts'])
        compare('stationary_mean_shares', mean, case['stationary_mean_shares'])
        compare('stationary_share_covariance', covariance, case['stationary_share_covariance'])
        compare('stationary_exact_mean_shares', mean,
                [float(Fraction(x)) for x in case['stationary_exact_mean_shares']])
        initial = product_probability(states, mechanism)
        compare('baseline_initialization', initial, case['initial_probabilities'])
        endpoint = expm(duration*matrix) @ initial
        compare('finite_time_probability', endpoint, case['finite_time_probabilities'])
        compare('finite_time_normalization', endpoint.sum(), 1.)
        if min(endpoint) < -TOLERANCE:
            raise AssertionError('Negative finite-time probability')
        _, mean, covariance = scalar_moments(states, endpoint, budget)
        compare('finite_time_mean_shares', mean, case['finite_time_mean_shares'])
        compare('finite_time_share_covariance', covariance, case['finite_time_share_covariance'])

    for row in prediction['asymptotic_channel']:
        b = row['budget']
        points = lattice_states(b)
        if b % 4 or len(points) != row['states']:
            raise AssertionError('Finite-budget lattice count differs')
        m = b//4
        if len(points) != (m+1)**2:
            raise AssertionError('Closed-form state count differs')
        uniform = np.full(len(points), 1/len(points))
        _, mean, covariance = scalar_moments(points, uniform, b)
        compare('finite_budget_mean', mean, row['mean_shares'])
        compare('finite_budget_covariance', covariance, row['share_covariance'])
        compare('finite_budget_closed_form', mean,
                [1/3+1/(12*(m+1)), 1/3+1/(12*(m+1)), 1/3-1/(6*(m+1))])
    compare('dirichlet_covariance_limit',
            [[(2 if i == j else -1)/36 for j in range(3)] for i in range(3)],
            prediction['limiting_share_covariance'])
    bound = sqrt(log(2*3*len(prediction['cases'])/prediction['family_error_bound'])
                 /(2*prediction['replicates']))
    compare('simultaneous_hoeffding_bound', bound,
            prediction['simultaneous_mean_absolute_tolerance'])
    if 'channel_bias_clock3' in generators and 'channel_bias' in generators:
        compare('common_clock_generator', generators['channel_bias_clock3'],
                3*generators['channel_bias'])
        compare('common_clock_semigroup', expm(duration*generators['channel_bias_clock3']),
                expm((3*duration)*generators['channel_bias']))
    return {
        'kind': 'Independent analytic forecast audit; no stochastic simulations or empirical data',
        'prediction_sha256': hashlib.sha256(raw).hexdigest(),
        'reference_measure': prediction['reference_measure'],
        'budget': budget, 'states': len(states), 'cases': len(prediction['cases']),
        'finite_budget_cases': len(prediction['asymptotic_channel']),
        'conserved_directed_transitions_checked': transitions,
        'scalar_quantities_compared': compared,
        'absolute_tolerance': TOLERANCE,
        'maximum_absolute_error': max(errors.values()),
        'maximum_errors_by_check': errors,
        'passed': True,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prediction', type=Path, default=DEFAULT_PREDICTION)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = audit(args.prediction)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({key: result[key] for key in (
        'cases', 'scalar_quantities_compared', 'maximum_absolute_error', 'passed')},
        sort_keys=True))


if __name__ == '__main__':
    main()
