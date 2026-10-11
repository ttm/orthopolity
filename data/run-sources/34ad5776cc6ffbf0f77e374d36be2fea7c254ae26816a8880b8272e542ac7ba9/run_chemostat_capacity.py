"""Retrospective conditional capacity diagnosis; refuses unfrozen source code."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys

import numpy as np
import scipy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"src"))
from orthopolity.chemostat_capacity import (nitrogen_share_segment, quota_calibration,
                                          ratio_intervals, redistribution_bound,
                                          segment_tv_range)

CONFIG = "configs/chemostat_capacity_followup_2026-10-10.json"
FROZEN_SOURCES = [CONFIG, "docs/chemostat-capacity-followup-protocol-2026-10-10.md",
                  "src/orthopolity/chemostat_capacity.py",
                  "experiments/run_chemostat_capacity.py", "tests/test_chemostat_capacity.py"]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load_json(path):
    return json.loads(Path(path).read_text())


def valid_volumes(row):
    if row is None:
        return False
    raw = row.get("biovolumes")
    if not isinstance(raw, list) or len(raw) != 3 or any(value is None for value in raw):
        return False
    try:
        values = np.asarray(raw, dtype=float)
    except (ValueError, TypeError):
        return False
    return bool(np.all(np.isfinite(values)) and np.all(values >= 0) and values.sum() > 0)


def analyse(config, calibration, records):
    """Pure diagnostic computation, also exercised with synthetic records."""
    if (config["species"] != ["Cr", "Ca", "Mo", "Co"]
            or config["target_days"] != [1, 2, 3]
            or config["baseline_observation_day"] != 0
            or config["modes"] != ["fixed_prepulse_densities", "measured_preliminary_density_changes"]):
        raise ValueError("Unsupported change to the frozen design")
    seen_sources = set()
    vessels = defaultdict(dict)
    metadata = {}
    categories = {config["primary_category"], config["secondary_category"]}
    for row in records:
        if row["source_row"] in seen_sources:
            raise ValueError("Duplicate source row across retained inputs")
        seen_sources.add(row["source_row"])
        vessel = str(row["chemostat"])
        if row["category"] not in categories or not row["decoded"]:
            raise ValueError("Unexpected category or undecoded source row")
        current = (row["category"], row["treatment"])
        if vessel in metadata and metadata[vessel] != current:
            raise ValueError("Conflicting vessel metadata")
        metadata[vessel] = current
        time = float(row["time"])
        if not np.isfinite(time) or time in vessels[vessel]:
            raise ValueError("Invalid or duplicate vessel time")
        vessels[vessel][time] = row
    if len(records) != config["expected_main_records"]:
        raise ValueError("Unexpected total source row count")
    counts = Counter(category for category, _ in metadata.values())
    if any(counts[c] != config["expected_vessels_per_category"] for c in categories):
        raise ValueError("Unexpected number of vessels per category")

    initial = calibration["initial"]
    r0 = ratio_intervals(initial["nitrogen"], initial["carbon"])
    bounds, ledger = [], []
    for mode in config["modes"]:
        for day in config["target_days"]:
            current = (initial if mode == "fixed_prepulse_densities"
                       else calibration["final"][day])
            bound = redistribution_bound(r0, ratio_intervals(current["nitrogen"], current["carbon"]))
            bounds.append(dict(mode=mode, day=day, **bound))
            for vessel in sorted(vessels):
                baseline = vessels[vessel].get(0.)
                target = vessels[vessel].get(float(day))
                row = dict(vessel=vessel, category=metadata[vessel][0], treatment=metadata[vessel][1],
                           mode=mode, day=day,
                           baseline_source_row=baseline["source_row"] if baseline else None,
                           target_source_row=target["source_row"] if target else None,
                           tv_upper=bound["tv_upper"], multiplier_span_upper=bound["multiplier_span_upper"])
                if not valid_volumes(baseline) or not valid_volumes(target):
                    row.update(status="unscored", reason=("unusable_or_absent_baseline"
                               if not valid_volumes(baseline) else "unusable_or_absent_target"))
                else:
                    first = nitrogen_share_segment(baseline["biovolumes"], initial["nitrogen"])
                    second = nitrogen_share_segment(target["biovolumes"], current["nitrogen"])
                    envelope = segment_tv_range(first, second)
                    gap = envelope["minimum_lower_bound"]-bound["tv_upper"]
                    row.update(status="scored", initial_share_segment=first.tolist(),
                               final_share_segment=second.tolist(), observed_tv=envelope,
                               minimum_excess_over_bound=gap,
                               exclusion_basis="feasible_dual_lower_bound_minus_analytic_upper_bound",
                               conditional_bound_exceeded=gap > config["numerical_tolerance"])
                ledger.append(row)
    summaries = []
    for mode in config["modes"]:
        for category in [config["primary_category"], config["secondary_category"]]:
            chosen = [r for r in ledger if r["mode"] == mode and r["category"] == category]
            scored = [r for r in chosen if r["status"] == "scored"]
            exceeded = [r for r in scored if r["conditional_bound_exceeded"]]
            summaries.append(dict(mode=mode, category=category, n_rows=len(chosen),
                                  n_scored=len(scored), n_unscored=len(chosen)-len(scored),
                                  n_rows_exceeding=len(exceeded),
                                  vessels_exceeding=sorted({r["vessel"] for r in exceeded}),
                                  n_vessels_exceeding=len({r["vessel"] for r in exceeded}),
                                  scored_vessels=sorted({r["vessel"] for r in scored})))
    primary = next(s for s in summaries if s["mode"] == config["primary_mode"]
                   and s["category"] == config["primary_category"])
    verdict = ("conditional bound exceeded in recorded primary observations"
               if primary["n_rows_exceeding"] else
               "primary bound not exceeded; model adequacy not established")
    if not primary["n_scored"]:
        verdict = "no usable primary observations"
    return dict(ledger=ledger, bounds=bounds, summary=dict(
        run_id=config["run_id"], evidence_kind=config["evidence_kind"], verdict=verdict,
        primary=primary, comparisons=summaries, n_main_records=len(records),
        prior_exposure=config["prior_exposure"],
        interpretation_limit=config["interpretation_limit"],
        statistical_rejection_claimed=False, prices_or_opportunities_fitted=False,
        original_forecasts_or_verdicts_changed=False))


def verify_freeze(commit):
    records = []
    for name in FROZEN_SOURCES:
        frozen = subprocess.check_output(["git", "show", f"{commit}:{name}"], cwd=ROOT)
        actual = (ROOT/name).read_bytes()
        if frozen != actual:
            raise ValueError("Executed file differs from freeze: "+name)
        records.append(dict(path=name, sha256=digest(actual), size_bytes=len(actual)))
    return records


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+"\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze-commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("Output directory already exists; completed runs cannot be overwritten")
    sources = verify_freeze(args.freeze_commit)
    config = load_json(ROOT/CONFIG)
    inputs = []
    for reference in config["inputs"]:
        raw = (ROOT/reference["path"]).read_bytes()
        if len(raw) != reference["size_bytes"] or digest(raw) != reference["sha256"]:
            raise ValueError("Changed retained source: "+reference["path"])
        inputs.append(json.loads(raw))
    started = datetime.now(timezone.utc).isoformat()
    calibration = quota_calibration(inputs[0]["rows"])
    result = analyse(config, calibration, inputs[1]["main"]+inputs[2])
    args.output.mkdir(parents=True, exist_ok=False)
    for name in ("ledger", "bounds", "summary"):
        write_json(args.output/(name+".json"), result[name])
    write_json(args.output/"quota-calibration.json", calibration)
    execution = dict(freeze_commit=args.freeze_commit, started_at_utc=started,
                     completed_at_utc=datetime.now(timezone.utc).isoformat(),
                     inputs=config["inputs"], sources=sources, python=sys.version,
                     numpy=np.__version__, scipy=scipy.__version__, system=platform.system())
    write_json(args.output/"execution.json", execution)
    print(json.dumps(result["summary"], indent=2))


if __name__ == "__main__":
    main()
