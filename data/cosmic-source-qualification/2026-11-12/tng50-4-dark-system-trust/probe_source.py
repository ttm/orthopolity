"""One bounded, anonymous TNG run-metadata request; never fetch numerical arrays.

This is the first access gate of cosmic development task D1, not the complete
metadata manifest or an empirical log-orthopolic allocation test. No credential
is read. Redirects, retries and follow-up requests are deliberately disabled.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import http.client
import json
from pathlib import Path
import ssl
import urllib.error
import urllib.request


URL = "https://www.tng-project.org/api/TNG50-4-Dark/"
BYTE_CAP = 1_048_576


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def probe(destination: Path, ca_bundle: Path | None = None):
    # Never replace a previous receipt or body.
    destination.mkdir(parents=True, exist_ok=False)
    started = datetime.now(timezone.utc).isoformat()
    source = Path(__file__).read_bytes()
    (destination / "probe_source.py").write_bytes(source)
    receipt = {
        "kind": "Anonymous run-metadata access probe; no empirical test",
        "requested_url": URL,
        "started_utc": started,
        "credential_used": False,
        "response_body_cap_bytes": BYTE_CAP,
        "request_limit": 1,
        "redirects_followed": 0,
        "retries": 0,
        "http_status": None,
        "response_bytes_retained": 0,
        "body_complete": False,
        "numerical_arrays_requested": False,
        "complete_D1_manifest": False,
        "script_sha256": hashlib.sha256(source).hexdigest(),
        "tls_certificate_verification": True,
        "tls_hostname_verification": True,
        "ca_bundle": str(ca_bundle) if ca_bundle else "Python platform default",
        "ca_bundle_sha256": hashlib.sha256(ca_bundle.read_bytes()).hexdigest() if ca_bundle else None,
    }
    request = urllib.request.Request(URL, headers={
        "Accept": "application/json",
        "Accept-Encoding": "identity",
        "User-Agent": "orthopolity-source-qualification/1.0",
    })
    context = ssl.create_default_context(cafile=str(ca_bundle) if ca_bundle else None)
    opener = urllib.request.build_opener(NoRedirect, urllib.request.HTTPSHandler(context=context))
    body = bytearray()
    response_started = False
    try:
        try:
            response = opener.open(request, timeout=30)
        except urllib.error.HTTPError as error:
            response = error  # Retain the actual HTTP error body within the same cap.
        with response:
            response_started = True
            receipt["http_status"] = response.code
            receipt["content_type"] = response.headers.get("Content-Type")
            receipt["content_encoding"] = response.headers.get("Content-Encoding")
            advertised = response.headers.get("Content-Length")
            receipt["advertised_content_length"] = advertised
            reached_eof = False
            while len(body) < BYTE_CAP:
                try:
                    block = response.read(min(65_536, BYTE_CAP - len(body)))
                except http.client.IncompleteRead as error:
                    body.extend(error.partial[:BYTE_CAP - len(body)])
                    raise
                if not block:
                    reached_eof = True
                    break
                body.extend(block)
            # Conservatively mark a body at the cap incomplete, even if its length
            # happens to equal the cap. Never read an extra byte to test EOF.
            complete = reached_eof
            if advertised is not None:
                try:
                    complete = complete and len(body) == int(advertised)
                except ValueError:
                    complete = False
            receipt.update({
                "body_complete": complete,
                "outcome": "http_response",
            })
    except (urllib.error.URLError, OSError, http.client.HTTPException) as error:
        # No exception repr: proxies or environment URLs could contain credentials.
        receipt["outcome"] = "transport_failure"
        receipt["error_type"] = type(error).__name__
        reason = getattr(error, "reason", None)
        receipt["reason_type"] = type(reason).__name__ if reason is not None else None
        receipt["reason_errno"] = getattr(reason, "errno", None)
    if response_started:
        body_path = destination / "response-body.bin"
        body_path.write_bytes(body)
        receipt.update({
            "response_bytes_retained": len(body),
            "body_path": body_path.name,
            "body_sha256": hashlib.sha256(body).hexdigest(),
        })
    receipt["finished_utc"] = datetime.now(timezone.utc).isoformat()
    (destination / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--ca-bundle", type=Path, help="Explicit trusted CA bundle; TLS verification stays required")
    args = parser.parse_args()
    probe(args.output_dir, args.ca_bundle)
