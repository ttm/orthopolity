"""Retain public sorted-cell, ambient-count and bulk-stock archives unchanged.

Acquisition prints no response values. The fixed five-dataset inventory covers
the sorted-cell archive and candidate Pacific, Atlantic and Indian Ocean joins.
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
BASE = ROOT / "data/field-resources/2026-10-12"
DATASETS = ("849153", "829895", "538091", "723191", "734915")


def encode(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False,
                       allow_nan=False) + "\n").encode()


def verify(receipt=None):
    receipt = receipt or json.loads((BASE / "acquisition.json").read_text())
    expected = {f"{identifier}.{extension}" for identifier in DATASETS for extension in ("html", "csv")}
    if not receipt.get("complete") or {r["name"] for r in receipt["files"]} != expected:
        raise ValueError("Incomplete field source inventory")
    for record in receipt["files"]:
        body = (ROOT / record["path"]).read_bytes()
        if len(body) != record["bytes"] or hashlib.sha256(body).hexdigest() != record["sha256"]:
            raise ValueError(f"Changed retained source: {record['path']}")
    return dict(verified=True, files=len(receipt["files"]), datasets=list(DATASETS))


def acquire():
    BASE.mkdir(parents=True, exist_ok=True)
    receipt_path = BASE / "acquisition.json"
    receipt = json.loads(receipt_path.read_text()) if receipt_path.exists() else {
        "schema_version": 1, "files": [], "complete": False,
        "scope": "Metadata and raw CSV acquisition only; numerical responses not displayed"}
    if receipt["complete"]:
        return verify(receipt)
    context = ssl.create_default_context(cafile="/etc/ssl/cert.pem")
    inventory = {item["name"]: item for item in receipt["files"]}

    def fetch(name, url):
        path = BASE / name
        if name in inventory:
            body = path.read_bytes()
            if hashlib.sha256(body).hexdigest() != inventory[name]["sha256"]:
                raise ValueError(f"Changed source: {name}")
            return body
        started = dt.datetime.now(dt.timezone.utc).isoformat()
        request = urllib.request.Request(url, headers={"User-Agent": "OrthopolityResearch/1.0"})
        with urllib.request.urlopen(request, context=context, timeout=45) as response:
            body = response.read(8_000_001)
            if len(body) > 8_000_000:
                raise ValueError("Unexpected response larger than 8 MB")
            item = dict(name=name, path=path.relative_to(ROOT).as_posix(), requested_url=url,
                        final_url=response.url, retrieval_started_utc=started,
                        retrieval_completed_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
                        http_status=response.status, headers=dict(response.headers),
                        bytes=len(body), sha256=hashlib.sha256(body).hexdigest(),
                        tls_certificate_verification=True)
        if path.exists() and path.read_bytes() != body:
            raise ValueError(f"Refusing to overwrite changed source: {name}")
        path.write_bytes(body)
        receipt["files"].append(item)
        inventory[name] = item
        receipt_path.write_bytes(encode(receipt))
        return body

    for dataset in DATASETS:
        page = fetch(f"{dataset}.html", f"https://www.bco-dmo.org/dataset/{dataset}").decode()
        metadata = [json.loads(raw) for raw in re.findall(
            r'<script type="application/ld\+json">(.*?)</script>', page)]
        records = [item for item in metadata if item.get("@type") == "Dataset"]
        if len(records) != 1:
            raise ValueError("Expected one dataset metadata record")
        distributions = records[0]["distribution"]
        if len(distributions) != 1 or not distributions[0]["contentUrl"].endswith(".csv"):
            raise ValueError("Expected one primary CSV")
        fetch(f"{dataset}.csv", distributions[0]["contentUrl"])
    receipt["complete"] = True
    verify(receipt)
    receipt_path.write_bytes(encode(receipt))
    return verify(receipt)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("acquire", "verify"), default="verify")
    print(json.dumps({"acquire": acquire, "verify": verify}[parser.parse_args().stage](), indent=2))
