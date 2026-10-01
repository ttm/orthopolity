"""Checks of capacity-only scoring, bounded targets and bootstrap functionals."""
import unittest

import numpy as np

from orthopolity.forecast import (
    bounded_bootstrap_cdf_distance, bounded_population_cdf_distance,
    bounded_resource_moments, fit_capacity_candidates, lookup_prediction,
    resource_prediction_from_survival, select_capacity_candidate,
    sup_bootstrap_radius, threshold_brier_score,
)


class ForecastChecks(unittest.TestCase):
    def test_resource_means_keep_outside_exposure_and_empty_bins(self):
        result = bounded_resource_moments([1, 2, 2, 20], [1, 2, 4, 8])
        np.testing.assert_allclose(result["means"], [.25, 1, 0])
        self.assertEqual(result["phi"][-1], 0)
        np.testing.assert_allclose(result["phi"].mean(), 1)

    def test_forward_prediction_against_independent_pareto_integrals(self):
        edges = np.geomspace(1, 12, 7)
        result = resource_prediction_from_survival(edges, lambda x: np.asarray(x)**-2)
        np.testing.assert_allclose(result["means"], 2*(1/edges[:-1]-1/edges[1:]), rtol=1e-12)

    def test_proper_score_prefers_correct_distribution_in_expectation(self):
        minima = np.r_[np.ones(60), np.full(40, 3)]
        true = np.array([.4])
        self.assertAlmostEqual(threshold_brier_score(true, minima, [2]), .24)
        self.assertGreater(threshold_brier_score([.6], minima, [2]), .24)
        predictions = {"independent": true, "common_shock": [.6], "gaussian": [.7], "student": [.8]}
        self.assertEqual(select_capacity_candidate(predictions, minima, [2])[0], "independent")

    def test_bootstrap_sup_distance_handles_tied_minima(self):
        # After an entire tie group at one, the EDF changes by 1/4, not the
        # spurious discrepancy that arises by treating equal points separately.
        self.assertAlmostEqual(bounded_bootstrap_cdf_distance([1, 1, 2, 3], [0, 1, 2, 1], 3), .25)
        self.assertEqual(bounded_bootstrap_cdf_distance([1, 1, 2, 3], [0, 2, 1, 1], 3), 0)

    def test_population_cdf_sup_checks_both_jump_sides(self):
        # Uniform distribution on [1,3], evaluated at two endpoints.
        survival = lambda x: 1-(np.asarray(x)-1)/2
        self.assertAlmostEqual(bounded_population_cdf_distance([1, 3], survival, 3), .5)

    def test_interpolation_preserves_raw_resource_before_normalizing(self):
        bank = {"log_widths": [1, 1], "gaussian": {"parameter_grid": [0, 1],
            "survival": [[.5, .2], [.7, .4]], "resource_means": [[1, 1], [3, 1]]}}
        result = lookup_prediction(bank, "gaussian", .5)
        np.testing.assert_allclose(result["resource_means"], [2, 1])
        np.testing.assert_allclose(result["phi"], [4/3, 2/3])
        with self.assertRaises(ValueError):
            lookup_prediction(bank, "gaussian", 1.1)

    def test_simultaneous_radius_uses_whole_vector_departures(self):
        radius = sup_bootstrap_radius([1, 1], [[1, 1], [2, 1], [1, 3]], .5)
        self.assertEqual(radius, 1)

    def test_candidate_parameters_depend_only_on_given_capacities(self):
        from orthopolity.dependence import capacity_samples
        capacities = capacity_samples(20000, 2, "gaussian", .5, np.random.default_rng(384))
        fitted = fit_capacity_candidates(capacities)
        self.assertAlmostEqual(fitted["gaussian"], .5, delta=.04)
        self.assertEqual(fitted["gaussian"], fitted["student"])
        self.assertEqual(fitted["independent"], 0)


if __name__ == "__main__":
    unittest.main()
