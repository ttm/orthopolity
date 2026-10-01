"""Frozen intervention predictions and legitimate categorical sampling targets.

Uniform object sampling targets normalized object counts. Resource-proportional
sampling targets cost-weighted counts. The latter is an observation design,
not a conserved sample budget. Model rejection and forced likelihood selection
are separate operations throughout this module.
"""
from __future__ import annotations

import numpy as np
from scipy.special import xlogy
from scipy.stats import norm

from orthopolity.restrictions import proportional_fair_allocation, neutral_resource_projection


def _probabilities(values):
    p = np.asarray(values, dtype=float)
    if p.ndim != 2 or np.any(~np.isfinite(p)) or np.any(p <= 0) or not np.allclose(p.sum(axis=-1), 1, atol=1e-12, rtol=0):
        raise ValueError('Strictly positive, normalized cohort-by-class probabilities required')
    return p


def _cost_vector(values, classes, name):
    q = np.asarray(values, dtype=float)
    if q.shape != (classes,) or np.any(~np.isfinite(q)) or np.any(q <= 0):
        raise ValueError(f'{name} must be a finite positive class vector')
    return q


def intervention_allocations(costs, weights, primary_budget, auxiliary_budgets, *, extra_weights=None):
    """Before/after allocations with the same binding physical budgets.

    Counts are continuous intensities. Scaling population opportunities changes
    their normalization but not the sampling probabilities. An optional third
    objective uses declared alternative class weights in proportional fairness.
    """
    q = np.asarray(costs, dtype=float)
    b = np.asarray(auxiliary_budgets, dtype=float)
    if q.ndim != 2 or q.shape[0] != 2 or b.shape != (2,):
        raise ValueError('Two resource costs and two intervention budgets required')
    predictions = {'pf': [], 'kl': []}
    totals = {'pf': [], 'kl': []}
    if extra_weights is not None:
        predictions['extra'] = []
        totals['extra'] = []
    for auxiliary in b:
        pf = proportional_fair_allocation(q, [primary_budget, auxiliary], weights)
        kl = neutral_resource_projection(*q, primary_budget, auxiliary, weights)
        candidates = {'pf': pf, 'kl': kl}
        if extra_weights is not None:
            candidates['extra'] = proportional_fair_allocation(q, [primary_budget, auxiliary], extra_weights)
        for name, candidate in candidates.items():
            target = np.array([primary_budget, auxiliary])
            if not np.allclose(candidate['resource_totals'], target, rtol=1e-8, atol=1e-10):
                raise ValueError(f'{name} does not use the same binding budgets at this intervention')
            predictions[name].append(candidate['counts'])
            totals[name].append(candidate['resource_totals'])
    return {name: dict(counts=np.asarray(value), resource_totals=np.asarray(totals[name]))
            for name, value in predictions.items()}


def observation_probabilities(counts, primary_cost, *, sampling='objects'):
    """Object or primary-resource sampling probabilities for each cohort.

    For object intensities N_j and known primary cost q_j, uniform objects have
    probability N_j/sum N. Drawing objects proportional to primary cost instead
    gives q_j*N_j/sum(q*N). Every draw is independent conditional on the cohort.
    """
    counts = np.asarray(counts, dtype=float)
    if counts.ndim != 2 or np.any(~np.isfinite(counts)) or np.any(counts < 0):
        raise ValueError('Nonnegative finite cohort-by-class intensities required')
    q = _cost_vector(primary_cost, counts.shape[-1], 'primary_cost')
    if sampling not in ('objects', 'primary_resource'):
        raise ValueError('Unknown sampling design')
    mass = counts if sampling == 'objects' else counts*q
    if np.any(mass.sum(axis=-1) <= 0):
        raise ValueError('Each cohort must have positive intensity')
    return mass/mass.sum(axis=-1, keepdims=True)


def resource_probability_from_sample(counts, primary_cost, *, sampling='objects'):
    """Estimate primary resource from sampled objects with known propensities.

    For sampling propensity s_j, resource weights are q_j/s_j. Uniform objects
    use s=1 and explicitly weight each observed object by q. Resource sampling
    uses s=q, so these weights cancel. Applying q again to that design would
    estimate a second-moment quantity rather than primary resource allocation.
    The normalized ratio estimator has finite-sample bias under object sampling.
    """
    c = np.asarray(counts, dtype=float)
    if c.ndim < 1 or np.any(~np.isfinite(c)) or np.any(c < 0):
        raise ValueError('Finite nonnegative observed counts required')
    q = _cost_vector(primary_cost, c.shape[-1], 'primary_cost')
    if sampling not in ('objects', 'primary_resource'):
        raise ValueError('Unknown sampling design')
    propensity = np.ones_like(q) if sampling == 'objects' else q
    resource = c*(q/propensity)
    total = resource.sum(axis=-1, keepdims=True)
    if np.any(total <= 0):
        raise ValueError('Each sampled cohort must contain positive resource')
    return resource/total


def multinomial_samples(probability, sample_size, replicates, rng):
    """Independent cohorts with shape (replicate, cohort, class)."""
    p = _probabilities(probability)
    for value, name in ((sample_size, 'sample_size'), (replicates, 'replicates')):
        if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)) or value < 1:
            raise ValueError(f'{name} must be a positive integer')
    return np.stack([rng.multinomial(sample_size, row, size=replicates) for row in p], axis=1)


def multinomial_deviance(counts, probability):
    """Joint multinomial deviance against a completely frozen probability law.

    Zero observed classes contribute zero; they are retained. No parameter is
    fitted from these observations. Null calibration is done by simulation,
    rather than a chi-square approximation for sparse counts.
    """
    p = _probabilities(probability)
    c = np.asarray(counts, dtype=float)
    if c.ndim < 2 or c.shape[-2:] != p.shape or np.any(~np.isfinite(c)) or np.any(c < 0) or np.any(c != np.floor(c)):
        raise ValueError('Aligned nonnegative integer cohort counts required')
    size = c.sum(axis=-1, keepdims=True)
    if np.any(size <= 0):
        raise ValueError('Cohort samples must be nonempty')
    expected = size*p
    return 2*np.sum(xlogy(c, c/expected), axis=(-2, -1))


def log_likelihood_ratio(counts, pf_probability, kl_probability, *, by_cohort=False):
    """PF-minus-KL log likelihood, with common multinomial constants cancelled."""
    pf, kl = _probabilities(pf_probability), _probabilities(kl_probability)
    c = np.asarray(counts, dtype=float)
    if pf.shape != kl.shape or c.ndim < 2 or c.shape[-2:] != pf.shape or np.any(~np.isfinite(c)) or np.any(c < 0) or np.any(c != np.floor(c)):
        raise ValueError('Aligned candidate probabilities and observed counts required')
    values = np.sum(c*np.log(pf/kl), axis=-1)
    return values if by_cohort else values.sum(axis=-1)


def expected_log_likelihood_ratio(truth_probability, pf_probability, kl_probability, sample_size):
    """Exact mean and variance under independent fixed-size cohort sampling."""
    truth, pf, kl = (_probabilities(p) for p in (truth_probability, pf_probability, kl_probability))
    if truth.shape != pf.shape or truth.shape != kl.shape or not np.isfinite(sample_size) or sample_size <= 0:
        raise ValueError('Aligned probabilities and positive sample size required')
    score = np.log(pf/kl)
    mean = np.sum(truth*score, axis=-1)
    variance = np.sum(truth*score**2, axis=-1)-mean**2
    return dict(cohort_mean=sample_size*mean,
                mean=float(sample_size*mean.sum()),
                variance=float(sample_size*np.maximum(variance,0).sum()))


def monte_carlo_rank_pvalue(statistics, calibration_statistics):
    """Upper-tail Monte Carlo p=(1+# calibration>=observed)/(R+1).

    The +1 includes the observation in its exchangeability rank. Ties make the
    test conservative. Calibration and evaluation must be independent draws;
    a frozen calibration set can be reused for held-out design simulations.
    """
    null = np.asarray(calibration_statistics, dtype=float)
    observed = np.asarray(statistics, dtype=float)
    if null.ndim != 1 or not null.size or np.any(~np.isfinite(null)) or np.any(~np.isfinite(observed)):
        raise ValueError('Finite observed statistics and nonempty finite calibration required')
    ordered = np.sort(null)
    preceding = np.searchsorted(ordered, observed, side='left')
    return (1+len(ordered)-preceding)/(len(ordered)+1)


def decision_outcomes(pf_pvalue, kl_pvalue, candidate_alpha):
    """Four outcomes: pf, kl, ambiguous, or both_rejected."""
    pf, kl = np.asarray(pf_pvalue), np.asarray(kl_pvalue)
    if pf.shape != kl.shape or not 0 < candidate_alpha < 1 or np.any(~np.isfinite(pf)) or np.any(~np.isfinite(kl)) or np.any((pf < 0) | (pf > 1)) or np.any((kl < 0) | (kl > 1)):
        raise ValueError('Aligned finite p-values and alpha in (0,1) required')
    accepted_pf, accepted_kl = pf > candidate_alpha, kl > candidate_alpha
    return np.where(accepted_pf & ~accepted_kl, 'pf',
                    np.where(accepted_kl & ~accepted_pf, 'kl',
                             np.where(accepted_pf & accepted_kl, 'ambiguous', 'both_rejected')))


def wilson_interval(successes, trials, level=.95):
    """Binomial Monte Carlo interval conditional on frozen calibration."""
    if trials < 1 or not 0 <= successes <= trials or not 0 < level < 1:
        raise ValueError('Valid successes, trials, and interval level required')
    z = float(norm.ppf((1+level)/2)); p = successes/trials
    denominator = 1+z*z/trials
    center = (p+z*z/(2*trials))/denominator
    radius = z*np.sqrt(p*(1-p)/trials+z*z/(4*trials*trials))/denominator
    return float(center-radius), float(center+radius)
