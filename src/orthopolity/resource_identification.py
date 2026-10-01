"""Power-law exponents can coincide while independently fixed resources differ.

The positive curved law is a deliberate orthogonal perturbation of a bounded
exponential law in log size. It also has an explicit growth/removal realization.
This is a constructive counterexample, not an allocation-neutrality generator.
"""
from __future__ import annotations

import math
import numpy as np
from scipy.integrate import quad
from scipy.special import gammainc, xlogy


def exponential_moment(order, upper, rate):
    """Integral_0^upper u**order exp(-rate*u) du for rate > 0."""
    if isinstance(order, bool) or int(order) != order or order < 0:
        raise ValueError('Nonnegative integer moment order required')
    upper = np.asarray(upper, dtype=float)
    if not np.isfinite(rate) or rate <= 0 or np.any(~np.isfinite(upper)) or np.any(upper < 0):
        raise ValueError('Finite positive rate and nonnegative upper limits required')
    return math.factorial(order)*gammainc(order+1, rate*upper)/rate**(order+1)


def matched_curvature(log_width, rate):
    """Quadratic H orthogonal to 1 and u under exp(-rate*u) on [0,L].

    H=(u**2-a*u-b)/scale, with max abs H = 1. The normalization and
    mean-log-size scores therefore agree exactly with the unperturbed law.
    """
    if not np.isfinite(log_width) or log_width <= 0:
        raise ValueError('Positive finite log width required')
    moments = [float(exponential_moment(n, log_width, rate)) for n in range(4)]
    a, b = np.linalg.solve([[moments[1], moments[0]], [moments[2], moments[1]]],
                           [moments[2], moments[3]])
    points = [0., log_width]
    if 0 < a/2 < log_width:
        points.append(a/2)
    scale = max(abs(u*u-a*u-b) for u in points)
    return dict(log_width=float(log_width), rate=float(rate), a=float(a), b=float(b),
                scale=float(scale), orthogonality_residuals=[
                    (moments[2]-a*moments[1]-b*moments[0])/scale,
                    (moments[3]-a*moments[2]-b*moments[1])/scale])


def curvature(u, model):
    u = np.asarray(u, dtype=float)
    return (u*u-model['a']*u-model['b'])/model['scale']


def curvature_derivative(u, model):
    return (2*np.asarray(u, dtype=float)-model['a'])/model['scale']


def log_density(u, model, amplitude=0.):
    """Normalized continuous object density per log size on [0,L]."""
    u = np.asarray(u, dtype=float)
    modulation = 1+amplitude*curvature(u, model)
    if not np.isfinite(amplitude) or np.any(modulation <= 0):
        raise ValueError('Positive finite modulation required')
    return np.exp(-model['rate']*u)*modulation/exponential_moment(0, model['log_width'], model['rate'])


def log_cdf(u, model, amplitude=0.):
    """Exact polynomial/exponential integral for the curved log-size law."""
    u = np.asarray(u, dtype=float)
    if np.any(~np.isfinite(u)) or np.any(u < 0) or np.any(u > model['log_width']):
        raise ValueError('CDF arguments must lie within the declared log domain')
    rate = model['rate']
    i0, i1, i2 = [exponential_moment(n, u, rate) for n in range(3)]
    correction = (i2-model['a']*i1-model['b']*i0)/model['scale']
    return (i0+amplitude*correction)/exponential_moment(0, model['log_width'], rate)


def removal_hazard(u, model, amplitude=0., growth_rate=1.):
    """Rate h=-g*d(log n)/du giving this stationary transport solution."""
    modulation = 1+amplitude*curvature(u, model)
    if not np.isfinite(growth_rate) or growth_rate <= 0 or np.any(modulation <= 0):
        raise ValueError('Positive growth and modulation required')
    return growth_rate*(model['rate']-amplitude*curvature_derivative(u, model)/modulation)


def hazard_extrema(model, amplitude, growth_rate=1.):
    """Exact extrema of the rational quadratic hazard on the bounded domain."""
    a, b, scale = model['a'], model['b'], model['scale']
    points = [0., model['log_width']]
    # Derivative of H'/(1+amplitude H) vanishes where:
    # 2*scale + amplitude*(-2*u**2+2*a*u-2*b-a**2) = 0.
    if amplitude:
        roots = np.roots([-2*amplitude, 2*amplitude*a,
                          2*scale-amplitude*(2*b+a*a)])
        points.extend(float(root.real) for root in roots
                      if abs(root.imag) < 1e-12 and 0 < root.real < model['log_width'])
    values = removal_hazard(points, model, amplitude, growth_rate)
    return dict(minimum=float(values.min()), maximum=float(values.max()),
                audited_points=points, values=values.tolist())


def bounded_log_mean(rate, log_width):
    """Mean log size for density proportional to exp(-rate*u), any real rate."""
    rate = np.asarray(rate, dtype=float)
    t = rate*log_width
    result = np.empty_like(rate)
    tiny = np.abs(t) < 1e-4
    result[tiny] = log_width*(.5-t[tiny]/12+t[tiny]**3/720-t[tiny]**5/30240)
    high = (t > 700) & ~tiny
    low = (t < -700) & ~tiny
    result[high] = 1/rate[high]
    result[low] = log_width+1/rate[low]
    regular = ~(tiny | high | low)
    result[regular] = 1/rate[regular]-log_width/np.expm1(t[regular])
    return result


def bounded_power_mle(mean_log_size, log_width):
    """Continuous x-density exponent alpha=1+kappa, from exact sample mean u.

    Bisection solves the bounded likelihood score. This uses the continuously
    observed log sizes, not bin midpoints or a log regression of bin counts.
    """
    mean = np.asarray(mean_log_size, dtype=float)
    if not np.isfinite(log_width) or log_width <= 0 or np.any(~np.isfinite(mean)) or np.any(mean <= 0) or np.any(mean >= log_width):
        raise ValueError('Mean log sizes strictly inside a finite positive domain required')
    # The endpoint limits are 0 and L. Expand the bracket for unusually
    # concentrated samples instead of silently clipping an extreme estimate.
    bound = np.maximum(10/log_width, 2/np.minimum(mean, log_width-mean))
    lo, hi = -bound, bound
    for _ in range(64):
        mid = (lo+hi)/2
        below = bounded_log_mean(mid, log_width) > mean
        lo = np.where(below, mid, lo)
        hi = np.where(below, hi, mid)
    return 1+(lo+hi)/2


def inverse_cdf_table(model, amplitude, points):
    """Monotone numerical sampler and independent midpoint CDF-error audit."""
    if isinstance(points, bool) or int(points) != points or points < 17:
        raise ValueError('At least 17 inverse-CDF knots required')
    u = np.linspace(0, model['log_width'], points)
    cdf = log_cdf(u, model, amplitude)
    cdf[0], cdf[-1] = 0., 1.
    if np.any(np.diff(cdf) <= 0):
        raise ValueError('CDF table must be strictly increasing')
    mid = (u[:-1]+u[1:])/2
    error = np.max(np.abs(log_cdf(mid, model, amplitude)-(cdf[:-1]+cdf[1:])/2))
    return dict(log_knots=u, probabilities=cdf, maximum_midpoint_cdf_error=float(error))


def sample_cohorts(model, amplitude, sample_size, replicates, bins, rng, *, table=None, chunk=64, resource_exponent=1.):
    """Exact log sums, bin counts, and physical resource sums within each bin."""
    for value in (sample_size, replicates, bins, chunk):
        if isinstance(value, bool) or int(value) != value or value < 1:
            raise ValueError('Positive integer sample sizes, replicates, bins, and chunks required')
    width = model['log_width']
    if not np.isfinite(resource_exponent):
        raise ValueError('Finite independently fixed physical resource exponent required')
    counts = np.empty((replicates, bins), dtype=np.int64)
    resource = np.empty((replicates, bins), dtype=float)
    sums = np.empty(replicates, dtype=float)
    for start in range(0, replicates, chunk):
        stop = min(start+chunk, replicates)
        uniforms = rng.random((stop-start, sample_size))
        if amplitude == 0:
            u = -np.log1p(-uniforms*(-np.expm1(-model['rate']*width)))/model['rate']
        else:
            if table is None:
                raise ValueError('A pre-audited inverse-CDF table is required for curved sampling')
            u = np.interp(uniforms, table['probabilities'], table['log_knots'])
        index = np.minimum((u*bins/width).astype(np.int64), bins-1)
        offsets = np.arange(stop-start, dtype=np.int64)[:, None]*bins
        counts[start:stop] = np.bincount((index+offsets).ravel(), minlength=(stop-start)*bins).reshape(stop-start, bins)
        resource[start:stop] = np.bincount((index+offsets).ravel(), weights=np.exp(resource_exponent*u).ravel(),
                                          minlength=(stop-start)*bins).reshape(stop-start, bins)
        sums[start:stop] = u.sum(axis=1)
    return dict(log_sums=sums, counts=counts, resource_bin_totals=resource,
                exponent=bounded_power_mle(sums/sample_size, width))


def binned_deviance(counts, probability):
    counts = np.asarray(counts)
    p = np.asarray(probability, dtype=float)
    if p.ndim != 1 or np.any(~np.isfinite(p)) or np.any(p <= 0) or not np.isclose(p.sum(), 1, rtol=0, atol=1e-12):
        raise ValueError('Positive normalized class probabilities required')
    if counts.shape[-1] != len(p) or np.any(counts < 0) or np.any(counts != np.floor(counts)) or np.any(counts.sum(axis=-1) <= 0):
        raise ValueError('Aligned nonempty integer counts required')
    expected = counts.sum(axis=-1, keepdims=True)*p
    return 2*xlogy(counts, counts/expected).sum(axis=-1)


def population_summary(model, amplitude, resource_exponent, bins):
    """Independent quadrature checks, physical resource profile, and exact MLE."""
    width = model['log_width']
    norm = quad(lambda u: float(log_density(u, model, amplitude)), 0, width, epsabs=1e-12)[0]
    mean = quad(lambda u: u*float(log_density(u, model, amplitude)), 0, width, epsabs=1e-12)[0]/norm
    second = quad(lambda u: u*u*float(log_density(u, model, amplitude)), 0, width, epsabs=1e-12)[0]/norm
    edges = np.linspace(0, width, bins+1)
    probability = np.diff(log_cdf(edges, model, amplitude))
    resource = np.array([quad(lambda u: np.exp(resource_exponent*u)*float(log_density(u, model, amplitude)), lo, hi,
                             epsabs=1e-12)[0]/(hi-lo) for lo, hi in zip(edges[:-1], edges[1:])])
    center = float(np.mean(resource))
    normalized = resource/center
    return dict(probability_integral=float(norm), mean_log_size=float(mean),
                variance_log_size=float(second-mean*mean),
                population_bounded_power_mle=float(bounded_power_mle(mean, width)),
                object_bin_probabilities=probability.tolist(), resource_per_log_bin=resource.tolist(),
                normalized_resource_per_log_bin=normalized.tolist(),
                binned_max_log_departure=float(np.max(np.abs(np.log(normalized)))),
                binned_resource_max_min_ratio=float(normalized.max()/normalized.min()))


def coordinate_prediction(exponent, resource_exponent, coordinate_power):
    """x -> y=x**c, transporting the same objects and same physical resource."""
    if not np.isfinite(coordinate_power) or coordinate_power <= 0:
        raise ValueError('Finite positive coordinate power required')
    return dict(coordinate_power=float(coordinate_power),
                density_exponent=float(1+(exponent-1)/coordinate_power),
                physical_cost_exponent=float(resource_exponent/coordinate_power),
                log_resource_density_jacobian=float(1/coordinate_power),
                normalized_resource_profile='unchanged at corresponding transformed bin edges')
