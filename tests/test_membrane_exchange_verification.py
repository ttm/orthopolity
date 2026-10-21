"""Independent mathematical checks using invented data only; no source ZIP access."""

import csv
import hashlib
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZIP_DEFLATED, ZipFile

import numpy as np

from orthopolity.membrane_exchange import fit_optics, profile_rate, total_stock_test
from orthopolity.membrane_exchange_source import OpticalStandard


SPEC = importlib.util.spec_from_file_location(
    'verify_membrane_for_synthetic_tests',
    Path(__file__).resolve().parents[1] / 'experiments/verify_membrane_exchange.py')
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)

TIMES = np.arange(12, dtype=float) * 6
RETENTION = 549 / 550


def optical_fixture():
    concentration = np.arange(5, dtype=float) * 5
    # The invented residual vector is orthogonal to both OLS columns.
    absorbance = .02 + .04 * concentration + .002 * np.array([1, -1, 0, -1, 1])
    return list(zip(concentration, absorbance))


def stock_fixture(loss=False):
    pairs = []
    for k in range(4):
        retained = RETENTION ** np.arange(12)
        total = (.8 + .04 * k) * retained
        difference = (.7 + .02 * k) * retained * np.exp(-(.02 + .004 * k) * TIMES)
        if loss:
            # A common loss preserves shares, but violates known stock recovery.
            total = total * np.exp(-.03 * TIMES)
            difference = difference * np.exp(-.03 * TIMES)
        pairs.append({
            'sample': f'invented_{k}', 'times_hours': TIMES.tolist(),
            'donor_chamber': f'H{k + 1}_C1', 'recipient_chamber': f'H{k + 1}_C2',
            'donor': (.02 + (total + difference) / 2
                      + .0001 * np.sin(np.arange(12) + k)).tolist(),
            'recipient': (.02 + (total - difference) / 2
                          + .0001 * np.cos(np.arange(12) + k)).tolist(),
        })
    return pairs


def synthetic_archive(withheld):
    """Create only invented source members, including poisoned unused fields."""
    data = io.BytesIO()
    with ZipFile(data, 'w', compression=ZIP_DEFLATED) as archive:
        for index, run in enumerate(VERIFY.RUNS):
            standards = io.StringIO(newline='')
            writer = csv.writer(standards, lineterminator='\n')
            writer.writerow(['C_uM', 'Abs_raw', 'Abs'])
            for concentration, absorbance in optical_fixture():
                writer.writerow([concentration, absorbance, 'UNUSED OPTICAL FIELD'])
            archive.writestr(VERIFY.STANDARDS[run], standards.getvalue())
            samples = io.StringIO(newline='')
            writer = csv.writer(samples, lineterminator='\n')
            writer.writerow(['Time', 'Hcell', 'Sample', 'Abs_raw', 'C_original'])
            for pair in range(1, 5):
                for chamber in (1, 2):
                    for time in VERIFY.TIMES[run]:
                        value = (.6 + pair / 100 + chamber / 1000 + time / 10000
                                 if index == 0 or time == 0 else withheld)
                        writer.writerow([time, f'H{pair}_C{chamber}',
                                         f'PES_PEG25_AO_S{4 * index + pair}',
                                         value, 'UNUSED DERIVED CONCENTRATION'])
            archive.writestr(VERIFY.SAMPLES[run], samples.getvalue())
        archive.writestr('unselected-response-table.csv', b'\xff\xfe UNREAD')
    return data.getvalue()


class MembraneExchangeVerification(unittest.TestCase):
    def test_independent_reader_leaves_poisoned_later_target_responses_undecoded(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'invented-membrane.zip'

            def read(withheld):
                raw = synthetic_archive(withheld)
                path.write_bytes(raw)
                result = VERIFY.read_qualification_source(
                    path, hashlib.sha256(raw).hexdigest())
                # Different withheld strings necessarily change archive bytes.
                result.pop('archive_sha256')
                return result

            expected = read('17.5')
            for poison in ('SEALED DO NOT DECODE', '', 'nan', 'inf', '1e999', '0,\nPOISON'):
                with self.subTest(poison=poison):
                    self.assertEqual(read(poison), expected)
            calibration, target = [expected['runs'][run]['pairs'] for run in VERIFY.RUNS]
            self.assertEqual(sum(len(p[field]) for p in calibration
                                 for field in ('donor', 'acceptor')), 96)
            self.assertEqual(sum(len(p[field]) for p in target
                                 for field in ('donor', 'acceptor')), 8)
            self.assertTrue(all(p['times_hours'] == (0,) for p in target))

    def test_independent_optical_failure_skips_all_dependent_checks(self):
        exact_standards = [(5 * j, .125 + .25 * (5 * j)) for j in range(5)]
        for failed_run in VERIFY.RUNS:
            with self.subTest(failed_run=failed_run):
                # Intentionally omit pair data: no dependent input should be
                # inspected after either run's unresolved optical variance.
                source = {'runs': {
                    run: {'standards': exact_standards if run == failed_run else optical_fixture()}
                    for run in VERIFY.RUNS}}
                with patch.object(VERIFY, 'baseline_check') as baseline, \
                        patch.object(VERIFY, 'profile_fit') as rate, \
                        patch.object(VERIFY, 'total_stock_check') as stock:
                    result = VERIFY.independent_qualification(source)
                baseline.assert_not_called()
                rate.assert_not_called()
                stock.assert_not_called()
                self.assertFalse(result['passed'])
                self.assertFalse(result['optics'][failed_run]['passed'])
                self.assertEqual(result['baselines'], {})
                self.assertEqual(result['rates'], [])
                self.assertIsNone(result['total_stock'])
                self.assertIs(result['later_target_responses_decoded'], False)

    def compare_rate(self, differences, variance):
        primary = profile_rate(TIMES, differences, retention_fraction=RETENTION,
                               variance=variance)
        independent = VERIFY.profile_fit(TIMES, differences, RETENTION, variance)
        self.assertAlmostEqual(primary['z'], independent['z'], delta=2e-8)
        self.assertAlmostEqual(primary['rss'], independent['rss'], delta=2e-13)
        self.assertAlmostEqual(primary['amplitude'], independent['amplitude'], delta=2e-8)
        np.testing.assert_allclose(primary['fitted_differences'], independent['fitted_curve'],
                                   atol=2e-8, rtol=0)
        np.testing.assert_allclose(primary['confidence_intervals_z'],
                                   independent['acceptance_intervals_z'], atol=2e-11, rtol=0)
        self.assertEqual(primary['endpoint_tests']['z0']['accepted'],
                         independent['accepts_z_zero'])
        self.assertEqual(primary['endpoint_tests']['z1']['accepted'],
                         independent['accepts_z_one'])
        self.assertEqual(primary['passed'], independent['passed'])
        return primary, independent

    def test_decimal_optics_matches_matrix_fit_and_known_residual_variance(self):
        standards = optical_fixture()
        primary = fit_optics([OpticalStandard(*row) for row in standards])
        independent = VERIFY.optical_fit(standards)
        self.assertTrue(primary['passed'])
        self.assertTrue(independent['passed'])
        self.assertAlmostEqual(independent['slope'], .04, places=14)
        self.assertAlmostEqual(independent['intercept'], .02, places=14)
        self.assertAlmostEqual(independent['variance'], 4 * .002 ** 2 / 3, places=16)
        for left, right in [('slope', 'slope'), ('intercept', 'intercept'),
                            ('variance', 'variance'), ('slope_ci', 'slope_interval'),
                            ('inverse_xtx', 'H'), ('residuals', 'residuals'),
                            ('coefficient_covariance', 'coefficient_covariance')]:
            np.testing.assert_allclose(primary[left], independent[right], atol=2e-15, rtol=2e-12)

    def test_optics_zero_variance_and_negative_slope_are_not_qualified(self):
        for slope in (.04, -.04):
            with self.subTest(slope=slope):
                residual = np.zeros(5) if slope > 0 else .002 * np.array([1, -1, 0, -1, 1])
                standards = [(5 * j, .02 + slope * 5 * j + residual[j]) for j in range(5)]
                primary = fit_optics([OpticalStandard(*row) for row in standards])
                independent = VERIFY.optical_fit(standards)
                self.assertFalse(primary['passed'])
                self.assertFalse(independent['passed'])

    def test_polynomial_profile_recovers_finite_exchange_and_confidence_boundaries(self):
        z = .73
        differences = .8 * (RETENTION * z) ** np.arange(12)
        differences += .0002 * np.sin(np.arange(12))
        primary, independent = self.compare_rate(differences, 1e-6)
        self.assertTrue(primary['passed'])
        self.assertTrue(any(lo <= z <= hi for lo, hi in independent['acceptance_intervals_z']))

    def test_refined_confidence_set_survives_when_no_original_grid_point_is_accepted(self):
        z = .713579
        differences = .8 * (RETENTION * z) ** np.arange(12)
        primary, independent = self.compare_rate(differences, 1e-16)
        self.assertTrue(primary['passed'])
        self.assertEqual(len(independent['acceptance_intervals_z']), 1)
        lower, upper = independent['acceptance_intervals_z'][0]
        grid = np.linspace(0, 1, 4097)
        self.assertFalse(np.any((grid >= lower) & (grid <= upper)))
        self.assertLessEqual(lower, z)
        self.assertGreaterEqual(upper, z)

    def test_endpoint_models_do_not_qualify_as_identified_finite_rates(self):
        for z, endpoint in ((0., 'z0'), (1., 'z1')):
            with self.subTest(z=z):
                differences = .8 * (RETENTION * z) ** np.arange(12)
                primary, _ = self.compare_rate(differences, 1e-6)
                self.assertFalse(primary['passed'])
                self.assertTrue(primary['endpoint_tests'][endpoint]['accepted'])
                self.assertEqual(primary['z'], z)

    def test_abrupt_loss_is_not_rescued_by_best_fitting_an_exponential(self):
        differences = .8 * (RETENTION * .8) ** np.arange(12)
        differences[5:] *= .2
        primary, independent = self.compare_rate(differences, 1e-8)
        self.assertFalse(primary['passed'])
        self.assertEqual(primary['confidence_intervals_z'], [])
        self.assertFalse(independent['fit_accepted'])

    def test_observation_map_covariance_matches_compact_stock_test_and_detects_loss(self):
        standards = optical_fixture()
        primary_optics = fit_optics([OpticalStandard(*row) for row in standards])
        independent_optics = VERIFY.optical_fit(standards)
        for loss in (False, True):
            with self.subTest(loss=loss):
                pairs = stock_fixture(loss)
                primary = total_stock_test(pairs, primary_optics, retention_fraction=RETENTION)
                independent_pairs = [{**p, 'acceptor': p['recipient']} for p in pairs]
                independent = VERIFY.total_stock_check(independent_pairs, independent_optics,
                                                       RETENTION)
                np.testing.assert_allclose(primary['covariance_q'], independent['Q'],
                                           atol=2e-14, rtol=2e-14)
                np.testing.assert_allclose(primary['residuals'], independent['residuals'],
                                           atol=3e-15, rtol=1e-10)
                self.assertAlmostEqual(primary['statistic'], independent['statistic'],
                                       delta=1e-9)
                self.assertEqual(primary['passed'], not loss)
                self.assertEqual(independent['passed'], not loss)
                # Intercept estimation couples even observations from distinct pairs.
                self.assertGreater(independent['Q'][0][11], 0)

    def test_event_integration_matches_general_two_chamber_solution(self):
        times = np.array([0., 4., 21.3, 24., 27.5, 45.6, 48., 69.6])
        initial = np.array([.83, .17])
        for g in (0., .2):
            for withdrawal in (0., .02):
                with self.subTest(g=g, withdrawal=withdrawal):
                    numeric = VERIFY.integrated_pair(times, initial, g, withdrawal_ml=withdrawal)
                    retained = (1 - withdrawal / 11) ** np.arange(len(times))
                    contrast = (initial[0] - initial[1]) * np.exp(-2 * g * times / 11)
                    analytic = retained[:, None] * np.column_stack(
                        ((initial.sum() + contrast) / 2, (initial.sum() - contrast) / 2))
                    np.testing.assert_allclose(numeric, analytic, atol=5e-12, rtol=5e-12)
                    np.testing.assert_allclose(numeric.sum(axis=1), retained * initial.sum(),
                                               atol=5e-13, rtol=0)
                    np.testing.assert_array_equal(numeric[0], initial)


if __name__ == '__main__':
    unittest.main()
