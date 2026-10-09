"""Retain candidate metadata for the next neutrality study; never fetch outcomes.

The allowlist contains repository information and dataset landing pages only.
No CSV, data-table view, archive, or raw GitHub data URL is requested. Published
summaries on landing pages are source exposure, not numerical validation data.
The plant header-reader incident is recorded separately in exposure.json.

  --stage acquire  retrieve the allowlisted metadata once, with byte receipts
  --stage verify   check those retained bytes offline (the default)
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
BASE = ROOT / "data/neutrality-audit/2026-10-03"
PLANT_COMMIT = "defccc3dcbbbf3ba57ff1572377de88fba83ff7f"
PLANT_TREE = "e5f236b242712cc4d6b64dea0e5e458158aca2c3"
GITHUB = "https://api.github.com/repos/KerkhoffLab/PlantSizeDist"
SOURCES = {
    "plant-repository.json": GITHUB,
    "plant-commit.json": f"{GITHUB}/commits/{PLANT_COMMIT}",
    "plant-tree.json": f"{GITHUB}/git/trees/{PLANT_COMMIT}?recursive=1",
    "plant-resolved-tree.json": f"{GITHUB}/git/trees/{PLANT_TREE}?recursive=1",
    "malaspina-816451.html": "https://doi.pangaea.de/10.1594/PANGAEA.816451",
    "pelacus-983551.html": "https://doi.pangaea.de/10.1594/PANGAEA.983551",
    "coruna-911575.html": "https://doi.pangaea.de/10.1594/PANGAEA.911575",
}


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def encode(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False,
                       allow_nan=False) + "\n").encode()


def verify(receipt: dict | None = None) -> dict:
    receipt = receipt or json.loads((BASE / "acquisition.json").read_text())
    if (receipt.get("schema_version") != 1 or receipt.get("complete") is not True
            or receipt.get("plant_commit") != PLANT_COMMIT):
        raise ValueError("Incomplete or incompatible metadata receipt")
    files = receipt["files"]
    if {item["name"] for item in files} != set(SOURCES) or len(files) != len(SOURCES):
        raise ValueError("The complete metadata allowlist was not retained")
    for item in files:
        if item["requested_url"] != SOURCES[item["name"]]:
            raise ValueError("Unexpected source URL")
        expected_path = (BASE / item["name"]).relative_to(ROOT).as_posix()
        if item["path"] != expected_path:
            raise ValueError("Unexpected retained metadata path")
        body = (ROOT / item["path"]).read_bytes()
        if len(body) != item["bytes"] or sha(body) != item["sha256"]:
            raise ValueError(f"Changed retained metadata: {item['name']}")
    commit = json.loads((BASE / "plant-commit.json").read_text())
    tree = json.loads((BASE / "plant-tree.json").read_text())
    resolved = json.loads((BASE / "plant-resolved-tree.json").read_text())
    if commit["sha"] != PLANT_COMMIT or tree.get("truncated") or resolved.get("truncated"):
        raise ValueError("Unexpected commit or truncated source inventory")
    # GitHub's commit-addressed response repeats the requested commit SHA.
    # Retain it, but also request the actual tree object named by the commit.
    if (commit["commit"]["tree"]["sha"] != PLANT_TREE or resolved["sha"] != PLANT_TREE
            or tree["sha"] != PLANT_COMMIT or tree["tree"] != resolved["tree"]):
        raise ValueError("Source tree differs from pinned commit")
    plant_files = [item["path"] for item in tree["tree"]
                   if item["type"] == "blob" and item["path"].startswith("Data/")
                   and item["path"].endswith(".csv")]
    return {"complete": bool(receipt.get("complete")), "retained_metadata_files": len(files),
            "plant_commit": PLANT_COMMIT, "plant_csv_inventory": plant_files,
            "scope": "Metadata only; the separate plant outcome-exposure incident remains disclosed"}


def acquire() -> dict:
    BASE.mkdir(parents=True, exist_ok=True)
    receipt_path = BASE / "acquisition.json"
    receipt = json.loads(receipt_path.read_text()) if receipt_path.exists() else {
        "schema_version": 1, "started_utc": now(), "files": [],
        "scope": "Candidate metadata only; no outcome-file endpoint requested by this driver",
        "plant_commit": PLANT_COMMIT,
    }
    if receipt.get("complete"):
        return verify(receipt)
    cert = Path("/etc/ssl/cert.pem")
    context = ssl.create_default_context(cafile=str(cert) if cert.exists() else None)
    receipt["tls"] = {"certificate_verification": "CERT_REQUIRED",
                      "hostname_verification": True, "openssl_version": ssl.OPENSSL_VERSION,
                      "cafile": str(cert) if cert.exists() else None,
                      "cafile_sha256": sha(cert.read_bytes()) if cert.exists() else None}
    inventory = {item["name"]: item for item in receipt["files"]}
    for name, url in SOURCES.items():
        path = BASE / name
        if name in inventory:
            body = path.read_bytes()
            if sha(body) != inventory[name]["sha256"] or len(body) != inventory[name]["bytes"]:
                raise ValueError(f"Changed retained metadata: {name}")
            continue
        started = now()
        request = urllib.request.Request(url, headers={
            "User-Agent": "OrthopolityResearch/1.0 (public metadata audit)",
        })
        try:
            with urllib.request.urlopen(request, context=context, timeout=45) as response:
                body = response.read(4_000_001)
                if len(body) > 4_000_000:
                    raise ValueError("Metadata response exceeds 4 MB")
                item = {"name": name, "path": path.relative_to(ROOT).as_posix(),
                        "requested_url": url, "final_url": response.url,
                        "retrieval_started_utc": started, "retrieval_completed_utc": now(),
                        "http_status": response.status, "headers": dict(response.headers),
                        "bytes": len(body), "sha256": sha(body)}
        except Exception as error:
            with (BASE / "retrieval-attempts.jsonl").open("a") as stream:
                stream.write(json.dumps({"requested_url": url, "started_utc": started,
                                         "completed_utc": now(),
                                         "error": f"{type(error).__name__}: {error}"},
                                        sort_keys=True) + "\n")
            raise
        if path.exists() and path.read_bytes() != body:
            raise ValueError(f"Refusing to replace changed metadata: {name}")
        path.write_bytes(body)
        receipt["files"].append(item)
        inventory[name] = item
        receipt_path.write_bytes(encode(receipt))
    receipt["complete"], receipt["completed_utc"] = True, now()
    verify(receipt)
    receipt_path.write_bytes(encode(receipt))
    return verify(receipt)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--stage", choices=("acquire", "verify"), default="verify")
    print(json.dumps({"acquire": acquire, "verify": verify}[parser.parse_args().stage](), indent=2))
