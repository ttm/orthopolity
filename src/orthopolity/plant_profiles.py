"""Development-only forecasts of count and additive dry-mass profiles.

The stock forecast normalizes expected bin masses. It is not the expectation
of the normalized profile of a finite random census. All densities are bounded
on the same development-defined support; no function loads study data.
"""
from __future__ import annotations

import math

import numpy as np
from scipy.integrate import quad
from scipy.optimize import minimize, minimize_scalar
from scipy.special import logsumexp


def _masses(values):
    values = np.asarray(values, dtype=float)
    if values.ndim != 1 or not np.all(np.isfinite(values)) or np.any(values <= 0):
        raise ValueError('Masses must be a one-dimensional positive finite vector')
    return values


def _bounds(lower, upper):
    if not math.isfinite(lower) or not math.isfinite(upper) or not 0 < lower < upper:
        raise ValueError('Bounds must be finite and satisfy 0 < lower < upper')


def _log_power_integral(lower, upper, exponent):
    """Log integral of m**exponent, avoiding subtraction of nearby powers."""
    power = exponent + 1.
    width = math.log(upper/lower)
    if abs(power) < 1e-12:
        return math.log(width)
    if power > 0:
        return power*math.log(upper) + math.log(-math.expm1(-power*width)) - math.log(power)
    return power*math.log(lower) + math.log(-math.expm1(power*width)) - math.log(-power)


def _power_model(edges, alpha):
    count_logs = [_log_power_integral(a, b, -alpha) for a, b in zip(edges[:-1], edges[1:])]
    stock_logs = [_log_power_integral(a, b, 1.-alpha) for a, b in zip(edges[:-1], edges[1:])]
    return _model(count_logs, stock_logs)


def _model(count_logs, stock_logs):
    count_logs = np.asarray(count_logs, dtype=float)
    stock_logs = np.asarray(stock_logs, dtype=float)
    count_logs = count_logs - logsumexp(count_logs)
    stock_logs = stock_logs - logsumexp(stock_logs)
    return dict(count_shares=np.exp(count_logs).tolist(), stock_shares=np.exp(stock_logs).tolist(),
                count_log_shares=count_logs.tolist())


def draw_bounded_power(rng, n, lower, upper, alpha):
    """Draw n masses with density proportional to m**(-alpha) on [L,U]."""
    _bounds(lower, upper)
    if not math.isfinite(alpha) or not isinstance(n, (int, np.integer)) or n < 0:
        raise ValueError('A finite exponent and nonnegative integer draw count are required')
    u = rng.random(n)
    power = 1.-alpha
    if abs(power) < 1e-10:
        return np.exp(math.log(lower)+u*math.log(upper/lower))
    with np.errstate(divide='ignore'):
        logs = np.logaddexp(np.log1p(-u)+power*math.log(lower), np.log(u)+power*math.log(upper))
    return np.clip(np.exp(logs/power), lower, upper)


def _power_difference(lower, upper, shape, log_scale):
    """(upper/scale)**shape - (lower/scale)**shape, stably."""
    if upper == lower:
        return 0.
    z = shape*math.log(upper/lower)
    log_expm1 = z + math.log1p(-math.exp(-z)) if z > 50 else math.log(math.expm1(z))
    log_difference = shape*(math.log(lower)-log_scale)+log_expm1
    return math.exp(log_difference) if log_difference < 709 else math.inf


def _weibull_logpdf_logs(log_values, lower, upper, shape, log_scale):
    span = _power_difference(lower, upper, shape, log_scale)
    log_normalizer = math.log(-math.expm1(-span))
    z = shape*(log_values-math.log(lower))
    with np.errstate(over='ignore', invalid='ignore'):
        # log(expm1(z)) is evaluated separately in its small and large regimes.
        log_delta = np.full_like(z, -math.inf)
        small = (z > 0) & (z <= 50)
        large = z > 50
        log_delta[small] = np.log(np.expm1(z[small]))
        log_delta[large] = z[large]+np.log1p(-np.exp(-z[large]))
        delta = np.exp(shape*(math.log(lower)-log_scale)+log_delta)
        return math.log(shape)-log_scale+(shape-1.)*(log_values-log_scale)-delta-log_normalizer


def weibull_logpdf(masses, lower, upper, shape, scale):
    """Log density of a Weibull conditional on [lower,upper]."""
    _bounds(lower, upper)
    values = _masses(masses)
    if not math.isfinite(shape) or not math.isfinite(scale) or shape <= 0 or scale <= 0:
        raise ValueError('Weibull shape and scale must be positive and finite')
    result = np.full(values.shape, -math.inf)
    inside = (values >= lower) & (values <= upper)
    result[inside] = _weibull_logpdf_logs(np.log(values[inside]), lower, upper, shape, math.log(scale))
    return result


def _weibull_model(edges, shape, scale):
    """Bin probabilities and first moments using shifted exponential quadrature.

    Integrating in s=(m/scale)**shape-(L/scale)**shape avoids underflow of
    the Weibull survival at L. A 200-unit local exponential tail truncation
    has negligible relative error for the fitted shape range [0.1,5].
    """
    lower, upper = edges[0], edges[-1]
    log_scale = math.log(scale)
    log_t_lower = shape*(math.log(lower)-log_scale)
    span = _power_difference(lower, upper, shape, log_scale)
    log_z = math.log(-math.expm1(-span))
    count_logs, stock_logs = [], []
    for a, b in zip(edges[:-1], edges[1:]):
        offset = _power_difference(lower, a, shape, log_scale)
        gap = _power_difference(a, b, shape, log_scale)
        count_logs.append(-offset+math.log(-math.expm1(-gap))-log_z)
        if not math.isfinite(offset):
            stock_logs.append(-math.inf)
            continue

        def log_mass(s):
            if s == 0:
                return math.log(lower)
            return log_scale+float(np.logaddexp(log_t_lower, math.log(s)))/shape

        reference = log_mass(offset+min(gap, 1.))
        if gap < 1.:
            integral = quad(lambda u: math.exp(log_mass(offset+gap*u)-reference-gap*u),
                            0., 1., epsabs=1e-12, epsrel=1e-11)[0]
            log_integral = math.log(gap)+reference+math.log(integral)
        else:
            integral = quad(lambda v: math.exp(log_mass(offset+v)-reference-v),
                            0., min(gap, 200.), epsabs=1e-12, epsrel=1e-11)[0]
            log_integral = reference+math.log(integral)
        stock_logs.append(-offset+log_integral)
    return _model(count_logs, stock_logs)


def profile(masses, domain):
    """Observed bin counts/masses and explicit lower/upper tail coverage.

    Internal boundaries belong to the next bin; the final upper bound is
    included. Empty in-domain samples have null shares and remain scoreable
    only after the caller declares an exclusion rule.
    """
    values = _masses(masses)
    lower, upper = float(domain['lower']), float(domain['upper'])
    _bounds(lower, upper)
    edges = np.asarray(domain['edges'], dtype=float)
    if edges.ndim != 1 or len(edges) < 2 or not np.all(np.isfinite(edges)) or edges[0] != lower or edges[-1] != upper or np.any(np.diff(edges) <= 0):
        raise ValueError('Domain edges must increase from its lower to upper bound')
    below, above = values < lower, values > upper
    inside = ~(below | above)
    selected = values[inside]
    counts = np.histogram(selected, bins=edges)[0]
    stocks = np.histogram(selected, bins=edges, weights=selected)[0]
    total_count, total_mass = len(values), float(values.sum())
    in_count, in_mass = len(selected), float(selected.sum())
    return dict(raw_count=total_count, raw_mass=total_mass,
                below_count=int(below.sum()), below_mass=float(values[below].sum()),
                in_domain_count=in_count, in_domain_mass=in_mass,
                above_count=int(above.sum()), above_mass=float(values[above].sum()),
                counts=counts.tolist(), stocks=stocks.tolist(),
                count_shares=(counts/in_count).tolist() if in_count else None,
                stock_shares=(stocks/in_mass).tolist() if in_mass else None,
                count_coverage=in_count/total_count if total_count else None,
                mass_coverage=in_mass/total_mass if total_mass else None)


def fit_forecasts(development, lower=0.01, bin_log10_width=0.5):
    """Fit five declared profile models using complete development plots only.

    Each plot gets equal weight in histograms and unbinned likelihoods.
    The upper support is the next enclosing power of ten, determined solely
    from the maximum positive development mass. Below-L masses are excluded
    from fitting and retained in the reported coverage.
    """
    if not development or not math.isfinite(lower) or lower <= 0 or not math.isfinite(bin_log10_width) or bin_log10_width <= 0:
        raise ValueError('Nonempty development plots and positive finite domain settings are required')
    units = sorted(development)
    arrays = {unit: _masses(development[unit]) for unit in units}
    if any(not len(values) for values in arrays.values()):
        raise ValueError('Development plots must not be empty')
    maximum = max(float(values.max()) for values in arrays.values())
    upper = 10.**math.ceil(math.log10(maximum))
    if upper < maximum:  # Guard the ceil/power round trip at exact powers of ten.
        upper *= 10.
    _bounds(lower, upper)
    log_lower, log_upper = math.log10(lower), math.log10(upper)
    n_bins = int(math.ceil((log_upper-log_lower)/bin_log10_width-1e-12))
    edges = [10.**(log_lower+i*bin_log10_width) for i in range(n_bins)]+[upper]
    edges[0] = float(lower)
    domain = dict(lower=float(lower), upper=float(upper), edges=edges, bin_log10_width=float(bin_log10_width))
    observed = {unit: profile(values, domain) for unit, values in arrays.items()}
    if any(row['in_domain_count'] == 0 for row in observed.values()):
        raise ValueError('Every development plot must contain at least one in-domain mass')
    logs = [np.log(values[(values >= lower) & (values <= upper)]) for values in arrays.values()]
    average_log_mass = float(np.mean([values.mean() for values in logs]))

    def pareto_loss(alpha):
        return alpha*average_log_mass+_log_power_integral(lower, upper, -alpha)

    fitted = minimize_scalar(pareto_loss, bounds=(-2., 4.), method='bounded', options={'xatol': 1e-10})
    if not fitted.success or not math.isfinite(float(fitted.fun)) or not math.isfinite(float(fitted.x)):
        raise ValueError('Bounded Pareto optimization failed to converge')
    alpha = min([-2., 4., float(fitted.x)], key=lambda value: (pareto_loss(value), value))

    def weibull_loss(theta):
        shape, log_scale = math.exp(float(theta[0])), float(theta[1])
        likelihood = float(np.mean([np.mean(_weibull_logpdf_logs(values, lower, upper, shape, log_scale))
                                    for values in logs]))
        return -likelihood if math.isfinite(likelihood) else 1e100

    bounds = [(math.log(.1), math.log(5.)), (math.log(lower/100.), math.log(upper*100.))]
    pooled = np.concatenate(logs)
    scale_starts = np.quantile(pooled, [.25, .5, .75])
    candidates, restart_statuses = [], []
    for shape_start in (.3, .8, 1.5, 3.5):
        for scale_start in scale_starts:
            start = np.array([math.log(shape_start), float(scale_start)])
            result = minimize(weibull_loss, start, method='L-BFGS-B', bounds=bounds,
                              options={'maxiter': 600, 'ftol': 1e-12, 'gtol': 1e-7})
            converged = bool(result.success) and math.isfinite(float(result.fun)) and np.all(np.isfinite(result.x))
            restart_statuses.append(dict(start_shape=shape_start, start_scale=math.exp(float(scale_start)),
                                         success=bool(result.success), usable=bool(converged),
                                         status=int(result.status), message=str(result.message),
                                         iterations=int(getattr(result, 'nit', 0))))
            if converged:
                candidates.append((float(result.fun), tuple(float(value) for value in result.x)))
    if not candidates:
        raise ValueError('No bounded Weibull optimization restart converged')
    loss, theta = min(candidates)
    shape, scale = math.exp(theta[0]), math.exp(theta[1])
    counts = np.mean([(np.array(row['counts'])+.5)/(row['in_domain_count']+.5*n_bins)
                      for row in observed.values()], axis=0)
    stocks = np.mean([row['stock_shares'] for row in observed.values()], axis=0)
    models = dict(log_neutral=_power_model(edges, 2.), linear_neutral=_power_model(edges, 1.),
                  empirical=dict(count_shares=counts.tolist(), stock_shares=stocks.tolist(),
                                 count_log_shares=np.log(counts).tolist()),
                  bounded_pareto=_power_model(edges, alpha), bounded_weibull=_weibull_model(edges, shape, scale))
    bins = [dict(lower=a, upper=b, log10_width=math.log10(b/a), linear_width=b-a,
                 upper_inclusive=i == n_bins-1) for i, (a, b) in enumerate(zip(edges[:-1], edges[1:]))]
    return dict(domain=domain, bins=bins, development_units=units,
                development_profiles=observed,
                parameters=dict(bounded_pareto=dict(alpha=alpha, bounds=[-2., 4.], mean_log_mass=average_log_mass,
                                                   optimizer_success=bool(fitted.success),
                                                   optimizer_status=int(fitted.status), optimizer_message=str(fitted.message)),
                                bounded_weibull=dict(shape=shape, scale=scale, negative_loglikelihood=loss,
                                                     shape_bounds=[.1, 5.], scale_bounds=[lower/100., upper*100.], restarts=12,
                                                     start_shapes=[.3, .8, 1.5, 3.5], start_scale_log_quantiles=[.25, .5, .75],
                                                     successful_restarts=len(candidates), restart_statuses=restart_statuses),
                                empirical=dict(count_pseudocount=.5, plot_weighting='equal')),
                models=models)


def score_profile(forecasts, observed):
    """Descriptive stock/count total variation and per-object binned log loss."""
    if not observed['in_domain_count']:
        raise ValueError('An empty in-domain profile cannot be scored')
    count = np.asarray(observed['count_shares'], dtype=float)
    stock = np.asarray(observed['stock_shares'], dtype=float)
    result = {}
    for name, model in forecasts['models'].items():
        predicted_count = np.asarray(model['count_shares'], dtype=float)
        predicted_stock = np.asarray(model['stock_shares'], dtype=float)
        if predicted_count.shape != count.shape or predicted_stock.shape != stock.shape:
            raise ValueError('Forecast and observation bins must match')
        for shares in (predicted_count, predicted_stock):
            if np.any(shares < 0) or not np.all(np.isfinite(shares)) or not math.isclose(float(shares.sum()), 1., abs_tol=1e-9):
                raise ValueError('Forecast shares must be nonnegative and normalized')
        with np.errstate(divide='ignore'):
            log_shares = np.asarray(model.get('count_log_shares', np.log(predicted_count)), dtype=float)
        occupied = count > 0
        result[name] = dict(stock_tv=float(np.abs(stock-predicted_stock).sum()/2.),
                            count_tv=float(np.abs(count-predicted_count).sum()/2.),
                            count_logloss=float(-np.dot(count[occupied], log_shares[occupied])))
    return result
