"""Partial elemental-stock compatibility, not an equal-allocation test.

The metadata-only audit never reads quota, abundance or chemistry fields.
Quotas come from separately counted sorted cells, not bulk/ambient abundance.
"""
from __future__ import annotations

from collections import Counter
from datetime import date
from decimal import Decimal, InvalidOperation
import math

GROUPS = ("Prochlorococcus", "Synechococcus")
QUOTAS = {
    "Prochlorococcus": {"C": "Prochlorococcus_POC", "N": "Prochlorcoccus_PON", "P": "Prochlorococcus_POP"},
    "Synechococcus": {"C": "Synechococcus_POC", "N": "Synechococcus_PON", "P": "Synechococcus_POP"},
}
SCHEMAS = {
    "NH1418": dict(dataset="829895", cruise="Cruise", station="Station", depth="Depth",
                   date="ISO_DateTime_UTC", lat="Latitude", lon="Longitude",
                   counts=dict(zip(GROUPS, GROUPS)), elements=("C", "N", "P")),
    "AE1319": dict(dataset="538091", cruise="cruise_id", station="station", depth="depth",
                   date="date", lat="lat", lon="lon",
                   counts=dict(zip(GROUPS, ("Pro", "Syn"))), elements=("C", "N")),
}
MISSING = {"", "nd", "na", "nan", "null", "none"}


def coordinate(value):
    number = Decimal(value)
    if not number.is_finite():
        raise ValueError("Nonfinite matching coordinate")
    return number


def identity_field(value):
    # Stations outside the eligible cruises can have textual labels.
    try:
        return coordinate(value)
    except (InvalidOperation, ValueError):
        return value.strip()


def audit(quotas, tables, tolerance="0.02"):
    """Retain every quota row; match only exact reported identities and depths."""
    tol = Decimal(tolerance)
    identities = [(r["Cruise_ID"], identity_field(r["Station"]), identity_field(r["Depth"]), r["Date"])
                  for r in quotas]
    multiplicities = Counter(identities)
    records = []
    for row_number, (q, key) in enumerate(zip(quotas, identities), 2):
        cruise = q["Cruise_ID"]
        item = dict(quota_row=row_number, cruise=cruise, station=q["Station"],
                    depth_m=q["Depth"], quota_date=q["Date"], quota_lat=q["Latitude"],
                    quota_lon=q["Longitude"], status="no_qualified_bulk_source")
        records.append(item)
        if multiplicities[key] != 1:
            item["status"] = "nonunique_quota_identity"
            continue
        if cruise not in SCHEMAS:
            continue
        schema = SCHEMAS[cruise]
        item["bulk_dataset"] = schema["dataset"]
        candidates = [(i, b) for i, b in enumerate(tables[schema["dataset"]], 2)
                      if b[schema["cruise"]] == cruise
                      and identity_field(b[schema["station"]]) == key[1]
                      and coordinate(b[schema["depth"]]) == key[2]]
        item["candidate_bulk_rows"] = [i for i, _ in candidates]
        if len(candidates) != 1:
            item["status"] = "no_exact_station_depth" if not candidates else "nonunique_bulk_identity"
            continue
        i, b = candidates[0]
        delta = (date.fromisoformat(b[schema["date"]][:10]) - date.fromisoformat(q["Date"])).days
        dlat = abs(coordinate(b[schema["lat"]]) - coordinate(q["Latitude"]))
        dlon = abs(coordinate(b[schema["lon"]]) - coordinate(q["Longitude"]))
        item.update(bulk_row=i, bulk_date=b[schema["date"]], bulk_lat=b[schema["lat"]],
                    bulk_lon=b[schema["lon"]], date_offset_days=delta,
                    latitude_difference_degrees=str(dlat), longitude_difference_degrees=str(dlon))
        if max(dlat, dlon) > tol:
            item["status"] = "coordinate_discrepancy"
        elif delta == 0:
            item["status"] = "primary"
        elif abs(delta) == 1:
            item["status"] = "date_offset_sensitivity"
        else:
            item["status"] = "date_discrepancy"
    selected = [r for r in records if r["status"] in ("primary", "date_offset_sensitivity")]
    # A bulk record cannot silently support two quota samples.
    matches = Counter((r["bulk_dataset"], r["bulk_row"]) for r in selected)
    for r in selected:
        if matches[(r["bulk_dataset"], r["bulk_row"])] != 1:
            r["status"] = "reused_bulk_identity"
    return dict(records=records, status_counts=dict(sorted(Counter(r["status"] for r in records).items())),
                numerical_responses_examined=False, coordinate_tolerance_degrees=str(tol))


def numeric(value, *, zero_allowed=False):
    if str(value).strip().lower() in MISSING:
        return None, "missing"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None, "unparseable"
    if not math.isfinite(number):
        return None, "nonfinite"
    if number < 0 or (number == 0 and not zero_allowed):
        return None, "nonpositive" if not zero_allowed else "negative"
    return number, None


def evaluate_element(q, b, schema, element):
    terms, omitted = [], []
    for group in GROUPS:
        quota, q_reason = numeric(q[QUOTAS[group][element]])
        count, n_reason = numeric(b[schema["counts"][group]], zero_allowed=True)
        if q_reason or n_reason:
            omitted.append(dict(group=group, quota_reason=q_reason, count_reason=n_reason))
        else:
            terms.append(dict(group=group, quota_fmol_cell=quota, count_cells_ml=count,
                              stock_uM=quota * count * 1e-6))
    stock = math.fsum(t["stock_uM"] for t in terms)
    bulk, reason = numeric(b["PO" + element])
    result = dict(element=element, terms=terms, omitted=omitted, bulk_uM=bulk,
                  partial_stock_uM=stock if terms else None,
                  status="scored" if terms and reason is None else "unscored",
                  unscored_reason=reason or ("no_valid_group" if not terms else None))
    if result["status"] == "scored":
        result.update(partial_over_bulk=stock / bulk, exceeds_bulk=stock > bulk,
                      maximum_common_minimum_retention=min(1., bulk / stock) if stock > 0 else 1.,
                      minimum_symmetric_relative_allowance=max(0., (stock - bulk) / (stock + bulk)))
    return result


def summarize(samples):
    scored = [(s, e) for s in samples for e in s["elements"] if e["status"] == "scored"]
    return dict(samples=len(samples), stations=len({(s["cruise"], s["station"]) for s in samples}),
                scored_elements=len(scored), exceeding_elements=sum(e["exceeds_bulk"] for _, e in scored),
                samples_with_excess=sum(any(e.get("exceeds_bulk", False) for e in s["elements"]) for s in samples),
                by_element={element: dict(scored=sum(e["element"] == element for _, e in scored),
                    exceeding=sum(e["element"] == element and e["exceeds_bulk"] for _, e in scored))
                    for element in ("C", "N", "P")})


def analyse(quotas, tables, config):
    qualification = audit(quotas, tables, config["coordinate_tolerance_degrees"])
    for status, expected in config["expected_quota_rows"].items():
        actual = [r["quota_row"] for r in qualification["records"] if r["status"] == status]
        if actual != expected:
            raise ValueError(f"Changed pre-response qualification: {status}")
    samples = []
    for match in qualification["records"]:
        if match["status"] not in ("primary", "date_offset_sensitivity"):
            continue
        schema = SCHEMAS[match["cruise"]]
        q, b = quotas[match["quota_row"] - 2], tables[match["bulk_dataset"]][match["bulk_row"] - 2]
        samples.append(dict(**match, elements=[evaluate_element(q, b, schema, e) for e in schema["elements"]]))
    primary = [s for s in samples if s["status"] == "primary"]
    secondary = [s for s in samples if s["status"] == "date_offset_sensitivity"]
    return dict(run_id=config["run_id"], qualification=qualification, samples=samples,
                summaries=dict(primary=summarize(primary), date_offset_only=summarize(secondary),
                               combined_sensitivity=summarize(samples)),
                scope="Conditional compatibility of partial whole-water cell stocks with filtered bulk; no equal-allocation or population test",
                reference_measure="Finite cell counting measure; no log-size or equal-taxon opportunity measure specified",
                units="fmol/cell times cells/mL times 1e-6 = micromol/L")
