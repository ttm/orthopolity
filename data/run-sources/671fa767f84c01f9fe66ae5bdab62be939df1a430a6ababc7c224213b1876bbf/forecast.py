"""Capacity-only family selection and approximate training uncertainty.

Known Pareto margins and the bottleneck mechanism remain assumptions. Candidate
families are selected using separate capacity observations, never realized
output sizes. Bootstrap bands require coverage assessment, especially after
selection; this module makes no distribution-free coverage claim.
"""
import numpy as np
from numpy.polynomial.legendre import leggauss

from orthopolity.dependence import estimate_dependence_parameter


FAMILIES = ("independent", "common_shock", "gaussian", "student")


def bounded_resource_moments(sizes, edges):
    """Unconditional bounded resource means E[K I(bin)] and normalized profile.

    Samples outside the declared range contribute zero, with the full sample
    size as denominator. Empty bins remain zero; normalization is a ratio of
    means and is not evidence of neutrality.
    """
    sizes, edges = np.asarray(sizes, float), np.asarray(edges, float)
    if sizes.ndim != 1 or not len(sizes) or np.any(~np.isfinite(sizes)) or np.any(sizes < 1):
        raise ValueError("finite capacity minima above or equal to one required")
    if edges.ndim != 1 or len(edges) < 2 or np.any(~np.isfinite(edges)) or edges[0] < 1 or np.any(np.diff(edges) <= 0):
        raise ValueError("finite increasing profile edges required")
    totals = np.histogram(sizes, bins=edges, weights=sizes)[0] / len(sizes)
    widths = np.diff(np.log(edges))
    if totals.sum() <= 0:
        raise ValueError("no resource in the declared bounded domain")
    return dict(means=totals, phi=totals / widths / (totals.sum()/widths.sum()))


def resource_prediction_from_survival(edges, survival, order=24):
    """Independent forward bounded moments from a declared survival function."""
    edges = np.asarray(edges, float)
    nodes, weights = leggauss(order)
    means = []
    for a, b in zip(edges[:-1], edges[1:]):
        lo, hi = np.log(a), np.log(b)
        xx = np.exp((lo+hi)/2+(hi-lo)*nodes/2)
        value = a*survival(a)-b*survival(b)+(hi-lo)/2*np.dot(weights, xx*survival(xx))
        means.append(value)
    means = np.asarray(means)
    if np.any(means <= 0):
        raise ArithmeticError("nonpositive predicted resource moment")
    widths = np.diff(np.log(edges))
    return dict(means=means, phi=means/widths/(means.sum()/widths.sum()))


def fit_capacity_candidates(capacities):
    """Known unit-Pareto margins; Student df=4 is a candidate assumption."""
    rho = estimate_dependence_parameter(capacities, "gaussian")
    theta = estimate_dependence_parameter(capacities, "common_shock")
    return dict(independent=0.0, common_shock=theta, gaussian=rho, student=rho)


def threshold_brier_score(prediction, capacity_minima, thresholds):
    """Mean proper binary score over fixed exceedance events.

    The target is the joint-feasible capacity distribution at these thresholds,
    not identification of the entire copula from its diagonal section.
    """
    prediction = np.asarray(prediction, float)
    minima, thresholds = np.asarray(capacity_minima, float), np.asarray(thresholds, float)
    if prediction.shape != thresholds.shape or np.any((prediction < 0) | (prediction > 1)):
        raise ValueError("aligned predicted probabilities required")
    observed = np.mean(minima[:, None] >= thresholds[None, :], axis=0)
    return float(np.mean(prediction**2-2*prediction*observed+observed))


def select_capacity_candidate(predictions, capacity_minima, thresholds):
    """Deterministic ordering resolves exact ties in predeclared family order."""
    scores = {family: threshold_brier_score(predictions[family], capacity_minima, thresholds) for family in FAMILIES}
    return min(FAMILIES, key=scores.get), scores


def lookup_prediction(bank, family, parameter):
    """Interpolate bounded predictions; reject extrapolation silently escaping grid."""
    entry = bank[family]
    grid = np.asarray(entry["parameter_grid"])
    if parameter < grid[0] or parameter > grid[-1]:
        raise ValueError("fitted parameter lies outside the frozen prediction grid")
    result = {}
    for key in ("survival", "resource_means"):
        array = np.asarray(entry[key])
        result[key] = np.array([np.interp(parameter, grid, array[:, j]) for j in range(array.shape[1])])
    widths = np.asarray(bank["log_widths"])
    moments = result["resource_means"]
    result["phi"] = moments/widths/(moments.sum()/widths.sum())
    return result


def empirical_survival(sizes, thresholds):
    return np.mean(np.asarray(sizes)[:, None] >= np.asarray(thresholds)[None, :], axis=0)


def bounded_bootstrap_cdf_distance(sorted_sizes, sorted_frequencies, hi):
    """Exact sup bootstrap EDF minus original EDF on [1,hi], retaining ties.

    Sorted frequencies are multiplicities of original ordered observations.
    Differences are evaluated after each entire equal-value group.
    """
    xx = np.asarray(sorted_sizes)
    frequencies = np.asarray(sorted_frequencies)
    n = len(xx)
    groups = np.r_[np.flatnonzero(xx[1:] != xx[:-1]), n-1]
    groups = groups[xx[groups] <= hi]
    if not len(groups):
        return 0.0
    return float(np.max(abs(np.cumsum(frequencies)[groups]/n-(groups+1)/n)))


def bounded_population_cdf_distance(sizes, survival, hi):
    """KS distance to a declared population law on [1,hi].

    The supplied survival may be a numerically audited interpolant. Include
    EDF jumps, tied sample groups, and the upper domain boundary.
    """
    xx = np.sort(np.asarray(sizes, float))
    n = len(xx)
    unique, starts, counts = np.unique(xx[xx <= hi], return_index=True, return_counts=True)
    if not len(unique):
        return float(1-survival(hi))
    truth = 1-survival(unique)
    right = (starts+counts)/n
    left = starts/n
    return float(max(np.max(abs(right-truth)), np.max(abs(left-truth)),
                     abs(np.mean(xx <= hi)-(1-survival(hi)))))


def sup_bootstrap_radius(center, replicates, confidence=.95):
    """Approximate centered sup-norm radius; no automatic coverage guarantee."""
    center, replicates = np.asarray(center, float), np.asarray(replicates, float)
    if replicates.ndim != 2 or replicates.shape[1:] != center.shape or not 0 < confidence < 1:
        raise ValueError("aligned bootstrap vectors and interior confidence required")
    return float(np.quantile(np.max(abs(replicates-center), axis=1), confidence, method="higher"))
