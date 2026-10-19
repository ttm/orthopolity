"""Check analytic design examples; no empirical inputs or new study verdict.

Run with the repository's Python 3.11 environment. The proof and interpretation
are in docs/equalization-release-design-2026-10-19.md. Numerical output is a
calculation check, not an additional empirical or registered simulation study.
"""
import json
import math

import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import expm


def path_laplacian(n):
    matrix = np.zeros((n, n))
    for j in range(n - 1):
        matrix[j, j] += 1
        matrix[j + 1, j + 1] += 1
        matrix[j, j + 1] -= 1
        matrix[j + 1, j] -= 1
    return matrix


def main():
    pair, chain = path_laplacian(2), path_laplacian(5)
    gap_pair = np.linalg.eigvalsh(pair)[1]
    gap_chain = np.linalg.eigvalsh(chain)[1]
    ratio = gap_pair / gap_chain
    assert abs(ratio - (3 + math.sqrt(5))) < 1e-13

    times = np.linspace(0, 20, 201)
    initial = np.array([1., 0., 0., 0., 0.])

    # Integrate explicit edge balances independently of the matrix exponential.
    def edge_balance(t, resource):
        return np.r_[-(resource[0] - resource[1]),
                     resource[:-2] - 2 * resource[1:-1] + resource[2:],
                     resource[-2] - resource[-1]]

    numeric = solve_ivp(edge_balance, (0, 20), initial, t_eval=times,
                        rtol=1e-11, atol=1e-13)
    assert numeric.success
    analytic = np.array([expm(-chain * t) @ initial for t in times]).T
    flow_error = float(np.max(abs(numeric.y - analytic)))
    assert flow_error < 1e-10
    assert np.min(analytic) >= -1e-14
    conservation_error = float(np.max(abs(analytic.sum(axis=0) - 1)))
    assert conservation_error < 1e-13

    # Exactly the same observed shares arise from exchange or losses alone.
    decay = np.exp(-2 * times)
    shares = np.stack([.5 - .25 * decay, .5 + .25 * decay])
    share_derivative = np.stack([.5 * decay, -.5 * decay])
    remaining = decay * shares
    loss_rates = 2 - share_derivative / shares
    assert np.min(loss_rates) >= 0
    assert np.max(abs(share_derivative + pair @ shares)) < 1e-14
    normalized_error = float(np.max(abs(remaining / remaining.sum(axis=0) - shares)))
    assert normalized_error < 1e-14
    assert np.max(abs(decay * (share_derivative - 2 * shares)
                      + loss_rates * remaining)) < 1e-14
    assert np.max(decay * (share_derivative - 2 * shares)) <= 1e-14
    print(json.dumps(dict(
        kind='Analytic design checks only; no empirical inputs or study verdict',
        five_to_two_relaxation_time_ratio=float(ratio),
        closed_form=3 + math.sqrt(5),
        matrix_vs_edge_ode_max_error=flow_error,
        conserved_total_max_error=conservation_error,
        loss_only_normalized_path_max_error=normalized_error,
        minimum_nonnegative_loss_rate=float(loss_rates.min()),
        loss_only_total_at_time_one=math.exp(-2),
    ), indent=2))


if __name__ == '__main__':
    main()
