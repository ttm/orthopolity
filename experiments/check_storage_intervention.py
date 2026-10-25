"""Analytic storage intervention, not an empirical study or fitted model.

Reference measure: independently specified storage at unit potential; neither
log-orthopolic nor linear-orthopolic size allocation. See the dated design note.
The two solvers use different state coordinates and independent flux assembly.
"""
import json

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq


def storage(level, scale, nonlinear):
    result = np.asarray(level, dtype=float) * scale
    if nonlinear:
        h = level[2]
        result[2] = 3 * h - 4 * h**2 + 2 * h**3
    return result


def capacity(level, scale, nonlinear):
    result = np.array(scale, dtype=float)
    if nonlinear:
        h = level[2]
        result[2] = 3 - 8 * h + 6 * h**2
    return result


def potential(stock, scale, nonlinear):
    result = np.asarray(stock, dtype=float) / scale
    if nonlinear:
        # Unique nonnegative inverse: F'_3 >= 1/3. This root solver does
        # not use the level-coordinate integration or its initial guesses.
        r = stock[2]
        if r < 0:
            raise ValueError('Negative stock outside the physical example')
        result[2] = brentq(lambda h: 3*h - 4*h*h + 2*h**3 - r,
                          0, max(2., r + 1), xtol=5e-15)
    return result


def equilibrium(budget, scale, nonlinear):
    h = brentq(lambda x: sum(storage(np.full(3, x), scale, nonlinear)) - budget,
               0, max(2., budget), xtol=5e-15)
    return h, storage(np.full(3, h), scale, nonlinear)


def stock_flow(t, stock, scale, nonlinear, edges, speed):
    level = potential(stock, scale, nonlinear)
    derivative = np.zeros(3)
    for i, j, conductance in edges:
        current = speed * conductance * (level[i] - level[j])
        derivative[i] -= current
        derivative[j] += current
    return derivative


def level_solution(initial, scale, nonlinear, edges, times, speed=1.):
    # Incidence assembly, independent of the explicit edge loop above.
    incidence = np.zeros((len(edges), 3))
    for row, (i, j, conductance) in enumerate(edges):
        incidence[row, i] = np.sqrt(conductance)
        incidence[row, j] = -np.sqrt(conductance)
    laplacian = incidence.T @ incidence
    def rhs(t, level):
        return -speed * (laplacian @ level) / capacity(level, scale, nonlinear)
    solution = solve_ivp(rhs, (0., times[-1]), potential(initial, scale, nonlinear),
                         t_eval=times, method='Radau', rtol=2e-11, atol=2e-13)
    assert solution.success
    return np.column_stack([storage(h, scale, nonlinear) for h in solution.y.T])


def energy(level, scale, nonlinear):
    # Integral h dF(h), gravitational energy apart from fixed rho*g factors.
    result = .5 * scale * level**2
    if nonlinear:
        h = level[2]
        result[2] = 1.5*h**2 - (8./3)*h**3 + 1.5*h**4
    return sum(result)


def check():
    unit = np.ones(3)
    # Baseline endpoints AND small-signal storage agree exactly.
    assert np.array_equal(storage(unit, unit, True), unit)
    assert np.array_equal(capacity(unit, unit, True), unit)
    assert np.min(capacity(np.array([1., 1., 2./3]), unit, True)) > .3333333333
    paths = [((0, 1, 1.), (1, 2, .7)),
             ((0, 1, .4), (0, 2, 1.3), (1, 2, .8))]
    times = np.linspace(0, 120, 241)
    differences, stocks, endpoints, clock, balance = [], [], [], [], []
    cases = []
    for nonlinear in [False, True]:
        for changed in [False, True]:
            scale = np.array([2. if changed else 1., 1., 1.])
            initial = unit.copy() if changed else np.array([.2, 1., 1.8])
            h, endpoint = equilibrium(3., scale, nonlinear)
            for edges in paths:
                direct = solve_ivp(stock_flow, (0., times[-1]), initial,
                                   args=(scale, nonlinear, edges, 1.), t_eval=times,
                                   method='DOP853', rtol=2e-12, atol=2e-14)
                assert direct.success
                transformed = level_solution(initial, scale, nonlinear, edges, times)
                differences.append(float(np.max(abs(direct.y - transformed))))
                stocks.append(float(np.max(abs(transformed.sum(axis=0) - 3))))
                endpoints.append(float(np.max(abs(direct.y[:, -1] - endpoint))))
                assert np.min(direct.y) > 0
                accelerated = level_solution(initial, scale, nonlinear, edges,
                                              times / 3, speed=3.)
                clock.append(float(np.max(abs(accelerated - transformed))))
                heights = [potential(r, scale, nonlinear) for r in direct.y.T]
                energies = [energy(x, scale, nonlinear) for x in heights]
                assert np.max(np.diff(energies)) < 1e-10
                for r, x in zip(direct.y.T[::24], heights[::24]):
                    derivative = stock_flow(0, r, scale, nonlinear, edges, 1.)
                    dissipation = sum(g*(x[i]-x[j])**2 for i, j, g in edges)
                    balance.append(float(abs(x @ derivative + dissipation)))
            cases.append(dict(nonlinear=nonlinear, capacity_doubled=changed,
                              level=h, stocks=endpoint.tolist()))

    # Independent polynomial endpoint, rather than another budget root solve.
    roots = np.roots([2., -4., 6., -3.])
    h_polynomial = [r.real for r in roots if abs(r.imag) < 1e-12 and r.real > 0]
    assert len(h_polynomial) == 1
    h, nonlinear_endpoint = equilibrium(3., np.array([2., 1., 1.]), True)
    polynomial_error = abs(h_polynomial[0] - h)
    assert polynomial_error < 1e-12

    # Capacity susceptibility is independent of all conductance choices.
    derivative_errors = []
    for nonlinear in [False, True]:
        for factor in [1., 1.4, 2., 3.]:
            scale = np.array([factor, 1., 1.])
            level, _ = equilibrium(3., scale, nonlinear)
            capacities = capacity(np.full(3, level), scale, nonlinear)
            expected = -capacities * level / capacities.sum()
            expected[0] += level
            step = 1e-5
            plus = equilibrium(3., scale + np.array([step, 0., 0.]), nonlinear)[1]
            minus = equilibrium(3., scale - np.array([step, 0., 0.]), nonlinear)[1]
            derivative_errors.append(float(np.max(abs((plus-minus)/(2*step)-expected))))
            assert abs(expected.sum()) < 1e-14

    assert max(differences) < 2e-9
    assert max(stocks) < 2e-9
    assert max(endpoints) < 2e-9
    assert max(clock) < 2e-9
    assert max(balance) < 1e-12
    assert max(derivative_errors) < 2e-9
    return dict(
        kind='Constructed analytic design only; no experimental response or verdict',
        reference_measure='Storage at unit potential; neither log-orthopolic nor linear-orthopolic size allocation',
        initial_budget=3., baseline_stocks=[1., 1., 1.], baseline_capacities=[1., 1., 1.],
        linear_capacity_intervention_stocks=[1.5, .75, .75],
        nonlinear_capacity_intervention_stocks=nonlinear_endpoint.tolist(),
        nonlinear_common_level=h,
        unchanged_store_depletion_ratio=(1-nonlinear_endpoint[2])/(1-nonlinear_endpoint[1]),
        independent_coordinate_trajectory_max_error=max(differences),
        conservation_max_error=max(stocks), endpoint_max_error=max(endpoints),
        coupling_clock_rescaling_max_error=max(clock), energy_balance_max_error=max(balance),
        polynomial_endpoint_max_error=polynomial_error,
        susceptibility_finite_difference_max_error=max(derivative_errors),
        fixed_network_cases=len(cases)*len(paths), cases=cases)


if __name__ == '__main__':
    print(json.dumps(check(), indent=2))
