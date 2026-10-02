#!/usr/bin/env python3
"""Post-hoc diagnostics and figures for the evaluated chemostat response study.

Reads only retained outputs whose digests the frozen study recorded; it never
refits a forecast or changes a score. The diagnostics were specified after the
held-out evaluation and are labelled post hoc:
  - pre-pulse composition variability (a noise floor for the scores);
  - the nitrogen-budget diagnostic in corrected units (the frozen field name
    says umol/L, but pmol/um3 x um3/mL is nmol/L);
  - a per-vessel summary table.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from orthopolity.chemostat_response import resource_profile  # noqa: E402

DATA = ROOT / 'data/chemostat-response/2026-10-02'
RESULTS = ROOT / 'results/chemostat-response'
NOMINAL = 'nitrogen-midpoint'
GROUPS = ['Cryptomonas', 'Chlamydomonas', 'Monoraphidium + Chlorella']
MODELS = {'development_mean_response': 'Development response', 'persistence': 'Persistence',
          'two_budget_cost_ratio': 'Two-budget cost ratio', 'equal_group_stock': 'Equal group stock',
          'preliminary_no_herbivore': 'No-herbivore response'}
WINDOW_DAYS = 6.
INFLOW_NITROGEN_UMOL_PER_L = 80.
# Reference palette (dataviz skill): categorical slots 1-3, validated all-pairs.
SERIES = ['#2a78d6', '#eb6834', '#1baf7a']
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


def inputs():
    study = json.loads((RESULTS/'study.json').read_text())
    frozen = json.loads(checked(study['frozen_forecasts']).read_text())
    records = json.loads(checked(frozen['development_records_reference']).read_text())
    held = json.loads(checked(study['evaluation_records_reference']).read_text())
    return study, frozen, records, held


def prepulse_variability(records, densities):
    """Composition variability before the pulse, from rows decoded at the freeze."""
    vessels = {}
    for row in records['main']:
        vessels.setdefault((row['category'], row['chemostat']), []).append(row)
    result = {}
    for (category, vessel), rows in sorted(vessels.items()):
        rows = sorted((row for row in rows if -WINDOW_DAYS <= row['time'] <= 0
                       and all(value is not None for value in row['biovolumes'])), key=lambda row: row['time'])
        if len(rows) < 2 or rows[-1]['time'] != 0:
            continue
        shares = resource_profile(np.array([row['biovolumes'] for row in rows]), densities)['shares']
        consecutive = .5*np.sum(np.abs(np.diff(shares, axis=0)), axis=1)
        from_baseline = .5*np.sum(np.abs(shares[:-1]-shares[-1]), axis=1)
        result[vessel] = dict(category=category, samples=len(rows),
                              mean_consecutive_total_variation=float(np.mean(consecutive)),
                              mean_total_variation_from_day0=float(np.mean(from_baseline)))
    return result


def diagnostics(study, frozen, records):
    variants = {row['variant_id']: row for row in frozen['computation']['variants']}
    evaluated = {row['variant_id']: row for row in study['evaluation']['variants']}
    nominal, scored = variants[NOMINAL], evaluated[NOMINAL]
    floors = {}
    for variant in (NOMINAL, 'biovolume-reference'):
        per_vessel = prepulse_variability(records, np.array(variants[variant]['densities']))
        summary = {}
        for category in ('Monocultures', 'Polycultures'):
            rows = [row for row in per_vessel.values() if row['category'] == category]
            summary[category] = dict(vessels=len(rows),
                                     mean_consecutive_total_variation=float(np.mean([row['mean_consecutive_total_variation'] for row in rows])),
                                     mean_total_variation_from_day0=float(np.mean([row['mean_total_variation_from_day0'] for row in rows])))
        floors[variant] = dict(summary=summary, vessels=per_vessel)
    budget = {}
    for scenario in ('lower', 'midpoint', 'upper'):
        values = {vessel: value/1000. for vessel, value in variants[f'nitrogen-{scenario}']['baseline_algal_nitrogen_umol_per_l'].items()}
        budget[scenario] = dict(micromol_per_l=values, maximum=max(values.values()),
                                vessels_above_inflow=sorted(vessel for vessel, value in values.items()
                                                            if value > INFLOW_NITROGEN_UMOL_PER_L))
    table = []
    for vessel in sorted(scored['vessels'], key=int):
        row, forecast = scored['vessels'][vessel], nominal['forecasts'][vessel]
        table.append(dict(vessel=vessel, treatment=next(item['treatment'] for item in records['main'] if item['chemostat'] == vessel),
                          baseline_shares=forecast['baseline_shares'],
                          maximum_departure_total_variation=row['observed']['maximum_departure_total_variation'],
                          two_budget_capacity_total_variation=forecast['two_budget_capacity_total_variation'],
                          time_weighted_total_variation={model: row['composition'][model]['time_weighted_total_variation'] for model in MODELS},
                          lowest_growth_group=GROUPS[row['observed']['ordinal']['lowest_growth_group']],
                          observed_recovery=row['observed']['recovery']['status']))
    return dict(scope='Post hoc: specified after the held-out evaluation; no forecast, score or verdict is changed',
                prepulse_window_days=[-WINDOW_DAYS, 0.],
                prepulse_variability=floors,
                nitrogen_budget=dict(units_erratum='The frozen field baseline_algal_nitrogen_umol_per_l holds nmol/L (pmol per um3 times um3 per mL); values here are divided by 1000',
                                     inflow_micromol_per_l=INFLOW_NITROGEN_UMOL_PER_L, scenarios=budget),
                heldout_table=table)


def style(plt):
    plt.rcParams.update({'font.family': 'sans-serif', 'font.sans-serif': ['Helvetica', 'Arial', 'DejaVu Sans'],
                         'font.size': 9, 'axes.edgecolor': AXIS, 'axes.labelcolor': SECONDARY,
                         'axes.titlecolor': INK, 'axes.titlesize': 9.5, 'axes.spines.top': False,
                         'axes.spines.right': False, 'axes.linewidth': .8, 'axes.facecolor': SURFACE,
                         'figure.facecolor': SURFACE, 'savefig.facecolor': SURFACE, 'xtick.color': MUTED,
                         'ytick.color': MUTED, 'xtick.labelcolor': SECONDARY, 'ytick.labelcolor': SECONDARY,
                         'grid.color': GRID, 'grid.linewidth': .6, 'grid.linestyle': '-',
                         'legend.frameon': False, 'svg.hashsalt': 'chemostat-resource-response-2026-10-02'})


def save(figure, name):
    import io
    for extension in ('png', 'svg'):
        buffer = io.BytesIO()
        figure.savefig(buffer, format=extension, dpi=170, bbox_inches='tight',
                       metadata={'Date': None} if extension == 'svg' else {'Software': None})
        write_exact(RESULTS/f'{name}.{extension}', buffer.getvalue())


def trajectories(study, frozen, records, plt):
    from matplotlib.lines import Line2D
    nominal = {row['variant_id']: row for row in frozen['computation']['variants']}[NOMINAL]
    scored = {row['variant_id']: row for row in study['evaluation']['variants']}[NOMINAL]
    treatment = {row['chemostat']: row['treatment'] for row in records['main'] if row['chemostat'] in nominal['forecasts']}
    order = sorted(nominal['forecasts'], key=lambda vessel: (treatment[vessel] != '9d', int(vessel)))
    figure, axes = plt.subplots(3, 4, figsize=(12.5, 8.2), sharex=True, sharey=True)
    for axis, vessel in zip(axes.flat, order):
        forecast, row = nominal['forecasts'][vessel], scored['vessels'][vessel]
        times = np.array(forecast['times'])
        predicted = np.array(forecast['models']['development_mean_response']['shares'], dtype=float)
        observed = np.array([[np.nan if value is None else value for value in shares] for shares in row['observed_shares']])
        axis.grid(True, axis='y')
        for group, color in enumerate(SERIES):
            axis.plot(times, predicted[:, group], color=color, linewidth=2.2, alpha=.35, solid_capstyle='round')
            axis.plot(times, observed[:, group], color=color, linewidth=.9, alpha=.8)
            axis.plot(times, observed[:, group], linestyle='none', marker='o', markersize=5.2, color=color,
                      markeredgecolor=SURFACE, markeredgewidth=1.)
        persistence = row['composition']['persistence']['time_weighted_total_variation']
        development = row['composition']['development_mean_response']['time_weighted_total_variation']
        axis.set_title(f'Vessel {vessel} · pulse {treatment[vessel]} after inoculation', loc='left', pad=14)
        axis.text(0., 1.015, f'Time-weighted TV: development {development:.2f}, persistence {persistence:.2f}',
                  transform=axis.transAxes, fontsize=7.5, color=SECONDARY, va='bottom')
        axis.set_ylim(-.03, 1.03)
        axis.set_xlim(-.3, 12.3)
        axis.set_xticks([0, 3, 6, 9, 12])
        axis.set_yticks([0, .5, 1])
    for axis in axes[-1]:
        axis.set_xlabel('Days after the nitrogen pulse')
    for axis in axes[:, 0]:
        axis.set_ylabel('Share of algal nitrogen')
    handles = [Line2D([], [], color=color, marker='o', markersize=5.2, markeredgecolor=SURFACE, linewidth=.9,
                      label=name) for name, color in zip(GROUPS, SERIES)]
    handles += [Line2D([], [], color=MUTED, linestyle='none', marker='o', markersize=5.2, markeredgecolor=SURFACE,
                       label='Observed (held out)'),
                Line2D([], [], color=MUTED, linewidth=2.2, alpha=.5, label='Frozen development-response forecast')]
    figure.tight_layout(rect=(0, 0, 1, .9))
    figure.text(.01, .985, 'Held-out polyculture vessels: nitrogen-resource shares against the frozen development forecast',
                ha='left', va='top', color=INK, fontsize=11.5)
    figure.text(.01, .958, 'Nitrogen midpoint conversion. Forecasts frozen before any held-out post-pulse value was decoded.',
                ha='left', va='top', color=SECONDARY, fontsize=8.5)
    figure.legend(handles=handles, loc='upper left', ncol=5, bbox_to_anchor=(.005, .935), fontsize=8.5,
                  handlelength=2.2, labelcolor=SECONDARY)
    save(figure, 'heldout-trajectories')
    plt.close(figure)


def summary(study, frozen, posthoc, plt):
    nominal = {row['variant_id']: row for row in frozen['computation']['variants']}[NOMINAL]
    variants = {row['variant_id']: row for row in study['evaluation']['variants']}
    scored = variants[NOMINAL]
    figure, axes = plt.subplots(2, 2, figsize=(12, 8.6))
    axis = axes[0, 0]
    order = sorted(MODELS, key=lambda model: scored['primary'][model]['equal_vessel_mean_time_weighted_total_variation'])
    floor = posthoc['prepulse_variability'][NOMINAL]['summary']['Polycultures']
    for value, label, height in ((floor['mean_consecutive_total_variation'], 'between consecutive pre-pulse samples', len(order)-.35),
                                 (floor['mean_total_variation_from_day0'], 'pre-pulse days vs day 0', len(order)-.75)):
        axis.axvline(value, color=AXIS, linewidth=1.)
        axis.text(value+.003, height, f'{value:.2f} {label}', fontsize=7.5, color=SECONDARY, va='center')
    for position, model in enumerate(order):
        envelope = scored['pooled_envelope'][model]
        axis.plot([envelope['equal_vessel_mean_lower'], envelope['equal_vessel_mean_upper']], [position]*2,
                  color=SERIES[0], alpha=.25, linewidth=7, solid_capstyle='round')
        ends = [variants[f'nitrogen-{scenario}']['primary'][model]['equal_vessel_mean_time_weighted_total_variation']
                for scenario in ('lower', 'upper')]
        axis.plot(ends, [position]*2, linestyle='none', marker='|', markersize=9, color=SERIES[0], markeredgewidth=1.4)
        value = scored['primary'][model]['equal_vessel_mean_time_weighted_total_variation']
        axis.plot(value, position, marker='o', markersize=7, color=SERIES[0], markeredgecolor=SURFACE, markeredgewidth=1.2)
        axis.text(envelope['equal_vessel_mean_upper']+.006, position, f'{value:.3f}', va='center', fontsize=8, color=INK)
    axis.set_yticks(range(len(order)), [MODELS[model] for model in order])
    axis.set_ylim(-.6, len(order)-.3)
    axis.invert_yaxis()
    axis.set_xlim(.09, .37)
    axis.grid(True, axis='x')
    axis.set_xlabel('Equal-vessel mean time-weighted TV (lower is better)')
    axis.set_title('(a) Held-out resource-composition error, 12 vessels', loc='left')
    axis.text(0., -.2, 'Dot: midpoint conversion. Ticks: Monoraphidium/Chlorella endpoint reruns.\n'
                       'Band: exact range under any time-varying pooled mixture.',
              transform=axis.transAxes, fontsize=7.5, color=SECONDARY, va='top')
    axis = axes[0, 1]
    table = posthoc['heldout_table']
    persistence = [row['time_weighted_total_variation']['persistence'] for row in table]
    development = [row['time_weighted_total_variation']['development_mean_response'] for row in table]
    axis.plot([0, .45], [0, .45], color=AXIS, linewidth=1.)
    axis.plot(persistence, development, linestyle='none', marker='o', markersize=7, color=SERIES[0],
              markeredgecolor=SURFACE, markeredgewidth=1.2)
    below = sum(d < p for d, p in zip(development, persistence))
    axis.text(.03, .41, f'Development forecast lower in {below} of {len(table)} vessels', fontsize=8, color=SECONDARY)
    axis.text(.375, .4, 'equal error', fontsize=7.5, color=MUTED, rotation=45, ha='center', va='center')
    axis.set(xlim=(0, .45), ylim=(0, .45), xlabel='Persistence time-weighted TV', ylabel='Development-response time-weighted TV')
    axis.set_aspect('equal')
    axis.grid(True)
    axis.set_title('(b) Per-vessel error: development response vs persistence', loc='left')
    axis = axes[1, 0]
    capacity = [row['two_budget_capacity_total_variation'] for row in table]
    departure = [row['maximum_departure_total_variation'] for row in table]
    axis.plot([0, .6], [0, .6], color=AXIS, linewidth=1.)
    axis.plot(capacity, departure, linestyle='none', marker='o', markersize=7, color=SERIES[0],
              markeredgecolor=SURFACE, markeredgewidth=1.2)
    exceeded = sum(d > c for d, c in zip(departure, capacity))
    axis.text(.01, .56, f'Observed departure exceeds the rule\'s maximum in {exceeded} of {len(table)} vessels',
              fontsize=8, color=SECONDARY)
    axis.text(.2, .23, 'departure = maximum', fontsize=7.5, color=MUTED, rotation=45)
    axis.set(xlim=(0, .6), ylim=(0, .6), xlabel='Two-budget maximum attainable TV (frozen)',
             ylabel='Observed maximum TV from baseline')
    axis.set_aspect('equal')
    axis.grid(True)
    axis.set_title('(c) Redistribution the measured C:N ratios cannot produce', loc='left')
    axis = axes[1, 1]
    vessels = scored['vessels']
    order = sorted(vessels, key=int)
    ratios = nominal['cost_ratios']
    finite = [value for vessel in order for value in vessels[vessel]['observed']['time_weighted_log_share_growth']
              if value != '-inf']
    edge = min(finite)-.35
    for index, vessel in enumerate(order):
        growth = vessels[vessel]['observed']['time_weighted_log_share_growth']
        values = [edge if value == '-inf' else value for value in growth]
        axis.plot([min(values), max(values)], [index]*2, color=GRID, linewidth=1.)
        for value, raw, color in zip(values, growth, SERIES):
            axis.plot(value, index, marker='<' if raw == '-inf' else 'o', markersize=6.5, color=color,
                      markeredgecolor=SURFACE, markeredgewidth=1.)
        if int(np.argmin(values)) == int(np.argmax(ratios)):
            axis.text(max(values)+.08, index, 'satisfied', va='center', fontsize=7.5, color=SECONDARY)
    if any(value == '-inf' for vessel in order for value in vessels[vessel]['observed']['time_weighted_log_share_growth']):
        axis.text(edge, len(order)-.2, 'absent on some day (log share -inf)', fontsize=7, color=MUTED, va='top')
    axis.axvline(0, color=AXIS, linewidth=1.)
    axis.set_yticks(range(len(order)), [f'Vessel {vessel}' for vessel in order])
    axis.invert_yaxis()
    axis.grid(True, axis='x')
    axis.set_xlabel('Time-weighted mean log share growth, days 0-12')
    satisfied = scored['ordinal']
    axis.set_title(f'(d) Highest-C:N group lowest in {satisfied["satisfied"]} of {satisfied["scored"]} vessels (chance 4)', loc='left')
    from matplotlib.lines import Line2D
    axis.legend(handles=[Line2D([], [], linestyle='none', marker='o', markersize=6.5, color=color,
                                markeredgecolor=SURFACE, label=f'{name} (C:N {ratio:.1f})')
                         for name, color, ratio in zip(GROUPS, SERIES, ratios)],
                loc='lower left', fontsize=7.5, labelcolor=SECONDARY)
    figure.suptitle('Chemostat resource-response study: frozen forecasts on 12 held-out vessels', x=.01, ha='left',
                    color=INK, fontsize=12)
    figure.tight_layout()
    save(figure, 'scores')
    plt.close(figure)


def main():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    style(plt)
    study, frozen, records, held = inputs()
    posthoc = diagnostics(study, frozen, records)
    write_exact(RESULTS/'posthoc-diagnostics.json',
                (json.dumps(posthoc, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)+'\n').encode())
    trajectories(study, frozen, records, plt)
    summary(study, frozen, posthoc, plt)
    manifest = dict(run_id=study['run_id'], scope=posthoc['scope'],
                    inputs=[ref(RESULTS/'study.json'), study['frozen_forecasts'], study['evaluation_records_reference'],
                            frozen['development_records_reference']],
                    source=ref(Path(__file__)),
                    artifacts=[ref(RESULTS/name) for name in ('posthoc-diagnostics.json', 'heldout-trajectories.png',
                                                              'heldout-trajectories.svg', 'scores.png', 'scores.svg')])
    write_exact(RESULTS/'report-manifest.json', (json.dumps(manifest, indent=2, sort_keys=True)+'\n').encode())
    print(json.dumps(dict(status='complete', artifacts=len(manifest['artifacts']))))


if __name__ == '__main__':
    main()
