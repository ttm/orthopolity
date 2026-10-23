"""Check a hidden-link-storage counterexample; no empirical data or verdict.

The reference weights are physical capacities, neither logarithmic nor linear
size intervals. See docs/topology-storage-2026-10-23.md. Use Python 3.11.
"""
import json
import math

import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import eigh
from scipy.optimize import brentq


def chain(chambers, link_capacity):
    """Unit chamber capacities and unit conductances to intervening stores."""
    if chambers < 2 or int(chambers) != chambers:
        raise ValueError('Need an integer number of chambers, at least two')
    if not math.isfinite(link_capacity) or link_capacity <= 0:
        raise ValueError('Link capacity must be finite and positive')
    size = 2 * chambers - 1
    incidence = np.zeros((size - 1, size))
    for j in range(size - 1):
        incidence[j, j:j + 2] = [1, -1]
    capacities = np.ones(size)
    capacities[1::2] = link_capacity
    return incidence.T @ incidence, capacities


def five_pair_time_ratio(link_capacity):
    """Pair contrast has rate one, independently of hidden link capacity."""
    if link_capacity == 0:
        return 3 + math.sqrt(5)
    laplacian, capacities = chain(5, link_capacity)
    rates = eigh(laplacian, np.diag(capacities), eigvals_only=True)
    return float(1 / rates[1])


def explicit_flux(t, concentrations, capacities):
    """Local flux balances, independent of the assembled matrix operator."""
    derivative = np.zeros_like(concentrations)
    for j in range(len(concentrations) - 1):
        current = concentrations[j] - concentrations[j + 1]
        derivative[j] -= current / capacities[j]
        derivative[j + 1] += current / capacities[j + 1]
    return derivative


def spectral_trajectory(laplacian, capacities, initial, times):
    """Propagate concentrations through the symmetric generalized problem."""
    rates, modes = eigh(laplacian, np.diag(capacities))
    coefficients = modes.T @ (capacities * initial)
    return modes @ (coefficients[:, None] * np.exp(-rates[:, None] * times))


def check():
    # These ratios and initial states are constructed mathematical examples.
    capacity_ratios = [.01, .05, .1, .5, 1., 2., 10.]
    times = np.linspace(0, 15, 101)
    pair_initial = np.array([1., .5, 0.])
    pair_expected = np.vstack((.5 + .5 * np.exp(-times),
                               np.full(len(times), .5),
                               .5 - .5 * np.exp(-times)))
    pair_errors, ode_errors, stock_errors, root_errors, common_errors = [], [], [], [], []
    ratios, projections, excitations = [], [], []
    for r in capacity_ratios:
        laplacian, capacities = chain(2, r)
        pair_solution = spectral_trajectory(laplacian, capacities, pair_initial, times)
        pair_errors.append(float(np.max(abs(pair_solution - pair_expected))))
        # Both observed chamber stock and full-system stock stay constant.
        stock_errors.extend([float(np.max(abs(pair_solution[[0, 2]].sum(0) - 1))),
                             float(np.max(abs(capacities @ pair_solution
                                              - (1 + r / 2))))])
        # A different, independently prepared pair experiment identifies r.
        # Both chambers start at one, connector empty: total resource is two.
        common_times = np.linspace(0, 10 / (1 + 2 / r), 101)
        common = spectral_trajectory(laplacian, capacities,
                                      np.array([1., 0., 1.]), common_times)
        expected_total = 4 / (2 + r) + 2 * r / (2 + r) * np.exp(
            -(1 + 2 / r) * common_times)
        common_errors.append(float(np.max(abs(common[[0, 2]].sum(0) - expected_total))))
        pair_rates = eigh(laplacian, np.diag(capacities), eigvals_only=True)
        assert abs(2 / (pair_rates[2] / pair_rates[1] - 1) - r) < 1e-11
        stock_errors.append(float(np.max(abs(capacities @ common - 2))))

        laplacian, capacities = chain(5, r)
        rates, modes = eigh(laplacian, np.diag(capacities))
        ratios.append(float(1 / rates[1]))
        # Odd mode: chamber at the left endpoint has a nonzero projection.
        projections.append(float(abs(modes[0, 1])))
        assert np.max(abs(modes[:, 1] + modes[::-1, 1])) < 1e-10
        # Independent reduction to the antisymmetric half-chain polynomial.
        coefficients = [r * r, -(3 * r * r + 4 * r),
                        2 * r * r + 9 * r + 4, -(4 * r + 6), 1.]
        roots = np.roots(coefficients)
        assert np.max(abs(roots.imag)) < 1e-9
        root_errors.append(float(abs(min(roots.real) - rates[1])))

        # Same concentrations for every capacity ratio. Links start at adjacent
        # chamber means. Odd deviations preserve observed chamber total too.
        initial = np.array([2., 1.5, 1., 1., 1., 1., 1., .5, 0.])
        excitations.append(float(abs(modes[:, 1] @ (capacities * (initial - 1)))))
        exact = spectral_trajectory(laplacian, capacities, initial, times)
        solution = solve_ivp(explicit_flux, (times[0], times[-1]), initial,
                             args=(capacities,), t_eval=times, method='Radau',
                             rtol=1e-11, atol=1e-13)
        assert solution.success
        ode_errors.append(float(np.max(abs(exact - solution.y))))
        stock_errors.extend([float(np.max(abs(capacities @ exact - (5 + 4 * r)))),
                             float(np.max(abs(exact[::2].sum(0) - 5)))])
        assert np.min(exact) >= -1e-12

    ideal = 3 + math.sqrt(5)
    equal_capacity = 1 / (2 * (1 - math.cos(math.pi / 9)))
    assert abs(five_pair_time_ratio(1) - equal_capacity) < 1e-11
    # Positive link storage increases the slow time for this fixed network.
    assert np.all(np.diff(ratios) > 0)
    assert ratios[0] > ideal
    assert abs(five_pair_time_ratio(1e-5) / ideal - 1) < 6e-6
    # Illustrative design tolerance, not a registered empirical pass rule.
    five_percent_limit = brentq(lambda r: five_pair_time_ratio(r) / ideal - 1.05,
                                .01, .5, xtol=1e-13)
    assert max(pair_errors) < 1e-11
    assert max(ode_errors) < 1e-9
    assert max(stock_errors) < 1e-11
    assert max(root_errors) < 1e-11
    assert max(common_errors) < 1e-11
    assert min(projections) > 0.01
    assert min(excitations) > 0.01
    return dict(
        kind='Analytic checks only; no experimental data or study verdict',
        measure='Physical capacities; neither log- nor linear-orthopolic size allocation',
        capacity_ratios=capacity_ratios,
        pair_chamber_timecourses_identical=True,
        pair_spectrum_vs_formula_max_error=max(pair_errors),
        network_spectrum_vs_local_flux_ode_max_error=max(ode_errors),
        full_and_observed_stock_max_error=max(stock_errors),
        generalized_eigenvalue_vs_quartic_max_error=max(root_errors),
        common_mode_calibration_formula_max_error=max(common_errors),
        slow_mode_minimum_endpoint_projection=min(projections),
        slow_mode_minimum_initial_excitation=min(excitations),
        five_to_pair_relaxation_time_ratios=ratios,
        negligible_link_storage_ratio=ideal,
        equal_link_chamber_storage_ratio=equal_capacity,
        equal_storage_relative_increase=equal_capacity / ideal - 1,
        illustrative_five_percent_relative_error_capacity_limit=five_percent_limit,
        five_percent_limit_scope='This homogeneous hidden-node model only',
    )


if __name__ == '__main__':
    print(json.dumps(check(), indent=2))
