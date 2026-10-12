"""Acquire the two public Synechococcus archives without displaying outcomes.

Only acquisition metadata and file hashes are printed. Existing snapshots are
verified, never refreshed. Use a new dated directory for later source versions.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import ssl
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data/paired-phosphorus/2026-10-12"
DATASETS = ("1005084", "1005186")


def encode(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False,
                       allow_nan=False) + "\n").encode()


def verify(receipt=None):
    receipt = receipt or json.loads((BASE / "acquisition.json").read_text())
    if not receipt.get("complete") or len(receipt["files"]) != 6:
        raise ValueError("Incomplete acquisition")
    for item in receipt["files"]:
        body = (ROOT / item["path"]).read_bytes()
        if len(body) != item["bytes"] or hashlib.sha256(body).hexdigest() != item["sha256"]:
            raise ValueError(f"Changed source: {item['path']}")
    return {"complete": True, "files": len(receipt["files"]),
            "scope": "Two landing pages, two README files, two unchanged CSV files"}


def acquire():
    BASE.mkdir(parents=True, exist_ok=True)
    receipt_path = BASE / "acquisition.json"
    receipt = json.loads(receipt_path.read_text()) if receipt_path.exists() else {
        "schema_version": 1, "files": [], "complete": False,
        "scope": "Acquisition does not display or summarize numerical responses"}
    if receipt["complete"]:
        return verify(receipt)
    cert = Path("/etc/ssl/cert.pem")
    context = ssl.create_default_context(cafile=str(cert) if cert.exists() else None)
    inventory = {item["name"]: item for item in receipt["files"]}

    def fetch(name, url):
        path = BASE / name
        if name in inventory:
            body = path.read_bytes()
            if hashlib.sha256(body).hexdigest() != inventory[name]["sha256"]:
                raise ValueError(f"Changed retained source: {name}")
            return body
        started = dt.datetime.now(dt.timezone.utc).isoformat()
        request = urllib.request.Request(url, headers={"User-Agent": "OrthopolityResearch/1.0"})
        with urllib.request.urlopen(request, context=context, timeout=45) as response:
            body = response.read(4_000_001)
            if len(body) > 4_000_000:
                raise ValueError("Unexpected response larger than 4 MB")
            item = {"name": name, "path": path.relative_to(ROOT).as_posix(),
                    "requested_url": url, "final_url": response.url,
                    "retrieval_started_utc": started,
                    "retrieval_completed_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                    "http_status": response.status, "headers": dict(response.headers),
                    "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest(),
                    "tls_certificate_verification": True}
        if path.exists() and path.read_bytes() != body:
            raise ValueError(f"Refusing to replace changed source: {name}")
        path.write_bytes(body)
        receipt["files"].append(item)
        inventory[name] = item
        receipt_path.write_bytes(encode(receipt))
        return body

    for dataset in DATASETS:
        html = fetch(f"{dataset}.html", f"https://www.bco-dmo.org/dataset/{dataset}").decode()
        linked = [json.loads(raw) for raw in re.findall(
            r'<script type="application/ld\+json">(.*?)</script>', html)]
        dataset_metadata = [item for item in linked if item.get("@type") == "Dataset"]
        if len(dataset_metadata) != 1:
            raise ValueError("Expected exactly one Dataset metadata record")
        distributions = dataset_metadata[0]["distribution"]
        if len(distributions) != 1 or not distributions[0]["contentUrl"].endswith(".csv"):
            raise ValueError("Expected one primary CSV")
        fetch(f"{dataset}.csv", distributions[0]["contentUrl"])
        urls = set(re.findall(r'https://datadocs\.bco-dmo\.org/dataset/[^<>"\\]+', html))
        readmes = [url for url in urls if url.endswith(".txt")]
        if len(readmes) != 1:
            raise ValueError("Expected exactly one supplemental README")
        fetch(f"{dataset}-README.txt", urllib.parse.quote(
            readmes[0].replace("&amp;", "&"), safe=":/%?=&"))
    receipt["complete"] = True
    verify(receipt)
    receipt_path.write_bytes(encode(receipt))
    return verify(receipt)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("acquire", "verify"), default="verify")
    print(json.dumps({"acquire": acquire, "verify": verify}[parser.parse_args().stage](), indent=2))
