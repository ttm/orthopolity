"""Descriptive comparison of completed lake geometry/uncertainty calculations."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--result-dir', type=Path, default=ROOT/'results/lake-metric-followup-2026-10-09')
    args = parser.parse_args()
    old = json.loads((ROOT/'results/lake-gyration-2026-10-09/result.json').read_text())
    new = json.loads((args.result_dir/'result.json').read_text())
    full, matched = new['primary_all_lakes_country_blocks'], new['matched_lakes_basin_blocks']
    rows = [
        ('Original map geometry · iid', old['zeta_R'], old['zeta_R_ci95'], '#737b85'),
        ('Original map geometry · Country', old['zeta_R'], old['country_block_ci95_not_preregistered'], '#737b85'),
        ('Local full geometry · iid', full['zeta_R'], full['iid_ci95'], '#216e9e'),
        ('Local full geometry · Country', full['zeta_R'], full['block_ci95'], '#216e9e'),
        ('Local full geometry · matched basins', matched['zeta_R'], matched['block_ci95'], '#a44322')]
    fig, ax = plt.subplots(figsize=(8, 4.3), constrained_layout=True)
    ax.axvspan(1.9, 2.1, color='#dcebd9', label='Declared equivalence band [1.9, 2.1]')
    ax.axvline(2, color='#43733b', lw=1, ls=':')
    for y, (_, estimate, interval, color) in enumerate(rows):
        ax.plot(interval, [y, y], color=color, lw=2.2)
        ax.plot(estimate, y, 'o', color=color, ms=6)
    ax.set_yticks(range(len(rows)), [row[0] for row in rows], fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel('Survival exponent ζ, with 95% resampling interval')
    ax.set_title('Global lake result: geometry and spatial uncertainty', fontsize=12, loc='left')
    ax.spines[['top', 'right']].set_visible(False)
    ax.legend(loc='lower left', fontsize=8)
    ax.set_ylim(len(rows)-.25, -.7)
    fig.savefig(args.result_dir/'interval-comparison.png', dpi=180)
    fig.savefig(args.result_dir/'interval-comparison.svg')
    plt.close(fig)


if __name__ == '__main__':
    main()
