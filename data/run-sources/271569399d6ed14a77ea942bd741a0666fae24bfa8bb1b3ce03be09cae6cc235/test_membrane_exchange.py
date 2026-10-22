"""Qualification checks use synthetic observations only, never the real ZIP."""

from dataclasses import replace
import json
import math
import unittest
from unittest.mock import patch

import numpy as np
from scipy.stats import f as f_distribution

from orthopolity.membrane_exchange import fit_optics, profile_rate, qualify
from orthopolity.membrane_exchange_source import (
    CALIBRATION_RUN, TARGET_RUN, CALIBRATION_TIMES, TARGET_TIMES,
    ChamberDesign, ChamberObservation, MembraneSourceData, OpticalStandard,
)


CONFIG = {
    'volume_mL': 11.0, 'withdrawal_mL': 0.02, 'reference_time_hours': 6.0,
    'alpha': 0.01, 'baseline_family_size': 16, 'rate_grid_points': 4097,
}
RETENTION = 549 / 550


def synthetic_source(z_values=(0.35, 0.5, 0.65, 0.8), loss=0.0):
    # Residuals are orthogonal to both concentration and intercept columns.
    standards = tuple(OpticalStandard(c, 0.03 * c + 0.05 + 0.0002 * e)
                      for c, e in zip((0, 5, 10, 15, 20), (1, -2, 2, -2, 1)))
    observations, baselines, design = [], [], []
    for h, z in enumerate(z_values, start=1):
        for j, time in enumerate(CALIBRATION_TIMES):
            total = 1.2 * RETENTION ** j - loss * j
            difference = 0.8 * RETENTION ** j * z ** j
            for c, sign in ((1, 1), (2, -1)):
                observations.append(ChamberObservation(
                    time, f'PES_PEG25_AO_S{h}', f'H{h}_C{c}',
                    0.05 + (total + sign * difference) / 2))
        for c, absorbance in ((1, 1.05), (2, 0.25)):
            baselines.append(ChamberObservation(
                0.0, f'PES_PEG25_AO_S{h + 4}', f'H{h}_C{c}', absorbance))
            for time in TARGET_TIMES:
                design.append(ChamberDesign(time, f'PES_PEG25_AO_S{h + 4}', f'H{h}_C{c}'))
    return MembraneSourceData('synthetic', standards, standards, tuple(observations),
                              tuple(baselines), tuple(design), None)


def transform_source(source, scale, offset):
    def standard(row):
        return replace(row, absorbance=scale * row.absorbance + offset)

    def observation(row):
        return replace(row, absorbance=scale * row.absorbance + offset)

    return replace(
        source, calibration_standards=tuple(map(standard, source.calibration_standards)),
        target_standards=tuple(map(standard, source.target_standards)),
        calibration_observations=tuple(map(observation, source.calibration_observations)),
        target_baselines=tuple(map(observation, source.target_baselines)))


class MembraneExchangeQualification(unittest.TestCase):
    def test_synthetic_rates_and_stock_recovered_with_correct_configuration_units(self):
        result = qualify(synthetic_source(), CONFIG)
        self.assertTrue(result['passed'], result['stop_reasons'])
        self.assertAlmostEqual(result['retention_fraction'], RETENTION)
        optics = result['optics'][CALIBRATION_RUN]
        self.assertAlmostEqual(optics['slope'], 0.03)
        self.assertAlmostEqual(optics['intercept'], 0.05)
        self.assertAlmostEqual(optics['variance'], 14 * 0.0002 ** 2 / 3)
        self.assertLess(optics['slope_ci'][0], 0.03)
        self.assertEqual(optics['sample_extrapolation']['input_count'], 96)
        self.assertGreater(optics['sample_extrapolation']['outside_support_count'], 0)
        self.assertEqual(result['optics'][TARGET_RUN]['sample_extrapolation']['input_count'], 8)
        for rate, expected in zip(result['rates'], (0.35, 0.5, 0.65, 0.8)):
            self.assertAlmostEqual(rate['z'], expected, places=12)
            self.assertAlmostEqual(rate['lambda_per_hour'], -math.log(expected) / 6, places=12)
            self.assertAlmostEqual(rate['g_ml_per_hour'], -11 * math.log(expected) / 12, places=12)
            self.assertAlmostEqual(rate['amplitude'], 0.8)
            self.assertEqual(len(rate['confidence_intervals_z']), 1)
            lower, upper = rate['confidence_intervals_z'][0]
            self.assertLess(lower, expected)
            self.assertGreater(upper, expected)
            self.assertFalse(rate['endpoint_tests']['z0']['accepted'])
            self.assertFalse(rate['endpoint_tests']['z1']['accepted'])
            self.assertAlmostEqual(rate['threshold'], 22 * optics['variance']
                                   * f_distribution.ppf(0.99, 11, 3))
        self.assertEqual(result['total_stock']['n'], 44)
        self.assertEqual(len(result['total_stock']['identities']), 44)
        self.assertLess(result['total_stock']['statistic'], 1e-20)
        json.dumps(result, allow_nan=False)

    def test_lossy_total_fails_even_with_exact_contrast_forecasts(self):
        result = qualify(synthetic_source(loss=0.025), CONFIG)
        self.assertFalse(result['passed'])
        self.assertTrue(all(row['passed'] for row in result['rates']))
        self.assertFalse(result['total_stock']['passed'])
        self.assertLess(result['total_stock']['p_value'], 0.01)
        self.assertIn('total_stock_model_incompatible', result['stop_reasons'])

    def test_boundary_rates_stop_but_stock_gate_still_runs(self):
        result = qualify(synthetic_source(z_values=(0.0, 1.0, 0.65, 0.8)), CONFIG)
        self.assertFalse(result['passed'])
        self.assertTrue(result['total_stock']['passed'])
        instantaneous, persistence = result['rates'][:2]
        self.assertEqual(instantaneous['z'], 0.0)
        self.assertEqual(instantaneous['boundary'], 'instantaneous')
        self.assertIsNone(instantaneous['lambda_per_hour'])
        self.assertIsNone(instantaneous['g_ml_per_hour'])
        self.assertTrue(instantaneous['endpoint_tests']['z0']['accepted'])
        self.assertIsNone(instantaneous['confidence_intervals_g_ml_per_hour'][0][1])
        self.assertEqual(persistence['z'], 1.0)
        self.assertEqual(persistence['g_ml_per_hour'], 0.0)
        self.assertEqual(persistence['boundary'], 'no_exchange')
        self.assertTrue(persistence['endpoint_tests']['z1']['accepted'])
        json.dumps(result, allow_nan=False)

    def test_common_affine_measurement_transformation_cancels_from_qualification(self):
        source = synthetic_source(loss=0.002)
        first = qualify(source, CONFIG)
        second = qualify(transform_source(source, 2.7, -1.3), CONFIG)
        self.assertEqual(first['passed'], second['passed'])
        self.assertEqual(first['stop_reasons'], second['stop_reasons'])
        for a, b in zip(first['rates'], second['rates']):
            self.assertAlmostEqual(a['z'], b['z'], places=12)
            np.testing.assert_allclose(a['confidence_intervals_z'], b['confidence_intervals_z'],
                                       atol=2e-12, rtol=2e-12)
            self.assertAlmostEqual(a['rss'] * 2.7 ** 2, b['rss'], places=22)
        self.assertAlmostEqual(first['total_stock']['statistic'],
                               second['total_stock']['statistic'], places=9)

    def test_perfect_affine_standards_stop_without_variance_floor(self):
        source = synthetic_source()
        standards = tuple(OpticalStandard(c, 0.03 * c + 0.05) for c in (0, 5, 10, 15, 20))
        result = qualify(replace(source, calibration_standards=standards), CONFIG)
        optics = result['optics'][CALIBRATION_RUN]
        self.assertFalse(optics['passed'])
        self.assertLessEqual(optics['sse'], optics['numerical_zero_sse_threshold'])
        self.assertEqual(optics['variance'], optics['sse'] / 3)
        self.assertIn('unresolved_optical_variance', optics['stop_reasons'])
        self.assertEqual(result['rates'], [])
        self.assertIsNone(result['total_stock'])

    def test_nonpositive_slope_and_singular_standards_fail(self):
        source = synthetic_source()
        decreasing = tuple(replace(row, absorbance=-row.absorbance)
                           for row in source.calibration_standards)
        self.assertIn('optical_slope_not_identified_positive', fit_optics(decreasing)['stop_reasons'])
        singular = tuple(OpticalStandard(1.0, row.absorbance)
                         for row in source.calibration_standards)
        self.assertFalse(fit_optics(singular)['passed'])

    def test_negative_baseline_reading_is_retained_with_a_separate_compatibility_gate(self):
        source = synthetic_source()
        for raw, expected_pass in ((0.0499, True), (0.0, False)):
            baselines = tuple(replace(row, absorbance=raw)
                              if row.chamber == 'H1_C2' else row for row in source.target_baselines)
            result = qualify(replace(source, target_baselines=baselines), CONFIG)
            pair = result['baselines'][TARGET_RUN]['pairs'][0]
            self.assertLess(pair['recipient_minus_intercept'], 0)
            self.assertEqual(pair['recipient_raw'], raw)
            self.assertEqual(pair['passed'], expected_pass)
            self.assertTrue(result['total_stock']['passed'])

    def test_stock_covariance_includes_shared_baselines_and_intercept(self):
        result = qualify(synthetic_source(), CONFIG)
        q = np.array(result['total_stock']['covariance_q'])
        hbb = result['optics'][CALIBRATION_RUN]['inverse_xtx'][1][1]
        f1, f2 = RETENTION, RETENTION ** 2
        self.assertAlmostEqual(q[0, 0], 2 + 2 * f1 ** 2 + 4 * hbb * (1 - f1) ** 2)
        self.assertAlmostEqual(q[0, 1], 2 * f1 * f2 + 4 * hbb * (1 - f1) * (1 - f2))
        self.assertAlmostEqual(q[0, 11], 4 * hbb * (1 - f1) ** 2)
        self.assertGreater(np.linalg.eigvalsh(q).min(), 0)

    def test_narrow_interval_is_retained_between_grid_points(self):
        z = 0.537123456789
        difference = 0.8 * RETENTION ** np.arange(12) * z ** np.arange(12)
        result = profile_rate(CALIBRATION_TIMES, difference, retention_fraction=RETENTION,
                              variance=1e-20)
        self.assertTrue(result['passed'])
        lower, upper = result['confidence_intervals_z'][0]
        self.assertLess(lower, z)
        self.assertGreater(upper, z)
        self.assertLess(upper - lower, 1 / 4096)
        self.assertFalse(any(lower <= point <= upper for point in np.linspace(0, 1, 4097)))

    def test_incompatible_curve_has_empty_absolute_rss_set(self):
        difference = [1.0] + [0.5 if j % 2 else -0.5 for j in range(1, 12)]
        result = profile_rate(CALIBRATION_TIMES, difference, retention_fraction=RETENTION,
                              variance=1e-8)
        self.assertFalse(result['passed'])
        self.assertEqual(result['confidence_intervals_z'], [])
        self.assertIn('empty_rate_confidence_set', result['stop_reasons'])

    def test_qualification_never_accesses_later_target_responses(self):
        source = synthetic_source()
        with patch.object(MembraneSourceData, 'target_observations',
                          property(lambda _: (_ for _ in ()).throw(AssertionError('target accessed'))),
                          create=True):
            self.assertTrue(qualify(source, CONFIG)['passed'])

    def test_malformed_selected_inputs_fail(self):
        source = synthetic_source()
        for observations in (source.calibration_observations[:-1],
                             source.calibration_observations + source.calibration_observations[:1],
                             tuple(row for row in source.calibration_observations
                                   if not (row.sample == 'PES_PEG25_AO_S1'
                                           and row.time_hours == 66))):
            with self.assertRaises(ValueError):
                qualify(replace(source, calibration_observations=observations), CONFIG)
        with self.assertRaises(ValueError):
            qualify(source, {**CONFIG, 'withdrawal_mL': 11})


if __name__ == '__main__':
    unittest.main()
