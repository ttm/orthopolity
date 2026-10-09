"""Known growth-fragmentation identities in a resource-allocation formulation.

Common exponential growth, symmetric binary division, stationary lineage and
balanced population; Genthon (2022), doi:10.1098/rsif.2022.0405.
Size is additive mass in the theory. Length is only an empirical proxy.
"""
from __future__ import annotations

import numpy as np
from scipy.special import ndtr


def lognormal_parameters(mean, variance):
    if not np.isfinite(mean) or mean <= 0 or not np.isfinite(variance) or variance < 0:
        raise ValueError("Positive finite mean and nonnegative finite variance required")
    sigma2 = np.log1p(variance / mean**2)
    return np.log(mean) - sigma2 / 2, np.sqrt(sigma2)


def summary_predictions(mean, variance, sampling="population"):
    """Arithmetic moments from a coherent lognormal chronological birth law.

    Division marginal is constrained to 2*birth. Independent division fits
    cannot be substituted into the crossing envelope without compatibility.
    """
    lognormal_parameters(mean, variance)
    c2 = variance / mean**2
    if sampling == "population":
        expected = 2 * np.log(2) * mean / (1 + c2)
        cv2 = (1 + c2) / (2 * np.log(2)**2) - 1
    elif sampling == "lineage":
        expected = mean / np.log(2)
        cv2 = 1.5 * np.log(2) * (1 + c2) - 1
    else:
        raise ValueError("Unknown sampling scheme")
    return dict(mean=float(expected), cv=float(np.sqrt(cv2)),
                variance=float(cv2 * expected**2))


def crossing_envelope(size, mean, variance):
    """H(x)=F_B(x)-F_B(x/2), using stable normal-tail differences."""
    x = np.asarray(size, dtype=float)
    if np.any(~np.isfinite(x)) or np.any(x <= 0):
        raise ValueError("Sizes must be positive and finite")
    mu, sigma = lognormal_parameters(mean, variance)
    if sigma == 0:
        return ((x >= mean) & (x < 2 * mean)).astype(float)
    z = (np.log(x) - mu) / sigma
    lower = z - np.log(2) / sigma
    return np.where(lower > 0, ndtr(-lower) - ndtr(-z), ndtr(z) - ndtr(lower))


def density(size, mean, variance, sampling="population"):
    x = np.asarray(size, dtype=float)
    h = crossing_envelope(x, mean, variance)
    if sampling == "population":
        inverse_birth = (1 + variance / mean**2) / mean
        return 2 * h / (inverse_birth * x**2)
    if sampling == "lineage":
        return h / (np.log(2) * x)
    raise ValueError("Unknown sampling scheme")


def resource_per_log_size(size, mean, variance):
    """Normalized additive-size resource density with respect to d(log x)."""
    return crossing_envelope(size, mean, variance) / np.log(2)
