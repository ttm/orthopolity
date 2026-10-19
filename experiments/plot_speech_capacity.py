"""Display sealed speech-capacity forecasts and the five frozen comparisons."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def plot(result_path, output):
    output = Path(output)
    if output.exists():
        raise ValueError('Refusing to overwrite a retained figure')
    result = json.loads(Path(result_path).read_text())
    scores = result['scores']
    primary = scores['conditional']['per_language']
    comparator = scores['same_text']['per_language']
    languages = sorted(primary)
    observed = np.array([primary[k]['observed_geometric_rate'] for k in languages])
    forecast = np.array([primary[k]['forecast_geometric_rate'] for k in languages])
    same_text = np.array([comparator[k]['forecast_geometric_rate'] for k in languages])

    fig, (left, right) = plt.subplots(1, 2, figsize=(11.2, 4.7))
    limits = (4.2, 9.9)
    left.plot(limits, limits, color='.65', lw=1)
    left.vlines(observed, np.minimum(forecast, same_text),
                np.maximum(forecast, same_text), color='.75', lw=1)
    left.scatter(observed, same_text, s=37, facecolors='white',
                 edgecolors='#5C8062', label='Same-text duration')
    left.scatter(observed, forecast, s=37, c='#216A94',
                 label='Conditional information')
    offsets = {
        'CMN': (6, -10), 'EUS': (-30, 7), 'FIN': (10, -4),
        'HUN': (6, 5), 'JPN': (6, 5), 'KOR': (5, -15),
        'THA': (6, 5), 'TUR': (-30, 8), 'VIE': (6, -11),
        'YUE': (-29, 4),
    }
    for language, x, y in zip(languages, observed, forecast):
        left.annotate(language, (x, y), xytext=offsets[language],
                      textcoords='offset points', fontsize=8,
                      arrowprops={'arrowstyle': '-', 'color': '.5', 'lw': .5})
    left.set(xlim=limits, ylim=limits,
             xlabel='Observed speech rate (syllables/s)',
             ylabel='Forecast speech rate (syllables/s)',
             title='Ten held-out languages')
    left.set_aspect('equal')
    left.legend(frameon=False, fontsize=8, loc='upper left')

    models = ['conditional', 'same_text', 'power', 'unigram', 'syllabic']
    labels = ['Conditional information', 'Same-text duration', 'Fitted power law',
              'Unigram information', 'Constant syllabic rate']
    values = [scores[m]['family_balanced_language_log_mae'] for m in models]
    threshold = np.log(result['config']['maximum_average_factor'])
    right.barh(range(len(models)), values, height=.58,
               color=['#216A94', '#5C8062', '.65', '.65', '.65'])
    for i, value in enumerate(values):
        right.text(value-.004, i, f'{value:.4f}', va='center', ha='right',
                   fontsize=9, color='white' if i < 2 else '.15')
    right.axvline(threshold, ls='--', color='.35', lw=1,
                  label='Frozen limit: ln(1.20)')
    right.set(yticks=range(len(models)), yticklabels=labels,
              xlim=(0, .215), ylim=(5.0, -.6),
              xlabel='Family-balanced language log MAE',
              title='Eight source-defined families, equal weight')
    right.legend(frameon=False, fontsize=8, loc='lower left')
    for ax in (left, right):
        ax.spines[['top', 'right']].set_visible(False)
        ax.grid(alpha=.12)
        ax.set_axisbelow(True)
    fig.suptitle('Speech-rate transfer to held-out languages', fontsize=12)
    fig.text(.5, .035,
             'Retrospective cohort; language geometric means. Entropy uncertainty is not propagated.',
             ha='center', fontsize=8, color='.3')
    fig.subplots_adjust(left=.075, right=.97, top=.82, bottom=.18, wspace=.76)
    fig.savefig(output, dpi=180,
                metadata={'Software': 'Orthopolity speech-capacity transfer'})
    plt.close(fig)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--result', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    plot(args.result, args.output)
