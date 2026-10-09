"""Frozen retrospective quota transfer from independently published culture data.

The training and predictor readers deliberately do not convert held-out quota
columns. Published quotas are retained elemental stocks per counted cell; they
are not uptake fluxes or energy spent making a cell.
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

import numpy as np


def numeric(value):
    """Preserve reported missingness and reject accidental nonfinite values."""
    text = str(value).strip()
    if text.lower() in {"", "na", "n/a", "nan", "none"}:
        return None
    result = float(text)
    if not math.isfinite(result):
        raise ValueError("Nonfinite source number")
    return result


def read_cultures(path: str | Path, config: dict, *, view: str) -> list[dict]:
    """Read training quotas, validation predictors, or evaluation quotas.

    The predictor view never accesses quota columns. The training view returns
    quota=None for all held-out cultures without calling numeric on their text.
    Whole cultures are assigned by metadata-defined temperature, not values.
    """
    if view not in {"training", "predictors", "evaluation"}:
        raise ValueError("Unknown source view")
    train = set(config["training_temperatures_degC"])
    valid = set(config["validation_temperatures_degC"])
    if train & valid:
        raise ValueError("Training and validation temperatures overlap")
    rows, seen = [], set()
    with Path(path).open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        required = {"Temp", "Rep", "Strain", config["coordinate"], *config["resources"]}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError(f"Missing source columns: {sorted(required - set(reader.fieldnames or []))}")
        for line, source in enumerate(reader, start=2):
            temperature = numeric(source["Temp"])
            if temperature not in train | valid:
                raise ValueError(f"Unspecified temperature at source line {line}: {temperature}")
            strain = source["Strain"].strip()
            if strain not in config["strains"]:
                raise ValueError(f"Unspecified strain: {strain}")
            replicate = source["Rep"].strip()
            if not replicate:
                raise ValueError("Missing biological replicate identity")
            key = f"{strain}:{temperature:g}:{replicate}"
            if key in seen:
                raise ValueError(f"Duplicate culture: {key}")
            seen.add(key)
            split = "training" if temperature in train else "validation"
            quota = {r: None for r in config["resources"]}
            convert = view == "evaluation" or (view == "training" and split == "training")
            if convert:
                quota = {r: numeric(source[r]) for r in config["resources"]}
            rows.append(dict(culture_id=key, source_line=line, strain=strain,
                             temperature_degC=temperature, replicate=replicate,
                             split=split, diameter_um=numeric(source[config["coordinate"]]),
                             quotas=quota))
    return rows


def eligible(row: dict, resource: str) -> bool:
    d, q = row["diameter_um"], row["quotas"][resource]
    return d is not None and q is not None and d > 0 and q > 0


def _linear(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    matrix = np.column_stack([np.ones(len(x)), x])
    if len(x) < 2 or np.linalg.matrix_rank(matrix) != 2:
        raise ValueError("Insufficient predictor variation for linear fit")
    intercept, slope = np.linalg.lstsq(matrix, y, rcond=None)[0]
    return dict(log_intercept=float(intercept), coefficient=float(slope))


def fit_models(rows: list[dict], config: dict) -> dict:
    if any(r["split"] != "training" for r in rows):
        raise ValueError("Fit input must contain only training cultures")
    fitted = {}
    for resource in config["resources"]:
        usable = [r for r in rows if eligible(r, resource)]
        if not usable:
            raise ValueError(f"No eligible training cultures for {resource}")
        x = np.log([r["diameter_um"] for r in usable])
        y = np.log([r["quotas"][resource] for r in usable])
        cubic = dict(log_intercept=float(np.mean(y - 3 * x)), coefficient=3.)
        power = _linear(x, y)
        means, trends, within_x, within_y = {}, {}, [], []
        for strain in config["strains"]:
            strain_rows = [r for r in usable if r["strain"] == strain]
            if not strain_rows:
                raise ValueError(f"No eligible training cultures for {strain}, {resource}")
            sx = np.log([r["diameter_um"] for r in strain_rows])
            sy = np.log([r["quotas"][resource] for r in strain_rows])
            means[strain] = dict(log_intercept=float(np.mean(sy)))
            trends[strain] = _linear([r["temperature_degC"] for r in strain_rows], sy)
            within_x.extend(sx - sx.mean())
            within_y.extend(sy - sy.mean())
        denominator = float(np.sum(np.asarray(within_x) ** 2))
        adjusted = float(np.dot(within_x, within_y) / denominator) if denominator > 0 else None
        leave_out = {}
        for strain in config["strains"]:
            other = [r for r in usable if r["strain"] != strain]
            leave_out[strain] = _linear(np.log([r["diameter_um"] for r in other]),
                                       np.log([r["quotas"][resource] for r in other]))["coefficient"]
        fitted[resource] = dict(
            eligible_training_rows=len(usable), training_culture_ids=[r["culture_id"] for r in usable],
            diameter_range_um=[float(np.exp(x.min())), float(np.exp(x.max()))],
            models=dict(fixed_cubic=cubic, pooled_free_power=power,
                        strain_geometric_mean=means, strain_temperature_trend=trends),
            diagnostics=dict(within_strain_demeaned_cost_degree=adjusted,
                             leave_one_strain_out_pooled_cost_degrees=leave_out,
                             inference="Finite observed calibration slopes; no confidence or asymptotic dimension claim"))
    return fitted


def predict(row: dict, fitted: dict, model: str) -> float:
    """Evaluate log-quota prediction without consulting row quotas."""
    parameters = fitted["models"][model]
    if model in {"fixed_cubic", "pooled_free_power"}:
        diameter = row["diameter_um"]
        if diameter is None or diameter <= 0:
            raise ValueError("Positive measured diameter required")
        return parameters["log_intercept"] + parameters["coefficient"] * math.log(diameter)
    if model == "strain_geometric_mean":
        return parameters[row["strain"]]["log_intercept"]
    if model == "strain_temperature_trend":
        item = parameters[row["strain"]]
        return item["log_intercept"] + item["coefficient"] * row["temperature_degC"]
    raise ValueError("Unknown prediction model")


def predictions(rows: list[dict], fitted: dict, config: dict) -> list[dict]:
    result = []
    for row in rows:
        if row["split"] != "validation":
            continue
        for resource in config["resources"]:
            diameter = row["diameter_um"]
            available = diameter is not None and diameter > 0
            logs = {m: predict(row, fitted[resource], m) for m in config["models"]} if available else None
            result.append(dict(culture_id=row["culture_id"], strain=row["strain"],
                               temperature_degC=row["temperature_degC"], diameter_um=diameter,
                               resource=resource, predicted_log_quota=logs,
                               predicted_quota_fmol_per_cell={m: math.exp(v) for m, v in logs.items()} if logs else None))
    return result


def score_evaluation(rows: list[dict], frozen_predictions: list[dict], config: dict) -> dict:
    held = {r["culture_id"]: r for r in rows if r["split"] == "validation"}
    scores = {}
    for resource in config["resources"]:
        errors, excluded = [], []
        for forecast in frozen_predictions:
            if forecast["resource"] != resource:
                continue
            row = held[forecast["culture_id"]]
            if not eligible(row, resource):
                excluded.append(dict(culture_id=row["culture_id"], diameter_um=row["diameter_um"],
                                     observed_quota=row["quotas"][resource]))
                continue
            observed = row["quotas"][resource]
            errors.append(dict(culture_id=row["culture_id"], strain=row["strain"],
                               temperature_degC=row["temperature_degC"], diameter_um=row["diameter_um"],
                               observed_quota_fmol_per_cell=observed,
                               predicted_quota_fmol_per_cell=forecast["predicted_quota_fmol_per_cell"],
                               log_error={m: forecast["predicted_log_quota"][m] - math.log(observed)
                                          for m in config["models"]}))
        if not errors:
            raise ValueError("No eligible evaluation cultures")
        cells = sorted({(e["strain"], e["temperature_degC"]) for e in errors})
        summaries = {}
        for model in config["models"]:
            cell_summaries = []
            for strain, temperature in cells:
                values = np.asarray([e["log_error"][model] for e in errors
                                     if e["strain"] == strain and e["temperature_degC"] == temperature])
                cell_summaries.append(dict(strain=strain, temperature_degC=temperature, rows=len(values),
                                           mean_absolute_log_error=float(np.mean(abs(values))),
                                           mean_squared_log_error=float(np.mean(values**2))))
            mae = float(np.mean([c["mean_absolute_log_error"] for c in cell_summaries]))
            rmse = float(np.sqrt(np.mean([c["mean_squared_log_error"] for c in cell_summaries])))
            summaries[model] = dict(equal_cell_mean_absolute_log_error=mae,
                                    geometric_absolute_error_factor=math.exp(mae),
                                    equal_cell_root_mean_squared_log_error=rmse,
                                    maximum_absolute_log_error=max(abs(e["log_error"][model]) for e in errors),
                                    cells=cell_summaries)
        scores[resource] = dict(eligible_validation_rows=len(errors), observed_cells=len(cells),
                               excluded=excluded, models=summaries, rows=errors,
                               ranking_by_primary_error=sorted(config["models"], key=lambda m: summaries[m]["equal_cell_mean_absolute_log_error"]))
    return scores
