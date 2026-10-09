"""Render the retained qualification gates; no inference or new selection."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT/'results/seismic-qualification-2026-10-10'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, default=DIRECTORY)
    args = parser.parse_args()
    result = json.loads((args.directory/'result.json').read_text())
    rows = pd.read_csv(args.directory/'cluster-ledger.csv')
    rows = rows[rows.scaling_ratio.notna()].sort_values('scaling_ratio')
    fig, (left, right) = plt.subplots(1, 2, figsize=(11, 7.5), gridspec_kw={'width_ratios': [1, 1.3]})
    counts = [result[key] for key in ['n_clusters_at_least_200_raw',
        'n_clusters_at_least_200_quality', 'n_clusters_at_least_200_complete',
        'n_resolution_qualified_clusters']]
    bars = left.bar(range(4), counts, color=['#97a8b7', '#7893aa', '#4c789b', '#206391'], width=.68)
    left.bar_label(bars, padding=4, fontsize=12)
    left.axhline(10, ls='--', color='#a24332', label='Required: 10 sequences')
    left.set_xticks(range(4), ['Raw\n≥200', 'Quality\n≥200', 'Complete\n≥200', 'Resolved\nspan ≥3'])
    left.set_ylim(0, 45)
    left.set_ylabel('Number of published sequences')
    left.set_title('Six sequences survive all gates', loc='left', pad=15)
    left.legend(loc='upper right', frameon=False, fontsize=9)
    y = np.arange(len(rows))
    right.hlines(y, rows.scaling_ratio, rows.geometry_only_ratio, color='#c9cdd0', lw=1)
    right.scatter(rows.geometry_only_ratio, y, color='#b3b9bd', s=24, label='Ignoring location error (diagnostic)')
    right.scatter(rows.scaling_ratio, y, color='#206391', s=32, label='With frozen absolute-error floor', zorder=3)
    right.axvline(3, color='#a24332', ls='--', label='Required span: 3')
    right.set_xscale('log')
    right.set_yticks(y, rows.cluster.astype(str))
    right.set_ylabel('Published sequence ID')
    right.set_xlabel('Available distance span, r_max / r_min (log scale)')
    right.set_title('Location precision limits the usable span', loc='left', pad=15)
    right.legend(loc='upper center', bbox_to_anchor=(.5, -.14), fontsize=8, frameon=False)
    for ax in (left, right):
        ax.spines[['top', 'right']].set_visible(False)
    fig.suptitle('Southern California, 1981–2018: eligibility assessment', fontsize=15, y=.98)
    fig.text(.06, .018, '123,275 events • 26,137 published sequences • No b-value, D2 or hypothesis regression fitted', fontsize=10)
    fig.tight_layout(rect=(0, .08, 1, .95), w_pad=3)
    for suffix in ['png', 'svg']:
        fig.savefig(args.directory/f'qualification.{suffix}', dpi=180, metadata={'Date': None} if suffix == 'svg' else None)
    plt.close(fig)


if __name__ == '__main__':
    main()
