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
from scipy.special import erfc, expm1, log_ndtr
from scipy.stats import norm

__all__ = ['fit_powerlaw', 'fit_lognormal', 'fit_exponential', 'fit_weibull',
           'ks_distance', 'powerlaw_gof', 'vuong', 'compare_alternatives',
           'flatness_equivalence', 'sample_powerlaw',
           'geometric_mle', 'discrete_ks', 'discrete_gr_gof']

_TINY = 1e-12


def _check(x, lo, hi):
    x = np.asarray(x, float)
    if lo <= 0 or hi <= lo:
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
                loglike=float(-len(x) * fit.fun))


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
    r['params']['sigma'] = abs(r['params']['sigma'])
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
    """Stretched exponential (Weibull) truncated to [lo, hi]; scale, shape."""
    def logpdf(xx, p):
        scale, beta = abs(p[0]) + _TINY, abs(p[1]) + _TINY
        core = (np.log(beta) - np.log(scale) + (beta - 1) * (np.log(xx) - np.log(scale))
                - (xx / scale) ** beta)
        mass = np.exp(-(lo / scale) ** beta) - np.exp(-(hi / scale) ** beta)
        if mass <= _TINY:
            return np.full_like(xx, -np.inf)
        return core - np.log(mass)

    m = np.mean(np.asarray(x, float))
    starts = [[m, 1.0], [m, 0.5], [lo, 0.3]]
    r = _trunc_fit(x, lo, hi, logpdf, starts, 'stretched_exponential', ['scale', 'beta'])
    r['params'] = {k: abs(v) for k, v in r['params'].items()}
    return r


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
    scale, beta = p['scale'], p['beta']
    core = (np.log(beta) - np.log(scale) + (beta - 1) * (np.log(x) - np.log(scale))
            - (x / scale) ** beta)
    mass = np.exp(-(lo / scale) ** beta) - np.exp(-(hi / scale) ** beta)
    return core - np.log(mass)


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


def powerlaw_gof(x, lo, hi, n_boot=500, seed=0):
    """Parametric bootstrap p-value for the bounded power law (CSN procedure).

    p is the fraction of synthetic datasets, drawn from the fitted model and
    refitted, whose KS distance is at least the observed one. Following CSN,
    p <= 0.1 rules the power law out; p > 0.1 means it cannot be ruled out,
    which is not the same as support.
    """
    x = _check(x, lo, hi)
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
    return dict(alpha=alpha, n=n, ks=ks, p_value=float(worse / n_boot),
                n_boot=n_boot, ks_synthetic_median=float(np.median(draws)),
                ruled_out=bool(worse / n_boot <= 0.1),
                note='p <= 0.1 rules the power law out; p > 0.1 is non-rejection, not support')


def vuong(x, fit1, fit2, lo, hi):
    """Vuong test for two non-nested models on the same support.

    Positive R favours fit1. The p-value is two-sided; a large p means the
    comparison is inconclusive, which is the common outcome for power law
    against lognormal over a narrow range.
    """
    x = np.asarray(x, float)
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
    fav = 'inconclusive' if p > 0.05 else ('power_law' if R > 0 else fit2['name'])
    return dict(against=fit2['name'], loglike_ratio=R, statistic=float(stat),
                p_value=p, favours=fav)


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
        alts.append(r)
    return dict(domain=[lo, hi], power_law=dict(**pl['params'], loglike=pl['loglike']),
                goodness_of_fit=gof, comparisons=alts)


# --------------------------------------------------------------------------
# Equivalence testing for flatness
# --------------------------------------------------------------------------

def flatness_equivalence(centers, phi, tolerance_factor=1.25, slope_draws=None,
                         alpha_level=0.05):
    """Test a resource spectrum for flatness against a declared tolerance.

    Two criteria, both required:

    - Slope equivalence (TOST). The declared tolerance is a maximum systematic
      drift by `tolerance_factor` across the whole domain, which corresponds to
      |s| <= ln(factor)/ln(hi/lo) for a residual spectrum Phi proportional to
      k**s. Equivalence is concluded when a (1 - 2*alpha_level) interval for
      the slope lies entirely inside the tolerance band.
    - Bounded departure. max |ln Phi| <= ln(factor). A spectrum can undulate
      with zero fitted slope, so the slope criterion alone is not sufficient.

    `slope_draws` are bootstrap replicates of the slope. Without them no
    interval is available and the slope verdict is reported as unavailable.
    """
    centers = np.asarray(centers, float)
    phi = np.asarray(phi, float)
    if centers.shape != phi.shape or len(phi) < 3:
        raise ValueError('Aligned arrays with at least three bins required')
    if tolerance_factor <= 1:
        raise ValueError('Tolerance factor must exceed 1')
    good = np.isfinite(phi) & (phi > 0)
    if good.sum() < 3:
        raise ValueError('At least three positive finite bins required')

    span = np.log(centers[good].max() / centers[good].min())
    s_tol = float(np.log(tolerance_factor) / span)
    lx, ly = np.log(centers[good]), np.log(phi[good])
    slope = float(np.polyfit(lx, ly, 1)[0])

    departure = float(np.max(np.abs(ly)))
    dep_ok = bool(departure <= np.log(tolerance_factor))

    out = dict(tolerance_factor=tolerance_factor, slope_tolerance=s_tol,
               slope=slope, n_bins=int(good.sum()), empty_bins=int((~good).sum()),
               max_abs_log_departure=departure,
               departure_tolerance=float(np.log(tolerance_factor)),
               departure_within_tolerance=dep_ok,
               phi_min=float(phi[good].min()), phi_max=float(phi[good].max()),
               phi_ratio=float(phi[good].max() / phi[good].min()))

    if slope_draws is None:
        out.update(slope_ci=None, slope_equivalent=None,
                   verdict='unavailable: no sampling model for an interval')
        return out

    d = np.asarray(slope_draws, float)
    d = d[np.isfinite(d)]
    if len(d) < 20:
        out.update(slope_ci=None, slope_equivalent=None,
                   verdict='unavailable: too few valid bootstrap replicates')
        return out
    ci = [float(v) for v in np.quantile(d, [alpha_level, 1 - alpha_level])]
    eq = bool(ci[0] > -s_tol and ci[1] < s_tol)
    out.update(slope_ci=ci, slope_equivalent=eq, n_slope_draws=int(len(d)),
               ci_level=f'{100*(1-2*alpha_level):.0f}% (TOST)',
               verdict=('equivalent to flat' if (eq and dep_ok) else
                        'not equivalent to flat'),
               failed_criterion=(None if (eq and dep_ok) else
                                 ('slope' if not eq else '') +
                                 ('+' if (not eq and not dep_ok) else '') +
                                 ('departure' if not dep_ok else '')))
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
    if not np.all(np.isfinite(m)):
        raise ValueError('Finite magnitudes required')
    mr = np.round(m / step) * step
    k = np.round((mr[mr >= threshold - 1e-8] - threshold) / step).astype(np.int64)
    if len(k) < 2:
        raise ValueError('At least two events at or above the threshold required')
    return k


def geometric_mle(k):
    """MLE of q for P(K=k) = (1-q) q^k on non-negative integers."""
    k = np.asarray(k, np.int64)
    if k.min() < 0:
        raise ValueError('Counts must be non-negative integers')
    kbar = float(k.mean())
    if kbar <= 0:
        raise ValueError('Insufficient variation above the threshold')
    return kbar / (1.0 + kbar)


def discrete_ks(k, q):
    """KS distance between the empirical and geometric CDFs on the integer grid.

    Both CDFs are supported on the same lattice and jump at the same points, so
    they are compared only at those points. The left-limit correction used for
    continuous fits would compare across a jump and inflate the statistic by
    roughly the size of the largest probability atom.
    """
    k = np.asarray(k, np.int64)
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
    q = geometric_mle(k)
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

    return dict(n=int(n), threshold=float(threshold), step=float(step),
                q=float(q), b=float(-np.log10(q) / step), ks=ks,
                p_value=float(worse / n_boot), n_boot=int(n_boot),
                ruled_out=bool(worse / n_boot <= 0.1),
                loglike=ll, aic=float(2 * 1 - 2 * ll),
                truncated=best,
                delta_aic_truncated=float(best['aic'] - (2 * 1 - 2 * ll)),
                note='Geometric on the rounded magnitude grid is exactly the '
                     'Gutenberg-Richter law; a power law in the magnitude-derived '
                     'energy proxy is the same hypothesis. p <= 0.1 rules it out.')
