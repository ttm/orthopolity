"""R workspace reading checks use synthetic XDR streams, never study data."""
import gzip
import struct
import tempfile
import unittest
from pathlib import Path

import numpy as np

from orthopolity.rdata_reader import data_frame, load_rdata

NA_INTEGER = -2**31
NA_REAL = struct.unpack('>d', bytes.fromhex('7ff00000000007a2'))[0]


class Writer:
    """Minimal R serialization (version 2) writer for test fixtures."""
    def __init__(self):
        self.out = bytearray()
        self.symbols = {}
        self.references = 0

    def integer(self, value):
        self.out += struct.pack('>i', value)

    def flags(self, kind, attributes=False, tag=False, levels=0):
        self.integer(kind | (attributes << 9) | (tag << 10) | (levels << 12))

    def char(self, text):
        if text is None:
            self.flags(9)
            self.integer(-1)
            return
        raw = text.encode()
        self.flags(9, levels=1 << 3)
        self.integer(len(raw))
        self.out += raw

    def symbol(self, name):
        if name in self.symbols:
            self.integer((self.symbols[name] << 8) | 255)
            return
        self.flags(1)
        self.char(name)
        self.references += 1
        self.symbols[name] = self.references

    def attributes(self, pairs):
        for tag, write in pairs:
            self.flags(2, tag=True)
            self.symbol(tag)
            write()
        self.integer(254)

    def strings(self, values, attributes=None):
        self.flags(16, attributes=bool(attributes))
        self.integer(len(values))
        for value in values:
            self.char(value)
        if attributes:
            self.attributes(attributes)

    def integers(self, values, attributes=None):
        self.flags(13, attributes=bool(attributes))
        self.integer(len(values))
        for value in values:
            self.integer(value)
        if attributes:
            self.attributes(attributes)

    def reals(self, values):
        self.flags(14)
        self.integer(len(values))
        for value in values:
            self.out += struct.pack('>d', value)

    def frame(self, columns):
        self.flags(19, attributes=True)
        self.integer(len(columns))
        for _, write in columns:
            write()
        self.attributes([('names', lambda: self.strings([name for name, _ in columns])),
                         ('class', lambda: self.strings(['data.frame'])),
                         ('row.names', lambda: self.integers([NA_INTEGER, -3]))])


def workspace(objects, directory, version=2):
    writer = Writer()
    writer.out += b'RDX2\nX\n'
    writer.integer(version)
    writer.integer(0x030502)
    writer.integer(0x020300)
    for name, write in objects:
        writer.flags(2, tag=True)
        writer.symbol(name)
        write(writer)
    writer.integer(254)
    path = Path(directory)/'fixture.RData'
    path.write_bytes(gzip.compress(bytes(writer.out)))
    return path


def example(writer):
    writer.frame([
        ('Treat', lambda: writer.integers([1, 2, NA_INTEGER], [
            ('levels', lambda: writer.strings(['Small', 'Large'])),
            ('class', lambda: writer.strings(['factor']))])),
        ('Rep', lambda: writer.integers([1, 2, 3])),
        ('Value', lambda: writer.reals([1.5, NA_REAL, 3.])),
        ('Label', lambda: writer.strings(['a', None, 'c']))])


class RDataReaderChecks(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.directory.cleanup()

    def test_data_frame_columns_factors_and_missing_values(self):
        objects = load_rdata(workspace([('Frame', example)], self.directory.name))
        columns = data_frame(objects['Frame'])
        self.assertEqual(list(columns), ['Treat', 'Rep', 'Value', 'Label'])
        self.assertEqual(columns['Treat'].factor_labels(), ['Small', 'Large', None])
        np.testing.assert_array_equal(columns['Rep'].decode(), [1, 2, 3])
        value = columns['Value'].decode()
        self.assertEqual(value[0], 1.5)
        self.assertTrue(np.isnan(value[1]))
        self.assertEqual(columns['Label'].decode(), ['a', None, 'c'])
        self.assertFalse(columns['Rep'].is_factor())

    def test_row_decoding_converts_only_requested_elements(self):
        columns = data_frame(load_rdata(workspace([('Frame', example)], self.directory.name))['Frame'])
        np.testing.assert_array_equal(columns['Value'].decode_rows([2, 0]), [3., 1.5])
        self.assertTrue(np.isnan(columns['Value'].decode_rows([1])[0]))
        np.testing.assert_array_equal(columns['Rep'].decode_rows([1]), [2.])
        with self.assertRaises(IndexError):
            columns['Value'].decode_rows([3])
        with self.assertRaises(ValueError):
            columns['Label'].decode_rows([0])

    def test_symbol_references_and_multiple_objects(self):
        objects = load_rdata(workspace([('First', example), ('Second', example)], self.directory.name))
        self.assertEqual(list(objects), ['First', 'Second'])
        self.assertEqual(data_frame(objects['Second'])['Treat'].factor_labels(), ['Small', 'Large', None])

    def test_malformed_streams_are_rejected(self):
        path = workspace([('Frame', example)], self.directory.name)
        truncated = Path(self.directory.name)/'truncated.RData'
        truncated.write_bytes(gzip.compress(gzip.decompress(path.read_bytes())[:-6]))
        with self.assertRaises(ValueError):
            load_rdata(truncated)
        (Path(self.directory.name)/'plain.RData').write_bytes(b'not R data')
        with self.assertRaises(ValueError):
            load_rdata(Path(self.directory.name)/'plain.RData')
        compact = workspace([('Bad', lambda writer: writer.flags(238))], self.directory.name)
        with self.assertRaises(ValueError):
            load_rdata(compact)

    def test_non_frames_are_not_treated_as_tables(self):
        objects = load_rdata(workspace([('Vector', lambda writer: writer.integers([1]))], self.directory.name))
        with self.assertRaises(ValueError):
            data_frame(objects['Vector'])


if __name__ == '__main__':
    unittest.main()
