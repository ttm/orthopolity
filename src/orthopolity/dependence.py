"""Fixed-marginal capacity models and forward joint-feasibility predictions.

These are known or elementary copula constructions, not empirical allocation
laws. Numerical integration predicts bounded resource profiles independently
of sampled output sizes. All Pareto marginal survival functions are 1/x.
"""
from functools import lru_cache
from math import gamma

import numpy as np
from numpy.polynomial.hermite import hermgauss
from numpy.polynomial.legendre import leggauss
from scipy.integrate import quad
from scipy.stats import chi2, kendalltau, norm, t


def _validate(family, resources, parameter, df):
    if family not in ("independent", "common_shock", "gaussian", "student"):
        raise ValueError("Unknown capacity family")
    if isinstance(resources, (bool, np.bool_)) or not isinstance(resources, (int, np.integer)) or resources < 1:
        raise ValueError("resources must be a positive integer")
    if not np.isfinite(parameter) or not 0 <= parameter <= 1:
        raise ValueError("parameter must lie in [0,1]")
    if not np.isfinite(df) or df <= 0:
        raise ValueError("df must be positive and finite")


def capacity_samples(n, resources, family, parameter, rng, *, df=4, cap=None):
    """Equicorrelated Gaussian/t copulas, or a common-shock construction.

    The parameter is latent correlation rho for Gaussian/t and shared hazard
    theta for common shocks. These parameters are not interchangeable. Student
    rho=0 is not independence: a common random scale remains. A cap clips each
    capacity and introduces an atom; it is not conditional tail truncation.
    """
    _validate(family, resources, parameter, df)
    if isinstance(n, (bool, np.bool_)) or not isinstance(n, (int, np.integer)) or n < 1:
        raise ValueError("n must be a positive integer")
    if cap is not None and (not np.isfinite(cap) or cap <= 1):
        raise ValueError("cap must be finite and greater than one")
    if family == "independent":
        log_x = rng.exponential(size=(n, resources))
    elif family == "common_shock":
        shared = rng.exponential(1 / parameter, size=(n, 1)) if parameter else np.full((n, 1), np.inf)
        own = rng.exponential(1 / (1-parameter), size=(n, resources)) if parameter < 1 else np.full((n, resources), np.inf)
        log_x = np.minimum(shared, own)
    else:
        latent = np.sqrt(parameter) * rng.standard_normal((n, 1)) + np.sqrt(1-parameter) * rng.standard_normal((n, resources))
        if family == "student":
            latent /= np.sqrt(rng.chisquare(df, size=(n, 1)) / df)
            log_x = -t.logsf(latent, df)
        else:
            log_x = -norm.logsf(latent)
    if cap is not None:
        log_x = np.minimum(log_x, np.log(cap))
    with np.errstate(over="raise"):
        capacities = np.exp(log_x)
    # Preserve an exact endpoint atom despite exp(log(cap)) roundoff.
    return np.where(log_x == np.log(cap), cap, capacities) if cap is not None else capacities


@lru_cache(maxsize=8)
def _normal_rule(order):
    nodes, weights = hermgauss(order)
    return np.sqrt(2) * nodes, weights / np.sqrt(np.pi)


@lru_cache(maxsize=32768)
def _survival_one(x, resources, family, parameter, df, order):
    if x <= 1:
        return 1.0
    if family == "independent" or (family == "gaussian" and parameter == 0):
        return x ** (-resources)
    if resources == 1 or parameter == 1:
        return 1 / x
    if family == "common_shock":
        return x ** (-(resources-(resources-1)*parameter))
    root_rho, root_other = np.sqrt(parameter), np.sqrt(1-parameter)
    if family == "gaussian":
        threshold = norm.isf(1 / x)
        value = quad(lambda z: norm.pdf(z) * norm.sf((threshold-root_rho*z)/root_other)**resources,
                     -np.inf, np.inf, epsabs=1e-13, epsrel=2e-9, limit=150)[0]
        return float(value)
    threshold = t.isf(1 / x, df)
    z, weights = _normal_rule(order)
    def normal_probability(boundary):
        return float(np.dot(weights, norm.sf((boundary-root_rho*z)/root_other)**resources))
    if threshold >= 1:
        # Scale the chi-square mixture integral to avoid concentrating a tiny
        # probability into an increasingly narrow region near zero.
        prefactor = (df / threshold**2) ** (df/2) / (2**(df/2) * gamma(df/2))
        integrand = lambda u: u**(df/2-1) * np.exp(-df*u/(2*threshold**2)) * normal_probability(np.sqrt(u))
        value = prefactor * quad(integrand, 0, np.inf, epsabs=1e-10, epsrel=2e-8, limit=150)[0]
    else:
        value = quad(lambda w: chi2.pdf(w, df) * normal_probability(threshold*np.sqrt(w/df)),
                     0, np.inf, epsabs=1e-11, epsrel=2e-8, limit=150)[0]
    return float(value)


def joint_survival(x, resources, family, parameter=0, *, df=4, cap=None, order=96):
    """P(min capacities >= x), exact or deterministic numerical integration.

    Gaussian prediction is a one-factor normal integral. Student prediction
    integrates its normal/chi-square mixture; Gauss-Hermite integrates the
    normal factor, with adaptive integration over the common random scale.
    Prediction at a finite cap includes its point mass, whereas x>cap gives 0.
    """
    _validate(family, resources, parameter, df)
    values = np.asarray(x, dtype=float)
    if np.any(~np.isfinite(values)) or np.any(values <= 0):
        raise ValueError("finite positive thresholds required")
    if cap is not None and (not np.isfinite(cap) or cap <= 1):
        raise ValueError("cap must be finite and greater than one")
    result = np.asarray([0.0 if cap is not None and value > cap else _survival_one(float(value), int(resources), family, float(parameter), float(df), int(order))
                         for value in values.ravel()]).reshape(values.shape)
    return float(result) if values.ndim == 0 else result


def student_bivariate_survival_check(x, rho, df=4):
    """Independent conditional-t integration, used to audit mixture quadrature."""
    if x <= 1:
        return 1.0
    threshold = t.isf(1 / x, df)
    def integrand(y):
        scale = np.sqrt((df+y*y)*(1-rho*rho)/(df+1))
        return t.pdf(y, df) * t.sf((threshold-rho*y)/scale, df+1)
    return float(quad(integrand, threshold, np.inf, epsabs=1e-12, epsrel=1e-9, limit=150)[0])


def asymptotic_dimension(resources, family, parameter=0):
    """Joint-survival index for uncapped unit-Pareto equicorrelated models."""
    _validate(family, resources, parameter, 4)
    if family == "independent":
        return float(resources)
    if family == "common_shock":
        return float(resources-(resources-1)*parameter)
    if family == "gaussian":
        return float(resources/(1+(resources-1)*parameter))
    return 1.0


def student_tail_coefficient(rho, df=4):
    """Bivariate upper-tail dependence, not a Pearson correlation."""
    if not np.isfinite(rho) or not -1 < rho <= 1 or not np.isfinite(df) or df <= 0:
        raise ValueError("valid rho and df required")
    return float(2*t.cdf(-np.sqrt((df+1)*(1-rho)/(1+rho)), df+1))


def finite_dimension(x, resources, family, parameter=0, *, df=4, cap=None):
    """Local joint-survival elasticity, not a fitted asymptotic tail exponent."""
    thresholds = np.asarray(x, float)
    step = .015
    left, right = thresholds*np.exp(-step), thresholds*np.exp(step)
    if np.any(left <= 1) or (cap is not None and np.any(right >= cap)):
        raise ValueError("elasticity requires an interior smooth domain")
    return -(np.log(joint_survival(right, resources, family, parameter, df=df))-
             np.log(joint_survival(left, resources, family, parameter, df=df)))/(2*step)


def forward_resource_profile(edges, resources, family, parameter=0, *, df=4, cap=None, cost_exponent=1, integration_order=24, normal_order=96):
    """Expected q(K)=K**d in each fixed log bin, including a cap's atom.

    Integration by parts: E[K**d; a<=K<b] = a**d S(a)-b**d S(b)
    + d integral_a^b x**(d-1) S(x) dx. Legendre quadrature is on log x.
    The last bin includes its endpoint and a possible imposed-cap atom.
    """
    edges = np.asarray(edges, float)
    if edges.ndim != 1 or len(edges) < 2 or np.any(~np.isfinite(edges)) or edges[0] < 1 or np.any(np.diff(edges) <= 0):
        raise ValueError("increasing finite edges above or equal to one required")
    if not np.isfinite(cost_exponent) or cost_exponent <= 0:
        raise ValueError("positive finite cost exponent required")
    if cap is not None and edges[-1] > cap:
        raise ValueError("profile domain must not extend above cap")
    nodes, weights = leggauss(integration_order)
    log_edges = np.log(edges)
    integrals = []
    for a, b, lo, hi in zip(edges[:-1], edges[1:], log_edges[:-1], log_edges[1:]):
        xx = np.exp((lo+hi)/2 + (hi-lo)*nodes/2)
        surv = joint_survival(xx, resources, family, parameter, df=df, order=normal_order)
        integral = (hi-lo)/2*np.dot(weights, xx**cost_exponent*surv)
        value = a**cost_exponent*joint_survival(a, resources, family, parameter, df=df, order=normal_order)-b**cost_exponent*joint_survival(b, resources, family, parameter, df=df, order=normal_order)+cost_exponent*integral
        integrals.append(value)
    if cap is not None and edges[-1] == cap:
        integrals[-1] += cap**cost_exponent*joint_survival(cap, resources, family, parameter, df=df, order=normal_order)
    totals = np.asarray(integrals)
    if np.any(totals <= 0):
        raise ArithmeticError("numerical integration produced a nonpositive resource bin")
    widths = np.diff(log_edges)
    density = totals / widths
    phi = density / (totals.sum()/widths.sum())
    return dict(resource_totals=totals, resource_density=density, phi=phi)


def estimate_dependence_parameter(capacities, family):
    """Fit only from independent capacity-training observations.

    Gaussian/t: invert averaged Kendall tau; Student df remains predeclared.
    Common shock: invert joint exceedance at the fixed training threshold two.
    Family identification is assumed, not learned or validated here.
    """
    x = np.asarray(capacities, float)
    if x.ndim != 2 or len(x) < 2 or x.shape[1] < 2 or np.any(~np.isfinite(x)) or np.any(x < 1):
        raise ValueError("an aligned capacity-training matrix is required")
    resources = x.shape[1]
    if family == "independent":
        return 0.0
    if family == "common_shock":
        probability = np.mean(np.all(x >= 2, axis=1))
        if probability <= 0:
            raise ValueError("no training joint exceedances")
        return float(np.clip((resources+np.log(probability)/np.log(2))/(resources-1), 0, 1))
    if family not in ("gaussian", "student"):
        raise ValueError("unknown family")
    tau = np.mean([kendalltau(x[:, i], x[:, j]).statistic for i in range(resources) for j in range(i+1, resources)])
    return float(np.clip(np.sin(np.pi*tau/2), 0, .999))
