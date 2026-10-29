"""Verify an analytic fragmentation boundary; no experimental data are read.

Uniform cuts of a homogeneous rod conserve mass in each realization. Their
expected mass allocation is not log-orthopolic in fragment mass. The separate
completion calculation uses logarithmic sieve diameter when weights are sieve
bin widths. These two observables must not be silently identified.
"""
import argparse
from fractions import Fraction
import json
import operator
from pathlib import Path

import numpy as np
from scipy.integrate import quad
from scipy.optimize import linprog


def _parent(parent_mass, fragments):
    mass = float(parent_mass)
    if not np.isfinite(mass) or mass <= 0:
        raise ValueError('Parent mass must be finite and positive')
    if isinstance(fragments, (bool, np.bool_)):
        raise ValueError('Fragment count must be an integer at least two')
    try:
        count = operator.index(fragments)
    except TypeError as error:
        raise ValueError('Fragment count must be an integer at least two') from error
    if count < 2:
        raise ValueError('Fragment count must be an integer at least two')
    return mass, count


def expected_bins(edges, parent_mass, fragments):
    """Return unconditional expected bin counts and physical bin masses."""
    mass, count = _parent(parent_mass, fragments)
    edges = np.asarray(edges, dtype=float)
    if (edges.ndim != 1 or len(edges) < 2 or not np.isfinite(edges).all()
            or np.any(np.diff(edges) <= 0) or edges[0] < 0 or edges[-1] > mass):
        raise ValueError('Edges must increase inside the closed parent-mass interval')
    x = edges / mass
    number_survival = (1 - x)**(count - 1)
    mass_survival = number_survival * (1 + (count - 1) * x)
    return -count * np.diff(number_survival), -mass * np.diff(mass_survival)


def _allocation(masses, widths):
    y = np.asarray(masses, dtype=float)
    w = np.asarray(widths, dtype=float)
    if (y.ndim != 1 or len(y) == 0 or w.shape != y.shape
            or not np.isfinite(y).all() or not np.isfinite(w).all()
            or np.any(y < 0) or np.any(w <= 0)):
        raise ValueError('Masses must be nonnegative and reference widths positive')
    return y, w


def minimum_added_mass(masses, widths):
    """Smallest nonnegative addition that makes mass per width equal."""
    y, w = _allocation(masses, widths)
    return float(np.sum(np.max(y / w) * w - y))


def minimum_tv(masses, widths, missing_mass):
    """Sharp TV lower bound after adding at most the supplied missing mass.

    The observed profile must contain some mass. The bound concerns a realized
    profile, not an expectation across independent fragmentation experiments.
    """
    y, w = _allocation(masses, widths)
    missing = float(missing_mass)
    if not np.isfinite(missing) or missing < 0 or y.sum() <= 0:
        raise ValueError('Missing mass must be nonnegative; observed mass positive')
    return float(np.maximum(y / (y.sum() + missing) - w / w.sum(), 0).sum())


def _lp_added_mass(y, w):
    # Optimize each missing-bin mass and the unknown common plateau separately.
    count = len(y)
    matrix = np.column_stack((np.eye(count), -w))
    result = linprog(np.r_[np.ones(count), 0.], A_eq=matrix, b_eq=-y,
                     bounds=[(0, None)] * (count + 1), method='highs')
    if not result.success:
        raise AssertionError(result.message)
    return float(result.fun)


def _lp_tv(y, w, missing):
    # Charnes-Cooper variables v_j=z_j/(sum(y)+sum(z)), t=1/total,
    # and positive deviations h_j. Unlike the formula, this LP optimizes over
    # every addition from zero to missing, not only over the maximal addition.
    count = len(y)
    total = y.sum()
    objective = np.r_[np.zeros(count + 1), np.ones(count)]
    equality = np.r_[np.ones(count), total, np.zeros(count)][None, :]
    upper = np.zeros((count + 1, 2 * count + 1))
    upper[:count, :count] = np.eye(count)
    upper[:count, count] = y
    upper[:count, count + 1:] = -np.eye(count)
    upper[count, :count] = 1
    upper[count, count] = -missing
    bounds = ([(0, None)] * count + [(1 / (total + missing), 1 / total)]
              + [(0, None)] * count)
    result = linprog(objective, A_ub=upper, b_ub=np.r_[w / w.sum(), 0.],
                     A_eq=equality, b_eq=[1.], bounds=bounds, method='highs')
    if not result.success:
        raise AssertionError(result.message)
    return float(result.fun)


def check():
    relative_edges = np.array([0., 1/32, 1/16, 1/8, 1/4, 1/2, 3/4, 1.])
    quadrature_errors = []
    moment_errors = []
    cases = 0
    for count in (2, 3, 8, 32):
        for parent in (.25, 1., 7.5):
            edges = parent * relative_edges
            counts, masses = expected_bins(edges, parent, count)
            # Integrate the density directly, independently of its antiderivatives.
            def density(m):
                return count * (count - 1) / parent * (1 - m / parent)**(count - 2)
            for a, b, number, mass in zip(edges[:-1], edges[1:], counts, masses):
                number_quad = quad(density, a, b, epsabs=1e-12, epsrel=1e-12)[0]
                mass_quad = quad(lambda m: m * density(m), a, b,
                                 epsabs=1e-12, epsrel=1e-12)[0]
                quadrature_errors.extend([abs(number - number_quad) / count,
                                          abs(mass - mass_quad) / parent])
            moment_errors.extend([abs(counts.sum() - count) / count,
                                  abs(masses.sum() - parent) / parent])
            second = quad(lambda m: m*m*density(m), 0., parent,
                          epsabs=1e-12, epsrel=1e-12)[0]
            moment_errors.append(abs(second / parent**2 - 2 / (count + 1)))
            if count == 2:
                # A single uniform cut supplies an independently elementary case.
                np.testing.assert_allclose(counts, 2*np.diff(edges)/parent, atol=1e-14)
                np.testing.assert_allclose(masses, np.diff(edges**2)/parent, atol=1e-14)
            cases += 1

    # Exact rational arithmetic for the fixed eight-fragment comparison.
    count = 8
    fractional_edges = [Fraction(1, 16), Fraction(1, 8), Fraction(1, 4), Fraction(1, 2)]
    cumulative = [1 - (1-x)**(count-1)*(1+(count-1)*x) for x in fractional_edges]
    exact_masses = [b-a for a, b in zip(cumulative[:-1], cumulative[1:])]
    exact_counts = [count*((1-a)**(count-1)-(1-b)**(count-1))
                    for a, b in zip(fractional_edges[:-1], fractional_edges[1:])]
    exact_window = sum(exact_masses)
    exact_profile = [m / exact_window for m in exact_masses]
    edges = np.array([float(x) for x in fractional_edges])
    counts, masses = expected_bins(edges, 1., count)
    fraction_error = max(np.max(abs(counts - [float(x) for x in exact_counts])),
                         np.max(abs(masses - [float(x) for x in exact_masses])))
    log_weights = np.diff(np.log(edges))
    neutral = log_weights / log_weights.sum()
    profile = masses / masses.sum()
    np.testing.assert_allclose(neutral, np.full(3, 1/3), rtol=0., atol=2e-16)
    np.testing.assert_allclose(profile, [float(x) for x in exact_profile], atol=1e-15)

    # Generated cuts demonstrate per-realization conservation only. No empirical
    # observations or claims about statistical detection power enter this check.
    rng = np.random.default_rng(20261028)
    cuts = np.sort(rng.uniform(size=(4096, count-1)), axis=1)
    pieces = np.diff(np.column_stack((np.zeros(len(cuts)), cuts, np.ones(len(cuts)))), axis=1)
    conservation_error = float(np.max(abs(pieces.sum(axis=1) - 1.)))
    if np.any(pieces < 0):
        raise AssertionError('Generated cuts must produce nonnegative masses')

    missing_errors, tv_errors = [], []
    for case in range(60):
        size = 2 + case % 6
        y = rng.uniform(.05, 4., size=size)
        y[rng.random(size) < .2] = 0.
        if y.sum() == 0:
            y[0] = 1.
        w = np.exp(rng.uniform(-2., 2., size=size))
        missing = float(rng.uniform(0., 3.) * y.sum())
        needed = minimum_added_mass(y, w)
        missing_errors.append(abs(needed - _lp_added_mass(y, w)))
        tv_errors.append(abs(minimum_tv(y, w, missing) - _lp_tv(y, w, missing)))
        # A constructive equality witness, with neither removals nor redistribution.
        completion = y + (np.max(y / w)*w - y)
        np.testing.assert_allclose(completion / w, np.full(size, np.max(y / w)),
                                   rtol=2e-15, atol=1e-14)
        if minimum_tv(y, w, needed) > 2e-15:
            raise AssertionError('The minimal complete plateau must have zero TV')
        np.testing.assert_allclose(minimum_added_mass(3*y, 7*w), 3*needed,
                                   rtol=2e-14, atol=1e-13)

    if minimum_added_mass([9., 1.], [1., 1.]) != 8.:
        raise AssertionError('Known missing-mass example failed')
    np.testing.assert_allclose(minimum_tv([9., 1.], [1., 1.], 7.), 1/34, atol=1e-16)

    invalid_calls = [
        lambda: expected_bins([0, 1], 0, 8),
        lambda: expected_bins([0, 1], 1, 1),
        lambda: expected_bins([0, 1], 1, 2.5),
        lambda: expected_bins([0, 1], 1, True),
        lambda: expected_bins([0, 2], 1, 8),
        lambda: expected_bins([0, .5, .5], 1, 8),
        lambda: minimum_added_mass([-1, 2], [1, 1]),
        lambda: minimum_added_mass([1, 2], [0, 1]),
        lambda: minimum_added_mass([1, np.nan], [1, 1]),
        lambda: minimum_tv([1, 2], [1, 1], -1),
        lambda: minimum_tv([0, 0], [1, 1], 0),
    ]
    for call in invalid_calls:
        try:
            call()
        except ValueError:
            pass
        else:
            raise AssertionError('Invalid physical inputs must raise ValueError')

    if (max(quadrature_errors + moment_errors) > 2e-13 or fraction_error > 1e-14
            or conservation_error > 5e-16 or max(missing_errors) > 2e-11
            or max(tv_errors) > 2e-12):
        raise AssertionError('Independent analytic checks exceeded numerical tolerances')
    return {
        'kind': 'Analytic fragmentation boundary only; no experimental data read',
        'reference_measure': 'Log-orthopolic in fragment mass for the rod; logarithmic sieve diameter for the separate completion bound',
        'interpretation': 'Ratio of expected bin masses, not mean of per-realization conditional shares',
        'uniform_cut_example': {
            'parent_mass': 1., 'fragments': count,
            'bin_edges_as_parent_mass_fractions': edges.tolist(),
            'expected_bin_counts': counts.tolist(),
            'expected_bin_mass_fractions': masses.tolist(),
            'expected_window_mass_fraction': float(exact_window),
            'conditional_expected_mass_shares': profile.tolist(),
            'exact_conditional_expected_mass_shares': [str(x) for x in exact_profile],
            'equal_mass_per_log_bin_shares': neutral.tolist(),
            'total_variation_from_log_equality': float(.5*abs(profile-neutral).sum()),
            'expected_log_resource_peak_as_parent_fraction': 2/count,
        },
        'verification': {
            'quadrature_cases': cases,
            'maximum_normalized_quadrature_error': max(quadrature_errors),
            'maximum_normalized_count_mass_second_moment_error': max(moment_errors),
            'maximum_exact_fraction_error': float(fraction_error),
            'generated_uniform_cut_realizations': len(cuts),
            'maximum_per_realization_mass_conservation_error': conservation_error,
            'linear_program_cases_each': len(missing_errors),
            'maximum_missing_mass_formula_vs_lp_error': max(missing_errors),
            'maximum_tv_formula_vs_lp_error': max(tv_errors),
            'invalid_input_checks': len(invalid_calls),
        },
        'generated_seed': 20261028,
        'qualifications': [
            'Uniform cuts are a specified ideal mechanism, not a fitted rock-fracture model',
            'Conservation alone does not imply equal expected mass per logarithmic fragment mass',
            'Completion bounds concern actual profiles, not an unspecified stochastic mean claim',
            'Missing-material feasibility is not an independent absolute-budget prediction',
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = check()
    rendered = json.dumps(result, indent=2, allow_nan=False) + '\n'
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)
    print(rendered, end='')


if __name__ == '__main__':
    main()
