"""Orthopolic resource catalogue: rule predictions, algebra checks, chance baseline.

Exploratory synthesis of published power laws (configs/resource_catalogue.json).
Each rule case states an orthopolic rule and its inputs; the predicted density
exponent is recomputed here with rule_alpha, so the arithmetic is checked, and
compared with the observed exponent. Most rules restate published derivations;
inputs are independent of the observation only where the config says so.

The catalogue cases are checked for d_log = alpha - 1 and d_lin = alpha, and
grade counts are tabulated. The chance baseline gives the fraction of exponents
in [1, 4.5] that lie within a tolerance of a simple fraction, the probability of
a coincidental "match". Outputs results/resource_catalogue.json and .png.
"""
from collections import Counter
from pathlib import Path
import json
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from orthopolity import rule_alpha, simple_rationals, chance_match   # noqa: E402

OUT = ROOT / 'results'
CFG = json.loads((ROOT / 'configs' / 'resource_catalogue.json').read_text())
RANGE = (1.0, 4.5)
DENOMINATORS = [1, 2, 3, 4, 6]
TOLERANCES = [0.02, 0.05, 0.1]
RULE_ORDER = ['territory', 'press_schechter', 'coordinate', 'transport', 'martingale',
              'growth', 'rate_ratio']
RULE_TITLE = {'territory': 'Territory  α = 1 + d_s/D_k', 'press_schechter': 'Peak height (Press–Schechter)',
              'coordinate': 'Coordinate change  α = 1 + ζ/c', 'transport': 'Transport  α = 1 + w + z − d_F',
              'martingale': 'Martingale  α = 1 + 1/c', 'growth': 'Proportional growth  α → 2',
              'rate_ratio': 'Rate ratio'}
LABEL = {'craters': 'Lunar craters', 'eq_moment': 'Earthquake moment', 'eq_moment_large': 'Moment, M ≥ 6.7',
         'perc2d': 'Percolation 2D', 'perc3d': 'Percolation 3D', 'lakes': 'Lakes', 'imf': 'Stellar IMF',
         'rivers': 'River basins', 'halos': 'Dark-matter halos', 'gsmf': 'Galaxy stellar mass',
         'k41': 'Turbulence 3D', 'kraichnan': 'Turbulence 2D', 'batchelor': 'Passive scalar',
         'dohnanyi': 'Asteroid cascade', 'mrn': 'Dust grains', 'sheldon': 'Ocean biomass',
         'dsa': 'Cosmic rays', 'firms': 'US firms', 'metros': 'US metro areas', 'words': 'Word tokens',
         'weblinks': 'Web in-links', 'avalanches': 'Neuronal avalanches', 'returns': 'Stock returns',
         'omori': 'Aftershocks (Omori)', 'flicker': '1/f noise'}
INK, MUTED, GRID, SURFACE = '#0b0b0b', '#52514e', '#e6e5e0', '#fcfcfb'
AGREE, DISAGREE = '#2a78d6', '#eb6834'
LINES = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100']


def rule_table():
    rows = []
    for c in CFG['rule_cases']:
        pred = rule_alpha(c['rule'], **c['inputs'])
        res = c['observed_alpha'] - pred
        rows.append(dict(id=c['id'], rule=c['rule'], predicted_alpha=pred, observed_alpha=c['observed_alpha'],
                         observed_halfwidth=c['observed_halfwidth'], residual=res,
                         agrees=bool(abs(res) <= c['observed_halfwidth']), inputs_status=c['inputs_status'],
                         grade=c['grade']))
    return rows


def catalogue_checks():
    cases, issues = CFG['catalogue'], []
    for c in cases:
        if c['kind'] in ('density', 'survival', 'rank'):
            a = c['alpha']
            if abs(c['d_log'] - (a - 1)) > 0.02 or abs(c['d_lin'] - a) > 0.02:
                issues.append(dict(system=c['system'], alpha=a, d_log=c['d_log'], d_lin=c['d_lin']))
    grades = Counter(c['grade'] for c in cases)
    by_domain = {d: dict(Counter(c['grade'] for c in cases if c['domain'] == d))
                 for d in sorted({c['domain'] for c in cases})}
    return dict(n_cases=len(cases), grades=dict(grades), grades_by_domain=by_domain,
                exponent_checks=dict(Counter(c['exponent_check'] for c in cases)),
                distribution_algebra_mismatches=issues)


def chance_table():
    lo, hi = RANGE
    return {str(q): {str(t): chance_match(simple_rationals(q, lo, hi), t, lo, hi) for t in TOLERANCES}
            for q in DENOMINATORS}


def plot(rows):
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'axes.edgecolor': MUTED,
                         'axes.labelcolor': INK, 'xtick.color': MUTED, 'ytick.color': INK,
                         'figure.facecolor': SURFACE, 'axes.facecolor': SURFACE})
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(12.5, 8.2), layout='constrained',
                                 gridspec_kw=dict(width_ratios=[1.35, 1]))
    y, ticks, labels, headers = 0, [], [], []
    for rule in RULE_ORDER:
        group = [r for r in rows if r['rule'] == rule]
        if not group:
            continue
        ticks.append(y)
        labels.append(RULE_TITLE[rule])
        headers.append(len(labels) - 1)
        y -= 1
        for r in group:
            color = AGREE if r['agrees'] else DISAGREE
            ax.errorbar(r['residual'], y, xerr=r['observed_halfwidth'], fmt='o', ms=6, color=color,
                        ecolor=color, elinewidth=2, capsize=0, zorder=3)
            ticks.append(y)
            labels.append(LABEL.get(r['id'], r['id']))
            y -= 1
        y -= 0.4
    ax.axvline(0, color=MUTED, lw=1)
    ax.set_yticks(ticks, labels)
    for i, t in enumerate(ax.get_yticklabels()):
        if i in headers:
            t.set_fontweight('bold')
            t.set_color(MUTED)
    ax.tick_params(axis='y', length=0)
    ax.set_xlim(-0.75, 0.75)
    ax.set_ylim(y + 0.4, 0.8)
    ax.set_xlabel('Observed minus rule-predicted density exponent α')
    ax.set_title('A  Orthopolic rules against observed exponents', loc='left', color=INK)
    ax.grid(axis='x', color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.plot([], [], 'o', color=AGREE, label='within observational range')
    ax.plot([], [], 'o', color=DISAGREE, label='outside it')
    ax.legend(loc='upper right', frameon=False, fontsize=8.5,
              title='Bars: reported range of the observation', title_fontsize=7.5)

    lo, hi = RANGE
    tol = np.linspace(0, 0.15, 151)
    for q, color in zip([1, 2, 3, 4], LINES):
        cand = simple_rationals(q, lo, hi)
        cov = [chance_match(cand, t, lo, hi) for t in tol]
        bx.plot(tol, cov, color=color, lw=2)
        name = {1: 'integers', 2: 'halves', 3: 'thirds', 4: 'quarters'}[q]
        bx.annotate(name, (tol[-1], cov[-1]), xytext=(5, 0), textcoords='offset points',
                    fontsize=8.5, color=INK, va='center')
    bx.set(xlim=(0, 0.19), ylim=(0, 1.02), xlabel='Tolerance on the exponent (±)',
           ylabel=f'Chance that a random exponent in [{lo:g}, {hi:g}] matches')
    bx.set_title('B  Chance matches to simple fractions', loc='left', color=INK)
    bx.grid(color=GRID, lw=0.8)
    bx.set_axisbelow(True)
    for a in (ax, bx):
        a.spines[['top', 'right']].set_visible(False)
    fig.savefig(OUT / 'resource_catalogue.png', dpi=180)
    plt.close(fig)


def main():
    rows = rule_table()
    result = dict(status=CFG['status'], rule_cases=rows,
                  rule_summary=dict(n=len(rows), agree=sum(r['agrees'] for r in rows),
                                    disagree=[r['id'] for r in rows if not r['agrees']]),
                  catalogue=catalogue_checks(), chance_match=dict(range=RANGE, by_max_denominator=chance_table()))
    OUT.mkdir(exist_ok=True)
    (OUT / 'resource_catalogue.json').write_text(json.dumps(result, indent=2, ensure_ascii=False))
    plot(rows)
    for r in rows:
        print(f"{r['id']:16s} {r['rule']:15s} pred {r['predicted_alpha']:.3f}  obs {r['observed_alpha']:.3f}"
              f" ± {r['observed_halfwidth']:.3f}  {'agree' if r['agrees'] else 'DISAGREE'}")
    print('catalogue:', json.dumps(result['catalogue'], ensure_ascii=False)[:600])
    print('chance:', json.dumps(result['chance_match']['by_max_denominator']))


if __name__ == '__main__':
    main()
