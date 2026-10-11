"""Plot every primary-cohort comparison from the retained conditional diagnostic."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, required=True)
    args = parser.parse_args()
    ledger = json.loads((args.directory/'ledger.json').read_text())
    bounds = json.loads((args.directory/'bounds.json').read_text())
    modes = [('fixed_prepulse_densities', 'Fixed pre-pulse quotas'),
             ('measured_preliminary_density_changes', 'Measured quota changes (primary)')]
    plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.8), sharey=True)
    for ax, (mode, title) in zip(axes, modes):
        chosen = [r for r in ledger if r['category'] == 'Polycultures' and r['mode'] == mode]
        for row in chosen:
            if row['status'] != 'scored':
                raise ValueError('Plot expects the completed, fully scored cohort')
            x = row['day']+(int(row['vessel'])-6.5)*.055
            low, high = row['observed_tv']['minimum'], row['observed_tv']['maximum']
            color = '#b73526' if row['conditional_bound_exceeded'] else '#276482'
            ax.vlines(x, low, high, color=color, linewidth=1.5)
            ax.plot(x, low, 'o', color=color, markersize=3.4)
            ax.plot(x, high, '_', color=color, markersize=4)
        for bound in bounds:
            if bound['mode'] == mode:
                day, upper = bound['day'], bound['tv_upper']
                ax.hlines(upper, day-.39, day+.39, colors='black', linestyles='--', linewidth=1.5)
        ax.set(title=title, xlabel='Days after nutrient pulse', xticks=[1, 2, 3], xlim=(.5, 3.5))
        ax.grid(axis='y', alpha=.2)
    axes[0].set_ylabel('Total-variation change in nitrogen shares')
    axes[0].set_ylim(0, .65)
    fig.suptitle('Can any carbon/nitrogen prices explain the redistribution?', fontsize=13, y=.98)
    legend = [Line2D([0], [0], color='black', linestyle='--', label='Maximum allowed by model family'),
              Line2D([0], [0], color='#b73526', marker='o', label='All mixtures exceed the bound'),
              Line2D([0], [0], color='#276482', marker='o', label='Bound not exceeded (not model validation)')]
    fig.legend(handles=legend, loc='lower center', bbox_to_anchor=(.5, .06), ncol=1, frameon=False, fontsize=9)
    fig.text(.5, .025, 'Each vertical range covers every pooled-species mixture, not sampling uncertainty. Twelve vessels per day.', ha='center', fontsize=9)
    fig.subplots_adjust(top=.85, bottom=.32, left=.08, right=.98, wspace=.1)
    fig.savefig(args.directory/'capacity.png', dpi=180)
    # No creation clock in the retained figure.
    fig.savefig(args.directory/'capacity.pdf', metadata={'CreationDate': None, 'ModDate': None})
    plt.close(fig)


if __name__ == '__main__':
    main()
