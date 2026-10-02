"""Finite-group resource-response forecasts without outcome-derived budgets.

All functions are independent of dataset paths.  A resource density is a
separately calibrated stock per cell volume, not an uptake or supply rate.
Missing observations stay missing, zero groups stay zero, and time points are
never substituted for independent experimental units.
"""
from __future__ import annotations

import numpy as np


def _nonnegative_array(values, name):
    result = np.asarray(values, dtype=float)
    if np.any(np.isinf(result)) or np.any(result[np.isfinite(result)] < 0):
        raise ValueError(f'{name} requires nonnegative observations; NaN denotes missing')
    return result


def _probability_vector(values, name):
    result = np.asarray(values, dtype=float)
    if (result.ndim != 1 or not result.size or not np.all(np.isfinite(result))
            or np.any(result < 0) or not np.isclose(np.sum(result), 1., rtol=0., atol=1e-12)):
        raise ValueError(f'{name} must be a finite nonnegative probability vector')
    return result


def resource_profile(volumes, resource_density):
    """Translate group biovolumes to resource stocks and complete compositions.

The last axis indexes groups.  Any missing group makes its entire resource
composition unavailable.  Complete all-zero rows have an observed total of zero
but an undefined composition, without inserting pseudocounts.
"""
    volume = _nonnegative_array(volumes, 'Biovolumes')
    rho = np.asarray(resource_density, dtype=float)
    if (volume.ndim not in (1, 2) or rho.ndim != 1 or not rho.size
            or volume.shape[-1] != rho.size or not np.all(np.isfinite(rho))
            or np.any(rho <= 0)):
        raise ValueError('One positive finite resource density is required per group')
    stock = volume*rho
    total = np.sum(stock, axis=-1)
    valid = np.all(np.isfinite(stock), axis=-1) & (total > 0)
    shares = np.full(stock.shape, np.nan)
    np.divide(stock, np.expand_dims(total, -1), out=shares,
              where=np.expand_dims(valid, -1))
    return dict(stocks=stock, total=total, shares=shares, valid=valid)


def pooled_profile_envelope(volumes, resource_density, pooled_index, pooled_bounds):
    """Exact coordinate bounds for one unresolved two-species pooled group.

An unknown mixture has density between its constituent densities, weighted by
their unobserved biovolumes.  The normalized pooled share increases with that
density, and every other share decreases.  The coordinate bounds can therefore
be obtained exactly at the two endpoints; their coordinates need not jointly
form one feasible probability vector.  These are sensitivity bounds conditional
on the supplied densities, not confidence intervals for trait transfer.
"""
    rho = np.asarray(resource_density, dtype=float)
    bounds = np.asarray(pooled_bounds, dtype=float)
    if (rho.ndim != 1 or not isinstance(pooled_index, (int, np.integer))
            or not 0 <= pooled_index < len(rho) or bounds.shape != (2,)
            or not np.all(np.isfinite(bounds)) or not 0 < bounds[0] <= bounds[1]):
        raise ValueError('A pooled group and ordered positive density bounds are required')
    endpoint_profiles = []
    for density in bounds:
        current = rho.copy()
        current[pooled_index] = density
        endpoint_profiles.append(resource_profile(volumes, current))
    endpoint_shares = np.asarray([row['shares'] for row in endpoint_profiles])
    return dict(lower=np.min(endpoint_shares, axis=0),
                upper=np.max(endpoint_shares, axis=0),
                endpoint_shares=endpoint_shares,
                total_lower=np.minimum(endpoint_profiles[0]['total'], endpoint_profiles[1]['total']),
                total_upper=np.maximum(endpoint_profiles[0]['total'], endpoint_profiles[1]['total']),
                valid=endpoint_profiles[0]['valid'] & endpoint_profiles[1]['valid'])


def profile_tv_envelope(predicted_shares, volumes, resource_density, pooled_index, pooled_bounds):
    """Exact TV range against a fixed forecast over the pooled-density interval.

The feasible observed profiles form a line segment in the probability simplex.
Maximum TV is attained at an endpoint.  Minimum TV can occur inside the
interval, so checking only the endpoint scores is incorrect.
"""
    prediction = _probability_vector(predicted_shares, 'Forecast')
    envelope = pooled_profile_envelope(volumes, resource_density, pooled_index, pooled_bounds)
    endpoints = envelope['endpoint_shares']
    if endpoints.shape != (2, len(prediction)) or not np.all(envelope['valid']):
        raise ValueError('TV sensitivity requires one complete positive-total observed row')
    first, last = endpoints
    direction = last-first
    candidates = [0., 1.]
    for actual, change, forecast in zip(first, direction, prediction):
        if change != 0:
            position = (forecast-actual)/change
            if 0 < position < 1:
                candidates.append(float(position))
    scores = [.5*float(np.sum(np.abs(first+position*direction-prediction)))
              for position in candidates]
    return dict(lower=min(scores), upper=max(scores),
                endpoint_scores=[scores[0], scores[1]],
                minimum_segment_position=candidates[int(np.argmin(scores))])


def simplex_projection(values):
    """Euclidean projection onto the probability simplex, with no pseudocounts."""
    value = np.asarray(values, dtype=float)
    if value.ndim != 1 or not value.size or not np.all(np.isfinite(value)):
        raise ValueError('A finite nonempty vector is required')
    ordered = np.sort(value)[::-1]
    cumulative = np.cumsum(ordered)-1.
    eligible = ordered-cumulative/np.arange(1, len(value)+1) > 0
    last = np.flatnonzero(eligible)[-1]
    threshold = cumulative[last]/(last+1)
    return np.maximum(value-threshold, 0.)


def baseline_anchored_forecast(baseline_shares, mean_share_change):
    """Apply a development-only additive change to a declared initial state.

Projection handles an extrapolated negative share explicitly.  It may permit
emergence from an initial zero if separate development units forecast it; no
division by initial group abundance is needed.  The projection distance should
be retained as an extrapolation diagnostic.
"""
    baseline = _probability_vector(baseline_shares, 'Initial composition')
    change = np.asarray(mean_share_change, dtype=float)
    if (change.shape != baseline.shape or not np.all(np.isfinite(change))
            or not np.isclose(np.sum(change), 0., rtol=0., atol=1e-12)):
        raise ValueError('A finite zero-sum change is required per group')
    raw = baseline+change
    shares = simplex_projection(raw)
    return dict(shares=shares, unprojected=raw,
                projection_distance=float(np.linalg.norm(shares-raw)))


def stock_forecast(baseline_volumes, resource_density, mean_share_change, total_factor):
    """Combine a share-change forecast with a separately learned total factor.

The total factor is an equal-unit training mean, supplied by the caller.  A
nonpositive or unavailable total factor cannot supply a normalized stock
forecast and is rejected, rather than silently clipped.
"""
    initial = resource_profile(baseline_volumes, resource_density)
    if initial['stocks'].ndim != 1 or not initial['valid']:
        raise ValueError('A complete initial state with positive resource total is required')
    if not np.isfinite(total_factor) or total_factor <= 0:
        raise ValueError('A positive finite resource-total factor is required')
    prediction = baseline_anchored_forecast(initial['shares'], mean_share_change)
    total = float(initial['total']*total_factor)
    if not np.isfinite(total):
        raise ValueError('The predicted resource total must remain finite')
    return dict(prediction, total=total, stocks=prediction['shares']*total,
                baseline_total=float(initial['total']), total_factor=float(total_factor),
                valid_total=True)


def fractional_trajectory(times, volumes, resource_density, baseline_volumes):
    """Resource-share change and total-stock factor relative to an initial state."""
    time = np.asarray(times, dtype=float)
    volume = np.asarray(volumes, dtype=float)
    if (time.ndim != 1 or volume.ndim != 2 or len(time) != len(volume)
            or not np.all(np.isfinite(time)) or np.any(np.diff(time) <= 0)):
        raise ValueError('Strictly ordered finite times and one biovolume row per time are required')
    initial = resource_profile(baseline_volumes, resource_density)
    if initial['stocks'].ndim != 1 or not initial['valid']:
        raise ValueError('The initial resource composition must be complete with positive total')
    profile = resource_profile(volume, resource_density)
    return dict(times=time, share_change=profile['shares']-initial['shares'],
                total_factor=profile['total']/initial['total'],
                baseline_shares=initial['shares'], baseline_total=float(initial['total']),
                valid=profile['valid'])


def interpolate_trajectory(times, values, targets):
    """Linear interpolation without extrapolation or bridging missing samples.

Exact observations retain their missing values.  An interpolated coordinate is
available only if both immediately neighboring observations are finite.
"""
    time = np.asarray(times, dtype=float)
    value = np.asarray(values, dtype=float)
    target = np.asarray(targets, dtype=float)
    if (time.ndim != 1 or not time.size or value.ndim not in (1, 2)
            or len(value) != len(time) or target.ndim != 1
            or not np.all(np.isfinite(time)) or not np.all(np.isfinite(target))
            or np.any(np.diff(time) <= 0) or np.any(np.isinf(value))):
        raise ValueError('Ordered observed times and finite targets are required; NaN denotes missing')
    output = np.full((len(target),)+value.shape[1:], np.nan)
    for i, point in enumerate(target):
        right = int(np.searchsorted(time, point, side='left'))
        if right < len(time) and time[right] == point:
            output[i] = value[right]
        elif 0 < right < len(time):
            left = right-1
            fraction = (point-time[left])/(time[right]-time[left])
            available = np.isfinite(value[left]) & np.isfinite(value[right])
            output[i] = np.where(available, value[left]+fraction*(value[right]-value[left]), np.nan)
    return output


def mean_unit_trajectory(unit_trajectories, targets):
    """Average complete interpolated rows equally across distinct units.

Input mappings require unit_id, times, and values.  Duplicate unit identifiers
are rejected rather than treating repeated rows as extra replicates.  The
returned contributor count describes support, not independent time-point n.
"""
    units = list(unit_trajectories)
    if not units or len({row['unit_id'] for row in units}) != len(units):
        raise ValueError('At least one trajectory per distinct experimental unit is required')
    interpolated = np.asarray([interpolate_trajectory(row['times'], row['values'], targets)
                               for row in units])
    if interpolated.ndim != 3:
        raise ValueError('A vector of group responses is required at each time')
    complete = np.all(np.isfinite(interpolated), axis=-1)
    contributors = np.sum(complete, axis=0)
    sums = np.sum(np.where(complete[..., None], interpolated, 0.), axis=0)
    mean = np.full(sums.shape, np.nan)
    np.divide(sums, contributors[:, None], out=mean, where=contributors[:, None] > 0)
    return dict(mean=mean, contributors=contributors,
                unit_ids=[row['unit_id'] for row in units])


def whole_unit_partition(unit_metadata, development_category, validation_category, category_key='category'):
    """Freeze a metadata-only partition; unsupported categories are explicit."""
    if development_category == validation_category:
        raise ValueError('Development and validation categories must differ')
    development, validation, unsupported = [], [], []
    seen = set()
    for row in unit_metadata:
        unit = row['unit_id']
        if unit in seen:
            raise ValueError('Duplicate experimental-unit metadata')
        seen.add(unit)
        category = row[category_key]
        target = (development if category == development_category else
                  validation if category == validation_category else unsupported)
        target.append(unit)
    if not development or not validation:
        raise ValueError('Both declared categories need experimental units')
    return dict(development=sorted(development), validation=sorted(validation),
                unsupported=sorted(unsupported))


def trajectory_scores(times, predicted_shares, observed_shares):
    """Score one independent unit, keeping missing intervals out of exposure.

Time-weighted TV integrates only adjacent valid observation pairs; an invalid
row breaks continuity.  A lone valid observation supplies point scores but no
time-integrated score.  These descriptive errors are not confidence intervals.
"""
    time = np.asarray(times, dtype=float)
    predicted = _nonnegative_array(predicted_shares, 'Predicted shares')
    observed = _nonnegative_array(observed_shares, 'Observed shares')
    if (time.ndim != 1 or predicted.ndim != 2 or predicted.shape != observed.shape
            or len(time) != len(predicted) or not np.all(np.isfinite(time))
            or np.any(np.diff(time) <= 0) or np.any(np.isinf(predicted)) or np.any(np.isinf(observed))):
        raise ValueError('Matched group compositions at strictly ordered times are required')
    valid = np.all(np.isfinite(predicted), axis=1) & np.all(np.isfinite(observed), axis=1)
    for row in np.concatenate([predicted[valid], observed[valid]]):
        _probability_vector(row, 'Complete scored composition')
    error = predicted-observed
    tv = np.full(len(time), np.nan)
    tv[valid] = .5*np.sum(np.abs(error[valid]), axis=1)
    adjacent = valid[:-1] & valid[1:]
    durations = np.diff(time)
    exposure = float(np.sum(durations[adjacent]))
    integrated = float(np.sum(.5*(tv[:-1][adjacent]+tv[1:][adjacent])*durations[adjacent]))
    return dict(total_variation=tv, valid=valid, scored_observations=int(np.sum(valid)),
                invalid_observations=int(np.sum(~valid)),
                covered_duration=exposure,
                time_weighted_total_variation=(integrated/exposure if exposure > 0 else None),
                maximum_absolute_share_error=(float(np.max(np.abs(error[valid]))) if np.any(valid) else None),
                signed_share_error=error)


def common_comparison_support(observed_shares, forecasts):
    """Return one paired scoring support for every declared comparator.

All models must be registered by the caller before constructing this support.
The function does not select models by their errors or fill unavailable rows.
"""
    observed = _nonnegative_array(observed_shares, 'Observed shares')
    if observed.ndim != 2 or not forecasts:
        raise ValueError('Observed composition rows and at least one forecast are required')
    support = np.all(np.isfinite(observed), axis=1)
    individual = {}
    for name, values in forecasts.items():
        prediction = _nonnegative_array(values, 'Predicted shares')
        if prediction.shape != observed.shape:
            raise ValueError('Every comparator must use the same observation rows and groups')
        valid = np.all(np.isfinite(prediction), axis=1)
        for row in prediction[valid]:
            _probability_vector(row, 'Complete forecast composition')
        individual[name] = valid
        support &= valid
    for row in observed[np.all(np.isfinite(observed), axis=1)]:
        _probability_vector(row, 'Complete observed composition')
    return dict(valid=support, individual_valid=individual,
                common_observations=int(np.sum(support)), excluded_observations=int(np.sum(~support)))


def recovery_endpoint(times, shares, baseline_shares, tolerance, minimum_time=0., consecutive=2):
    """Descriptive observed recovery to baseline after an observed departure.

Recovery requires the declared number of consecutive valid observations within
the TV margin after a preceding observed departure. Missing rows break a run.
The first confirming sequence's last observation is its observed confirmation
time, not an estimate of the unobserved continuous crossing time.  No observed
departure is distinguished from no observed recovery before right censoring.
This endpoint does not test neutrality against a logarithmic reference.
"""
    baseline = _probability_vector(baseline_shares, 'Initial composition')
    if (not np.isfinite(tolerance) or not 0 <= tolerance <= 1
            or not np.isfinite(minimum_time) or not isinstance(consecutive, (int, np.integer))
            or consecutive < 1):
        raise ValueError('A TV tolerance, finite start time and positive observation count are required')
    observed = np.asarray(shares, dtype=float)
    if observed.ndim != 2 or observed.shape[1] != len(baseline):
        raise ValueError('One group-composition vector is required per time')
    scores = trajectory_scores(times, np.broadcast_to(baseline, observed.shape), observed)
    time = np.asarray(times, dtype=float)
    departed, run = False, []
    last_observed = None
    for point, valid, distance in zip(time, scores['valid'], scores['total_variation']):
        if point < minimum_time:
            continue
        if not valid:
            run = []
            continue
        last_observed = float(point)
        if distance > tolerance:
            departed, run = True, []
        elif departed:
            run.append(float(point))
            if len(run) == consecutive:
                return dict(status='observed_baseline_recovery',
                            confirmation_time=run[-1], within_margin_from=run[0],
                            total_variation=scores['total_variation'])
    return dict(status=('recovery_right_censored' if departed else 'no_observed_departure'),
                confirmation_time=None, last_valid_time=last_observed,
                total_variation=scores['total_variation'])


def cost_ratio_forecast(baseline_shares, cost_ratios, strength):
    """Two-budget reweighting of a declared initial resource composition.

The orthopolic rule N_j = w_j/(lambda_1 q_1j + lambda_2 q_2j) gives primary
resource stocks w_j/(lambda_1 + lambda_2 r_j), with r_j = q_2j/q_1j.  If only
the primary budget binds initially, baseline shares are proportional to w_j,
and a binding secondary budget multiplies each share by 1/(1 + kappa r_j),
kappa = lambda_2/lambda_1, before renormalization.  kappa = 0 is persistence.
Measured cost ratios fix the direction of change; kappa is supplied separately
and is never fitted to the scored unit.
"""
    baseline = _probability_vector(baseline_shares, 'Initial composition')
    ratio = np.asarray(cost_ratios, dtype=float)
    if ratio.shape != baseline.shape or not np.all(np.isfinite(ratio)) or np.any(ratio <= 0):
        raise ValueError('One positive finite cost ratio is required per group')
    if not np.isfinite(strength) or strength < 0:
        raise ValueError('A finite nonnegative secondary-budget strength is required')
    weighted = baseline/(1.+strength*ratio)
    return weighted/np.sum(weighted)


def fit_cost_ratio_strength(baselines, observed, cost_ratios, strengths):
    """Choose the candidate strength minimizing equal-unit mean TV at one time.

Rows index distinct experimental units.  Units with an incomplete observed
composition are excluded.  The first minimizing candidate in increasing order
is chosen, so exact ties resolve to the smallest strength.
"""
    base = np.asarray(baselines, dtype=float)
    seen = np.asarray(observed, dtype=float)
    ratio = np.asarray(cost_ratios, dtype=float)
    candidates = np.asarray(strengths, dtype=float)
    if (base.ndim != 2 or seen.shape != base.shape or ratio.shape != base.shape[1:]
            or candidates.ndim != 1 or not candidates.size or not np.all(np.isfinite(candidates))
            or candidates[0] < 0 or np.any(np.diff(candidates) <= 0)
            or not np.all(np.isfinite(ratio)) or np.any(ratio <= 0)):
        raise ValueError('Matched unit compositions, positive ratios and increasing nonnegative strengths are required')
    complete = np.all(np.isfinite(seen), axis=1)
    if not np.any(complete):
        return dict(strength=None, units=0, mean_total_variation=None, persistence_total_variation=None)
    for row in np.concatenate([base[complete], seen[complete]]):
        _probability_vector(row, 'Complete fitted composition')
    weighted = base[complete][None, :, :]/(1.+candidates[:, None, None]*ratio[None, None, :])
    forecast = weighted/np.sum(weighted, axis=2, keepdims=True)
    objective = np.mean(.5*np.sum(np.abs(forecast-seen[complete][None, :, :]), axis=2), axis=1)
    best = int(np.argmin(objective))
    return dict(strength=float(candidates[best]), units=int(np.sum(complete)),
                mean_total_variation=float(objective[best]),
                persistence_total_variation=float(np.mean(.5*np.sum(np.abs(base[complete]-seen[complete]), axis=1))))


def time_weighted_mean(times, values):
    """Trapezoidal mean over adjacent pairs of non-missing values.

NaN marks a missing row and breaks continuity; -inf (an observed extinction in
a log growth factor) propagates.  Returns None without positive exposure.
"""
    time = np.asarray(times, dtype=float)
    value = np.asarray(values, dtype=float)
    if (time.ndim != 1 or value.shape != time.shape or not np.all(np.isfinite(time))
            or np.any(np.diff(time) <= 0) or np.any(value == np.inf)):
        raise ValueError('Strictly ordered times and one value per time are required')
    present = ~np.isnan(value)
    adjacent = present[:-1] & present[1:]
    durations = np.diff(time)[adjacent]
    exposure = float(np.sum(durations))
    if exposure <= 0:
        return None
    return float(np.sum(.5*(value[:-1][adjacent]+value[1:][adjacent])*durations)/exposure)


def log_share_growth(shares, baseline_shares):
    """Rowwise log(s_j(t)/s_j(baseline)); an absent group gives -inf.

Missing rows stay NaN.  Every group needs a positive baseline share, otherwise
its growth factor is undefined rather than infinite.
"""
    baseline = _probability_vector(baseline_shares, 'Initial composition')
    if np.any(baseline <= 0):
        raise ValueError('Every group needs a positive initial share')
    observed = _nonnegative_array(shares, 'Observed shares')
    if observed.ndim != 2 or observed.shape[1] != len(baseline):
        raise ValueError('One group-composition vector is required per time')
    with np.errstate(divide='ignore'):
        return np.log(observed/baseline)
