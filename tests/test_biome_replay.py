"""The replay allowance must not hide changed data, design or verification."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


spec = importlib.util.spec_from_file_location(
    'biome_replay', Path(__file__).resolve().parents[1] / 'experiments/check_biome_replay.py')
replay = importlib.util.module_from_spec(spec)
spec.loader.exec_module(replay)


class TestBioMeReplay(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.reference = Path(self.temp.name) / 'reference'
        self.actual = Path(self.temp.name) / 'actual'
        self.diagnostic = {
            'scope': 'source qualification', 'reference_measure': 'physical chamber volume',
            'freeze_commit': 'frozen', 'hours': [0., .25],
            'source_inventory': {'verified_files': 2, 'numerical_response_values_decoded': False,
                                 'instrument_hours': [.01, 72.01]},
            'dyes': {'synthetic': {'calibration': {'slope': .002, 'independent_wells': 30},
                                   'groups': [{'pore_um': .03, 'mean': 1., 'missing': None}]}}}
        self.verification = {
            'passed': True, 'freeze_commit': 'frozen', 'numerical_comparisons': 20,
            'production_analysis_imported': False,
            'relative_tolerance': replay.REL_TOL, 'absolute_tolerance': replay.ABS_TOL,
            'maximum_absolute_difference': 2e-13}
        self.write(self.reference, self.diagnostic)

    def write(self, directory, diagnostic, verification=None):
        directory.mkdir(exist_ok=True)
        path = directory / 'diagnostic.json'
        path.write_text(json.dumps(diagnostic))
        report = copy.deepcopy(self.verification if verification is None else verification)
        report['diagnostic_sha256'] = replay.digest(path)
        (directory / 'verification.json').write_text(json.dumps(report))

    def check(self):
        return replay.check_replay(self.reference, self.actual)

    def test_exact_and_roundoff_replay_are_distinguished(self):
        self.write(self.actual, self.diagnostic)
        self.assertTrue(self.check()['diagnostic_byte_equal'])
        changed = copy.deepcopy(self.diagnostic)
        changed['dyes']['synthetic']['groups'][0]['mean'] += 2e-13
        self.write(self.actual, changed)
        report = self.check()
        self.assertTrue(report['passed'])
        self.assertFalse(report['diagnostic_byte_equal'])
        self.assertFalse(report['verification_byte_equal'])
        self.assertEqual(report['diagnostic_comparison']['different_floats'], 1)

    def test_design_metadata_cannot_drift(self):
        mutations = [
            lambda d: d['hours'].__setitem__(1, .25 + 1e-14),
            lambda d: d['source_inventory']['instrument_hours'].__setitem__(0, .01 + 1e-14),
            lambda d: d['dyes']['synthetic']['groups'][0].__setitem__('pore_um', .03 + 1e-14),
            lambda d: d.__setitem__('reference_measure', 'different measure'),
            lambda d: d.__setitem__('freeze_commit', 'different freeze'),
        ]
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                changed = copy.deepcopy(self.diagnostic)
                mutation(changed)
                self.write(self.actual, changed)
                with self.assertRaises(ValueError):
                    self.check()

    def test_counts_booleans_nulls_and_types_are_exact(self):
        mutations = [
            lambda d: d['dyes']['synthetic']['calibration'].__setitem__('independent_wells', 31),
            lambda d: d['dyes']['synthetic']['calibration'].__setitem__('independent_wells', 30.),
            lambda d: d['source_inventory'].__setitem__('numerical_response_values_decoded', 0),
            lambda d: d['dyes']['synthetic']['groups'][0].__setitem__('mean', 1),
            lambda d: d['dyes']['synthetic']['groups'][0].__setitem__('missing', 0.),
        ]
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                changed = copy.deepcopy(self.diagnostic)
                mutation(changed)
                self.write(self.actual, changed)
                with self.assertRaises(ValueError):
                    self.check()

    def test_missing_fields_and_list_entries_fail(self):
        for field in ('field', 'list'):
            with self.subTest(field=field):
                changed = copy.deepcopy(self.diagnostic)
                if field == 'field':
                    del changed['dyes']['synthetic']['calibration']['slope']
                else:
                    changed['dyes']['synthetic']['groups'].pop()
                self.write(self.actual, changed)
                with self.assertRaises(ValueError):
                    self.check()

    def test_nonfinite_and_substantive_changes_fail(self):
        for value in (float('nan'), float('inf'), -float('inf'), 1.001):
            with self.subTest(value=value):
                changed = copy.deepcopy(self.diagnostic)
                changed['dyes']['synthetic']['groups'][0]['mean'] = value
                self.write(self.actual, changed)
                with self.assertRaises(ValueError):
                    self.check()

    def test_wrong_hash_fails_for_either_artifact(self):
        for directory in (self.reference, self.actual):
            with self.subTest(directory=directory):
                self.write(self.reference, self.diagnostic)
                self.write(self.actual, self.diagnostic)
                path = directory / 'verification.json'
                report = json.loads(path.read_text())
                report['diagnostic_sha256'] = 'wrong'
                path.write_text(json.dumps(report))
                with self.assertRaisesRegex(ValueError, 'different diagnostic'):
                    self.check()

    def test_verifier_cannot_change_its_policy_or_success(self):
        for key, value in (('passed', False), ('passed', 1),
                           ('relative_tolerance', 1e-8), ('absolute_tolerance', 1e-8),
                           ('numerical_comparisons', 19),
                           ('maximum_absolute_difference', -1e-13),
                           ('maximum_absolute_difference', 1.),
                           ('production_analysis_imported', True)):
            with self.subTest(key=key, value=value):
                report = copy.deepcopy(self.verification)
                report[key] = value
                self.write(self.actual, self.diagnostic, report)
                with self.assertRaises(ValueError):
                    self.check()

    def test_duplicate_keys_and_overflow_are_rejected(self):
        for value in ('{"value": 1, "value": 2}', '{"value": NaN}'):
            path = Path(self.temp.name) / 'invalid.json'
            path.write_text(value)
            with self.assertRaises(ValueError):
                replay.load_json(path)
        with self.assertRaisesRegex(ValueError, 'Nonfinite'):
            replay.compare(1., float('inf'), {}, 'diagnostic.dyes.synthetic.mean')

    def test_tolerance_uses_maximum_not_sum_of_bounds(self):
        # At 10 the relative and absolute bounds are both 1e-10. Adding
        # them would wrongly accept a 1.5e-10 discrepancy.
        with self.assertRaisesRegex(ValueError, 'Numerical replay'):
            replay.compare(10., 10. + 1.5e-10, {}, 'diagnostic.dyes.synthetic.mean')
