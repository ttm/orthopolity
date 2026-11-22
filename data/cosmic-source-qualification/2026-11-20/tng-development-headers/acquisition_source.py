"""Inspect three representative development transfer headers without file bodies."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, str(Path.cwd() / "experiments"))
from fetch_cosmic_metadata import hidden_key, NoRedirect

base = Path("data/cosmic-source-qualification/2026-11-19")
previous_path = base / "tng50-4-dark-file-lists/acquisition.json"
previous_raw = previous_path.read_bytes()
previous = json.loads(previous_raw)
destination = Path("data/cosmic-source-qualification/2026-11-20/tng-development-headers")
destination.mkdir(parents=True, exist_ok=False)
source = Path(__file__).read_bytes()
(destination / "acquisition_source.py").write_bytes(source)
listed = json.loads((base / "tng50-4-dark-file-lists/01-snapshot-97-files.json").read_text())["files"]
groups = json.loads((base / "tng50-4-dark-file-lists/02-groupcat-97-files.json").read_text())["files"]
urls = [listed[0].replace("http:","https:") + "?dm=ParticleIDs",
        groups[0].replace("http:","https:"),
        "https://www.tng-project.org/api/TNG50-4-Dark/files/offsets.97.hdf5"]
key = hidden_key()
context = ssl.create_default_context(cafile="/etc/ssl/cert.pem")
opener = urllib.request.build_opener(NoRedirect, urllib.request.HTTPSHandler(context=context))
records = []
for url in urls:
    item = dict(url=url, method="HEAD", started_utc=datetime.now(timezone.utc).isoformat())
    try:
        request = urllib.request.Request(url, method="HEAD", headers={"api-key":key, "Accept-Encoding":"identity"})
        try:
            response = opener.open(request, timeout=30)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            item.update(http_status=response.code, content_length=response.headers.get("Content-Length"),
                        content_type=response.headers.get("Content-Type"), accept_ranges=response.headers.get("Accept-Ranges"))
            location = response.headers.get("Location")
            if location:
                parsed = urllib.parse.urlsplit(location)
                item["redirect_destination"] = dict(scheme=parsed.scheme, host=parsed.hostname,
                                                    path=parsed.path, query_present=bool(parsed.query))
                # Query values may be signed bearer tokens; no redirect is followed.
            if key.lower() in json.dumps(item).lower():
                item = dict(http_status=response.code, metadata_suppressed="credential_echo")
    except (urllib.error.URLError, OSError, ValueError) as error:
        item.update(error_type=type(error).__name__)
    item.update(finished_utc=datetime.now(timezone.utc).isoformat(), body_bytes_read=0)
    records.append(item)
manifest = dict(kind="TNG development HEAD metadata, no numerical file bodies", requests=records,
                credential_used=True, credential_retained=False, redirects_followed=0,
                tls_certificate_verification=True, tls_hostname_verification=True,
                prior_receipt_sha256=hashlib.sha256(previous_raw).hexdigest(),
                aggregate_body_bytes=previous["aggregate_body_bytes"],
                remaining_body_budget_bytes=previous["remaining_body_budget_bytes"],
                source_sha256=hashlib.sha256(source).hexdigest())
(destination / "acquisition.json").write_text(json.dumps(manifest,indent=2)+"\n")
print(json.dumps(manifest,indent=2))
