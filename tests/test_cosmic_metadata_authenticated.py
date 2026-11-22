"""Offline checks of authenticated metadata boundaries; no actual credentials."""
import contextlib
import getpass
import gzip
import hashlib
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
    "authenticated_cosmic_metadata", ROOT / "experiments/fetch_cosmic_metadata.py")
CLIENT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CLIENT)
FAKE_KEY = "a1" * 16
RUN_URL = "https://" + CLIENT.HOST + CLIENT.RUN_PATH


class Response(io.BytesIO):
    def __init__(self, body, code=200, headers=None):
        super().__init__(body)
        self.code = code
        self.headers = {"Content-Type": "application/json"}
        self.headers.update(headers or {})
        self.read_sizes = []

    def read(self, size=-1):
        self.read_sizes.append(size)
        return super().read(size)


def json_response(data):
    return Response(json.dumps(data).encode())


class AuthenticatedMetadataTests(unittest.TestCase):
    def setUp(self):
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        self.root = Path(self.stack.enter_context(tempfile.TemporaryDirectory()))
        self.counter = 0

    def session(self, responses, cap=1_048_576, prior=None):
        self.counter += 1
        self.stack.enter_context(patch.object(CLIENT, "CAP", cap))
        if prior is None:
            prior = self.root / "prior.json"
            prior.write_text(json.dumps({"aggregate_body_cap_bytes": cap,
                                         "aggregate_body_bytes": 55}))
        ca = self.root / "ca.pem"
        ca.write_text("mock trust bundle; no connection is made")
        self.stack.enter_context(patch.object(CLIENT.ssl, "create_default_context", return_value=Mock()))
        opener = Mock()
        opener.open.side_effect = responses
        factory = self.stack.enter_context(patch.object(CLIENT.urllib.request, "build_opener", return_value=opener))
        destination = self.root / f"output-{self.counter}"
        session = CLIENT.MetadataSession(destination, FAKE_KEY, ca, prior)
        self.assertIn(CLIENT.NoRedirect, factory.call_args.args)
        return session, opener

    def assert_no_key_saved(self, session):
        for path in session.destination.iterdir():
            self.assertNotIn(FAKE_KEY.encode(), path.read_bytes().lower(), path.name)

    def run_session(self, session):
        capture = io.StringIO()
        with contextlib.redirect_stdout(capture):
            result = session.run()
        self.assertNotIn(FAKE_KEY, capture.getvalue().lower())
        self.assert_no_key_saved(session)
        return result

    def test_exact_metadata_url_boundary_and_https_normalization(self):
        self.assertEqual(CLIENT.metadata_url(RUN_URL.replace("https:", "http:"), {CLIENT.RUN_PATH}), RUN_URL)
        denied = [
            "https://example.org" + CLIENT.RUN_PATH,
            "https://www.tng-project.org.evil.example" + CLIENT.RUN_PATH,
            "https://user@www.tng-project.org" + CLIENT.RUN_PATH,
            RUN_URL + "?api_key=ignored", RUN_URL + "#fragment",
            RUN_URL + "snapshots/99/halos/", RUN_URL + "files/snapshot-99/",
            RUN_URL.replace("TNG50-4-Dark", "TNG100-3-Dark"),
            "https://[", None,
        ]
        for url in denied:
            with self.subTest(url=url), self.assertRaises(CLIENT.StopAcquisition):
                CLIENT.metadata_url(url, {CLIENT.RUN_PATH})

    def test_hidden_key_refuses_getpass_echo_fallback(self):
        def fallback(*args, **kwargs):
            warnings.warn("fallback attempted", getpass.GetPassWarning)
            return FAKE_KEY
        with patch.object(CLIENT.getpass, "getpass", side_effect=fallback):
            with self.assertRaises(getpass.GetPassWarning):
                CLIENT.hidden_key()
        with patch.object(CLIENT.getpass, "getpass", return_value="bad"):
            with self.assertRaises(CLIENT.StopAcquisition):
                CLIENT.hidden_key()

    def test_shared_budget_carries_prior_bytes_and_stops_at_cap(self):
        response = Response(b"0123456789abcdef")
        session, opener = self.session([response], cap=63)
        result = self.run_session(session)
        self.assertEqual(result["prior_body_bytes"], 55)
        self.assertEqual(result["new_body_bytes"], 8)
        self.assertEqual(result["aggregate_body_bytes"], 63)
        self.assertEqual(result["remaining_body_budget_bytes"], 0)
        self.assertEqual(result["outcome"], "incomplete_body")
        self.assertEqual(response.read_sizes, [8])
        opener.open.assert_called_once()

    def test_partial_read_bytes_are_counted_and_preserved(self):
        response = Response(b"")
        response.read = Mock(side_effect=[b"abc", http.client.IncompleteRead(b"de", 10)])
        session, opener = self.session([response])
        result = self.run_session(session)
        self.assertEqual(result["new_body_bytes"], 5)
        self.assertEqual(result["outcome"], "transport_failure")
        self.assertEqual((session.destination / "01-run.json").read_bytes(), b"abcde")
        self.assertFalse(result["requests"][0]["body_complete"])
        opener.open.assert_called_once()

    def test_credential_echo_in_body_header_or_decoded_json_is_suppressed(self):
        escaped = "".join("\\u%04x" % ord(char) for char in FAKE_KEY)
        responses = [
            Response(FAKE_KEY.encode()),
            Response(b"{}", headers={"Content-Type": "application/json; " + FAKE_KEY}),
            Response(('"' + escaped + '"').encode()),
        ]
        for response in responses:
            with self.subTest(response=response):
                session, opener = self.session([response])
                result = self.run_session(session)
                self.assertEqual(result["outcome"], "credential_echo_suppressed")
                self.assertFalse(result["requests"][0]["retained"])
                self.assertFalse((session.destination / "01-run.json").exists())
                self.assertGreater(result["new_body_bytes"], 0)
                opener.open.assert_called_once()

    def test_redirect_response_is_retained_but_never_followed(self):
        response = urllib.error.HTTPError(RUN_URL, 302, "redirect",
                                           {"Location": "https://elsewhere.invalid/"}, io.BytesIO(b"move"))
        session, opener = self.session([response])
        result = self.run_session(session)
        self.assertEqual(result["outcome"], "http_error_or_redirect")
        self.assertEqual(result["new_body_bytes"], 4)
        self.assertEqual(result["requests"][0]["http_status"], 302)
        opener.open.assert_called_once()
        self.assertIsNone(CLIENT.NoRedirect().redirect_request(None, None, 302, "", {}, RUN_URL))

    def test_truncated_unicode_escaped_key_is_not_retained(self):
        escaped = "".join("\\u%04x" % ord(char) for char in FAKE_KEY)
        body = ('{"echo":"' + escaped).encode()  # Intentionally invalid/incomplete JSON.
        session, opener = self.session([Response(body)])
        result = self.run_session(session)
        self.assertEqual(result["outcome"], "credential_echo_suppressed")
        self.assertFalse((session.destination / "01-run.json").exists())
        opener.open.assert_called_once()

    def test_unexpected_encoding_is_counted_without_retaining_opaque_body(self):
        compressed = gzip.compress(json.dumps({"echo": FAKE_KEY}).encode())
        session, opener = self.session([Response(compressed, headers={"Content-Encoding": "gzip"})])
        result = self.run_session(session)
        self.assertEqual(result["outcome"], "unexpected_content_encoding")
        self.assertEqual(result["new_body_bytes"], len(compressed))
        self.assertFalse(result["requests"][0]["retained"])
        self.assertFalse((session.destination / "01-run.json").exists())
        opener.open.assert_called_once()

    def test_last_three_stored_outputs_are_selected_without_reading_arrays(self):
        numbers = [12, 2, 10, 8]
        schedule = [{"number": n, "url": RUN_URL.replace("https:", "http:") + f"snapshots/{n}/"}
                    for n in numbers]
        session, opener = self.session([
            json_response({"snapshots": RUN_URL + "snapshots/"}),
            json_response(schedule), json_response({}), json_response({}), json_response({}),
        ])
        result = self.run_session(session)
        self.assertEqual(result["selected_outputs"], [8, 10, 12])
        self.assertEqual(result["outcome"], "metadata_requests_complete")
        self.assertFalse(result["complete_D1_manifest"])
        self.assertFalse(result["numerical_arrays_requested"])
        self.assertEqual(opener.open.call_count, 5)
        urls = [call.args[0].full_url for call in opener.open.call_args_list]
        self.assertEqual(urls[-3:], [RUN_URL + f"snapshots/{n}/" for n in [8, 10, 12]])
        for call in opener.open.call_args_list:
            request = call.args[0]
            self.assertEqual(request.get_header("Api-key"), FAKE_KEY)
            self.assertEqual(request.get_header("Accept-encoding"), "identity")

    def test_invalid_remote_url_stops_with_budget_record(self):
        session, opener = self.session([json_response({"snapshots": "https://["})])
        result = self.run_session(session)
        self.assertEqual(result["outcome"], "unapproved_metadata_url")
        self.assertGreater(result["new_body_bytes"], 0)
        opener.open.assert_called_once()

    def test_negative_or_duplicate_schedule_numbers_are_rejected(self):
        for numbers in ([1, 2, -1], [1, 2, 2]):
            with self.subTest(numbers=numbers):
                session, opener = self.session([
                    json_response({"snapshots": RUN_URL + "snapshots/"}),
                    json_response([{"number": n, "url": RUN_URL + f"snapshots/{n}/"} for n in numbers]),
                ])
                result = self.run_session(session)
                self.assertNotEqual(result["outcome"], "metadata_requests_complete")
                self.assertEqual(opener.open.call_count, 2)

    def retained_snapshot_metadata(self):
        numbers = [8, 10, 12]
        schedule = [{"number": n, "url": RUN_URL + f"snapshots/{n}/"} for n in numbers]
        responses = [json_response({"snapshots": RUN_URL + "snapshots/"}), json_response(schedule)]
        for number in numbers:
            responses.append(json_response({"files": {
                kind: RUN_URL.replace("https:", "http:") + f"files/{kind}-{number}/"
                for kind in ("snapshot", "groupcat")}}))
        session, _ = self.session(responses)
        manifest = self.run_session(session)
        return session.destination, manifest

    def test_file_list_continuation_carries_usage_and_never_follows_binary_links(self):
        metadata, previous = self.retained_snapshot_metadata()
        binary_link = RUN_URL + "files/snapshot-8.0.hdf5"
        responses = [json_response({"files": [binary_link]}) for _ in range(6)]
        session, opener = self.session(responses, prior=metadata / "acquisition.json")
        with contextlib.redirect_stdout(io.StringIO()):
            result = session.file_lists(metadata)
        self.assertEqual(result["outcome"], "metadata_requests_complete")
        self.assertEqual(result["prior_body_bytes"], previous["aggregate_body_bytes"])
        self.assertEqual(result["aggregate_body_bytes"], result["prior_body_bytes"] + result["new_body_bytes"])
        self.assertEqual(result["selected_outputs"], [8, 10, 12])
        self.assertEqual(opener.open.call_count, 6)
        urls = [call.args[0].full_url for call in opener.open.call_args_list]
        expected = [RUN_URL + f"files/{kind}-{number}/"
                    for number in [8, 10, 12] for kind in ("snapshot", "groupcat")]
        self.assertEqual(urls, expected)
        self.assertNotIn(binary_link, urls)
        self.assertFalse(result["complete_D1_manifest"])
        self.assert_no_key_saved(session)

    def test_file_list_continuation_stops_before_network_on_source_hash_mismatch(self):
        metadata, previous = self.retained_snapshot_metadata()
        source_item = next(item for item in previous["requests"] if item["label"] == "snapshot-8")
        (metadata / source_item["path"]).write_text("{}")
        session, opener = self.session([], prior=metadata / "acquisition.json")
        with contextlib.redirect_stdout(io.StringIO()):
            result = session.file_lists(metadata)
        self.assertEqual(result["outcome"], "retained_snapshot_hash_mismatch")
        self.assertEqual(result["new_body_bytes"], 0)
        self.assertEqual(result["aggregate_body_bytes"], previous["aggregate_body_bytes"])
        opener.open.assert_not_called()

    def continuation_result(self, session, metadata):
        with contextlib.redirect_stdout(io.StringIO()):
            result = session.file_lists(metadata)
        retained = json.loads((session.destination / "acquisition.json").read_text())
        self.assertEqual(result, retained)
        self.assertNotEqual(result["outcome"], "metadata_requests_complete")
        self.assertEqual(result["aggregate_body_bytes"],
                         result["prior_body_bytes"] + sum(item["body_bytes"] for item in result["requests"]))
        self.assert_no_key_saved(session)
        return result

    def test_continuation_requires_three_nonnegative_plain_integer_outputs(self):
        for selected in ([8, 10, -1], [8, 10, True], [8, 10, 12.0],
                         [8, 10, "12"], [8, 10, []], None):
            with self.subTest(selected=selected):
                metadata, previous = self.retained_snapshot_metadata()
                previous["selected_outputs"] = selected
                (metadata / "acquisition.json").write_text(json.dumps(previous))
                session, opener = self.session([], prior=metadata / "acquisition.json")
                result = self.continuation_result(session, metadata)
                self.assertEqual(result["new_body_bytes"], 0)
                opener.open.assert_not_called()

    def test_continuation_rejects_unsuccessful_or_incomplete_source_receipts(self):
        for mutation in ({"http_status": 403}, {"body_complete": False}, {"retained": False}):
            with self.subTest(mutation=mutation):
                metadata, previous = self.retained_snapshot_metadata()
                item = next(item for item in previous["requests"] if item["label"] == "snapshot-8")
                item.update(mutation)
                (metadata / "acquisition.json").write_text(json.dumps(previous))
                session, opener = self.session([], prior=metadata / "acquisition.json")
                result = self.continuation_result(session, metadata)
                self.assertEqual(result["new_body_bytes"], 0)
                opener.open.assert_not_called()

    def test_continuation_bad_snapshot_schema_finalizes_usage(self):
        for payload in ([], None, {"files": []}, {"files": None}):
            with self.subTest(payload=payload):
                metadata, previous = self.retained_snapshot_metadata()
                item = next(item for item in previous["requests"] if item["label"] == "snapshot-10")
                body = json.dumps(payload).encode()
                (metadata / item["path"]).write_bytes(body)
                item["sha256"] = hashlib.sha256(body).hexdigest()
                item["body_bytes"] = len(body)
                (metadata / "acquisition.json").write_text(json.dumps(previous))
                session, opener = self.session([json_response({"files": []}) for _ in range(6)],
                                               prior=metadata / "acquisition.json")
                self.continuation_result(session, metadata)
                self.assertLessEqual(opener.open.call_count, 2)

    def test_continuation_malformed_or_missing_source_finalizes_usage(self):
        for missing in (False, True):
            with self.subTest(missing=missing):
                metadata, previous = self.retained_snapshot_metadata()
                item = next(item for item in previous["requests"] if item["label"] == "snapshot-10")
                source = metadata / item["path"]
                if missing:
                    source.unlink()
                else:
                    source.write_bytes(b"{")
                    item["sha256"] = hashlib.sha256(b"{").hexdigest()
                    item["body_bytes"] = 1
                    (metadata / "acquisition.json").write_text(json.dumps(previous))
                session, opener = self.session([json_response({"files": []}) for _ in range(6)],
                                               prior=metadata / "acquisition.json")
                self.continuation_result(session, metadata)
                self.assertLessEqual(opener.open.call_count, 2)

    def test_local_body_write_failure_still_records_consumed_budget(self):
        payload = {"snapshots": RUN_URL + "snapshots/"}
        session, opener = self.session([json_response(payload)])
        original_write = Path.write_bytes
        def fail_only_response(path, content):
            if path == session.destination / "01-run.json":
                raise OSError("private-local-detail")
            return original_write(path, content)
        with patch.object(Path, "write_bytes", new=fail_only_response):
            result = self.run_session(session)
        self.assertNotEqual(result["outcome"], "metadata_requests_complete")
        self.assertEqual(result["new_body_bytes"], len(json.dumps(payload).encode()))
        self.assertNotIn("private-local-detail", json.dumps(result))
        self.assertTrue((session.destination / "acquisition.json").is_file())
        opener.open.assert_called_once()

    def test_retained_live_chain_hashes_and_shared_budget(self):
        base = ROOT / "data/cosmic-source-qualification"
        prior_raw = (base / "2026-11-12/acquisition.json").read_bytes()
        total = json.loads(prior_raw)["aggregate_body_bytes"]
        for name in ("tng50-4-dark-metadata", "tng50-4-dark-file-lists"):
            folder = base / "2026-11-19" / name
            raw = (folder / "acquisition.json").read_bytes()
            receipt = json.loads(raw)
            self.assertEqual(receipt["prior_receipt_sha256"], hashlib.sha256(prior_raw).hexdigest())
            self.assertEqual(receipt["prior_body_bytes"], total)
            self.assertEqual(receipt["source_sha256"], hashlib.sha256(
                (folder / "acquisition_source.py").read_bytes()).hexdigest())
            new_bytes = 0
            for item in receipt["requests"]:
                body = (folder / item["path"]).read_bytes()
                self.assertEqual(hashlib.sha256(body).hexdigest(), item["sha256"])
                self.assertEqual(len(body), item["body_bytes"])
                self.assertEqual(item["http_status"], 200)
                self.assertTrue(item["body_complete"])
                new_bytes += len(body)
            self.assertEqual(new_bytes, receipt["new_body_bytes"])
            total += new_bytes
            self.assertEqual(receipt["aggregate_body_bytes"], total)
            self.assertEqual(receipt["remaining_body_budget_bytes"], 1_048_576 - total)
            prior_raw = raw
        self.assertEqual(total, 19_587)


if __name__ == "__main__":
    unittest.main()
