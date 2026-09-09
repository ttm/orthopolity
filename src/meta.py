"""Random-effects meta-analysis and reporting-artefact diagnostics.

These support the ensemble analysis: deciding whether dispersion across many
published estimates is real between-system heterogeneity or estimation noise,
and whether an apparent concentration at a predicted value is a reporting
artefact rather than a finding.

Nothing here selects a subset or a threshold. Callers declare those.
"""
import numpy as np
from scipy.stats import chi2 as _chi2

__all__ = ['random_effects', 'digit_preference', 'round_number_excess']


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
