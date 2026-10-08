"""Simulated check of the Gibrat deviation law; this is not empirical evidence.

Units enter at size 1, grow as geometric Brownian motion with drift g and
variance rate sigma2 relative to entrants, and exit at hazard h; entry is
constant (d = 0). The stationary upper tail is Pareto with exponent zeta,
the positive root of (sigma2/2) z^2 + (g - sigma2/2) z - h = 0, equivalently
(zeta - 1)(g + sigma2 zeta/2) = phi with phi = h - g the share of the
normalized total injected by entry per unit time (gibrat_zeta in src/).
zeta = 1, equal resource per logarithmic size interval, holds iff phi = 0.

Two checks: an exact stationary sampler over a grid of phi, and a
time-stepped population started empty, which tests that the dynamics reach
the predicted state rather than assuming it. Outputs results/gibrat.json
and results/gibrat.png.
"""
from pathlib import Path
import json
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from orthopolity import gibrat_zeta, resource_spectrum      # noqa: E402

OUT = ROOT / 'results'
SEED = 20261008
SIGMA2, H = 0.1, 0.05
PHIS = [-0.02, -0.01, 0.0, 0.01, 0.02, 0.05]
N_EXACT = 400000
STEP = dict(birth_rate=1000.0, dt=0.05, horizon=300.0)
MIN_BIN_COUNT = 50   # spectrum bins with fewer units are too noisy to display or fit


def exact_sizes(g, n, rng):
    age = rng.exponential(1 / H, n)
    return np.exp((g - SIGMA2 / 2) * age + np.sqrt(SIGMA2 * age) * rng.standard_normal(n))


def stepped_sizes(g, rng):
    """Euler steps of log size from an empty population; Poisson entry, Bernoulli exit."""
    dt = STEP['dt']
    logs = np.empty(0)
    for _ in range(int(STEP['horizon'] / dt)):
        logs = logs + (g - SIGMA2 / 2) * dt + np.sqrt(SIGMA2 * dt) * rng.standard_normal(len(logs))
        logs = logs[rng.random(len(logs)) >= H * dt]
        logs = np.concatenate([logs, np.zeros(rng.poisson(STEP['birth_rate'] * dt))])
    return np.exp(logs)


def tail_fit(x):
    """MLE of the exact Pareto branch above the entry size, with its standard error."""
    t = x[x > 1]
    z = len(t) / np.log(t).sum()
    return float(z), float(z / np.sqrt(len(t))), len(t)


def resource_slope(s):
    keep = s['count'] >= MIN_BIN_COUNT
    return float(np.polyfit(np.log(s['center'][keep]), np.log(s['phi'][keep]), 1)[0])


def main():
    rng = np.random.default_rng(SEED)
    rows = []
    edges = np.geomspace(1, 1e4, 17)
    profiles = {}
    for phi in PHIS:
        g = H - phi
        predicted = gibrat_zeta(g, SIGMA2, 0.0, H)
        z, se, n = tail_fit(exact_sizes(g, N_EXACT, rng))
        x = stepped_sizes(g, rng)
        zs, ses, ns = tail_fit(x)
        s = resource_spectrum(x[x >= 1], x[x >= 1], edges)
        profiles[phi] = s
        rows.append(dict(phi=phi, g=g, sigma2=SIGMA2, h=H, predicted_zeta=predicted,
                         exact_sampler=dict(zeta=z, se=se, n_tail=n),
                         time_stepped=dict(zeta=zs, se=ses, n_tail=ns, population=len(x)),
                         stepped_log_resource_slope=resource_slope(s)))
        print(f"phi={phi:+.2f}  predicted zeta={predicted:.3f}  exact={z:.3f}±{se:.3f}  "
              f"stepped={zs:.3f}±{ses:.3f} (n={len(x)})")

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), layout='constrained')
    ax = axes[0]
    grid = np.linspace(min(PHIS), max(PHIS), 200)
    ax.plot(grid, [gibrat_zeta(H - p, SIGMA2, 0, H) for p in grid], color='#2468a0', lw=2,
            label='Deviation law (root of the quadratic)')
    ax.errorbar(PHIS, [r['time_stepped']['zeta'] for r in rows],
                yerr=[2 * r['time_stepped']['se'] for r in rows], fmt='o', color='black',
                label='Time-stepped population, ±2 SE')
    ax.axhline(1, ls='--', color='#999'); ax.axvline(0, ls=':', color='#999')
    ax.set(xlabel=r'Entry share of normalized resource growth $\phi$',
           ylabel=r'Upper-tail exponent $\zeta$', title='A  Equal log allocation at $\\phi=0$')
    ax.legend(frameon=False, fontsize=8.5)
    ax = axes[1]
    colors = {-0.02: '#2468a0', -0.01: '#7fa6c9', 0.0: 'black', 0.01: '#e0a07a', 0.02: '#c8703f', 0.05: '#8f3b1b'}
    for phi in PHIS:
        s = profiles[phi]
        keep = s['count'] >= MIN_BIN_COUNT
        ax.plot(s['center'][keep], s['phi'][keep], 'o-', ms=3, lw=2.4 if phi == 0 else 1.3,
                color=colors[phi], label=fr'$\phi={phi:+.2f}$')
    ax.set(xscale='log', yscale='log', xlabel='Size relative to entrants',
           ylabel='Normalized resource per log interval', title='B  Resource spectra from the dynamics')
    ax.text(0.02, 0.03, f'Bins with at least {MIN_BIN_COUNT} units', transform=ax.transAxes,
            fontsize=8, color='#555555')
    ax.legend(frameon=False, fontsize=8, ncol=2)
    for ax in axes:
        ax.spines[['top', 'right']].set_visible(False)
    fig.suptitle('Simulation of a stated model — not empirical data', fontsize=10, color='#555555')
    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / 'gibrat.png', dpi=180)
    plt.close(fig)
    (OUT / 'gibrat.json').write_text(json.dumps(dict(
        model='GBM growth relative to entrants, constant entry, exit hazard h; d = 0',
        seed=SEED, exact_sample_size=N_EXACT, time_stepping=STEP, rows=rows,
        note='Simulation of a stated model. It checks the algebra and the approach to the '
             'stationary state; it does not show that any real system satisfies the model.'),
        indent=2))


if __name__ == '__main__':
    main()
