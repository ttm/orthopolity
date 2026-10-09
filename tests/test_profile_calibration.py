import unittest
import importlib.util
import json
import tempfile
from pathlib import Path

import numpy as np

from orthopolity.goodness_of_fit import flatness_equivalence
from orthopolity.profile_calibration import (
    batch_profile_decisions, departure_bounds_from_log_band, known_bound_bands,
    normalized_profile, profile_decision, three_way,
)


class ProfileCalibrationTests(unittest.TestCase):
    def test_pool_before_normalizing_and_account_for_unequal_widths(self):
        blocks = np.array([[1., 1.], [1., 9.]])
        phi, _, invalid = normalized_profile(blocks.mean(axis=0), [1., 2.])
        np.testing.assert_allclose(phi, [.5, 1.25])
        self.assertFalse(invalid)
        self.assertAlmostEqual(float(np.dot(phi, [1, 2])/3), 1)
        # Equal averaging of the individually normalized blocks has a
        # different estimand; neither that average nor equal-bin weighting
        # should silently replace arithmetic raw-resource pooling.
        individual, _, _ = normalized_profile(blocks, [1., 2.])
        self.assertFalse(np.allclose(phi, individual.mean(axis=0)))

    def test_zero_bins_are_unbounded_and_not_removed(self):
        result = profile_decision(np.tile([2., 0., 3.], (12, 1)), [1., 1., 1.], bootstrap_replicates=99)
        self.assertEqual(result['n_bins'], 3)
        self.assertEqual(result['point']['zero_bins'], 1)
        self.assertEqual(result['centered_bootstrap']['decision'], 'unresolved')
        self.assertTrue(result['centered_bootstrap']['departure_upper_unbounded'])
        self.assertIsNone(result['point']['log_phi'][1])

    def test_all_zero_observation_has_no_population_equivalence(self):
        result = profile_decision(np.zeros((12, 3)), [1., 1., 2.], bootstrap_replicates=99)
        self.assertTrue(result['point']['zero_total'])
        self.assertEqual(result['centered_bootstrap']['decision'], 'unresolved')
        self.assertFalse(result['percentile_max']['equivalent'])

    def test_strict_three_way_boundary_and_profile_band(self):
        margin = np.log(1.5)
        decisions = three_way([0, margin, margin+.01], [margin-.01, margin, margin+.1], 1.5)
        np.testing.assert_array_equal(decisions, ['equivalent', 'unresolved', 'departure'])
        lo, hi = departure_bounds_from_log_band([[-.3, .4], [-.1, -.7]], [[.1, .6], [.2, -.5]])
        np.testing.assert_allclose(lo, [.4, .5]); np.testing.assert_allclose(hi, [.6, .7])

    def test_known_bound_profile_ratios_cover_all_mean_box_vertices(self):
        blocks = np.array([[.4, .8], [.6, .5], [.5, .7]])
        result = known_bound_bands(blocks, [1., 2.], [.7, 1.])
        lower, upper = result['mean_lower'], result['mean_upper']
        for first in [lower[0], upper[0]]:
            for second in [lower[1], upper[1]]:
                if first+second > 0:
                    _, logs, _ = normalized_profile([first, second], [1., 2.])
                    self.assertTrue(np.all(logs >= result['log_lower']-1e-12))
                    self.assertTrue(np.all(logs <= result['log_upper']+1e-12))
        with self.assertRaises(ValueError):
            known_bound_bands(blocks, [1., 2.], [.3, 1.])

    def test_known_bound_reference_requires_external_bounds(self):
        blocks = np.ones((12, 2))
        unspecified = profile_decision(blocks, [1., 1.], bootstrap_replicates=99)
        self.assertFalse(unspecified['bounded_reference']['available'])
        specified = profile_decision(blocks, [1., 1.], bootstrap_replicates=99, resource_upper_bounds=[20., 20.])
        self.assertEqual(specified['bounded_reference']['decision'], 'unresolved')
        self.assertTrue(specified['bounded_reference']['available'])

    def test_bootstrap_reproduces_immutable_historical_max_component(self):
        blocks = np.array([[1., 2., 3.], [3., 1., 2.], [2., 3., 1.], [2., 1., 2.]])
        widths = np.ones(3); seed = 7; repeats = 99
        current = profile_decision(blocks, widths, bootstrap_replicates=repeats, seed=seed)
        weights = np.random.default_rng(seed).multinomial(4, [.25]*4, size=(1, repeats))[0]
        phi, _, _ = normalized_profile(blocks.mean(axis=0), widths)
        draws, _, _ = normalized_profile(weights@blocks/4, widths)
        historical = flatness_equivalence(np.exp([.5, 1.5, 2.5]), phi, tolerance_factor=1.5,
                                          domain=(1, np.exp(3)), phi_draws=draws)
        self.assertAlmostEqual(current['percentile_max']['departure_upper'], historical['departure_upper_bound'])
        self.assertEqual(current['percentile_max']['equivalent'], historical['departure_equivalent'])

    def test_units_and_log_width_scale_do_not_change_decision(self):
        rng = np.random.default_rng(9)
        blocks = rng.uniform(.5, 2, size=(12, 3))
        first = profile_decision(blocks, [1., 1., 3.], seed=5, bootstrap_replicates=99)
        second = profile_decision(blocks*1000, np.array([1., 1., 3.])*np.log(10), seed=5, bootstrap_replicates=99)
        np.testing.assert_allclose(first['point']['phi'], second['point']['phi'], rtol=1e-12)
        self.assertAlmostEqual(first['centered_bootstrap']['radius'], second['centered_bootstrap']['radius'])
        self.assertEqual(first['centered_bootstrap']['decision'], second['centered_bootstrap']['decision'])

    def test_batch_agrees_with_single_dataset_api(self):
        blocks = np.random.default_rng(10).uniform(.5, 2, size=(12, 3))
        single = profile_decision(blocks, [1., 1., 3.], seed=13, bootstrap_replicates=99)
        batch = batch_profile_decisions(blocks[None], [1., 1., 3.], rng=np.random.default_rng(13), bootstrap_replicates=99)
        self.assertAlmostEqual(single['centered_bootstrap']['radius'], batch['radius'][0])
        self.assertEqual(single['centered_bootstrap']['decision'], batch['methods']['centered_bootstrap']['decision'][0])

    def test_invalid_negative_resources_and_widths_rejected(self):
        with self.assertRaises(ValueError):
            profile_decision([[1, -1], [2, 1]], [1, 1])
        with self.assertRaises(ValueError):
            profile_decision([[1, 1], [2, 1]], [1, 0])

    def test_completed_output_audit_detects_tampered_artifact(self):
        root = Path(__file__).resolve().parents[1]
        spec = importlib.util.spec_from_file_location('profile_calibration_runner', root/'experiments/run_profile_calibration.py')
        runner = importlib.util.module_from_spec(spec); spec.loader.exec_module(runner)
        with tempfile.TemporaryDirectory(dir=root/'build') as temporary:
            output = Path(temporary); artifact = output/'example.json'
            artifact.write_text('{}\n')
            record = dict(artifacts=[dict(path=str(artifact.relative_to(root)), sha256=runner.digest(artifact))])
            (output/'output-manifest.json').write_text(json.dumps(record))
            runner.output_audit(output)
            artifact.write_text('{"changed":true}\n')
            with self.assertRaises(ValueError):
                runner.output_audit(output)


if __name__ == '__main__':
    unittest.main()
