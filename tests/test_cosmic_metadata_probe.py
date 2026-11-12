"""Offline checks for bounded metadata acquisition and retained access evidence."""
import contextlib
import hashlib
import http.client
import importlib.util
import io
import json
from pathlib import Path
import ssl
import tempfile
import unittest
from unittest.mock import Mock, patch
import urllib.error


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "cosmic_metadata_probe", ROOT / "experiments/probe_cosmic_metadata.py")
PROBE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PROBE)


class Response(io.BytesIO):
    def __init__(self, body=b"{}", status=200, length=None):
        super().__init__(body)
        self.code = status
        self.headers = {"Content-Type": "application/json"}
        if length is not None:
            self.headers["Content-Length"] = length
        self.read_sizes = []

    def read(self, size=-1):
        self.read_sizes.append(size)
        return super().read(size)


class CosmicMetadataProbeTests(unittest.TestCase):
    def run_probe(self, response=None, error=None, cap=64):
        opener = Mock()
        opener.open.return_value = response
        opener.open.side_effect = error
        with tempfile.TemporaryDirectory() as temp:
            destination = Path(temp) / "probe"
            with patch.object(PROBE.urllib.request, "build_opener", return_value=opener) as factory:
                with patch.object(PROBE, "BYTE_CAP", cap), contextlib.redirect_stdout(io.StringIO()):
                    PROBE.probe(destination)
            receipt = json.loads((destination / "receipt.json").read_text())
            body_path = destination / "response-body.bin"
            body = body_path.read_bytes() if body_path.exists() else None
            self.assertEqual(receipt["script_sha256"], hashlib.sha256(
                (destination / "probe_source.py").read_bytes()).hexdigest())
        opener.open.assert_called_once()
        self.assertIn(PROBE.NoRedirect, factory.call_args.args)
        request = opener.open.call_args.args[0]
        self.assertEqual(request.full_url, PROBE.URL)
        self.assertEqual(request.get_header("Accept-encoding"), "identity")
        self.assertFalse(any(k.lower() in {"api-key", "authorization", "cookie"}
                             for k in request.headers))
        self.assertTrue(receipt["tls_certificate_verification"])
        self.assertTrue(receipt["tls_hostname_verification"])
        self.assertFalse(receipt["complete_D1_manifest"])
        self.assertEqual(receipt["redirects_followed"], 0)
        self.assertEqual(receipt["retries"], 0)
        if body is not None:
            self.assertEqual(len(body), receipt["response_bytes_retained"])
            self.assertEqual(hashlib.sha256(body).hexdigest(), receipt["body_sha256"])
        return receipt, body

    def test_complete_metadata_does_not_claim_complete_manifest(self):
        receipt, body = self.run_probe(Response(b'{"name":"TNG50-4-Dark"}'))
        self.assertTrue(receipt["body_complete"])
        self.assertEqual(receipt["http_status"], 200)
        self.assertEqual(receipt["outcome"], "http_response")
        self.assertEqual(json.loads(body)["name"], "TNG50-4-Dark")

    def test_cap_stops_without_extra_byte_read(self):
        for payload in (b"12345678", b"123456789abcdef"):
            with self.subTest(payload=payload):
                response = Response(payload)
                receipt, body = self.run_probe(response, cap=8)
                self.assertEqual(body, b"12345678")
                self.assertFalse(receipt["body_complete"])
                self.assertEqual(response.read_sizes, [8])

    def test_incorrect_content_length_is_not_complete(self):
        for advertised in ("5", "1", "not-a-number"):
            with self.subTest(advertised=advertised):
                receipt, body = self.run_probe(Response(b"{}", length=advertised))
                self.assertFalse(receipt["body_complete"])
                self.assertEqual(body, b"{}")

    def test_http_access_errors_are_responses_not_transport_failures(self):
        for code in (401, 403):
            with self.subTest(code=code):
                error = urllib.error.HTTPError(PROBE.URL, code, "Denied",
                                               {"Content-Type": "application/json"},
                                               io.BytesIO(b'{"detail":"denied"}'))
                receipt, body = self.run_probe(error=error)
                self.assertEqual(receipt["http_status"], code)
                self.assertEqual(receipt["outcome"], "http_response")
                self.assertTrue(receipt["body_complete"])
                self.assertEqual(json.loads(body)["detail"], "denied")

    def test_tls_failure_does_not_invent_http_status_or_expose_error_text(self):
        error = urllib.error.URLError(ssl.SSLCertVerificationError("private-proxy-detail"))
        receipt, body = self.run_probe(error=error)
        self.assertIsNone(body)
        self.assertIsNone(receipt["http_status"])
        self.assertEqual(receipt["response_bytes_retained"], 0)
        self.assertEqual(receipt["reason_type"], "SSLCertVerificationError")
        self.assertEqual(receipt["outcome"], "transport_failure")
        self.assertNotIn("private-proxy-detail", json.dumps(receipt))

    def test_partial_body_survives_read_failure(self):
        response = Response()
        response.read = Mock(side_effect=[b"abc", OSError("private-detail")])
        receipt, body = self.run_probe(response)
        self.assertEqual(body, b"abc")
        self.assertFalse(receipt["body_complete"])
        self.assertEqual(receipt["http_status"], 200)
        self.assertEqual(receipt["outcome"], "transport_failure")
        self.assertNotIn("private-detail", json.dumps(receipt))

    def test_incomplete_read_exception_payload_is_retained(self):
        response = Response()
        response.read = Mock(side_effect=[b"abc", http.client.IncompleteRead(b"de", 8)])
        receipt, body = self.run_probe(response)
        self.assertEqual(body, b"abcde")
        self.assertFalse(receipt["body_complete"])
        self.assertEqual(receipt["error_type"], "IncompleteRead")

    def test_redirect_is_not_followed(self):
        handler = PROBE.NoRedirect()
        for url in (PROBE.URL + "snapshots/", "https://example.org/", "http://www.tng-project.org/"):
            self.assertIsNone(handler.redirect_request(None, None, 302, "", {}, url))
        error = urllib.error.HTTPError(PROBE.URL, 302, "Redirect",
                                       {"Location": "https://example.org/"}, io.BytesIO(b"move"))
        receipt, body = self.run_probe(error=error)
        self.assertEqual(receipt["http_status"], 302)
        self.assertEqual(body, b"move")

    def test_previous_receipt_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            destination = Path(temp) / "probe"
            destination.mkdir()
            sentinel = destination / "receipt.json"
            sentinel.write_text("original")
            with patch.object(PROBE.urllib.request, "build_opener") as factory:
                with self.assertRaises(FileExistsError):
                    PROBE.probe(destination)
                factory.assert_not_called()
            self.assertEqual(sentinel.read_text(), "original")

    def test_retained_access_receipts_and_aggregate_budget(self):
        base = ROOT / "data/cosmic-source-qualification/2026-11-12"
        receipts = []
        for name in ("tng50-4-dark-anonymous", "tng50-4-dark-system-trust"):
            folder = base / name
            receipt = json.loads((folder / "receipt.json").read_text())
            receipts.append(receipt)
            self.assertEqual(receipt["requested_url"], PROBE.URL)
            self.assertEqual(receipt["script_sha256"], hashlib.sha256(
                (folder / "probe_source.py").read_bytes()).hexdigest())
            self.assertFalse(receipt["credential_used"])
            if "body_path" in receipt:
                body = (folder / receipt["body_path"]).read_bytes()
                self.assertEqual(len(body), receipt["response_bytes_retained"])
                self.assertEqual(hashlib.sha256(body).hexdigest(), receipt["body_sha256"])
        self.assertIsNone(receipts[0]["http_status"])
        self.assertEqual(receipts[0]["reason_type"], "SSLCertVerificationError")
        self.assertEqual(receipts[1]["http_status"], 403)
        self.assertTrue(receipts[1]["body_complete"])
        total = sum(r["response_bytes_retained"] for r in receipts)
        self.assertEqual(total, 55)
        self.assertLessEqual(total, PROBE.BYTE_CAP)
        manifest = json.loads((base / "acquisition.json").read_text())
        self.assertEqual(manifest["aggregate_body_bytes"], total)
        self.assertEqual(manifest["request_count"], len(receipts))
        self.assertEqual(manifest["aggregate_body_cap_bytes"], PROBE.BYTE_CAP)
        self.assertEqual(manifest["remaining_body_budget_bytes"], PROBE.BYTE_CAP - total)
        self.assertFalse(manifest["complete_D1_manifest"])
        for attempt in manifest["attempts"]:
            for item in attempt["files"]:
                raw = (base / item["path"]).read_bytes()
                self.assertEqual(len(raw), item["bytes"])
                self.assertEqual(hashlib.sha256(raw).hexdigest(), item["sha256"])


if __name__ == "__main__":
    unittest.main()
