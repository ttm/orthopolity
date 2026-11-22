"""Retain one public directory listing; no numerical data files."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import re
import ssl
import urllib.request

url = "https://users.flatironinstitute.org/~camels/Sims/IllustrisTNG_DM/L25n256/CV/CV_0/"
cap = 65536
destination = Path("data/cosmic-source-qualification/2026-11-16/camels-cv0-directory")
destination.mkdir(parents=True, exist_ok=False)
source = Path(__file__).read_bytes()
(destination / "acquisition_source.py").write_bytes(source)

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None

context = ssl.create_default_context(cafile="/etc/ssl/cert.pem")
opener = urllib.request.build_opener(NoRedirect, urllib.request.HTTPSHandler(context=context))
request = urllib.request.Request(url, headers={"Accept-Encoding": "identity"})
started = datetime.now(timezone.utc).isoformat()
with opener.open(request, timeout=30) as response:
    body = response.read(cap)
    complete = len(body) < cap
    receipt = dict(requested_url=url, final_url=response.url, http_status=response.status,
                   content_type=response.headers.get("Content-Type"),
                   advertised_content_length=response.headers.get("Content-Length"),
                   bytes=len(body), byte_cap=cap, complete=complete,
                   sha256=hashlib.sha256(body).hexdigest(),
                   source_sha256=hashlib.sha256(source).hexdigest(),
                   started_utc=started, finished_utc=datetime.now(timezone.utc).isoformat(),
                   credentials_used=False, redirects_followed=0,
                   tls_certificate_verification=True, tls_hostname_verification=True,
                   numerical_file_bodies_requested=False)
(destination / "response.html").write_bytes(body)
(destination / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps(receipt, indent=2))
assert complete, "Listing reached cap; do not parse as complete"
assert receipt["http_status"] == 200
links = re.findall(r'href="([^"]+)"', body.decode())
print(json.dumps({"listed_hdf5_names": [link for link in links if link.endswith('.hdf5')]}, indent=2))
