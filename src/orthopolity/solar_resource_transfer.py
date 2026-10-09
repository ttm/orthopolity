"""Fixed-bin fluence-cost prediction without an assumed power-law cost curve."""
import csv
from datetime import datetime
from pathlib import Path

import numpy as np


RESOURCES = ("integrated_irrad_peak", "integrated_irrad_end")
MODELS = ("log_resource_neutral", "linear_resource_neutral", "historical_count_shape")


def fixed_edges(config):
    lo, hi = config["peak_irradiance_domain_W_m2"]
    if lo <= 0 or hi <= lo:
        raise ValueError("The domain must be positive and increasing")
    span = np.log10(hi / lo)
    bins = int(round(span * config["bins_per_decade"]))
    if bins < 2 or not np.isclose(bins, span * config["bins_per_decade"]):
        raise ValueError("The domain must contain a whole number of fixed bins")
    return np.geomspace(lo, hi, bins + 1)


def pooled_edges(training_counts, edges, minimum):
    """Pool high bins downward by training support, never by validation outcomes."""
    counts = np.asarray(training_counts, int)
    if counts.ndim != 2 or counts.shape[1] != len(edges) - 1 or minimum < 1 or np.any(counts < 0):
        raise ValueError("Invalid calibration support")
    if np.any(counts.sum(axis=1) < minimum):
        raise ValueError("Insufficient training support for the declared resources")
    boundaries = [len(edges) - 1]
    accumulated = np.zeros(counts.shape[0], dtype=int)
    for j in range(counts.shape[1] - 1, -1, -1):
        accumulated += counts[:, j]
        if np.all(accumulated >= minimum):
            boundaries.append(j)
            accumulated[:] = 0
    if boundaries[-1] != 0:
        boundaries.pop()
        boundaries.append(0)
    result = np.asarray(edges)[sorted(boundaries)]
    if len(result) < 3:
        raise ValueError("Fewer than two supported classes remain")
    return result


def _number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("nan")


def _time(value):
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def catalogue(raw_directory, years, edges):
    """Load only named years; preserve raw row identities and every exclusion."""
    rows = []
    identifiers = set()
    for year in years:
        source = f"noaa_{year}.csv"
        with (Path(raw_directory) / source).open(newline="") as stream:
            for i, row in enumerate(csv.DictReader(stream)):
                flare_id = row["flare_id"]
                if flare_id in identifiers:
                    raise ValueError("Duplicate flare identifiers in the named years")
                identifiers.add(flare_id)
                peak_time = _time(row["time"])
                if peak_time is None or peak_time.year != year:
                    raise ValueError("The year/peak-time membership is inconsistent")
                start, end = _time(row["start_time"]), _time(row["end_time"])
                rise_duration = (peak_time - start).total_seconds() if start else float("nan")
                end_duration = (end - start).total_seconds() if start and end else float("nan")
                k = _number(row["xrsb_irrad"])
                if not np.isfinite(k) or k <= 0:
                    reason = "invalid_peak"
                elif _number(row["peak_saturated"]) != 0:
                    reason = "saturated_or_unknown"
                elif k < edges[0] or k > edges[-1]:
                    reason = "outside_fixed_domain"
                else:
                    reason = "selected_peak"
                index = min(int(np.searchsorted(edges, k, side="right") - 1), len(edges) - 2)
                record = dict(source_file=source, source_row_index=i, flare_id=flare_id,
                              year=year, month=peak_time.strftime("%Y-%m"), peak_selection=reason,
                              bin=index if reason == "selected_peak" else -1,
                              peak_irradiance_W_m2=k, rise_duration_s=rise_duration,
                              end_duration_s=end_duration)
                for resource, duration in zip(RESOURCES, (rise_duration, end_duration)):
                    q = _number(row[resource])
                    record[resource] = q
                    record[f"valid_{resource}"] = bool(np.isfinite(q) and q > 0 and duration > 0)
                rows.append(record)
    return rows


def membership(rows):
    keys = ("source_file", "source_row_index", "flare_id", "year", "month",
            "peak_selection", "bin", "valid_integrated_irrad_peak", "valid_integrated_irrad_end")
    return [{key: row[key] for key in keys} for row in rows]


def monthly_statistics(rows, resource, edges, years):
    """Keep zero and missing bins and all 12 calendar months, including empty months."""
    months = [f"{year}-{month:02d}" for year in years for month in range(1, 13)]
    month_index = {month: i for i, month in enumerate(months)}
    n = len(edges) - 1
    all_counts = np.zeros((len(months), n), dtype=int)
    counts = np.zeros_like(all_counts)
    sums = np.zeros((len(months), n), dtype=float)
    for row in rows:
        if row["bin"] < 0:
            continue
        i, j = month_index[row["month"]], row["bin"]
        all_counts[i, j] += 1
        if row[f"valid_{resource}"]:
            counts[i, j] += 1
            sums[i, j] += row[resource]
    return {"months": months, "years": list(years), "all_counts": all_counts,
            "counts": counts, "resource_sums": sums}


def aggregate(statistics, indices=None):
    index = np.arange(len(statistics["months"])) if indices is None else np.asarray(indices, int)
    count = statistics["counts"][index].sum(axis=0)
    resource = statistics["resource_sums"][index].sum(axis=0)
    mean = np.divide(resource, count, out=np.full(len(count), np.nan), where=count > 0)
    return {"all_counts": statistics["all_counts"][index].sum(axis=0),
            "counts": count, "resource_sums": resource, "mean_cost": mean}


def forecast(mean_cost, training_counts, edges):
    q = np.asarray(mean_cost, float)
    n = np.asarray(training_counts, float)
    if len(q) != len(edges) - 1 or n.shape != q.shape or np.any(~np.isfinite(q)) or np.any(q <= 0) or np.any(n <= 0):
        raise ValueError("Each fixed training bin needs a positive measured mean cost and count")
    log_widths = np.diff(np.log(edges))
    linear_widths = np.diff(edges)
    masses = {"log_resource_neutral": log_widths / q,
              "linear_resource_neutral": linear_widths / q,
              "historical_count_shape": n}
    return {name: {"count_share": (mass / mass.sum()).tolist(),
                   "resource_share": (mass * q / (mass * q).sum()).tolist()}
            for name, mass in masses.items()}


def score(forecasts, observed):
    n = np.asarray(observed["counts"], float)
    qsum = np.asarray(observed["resource_sums"], float)
    if n.sum() <= 0 or qsum.sum() <= 0:
        raise ValueError("The evaluation sample has no measured resource events")
    count_share = n / n.sum()
    resource_share = qsum / qsum.sum()
    scores = {}
    for name, prediction in forecasts.items():
        p = np.asarray(prediction["count_share"])
        r = np.asarray(prediction["resource_share"])
        if np.any(p <= 0) or p.shape != n.shape or r.shape != n.shape:
            raise ValueError("Invalid forecast probability")
        scores[name] = {
            "count_cross_entropy_nats_per_event": float(-np.dot(count_share, np.log(p))),
            "count_total_variation": float(np.abs(count_share - p).sum() / 2),
            "resource_share_total_variation": float(np.abs(resource_share - r).sum() / 2),
        }
    return scores


def stratified_month_indices(statistics, rng):
    return np.concatenate([12 * i + rng.integers(0, 12, size=12)
                           for i in range(len(statistics["years"]))])


def bootstrap(training, evaluation, edges, *, replicates, seed):
    """Pair held-out months across forecasts/resources; independently resample cost years."""
    rng = np.random.default_rng(seed)
    draws = {resource: [] for resource in training}
    profiles = {resource: {"count_share": [], "resource_share": [], "cost_ratio": []}
                for resource in training}
    invalid = {resource: 0 for resource in training}
    template_training = next(iter(training.values()))
    template_evaluation = next(iter(evaluation.values()))
    for replicate in range(replicates):
        ti = stratified_month_indices(template_training, rng)
        vi = stratified_month_indices(template_evaluation, rng)
        for resource in training:
            tr = aggregate(training[resource], ti)
            ev = aggregate(evaluation[resource], vi)
            try:
                prediction = forecast(tr["mean_cost"], tr["counts"], edges)
                scores = score(prediction, ev)
            except ValueError:
                invalid[resource] += 1
                continue
            record = {"replicate": replicate}
            for model in MODELS:
                for metric, value in scores[model].items():
                    record[f"{model}:{metric}"] = value
            for model in MODELS[1:]:
                record[f"{model}:cross_entropy_minus_log_neutral"] = (
                    scores[model]["count_cross_entropy_nats_per_event"]
                    - scores[MODELS[0]]["count_cross_entropy_nats_per_event"])
            draws[resource].append(record)
            profiles[resource]["count_share"].append(ev["counts"] / ev["counts"].sum())
            profiles[resource]["resource_share"].append(ev["resource_sums"] / ev["resource_sums"].sum())
            profiles[resource]["cost_ratio"].append(ev["mean_cost"] / tr["mean_cost"])
    return draws, profiles, invalid


def finite_interval(values):
    values = np.asarray(values, float)
    values = values[np.isfinite(values)]
    return np.quantile(values, [.025, .975]).tolist() if len(values) else [None, None]


def profile_rows(training, evaluation, predictions, edges, draws):
    tr = aggregate(training)
    ev = aggregate(evaluation)
    rows = []
    for j in range(len(edges) - 1):
        row = dict(left_W_m2=edges[j], right_W_m2=edges[j + 1],
                   center_W_m2=np.sqrt(edges[j] * edges[j + 1]),
                   training_all_peak_count=int(tr["all_counts"][j]),
                   training_complete_count=int(tr["counts"][j]),
                   training_mean_cost_J_m2=tr["mean_cost"][j],
                   evaluation_all_peak_count=int(ev["all_counts"][j]),
                   evaluation_complete_count=int(ev["counts"][j]),
                   evaluation_mean_cost_J_m2=ev["mean_cost"][j],
                   evaluation_resource_sum_J_m2=ev["resource_sums"][j],
                   evaluation_count_share=ev["counts"][j] / ev["counts"].sum(),
                   evaluation_resource_share=ev["resource_sums"][j] / ev["resource_sums"].sum(),
                   cost_ratio_evaluation_to_training=ev["mean_cost"][j] / tr["mean_cost"][j])
        for model, prediction in predictions.items():
            row[f"{model}_count_share"] = prediction["count_share"][j]
            row[f"{model}_resource_share"] = prediction["resource_share"][j]
        for name, matrix in draws.items():
            interval = finite_interval(np.asarray(matrix)[:, j]) if len(matrix) else [None, None]
            row[f"{name}_ci_low"], row[f"{name}_ci_high"] = interval
        rows.append(row)
    return rows


def analysis_summary(training, evaluation, predictions, bootstrap_draws, invalid):
    summary = {}
    for resource in training:
        tr, ev = aggregate(training[resource]), aggregate(evaluation[resource])
        scores = score(predictions[resource], ev)
        table = bootstrap_draws[resource]
        for model, metrics in scores.items():
            for metric, value in list(metrics.items()):
                name = f"{model}:{metric}"
                metrics[metric + "_ci"] = finite_interval([row[name] for row in table])
        differences = {}
        for model in MODELS[1:]:
            name = f"{model}:cross_entropy_minus_log_neutral"
            differences[model] = {"value": scores[model]["count_cross_entropy_nats_per_event"] - scores[MODELS[0]]["count_cross_entropy_nats_per_event"],
                                  "ci": finite_interval([row[name] for row in table])}
        observed_share = ev["resource_sums"] / ev["resource_sums"].sum()
        summary[resource] = {
            "training_complete_n": int(tr["counts"].sum()),
            "evaluation_complete_n": int(ev["counts"].sum()),
            "training_all_peak_n": int(tr["all_counts"].sum()),
            "evaluation_all_peak_n": int(ev["all_counts"].sum()),
            "training_missing_fraction": float(1 - tr["counts"].sum() / tr["all_counts"].sum()),
            "evaluation_missing_fraction": float(1 - ev["counts"].sum() / ev["all_counts"].sum()),
            "cost_ratio_by_bin": (ev["mean_cost"] / tr["mean_cost"]).tolist(),
            "resource_share_max_to_min": float(observed_share.max() / observed_share.min()) if observed_share.min() > 0 else None,
            "scores": scores,
            "paired_cross_entropy_differences": differences,
            "valid_bootstrap_replicates": len(table),
            "invalid_training_bin_or_empty_evaluation_replicates": invalid[resource],
        }
    return summary
