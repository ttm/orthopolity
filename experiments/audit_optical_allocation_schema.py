"""Check optical source hashes and workbook schemas without decoding numeric cells.

Original workbooks are not redistributed. Supply their download directory.
This is an availability audit, not an allocation analysis.
"""
import argparse
import hashlib
import json
from pathlib import Path
import posixpath
import xml.etree.ElementTree as ET
import zipfile


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'data/physics-candidates/2026-10-28/allocation/optical-schema.json'
NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
RID = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'


def inspect_workbook(path):
    raw = path.read_bytes()
    sheets = []
    with zipfile.ZipFile(path) as archive:
        shared = []
        if 'xl/sharedStrings.xml' in archive.namelist():
            shared = [''.join(e.itertext()) for e in
                      ET.fromstring(archive.read('xl/sharedStrings.xml'))]
        relations = {
            e.attrib['Id']: e.attrib['Target'] for e in ET.fromstring(
                archive.read('xl/_rels/workbook.xml.rels'))
        }
        workbook = ET.fromstring(archive.read('xl/workbook.xml'))
        for sheet in workbook.findall('s:sheets/s:sheet', NS):
            target = relations[sheet.attrib[RID]]
            member = target.lstrip('/') if target.startswith('/') else posixpath.normpath(
                posixpath.join('xl', target))
            tree = ET.fromstring(archive.read(member))
            rows = tree.findall('s:sheetData/s:row', NS)
            labels = []
            for row in rows:
                # Row indices and shared-string indices are metadata. Numerical
                # cell payloads are never converted to numbers or reported.
                if int(row.attrib['r']) > 3:
                    continue
                for cell in row.findall('s:c', NS):
                    kind = cell.attrib.get('t')
                    if kind == 's':
                        label = shared[int(cell.find('s:v', NS).text)]
                    elif kind == 'inlineStr':
                        label = ''.join(cell.find('s:is', NS).itertext())
                    else:
                        continue
                    labels.append({'cell': cell.attrib['r'], 'label': label})
            sheets.append({
                'name': sheet.attrib['name'],
                'dimension': tree.find('s:dimension', NS).attrib['ref'],
                'stored_rows': len(rows),
                'first_three_row_string_labels': labels,
            })
    return {'file': path.name, 'bytes': len(raw),
            'sha256': hashlib.sha256(raw).hexdigest(), 'sheets': sheets}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, required=True)
    args = parser.parse_args()
    expected = json.loads(MANIFEST.read_text())
    for record in expected:
        if Path(record['file']).name != record['file']:
            raise ValueError('Expected source basename')
        actual = inspect_workbook(args.source_dir / record['file'])
        if actual != record:
            raise ValueError(f"Hash or schema mismatch: {record['file']}")
    print(json.dumps({
        'verified_source_workbooks': len(expected),
        'verified_sheet_schemas': sum(len(r['sheets']) for r in expected),
        'numerical_experimental_values_converted_or_reported': False,
    }, indent=2))


if __name__ == '__main__':
    main()
