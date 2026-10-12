"""Independent phosphorus assays: sample qualification and conditional counts.

This is a resource-accounting pilot, not a test of equal allocation. Numerical
values from disqualified cultures are never converted or used in predictions.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import math
import re
from statistics import mean

P_MOLAR_MASS = 30.973761998  # g/mol; numerically fg/fmol
MISSING = frozenset(("", "na", "nan", "nd"))
TREATMENTS = {"High P": ("High-P", "1"), "Mid P": ("Mid-P", "2"),
              "Low P": ("Low-P", "3")}


def missing(value):
    return str(value).strip().lower() in MISSING


def key(row):
    return (TREATMENTS[row["exp"]][0], int(row["time"]), row["rep"])


def qualify(cells, bulk, minimum_cells=20):
    """Use identifiers and missingness only; quarantine whole affected samples."""
    ids = Counter(row["SampleID"] for row in cells)
    bulk_counts = Counter((r["treatment"], int(r["day"]), r["bottle"]) for r in bulk)
    groups = defaultdict(list)
    for row in cells:
        groups[key(row)].append(row)
    ledger = []
    for sample, rows in sorted(groups.items()):
        conflicts = []
        duplicates = []
        for row in rows:
            match = re.fullmatch(r"BIO5_EFB_EFB([123])_T(\d+)_([ABC])_(\d+)", row["SampleID"])
            expected = (TREATMENTS[row["exp"]][1], str(int(row["time"])), row["rep"].upper())
            if not match or match.groups()[:3] != expected:
                conflicts.append(row["SampleID"])
            if ids[row["SampleID"]] > 1:
                duplicates.append(row["SampleID"])
        n_missing = sum(missing(row["P_fg_cell"]) for row in rows)
        reasons = []
        if conflicts:
            reasons.append("identifier_field_conflict")
        if duplicates:
            reasons.append("nonunique_cell_identifier")
        if n_missing:
            reasons.append("incomplete_phosphorus_assay")
        if len(rows) < minimum_cells:
            reasons.append("fewer_than_minimum_cells")
        if bulk_counts[sample] != 1:
            reasons.append("bulk_match_not_unique")
        ledger.append(dict(treatment=sample[0], day=sample[1], bottle=sample[2],
                           n_cells=len(rows), n_missing_phosphorus=n_missing,
                           conflicting_ids=sorted(set(conflicts)),
                           duplicate_ids=sorted(set(duplicates)),
                           eligible=not reasons, exclusion_reasons=reasons))
    return ledger


def positive(value):
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise ValueError("An eligible measurement is nonpositive or nonfinite")
    return number


def predict(calibration, target):
    """No target count enters a prediction; Q is measured current stock, not feed."""
    multiplier = calibration["observed_cells_ml"] * target["tpp_uM"] / calibration["tpp_uM"]
    predictions = {
        "fixed_quota": multiplier,
        "measured_quota": multiplier * calibration["mean_p_fg"] / target["mean_p_fg"],
    }
    return predictions


def analyse(cells, bulk, config):
    ledger = qualify(cells, bulk, config["minimum_cells"])
    eligible_keys = {(r["treatment"], r["day"], r["bottle"]) for r in ledger if r["eligible"]}
    expected_keys = {tuple(k) for k in config["expected_eligible_keys"]}
    if eligible_keys != expected_keys:
        raise ValueError("Eligibility differs from the frozen identifier/missingness audit")
    samples = []
    for sample in sorted(eligible_keys):
        rows = [r for r in cells if key(r) == sample]
        target = next(r for r in bulk if (r["treatment"], int(r["day"]), r["bottle"]) == sample)
        # Only complete, unambiguous samples reach this point. No per-cell quota
        # calculated from bulk chemistry divided by the response count is used.
        p_fg = mean(positive(r["P_fg_cell"]) for r in rows)
        tpp = positive(target["TPP_value_uM"])
        observed = positive(target["cell"])
        raw_prediction = tpp * P_MOLAR_MASS * 1e6 / p_fg
        samples.append(dict(treatment=sample[0], day=sample[1], bottle=sample[2],
                            n_xrma_cells=len(rows), mean_p_fg=p_fg,
                            tpp_uM=tpp, observed_cells_ml=observed,
                            raw_capacity_cells_ml=raw_prediction,
                            raw_predicted_over_observed=raw_prediction / observed))
    calibration_key = tuple(config["calibration_key"])
    calibration = next(s for s in samples if (s["treatment"], s["day"], s["bottle"]) == calibration_key)
    targets = []
    for sample in samples:
        if sample is calibration:
            continue
        predictions = predict(calibration, sample)
        scores = {}
        for name, prediction in predictions.items():
            ratio = prediction / sample["observed_cells_ml"]
            scores[name] = dict(predicted_cells_ml=prediction, predicted_over_observed=ratio,
                               absolute_log_error=abs(math.log(ratio)),
                               within_pilot_factor=1 / config["pilot_factor"] <= ratio <= config["pilot_factor"])
        targets.append(dict(sample=sample, models=scores,
                            measured_improves_on_fixed=(scores["measured_quota"]["absolute_log_error"]
                                                       < scores["fixed_quota"]["absolute_log_error"])))
    return dict(run_id=config["run_id"], qualification=ledger, calibration=calibration,
                targets=targets, n_target_cultures=len(targets),
                inference_scope="Conditional measurement-transfer pilot; no equal-allocation test, confidence interval, or population-level verdict",
                uncertainty="Cell sampling, bulk-assay error, preparation losses and instrument calibration are not quantified")
