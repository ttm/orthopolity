"""Independent transfer verification on invented cohorts; no real targets."""

from copy import deepcopy
import importlib.util
from pathlib import Path
import unittest

import numpy as np

from orthopolity.membrane_exchange_transfer import evaluate, forecast
from test_membrane_exchange_transfer import synthetic_document, synthetic_targets


SPEC = importlib.util.spec_from_file_location(
    'independent_membrane_transfer_tests',
    Path(__file__).resolve().parents[1] / 'experiments/verify_membrane_transfer.py')
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


def prediction_document(qdoc):
    return {'study': qdoc['study'], 'design_commit': qdoc['design_commit'],
            'implementation_commit': '1' * 40, 'qualification_sha256': VERIFY.canonical_hash(qdoc),
            'source_sha256': qdoc['source_sha256'], 'target_later_responses_decoded': False,
            'forecasts': forecast(qdoc)}


def result_document(prediction, observations):
    return {'study': prediction['study'], 'design_commit': prediction['design_commit'],
            'implementation_commit': prediction['implementation_commit'], 'prediction_commit': '2' * 40,
            'prediction_sha256': VERIFY.canonical_hash(prediction),
            'qualification_sha256': prediction['qualification_sha256'],
            'target_later_responses_decoded': True,
            'evaluation': evaluate(prediction['forecasts'], observations)}


class MembraneTransferVerification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qualification = synthetic_document()
        cls.qualification['study'] = cls.qualification['config']['study']
        cls.qualification['config']['target_run'] = '20250603'
        cls.prediction = prediction_document(cls.qualification)

    def test_independent_forecasts_ode_and_full_complex_step_covariance(self):
        report = VERIFY.verify_predictions(self.prediction, self.qualification)
        self.assertGreater(report['numeric_checks'], 4000)
        self.assertLess(report['integration_max_abs_diff'], 2e-8)
        self.assertFalse(report['target_later_responses_decoded'])

    def test_disconnected_sets_and_unclipped_empirical_kernel(self):
        qdoc = deepcopy(self.qualification)
        f = qdoc['qualification']['retention_fraction']
        for row in qdoc['qualification']['rates']:
            row['confidence_intervals_z'] = [[.1, .2], [.8, .9]]
            row['differences'] = [1.0] + [-2.0 * f ** j for j in range(1, 12)]
        prediction = prediction_document(qdoc)
        VERIFY.verify_predictions(prediction, qdoc)
        self.assertLess(prediction['forecasts']['kernels'][-1]['models']['empirical'], 0)
        prediction['forecasts']['kernels'][1]['rate_envelope'][1] = .2
        with self.assertRaisesRegex(ValueError, 'kernels'):
            VERIFY.verify_predictions(prediction, qdoc)

    def test_joint_covariance_and_identity_corruptions_are_detected(self):
        for kind in ('offdiagonal', 'jacobian', 'identity', 'hash'):
            changed = deepcopy(self.prediction)
            if kind == 'offdiagonal':
                changed['forecasts']['conditional_uncertainty']['prediction_covariance_uM2'][0][14] = 0
            elif kind == 'jacobian':
                changed['forecasts']['conditional_uncertainty']['jacobian'][0][1] = 0
            elif kind == 'identity':
                changed['forecasts']['predictions'][0]['chamber'] = 'WRONG_CHAMBER'
            else:
                changed['qualification_sha256'] = 'f' * 64
            with self.subTest(corruption=kind), self.assertRaises(ValueError):
                VERIFY.verify_predictions(changed, self.qualification)

    def test_independent_scores_stock_covariance_and_negative_observations(self):
        rows = synthetic_targets(self.prediction['forecasts'])
        for i, row in enumerate(rows):
            row['absorbance'] += .002 * np.sin(i + .3)
        rows[1]['absorbance'] = -.1
        result = result_document(self.prediction, rows)
        report = VERIFY.verify_result(result, self.prediction, self.qualification)
        self.assertGreater(report['numeric_checks'], 6000)
        self.assertTrue(report['target_later_responses_decoded'])
        for kind in ('stock_covariance', 'score', 'decision', 'observation_identity'):
            changed = deepcopy(result)
            if kind == 'stock_covariance':
                changed['evaluation']['total_stock']['covariance_q'][0][1] = 0
            elif kind == 'score':
                changed['evaluation']['scores']['exchange']['primary_contrast_mae'] = 0
            elif kind == 'decision':
                changed['evaluation']['decision']['target_stock_compatible'] = not changed['evaluation']['decision']['target_stock_compatible']
            else:
                changed['evaluation']['observations'][0]['time_hours'] = 5
            with self.subTest(corruption=kind), self.assertRaises(ValueError):
                VERIFY.verify_result(changed, self.prediction, self.qualification)

    def test_common_loss_can_preserve_contrast_ranking_but_fail_stock(self):
        rows = synthetic_targets(self.prediction['forecasts'], common_raw_shift=-.2)
        result = result_document(self.prediction, rows)
        VERIFY.verify_result(result, self.prediction, self.qualification)
        self.assertLess(result['evaluation']['scores']['exchange']['primary_contrast_mae'], 1e-14)
        self.assertFalse(result['evaluation']['decision']['target_stock_compatible'])

    def test_qualification_partition_and_pass_are_required(self):
        for key in ('passed', 'target_observations'):
            qdoc = deepcopy(self.qualification)
            if key == 'passed':
                qdoc['qualification']['passed'] = False
            else:
                qdoc['inputs']['target_observations'] = []
            with self.subTest(gate=key), self.assertRaises(ValueError):
                VERIFY.parameterization(qdoc)


if __name__ == '__main__':
    unittest.main()
