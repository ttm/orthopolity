"""Pre-registered test: aftershock productivity against rupture area or seismic moment.

Implements configs/prereg_2026-10-08_aftershock_productivity.json without
changes. Under the rupture-area reading of earthquake size statistics the
expected number of aftershocks scales as 10^(alpha M) with alpha = 1.0; under
the seismic-moment reading alpha = 1.5. Mainshocks are selected by Gardner and
Knopoff (1974) windows from the frozen catalogue; alpha is the Poisson maximum
likelihood slope with a mainshock bootstrap interval.

Outputs results/aftershock_productivity.json and .png.
"""
from pathlib import Path
import json
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import gammaln

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from orthopolity import rounded_gr_b                   # noqa: E402

RAW, OUT = ROOT / 'data' / 'raw', ROOT / 'results'
PREREG = json.loads((ROOT / 'configs' / 'prereg_2026-10-08_aftershock_productivity.json').read_text())
SEED, N_BOOT = 20261008, 2000
END = pd.Timestamp('2025-01-01', tz='UTC')
M_MAIN, M_AFTER, M_REF = 6.5, 5.5, 6.5
HYP = {name: h['alpha'] for name, h in PREREG['hypotheses'].items()}


def gk_distance(m):
    return 10 ** (0.1238 * m + 0.983)


def gk_time(m):
    return np.where(m >= 6.5, 10 ** (0.032 * m + 2.7389), 10 ** (0.5409 * m - 0.547))


def rupture_distance(m):
    return np.maximum(gk_distance(m), 10 ** (-2.44 + 0.59 * m))


def load(all_types=False):
    a = pd.read_csv(RAW / 'usgs_2010_2024.csv')
    a['date'] = pd.to_datetime(a.time, utc=True)
    a = a[a.date < END]
    if not all_types:
        a = a[a.magType.str.startswith('mw', na=False)]
    a = a.assign(mag=np.round(a.mag.astype(float) * 10) / 10,
                 t=(a.date - END).dt.total_seconds() / 86400.0)
    return a.reset_index(drop=True)


def haversine(lat0, lon0, lat, lon):
    p0, p, dl = np.radians(lat0), np.radians(lat), np.radians(lon - lon0)
    h = np.sin((p - p0) / 2) ** 2 + np.cos(p0) * np.cos(p) * np.sin(dl / 2) ** 2
    return 2 * 6371.0 * np.arcsin(np.sqrt(np.minimum(h, 1)))


def decluster(a, dist_fn, time_fn):
    """Assign every event to the cluster of the largest event whose window contains it."""
    mag, t = a.mag.to_numpy(), a.t.to_numpy()
    lat, lon = a.latitude.to_numpy(), a.longitude.to_numpy()
    order = np.lexsort((t, -mag))
    owner = np.full(len(a), -1)
    for i in order:
        if owner[i] != -1:
            continue
        owner[i] = i
        free = owner == -1
        near = (free & (mag <= mag[i]) & (np.abs(t - t[i]) <= time_fn(mag[i]))
                & (haversine(lat[i], lon[i], lat, lon) <= dist_fn(mag[i])))
        owner[near] = i
    return owner


def counts(a, owner, time_fn, delay_days=0.0, max_depth=None):
    mag, t, depth = a.mag.to_numpy(), a.t.to_numpy(), a.depth.to_numpy()
    rows = []
    for i in np.where((owner == np.arange(len(a))) & (mag >= M_MAIN))[0]:
        if t[i] + time_fn(mag[i]) >= 0:          # window must end before 2025-01-01
            continue
        if max_depth is not None and depth[i] > max_depth:
            continue
        after = (owner == i) & (t > t[i] + delay_days) & (mag >= M_AFTER)
        rows.append((mag[i], int(after.sum())))
    return np.array(rows, float)


def poisson_fit(m, n):
    x = np.log(10) * (m - M_REF)

    def nll(p):
        mu = np.exp(p[0] + p[1] * x)
        return np.sum(mu - n * (p[0] + p[1] * x))
    r = minimize(nll, [np.log(max(n.mean(), 0.1)), 1.0], method='BFGS')
    return float(r.x[1]), float(r.x[0])


def negbin_alpha(m, n):
    x = np.log(10) * (m - M_REF)

    def nll(p):
        mu, k = np.exp(p[0] + p[1] * x), np.exp(p[2])
        return -np.sum(gammaln(n + k) - gammaln(k) - gammaln(n + 1)
                       + k * np.log(k / (k + mu)) + n * np.log(mu / (k + mu)))
    r = minimize(nll, [np.log(max(n.mean(), 0.1)), 1.0, 0.0], method='Nelder-Mead',
                 options=dict(maxiter=20000, xatol=1e-8, fatol=1e-10))
    return float(r.x[1]), float(np.exp(r.x[2]))


def analyse(data, rng):
    m, n = data[:, 0], data[:, 1]
    alpha, logk = poisson_fit(m, n)
    boot = np.empty(N_BOOT)
    for b in range(N_BOOT):
        idx = rng.integers(len(m), size=len(m))
        boot[b] = poisson_fit(m[idx], n[idx])[0]
    lo, hi = np.percentile(boot, [2.5, 97.5])
    nb_alpha, nb_k = negbin_alpha(m, n)
    inside = {name: bool(lo <= v <= hi) for name, v in HYP.items()}
    if inside['H_area'] and not inside['H_moment']:
        verdict = 'supports H_area'
    elif inside['H_moment'] and not inside['H_area']:
        verdict = 'supports H_moment'
    elif inside['H_width'] and not inside['H_area']:
        verdict = 'consistent with H_width'
    else:
        verdict = 'inconclusive'
    return dict(n_mainshocks=len(m), n_aftershocks=int(n.sum()), mainshocks_with_aftershocks=int((n > 0).sum()),
                magnitude_range=[float(m.min()), float(m.max())], alpha=alpha, alpha_ci95=[float(lo), float(hi)],
                log_K=logk, negative_binomial_alpha=nb_alpha, negative_binomial_shape=nb_k,
                hypotheses_in_interval=inside, verdict=verdict)


def plot(data, fit):
    m, n = data[:, 0], data[:, 1]
    edges = np.arange(6.5, 9.25, 0.25)
    centers, means, los, his = [], [], [], []
    rng = np.random.default_rng(SEED)
    for a0, a1 in zip(edges[:-1], edges[1:]):
        sel = n[(m >= a0) & (m < a1)]
        if len(sel) < 3:
            continue
        bm = [rng.choice(sel, len(sel)).mean() for _ in range(1000)]
        centers.append(sel.size and m[(m >= a0) & (m < a1)].mean())
        means.append(sel.mean())
        los.append(np.percentile(bm, 2.5))
        his.append(np.percentile(bm, 97.5))
    centers, means, los, his = map(np.array, (centers, means, los, his))
    ink, muted, grid = '#0b0b0b', '#52514e', '#e6e5e0'
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9})
    fig, ax = plt.subplots(figsize=(7.2, 4.6), layout='constrained')
    pos = means > 0
    ax.errorbar(centers[pos], means[pos], yerr=[means[pos] - np.maximum(los[pos], 1e-3), his[pos] - means[pos]],
                fmt='o', color=ink, ms=6, elinewidth=1.5, capsize=0, label='Mean aftershocks per mainshock, 95% interval')
    x = np.linspace(6.5, 9.1, 50)
    anchor_m = np.average(m, weights=np.maximum(n, 0) + 1e-9)
    anchor = np.exp(fit['log_K'] + fit['alpha'] * np.log(10) * (anchor_m - M_REF))
    for slope, color, label in [(1.0, '#2a78d6', 'Rupture area, α = 1'), (1.5, '#eb6834', 'Seismic moment, α = 1.5')]:
        ax.plot(x, anchor * 10 ** (slope * (x - anchor_m)), color=color, lw=2, label=label)
    ax.plot(x, np.exp(fit['log_K'] + fit['alpha'] * np.log(10) * (x - M_REF)), color=muted, lw=1.5, ls='--',
            label=f"Fit, α = {fit['alpha']:.2f} [{fit['alpha_ci95'][0]:.2f}, {fit['alpha_ci95'][1]:.2f}]")
    ax.set(yscale='log', xlabel='Mainshock moment magnitude',
           ylabel=f'Aftershocks with M ≥ {M_AFTER}', title='Aftershock productivity, USGS 2010–2024 (pre-registered)')
    ax.grid(color=grid, lw=0.8)
    ax.set_axisbelow(True)
    ax.spines[['top', 'right']].set_visible(False)
    ax.legend(frameon=False, fontsize=8, loc='upper left')
    fig.savefig(OUT / 'aftershock_productivity.png', dpi=180)
    plt.close(fig)


def main():
    rng = np.random.default_rng(SEED)
    a = load()
    owner = decluster(a, gk_distance, gk_time)
    primary = counts(a, owner, gk_time)
    result = dict(preregistration='configs/prereg_2026-10-08_aftershock_productivity.json',
                  catalogue_events=len(a), b_value=rounded_gr_b(a.mag, M_AFTER)[0],
                  primary=analyse(primary, rng))
    fixed365 = lambda m: np.full(np.shape(m), 365.0)                      # noqa: E731
    owner_r = decluster(a, rupture_distance, fixed365)
    owner_all = None
    sens = {
        'rupture_length_windows': analyse(counts(a, owner_r, fixed365), rng),
        'exclude_first_day': analyse(counts(a, owner, gk_time, delay_days=1.0), rng),
        'shallow_mainshocks': analyse(counts(a, owner, gk_time, max_depth=70.0), rng),
    }
    b_all = load(all_types=True)
    owner_all = decluster(b_all, gk_distance, gk_time)
    sens['all_magnitude_types'] = analyse(counts(b_all, owner_all, gk_time), rng)
    result['sensitivity'] = sens
    OUT.mkdir(exist_ok=True)
    (OUT / 'aftershock_productivity.json').write_text(json.dumps(result, indent=2))
    plot(primary, result['primary'])
    p = result['primary']
    print(f"b = {result['b_value']:.3f}; mainshocks {p['n_mainshocks']}, aftershocks {p['n_aftershocks']}")
    print(f"PRIMARY alpha = {p['alpha']:.3f} {np.round(p['alpha_ci95'], 3).tolist()}  NB {p['negative_binomial_alpha']:.3f}"
          f"  -> {p['verdict']}")
    for k, s in sens.items():
        print(f"  {k:24s} alpha = {s['alpha']:.3f} {np.round(s['alpha_ci95'], 3).tolist()} n={s['n_mainshocks']}"
              f" after={s['n_aftershocks']} -> {s['verdict']}")


if __name__ == '__main__':
    main()
