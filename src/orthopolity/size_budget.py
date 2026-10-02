"""Size-law and restoration forecasts for separately grown size-selected lineages.

Under one shared budget R, a lineage whose cells each cost q(V) = c V**d
reaches N = R/q(V) cells and total biovolume N V proportional to V**(1-d).
Every fit here receives development units only; held-out units contribute
predictors (cell volume) and, for anchored restoration models, a declared
observed input. All functions are independent of dataset paths.
"""
from __future__ import annotations

import math

import numpy as np


def carrying_capacity(wells, minimum_wells=2):
    """Maximum over days of the across-well mean log outcome.

    `wells` maps a well to {day: log value}; NaN marks a missing reading.
    Days with fewer than `minimum_wells` finite readings are skipped.
    Returns None when no day qualifies.
    """
    days = sorted({day for readings in wells.values() for day in readings})
    means = []
    for day in days:
        values = [readings[day] for readings in wells.values()
                  if day in readings and math.isfinite(readings[day])]
        if len(values) >= minimum_wells:
            means.append(float(np.mean(values)))
    return max(means) if means else None


def fit_line(x, y):
    """Ordinary least squares intercept and slope."""
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    if x.shape != y.shape or x.ndim != 1 or len(x) < 2 or not np.all(np.isfinite(x)) or not np.all(np.isfinite(y)):
        raise ValueError('Finite paired values for at least two units are required')
    if np.ptp(x) == 0:
        raise ValueError('The size coordinate must vary across development units')
    slope, intercept = np.polyfit(x, y, 1)
    return float(intercept), float(slope)


def size_law_forecasts(development, held_out, assigned_slopes):
    """E1 forecasts of log carrying capacity from log cell volume.

    `development` and `held_out` map unit ids to dicts with 'log_volume', and
    development units also carry 'log_k'. Held-out log K is never read.
    """
    keys = sorted(development)
    x = np.array([development[key]['log_volume'] for key in keys])
    y = np.array([development[key]['log_k'] for key in keys])
    intercept, slope = fit_line(x, y)
    parameters = {'size_law': (intercept, slope), 'constant_biovolume': (float(np.mean(y)), 0.),
                  'constant_cells': (float(np.mean(y-x)), 1.)}
    for name, assigned in sorted(assigned_slopes.items()):
        parameters[name] = (float(np.mean(y-assigned*x)), float(assigned))
    forecasts = {name: {key: a+b*held_out[key]['log_volume'] for key in sorted(held_out)}
                 for name, (a, b) in parameters.items()}
    return dict(parameters={name: dict(intercept=a, slope=b, implied_cost_dimension=1.-b)
                            for name, (a, b) in parameters.items()},
                forecasts=forecasts, development_units=keys)


def restoration_forecasts(development, held_out):
    """E2 forecasts of log K after deprivation, within one history.

    Development units carry 'log_k', 'replete_log_k' and 'log_volume'. Held-out
    units carry 'log_volume' and, optionally, 'replete_log_k' (a declared
    observed input); anchored forecasts exist only for units that supply it.
    """
    keys = sorted(development)
    deficit = float(np.mean([development[key]['log_k']-development[key]['replete_log_k'] for key in keys]))
    level = float(np.mean([development[key]['log_k'] for key in keys]))
    intercept, slope = fit_line([development[key]['log_volume'] for key in keys],
                                [development[key]['log_k'] for key in keys])
    anchored = {key: unit['replete_log_k'] for key, unit in sorted(held_out.items()) if 'replete_log_k' in unit}
    forecasts = {
        'full_restoration': dict(anchored),
        'history_offset': {key: value+deficit for key, value in anchored.items()},
        'size_law_history': {key: intercept+slope*unit['log_volume'] for key, unit in sorted(held_out.items())},
        'constant_history': {key: level for key in sorted(held_out)}}
    return dict(parameters=dict(development_mean_deficit=deficit, development_mean=level,
                                size_law_intercept=intercept, size_law_slope=slope,
                                implied_cost_dimension=1.-slope),
                forecasts=forecasts, development_units=keys)


def absolute_errors(forecasts, observed):
    """Per-unit absolute errors on the units every model and the observation share."""
    units = sorted(set(observed).intersection(*[set(values) for values in forecasts.values()]))
    units = [unit for unit in units if observed[unit] is not None and math.isfinite(observed[unit])]
    return {model: {unit: abs(values[unit]-observed[unit]) for unit in units}
            for model, values in forecasts.items()}, units


def pairwise_verdict(errors_by_fold, first, second, margin):
    """Descriptive verdict: both folds by the margin and a per-fold unit majority."""
    differences, majorities = [], []
    for errors in errors_by_fold:
        a, b = errors[first], errors[second]
        if set(a) != set(b) or not a:
            raise ValueError('Compared models must score the same nonempty units')
        differences.append(float(np.mean(list(b.values()))-np.mean(list(a.values()))))
        wins = sum(a[unit] < b[unit] for unit in a)
        losses = sum(b[unit] < a[unit] for unit in a)
        majorities.append((wins, losses, len(a)))
    if all(value >= margin for value in differences) and all(w > n/2 for w, _, n in majorities):
        verdict = f'{first} outperforms {second}'
    elif all(value <= -margin for value in differences) and all(l > n/2 for _, l, n in majorities):
        verdict = f'{second} outperforms {first}'
    else:
        verdict = 'not distinguished'
    return dict(pair=[first, second], improvement_by_fold=differences,
                first_lower_by_fold=[w for w, _, _ in majorities],
                second_lower_by_fold=[l for _, l, _ in majorities],
                scored_units_by_fold=[n for _, _, n in majorities], verdict=verdict)
