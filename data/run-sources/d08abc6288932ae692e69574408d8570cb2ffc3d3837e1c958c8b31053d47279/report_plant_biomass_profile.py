#!/usr/bin/env python3
"""Post-hoc figures from retained plant-profile forecasts and evaluations only.

No source CSV, fitting, scoring, simulation, or decision procedure is called.
The only new aggregation is an equal-plot arithmetic mean of retained count
shares for presentation. Synthetic census means and empirical scores are read
from their retained outputs. Existing artifacts are never replaced by changed
bytes, and the manifest records every input and this report's source digest.
"""
from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/plant-biomass-profile/2026-10-03'
RESULTS = ROOT / 'results/plant-biomass-profile'
MODEL_NAMES = {'log_neutral': 'Logarithmic neutrality', 'linear_neutral': 'Linear neutrality',
               'empirical': 'Development histogram', 'bounded_pareto': 'Bounded Pareto',
               'bounded_weibull': 'Bounded Weibull'}
COLORS = {'log_neutral': '#52514e', 'linear_neutral': '#898781', 'empirical': '#2a78d6',
          'bounded_pareto': '#1baf7a', 'bounded_weibull': '#eb6834'}
LINESTYLES = {'log_neutral': '--', 'linear_neutral': ':', 'empirical': '-',
              'bounded_pareto': '-.', 'bounded_weibull': '-'}
SURFACE, INK, SECONDARY, MUTED, GRID, AXIS = '#fcfcfb', '#0b0b0b', '#52514e', '#898781', '#e1e0d9', '#c3c2b7'
ARTIFACT_NAMES = ['mass-profile.png', 'mass-profile.svg']
REPORT_MANIFEST = RESULTS / 'figure-manifest.json'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def ref(path):
    path = Path(path)
    return dict(path=path.relative_to(ROOT).as_posix(), sha256=digest(path))


def checked(reference):
    path = ROOT / reference['path']
    if digest(path) != reference['sha256']:
        raise RuntimeError(f'Retained input changed: {reference["path"]}')
    return path


def read_json(path):
    return json.loads(Path(path).read_text())


def write_exact(path, content):
    path = Path(path)
    if path.exists() and path.read_bytes() != content:
        raise RuntimeError(f'Refusing to overwrite changed retained artifact: {path}')
    path.write_bytes(content)


def inputs():
    """Verify retained-output hashes without reading source observations."""
    if REPORT_MANIFEST.exists():
        previous = read_json(REPORT_MANIFEST)
        for item in [previous['source'], *previous['inputs'], *previous['artifacts']]:
            checked(item)
    output_manifest = read_json(RESULTS / 'output-manifest.json')
    study_path = RESULTS / 'study.json'
    study_reference = next(item for item in output_manifest['artifacts']
                           if ROOT / item['path'] == study_path)
    study = read_json(checked(study_reference))
    frozen = read_json(checked(study['frozen_forecasts']))
    calibration = read_json(checked(frozen['calibration_reference']))
    if not study['run_id'] == frozen['run_id'] == calibration['run_id'] == output_manifest['run_id']:
        raise RuntimeError('Retained outputs identify different runs')
    return study, frozen, calibration


def style(plt):
    plt.rcParams.update({'font.family': 'sans-serif', 'font.sans-serif': ['Helvetica', 'Arial', 'DejaVu Sans'],
                         'font.size': 9, 'axes.edgecolor': AXIS, 'axes.labelcolor': SECONDARY,
                         'axes.titlecolor': INK, 'axes.titlesize': 10, 'axes.spines.top': False,
                         'axes.spines.right': False, 'axes.linewidth': .8, 'axes.facecolor': SURFACE,
                         'figure.facecolor': SURFACE, 'savefig.facecolor': SURFACE,
                         'xtick.color': MUTED, 'ytick.color': MUTED, 'xtick.labelcolor': SECONDARY,
                         'ytick.labelcolor': SECONDARY, 'grid.color': GRID, 'grid.linewidth': .6,
                         'legend.frameon': False, 'svg.hashsalt': 'plant-biomass-profile-2026-10-03'})


def save(figure):
    for extension in ('png', 'svg'):
        buffer = io.BytesIO()
        figure.savefig(buffer, format=extension, dpi=190, bbox_inches='tight',
                       metadata={'Date': None} if extension == 'svg' else {'Software': None})
        write_exact(RESULTS / f'mass-profile.{extension}', buffer.getvalue())


def plot_template(axis, x, models, model, quantity):
    axis.plot(x, models[model][quantity], color=COLORS[model], linestyle=LINESTYLES[model],
              linewidth=1.6, label=MODEL_NAMES[model])


def figure(study, frozen, calibration, plt):
    from matplotlib.lines import Line2D

    forecasts, evaluated = frozen['forecasts'], study['evaluation']
    observed = evaluated['observed_profiles']
    plots = sorted(observed)
    models = forecasts['models']
    log_edges = np.log10(forecasts['domain']['edges'])
    midpoints = (log_edges[:-1]+log_edges[1:])/2
    trained = next(model for model in evaluated['ranking_by_stock_tv']
                   if model in {'empirical', 'bounded_pareto', 'bounded_weibull'})
    fig, axes = plt.subplots(2, 2, figsize=(12.4, 9.0))

    axis = axes[0, 0]
    for model in ('log_neutral', 'empirical', 'bounded_weibull', 'bounded_pareto'):
        plot_template(axis, midpoints, models, model, 'stock_shares')
    axis.plot(midpoints, evaluated['mean_observed_stock_shares'], 'o-', color=INK,
              linewidth=2.2, markersize=5.3, markeredgecolor=SURFACE,
              label=f'Realized census ({len(plots)} plots, equal weight)')
    axis.set_title('(a) Held-out mass shares and frozen templates', loc='left')
    axis.set(xlabel=r'$\log_{10}$ aboveground dry mass (g), bin midpoint', ylabel='Share of in-domain dry mass', ylim=(0, None))
    axis.grid(True, axis='y')
    axis.legend(fontsize=7.7, loc='best')
    axis.text(.02, .98, 'Templates normalize expected stocks; points normalize each realized census.',
              transform=axis.transAxes, va='top', fontsize=7.2, color=SECONDARY)

    axis = axes[0, 1]
    mean_counts = np.mean([observed[plot]['count_shares'] for plot in plots], axis=0)
    for model in ('log_neutral', 'linear_neutral', trained):
        plot_template(axis, midpoints, models, model, 'count_shares')
    axis.plot(midpoints, mean_counts, 'o-', color=INK, linewidth=2.2, markersize=5.3,
              markeredgecolor=SURFACE, label='Realized census, equal-plot mean')
    if np.all(mean_counts > 0) and np.max(mean_counts)/np.min(mean_counts) > 20:
        axis.set_yscale('log')
        axis.set_ylim(top=axis.get_ylim()[1]*1.8)
    else:
        axis.set_ylim(bottom=0)
    axis.set_title('(b) Held-out count shares', loc='left')
    axis.set(xlabel=r'$\log_{10}$ aboveground dry mass (g), bin midpoint', ylabel='Share of in-domain ramets')
    axis.grid(True, axis='y')
    axis.legend(fontsize=8, loc='best')
    axis.text(.02, .98, f'Trained curve shown: lowest retained mean stock TV ({MODEL_NAMES[trained]}).',
              transform=axis.transAxes, va='top', fontsize=7.2, color=SECONDARY)

    axis = axes[1, 0]
    order = ['log_neutral', 'linear_neutral', 'empirical', 'bounded_pareto', 'bounded_weibull']
    offsets = np.linspace(-.16, .16, len(plots)) if len(plots) > 1 else [0.]
    markers = ['o', 's', '^', 'D', 'v', 'P', 'X', '*']
    for j, plot in enumerate(plots):
        values = [evaluated['per_plot_scores'][plot][model]['stock_tv'] for model in order]
        axis.scatter(values, np.arange(len(order))+offsets[j], marker=markers[j % len(markers)],
                     s=38, c=[COLORS[model] for model in order], edgecolors=SURFACE, linewidths=.6)
    means = [evaluated['equal_plot_mean_scores'][model]['stock_tv'] for model in order]
    axis.plot(means, np.arange(len(order)), '|', color=INK, markersize=17, markeredgewidth=2.4)
    axis.set_yticks(np.arange(len(order)), [MODEL_NAMES[model] for model in order])
    axis.invert_yaxis()
    axis.set(xlim=(0, 1), xlabel='Dry-mass total variation (lower is better)')
    axis.grid(True, axis='x')
    axis.set_title('(c) Retained scores for complete held-out plots', loc='left')
    handles = [Line2D([], [], marker=markers[j % len(markers)], linestyle='none', color=SECONDARY,
                      markersize=5.5, label=plot) for j, plot in enumerate(plots)]
    handles.append(Line2D([], [], marker='|', linestyle='none', color=INK, markersize=12,
                          markeredgewidth=2, label='Equal-plot mean'))
    fig.legend(handles=handles, fontsize=7.8, loc='lower center',
               bbox_to_anchor=(.5, .042), ncol=len(handles))

    axis = axes[1, 1]
    synthetic = calibration['calibration']
    simulated_edges = np.log10(synthetic['bin_edges_g'])
    simulated_x = (simulated_edges[:-1]+simulated_edges[1:])/2
    axis.plot(simulated_x, synthetic['log_neutral_expected_stock_template'], '--', color=SECONDARY,
              linewidth=1.5, label='Normalized expected stocks (continuous law)')
    for n, color in ((160, '#2a78d6'), (1280, '#eb6834')):
        condition = next(item for item in synthetic['conditions']
                         if item['exponent'] == 2. and item['block_size'] == 1 and item['n'] == n)
        axis.plot(simulated_x, condition['summary']['mean_normalized_census_stock_shares'], 'o-',
                  color=color, linewidth=1.6, markersize=4.5,
                  label=f'Mean normalized realized census, N = {n}')
    axis.set_title('(d) Synthetic finite-census normalization', loc='left')
    axis.set(xlabel=r'$\log_{10}$ recorded dry mass (g), bin midpoint', ylabel='Dry-mass share', ylim=(0, None))
    axis.set_ylim(0, axis.get_ylim()[1]*1.25)
    axis.grid(True, axis='y')
    axis.legend(fontsize=7.5, loc='best')
    axis.text(.02, .98, r'IID draws, count density $\propto m^{-2}$; 0.001 g rounding.'+'\n'
              'The two targets differ even under the specified marginal law.',
              transform=axis.transAxes, va='top', fontsize=7.3, color=SECONDARY)

    fig.suptitle('Measured plant dry mass: retrospective profile transfer and census calibration',
                 x=.02, ha='left', fontsize=12.5, color=INK)
    fig.text(.02, .012, 'Empirical panels condition on the frozen mass domain and recorded ramets. '
             'Synthetic diagnostics do not determine ecological neutrality.', fontsize=8, color=SECONDARY)
    fig.tight_layout(rect=(0, .095, 1, .96), h_pad=2.1, w_pad=2.7)
    save(fig)
    plt.close(fig)


def main():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    study, frozen, calibration = inputs()
    style(plt)
    figure(study, frozen, calibration, plt)
    manifest = dict(run_id=study['run_id'],
                    scope='Post-hoc visualization of retained outputs; no fits, scores, simulations or decisions recomputed',
                    source=ref(Path(__file__)),
                    inputs=[ref(RESULTS / 'output-manifest.json'), ref(RESULTS / 'study.json'),
                            study['frozen_forecasts'], frozen['calibration_reference']],
                    presentation_aggregation='Arithmetic mean of retained per-plot count shares; observed stock mean and all scores retained',
                    artifacts=[ref(RESULTS / name) for name in ARTIFACT_NAMES])
    write_exact(REPORT_MANIFEST, (json.dumps(manifest, indent=2, sort_keys=True, allow_nan=False)+'\n').encode())
    print(json.dumps(dict(status='complete', artifacts=len(manifest['artifacts']), manifest=ref(REPORT_MANIFEST))))


if __name__ == '__main__':
    main()
