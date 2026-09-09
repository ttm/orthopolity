"""Deterministic analytic illustrations; these are not empirical evidence.

Panel A uses q(k)=k on k in [1,100]. If n(k) is number density per dk,
constant dR/dk implies n(k) proportional to k^-1, whereas constant dR/dln(k)
implies n(k) proportional to k^-2. Both plotted log-resource densities are
normalized to integrate to one with respect to u=ln(k).

Panel B uses f_+(u)=C exp(cu), f_-(u)=C exp(-cu), u in [-1,1], with
C=c/(2 sinh(c)) and c=2. Each integrates to one. Their mean log-slope is zero,
but their arithmetic mean is C cosh(cu), which is not constant.
"""
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results'


def main():
    plt.rcParams.update({
        'font.family': 'DejaVu Sans', 'font.size': 10,
        'axes.titlesize': 11, 'axes.labelsize': 10,
        'legend.fontsize': 9, 'svg.fonttype': 'none',
    })
    blue, orange, purple, grey = '#2468a0', '#b65c22', '#684593', '#737373'
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.4), layout='constrained')

    # Analytic unit-integral densities with respect to logarithmic size.
    k = np.geomspace(1.0, 100.0, 2001)
    logk = np.log(k)
    logflat = np.full_like(k, 1 / np.log(100))
    linearflat = k / (100 - 1)
    ax = axes[0]
    ax.plot(k, logflat, color=blue, lw=2.3,
            label=r'Equal per $d\ln k$: $n(k)\propto k^{-2}$')
    ax.plot(k, linearflat, color=orange, lw=2.3,
            label=r'Equal per $dk$: $n(k)\propto k^{-1}$')
    ax.set(xscale='log', yscale='log', xlim=(1, 100), ylim=(0.008, 1.8),
           xlabel=r'Size ratio $k/k_{\min}$',
           ylabel=r'Normalized log-resource density $p(u)$',
           title='A  Equal allocation depends on the measure')
    ax.set_xticks([1, 10, 100], labels=['1', '10', '100'])
    ax.set_yticks([0.01, 0.1, 1], labels=['0.01', '0.1', '1'])
    ax.legend(loc='upper left', frameon=False)
    ax.text(0.98, 0.05,
            r'$q(k)=k,\quad u=\ln(k/k_{\min})$' '\n'
            r'Both curves: $\int_0^{\ln 100}p(u)\,du=1$',
            transform=ax.transAxes, ha='right', va='bottom', fontsize=9,
            bbox=dict(facecolor='white', edgecolor='none', alpha=0.9, pad=3))

    # Equal resource totals do not make a zero mean log-slope imply a flat mean.
    u = np.linspace(-1, 1, 2001)
    c = 2.0
    normalizer = c / (2 * np.sinh(c))
    positive = normalizer * np.exp(c * u)
    negative = normalizer * np.exp(-c * u)
    arithmetic = (positive + negative) / 2
    ax = axes[1]
    ax.plot(u, positive, color=orange, lw=1.5, alpha=0.8,
            label=r'$f_+(u)=C e^{2u}$')
    ax.plot(u, negative, color=blue, lw=1.5, alpha=0.8,
            label=r'$f_-(u)=C e^{-2u}$')
    ax.plot(u, arithmetic, color=purple, lw=2.8,
            label=r'Arithmetic mean: $C\cosh(2u)$')
    ax.axhline(0.5, color=grey, lw=1.3, ls='--', label='Flat profile with equal total')
    ax.set(xlim=(-1, 1), ylim=(0, 2.2),
           xlabel=r'Log-size coordinate $u$', ylabel='Normalized resource profile',
           title='B  Zero mean log-slope does not imply flatness')
    ax.set_xticks([-1, -0.5, 0, 0.5, 1])
    ax.legend(loc='upper center', frameon=False, fontsize=8.5)
    ax.text(0.5, 0.48,
            r'Log-slopes: $+2$ and $-2$; mean $=0$' '\n'
            r'$C=1/\sinh(2);\quad\int_{-1}^{1}f_\pm(u)\,du=1$',
            transform=ax.transAxes, ha='center', va='center', fontsize=9,
            bbox=dict(facecolor='white', edgecolor='none', alpha=0.9, pad=3))
    for ax in axes:
        ax.spines[['top', 'right']].set_visible(False)
        ax.grid(axis='y', color='#e6e6e6', lw=0.6)
        ax.set_axisbelow(True)
    fig.suptitle('Analytic illustrations — no empirical data', fontsize=10, color='#555555')
    OUT.mkdir(exist_ok=True)
    for suffix in ('png', 'svg'):
        path = OUT / f'theory.{suffix}'
        fig.savefig(path, dpi=200)
        if suffix == 'svg':
            path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines()) + '\n')
    plt.close(fig)

    integrals = {
        'panel_A_equal_log': np.trapezoid(logflat, logk),
        'panel_A_equal_linear': np.trapezoid(linearflat, logk),
        'panel_B_positive': np.trapezoid(positive, u),
        'panel_B_negative': np.trapezoid(negative, u),
        'panel_B_arithmetic_mean': np.trapezoid(arithmetic, u),
    }
    if not all(abs(value - 1) < 2e-6 for value in integrals.values()):
        raise ArithmeticError(f'Illustration normalization failed: {integrals}')
    print('Analytic figure saved to results/theory.png and results/theory.svg')
    print('Numerical integrals (each analytically 1):',
          {key: round(float(value), 8) for key, value in integrals.items()})


if __name__ == '__main__':
    main()
