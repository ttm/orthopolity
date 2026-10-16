"""Display the sealed biological forecasts and all predeclared alternatives."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def plot(result_path, output):
    result = json.loads(Path(result_path).read_text())
    observed = np.array([r['observed'] for r in result['outcomes']])
    primary = observed+np.array(result['scores']['pool']['errors'])
    direct = observed+np.array(result['scores']['direct_assay']['errors'])
    fig, (left, right) = plt.subplots(1, 2, figsize=(10.4, 4.2))
    left.plot([.25, 1.02], [.25, 1.02], color='.65', lw=1)
    left.vlines(observed, np.minimum(primary, direct), np.maximum(primary, direct), color='.7', lw=1)
    left.scatter(observed, direct, s=35, facecolors='white', edgecolors='#5C8062', label='Direct assay')
    left.scatter(observed, primary, s=35, c='#216A94', label='Resource-pool forecast')
    for row, x, y in zip(result['outcomes'], observed, primary):
        left.annotate(row['id'], (x, y), xytext=(4, 5), textcoords='offset points', fontsize=8)
    left.set(xlim=(.25, 1.02), ylim=(.25, 1.02), xlabel='Observed cell capacity',
             ylabel='Forecast cell capacity', title='Ten new protein constructs')
    left.set_aspect('equal')
    left.legend(frameon=False, fontsize=8, loc='upper left')
    models = ['pool', 'direct_assay', 'linear_burden', 'affine', 'constant']
    names = ['Resource-pool model', 'Direct assay', 'Linear burden', 'Affine transfer', 'Constant capacity']
    values = [result['scores'][m]['family_balanced_mae'] for m in models]
    right.barh(range(5), values, height=.58, color=['#216A94', '#5C8062', '.65', '.65', '.65'])
    for i, value in enumerate(values):
        right.text(value+.004, i, f'{value:.4f}', va='center', fontsize=9)
    right.axvline(.10, ls='--', color='.35', lw=1, label='Frozen accuracy limit')
    right.set(yticks=range(5), yticklabels=names, xlim=(0, .25),
              xlabel='Family-balanced mean absolute error', title='Seven gene families, equal weight')
    right.invert_yaxis()
    right.set_ylim(5.0, -.6)
    right.legend(frameon=False, fontsize=8, loc='lower right')
    for ax in (left, right):
        ax.spines[['top', 'right']].set_visible(False)
        ax.grid(alpha=.12)
        ax.set_axisbelow(True)
    fig.suptitle('Independent assay information transfers; reciprocal correction does not improve it', fontsize=12)
    fig.text(.5, .015, 'Retrospective cohort; forecasts sealed before numerical targets. Shared input uncertainty is not propagated.',
             ha='center', fontsize=8, color='.3')
    fig.subplots_adjust(left=.07, right=.97, top=.82, bottom=.17, wspace=.70)
    output = Path(output)
    if output.exists():
        raise ValueError('Refusing to overwrite a retained figure')
    fig.savefig(output, dpi=180, metadata={'Software': 'Orthopolity biological assay transfer'})
    plt.close(fig)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--result', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    plot(a.result, a.output)
