"""Reproducible comparison models for resource-spectrum experiments.

Each model takes an explicit ``numpy.random.Generator``. These are generative
models and constructed controls, rather than tests of a universal allocation
law. Distribution exponents refer to continuous densities unless explicitly
named ``survival_exponent``.
"""

import numpy as np


def _integer(value, name, minimum):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)) or value < minimum:
        raise ValueError(f'{name} must be an integer >= {minimum}')
    return int(value)


def preferential_attachment_degrees(n, m, rng):
    """Degrees of an undirected Barabasi--Albert graph with distinct targets.

    Start from a complete graph on ``m + 1`` vertices. Each new vertex attaches
    to ``m`` distinct existing vertices, drawn in proportion to their degrees
    before the insertion. An endpoint urn avoids rebuilding probabilities.
    Memory and expected time are O(n*m) for fixed, sparse ``m``; target
    rejection can be slower for dense graphs. Vertex order is insertion order.
    """
    m = _integer(m, 'm', 1)
    n = _integer(n, 'n', m + 1)
    degree = np.zeros(n, dtype=np.int64)
    degree[:m + 1] = m
    total_degree = 2 * m * n - m * (m + 1)
    urn = np.empty(total_degree, dtype=np.int64)
    seed = np.repeat(np.arange(m + 1), m)
    urn[:len(seed)] = seed
    used = len(seed)
    for vertex in range(m + 1, n):
        targets = set()
        while len(targets) < m:
            targets.add(int(urn[rng.integers(used)]))
        # Sort so reproducibility does not depend on set iteration order.
        chosen = np.asarray(sorted(targets), dtype=np.int64)
        degree[chosen] += 1
        degree[vertex] = m
        urn[used:used + m] = chosen
        urn[used + m:used + 2 * m] = vertex
        used += 2 * m
    return degree


def erdos_renyi_degrees(n, mean_degree, rng):
    """Exact undirected G(n,p) degrees, with p=mean_degree/(n-1).

    Independent geometric gaps skip absent edges in the lower triangle. This
    uses O(n) memory and expected O(n + number_of_edges) time for sparse graphs,
    without allocating an adjacency matrix. ``mean_degree`` is the ensemble
    expectation, rather than a fixed realized degree average.
    """
    n = _integer(n, 'n', 2)
    if not np.isfinite(mean_degree) or not 0 <= mean_degree <= n - 1:
        raise ValueError('mean_degree must be finite and lie in [0, n-1]')
    degree = np.zeros(n, dtype=np.int64)
    p = float(mean_degree) / (n - 1)
    if p == 0:
        return degree
    if p == 1:
        degree.fill(n - 1)
        return degree
    log_no_edge = np.log1p(-p)
    vertex, target = 1, -1
    while vertex < n:
        gap = int(np.floor(np.log1p(-rng.random()) / log_no_edge))
        target += 1 + gap
        while target >= vertex and vertex < n:
            target -= vertex
            vertex += 1
        if vertex < n:
            degree[vertex] += 1
            degree[target] += 1
    return degree


def conservative_exchange(n, sweeps, rng, *, saving=0.0):
    """Random pairwise exchange of a conserved resource, initially one each.

    Every sweep shuffles an even population into disjoint pairs. Each member
    retains the fraction ``saving`` of its holdings, then a uniform random
    split redistributes the remaining pair total. With zero saving the
    invariant joint distribution is uniform on the fixed-total simplex; its
    marginal approaches an exponential at large n. Uniform positive saving
    narrows the stationary distribution, often described as gamma-like, but
    this function makes no claim that its stationary law is exactly Gamma.
    """
    n = _integer(n, 'n', 2)
    sweeps = _integer(sweeps, 'sweeps', 0)
    if n % 2:
        raise ValueError('n must be even for disjoint pair sweeps')
    if not np.isfinite(saving) or not 0 <= saving <= 1:
        raise ValueError('saving must be finite and lie in [0, 1]')
    saving = float(saving)
    resource = np.ones(n, dtype=float)
    for _ in range(sweeps):
        pairs = rng.permutation(n).reshape(-1, 2)
        first, second = pairs[:, 0], pairs[:, 1]
        a, b = resource[first], resource[second]
        exchanged = (1 - saving) * (a + b)
        fraction = rng.random(len(pairs))
        resource[first] = saving * a + fraction * exchanged
        resource[second] = saving * b + (1 - fraction) * exchanged
    return resource


def bounded_multiplicative_growth(n, steps, drift, diffusion, rng):
    """Multiplicative growth with a lower boundary at size one.

    The log size follows z <- max(0, z + drift + diffusion*Normal(0,1)),
    starting at zero. Negative drift gives a stationary reflected random walk.
    Its stationary upper-tail survival exponent solves E[A**kappa]=1 for
    lognormal multiplier A, giving kappa=-2*drift/diffusion**2. Thus the
    asymptotic size-density exponent is 1+kappa. The same exponent describes
    the continuous reflected-Brownian comparison, whose full log-size law is
    exponential. The discrete model has a boundary atom, and neither its full
    stationary profile nor a finite-step sample is an exact pure power law.
    """
    n = _integer(n, 'n', 1)
    steps = _integer(steps, 'steps', 0)
    if not np.isfinite([drift, diffusion]).all() or drift >= 0 or diffusion <= 0:
        raise ValueError('Finite negative drift and positive diffusion required')
    log_size = np.zeros(n, dtype=float)
    for _ in range(steps):
        log_size = np.maximum(0, log_size + drift + diffusion * rng.standard_normal(n))
    with np.errstate(over='raise'):
        return np.exp(log_size)


def joint_feasibility_samples(n, resources, shared_rate, rng):
    """Constructed common-shock resource capacities and feasible sizes.

    Let Z be exponential with rate theta=``shared_rate`` and each U_a
    independently exponential with rate 1-theta. Define X_a=exp(min(Z,U_a))
    and feasible size K=min_a X_a. Every capacity has survival P(X_a>=k)=k^-1
    for k>=1, while K has survival exponent m-(m-1)*theta. Zero-rate variables
    are treated as infinity, allowing independent and identical endpoints.
    Dependence changes the joint feasibility exponent while preserving each
    marginal. This is an illustrative construction, not an empirical law.
    """
    n = _integer(n, 'n', 1)
    resources = _integer(resources, 'resources', 1)
    if not np.isfinite(shared_rate) or not 0 <= shared_rate <= 1:
        raise ValueError('shared_rate must be finite and lie in [0, 1]')
    theta = float(shared_rate)
    shared = (rng.exponential(1 / theta, size=(n, 1))
              if theta > 0 else np.full((n, 1), np.inf))
    independent = (rng.exponential(1 / (1 - theta), size=(n, resources))
                   if theta < 1 else np.full((n, resources), np.inf))
    log_capacities = np.minimum(shared, independent)
    with np.errstate(over='raise'):
        capacities = np.exp(log_capacities)
    return dict(capacities=capacities, size=capacities.min(axis=1),
                log_capacities=log_capacities,
                survival_exponent=float(resources - (resources - 1) * theta),
                marginal_exponent=1.0)


def inverse_cost_samples(n, lo, hi, d, allocation_tilt, rng):
    """Exact bounded control with PDF p(x) proportional to x^-alpha.

    With independently declared cost q(x)=x**d and resource allocated per
    logarithmic interval proportional to x**allocation_tilt, accounting gives
    alpha=d+1-allocation_tilt. This generator builds that allocation into its
    distribution, so agreement with it checks the framework implementation,
    rather than providing independent evidence for equal resource allocation.
    """
    n = _integer(n, 'n', 1)
    if not np.isfinite([lo, hi, d, allocation_tilt]).all() or lo <= 0 or hi <= lo:
        raise ValueError('Finite parameters and a positive increasing domain required')
    exponent = float(allocation_tilt - d)  # 1-alpha
    if not np.isfinite(exponent):
        raise ValueError('Exponent must be finite')
    log_lo, log_hi = np.log(lo), np.log(hi)
    width = log_hi - log_lo
    uniform = rng.random(n)
    if exponent == 0:
        log_offset = uniform * width
    elif abs(exponent * width) < 1:
        log_offset = np.log1p(uniform * np.expm1(exponent * width)) / exponent
    else:
        with np.errstate(divide='ignore'):
            log_offset = np.logaddexp(np.log1p(-uniform),
                                       np.log(uniform) + exponent * width) / exponent
    return np.clip(np.exp(log_lo + log_offset), lo, hi)
