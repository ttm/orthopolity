"""Freeze, execute and audit a calibration-only cost discrimination gate.

Reads the previously exposed monoculture JSON ledger only. No XLSX worksheet
is opened. All signed rates remain in group means; no community law is scored.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
from pathlib import Path
import platform
import subprocess

import numpy as np
import scipy

from orthopolity.cost_calibration import (
    fit_cost_curve, moment_predictions, predict_cost, summarize_calibration,
)
from orthopolity.run_registry import archive_reference, file_reference, register_run, verify_registry

ROOT = Path(__file__).resolve().parents[1]
CONFIG = "configs/ghedini_cost_calibration_2026-10-05.json"
DATA = "data/ghedini-cost-calibration/2026-10-05"
OUTPUT = "results/ghedini-cost-calibration"
MODELS = ("power", "additive")
WEIGHTINGS = ("equal_groups", "species_rms")


def encode(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def read(relative):
    return json.loads((ROOT / relative).read_text())


def keep(relative, value):
    path = ROOT / relative
    body = encode(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_bytes() != body:
        raise ValueError(f"Refusing to change retained output: {relative}")
    if not path.exists():
        path.write_bytes(body)


def checked(reference, *, live_source=False):
    relative = reference["original_path"] if live_source else reference["path"]
    actual = file_reference(ROOT, relative)
    if actual["sha256"] != reference["sha256"]:
        raise ValueError(f"Frozen source changed: {relative}")
    return reference


def software():
    return dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__)


def group_id(group):
    return f"{group['species']}|OD={group['od']:.12g}"


def make_folds(groups):
    """Partitions depend only on species/assay metadata, never response values."""
    species = sorted({g["species"] for g in groups})
    ods = sorted({g["od"] for g in groups})
    by_species = {s: {g["volume_um3"] for g in groups if g["species"] == s} for s in species}
    if any(len(values) != 1 for values in by_species.values()):
        raise ValueError("This protocol requires one fixed calibration size per species")
    sizes = {s: next(iter(values)) for s, values in by_species.items()}
    minimum, maximum = min(sizes.values()), max(sizes.values())
    result = []
    for kind, values, key in (("species", species, "species"), ("optical_density", ods, "od")):
        for value in values:
            result.append(dict(
                fold_id=f"{kind}:{value}", kind=kind, heldout_value=value,
                extrapolation=kind == "species" and sizes[value] in (minimum, maximum),
                training_ids=[group_id(g) for g in groups if g[key] != value],
                evaluation_ids=[group_id(g) for g in groups if g[key] == value],
            ))
    return result


def selected(groups, ids):
    wanted = set(ids)
    result = [g for g in groups if group_id(g) in wanted]
    if {group_id(g) for g in result} != wanted:
        raise ValueError("Fold contains unknown group membership")
    return result


def evaluate_fold(groups, fold, model, weighting, config):
    training = selected(groups, fold["training_ids"])
    evaluation = selected(groups, fold["evaluation_ids"])
    fitted = fit_cost_curve(training, model=model, weighting=weighting, config=config)
    forecasts = predict_cost(fitted, [g["volume_um3"] for g in evaluation], [g["od"] for g in evaluation])
    predictions = [dict(group_id=group_id(g), species=g["species"], od=g["od"],
                        volume_um3=g["volume_um3"], observed_mean_rate=g["mean_rate"],
                        observed_sd_rate=g["sd_rate"], predicted_rate=float(prediction),
                        residual_rate=float(prediction) - g["mean_rate"])
                   for g, prediction in zip(evaluation, forecasts)]
    return dict(fold=fold, fit=fitted, predictions=predictions, scores=scores(predictions))


def scores(predictions):
    if not predictions:
        raise ValueError("No held-out group predictions")
    species = sorted({p["species"] for p in predictions})
    scales = {s: max(1e-15, math.sqrt(math.fsum(
        p["observed_mean_rate"]**2 + (p["observed_sd_rate"] or 0.0)**2
        for p in predictions if p["species"] == s) / sum(p["species"] == s for p in predictions)))
        for s in species}
    balanced = math.fsum(math.fsum((p["residual_rate"] / scales[s])**2
                                  for p in predictions if p["species"] == s)
                         / sum(p["species"] == s for p in predictions) for s in species) / len(species)
    return dict(groups=len(predictions), raw_rate_rmse=math.sqrt(math.fsum(p["residual_rate"]**2 for p in predictions) / len(predictions)),
                species_balanced_scale_rmse=math.sqrt(balanced), evaluation_species_scales=scales)


def comparison(power, additive):
    baseline, candidate = power["raw_rate_rmse"], additive["raw_rate_rmse"]
    improvement = 1.0 - candidate / baseline if baseline > 0 else (0.0 if candidate == 0 else None)
    return dict(power=power, additive=additive, additive_fractional_rmse_improvement=improvement)


def moment_separation(robust, thresholds):
    """Require both paired contrast and separation across calibration scenarios."""
    gap = min(r["relative_gap"] for r in robust)
    ranges = {key: [min(r[key] for r in robust), max(r[key] for r in robust)] for key in ("m_S", "m_Q")}
    crossfit_gap = ranges["m_Q"][0] / ranges["m_S"][1] - 1.0
    return [dict(name="robust_moment_separation", passed=gap >= thresholds["minimum_relative_moment_separation"],
                 value=gap, required=thresholds["minimum_relative_moment_separation"]),
            dict(name="robust_crossfit_range_separation",
                 passed=crossfit_gap >= thresholds["minimum_relative_crossfit_range_separation"],
                 value=crossfit_gap, required=thresholds["minimum_relative_crossfit_range_separation"],
                 sensitivity_ranges_um3=ranges)]


def freeze():
    if (ROOT / DATA / "frozen-plan.json").exists():
        return load_plan()
    config = read(CONFIG)
    source = config["input"]
    checked(source)
    rows = read(source["path"])
    groups = summarize_calibration(rows)
    if len(groups) != 24 or len({g["species"] for g in groups}) != 6:
        raise ValueError("Calibration membership differs from the inspected source")
    folds = make_folds(groups)
    keep(f"{DATA}/group-ledger.json", groups)
    keep(f"{DATA}/fold-membership.json", folds)
    refs = {name: file_reference(ROOT, source[name]) for name in ("raw_source", "raw_source_receipt")}
    refs["calibration_rows"] = file_reference(ROOT, source["path"])
    refs["group_ledger"] = file_reference(ROOT, f"{DATA}/group-ledger.json")
    refs["fold_membership"] = file_reference(ROOT, f"{DATA}/fold-membership.json")
    refs["prior_exposure"] = archive_reference(ROOT, "data/measure-candidates/2026-10-04/exposure.json")
    plan = dict(run_id=config["run_id"], created_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
                client_date="2026-10-05", config_reference=archive_reference(ROOT, CONFIG),
                source_references=[archive_reference(ROOT, path) for path in config["sources_to_freeze"]],
                input_references=refs, software=software(),
                git_head_at_freeze=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                scope="Calibration observations already exposed; analysis choices recorded before fitting. No community observations read.")
    keep(f"{DATA}/frozen-plan.json", plan)
    return plan


def load_plan():
    plan = read(f"{DATA}/frozen-plan.json")
    checked(plan["config_reference"])
    checked(plan["config_reference"], live_source=True)
    for reference in plan["source_references"]:
        checked(reference)
        checked(reference, live_source=True)
    for reference in plan["input_references"].values():
        checked(reference)
    if software() != plan["software"]:
        raise ValueError("Use the software versions retained in the frozen plan")
    return plan


def analyze(plan):
    config = read(CONFIG)
    groups = read(f"{DATA}/group-ledger.json")
    folds = read(f"{DATA}/fold-membership.json")
    all_fits, ledger, moment_rows, metric_rows = {}, [], [], {}
    domain = config["diagnostic_domain_um3"]
    for weighting in WEIGHTINGS:
        fits = {model: fit_cost_curve(groups, model=model, weighting=weighting, config=config) for model in MODELS}
        fold_results = {model: [] for model in MODELS}
        for fold in folds:
            for model in MODELS:
                result = evaluate_fold(groups, fold, model, weighting, config)
                fold_results[model].append(result)
                for prediction in result["predictions"]:
                    ledger.append(dict(weighting=weighting, model=model, fold_id=fold["fold_id"],
                                       fold_kind=fold["kind"], extrapolation=fold["extrapolation"], **prediction))
        conditions = []
        for od in sorted({g["od"] for g in groups}):
            data = [g for g in groups if g["od"] == od]
            conditions.append(dict(od=od, fits={model: fit_cost_curve(data, model=model, weighting=weighting,
                                                                   config=config, fit_density=False) for model in MODELS}))
        metrics = {}
        for label, selector in (
            ("species_all", lambda f: f["kind"] == "species"),
            ("species_interior", lambda f: f["kind"] == "species" and not f["extrapolation"]),
            ("species_endpoints", lambda f: f["kind"] == "species" and f["extrapolation"]),
            ("optical_density", lambda f: f["kind"] == "optical_density"),
        ):
            by_model = {model: scores([p for r in fold_results[model] if selector(r["fold"]) for p in r["predictions"]]) for model in MODELS}
            metrics[label] = comparison(by_model["power"], by_model["additive"])
        metric_rows[weighting] = metrics
        all_fits[weighting] = dict(full=fits, folds=fold_results, separate_conditions=conditions)
        for model in MODELS:
            cases = [("full", fits[model], True)]
            cases += [(r["fold"]["fold_id"], r["fit"], not r["fold"]["extrapolation"]) for r in fold_results[model]]
            cases += [(f"separate_OD:{r['od']}", r["fits"][model], True) for r in conditions]
            for case, fit, in_gate in cases:
                candidates = [("best", fit)]
                candidates += [(f"near_optimal:{i}", candidate) for i, candidate in enumerate(fit["near_optimal_candidates"])]
                for candidate_name, candidate in candidates:
                    moment_rows.append(dict(weighting=weighting, model=model, case=case, candidate=candidate_name,
                                            in_robust_gate=in_gate, bound_flags=candidate["bound_flags"],
                                            **moment_predictions(candidate, domain)))
    criteria = []
    thresholds = config["numerical_gate"]
    for weighting in WEIGHTINGS:
        gain = metric_rows[weighting]["species_all"]["additive_fractional_rmse_improvement"]
        criteria.append(dict(name=f"{weighting}:species_prediction", passed=gain is not None and gain >= thresholds["minimum_species_cv_rmse_improvement"],
                             value=gain, required=thresholds["minimum_species_cv_rmse_improvement"]))
        density = metric_rows[weighting]["optical_density"]
        criteria.append(dict(name=f"{weighting}:condition_prediction", passed=density["additive"]["raw_rate_rmse"] <= density["power"]["raw_rate_rmse"],
                             value=density["additive_fractional_rmse_improvement"], required="not worse"))
    robust = [r for r in moment_rows if r["model"] == "additive" and r["in_robust_gate"]]
    criteria.extend(moment_separation(robust, thresholds))
    technical = [dict(weighting=w, case=case, flags=fit["bound_flags"]["technical"])
                 for w, bundle in all_fits.items()
                 for case, fit in [("full", bundle["full"]["additive"])]
                    + [(r["fold"]["fold_id"], r["fit"]) for r in bundle["folds"]["additive"] if not r["fold"]["extrapolation"]]
                    + [(f"separate_OD:{r['od']}", r["fits"]["additive"]) for r in bundle["separate_conditions"]]
                 if fit["bound_flags"]["technical"]]
    criteria.append(dict(name="technical_boundaries", passed=not technical, value=technical, required="none"))
    passed = all(c["passed"] for c in criteria)
    return dict(run_id=config["run_id"], status="complete", frozen_plan=file_reference(ROOT, f"{DATA}/frozen-plan.json"),
                scope=config["scope"], software=software(), group_count=len(groups), species_count=6,
                fits=all_fits, predictive_metrics=metric_rows,
                gate=dict(passed=passed, label=thresholds["pass_label" if passed else "fail_label"], criteria=criteria,
                          community_evaluation_ready=False, remaining_requirements=thresholds["remaining_requirements_even_if_passed"]),
                sensitivity_ranges_are_confidence_intervals=False, community_numerical_rows_read=False), ledger, moment_rows


def run():
    plan = load_plan()
    report, predictions, moments = analyze(plan)
    keep(f"{OUTPUT}/heldout-predictions.json", predictions)
    keep(f"{OUTPUT}/moment-sensitivity.json", moments)
    keep(f"{OUTPUT}/study.json", report)
    return dict(run_id=report["run_id"], status=report["status"], gate=report["gate"], predictive_metrics=report["predictive_metrics"])


def audit():
    plan = load_plan()
    observed = analyze(plan)
    for name, actual in zip(("study.json", "heldout-predictions.json", "moment-sensitivity.json"), observed):
        if (ROOT / OUTPUT / name).read_bytes() != encode(actual):
            raise ValueError(f"Numerical replay differs: {name}")
    return dict(run_id=plan["run_id"], exact_replay=True, community_numerical_rows_read=False)


def register():
    replay = audit()
    plan = load_plan()
    report = read(f"{OUTPUT}/study.json")
    checked(report["frozen_plan"])
    if report["status"] != "complete" or report["run_id"] != plan["run_id"]:
        raise ValueError("Only this completed calibration gate can be registered")
    artifacts = [file_reference(ROOT, path.relative_to(ROOT).as_posix())
                 for path in sorted((ROOT / OUTPUT).iterdir())
                 if path.is_file() and path.name != ".DS_Store"]
    algorithms = [dict(name="Signed-cost calibration gate with whole-species/OD validation; numerical community outcomes excluded",
                       sources=plan["source_references"])]
    presentation_source = "experiments/report_ghedini_cost_calibration.py"
    if (ROOT / presentation_source).is_file():
        algorithms.append(dict(name="Post-analysis figure from retained calibration results; no fitting",
                               sources=[archive_reference(ROOT, presentation_source)]))
    inputs = list(plan["input_references"].values()) + [file_reference(ROOT, f"{DATA}/frozen-plan.json")]
    entry = dict(schema_version=1, run_id=plan["run_id"], evidence_kind="actual_measurement",
                 resources=[dict(name="Dark respiration cost calibration", units="micromoles O2 per minute per cell",
                                 definition="Published blank-corrected monoculture oxygen consumption divided by calibration cell count; signed assay observations of a positive expected flux, not a nutrient stock or measured community allocation")],
                 generated_seeds=dict(status="Deterministic multistart fitting, deletion sensitivity and quadrature; no random seed"),
                 hardware_metadata=dict(scope="Reanalysis of existing biological data; no new hardware measurements", software=software()),
                 data_inputs=inputs, configs=[plan["config_reference"]],
                 algorithms=algorithms,
                 artifacts=artifacts,
                 relationships=[dict(run_id="archived-cost-transfer-2026-10-02", type="extends_independent_cost_calibration_to_phytoplankton_respiration")],
                 summary=dict(scope=report["scope"], gate=report["gate"], predictive_metrics=report["predictive_metrics"],
                              groups=report["group_count"], species=report["species_count"], community_numerical_rows_read=False))
    result = register_run(ROOT, entry)
    keep(f"{DATA}/registry-entry.json", {key: value for key, value in result.items() if key != "appended"})
    return dict(registration=result, exact_replay=replay["exact_replay"], registry=verify_registry(ROOT))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=["freeze", "run", "audit", "register"], default="audit")
    stage = parser.parse_args().stage
    result = {"freeze": freeze, "run": run, "audit": audit, "register": register}[stage]()
    if stage == "freeze":
        result = dict(run_id=result["run_id"], frozen_plan=f"{DATA}/frozen-plan.json", no_fit_computed=True)
    print(json.dumps(result, indent=2, allow_nan=False))
