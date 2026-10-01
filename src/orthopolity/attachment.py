"""Attachment trees with a fixed wedge resource and explicit references.

All generators add one link per vertex to a seed edge. This m=1 model is
consistent with the recurrence used here; it is not an m=2 reference. Kernels
are A(k)=k**gamma+attractiveness, k>=1. Nonlinear normalizers are random, so
the exact finite expectation recurrence is deliberately restricted to gamma
zero and one. Sublinear comparisons use a separately labelled limiting law.
"""
import numpy as np
from scipy.optimize import brentq


def _validate_kernel(gamma, attractiveness):
    if not np.isfinite([gamma, attractiveness]).all() or gamma < 0 or attractiveness <= -1:
        raise ValueError('Finite gamma >= 0 and attractiveness > -1 required')
    return float(gamma), float(attractiveness)


def _validate_sizes(sizes):
    values = list(sizes)
    if not values or any(isinstance(v, (bool, np.bool_)) or not isinstance(v, (int, np.integer)) or v < 2 for v in values):
        raise ValueError('Graph sizes must be integers >= 2')
    if any(b <= a for a, b in zip(values, values[1:])):
        raise ValueError('Graph sizes must be strictly increasing')
    return [int(v) for v in values]


def attachment_tree_snapshots(sizes, gamma, rng, *, attractiveness=0.0):
    """Nested degree snapshots from exact weighted random attachment.

    A Fenwick tree stores current vertex weights, giving O(n log n) time and
    O(n) working memory. Every insertion draws an existing vertex proportional
    to A(k), increases its degree, and adds a degree-one vertex. The snapshots
    share a growth history; independent Generators give independent histories.
    """
    sizes = _validate_sizes(sizes)
    gamma, attractiveness = _validate_kernel(gamma, attractiveness)
    n = sizes[-1]
    tree = np.zeros(n + 1, dtype=float)
    degree = np.ones(n, dtype=np.int64)
    first_bit = 1 << (n.bit_length() - 1)

    def add(index, amount):
        index += 1
        while index <= n:
            tree[index] += amount
            index += index & -index

    initial_weight = 1 + attractiveness
    add(0, initial_weight)
    add(1, initial_weight)
    total = 2 * initial_weight
    snapshots = {2: degree[:2].copy()} if sizes[0] == 2 else {}
    requested = set(sizes)
    for vertex in range(2, n):
        draw = rng.random() * total
        index, bit = 0, first_bit
        while bit:
            probe = index + bit
            if probe <= n and tree[probe] <= draw:
                index = probe
                draw -= tree[probe]
            bit >>= 1
        target = index
        if target >= vertex:
            raise FloatingPointError('Weighted sampler reached an inactive vertex')
        old_degree = int(degree[target])
        degree[target] += 1
        increment = float((old_degree + 1) ** gamma - old_degree ** gamma)
        if not np.isfinite(increment):
            raise ValueError('Kernel weights overflow at this graph size')
        if increment:
            add(target, increment)
        add(vertex, initial_weight)
        total += increment + initial_weight
        if vertex + 1 in requested:
            snapshots[vertex + 1] = degree[:vertex + 1].copy()
    return snapshots


def attachment_tree_degrees(n, gamma, rng, *, attractiveness=0.0):
    """Single graph endpoint; see ``attachment_tree_snapshots``."""
    return attachment_tree_snapshots([n], gamma, rng, attractiveness=attractiveness)[n]


def finite_expected_degree_snapshots(sizes, max_degree, *, gamma=1.0, attractiveness=0.0):
    """Exact finite expected counts for constant or affine attachment kernels.

    With t vertices, the kernel sum is deterministic: (1+a)t for gamma=0,
    and (2+a)t-2 for gamma=1. Conditional count transitions therefore close
    exactly after expectation. Counts below ``max_degree`` need no closure for
    the untracked upper tail: degree only increases and the total kernel is
    known. Tail counts, tail degree, and full expected wedge resource are
    returned separately. This function rejects nonlinear expectation closure.
    """
    sizes = _validate_sizes(sizes)
    gamma, attractiveness = _validate_kernel(gamma, attractiveness)
    if gamma not in (0.0, 1.0):
        raise ValueError('Exact finite expectation requires gamma=0 or gamma=1')
    if isinstance(max_degree, (bool, np.bool_)) or not isinstance(max_degree, (int, np.integer)) or max_degree < 1:
        raise ValueError('max_degree must be a positive integer')
    k = np.arange(1, int(max_degree) + 1, dtype=float)
    kernel = k ** gamma + attractiveness
    counts = np.zeros(len(k), dtype=float)
    counts[0] = 2
    wedges = 0.0
    snapshots = {}
    requested = set(sizes)

    def capture(t):
        snapshots[t] = dict(degree=k.copy(), expected_count=counts.copy(),
            unrepresented_expected_count=max(0.0, float(t - counts.sum())),
            unrepresented_expected_degree=max(0.0, float(2 * (t - 1) - np.dot(k, counts))),
            expected_full_wedges=float(wedges),
            kind='exact finite discrete expectation')

    if 2 in requested:
        capture(2)
    for t in range(2, sizes[-1]):
        denominator = (1 + attractiveness) * t if gamma == 0 else (2 + attractiveness) * t - 2
        flow = kernel * counts / denominator
        counts -= flow
        counts[1:] += flow[:-1]
        counts[0] += 1
        if gamma == 0:
            wedges += 2 * (t - 1) / t
        else:
            wedges += (2 * wedges + (1 + attractiveness) * 2 * (t - 1)) / denominator
        if t + 1 in requested:
            capture(t + 1)
    return snapshots


def stationary_degree_law(gamma, max_degree=4096, *, attractiveness=0.0):
    """Limiting degree probabilities for sublinear or affine tree growth.

    Write mu=lim sum_i A(k_i)/n. The recurrence is p_1=mu/(mu+A(1)),
    p_k=A(k-1)*p_(k-1)/(mu+A(k)). For gamma<1, solve the truncated
    self-consistency mu=sum A(k)*p_k with its omitted tail reported, without
    renormalizing probabilities. For gamma=1, mu=2+a is known exactly.
    Nonlinear superlinear kernels have condensation and are rejected here.
    """
    gamma, attractiveness = _validate_kernel(gamma, attractiveness)
    if gamma > 1:
        raise ValueError('Superlinear condensation has no reference of this form')
    if isinstance(max_degree, (bool, np.bool_)) or not isinstance(max_degree, (int, np.integer)) or max_degree < 2:
        raise ValueError('max_degree must be an integer >= 2')
    k = np.arange(1, int(max_degree) + 1, dtype=float)
    kernel = k ** gamma + attractiveness

    def probabilities(mu):
        ratios = kernel[:-1] / (mu + kernel[1:])
        p = np.empty_like(k)
        p[0] = mu / (mu + kernel[0])
        p[1:] = p[0] * np.cumprod(ratios)
        return p

    if gamma == 1:
        mu = 2 + attractiveness
    elif gamma == 0:
        mu = 1 + attractiveness
    else:
        lower, upper = 1 + attractiveness, 2 ** gamma + attractiveness
        def residual(mu):
            return np.dot(kernel, probabilities(mu)) - mu
        if residual(lower) <= 0:
            raise ValueError('Reference cutoff is too small for self-consistency')
        mu = brentq(residual, lower, upper, xtol=1e-13)
    p = probabilities(mu)
    missing = max(0.0, float(1 - p.sum()))
    if gamma < 1 and missing > 1e-9:
        raise ValueError('Sublinear reference cutoff leaves appreciable probability mass')
    return dict(degree=k, probability=p, normalizer=float(mu),
                unrepresented_probability=missing,
                represented_mean_degree=float(np.dot(k, p)),
                kind='limiting discrete degree law; not exact finite expectation')
