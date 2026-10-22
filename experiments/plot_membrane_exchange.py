"""Plot retained membrane qualification/transfer JSON without reading the archive.

The display has no fitting or target-release path.  Concentration contrasts and
totals use each pair's measured initial stock; the reference measure is chamber
volume, neither log-orthopolic nor linear-orthopolic size allocation.
"""

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


COLORS = ('#216A94', '#6A8264', '#A06435', '#7D6393')
STYLE = {
    'font.family': 'DejaVu Sans',
    'font.size': 9,
    'axes.titlesize': 10,
    'axes.labelsize': 9,
    'legend.fontsize': 8,
    'svg.hashsalt': 'orthopolity-membrane-exchange',
}


def _load(path):
    result = json.loads(Path(path).read_text())
    if not isinstance(result, dict):
        raise ValueError('Expected a saved JSON object')
    return result


def _destination(output):
    output = Path(output)
    if output.exists():
        raise ValueError('Refusing to overwrite a retained figure')
    if output.suffix.lower() != '.png':
        raise ValueError('Use a PNG destination for deterministic figure replay')
    return output


def _axes_style(ax):
    ax.spines[['top', 'right']].set_visible(False)
    ax.grid(alpha=.14)
    ax.set_axisbelow(True)


def _save(fig, output):
    fig.savefig(output, dpi=180,
                metadata={'Software': 'Orthopolity membrane-exchange transfer'})
    plt.close(fig)


def _paired_values(observations, sample):
    rows = [row for row in observations if row['sample'] == sample]
    times = sorted({row['time_hours'] for row in rows})
    donor, recipient = [], []
    for time in times:
        pair = [row for row in rows if row['time_hours'] == time]
        d = [row['absorbance'] for row in pair if row['chamber'].endswith('_C1')]
        a = [row['absorbance'] for row in pair if row['chamber'].endswith('_C2')]
        if len(d) != 1 or len(a) != 1:
            raise ValueError('Expected exactly one observation of each chamber')
        donor.append(d[0])
        recipient.append(a[0])
    if not times or times[0] != 0:
        raise ValueError('An observed time-zero pair is required')
    return np.asarray(times), np.asarray(donor), np.asarray(recipient)


def plot_qualification(qualification_path, output):
    """Display already authorized earlier-cohort measurements and fitted rates."""
    output = _destination(output)
    document = _load(qualification_path)
    result = document['qualification']
    rates = result['rates']
    if len(rates) != 4 or result['total_stock'] is None:
        raise ValueError('This display requires the four earlier rate/stock calculations')
    config = document['config']
    optics = result['optics'][config['calibration_run']]
    intercept = optics['intercept']
    observations = document['inputs']['calibration_observations']
    f = result['retention_fraction']

    with plt.rc_context(STYLE):
        fig = plt.figure(figsize=(12, 7.2))
        grid = fig.add_gridspec(2, 4, height_ratios=[1, 1.05], hspace=.56, wspace=.34)
        stock_ax = fig.add_subplot(grid[1, :2])
        rate_ax = fig.add_subplot(grid[1, 2:])
        contrast_axes = []
        for index, (rate, color) in enumerate(zip(rates, COLORS)):
            ax = fig.add_subplot(grid[0, index])
            contrast_axes.append(ax)
            times, donor, recipient = _paired_values(observations, rate['sample'])
            initial_total = donor[0] + recipient[0] - 2 * intercept
            if initial_total <= 0:
                raise ValueError('Normalized display requires positive initial stock')
            label = rate['sample'].rsplit('_', 1)[-1]
            ax.plot(times, np.asarray(rate['fitted_differences']) / initial_total,
                    color=color, lw=1.6, label='Fitted exchange')
            ax.scatter(times, (donor - recipient) / initial_total,
                       color=color, s=18, zorder=3, label='Observed contrast')
            ax.set(title=label, xlabel='Elapsed time (h)', xlim=(-1.5, 68))
            if index == 0:
                ax.set_ylabel('Contrast / initial total')
            stock_ax.plot(times, (donor + recipient - 2 * intercept) / initial_total,
                          color=color, marker='o', ms=3.2, lw=1, label=label)
            for lo, hi in rate['confidence_intervals_g_ml_per_hour']:
                if lo is None or hi is None:
                    raise ValueError('The finite-rate display requires bounded conductance sets')
                rate_ax.plot([lo, hi], [index, index], color=color, lw=3,
                             solid_capstyle='butt')
            rate_ax.scatter([rate['g_ml_per_hour']], [index], color=color,
                            edgecolors='white', linewidths=.7, s=38, zorder=3)
            _axes_style(ax)
        ymin = min(ax.get_ylim()[0] for ax in contrast_axes)
        ymax = max(ax.get_ylim()[1] for ax in contrast_axes)
        for ax in contrast_axes:
            ax.set_ylim(ymin, ymax)
        contrast_axes[0].legend(frameon=False, loc='upper right', fontsize=7)
        stock_ax.plot(times, f ** np.arange(len(times)), color='.15', ls='--',
                      lw=1.6, label='Sampling-only total')
        stock_ax.set(xlabel='Elapsed time (h)', ylabel='Total / initial total',
                     title='Earlier-cohort stock recovery', xlim=(-1.5, 68))
        stock_ax.legend(frameon=False, ncol=3, loc='lower left', fontsize=7)
        stock = result['total_stock']
        stock_ax.text(.02, .97,
                      f"Joint stock test: F = {stock['statistic']:.3f}, "
                      f"p = {stock['p_value']:.3f}",
                      transform=stock_ax.transAxes, va='top', fontsize=8)
        rate_ax.set(yticks=range(4),
                    yticklabels=[rate['sample'].rsplit('_', 1)[-1] for rate in rates],
                    xlabel='Effective conductance (mL/h)',
                    title='Full 99% rate sets', ylim=(3.5, -.5))
        for ax in (stock_ax, rate_ax):
            _axes_style(ax)
        fig.suptitle('Membrane-pair exchange: earlier-cohort qualification', fontsize=13, y=.96)
        fig.text(.5, .045,
                 'Reference measure: chamber volume. The common standards/sample noise model is assumed; '
                 'stock non-rejection does not prove conservation.',
                 ha='center', fontsize=8, color='.3')
        fig.subplots_adjust(left=.065, right=.98, bottom=.16, top=.86)
        _save(fig, output)


def plot_transfer(result_path, forecast_path, output):
    """Display released target results and sealed predictions from JSON only.

    The shaded region contains only the frozen rate-set sensitivity, conditional
    on measured baselines and optical coefficients.  Shared optical/baseline
    uncertainty is retained numerically in the forecast artifact; this region
    is deliberately not labelled as a prediction interval for new membranes.
    """
    output = _destination(output)
    evaluation = _load(result_path)['evaluation']
    forecasts = _load(forecast_path)['forecasts']
    pairs = evaluation['pairs']
    if len(pairs) != 4:
        raise ValueError('Expected the four frozen target pairs')
    predictions = forecasts['predictions']
    forecast_index = {
        (row['sample'], row['time_hours'], row['chamber']): row
        for row in predictions
    }
    if len(predictions) != 56 or len(forecast_index) != 56:
        raise ValueError('Expected exactly the 56 sealed chamber forecasts')
    styles = {
        'exchange': ('#216A94', '-', 1.8, 'Transferred exchange'),
        'empirical': ('#6A8264', '--', 1.4, 'Earlier empirical kernel'),
        'persistence': ('.50', ':', 1.2, 'Persistence'),
        'instant_mixing': ('.65', '-.', 1.2, 'Instantaneous mixing'),
    }
    with plt.rc_context(STYLE):
        fig, axes = plt.subplots(2, 4, figsize=(12, 7.4), squeeze=False)
        for column, pair in enumerate(pairs):
            points = pair['points']
            if len(points) != 7 or len({p['time_hours'] for p in points}) != 7:
                raise ValueError('Expected all seven positive-time target observations')
            points = sorted(points, key=lambda p: p['time_hours'])
            times = [point['time_hours'] for point in points]
            upper, lower = axes[:, column]
            envelope_lo, envelope_hi = [], []
            for point in points:
                rows = [row for key, row in forecast_index.items()
                        if key[:2] == (pair['sample'], point['time_hours'])]
                donor = [row for row in rows if row['chamber'].endswith('_C1')]
                recipient = [row for row in rows if row['chamber'].endswith('_C2')]
                if len(donor) != 1 or len(recipient) != 1:
                    raise ValueError('Missing or duplicate sealed chamber forecast')
                d_lo, d_hi = donor[0]['rate_envelope_uM']
                a_lo, a_hi = recipient[0]['rate_envelope_uM']
                initial_total = pair['baseline_total_uM']
                envelope_lo.append((d_lo - a_hi) / initial_total)
                envelope_hi.append((d_hi - a_lo) / initial_total)
            upper.fill_between(times, envelope_lo, envelope_hi, color='#216A94',
                               alpha=.12, linewidth=0, label='Four 99% rate sets')
            for model, (color, linestyle, width, label) in styles.items():
                upper.plot(times, [point['models'][model]['normalized_contrast']
                                   for point in points],
                           color=color, ls=linestyle, lw=width, label=label)
            upper.scatter(times, [point['normalized_contrast'] for point in points],
                          color='.12', s=23, zorder=5, label='Observed')
            upper.set(title=pair['sample'].rsplit('_', 1)[-1], xlim=(0, 72))
            lower.axhline(1, color='.45', lw=1.2, ls='--', label='Sampling-only total')
            lower.plot(times, [point['total_recovery_ratio'] for point in points],
                       color='.12', marker='o', ms=4, lw=1, label='Observed total')
            lower.set(xlabel='Elapsed time (h)', xlim=(0, 72))
            for ax in (upper, lower):
                _axes_style(ax)
        for row in axes:
            ymin = min(ax.get_ylim()[0] for ax in row)
            ymax = max(ax.get_ylim()[1] for ax in row)
            for ax in row:
                ax.set_ylim(ymin, ymax)
        axes[0, 0].set_ylabel('Contrast / initial total')
        axes[1, 0].set_ylabel('Total / sampling-only total')
        handles, labels = axes[0, 0].get_legend_handles_labels()
        # Point observations lead; the broad shaded envelope is explicitly
        # separated from the four point-forecast comparisons in the legend.
        order = [5, 1, 2, 3, 4, 0]
        fig.legend([handles[i] for i in order], [labels[i] for i in order],
                   loc='upper center', bbox_to_anchor=(.52, .915),
                   frameon=False, ncol=3, columnspacing=2.2)
        fig.suptitle('Membrane-pair transfer: four later manual pairs', fontsize=13, y=.975)
        fig.text(.5, .435, 'Separate stock recovery; unity includes the prescribed sampling loss',
                 ha='center', fontsize=10)
        fig.text(.5, .065,
                 'Shading: conditional rate-set sensitivity, not a new-membrane prediction interval. '
                 'Optical/baseline uncertainty is reported separately.',
                 ha='center', fontsize=8, color='.3')
        fig.text(.5, .035,
                 'Reference measure: chamber volume. Procedure and batch change together; '
                 'kinetic agreement does not establish conservation.',
                 ha='center', fontsize=8, color='.3')
        fig.subplots_adjust(left=.065, right=.98, bottom=.16, top=.78,
                            hspace=.46, wspace=.31)
        _save(fig, output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    stage = parser.add_mutually_exclusive_group(required=True)
    stage.add_argument('--qualification', type=Path)
    stage.add_argument('--result', type=Path)
    parser.add_argument('--forecast', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.qualification is not None:
        if args.forecast is not None:
            parser.error('--forecast is only used with --result')
        plot_qualification(args.qualification, args.output)
    else:
        if args.forecast is None:
            parser.error('--result requires --forecast')
        plot_transfer(args.result, args.forecast, args.output)


if __name__ == '__main__':
    main()
