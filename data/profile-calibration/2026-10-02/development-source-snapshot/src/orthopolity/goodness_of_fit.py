"""Goodness-of-fit and equivalence tests for bounded resource-spectrum analyses.

Two families of test, both required before any confirmatory claim:

1. Distribution goodness-of-fit, in the spirit of Clauset, Shalizi and Newman
   (2009): maximum-likelihood fits, a Kolmogorov-Smirnov statistic, a
   parametric bootstrap p-value, and Vuong likelihood-ratio comparisons
   against lognormal, exponential and stretched-exponential alternatives.

2. Equivalence testing for flatness of a resource spectrum. Failure to reject
   a zero slope is not evidence of flatness; a declared tolerance is required,
   and a slope criterion alone is insufficient because a spectrum can undulate
   with zero fitted slope.

Every fit here is on an explicitly declared bounded domain [lo, hi]. The lower
bound is never estimated from the data. This departs from the usual CSN
practice of selecting x_min by minimising the KS distance, deliberately: the
protocol this module serves declares the domain in advance, and choosing it
afterwards is the threshold-shopping failure the project is trying to avoid.
Alternatives are therefore fitted on the same truncated support, so the
likelihood ratios compare like with like.
"""
import numpy as np
from scipy.optimize import minimize, minimize_scalar
from scipy.special import erfc, expm1
from scipy.stats import norm

__all__ = ['fit_powerlaw', 'fit_lognormal', 'fit_exponential', 'fit_weibull',
           'ks_distance', 'powerlaw_gof', 'vuong', 'compare_alternatives',
           'flatness_equivalence', 'sample_powerlaw',
           'geometric_mle', 'discrete_ks', 'discrete_gr_gof']

_TINY = 1e-12


def _check(x, lo, hi):
    x = np.asarray(x, float)
    if not np.isfinite([lo, hi]).all() or lo <= 0 or hi <= lo:
        raise ValueError('Domain must satisfy 0 < lo < hi')
    if x.ndim != 1 or len(x) < 2 or not np.all(np.isfinite(x)):
        raise ValueError('At least two finite observations required')
    if np.any((x < lo) | (x > hi)):
        raise ValueError('Observations outside the declared domain; select before fitting')
    return x


# --------------------------------------------------------------------------
# Truncated power law:  p(x) proportional to x**-alpha on [lo, hi]
# --------------------------------------------------------------------------

def _pl_logpdf(x, alpha, lo, hi):
    """Log density of the bounded power law, stable near alpha == 1."""
    t = alpha - 1.0
    L = np.log(hi / lo)
    z = np.log(np.asarray(x, float) / lo)
    # density of z is t*exp(-t z)/(1-exp(-t L)) on [0, L]
    if abs(t) < 1e-9:
        log_norm = np.log(L)
    else:
        log_norm = np.log(-expm1(-t * L) / t)
    return -t * z - log_norm - np.log(np.asarray(x, float))


def fit_powerlaw(x, lo, hi):
    """MLE exponent alpha for p(x) proportional to x**-alpha on [lo, hi]."""
    x = _check(x, lo, hi)
    z = np.log(x / lo)
    L = np.log(hi / lo)

    def nll(t):
        if abs(t) < 1e-9:
            return np.log(L) + t * z.mean()
        return t * z.mean() + np.log(-expm1(-t * L) / t)

    fit = minimize_scalar(nll, bounds=(-5, 10), method='bounded')
    if not fit.success:
        raise RuntimeError('Bounded power-law fit failed')
    return dict(name='power_law', params=dict(alpha=float(1 + fit.x)),
                loglike=float(-len(x) * fit.fun - np.log(x).sum()))


def _pl_cdf(x, alpha, lo, hi):
    t = alpha - 1.0
    z = np.log(np.asarray(x, float) / lo)
    L = np.log(hi / lo)
    if abs(t) < 1e-9:
        return z / L
    return -expm1(-t * z) / -expm1(-t * L)


def sample_powerlaw(n, alpha, lo, hi, rng):
    """Inverse-CDF draw from the bounded power law."""
    u = rng.random(n)
    t = alpha - 1.0
    L = np.log(hi / lo)
    if abs(t) < 1e-9:
        z = u * L
    else:
        z = -np.log1p(u * expm1(-t * L)) / t
    return lo * np.exp(z)


# --------------------------------------------------------------------------
# Truncated alternatives, all on the same support
# --------------------------------------------------------------------------

def _trunc_fit(x, lo, hi, logpdf, x0, name, pnames):
    x = _check(x, lo, hi)

    def nll(p):
        with np.errstate(all='ignore'):
            v = logpdf(x, p)
            if not np.all(np.isfinite(v)):
                return 1e12
            return -float(v.sum())

    best = None
    for start in x0:
        try:
            r = minimize(nll, start, method='Nelder-Mead',
                         options=dict(maxiter=4000, xatol=1e-10, fatol=1e-10))
        except Exception:
            continue
        if r.success or np.isfinite(r.fun):
            if best is None or r.fun < best.fun:
                best = r
    if best is None:
        raise RuntimeError(f'{name} fit failed')
    p = np.asarray(best.x, float)
    return dict(name=name, params={k: float(v) for k, v in zip(pnames, p)},
                loglike=float(-best.fun), _p=p)


def fit_lognormal(x, lo, hi):
    """Lognormal truncated to [lo, hi]; parameters mu, sigma of log x."""
    lx = np.log(_check(x, lo, hi))

    def logpdf(xx, p):
        mu, sig = p[0], abs(p[1]) + _TINY
        lxx = np.log(xx)
        core = -0.5 * ((lxx - mu) / sig) ** 2 - np.log(sig * np.sqrt(2 * np.pi)) - lxx
        za, zb = (np.log(lo) - mu) / sig, (np.log(hi) - mu) / sig
        mass = norm.cdf(zb) - norm.cdf(za)
        if mass <= _TINY:
            return np.full_like(xx, -np.inf)
        return core - np.log(mass)

    starts = [[lx.mean(), lx.std() + 1e-3], [lx.mean(), 2 * lx.std() + 1e-3],
              [np.log(lo), 1.0]]
    r = _trunc_fit(x, lo, hi, logpdf, starts, 'lognormal', ['mu', 'sigma'])
    r['params']['sigma'] = abs(r['params']['sigma']) + _TINY
    return r


def fit_exponential(x, lo, hi):
    """Exponential truncated to [lo, hi]; rate lambda."""
    def logpdf(xx, p):
        lam = p[0]
        if abs(lam) < 1e-300:
            return np.full_like(xx, -np.inf)
        # normaliser: integral of exp(-lam x) over [lo,hi]
        d = (np.exp(-lam * lo) - np.exp(-lam * hi)) / lam if lam != 0 else (hi - lo)
        if not np.isfinite(d) or d <= 0:
            return np.full_like(xx, -np.inf)
        return -lam * xx - np.log(d)

    m = np.mean(np.asarray(x, float))
    starts = [[1.0 / m], [0.5 / m], [2.0 / m]]
    return _trunc_fit(x, lo, hi, logpdf, starts, 'exponential', ['lambda'])


def fit_weibull(x, lo, hi):
    """Truncated Weibull in dimensionless shape/hazard coordinates.

    h = beta*(lo/scale)**beta is the log-coordinate hazard at the lower
    boundary. This parameterization avoids subtracting tiny survival masses
    and avoids a unit-dependent additive floor on scale. Near beta=0 the
    family approaches a power law; report that numerical boundary explicitly.
    """
    x = _check(x, lo, hi)
    # Optimize in x/lo so parameter estimates are invariant to physical units.
    relative = x / lo
    bounds = [(np.log(1e-8), np.log(1e4)), (np.log(1e-6), np.log(100))]

    def nll(p):
        with np.errstate(all='ignore'):
            values = _we_logpdf(relative, dict(hazard_at_lo=np.exp(p[0]),
                                              beta=np.exp(p[1])), 1.0, hi / lo)
        return -float(values.sum()) if np.isfinite(values).all() else 1e100

    fits = [minimize(nll, np.log([h, beta]), method='Nelder-Mead', bounds=bounds,
                     options=dict(maxiter=4000, xatol=1e-9, fatol=1e-9))
            for h, beta in [(1, .05), (1, .5), (1, 1), (.1, 2)]]
    successful = [r for r in fits if r.success and np.isfinite(r.fun) and r.fun < 1e99]
    if not successful:
        raise RuntimeError('Truncated Weibull fit failed')
    best = min(successful, key=lambda r: r.fun)
    h, beta = np.exp(best.x)
    fit = dict(name='stretched_exponential',
               params=dict(hazard_at_lo=float(h), beta=float(beta)),
               parameterization='h=beta*(lo/scale)^beta; dimensionless relative to declared lo',
               power_law_boundary=bool(beta < 1e-5))
    fit['loglike'] = float(_we_logpdf(x, fit['params'], lo, hi).sum())
    return fit


_LOGPDF = {
    'power_law': lambda x, p, lo, hi: _pl_logpdf(x, p['alpha'], lo, hi),
    'lognormal': lambda x, p, lo, hi: _ln_logpdf(x, p, lo, hi),
    'exponential': lambda x, p, lo, hi: _ex_logpdf(x, p, lo, hi),
    'stretched_exponential': lambda x, p, lo, hi: _we_logpdf(x, p, lo, hi),
}


def _ln_logpdf(x, p, lo, hi):
    mu, sig = p['mu'], p['sigma']
    lx = np.log(x)
    core = -0.5 * ((lx - mu) / sig) ** 2 - np.log(sig * np.sqrt(2 * np.pi)) - lx
    mass = norm.cdf((np.log(hi) - mu) / sig) - norm.cdf((np.log(lo) - mu) / sig)
    return core - np.log(mass)


def _ex_logpdf(x, p, lo, hi):
    lam = p['lambda']
    d = (np.exp(-lam * lo) - np.exp(-lam * hi)) / lam
    return -lam * x - np.log(d)


def _we_logpdf(x, p, lo, hi):
    beta = p['beta']
    # The fallback supports historical stored fits, without adding a scale floor.
    h = p['hazard_at_lo'] if 'hazard_at_lo' in p else beta * (lo / p['scale']) ** beta
    z, L = np.log(np.asarray(x, float) / lo), np.log(hi / lo)
    delta = h * np.expm1(beta * z) / beta
    delta_max = h * np.expm1(beta * L) / beta
    return np.log(h) + beta * z - np.log(x) - delta - np.log(-np.expm1(-delta_max))


def logpdf_of(fit, x, lo, hi):
    """Pointwise log density of a fitted model."""
    return _LOGPDF[fit['name']](np.asarray(x, float), fit['params'], lo, hi)


# --------------------------------------------------------------------------
# Goodness of fit
# --------------------------------------------------------------------------

def ks_distance(x, alpha, lo, hi):
    """Kolmogorov-Smirnov distance between the sample and the fitted power law."""
    x = np.sort(np.asarray(x, float))
    n = len(x)
    cdf = _pl_cdf(x, alpha, lo, hi)
    upper = np.arange(1, n + 1) / n
    lower = np.arange(0, n) / n
    return float(max(np.max(upper - cdf), np.max(cdf - lower)))


def _check_n_boot(n_boot):
    if isinstance(n_boot, bool) or not isinstance(n_boot, (int, np.integer)) or n_boot < 1:
        raise ValueError('n_boot must be a positive integer')


def powerlaw_gof(x, lo, hi, n_boot=500, seed=0):
    """Parametric bootstrap p-value for the bounded power law (CSN procedure).

    p is (1 + exceedances)/(1 + n_boot) for synthetic datasets drawn from the
    fitted model and refitted. This finite-simulation correction avoids zero
    p-values; fitting nuisance parameters still makes calibration approximate.
    The bootstrap assumes independent identically distributed observations.
    Following CSN,
    p <= 0.1 rules the power law out; p > 0.1 means it cannot be ruled out,
    which is not the same as support.
    """
    x = _check(x, lo, hi)
    _check_n_boot(n_boot)
    fit = fit_powerlaw(x, lo, hi)
    alpha = fit['params']['alpha']
    ks = ks_distance(x, alpha, lo, hi)
    rng = np.random.default_rng(seed)
    n = len(x)
    worse = 0
    draws = np.empty(n_boot)
    for i in range(n_boot):
        xs = sample_powerlaw(n, alpha, lo, hi, rng)
        a_s = fit_powerlaw(xs, lo, hi)['params']['alpha']
        draws[i] = ks_distance(xs, a_s, lo, hi)
        worse += draws[i] >= ks
    p_value = float((worse + 1) / (n_boot + 1))
    return dict(alpha=alpha, n=n, ks=ks, p_value=p_value,
                exceedances=int(worse),
                n_boot=n_boot, ks_synthetic_median=float(np.median(draws)),
                ruled_out=bool(p_value <= 0.1),
                note='Approximate iid parametric bootstrap, p=(exceedances+1)/(B+1). '
                     'p <= 0.1 rejects the fitted power law under those assumptions; '
                     'p > 0.1 is non-rejection, not support.')


def vuong(x, fit1, fit2, lo, hi):
    """Vuong test for two non-nested models on the same support.

    Positive R favours fit1. The p-value is two-sided; a large p means the
    comparison is inconclusive, which is the common outcome for power law
    against lognormal over a narrow range.
    """
    x = _check(x, lo, hi)
    l1 = logpdf_of(fit1, x, lo, hi)
    l2 = logpdf_of(fit2, x, lo, hi)
    d = l1 - l2
    n = len(x)
    R = float(d.sum())
    sd = float(d.std(ddof=1))
    if sd < _TINY:
        return dict(against=fit2['name'], loglike_ratio=R, statistic=0.0,
                    p_value=1.0, favours='inconclusive')
    stat = R / (np.sqrt(n) * sd)
    p = float(erfc(abs(stat) / np.sqrt(2)))
    fav = 'inconclusive' if p > 0.05 else (fit1['name'] if R > 0 else fit2['name'])
    return dict(against=fit2['name'], loglike_ratio=R, statistic=float(stat),
                p_value=p, favours=fav,
                caveat='Nominal iid non-nested Vuong calibration; not justified for '
                       'dependent observations or overlapping/boundary-limit models.')


def compare_alternatives(x, lo, hi, n_boot=500, seed=0):
    """Full CSN-style report: power-law GOF plus likelihood-ratio comparisons."""
    x = _check(x, lo, hi)
    gof = powerlaw_gof(x, lo, hi, n_boot=n_boot, seed=seed)
    pl = fit_powerlaw(x, lo, hi)
    alts = []
    for f in (fit_lognormal, fit_exponential, fit_weibull):
        try:
            fit = f(x, lo, hi)
        except Exception as e:  # a failed alternative is reported, not hidden
            alts.append(dict(against=f.__name__, error=str(e)))
            continue
        r = vuong(x, pl, fit, lo, hi)
        r['params'] = fit['params']
        r['loglike'] = fit['loglike']
        if 'power_law_boundary' in fit:
            r['power_law_boundary'] = fit['power_law_boundary']
            r['parameterization'] = fit['parameterization']
            if fit['power_law_boundary']:
                r['caveat'] += ' Weibull optimum is at a numerical power-law limit; nominal p-value is not calibrated here.'
                r['favours'] = 'inconclusive (boundary limit)'
        alts.append(r)
    return dict(domain=[lo, hi], power_law=dict(**pl['params'], loglike=pl['loglike']),
                goodness_of_fit=gof, comparisons=alts)


# --------------------------------------------------------------------------
# Equivalence testing for flatness
# --------------------------------------------------------------------------

def flatness_equivalence(centers, phi, tolerance_factor=1.25, slope_draws=None,
                         alpha_level=0.05, domain=None, phi_draws=None):
    """Assess slope equivalence and simultaneous departure over declared bins.

    The slope tolerance is ln(factor)/ln(hi/lo). Pass bin *boundaries* as
    ``domain=(lo, hi)``; otherwise the declared domain is the center span.
    A 1-2*alpha slope interval must lie strictly within that tolerance.

    The observed max(abs(log(phi))) is descriptive. A positive overall verdict
    additionally requires ``phi_draws``: aligned bootstrap or uncertainty-model
    replicates of the ENTIRE normalized spectrum. Their 1-alpha quantile of
    max(abs(log(phi))) supplies an approximate simultaneous upper bound.
    Calibration inherits the supplied resampling/model assumptions; model
    uncertainty draws do not become empirical confidence intervals.

    Empty bins are retained, prevent a finite log-slope fit, and fail the
    observed departure criterion. Failed slope replicates are counted and
    never silently discarded to manufacture a positive equivalence result.
    """
    centers = np.asarray(centers, float)
    phi = np.asarray(phi, float)
    if centers.ndim != 1 or centers.shape != phi.shape or len(phi) < 3:
        raise ValueError('Aligned one-dimensional arrays with at least three bins required')
    if not np.all(np.isfinite(centers)) or np.any(centers <= 0) or np.any(np.diff(centers) <= 0):
        raise ValueError('Centers must be finite, positive and strictly increasing')
    if not np.all(np.isfinite(phi)) or np.any(phi < 0):
        raise ValueError('Phi must be finite and nonnegative; missing bins need an explicit policy')
    if not np.isfinite(tolerance_factor) or tolerance_factor <= 1:
        raise ValueError('Tolerance factor must be finite and exceed 1')
    if not np.isfinite(alpha_level) or not 0 < alpha_level < 0.5:
        raise ValueError('alpha_level must lie strictly between 0 and 0.5')
    lo, hi = (centers[0], centers[-1]) if domain is None else domain
    if not np.isfinite([lo, hi]).all() or not 0 < lo < hi or lo > centers[0] or hi < centers[-1]:
        raise ValueError('A finite positive domain containing all centers is required')

    span = np.log(hi) - np.log(lo)
    s_tol = float(np.log(tolerance_factor) / span)
    empty = int(np.count_nonzero(phi == 0))
    ly = np.log(phi) if not empty else None
    slope = float(np.polyfit(np.log(centers), ly, 1)[0]) if not empty else None
    departure = float(np.max(np.abs(ly))) if not empty else None
    dep_ok = bool(not empty and departure <= np.log(tolerance_factor))
    out = dict(tolerance_factor=float(tolerance_factor), slope_tolerance=s_tol,
               domain=[float(lo), float(hi)],
               span_basis='declared boundaries' if domain is not None else 'center extrema',
               slope=slope, n_bins=len(phi), empty_bins=empty,
               max_abs_log_departure=departure,
               departure_tolerance=float(np.log(tolerance_factor)),
               departure_within_tolerance=dep_ok,
               departure_upper_bound=None, departure_equivalent=None,
               phi_min=float(phi.min()), phi_max=float(phi.max()),
               phi_ratio=float(phi.max() / phi.min()) if not empty else None,
               slope_ci=None, slope_equivalent=None,
               verdict='unavailable: no sampling model for an interval',
               note='Observed departures alone do not establish population equivalence. '
                    'Failure to establish equivalence is not evidence of inequivalence.')

    if phi_draws is not None:
        pd = np.asarray(phi_draws, float)
        if pd.ndim != 2 or pd.shape[1] != len(phi) or len(pd) < 20:
            raise ValueError('At least 20 full-spectrum replicates aligned with the bins required')
        if not np.isfinite(pd).all() or np.any(pd < 0):
            raise ValueError('Spectrum replicates must be finite and nonnegative')
        # Zero resource in any replicate is infinite log departure, not a missing bin.
        with np.errstate(divide='ignore'):
            maxima = np.max(np.abs(np.log(pd)), axis=1)
        # An order-statistic quantile avoids interpolation of infinity.
        upper = float(np.quantile(maxima, 1 - alpha_level, method='higher'))
        out.update(departure_upper_bound=upper if np.isfinite(upper) else None,
                   departure_equivalent=bool(upper < np.log(tolerance_factor)),
                   n_spectrum_draws=len(pd),
                   departure_bound_level=float(1 - alpha_level))

    if empty:
        out.update(verdict='equivalence not established: empty resource bins',
                   failed_criterion='empty bins')
        return out
    if slope_draws is None:
        return out
    d = np.asarray(slope_draws, float)
    if d.ndim != 1:
        raise ValueError('Slope replicates must be one-dimensional')
    out.update(n_slope_draws=len(d), invalid_slope_draws=int(np.count_nonzero(~np.isfinite(d))))
    if len(d) < 20 or not np.isfinite(d).all():
        out['verdict'] = 'unavailable: insufficient or invalid slope replicates'
        return out
    ci = [float(v) for v in np.quantile(d, [alpha_level, 1 - alpha_level])]
    eq = bool(ci[0] > -s_tol and ci[1] < s_tol)
    out.update(slope_ci=ci, slope_equivalent=eq,
               ci_level=f'{100*(1-2*alpha_level):.0f}% (TOST)')
    if not eq or not dep_ok or out['departure_equivalent'] is False:
        failed = ([] if eq else ['slope']) + ([] if dep_ok and out['departure_equivalent'] is not False else ['departure'])
        out.update(verdict='equivalence not established', failed_criterion='+'.join(failed))
    elif phi_draws is None:
        out['verdict'] = 'unavailable: no uncertainty bound for whole-spectrum departure'
    else:
        out.update(verdict='equivalent to flat under supplied uncertainty model', failed_criterion=None)
    return out


# ---------------------------------------------------------------------------
# Discrete goodness of fit for catalogues recorded on a fixed grid
# ---------------------------------------------------------------------------
#
# A continuous KS statistic is invalid on heavily tied data: the ties inflate
# it on their own. Earthquake magnitudes are rounded to 0.1, so the energy
# proxy takes a few dozen distinct values and the continuous test in
# powerlaw_gof cannot be applied to it.
#
# On that grid the Gutenberg-Richter law is exactly a geometric distribution.
# With magnitudes rounded to step D and thresholded at M0, k = (M - M0)/D is a
# non-negative integer and N(>=M) proportional to 10^(-bM) means
#
#     P(K = k) = (1 - q) q^k,   q = 10^(-b D),
#
# so a power law in the magnitude-derived energy proxy is the same hypothesis
# as a geometric law in k. Testing it on k is the correct discrete treatment.


def _to_grid(magnitudes, threshold, step=0.1):
    m = np.asarray(magnitudes, float)
    if m.ndim != 1 or not np.all(np.isfinite(m)):
        raise ValueError('Finite magnitudes required')
    if not np.isfinite([threshold, step]).all() or step <= 0:
        raise ValueError('A finite threshold and positive finite rounding step required')
    if not np.isclose(threshold / step, np.round(threshold / step), rtol=0, atol=1e-8):
        raise ValueError('Threshold must lie on the declared magnitude grid')
    mr = np.round(m / step) * step
    k = np.round((mr[mr >= threshold - 1e-8] - threshold) / step).astype(np.int64)
    if len(k) < 2:
        raise ValueError('At least two events at or above the threshold required')
    return k


def geometric_mle(k):
    """MLE of q for P(K=k) = (1-q) q^k on non-negative integers."""
    k = _check_counts(k)
    kbar = float(k.mean())
    return kbar / (1.0 + kbar)


def _check_counts(k):
    k = np.asarray(k, float)
    if k.ndim != 1 or not len(k) or not np.isfinite(k).all() or np.any(k < 0) or np.any(k != np.floor(k)):
        raise ValueError('A nonempty one-dimensional array of non-negative integer counts required')
    return k.astype(np.int64)


def discrete_ks(k, q):
    """KS distance between the empirical and geometric CDFs on the integer grid.

    Both CDFs are supported on the same lattice and jump at the same points, so
    they are compared only at those points. The left-limit correction used for
    continuous fits would compare across a jump and inflate the statistic by
    roughly the size of the largest probability atom.
    """
    k = _check_counts(k)
    if not np.isfinite(q) or not 0 <= q < 1:
        raise ValueError('Geometric parameter q must satisfy 0 <= q < 1')
    n = len(k)
    kmax = int(k.max())
    obs = np.bincount(k, minlength=kmax + 1)
    emp = np.cumsum(obs) / n
    fit = 1.0 - q ** (np.arange(kmax + 1) + 1)
    return float(np.max(np.abs(emp - fit)))


def discrete_gr_gof(magnitudes, threshold, step=0.1, n_boot=500, seed=0):
    """Discrete Clauset-Shalizi-Newman test of the Gutenberg-Richter law.

    Fits the geometric law on the rounded magnitude grid, measures the discrete
    KS distance, and obtains a p-value by refitting synthetic catalogues drawn
    from the fitted model. Following CSN, p <= 0.1 rules the model out and
    p > 0.1 is non-rejection rather than support.

    Also fits a truncated version with a finite maximum magnitude and reports
    the AIC difference. The truncation point is a boundary parameter, so this
    is a descriptive comparison and not a likelihood-ratio test.
    """
    k = _to_grid(magnitudes, threshold, step)
    _check_n_boot(n_boot)
    q = geometric_mle(k)
    if q == 0:
        raise ValueError('An observed all-threshold catalogue has no finite b estimate')
    ks = discrete_ks(k, q)
    n = len(k)

    rng = np.random.default_rng(seed)
    worse = 0
    for _ in range(n_boot):
        ks_syn = rng.geometric(1 - q, size=n) - 1          # numpy counts trials
        worse += discrete_ks(ks_syn, geometric_mle(ks_syn)) >= ks

    ll = float(n * (np.log1p(-q) + k.mean() * np.log(q)))

    best = None
    for kmax in range(int(k.max()), int(k.max()) + 40):
        def nll(qq):
            qq = min(max(qq, 1e-9), 1 - 1e-9)
            norm = 1.0 - qq ** (kmax + 1)
            return -float(n * (np.log1p(-qq) + k.mean() * np.log(qq) - np.log(norm)))
        r = minimize_scalar(nll, bounds=(1e-6, 1 - 1e-6), method='bounded')
        cand = dict(k_max=kmax, m_max=float(threshold + kmax * step),
                    q=float(r.x), loglike=float(-r.fun), aic=float(2 * 2 + 2 * r.fun))
        if best is None or cand['aic'] < best['aic']:
            best = cand

    p_value = float((worse + 1) / (n_boot + 1))
    return dict(n=int(n), threshold=float(threshold), step=float(step),
                q=float(q), b=float(-np.log10(q) / step), ks=ks,
                p_value=p_value, n_boot=int(n_boot), exceedances=int(worse),
                ruled_out=bool(p_value <= 0.1),
                loglike=ll, aic=float(2 * 1 - 2 * ll),
                truncated=best,
                delta_aic_truncated=float(best['aic'] - (2 * 1 - 2 * ll)),
                note='Geometric on the rounded magnitude grid is exactly the '
                     'Gutenberg-Richter law; a power law in the magnitude-derived '
                     'energy proxy is the same hypothesis. Approximate iid parametric '
                     'bootstrap, p=(exceedances+1)/(B+1); p <= 0.1 rejects under those '
                     'assumptions. Clustering and completeness are not modelled.')
