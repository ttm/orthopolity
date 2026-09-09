"""Random-effects meta-analysis and reporting-artefact diagnostics.

These support the ensemble analysis: deciding whether dispersion across many
published estimates is real between-system heterogeneity or estimation noise,
and whether an apparent concentration at a predicted value is a reporting
artefact rather than a finding.

Nothing here selects a subset or a threshold. Callers declare those.
"""
import numpy as np
from scipy.optimize import minimize
from scipy.stats import chi2 as _chi2, norm as _norm, laplace as _laplace, t as _t

__all__ = ['random_effects', 'digit_preference', 'round_number_excess',
           'latent_shape', 'predicted_pass_fraction']


def random_effects(y, se):
    """DerSimonian-Laird random-effects summary of estimates y with errors se.

    Returns Cochran's Q, the heterogeneity variance tau^2, I^2 (the share of
    total variance not attributable to sampling error), and both the
    fixed-effect and random-effects pooled means.

    I^2 is a proportion of variance, not a significance test: a large I^2 with
    few studies is weak evidence. The Q p-value is reported alongside it.
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

    A non-uniform final digit indicates rounding in the source literature. It
    says nothing on its own about any particular value; use round_number_excess
    for that.
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
                        excess_ratio=float(count(val) / base) if base > 0 else float('nan'))

    tgt = round(float(target), dec)
    if tgt not in out:
        raise ValueError(f'target {target} is not a multiple of step {step} in range')
    others = [d['excess_ratio'] for k, d in out.items()
              if k != tgt and np.isfinite(d['excess_ratio'])]
    at = out[tgt]['excess_ratio']
    return dict(per_value={str(k): d for k, d in out.items()},
                target=tgt, excess_at_target=at,
                median_excess_elsewhere=float(np.median(others)) if others else float('nan'),
                n_other_round_values=len(others),
                rank_of_target=int(sum(o >= at for o in others) + 1),
                stands_out=bool(others and at > np.quantile(others, 0.9)))


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


def _loglik(y, se, mu, tau, family, nu=None, n_nodes=241, width=12.0):
    """Log-likelihood of y = latent + N(0, se^2), by quadrature over the latent.

    The Gaussian case is closed form; the others are integrated on a fixed grid
    wide enough to cover the heavy tails at the scales used here.
    """
    if tau <= 0:
        tau = 1e-9
    if family == 'gaussian':
        v = tau ** 2 + se ** 2
        return float(np.sum(-0.5 * np.log(2 * np.pi * v) - (y - mu) ** 2 / (2 * v)))
    f = _unit_family(family, nu)
    z = np.linspace(-width, width, n_nodes)
    dz = z[1] - z[0]
    prior = f(z)
    prior = prior / (prior.sum() * dz)
    s = mu + tau * z
    d = (y[:, None] - s[None, :]) / se[:, None]
    # latent = mu + tau*Z, so f(s) ds = f_unit(z) dz: no extra Jacobian factor.
    lik = (np.exp(-0.5 * d ** 2) / (se[:, None] * np.sqrt(2 * np.pi))) @ (prior * dz)
    return float(np.sum(np.log(np.maximum(lik, 1e-300))))


def latent_shape(y, se, families=('gaussian', 'laplace', 'student_t'), nu_grid=(3, 4, 5, 8, 15)):
    """Which latent shape best explains estimates y with known errors se?

    Under a hypothesis constraining only the mean and variance of the latent
    quantity, maximum entropy makes the latent Gaussian. Heavier-observed tails
    than that imply structure beyond two moments.

    The comparison is against the *convolution* of each latent shape with the
    reported measurement errors, not against the raw histogram, since the
    observed spread already contains those errors.
    """
    y = np.asarray(y, float)
    se = np.asarray(se, float)
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
                maxent_consistent=bool(ranked[0][0] == 'gaussian'))


def predicted_pass_fraction(tolerances, tau, family='gaussian', nu=None):
    """Fraction of systems an ensemble hypothesis predicts will pass individually.

    Given latent departures with mean zero and dispersion tau, and a per-system
    tolerance, this is the share expected to fall inside their own tolerance.
    A hypothesis about the ensemble mean therefore *predicts* the individual
    failure rate, and can be refuted by it.
    """
    tol = np.asarray(tolerances, float)
    tol = tol[np.isfinite(tol) & (tol > 0)]
    if len(tol) == 0 or tau <= 0:
        raise ValueError('Positive tolerances and tau required')
    if family == 'gaussian':
        frac = 2 * _norm.cdf(tol / tau) - 1
    elif family == 'laplace':
        frac = 1 - np.exp(-np.sqrt(2.0) * tol / tau)
    elif family == 'student_t':
        if nu is None or nu <= 2:
            raise ValueError('student_t needs nu > 2')
        c = np.sqrt(nu / (nu - 2.0))
        frac = 2 * _t.cdf(tol / tau * c, df=nu) - 1
    else:
        raise ValueError(f'unknown family {family}')
    return dict(mean_predicted_fraction=float(np.mean(frac)),
                median_tolerance=float(np.median(tol)), tau=float(tau),
                family=family, n=int(len(tol)))
