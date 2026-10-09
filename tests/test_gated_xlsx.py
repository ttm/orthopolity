"""Gated worksheet reading uses synthetic workbooks, never study outcomes."""
import tempfile
import unittest
from pathlib import Path

import openpyxl

from orthopolity.gated_xlsx import numeric, read_gated_rows, serial_date


def write_workbook(directory, rows):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    for row in rows:
        sheet.append(row)
    path = Path(directory)/'synthetic.xlsx'
    workbook.save(path)
    return path


class GatedWorkbookChecks(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = write_workbook(self.directory.name, [
            ['Unit', 'Time', 'Outcome µm³/mL', 'Note'],
            ['dev', -1, 2.5, 'kept'],
            ['held', 0, 'NA', None],
            ['held', 3, '#N/A', 'secret'],
            [None, None, None, None],
            ['dev', 4, 7, 'x'],
        ])

    def tearDown(self):
        self.directory.cleanup()

    def test_rejected_rows_are_never_decoded(self):
        gate = lambda metadata: metadata['Unit'] == 'dev' or metadata['Time'] <= 0
        result = read_gated_rows(self.path, ['Unit', 'Time'], ['Outcome µm³/mL'], gate)
        self.assertEqual(result['gated_rows'], 1)
        self.assertEqual([row['source_row'] for row in result['rows']], [2, 3, 4, 6])
        held = result['rows'][2]
        self.assertEqual(held['metadata'], {'Unit': 'held', 'Time': 3})
        self.assertIsNone(held['values'])
        self.assertFalse(held['decoded'])
        with self.assertRaises(ValueError):
            read_gated_rows(self.path, ['Unit', 'Time'], ['Outcome µm³/mL'], lambda metadata: True)

    def test_numbers_text_missing_values_and_integer_types_are_preserved(self):
        result = read_gated_rows(self.path, ['Unit', 'Time'], ['Outcome µm³/mL', 'Note'],
                                 lambda metadata: metadata['Time'] != 3)
        first, second, last = result['rows'][0], result['rows'][1], result['rows'][3]
        self.assertEqual(first['values'], {'Outcome µm³/mL': 2.5, 'Note': 'kept'})
        self.assertIsInstance(first['metadata']['Time'], int)
        self.assertEqual(second['values'], {'Outcome µm³/mL': 'NA', 'Note': None})
        self.assertIsNone(numeric(second['values']['Outcome µm³/mL']))
        self.assertIsInstance(last['values']['Outcome µm³/mL'], int)
        self.assertEqual(result['columns'], {'Unit': 'A', 'Time': 'B', 'Outcome µm³/mL': 'C', 'Note': 'D'})

    def test_missing_or_duplicate_requested_headers_are_rejected(self):
        with self.assertRaises(ValueError):
            read_gated_rows(self.path, ['Unit', 'Absent'], [], lambda metadata: True)
        with self.assertRaises(ValueError):
            read_gated_rows(self.path, ['Unit'], ['Unit'], lambda metadata: True)
        duplicate = write_workbook(self.directory.name, [['A', 'A'], [1, 2]])
        with self.assertRaises(ValueError):
            read_gated_rows(duplicate, ['A'], [], lambda metadata: True)

    def test_numeric_conversion_is_strict(self):
        self.assertEqual(numeric(3), 3.)
        for missing in [None, '', ' NA ', 'n/a', 'NaN']:
            self.assertIsNone(numeric(missing))
        for invalid in ['abc', True, float('inf'), float('nan')]:
            with self.assertRaises(ValueError):
                numeric(invalid)

    def test_spreadsheet_serial_dates(self):
        self.assertEqual(serial_date(45000), '2023-03-15T00:00:00')
        self.assertEqual(serial_date(45000.5), '2023-03-15T12:00:00')
        self.assertEqual(serial_date(61, date1904=True), '1904-03-02T00:00:00')
        for invalid in [60, True, 'x']:
            with self.assertRaises(ValueError):
                serial_date(invalid)


if __name__ == '__main__':
    unittest.main()
