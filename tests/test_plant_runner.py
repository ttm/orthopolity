import importlib.util
import math
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('plant_runner', ROOT / 'experiments/run_plant_biomass_profile.py')
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


class PlantSourceGateTests(unittest.TestCase):
    def test_all_newline_conventions_preserve_separate_records(self):
        for ending in ['\r', '\n', '\r\n']:
            body = ending.join(['name,mass', 'a,0.01', 'b,1.2', 'c,NA', 'd,0', 'e,inf', 'f,broken', '']).encode()
            masses, rows = RUNNER.decode_mass_csv(body, 'mass', 'synthetic')
            self.assertEqual(masses.tolist(), [.01, 1.2])
            self.assertEqual(len(rows), 6)
            self.assertEqual([row['status'] for row in rows],
                             ['included_positive', 'included_positive', 'missing', 'nonpositive', 'nonfinite', 'unparseable'])
            self.assertEqual([row['csv_record'] for row in rows], list(range(2, 8)))

    def test_evaluation_gate_rejects_before_any_file_access(self):
        with patch.object(Path, 'read_bytes', side_effect=AssertionError('attempted evaluation read')):
            with self.assertRaisesRegex(RuntimeError, 'unavailable'):
                RUNNER.read_plots({'source': {'files': []}}, 'evaluation')

    def test_development_reader_cannot_request_evaluation_paths(self):
        files = [dict(plot=f'dev{i}', role='development', mass_field='mass') for i in range(5)]
        files += [dict(plot=f'eval{i}', role='evaluation', mass_field='mass') for i in range(5)]
        def synthetic_read(path):
            if path.name.startswith('eval'):
                raise AssertionError('held-out path read')
            return b'mass\r0.01\r1\r'
        with patch.object(Path, 'read_bytes', synthetic_read):
            arrays, membership = RUNNER.read_plots({'source': {'files': files}}, 'development')
        self.assertEqual(set(arrays), {f'dev{i}' for i in range(5)})
        self.assertEqual(len(membership), 10)

    def test_membership_keeps_frozen_tail_and_inclusive_upper(self):
        _, rows = RUNNER.decode_mass_csv(b'mass\r0.001\r0.01\r100\r101\r', 'mass', 'synthetic')
        result = RUNNER.classify_membership(rows, {'lower': .01, 'upper': 100})
        self.assertEqual([row['status'] for row in result], ['below_domain', 'in_domain', 'in_domain', 'above_domain'])
        self.assertEqual([row['status'] for row in rows], ['included_positive']*4)

    def test_zero_probability_retains_infinite_loss_in_json_safe_form(self):
        forecasts = dict(domain=dict(lower=.01, upper=1., edges=[.01, .1, 1.]),
                         models={'log_neutral': dict(count_shares=[1., 0.], count_log_shares=[0., -math.inf],
                                                     stock_shares=[.5, .5])})
        result = RUNNER.evaluation_computation(forecasts, {'synthetic': [.01, 1.]})
        score = result['equal_plot_mean_scores']['log_neutral']
        self.assertIsNone(score['count_logloss'])
        self.assertTrue(score['count_logloss_infinite'])
        RUNNER.encoded(result)


if __name__ == '__main__':
    unittest.main()
