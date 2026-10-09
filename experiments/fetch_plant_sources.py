"""Retain the pinned plant census CSVs with provider blob and SHA-256 checks.

Acquisition reads source bytes for checksums, not numeric outcomes. Decoding is
performed later by the separate development/evaluation runner. Source exposure
from the earlier header-reader incident remains disclosed in the protocol.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import ssl
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data/plant-sources/2026-10-03"
CONFIG = ROOT / "configs/plant_biomass_profile_2026-10-03.json"


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha(body):
    return hashlib.sha256(body).hexdigest()


def blob_sha(body):
    return hashlib.sha1(b"blob " + str(len(body)).encode() + b"\0" + body).hexdigest()


def encode(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)+"\n").encode()


def configuration():
    config = json.loads(CONFIG.read_text())
    source = config["source"]
    tree = json.loads((ROOT / "data/neutrality-audit/2026-10-03/plant-resolved-tree.json").read_text())
    lookup = {item["path"]: item for item in tree["tree"]}
    for item in source["files"]:
        upstream = lookup[item["upstream_path"]]
        if (upstream["type"] != "blob" or upstream["sha"] != item["git_blob_sha1"]
                or upstream["size"] != item["bytes"]):
            raise ValueError("Protocol source differs from pinned tree")
    return config


def check_body(item, body):
    if len(body) != item["bytes"] or blob_sha(body) != item["git_blob_sha1"]:
        raise ValueError(f"Provider blob mismatch: {item['plot']}")


def verify(receipt=None):
    config = configuration()
    receipt = receipt or json.loads((BASE / "acquisition.json").read_text())
    if (receipt.get("schema_version") != 1 or receipt.get("complete") is not True
            or receipt.get("config_sha256") != sha(CONFIG.read_bytes())
            or receipt.get("source_commit") != config["source"]["commit"]):
        raise ValueError("Incomplete or changed acquisition specification")
    expected = {item["plot"]: item for item in config["source"]["files"]}
    if len(receipt["files"]) != len(expected) or {x["plot"] for x in receipt["files"]} != set(expected):
        raise ValueError("Incomplete or duplicate plant source inventory")
    for retained in receipt["files"]:
        item = expected[retained["plot"]]
        relative = (BASE / (item["plot"]+".csv")).relative_to(ROOT).as_posix()
        url = f"https://raw.githubusercontent.com/KerkhoffLab/PlantSizeDist/{config['source']['commit']}/{item['upstream_path']}"
        if retained["path"] != relative or retained["requested_url"] != url:
            raise ValueError("Unexpected source path or URL")
        body = (ROOT / relative).read_bytes()
        check_body(item, body)
        if sha(body) != retained["sha256"]:
            raise ValueError("Retained source bytes changed")
    return {"complete": True, "source_files": len(expected), "source_commit": receipt["source_commit"],
            "scope": "Pinned raw bytes verified; acquisition computes no numeric outcome"}


def acquire():
    config = configuration()
    BASE.mkdir(parents=True, exist_ok=True)
    receipt_path = BASE / "acquisition.json"
    receipt = json.loads(receipt_path.read_text()) if receipt_path.exists() else {
        "schema_version": 1, "started_utc": now(), "source_commit": config["source"]["commit"],
        "config_sha256": sha(CONFIG.read_bytes()), "files": [],
        "scope": "Raw files retained unchanged; no numeric rows decoded by acquisition. Prior source exposure is disclosed."}
    if receipt.get("complete"):
        return verify(receipt)
    if receipt["config_sha256"] != sha(CONFIG.read_bytes()):
        raise ValueError("Acquisition configuration changed; use a new study")
    cert = Path("/etc/ssl/cert.pem")
    context = ssl.create_default_context(cafile=str(cert) if cert.exists() else None)
    receipt["tls"] = {"certificate_verification": "CERT_REQUIRED", "hostname_verification": True,
                      "cafile": str(cert) if cert.exists() else None,
                      "cafile_sha256": sha(cert.read_bytes()) if cert.exists() else None}
    inventory = {item["plot"]: item for item in receipt["files"]}
    for item in config["source"]["files"]:
        path = BASE / (item["plot"]+".csv")
        if item["plot"] in inventory:
            body = path.read_bytes()
            check_body(item, body)
            if sha(body) != inventory[item["plot"]]["sha256"]:
                raise ValueError("Previously retained bytes changed")
            continue
        url = f"https://raw.githubusercontent.com/KerkhoffLab/PlantSizeDist/{config['source']['commit']}/{item['upstream_path']}"
        started = now()
        request = urllib.request.Request(url, headers={"User-Agent": "OrthopolityResearch/1.0 (public data study)"})
        try:
            with urllib.request.urlopen(request, context=context, timeout=45) as response:
                body = response.read(item["bytes"]+1)
                retained = {"plot": item["plot"], "path": path.relative_to(ROOT).as_posix(),
                            "requested_url": url, "final_url": response.url, "http_status": response.status,
                            "retrieval_started_utc": started, "retrieval_completed_utc": now(),
                            "headers": dict(response.headers), "bytes": len(body), "sha256": sha(body),
                            "git_blob_sha1": blob_sha(body)}
            check_body(item, body)
        except Exception as error:
            with (BASE / "retrieval-attempts.jsonl").open("a") as stream:
                stream.write(json.dumps({"requested_url": url, "started_utc": started,
                                         "completed_utc": now(), "error": f"{type(error).__name__}: {error}"})+"\n")
            raise
        if path.exists() and path.read_bytes() != body:
            raise ValueError("Refusing to replace changed raw source")
        path.write_bytes(body)
        receipt["files"].append(retained)
        receipt_path.write_bytes(encode(receipt))
    receipt["complete"], receipt["completed_utc"] = True, now()
    verify(receipt)
    receipt_path.write_bytes(encode(receipt))
    return verify(receipt)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("acquire", "verify"), default="verify")
    print(json.dumps({"acquire": acquire, "verify": verify}[parser.parse_args().stage](), indent=2))
