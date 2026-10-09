import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("law_metadata", ROOT / "experiments/fetch_law_observation_metadata.py")
META = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(META)


class MetadataOutcomeGate(unittest.TestCase):
    def test_redirect_is_rejected_before_a_followup_request_exists(self):
        handler = META.ExactMetadataRedirect("malaspina-panmd.xml")
        url = META.SOURCES["malaspina-panmd.xml"][0]
        with self.assertRaisesRegex(ValueError, "allowlist"):
            handler.redirect_request(None, None, 302, "Found", {}, url.replace("metadata_panmd", "textfile"))

    def test_redirect_to_numerical_data_fails_even_with_xml_body(self):
        url = META.SOURCES["malaspina-panmd.xml"][0]
        with self.assertRaisesRegex(ValueError, "allowlist"):
            META.validate_response("malaspina-panmd.xml", url.replace("metadata_panmd", "textfile"),
                                   b"<pangaea_metadata/>")

    def test_csv_body_cannot_be_retained_as_methods_pdf(self):
        name = "bloofinz-description.pdf"
        with self.assertRaisesRegex(ValueError, "PDF"):
            META.validate_response(name, META.SOURCES[name][0], b"cycle,nitrogen\r1,5.2\r")

    def test_complete_receipt_rejects_changed_bytes_without_network(self):
        name = "bloofinz-description.pdf"
        with tempfile.TemporaryDirectory() as tmp, patch.object(META, "BASE", Path(tmp)):
            body = b"%PDF-synthetic metadata"
            (Path(tmp)/name).write_bytes(body + b"changed")
            receipt = dict(schema_version=1, complete=True, files=[dict(name=name,
                           path=(Path(tmp)/name).relative_to(Path(tmp)).as_posix(),
                           requested_url=META.SOURCES[name][0], final_url=META.SOURCES[name][0],
                           bytes=len(body), sha256=META.sha(body))])
            with patch.object(META, "ROOT", Path(tmp)), patch.object(META, "SOURCES", {name:META.SOURCES[name]}):
                with self.assertRaisesRegex(ValueError, "bytes changed"):
                    META.verify(receipt)


if __name__ == "__main__":
    unittest.main()
