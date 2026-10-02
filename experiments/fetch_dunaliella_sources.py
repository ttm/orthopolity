"""Acquire the Dunaliella size-selection archive, or verify it offline.

Dryad (doi:10.5061/dryad.4mh47r7) refuses unauthenticated downloads, so the
data bundle comes from its Zenodo copy (record 4990483). Bytes are accepted
only if their MD5 equals the digest Dryad itself publishes. The 806 MB photo
archive is not retrieved: no planned endpoint uses photographs.

  --stage acquire   retrieve metadata and the data bundle, with receipts
  --stage verify    offline: check every retained byte and re-extract members
  --stage schema    offline: member inventory and tabular headers only; no
                    data row is read, so no outcome value is inspected
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import ssl
import stat
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data/dunaliella-sources/2026-10-02"
DRYAD = "https://datadryad.org/api/v2"
BUNDLE = "Codes and analysis.zip"
PHOTOS = "Algae Mic Photos - Originals.zip"


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n").encode()


def write_exact(path: Path, body: bytes) -> None:
    if path.exists():
        if path.read_bytes() != body:
            raise RuntimeError(f"Refusing to replace changed snapshot: {path.relative_to(ROOT)}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)


def acquire() -> dict:
    receipt_path = BASE / "acquisition.json"
    receipt = json.loads(receipt_path.read_text()) if receipt_path.exists() else {
        "schema_version": 1, "source_doi": "10.5061/dryad.4mh47r7",
        "publication_doi": "10.1098/rspb.2018.1347", "started_utc": now(), "files": [],
        "scope": "Published files retained unchanged; outcome values not inspected during acquisition or schema audit."}
    if receipt.get("complete"):
        return verify(receipt)
    cert = Path("/etc/ssl/cert.pem")
    context = ssl.create_default_context(cafile=str(cert) if cert.exists() else None)
    receipt["tls"] = {"certificate_verification": "CERT_REQUIRED", "hostname_verification": True,
                      "openssl_version": ssl.OPENSSL_VERSION, "cafile": str(cert) if cert.exists() else None,
                      "cafile_sha256": sha(cert.read_bytes()) if cert.exists() else None}
    inventory = {item["path"]: item for item in receipt["files"]}

    def download(relative: str, url: str, md5: str | None = None) -> bytes:
        path = BASE / relative
        key = path.relative_to(ROOT).as_posix()
        if key in inventory:
            body = path.read_bytes()
            if sha(body) != inventory[key]["sha256"]:
                raise RuntimeError(f"Changed retained source: {key}")
            return body
        started = now()
        request = urllib.request.Request(url, headers={"User-Agent": "OrthopolityResearch/1.0 (public research source audit)"})
        try:
            with urllib.request.urlopen(request, context=context, timeout=120) as response:
                body = response.read()
                metadata = {"path": key, "requested_url": url, "final_url": response.url,
                            "retrieval_started_utc": started, "retrieval_completed_utc": now(),
                            "http_status": response.status, "headers": dict(response.headers),
                            "bytes": len(body), "sha256": sha(body), "expected_md5": md5}
        except Exception as error:
            with (BASE / "retrieval-attempts.jsonl").open("a") as stream:
                stream.write(json.dumps({"requested_url": url, "started_utc": started, "completed_utc": now(),
                                         "error": f"{type(error).__name__}: {error}"}, sort_keys=True) + "\n")
            raise
        if md5 and hashlib.md5(body).hexdigest() != md5:
            raise RuntimeError(f"MD5 mismatch: {key}")
        write_exact(path, body)
        receipt["files"].append(metadata)
        inventory[key] = metadata
        receipt_path.write_bytes(json_bytes(receipt))
        return body

    BASE.mkdir(parents=True, exist_ok=True)
    dataset = json.loads(download("dryad/dataset-metadata.json", f"{DRYAD}/datasets/doi%3A10.5061%2Fdryad.4mh47r7"))
    version = dataset["_links"]["stash:version"]["href"].rsplit("/", 1)[-1]
    json.loads(download("dryad/version-metadata.json", f"{DRYAD}/versions/{version}"))
    files = json.loads(download("dryad/files-metadata.json", f"{DRYAD}/versions/{version}/files"))
    dryad = {entry["path"]: entry for entry in files["_embedded"]["stash:files"]}
    for name in (BUNDLE, PHOTOS):
        if dryad[name]["digestType"] != "md5":
            raise RuntimeError(f"Unexpected Dryad digest type for {name}")
    attempts = []
    for name in (BUNDLE,):
        file_id = dryad[name]["_links"]["self"]["href"].rsplit("/", 1)[-1]
        url = f"https://datadryad.org/downloads/file_stream/{file_id}"
        try:
            download(f"dryad/{name}", url, dryad[name]["digest"])
        except urllib.error.HTTPError as error:
            if error.code not in (401, 403):
                raise
            attempts.append({"name": name, "requested_url": url, "http_status": error.code})
    mirror = json.loads(download("zenodo/record-4990483-metadata.json", "https://zenodo.org/api/records/4990483"))
    if mirror.get("doi") != "10.5061/dryad.4mh47r7":
        raise RuntimeError("Zenodo record is not the Dryad dataset copy")
    zenodo = {entry["key"]: entry for entry in mirror["files"]}
    for name in (BUNDLE, PHOTOS):
        if zenodo[name]["checksum"] != f"md5:{dryad[name]['digest']}":
            raise RuntimeError(f"Zenodo and Dryad digests differ for {name}")
    if not (BASE / "dryad" / BUNDLE).exists():
        download(f"zenodo/{BUNDLE}", zenodo[BUNDLE]["links"]["self"], dryad[BUNDLE]["digest"])
    receipt["unavailable_dryad_files"] = attempts
    receipt["not_retrieved"] = [{"name": PHOTOS, "bytes": dryad[PHOTOS]["size"], "dryad_md5": dryad[PHOTOS]["digest"],
                                 "reason": "Photographs only; no planned endpoint uses them"}]
    receipt["source_selection"] = "dryad_original" if (BASE / "dryad" / BUNDLE).exists() else "zenodo_copy_with_dryad_md5"
    receipt["complete"], receipt["completed_utc"] = True, now()
    receipt_path.write_bytes(json_bytes(receipt))
    return verify(receipt)


def bundle_path() -> Path:
    for candidate in (BASE / "dryad" / BUNDLE, BASE / "zenodo" / BUNDLE):
        if candidate.exists():
            return candidate
    raise RuntimeError("Data bundle is absent")


def extract(path: Path) -> list[dict]:
    target = BASE / "extracted"
    inventory = []
    with zipfile.ZipFile(path) as archive:
        entries = archive.infolist()
        if sum(item.file_size for item in entries) > 50_000_000:
            raise RuntimeError("Archive expansion exceeds 50 MB")
        names = set()
        for item in entries:
            name = PurePosixPath(item.filename)
            if (name.is_absolute() or ".." in name.parts or "\\" in item.filename
                    or stat.S_ISLNK(item.external_attr >> 16) or item.filename in names):
                raise RuntimeError(f"Unsafe or duplicate archive member: {item.filename}")
            names.add(item.filename)
            if item.is_dir() or name.parts[0] == "__MACOSX" or name.name == ".DS_Store":
                continue
            body = archive.read(item)
            write_exact(target.joinpath(*name.parts), body)
            inventory.append({"archive_member": item.filename,
                              "path": target.joinpath(*name.parts).relative_to(ROOT).as_posix(),
                              "bytes": len(body), "sha256": sha(body)})
    write_exact(BASE / "archive-members.json", json_bytes(inventory))
    return inventory


def verify(receipt: dict | None = None) -> dict:
    receipt = receipt or json.loads((BASE / "acquisition.json").read_text())
    for item in receipt["files"]:
        body = (ROOT / item["path"]).read_bytes()
        if len(body) != item["bytes"] or sha(body) != item["sha256"]:
            raise RuntimeError(f"Retained source mismatch: {item['path']}")
        if item.get("expected_md5") and hashlib.md5(body).hexdigest() != item["expected_md5"]:
            raise RuntimeError(f"Retained MD5 mismatch: {item['path']}")
    members = extract(bundle_path())
    return {"retained_source_files": len(receipt["files"]), "archive_members": len(members),
            "source_selection": receipt.get("source_selection"), "complete": receipt.get("complete", False)}


def schema() -> dict:
    """Member list with tabular headers only; data rows are never read."""
    verify()
    rows = []
    for member in json.loads((BASE / "archive-members.json").read_text()):
        path = ROOT / member["path"]
        item = {"path": member["path"], "bytes": member["bytes"], "suffix": path.suffix.lower()}
        if item["suffix"] in {".csv", ".txt", ".tsv"}:
            with path.open(newline="", encoding="utf-8-sig", errors="replace") as stream:
                first = stream.readline()
            delimiter = "\t" if first.count("\t") > first.count(",") else ","
            item["header"] = next(csv.reader(io.StringIO(first), delimiter=delimiter), [])
            item["delimiter"] = "tab" if delimiter == "\t" else "comma"
        elif item["suffix"] in {".xlsx", ".xlsm"}:
            import openpyxl
            workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
            item["sheets"] = [{"sheet": sheet.title,
                               "header": list(next(sheet.iter_rows(min_row=1, max_row=1, values_only=True), []))}
                              for sheet in workbook.worksheets]
            workbook.close()
        rows.append(item)
    result = {"scope": "Headers and member names only; no data row was read", "members": rows}
    write_exact(BASE / "bundle-schema.json", json_bytes(result))
    return {"members": len(rows), "tabular": sum("header" in row or "sheets" in row for row in rows)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--stage", choices=("acquire", "verify", "schema"), default="verify")
    stage = parser.parse_args().stage
    print(json.dumps({"acquire": acquire, "verify": verify, "schema": schema}[stage](), indent=2, sort_keys=True))
