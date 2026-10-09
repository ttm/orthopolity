"""Fixed-support exponent inference, including whole-catchment resampling."""
import numpy as np
from scipy.optimize import minimize_scalar
from scipy.special import exprel


def fit_mean_log(mean_log, lo=1., hi=20.):
    """Bounded-power-law MLE from sufficient statistic mean(log(R/lo))."""
    length = np.log(hi/lo)
    if not 0 <= mean_log <= length:
        raise ValueError('Mean log radius outside declared support')
    fit = minimize_scalar(lambda z: z*mean_log + np.log(length*exprel(-z*length)),
                          bounds=(-5, 10), method='bounded')
    if not fit.success:
        raise RuntimeError('Exponent optimisation failed')
    return float(fit.x)


def intervals(radii, groups, seed, draws=1000, lo=1., hi=20.):
    """Iid and whole-group percentile intervals with independent streams."""
    r, labels = np.asarray(radii, float), np.asarray(groups)
    if (r.ndim != 1 or labels.shape != r.shape or not np.isfinite(r).all()
            or np.any((r < lo) | (r > hi))):
        raise ValueError('Aligned finite radii within fixed support required')
    if len(r) < 2:
        raise ValueError('At least two observations required')
    z = np.log(r/lo)
    _, inverse, counts = np.unique(labels, return_inverse=True, return_counts=True)
    sums = np.bincount(inverse, weights=z)
    n, k = len(r), len(counts)
    iid_rng, block_rng = [np.random.default_rng(s) for s in np.random.SeedSequence(seed).spawn(2)]
    iid = [fit_mean_log(iid_rng.choice(z, n).mean(), lo, hi) for _ in range(draws)]
    block = []
    if k >= 2:
        for _ in range(draws):
            selected = block_rng.integers(k, size=k)
            block.append(fit_mean_log(sums[selected].sum()/counts[selected].sum(), lo, hi))
    return dict(n=n, zeta_R=fit_mean_log(z.mean(), lo, hi),
                iid_ci95=np.percentile(iid, [2.5, 97.5]).tolist(),
                block_ci95=np.percentile(block, [2.5, 97.5]).tolist() if block else None,
                n_blocks=k, largest_block_share=float(counts.max()/n))


def decision(result, band=(1.9, 2.1), minimum_lakes=100, minimum_blocks=10):
    if (result['n'] < minimum_lakes or result['n_blocks'] < minimum_blocks
            or result['block_ci95'] is None):
        return 'insufficient'
    cis = np.asarray([result['iid_ci95'], result['block_ci95']], float)
    if cis.shape != (2, 2) or not np.isfinite(cis).all() or np.any(cis[:, 0] > cis[:, 1]):
        raise ValueError('Ordered finite intervals required')
    if np.all(cis[:, 0] >= band[0]) and np.all(cis[:, 1] <= band[1]):
        return 'conditional exponent equivalence'
    if np.all(cis[:, 1] < band[0]) or np.all(cis[:, 0] > band[1]):
        return 'robust exponent departure under declared resampling'
    return 'inconclusive'
