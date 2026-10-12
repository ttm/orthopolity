"""Independently replay field-stock records using original strings and Decimal.

This verifier does not import the stock-analysis module.  Its synthetic tests
need no field-response values; the CLI is run only after the frozen evaluation.
"""
import argparse
import csv
from datetime import date
from decimal import Decimal, InvalidOperation, localcontext
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BASE = "data/field-resources/2026-10-12"
CONFIG = "configs/field_resources_2026-10-12.json"
AUDIT = BASE + "/qualification-before-response.json"
GROUPS = ("Prochlorococcus", "Synechococcus")
FIELDS = {
    "NH1418": {"dataset": "829895", "cruise": "Cruise", "station": "Station",
               "depth": "Depth", "date": "ISO_DateTime_UTC", "lat": "Latitude",
               "lon": "Longitude", "counts": GROUPS, "elements": ("C", "N", "P")},
    "AE1319": {"dataset": "538091", "cruise": "cruise_id", "station": "station",
               "depth": "depth", "date": "date", "lat": "lat", "lon": "lon",
               "counts": ("Pro", "Syn"), "elements": ("C", "N")},
}


def decimal_value(raw, *, count=False):
    """Reproduce the declared validity categories independently of float parsing."""
    if str(raw).strip().lower() in ("", "nd", "na", "nan", "null", "none"):
        return None, "missing"
    try:
        value = Decimal(str(raw))
    except (InvalidOperation, TypeError, ValueError):
        return None, "unparseable"
    if not value.is_finite():
        return None, "nonfinite"
    if value < 0 or (value == 0 and not count):
        return None, "negative" if count else "nonpositive"
    return value, None


def reconstruct_element(quota, bulk, fields, element):
    terms, omitted = [], []
    for group, count_column in zip(GROUPS, fields["counts"]):
        quota_column = group + "_PO" + element
        if quota_column == "Prochlorococcus_PON":
            quota_column = "Prochlorcoccus_PON"  # Published header's spelling.
        q, q_reason = decimal_value(quota[quota_column])
        n, n_reason = decimal_value(bulk[count_column], count=True)
        if q_reason or n_reason:
            omitted.append(dict(group=group, quota_reason=q_reason, count_reason=n_reason))
        else:
            terms.append(dict(group=group, quota_fmol_cell=q, count_cells_ml=n,
                              stock_uM=q * n / Decimal(1_000_000)))
    stock = sum((term["stock_uM"] for term in terms), Decimal(0))
    b, b_reason = decimal_value(bulk["PO" + element])
    scored = bool(terms) and b_reason is None
    output = dict(element=element, terms=terms, omitted=omitted, bulk_uM=b,
                  partial_stock_uM=stock if terms else None,
                  status="scored" if scored else "unscored",
                  unscored_reason=b_reason or ("no_valid_group" if not terms else None))
    if scored:
        output.update(partial_over_bulk=stock / b, exceeds_bulk=stock > b,
                      maximum_common_minimum_retention=min(Decimal(1), b / stock) if stock else Decimal(1),
                      minimum_symmetric_relative_allowance=max(Decimal(0), (stock - b) / (stock + b)))
    return output


def compare(recorded, expected, discrepancies, path="result"):
    """Require exact structure/flags and 1e-12 relative numerical agreement."""
    if isinstance(expected, Decimal):
        if isinstance(recorded, bool) or not isinstance(recorded, (int, float)):
            raise ValueError(f"Expected numerical value at {path}")
        actual = Decimal(str(recorded))
        if not actual.is_finite():
            raise ValueError(f"Nonfinite recorded value at {path}")
        error = abs(actual - expected) / max(abs(expected), Decimal("1e-30"))
        if error > Decimal("1e-12"):
            raise ValueError(f"Independent calculation mismatch at {path}: relative error {error}")
        discrepancies.append(float(error))
    elif isinstance(expected, dict):
        if not isinstance(recorded, dict) or set(recorded) != set(expected):
            raise ValueError(f"Changed fields at {path}")
        for key, value in expected.items():
            compare(recorded[key], value, discrepancies, path + "." + key)
    elif isinstance(expected, list):
        if not isinstance(recorded, list) or len(recorded) != len(expected):
            raise ValueError(f"Changed list membership at {path}")
        for index, value in enumerate(expected):
            compare(recorded[index], value, discrepancies, f"{path}[{index}]")
    elif type(recorded) is not type(expected) or recorded != expected:
        raise ValueError(f"Changed categorical value at {path}")


def summary(samples):
    records = [element for sample in samples for element in sample["elements"]
               if element["status"] == "scored"]
    by_element = {}
    for symbol in ("C", "N", "P"):
        relevant = [element for element in records if element["element"] == symbol]
        by_element[symbol] = {"scored": len(relevant),
                              "exceeding": len([element for element in relevant if element["exceeds_bulk"]])}
    return {"samples": len(samples),
            "stations": len({(sample["cruise"], sample["station"]) for sample in samples}),
            "scored_elements": len(records),
            "exceeding_elements": sum(element["exceeds_bulk"] for element in records),
            "samples_with_excess": sum(any(element.get("exceeds_bulk", False)
                                           for element in sample["elements"]) for sample in samples),
            "by_element": by_element}


def check_selected_metadata(match, quota, bulk, fields, tolerance):
    for field, source in (("cruise", "Cruise_ID"), ("station", "Station"), ("depth_m", "Depth"),
                          ("quota_date", "Date"), ("quota_lat", "Latitude"), ("quota_lon", "Longitude")):
        if match[field] != quota[source]:
            raise ValueError(f"Quota metadata mismatch: {field}")
    if (match["bulk_dataset"] != fields["dataset"]
            or match["cruise"] != bulk[fields["cruise"]]
            or Decimal(quota["Station"]) != Decimal(bulk[fields["station"]])
            or Decimal(quota["Depth"]) != Decimal(bulk[fields["depth"]])):
        raise ValueError("Selected bulk identity differs from quota")
    for field, source in (("bulk_date", "date"), ("bulk_lat", "lat"), ("bulk_lon", "lon")):
        if match[field] != bulk[fields[source]]:
            raise ValueError(f"Bulk metadata mismatch: {field}")
    days = (date.fromisoformat(bulk[fields["date"]][:10]) - date.fromisoformat(quota["Date"])).days
    if days != match["date_offset_days"]:
        raise ValueError("Incorrect date offset")
    if match["status"] == "primary" and days != 0:
        raise ValueError("Primary sample has a different date")
    if match["status"] == "date_offset_sensitivity" and abs(days) != 1:
        raise ValueError("Sensitivity sample lacks a one-day offset")
    for name, source, quota_field in (("latitude", "lat", "Latitude"), ("longitude", "lon", "Longitude")):
        difference = abs(Decimal(bulk[fields[source]]) - Decimal(quota[quota_field]))
        if difference > tolerance or difference != Decimal(match[name + "_difference_degrees"]):
            raise ValueError("Changed coordinate qualification")


def verify_records(result, qualification, config, quotas, tables):
    """Check all retained records and summaries; usable with synthetic fixtures."""
    if result["qualification"] != qualification:
        raise ValueError("Qualification changed after response exposure")
    if result["run_id"] != config["run_id"]:
        raise ValueError("Wrong run identity")
    for status, rows in config["expected_quota_rows"].items():
        if [r["quota_row"] for r in qualification["records"] if r["status"] == status] != rows:
            raise ValueError("Changed configured membership")
    selected = [r for r in qualification["records"] if r["status"] in ("primary", "date_offset_sensitivity")]
    if len({r["quota_row"] for r in selected}) != len(selected):
        raise ValueError("Reused selected quota identity")
    if len({(r["bulk_dataset"], r["bulk_row"]) for r in selected}) != len(selected):
        raise ValueError("Reused selected bulk identity")
    expected, discrepancies = [], []
    with localcontext() as context:
        context.prec = 40
        for match in selected:
            fields = FIELDS[match["cruise"]]
            quota, bulk = quotas[match["quota_row"] - 2], tables[fields["dataset"]][match["bulk_row"] - 2]
            check_selected_metadata(match, quota, bulk, fields, Decimal(config["coordinate_tolerance_degrees"]))
            candidates = [i for i, row in enumerate(tables[fields["dataset"]], 2)
                          if row[fields["cruise"]] == match["cruise"]
                          and Decimal(row[fields["station"]]) == Decimal(quota["Station"])
                          and Decimal(row[fields["depth"]]) == Decimal(quota["Depth"])]
            if candidates != [match["bulk_row"]] or match["candidate_bulk_rows"] != candidates:
                raise ValueError("Nonunique selected bulk candidate")
            identities = [row for row in quotas if row["Cruise_ID"] == quota["Cruise_ID"]
                          and row["Date"] == quota["Date"]
                          and Decimal(row["Station"]) == Decimal(quota["Station"])
                          and Decimal(row["Depth"]) == Decimal(quota["Depth"])]
            if len(identities) != 1:
                raise ValueError("Nonunique selected quota identity")
            expected.append(dict(**match, elements=[reconstruct_element(quota, bulk, fields, element)
                                                    for element in fields["elements"]]))
        compare(result["samples"], expected, discrepancies, "samples")
        summaries = dict(primary=summary([s for s in expected if s["status"] == "primary"]),
                         date_offset_only=summary([s for s in expected if s["status"] == "date_offset_sensitivity"]),
                         combined_sensitivity=summary(expected))
        compare(result["summaries"], summaries, discrepancies, "summaries")
    return dict(verified=True, independently_checked_numbers=len(discrepancies),
                maximum_relative_discrepancy=max(discrepancies, default=0),
                checked_samples=len(expected), checked_elements=sum(len(s["elements"]) for s in expected),
                qualification_unchanged=True, all_coverage_flags_and_summaries_checked=True,
                method="40-digit Decimal arithmetic from original rows; no analysis-module import")


def verify(directory):
    directory = Path(directory)
    result = json.loads((directory / "result.json").read_text())
    execution = json.loads((directory / "execution.json").read_text())
    required = {CONFIG, AUDIT, "src/orthopolity/field_resources.py",
                "docs/field-resources-protocol-2026-10-12.md",
                "experiments/run_field_resources.py", "experiments/fetch_field_resources.py",
                "tests/test_field_resources.py"}
    if not required.issubset({item["path"] for item in execution["sources"]}):
        raise ValueError("Incomplete execution-source manifest")
    for item in execution["sources"]:
        frozen = subprocess.check_output(["git", "show", f"{execution['freeze_commit']}:{item['path']}"], cwd=ROOT)
        if (hashlib.sha256(frozen).hexdigest() != item["sha256"]
                or (ROOT / item["path"]).read_bytes() != frozen):
            raise ValueError("Source differs from recorded execution freeze")
    config = json.loads((ROOT / CONFIG).read_text())
    if config["inputs"] != execution["inputs"]:
        raise ValueError("Changed input inventory")
    for item in execution["inputs"]:
        if hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError("Changed field source")
    qualification = json.loads((ROOT / AUDIT).read_text())
    with (ROOT / BASE / "849153.csv").open() as handle:
        quotas = list(csv.DictReader(handle))
    tables = {}
    for dataset in ("829895", "538091"):
        with (ROOT / BASE / (dataset + ".csv")).open() as handle:
            tables[dataset] = list(csv.DictReader(handle))
    output = verify_records(result, qualification, config, quotas, tables)
    output.update(input_checksums_verified=True, execution_freeze_verified=True)
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    verified = verify(args.directory)
    body = json.dumps(verified, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.write:
        path = args.directory / "verification.json"
        if path.exists() and path.read_text() != body:
            raise ValueError("Refusing to replace changed verification")
        path.write_text(body)
    print(body)
