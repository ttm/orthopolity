"""Synthetic checks only: no experimental temperature values are read."""
import importlib.util
import itertools
import json
from pathlib import Path
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('hotbox', ROOT/'experiments/run_hotbox_transfer.py')
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)
CFG = json.loads((ROOT/h.CONFIG).read_text())
vspec = importlib.util.spec_from_file_location('hotbox_verify', ROOT/'experiments/verify_hotbox_transfer.py')
v = importlib.util.module_from_spec(vspec)
vspec.loader.exec_module(v)


def synthetic_summary(betas=(.8, .6, .3)):
    rows = []
    for case in range(1, 8):
        c, g = (20., 5.) if case == 6 else (20., 20.) if case == 7 else (25., -5.)
        for p in CFG['positions']:
            for s in ('cdefg' if case >= 6 else 'cg'):
                value = c if s == 'c' else g if s == 'g' else g+betas['def'.index(s)]*(c-g)
                rows.append(dict(case=case, position=p, sensor=s, mean_c=value,
                                 min_c=value, max_c=value, drift_c=0.))
    return rows


class TestHotboxTransfer(unittest.TestCase):
    def test_independent_forecast_verifier(self):
        pred = dict(config=CFG, input_summary=synthetic_summary(), design_commit='a'*40,
                    numeric_temperature_cells=50680, target_interior_temperatures_decoded=False)
        pred['predictions'] = h.predict(pred['input_summary'], CFG)
        report = v.verify(pred)
        self.assertLess(report['maximum_absolute_difference'], 1e-12)
        pred['predictions'][0]['transfer_prediction_c'] += .01
        with self.assertRaises(ValueError):
            v.verify(pred)

    def test_verifier_accepts_roundoff_at_constant_series_extrema(self):
        summary = synthetic_summary()
        summary[0]['mean_c'] += 4e-15
        pred = dict(config=CFG, input_summary=summary, design_commit='a'*40,
                    numeric_temperature_cells=50680, target_interior_temperatures_decoded=False)
        pred['predictions'] = h.predict(summary, CFG)
        v.verify(pred)
        summary[0]['mean_c'] += .001
        with self.assertRaises(ValueError):
            v.verify(pred)

    def test_firewall_does_not_parse_unselected_numeric_or_poison_cells(self):
        cfg = dict(CFG, expected_rows=3, expected_columns=4)
        raw = b'Time\t1_c\t1_d\t1_g\n0\t20\tDO_NOT_PARSE\t0\n60\t21\t1e99999\t1\n120\t22\tNaN\t2\n'
        table = h.selected_table(raw, ['1_c', '1_g'], cfg)
        self.assertEqual(set(table), {'Time', '1_c', '1_g'})
        np.testing.assert_array_equal(table['1_c'], [20, 21, 22])

    def test_bad_clock_and_selected_nonfinite_fail(self):
        cfg = dict(CFG, expected_rows=2, expected_columns=2)
        for raw in (b'Time\t1_c\n0\t20\n1\t21\n', b'Time\t1_c\n0\tNaN\n60\t21\n'):
            with self.assertRaises(ValueError):
                h.selected_table(raw, ['1_c'], cfg)

    def test_feasibility_requires_joint_monotone_temperature_vector(self):
        self.assertTrue(h.descending_feasible([20, 15, 15.2, 8, 0], .15))
        self.assertFalse(h.descending_feasible([20, 15, 15.4, 8, 0], .15))
        self.assertIsNotNone(h.beta_interval(20, 0, 15.4, .15))
        self.assertIsNone(h.beta_interval(20, 0, 21, .15))

    def test_interval_contains_interior_error_combinations(self):
        beta = h.beta_interval(20, 0, 12, .15)
        interval = h.observation_interval(30, -5, beta, .15)
        for ec, eg, em in itertools.product(np.linspace(-.15, .15, 5), repeat=3):
            b = (12+em-eg)/(20+ec-eg)
            self.assertLessEqual(beta[0], b+1e-12)
            self.assertGreaterEqual(beta[1], b-1e-12)
            for a, z, v in itertools.product([-.15, .15], repeat=3):
                y = b*(30+a)+(1-b)*(-5+z)+v
                self.assertLessEqual(interval[0], y+1e-12)
                self.assertGreaterEqual(interval[1], y-1e-12)

    def test_shared_additive_offset_cancels_beta_and_residual(self):
        original = h.beta_interval(20, 0, 12, .15)
        np.testing.assert_allclose(original, h.beta_interval(37, 17, 29, .15))

    def test_synthetic_fixed_resistance_predicts_new_forcing_exactly(self):
        summary = synthetic_summary()
        predictions = h.predict(summary, CFG)
        self.assertEqual(len(predictions), 210)
        for row in predictions:
            beta = {'d': .8, 'e': .6, 'f': .3}[row['sensor']]
            self.assertAlmostEqual(row['transfer_prediction_c'], -5+30*beta)
            self.assertTrue(row['input_qualified'])
            self.assertLess(row['transfer_observation_interval_c'][0], row['transfer_prediction_c'])

    def test_additive_and_resistance_rivals_agree_only_at_calibration(self):
        rows = h.predict(synthetic_summary(), CFG)
        self.assertTrue(any(abs(r['additive_prediction_c']-r['transfer_prediction_c']) > 1
                            for r in rows))
        summary = synthetic_summary()
        for r in summary:
            if r['case'] <= 5:
                value = 20. if r['sensor']=='c' else 5.
                r.update(mean_c=value, min_c=value, max_c=value)
        for r in h.predict(summary, CFG):
            self.assertAlmostEqual(r['additive_prediction_c'], r['transfer_prediction_c'])

    def test_range_and_drift_failures_remain_visible(self):
        row = dict(min_c=-9.9, max_c=20, drift_c=0)
        self.assertFalse(h.qualified(row, CFG))
        row.update(min_c=0, drift_c=.301)
        self.assertFalse(h.qualified(row, CFG))

    def test_same_means_do_not_make_time_samples_independent(self):
        table = {6: {'Time': np.arange(181)*60, '1_c': np.ones(181)*20}}
        summary = h.summarize(table, CFG)
        self.assertEqual(summary[0]['drift_c'], 0)
        a = h.observation_interval(20, 0, [.6, .6], .15)
        self.assertAlmostEqual(a[1]-a[0], .6)

    def test_evaluation_preserves_departure_and_qualification_failure(self):
        pred = dict(config=CFG, input_summary=synthetic_summary())
        pred['predictions'] = h.predict(pred['input_summary'], CFG)
        targets = []
        for r in pred['predictions']:
            value = r['transfer_prediction_c']
            targets.append(dict(case=r['case'], position=r['position'], sensor=r['sensor'],
                                mean_c=value, min_c=value, max_c=value, drift_c=0.))
        result = h.evaluate(pred, targets)
        self.assertEqual(result['verdict'], 'not_excluded_by_marginal_bounds')
        targets[0]['mean_c'] += 3
        targets[0]['max_c'] += 3
        result = h.evaluate(pred, targets)
        self.assertEqual(result['verdict'], 'conditional_transfer_departure')
        targets[0]['drift_c'] = 1
        result = h.evaluate(pred, targets)
        self.assertEqual(result['verdict'], 'qualification_incomplete')
        self.assertEqual(result['groups']['all']['target_means'], 210)
        self.assertEqual(result['groups']['all']['transfer_outside_all'], 1)


if __name__ == '__main__':
    unittest.main()
