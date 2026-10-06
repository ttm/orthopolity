"""Acquire public FIRAS product bytes explicitly, or verify them offline."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "data/thermal-radiation/2026-10-06"
SOURCES = [
    ("firas_monopole_spec_v1.txt", "https://lambda.gsfc.nasa.gov/data/cobe/firas/monopole_spec/firas_monopole_spec_v1.txt", "Published reconstructed CMB monopole and original fitted residuals"),
    ("product-description.html", "https://lambda.gsfc.nasa.gov/product/cobe/firas_monopole_spect.html", "Construction and calibration metadata"),
    ("download-page.html", "https://lambda.gsfc.nasa.gov/product/cobe/firas_monopole_get.html", "Download listing and delivery metadata"),
    ("fixsen-1996.pdf", "https://arxiv.org/pdf/astro-ph/9605054", "Primary measurement article; covariance Section 3.3, residuals Table 4"),
]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify():
    manifest = json.loads((DIRECTORY / "sources.json").read_text())
    expected = {name: url for name, url, _ in SOURCES}
    if {s["filename"]: s["url"] for s in manifest["sources"]} != expected:
        raise ValueError("Source manifest membership changed")
    for source in manifest["sources"]:
        path = DIRECTORY / source["filename"]
        if sha256(path) != source["sha256"] or path.stat().st_size != source["size_bytes"]:
            raise ValueError(f"Changed source: {path}")
    print(json.dumps(dict(verified_sources=len(expected))))


def acquire():
    DIRECTORY.mkdir(parents=True, exist_ok=True)
    manifest_path = DIRECTORY / "sources.json"
    if manifest_path.exists():
        verify()
        return
    records = []
    for name, url, role in SOURCES:
        receipt_path = DIRECTORY / (name + ".receipt.json")
        target = DIRECTORY / name
        if receipt_path.exists():
            record = json.loads(receipt_path.read_text())
            if record["url"] != url or sha256(target) != record["sha256"]:
                raise ValueError(f"Partial acquisition changed: {name}")
            records.append(record)
            continue
        if target.exists():
            raise ValueError(f"Unreceipted source exists: {target}")
        with tempfile.TemporaryDirectory(dir=DIRECTORY) as scratch:
            temporary = Path(scratch) / name
            response = subprocess.run([
                "/usr/bin/curl", "--fail", "--location", "--silent", "--show-error",
                "--max-time", "60", "--output", str(temporary),
                "--write-out", "%{url_effective}\n%{content_type}\n", url,
            ], check=True, capture_output=True, text=True)
            effective, content_type = response.stdout.strip().splitlines()
            record = dict(filename=name, url=url, final_url=effective,
                          retrieved_at_utc=datetime.now(timezone.utc).isoformat(),
                          content_type=content_type, size_bytes=temporary.stat().st_size,
                          sha256=sha256(temporary), role=role)
            temporary.rename(target)
        receipt_path.write_text(json.dumps(record, indent=2) + "\n")
        records.append(record)
        print(name, record["size_bytes"], record["sha256"])
    manifest_path.write_text(json.dumps(dict(schema_version=1,
        scope="Retrospective published-product analysis; no new measurement collection",
        sources=records), indent=2) + "\n")
    verify()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch", action="store_true", help="Explicitly enable public network acquisition")
    args = parser.parse_args()
    acquire() if args.fetch else verify()
