#!/usr/bin/env python3
"""Post-hoc diagnostics and figures for the evaluated Dunaliella size-budget study.

Reads only retained outputs whose digests the study recorded; no forecast,
score or verdict is recomputed or changed. The descriptive all-lineage fit
and treatment summaries were specified after the evaluation.
"""
from __future__ import annotations

import hashlib
import io
import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/dunaliella-size-budget/2026-10-02'
RESULTS = ROOT / 'results/dunaliella-size-budget'
TREATMENTS = {'S': 'Small-selected', 'C': 'Control', 'L': 'Large-selected'}
HISTORIES = ['Replete', 'N-Deplete', 'P-Deplete']
MODELS = {'constant_biovolume': 'Equal biovolume (d = 1)', 'assigned_carbon_cost': 'Assigned carbon exponent',
          'size_law': 'Fitted size law', 'assigned_nitrogen_cost': 'Assigned nitrogen exponent',
          'constant_cells': 'Equal cell number (d = 0)'}
# Reference palette (dataviz skill): categorical slots 1-3, validated all-pairs.
SERIES = {'S': '#2a78d6', 'C': '#eb6834', 'L': '#1baf7a'}
SURFACE, INK, SECONDARY, MUTED, GRID, AXIS = '#fcfcfb', '#0b0b0b', '#52514e', '#898781', '#e1e0d9', '#c3c2b7'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def ref(path):
    return dict(path=Path(path).relative_to(ROOT).as_posix(), sha256=digest(path))


def checked(reference):
    if digest(ROOT/reference['path']) != reference['sha256']:
        raise RuntimeError(f'Retained input changed: {reference["path"]}')
    return ROOT/reference['path']


def write_exact(path, content):
    path = Path(path)
    if path.exists() and path.read_bytes() != content:
        raise RuntimeError(f'Refusing to overwrite changed retained artifact: {path}')
    path.write_bytes(content)


def diagnostics(capacities, volumes):
    result = {}
    for outcome, values in capacities.items():
        summary = {}
        for history in HISTORIES:
            for code in TREATMENTS:
                keys = [key for key in values if key.startswith(code+'.') and key.endswith('|'+history)
                        and values[key] is not None and key in volumes]
                summary[f'{code}|{history}'] = dict(lineages=len(keys),
                                                    mean_log_k=float(np.mean([values[key] for key in keys])),
                                                    sd_log_k=float(np.std([values[key] for key in keys], ddof=1)),
                                                    mean_log_volume=float(np.mean([volumes[key] for key in keys])))
        keys = [key for key in values if key.endswith('|Replete') and key in volumes and values[key] is not None]
        slope, intercept = np.polyfit([volumes[key] for key in keys], [values[key] for key in keys], 1)
        small, large = summary['S|Replete'], summary['L|Replete']
        result[outcome] = dict(
            treatment_summaries=summary,
            all_lineage_replete_fit=dict(lineages=len(keys), slope=float(slope), intercept=float(intercept),
                                         implied_cost_dimension=float(1-slope)),
            large_over_small=dict(volume_ratio=math.exp(large['mean_log_volume']-small['mean_log_volume']),
                                  capacity_ratio=math.exp(large['mean_log_k']-small['mean_log_k']),
                                  cell_number_ratio=math.exp((large['mean_log_k']-large['mean_log_volume'])
                                                             - (small['mean_log_k']-small['mean_log_volume']))))
    return dict(scope='Post hoc: specified after the held-out evaluation; no forecast, score or verdict is changed',
                outcomes=result)


def style(plt):
    plt.rcParams.update({'font.family': 'sans-serif', 'font.sans-serif': ['Helvetica', 'Arial', 'DejaVu Sans'],
                         'font.size': 9, 'axes.edgecolor': AXIS, 'axes.labelcolor': SECONDARY, 'axes.titlecolor': INK,
                         'axes.titlesize': 9.5, 'axes.spines.top': False, 'axes.spines.right': False,
                         'axes.linewidth': .8, 'axes.facecolor': SURFACE, 'figure.facecolor': SURFACE,
                         'savefig.facecolor': SURFACE, 'xtick.color': MUTED, 'ytick.color': MUTED,
                         'xtick.labelcolor': SECONDARY, 'ytick.labelcolor': SECONDARY, 'grid.color': GRID,
                         'grid.linewidth': .6, 'grid.linestyle': '-', 'legend.frameon': False,
                         'svg.hashsalt': 'dunaliella-size-budget-2026-10-02'})


def save(figure, name):
    for extension in ('png', 'svg'):
        buffer = io.BytesIO()
        figure.savefig(buffer, format=extension, dpi=170, bbox_inches='tight',
                       metadata={'Date': None} if extension == 'svg' else {'Software': None})
        write_exact(RESULTS/f'{name}.{extension}', buffer.getvalue())


def dot(axis, x, y, code, size=7):
    axis.plot(x, y, linestyle='none', marker='o', markersize=size, color=SERIES[code],
              markeredgecolor=SURFACE, markeredgewidth=1.1)


def figure(study, frozen, capacities, posthoc, plt):
    from matplotlib.lines import Line2D
    volumes = frozen['size_log_volumes']
    values = capacities['biovolume']
    figure, axes = plt.subplots(2, 2, figsize=(12, 8.8))
    axis = axes[0, 0]
    grid = np.linspace(math.log(60), math.log(1500), 50)
    for fold, label in (('A', 'fold A fit (Small + Control)'), ('B', 'fold B fit (Control + Large)')):
        p = frozen['forecasts']['biovolume'][fold]['size_law']['parameters']['size_law']
        axis.plot(np.exp(grid), np.exp(p['intercept']+p['slope']*grid), color=MUTED, linewidth=1.4)
        axis.text(np.exp(grid[-1]), np.exp(p['intercept']+p['slope']*grid[-1]), f'  {label}, d = {p["implied_cost_dimension"]:.2f}',
                  fontsize=7.5, color=SECONDARY, va='center')
    level = np.mean([values[key] for key in values if key.endswith('|Replete') and values[key] is not None])
    axis.axhline(math.exp(level), color=AXIS, linewidth=1.)
    axis.text(1650, math.exp(level)*1.03, ' equal biovolume (d = 1)', fontsize=7.5, color=MUTED, va='bottom')
    for key, value in values.items():
        if key.endswith('|Replete') and key in volumes and value is not None:
            dot(axis, math.exp(volumes[key]), math.exp(value), key[0])
    axis.set(xscale='log', yscale='log', xlim=(60, 6000), ylim=(6e4, 4e5),
             xlabel='Mean cell volume (µm³, microscopy)', ylabel='Carrying capacity, total biovolume (µm³ per µL)')
    axis.grid(True, which='major')
    axis.set_title('(a) Replete carrying capacity is flat across a 10-fold size range', loc='left')
    axis.legend(handles=[Line2D([], [], linestyle='none', marker='o', markersize=7, color=SERIES[code],
                                markeredgecolor=SURFACE, label=name) for code, name in TREATMENTS.items()],
                loc='upper left', fontsize=8, labelcolor=SECONDARY)
    axis = axes[0, 1]
    for key, value in values.items():
        if key.endswith('|Replete') and key in volumes and value is not None:
            dot(axis, math.exp(volumes[key]), math.exp(value-volumes[key]), key[0])
    fit = posthoc['outcomes']['biovolume']['all_lineage_replete_fit']
    axis.plot(np.exp(grid), np.exp(fit['intercept']+(fit['slope']-1)*grid), color=AXIS, linewidth=1.)
    ratio = posthoc['outcomes']['biovolume']['large_over_small']
    axis.text(.03, .1, f'Large lineages: {ratio["volume_ratio"]:.1f}x the volume, {ratio["cell_number_ratio"]:.3f}x the cells',
              transform=axis.transAxes, fontsize=8, color=SECONDARY)
    axis.text(.03, .04, f'Line: post-hoc fit across all 30 lineages, slope {fit["slope"]-1:.2f}',
              transform=axis.transAxes, fontsize=7.5, color=MUTED)
    axis.set(xscale='log', yscale='log', xlabel='Mean cell volume (µm³)', ylabel='Implied cells at carrying capacity (per µL)')
    axis.grid(True, which='major')
    axis.set_title('(b) Cell number at capacity scales as 1/volume', loc='left')
    axis = axes[1, 0]
    order = list(MODELS)
    folds = study['evaluation']['biovolume']['folds']
    width = .36
    for offset, (fold, code, label) in zip((-width/2, width/2), (('A', 'L', 'Large held out (fold A)'),
                                                                 ('B', 'S', 'Small held out (fold B)'))):
        errors = [folds[fold]['E1']['mean_absolute_log_error'][model] for model in order]
        axis.barh(np.arange(len(order))+offset, errors, height=width*.9, color=SERIES[code], label=label)
        for position, error in enumerate(errors):
            axis.text(error+.03, position+offset, f'{error:.2f}', va='center', fontsize=7.5, color=INK)
    axis.set_yticks(range(len(order)), [MODELS[model] for model in order])
    axis.invert_yaxis()
    axis.set_xlim(0, 2.45)
    axis.grid(True, axis='x')
    axis.set_xlabel('Held-out mean absolute log error (lower is better)')
    axis.set_title('(c) Frozen size-law forecasts for the held-out treatment', loc='left')
    axis.legend(loc='upper right', fontsize=8, labelcolor=SECONDARY)
    axis = axes[1, 1]
    markers = {'N-Deplete': 'o', 'P-Deplete': 's'}
    axis.plot([11.2, 12.7], [11.2, 12.7], color=AXIS, linewidth=1.)
    axis.text(12.42, 12.36, 'full restoration', fontsize=7.5, color=MUTED, rotation=45, ha='center')
    for key, value in values.items():
        lineage, history = key.split('|')
        if history in markers and value is not None and values.get(f'{lineage}|Replete') is not None:
            axis.plot(values[f'{lineage}|Replete'], value, linestyle='none', marker=markers[history], markersize=6.5,
                      color=SERIES[lineage[0]], markeredgecolor=SURFACE, markeredgewidth=1.)
    axis.set(xlim=(11.2, 12.7), ylim=(11.2, 12.7), xlabel='Replete carrying capacity (log µm³ per µL)',
             ylabel='Capacity after deprivation (log µm³ per µL)')
    axis.set_aspect('equal')
    axis.grid(True)
    axis.set_title('(d) Regrowth after N or P deprivation (12 days, same medium)', loc='left')
    axis.legend(handles=[Line2D([], [], linestyle='none', marker=marker, markersize=6.5, color=MUTED,
                                markeredgecolor=SURFACE, label=f'after {history}') for history, marker in markers.items()],
                loc='lower right', fontsize=8, labelcolor=SECONDARY)
    figure.suptitle('Dunaliella size-selected lineages in one shared medium: frozen budget-law forecasts', x=.01, ha='left',
                    color=INK, fontsize=12)
    figure.tight_layout()
    save(figure, 'size-budget')
    plt.close(figure)


def main():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    style(plt)
    study = json.loads((RESULTS/'study.json').read_text())
    frozen = json.loads(checked(study['frozen_forecasts']).read_text())
    capacities = json.loads(checked(study['capacities_reference']).read_text())
    posthoc = diagnostics(capacities, frozen['size_log_volumes'])
    write_exact(RESULTS/'posthoc-diagnostics.json',
                (json.dumps(posthoc, indent=2, sort_keys=True, allow_nan=False)+'\n').encode())
    figure(study, frozen, capacities, posthoc, plt)
    manifest = dict(run_id=study['run_id'], scope=posthoc['scope'], source=ref(Path(__file__)),
                    inputs=[ref(RESULTS/'study.json'), study['frozen_forecasts'], study['capacities_reference']],
                    artifacts=[ref(RESULTS/name) for name in ('posthoc-diagnostics.json', 'size-budget.png', 'size-budget.svg')])
    write_exact(RESULTS/'report-manifest.json', (json.dumps(manifest, indent=2, sort_keys=True)+'\n').encode())
    print(json.dumps(dict(status='complete', artifacts=len(manifest['artifacts']))))


if __name__ == '__main__':
    main()
