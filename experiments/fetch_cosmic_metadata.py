"""Bounded authenticated TNG run/snapshot metadata; no numerical arrays.

The API key is entered through a terminal without echo and is held only in
memory. No redirects, pagination, retries or non-metadata endpoints are used.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import getpass
import hashlib
import http.client
import json
from pathlib import Path
import re
import ssl
import urllib.error
import urllib.parse
import urllib.request
import warnings


ROOT = Path(__file__).resolve().parents[1]
PRIOR = ROOT / "data/cosmic-source-qualification/2026-11-12/acquisition.json"
RUN_PATH = "/api/TNG50-4-Dark/"
HOST = "www.tng-project.org"
CAP = 1_048_576


class StopAcquisition(Exception):
    """Public reason codes only; never put response or credential text here."""


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def metadata_url(value, allowed_paths):
    if not isinstance(value, str):
        raise StopAcquisition("missing_metadata_url")
    try:
        parts = urllib.parse.urlsplit(value)
    except ValueError:
        raise StopAcquisition("unapproved_metadata_url") from None
    if (parts.scheme not in {"http", "https"} or parts.netloc != HOST
            or parts.query or parts.fragment or parts.path not in allowed_paths):
        raise StopAcquisition("unapproved_metadata_url")
    return "https://" + HOST + parts.path


def hidden_key():
    with warnings.catch_warnings():
        warnings.simplefilter("error", getpass.GetPassWarning)
        value = getpass.getpass("TNG API key (hidden): ").strip()
    if not re.fullmatch(r"[0-9a-fA-F]{32}", value):
        raise StopAcquisition("invalid_key_format")
    return value


class MetadataSession:
    def __init__(self, destination, key, ca_bundle, prior=PRIOR):
        prior_raw = prior.read_bytes()
        previous = json.loads(prior_raw)
        if previous["aggregate_body_cap_bytes"] != CAP:
            raise StopAcquisition("prior_budget_mismatch")
        self.prior_bytes = previous["aggregate_body_bytes"]
        self.total_bytes = self.prior_bytes
        if not 0 <= self.total_bytes < CAP:
            raise StopAcquisition("no_remaining_budget")
        destination.mkdir(parents=True, exist_ok=False)
        self.destination = destination
        self.key = key
        self.items = []
        source = Path(__file__).read_bytes()
        (destination / "acquisition_source.py").write_bytes(source)
        context = ssl.create_default_context(cafile=str(ca_bundle))
        self.opener = urllib.request.build_opener(NoRedirect, urllib.request.HTTPSHandler(context=context))
        self.manifest = dict(
            kind="TNG D1 metadata qualification; no empirical test",
            reference_measure="logarithmic host mass; log-orthopolic collisionless total-matter candidate",
            prior_receipt_sha256=hashlib.sha256(prior_raw).hexdigest(),
            prior_body_bytes=self.prior_bytes, aggregate_body_cap_bytes=CAP,
            credential_used=True, credential_retained=False,
            source_sha256=hashlib.sha256(source).hexdigest(),
            ca_bundle=str(ca_bundle), ca_bundle_sha256=hashlib.sha256(ca_bundle.read_bytes()).hexdigest(),
            tls_certificate_verification=True, tls_hostname_verification=True,
            redirects_followed=0, retries=0,
            development_run="TNG50-4-Dark",
            selection_rule="Last three stored outputs, selected from metadata before numerical arrays",
            numerical_arrays_requested=False, validation_target_assigned=False,
            complete_D1_manifest=False, requests=self.items,
        )

    def fetch(self, value, allowed_paths, label):
        url = metadata_url(value, allowed_paths)
        remaining = CAP - self.total_bytes
        if remaining <= 0:
            raise StopAcquisition("budget_exhausted")
        item = dict(url=url, label=label, started_utc=datetime.now(timezone.utc).isoformat(),
                    http_status=None, body_bytes=0, body_complete=False)
        self.items.append(item)
        request = urllib.request.Request(url, headers={
            "api-key": self.key, "Accept": "application/json", "Accept-Encoding": "identity",
        })
        body = bytearray()
        stop = None
        try:
            try:
                response = self.opener.open(request, timeout=30)
            except urllib.error.HTTPError as error:
                response = error
            with response:
                item["http_status"] = response.code
                item["content_type"] = response.headers.get("Content-Type", "")
                item["content_encoding"] = response.headers.get("Content-Encoding")
                item["content_length"] = response.headers.get("Content-Length")
                eof = False
                while len(body) < remaining:
                    try:
                        block = response.read(min(65536, remaining - len(body)))
                    except http.client.IncompleteRead as error:
                        body.extend(error.partial[:remaining - len(body)])
                        raise
                    if not block:
                        eof = True
                        break
                    body.extend(block)
                item["body_complete"] = eof
                if item["content_length"] is not None:
                    try:
                        item["body_complete"] &= len(body) == int(item["content_length"])
                    except ValueError:
                        item["body_complete"] = False
        except (urllib.error.URLError, OSError, http.client.HTTPException) as error:
            item["error_type"] = type(error).__name__
            item["reason_type"] = type(getattr(error, "reason", None)).__name__
            stop = "transport_failure"
        self.total_bytes += len(body)
        item["body_bytes"] = len(body)
        item["finished_utc"] = datetime.now(timezone.utc).isoformat()

        # An echoed credential must not reach a retained body, arbitrary header,
        # decoded JSON, error message or stdout. Request headers are never saved.
        secret = self.key.lower()
        parsed = None
        if item["body_complete"]:
            try:
                parsed = json.loads(body)
            except (ValueError, UnicodeError):
                pass
        unescaped_body = re.sub(r"\\u([0-9a-fA-F]{4})", lambda match: chr(int(match[1], 16)),
                                body.decode("utf-8", errors="replace"))
        if (secret.encode() in bytes(body).lower()
                or secret in unescaped_body.lower()
                or secret in json.dumps(item).lower()
                or (parsed is not None and secret in json.dumps(parsed).lower())):
            item.clear()
            item.update(label=label, body_bytes=len(body), retained=False,
                        body_complete=False, stop_reason="credential_echo_suppressed")
            raise StopAcquisition("credential_echo_suppressed")
        if item.get("content_encoding") not in (None, "identity"):
            item.update(retained=False, stop_reason="unexpected_content_encoding")
            raise StopAcquisition("unexpected_content_encoding")
        filename = f"{len(self.items):02d}-{label}.json"
        (self.destination / filename).write_bytes(body)
        item.update(path=filename, sha256=hashlib.sha256(body).hexdigest(), retained=True)
        if stop:
            raise StopAcquisition(stop)
        if item["http_status"] != 200:
            raise StopAcquisition("http_error_or_redirect")
        if not item["body_complete"]:
            raise StopAcquisition("incomplete_body")
        if "application/json" not in item["content_type"].lower() or parsed is None:
            raise StopAcquisition("not_json_metadata")
        return parsed

    def run(self):
        reason = "metadata_requests_complete"
        try:
            run = self.fetch("https://" + HOST + RUN_PATH, {RUN_PATH}, "run")
            if not isinstance(run, dict):
                raise StopAcquisition("unexpected_run_schema")
            schedule = self.fetch(run.get("snapshots"), {RUN_PATH + "snapshots/"}, "snapshots")
            if not isinstance(schedule, list) or not schedule:
                raise StopAcquisition("unexpected_snapshot_schedule")
            if any(not isinstance(item, dict) or type(item.get("number")) is not int for item in schedule):
                raise StopAcquisition("unexpected_snapshot_number")
            numbers = [item["number"] for item in schedule]
            if len(set(numbers)) != len(numbers) or len(numbers) < 3 or min(numbers) < 0:
                raise StopAcquisition("invalid_snapshot_schedule")
            selected = sorted(schedule, key=lambda item: item["number"])[-3:]
            self.manifest["selected_outputs"] = [item["number"] for item in selected]
            for item in selected:
                number = item["number"]
                self.fetch(item.get("url"), {RUN_PATH + f"snapshots/{number}/"}, f"snapshot-{number}")
        except StopAcquisition as error:
            reason = str(error)  # Only our fixed public reason codes.
        except OSError:
            reason = "local_io_failure"
        return self.finish(reason)

    def file_lists(self, metadata_directory):
        """Continue from retained snapshot metadata, without repeating requests."""
        reason = "metadata_requests_complete"
        self.manifest["stage"] = "file_lists"
        try:
            previous = json.loads((metadata_directory / "acquisition.json").read_text())
            if not isinstance(previous, dict):
                raise StopAcquisition("invalid_retained_manifest")
            if previous["aggregate_body_bytes"] != self.prior_bytes:
                raise StopAcquisition("continuation_budget_mismatch")
            selected = previous.get("selected_outputs", [])
            if (not isinstance(selected, list) or len(selected) != 3
                    or any(type(number) is not int or number < 0 for number in selected)
                    or len(set(selected)) != 3):
                raise StopAcquisition("invalid_selected_outputs")
            self.manifest["selected_outputs"] = selected
            for number in selected:
                candidates = [item for item in previous["requests"] if item.get("label") == f"snapshot-{number}"]
                if len(candidates) != 1:
                    raise StopAcquisition("missing_retained_snapshot")
                item = candidates[0]
                if (item.get("http_status") != 200 or item.get("body_complete") is not True
                        or item.get("retained") is not True):
                    raise StopAcquisition("incomplete_retained_snapshot")
                path = metadata_directory / item["path"]
                if path.resolve().parent != metadata_directory.resolve():
                    raise StopAcquisition("unapproved_retained_path")
                raw = path.read_bytes()
                if hashlib.sha256(raw).hexdigest() != item["sha256"]:
                    raise StopAcquisition("retained_snapshot_hash_mismatch")
                snapshot = json.loads(raw)
                if not isinstance(snapshot, dict) or not isinstance(snapshot.get("files"), dict):
                    raise StopAcquisition("unexpected_retained_snapshot_schema")
                for kind in ("snapshot", "groupcat"):
                    link = snapshot.get("files", {}).get(kind)
                    self.fetch(link, {RUN_PATH + f"files/{kind}-{number}/"}, f"{kind}-{number}-files")
        except StopAcquisition as error:
            reason = str(error)
        except (OSError, ValueError, KeyError, TypeError):
            reason = "invalid_retained_metadata"
        return self.finish(reason)

    def finish(self, reason):
        self.manifest.update(
            outcome=reason, aggregate_body_bytes=self.total_bytes,
            new_body_bytes=self.total_bytes - self.prior_bytes,
            remaining_body_budget_bytes=CAP - self.total_bytes,
        )
        (self.destination / "acquisition.json").write_text(json.dumps(self.manifest, indent=2) + "\n")
        print(json.dumps({"outcome":reason, "requests":len(self.items),
                          "new_body_bytes":self.total_bytes-self.prior_bytes,
                          "remaining_body_budget_bytes":CAP-self.total_bytes}, indent=2))
        return self.manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--ca-bundle", type=Path, default=Path("/etc/ssl/cert.pem"))
    parser.add_argument("--file-lists-from", type=Path,
                        help="Continue from this retained metadata directory and its remaining budget")
    args = parser.parse_args()
    credential = hidden_key()
    prior = args.file_lists_from / "acquisition.json" if args.file_lists_from else PRIOR
    session = MetadataSession(args.output_dir, credential, args.ca_bundle, prior=prior)
    if args.file_lists_from:
        session.file_lists(args.file_lists_from)
    else:
        session.run()
