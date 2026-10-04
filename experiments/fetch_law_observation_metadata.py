"""Retain only allowlisted observation-method metadata for the law feasibility gate.

Default: verify existing bytes offline. Acquisition never requests a stock CSV,
table view, ERDDAP data query or whole results paper. It prints integrity status
only; source contents are not emitted. These are audit inputs, not a study.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import ssl
import subprocess
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data/law-route/2026-10-04/metadata"
SOURCES = {
    "malaspina-panmd.xml": ("https://doi.pangaea.de/10.1594/PANGAEA.816451?format=metadata_panmd", "xml"),
    "malaspina-events.kml": ("https://doi.pangaea.de/10.1594/PANGAEA.816451?format=events_kml", "xml"),
    "malaspina-processing-methods.pdf": ("https://digital.csic.es/bitstream/10261/316565/2/Bode_MalaspinaLibroBlanco_2012_617-622.pdf", "pdf"),
    "bloofinz-description.pdf": ("https://www.bco-dmo.org/dataset/956590/Dataset_description.pdf", "pdf"),
    "bloofinz-event-log-description.pdf": ("https://www.bco-dmo.org/dataset/943418/Dataset_description.pdf", "pdf"),
    "bloofinz-deployment.html": ("https://www.bco-dmo.org/deployment/916293", "html"),
}
LIMIT = 8_000_000


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha(body):
    return hashlib.sha256(body).hexdigest()


def encode(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False,
                       allow_nan=False) + "\n").encode()


def validate_location(name, final_url):
    requested, _ = SOURCES[name]
    expected, actual = urllib.parse.urlsplit(requested), urllib.parse.urlsplit(final_url)
    if (actual.scheme != "https" or actual.netloc != expected.netloc
            or actual.path != expected.path or actual.query != expected.query):
        raise ValueError("Redirect left the exact metadata allowlist")


class ExactMetadataRedirect(urllib.request.HTTPRedirectHandler):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def redirect_request(self, request, response, code, message, headers, new_url):
        validate_location(self.name, new_url)
        return super().redirect_request(request, response, code, message, headers, new_url)


def validate_response(name, final_url, body):
    _, kind = SOURCES[name]
    validate_location(name, final_url)
    if not body or len(body) > LIMIT:
        raise ValueError("Empty or oversized metadata response")
    if kind == "pdf" and not body.startswith(b"%PDF-"):
        raise ValueError("Expected a metadata/methods PDF")
    if kind == "xml":
        root = ET.fromstring(body)
        if name.endswith(".kml") and root.tag.rsplit("}", 1)[-1] != "kml":
            raise ValueError("Expected event-only KML")
        if name.endswith("panmd.xml") and "pangaea" not in root.tag.lower():
            raise ValueError("Expected PANGAEA metadata XML")
    if kind == "html" and (b"<html" not in body.lower() or b"RR2201" not in body):
        raise ValueError("Expected deployment metadata")


def native_tls_download(name):
    """Use macOS native trust when Python cannot build a certificate chain.

    curl verifies certificates and hostnames. It never follows redirects, and
    only this already-allowlisted URL is passed. No source body reaches stdout.
    """
    url, _ = SOURCES[name]
    with tempfile.NamedTemporaryFile(dir=BASE, prefix=".download-", delete=True) as tmp:
        result = subprocess.run([
            "/usr/bin/curl", "-q", "--fail", "--proto", "=https", "--max-redirs", "0",
            "--max-time", "30", "--max-filesize", str(LIMIT), "--silent", "--show-error",
            "--output", tmp.name, "--write-out",
            "%{http_code}\n%{url_effective}\n%{content_type}\n%{ssl_verify_result}\n", url,
        ], capture_output=True, text=True, check=True)
        status, final_url, content_type, tls_result = result.stdout.splitlines()
        if status != "200" or tls_result != "0":
            raise ValueError("Native-TLS metadata acquisition failed verification")
        body = Path(tmp.name).read_bytes()
    validate_response(name, final_url, body)
    return body, dict(final_url=final_url, http_status=int(status), content_type=content_type,
                      transport="macOS system curl; native TLS verification; redirects disabled")


def verify(receipt=None):
    receipt = receipt or json.loads((BASE / "acquisition.json").read_text())
    if receipt.get("schema_version") != 1 or receipt.get("complete") is not True:
        raise ValueError("Incomplete metadata receipt")
    items = receipt["files"]
    if len(items) != len(SOURCES) or {row["name"] for row in items} != set(SOURCES):
        raise ValueError("Metadata inventory differs from the allowlist")
    for row in items:
        path = BASE / row["name"]
        if (row["requested_url"] != SOURCES[row["name"]][0]
                or row["path"] != path.relative_to(ROOT).as_posix()):
            raise ValueError("Metadata provenance differs")
        body = path.read_bytes()
        if sha(body) != row["sha256"] or len(body) != row["bytes"]:
            raise ValueError("Retained metadata bytes changed")
        validate_response(row["name"], row["final_url"], body)
    return dict(complete=True, files=len(items), scope="Observation metadata only; no nitrogen-stock outcome request")


def acquire():
    BASE.mkdir(parents=True, exist_ok=True)
    receipt_path = BASE / "acquisition.json"
    receipt = json.loads(receipt_path.read_text()) if receipt_path.exists() else dict(
        schema_version=1, started_utc=now(), complete=False, files=[],
        scope="Fixed methods/schema/event-metadata URLs; no outcome-table request")
    if receipt.get("complete"):
        return verify(receipt)
    cert = Path("/etc/ssl/cert.pem")
    context = ssl.create_default_context(cafile=str(cert) if cert.exists() else None)
    receipt["tls"] = dict(certificate_verification="CERT_REQUIRED", hostname_verification=True,
                          openssl_version=ssl.OPENSSL_VERSION,
                          cafile_sha256=sha(cert.read_bytes()) if cert.exists() else None)
    known = {row["name"]: row for row in receipt["files"]}
    for name, (url, _) in SOURCES.items():
        path = BASE / name
        if name in known:
            row = known[name]
            body = path.read_bytes()
            if (row["requested_url"] != url or sha(body) != row["sha256"]
                    or len(body) != row["bytes"]):
                raise ValueError("Changed retained partial acquisition")
            validate_response(name, row["final_url"], body)
            continue
        started = now()
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "OrthopolityResearch/1.0 (methods metadata audit)"})
            opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=context),
                                                 ExactMetadataRedirect(name))
            try:
                with opener.open(request, timeout=30) as response:
                    body = response.read(LIMIT + 1)
                    validate_response(name, response.url, body)
                    metadata = dict(final_url=response.url, http_status=response.status,
                                    content_type=response.headers.get("Content-Type"),
                                    transport="Python urllib; verified system-CA TLS")
            except urllib.error.URLError as error:
                if not isinstance(error.reason, ssl.SSLCertVerificationError):
                    raise
                with (BASE / "retrieval-attempts.jsonl").open("a") as stream:
                    stream.write(json.dumps(dict(name=name, requested_url=url, started_utc=started,
                                                completed_utc=now(), error=str(error),
                                                next_attempt="Native-TLS curl; verification remains enabled")) + "\n")
                body, metadata = native_tls_download(name)
            row = dict(name=name, path=path.relative_to(ROOT).as_posix(), requested_url=url,
                       started_utc=started, completed_utc=now(), bytes=len(body), sha256=sha(body), **metadata)
        except Exception as error:
            with (BASE / "retrieval-attempts.jsonl").open("a") as stream:
                stream.write(json.dumps(dict(name=name, requested_url=url, started_utc=started,
                                            completed_utc=now(), error=f"{type(error).__name__}: {error}")) + "\n")
            receipt_path.write_bytes(encode(receipt))
            raise
        if path.exists() and path.read_bytes() != body:
            raise ValueError("Refusing to replace different retained metadata")
        path.write_bytes(body)
        receipt["files"].append(row)
        receipt_path.write_bytes(encode(receipt))
    receipt.update(complete=True, completed_utc=now())
    verify(receipt)
    receipt_path.write_bytes(encode(receipt))
    return verify(receipt)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=["acquire", "verify"], default="verify")
    print(json.dumps(dict(acquire=acquire, verify=verify)[parser.parse_args().stage](), indent=2))
