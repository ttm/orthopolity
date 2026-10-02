"""Read worksheet cells with a row gate applied before outcome decoding.

Metadata columns are decoded for every row. Value columns are decoded only for
rows the caller's gate accepts; the gate sees decoded metadata alone. Cells of
rejected rows are skipped without converting their stored text, so a held-out
outcome cannot enter a computation before an explicit later stage. Cached
formula results are read as stored; no formula is evaluated.
"""
from __future__ import annotations

import datetime as dt
import math
import posixpath
import re
import zipfile
import xml.etree.ElementTree as ET

MAIN = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
OFFICE_RELATIONSHIP = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
PACKAGE_RELATIONSHIP = '{http://schemas.openxmlformats.org/package/2006/relationships}'
MISSING_TEXT = frozenset({'', 'na', 'n/a', 'nan'})
_REFERENCE = re.compile(r'([A-Z]+)([0-9]+)$')
_INTEGER = re.compile(r'[+-]?[0-9]+$')


def _string_item(element):
    """Concatenate plain or rich-text runs, excluding phonetic annotations."""
    parts = []
    for child in element:
        if child.tag == MAIN + 't':
            parts.append(child.text or '')
        elif child.tag == MAIN + 'r':
            parts.extend(run.text or '' for run in child.findall(MAIN + 't'))
    return ''.join(parts)


def _workbook_parts(archive):
    workbook = ET.fromstring(archive.read('xl/workbook.xml'))
    properties = workbook.find(MAIN + 'workbookPr')
    date1904 = properties is not None and properties.get('date1904') in {'1', 'true'}
    sheet = workbook.find(f'{MAIN}sheets/{MAIN}sheet')
    if sheet is None:
        raise ValueError('Workbook has no worksheet')
    relationship = sheet.get(OFFICE_RELATIONSHIP + 'id')
    relationships = ET.fromstring(archive.read('xl/_rels/workbook.xml.rels'))
    for item in relationships.findall(PACKAGE_RELATIONSHIP + 'Relationship'):
        if item.get('Id') == relationship:
            target = item.get('Target', '')
            path = (target.lstrip('/') if target.startswith('/')
                    else posixpath.normpath(posixpath.join('xl', target)))
            return sheet.get('name'), path, date1904
    raise ValueError('First worksheet relationship is missing')


def _decode(cell, strings):
    kind = cell.get('t', 'n')
    if kind == 'inlineStr':
        inline = cell.find(MAIN + 'is')
        return None if inline is None else _string_item(inline)
    stored = cell.find(MAIN + 'v')
    if stored is None or stored.text is None:
        return None
    text = stored.text
    if kind == 'n':
        return int(text) if _INTEGER.match(text) else float(text)
    if kind == 's':
        return strings[int(text)]
    if kind == 'str':
        return text
    if kind == 'b':
        return text == '1'
    if kind == 'e':
        raise ValueError(f'Spreadsheet error value in cell {cell.get("r")}: {text}')
    raise ValueError(f'Unsupported cell type {kind!r} in cell {cell.get("r")}')


def numeric(value, context=''):
    """Finite float, or None for absent/empty/textual-missing values."""
    if value is None:
        return None
    if isinstance(value, bool):
        raise ValueError(f'Boolean in numeric field {context}')
    if isinstance(value, (int, float)):
        result = float(value)
        if not math.isfinite(result):
            raise ValueError(f'Nonfinite numeric value {context}')
        return result
    if isinstance(value, str) and value.strip().lower() in MISSING_TEXT:
        return None
    raise ValueError(f'Non-numeric text in numeric field {context}: {value!r}')


def serial_date(value, date1904=False):
    """ISO date for a spreadsheet day serial (valid after 1 March 1900)."""
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 61:
        raise ValueError(f'Unsupported date serial: {value!r}')
    epoch = dt.datetime(1904, 1, 1) if date1904 else dt.datetime(1899, 12, 30)
    return (epoch + dt.timedelta(days=float(value))).isoformat()


def read_gated_rows(path, metadata_headers, value_headers, gate):
    """Decode metadata for every data row and values for gate-accepted rows.

    The first worksheet row supplies headers; requested headers must be unique.
    Rows whose requested metadata cells are all absent are skipped as blank.
    Each returned row records its source row, metadata, decoded values (None
    when gated) and whether its values were decoded.
    """
    metadata_headers, value_headers = list(metadata_headers), list(value_headers)
    requested = metadata_headers + value_headers
    if len(set(requested)) != len(requested):
        raise ValueError('Requested headers must be distinct')
    with zipfile.ZipFile(path) as archive:
        strings = []
        if 'xl/sharedStrings.xml' in archive.namelist():
            table = ET.fromstring(archive.read('xl/sharedStrings.xml'))
            strings = [_string_item(item) for item in table.findall(MAIN + 'si')]
        sheet, sheet_path, date1904 = _workbook_parts(archive)
        columns, rows, gated = None, [], 0
        with archive.open(sheet_path) as stream:
            for _, element in ET.iterparse(stream, events=('end',)):
                if element.tag != MAIN + 'row':
                    continue
                number = int(element.get('r'))
                cells = {}
                for cell in element.findall(MAIN + 'c'):
                    match = _REFERENCE.match(cell.get('r', ''))
                    if not match or int(match.group(2)) != number or match.group(1) in cells:
                        raise ValueError(f'Malformed cell reference in row {number}')
                    cells[match.group(1)] = cell
                if columns is None:
                    headers = {column: _decode(cell, strings) for column, cell in cells.items()}
                    columns = {}
                    for column, header in headers.items():
                        if header in requested:
                            if header in columns:
                                raise ValueError(f'Duplicate requested header: {header!r}')
                            columns[header] = column
                    missing = [header for header in requested if header not in columns]
                    if missing:
                        raise ValueError(f'Missing requested headers: {missing}')
                    element.clear()
                    continue

                def decoded(header):
                    cell = cells.get(columns[header])
                    return None if cell is None else _decode(cell, strings)

                metadata = {header: decoded(header) for header in metadata_headers}
                if all(value is None for value in metadata.values()):
                    element.clear()
                    continue
                accepted = bool(gate(metadata))
                values = {header: decoded(header) for header in value_headers} if accepted else None
                gated += not accepted
                rows.append(dict(source_row=number, metadata=metadata, values=values, decoded=accepted))
                element.clear()
    if columns is None:
        raise ValueError('Worksheet has no header row')
    return dict(sheet=sheet, date1904=date1904, rows=rows, gated_rows=gated,
                columns={header: columns[header] for header in requested})
