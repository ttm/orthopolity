"""Recompute the retained pilot with Decimal arithmetic, without its model code."""
import argparse
import csv
from decimal import Decimal, localcontext
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data/paired-phosphorus/2026-10-12"


def verify(directory):
    directory = Path(directory)
    result = json.loads((directory / "result.json").read_text())
    execution = json.loads((directory / "execution.json").read_text())
    for item in execution["inputs"]:
        if hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError("Changed pilot source")
    for item in execution["sources"]:
        frozen = subprocess.check_output(["git", "show", f"{execution['freeze_commit']}:{item['path']}"], cwd=ROOT)
        if hashlib.sha256(frozen).hexdigest() != item["sha256"]:
            raise ValueError("Source differs from recorded execution freeze")
    if result["qualification"] != json.loads((BASE / "qualification-before-response.json").read_text()):
        raise ValueError("Qualification changed after response exposure")
    if len(result["targets"]) != 1 or result["n_target_cultures"] != 1:
        raise ValueError("Expected one independent target culture")
    cells = list(csv.DictReader((BASE / "1005186.csv").open()))
    bulk = list(csv.DictReader((BASE / "1005084.csv").open()))
    differences = []

    def check(recorded, expected):
        error = abs(Decimal(str(recorded)) - expected) / max(abs(expected), Decimal("1e-30"))
        if error > Decimal("1e-12"):
            raise ValueError(f"Independent calculation mismatch: relative error {error}")
        differences.append(float(error))

    with localcontext() as context:
        context.prec = 40
        samples = []
        for treatment, day, bottle, recorded in (
                ("High-P", "1", "c", result["calibration"]),
                ("Low-P", "2", "b", result["targets"][0]["sample"])):
            if (recorded["treatment"], str(recorded["day"]), recorded["bottle"]) != (treatment, day, bottle):
                raise ValueError("Wrong retained sample identity")
            rr = [r for r in cells if (r["exp"], r["time"], r["rep"]) == (treatment.replace("-", " "), day, bottle)]
            bb = [r for r in bulk if (r["treatment"], r["day"], r["bottle"]) == (treatment, day, bottle)]
            if len(bb) != 1 or len(rr) != recorded["n_xrma_cells"]:
                raise ValueError("Changed sample match/count")
            quota = sum(Decimal(r["P_fg_cell"]) for r in rr) / len(rr)
            stock, count = Decimal(bb[0]["TPP_value_uM"]), Decimal(bb[0]["cell"])
            raw = stock * Decimal("30.973761998") * Decimal(1_000_000) / quota
            for field, value in (("mean_p_fg", quota), ("tpp_uM", stock), ("observed_cells_ml", count),
                                 ("raw_capacity_cells_ml", raw), ("raw_predicted_over_observed", raw / count)):
                check(recorded[field], value)
            samples.append((quota, stock, count))
        (q0, stock0, n0), (q1, stock1, n1) = samples
        predictions = {"fixed_quota": n0 * stock1 / stock0,
                       "measured_quota": n0 * stock1 * q0 / (stock0 * q1)}
        scores = result["targets"][0]["models"]
        for name, prediction in predictions.items():
            ratio = prediction / n1
            check(scores[name]["predicted_cells_ml"], prediction)
            check(scores[name]["predicted_over_observed"], ratio)
            check(scores[name]["absolute_log_error"], abs(ratio.ln()))
            if scores[name]["within_pilot_factor"] != (Decimal("0.8") <= ratio <= Decimal("1.25")):
                raise ValueError("Wrong pilot accuracy flag")
        improved = abs((predictions["measured_quota"] / n1).ln()) < abs((predictions["fixed_quota"] / n1).ln())
        if result["targets"][0]["measured_improves_on_fixed"] != improved:
            raise ValueError("Wrong improvement flag")
    return dict(verified=True, independently_checked_numbers=len(differences),
                maximum_relative_discrepancy=max(differences),
                qualification_unchanged=True, test_cultures=1,
                method="40-digit Decimal arithmetic from original rows; no analysis-module import")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    verified = verify(args.directory)
    body = json.dumps(verified, indent=2, sort_keys=True) + "\n"
    if args.write:
        (args.directory / "verification.json").write_text(body)
    print(body)
