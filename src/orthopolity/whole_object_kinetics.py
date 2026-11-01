"""Kinetics of whole objects with resource costs one, two and four.

The reactions are 2 X1 <-> X2 and 2 X2 <-> X4.  The ``channel`` mechanism
assigns a fixed rate to each feasible directed reaction.  The ``mass_action``
mechanism assigns forward propensity a*n*(n-1), using the falling-factorial
convention (no factor 1/2), and reverse propensity b*n_product.

This module constructs dynamics without using a stationary-distribution formula.
Resource conservation does not by itself select log-orthopolic or
linear-orthopolic allocation; those comparisons belong to the study protocol.
"""
from __future__ import annotations

from collections import deque
import operator

import numpy as np


COSTS = np.array([1, 2, 4], dtype=np.int64)
# Forward and reverse directions alternate, starting with the monomer reaction.
STEPS = np.array([[-2, 1, 0], [2, -1, 0],
                  [0, -2, 1], [0, 2, -1]], dtype=np.int64)


def _integer(value, name, *, positive=False):
    if isinstance(value, (bool, np.bool_)):
        raise ValueError(f"{name} must be an integer")
    try:
        value = operator.index(value)
    except TypeError as error:
        raise ValueError(f"{name} must be an integer") from error
    if value < (1 if positive else 0) or value > np.iinfo(np.int64).max:
        requirement = "positive" if positive else "nonnegative"
        raise ValueError(f"{name} must be a {requirement} representable integer")
    return value


def _rates(values, name):
    raw = np.asarray(values, dtype=object)
    if raw.shape != (2,) or any(isinstance(x, (bool, np.bool_, str, bytes))
                                for x in raw.flat):
        raise ValueError(f"{name} must contain two positive finite rates")
    try:
        values = np.asarray(values, dtype=float)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError(f"{name} must contain two positive finite rates") from error
    if not np.isfinite(values).all() or np.any(values <= 0):
        raise ValueError(f"{name} must contain two positive finite rates")
    return values


def _parameters(mechanism, forward, reverse):
    if mechanism not in ("channel", "mass_action"):
        raise ValueError("mechanism must be 'channel' or 'mass_action'")
    return _rates(forward, "forward"), _rates(reverse, "reverse")


def _propensities(counts, mechanism, forward, reverse):
    """Return one row per state, with the four directed reaction rates."""
    lower = counts[:, :2].astype(float)
    upper = counts[:, 1:].astype(float)
    rates = np.empty((len(counts), 4), dtype=float)
    with np.errstate(over="ignore", invalid="ignore"):
        if mechanism == "channel":
            rates[:, ::2] = (lower >= 2) * forward
            rates[:, 1::2] = (upper >= 1) * reverse
        else:
            rates[:, ::2] = forward * lower * (lower - 1)
            rates[:, 1::2] = reverse * upper
    if not np.isfinite(rates).all() or not np.isfinite(rates.sum(axis=1)).all():
        raise ValueError("propensities exceed floating-point range")
    return rates


def states_for_budget(budget):
    """Enumerate reachable count vectors by graph traversal, sorted lexically.

    Starting with all resource in monomers makes this independent of a closed
    formula for integer partitions.  Every allowed state can reverse its
    assembly steps to this initial state, so the traversal covers the budget
    class.  The zero-budget class contains only (0, 0, 0).
    """
    budget = _integer(budget, "budget")
    initial = (budget, 0, 0)
    seen = {initial}
    pending = deque([initial])
    while pending:
        state = pending.popleft()
        for step in STEPS:
            candidate = tuple(int(n) + int(d) for n, d in zip(state, step))
            if min(candidate) >= 0 and candidate not in seen:
                seen.add(candidate)
                pending.append(candidate)
    return np.array(sorted(seen), dtype=np.int64)


def generator(budget, mechanism="channel", forward=(1., 1.), reverse=(1., 1.)):
    """Return ``(states, G)`` with column convention G[target, source].

    State probabilities obey dp/dt = G @ p.  Only the four feasible whole-object
    reaction directions enter the generator; its columns sum to zero.
    """
    forward, reverse = _parameters(mechanism, forward, reverse)
    states = states_for_budget(budget)
    index = {tuple(state): i for i, state in enumerate(states)}
    rates = _propensities(states, mechanism, forward, reverse)
    matrix = np.zeros((len(states), len(states)))
    for source, state in enumerate(states):
        for step, rate in zip(STEPS, rates[source]):
            if rate:
                target = index[tuple(state + step)]
                matrix[target, source] += rate
        matrix[source, source] = -rates[source].sum()
    return states, matrix


def generator_stationary(matrix):
    """Solve G @ pi = 0 and sum(pi) = 1, without a detailed-balance formula.

    The supplied column generator must have a unique stationary probability.
    Singleton zero generators are accepted; nonunique systems are rejected.
    """
    matrix = np.asarray(matrix, dtype=float)
    if (matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]
            or not len(matrix) or not np.isfinite(matrix).all()):
        raise ValueError("generator must be a nonempty finite square matrix")
    off_diagonal = matrix.copy()
    np.fill_diagonal(off_diagonal, 0.)
    if np.any(off_diagonal < 0) or np.any(np.diag(matrix) > 0):
        raise ValueError("generator has invalid rate signs")
    scale = float(np.max(np.abs(matrix)))
    if scale == 0:
        if len(matrix) == 1:
            return np.ones(1)
        raise ValueError("generator has no unique stationary probability")
    normalized = matrix / scale
    if not np.allclose(normalized.sum(axis=0), 0., rtol=0., atol=1e-12):
        raise ValueError("generator columns must sum to zero")
    system = normalized.copy()
    system[-1] = 1.
    target = np.zeros(len(matrix))
    target[-1] = 1.
    try:
        probability = np.linalg.solve(system, target)
    except np.linalg.LinAlgError as error:
        raise ValueError("generator has no unique stationary probability") from error
    if (not np.isfinite(probability).all() or np.min(probability) < -1e-11
            or np.max(np.abs(normalized @ probability)) > 1e-10):
        raise ValueError("stationary solve is numerically invalid")
    probability = np.maximum(probability, 0.)
    return probability / probability.sum()


def _initial_states(initial, replicates):
    raw = np.asarray(initial, dtype=object)
    if raw.ndim not in (1, 2) or raw.shape[-1] != 3 or raw.size == 0:
        raise ValueError("initial counts must have shape (3,) or (replicates, 3)")
    counts = np.array([_integer(x, "initial count") for x in raw.flat],
                      dtype=np.int64).reshape(raw.shape)
    if raw.ndim == 1:
        size = 1 if replicates is None else _integer(replicates, "replicates", positive=True)
        counts = np.repeat(counts[None, :], size, axis=0)
    elif replicates is not None and _integer(replicates, "replicates", positive=True) != len(counts):
        raise ValueError("replicates does not match the initial-state rows")
    # Compute in Python integers first so a wrapped int64 budget cannot pass.
    budgets = [sum(int(n) * int(q) for n, q in zip(row, COSTS)) for row in counts]
    if max(budgets) > np.iinfo(np.int64).max or len(set(budgets)) != 1:
        raise ValueError("initial states must share one representable resource budget")
    return counts, budgets[0]


def gillespie_endpoints(initial, duration, mechanism="channel", forward=(1., 1.),
                       reverse=(1., 1.), *, replicates=None, rng=None,
                       max_events=1_000_000):
    """Simulate independent continuous-time paths using actual reaction jumps.

    Return ``(endpoint_counts, event_counts)``.  ``initial`` can be one count
    vector, repeated ``replicates`` times, or one vector per replicate.  All
    replicates must have the same budget.  With ``replicates=None``, use one
    path for a single vector or all supplied rows.  A supplied NumPy Generator
    controls reproducibility.  ``max_events`` limits events on each path;
    exceeding the cap raises instead of silently stopping early.

    Resource conservation and nonnegative counts are checked after every event.
    An event after ``duration`` is not applied.  No samples are drawn directly
    from a stationary distribution or a matrix exponential.
    """
    forward, reverse = _parameters(mechanism, forward, reverse)
    counts, budget = _initial_states(initial, replicates)
    if isinstance(duration, (bool, np.bool_)):
        raise ValueError("duration must be finite and nonnegative")
    try:
        duration = float(duration)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError("duration must be finite and nonnegative") from error
    if not np.isfinite(duration) or duration < 0:
        raise ValueError("duration must be finite and nonnegative")
    max_events = _integer(max_events, "max_events", positive=True)
    if rng is None:
        rng = np.random.default_rng()
    if not isinstance(rng, np.random.Generator):
        raise ValueError("rng must be a NumPy Generator")
    clocks = np.zeros(len(counts))
    events = np.zeros(len(counts), dtype=np.int64)
    if duration == 0:
        return counts, events
    active = np.ones(len(counts), dtype=bool)
    while np.any(active):
        indices = np.flatnonzero(active)
        rates = _propensities(counts[indices], mechanism, forward, reverse)
        totals = rates.sum(axis=1)
        active[indices[totals == 0]] = False
        indices = indices[totals > 0]
        rates = rates[totals > 0]
        totals = totals[totals > 0]
        if not len(indices):
            continue
        with np.errstate(over="ignore"):
            next_clocks = clocks[indices] + rng.exponential(size=len(indices)) / totals
        occurs = next_clocks <= duration
        active[indices[~occurs]] = False
        indices = indices[occurs]
        if not len(indices):
            continue
        if np.any(events[indices] >= max_events):
            raise RuntimeError("Gillespie event cap exceeded before the endpoint")
        cumulative = np.cumsum(rates[occurs], axis=1)
        # Use the same cumulative total for drawing and selecting, and keep the
        # draw strictly below it even if multiplication rounds upward.  This
        # prevents selecting a trailing zero-rate channel.
        choices = np.minimum(rng.random(len(indices)) * cumulative[:, -1],
                             np.nextafter(cumulative[:, -1], 0.))
        cumulative[:, -1] = np.inf
        selected = np.sum(choices[:, None] >= cumulative, axis=1)
        counts[indices] += STEPS[selected]
        clocks[indices] = next_clocks[occurs]
        events[indices] += 1
        if np.any(counts[indices] < 0) or np.any(counts[indices] @ COSTS != budget):
            raise AssertionError("whole-object jump violated resource conservation")
    return counts, events
