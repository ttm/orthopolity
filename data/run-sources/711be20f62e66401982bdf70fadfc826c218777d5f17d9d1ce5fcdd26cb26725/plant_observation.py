"""Synthetic finite-census diagnostics for recorded plant-mass profiles.

This module reads no plant source data. Its IID envelopes are conditional on a
fixed object count and a specified bounded count law. Perfectly repeated mass
blocks are dependence stress tests, not ecological observation models. No
practical equivalence tolerance or ecological neutrality verdict is supplied.
"""
from __future__ import annotations

from math import ceil, log10, sqrt

import numpy as np


DEFAULT_SPECIFICATION = {
    "domain": [0.01, 100.0],
    "log10_bin_width": 0.5,
    "rounding": 0.001,
    "sample_sizes": [160, 320, 640, 1280],
    "block_sizes": [1, 5, 20],
    "exponents": [2.0, 1.5],
    "replicates": 1000,
    "null_reference_replicates": 2000,
    "seed": 2026100301,
}


def _positive_integer(value, name):
    if isinstance(value, (bool, np.bool_)) or int(value) != value or value < 1:
        raise ValueError(f"{name} must be a positive integer")
    return int(value)


def _specification(specification):
    supplied = dict(specification)
    unknown = set(supplied)-set(DEFAULT_SPECIFICATION)
    if unknown:
        raise ValueError(f"Unknown calibration specification fields: {sorted(unknown)}")
    spec = {**DEFAULT_SPECIFICATION, **supplied}
    domain = np.asarray(spec["domain"], dtype=float)
    if domain.shape != (2,) or np.any(~np.isfinite(domain)) or not 0 < domain[0] < domain[1]:
        raise ValueError("A finite positive increasing two-endpoint domain is required")
    spec["domain"] = domain.tolist()
    for key in ("log10_bin_width", "rounding"):
        value = float(spec[key])
        if not np.isfinite(value) or value <= 0:
            raise ValueError(f"{key} must be positive and finite")
        spec[key] = value
    if not np.allclose(domain/spec["rounding"], np.rint(domain/spec["rounding"]), rtol=0, atol=1e-8):
        raise ValueError("Domain endpoints must lie on the declared measurement grid")
    if domain[0] < spec["rounding"]:
        raise ValueError("The lower domain endpoint must be at least one rounding increment")
    if domain[1]/spec["rounding"]-domain[0]/spec["rounding"] > 2_000_000:
        raise ValueError("Exact rounding integration is limited to two million grid cells")
    for key in ("sample_sizes", "block_sizes"):
        values = [_positive_integer(value, key) for value in spec[key]]
        if not values or len(set(values)) != len(values):
            raise ValueError(f"{key} must contain distinct positive integers")
        spec[key] = values
    exponents = [float(value) for value in spec["exponents"]]
    if not exponents or any(not np.isfinite(value) or value <= 0 for value in exponents):
        raise ValueError("Finite positive count-law exponents are required")
    if len(set(exponents)) != len(exponents):
        raise ValueError("Count-law exponents must be distinct")
    if any(abs(value*100-round(value*100)) > 1e-8 for value in exponents):
        raise ValueError("Exponents require at most two decimal places for unique random-stream tags")
    spec["exponents"] = exponents
    for key in ("replicates", "null_reference_replicates"):
        spec[key] = _positive_integer(spec[key], key)
        if spec[key] < 20:
            raise ValueError(f"{key} must be at least twenty")
    seed = spec["seed"]
    if isinstance(seed, (bool, np.bool_)) or int(seed) != seed or seed < 0:
        raise ValueError("seed must be a nonnegative integer")
    spec["seed"] = int(seed)
    return spec


def _edges(domain, width):
    lower, upper = domain
    span = log10(upper/lower)
    full = int(np.floor(span/width+1e-12))
    edges = lower*10.0**(np.arange(full+1)*width)
    edges = edges[edges < upper*(1-1e-12)]
    edges = np.concatenate((edges, [upper]))
    edges[0] = lower
    if len(edges) < 3:
        raise ValueError("At least two logarithmic bins are required")
    return edges


def _power_integral(lower, upper, power):
    """Stable integral of x**power, including narrow rounding cells."""
    lower, upper = np.asarray(lower, dtype=float), np.asarray(upper, dtype=float)
    degree = power+1
    if abs(degree) < 1e-12:
        return np.log(upper/lower)
    return lower**degree*np.expm1(degree*np.log(upper/lower))/degree


def rounded_expected_profile(domain, edges, rounding, exponent=2.0):
    """Integrate recorded-grid count and stock weights exactly.

    Latent density is proportional to m**(-exponent) on the bounded domain.
    Each latent interval maps to its nearest recorded mass; tie conventions at
    exact half increments have zero probability under the continuous law.
    Bins are left-closed/right-open, with the final right endpoint included.
    Stock uses recorded mass, rather than latent mass. Domain endpoints must
    be grid points, so rounding loses no object outside the declared support.
    """
    lower, upper = map(float, domain)
    edges = np.asarray(edges, dtype=float)
    rounding, exponent = float(rounding), float(exponent)
    if not np.isfinite(rounding) or rounding <= 0 or not np.isfinite(exponent) or exponent <= 0:
        raise ValueError("Positive finite rounding and exponent are required")
    if not 0 < lower < upper or np.any(~np.isfinite(edges)) or np.any(np.diff(edges) <= 0):
        raise ValueError("Positive increasing domain and bin edges are required")
    if edges.ndim != 1 or len(edges) < 3 or edges[0] != lower or edges[-1] != upper:
        raise ValueError("At least two complete bins with exact domain endpoints are required")
    endpoints = np.asarray([lower, upper])/rounding
    if not np.allclose(endpoints, np.rint(endpoints), rtol=0, atol=1e-8):
        raise ValueError("Domain endpoints must lie on the measurement grid")
    first, last = np.rint(endpoints).astype(np.int64)
    if first < 1 or last-first > 2_000_000:
        raise ValueError("Positive grid support with at most two million cells is required")
    recorded = rounding*np.arange(first, last+1, dtype=float)
    left = np.maximum(lower, recorded-rounding/2)
    right = np.minimum(upper, recorded+rounding/2)
    normalization = float(_power_integral(lower, upper, -exponent))
    probabilities = _power_integral(left, right, -exponent)/normalization
    labels = np.clip(np.searchsorted(edges, recorded, side="right")-1, 0, len(edges)-2)
    counts = np.bincount(labels, weights=probabilities, minlength=len(edges)-1)
    stocks = np.bincount(labels, weights=recorded*probabilities, minlength=len(edges)-1)
    unrounded_counts = _power_integral(edges[:-1], edges[1:], -exponent)/normalization
    unrounded_stocks = _power_integral(edges[:-1], edges[1:], 1-exponent)/normalization
    stock_shares = stocks/stocks.sum()
    unrounded_stock_shares = unrounded_stocks/unrounded_stocks.sum()
    return {
        "exponent": exponent,
        "expected_count_shares": counts.tolist(),
        "expected_stock_per_object_by_bin": stocks.tolist(),
        "expected_recorded_mass_per_object": float(stocks.sum()),
        "normalized_expected_stock_shares": stock_shares.tolist(),
        "unrounded_expected_count_shares": unrounded_counts.tolist(),
        "unrounded_normalized_expected_stock_shares": unrounded_stock_shares.tolist(),
        "measurement_tv_from_unrounded_expected_stock": float(np.abs(stock_shares-unrounded_stock_shares).sum()/2),
        "target": "Normalized expectations of bin stocks; not expectation of normalized finite-census shares",
    }


def _sample_profiles(rng, n, block_size, replicates, domain, edges, rounding, exponent):
    lower, upper = domain
    groups = ceil(n/block_size)
    uniform = rng.uniform(size=(replicates, groups))
    degree = 1-exponent
    if abs(degree) < 1e-12:
        latent = lower*np.exp(uniform*np.log(upper/lower))
    else:
        latent = lower*(1+uniform*np.expm1(degree*np.log(upper/lower)))**(1/degree)
    recorded = np.rint(latent/rounding)*rounding
    multiplicities = np.full(groups, block_size, dtype=np.int64)
    multiplicities[-1] = n-block_size*(groups-1)
    labels = np.clip(np.searchsorted(edges, recorded, side="right")-1, 0, len(edges)-2)
    stocks = np.column_stack([
        np.sum(recorded*multiplicities*(labels == index), axis=1)
        for index in range(len(edges)-1)
    ])
    shares = stocks/stocks.sum(axis=1, keepdims=True)
    return shares


def _wilson(successes, trials):
    # Standard normal 0.975 quantile; these intervals quantify Monte Carlo
    # frequency uncertainty and are not ecological confidence intervals.
    z = 1.959963984540054
    proportion = successes/trials
    denominator = 1+z*z/trials
    center = (proportion+z*z/(2*trials))/denominator
    radius = z*sqrt(proportion*(1-proportion)/trials+z*z/(4*trials*trials))/denominator
    return [max(0., center-radius), min(1., center+radius)]


def _raw_statistics(shares, null_template, rounded_stock_template):
    return {
        "tv_from_log_neutral_template": (np.abs(shares-null_template).sum(axis=1)/2).tolist(),
        "tv_from_rounded_expected_stock": (np.abs(shares-rounded_stock_template).sum(axis=1)/2).tolist(),
        "any_empty_bin": np.any(shares == 0, axis=1).tolist(),
        "last_bin_share": shares[:, -1].tolist(),
        "normalized_stock_shares": shares.tolist(),
    }


def calibrate_observation(specification):
    """Return replayable JSON-safe synthetic diagnostics, without source data.

    Canonical specification fields are those in DEFAULT_SPECIFICATION. Stream
    identities depend on condition labels, never the order of conditions. IID
    alpha=2 null-reference entropy is [seed,n,0]; evaluation entropy is
    [seed,n,block_size,round(exponent*100),1]. References and evaluation draws
    are disjoint. The 95% null critical TV is an IID compatibility envelope,
    not a practical equivalence margin or a plant-study neutrality decision.
    """
    spec = _specification(specification)
    edges = _edges(spec["domain"], spec["log10_bin_width"])
    null_template = np.diff(np.log(edges))/np.log(edges[-1]/edges[0])
    expectations = {
        exponent: rounded_expected_profile(spec["domain"], edges, spec["rounding"], exponent)
        for exponent in dict.fromkeys([2.0, *spec["exponents"]])
    }
    references = []
    critical_by_n = {}
    for n in spec["sample_sizes"]:
        entropy = [spec["seed"], n, 0]
        rng = np.random.default_rng(np.random.SeedSequence(entropy))
        shares = _sample_profiles(rng, n, 1, spec["null_reference_replicates"], spec["domain"],
                                  edges, spec["rounding"], 2.0)
        tv = np.abs(shares-null_template).sum(axis=1)/2
        critical = float(np.quantile(tv, .95, method="higher"))
        critical_by_n[n] = critical
        stats = _raw_statistics(shares, null_template, np.asarray(expectations[2.0]["normalized_expected_stock_shares"]))
        references.append({"n": n, "seed_sequence_entropy": entropy,
                           "replicates": spec["null_reference_replicates"],
                           "critical_tv_95": critical, "quantile_method": "higher", "raw": stats})
    conditions = []
    for n in spec["sample_sizes"]:
        for block_size in spec["block_sizes"]:
            for exponent in spec["exponents"]:
                entropy = [spec["seed"], n, block_size, int(round(exponent*100)), 1]
                rng = np.random.default_rng(np.random.SeedSequence(entropy))
                shares = _sample_profiles(rng, n, block_size, spec["replicates"], spec["domain"],
                                          edges, spec["rounding"], exponent)
                expectation = expectations[exponent]
                stock_template = np.asarray(expectation["normalized_expected_stock_shares"])
                tv = np.abs(shares-null_template).sum(axis=1)/2
                mean_profile = shares.mean(axis=0)
                exceedances = int(np.count_nonzero(tv > critical_by_n[n]))
                zero_count = int(np.count_nonzero(np.any(shares == 0, axis=1)))
                raw = _raw_statistics(shares, null_template, stock_template)
                conditions.append({
                    "n": n, "block_size": block_size, "exponent": exponent,
                    "independent_mass_draws_per_census": ceil(n/block_size),
                    "last_block_size": n-block_size*(ceil(n/block_size)-1),
                    "seed_sequence_entropy": entropy, "replicates": spec["replicates"],
                    "role": ("IID null coverage check" if exponent == 2.0 and block_size == 1 else
                             "Perfect-block dependence stress under the null marginal law" if exponent == 2.0 else
                             "Departure-marginal and dependence stress"),
                    "rounded_expectation": expectation,
                    "summary": {
                        "mean_normalized_census_stock_shares": mean_profile.tolist(),
                        "mean_share_monte_carlo_standard_errors": (shares.std(axis=0, ddof=1)/sqrt(spec["replicates"])).tolist(),
                        "normalization_bias_tv_from_rounded_expected_stock": float(np.abs(mean_profile-stock_template).sum()/2),
                        "mean_profile_tv_from_log_neutral_template": float(np.abs(mean_profile-null_template).sum()/2),
                        "mean_realized_tv_from_log_neutral_template": float(tv.mean()),
                        "mean_realized_tv_from_rounded_expected_stock": float(np.abs(shares-stock_template).sum(axis=1).mean()/2),
                        "iid_null_critical_tv_95": critical_by_n[n],
                        "iid_envelope_exceedance_count": exceedances,
                        "iid_envelope_exceedance_rate": exceedances/spec["replicates"],
                        "iid_envelope_exceedance_wilson95": _wilson(exceedances, spec["replicates"]),
                        "any_empty_bin_frequency": zero_count/spec["replicates"],
                        "any_empty_bin_wilson95": _wilson(zero_count, spec["replicates"]),
                        "mean_last_bin_share": float(shares[:, -1].mean()),
                    },
                    "raw": raw,
                })
    return {
        "study_type": "Synthetic observation calibration; contains no empirical plant data",
        "specification": spec,
        "bin_edges_g": edges.tolist(),
        "bin_endpoint_policy": "Left-closed and right-open; final upper endpoint included",
        "log_neutral_expected_stock_template": null_template.tolist(),
        "rounded_expectations": list(expectations.values()),
        "null_reference": references,
        "conditions": conditions,
        "null_critical_interpretation": "Conditional fixed-n IID alpha=2 compatibility envelope; not an equivalence tolerance",
        "monte_carlo_interval_interpretation": "Wilson 95% intervals quantify Monte Carlo exceedance/frequency uncertainty only",
        "ecological_neutrality_decision": "unresolved",
        "limitations": [
            "Perfect repeated-mass blocks do not identify real plant dependence or biological stem grouping",
            "Counts are fixed; count-mass/budget dependence and plot heterogeneity are not modeled",
            "All latent masses lie inside the domain; tails and missingness are absent",
            "A mean normalized census profile and normalized expected stocks are different estimands",
            "Empty bins can make complete-profile log-bootstrap intervals unbounded",
        ],
    }
