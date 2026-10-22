"""Invented transfer cohorts only; no archive or real later-target access."""

from copy import deepcopy
from dataclasses import asdict
import json
import math
import unittest

import numpy as np

from orthopolity.membrane_exchange import qualify
from orthopolity.membrane_exchange_source import TARGET_RUN
from orthopolity.membrane_exchange_transfer import MODELS, evaluate, forecast
from test_membrane_exchange import CONFIG, synthetic_source


def synthetic_document():
    source = synthetic_source()
    cfg = {**CONFIG, 'dilution_factor': 10.0, 'study': 'invented-transfer',
           'reference_measure': 'Compartment volume; neither log-orthopolic nor linear-orthopolic size allocation.'}
    return dict(qualification=qualify(source, cfg), config=cfg, inputs=asdict(source),
                target_later_responses_decoded=False, design_commit='0' * 40,
                source_sha256='synthetic-no-archive')


def synthetic_targets(predictions, model='exchange', common_raw_shift=0.0):
    a, b = predictions['optics']['slope'], predictions['optics']['intercept']
    dilution = predictions['config']['dilution_factor']
    return [dict(sample=row['sample'], chamber=row['chamber'], time_hours=row['time_hours'],
                 absorbance=b + a * row['model_concentrations_uM'][model] / dilution + common_raw_shift)
            for row in predictions['predictions']]


class MembraneExchangeTransfer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = synthetic_document()

    def setUp(self):
        self.qdoc = deepcopy(self.document)

    def test_arithmetic_mixture_not_exponentiated_average_and_sampling_balance(self):
        output = forecast(self.qdoc)
        self.assertEqual(len(output['predictions']), 56)
        self.assertFalse(output['target_later_responses_decoded'])
        kernel = output['kernels'][2]
        time = kernel['time_hours']
        rates = np.array([r['lambda_per_hour'] for r in output['calibrators']])
        self.assertAlmostEqual(kernel['models']['exchange'], np.exp(-rates * time).mean())
        self.assertGreater(kernel['models']['exchange'], math.exp(-rates.mean() * time))
        for k, baseline in enumerate(output['baseline_pairs']):
            for j in range(1, 8):
                donor, recipient = output['predictions'][14 * k + 2 * (j - 1):14 * k + 2 * j]
                for name in MODELS:
                    self.assertAlmostEqual(donor['model_concentrations_uM'][name]
                                           + recipient['model_concentrations_uM'][name],
                                           output['retention_fraction'] ** j * baseline['total_uM'])
        json.dumps(output, allow_nan=False)

    def test_full_covariance_and_jacobian_preserve_shared_optics_and_pair_baselines(self):
        original = forecast(self.qdoc)
        jacobian = np.asarray(original['conditional_uncertainty']['jacobian'])
        numeric = np.zeros_like(jacobian)
        for column in range(10):
            step = 1e-7
            values = []
            for sign in (-1, 1):
                changed = deepcopy(self.qdoc)
                if column < 2:
                    field = ('slope', 'intercept')[column]
                    changed['qualification']['optics'][TARGET_RUN][field] += sign * step
                else:
                    pair, chamber = divmod(column - 2, 2)
                    field = ('donor_raw', 'recipient_raw')[chamber]
                    changed['qualification']['baselines'][TARGET_RUN]['pairs'][pair][field] += sign * step
                values.append([r['concentration_uM'] for r in forecast(changed)['predictions']])
            numeric[:, column] = (np.asarray(values[1]) - np.asarray(values[0])) / (2 * step)
        np.testing.assert_allclose(jacobian, numeric, rtol=2e-8, atol=2e-7)
        uncertainty = original['conditional_uncertainty']
        inputs = np.asarray(uncertainty['input_covariance'])
        covariance = np.asarray(uncertainty['prediction_covariance_uM2'])
        np.testing.assert_allclose(covariance, numeric @ inputs @ numeric.T, rtol=8e-8, atol=1e-10)
        self.assertEqual(covariance.shape, (56, 56))
        self.assertNotEqual(covariance[0, 14], 0)
        self.assertNotEqual(inputs[0, 1], 0)
        self.assertGreaterEqual(np.linalg.eigvalsh(covariance).min(), -1e-12)
        for row, variance in zip(original['predictions'], covariance.diagonal()):
            self.assertAlmostEqual(row['optical_baseline_sd_uM'] ** 2, variance)

    def test_disconnected_rate_sets_all_contribute_to_envelope_and_timing_is_separate(self):
        for row in self.qdoc['qualification']['rates']:
            row['confidence_intervals_z'] = [[.1, .2], [.8, .9]]
        output = forecast(self.qdoc)
        kernel = output['kernels'][1]
        t = kernel['time_hours']
        np.testing.assert_allclose(kernel['rate_envelope'], [.1 ** (t / 6), .9 ** (t / 6)])
        self.assertGreater(kernel['timing_sensitivity']['minus_10_minutes'], kernel['models']['exchange'])
        self.assertLess(kernel['timing_sensitivity']['plus_10_minutes'], kernel['models']['exchange'])
        for row in output['predictions']:
            self.assertLessEqual(row['rate_envelope_uM'][0], row['rate_envelope_uM'][1])
            self.assertEqual(row['between_calibrator_range_uM'],
                             [min(row['single_calibrator_concentrations_uM']),
                              max(row['single_calibrator_concentrations_uM'])])

    def test_empirical_kernel_is_unclipped_and_flat_beyond_last_calibration(self):
        f = self.qdoc['qualification']['retention_fraction']
        for row in self.qdoc['qualification']['rates']:
            row['differences'] = [1.0] + [-2.0 * f ** j for j in range(1, 12)]
        output = forecast(self.qdoc)
        self.assertEqual(output['kernels'][-1]['models']['empirical'], -2.0)
        self.assertEqual(output['empirical_calibration']['normalized_contrast'][-1], -2.0)
        self.assertLess(output['kernels'][2]['models']['empirical'], 0)

    def test_exact_transfer_wins_declared_scores_and_stock_is_separate(self):
        output = forecast(self.qdoc)
        result = evaluate(output, synthetic_targets(output))
        self.assertLess(result['scores']['exchange']['primary_contrast_mae'], 1e-14)
        self.assertTrue(result['decision']['exchange_beats_all_benchmarks'])
        self.assertTrue(result['decision']['target_stock_compatible'])
        self.assertEqual(result['total_stock']['n'], 28)
        self.assertEqual(len(result['observations']), 56)
        # A common chamber offset leaves contrast forecasts exactly right but
        # causes a separately detectable stock discrepancy.
        shifted = evaluate(output, synthetic_targets(output, common_raw_shift=-.2))
        self.assertLess(shifted['scores']['exchange']['primary_contrast_mae'], 1e-14)
        self.assertFalse(shifted['decision']['target_stock_compatible'])
        self.assertGreater(shifted['scores']['exchange']['normalized_total_mae'], .3)
        json.dumps(shifted, allow_nan=False)

    def test_each_benchmark_can_win_without_target_refitting(self):
        output = forecast(self.qdoc)
        for name in MODELS[1:]:
            with self.subTest(model=name):
                result = evaluate(output, synthetic_targets(output, model=name))
                self.assertLess(result['scores'][name]['primary_contrast_mae'], 1e-14)
                self.assertFalse(result['decision']['exchange_beats_each_benchmark'][name])
                self.assertLess(result['gains'][name]['absolute_difference'], 0)

    def test_scores_balance_times_then_pairs_and_preserve_negative_observations(self):
        output = forecast(self.qdoc)
        rows = synthetic_targets(output)
        rows[0]['absorbance'] = -.1
        result = evaluate(output, rows)
        self.assertEqual(result['observations'][0]['absorbance'], -.1)
        self.assertGreater(result['extrapolation']['outside_support_count'], 0)
        pair_scores = result['scores']['exchange']['per_pair']
        self.assertAlmostEqual(result['scores']['exchange']['primary_contrast_mae'],
                               sum(p['primary_contrast_mae'] for p in pair_scores) / 4)
        reversed_result = evaluate(output, list(reversed(rows)))
        self.assertEqual(result, reversed_result)

    def test_qualification_and_complete_identity_grid_are_required(self):
        changed = deepcopy(self.qdoc)
        changed['qualification']['passed'] = False
        with self.assertRaises(ValueError):
            forecast(changed)
        changed = deepcopy(self.qdoc)
        changed['inputs']['target_observations'] = []
        with self.assertRaises(ValueError):
            forecast(changed)
        output = forecast(self.qdoc)
        rows = synthetic_targets(output)
        for malformed in (rows[:-1], rows + rows[:1],
                          [{**rows[0], 'absorbance': float('nan')}] + rows[1:]):
            with self.assertRaises(ValueError):
                evaluate(output, malformed)


if __name__ == '__main__':
    unittest.main()
