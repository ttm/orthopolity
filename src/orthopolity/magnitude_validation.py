"""Synthetic observation models; this module never reads earthquake catalogues."""
from __future__ import annotations

import numpy as np
from scipy.stats import exponnorm

BIN = 0.1
LOG10E = 1 / np.log(10)


def validate_model(model):
    values = [model['intercept'], model['slope'], model.get('true_slope', model['slope']),
              model['source_sigma']]
    if not np.isfinite(values).all() or min(values[1:3]) <= 0 or values[3] < 0:
        raise ValueError('Finite coefficients, positive slopes and nonnegative scatter required')


def observed_bins(ticks, model):
    """Original source tenths -> published proxy hundredths -> registered tenths."""
    ticks = np.asarray(ticks)
    return np.round(np.round(model['intercept'] + model['slope'] * BIN * ticks, 2), 1)


def simulate_source_ticks(b, lower, n, model, rng):
    validate_model(model)
    if b <= 0 or n < 1 or not np.isfinite([b, lower]).all():
        raise ValueError('Positive b and n and finite lower support required')
    true_mw = lower + rng.exponential(LOG10E / b, n)
    source = (true_mw - model['intercept']) / model.get('true_slope', model['slope'])
    if model['source_sigma']:
        source += rng.normal(0, model['source_sigma'], n)
    # Match np.round(source, 1), not a distinct floor/half-up rule.
    return np.rint(np.round(source, 1) / BIN).astype(np.int64)


def registered_summary(magnitudes, rng, n_boot=500, minimum=200):
    """Original MAXC/point statistic; exact conditional event-bootstrap distribution.

    Multinomial bin counts avoid allocating 500 copies of the full event vector.
    Random draws differ from the old runner; their distribution is identical.
    """
    m = np.round(np.asarray(magnitudes, dtype=float), 1)
    if not len(m) or not np.isfinite(m).all():
        raise ValueError('Nonempty finite magnitudes required')
    vals, counts = np.unique(m, return_counts=True)
    mc = float(vals[np.argmax(counts)] + 0.2)
    selected = vals >= mc - 1e-9
    vals, counts = vals[selected], counts[selected]
    n = int(counts.sum())
    result = dict(mc=mc, n_complete=n, eligible=n >= minimum)
    if n < minimum:
        return result
    mean = np.dot(vals, counts) / n
    b = LOG10E / (mean - (mc - 0.05))
    samples = rng.multinomial(n, counts / n, size=n_boot)
    boot_b = LOG10E / (samples @ vals / n - (mc - 0.05))
    se = float(np.std(boot_b, ddof=1))
    return dict(result, b=float(b), se=se, ci_low=float(b-1.96*se), ci_high=float(b+1.96*se))


def first_accepted_tick(mc, model):
    """Invert the monotone, twice-rounded observation map at the inclusion boundary."""
    centre = int(np.floor((mc - model['intercept']) / model['slope'] / BIN))
    ticks = np.arange(centre-5, centre+6)
    accepted = observed_bins(ticks, model) >= mc-1e-9
    if accepted[0] or not accepted[-1]:
        raise ValueError('Observation boundary outside bracketing bins')
    return int(ticks[np.flatnonzero(accepted)[0]])


def source_grid_estimate(ticks, mc, model):
    first = first_accepted_tick(mc, model)
    selected = np.asarray(ticks)[observed_bins(ticks, model) >= mc-1e-9]
    if not len(selected) or np.mean(selected-first) <= 0:
        return None
    return float(np.log1p(1 / np.mean(selected-first)) / (model['slope']*BIN*np.log(10)))


def population_limit(b, lower, model):
    """Independent CDF integration over source bins, including optional Gaussian error.

    Integrate far beyond both tails. No simulated data or fitted b enters here.
    """
    validate_model(model)
    true_beta = model.get('true_slope', model['slope'])
    loc = (lower-model['intercept']) / true_beta
    sigma = model['source_sigma']
    rate = b*np.log(10)*true_beta
    first = int(np.floor((loc-10*sigma) / BIN))-2
    last = int(np.ceil((loc+32/rate+10*sigma) / BIN))+2
    ticks = np.arange(first, last+1)
    edges = BIN * (np.arange(first, last+2)-0.5)
    if sigma:
        cdf = exponnorm.cdf(edges, 1/(rate*sigma), loc=loc, scale=sigma)
    else:
        cdf = -np.expm1(-rate*np.maximum(edges-loc, 0))
    probabilities = np.diff(cdf)
    mass = probabilities.sum()
    if abs(1-mass) > 1e-12 or probabilities.min() < -1e-14:
        raise ValueError('Invalid or insufficiently integrated bin probabilities')
    magnitudes = observed_bins(ticks, model)
    values, inverse = np.unique(magnitudes, return_inverse=True)
    aggregate = np.bincount(inverse, weights=probabilities)
    mc = float(values[np.argmax(aggregate)] + 0.2)
    accepted = magnitudes >= mc-1e-9
    selected_mass = probabilities[accepted].sum()
    mean = np.dot(magnitudes[accepted], probabilities[accepted]) / selected_mass
    estimate = LOG10E / (mean-(mc-0.05))
    first_tick = first_accepted_tick(mc, model)
    mean_k = np.dot(ticks[accepted]-first_tick, probabilities[accepted]) / selected_mass
    grid = np.log1p(1/mean_k) / (model['slope']*BIN*np.log(10))
    return dict(mc=mc, b_limit=float(estimate), bias_limit=float(estimate-b),
                grid_b_limit=float(grid), selected_mass=float(selected_mass),
                integrated_mass=float(mass), mode_gap=float(np.diff(np.sort(aggregate)[-2:])[0]),
                lowest_accepted_source_edge=float((first_tick-0.5)*BIN),
                true_source_lower=float(loc))


def wilson_interval(successes, n):
    if not n:
        return [None, None]
    p, z = successes/n, 1.96
    centre = (p+z*z/(2*n))/(1+z*z/n)
    radius = z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/(1+z*z/n)
    return [float(centre-radius), float(centre+radius)]


def gate_cell(eligible, total, bias, coverage, gate):
    return bool(eligible/total >= gate['minimum_eligibility_rate']
                and bias is not None and abs(bias) <= gate['max_absolute_mean_bias']
                and coverage is not None and coverage >= gate['minimum_coverage'])
