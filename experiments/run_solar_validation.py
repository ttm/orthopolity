"""Freeze a development forecast, then separately acquire and evaluate NOAA 2025."""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import shutil
import ssl
import sys
import urllib.error
import urllib.request

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from orthopolity.figures import save_figure
from orthopolity.solar_resource_transfer import RESOURCES, MODELS, catalogue, membership, aggregate
from orthopolity.solar_validation import development, development_diagnostics, solar_application_gate, gate_verdict, evaluate

SOURCES = ["experiments/run_solar_validation.py", "src/orthopolity/solar_validation.py",
           "src/orthopolity/solar_resource_transfer.py", "src/orthopolity/profile_calibration.py",
           "src/orthopolity/figures.py"]


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def reference(path):
    path = Path(path)
    return {"path": str(path.relative_to(ROOT)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def verify_references(refs):
    for ref in refs:
        if reference(ROOT / ref["path"])["sha256"] != ref["sha256"]:
            raise ValueError(f"Frozen input changed: {ref['path']}")


def json_ready(value):
    if isinstance(value, np.ndarray):
        return json_ready(value.tolist())
    if isinstance(value, np.generic):
        return json_ready(value.item())
    if isinstance(value, float) and not np.isfinite(value):
        return None
    if isinstance(value, dict):
        return {key: json_ready(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [json_ready(item) for item in value]
    return value


def write_json(path, value):
    path.write_text(json.dumps(json_ready(value), indent=2, allow_nan=False) + "\n")


def write_csv(path, rows):
    if not rows:
        raise ValueError("No rows to retain")
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def restore_statistics(stats):
    return {resource: {key: np.asarray(value) if key in ("all_counts", "counts", "resource_sums") else value
                       for key, value in statistics.items()}
            for resource, statistics in stats.items()}


def archive_reference(path, directory):
    ref = reference(path)
    archive = directory / "source-snapshots" / ref["sha256"] / Path(path).name
    archive.parent.mkdir(parents=True, exist_ok=True)
    if archive.exists():
        if hashlib.sha256(archive.read_bytes()).hexdigest() != ref["sha256"]:
            raise ValueError("Archived source bytes differ")
    else:
        shutil.copyfile(path, archive)
    return dict(ref, archived=reference(archive))


def verify_plan(plan):
    refs = plan["sources"] + plan["development_inputs"] + plan["benchmark_references"] + [plan["config_reference"], plan["training_membership"]]
    verify_references(refs)
    verify_references([ref["archived"] for ref in plan["sources"] + [plan["config_reference"]]])


def validate_benchmark(study, config, actual_log_widths):
    if study.get("status") != "complete" or study.get("run_id") != config["candidate_benchmark_run_id"]:
        raise ValueError("The candidate benchmark must be complete with the declared run identifier")
    benchmark_config = study.get("config", {})
    for solar_key, benchmark_key in (("factor_margin", "factor"), ("alpha", "alpha"),
                                      ("profile_bootstrap_replicates", "bootstrap_replicates")):
        if benchmark_config.get(benchmark_key) != config[solar_key]:
            raise ValueError(f"Candidate benchmark parameter differs: {benchmark_key}")
    expected_blocks = 12 * len(config["evaluation_years"])
    if expected_blocks not in benchmark_config.get("block_counts", []):
        raise ValueError("The candidate benchmark does not include the declared validation block count")
    benchmark_widths = np.asarray(benchmark_config.get("log_widths", []), float)
    actual_widths = np.asarray(actual_log_widths, float)
    if benchmark_widths.shape != actual_widths.shape or np.any(benchmark_widths <= 0):
        raise ValueError("Candidate benchmark profile widths differ")
    if not np.allclose(benchmark_widths / benchmark_widths.sum(), actual_widths / actual_widths.sum(), rtol=1e-12, atol=1e-14):
        raise ValueError("Candidate benchmark normalized profile widths differ")
    if not any(entry.get("method") == "centered_bootstrap" for entry in study.get("eligibility", [])):
        raise ValueError("Candidate benchmark has no centered-bootstrap eligibility assessment")
    algorithm_sha = hashlib.sha256((ROOT / "src/orthopolity/profile_calibration.py").read_bytes()).hexdigest()
    if algorithm_sha not in study.get("source_sha256", {}).values():
        raise ValueError("Candidate API source does not match the completed benchmark")


def freeze(config_path, directory, benchmark_gate_path, benchmark_study_path):
    plan_path = directory / "frozen-plan.json"
    config = json.loads(config_path.read_text())
    if plan_path.exists():
        plan = json.loads(plan_path.read_text())
        verify_plan(plan)
        if config != plan["config"]:
            raise ValueError("Configuration changed after the forecast freeze")
        return plan
    if (directory / "noaa_2025.csv").exists() or (directory / "acquisition.json").exists():
        raise ValueError("Validation bytes already exist before the forecast freeze")
    # Require the completed candidate calibration and its explicit eligibility
    # record before any evaluation-byte acquisition. These are not generated here.
    benchmark_gate = json.loads(benchmark_gate_path.read_text())
    benchmark_study = json.loads(benchmark_study_path.read_text())
    benchmark_references = [reference(benchmark_gate_path), reference(benchmark_study_path)]
    checksums = {row["file"]: row["sha256"] for row in json.loads((ROOT / "data/snapshot_checksums.json").read_text())}
    names = [f"noaa_{year}.csv" for year in config["training_years"]] + ["noaa_metadata.json"]
    inputs = [reference(ROOT / "data/raw" / name) for name in names]
    for ref in inputs:
        if ref["sha256"] != checksums[Path(ref["path"]).name]:
            raise ValueError("Development snapshot differs from the retained checksum catalogue")
    development_data = development(ROOT / "data/raw", config)
    edges = development_data["edges"]
    validate_benchmark(benchmark_study, config, np.diff(np.log(edges)))
    diagnostics = development_diagnostics(development_data["statistics"], np.diff(np.log(edges)))
    gate = solar_application_gate(benchmark_gate, diagnostics, config)
    directory.mkdir(parents=True, exist_ok=True)
    membership_path = directory / "training-membership.csv"
    write_csv(membership_path, development_data["membership"])
    sources = [archive_reference(ROOT / path, directory) for path in SOURCES]
    config_ref = archive_reference(config_path, directory)
    metadata = json.loads((ROOT / "data/raw/noaa_metadata.json").read_text())
    plan = {
        "run_id": config["run_id"], "frozen_utc": utc_now(), "config": config,
        "config_reference": config_ref, "sources": sources, "development_inputs": inputs,
        "benchmark_references": benchmark_references, "application_gate": gate,
        "training_membership": reference(membership_path),
        "fine_edges_W_m2": development_data["fine_edges"],
        "fine_training_counts": development_data["fine_counts"],
        "pooled_edges_W_m2": edges, "training_statistics": development_data["statistics"],
        "forecasts": development_data["forecasts"],
        "factor_margin": config["factor_margin"],
        "metadata_definitions": {key: metadata["variable_attributes"][key]
                                 for key in ("xrsb_irrad", "integrated_irrad_peak", "integrated_irrad_end", "end_time")},
        "environment": {"python": platform.python_version(), "numpy": np.__version__, "matplotlib": matplotlib.__version__},
        "acquisition_order_scope": "2025 event bytes not acquired or inspected by this analysis before this freeze; only the public directory listing was consulted. Existing public observations, not prospective measurement or independently verified blinding.",
        "pre_acquisition_primary_verdict_scope": "Formal full-profile neutrality verdict will remain unresolved because observational sampling assumptions are not established. Candidate classifications and frozen prediction scores are explicitly conditional diagnostics.",
    }
    write_json(plan_path, plan)
    return json_ready(plan)


def append_attempt(path, record):
    with path.open("a") as stream:
        stream.write(json.dumps(record, allow_nan=False) + "\n")


def acquire(plan, directory):
    verify_plan(plan)
    snapshot = directory / "noaa_2025.csv"
    receipt_path = directory / "acquisition.json"
    attempts_path = directory / "retrieval-attempts.jsonl"
    plan_ref = reference(directory / "frozen-plan.json")
    if receipt_path.exists():
        receipt = json.loads(receipt_path.read_text())
        if receipt["frozen_plan"] != plan_ref:
            raise ValueError("Acquisition belongs to another forecast freeze")
        verify_references([receipt["snapshot"], receipt["retrieval_attempts"]])
        return receipt
    if snapshot.exists():
        raise ValueError("Unreceipted validation snapshot already exists; preserve it and investigate rather than overwrite")
    url = plan["config"]["validation_url"]
    started = utc_now()
    request = urllib.request.Request(url, headers={"User-Agent": "Orthopolity-reproducible-public-data-validation/1.0", "Accept": "text/csv"})
    ca_bundle = Path("/etc/ssl/cert.pem")
    tls_metadata = {"certificate_verification": True, "hostname_verification": True,
                    "openssl_version": ssl.OPENSSL_VERSION,
                    "ca_bundle": str(ca_bundle) if ca_bundle.is_file() else "platform default",
                    "ca_bundle_sha256": hashlib.sha256(ca_bundle.read_bytes()).hexdigest() if ca_bundle.is_file() else None}
    try:
        context = ssl.create_default_context(cafile=str(ca_bundle) if ca_bundle.is_file() else None)
        with urllib.request.urlopen(request, timeout=60, context=context) as response:
            payload = response.read()
            headers = dict(response.headers.items())
            status = response.status
            final_url = response.geturl()
    except Exception as error:
        record = {"started_utc": started, "finished_utc": utc_now(), "url": url,
                  "status": "failed", "error_type": type(error).__name__, "error": str(error),
                  "http_status": getattr(error, "code", None),
                  "tls": tls_metadata,
                  "http_headers": dict(error.headers.items()) if isinstance(error, urllib.error.HTTPError) else None}
        append_attempt(attempts_path, record)
        raise
    temporary = snapshot.with_suffix(".csv.download.tmp")
    temporary.write_bytes(payload)
    temporary.replace(snapshot)
    record = {"started_utc": started, "finished_utc": utc_now(), "url": url,
              "final_url": final_url, "status": "successful", "http_status": status,
              "http_headers": headers, "tls": tls_metadata, "bytes": len(payload), "snapshot": reference(snapshot)}
    append_attempt(attempts_path, record)
    receipt = dict(record, frozen_plan=plan_ref, retrieval_attempts=reference(attempts_path),
                   scope="Immutable new annual snapshot; historical raw snapshot catalogue untouched")
    write_json(receipt_path, receipt)
    return receipt


def candidate_profiles(evaluation, widths, config):
    from orthopolity.profile_calibration import profile_decision
    return {resource: profile_decision(stats["resource_sums"], widths,
                                       factor=config["factor_margin"], alpha=config["alpha"],
                                       bootstrap_replicates=config["profile_bootstrap_replicates"],
                                       seed=config["profile_seed"] + i, resource_upper_bounds=None)
            for i, (resource, stats) in enumerate(evaluation.items())}


def make_figures(profiles, config, directory):
    colors = {MODELS[0]: "#286692", MODELS[1]: "#ad612f", MODELS[2]: "#477c53"}
    labels = {MODELS[0]: "Neutral per log irradiance", MODELS[1]: "Neutral per linear irradiance", MODELS[2]: "2022–24 count shape"}
    fig, axes = plt.subplots(2, 3, figsize=(13, 7), layout="constrained")
    for i, resource in enumerate(RESOURCES):
        rows = profiles[resource]
        get = lambda key: np.asarray([row[key] for row in rows], float)
        x = get("center_W_m2")
        widths = np.log(get("right_W_m2") / get("left_W_m2"))
        width_share = widths / widths.sum()
        name = "Start-to-peak" if resource.endswith("peak") else "Start-to-end"
        ax = axes[i, 0]
        ax.plot(x, get("evaluation_count_share"), "o-", color="black", label="2025 measured")
        ax.fill_between(x, get("count_share_ci_low"), get("count_share_ci_high"), color="black", alpha=.12)
        for model in MODELS:
            ax.plot(x, get(f"{model}_count_share"), "s--", color=colors[model], label=labels[model], markersize=3)
        ax.set(xscale="log", ylabel="Fraction of complete events", title=f"{name}: frozen count forecast")
        ax = axes[i, 1]
        ax.axhspan(1 / config["factor_margin"], config["factor_margin"], color="#286692", alpha=.08, label="Declared F = 1.5 margin")
        ax.plot(x, get("evaluation_resource_share") / width_share, "o-", color="black")
        ax.fill_between(x, get("resource_share_ci_low") / width_share, get("resource_share_ci_high") / width_share, color="black", alpha=.12)
        for model in MODELS:
            ax.plot(x, get(f"{model}_resource_share") / width_share, "s--", color=colors[model], markersize=3)
        ax.set(xscale="log", ylabel="Fluence per log width / domain mean", title=f"{name}: measured resource profile")
        ax = axes[i, 2]
        ax.axhline(1, color="#888888", linestyle="--")
        ax.plot(x, get("cost_ratio_evaluation_to_training"), "o-", color="black")
        ax.fill_between(x, get("cost_ratio_ci_low"), get("cost_ratio_ci_high"), color="black", alpha=.12)
        ax.set(xscale="log", ylabel="2025 / 2022–24 mean fluence", title=f"{name}: cost transfer")
    axes[0, 0].legend(fontsize=7)
    axes[0, 1].legend(fontsize=7)
    for ax in axes.flat:
        ax.set_xlabel("Peak irradiance bin centre (W/m²)")
        ax.spines[["top", "right"]].set_visible(False)
    for suffix in ("png", "svg"):
        save_figure(fig, directory / f"profiles.{suffix}", dpi=180)
    plt.close(fig)


def analyse(plan, directory, output_directory):
    verify_plan(plan)
    receipt_path = directory / "acquisition.json"
    receipt = json.loads(receipt_path.read_text())
    plan_ref = reference(directory / "frozen-plan.json")
    if receipt["frozen_plan"] != plan_ref:
        raise ValueError("Snapshot belongs to another forecast freeze")
    verify_references([receipt["snapshot"], receipt["retrieval_attempts"]])
    study_path = output_directory / "study.json"
    if study_path.exists():
        existing = json.loads(study_path.read_text())
        if existing["frozen_plan"] != plan_ref or existing["acquisition"] != reference(receipt_path):
            raise ValueError("Existing results belong to different frozen inputs")
        verify_references(existing["generated_artifacts"])
        return existing
    config = plan["config"]
    edges = np.asarray(plan["pooled_edges_W_m2"])
    training = restore_statistics(plan["training_statistics"])
    validation_rows = catalogue(directory, config["evaluation_years"], edges)
    evaluation, draws, profiles, summary = evaluate(training, validation_rows, plan["forecasts"], edges, config)
    candidates = candidate_profiles(evaluation, np.diff(np.log(edges)), config)
    formal = {}
    for resource in RESOURCES:
        observed = aggregate(evaluation[resource])
        missing = int(observed["all_counts"].sum() - observed["counts"].sum())
        formal[resource] = gate_verdict(candidates[resource], plan["application_gate"], primary_missing_count=missing)
    membership_path = directory / "validation-membership.csv"
    write_csv(membership_path, membership(validation_rows))
    output_directory.mkdir(parents=True, exist_ok=True)
    artifacts = [reference(membership_path)]
    for resource in RESOURCES:
        short = "rise" if resource.endswith("peak") else "end"
        for filename, rows in ((f"{short}-profiles.csv", profiles[resource]), (f"{short}-bootstrap.csv", draws[resource])):
            path = output_directory / filename
            write_csv(path, rows)
            artifacts.append(reference(path))
        path = output_directory / f"{short}-candidate-profile.json"
        write_json(path, candidates[resource])
        artifacts.append(reference(path))
    monthly_path = output_directory / "validation-monthly-resource-totals.json"
    write_json(monthly_path, evaluation)
    artifacts.append(reference(monthly_path))
    make_figures(profiles, config, output_directory)
    artifacts.extend(reference(output_directory / f"profiles.{suffix}") for suffix in ("png", "svg"))
    study = {
        "run_id": config["run_id"], "analysed_utc": utc_now(), "evidence_kind": "actual_measurement",
        "frozen_plan": plan_ref, "acquisition": reference(receipt_path), "new_snapshot": receipt["snapshot"],
        "config": config, "sources": plan["sources"], "development_inputs": plan["development_inputs"],
        "benchmark_references": plan["benchmark_references"], "application_gate": plan["application_gate"],
        "training_membership": plan["training_membership"], "generated_artifacts": artifacts,
        "pooled_edges_W_m2": edges, "results": summary, "formal_profile_verdicts": formal,
        "conditional_candidate_profiles": candidates, "environment": plan["environment"],
        "interpretation": "Frozen forecasts scored on newly acquired historical public observations. Formal full-profile neutrality remains unresolved under the pre-acquisition application gate; conditional bands do not establish their observational sampling assumptions.",
    }
    write_json(study_path, study)
    return json_ready(study)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("freeze", "acquire", "analyse"), required=True)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/solar_validation_2026-10-02.json")
    parser.add_argument("--data-directory", type=Path, default=ROOT / "data/solar-validation/2026-10-02")
    parser.add_argument("--output-directory", type=Path, default=ROOT / "results/solar-validation")
    parser.add_argument("--benchmark-gate", type=Path)
    parser.add_argument("--benchmark-study", type=Path)
    args = parser.parse_args()
    if args.stage == "freeze":
        if args.benchmark_gate is None or args.benchmark_study is None:
            parser.error("freeze requires --benchmark-gate and --benchmark-study retained completed records")
        plan = freeze(args.config.resolve(), args.data_directory.resolve(), args.benchmark_gate.resolve(), args.benchmark_study.resolve())
        print(json.dumps({"frozen_plan": reference(args.data_directory.resolve() / "frozen-plan.json"),
                          "pooled_edges_W_m2": plan["pooled_edges_W_m2"], "formal_profile_eligible": plan["application_gate"]["formal_profile_eligible"]}, indent=2))
        return
    plan = json.loads((args.data_directory / "frozen-plan.json").read_text())
    if args.stage == "acquire":
        print(json.dumps(acquire(plan, args.data_directory.resolve()), indent=2))
    else:
        result = analyse(plan, args.data_directory.resolve(), args.output_directory.resolve())
        print(json.dumps({"results": result["results"], "formal_profile_verdicts": result["formal_profile_verdicts"]}, indent=2))


if __name__ == "__main__":
    main()
