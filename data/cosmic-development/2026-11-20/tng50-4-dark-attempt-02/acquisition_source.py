"""Bounded, staged TNG development acquisition; credentials stay in memory.

Bootstrap downloads three files. A separate schema-validation receipt is
required before the remaining frozen inventory can be acquired. No retries.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import getpass
import hashlib
import http.client
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import ssl
import urllib.error
import urllib.parse
import urllib.request
import warnings


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "configs/cosmic-development-2026-11-20.json"
RUN = "TNG50-4-Dark"
API_HOST = "www.tng-project.org"
DATA_HOST = "data-eu.tng-project.org"
API_PREFIX = f"/api/{RUN}/files/"
AGGREGATE_CAP = 768 * 1024 ** 2
KIND_CAPS = {"particle_ids": 64 * 1024 ** 2,
             "groupcat": 16 * 1024 ** 2, "offsets": 8 * 1024 ** 2}
HDF5_MAGIC = b"\x89HDF\r\n\x1a\n"


class StopAcquisition(Exception):
    """Fixed public codes only: never include remote text or credentials."""


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def hidden_key():
    with warnings.catch_warnings():
        warnings.simplefilter("error", getpass.GetPassWarning)
        value = getpass.getpass("TNG API key (hidden): ").strip()
    if not re.fullmatch(r"[0-9a-fA-F]{32}", value):
        raise StopAcquisition("invalid_key_format")
    return value


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_digest(path):
    value = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def positive_int(value):
    return type(value) is int and value > 0


def read_json(path):
    try:
        raw = path.read_bytes()
        return raw, json.loads(raw)
    except (OSError, ValueError):
        raise StopAcquisition("unreadable_local_json") from None


def validate_config(config):
    if (not isinstance(config, dict) or type(config.get("schema_version")) is not int
            or config["schema_version"] != 1):
        raise StopAcquisition("invalid_config_schema")
    if config.get("run") != RUN or config.get("outputs") != [97, 98, 99]:
        raise StopAcquisition("unapproved_run_or_outputs")
    cap = config.get("aggregate_byte_cap")
    if not positive_int(cap) or cap > AGGREGATE_CAP:
        raise StopAcquisition("invalid_aggregate_cap")
    if not positive_int(config.get("min_free_disk_bytes")):
        raise StopAcquisition("invalid_disk_floor")
    files = config.get("files")
    if not isinstance(files, list) or len(files) != 27:
        raise StopAcquisition("invalid_file_inventory")
    seen, ids, paths = set(), set(), set()
    for item in files:
        if not isinstance(item, dict):
            raise StopAcquisition("invalid_file_entry")
        kind, output, chunk = item.get("kind"), item.get("output"), item.get("chunk")
        if kind not in KIND_CAPS or type(output) is not int or output not in (97, 98, 99):
            raise StopAcquisition("invalid_file_identity")
        if kind == "offsets":
            if chunk is not None:
                raise StopAcquisition("invalid_offset_chunk")
            endpoint = f"offsets.{output}.hdf5"
            expected_redirect = f"/file/offsets/L35n270TNG_DM/{output}/"
        else:
            if type(chunk) is not int or chunk not in range(4):
                raise StopAcquisition("invalid_file_chunk")
            prefix = "snapshot" if kind == "particle_ids" else "groupcat"
            endpoint = f"{prefix}-{output}.{chunk}.hdf5"
            expected_redirect = f"/file/{prefix}/L35n270TNG_DM/{output}/{chunk}/"
            if kind == "particle_ids":
                expected_redirect += "0.2.0.0.0.0/"
        expected = f"https://{API_HOST}{API_PREFIX}{endpoint}"
        if kind == "particle_ids":
            expected += "?dm=ParticleIDs"
        if item.get("url") != expected:
            raise StopAcquisition("unapproved_api_url")
        redirect_path = item.get("redirect_path")
        if redirect_path != expected_redirect:
            raise StopAcquisition("invalid_redirect_path")
        ident, relative = item.get("id"), item.get("relative_path")
        if not isinstance(ident, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+", ident):
            raise StopAcquisition("invalid_file_id")
        if (not isinstance(relative, str) or not relative.startswith("raw/")
                or "\\" in relative or any(part in ("", ".", "..") for part in relative.split("/"))
                or PurePosixPath(relative).suffix != ".hdf5"):
            raise StopAcquisition("invalid_raw_path")
        if not positive_int(item.get("byte_cap")) or item["byte_cap"] > KIND_CAPS[kind]:
            raise StopAcquisition("invalid_file_cap")
        bootstrap = output == 97 and (kind == "offsets" or chunk == 0)
        if type(item.get("bootstrap")) is not bool or item["bootstrap"] != bootstrap:
            raise StopAcquisition("invalid_bootstrap_inventory")
        identity = (kind, output, chunk)
        if identity in seen or ident in ids or relative in paths:
            raise StopAcquisition("duplicate_file_entry")
        seen.add(identity)
        ids.add(ident)
        paths.add(relative)
    return config


def redirect_url(location, expected_path, key):
    if not isinstance(location, str) or key.lower() in location.lower():
        raise StopAcquisition("unapproved_redirect")
    try:
        parts = urllib.parse.urlsplit(location)
    except ValueError:
        raise StopAcquisition("unapproved_redirect") from None
    if (parts.scheme != "https" or parts.netloc != DATA_HOST
            or parts.path != expected_path or parts.fragment
            or any(c in location for c in "\r\n\\")):
        raise StopAcquisition("unapproved_redirect")
    return location


def verify_prior_record(config, receipt):
    """Validate a single failed bootstrap with no retained numerical files.

    This deliberately does not implement arbitrary retries or partial recovery.
    Frozen source/config files must be checked separately by the caller.
    """
    if (not isinstance(receipt, dict) or type(receipt.get("schema_version")) is not int
            or receipt["schema_version"] != 1 or receipt.get("run") != RUN
            or receipt.get("development_only") is not True
            or receipt.get("aggregate_byte_cap") != config["aggregate_byte_cap"]
            or receipt.get("outcome") in (None, "initialized", "bootstrap_downloaded", "complete_downloaded")
            or receipt.get("prior_body_bytes", 0) != 0
            or receipt.get("prior_acquisition_sha256") is not None):
        raise StopAcquisition("unsupported_prior_acquisition")
    stages = receipt.get("stages")
    if (not isinstance(stages, list) or len(stages) != 1 or not isinstance(stages[0], dict)
            or stages[0].get("stage") != "bootstrap"
            or stages[0].get("outcome") != receipt["outcome"]):
        raise StopAcquisition("unsupported_prior_acquisition")
    total = receipt.get("aggregate_body_bytes")
    if type(total) is not int or not 0 <= total <= config["aggregate_byte_cap"]:
        raise StopAcquisition("invalid_prior_budget")
    if receipt.get("remaining_body_bytes") != config["aggregate_byte_cap"] - total:
        raise StopAcquisition("invalid_prior_budget")
    requests = receipt.get("requests")
    if not isinstance(requests, list) or len(requests) > 1:
        raise StopAcquisition("unsupported_prior_acquisition")
    planned = {item["id"]: item for item in config["files"] if item["bootstrap"]}
    counted = 0
    for item in requests:
        if (not isinstance(item, dict) or item.get("id") not in planned
                or item.get("outcome") != receipt["outcome"]
                or item.get("retained") is not False or item.get("file_bytes") != 0
                or "partial_path" in item or type(item.get("body_bytes")) is not int
                or not 0 <= item["body_bytes"] <= planned[item["id"]]["byte_cap"]
                or item.get("url") != planned[item["id"]]["url"]
                or item.get("relative_path") != planned[item["id"]]["relative_path"]):
            raise StopAcquisition("unsupported_prior_acquisition")
        responses = item.get("responses")
        if not isinstance(responses, list) or len(responses) > 2:
            raise StopAcquisition("invalid_prior_budget")
        response_bytes = 0
        for hop, response in enumerate(responses):
            if (not isinstance(response, dict) or type(response.get("body_bytes")) is not int
                    or response["body_bytes"] < 0
                    or response.get("authenticated") is not (hop == 0)
                    or response.get("host") != (API_HOST if hop == 0 else DATA_HOST)
                    or response.get("path") != (urllib.parse.urlsplit(item["url"]).path
                                                 if hop == 0 else planned[item["id"]]["redirect_path"])):
                raise StopAcquisition("invalid_prior_budget")
            response_bytes += response["body_bytes"]
        if response_bytes != item["body_bytes"]:
            raise StopAcquisition("invalid_prior_budget")
        counted += item["body_bytes"]
    if counted != total:
        raise StopAcquisition("invalid_prior_budget")
    return total


def check_prior_snapshots(config, config_sha, receipt, source_path, config_path):
    total = verify_prior_record(config, receipt)
    if (receipt.get("config_sha256") != config_sha or file_digest(config_path) != config_sha
            or file_digest(source_path) != receipt.get("acquisition_source_sha256")):
        raise StopAcquisition("prior_provenance_mismatch")
    return total


class DevelopmentSession:
    def __init__(self, config_path, destination, key, ca_bundle, stage="bootstrap",
                 bootstrap_validation=None, prior_acquisition=None):
        if stage not in ("bootstrap", "complete"):
            raise StopAcquisition("invalid_stage")
        if prior_acquisition is not None and stage != "bootstrap":
            raise StopAcquisition("prior_requires_new_bootstrap")
        if not re.fullmatch(r"[0-9a-fA-F]{32}", key):
            raise StopAcquisition("invalid_key_format")
        config_raw, config = read_json(config_path)
        self.config = validate_config(config)
        self.destination = Path(destination)
        self.stage = stage
        self.key = key
        self.source = Path(__file__).read_bytes()
        self.config_raw = config_raw
        self.config_sha = digest(config_raw)
        self.source_sha = digest(self.source)
        self.total_bytes = 0
        self.completed = set()
        context = ssl.create_default_context(cafile=str(ca_bundle))
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED
        self.opener = urllib.request.build_opener(NoRedirect, urllib.request.HTTPSHandler(context=context))
        ca_sha = file_digest(ca_bundle)
        if stage == "bootstrap":
            prior_raw = None
            if prior_acquisition is not None:
                prior_path = Path(prior_acquisition)
                prior_raw, prior = read_json(prior_path)
                self.total_bytes = check_prior_snapshots(
                    config, self.config_sha, prior, prior_path.parent / "acquisition_source.py",
                    prior_path.parent / "config.json")
                if prior.get("ca_bundle_sha256") != ca_sha:
                    raise StopAcquisition("trust_bundle_changed")
            parent = self.destination.parent
            while not parent.exists():
                parent = parent.parent
            if shutil.disk_usage(parent).free < config["min_free_disk_bytes"]:
                raise StopAcquisition("insufficient_free_disk")
            if self.destination.exists():
                raise StopAcquisition("output_directory_exists")
            self.destination.mkdir(parents=True, exist_ok=False)
            (self.destination / "acquisition_source.py").write_bytes(self.source)
            (self.destination / "config.json").write_bytes(config_raw)
            (self.destination / ".gitignore").write_text("raw/\n")
            self.receipt = dict(
                schema_version=1, run=RUN, development_only=True,
                reference_measure="logarithmic host mass; log-orthopolic collisionless total-matter candidate",
                config_sha256=self.config_sha, acquisition_source_sha256=self.source_sha,
                aggregate_byte_cap=config["aggregate_byte_cap"], aggregate_body_bytes=0,
                credential_retained=False, tls_certificate_verification=True,
                tls_hostname_verification=True, ca_bundle_sha256=ca_sha,
                retries=0, requests=[], stages=[], outcome="initialized")
            if prior_raw is not None:
                self.receipt.update(prior_body_bytes=self.total_bytes,
                                    prior_acquisition_sha256=digest(prior_raw), manual_continuation=True)
                (self.destination / "prior_acquisition.json").write_bytes(prior_raw)
                (self.destination / "prior_acquisition_source.py").write_bytes(
                    (prior_path.parent / "acquisition_source.py").read_bytes())
                (self.destination / "prior_config.json").write_bytes(
                    (prior_path.parent / "config.json").read_bytes())
            self.persist()
        else:
            self.resume(bootstrap_validation)
            if ca_sha != self.receipt.get("ca_bundle_sha256"):
                raise StopAcquisition("trust_bundle_changed")
            if shutil.disk_usage(self.destination).free < config["min_free_disk_bytes"]:
                raise StopAcquisition("insufficient_free_disk")

    def persist(self):
        self.receipt["aggregate_body_bytes"] = self.total_bytes
        self.receipt["remaining_body_bytes"] = self.config["aggregate_byte_cap"] - self.total_bytes
        temporary = self.destination / "acquisition.json.tmp"
        with temporary.open("x", encoding="utf-8") as output:
            json.dump(self.receipt, output, indent=2, sort_keys=True)
            output.write("\n")
            output.flush()
            os.fsync(output.fileno())
        temporary.replace(self.destination / "acquisition.json")

    def resume(self, validation_path):
        if validation_path is None:
            raise StopAcquisition("bootstrap_validation_required")
        _, self.receipt = read_json(self.destination / "acquisition.json")
        validation_raw, validation = read_json(Path(validation_path))
        if not isinstance(validation, dict) or not isinstance(self.receipt, dict):
            raise StopAcquisition("invalid_bootstrap_receipt")
        for field, value in (("config_sha256", self.config_sha),
                             ("acquisition_source_sha256", self.source_sha)):
            if self.receipt.get(field) != value or validation.get(field) != value:
                raise StopAcquisition("bootstrap_provenance_mismatch")
        if (file_digest(self.destination / "config.json") != self.config_sha
                or file_digest(self.destination / "acquisition_source.py") != self.source_sha):
            raise StopAcquisition("frozen_source_modified")
        if (type(validation.get("schema_version")) is not int or validation["schema_version"] != 1
                or validation.get("outcome") != "passed"
                or type(self.receipt.get("schema_version")) is not int
                or self.receipt["schema_version"] != 1 or self.receipt.get("run") != RUN
                or self.receipt.get("development_only") is not True
                or self.receipt.get("outcome") != "bootstrap_downloaded"
                or self.receipt.get("aggregate_byte_cap") != self.config["aggregate_byte_cap"]):
            raise StopAcquisition("bootstrap_not_passed")
        requests = self.receipt.get("requests")
        bootstrap = {item["id"]: item for item in self.config["files"] if item["bootstrap"]}
        if not isinstance(requests, list) or len(requests) != 3 or not isinstance(validation.get("files"), dict):
            raise StopAcquisition("invalid_bootstrap_receipt")
        self.total_bytes = self.receipt.get("aggregate_body_bytes")
        if type(self.total_bytes) is not int or not 0 <= self.total_bytes <= self.config["aggregate_byte_cap"]:
            raise StopAcquisition("invalid_prior_budget")
        counted = self.receipt.get("prior_body_bytes", 0)
        if type(counted) is not int or not 0 <= counted <= self.total_bytes:
            raise StopAcquisition("invalid_prior_budget")
        if "prior_acquisition_sha256" in self.receipt:
            prior_raw, prior = read_json(self.destination / "prior_acquisition.json")
            if (digest(prior_raw) != self.receipt["prior_acquisition_sha256"]
                    or self.receipt.get("manual_continuation") is not True
                    or check_prior_snapshots(self.config, self.config_sha, prior,
                        self.destination / "prior_acquisition_source.py",
                        self.destination / "prior_config.json") != counted):
                raise StopAcquisition("invalid_prior_budget")
        elif counted != 0:
            raise StopAcquisition("invalid_prior_budget")
        for item in requests:
            if not isinstance(item, dict) or item.get("id") not in bootstrap or item["id"] in self.completed:
                raise StopAcquisition("invalid_bootstrap_receipt")
            planned = bootstrap[item["id"]]
            if (item.get("outcome") != "complete" or item.get("relative_path") != planned["relative_path"]
                    or item.get("url") != planned["url"] or not positive_int(item.get("body_bytes"))
                    or not positive_int(item.get("file_bytes"))
                    or item["file_bytes"] > item["body_bytes"]
                    or item["body_bytes"] > planned["byte_cap"]):
                raise StopAcquisition("invalid_bootstrap_receipt")
            responses = item.get("responses")
            if not isinstance(responses, list) or len(responses) not in (1, 2):
                raise StopAcquisition("invalid_bootstrap_receipt")
            response_bytes = 0
            for hop, response in enumerate(responses):
                last = hop == len(responses) - 1
                if (not isinstance(response, dict) or type(response.get("body_bytes")) is not int
                        or response["body_bytes"] < 0 or response.get("body_complete") is not True
                        or response.get("http_status") != (200 if last else 302)
                        or response.get("authenticated") is not (hop == 0)
                        or response.get("host") != (API_HOST if hop == 0 else DATA_HOST)
                        or response.get("path") != (urllib.parse.urlsplit(planned["url"]).path
                                                     if hop == 0 else planned["redirect_path"])):
                    raise StopAcquisition("invalid_bootstrap_receipt")
                response_bytes += response["body_bytes"]
            if (response_bytes != item["body_bytes"]
                    or responses[-1]["body_bytes"] != item["file_bytes"]
                    or responses[-1].get("body_sha256") != item.get("sha256")):
                raise StopAcquisition("invalid_bootstrap_receipt")
            path = self.raw_path(planned)
            if (not path.is_file() or path.stat().st_size != item["file_bytes"]
                    or file_digest(path) != item.get("sha256")
                    or validation["files"].get(item["id"]) != item["sha256"]):
                raise StopAcquisition("bootstrap_file_mismatch")
            counted += item["body_bytes"]
            self.completed.add(item["id"])
        if counted != self.total_bytes or set(validation["files"]) != self.completed:
            raise StopAcquisition("invalid_prior_budget")
        self.receipt["bootstrap_validation_sha256"] = digest(validation_raw)
        with (self.destination / "bootstrap_validation.json").open("xb") as output:
            output.write(validation_raw)

    def raw_path(self, planned):
        path = self.destination / planned["relative_path"]
        if path.resolve() != self.destination.resolve() / planned["relative_path"]:
            raise StopAcquisition("raw_path_symlink")
        return path

    def remaining(self, planned, item):
        return min(planned["byte_cap"] - item["body_bytes"],
                   self.config["aggregate_byte_cap"] - self.total_bytes)

    def consume(self, response, record, planned, item, target=None):
        """Read at most both remaining limits, accounting before local writes."""
        encoding = response.headers.get("Content-Encoding", "identity")
        if encoding.lower() != "identity":
            raise StopAcquisition("unexpected_content_encoding")
        length = response.headers.get("Content-Length")
        if length is not None:
            if not re.fullmatch(r"[0-9]+", str(length)):
                raise StopAcquisition("invalid_content_length")
            length = int(length)
            record["content_length"] = length
            if length > self.remaining(planned, item):
                raise StopAcquisition("advertised_length_exceeds_limit")
        hasher = hashlib.sha256()
        prefix, tail = bytearray(), b""
        binary = target is not None
        output = None
        partial = target.with_name(target.name + ".partial") if binary else None
        try:
            if binary:
                output = partial.open("xb")
            while True:
                allowance = self.remaining(planned, item)
                if length is not None and record["body_bytes"] == length:
                    record["body_complete"] = True
                    break
                if allowance <= 0:
                    raise StopAcquisition("body_limit_reached")
                amount = min(65536, allowance)
                if length is not None:
                    amount = min(amount, length - record["body_bytes"])
                interrupted = False
                try:
                    block = response.read(amount)
                except http.client.IncompleteRead as exc:
                    block, interrupted = exc.partial, True
                self.total_bytes += len(block)
                item["body_bytes"] += len(block)
                record["body_bytes"] += len(block)
                if len(block) > amount:
                    raise StopAcquisition("response_exceeded_read_limit")
                if not block:
                    if interrupted or (length is not None and record["body_bytes"] != length):
                        raise StopAcquisition("incomplete_response")
                    record["body_complete"] = True
                    break
                hasher.update(block)
                if binary:
                    if self.key.lower().encode() in (tail + block).lower():
                        output.close()
                        output = None
                        partial.unlink()
                        item["retained"] = False
                        raise StopAcquisition("credential_echo_suppressed")
                    tail = (tail + block)[-(len(self.key) - 1):]
                    if len(prefix) < len(HDF5_MAGIC):
                        prefix.extend(block[:len(HDF5_MAGIC) - len(prefix)])
                        if not HDF5_MAGIC.startswith(prefix):
                            raise StopAcquisition("not_hdf5")
                    output.write(block)
                    item["file_bytes"] += len(block)
                if interrupted:
                    raise StopAcquisition("incomplete_response")
            if binary and bytes(prefix) != HDF5_MAGIC:
                raise StopAcquisition("not_hdf5")
        finally:
            if output is not None:
                output.close()
            if binary and partial.exists():
                item["retained"] = True
                item["partial_path"] = str(partial.relative_to(self.destination))
                # Hash retained bytes even if a local write failed partway through.
                item["file_bytes"] = partial.stat().st_size
                item["sha256"] = file_digest(partial)
            record["body_sha256"] = hasher.hexdigest()

    def open_response(self, url, authenticated):
        headers = {"Accept-Encoding": "identity",
                   "Accept": "*/*" if authenticated else "application/octet-stream"}
        if authenticated:
            headers["api-key"] = self.key
        request = urllib.request.Request(url, headers=headers)
        try:
            return self.opener.open(request, timeout=60)
        except urllib.error.HTTPError as response:
            return response

    def fetch(self, planned):
        target = self.raw_path(planned)
        partial = target.with_name(target.name + ".partial")
        if target.exists() or partial.exists():
            raise StopAcquisition("raw_file_already_exists")
        target.parent.mkdir(parents=True, exist_ok=True)
        item = dict(id=planned["id"], url=planned["url"], relative_path=planned["relative_path"],
                    started_utc=datetime.now(timezone.utc).isoformat(), body_bytes=0,
                    file_bytes=0, retained=False, outcome="started", responses=[])
        self.receipt["requests"].append(item)
        self.persist()
        try:
            url = planned["url"]
            for hop in range(2):
                if self.remaining(planned, item) <= 0:
                    raise StopAcquisition("body_limit_reached")
                record = dict(host=API_HOST if hop == 0 else DATA_HOST,
                              path=urllib.parse.urlsplit(planned["url"]).path if hop == 0 else planned["redirect_path"],
                              authenticated=hop == 0, http_status=None, body_bytes=0, body_complete=False)
                item["responses"].append(record)
                response = self.open_response(url, authenticated=hop == 0)
                with response:
                    record["http_status"] = response.code
                    if response.code == 200:
                        self.consume(response, record, planned, item, target)
                        # Exclusive link creation never replaces an existing raw file.
                        os.link(partial, target)
                        partial.unlink()
                        item.pop("partial_path", None)
                        item["outcome"] = "complete"
                        self.completed.add(planned["id"])
                        return
                    self.consume(response, record, planned, item)
                    if response.code != 302 or hop != 0:
                        raise StopAcquisition("unapproved_http_status")
                    url = redirect_url(response.headers.get("Location"), planned["redirect_path"], self.key)
            raise StopAcquisition("redirect_limit_reached")
        except StopAcquisition as exc:
            item["outcome"] = str(exc)
            raise
        except (OSError, http.client.HTTPException) as exc:
            item["outcome"] = "io_failure"
            item["error_type"] = type(exc).__name__
            raise StopAcquisition("io_failure") from None
        except KeyboardInterrupt:
            item["outcome"] = "interrupted"
            raise StopAcquisition("interrupted") from None
        finally:
            item["finished_utc"] = datetime.now(timezone.utc).isoformat()
            self.persist()

    def run(self):
        reason = "bootstrap_downloaded" if self.stage == "bootstrap" else "complete_downloaded"
        stage_record = dict(stage=self.stage, started_utc=datetime.now(timezone.utc).isoformat())
        self.receipt["stages"].append(stage_record)
        try:
            selected = [item for item in self.config["files"]
                        if item["id"] not in self.completed and (self.stage == "complete" or item["bootstrap"])]
            order = {"offsets": 0, "groupcat": 1, "particle_ids": 2}
            selected.sort(key=lambda item: (item["output"], order[item["kind"]], item["chunk"] or 0))
            for planned in selected:
                self.fetch(planned)
        except StopAcquisition as exc:
            reason = str(exc)
        except (OSError, http.client.HTTPException) as exc:
            reason = "io_failure"
            stage_record["error_type"] = type(exc).__name__
        except KeyboardInterrupt:
            reason = "interrupted"
        finally:
            stage_record["finished_utc"] = datetime.now(timezone.utc).isoformat()
            stage_record["outcome"] = reason
            self.receipt["outcome"] = reason
            self.persist()
        print(json.dumps({"outcome": reason, "aggregate_body_bytes": self.total_bytes,
                          "completed_files": len(self.completed)}))
        return self.receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--stage", choices=("bootstrap", "complete"), default="bootstrap")
    parser.add_argument("--bootstrap-validation", type=Path)
    parser.add_argument("--prior-acquisition", type=Path,
                        help="Explicit failed-bootstrap receipt; carry its consumed bytes into a new directory")
    parser.add_argument("--ca-bundle", type=Path, default=Path("/etc/ssl/cert.pem"))
    args = parser.parse_args()
    try:
        session = DevelopmentSession(args.config, args.output_dir, hidden_key(), args.ca_bundle,
                                     args.stage, args.bootstrap_validation, args.prior_acquisition)
        receipt = session.run()
        return 0 if receipt["outcome"] in ("bootstrap_downloaded", "complete_downloaded") else 1
    except (StopAcquisition, OSError, ValueError, getpass.GetPassWarning) as exc:
        reason = str(exc) if isinstance(exc, StopAcquisition) else type(exc).__name__
        print(json.dumps({"outcome": reason}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
