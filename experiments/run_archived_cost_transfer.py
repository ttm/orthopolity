#!/usr/bin/env python3
"""Acquire and replay a quota-cost transfer study without new measurements.

Explicit stages enforce a metadata-only protocol freeze before source CSV
acquisition, and a coefficient/prediction freeze before held-out quota parsing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import ssl
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from orthopolity.archived_cost_transfer import (eligible, fit_models, predictions,
                                               read_cultures, score_evaluation)

CONFIG = ROOT / "configs/archived_cost_transfer_2026-10-02.json"
DATA = ROOT / "data/archived-cost-transfer/2026-10-02"
RESULTS = ROOT / "results/archived-cost-transfer"
SOURCE_PATHS = [Path("experiments/run_archived_cost_transfer.py"),
                Path("src/orthopolity/archived_cost_transfer.py")]


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def ref(path):
    path = Path(path)
    return dict(path=path.relative_to(ROOT).as_posix(), sha256=digest(path))


def read_json(path):
    return json.loads(Path(path).read_text())


def save_json(path, value):
    path = Path(path)
    content = (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    if path.exists():
        if path.read_bytes() != content:
            raise RuntimeError(f"Refusing to overwrite changed retained artifact: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def fetch(url, destination):
    destination = Path(destination)
    receipt_path = destination.with_suffix(destination.suffix + ".receipt.json")
    if destination.exists():
        receipt = read_json(receipt_path)
        if receipt["sha256"] != digest(destination) or receipt["requested_url"] != url:
            raise RuntimeError("Existing acquisition receipt mismatch")
        return ref(destination)
    ca = Path("/etc/ssl/cert.pem")
    context = ssl.create_default_context(cafile=str(ca))
    started = now()
    request = urllib.request.Request(url, headers={"User-Agent": "orthopolity-archived-cost-transfer/1.0"})
    with urllib.request.urlopen(request, context=context, timeout=45) as response:
        payload = response.read()
        receipt = dict(requested_url=url, final_url=response.url, http_status=response.status,
                       retrieval_started_utc=started, retrieval_finished_utc=now(),
                       response_headers=dict(response.headers), bytes=len(payload),
                       sha256=hashlib.sha256(payload).hexdigest(),
                       md5=hashlib.md5(payload).hexdigest(),
                       tls=dict(certificate_verification=True, hostname_verification=True,
                                ca_file=str(ca), ca_file_sha256=digest(ca), openssl=ssl.OPENSSL_VERSION))
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(payload)
    save_json(receipt_path, receipt)
    return ref(destination)


def verify_reference(reference):
    if digest(ROOT / reference["path"]) != reference["sha256"]:
        raise RuntimeError(f"Frozen reference changed: {reference['path']}")


def verify_plan():
    plan = read_json(DATA / "frozen-plan.json")
    for reference in [plan["config_reference"], *plan["metadata_references"],
                      *plan["source_references"], *plan["source_snapshot_references"]]:
        verify_reference(reference)
    return plan


def freeze():
    if (DATA / "frozen-plan.json").exists():
        verify_plan()
        return
    if (DATA / "926311_v1_syn-batch-cultures.csv").exists():
        raise RuntimeError("Cannot first freeze after raw CSV acquisition")
    config = read_json(CONFIG)
    metadata = [fetch(config["metadata_url"], DATA / "description.html"),
                fetch(config["catalogue_url"], DATA / "catalogue.html")]
    description = (DATA / "description.html").read_text()
    for field in ["QC", "QN", "QP", "Cell_Diameter_um", "27"]:
        if field not in description:
            raise RuntimeError(f"Metadata does not confirm declared field: {field}")
    sources, snapshots = [], []
    for source in SOURCE_PATHS:
        original = ROOT / source
        snapshot = DATA / "original-sources" / source
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        snapshot.write_bytes(original.read_bytes())
        sources.append(ref(original))
        snapshots.append(ref(snapshot))
    plan = dict(run_id=config["run_id"], frozen_utc=now(), config=config,
                config_reference=ref(CONFIG), metadata_references=metadata,
                source_references=sources, source_snapshot_references=snapshots,
                raw_csv_absent_at_freeze=True, status="frozen_before_acquisition",
                environment=dict(python=sys.version, numpy=np.__version__, platform=platform.platform()),
                git_head_at_freeze=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                scope=config["freeze_scope"])
    save_json(DATA / "frozen-plan.json", plan)


def acquire():
    plan = verify_plan()
    config = plan["config"]
    raw = DATA / "926311_v1_syn-batch-cultures.csv"
    fetch(config["data_url"], raw)
    receipt = read_json(raw.with_suffix(".csv.receipt.json"))
    if receipt["md5"] != config["published_csv_md5"]:
        raise RuntimeError("Acquired bytes do not match repository-published CSV MD5")
    if receipt["retrieval_started_utc"] <= plan["frozen_utc"]:
        raise RuntimeError("Source acquisition did not follow protocol freeze")


def calibrate():
    plan = verify_plan()
    target = DATA / "calibration.json"
    if target.exists():
        calibration = read_json(target)
        verify_reference(calibration["raw_reference"])
        verify_reference(calibration["frozen_plan_reference"])
        return
    raw, config = DATA / "926311_v1_syn-batch-cultures.csv", plan["config"]
    acquire()
    rows = read_cultures(raw, config, view="training")
    training = [r for r in rows if r["split"] == "training"]
    fitted = fit_models(training, config)
    predictor_rows = read_cultures(raw, config, view="predictors")
    forecasts = predictions(predictor_rows, fitted, config)
    membership = [{k: r[k] for k in ["culture_id", "source_line", "strain", "temperature_degC",
                                    "replicate", "split", "diameter_um"]} for r in predictor_rows]
    save_json(DATA / "membership.json", membership)
    save_json(DATA / "training-records.json", training)
    save_json(target, dict(run_id=config["run_id"], frozen_utc=now(),
                          held_out_quota_conversion_performed=False,
                          raw_reference=ref(raw), frozen_plan_reference=ref(DATA / "frozen-plan.json"),
                          membership_reference=ref(DATA / "membership.json"),
                          training_reference=ref(DATA / "training-records.json"),
                          fitted=fitted, validation_predictions=forecasts,
                          forecast_scope=config["forecast_scope"]))


def figure(rows, fitted, scores, config):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                         "svg.hashsalt": config["run_id"]})
    fig, axes = plt.subplots(2, 3, figsize=(13, 8), constrained_layout=True)
    colors = dict(BL107="#0072B2", CC9311="#E69F00", CC9902="#009E73", ROS8604="#CC79A7")
    model_colors = ["#CC6677", "#4477AA", "#228833", "#AA3377"]
    for col, resource in enumerate(config["resources"]):
        axis = axes[0, col]
        for strain, color in colors.items():
            for split, marker in [("training", "o"), ("validation", "^")]:
                group = [r for r in rows if r["strain"] == strain and r["split"] == split and eligible(r, resource)]
                axis.scatter([r["diameter_um"] for r in group], [r["quotas"][resource] for r in group],
                             color=color, marker=marker, s=28, alpha=.8,
                             label=f"{strain} {split}" if col == 0 else None)
        ds = np.geomspace(*fitted[resource]["diameter_range_um"], 80)
        for model, color in zip(config["models"][:2], model_colors[:2]):
            pars = fitted[resource]["models"][model]
            axis.plot(ds, np.exp(pars["log_intercept"]) * ds**pars["coefficient"],
                      color=color, linestyle="--" if model == "fixed_cubic" else "-", linewidth=2)
        axis.set(xscale="log", yscale="log", xlabel="Calibrated diameter (µm)", ylabel=f"{resource} (fmol/cell)",
                 title=f"{resource}: pooled training D={fitted[resource]['models']['pooled_free_power']['coefficient']:.3f}")
        bar = axes[1, col]
        values = [scores[resource]["models"][m]["equal_cell_mean_absolute_log_error"] for m in config["models"]]
        bar.bar(range(4), values, color=model_colors)
        bar.set_xticks(range(4), ["Cubic", "Free power", "Strain mean", "Strain temp."], rotation=20)
        bar.set(ylabel="Held-out mean absolute log error", title=f"{resource}: 25/27°C quota transfer")
    axes[0, 0].legend(fontsize=7, loc="best")
    fig.suptitle("Archived Synechococcus quotas: finite cost scaling and temperature transfer\n"
                 "Training 16/18/20/22°C; whole cultures at 25/27°C held out; no neutrality claim", fontsize=13)
    for extension in ["png", "svg"]:
        fig.savefig(RESULTS / f"cost-transfer.{extension}", dpi=160,
                    metadata={"Date": None} if extension == "svg" else None)
    plt.close(fig)


def evaluate():
    plan = verify_plan()
    if (RESULTS / "study.json").exists():
        audit()
        return
    calibrate()
    calibration = read_json(DATA / "calibration.json")
    for key in ["raw_reference", "frozen_plan_reference", "membership_reference", "training_reference"]:
        verify_reference(calibration[key])
    calibration_ref = ref(DATA / "calibration.json")
    evaluation_started = now()
    if evaluation_started <= calibration["frozen_utc"]:
        raise RuntimeError("Evaluation preceded coefficient freeze")
    config = plan["config"]
    rows = read_cultures(DATA / "926311_v1_syn-batch-cultures.csv", config, view="evaluation")
    scores = score_evaluation(rows, calibration["validation_predictions"], config)
    missingness = {split: {r: dict(total=sum(x["split"] == split for x in rows),
                                  eligible=sum(x["split"] == split and eligible(x, r) for x in rows),
                                  missing_quota=sum(x["split"] == split and x["quotas"][r] is None for x in rows),
                                  missing_diameter=sum(x["split"] == split and x["diameter_um"] is None for x in rows))
                           for r in config["resources"]} for split in ["training", "validation"]}
    report = dict(run_id=config["run_id"], status="complete", evaluation_started_utc=evaluation_started,
                  kind="retrospective_archived_quota_cost_transfer", config=config,
                  frozen_plan=ref(DATA / "frozen-plan.json"), calibration_reference=calibration_ref,
                  raw_reference=ref(DATA / "926311_v1_syn-batch-cultures.csv"),
                  source_references=plan["source_references"], acquisition_reference=ref(DATA / "926311_v1_syn-batch-cultures.csv.receipt.json"),
                  retained_cultures=len(rows), missingness=missingness, fitted=calibration["fitted"], scores=scores,
                  interpretation="Independently published retained elemental quotas conditional on calibrated diameter; finite slopes confound strain and temperature, and are not allocation neutrality, causal dimensionality, uptake fluxes, or a universal law.",
                  statistical_scope="Point prediction errors and descriptive calibration diagnostics only; four strains in one published experiment, no independence-based intervals or significance claims.")
    RESULTS.mkdir(parents=True, exist_ok=True)
    save_json(RESULTS / "study.json", report)
    save_json(DATA / "evaluation-records.json", [r for r in rows if r["split"] == "validation"])
    figure(rows, calibration["fitted"], scores, config)
    retained = [ref(p) for p in sorted(RESULTS.iterdir()) if p.name != "output-manifest.json"]
    save_json(RESULTS / "output-manifest.json", dict(run_id=config["run_id"], artifacts=retained,
                                                   evaluation_reference=ref(DATA / "evaluation-records.json")))


def audit():
    plan = verify_plan()
    calibration = read_json(DATA / "calibration.json")
    for key in ["raw_reference", "frozen_plan_reference", "membership_reference", "training_reference"]:
        verify_reference(calibration[key])
    report = read_json(RESULTS / "study.json")
    for key in ["frozen_plan", "calibration_reference", "raw_reference", "acquisition_reference"]:
        verify_reference(report[key])
    for reference in read_json(RESULTS / "output-manifest.json")["artifacts"]:
        verify_reference(reference)
    verify_reference(read_json(RESULTS / "output-manifest.json")["evaluation_reference"])
    config = plan["config"]
    raw = DATA / "926311_v1_syn-batch-cultures.csv"
    training = [r for r in read_cultures(raw, config, view="training") if r["split"] == "training"]
    if fit_models(training, config) != calibration["fitted"]:
        raise RuntimeError("Training fit replay differed")
    if predictions(read_cultures(raw, config, view="predictors"), calibration["fitted"], config) != calibration["validation_predictions"]:
        raise RuntimeError("Frozen conditional predictions differed")
    if score_evaluation(read_cultures(raw, config, view="evaluation"), calibration["validation_predictions"], config) != report["scores"]:
        raise RuntimeError("Evaluation replay differed")
    return dict(status="verified_offline", run_id=config["run_id"], cultures=report["retained_cultures"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=["freeze", "acquire", "calibrate", "evaluate", "audit"], required=True)
    args = parser.parse_args()
    {"freeze": freeze, "acquire": acquire, "calibrate": calibrate,
     "evaluate": evaluate, "audit": audit}[args.stage]()
    print(json.dumps(dict(stage=args.stage, status="complete", run_id=read_json(CONFIG)["run_id"])))


if __name__ == "__main__":
    main()
