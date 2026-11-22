"""Offline boundaries for staged TNG acquisition; no real key or network."""
import contextlib
import copy
import getpass
import http.client
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch
import urllib.error
import warnings


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "cosmic_development_client", ROOT / "experiments/fetch_cosmic_development.py")
CLIENT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CLIENT)
FAKE_KEY = "c7" * 16
FAKE_TOKEN = "synthetic-signed-query-never-save"
# Only a download fixture; the separate HDF5 schema checker must reject it.
BODY = CLIENT.HDF5_MAGIC + b"download-fixture-not-an-HDF5-dataset"


def fixture_config(cap=100_000, file_cap=4096):
    files = []
    for output in (97, 98, 99):
        for kind, prefix in (("offsets", "offsets"), ("groupcat", "groupcat"),
                             ("particle_ids", "snapshot")):
            for chunk in ([None] if kind == "offsets" else range(4)):
                endpoint = (f"offsets.{output}.hdf5" if kind == "offsets"
                            else f"{prefix}-{output}.{chunk}.hdf5")
                redirect = f"/file/{prefix}/L35n270TNG_DM/{output}/"
                if chunk is not None:
                    redirect += f"{chunk}/"
                if kind == "particle_ids":
                    redirect += "0.2.0.0.0.0/"
                files.append(dict(
                    id=f"{kind}-{output}-{chunk}", kind=kind, output=output, chunk=chunk,
                    url=f"https://{CLIENT.API_HOST}{CLIENT.API_PREFIX}{endpoint}"
                        + ("?dm=ParticleIDs" if kind == "particle_ids" else ""),
                    redirect_path=redirect, relative_path=f"raw/{endpoint}",
                    byte_cap=file_cap, bootstrap=output == 97 and (kind == "offsets" or chunk == 0)))
    return dict(schema_version=1, run=CLIENT.RUN, outputs=[97, 98, 99],
                aggregate_byte_cap=cap, min_free_disk_bytes=1, files=files)


class Response(io.BytesIO):
    def __init__(self, body=BODY, code=200, headers=None, length=True):
        super().__init__(body)
        self.code = code
        self.headers = {"Content-Length": str(len(body))} if length else {}
        self.headers.update(headers or {})
        self.read_sizes = []

    def read(self, size=-1):
        self.read_sizes.append(size)
        return super().read(size)


class DevelopmentAcquisitionTests(unittest.TestCase):
    def setUp(self):
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        self.root = Path(self.stack.enter_context(tempfile.TemporaryDirectory()))
        self.config = fixture_config()
        self.config_path = self.root / "config.json"
        self.destination = self.root / "acquisition"
        self.ca = self.root / "ca.pem"
        self.ca.write_text("offline mock CA")
        self.context = Mock()
        self.stack.enter_context(patch.object(CLIENT.ssl, "create_default_context", return_value=self.context))
        self.opener = Mock()
        self.factory = self.stack.enter_context(patch.object(
            CLIENT.urllib.request, "build_opener", return_value=self.opener))

    def session(self, responses, **kwargs):
        self.config_path.write_text(json.dumps(self.config))
        self.opener.open.side_effect = responses
        result = CLIENT.DevelopmentSession(self.config_path, self.destination, FAKE_KEY, self.ca, **kwargs)
        self.assertIn(CLIENT.NoRedirect, self.factory.call_args.args)
        self.assertTrue(self.context.check_hostname)
        self.assertEqual(self.context.verify_mode, CLIENT.ssl.CERT_REQUIRED)
        return result

    def run_session(self, session):
        capture = io.StringIO()
        with contextlib.redirect_stdout(capture):
            result = session.run()
        self.assertNotIn(FAKE_KEY, capture.getvalue().lower())
        for path in self.destination.rglob("*"):
            if path.is_file():
                raw = path.read_bytes()
                self.assertNotIn(FAKE_KEY.encode(), raw.lower(), str(path))
                self.assertNotIn(FAKE_TOKEN.encode(), raw, str(path))
        self.assertEqual(json.loads((self.destination / "acquisition.json").read_text()), result)
        return result

    def validation(self, receipt):
        path = self.root / "bootstrap-validation.json"
        value = dict(schema_version=1, outcome="passed", config_sha256=receipt["config_sha256"],
                     acquisition_source_sha256=receipt["acquisition_source_sha256"],
                     acquisition_receipt_sha256=CLIENT.file_digest(self.destination / "acquisition.json"),
                     files={item["id"]: item["sha256"] for item in receipt["requests"]})
        path.write_text(json.dumps(value))
        return path

    def bootstrap(self):
        result = self.run_session(self.session([Response() for _ in range(3)]))
        self.assertEqual(result["outcome"], "bootstrap_downloaded")
        return result, self.validation(result)

    def redirect(self, planned=None, body=b""):
        if planned is None:
            planned = self.config["files"][0]
        return Response(body, 302, {"Location": f"https://{CLIENT.DATA_HOST}"
                                   + planned["redirect_path"] + "?token=" + FAKE_TOKEN})

    def test_manifest_rejects_scope_selector_redirect_and_path_changes(self):
        mutations = [
            lambda c: c.update(run="TNG100-3-Dark"),
            lambda c: c.update(outputs=[96, 97, 98]),
            lambda c: c.update(schema_version=True),
            lambda c: c.update(aggregate_byte_cap=CLIENT.AGGREGATE_CAP + 1),
            lambda c: c.update(min_free_disk_bytes=0),
            lambda c: c["files"].pop(),
            lambda c: c["files"].__setitem__(1, copy.deepcopy(c["files"][0])),
            lambda c: c["files"][0].update(url="http://www.tng-project.org/api/TNG50-4-Dark/files/offsets.97.hdf5"),
            lambda c: c["files"][0].update(url=c["files"][0]["url"] + "?secret=1"),
            lambda c: c["files"][0].update(redirect_path="/file/snapshot/unselected/"),
            lambda c: c["files"][0].update(relative_path="raw/../escape.hdf5"),
            lambda c: c["files"][0].update(relative_path="/tmp/escape.hdf5"),
            lambda c: c["files"][0].update(bootstrap=False),
            lambda c: c["files"][0].update(byte_cap=CLIENT.KIND_CAPS["offsets"] + 1),
            lambda c: c["files"][0].update(chunk=0),
            lambda c: c["files"][5].update(url=c["files"][5]["url"].replace("ParticleIDs", "Coordinates")),
        ]
        CLIENT.validate_config(self.config)
        for mutation in mutations:
            config = copy.deepcopy(self.config)
            mutation(config)
            with self.subTest(config=config), self.assertRaises(CLIENT.StopAcquisition):
                CLIENT.validate_config(config)
        self.opener.open.assert_not_called()

    def test_redirect_validator_rejects_foreign_path_and_credential(self):
        path = self.config["files"][0]["redirect_path"]
        base = f"https://{CLIENT.DATA_HOST}{path}"
        for url in (None, "https://[", base.replace("https:", "http:"),
                    base.replace(CLIENT.DATA_HOST, "example.org"), base + "wrong/",
                    base.replace(CLIENT.DATA_HOST, "user@" + CLIENT.DATA_HOST),
                    base.replace(CLIENT.DATA_HOST, CLIENT.DATA_HOST + ":443"),
                    base + "#fragment", base + "?key=" + FAKE_KEY, base + "\n"):
            with self.subTest(url=url), self.assertRaises(CLIENT.StopAcquisition):
                CLIENT.redirect_url(url, path, FAKE_KEY)

    def test_hidden_key_refuses_echo_fallback(self):
        def fallback(*args, **kwargs):
            warnings.warn("echo fallback", getpass.GetPassWarning)
            return FAKE_KEY
        with patch.object(CLIENT.getpass, "getpass", side_effect=fallback):
            with self.assertRaises(getpass.GetPassWarning):
                CLIENT.hidden_key()
        with patch.object(CLIENT.getpass, "getpass", return_value="invalid"):
            with self.assertRaises(CLIENT.StopAcquisition):
                CLIENT.hidden_key()

    def test_bootstrap_freezes_inputs_and_only_three_files(self):
        session = self.session([Response() for _ in range(3)])
        result = self.run_session(session)
        self.assertEqual(result["outcome"], "bootstrap_downloaded")
        self.assertEqual(result["aggregate_body_bytes"], 3 * len(BODY))
        self.assertEqual(self.opener.open.call_count, 3)
        self.assertEqual([r["id"] for r in result["requests"]],
                         [f"{kind}-97-{chunk}" for kind, chunk in
                          (("offsets", None), ("groupcat", 0), ("particle_ids", 0))])
        self.assertEqual((self.destination / "config.json").read_bytes(), self.config_path.read_bytes())
        self.assertEqual(CLIENT.file_digest(self.destination / "acquisition_source.py"),
                         result["acquisition_source_sha256"])
        self.assertEqual((self.destination / ".gitignore").read_text(), "raw/\n")
        for item in result["requests"]:
            self.assertEqual(item["sha256"], CLIENT.digest(BODY))
            self.assertEqual((self.destination / item["relative_path"]).read_bytes(), BODY)
        self.assertFalse(list(self.destination.rglob("*.partial")))

    def test_redirect_counts_body_but_never_forwards_key_or_saves_token(self):
        responses = [self.redirect(body=b"move"), Response(), Response(), Response()]
        result = self.run_session(self.session(responses))
        self.assertEqual(result["outcome"], "bootstrap_downloaded")
        self.assertEqual(result["aggregate_body_bytes"], 3 * len(BODY) + 4)
        first, second = [call.args[0] for call in self.opener.open.call_args_list[:2]]
        self.assertEqual(dict(first.header_items())["Api-key"], FAKE_KEY)
        self.assertEqual(dict(first.header_items())["Accept"], "*/*")
        self.assertEqual(dict(second.header_items())["Accept"], "application/octet-stream")
        self.assertNotIn("Api-key", dict(second.header_items()))
        self.assertIn(FAKE_TOKEN, second.full_url)
        self.assertEqual(result["requests"][0]["responses"][1]["host"], CLIENT.DATA_HOST)

    def test_bad_redirect_does_not_send_second_request(self):
        response = Response(b"wrong", 302, {"Location": "https://unrelated.invalid/"})
        result = self.run_session(self.session([response]))
        self.assertEqual(result["outcome"], "unapproved_redirect")
        self.assertEqual(result["aggregate_body_bytes"], 5)
        self.opener.open.assert_called_once()

    def test_second_redirect_is_not_followed(self):
        result = self.run_session(self.session([self.redirect(), self.redirect(body=b"again")]))
        self.assertEqual(result["outcome"], "unapproved_http_status")
        self.assertEqual(result["aggregate_body_bytes"], 5)
        self.assertEqual(self.opener.open.call_count, 2)

    def test_error_body_counted_and_http_error_message_not_retained(self):
        error = urllib.error.HTTPError(self.config["files"][0]["url"], 403,
                                       "untrusted " + FAKE_KEY, {}, io.BytesIO(FAKE_KEY.encode()))
        result = self.run_session(self.session([error]))
        self.assertEqual(result["outcome"], "unapproved_http_status")
        self.assertEqual(result["aggregate_body_bytes"], 32)
        self.assertFalse(result["requests"][0]["retained"])

    def test_advertised_oversize_stops_without_reading_body(self):
        self.config["files"][0]["byte_cap"] = 32
        response = Response()
        result = self.run_session(self.session([response]))
        self.assertEqual(result["outcome"], "advertised_length_exceeds_limit")
        self.assertEqual(result["aggregate_body_bytes"], 0)
        self.assertEqual(response.read_sizes, [])

    def test_unadvertised_body_stops_exactly_at_file_cap(self):
        self.config["files"][0]["byte_cap"] = 12
        response = Response(length=False)
        result = self.run_session(self.session([response]))
        self.assertEqual(result["outcome"], "body_limit_reached")
        self.assertEqual(result["aggregate_body_bytes"], 12)
        self.assertEqual(response.read_sizes, [12])
        item = result["requests"][0]
        self.assertEqual((self.destination / item["partial_path"]).read_bytes(), BODY[:12])
        self.assertFalse((self.destination / item["relative_path"]).exists())

    def test_redirect_bytes_reduce_remaining_aggregate_budget(self):
        self.config["aggregate_byte_cap"] = len(BODY) + 3
        result = self.run_session(self.session([self.redirect(body=b"move"), Response()]))
        self.assertEqual(result["outcome"], "advertised_length_exceeds_limit")
        self.assertEqual(result["aggregate_body_bytes"], 4)
        self.assertEqual(self.opener.open.call_count, 2)

    def test_incomplete_read_preserves_partial_bytes_and_budget(self):
        response = Response(headers={"Content-Length": "100"})
        response.read = Mock(side_effect=[BODY[:10], http.client.IncompleteRead(BODY[10:15], 85)])
        result = self.run_session(self.session([response]))
        self.assertEqual(result["outcome"], "incomplete_response")
        self.assertEqual(result["aggregate_body_bytes"], 15)
        item = result["requests"][0]
        self.assertEqual(item["file_bytes"], 15)
        self.assertEqual((self.destination / item["partial_path"]).read_bytes(), BODY[:15])

    def test_unexpected_eof_preserves_partial_and_stops(self):
        result = self.run_session(self.session([Response(headers={"Content-Length": "100"})]))
        self.assertEqual(result["outcome"], "incomplete_response")
        self.assertEqual(result["aggregate_body_bytes"], len(BODY))

    def test_transport_failure_and_interrupt_do_not_claim_completion(self):
        for error, expected in ((OSError("remote " + FAKE_KEY), "io_failure"),
                                (KeyboardInterrupt(), "interrupted")):
            with self.subTest(expected=expected):
                self.destination = self.root / expected
                response = Response(headers={"Content-Length": "100"})
                response.read = Mock(side_effect=[BODY[:10], error])
                result = self.run_session(self.session([response]))
                self.assertEqual(result["outcome"], expected)
                self.assertEqual(result["requests"][0]["outcome"], expected)
                self.assertEqual(result["aggregate_body_bytes"], 10)

    def test_credential_echo_split_across_chunks_removes_partial(self):
        response = Response(length=False)
        response.read = Mock(side_effect=[CLIENT.HDF5_MAGIC + FAKE_KEY[:16].encode(),
                                         FAKE_KEY[16:].encode()])
        result = self.run_session(self.session([response]))
        self.assertEqual(result["outcome"], "credential_echo_suppressed")
        self.assertEqual(result["aggregate_body_bytes"], 40)
        self.assertFalse(list(self.destination.rglob("*.partial")))
        self.assertFalse(result["requests"][0]["retained"])

    def test_local_write_failure_still_accounts_for_received_bytes(self):
        session = self.session([Response()])
        original_open = Path.open

        class FailingWriter:
            def __init__(self, actual):
                self.actual = actual

            def write(self, block):
                raise OSError("simulated local write failure")

            def close(self):
                self.actual.close()

        def open_with_failed_partial(path, *args, **kwargs):
            actual = original_open(path, *args, **kwargs)
            return FailingWriter(actual) if path.suffix == ".partial" and args == ("xb",) else actual

        with patch.object(Path, "open", open_with_failed_partial):
            result = self.run_session(session)
        self.assertEqual(result["outcome"], "io_failure")
        self.assertEqual(result["aggregate_body_bytes"], len(BODY))
        self.assertEqual(result["requests"][0]["file_bytes"], 0)
        self.assertEqual(result["requests"][0]["sha256"], CLIENT.digest(b""))

    def test_non_hdf5_and_encoded_responses_stop_before_valid_file(self):
        for label, response, expected in (
                ("html", Response(b"<html>login required"), "not_hdf5"),
                ("gzip", Response(headers={"Content-Encoding": "gzip"}), "unexpected_content_encoding"),
                ("length", Response(headers={"Content-Length": "invalid"}), "invalid_content_length")):
            with self.subTest(label=label):
                self.destination = self.root / label
                result = self.run_session(self.session([response]))
                self.assertEqual(result["outcome"], expected)
                self.assertFalse(list((self.destination / "raw").glob("*.hdf5")))

    def test_existing_destination_and_raw_file_are_never_overwritten(self):
        session = self.session([Response()])
        with self.assertRaisesRegex(CLIENT.StopAcquisition, "output_directory_exists"):
            self.session([])
        planned = self.config["files"][0]
        path = self.destination / planned["relative_path"]
        path.parent.mkdir()
        path.write_bytes(b"existing")
        result = self.run_session(session)
        self.assertEqual(result["outcome"], "raw_file_already_exists")
        self.assertEqual(path.read_bytes(), b"existing")
        self.opener.open.assert_not_called()

    def test_raw_symlink_escape_is_rejected(self):
        session = self.session([])
        outside = self.root / "elsewhere"
        outside.mkdir()
        (self.destination / "raw").symlink_to(outside, target_is_directory=True)
        result = self.run_session(session)
        self.assertEqual(result["outcome"], "raw_path_symlink")
        self.opener.open.assert_not_called()
        self.assertEqual(list(outside.iterdir()), [])

    def test_disk_floor_checked_before_creating_destination(self):
        with patch.object(CLIENT.shutil, "disk_usage", return_value=Mock(free=0)):
            with self.assertRaisesRegex(CLIENT.StopAcquisition, "insufficient_free_disk"):
                self.session([])
        self.assertFalse(self.destination.exists())

    def test_complete_stage_requires_schema_gate_before_requests(self):
        self.bootstrap()
        self.opener.open.reset_mock()
        with self.assertRaisesRegex(CLIENT.StopAcquisition, "bootstrap_validation_required"):
            self.session([], stage="complete")
        self.opener.open.assert_not_called()

    def test_complete_stage_carries_budget_and_downloads_only_remaining_files(self):
        receipt, validation = self.bootstrap()
        bootstrap_raw = (self.destination / "acquisition.json").read_bytes()
        self.opener.open.reset_mock()
        session = self.session([Response() for _ in range(24)], stage="complete", bootstrap_validation=validation)
        result = self.run_session(session)
        self.assertEqual(result["outcome"], "complete_downloaded")
        self.assertEqual(result["aggregate_body_bytes"], 27 * len(BODY))
        self.assertEqual(len(result["requests"]), 27)
        self.assertEqual(self.opener.open.call_count, 24)
        self.assertEqual(result["bootstrap_validation_sha256"], CLIENT.file_digest(validation))
        self.assertEqual((self.destination / "bootstrap_validation.json").read_bytes(), validation.read_bytes())
        self.assertEqual((self.destination / "bootstrap_acquisition.json").read_bytes(), bootstrap_raw)
        self.assertEqual(result["bootstrap_acquisition_sha256"], CLIENT.digest(bootstrap_raw))
        self.assertNotEqual((self.destination / "acquisition.json").read_bytes(), bootstrap_raw)

    def test_existing_bootstrap_snapshot_must_match_exact_bytes(self):
        receipt, validation = self.bootstrap()
        bootstrap_raw = (self.destination / "acquisition.json").read_bytes()
        snapshot = self.destination / "bootstrap_acquisition.json"
        snapshot.write_bytes(b"different snapshot")
        self.opener.open.reset_mock()
        with self.assertRaisesRegex(CLIENT.StopAcquisition, "bootstrap_receipt_snapshot_mismatch"):
            self.session([], stage="complete", bootstrap_validation=validation)
        self.opener.open.assert_not_called()
        self.assertEqual(snapshot.read_bytes(), b"different snapshot")
        snapshot.write_bytes(bootstrap_raw)
        result = self.run_session(self.session([Response() for _ in range(24)],
                                  stage="complete", bootstrap_validation=validation))
        self.assertEqual(result["outcome"], "complete_downloaded")
        self.assertEqual(snapshot.read_bytes(), bootstrap_raw)

    def test_schema_gate_must_bind_exact_bootstrap_receipt(self):
        receipt, validation = self.bootstrap()
        data = json.loads(validation.read_text())
        data["acquisition_receipt_sha256"] = "0" * 64
        validation.write_text(json.dumps(data))
        self.opener.open.reset_mock()
        with self.assertRaisesRegex(CLIENT.StopAcquisition, "bootstrap_receipt_not_validated"):
            self.session([], stage="complete", bootstrap_validation=validation)
        self.opener.open.assert_not_called()
        self.assertFalse((self.destination / "bootstrap_acquisition.json").exists())

    def test_complete_stage_cannot_reset_already_consumed_budget(self):
        self.config["aggregate_byte_cap"] = 3 * len(BODY) + 1
        receipt, validation = self.bootstrap()
        response = Response()
        session = self.session([response], stage="complete", bootstrap_validation=validation)
        result = self.run_session(session)
        self.assertEqual(result["outcome"], "advertised_length_exceeds_limit")
        self.assertEqual(result["aggregate_body_bytes"], receipt["aggregate_body_bytes"])
        self.assertEqual(result["remaining_body_bytes"], 1)
        self.assertEqual(response.read_sizes, [])

    def test_tampered_bootstrap_file_or_source_stops_continuation(self):
        receipt, validation = self.bootstrap()
        source = self.destination / "acquisition_source.py"
        source_raw = source.read_bytes()
        source.write_bytes(source_raw + b"\n# altered\n")
        self.opener.open.reset_mock()
        with self.assertRaisesRegex(CLIENT.StopAcquisition, "frozen_source_modified"):
            self.session([], stage="complete", bootstrap_validation=validation)
        source.write_bytes(source_raw)
        (self.destination / receipt["requests"][0]["relative_path"]).write_bytes(b"tampered")
        with self.assertRaisesRegex(CLIENT.StopAcquisition, "bootstrap_file_mismatch"):
            self.session([], stage="complete", bootstrap_validation=validation)
        self.opener.open.assert_not_called()

    def test_tampered_budget_and_response_receipt_stop_continuation(self):
        receipt, validation = self.bootstrap()
        receipt_path = self.destination / "acquisition.json"
        for field in ("aggregate", "response", "status", "file_bytes"):
            altered = copy.deepcopy(receipt)
            if field == "aggregate":
                altered["aggregate_body_bytes"] -= 1
            elif field == "response":
                altered["requests"][0]["responses"][0]["body_bytes"] -= 1
            elif field == "status":
                altered["requests"][0]["responses"][0]["http_status"] = 403
            else:
                altered["requests"][0]["file_bytes"] += 1
            receipt_path.write_text(json.dumps(altered))
            self.opener.open.reset_mock()
            with self.subTest(field=field), self.assertRaises(CLIENT.StopAcquisition):
                self.session([], stage="complete", bootstrap_validation=validation)
            self.opener.open.assert_not_called()

    def test_failed_gate_or_changed_config_cannot_start_complete_stage(self):
        receipt, validation = self.bootstrap()
        invalid = json.loads(validation.read_text())
        invalid["outcome"] = "failed"
        validation.write_text(json.dumps(invalid))
        self.opener.open.reset_mock()
        with self.assertRaisesRegex(CLIENT.StopAcquisition, "bootstrap_not_passed"):
            self.session([], stage="complete", bootstrap_validation=validation)
        validation = self.validation(receipt)
        self.config["aggregate_byte_cap"] -= 1
        with self.assertRaisesRegex(CLIENT.StopAcquisition, "bootstrap_provenance_mismatch"):
            self.session([], stage="complete", bootstrap_validation=validation)
        self.opener.open.assert_not_called()

    def test_manual_continuation_retains_failed_bytes_through_both_stages(self):
        failed = self.run_session(self.session([Response(b"not acceptable", 406)]))
        prior_dir = self.destination
        prior_raw = (prior_dir / "acquisition.json").read_bytes()
        self.destination = self.root / "attempt-02"
        session = self.session([Response() for _ in range(3)],
                               prior_acquisition=prior_dir / "acquisition.json")
        result = self.run_session(session)
        self.assertEqual(result["outcome"], "bootstrap_downloaded")
        self.assertEqual(result["aggregate_body_bytes"], failed["aggregate_body_bytes"] + 3 * len(BODY))
        self.assertEqual(result["prior_body_bytes"], failed["aggregate_body_bytes"])
        self.assertTrue(result["manual_continuation"])
        self.assertEqual(result["prior_acquisition_sha256"], CLIENT.digest(prior_raw))
        self.assertEqual((self.destination / "prior_acquisition.json").read_bytes(), prior_raw)
        self.assertEqual((prior_dir / "acquisition.json").read_bytes(), prior_raw)
        validation = self.validation(result)
        complete = self.run_session(self.session([Response() for _ in range(24)],
                                   stage="complete", bootstrap_validation=validation))
        self.assertEqual(complete["outcome"], "complete_downloaded")
        self.assertEqual(complete["aggregate_body_bytes"], failed["aggregate_body_bytes"] + 27 * len(BODY))

    def test_manual_continuation_rejects_changed_config_and_bad_prior_counts(self):
        failed = self.run_session(self.session([Response(b"not acceptable", 406)]))
        prior_path = self.destination / "acquisition.json"
        self.destination = self.root / "attempt-02"
        for field in ("config", "cap", "aggregate", "response", "retained"):
            altered = copy.deepcopy(failed)
            if field == "config":
                altered["config_sha256"] = "0" * 64
            elif field == "cap":
                altered["aggregate_byte_cap"] += 1
            elif field == "aggregate":
                altered["aggregate_body_bytes"] += 1
                altered["remaining_body_bytes"] -= 1
            elif field == "response":
                altered["requests"][0]["responses"][0]["body_bytes"] += 1
            else:
                altered["requests"][0]["retained"] = True
            prior_path.write_text(json.dumps(altered))
            self.opener.open.reset_mock()
            with self.subTest(field=field), self.assertRaises(CLIENT.StopAcquisition):
                self.session([], prior_acquisition=prior_path)
            self.opener.open.assert_not_called()
            self.assertFalse(self.destination.exists())

    def test_manual_continuation_rejects_successful_prior_bootstrap(self):
        self.bootstrap()
        prior_path = self.destination / "acquisition.json"
        self.destination = self.root / "attempt-02"
        self.opener.open.reset_mock()
        with self.assertRaisesRegex(CLIENT.StopAcquisition, "unsupported_prior_acquisition"):
            self.session([], prior_acquisition=prior_path)
        self.opener.open.assert_not_called()

    def test_manual_continuation_checks_frozen_prior_source_and_copied_receipt(self):
        failed = self.run_session(self.session([Response(b"not acceptable", 406)]))
        prior_dir = self.destination
        prior_source = prior_dir / "acquisition_source.py"
        source_raw = prior_source.read_bytes()
        prior_source.write_bytes(b"changed")
        self.destination = self.root / "attempt-02"
        self.opener.open.reset_mock()
        with self.assertRaisesRegex(CLIENT.StopAcquisition, "prior_provenance_mismatch"):
            self.session([], prior_acquisition=prior_dir / "acquisition.json")
        self.opener.open.assert_not_called()
        prior_source.write_bytes(source_raw)
        result = self.run_session(self.session([Response() for _ in range(3)],
                                  prior_acquisition=prior_dir / "acquisition.json"))
        validation = self.validation(result)
        (self.destination / "prior_acquisition.json").write_text("{}")
        self.opener.open.reset_mock()
        with self.assertRaisesRegex(CLIENT.StopAcquisition, "invalid_prior_budget"):
            self.session([], stage="complete", bootstrap_validation=validation)
        self.opener.open.assert_not_called()


if __name__ == "__main__":
    unittest.main()
