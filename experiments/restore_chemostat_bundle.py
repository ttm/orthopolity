#!/usr/bin/env python3
"""Restore the untracked chemostat author bundle by its retained checksums.

The 98.7 MB Zenodo bundle and its extracted R workspace are not tracked by Git.
This explicit network stage re-downloads exactly the bytes recorded in the
retained acquisition receipt. Any byte-count, SHA-256 or provider-MD5 difference
fails before writing. `fetch_chemostat_sources.py --stage verify` then re-extracts
every member and checks it against the retained member inventory. This restores
an existing acquisition; it is not a new source acquisition.
"""
from __future__ import annotations

import hashlib
import json
import ssl
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data/chemostat-sources/2026-10-02"
BUNDLE = BASE / "zenodo/scripts_data_plankton_responses_Npulse.zip"


def main() -> None:
    receipt = json.loads((BASE / "acquisition.json").read_text())
    key = BUNDLE.relative_to(ROOT).as_posix()
    entry = next(item for item in receipt["files"] if item["path"] == key)
    if BUNDLE.exists():
        body = BUNDLE.read_bytes()
    else:
        cert = Path("/etc/ssl/cert.pem")
        context = ssl.create_default_context(cafile=str(cert) if cert.exists() else None)
        request = urllib.request.Request(entry["requested_url"], headers={
            "User-Agent": "OrthopolityResearch/1.0 (checksum restoration of retained source)"})
        with urllib.request.urlopen(request, context=context, timeout=120) as response:
            body = response.read()
    if (len(body) != entry["bytes"] or hashlib.sha256(body).hexdigest() != entry["sha256"]
            or hashlib.md5(body).hexdigest() != entry["provider_md5"]):
        raise RuntimeError("Bundle bytes differ from the retained acquisition receipt")
    if not BUNDLE.exists():
        partial = BUNDLE.with_name(BUNDLE.name + ".partial")
        partial.write_bytes(body)
        partial.replace(BUNDLE)
    print(json.dumps(dict(path=key, bytes=len(body), sha256=entry["sha256"], status="verified")))


if __name__ == "__main__":
    main()
