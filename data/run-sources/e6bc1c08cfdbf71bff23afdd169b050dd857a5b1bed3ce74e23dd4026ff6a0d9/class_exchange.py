"""Conservative exchange of resource between fixed concentration classes.

The state is class resource, not an object census.  For reference widths w,
symmetric conductances G, and prescribed potential V, the rate from i to j is
G[i,j] / w[i] * exp(max(V[i] - V[j], 0)).  A[j,i] contains that rate, so A acts
on column states.  Extra downhill transitions preserve all neutral transitions.
"""
from __future__ import annotations

import numpy as np
from scipy.linalg import expm
from scipy.special import logsumexp


def _vector(values, name, *, positive=False):
    result = np.asarray(values, dtype=float)
    if result.ndim != 1 or not result.size or not np.isfinite(result).all():
        raise ValueError(f"{name} must be a nonempty finite vector")
    if positive and np.any(result <= 0):
        raise ValueError(f"{name} must be strictly positive")
    return result


def _potential(weights, potential):
    result = np.zeros_like(weights) if potential is None else _vector(potential, "potential")
    if result.shape != weights.shape:
        raise ValueError("potential and weights must have the same shape")
    return result


def equilibrium(weights, potential=None):
    """Return the normalized resource equilibrium pi_i ∝ w_i exp(-V_i).

    Connected conductances make it the unique equilibrium. Disconnected graphs
    retain their initial component totals and need not converge to this vector.
    """
    weights = _vector(weights, "weights", positive=True)
    potential = _potential(weights, potential)
    log_pi = np.log(weights) - (potential - np.min(potential))
    pi = np.exp(log_pi - logsumexp(log_pi))
    if np.any(pi == 0) or not np.isfinite(pi).all():
        raise ValueError("potential range exceeds representable positive equilibrium")
    return pi


def generator(weights, conductances, potential=None):
    """Build a column generator: A[j,i] is the rate from class i to j."""
    weights = _vector(weights, "weights", positive=True)
    potential = _potential(weights, potential)
    conductances = np.asarray(conductances, dtype=float)
    n = len(weights)
    if conductances.shape != (n, n) or not np.isfinite(conductances).all():
        raise ValueError("conductances must be a finite square matrix matching weights")
    if np.any(conductances < 0) or np.any(np.diag(conductances) != 0):
        raise ValueError("conductances must be nonnegative with zero diagonal")
    if not np.allclose(conductances, conductances.T, rtol=1e-13, atol=0):
        raise ValueError("conductances must be symmetric")
    # Evaluate exponentials only on edges, avoiding irrelevant large differences.
    source, destination = np.nonzero(conductances)
    with np.errstate(over="ignore", invalid="ignore"):
        rates = conductances[source, destination] / weights[source] * np.exp(
            np.maximum(potential[source] - potential[destination], 0))
    if not np.isfinite(rates).all():
        raise ValueError("rates exceed floating-point range")
    matrix = np.zeros((n, n))
    matrix[destination, source] = rates
    np.fill_diagonal(matrix, -matrix.sum(axis=0))
    return _generator(matrix)


def _generator(matrix):
    matrix = np.asarray(matrix, dtype=float)
    if (matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]
            or not matrix.size or not np.isfinite(matrix).all()):
        raise ValueError("generator must be a nonempty finite square matrix")
    off_diagonal = matrix.copy()
    np.fill_diagonal(off_diagonal, 0)
    if np.any(off_diagonal < 0) or np.any(np.diag(matrix) > 0):
        raise ValueError("generator has an invalid rate sign")
    scale = max(1., float(np.abs(matrix).max()))
    if not np.allclose(matrix.sum(axis=0), 0, rtol=0, atol=1e-12 * scale):
        raise ValueError("generator columns must sum to zero")
    return matrix


def spectral_gap(matrix, pi):
    """Return the reversible relaxation gap; disconnected graphs return zero."""
    matrix = _generator(matrix)
    pi = _vector(pi, "pi", positive=True)
    if len(pi) != len(matrix) or not np.isclose(pi.sum(), 1., rtol=0, atol=1e-12):
        raise ValueError("pi must be a normalized stationary distribution")
    flux = matrix * pi[None, :]
    if not np.allclose(flux, flux.T, rtol=1e-10, atol=1e-13):
        raise ValueError("generator must satisfy detailed balance with pi")
    reached = {0}
    pending = [0]
    while pending:
        source = pending.pop()
        for destination in np.flatnonzero(matrix[:, source] > 0):
            if int(destination) not in reached:
                reached.add(int(destination))
                pending.append(int(destination))
    if len(reached) != len(pi) or len(pi) < 2:
        return 0.
    symmetric = -matrix * np.sqrt(pi)[None, :] / np.sqrt(pi)[:, None]
    eigenvalues = np.linalg.eigvalsh((symmetric + symmetric.T) / 2)
    gap = float(eigenvalues[1])
    if gap <= 0:
        raise ValueError("positive gap could not be resolved numerically")
    return gap


def transition_matrix(matrix, elapsed):
    """Return exp(A t); correct only numerical roundoff to stochastic columns."""
    matrix = _generator(matrix)
    if not np.isfinite(elapsed) or elapsed < 0:
        raise ValueError("elapsed time must be finite and nonnegative")
    transition = expm(matrix * elapsed)
    if (not np.isfinite(transition).all() or transition.min() < -1e-11
            or not np.allclose(transition.sum(axis=0), 1, rtol=0, atol=1e-9)):
        raise ValueError("matrix exponential failed probability validation")
    transition = np.maximum(transition, 0)
    return transition / transition.sum(axis=0, keepdims=True)


def evolve(matrix, resource, times):
    """Return exact deterministic checkpoints exp(A t) R(0), one row per time."""
    matrix = _generator(matrix)
    resource = _vector(resource, "resource")
    times = _vector(times, "times")
    if len(resource) != len(matrix) or np.any(resource < 0) or np.any(times < 0):
        raise ValueError("resource must match the generator and resource/times must be nonnegative")
    return np.array([transition_matrix(matrix, float(t)) @ resource for t in times])


def relative_l2(shares, pi):
    """Weighted relative L2 distance sqrt(sum_i (p_i-pi_i)^2 / pi_i)."""
    shares = np.asarray(shares, dtype=float)
    pi = _vector(pi, "pi", positive=True)
    if shares.ndim < 1 or shares.shape[-1] != len(pi) or not np.isfinite(shares).all():
        raise ValueError("shares must have pi's length on the final axis")
    if (np.any(shares < 0) or not np.allclose(shares.sum(axis=-1), 1, rtol=0, atol=1e-10)
            or not np.isclose(pi.sum(), 1, rtol=0, atol=1e-12)):
        raise ValueError("shares and pi must be probability distributions")
    return np.sqrt(np.sum((shares - pi) ** 2 / pi, axis=-1))


def advance_quanta(counts, transition, rng):
    """Move independent equal-resource quanta by exact checkpoint transitions.

    ``counts`` is an integer vector or (replicates, classes) array. For each
    source class, destinations are sampled jointly from its multinomial column.
    Quanta are resource packets; they are not objects with class-dependent q_i.
    """
    counts = np.asarray(counts)
    if (counts.ndim not in (1, 2) or not np.issubdtype(counts.dtype, np.integer)
            or np.any(counts < 0) or not counts.size):
        raise ValueError("counts must be nonnegative integer class counts")
    transition = np.asarray(transition, dtype=float)
    n = counts.shape[-1]
    if (transition.shape != (n, n) or not np.isfinite(transition).all()
            or np.any(transition < 0)
            or not np.allclose(transition.sum(axis=0), 1, rtol=0, atol=1e-12)):
        raise ValueError("transition must have nonnegative stochastic columns")
    batched = counts[None, :] if counts.ndim == 1 else counts
    updated = np.zeros_like(batched, dtype=np.int64)
    for source in range(n):
        updated += rng.multinomial(batched[:, source], transition[:, source])
    return updated[0] if counts.ndim == 1 else updated
