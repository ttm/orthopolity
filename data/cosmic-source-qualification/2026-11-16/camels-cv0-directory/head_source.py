"""HEAD six files already present in the retained listing; no HDF5 bodies."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import re
import ssl
import urllib.error
import urllib.request

base = Path("data/cosmic-source-qualification/2026-11-16/camels-cv0-directory")
output = base / "file-manifest.json"
assert not output.exists(), "Do not overwrite an existing manifest"
source = Path(__file__).read_bytes()
(base / "head_source.py").write_bytes(source)
receipt = json.loads((base / "receipt.json").read_text())
listing = (base / "response.html").read_bytes()
assert hashlib.sha256(listing).hexdigest() == receipt["sha256"]
rows = {}
for row in re.findall(r"<tr>(.*?)</tr>", listing.decode()):
    attributes = re.findall(r'data-order="([^"]*)"', row)
    links = re.findall(r'href="([^"]+)"', row)
    if len(attributes) == 4 and len(links) == 1 and links[0].endswith(".hdf5"):
        assert attributes[1] == links[0]
        rows[links[0]] = dict(listing_bytes=int(attributes[2]), listing_mtime_unix=attributes[3])
snapshots = sorted(int(re.fullmatch(r"snapshot_(\d+)\.hdf5", name).group(1))
                   for name in rows if name.startswith("snapshot_"))
assert snapshots[-3:] == [86, 88, 90]
files = []

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None

context = ssl.create_default_context(cafile="/etc/ssl/cert.pem")
opener = urllib.request.build_opener(NoRedirect, urllib.request.HTTPSHandler(context=context))
for number in snapshots[-3:]:
    for kind in ("snapshot", "groups"):
        name = f"{kind}_{number:03d}.hdf5"
        item = dict(name=name, output_number=number, url=receipt["requested_url"]+name,
                    **rows[name], method="HEAD", started_utc=datetime.now(timezone.utc).isoformat())
        try:
            request = urllib.request.Request(item["url"], method="HEAD", headers={"Accept-Encoding": "identity"})
            try:
                response = opener.open(request, timeout=30)
            except urllib.error.HTTPError as error:
                response = error
            with response:
                item.update(http_status=response.code, content_length=response.headers.get("Content-Length"),
                            content_type=response.headers.get("Content-Type"),
                            last_modified=response.headers.get("Last-Modified"),
                            etag=response.headers.get("ETag"), accept_ranges=response.headers.get("Accept-Ranges"))
        except (urllib.error.URLError, OSError) as error:
            item.update(http_status=None, error_type=type(error).__name__)
        item["finished_utc"] = datetime.now(timezone.utc).isoformat()
        item["body_bytes_read"] = 0
        files.append(item)
manifest = dict(purpose="Metadata-only candidate for development, not validation", development_run="CAMELS IllustrisTNG_DM/L25n256/CV/CV_0",
                stored_snapshot_numbers=snapshots, selected_outputs=snapshots[-3:],
                selection_rule="Last three stored outputs; chosen before any numerical arrays",
                source_sha256=hashlib.sha256(source).hexdigest(),
                listing_sha256=receipt["sha256"], credentials_used=False,
                tls_certificate_verification=True, tls_hostname_verification=True,
                redirects_followed=0, metadata_body_bytes=receipt["bytes"], metadata_body_cap=receipt["byte_cap"],
                files=files, selected_file_bytes=sum(i["listing_bytes"] for i in files),
                numerical_file_bodies_requested=False, validation_target_assigned=False)
output.write_text(json.dumps(manifest, indent=2)+"\n")
print(json.dumps({"stored_outputs":len(snapshots),"selected_file_bytes":manifest["selected_file_bytes"],
                  "files":[{k:v for k,v in item.items() if k in ("name","http_status","listing_bytes","content_length")} for item in files]},indent=2))
