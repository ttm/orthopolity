"""Plot all fixed BioMe diagnostic traces; no fitted dynamics."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--result', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = json.loads(args.result.read_text())
    time = result['hours']
    colors = ['#333333', '#0072B2', '#009E73', '#D55E00', '#CC79A7']
    metrics = ['recovery_nominal', 'recovery_initial', 'control_ratio_initial']
    titles = ['Calibrated stock / nominal 100 nmol', 'Calibrated stock / first reading',
              'Ratio to no-pore controls / first ratio']
    fig, axes = plt.subplots(2, 3, figsize=(13, 7), sharex=True)
    for row, dye in enumerate(['phenol_red', 'bromocresol_purple']):
        data = result['dyes'][dye]
        for col, metric in enumerate(metrics):
            ax = axes[row, col]
            values = np.asarray(data['traces'][metric], dtype=float)
            ax.axhline(1, color='#888888', lw=.8)
            for p, pore in enumerate([0, .03, .1, .2, .4]):
                # The normalized no-pore ratio equals one by definition.
                if metric == 'control_ratio_initial' and p == 0:
                    continue
                label = 'No pores' if p == 0 else f'{pore:g} µm'
                for replicate in range(3):
                    ax.plot(time, values[:, replicate, p], color=colors[p], lw=.7,
                            alpha=.45, ls='--' if p == 0 else '-')
                mean = np.ma.masked_invalid(values[:, :, p]).mean(axis=1)
                ax.plot(time, mean, color=colors[p], lw=1.7, label=label,
                        ls='--' if p == 0 else '-')
            ax.set_title(titles[col], fontsize=10)
            ax.set_xlim(0, 72)
            ax.set_xticks([0, 24, 48, 72])
            ax.spines[['top', 'right']].set_visible(False)
            ax.grid(alpha=.15)
            if row == 1:
                ax.set_xlabel('Hours since first reading')
        axes[row, 0].set_ylabel(dye.replace('_', ' ').capitalize()+'\nStock ratio')
    axes[0, 0].legend(fontsize=8, frameon=False, ncol=2, loc='lower left')
    fig.suptitle('BioMe source qualification: calibrated totals and simultaneous controls', fontsize=14)
    fig.text(.5, .015,
             'Thin lines: 3 same-plate replicates. Thick lines: means. No-pore control ratio is 1 by construction.\n'
             'Optical signal changes do not identify reversible storage, irreversible loss, or gain drift.',
             ha='center', fontsize=9)
    fig.tight_layout(rect=[0, .065, 1, .95])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=180, metadata={'Software': 'orthopolity BioMe diagnostic'})
    plt.close(fig)


if __name__ == '__main__':
    main()
