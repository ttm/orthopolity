"""Acquire the pinned Fontana--Bellon cantilever archive without viewing responses.

The default verifies retained bytes offline. Acquisition retains the publisher's
MATLAB data and scripts unchanged; it never executes those scripts. The derived
audit records field names, dimensions, units and published plotting selections,
without reporting fluctuation temperatures or the supplied theoretical curves.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import ssl
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data/cantilever/2026-10-13"
RECORD = "7640708"
FILES = ("data.mat", "plots.m", "Functions.zip")
METADATA_URL = f"https://zenodo.org/api/records/{RECORD}"
PAPER_URL = "https://arxiv.org/html/2208.08356v2"
SOURCE_NAMES = {"record.json", "paper.html", *FILES}


def encode(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False,
                       allow_nan=False) + "\n").encode()


def metadata_record():
    record = json.loads((BASE / "record.json").read_text())
    if str(record["id"]) != RECORD:
        raise ValueError("Unexpected Zenodo record version")
    if {entry["key"] for entry in record["files"]} != set(FILES):
        raise ValueError("Unexpected Zenodo file inventory")
    for entry in record["files"]:
        expected = f"https://zenodo.org/api/records/{RECORD}/files/{entry['key']}/content"
        if entry["links"]["self"] != expected:
            raise ValueError("Download does not belong to the pinned version")
    return record


def check_publisher_files(record):
    for entry in record["files"]:
        body = (BASE / entry["key"]).read_bytes()
        algorithm, digest = entry["checksum"].split(":", 1)
        if algorithm != "md5":
            raise ValueError("Unexpected publisher checksum algorithm")
        if len(body) != entry["size"] or hashlib.md5(body).hexdigest() != digest:
            raise ValueError(f"Publisher size/checksum mismatch: {entry['key']}")


def make_audit(record):
    # scipy parses the MATLAB container but no numerical array values are
    # inspected, reduced, printed or incorporated into this audit.
    from scipy.io import loadmat

    archive = loadmat(BASE / "data.mat", simplify_cells=True)
    expected_samples = {"C100", "C30", "C30C"}
    if {name for name in archive if not name.startswith("__")} != expected_samples:
        raise ValueError("Unexpected MATLAB sample inventory")
    fields = {}
    for sample in sorted(expected_samples):
        fields[sample] = {}
        for name, values in archive[sample].items():
            fields[sample][name] = {
                "shape": list(values.shape),
                "dtype": str(values.dtype),
                "units": "dimensionless loss angle" if "PHI" in name else "K",
                "role": ("response" if "TFLUC" in name else
                         "publisher_prediction_excluded_from_forward_inputs" if "TTHEO" in name else
                         "publisher_prediction_grid" if name in {"AVG_D_TAVG", "AVG_T_TAVG"} else
                         "potential_predictor"),
            }
    script = (BASE / "plots.m").read_text()
    masks = [line.strip() for line in script.splitlines()
             if re.search(r"\bC(?:100|30C?)\.\w+\([^;]+\)\s*=\s*NaN\s*;", line)]
    metadata = record["metadata"]
    return {
        "schema_version": 1,
        "doi": metadata["doi"],
        "title": metadata["title"],
        "publication_date": metadata["publication_date"],
        "license": metadata["license"],
        "source_version_id": RECORD,
        "source_concept_id": "7640707",
        "paper_doi": "10.1103/PhysRevE.107.034118",
        "paper_version": "arXiv:2208.08356v2",
        "schema": fields,
        "unit_provenance": "Article definitions and plot axis labels: TAVG, TMAX, TFLUC, TTHEO and their uncertainties are kelvin; PHI and its uncertainty are dimensionless loss angles.",
        "column_convention": "MATLAB columns use one-based indexing; D denotes flexural modes and T denotes torsional modes.",
        "published_mode_selection": {
            "C30": {"flexural": [1, 2, 3, 4, 5], "torsional": [1]},
            "C30C": {"flexural": [1, 2, 3, 4], "torsional": [1],
                      "unplotted_archive_columns": {"flexural": [5], "torsional": [2]}},
        },
        "mode_selection_provenance": "plots.m loops and article Figures 5--9. C30 flexural mode 3 has its own figure; it is not excluded. C30C contains additional archived columns not used in these published figures.",
        "publisher_script_nan_assignments": masks,
        "publisher_mask_policy": "Recorded only; no assignment is applied to the retained MATLAB archive or its schema audit. Analyses must declare whether they apply any publisher mask.",
        "exposure": {
            "inspected": ["publisher metadata", "paper text, including reported findings", "plotting script", "MATLAB field names, dtypes and dimensions"],
            "not_inspected": ["numerical TFLUC response arrays", "numerical TTHEO publisher prediction arrays"],
            "scripts_executed": False,
        },
        "interpretation_limits": [
            "Loss angle, resonance frequency and fluctuation amplitude are extracted from shared spectra; independent observables do not imply independent statistical errors.",
            "Equilibrium amplitudes are used for calibration under equipartition; their equality cannot be counted as a new empirical test.",
            "Distributed homogeneous losses, a linear temperature profile and a quadratic local loss law are hypotheses of the forward model.",
            "Archive contains reduced figure data rather than the individual time recordings or their joint covariance.",
        ],
    }


def verify(receipt=None):
    receipt = receipt or json.loads((BASE / "acquisition.json").read_text())
    names = [item["name"] for item in receipt["files"]]
    if not receipt.get("complete") or len(names) != len(SOURCE_NAMES) or set(names) != SOURCE_NAMES:
        raise ValueError("Incomplete cantilever source inventory")
    for item in receipt["files"]:
        expected_path = (BASE / item["name"]).relative_to(ROOT).as_posix()
        if item["path"] != expected_path:
            raise ValueError("Unexpected receipt path")
        body = (BASE / item["name"]).read_bytes()
        if len(body) != item["bytes"] or hashlib.sha256(body).hexdigest() != item["sha256"]:
            raise ValueError(f"Changed retained source: {item['path']}")
    record = metadata_record()
    check_publisher_files(record)
    audit = (BASE / "metadata-audit.json").read_bytes()
    if audit != encode(make_audit(record)):
        raise ValueError("Metadata audit does not match retained sources")
    if hashlib.sha256(audit).hexdigest() != receipt["metadata_audit_sha256"]:
        raise ValueError("Metadata audit receipt mismatch")
    return {"verified": True, "source_files": len(names), "record_version": RECORD,
            "publisher_checksums_verified": len(FILES), "response_values_reported": False}


def acquire():
    BASE.mkdir(parents=True, exist_ok=True)
    receipt_path = BASE / "acquisition.json"
    receipt = json.loads(receipt_path.read_text()) if receipt_path.exists() else {
        "schema_version": 1, "record_version": RECORD, "complete": False, "files": [],
        "scope": "Retain public source bytes and inspect schema only; no numerical response arrays are displayed.",
    }
    if receipt["complete"]:
        return verify(receipt)
    context = ssl.create_default_context(cafile="/etc/ssl/cert.pem")
    inventory = {entry["name"]: entry for entry in receipt["files"]}

    def fetch(name, url):
        path = BASE / name
        if name in inventory:
            item = inventory[name]
            body = path.read_bytes()
            if item["requested_url"] != url or len(body) != item["bytes"] or hashlib.sha256(body).hexdigest() != item["sha256"]:
                raise ValueError(f"Changed retained source: {name}")
            return
        started = dt.datetime.now(dt.timezone.utc).isoformat()
        request = urllib.request.Request(url, headers={"User-Agent": "OrthopolityResearch/1.0"})
        with urllib.request.urlopen(request, context=context, timeout=45) as response:
            body = response.read(8_000_001)
            if len(body) > 8_000_000:
                raise ValueError("Unexpected response larger than 8 MB")
            item = {"name": name, "path": path.relative_to(ROOT).as_posix(),
                    "requested_url": url, "final_url": response.url,
                    "retrieval_started_utc": started,
                    "retrieval_completed_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                    "http_status": response.status, "headers": dict(response.headers),
                    "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest(),
                    "tls_certificate_verification": True}
        if path.exists() and path.read_bytes() != body:
            raise ValueError(f"Refusing to overwrite changed source: {name}")
        path.write_bytes(body)
        receipt["files"].append(item)
        inventory[name] = item
        receipt_path.write_bytes(encode(receipt))

    fetch("record.json", METADATA_URL)
    record = metadata_record()
    for item in record["files"]:
        fetch(item["key"], item["links"]["self"])
    check_publisher_files(record)
    fetch("paper.html", PAPER_URL)
    audit = encode(make_audit(record))
    audit_path = BASE / "metadata-audit.json"
    if audit_path.exists() and audit_path.read_bytes() != audit:
        raise ValueError("Refusing to overwrite changed metadata audit")
    audit_path.write_bytes(audit)
    receipt["metadata_audit_sha256"] = hashlib.sha256(audit).hexdigest()
    receipt["complete"] = True
    verify(receipt)
    receipt_path.write_bytes(encode(receipt))
    return verify(receipt)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("acquire", "verify"), default="verify")
    print(json.dumps({"acquire": acquire, "verify": verify}[parser.parse_args().stage](), indent=2))
