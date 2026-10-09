"""Retain fixed candidate metadata and inspect explicitly selected workbook headers.

Default verification is offline. The archive stage downloads the separately
identified Ghedini source ZIP, checks its provider MD5 and lists its directory.
The schema stage reads sheet names and only the first-row text headers of the
species metabolism sheet. No numerical data rows are interpreted or emitted.
The separate all-headers stage extends the same first-row read to all sheets.
Original-archive and original-schema acquire and inspect the directly linked
original community experiment with the same restrictions.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from xml.parsers import expat

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data/measure-candidates/2026-10-04"
SOURCES = {
    "ghedini-2020.json": "https://api.figshare.com/v2/articles/11755200",
    "fant-ghedini-2024.json": "https://api.figshare.com/v2/articles/25234837",
    "briddon-2025.json": "https://api.figshare.com/v2/articles/28014971",
    "padfield-repository.json": "https://api.github.com/repos/padpadpadpad/Padfield_2018_ELE_metab_size_struc",
    "hengill-datacite.json": "https://api.datacite.org/dois/10.5526/ERDR-00000148",
    "seaflow-datacite.json": "https://api.datacite.org/dois/10.5281/zenodo.10896099",
    "ghedini-original-experiment.json": "https://api.figshare.com/v2/articles/11704749",
}
ARCHIVE_URL = "https://ndownloader.figshare.com/files/22484462"
ARCHIVE_MD5 = "af61d509937b76cb986d45683eea3617"
ARCHIVE_BYTES = 1879319
ORIGINAL_URL = "https://ndownloader.figshare.com/files/21286929"
ORIGINAL_MD5 = "6dc5a38875eb1eb9d44d08d7b020b95d"
ORIGINAL_BYTES = 466041
NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def encode(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def digest(body):
    return hashlib.sha256(body).hexdigest()


def retain(name, url, *, archive=False, expected_bytes=ARCHIVE_BYTES, expected_md5=ARCHIVE_MD5):
    path = BASE / name
    receipt_path = BASE / (name + ".receipt.json")
    if receipt_path.exists():
        receipt = json.loads(receipt_path.read_text())
        body = path.read_bytes()
        if receipt["requested_url"] != url or digest(body) != receipt["sha256"] or len(body) != receipt["bytes"]:
            raise ValueError("Retained source/provenance changed")
        return body
    started = now()
    with tempfile.NamedTemporaryFile(dir=BASE) as temporary:
        command = ["/usr/bin/curl", "-q", "--fail", "--silent", "--show-error",
                   "--proto", "=https", "--max-time", "45", "--max-filesize", "4000000",
                   "--output", temporary.name, "--write-out", "%{http_code}\n%{ssl_verify_result}\n"]
        # Metadata URLs must not redirect to a data-file endpoint. The explicitly
        # selected ZIP may redirect to storage; its exact provider digest is pinned.
        if archive:
            command.extend(["--location", "--max-redirs", "3", "--proto-redir", "=https"])
        result = subprocess.run([*command, url], capture_output=True, text=True, check=True)
        status, tls_result = result.stdout.splitlines()
        if status != "200" or tls_result != "0":
            raise ValueError("Unexpected status or TLS verification result")
        body = Path(temporary.name).read_bytes()
    if not body or len(body) > 4_000_000:
        raise ValueError("Empty or oversized source")
    if archive:
        if len(body) != expected_bytes or hashlib.md5(body).hexdigest() != expected_md5:
            raise ValueError("Archive does not match provider metadata")
    elif not isinstance(json.loads(body), dict):
        raise ValueError("Expected metadata JSON object")
    if path.exists() and path.read_bytes() != body:
        raise ValueError("Refusing to replace different retained bytes")
    path.write_bytes(body)
    receipt_path.write_bytes(encode(dict(name=name, requested_url=url, started_utc=started,
                                         completed_utc=now(), bytes=len(body), sha256=digest(body),
                                         http_status=int(status), tls_verification=True,
                                         transport="system curl, TLS verification enabled, user config disabled",
                                         scope="opaque ZIP; members undecoded" if archive else "metadata only")))
    return body


def verify():
    for name, url in SOURCES.items():
        receipt = json.loads((BASE / (name + ".receipt.json")).read_text())
        body = (BASE / name).read_bytes()
        if receipt["requested_url"] != url or digest(body) != receipt["sha256"] or len(body) != receipt["bytes"]:
            raise ValueError("Metadata integrity failure")
        json.loads(body)
    path = BASE / "ghedini-source.zip"
    if path.exists():
        body = path.read_bytes()
        receipt = json.loads((BASE / (path.name + ".receipt.json")).read_text())
        if (len(body) != ARCHIVE_BYTES or hashlib.md5(body).hexdigest() != ARCHIVE_MD5
                or digest(body) != receipt["sha256"] or receipt["requested_url"] != ARCHIVE_URL):
            raise ValueError("Archive integrity failure")
        if json.loads((BASE / "ghedini-inventory.json").read_text()) != inventory():
            raise ValueError("Archive inventory changed")
        for name, expected in (("ghedini-workbook-inventory.json", workbook_inventory),
                               ("ghedini-calibration-headers.json", calibration_headers),
                               ("ghedini-all-headers.json", all_headers)):
            report = BASE / name
            if report.exists() and json.loads(report.read_text()) != expected():
                raise ValueError("Retained schema report changed")
    original_path = BASE / "ghedini-original-experiment.xlsx"
    if original_path.exists():
        body = original_path.read_bytes()
        receipt = json.loads((BASE / (original_path.name + ".receipt.json")).read_text())
        if (len(body) != ORIGINAL_BYTES or hashlib.md5(body).hexdigest() != ORIGINAL_MD5
                or digest(body) != receipt["sha256"] or receipt["requested_url"] != ORIGINAL_URL):
            raise ValueError("Original experiment integrity failure")
        report = BASE / "ghedini-original-experiment-headers.json"
        if report.exists() and json.loads(report.read_text()) != original_headers():
            raise ValueError("Original experiment headers changed")
    return dict(metadata_files=len(SOURCES), archive_retained=path.exists(),
                original_experiment_retained=original_path.exists(),
                this_driver_interprets_numerical_data_rows=False)


def inventory():
    with zipfile.ZipFile(BASE / "ghedini-source.zip") as source:
        return [dict(name=row.filename, bytes=row.file_size, compressed_bytes=row.compress_size,
                     crc32=f"{row.CRC:08x}", directory=row.is_dir()) for row in source.infolist()]


def workbook_inventory():
    result = []
    with zipfile.ZipFile(BASE / "ghedini-source.zip") as source:
        for name in source.namelist():
            with zipfile.ZipFile(io.BytesIO(source.read(name))) as book:
                root = ET.fromstring(book.read("xl/workbook.xml"))
                sheets = [dict(name=s.attrib["name"], sheetId=s.attrib["sheetId"])
                          for s in root.findall(f"{{{NS}}}sheets/{{{NS}}}sheet")]
                result.append(dict(workbook=name, sheets=sheets))
    return result


class HeaderDone(Exception):
    """Stop XML parsing at the end of the first row."""


def first_row_headers(book, sheet_path):
    """Read only first-row text, without parsing later rows or formula text.

    Shared strings are selectively retained by index. XML syntax is parsed,
    but unrelated strings and numeric cell contents are never accumulated.
    """
    cells = []
    current = None
    field = None

    def start(name, attrs):
        nonlocal current, field
        if name == "row" and attrs.get("r") != "1":
            raise ValueError("Expected row 1")
        if name == "c":
            current = dict(cell=attrs["r"], kind=attrs.get("t", "n"), text="", formula=False)
        elif current is not None and name == "f":
            current["formula"] = True
        field = name

    def characters(value):
        if current is not None and not current["formula"]:
            if (current["kind"] == "s" and field == "v") or (current["kind"] == "inlineStr" and field == "t"):
                current["text"] += value

    def end(name):
        nonlocal current, field
        if name == "c":
            cells.append(current)
            current = None
        if name == "row":
            raise HeaderDone
        field = None

    parser = expat.ParserCreate()
    parser.StartElementHandler, parser.CharacterDataHandler, parser.EndElementHandler = start, characters, end
    with book.open(sheet_path) as source:
        try:
            parser.ParseFile(source)
        except HeaderDone:
            pass
    selected = {int(c["text"]) for c in cells if c["kind"] == "s" and not c["formula"]}
    strings = {}
    if selected:
        with book.open("xl/sharedStrings.xml") as source:
            index = 0
            for _, element in ET.iterparse(source, events=("end",)):
                if element.tag == f"{{{NS}}}si":
                    if index in selected:
                        strings[index] = "".join(element.itertext())
                    element.clear()
                    index += 1
                    if index > max(selected):
                        break
        if set(strings) != selected:
            raise ValueError("Missing shared-string index")
    result = []
    for c in cells:
        text = None
        if not c["formula"]:
            if c["kind"] == "s":
                text = strings[int(c["text"])]
            elif c["kind"] == "inlineStr":
                text = c["text"]
        result.append(dict(cell=c["cell"], header=text,
                           omitted_nontext_or_formula=text is None))
    return result


def calibration_headers():
    workbook = "1. Data summary.xlsx"
    sheet = "species metabolism"
    with zipfile.ZipFile(BASE / "ghedini-source.zip") as source:
        with zipfile.ZipFile(io.BytesIO(source.read(workbook))) as book:
            return dict(workbook=workbook, sheet=sheet, row=1,
                        cells=named_sheet_headers(book, sheet))


def named_sheet_headers(book, sheet):
    root = ET.fromstring(book.read("xl/workbook.xml"))
    matches = [s for s in root.findall(f"{{{NS}}}sheets/{{{NS}}}sheet") if s.attrib["name"] == sheet]
    if len(matches) != 1:
        raise ValueError("Expected exactly one named sheet")
    rid = matches[0].attrib[f"{{{REL}}}id"]
    relations = ET.fromstring(book.read("xl/_rels/workbook.xml.rels"))
    target = [r.attrib["Target"] for r in relations if r.attrib["Id"] == rid]
    if len(target) != 1 or not target[0].startswith("worksheets/") or ".." in target[0]:
        raise ValueError("Unexpected worksheet relationship")
    return first_row_headers(book, "xl/" + target[0])


def all_headers():
    result = []
    with zipfile.ZipFile(BASE / "ghedini-source.zip") as source:
        for entry in workbook_inventory():
            with zipfile.ZipFile(io.BytesIO(source.read(entry["workbook"]))) as book:
                for sheet in entry["sheets"]:
                    result.append(dict(workbook=entry["workbook"], sheet=sheet["name"], row=1,
                                       cells=named_sheet_headers(book, sheet["name"])))
    return result


def original_headers():
    with zipfile.ZipFile(BASE / "ghedini-original-experiment.xlsx") as book:
        root = ET.fromstring(book.read("xl/workbook.xml"))
        sheets = root.findall(f"{{{NS}}}sheets/{{{NS}}}sheet")
        return [dict(sheet=s.attrib["name"], sheetId=s.attrib["sheetId"], row=1,
                     cells=named_sheet_headers(book, s.attrib["name"])) for s in sheets]


def retain_report(name, value):
    path = BASE / name
    content = encode(value)
    if path.exists() and json.loads(path.read_text()) != value:
        raise ValueError("Refusing changed report")
    if not path.exists():
        path.write_bytes(content)


def main(stage):
    if stage == "verify":
        return verify()
    if stage == "schema":
        verify()
        retain_report("ghedini-workbook-inventory.json", workbook_inventory())
        retain_report("ghedini-calibration-headers.json", calibration_headers())
        return verify()
    if stage == "all-headers":
        verify()
        retain_report("ghedini-all-headers.json", all_headers())
        return verify()
    if stage == "original-schema":
        verify()
        retain_report("ghedini-original-experiment-headers.json", original_headers())
        return verify()
    BASE.mkdir(parents=True, exist_ok=True)
    for name, url in SOURCES.items():
        retain(name, url)
    if stage == "archive":
        metadata = json.loads((BASE / "ghedini-2020.json").read_text())
        files = [row for row in metadata["files"] if row["id"] == 22484462]
        if len(files) != 1 or files[0]["size"] != ARCHIVE_BYTES or files[0]["supplied_md5"] != ARCHIVE_MD5:
            raise ValueError("Provider metadata differs from pinned archive")
        retain("ghedini-source.zip", ARCHIVE_URL, archive=True)
        content = encode(inventory())
        path = BASE / "ghedini-inventory.json"
        if path.exists() and path.read_bytes() != content:
            raise ValueError("Refusing changed inventory")
        path.write_bytes(content)
    if stage == "original-archive":
        metadata = json.loads((BASE / "ghedini-original-experiment.json").read_text())
        files = [row for row in metadata["files"] if row["id"] == 21286929]
        if len(files) != 1 or files[0]["size"] != ORIGINAL_BYTES or files[0]["supplied_md5"] != ORIGINAL_MD5:
            raise ValueError("Original provider metadata differs from pinned archive")
        retain("ghedini-original-experiment.xlsx", ORIGINAL_URL, archive=True,
               expected_bytes=ORIGINAL_BYTES, expected_md5=ORIGINAL_MD5)
    return verify()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=["metadata", "archive", "schema", "all-headers", "original-archive", "original-schema", "verify"], default="verify")
    print(json.dumps(main(parser.parse_args().stage), indent=2))
