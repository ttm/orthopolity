"""HEAD the declared development files, following one validated TNG data redirect."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, str(Path.cwd()/"experiments"))
from fetch_cosmic_metadata import hidden_key, NoRedirect

base = Path("data/cosmic-source-qualification/2026-11-19/tng50-4-dark-file-lists")
prior_raw = (base / "acquisition.json").read_bytes()
prior = json.loads(prior_raw)
destination = Path("data/cosmic-source-qualification/2026-11-20/tng-selected-file-headers")
destination.mkdir(parents=True, exist_ok=False)
source = Path(__file__).read_bytes()
(destination/"acquisition_source.py").write_bytes(source)
requests = []
for item in prior["requests"]:
    raw = (base/item["path"]).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == item["sha256"]
    kind, number, _ = item["label"].split("-")
    for chunk, url in enumerate(json.loads(raw)["files"]):
        expected = f"http://www.tng-project.org/api/TNG50-4-Dark/files/{kind}-{number}.{chunk}.hdf5"
        assert url == expected
        path = f"/file/{kind}/L35n270TNG_DM/{number}/{chunk}/"
        if kind == "snapshot":
            path += "0.2.0.0.0.0/"
        requests.append(dict(kind=kind, output=int(number), chunk=chunk,
                             url=url.replace("http:","https:") + ("?dm=ParticleIDs" if kind == "snapshot" else ""),
                             expected_redirect_path=path))
for number in [97,98,99]:
    requests.append(dict(kind="offsets",output=number,chunk=None,
                         url=f"https://www.tng-project.org/api/TNG50-4-Dark/files/offsets.{number}.hdf5",
                         expected_redirect_path=f"/file/offsets/L35n270TNG_DM/{number}/"))

key = hidden_key()
opener = urllib.request.build_opener(NoRedirect, urllib.request.HTTPSHandler(
    context=ssl.create_default_context(cafile="/etc/ssl/cert.pem")))

def head(url, authenticated):
    headers={"Accept-Encoding":"identity"}
    if authenticated:
        headers["api-key"]=key
    try:
        return opener.open(urllib.request.Request(url,method="HEAD",headers=headers),timeout=30)
    except urllib.error.HTTPError as error:
        return error

results=[]
for item in requests:
    record={k:v for k,v in item.items() if k != "expected_redirect_path"}
    record["started_utc"]=datetime.now(timezone.utc).isoformat()
    try:
        with head(item["url"],True) as response:
            record["api_http_status"]=response.code
            if response.code != 302:
                raise ValueError("expected_redirect")
            location=response.headers.get("Location","")
        parts=urllib.parse.urlsplit(location)
        if (parts.scheme != "https" or parts.netloc != "data-eu.tng-project.org"
                or parts.path != item["expected_redirect_path"] or parts.fragment):
            raise ValueError("unexpected_redirect")
        record["redirect_host"]=parts.hostname
        record["redirect_path"]=parts.path
        record["redirect_query_retained"]=False
        # The signed URL is used only in memory. The API key header is not forwarded.
        with head(location,False) as response:
            record.update(data_http_status=response.code,content_length=response.headers.get("Content-Length"),
                          content_type=response.headers.get("Content-Type"),
                          accept_ranges=response.headers.get("Accept-Ranges"))
        if key.lower() in json.dumps(record).lower():
            record={"output":item["output"],"kind":item["kind"],"metadata_suppressed":"credential_echo"}
    except (urllib.error.URLError,OSError,ValueError) as error:
        record["error_type"]=type(error).__name__
    record.update(finished_utc=datetime.now(timezone.utc).isoformat(),body_bytes_read=0)
    results.append(record)

manifest=dict(kind="Selected development file HEAD inventory; no numerical arrays",requests=results,
              source_sha256=hashlib.sha256(source).hexdigest(),prior_receipt_sha256=hashlib.sha256(prior_raw).hexdigest(),
              aggregate_metadata_body_bytes=prior["aggregate_body_bytes"],remaining_metadata_body_budget_bytes=prior["remaining_body_budget_bytes"],
              credential_used=True,credential_retained=False,api_key_forwarded_to_data_host=False,
              redirect_queries_retained=False,tls_certificate_verification=True,tls_hostname_verification=True,
              complete=all(r.get("data_http_status")==200 and r.get("content_length") is not None for r in results))
(destination/"acquisition.json").write_text(json.dumps(manifest,indent=2)+"\n")
summary=[{k:r.get(k) for k in ("kind","output","chunk","data_http_status","content_length")} for r in results]
print(json.dumps({"complete":manifest["complete"],"files":summary},indent=2))
