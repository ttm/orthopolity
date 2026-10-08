"""Retain published cell-division figures; audit their receipts offline by default."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data/cell-division/2026-10-08"
SOURCES = {
    "dataset.json": "https://datadryad.org/api/v2/datasets/doi%3A10.5061%2Fdryad.2bs69",
    "files.json": "https://datadryad.org/api/v2/versions/27668/files",
    "article.xml": "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC5367290/fullTextXML",
    "figure2.jpg": "https://pmc-oa-opendata.s3.amazonaws.com/PMC5367290.1/rsos160417-g2.jpg",
    "figure1.jpg": "https://pmc-oa-opendata.s3.amazonaws.com/PMC5367290.1/rsos160417-g1.jpg",
}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch", action="store_true")
    parser.add_argument("--stage", choices=["calibration", "evaluation"], default="evaluation")
    args = parser.parse_args()
    BASE.mkdir(parents=True, exist_ok=True)
    records = []
    for name, url in SOURCES.items():
        if name == "figure1.jpg" and args.stage == "calibration":
            continue
        if name == "figure1.jpg" and args.fetch and not (BASE / "freeze.json").exists():
            raise ValueError("Freeze predictions before acquiring the target figure")
        path = BASE / name
        receipt_path = BASE / (name + ".receipt.json")
        if receipt_path.exists():
            record = json.loads(receipt_path.read_text())
            if record["url"] != url or record["sha256"] != digest(path):
                raise ValueError("Changed source or provenance: " + name)
        elif args.fetch:
            if path.exists():
                raise ValueError("Unreceipted source: " + name)
            started = datetime.now(timezone.utc).isoformat()
            with tempfile.TemporaryDirectory(dir=BASE) as scratch:
                temporary = Path(scratch) / name
                response = subprocess.run([
                    "/usr/bin/curl", "-q", "--fail", "--location", "--silent", "--show-error",
                    "--proto", "=https", "--proto-redir", "=https", "--max-time", "60",
                    "--max-filesize", "5000000", "--output", str(temporary),
                    "--write-out", "%{url_effective}\n%{http_code}\n%{ssl_verify_result}\n", url,
                ], check=True, text=True, capture_output=True)
                final_url, status, tls = response.stdout.splitlines()
                if status != "200" or tls != "0":
                    raise ValueError("Unexpected HTTP or TLS result")
                record = dict(filename=name, url=url, final_url=final_url,
                              retrieval_started_utc=started,
                              retrieved_at_utc=datetime.now(timezone.utc).isoformat(),
                              sha256=digest(temporary), size_bytes=temporary.stat().st_size,
                              tls_verification=True,
                              scope="Published source; download does not decode numerical figure annotations")
                temporary.rename(path)
            receipt_path.write_text(json.dumps(record, indent=2) + "\n")
        else:
            raise ValueError("Missing retained source: " + name)
        records.append(record)
        print(name, record["size_bytes"], record["sha256"])
    manifest = dict(schema_version=1, sources=records)
    manifest_path = BASE / ("sources-" + args.stage + ".json")
    if manifest_path.exists() and json.loads(manifest_path.read_text()) != manifest:
        raise ValueError("Changed source manifest")
    if not manifest_path.exists():
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
