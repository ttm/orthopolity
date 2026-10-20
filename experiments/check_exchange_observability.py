"""Verify loss-only identifiability bounds; no empirical data or study verdict.

See docs/exchange-observability-2026-10-20.md. Run with Python 3.11.
"""
import json
import math

import numpy as np
from scipy.integrate import quad, solve_ivp
from scipy.optimize import linprog


def sampled_retention_ceiling(shares):
    """Largest retained fraction at each sample under nonincreasing stocks.

    Rows are times, columns are compartments. A zero factor from support
    expansion excludes positive-total loss-only evolution. For long paths,
    accumulate logs instead: floating-point underflow is not that certificate.
    Finite fractional loss rates additionally require fixed support.
    """
    shares = np.asarray(shares, dtype=float)
    if (shares.ndim != 2 or min(shares.shape) < 1
            or not np.all(np.isfinite(shares)) or np.any(shares < 0)
            or not np.allclose(shares.sum(axis=1), 1, rtol=0, atol=1e-12)):
        raise ValueError('Rows must be finite nonnegative unit-sum shares')
    retention = [1.]
    for previous, current in zip(shares[:-1], shares[1:]):
        positive = current > 0
        ratio = float(np.min(previous[positive] / current[positive]))
        retention.append(retention[-1] * min(1., ratio))
    return np.asarray(retention)


def independent_lp_ceiling(shares):
    """Maximize the final total subject directly to all stock inequalities."""
    n_times, n_compartments = shares.shape
    constraints = []
    for t in range(1, n_times):
        for i in range(n_compartments):
            row = np.zeros(n_times)
            row[t] = shares[t, i]
            row[t - 1] = -shares[t - 1, i]
            constraints.append(row)
    objective = np.zeros(n_times)
    objective[-1] = -1
    result = linprog(objective, A_ub=np.asarray(constraints),
                     b_ub=np.zeros(len(constraints)),
                     bounds=[(1, 1)] + [(0, 1)] * (n_times - 1),
                     method='highs', options={'primal_feasibility_tolerance': 1e-9,
                                              'dual_feasibility_tolerance': 1e-9})
    assert result.success, result.message
    return float(result.x[-1])


def main():
    times = np.linspace(0, 2, 41)
    decay = np.exp(-2 * times)
    example = np.column_stack((.5 - .25 * decay, .5 + .25 * decay))
    cycle = np.array([[.2, .8], [.8, .2], [.2, .8]])
    paths = [example, cycle, np.full((5, 3), 1 / 3),
             np.array([[1., 0.], [.8, .2]])]
    # Fixed mathematical examples, independent of any observed source data.
    for phase in np.linspace(0, 2, 12):
        grid = np.linspace(0, 3, 7)[:, None]
        nodes = np.arange(4)[None, :]
        values = np.exp(.4 * np.sin(grid + nodes + phase)
                        + .3 * np.cos(2 * grid - nodes))
        paths.append(values / values.sum(axis=1, keepdims=True))

    errors = []
    for shares in paths:
        ceiling = sampled_retention_ceiling(shares)
        errors.append(abs(ceiling[-1] - independent_lp_ceiling(shares)))
        stocks = shares * ceiling[:, None]
        assert np.max(np.diff(stocks, axis=0)) < 1e-12
    assert max(errors) < 1e-9
    assert abs(sampled_retention_ceiling(cycle)[-1] - 1 / 16) < 1e-14
    assert sampled_retention_ceiling(paths[3])[-1] == 0
    # Identical endpoints alone give a ceiling of one, unlike the full cycle.
    assert sampled_retention_ceiling(cycle[[0, -1]])[-1] == 1
    assert np.max(abs(sampled_retention_ceiling(example)
                      - 1 / (2 - decay))) < 1e-14

    def loss_rates(t):
        e = math.exp(-2 * t)
        p = np.array([.5 - .25 * e, .5 + .25 * e])
        dp = np.array([.5 * e, -.5 * e])
        growth = dp / p
        return np.max(growth) - growth

    integral = quad(lambda t: .5 * math.exp(-2 * t)
                    / (.5 - .25 * math.exp(-2 * t)), 0, 1,
                    epsabs=1e-13, epsrel=1e-13)[0]
    ceiling_one = 1 / (2 - math.exp(-2))
    assert abs(math.exp(-integral) - ceiling_one) < 1e-13
    solution = solve_ivp(lambda t, r: -loss_rates(t) * r,
                         (0, 2), [.25, .75], t_eval=times,
                         method='DOP853', rtol=1e-12, atol=1e-14)
    assert solution.success
    expected = example.T / (2 - decay)
    ode_error = float(np.max(abs(solution.y - expected)))
    assert ode_error < 1e-10
    assert min(loss_rates(t).min() for t in times) >= 0
    # Simultaneous deterministic bounds: net influx follows even with uncertainty.
    assert .90 * .40 > .26
    # Without sufficient retention, those same bounds cannot certify influx.
    assert not (.60 * .40 > .26)

    print(json.dumps(dict(
        kind='Analytic observation checks only; no empirical inputs or verdict',
        sampled_paths_checked=len(paths),
        formula_vs_linear_program_max_error=float(max(errors)),
        continuous_loss_ode_max_error=ode_error,
        exact_zero_to_positive_excludes_positive_total_loss_only=True,
        example_maximum_retention_at_time_one=ceiling_one,
        example_minimum_total_loss_at_time_one=1 - ceiling_one,
        returning_cycle_maximum_retention=1 / 16,
    ), indent=2))


if __name__ == '__main__':
    main()
