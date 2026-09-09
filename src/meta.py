"""Random-effects meta-analysis and reporting-artefact diagnostics.

These support the ensemble analysis: deciding whether dispersion across many
published estimates is real between-system heterogeneity or estimation noise,
and whether an apparent concentration at a predicted value is a reporting
artefact rather than a finding.

Nothing here selects a subset or a threshold. Callers declare those.
"""
import numpy as np
from scipy.optimize import minimize
from scipy.integrate import quad_vec
from scipy.special import gammaln, ndtr
from scipy.stats import chi2 as _chi2, norm as _norm, laplace as _laplace, t as _t

__all__ = ['random_effects', 'digit_preference', 'round_number_excess',
           'latent_shape', 'predicted_pass_fraction', 'variance_components']

_TINY = 1e-12


def random_effects(y, se):
    """DerSimonian-Laird random-effects summary of estimates y with errors se.

    Returns Cochran's Q, heterogeneity variance tau^2, the conventional I^2
    relative excess-dispersion statistic, and fixed/random-effects means.
    Errors must be independent and correctly calibrated for the reported
    uncertainty and Q reference distribution. I^2 is not a literal variance
    partition for arbitrary heterogeneous errors, nor a significance test.
    """
    y = np.asarray(y, float)
    se = np.asarray(se, float)
    if y.shape != se.shape or y.ndim != 1:
        raise ValueError('y and se must be aligned one-dimensional arrays')
    ok = np.isfinite(y) & np.isfinite(se) & (se > 0)
    if ok.sum() < 2:
        raise ValueError('At least two estimates with positive finite errors required')
    y, se = y[ok], se[ok]
    k = len(y)

    w = 1.0 / se ** 2
    mu_fe = float((w * y).sum() / w.sum())
    se_fe = float(np.sqrt(1.0 / w.sum()))
    Q = float((w * (y - mu_fe) ** 2).sum())
    df = k - 1
    C = float(w.sum() - (w ** 2).sum() / w.sum())

    tau2 = max(0.0, (Q - df) / C) if C > 0 else 0.0
    i2 = max(0.0, (Q - df) / Q) if Q > 0 else 0.0

    ws = 1.0 / (se ** 2 + tau2)
    mu_re = float((ws * y).sum() / ws.sum())
    se_re = float(np.sqrt(1.0 / ws.sum()))

    return dict(k=int(k), Q=Q, df=int(df),
                Q_p_value=float(_chi2.sf(Q, df)) if df > 0 else float('nan'),
                tau_squared=float(tau2), tau=float(np.sqrt(tau2)),
                I_squared=float(i2),
                fixed_effect_mean=mu_fe, fixed_effect_se=se_fe,
                random_effects_mean=mu_re, random_effects_se=se_re,
                random_effects_ci=[mu_re - 1.96 * se_re, mu_re + 1.96 * se_re],
                observed_sd=float(np.std(y, ddof=1)), median_se=float(np.median(se)))


def digit_preference(values, decimals=2):
    """Chi-square test for uniformity of the final reported decimal digit.

    Rejection is evidence against a uniform-digit reference, conditional on
    independent values. Rounding, source conventions and distribution shape
    can all affect digits; this test cannot establish their cause.
    """
    v = np.asarray(values, float)
    v = v[np.isfinite(v)]
    if len(v) < 10:
        raise ValueError('At least ten values required')
    digits = np.round(np.abs(np.round(v, decimals)) * 10 ** decimals).astype(np.int64) % 10
    counts = np.array([(digits == d).sum() for d in range(10)])
    exp = counts.sum() / 10.0
    stat = float(((counts - exp) ** 2 / exp).sum())
    return dict(counts=counts.tolist(), expected=float(exp), chi2=stat, df=9,
                p_value=float(_chi2.sf(stat, 9)),
                uniform=bool(_chi2.sf(stat, 9) > 0.01))


def round_number_excess(values, target, grid=0.01, step=0.10, window=4,
                        lo=None, hi=None):
    """Excess of reported values at round numbers, relative to local baseline.

    For each multiple of `step` in the range, counts values landing exactly on
    it and divides by the mean count at the `window` neighbouring grid points
    on each side. A concentration at `target` is only evidence of anchoring on
    that value if its excess stands out against the excess at the other round
    numbers, so the target's rank among them is returned.
    """
    v = np.asarray(values, float)
    v = v[np.isfinite(v)]
    if len(v) < 10:
        raise ValueError('At least ten values required')
    r = np.round(v, int(round(-np.log10(grid))))
    lo = float(np.floor(r.min() / step) * step) if lo is None else lo
    hi = float(np.ceil(r.max() / step) * step) if hi is None else hi
    dec = int(round(-np.log10(grid)))

    def count(x):
        return int((np.abs(r - round(x, dec)) < grid / 2).sum())

    out = {}
    n_steps = int(round((hi - lo) / step))
    for i in range(n_steps + 1):
        val = round(lo + i * step, dec)
        nb = [count(val + k * grid) for k in range(-window, window + 1) if k != 0]
        base = float(np.mean(nb))
        out[val] = dict(count=count(val), local_baseline=base,
                        excess_ratio=float(count(val) / base) if base > 0 else None)

    tgt = round(float(target), dec)
    if tgt not in out:
        raise ValueError(f'target {target} is not a multiple of step {step} in range')
    others = [d['excess_ratio'] for k, d in out.items()
              if k != tgt and d['excess_ratio'] is not None]
    at = out[tgt]['excess_ratio']
    return dict(per_value={str(k): d for k, d in out.items()},
                target=tgt, excess_at_target=at,
                median_excess_elsewhere=float(np.median(others)) if others else None,
                n_other_round_values=len(others),
                rank_of_target=int(sum(o >= at for o in others) + 1) if at is not None else None,
                stands_out=bool(at is not None and others and at > np.quantile(others, 0.9)))


# ---------------------------------------------------------------------------
# Latent-distribution shape, and what a fitted ensemble forbids
# ---------------------------------------------------------------------------

def _unit_family(name, nu=None):
    """Standardised latent shape with mean 0 and variance 1."""
    if name == 'gaussian':
        return lambda z: _norm.pdf(z)
    if name == 'laplace':
        b = 1 / np.sqrt(2.0)
        return lambda z: _laplace.pdf(z, scale=b)
    if name == 'student_t':
        if nu is None or nu <= 2:
            raise ValueError('student_t needs nu > 2 for unit variance')
        c = np.sqrt(nu / (nu - 2.0))
        return lambda z: _t.pdf(z * c, df=nu) * c
    raise ValueError(f'unknown family {name}')


def _mixture_integral(fn, shape):
    """Integrate over a mean-one Gamma variable, on a scaled log coordinate.

    Gaussian scale mixtures avoid an under-resolved latent grid when some
    measurement errors are much smaller than the latent dispersion. The log
    coordinate also retains the Student distribution's unbounded tails.
    """
    root = np.sqrt(shape)
    constant = shape * np.log(shape) - shape - gammaln(shape) - np.log(root)

    def integrand(u):
        z = u / root
        if z > 700:
            return fn(0.0) * 0.0
        logweight = shape * (z - np.expm1(z)) + constant
        if logweight < -740:
            return fn(0.0) * 0.0
        return np.exp(logweight) * fn(z)

    value, error, info = quad_vec(integrand, -np.inf, np.inf,
                                  epsabs=1e-10, epsrel=1e-9, full_output=True)
    if not info.success or not np.all(np.isfinite(value)):
        raise ArithmeticError(f'convolution integration failed: {info.message}')
    return value


def _mixture_logvariance(logscale, tau, se, family, nu):
    if family == 'laplace':
        loglatent = 2 * np.log(tau) + logscale
    elif family == 'student_t':
        loglatent = 2 * np.log(tau) + np.log((nu - 2) / nu) - logscale
    else:
        raise ValueError(f'unknown family {family}')
    with np.errstate(divide='ignore'):
        return np.logaddexp(2 * np.log(se), loglatent)


def _loglik(y, se, mu, tau, family, nu=None):
    """Independent-observation convolution log likelihood.

    Laplace is a normal variance mixture with exponential mixing; Student t
    uses inverse-gamma mixing. Adaptive integration covers the full support.
    It does not turn dependent spectra into independent observations.
    """
    y, se = np.asarray(y, float), np.asarray(se, float)
    _unit_family(family, nu)  # validate the family even at the zero-variance boundary
    if tau <= 0 or family == 'gaussian':
        v = max(tau, 0) ** 2 + se ** 2
        return float(np.sum(-0.5 * np.log(2 * np.pi * v) - (y - mu) ** 2 / (2 * v)))
    residual = y - mu
    # Scaling by a nearby density makes quadrature relative accuracy meaningful
    # even for observations deep in the tails.
    scale = np.hypot(tau, se)
    if family == 'student_t':
        ref = _t.logpdf(residual / scale, df=nu) - np.log(scale)
        shape = nu / 2
    else:
        ref = _laplace.logpdf(residual, scale=scale / np.sqrt(2))
        shape = 1.0

    def density(logscale):
        lv = _mixture_logvariance(logscale, tau, se, family, nu)
        logpdf = -0.5 * (np.log(2 * np.pi) + lv + residual ** 2 * np.exp(-lv))
        return np.exp(logpdf - ref)

    relative = _mixture_integral(density, shape)
    if np.any(relative <= 0):
        raise ArithmeticError('convolution density underflow')
    return float(np.sum(np.log(relative) + ref))


def latent_shape(y, se, families=('gaussian', 'laplace', 'student_t'), nu_grid=(3, 4, 5, 8, 15)):
    """Which latent shape best explains estimates y with known errors se?

    Gaussianity is an additional modeling choice, not a consequence of a
    hypothesis about the ensemble mean. AIC compares the supplied candidates;
    its winner is not an absolute goodness-of-fit or adequacy test.

    The comparison is against the *convolution* of each latent shape with the
    reported measurement errors, not against the raw histogram, since the
    observed spread already contains those errors.
    """
    y = np.asarray(y, float)
    se = np.asarray(se, float)
    if y.shape != se.shape or y.ndim != 1:
        raise ValueError('y and se must be aligned one-dimensional arrays')
    if 'gaussian' not in families:
        raise ValueError('families must include the Gaussian reference')
    ok = np.isfinite(y) & np.isfinite(se) & (se > 0)
    y, se = y[ok], se[ok]
    if len(y) < 20:
        raise ValueError('At least twenty estimates required')

    out = {}
    for fam in families:
        best = None
        nus = nu_grid if fam == 'student_t' else (None,)
        for nu in nus:
            def nll(p):
                return -_loglik(y, se, p[0], abs(p[1]), fam, nu)
            r = minimize(nll, [float(np.median(y)), float(np.std(y, ddof=1))],
                         method='Nelder-Mead',
                         options=dict(maxiter=2000, xatol=1e-8, fatol=1e-8))
            if not r.success or not np.isfinite(r.fun):
                raise RuntimeError(f'{fam} optimization failed: {r.message}')
            k = 2 + (1 if fam == 'student_t' else 0)
            rec = dict(mu=float(r.x[0]), tau=float(abs(r.x[1])), nu=nu,
                       loglike=float(-r.fun), k_params=k,
                       aic=float(2 * k + 2 * r.fun))
            if best is None or rec['aic'] < best['aic']:
                best = rec
        out[fam] = best

    ranked = sorted(out.items(), key=lambda kv: kv[1]['aic'])
    g = out['gaussian']
    z = (y - g['mu']) / np.sqrt(g['tau'] ** 2 + se ** 2)
    return dict(n=int(len(y)), families=out,
                best_family=ranked[0][0],
                delta_aic_vs_gaussian={k: float(v['aic'] - g['aic']) for k, v in out.items()},
                gaussian_standardised_residuals=dict(
                    mean=float(z.mean()), sd=float(z.std(ddof=1)),
                    skew=float(((z - z.mean()) ** 3).mean() / z.std() ** 3),
                    excess_kurtosis=float(((z - z.mean()) ** 4).mean() / z.std() ** 4 - 3.0)),
                gaussian_best_by_aic=bool(ranked[0][0] == 'gaussian'),
                inference_note='Working independence likelihood; AIC ranks candidates and '
                               'does not establish model adequacy. Student degrees of '
                               'freedom are selected on a grid; its AIC penalty is approximate.')


def predicted_pass_fraction(tolerances, tau, family='gaussian', nu=None,
                            se=None, mu=0.0):
    """Expected fraction inside symmetric tolerances under a specified model.

    `mu` is the latent mean departure from the target. With supplied standard
    errors this predicts *observed* passes after measurement error; without
    them it predicts latent passes. Compare observations and tolerances from
    exactly the same sample. Fitting these parameters to that sample yields a
    descriptive consistency check, not an independent prediction.
    """
    tol = np.asarray(tolerances, float)
    if tol.ndim != 1 or not len(tol) or np.any(~np.isfinite(tol) | (tol <= 0)):
        raise ValueError('Positive finite one-dimensional tolerances required')
    if not np.isfinite(tau) or tau <= 0 or not np.isfinite(mu):
        raise ValueError('Positive finite tau and finite mu required')
    _unit_family(family, nu)
    errors = np.zeros_like(tol) if se is None else np.asarray(se, float)
    if errors.shape != tol.shape or np.any(~np.isfinite(errors) | (errors < 0)):
        raise ValueError('se must be aligned finite nonnegative errors')

    def normal_pass(sd):
        return ndtr((tol - mu) / sd) - ndtr((-tol - mu) / sd)

    if family == 'gaussian':
        frac = normal_pass(np.hypot(tau, errors))
    else:
        def conditional(logscale):
            lv = _mixture_logvariance(logscale, tau, errors, family, nu)
            return normal_pass(np.exp(lv / 2))
        frac = _mixture_integral(conditional, 1.0 if family == 'laplace' else nu / 2)
    return dict(mean_predicted_fraction=float(np.mean(frac)),
                median_tolerance=float(np.median(tol)), tau=float(tau), mu=float(mu),
                measurement_error_included=se is not None,
                family=family, n=int(len(tol)))


def variance_components(y, se, group):
    """Split dispersion into between-group and within-group, given known errors.

    Fits y_ij = mu + a_i + e_ij + eps_ij by maximum likelihood, where a_i is a
    group effect with variance tau_between^2, e_ij a within-group effect with
    variance tau_within^2, and eps_ij measurement error with the supplied,
    known standard error.

    The two components are only separable when some groups are observed more
    than once. With every group observed once they are confounded and only
    their sum is identified; the result then reports `separable: False` and the
    sum, rather than an arbitrary split.

    Each group's covariance is D + tau_b^2 * 11', with D diagonal, so the
    determinant and inverse are taken by rank-one update rather than by
    forming the matrix.
    """
    y = np.asarray(y, float)
    se = np.asarray(se, float)
    group = np.asarray(group)
    if y.ndim != 1 or y.shape != se.shape or y.shape != group.shape:
        raise ValueError('y, se and group must be aligned one-dimensional arrays')
    ok = np.isfinite(y) & np.isfinite(se) & (se >= 0)
    y, se, group = y[ok], se[ok], group[ok]
    if len(y) < 5:
        raise ValueError('At least five observations required')

    groups = [np.flatnonzero(group == g) for g in np.unique(group)]
    sizes = np.array([len(ix) for ix in groups])
    separable = bool((sizes > 1).sum() >= 2)

    def nll(p):
        mu, tb2, tw2 = p[0], p[1] ** 2, p[2] ** 2
        total = 0.0
        for ix in groups:
            d = tw2 + se[ix] ** 2 + _TINY
            r = y[ix] - mu
            inv_d = 1.0 / d
            s = float(inv_d.sum())
            quad = float((r ** 2 * inv_d).sum())
            cross = float((r * inv_d).sum())
            denom = 1.0 + tb2 * s
            quad -= tb2 * cross ** 2 / denom
            logdet = float(np.log(d).sum()) + np.log(denom)
            total += 0.5 * (logdet + quad + len(ix) * np.log(2 * np.pi))
        return total

    best = None
    s0 = float(np.std(y, ddof=1))
    for start in ([np.median(y), s0 / 2, s0 / 2], [np.median(y), s0, 1e-3],
                  [np.median(y), 1e-3, s0]):
        r = minimize(nll, start, method='Nelder-Mead',
                     options=dict(maxiter=4000, xatol=1e-9, fatol=1e-9))
        if best is None or r.fun < best.fun:
            best = r
    if not best.success or not np.isfinite(best.fun):
        raise RuntimeError(f'variance-component optimization failed: {best.message}')
    tb, tw = abs(float(best.x[1])), abs(float(best.x[2]))
    out = dict(n=int(len(y)), n_groups=int(len(groups)),
               groups_with_repeats=int((sizes > 1).sum()),
               max_group_size=int(sizes.max()), mu=float(best.x[0]),
               loglike=float(-best.fun), separable=separable,
               total_latent_sd=float(np.hypot(tb, tw)),
               median_se=float(np.median(se)))
    if separable:
        out.update(tau_between=tb, tau_within=tw,
                   fraction_between=float(tb ** 2 / (tb ** 2 + tw ** 2))
                   if (tb ** 2 + tw ** 2) > 0 else float('nan'))
    else:
        out.update(tau_between=None, tau_within=None, fraction_between=None,
                   note='fewer than two groups have repeats; the design is insufficient '
                        'for a reported between/within split')
    return out
