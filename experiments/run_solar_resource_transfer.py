"""Retrospective fluence-cost forecasts with a fitting holdout and immutable outputs."""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from orthopolity.figures import save_figure
from orthopolity.solar_resource_transfer import (
    RESOURCES, MODELS, fixed_edges, pooled_edges, catalogue, membership,
    monthly_statistics, aggregate, forecast, bootstrap, profile_rows, analysis_summary,
)

SOURCES = ["experiments/run_solar_resource_transfer.py",
           "src/orthopolity/solar_resource_transfer.py", "src/orthopolity/figures.py"]


def reference(path):
    path = Path(path)
    return {"path": str(path.relative_to(ROOT)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def verify_references(refs):
    for ref in refs:
        if reference(ROOT / ref["path"])["sha256"] != ref["sha256"]:
            raise ValueError(f"Frozen input changed: {ref['path']}")


def json_ready(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, dict):
        return {key: json_ready(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [json_ready(item) for item in value]
    if isinstance(value, np.generic):
        return value.item()
    return value


def write_json(path, value):
    path.write_text(json.dumps(json_ready(value), indent=2, allow_nan=False) + "\n")


def write_csv(path, rows):
    if not rows:
        raise ValueError("Cannot retain a CSV without a known schema")
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def restore_statistics(stats):
    return {resource: {key: np.asarray(value) if key in ("all_counts", "counts", "resource_sums") else value
                       for key, value in statistics.items()}
            for resource, statistics in stats.items()}


def freeze(config_path, data_directory):
    config = json.loads(config_path.read_text())
    plan_path = data_directory / "frozen-plan.json"
    if plan_path.exists():
        plan = json.loads(plan_path.read_text())
        verify_references(plan["sources"] + plan["data_inputs"] + [plan["config_reference"], plan["training_membership"]])
        if config != plan["config"]:
            raise ValueError("The frozen configuration differs")
        return plan
    if (data_directory / "validation-membership.csv").exists():
        raise ValueError("Validation membership exists before the forecast freeze")
    checksums = {row["file"]: row["sha256"] for row in json.loads((ROOT / "data/snapshot_checksums.json").read_text())}
    names = [f"noaa_{year}.csv" for year in config["training_years"] + config["evaluation_years"]] + ["noaa_metadata.json"]
    inputs = [reference(ROOT / "data/raw" / name) for name in names]
    for ref in inputs:
        if ref["sha256"] != checksums[Path(ref["path"]).name]:
            raise ValueError("The retained NOAA snapshot checksum differs")
    fine_edges = fixed_edges(config)
    # Evaluation rows are not loaded until analyse(). Hashing their existing
    # snapshot is provenance, not an assertion that it was previously unseen.
    training_rows = catalogue(ROOT / "data/raw", config["training_years"], fine_edges)
    fine_stats = {resource: monthly_statistics(training_rows, resource, fine_edges, config["training_years"])
                  for resource in RESOURCES}
    edges = pooled_edges([aggregate(fine_stats[resource])["counts"] for resource in RESOURCES], fine_edges,
                         config["minimum_training_events_per_resource_per_pooled_bin"])
    training_rows = catalogue(ROOT / "data/raw", config["training_years"], edges)
    stats = {resource: monthly_statistics(training_rows, resource, edges, config["training_years"])
             for resource in RESOURCES}
    predictions = {resource: forecast(aggregate(stats[resource])["mean_cost"], aggregate(stats[resource])["counts"], edges)
                   for resource in RESOURCES}
    data_directory.mkdir(parents=True, exist_ok=True)
    membership_path = data_directory / "training-membership.csv"
    write_csv(membership_path, membership(training_rows))
    metadata = json.loads((ROOT / "data/raw/noaa_metadata.json").read_text())
    plan = {
        "run_id": config["run_id"], "frozen_utc": datetime.now(timezone.utc).isoformat(),
        "status": config["status"], "config": config, "config_reference": reference(config_path),
        "sources": [reference(ROOT / path) for path in SOURCES], "data_inputs": inputs,
        "training_membership": reference(membership_path), "fine_edges_W_m2": fine_edges,
        "fine_training_counts": {resource: aggregate(fine_stats[resource])["counts"] for resource in RESOURCES},
        "pooled_edges_W_m2": edges, "training_statistics": stats, "forecasts": predictions,
        "metadata_definitions": {key: metadata["variable_attributes"][key]
                                 for key in ("xrsb_irrad", "integrated_irrad_peak", "integrated_irrad_end", "end_time")},
        "environment": {"python": platform.python_version(), "numpy": np.__version__, "matplotlib": matplotlib.__version__},
        "scope": "Previously inspected measured snapshots; frozen forecasts use only 2022/2023 cost and count summaries. No new observations, blinding or external preregistration.",
    }
    write_json(plan_path, plan)
    return json_ready(plan)


def make_figures(profiles, output_directory):
    colors = {MODELS[0]: "#286692", MODELS[1]: "#ad612f", MODELS[2]: "#477c53"}
    labels = {MODELS[0]: "Neutral per log irradiance", MODELS[1]: "Neutral per linear irradiance", MODELS[2]: "2022/23 count shape"}
    fig, axes = plt.subplots(2, 3, figsize=(13, 7), layout="constrained")
    for i, resource in enumerate(RESOURCES):
        rows = profiles[resource]
        get = lambda name: np.asarray([row[name] for row in rows], float)
        x = get("center_W_m2")
        widths = np.log(get("right_W_m2") / get("left_W_m2"))
        width_share = widths / widths.sum()
        name = "Start-to-peak" if resource.endswith("peak") else "Start-to-end"
        ax = axes[i, 0]
        ax.plot(x, get("evaluation_count_share"), "o-", color="black", label="2024 measured")
        ax.fill_between(x, get("count_share_ci_low"), get("count_share_ci_high"), color="black", alpha=.12)
        for model in MODELS:
            ax.plot(x, get(f"{model}_count_share"), "s--", color=colors[model], label=labels[model], markersize=3)
        ax.set(ylabel="Fraction of complete events", title=f"{name}: count forecast", xscale="log")
        ax = axes[i, 1]
        ax.plot(x, get("evaluation_resource_share") / width_share, "o-", color="black")
        ax.fill_between(x, get("resource_share_ci_low") / width_share, get("resource_share_ci_high") / width_share, color="black", alpha=.12)
        for model in MODELS:
            ax.plot(x, get(f"{model}_resource_share") / width_share, "s--", color=colors[model], markersize=3)
        ax.set(ylabel="Fluence per log width / domain mean", title=f"{name}: resource forecast", xscale="log")
        ax = axes[i, 2]
        ax.axhline(1, color="#888888", linestyle="--")
        ax.plot(x, get("cost_ratio_evaluation_to_training"), "o-", color="black")
        ax.fill_between(x, get("cost_ratio_ci_low"), get("cost_ratio_ci_high"), color="black", alpha=.12)
        ax.set(ylabel="2024 / 2022–23 mean fluence", title=f"{name}: cost transfer", xscale="log")
    axes[0, 0].legend(fontsize=7)
    for ax in axes.flat:
        ax.set_xlabel("Peak irradiance bin centre (W/m²)")
        ax.spines[["top", "right"]].set_visible(False)
    for suffix in ("png", "svg"):
        save_figure(fig, output_directory / f"profiles.{suffix}", dpi=180)
    plt.close(fig)


def analyse(plan, data_directory, output_directory):
    verify_references(plan["sources"] + plan["data_inputs"] + [plan["config_reference"], plan["training_membership"]])
    plan_ref = reference(data_directory / "frozen-plan.json")
    study_path = output_directory / "study.json"
    if study_path.exists():
        existing = json.loads(study_path.read_text())
        if existing["frozen_plan"] != plan_ref:
            raise ValueError("Existing results belong to a different forecast freeze")
        verify_references(existing["generated_artifacts"])
        return existing
    config = plan["config"]
    edges = np.asarray(plan["pooled_edges_W_m2"])
    training = restore_statistics(plan["training_statistics"])
    rows = catalogue(ROOT / "data/raw", config["evaluation_years"], edges)
    evaluation = {resource: monthly_statistics(rows, resource, edges, config["evaluation_years"])
                  for resource in RESOURCES}
    draws, intervals, invalid = bootstrap(training, evaluation, edges,
                                           replicates=config["bootstrap_replicates"], seed=config["seed"])
    membership_path = data_directory / "validation-membership.csv"
    write_csv(membership_path, membership(rows))
    output_directory.mkdir(parents=True, exist_ok=True)
    profiles = {}
    artifacts = [reference(membership_path)]
    for resource in RESOURCES:
        profiles[resource] = profile_rows(training[resource], evaluation[resource], plan["forecasts"][resource], edges, intervals[resource])
        short = "rise" if resource.endswith("peak") else "end"
        for filename, table in ((f"{short}-profiles.csv", profiles[resource]), (f"{short}-bootstrap.csv", draws[resource])):
            path = output_directory / filename
            write_csv(path, table)
            artifacts.append(reference(path))
    make_figures(profiles, output_directory)
    artifacts.extend(reference(output_directory / f"profiles.{suffix}") for suffix in ("png", "svg"))
    summary = analysis_summary(training, evaluation, plan["forecasts"], draws, invalid)
    study = {
        "run_id": config["run_id"], "analysed_utc": datetime.now(timezone.utc).isoformat(),
        "evidence_kind": "actual_measurement", "scope": plan["scope"],
        "frozen_plan": plan_ref, "config": config, "sources": plan["sources"],
        "data_inputs": plan["data_inputs"], "training_membership": plan["training_membership"],
        "generated_artifacts": artifacts, "pooled_edges_W_m2": edges,
        "results": summary, "environment": plan["environment"],
        "interpretation": "Compare full conditional profiles and diagnose cost transfer; scores are descriptive retrospective predictions. No formal universal-law test or proof of neutrality.",
    }
    write_json(study_path, study)
    return json_ready(study)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("freeze", "analyse", "all"), default="all")
    parser.add_argument("--config", type=Path, default=ROOT / "configs/solar_resource_transfer_2026-10-01.json")
    parser.add_argument("--data-directory", type=Path, default=ROOT / "data/solar-resource-transfer/2026-10-01")
    parser.add_argument("--output-directory", type=Path, default=ROOT / "results/solar-resource-transfer")
    args = parser.parse_args()
    plan = freeze(args.config.resolve(), args.data_directory.resolve())
    if args.stage == "freeze":
        print(json.dumps({"run_id": plan["run_id"], "pooled_edges_W_m2": plan["pooled_edges_W_m2"], "fine_training_counts": plan["fine_training_counts"]}, indent=2))
    else:
        result = analyse(plan, args.data_directory.resolve(), args.output_directory.resolve())
        print(json.dumps(result["results"], indent=2))


if __name__ == "__main__":
    main()
