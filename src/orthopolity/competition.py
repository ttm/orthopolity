"""Bivariate Gaussian capacities including competition and singular endpoints.

Both margins have survival 1/x. Exact conditional-normal calculations predict
the minimum's density and survival without fitting its observed exponent.
"""
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.integrate import quad
from scipy.stats import norm


def _rho(value):
    if not np.isfinite(value) or not -1 <= value <= 1:
        raise ValueError('rho must be finite and lie in [-1,1]')
    return float(value)


def competing_capacities(n, rho, rng):
    """Fixed unit-Pareto marginals, with a declared latent Gaussian correlation."""
    rho = _rho(rho)
    if isinstance(n, (bool, np.bool_)) or not isinstance(n, (int, np.integer)) or n < 1:
        raise ValueError('n must be a positive integer')
    first = rng.standard_normal(n)
    second = rho * first + np.sqrt(1-rho*rho) * rng.standard_normal(n)
    with np.errstate(over='raise'):
        return np.exp(-norm.logsf(np.column_stack([first, second])))


def minimum_survival(x, rho):
    """Exact endpoints/independence; conditional-normal quadrature otherwise."""
    rho = _rho(rho)
    values = np.asarray(x, float)
    if np.any(~np.isfinite(values)) or np.any(values <= 0):
        raise ValueError('thresholds must be finite and positive')
    def one(k):
        if k <= 1: return 1.0
        if rho == -1: return max(0.0, 2/k-1)
        if rho == 1: return 1/k
        if rho == 0: return 1/(k*k)
        z = norm.isf(1/k)
        scale = np.sqrt(1-rho*rho)
        return quad(lambda y: norm.pdf(y)*norm.sf((z-rho*y)/scale),
                    z, np.inf, epsabs=0, epsrel=2e-10, limit=160)[0]
    result = np.asarray([one(float(k)) for k in values.ravel()]).reshape(values.shape)
    return float(result) if result.ndim == 0 else result


def minimum_density(x, rho):
    """Density obtained by differentiating the diagonal joint survival."""
    rho = _rho(rho)
    values = np.asarray(x, float)
    if np.any(~np.isfinite(values)) or np.any(values <= 0):
        raise ValueError('sizes must be finite and positive')
    result = np.zeros_like(values)
    inside = values >= 1
    k = values[inside]
    if rho == -1:
        result[inside] = np.where(k < 2, 2/k**2, 0)
    elif rho == 1:
        result[inside] = 1/k**2
    else:
        a = np.sqrt((1-rho)/(1+rho))
        result[inside] = 2*norm.sf(a*norm.isf(1/k))/k**2
    return float(result) if result.ndim == 0 else result


def local_dimensions(x, rho):
    """Separate survival elasticity from the local count-density exponent."""
    rho = _rho(rho)
    values = np.asarray(x, float)
    if np.any(~np.isfinite(values)) or np.any(values <= 1) or (rho == -1 and np.any(values >= 2)):
        raise ValueError('dimensions require sizes in the interior smooth support')
    survival = minimum_survival(values, rho)
    density = minimum_density(values, rho)
    feasibility = values*density/survival
    if rho in (-1, 1):
        alpha = np.full_like(values, 2.0)
    else:
        z = norm.isf(1/values)
        a = np.sqrt((1-rho)/(1+rho))
        alpha = 2+a*np.exp(norm.logpdf(a*z)-norm.logsf(a*z)-norm.logpdf(z)-np.log(values))
    return dict(feasibility=feasibility, density_exponent=alpha)


def forward_resource_profile(edges, rho, *, cost_exponent=1, order=48):
    """Finite-domain expected additive resource, integrated in log size."""
    rho = _rho(rho)
    edges = np.asarray(edges, float)
    if edges.ndim != 1 or len(edges) < 2 or np.any(~np.isfinite(edges)) or edges[0] < 1 or np.any(np.diff(edges) <= 0):
        raise ValueError('increasing finite edges above or equal to one required')
    if not np.isfinite(cost_exponent) or cost_exponent <= 0:
        raise ValueError('positive finite cost exponent required')
    if rho == -1 and edges[-1] > 2:
        raise ValueError('opposed-resource profile must stay within its finite support')
    nodes, weights = leggauss(order)
    widths = np.diff(np.log(edges))
    totals = []
    for lo, hi in zip(np.log(edges[:-1]), np.log(edges[1:])):
        k = np.exp((lo+hi)/2+(hi-lo)*nodes/2)
        totals.append((hi-lo)/2*np.dot(weights, k**(cost_exponent+1)*minimum_density(k,rho)))
    totals = np.asarray(totals)
    if np.any(totals <= 0):
        raise ArithmeticError('resource profile contains a nonpositive bin')
    return dict(totals=totals, phi=(totals/widths)/(totals.sum()/widths.sum()))
