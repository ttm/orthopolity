"""Synthetic-only tests: no real archive, standards, or response rows are read."""

import csv
from dataclasses import asdict
import hashlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import warnings
from zipfile import ZIP_DEFLATED, ZipFile

from orthopolity.membrane_exchange_source import (
    ARCHIVE_SHA256, CALIBRATION_RUN, CALIBRATION_TIMES, TARGET_RUN,
    TARGET_TIMES, SAMPLE_MEMBERS, STANDARD_MEMBERS, read_membrane_archive,
)


def fixture_members(withheld='0.3', ignored='IGNORED'):
    members = {}
    for run, times, start in ((CALIBRATION_RUN, CALIBRATION_TIMES, 1),
                              (TARGET_RUN, TARGET_TIMES, 5)):
        rows = []
        for h in range(1, 5):
            for c in (1, 2):
                for time in times:
                    absorbance = (str(0.1 + h / 100 + c / 1000 + time / 1000)
                                  if run == CALIBRATION_RUN or time == 0 else withheld)
                    rows.append([str(time), f'H{h}_C{c}', f'PES_PEG25_AO_S{start+h-1}',
                                 absorbance, ignored, ignored, ignored, ignored])
        members[SAMPLE_MEMBERS[run]] = (
            ['Time', 'Hcell', 'Sample', 'Abs_raw', 'Abs', 'C_sample', 'C_original', 'Diffusivity'], rows)
        members[STANDARD_MEMBERS[run]] = (
            ['C_uM', 'Abs_raw', 'Abs'],
            [[str(c), str(0.02 + c * 0.01), ignored] for c in (0, 5, 10, 15, 20)])
    return members


def fixture_zip(members):
    stream = io.BytesIO()
    with ZipFile(stream, 'w', compression=ZIP_DEFLATED) as archive:
        for name, (header, rows) in members.items():
            text = io.StringIO(newline='')
            writer = csv.writer(text, lineterminator='\n')
            writer.writerow(header)
            writer.writerows(rows)
            archive.writestr(name, text.getvalue())
        # Unrelated mixed response/fit files must not be read at all.
        archive.writestr('Diffusion Testing/ADT_Diffusion_Test_Records.csv', b'\xff\xfe POISON')
    return stream.getvalue()


class MembraneExchangeSource(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'synthetic.zip'

    def read(self, members=None, **kwargs):
        raw = fixture_zip(fixture_members() if members is None else members)
        self.path.write_bytes(raw)
        return read_membrane_archive(
            self.path, expected_sha256=hashlib.sha256(raw).hexdigest(), **kwargs)

    def test_stage_shapes_raw_fields_and_deterministic_order(self):
        result = self.read()
        self.assertEqual(len(result.calibration_standards), 5)
        self.assertEqual(len(result.target_standards), 5)
        self.assertEqual(len(result.calibration_observations), 96)
        self.assertEqual(len(result.target_baselines), 8)
        self.assertEqual(len(result.target_design), 64)
        self.assertIsNone(result.target_observations)
        self.assertEqual(set(result.standards_by_run), {CALIBRATION_RUN, TARGET_RUN})
        self.assertAlmostEqual(result.calibration_observations[0].absorbance, 0.111)
        self.assertEqual(result.calibration_observations[0].chamber, 'H1_C1')
        self.assertEqual(result.calibration_observations[0].sample, 'PES_PEG25_AO_S1')
        self.assertEqual(result.target_design[-1].sample, 'PES_PEG25_AO_S8')
        self.assertEqual(result.target_design[-1].time_hours, 69.6)
        # Source row order has no effect on scientific payload ordering.
        members = fixture_members()
        for _, rows in members.values():
            rows.reverse()
        reordered = self.read(members)
        self.assertEqual(self.payload(result), self.payload(reordered))

    @staticmethod
    def payload(result):
        output = asdict(result)
        del output['archive_sha256']
        return output

    def test_poisoned_withheld_and_unselected_cells_do_not_change_calibration(self):
        normal = self.read(fixture_members(withheld='17.5', ignored='1000000'))
        for poison in ('WITHHELD DO NOT DECODE', '', 'nan', 'inf', '1e999', '0,\nPOISON'):
            with self.subTest(poison=poison):
                poisoned = self.read(fixture_members(withheld=poison, ignored='BAD FLOAT'))
                self.assertEqual(self.payload(normal), self.payload(poisoned))

    def test_evaluation_flag_is_explicit_and_only_adds_positive_time_targets(self):
        calibration = self.read()
        evaluation = self.read(allow_target=True)
        self.assertEqual(len(evaluation.target_observations), 56)
        self.assertTrue(all(row.time_hours > 0 for row in evaluation.target_observations))
        self.assertTrue(all(row.absorbance == 0.3 for row in evaluation.target_observations))
        a, b = self.payload(calibration), self.payload(evaluation)
        del a['target_observations']
        del b['target_observations']
        self.assertEqual(a, b)
        with self.assertRaisesRegex(ValueError, 'Invalid Abs_raw'):
            self.read(fixture_members(withheld='SEALED'), allow_target=True)
        for flag in ('True', 'False', 1, 0, None):
            with self.subTest(flag=flag), self.assertRaisesRegex(ValueError, 'explicitly'):
                self.read(allow_target=flag)

    def test_default_hash_is_pinned_and_checked_before_zip_open(self):
        self.assertEqual(ARCHIVE_SHA256,
                         'b50871afca499ae8d74873260a35cff5338388d1c4e6d52c4c3b53eace697c07')
        self.path.write_bytes(b'Not even a ZIP')
        with patch('orthopolity.membrane_exchange_source.ZipFile') as zip_reader:
            with self.assertRaisesRegex(ValueError, 'SHA-256 mismatch'):
                read_membrane_archive(self.path)
            zip_reader.assert_not_called()
        for digest in (None, '', 'unverified', 'f' * 63, 'z' * 64):
            with self.subTest(digest=digest), self.assertRaisesRegex(ValueError, '64-digit'):
                read_membrane_archive(self.path, expected_sha256=digest)

    def test_duplicate_missing_and_inconsistent_design_rows_fail(self):
        for kind in ('duplicate', 'missing', 'wrong_time', 'wrong_sample', 'wrong_chamber'):
            with self.subTest(kind=kind):
                members = fixture_members(withheld='SEALED')
                rows = members[SAMPLE_MEMBERS[TARGET_RUN]][1]
                if kind == 'duplicate':
                    rows.append(rows[-1].copy())
                elif kind == 'missing':
                    rows.pop()
                elif kind == 'wrong_time':
                    rows[-1][0] = '69.7'
                elif kind == 'wrong_sample':
                    rows[-1][2] = 'PES_PEG25_AO_S5'
                else:
                    rows[-1][1] = 'H1_C2'
                with self.assertRaises(ValueError):
                    self.read(members)

    def test_malformed_authorized_values_fail_without_echoing_values(self):
        for run, field, value in ((CALIBRATION_RUN, 3, 'PRIVATE_BAD_MEASUREMENT'),
                                  (TARGET_RUN, 3, 'PRIVATE_BAD_BASELINE'),
                                  (TARGET_RUN, 0, 'nan'),
                                  (CALIBRATION_RUN, 3, 'inf')):
            with self.subTest(run=run, field=field, value=value):
                members = fixture_members()
                members[SAMPLE_MEMBERS[run]][1][0][field] = value
                with self.assertRaises(ValueError) as caught:
                    self.read(members)
                self.assertNotIn(value, str(caught.exception))

    def test_negative_raw_absorbance_is_preserved(self):
        members = fixture_members()
        members[SAMPLE_MEMBERS[TARGET_RUN]][1][0][3] = '-0.005'
        members[STANDARD_MEMBERS[TARGET_RUN]][1][0][1] = '-0.001'
        result = self.read(members)
        self.assertEqual(result.target_baselines[0].absorbance, -0.005)
        self.assertEqual(result.target_standards[0].absorbance, -0.001)

    def test_missing_duplicate_header_or_structurally_invalid_csv_fails(self):
        for kind in ('missing_header', 'duplicate_header', 'short_row', 'long_row'):
            with self.subTest(kind=kind):
                members = fixture_members()
                header, rows = members[SAMPLE_MEMBERS[TARGET_RUN]]
                if kind == 'missing_header':
                    header[3] = 'Abs_raw_missing'
                elif kind == 'duplicate_header':
                    header[4] = 'Abs_raw'
                elif kind == 'short_row':
                    rows[-1].pop()
                else:
                    rows[-1].append('extra')
                with self.assertRaises(ValueError):
                    self.read(members)

    def test_standard_validation(self):
        for kind in ('missing', 'duplicate', 'negative', 'bad_concentration', 'bad_absorbance'):
            with self.subTest(kind=kind):
                members = fixture_members()
                rows = members[STANDARD_MEMBERS[TARGET_RUN]][1]
                if kind == 'missing':
                    rows.pop()
                elif kind == 'duplicate':
                    rows[-1][0] = rows[0][0]
                elif kind == 'negative':
                    rows[0][0] = '-1'
                elif kind == 'bad_concentration':
                    rows[0][0] = 'nan'
                else:
                    rows[0][1] = 'BAD'
                with self.assertRaises(ValueError):
                    self.read(members)

    def test_missing_or_duplicate_required_zip_member_fails(self):
        members = fixture_members()
        del members[STANDARD_MEMBERS[TARGET_RUN]]
        with self.assertRaisesRegex(ValueError, 'Missing or duplicated ZIP member'):
            self.read(members)
        raw = fixture_zip(fixture_members())
        stream = io.BytesIO(raw)
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)
            with ZipFile(stream, 'a') as archive:
                archive.writestr(STANDARD_MEMBERS[TARGET_RUN], 'C_uM,Abs_raw\n')
        raw = stream.getvalue()
        self.path.write_bytes(raw)
        with self.assertRaisesRegex(ValueError, 'Missing or duplicated ZIP member'):
            read_membrane_archive(self.path, expected_sha256=hashlib.sha256(raw).hexdigest())


if __name__ == '__main__':
    unittest.main()
