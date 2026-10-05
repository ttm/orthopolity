"""Qualify one independently measured calibration worksheet, without fitting.

Reads only the fixed sheet and columns in calibration-inspection-plan.json.
The calibration reader never opens community worksheets. Source verification
also replays retained first-row header inspections. No community data row is
interpreted. Formula cells stop before cached values can be used. Outputs are
development data, not forecasts.
"""
from __future__ import annotations

import collections
import io
import json
import math
import re
import xml.etree.ElementTree as ET
import zipfile

from fetch_measure_candidates import BASE, NS, REL, retain_report, verify

WORKBOOK = "1. Data summary.xlsx"
SHEET = "species metabolism"
FIELDS = ("light", "species", "dilution_percent", "optical_density", "volume_um3",
          "cells_per_ul", "cells_in_5ml", "oxygen_umol_per_min", "oxygen_umol_per_min_per_cell")


def selected_rows(book):
    root = ET.fromstring(book.read("xl/workbook.xml"))
    sheets = [s for s in root.findall(f"{{{NS}}}sheets/{{{NS}}}sheet") if s.attrib["name"] == SHEET]
    if len(sheets) != 1:
        raise ValueError("Expected exactly one species calibration sheet")
    rid = sheets[0].attrib[f"{{{REL}}}id"]
    relations = ET.fromstring(book.read("xl/_rels/workbook.xml.rels"))
    targets = [r.attrib["Target"] for r in relations if r.attrib["Id"] == rid]
    if len(targets) != 1 or not targets[0].startswith("worksheets/") or ".." in targets[0]:
        raise ValueError("Unexpected worksheet relationship")
    raw_rows, needed = [], set()
    with book.open("xl/" + targets[0]) as source:
        for _, element in ET.iterparse(source, events=("end",)):
            if element.tag != f"{{{NS}}}row":
                continue
            number = int(element.attrib["r"])
            cells = {}
            for cell in element.findall(f"{{{NS}}}c"):
                address = cell.attrib["r"]
                match = re.fullmatch(r"([A-Z]+)([0-9]+)", address)
                if not match or int(match[2]) != number:
                    raise ValueError("Malformed cell address")
                col = match[1]
                if len(col) != 1 or col > "I" or number == 1:
                    continue
                if cell.find(f"{{{NS}}}f") is not None:
                    raise ValueError(f"Formula in calibration {address}; dependency audit required")
                kind = cell.attrib.get("t", "n")
                value = cell.findtext(f"{{{NS}}}v")
                if kind == "s":
                    value = int(value)
                    needed.add(value)
                elif kind == "inlineStr":
                    value = "".join(t.text or "" for t in cell.findall(f"{{{NS}}}is//{{{NS}}}t"))
                elif kind == "n" and value is not None:
                    value = float(value)
                    if not math.isfinite(value):
                        raise ValueError(f"Nonfinite calibration value at {address}")
                elif value is not None:
                    raise ValueError(f"Unsupported calibration type at {address}")
                cells[col] = (kind, value)
            if cells:
                raw_rows.append((number, cells))
            element.clear()
    strings = {}
    if needed:
        with book.open("xl/sharedStrings.xml") as source:
            index = 0
            for _, element in ET.iterparse(source, events=("end",)):
                if element.tag == f"{{{NS}}}si":
                    if index in needed:
                        strings[index] = "".join(t.text or "" for t in element.iter(f"{{{NS}}}t"))
                    element.clear()
                    index += 1
                    if index > max(needed):
                        break
        if set(strings) != needed:
            raise ValueError("Missing calibration shared string")
    result = []
    for number, cells in raw_rows:
        row = dict(source_row=number)
        for col, field in zip("ABCDEFGHI", FIELDS):
            kind, value = cells.get(col, ("n", None))
            row[field] = strings[value] if kind == "s" else value
        if any(row[field] is not None for field in FIELDS):
            result.append(row)
    return result


def qualify(rows):
    if not rows:
        raise ValueError("Empty calibration")
    identities = {r["species"] for r in rows}
    if any(not isinstance(s, str) or not s for s in identities):
        raise ValueError("Missing species identity")
    species = sorted(identities)
    for row in rows:
        for field in FIELDS:
            if field != "species" and row[field] is not None and not isinstance(row[field], (int, float)):
                raise ValueError(f"Expected numeric calibration field: {field}")
    errors = []
    signs = collections.Counter()
    for row in rows:
        bulk, cells, rate = (row[k] for k in ("oxygen_umol_per_min", "cells_in_5ml", "oxygen_umol_per_min_per_cell"))
        if all(isinstance(x, (int, float)) for x in (bulk, cells, rate)) and cells > 0:
            expected = bulk / cells
            errors.append(abs(rate - expected) / max(abs(rate), abs(expected), 1e-300))
        signs["missing" if rate is None else "positive" if rate > 0 else "negative" if rate < 0 else "zero"] += 1
    return dict(
        stage="calibration qualification only; no fitted model or community score",
        rows=len(rows), species=len(species),
        light_values=sorted({r["light"] for r in rows if r["light"] is not None}),
        dilution_percent_values=sorted({r["dilution_percent"] for r in rows if r["dilution_percent"] is not None}),
        missing_by_field={f: sum(r[f] is None for r in rows) for f in FIELDS},
        per_cell_rate_signs=dict(signs),
        checked_bulk_to_cell_pairs=len(errors), max_relative_rate_identity_error=max(errors, default=None),
        by_species=[dict(species=s, rows=sum(r["species"] == s for r in rows),
                         size_values=sorted({r["volume_um3"] for r in rows if r["species"] == s and r["volume_um3"] is not None}))
                    for s in species],
        calibration_reader_opens_community_worksheets=False,
        community_numerical_data_rows_interpreted=False,
    )


def main():
    verify()
    with zipfile.ZipFile(BASE / "ghedini-source.zip") as source:
        with zipfile.ZipFile(io.BytesIO(source.read(WORKBOOK))) as book:
            rows = selected_rows(book)
    retain_report("ghedini-calibration-rows.json", rows)
    report = qualify(rows)
    retain_report("ghedini-calibration-qualification.json", report)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
