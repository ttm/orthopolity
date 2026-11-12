"""One bounded, anonymous TNG run-metadata request; never fetch numerical arrays.

This is the first access gate of cosmic development task D1, not the complete
metadata manifest or an empirical log-orthopolic allocation test. No credential
is read. Redirects, retries and follow-up requests are deliberately disabled.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import urllib.error
import urllib.request


URL = "https://www.tng-project.org/api/TNG50-4-Dark/"
BYTE_CAP = 1_048_576


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def probe(destination: Path):
    # Never replace a previous receipt or body.
    destination.mkdir(parents=True, exist_ok=False)
    started = datetime.now(timezone.utc).isoformat()
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
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    request = urllib.request.Request(URL, headers={
        "Accept": "application/json",
        "Accept-Encoding": "identity",
        "User-Agent": "orthopolity-source-qualification/1.0",
    })
    opener = urllib.request.build_opener(NoRedirect)
    try:
        try:
            response = opener.open(request, timeout=30)
        except urllib.error.HTTPError as error:
            response = error  # Retain the actual HTTP error body within the same cap.
        with response:
            receipt["http_status"] = response.code
            receipt["content_type"] = response.headers.get("Content-Type")
            receipt["content_encoding"] = response.headers.get("Content-Encoding")
            advertised = response.headers.get("Content-Length")
            receipt["advertised_content_length"] = advertised
            body = bytearray()
            reached_eof = False
            while len(body) < BYTE_CAP:
                block = response.read(min(65_536, BYTE_CAP - len(body)))
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
            body_path = destination / "response-body.bin"
            body_path.write_bytes(body)
            receipt.update({
                "response_bytes_retained": len(body),
                "body_complete": complete,
                "body_path": body_path.name,
                "body_sha256": hashlib.sha256(body).hexdigest(),
                "outcome": "http_response",
            })
    except (urllib.error.URLError, OSError, TimeoutError) as error:
        # No exception repr: proxies or environment URLs could contain credentials.
        receipt["outcome"] = "transport_failure"
        receipt["error_type"] = type(error).__name__
        reason = getattr(error, "reason", None)
        receipt["reason_type"] = type(reason).__name__ if reason is not None else None
        receipt["reason_errno"] = getattr(reason, "errno", None)
    receipt["finished_utc"] = datetime.now(timezone.utc).isoformat()
    (destination / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    probe(parser.parse_args().output_dir)
