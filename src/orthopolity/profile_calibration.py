"""Three-way decisions for a normalized complete resource profile.

Centered bootstrap bands are approximate and require a sampling model. The
optional Hoeffding reference has a finite-sample guarantee only for independent
bounded blocks with externally specified almost-sure resource bounds. Neither
method repairs detection bias or dependence not represented by its design.
"""
from __future__ import annotations

import numpy as np


METHODS = ['centered_bootstrap', 'percentile_delta_extension', 'known_bound']


def _inputs(resource_blocks, widths):
    blocks = np.asarray(resource_blocks, dtype=float)
    widths = np.asarray(widths, dtype=float)
    if blocks.ndim not in (2, 3) or blocks.shape[-2] < 2 or blocks.shape[-1] < 2:
        raise ValueError('At least two complete blocks and two bins required')
    if np.any(~np.isfinite(blocks)) or np.any(blocks < 0):
        raise ValueError('Finite nonnegative complete block resource totals required; retain zeros')
    if widths.shape != (blocks.shape[-1],) or np.any(~np.isfinite(widths)) or np.any(widths <= 0):
        raise ValueError('Finite positive logarithmic widths aligned with all bins required')
    return blocks, widths


def normalized_profile(resource_means, log_widths):
    """Normalize pooled resource density once, retaining every zero bin.

    For means mu_j of resource totals and widths w_j, phi_j is
    (sum w)*mu_j / (w_j*sum mu). An all-zero observation has no defined
    positive-total normalization and is explicitly marked unavailable.
    """
    means = np.asarray(resource_means, dtype=float)
    widths = np.asarray(log_widths, dtype=float)
    total = means.sum(axis=-1, keepdims=True)
    with np.errstate(divide='ignore', invalid='ignore'):
        phi = means*widths.sum()/(widths*total)
        log_phi = np.log(phi)
    invalid_total = np.squeeze(total <= 0, axis=-1)
    phi = np.where(np.expand_dims(invalid_total, -1), 0, phi)
    log_phi = np.where(np.expand_dims(invalid_total, -1), -np.inf, log_phi)
    return phi, log_phi, invalid_total


def three_way(lower, upper, factor):
    if not np.isfinite(factor) or factor <= 1:
        raise ValueError('A prospectively fixed finite factor greater than one required')
    margin = np.log(factor)
    lower, upper = np.asarray(lower), np.asarray(upper)
    if np.any(lower < 0) or np.any(upper < lower):
        raise ValueError('Ordered nonnegative departure bounds required')
    return np.where(upper < margin, 'equivalent', np.where(lower > margin, 'departure', 'unresolved'))


def departure_bounds_from_log_band(lower, upper):
    """Sharp max-absolute-log bounds over a rectangular complete-profile band."""
    lo, hi = np.asarray(lower, dtype=float), np.asarray(upper, dtype=float)
    minimum_abs = np.where(lo > 0, lo, np.where(hi < 0, -hi, 0.))
    delta_lower = np.max(minimum_abs, axis=-1)
    delta_upper = np.max(np.maximum(np.abs(lo), np.abs(hi)), axis=-1)
    return delta_lower, delta_upper


def known_bound_bands(resource_blocks, widths, upper_bounds, alpha=.05):
    """Simultaneous profile ratio bounds from independent bounded block means.

    Coordinate Hoeffding errors use a union bound over K means. The ratio
    extremes share the numerator with the denominator: all other components
    are placed at their opposite endpoints. Independence is needed across
    blocks, not across bins; identical distribution across blocks is not
    necessary for the target average of their population means.
    """
    blocks, widths = _inputs(resource_blocks, widths)
    bound = np.asarray(upper_bounds, dtype=float)
    if bound.shape != (blocks.shape[-1],) or np.any(~np.isfinite(bound)) or np.any(bound <= 0):
        raise ValueError('Positive finite predetermined almost-sure resource bounds aligned with bins required')
    if np.any(blocks > bound+1e-12*np.maximum(1, bound)):
        raise ValueError('Observed resource exceeds a declared almost-sure upper bound')
    if not 0 < alpha < 1:
        raise ValueError('Alpha in (0,1) required')
    n, k = blocks.shape[-2:]
    mean = blocks.mean(axis=-2)
    error = bound*np.sqrt(np.log(2*k/alpha)/(2*n))
    low, high = np.maximum(0, mean-error), np.minimum(bound, mean+error)
    lower_denominator = low+high.sum(axis=-1, keepdims=True)-high
    upper_denominator = high+low.sum(axis=-1, keepdims=True)-low
    with np.errstate(divide='ignore', invalid='ignore'):
        phi_lower = np.divide(widths.sum()*low, widths*lower_denominator,
                              out=np.zeros_like(low), where=lower_denominator > 0)
        # If all admissible means are zero, the positive-total population
        # premise supplies no observed information; retain the broad limit.
        phi_upper = np.divide(widths.sum()*high, widths*upper_denominator,
                              out=np.broadcast_to(widths.sum()/widths, high.shape).copy(),
                              where=upper_denominator > 0)
        log_lower, log_upper = np.log(phi_lower), np.log(phi_upper)
    delta_lower, delta_upper = departure_bounds_from_log_band(log_lower, log_upper)
    return dict(log_lower=log_lower, log_upper=log_upper,
                departure_lower=delta_lower, departure_upper=delta_upper,
                mean_lower=low, mean_upper=high)


def batch_profile_decisions(resource_blocks, log_widths, *, factor=1.5, alpha=.05,
                            bootstrap_replicates=499, rng, resource_upper_bounds=None,
                            chunk=32):
    """Vectorized repeated datasets, with independent whole-block bootstraps.

    Input shape is (outer dataset, block, bin). Output retains both the
    simultaneous centered-log-vector band and a naive percentile interval for
    Delta. The latter's upper endpoint reproduces the historical maximum rule;
    its lower endpoint is a new descriptive comparator, not that original API.
    """
    blocks, widths = _inputs(resource_blocks, log_widths)
    if blocks.ndim != 3:
        raise ValueError('Batch input must have outer-dataset, block, bin dimensions')
    if not 0 < alpha < .5:
        raise ValueError('Alpha strictly between zero and one half required')
    if isinstance(bootstrap_replicates, bool) or int(bootstrap_replicates) != bootstrap_replicates or bootstrap_replicates < 20:
        raise ValueError('At least twenty bootstrap replicates required')
    outer, n, k = blocks.shape
    phi, point_log, zero_total = normalized_profile(blocks.mean(axis=1), widths)
    point_delta = np.max(np.abs(point_log), axis=-1)
    radius = np.empty(outer)
    percentile_lower = np.empty(outer); percentile_upper = np.empty(outer)
    zero_bootstrap_profiles = np.empty(outer, dtype=np.int64)
    # The draws are independent within each outer dataset. A single seeded
    # stream is consumed in fixed chunks; chunk size belongs to the algorithm.
    for start in range(0, outer, chunk):
        stop = min(start+chunk, outer)
        weights = rng.multinomial(n, np.full(n, 1/n), size=(stop-start, bootstrap_replicates))
        bootstrap_means = np.matmul(weights, blocks[start:stop])/n
        _, boot_log, invalid_boot = normalized_profile(bootstrap_means, widths)
        with np.errstate(invalid='ignore'):
            errors = np.max(np.abs(boot_log-point_log[start:stop, None, :]), axis=-1)
        invalid = np.any(~np.isfinite(boot_log), axis=-1) | invalid_boot
        errors[invalid] = np.inf
        errors[np.any(~np.isfinite(point_log[start:stop]), axis=-1)] = np.inf
        radius[start:stop] = np.quantile(errors, 1-alpha, axis=-1, method='higher')
        maxima = np.max(np.abs(boot_log), axis=-1)
        percentile_lower[start:stop] = np.quantile(maxima, alpha, axis=-1, method='higher')
        percentile_upper[start:stop] = np.quantile(maxima, 1-alpha, axis=-1, method='higher')
        zero_bootstrap_profiles[start:stop] = invalid.sum(axis=-1)
    with np.errstate(invalid='ignore'):
        centered_lower = point_log-radius[:, None]
        centered_upper = point_log+radius[:, None]
    unbounded = ~np.isfinite(radius)
    centered_lower[unbounded] = -np.inf; centered_upper[unbounded] = np.inf
    lower, upper = departure_bounds_from_log_band(centered_lower, centered_upper)
    methods = dict(centered_bootstrap=dict(log_lower=centered_lower, log_upper=centered_upper,
        departure_lower=lower, departure_upper=upper, decision=three_way(lower, upper, factor)),
        percentile_delta_extension=dict(departure_lower=percentile_lower, departure_upper=percentile_upper,
            decision=three_way(percentile_lower, percentile_upper, factor)))
    if resource_upper_bounds is not None:
        known = known_bound_bands(blocks, widths, resource_upper_bounds, alpha)
        known['decision'] = three_way(known['departure_lower'], known['departure_upper'], factor)
        methods['known_bound'] = known
    return dict(phi=phi, point_log=point_log, point_delta=point_delta, zero_total=zero_total,
                radius=radius, zero_bootstrap_profiles=zero_bootstrap_profiles, methods=methods,
                historical_percentile_equivalent=percentile_upper < np.log(factor))


def _json_ready(value):
    if isinstance(value, dict):
        return {key: _json_ready(item) for key, item in value.items()}
    if isinstance(value, np.ndarray):
        return _json_ready(value.tolist())
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    if isinstance(value, (float, np.floating)):
        return float(value) if np.isfinite(value) else None
    if isinstance(value, np.generic):
        return value.item()
    return value


def profile_decision(block_resource_totals, log_widths, *, factor=1.5, alpha=.05,
                     bootstrap_replicates=499, seed=0, resource_upper_bounds=None):
    """Usable JSON-ready complete-profile API; assumptions determine legitimacy.

    A row is one entire independent sampling block, not one event or one bin.
    For seasonal/dependent months, the IID bootstrap output is a conditional
    exploratory diagnostic. Unknown finite variance or sampling bias cannot
    be validated from twelve observed rows. No bootstrap decision by itself
    establishes that these requirements hold in a physical application.
    None denotes an unbounded endpoint; flags retain the distinction from
    an unavailable measurement. A known-bound reference is unavailable unless
    externally defensible bounds are supplied before examining outcomes.
    """
    blocks, widths = _inputs(block_resource_totals, log_widths)
    if blocks.ndim != 2:
        raise ValueError('One dataset with block-by-bin resource totals required')
    result = batch_profile_decisions(blocks[None], widths, factor=factor, alpha=alpha,
        bootstrap_replicates=bootstrap_replicates, rng=np.random.default_rng(seed),
        resource_upper_bounds=resource_upper_bounds)
    center = result['methods']['centered_bootstrap']
    point = result['point_log'][0]
    centered = dict(decision=str(center['decision'][0]),
        departure_lower=center['departure_lower'][0], departure_upper=center['departure_upper'][0],
        departure_upper_unbounded=bool(~np.isfinite(center['departure_upper'][0])),
        simultaneous_log_lower=center['log_lower'][0], simultaneous_log_upper=center['log_upper'][0],
        radius=result['radius'][0], radius_unbounded=bool(~np.isfinite(result['radius'][0])),
        nominal_level=1-alpha, bootstrap_replicates=bootstrap_replicates,
        zero_bootstrap_profiles=int(result['zero_bootstrap_profiles'][0]),
        assumptions='Approximate IID whole-block bootstrap; positive population bin means and sufficient moments/regularity for joint mean-vector approximation. Verify sampling design and calibrated regimes separately.')
    percentile = result['methods']['percentile_delta_extension']
    comparator = dict(departure_upper=percentile['departure_upper'][0],
        departure_upper_unbounded=bool(~np.isfinite(percentile['departure_upper'][0])),
        equivalent=bool(result['historical_percentile_equivalent'][0]),
        interpretation='Historical whole-profile percentile-maximum upper component only; lower percentile and three-way extension are evaluated separately in the benchmark.')
    known = dict(available=False, decision='unresolved', reason='No independently established almost-sure block-resource bounds supplied')
    if resource_upper_bounds is not None:
        reference = result['methods']['known_bound']
        known = dict(available=True, decision=str(reference['decision'][0]),
            departure_lower=reference['departure_lower'][0], departure_upper=reference['departure_upper'][0],
            departure_upper_unbounded=bool(~np.isfinite(reference['departure_upper'][0])),
            simultaneous_log_lower=reference['log_lower'][0], simultaneous_log_upper=reference['log_upper'][0],
            nominal_level=1-alpha, resource_upper_bounds=np.asarray(resource_upper_bounds),
            assumptions='Independent block rows; predetermined true almost-sure upper bounds; correct observation weights and estimand. Bins may be dependent, and rows need not be identically distributed.')
    return _json_ready(dict(n_blocks=len(blocks), n_bins=len(widths), factor=factor, alpha=alpha,
        log_widths=widths, seed=seed,
        point=dict(phi=result['phi'][0], log_phi=point, max_abs_log_departure=result['point_delta'][0],
            zero_bins=int(np.count_nonzero(result['phi'][0] == 0)), zero_total=bool(result['zero_total'][0])),
        centered_bootstrap=centered, percentile_max=comparator, bounded_reference=known,
        interval_endpoint_policy='None in a log lower endpoint means minus infinity; in a log upper or departure upper endpoint it means plus infinity; explicit unbounded/zero flags are retained.',
        target='Normalized mean block-resource totals per fixed logarithmic bin width, pooled before normalization; population total resource assumed positive.'))
