"""Independently cross-check retained solar forecasts and optional CPU accounting.

This is a deterministic, post hoc descriptive audit. It reads ordinary CSV and
JSON directly and does not import any study selection, fitting, or scoring code.
It does not rerun forecasts, bootstrap inference, or acquire new observations.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import subprocess

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESOURCES = ("integrated_irrad_peak", "integrated_irrad_end")


def require(condition, explanation):
    if not condition:
        raise AssertionError(explanation)


def reference(path):
    path = Path(path).resolve()
    return {"path": str(path.relative_to(ROOT)),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def verify_reference(value):
    current = reference(ROOT / value["path"])
    require(current["sha256"] == value["sha256"],
            f"Retained file digest differs: {value['path']}")


def close(observed, expected):
    # A small absolute tolerance also handles exact zero shares and roundoff.
    np.testing.assert_allclose(observed, expected, rtol=1e-12, atol=1e-14)


def numeric(value):
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def timestamp(value):
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def inspect_catalogues(paths, years, edges, fine_edges):
    """Apply the declared measurements directly; preserve all row membership."""
    year_indices = {year: index for index, year in enumerate(years)}
    bins = len(edges) - 1
    months = [f"{year}-{month:02d}" for year in years for month in range(1, 13)]
    all_counts = np.zeros((len(months), bins), dtype=np.int64)
    counts = {resource: np.zeros_like(all_counts) for resource in RESOURCES}
    totals = {resource: np.zeros_like(all_counts, dtype=float) for resource in RESOURCES}
    fine_counts = {resource: np.zeros(len(fine_edges) - 1, dtype=np.int64)
                   for resource in RESOURCES}
    instruments = {str(year): {"eligible_peaks": {}, **{resource: {} for resource in RESOURCES}}
                   for year in years}
    valid_sources = {f"GOES-{number}" for number in range(1, 20)}
    ids, times, membership, headers = [], [], [], {}
    for path, year in zip(paths, years):
        with path.open(newline="") as stream:
            table = csv.DictReader(stream)
            headers[path.name] = list(table.fieldnames)
            for index, row in enumerate(table):
                ids.append(row["flare_id"])
                peak_time = timestamp(row["time"])
                require(peak_time is not None and peak_time.year == year,
                        f"Year/peak-time mismatch in {path.name} row {index}")
                times.append(peak_time)
                start, end = timestamp(row["start_time"]), timestamp(row["end_time"])
                peak = numeric(row["xrsb_irrad"])
                if peak is None or peak <= 0:
                    reason = "invalid_peak"
                elif numeric(row["peak_saturated"]) != 0:
                    reason = "saturated_or_unknown"
                elif not edges[0] <= peak <= edges[-1]:
                    reason = "outside_fixed_domain"
                else:
                    reason = "selected_peak"
                bin_index = min(int(np.searchsorted(edges, peak, side="right") - 1), bins - 1) if reason == "selected_peak" else -1
                record = {"source_file": path.name, "source_row_index": index,
                          "flare_id": row["flare_id"], "year": year,
                          "month": peak_time.strftime("%Y-%m"),
                          "peak_selection": reason, "bin": bin_index}
                monthly_index = year_indices[year] * 12 + peak_time.month - 1
                instrument = row["xrsb_irrad_source"]
                if reason == "selected_peak":
                    require(instrument in valid_sources,
                            f"Unknown eligible irradiance source: {instrument}")
                    all_counts[monthly_index, bin_index] += 1
                    target = instruments[str(year)]["eligible_peaks"]
                    target[instrument] = target.get(instrument, 0) + 1
                for resource, window in zip(RESOURCES, (peak_time, end)):
                    amount = numeric(row[resource])
                    valid = amount is not None and amount > 0 and start is not None and window is not None and window > start
                    record[f"valid_{resource}"] = str(valid)
                    if reason == "selected_peak" and valid:
                        counts[resource][monthly_index, bin_index] += 1
                        totals[resource][monthly_index, bin_index] += amount
                        fine_index = min(int(np.searchsorted(fine_edges, peak, side="right") - 1), len(fine_edges) - 2)
                        fine_counts[resource][fine_index] += 1
                        target = instruments[str(year)][resource]
                        target[instrument] = target.get(instrument, 0) + 1
                membership.append(record)
    require(len(ids) == len(set(ids)), "Duplicate flare IDs in named catalogues")
    return {"months": months, "all_counts": all_counts, "counts": counts,
            "resource_sums": totals, "fine_counts": fine_counts,
            "instrument_mix_by_year_and_resource": instruments,
            "ids": ids, "times": times, "membership": membership,
            "headers": headers}


def verify_membership(path, expected):
    with path.open(newline="") as stream:
        stored = list(csv.DictReader(stream))
    converted = [{key: str(value) for key, value in row.items()} for row in expected]
    require(stored == converted, f"Membership differs: {path}")


def independently_pool(fine_edges, resource_counts, minimum):
    """Reconstruct the declared upper-to-lower support merge from raw counts."""
    boundaries = [len(fine_edges) - 1]
    pending = np.zeros(len(RESOURCES), dtype=np.int64)
    for index in range(len(fine_edges) - 2, -1, -1):
        pending += [resource_counts[resource][index] for resource in RESOURCES]
        if np.all(pending >= minimum):
            boundaries.append(index)
            pending[:] = 0
    if boundaries[-1] != 0:
        if len(boundaries) > 1:
            boundaries.pop()
        boundaries.append(0)
    return np.asarray([fine_edges[index] for index in reversed(boundaries)])


def cpu_audit(directory, study_path):
    calibration_path, trials_path = directory / "calibration.json", directory / "trials.json"
    plan_path = directory / "frozen-plan.json"
    calibration = json.loads(calibration_path.read_text())
    trials = json.loads(trials_path.read_text())
    plan = json.loads(plan_path.read_text())
    study = json.loads(study_path.read_text())
    for path, key in ((calibration_path, "calibration_sha256"),
                      (trials_path, "trials_sha256"), (plan_path, "frozen_plan_sha256")):
        require(reference(path)["sha256"] == study[key], f"CPU input changed: {path}")
    workers = [worker for trial in trials for worker in trial["workers"]]
    accounting = {
        "allocation_trials": len(trials), "worker_records": len(workers),
        "calibration_completed_jobs": sum(len(row["job_cpu_seconds"]) for row in calibration),
        "completed_validation_jobs": sum(row["completed_jobs"] for row in workers),
        "censored_partial_jobs": sum(row["censored_partial_jobs"] for row in workers),
        "measured_worker_cpu_seconds": math.fsum(row["cpu_seconds"] for row in workers),
        "enclosing_process_cpu_seconds": math.fsum(row["process_control_envelope_cpu_seconds"] for row in trials),
        "unassigned_process_cpu_seconds": math.fsum(row["unassigned_process_cpu_seconds"] for row in trials),
    }
    for key, value in accounting.items():
        close(value, study["accounting"][key])
    for trial in trials:
        require(trial["timing_assumptions_satisfied"], "A CPU trial failed its frozen timing guard")
        require(trial["frozen_plan_sha256"] == study["frozen_plan_sha256"], "CPU trial uses another forecast")
        require(timestamp(plan["frozen_utc"]) < timestamp(trial["measured_utc"]), "CPU validation precedes freeze")
        close(math.fsum(row["cpu_seconds"] for row in trial["workers"]), trial["worker_cpu_seconds"])
        close(trial["worker_cpu_seconds"] + trial["unassigned_process_cpu_seconds"], trial["process_control_envelope_cpu_seconds"])
        for worker in trial["workers"]:
            close(worker["complete_job_cpu_seconds"] + worker["partial_job_cpu_seconds"] + worker["loop_overhead_cpu_seconds"], worker["cpu_seconds"])
    groups = {}
    sizes = plan["config"]["sizes"]
    for kernel in plan["config"]["kernels"]:
        costs = []
        for size in sizes:
            charges = [charge for row in calibration if row["kernel"] == kernel and row["size"] == size for charge in row["job_cpu_seconds"]]
            costs.append(math.fsum(charges) / len(charges))
        costs = np.asarray(costs)
        degree = float(np.polyfit(np.log(sizes), np.log(costs), 1)[0])
        close(costs, plan["independent_cost_calibration"][kernel]["q_cpu_seconds"])
        close(degree, plan["independent_cost_calibration"][kernel]["independently_measured_cost_fit"]["degree"])
        groups[kernel] = {"independent_mean_job_cpu_seconds": costs.tolist(),
                          "independent_cost_degree": degree, "conditions": {}}
        for condition, runnable_counts in plan["config"]["conditions"].items():
            selected = [trial for trial in trials if trial["kernel"] == kernel and trial["condition"] == condition]
            cpu = np.asarray([math.fsum(worker["cpu_seconds"] for trial in selected for worker in trial["workers"] if worker["size"] == size) for size in sizes])
            jobs = np.asarray([sum(worker["completed_jobs"] for trial in selected for worker in trial["workers"] if worker["size"] == size) for size in sizes])
            target = study["profiles"][kernel][condition]
            close(cpu, target["cpu_seconds_by_class"])
            np.testing.assert_array_equal(jobs, target["completed_jobs_by_class"])
            cpu_share, count_share = cpu / cpu.sum(), jobs / jobs.sum()
            close(cpu_share, target["measured_cpu_share"])
            fair = np.asarray(runnable_counts, dtype=float)
            fair /= fair.sum()
            prediction = fair / costs
            prediction /= prediction.sum()
            cpu_error = float(np.max(abs(cpu_share - fair)))
            count_tv = float(np.sum(abs(count_share - prediction)) / 2)
            close([cpu_error, count_tv], [target["errors"]["fair_thread_cpu"]["maximum_absolute_cpu_share_error"], target["errors"]["fair_thread_cpu"]["count_total_variation"]])
            groups[kernel]["conditions"][condition] = {"cpu_share": cpu_share.tolist(),
                "count_share": count_share.tolist(), "fair_thread_cpu_maximum_error": cpu_error,
                "fair_thread_count_total_variation": count_tv}
    return {"status": "passed", "inputs": [reference(path) for path in (calibration_path, trials_path, plan_path, study_path)],
            "accounting": accounting, "groups": groups,
            "maximum_start_lag_seconds": max(worker["start_lag_seconds"] for worker in workers),
            "maximum_stop_lag_seconds": max(worker["stop_lag_seconds"] for worker in workers),
            "scope": "Direct charge partitions, calibration arithmetic means, fitted finite cost slopes, and aggregate allocation profiles; not independent observations or a natural-law test"}


def audit(directory, study_path, checkpoint, cpu_directory, cpu_study):
    plan_path, acquisition_path = directory / "frozen-plan.json", directory / "acquisition.json"
    plan = json.loads(plan_path.read_text())
    acquisition = json.loads(acquisition_path.read_text())
    study = json.loads(study_path.read_text())
    references = plan["sources"] + plan["development_inputs"] + plan["benchmark_references"] + [plan["config_reference"], plan["training_membership"]]
    for value in references:
        verify_reference(value)
        if "archived" in value:
            verify_reference(value["archived"])
    for value in (acquisition["snapshot"], acquisition["frozen_plan"], acquisition["retrieval_attempts"]):
        verify_reference(value)
    config = plan["config"]
    require(json.loads((ROOT / plan["config_reference"]["path"]).read_text()) == config,
            "Frozen configuration content differs")
    require(acquisition["url"] == config["validation_url"], "Acquired URL differs from frozen source")
    development_paths = [ROOT / f"data/raw/noaa_{year}.csv" for year in config["training_years"]]
    validation_path = ROOT / acquisition["snapshot"]["path"]
    require(len(config["evaluation_years"]) == 1, "This audit expects one retained annual evaluation file")
    require(validation_path.stat().st_size == acquisition["bytes"], "Acquisition byte count differs")
    edges, fine_edges = np.asarray(plan["pooled_edges_W_m2"]), np.asarray(plan["fine_edges_W_m2"])
    development = inspect_catalogues(development_paths, config["training_years"], edges, fine_edges)
    validation = inspect_catalogues([validation_path], config["evaluation_years"], edges, fine_edges)
    require(not set(development["ids"]) & set(validation["ids"]), "Development/validation flare IDs overlap")
    require(all(header == next(iter(development["headers"].values())) for header in [*development["headers"].values(), *validation["headers"].values()]), "CSV field conventions changed")
    verify_membership(ROOT / plan["training_membership"]["path"], development["membership"])
    verify_membership(directory / "validation-membership.csv", validation["membership"])
    pooled = independently_pool(fine_edges, development["fine_counts"], config["minimum_training_events_per_resource_per_pooled_bin"])
    close(pooled, edges)
    widths, linear_widths = np.diff(np.log(edges)), np.diff(edges)
    metadata_path = ROOT / "data/raw/noaa_metadata.json"
    metadata = json.loads(metadata_path.read_text())["variable_attributes"]
    require(metadata["xrsb_irrad"]["units"] == "W/m2", "Peak irradiance unit changed")
    require(all(metadata[key]["units"] == "J/m2" for key in RESOURCES), "Fluence unit changed")
    require(all(plan["metadata_definitions"][key] == metadata[key] for key in plan["metadata_definitions"]), "Frozen measurement metadata differ")
    results, forecast_score_differences = {}, []
    for resource in RESOURCES:
        dev_counts = development["counts"][resource].sum(axis=0)
        dev_sums = development["resource_sums"][resource].sum(axis=0)
        val_counts = validation["counts"][resource].sum(axis=0)
        val_sums = validation["resource_sums"][resource].sum(axis=0)
        np.testing.assert_array_equal(development["fine_counts"][resource], plan["fine_training_counts"][resource])
        stored_training = plan["training_statistics"][resource]
        require(development["months"] == stored_training["months"], "Development calendar blocks differ")
        np.testing.assert_array_equal(development["all_counts"], stored_training["all_counts"])
        np.testing.assert_array_equal(development["counts"][resource], stored_training["counts"])
        close(development["resource_sums"][resource], stored_training["resource_sums"])
        means = dev_sums / dev_counts
        observed_counts, observed_resources = val_counts / val_counts.sum(), val_sums / val_sums.sum()
        phi = observed_resources / (widths / widths.sum())
        scores = {}
        for name, unnormalized in (("log_resource_neutral", widths / means), ("linear_resource_neutral", linear_widths / means), ("historical_count_shape", dev_counts)):
            prediction = unnormalized / unnormalized.sum()
            resource_prediction = prediction * means / (prediction @ means)
            cross_entropy = float(-observed_counts @ np.log(prediction))
            count_tv = float(np.sum(abs(prediction - observed_counts)) / 2)
            resource_tv = float(np.sum(abs(resource_prediction - observed_resources)) / 2)
            saved = study["results"][resource]["scores"][name]
            close(prediction, plan["forecasts"][resource][name]["count_share"])
            close(resource_prediction, plan["forecasts"][resource][name]["resource_share"])
            close([cross_entropy, count_tv, resource_tv], [saved["count_cross_entropy_nats_per_event"], saved["count_total_variation"], saved["resource_share_total_variation"]])
            forecast_score_differences.extend(abs(prediction - plan["forecasts"][resource][name]["count_share"]))
            forecast_score_differences.extend(abs(resource_prediction - plan["forecasts"][resource][name]["resource_share"]))
            forecast_score_differences.extend(abs(np.asarray([cross_entropy, count_tv, resource_tv]) -
                [saved["count_cross_entropy_nats_per_event"], saved["count_total_variation"], saved["resource_share_total_variation"]]))
            scores[name] = {"count_share": prediction.tolist(), "resource_share": resource_prediction.tolist(),
                           "count_cross_entropy_nats_per_event": cross_entropy,
                           "count_total_variation": count_tv, "resource_share_total_variation": resource_tv}
        close(phi, study["conditional_candidate_profiles"][resource]["point"]["phi"])
        cost_ratio = (val_sums / val_counts) / means
        close(cost_ratio, study["results"][resource]["cost_ratio_by_bin"])
        results[resource] = {"development_complete_counts": dev_counts.tolist(),
            "evaluation_complete_counts": val_counts.tolist(), "development_mean_cost_J_m2": means.tolist(),
            "evaluation_resource_totals_J_m2": val_sums.tolist(), "observed_count_share": observed_counts.tolist(),
            "observed_resource_share": observed_resources.tolist(), "relative_resource_density_phi": phi.tolist(),
            "raw_resource_share_max_to_min": float(observed_resources.max() / observed_resources.min()),
            "width_corrected_resource_density_max_to_min": float(phi.max() / phi.min()),
            "evaluation_to_development_mean_cost_ratio": cost_ratio.tolist(), "scores": scores}
        for split, computed in (("training", development), ("evaluation", validation)):
            complete = int(computed["counts"][resource].sum())
            peaks = int(computed["all_counts"].sum())
            require(complete == study["results"][resource][f"{split}_complete_n"], "Retained complete count differs")
            require(peaks == study["results"][resource][f"{split}_all_peak_n"], "Retained eligible peak count differs")
            close(1 - complete / peaks, study["results"][resource][f"{split}_missing_fraction"])
    checkpoint_full = subprocess.check_output(["git", "rev-parse", checkpoint], cwd=ROOT, text=True).strip()
    committed_plan = subprocess.check_output(["git", "show", f"{checkpoint}:{reference(plan_path)['path']}"], cwd=ROOT)
    require(hashlib.sha256(committed_plan).hexdigest() == reference(plan_path)["sha256"], "Checkpoint forecast bytes differ")
    checkpoint_files = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", checkpoint, "data"], cwd=ROOT, text=True).splitlines()
    require(reference(validation_path)["path"] not in checkpoint_files, "Checkpoint already contains the validation file")
    require(not any(Path(path).name == "noaa_2025.csv" for path in checkpoint_files), "Checkpoint has another retained 2025 NOAA file")
    committed_utc = subprocess.check_output(["git", "show", "-s", "--format=%cI", checkpoint], cwd=ROOT, text=True).strip()
    attempts = [json.loads(line) for line in (ROOT / acquisition["retrieval_attempts"]["path"]).read_text().splitlines()]
    require([attempt["status"] for attempt in attempts] == ["failed", "successful"], "Expected failed and successful attempts are not both retained")
    require(bool(attempts[0].get("error")), "Failed acquisition lacks its error receipt")
    require(timestamp(attempts[0]["started_utc"]) < timestamp(attempts[0]["finished_utc"]) < timestamp(attempts[1]["started_utc"]), "Attempt chronology differs")
    require(all(attempts[1][key] == acquisition[key] for key in ("started_utc", "finished_utc", "url", "final_url", "http_status", "snapshot")), "Successful attempt and acquisition receipt differ")
    require(all(attempt["tls"]["certificate_verification"] and attempt["tls"]["hostname_verification"] for attempt in attempts), "An acquisition attempt disabled TLS checks")
    require(timestamp(plan["frozen_utc"]) < timestamp(committed_utc) < min(timestamp(attempt["started_utc"]) for attempt in attempts) < timestamp(acquisition["finished_utc"]) < timestamp(study["analysed_utc"]), "Local freeze/checkpoint/acquisition/analysis ordering differs")
    require(acquisition["http_status"] == 200 and acquisition["status"] == "successful", "No successful HTTP acquisition")
    maximum_score_difference = float(max(forecast_score_differences))
    require(maximum_score_difference <= 1e-12, "Forecast or score differs by more than absolute 1e-12")
    input_paths = [plan_path, acquisition_path, study_path, validation_path, metadata_path,
                   ROOT / acquisition["retrieval_attempts"]["path"],
                   ROOT / plan["training_membership"]["path"],
                   directory / "validation-membership.csv", *development_paths]
    for value in references:
        input_paths.append(ROOT / value["path"])
        if "archived" in value:
            input_paths.append(ROOT / value["archived"]["path"])
    input_references = {value["path"]: value for value in map(reference, input_paths)}
    report = {
        "kind": "post_hoc_descriptive_independent_recomputation", "status": "passed",
        "audited_run_id": plan["run_id"], "audit_algorithm": reference(Path(__file__)),
        "audit_source_reference": reference(Path(__file__)),
        "post_hoc_scope": "Audit designed after the retained solar and CPU results were available; descriptive independent arithmetic cross-check only, with no additional observations or scientific hypothesis retuning",
        "algorithm_scope": "Standard CSV/datetime parsing and NumPy arithmetic only; no study-analysis functions imported. Recomputed selection, membership, support pooling, arithmetic costs, three forecast shapes, point scores, and CPU charge bookkeeping. No bootstrap regeneration, new fit, bin selection, or inferential verdict.",
        "comparison_tolerance": {"relative": 1e-12, "absolute": 1e-14},
        "maximum_absolute_forecast_and_score_difference": maximum_score_difference,
        "forecast_and_score_absolute_error_limit": 1e-12,
        "development_raw_rows": len(development["ids"]), "evaluation_raw_rows": len(validation["ids"]),
        "duplicated_flare_ids": {"development": 0, "evaluation": 0, "between_splits": 0},
        "evaluation_peak_time_range": [min(validation["times"]).isoformat(), max(validation["times"]).isoformat()],
        "measurement_units": {"peak_irradiance": "W/m2", "fluence": "J/m2"},
        "pooled_edges_W_m2": edges.tolist(), "reference_measure": "d ln peak irradiance",
        "instrument_mix": {"development": development["instrument_mix_by_year_and_resource"], "evaluation": validation["instrument_mix_by_year_and_resource"]},
        "resources": results,
        "local_ordering": {"checkpoint": checkpoint_full, "frozen_utc": plan["frozen_utc"], "checkpoint_committed_time": committed_utc,
            "attempts_started_utc": [attempt["started_utc"] for attempt in attempts],
            "attempt_statuses": [attempt["status"] for attempt in attempts], "acquisition_finished_utc": acquisition["finished_utc"],
            "analysed_utc": study["analysed_utc"], "committed_forecast_matches": True,
            "checkpoint_contains_2025_event_bytes": False, "tls_verification_preserved": True},
        "caveats": ["This audit adds no independent observations and is selected after results are available.",
            "Local Git ordering and receipt checks do not establish external preregistration or global blindness.",
            "The irradiance-source mix changes across years; temporal cost changes cannot isolate physics from instrument/source effects.",
            "Matching CSV columns and historical versioned metadata do not independently validate calibration, detection completeness, or annual exposure.",
            "Raw resource-share ratios differ from width-corrected resource-density ratios because the final class is wider.",
            "Conditional bootstrap coverage and formal application assumptions are not validated by arithmetic agreement."],
    }
    if cpu_directory is not None:
        report["cpu_accounting_crosscheck"] = cpu_audit(cpu_directory, cpu_study)
        for value in report["cpu_accounting_crosscheck"]["inputs"]:
            input_references[value["path"]] = value
    report["input_references"] = [input_references[path] for path in sorted(input_references)]
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=ROOT / "data/solar-validation/2026-10-02")
    parser.add_argument("--study", type=Path, default=ROOT / "results/solar-validation/study.json")
    parser.add_argument("--output", type=Path, default=ROOT / "results/solar-validation/independent-audit.json")
    parser.add_argument("--checkpoint", default="390856c")
    parser.add_argument("--cpu-directory", type=Path, default=ROOT / "data/dimensionality-intervention/2026-10-02")
    parser.add_argument("--cpu-study", type=Path, default=ROOT / "results/dimensionality-intervention/study.json")
    parser.add_argument("--skip-cpu", action="store_true")
    args = parser.parse_args()
    report = audit(args.directory.resolve(), args.study.resolve(), args.checkpoint,
                   None if args.skip_cpu else args.cpu_directory.resolve(), args.cpu_study.resolve())
    encoded = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.output.exists():
        require(args.output.read_text() == encoded, "Retained audit differs; use a new output path")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded)
    print(json.dumps({"status": report["status"], "output": reference(args.output),
                      "audit_algorithm": report["audit_algorithm"],
                      "evaluation_rows": report["evaluation_raw_rows"],
                      "cpu_crosscheck": report.get("cpu_accounting_crosscheck", {}).get("status")}, indent=2))


if __name__ == "__main__":
    main()
