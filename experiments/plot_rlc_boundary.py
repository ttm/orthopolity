"""Plot the sealed component forecast and released circuit observations."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prediction', type=Path, required=True)
    parser.add_argument('--result', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    prediction = json.loads(args.prediction.read_text())
    result = json.loads(args.result.read_text())
    rows = sorted(prediction['rows'], key=lambda r: r['frequency_hz'])
    measured = {r['row']: r for r in result['observations']}
    f = np.array([r['frequency_hz'] for r in rows])
    excluded = set(prediction['config']['previously_exposed_zero_based_rows'])
    primary = np.array([r['row'] not in excluded for r in rows])
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.5), sharex=True)
    for ax, field, title in zip(axes, ['real_ohm', 'imag_ohm'], ['Resistive response', 'Inductive and capacitive response']):
        forecast = np.array([r[field] for r in rows])
        actual = np.array([measured[r['row']][field] for r in rows])
        ax.axvspan(*prediction['crossing_hz_interval'], color='#E69F00', alpha=.22,
                   label='Conditional crossing range')
        ax.plot(f, forecast, color='#0072B2', lw=1.8, label='Independent component forecast')
        ax.scatter(f[primary], actual[primary], color='#222222', s=12,
                   label='80 unexposed observations', zorder=3)
        ax.scatter(f[~primary], actual[~primary], facecolors='white', edgecolors='#666666',
                   s=30, label='Previously exposed row', zorder=4)
        ax.axhline(0, color='#888888', lw=.7)
        ax.set_xscale('log')
        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel(('Real' if field == 'real_ohm' else 'Imaginary')+' impedance (Ω)')
        ax.set_title(title, fontsize=11)
        ax.spines[['top', 'right']].set_visible(False)
        ax.grid(alpha=.15)
    axes[0].legend(frameon=False, fontsize=8, loc='upper left')
    axes[1].text(.02, .96, 'Every passive RC network:\nIm Z ≤ 0 at the driven port.',
                 transform=axes[1].transAxes, va='top', fontsize=9)
    score = result['primary']
    fig.suptitle('Independent components predict an inductive response', fontsize=13)
    fig.text(.5, .018,
             f"Primary relative RMS error: RLC {100*score['rlc_relative_rms']:.2f}%  |  "
             f"Any passive RC model: at least {100*score['rc_relative_rms_lower_bound']:.2f}%\n"
             'One driven circuit; nominal components, no response fit. The shaded band is not a confidence interval.',
             ha='center', fontsize=9)
    fig.tight_layout(rect=[0, .11, 1, .93])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=180, metadata={'Software': 'orthopolity RLC boundary forecast'})
    plt.close(fig)


if __name__ == '__main__':
    main()
