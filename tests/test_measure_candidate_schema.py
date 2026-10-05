"""Exercise the boundary between workbook metadata and withheld outcomes."""
import hashlib
import importlib.util
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "measure_candidates", ROOT / "experiments/fetch_measure_candidates.py"
)
META = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(META)
CAL_SPEC = importlib.util.spec_from_file_location(
    "inspect_measure_calibration", ROOT / "experiments/inspect_measure_calibration.py"
)
CAL = importlib.util.module_from_spec(CAL_SPEC)
with patch.dict(sys.modules, {"fetch_measure_candidates": META}):
    CAL_SPEC.loader.exec_module(CAL)


def zip_bytes(parts):
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        for name, body in parts.items():
            archive.writestr(name, body)
    return output.getvalue()


def workbook_parts(first_row, later_rows=""):
    return {
        "xl/workbook.xml": f'''<workbook xmlns="{META.NS}" xmlns:r="{META.REL}">
          <sheets>
            <sheet name="community outcomes" sheetId="1" r:id="rId1"/>
            <sheet name="species metabolism" sheetId="2" r:id="rId2"/>
          </sheets>
        </workbook>''',
        "xl/_rels/workbook.xml.rels": '''<Relationships
          xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
          <Relationship Id="rId1" Target="worksheets/community.xml"/>
          <Relationship Id="rId2" Target="worksheets/calibration.xml"/>
        </Relationships>''',
        "xl/worksheets/calibration.xml": (
            f'<worksheet xmlns="{META.NS}"><sheetData><row r="1">'
            + first_row + "</row>" + later_rows + "</sheetData></worksheet>"
        ),
        # An opaque member, deliberately not even well-formed XML.
        "xl/worksheets/community.xml": "WITHHELD COMMUNITY OUTCOMES <unclosed",
    }


class CandidateSchemaBoundary(unittest.TestCase):
    def test_inventory_and_calibration_schema_never_open_community_parts(self):
        parts = workbook_parts('<c r="A1" t="inlineStr"><is><t>species</t></is></c>')
        archive = zip_bytes({"1. Data summary.xlsx": zip_bytes(parts)})
        opened = []
        original_open = zipfile.ZipFile.open

        def guarded_open(book, name, *args, **kwargs):
            member = name.filename if isinstance(name, zipfile.ZipInfo) else name
            opened.append(member)
            if member.startswith("xl/worksheets/") and member != "xl/worksheets/calibration.xml":
                raise AssertionError("Withheld community worksheet was opened")
            return original_open(book, name, *args, **kwargs)

        with tempfile.TemporaryDirectory() as tmp, patch.object(META, "BASE", Path(tmp)):
            (Path(tmp) / "ghedini-source.zip").write_bytes(archive)
            with patch.object(zipfile.ZipFile, "open", guarded_open):
                inventory = META.workbook_inventory()
                headers = META.calibration_headers()
        self.assertEqual(inventory[0]["sheets"][0]["name"], "community outcomes")
        self.assertEqual(headers["cells"][0]["header"], "species")
        self.assertIn("xl/worksheets/calibration.xml", opened)
        self.assertNotIn("xl/worksheets/community.xml", opened)

    def test_malformed_later_row_is_not_parsed(self):
        parts = workbook_parts(
            '<c r="A1" t="inlineStr"><is><t>Light</t></is></c>',
            '<row r="2"><c r="A2"><v>987654321 & INVALID XML',
        )
        with zipfile.ZipFile(io.BytesIO(zip_bytes(parts))) as book:
            headers = META.first_row_headers(book, "xl/worksheets/calibration.xml")
        self.assertEqual(headers, [dict(cell="A1", header="Light", omitted_nontext_or_formula=False)])

    def test_shared_and_inline_headers_decode_but_numeric_and_formulas_are_omitted(self):
        parts = workbook_parts('''
          <c r="A1" t="s"><v>1</v></c>
          <c r="B1" t="inlineStr"><is><r><t>cell_</t></r><r><t>volume_µm³</t></r></is></c>
          <c r="C1"><v>123456789</v></c>
          <c r="D1" t="s"><f>SUM(A2:A999)</f><v>0</v></c>
          <c r="E1"><f>1+1</f><v>2</v></c>
        ''')
        parts["xl/sharedStrings.xml"] = f'''<sst xmlns="{META.NS}">
          <si><t>CACHED FORMULA RESULT MUST NOT APPEAR</t></si>
          <si><r><t>metab_</t></r><r><t>umolO2_min_cell</t></r></si>
        </sst>'''
        with zipfile.ZipFile(io.BytesIO(zip_bytes(parts))) as book:
            headers = META.first_row_headers(book, "xl/worksheets/calibration.xml")
        self.assertEqual([row["header"] for row in headers],
                         ["metab_umolO2_min_cell", "cell_volume_µm³", None, None, None])
        self.assertEqual([row["omitted_nontext_or_formula"] for row in headers],
                         [False, False, True, True, True])

    def test_changed_retained_metadata_fails_offline_verification(self):
        source = {"metadata.json": "https://example.test/metadata"}
        body = b'{"files": []}\n'
        receipt = dict(requested_url=source["metadata.json"], bytes=len(body),
                       sha256=hashlib.sha256(body).hexdigest())
        with tempfile.TemporaryDirectory() as tmp, patch.object(META, "BASE", Path(tmp)), \
                patch.object(META, "SOURCES", source):
            path = Path(tmp) / "metadata.json"
            path.write_bytes(body)
            (Path(tmp) / "metadata.json.receipt.json").write_bytes(META.encode(receipt))
            self.assertEqual(META.verify()["metadata_files"], 1)
            # Still valid JSON and the same length: only the digest detects it.
            path.write_bytes(body.replace(b"files", b"other"))
            with patch.object(META.subprocess, "run", side_effect=AssertionError("Network attempted")):
                with self.assertRaisesRegex(ValueError, "integrity"):
                    META.verify()


class CalibrationInspectionBoundary(unittest.TestCase):
    def test_only_selected_sheet_and_columns_are_interpreted(self):
        parts = workbook_parts("", '''<row r="2">
          <c r="A2"><v>0</v></c><c r="B2" t="s"><v>0</v></c>
          <c r="C2"><v>100</v></c><c r="D2"><v>0.7</v></c>
          <c r="E2"><v>10</v></c><c r="F2"><v>2</v></c>
          <c r="G2"><v>10000</v></c><c r="H2"><v>-2</v></c>
          <c r="I2"><v>-0.0002</v></c>
          <c r="J2"><f>'community outcomes'!A2</f><v>not-a-number</v></c>
          <c r="AA2"><v>NaN</v></c>
        </row>''')
        parts["xl/sharedStrings.xml"] = f'<sst xmlns="{META.NS}"><si><t>Species A</t></si></sst>'
        opened = []
        original_open = zipfile.ZipFile.open

        def guarded_open(book, name, *args, **kwargs):
            member = name.filename if isinstance(name, zipfile.ZipInfo) else name
            opened.append(member)
            if member.startswith("xl/worksheets/") and member != "xl/worksheets/calibration.xml":
                raise AssertionError("Withheld community worksheet was opened")
            return original_open(book, name, *args, **kwargs)

        body = zip_bytes(parts)
        with zipfile.ZipFile(io.BytesIO(body)) as book, patch.object(zipfile.ZipFile, "open", guarded_open):
            rows = CAL.selected_rows(book)
        self.assertEqual(rows, [dict(source_row=2, light=0.0, species="Species A",
                                    dilution_percent=100.0, optical_density=0.7, volume_um3=10.0,
                                    cells_per_ul=2.0, cells_in_5ml=10000.0, oxygen_umol_per_min=-2.0,
                                    oxygen_umol_per_min_per_cell=-0.0002)])
        self.assertNotIn("xl/worksheets/community.xml", opened)

    def test_selected_formula_stops_before_using_cached_value(self):
        parts = workbook_parts("", '''<row r="2">
          <c r="I2"><f>'community outcomes'!A2</f><v>not-a-number</v></c>
        </row>''')
        with zipfile.ZipFile(io.BytesIO(zip_bytes(parts))) as book:
            with self.assertRaisesRegex(ValueError, "Formula in calibration I2"):
                CAL.selected_rows(book)

    def test_qualification_preserves_missing_zero_and_signed_rates(self):
        rows = []
        for number, (bulk, cells, rate) in enumerate(
                [(-2, 4, -0.5), (3, 4, 1), (0, 4, 0), (0, 4, None), (4, 0, 2)], start=2):
            row = dict.fromkeys(CAL.FIELDS)
            row.update(source_row=number, species="Species A", light=0, dilution_percent=100,
                       volume_um3=10, oxygen_umol_per_min=bulk, cells_in_5ml=cells,
                       oxygen_umol_per_min_per_cell=rate)
            rows.append(row)
        report = CAL.qualify(rows)
        self.assertEqual(report["per_cell_rate_signs"], dict(negative=1, positive=2, zero=1, missing=1))
        self.assertEqual(report["checked_bulk_to_cell_pairs"], 3)
        self.assertEqual(report["max_relative_rate_identity_error"], 0.25)
        self.assertEqual(report["missing_by_field"]["oxygen_umol_per_min_per_cell"], 1)
        self.assertEqual([row["oxygen_umol_per_min_per_cell"] for row in rows], [-0.5, 1, 0, None, 2])
        self.assertEqual(rows[-1]["cells_in_5ml"], 0)


if __name__ == "__main__":
    unittest.main()
