"""Conditional cantilever fluctuation predictions from mechanical loss.

No source-data reader lives here. Fits use only temperature increments and
loss angles; fluctuation amplitudes are not accepted by any calibration API.
Modes have counting measure and their squared strain profiles are normalized
on z=x/L. The supplied t0 is a calibration convention, not an estimated value.
"""
from __future__ import annotations

import math
import operator

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.optimize import brentq


LOCAL_RELATIVE_TOLERANCE = 1e-10


def _integer(value, name, minimum):
    if isinstance(value, (bool, np.bool_)):
        raise ValueError(f"{name} must be an integer >= {minimum}")
    try:
        number = operator.index(value)
    except TypeError as error:
        raise ValueError(f"{name} must be an integer >= {minimum}") from error
    if number < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return number


def mode_moments(kind, index, order=256):
    """Return normalized strain-weight moments [mu0, mu1, mu2, mu3].

    Flexural modes are Euler--Bernoulli clamped-free modes; torsional modes
    have sin((index-1/2)*pi*z) displacement. Arbitrary shape amplitudes cancel.
    Gauss--Legendre order controls spatial quadrature, not a fitted parameter.
    """
    index = _integer(index, "index", 1)
    order = _integer(order, "order", 8)
    if kind not in ("flexural", "torsional"):
        raise ValueError("kind must be flexural or torsional")
    nodes, weights = leggauss(order)
    z, weights = (nodes + 1) / 2, weights / 2
    if kind == "torsional":
        strain = np.cos((index - .5) * np.pi * z)
    else:
        # cos(beta)*cosh(beta)=-1, evaluated without overflowing cosh.
        def characteristic(beta):
            e = math.exp(-beta)
            return math.cos(beta) + 2 * e / (1 + e * e)

        beta = brentq(characteristic, (index - 1) * np.pi, index * np.pi,
                      xtol=1e-13)
        e = math.exp(-beta)
        sine, cosine = math.sin(beta), math.cos(beta)
        denominator = .5 * (1 - e * e) + sine * e
        ratio = (.5 * (1 + e * e) + cosine * e) / denominator
        # Stable form of cosh(beta*z)-ratio*sinh(beta*z). The beta**2
        # derivative factor is constant and cancels in normalization.
        hyperbolic = .5 * (
            (-e + sine - cosine) * np.exp(-beta * (1 - z))
            + (1 + (sine + cosine) * e) * np.exp(-beta * z)
        ) / denominator
        strain = hyperbolic + np.cos(beta * z) - ratio * np.sin(beta * z)
    weighted_strain = weights * strain**2
    normalizer = weighted_strain.sum()
    if not np.isfinite(normalizer) or normalizer <= 0:
        raise ValueError("Nonpositive or nonfinite strain normalization")
    moments = np.array([np.dot(weighted_strain, z**r) / normalizer
                        for r in range(4)])
    moments[0] = 1.0
    return moments


def _moments(values):
    moments = np.asarray(values, dtype=float)
    if (moments.shape != (4,) or not np.all(np.isfinite(moments))
            or not np.isclose(moments[0], 1., rtol=0, atol=1e-12)
            or np.any(moments < 0) or np.any(moments > 1)
            or np.any(np.diff(moments) > 1e-12)
            or moments[1] <= 0 or moments[2] <= 0):
        raise ValueError("Expected normalized nondegenerate moments mu0..mu3")
    return moments


def _coefficients(values):
    coefficients = np.asarray(values, dtype=float)
    if coefficients.shape != (3,) or not np.all(np.isfinite(coefficients)):
        raise ValueError("Expected three finite physical-Delta coefficients")
    return coefficients


def _increments(values):
    values = np.asarray(values, dtype=float)
    if not np.all(np.isfinite(values)) or np.any(values < 0):
        raise ValueError("Temperature increments must be finite and nonnegative")
    return values


def _output(values):
    if not np.all(np.isfinite(values)):
        raise ValueError("Nonfinite prediction")
    return float(values) if np.ndim(values) == 0 else values


def predict_loss(delta, coefficients):
    """Predict Phi=a+b*Delta+c*Delta**2, without clipping negative values."""
    delta = _increments(delta)
    a, b, c = _coefficients(coefficients)
    return _output((c * delta + b) * delta + a)


def predict_temperature(delta, coefficients, moments, t0=295):
    """Predict fluctuation temperature using fitted loss in the denominator.

    This is algebraic evaluation, not an admissibility gate. Unphysical but
    finite extrapolations are preserved. A zero denominator raises ValueError.
    Scalar inputs return a float and array inputs return an ndarray.
    """
    delta = _increments(delta)
    a, b, c = _coefficients(coefficients)
    mu = _moments(moments)
    if not np.isfinite(t0) or t0 <= 0:
        raise ValueError("t0 must be finite and positive")
    denominator = np.asarray(predict_loss(delta, coefficients))
    if np.any(denominator == 0):
        raise ValueError("Zero predicted global loss")
    numerator = a * mu[1] + b * delta * mu[2] / mu[1] + c * delta**2 * mu[3] / mu[2]
    return _output(t0 + delta * numerator / denominator)


def _extrema(coefficients):
    """Exact candidate extrema of a quadratic on the normalized interval [0,1]."""
    a, b, c = coefficients
    points = [0., 1.]
    if c != 0:
        vertex = -b / (2 * c)
        if 0 < vertex < 1:
            points.append(float(vertex))
    values = [(c * z + b) * z + a for z in points]
    position = int(np.argmin(values))
    return float(values[position]), float(points[position]), float(max(map(abs, values)))


def fit_loss(delta, phi, sigma, moments, domain_max):
    """Weighted quadratic loss fit and continuous-domain physical audit.

    Every supplied row must be valid: invalid rows are never silently removed.
    ``eligible`` means a rank-three fit was obtained; ``admissible`` additionally
    requires nonnegative local loss (relative roundoff tolerance 1e-10) and
    strictly positive global loss throughout [0, domain_max]. Coefficients and
    residuals are preserved for an eligible but physically inadmissible fit.
    All returned values support strict JSON serialization, including failures.
    Local-minimum location is a *local* temperature increment, in kelvin.
    """
    result = dict(status="ineligible", eligible=False, admissible=False,
                  reasons=[], coefficients=None, input_count=0, fit_count=0,
                  distinct_delta_count=0, rank=None, condition_number=None,
                  normalization_delta_K=None, local_minimum=None,
                  local_minimum_location=None, local_scale=None,
                  local_tolerance=None, global_minimum=None,
                  global_minimum_location=None, train_diagnostics=None)
    try:
        delta = np.asarray(delta, dtype=float)
        phi = np.asarray(phi, dtype=float)
        sigma = np.asarray(sigma, dtype=float)
        mu = _moments(moments)
        domain_max = float(domain_max)
    except (TypeError, ValueError, OverflowError):
        result["reasons"].append("invalid_input_structure_or_moments")
        return result
    if delta.ndim != 1 or phi.shape != delta.shape or sigma.shape != delta.shape:
        result["reasons"].append("training_arrays_must_be_matching_vectors")
        return result
    result["input_count"] = int(delta.size)
    if not np.isfinite(domain_max) or domain_max <= 0:
        result["reasons"].append("domain_max_must_be_finite_positive")
        return result
    result["normalization_delta_K"] = domain_max
    if not all(np.all(np.isfinite(values)) for values in (delta, phi, sigma)):
        result["reasons"].append("nonfinite_training_values")
    if np.any(delta < 0):
        result["reasons"].append("negative_training_temperature_increment")
    if np.any(delta > domain_max):
        result["reasons"].append("training_temperature_outside_domain")
    if np.any(phi <= 0):
        result["reasons"].append("nonpositive_training_loss")
    if np.any(sigma <= 0):
        result["reasons"].append("nonpositive_training_uncertainty")
    if delta.size < 4:
        result["reasons"].append("fewer_than_four_training_points")
    if result["reasons"]:
        return result
    result["distinct_delta_count"] = int(np.unique(delta).size)
    if result["distinct_delta_count"] < 3:
        result["reasons"].append("fewer_than_three_distinct_temperatures")
        return result

    u = delta / domain_max
    design = np.column_stack((np.ones(delta.size), u, u**2))
    # Common rescalings preserve WLS while avoiding unnecessarily huge weights.
    weights = sigma.min() / sigma
    loss_scale = phi.max()
    try:
        normalized, _, rank, singular = np.linalg.lstsq(
            design * weights[:, None], (phi / loss_scale) * weights, rcond=None)
    except np.linalg.LinAlgError:
        result["reasons"].append("weighted_least_squares_failure")
        return result
    result["rank"] = int(rank)
    if singular[-1] > 0:
        condition = singular[0] / singular[-1]
        result["condition_number"] = float(condition) if np.isfinite(condition) else None
    if rank != 3:
        result["reasons"].append("rank_deficient_weighted_design")
        return result
    normalized *= loss_scale
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        coefficients = normalized / np.array([1., domain_max, np.square(domain_max)])
        fitted = design @ normalized
        residuals = phi - fitted
        standardized = residuals / sigma
        weighted_ss = float(np.dot(standardized, standardized))
    if (not np.all(np.isfinite(coefficients)) or not np.all(np.isfinite(fitted))
            or not np.isfinite(weighted_ss)):
        result["reasons"].append("nonfinite_fit_outputs")
        return result
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        local = normalized / np.array([1., mu[1], mu[2]])
    if not np.all(np.isfinite(local)):
        result["reasons"].append("nonfinite_local_loss_outputs")
        return result
    local_minimum, local_at, local_scale = _extrema(local)
    global_minimum, global_at, _ = _extrema(normalized)
    tolerance = LOCAL_RELATIVE_TOLERANCE * local_scale
    if local_minimum < -tolerance:
        result["reasons"].append("negative_local_loss_on_prediction_domain")
    if global_minimum <= 0:
        result["reasons"].append("nonpositive_global_loss_on_prediction_domain")
    result.update(
        status="admissible" if not result["reasons"] else "inadmissible",
        eligible=True, admissible=not result["reasons"],
        coefficients=coefficients.tolist(), fit_count=int(delta.size),
        local_minimum=local_minimum, local_minimum_location=local_at * domain_max,
        local_scale=local_scale, local_tolerance=tolerance,
        global_minimum=global_minimum, global_minimum_location=global_at * domain_max,
        train_diagnostics=dict(fitted_loss=fitted.tolist(), residuals=residuals.tolist(),
            standardized_residuals=standardized.tolist(),
            mean_absolute_error=float(np.mean(np.abs(residuals))),
            root_mean_squared_error=float(np.sqrt(np.mean(residuals**2))),
            weighted_residual_sum_squares=weighted_ss,
            degrees_of_freedom=int(delta.size - 3),
            scope="Conditional fit diagnostics, not independent-sample significance tests"))
    return result
