"""Identification, analytic contrasts, conditioning, and correlated uncertainty."""
import unittest

import numpy as np
from scipy.stats import norm

from orthopolity.inverse_resources import (
    contrast_moments, corrected_slope_covariance, design_geometry,
    fit_composition, fixed_design_error_bound, heldout_prediction, target_weights,
)


class InverseResourceTests(unittest.TestCase):
    def test_exact_composition_and_heldout_identity_with_known_offsets(self):
        design = np.array([[1., 1.], [1., 2.], [2., 1.]])
        offsets = np.array([.15, -.1, .2])
        slopes = np.array([1.5, 2., 2.5]) + offsets
        fit = fit_composition(design[:2], slopes[:2], offsets=offsets[:2])
        np.testing.assert_allclose(fit["theta"], [1, .5], atol=1e-14)
        forecast = heldout_prediction(design[:2], design[2], slopes,
                                      offsets=offsets, joint_covariance=np.eye(3))
        np.testing.assert_allclose(forecast["weights"], [3, -1], atol=1e-14)
        np.testing.assert_allclose(forecast["contrast_weights"], [-3, 1, 1], atol=1e-14)
        self.assertAlmostEqual(forecast["prediction"], 2.7)
        self.assertAlmostEqual(forecast["residual"], 0)
        self.assertAlmostEqual(forecast["variance"], 11)

    def test_deficient_components_can_leave_a_target_identified(self):
        design = np.array([[1., 1.], [2., 2.]])
        geometry = design_geometry(design)
        self.assertEqual(geometry["rank"], 1)
        np.testing.assert_allclose(design @ geometry["null_basis"], 0, atol=1e-14)
        np.testing.assert_allclose(design @ [1, .5], design @ [.25, 1.25])
        weights = target_weights(design, [3, 3])
        np.testing.assert_allclose(weights, [.6, 1.2], atol=1e-14)
        self.assertAlmostEqual(weights @ [1.5, 3], 4.5)
        with self.assertRaisesRegex(ValueError, "row space"):
            target_weights(design, [1, 0])
        with self.assertRaisesRegex(ValueError, "not identified"):
            fit_composition(design, [1.5, 3])

    def test_left_null_contrasts_express_compatibility_not_training_fit(self):
        design = np.array([[1., 1.], [1., 2.], [2., 1.]])
        contrasts = design_geometry(design)["left_null_basis"].T
        np.testing.assert_allclose(contrasts @ design, 0, atol=1e-14)
        np.testing.assert_allclose(contrasts @ [1.5, 2, 2.5], 0, atol=1e-14)
        # The explicit unnormalised contrast detects a changed held-out slope.
        result = contrast_moments([[-3, 1, 1]], [1.5, 2, 3], np.eye(3))
        np.testing.assert_allclose(result["value"], [.5])
        np.testing.assert_allclose(result["covariance"], [[11]])
        self.assertEqual(design_geometry(design[:2])["left_null_basis"].shape, (2, 0))

    def test_weighted_partial_target_uses_precision_without_identifying_components(self):
        design = np.array([[1., 1.], [2., 2.]])
        # Both b1 and b2/2 estimate the sum with variance one. Average them,
        # then multiply by three: weights (3/2,3/4), target variance 9/2.
        covariance = np.diag([1., 4.])
        weights = target_weights(design, [3., 3.], covariance=covariance)
        np.testing.assert_allclose(weights, [1.5, .75], atol=1e-14)
        self.assertAlmostEqual(weights @ covariance @ weights, 4.5)
        self.assertIsNone(design_geometry(design)["condition_number"])
        with self.assertRaisesRegex(ValueError, "not identified"):
            fit_composition(design, [1.5, 3], covariance=covariance)

    def test_zero_design_identifies_only_zero_targets(self):
        geometry = design_geometry(np.zeros((3, 2)))
        self.assertEqual(geometry["rank"], 0)
        np.testing.assert_allclose(geometry["null_basis"] @ geometry["null_basis"].T, np.eye(2))
        np.testing.assert_allclose(target_weights(np.zeros((3, 2)), [0., 0.]), [0., 0., 0.])
        with self.assertRaisesRegex(ValueError, "row space"):
            target_weights(np.zeros((3, 2)), [0., 1.])

    def test_gls_matches_analytic_overdetermined_solution(self):
        # Minimise (1-a)^2 + (2-b)^2/4 + (3.5-a-b)^2.
        design = [[1, 0], [0, 1], [1, 1]]
        fit = fit_composition(design, [1, 2, 3.5], covariance=np.diag([1, 4, 1]))
        np.testing.assert_allclose(fit["theta"], [13 / 12, 7 / 3], atol=1e-14)
        np.testing.assert_allclose(fit["covariance"], [[5 / 6, -2 / 3], [-2 / 3, 4 / 3]], atol=1e-14)
        np.testing.assert_allclose(fit["estimator"] @ design, np.eye(2), atol=1e-14)

    def test_heldout_covariance_includes_cross_correlations(self):
        covariance = np.full((3, 3), .8)
        np.fill_diagonal(covariance, 1)
        result = heldout_prediction([[1, 1], [1, 2]], [2, 1], [1.5, 2, 2.5],
                                    joint_covariance=covariance)
        # c=(-3,1,1): c' Sigma c=.2*11+.8*(-1)^2=3.
        self.assertAlmostEqual(result["variance"], 3)
        self.assertAlmostEqual(result["prediction_variance"], 5.2)
        self.assertGreater(result["prediction_variance"] + covariance[-1, -1],
                           2 * result["variance"])

    def test_uncertain_offsets_propagate_both_cross_covariance_terms(self):
        slope = np.array([[.04, .01], [.01, .09]])
        offset = .01 * np.eye(2)
        cross = np.array([[.002, .001], [-.0005, .003]])
        np.testing.assert_array_equal(corrected_slope_covariance(slope), slope)
        result = corrected_slope_covariance(slope, offset, cross)
        np.testing.assert_allclose(result, [[.046, .0095], [.0095, .094]])
        # Perfectly shared slope/offset error cancels, producing a PSD zero matrix.
        np.testing.assert_allclose(corrected_slope_covariance(slope, slope, slope), 0)
        with self.assertRaises(ValueError):
            corrected_slope_covariance(slope, offset, np.eye(2))

    def test_fixed_design_bound_and_near_collinear_amplification(self):
        epsilon = 1e-4
        design = np.array([[1., 1.], [1., 1 + epsilon]])
        delta = np.array([0., .001])
        effect = design_geometry(design)["pseudoinverse"] @ delta
        np.testing.assert_allclose(effect, [-10, 10], rtol=1e-10)
        self.assertLessEqual(np.linalg.norm(effect), fixed_design_error_bound(design, delta))
        # The singular direction reaches the absolute operator-norm bound.
        u, _, _ = np.linalg.svd(design)
        weakest_delta = .001 * u[:, -1]
        weakest_effect = design_geometry(design)["pseudoinverse"] @ weakest_delta
        self.assertAlmostEqual(np.linalg.norm(weakest_effect)
                               / fixed_design_error_bound(design, weakest_delta), 1, places=12)
        well = fixed_design_error_bound([[1, 1], [1, 2]], delta)
        self.assertGreater(fixed_design_error_bound(design, delta) / well, 1000)

    def test_gaussian_replicates_follow_joint_prediction_uncertainty(self):
        design = np.array([[1., 1.], [1., 2.], [2., 1.]])
        covariance = .0004 * np.array([[1., .35, .2], [.35, 1., .4], [.2, .4, 1.]])
        truth = design @ [1, .5]
        rng = np.random.default_rng(840261)
        slopes = rng.multivariate_normal(truth, covariance, size=15000)
        fit = fit_composition(design[:2], truth[:2], covariance=covariance[:2, :2])
        estimated = slopes[:, :2] @ fit["estimator"].T
        np.testing.assert_allclose(np.cov(estimated, rowvar=False), fit["covariance"], rtol=.05)
        forecast = heldout_prediction(design[:2], design[2], truth, joint_covariance=covariance)
        z = (slopes @ forecast["contrast_weights"]) / forecast["standard_error"]
        self.assertLess(abs(z.mean()), 5 / np.sqrt(len(z)))
        self.assertLess(abs(z.var(ddof=1) - 1), .05)
        self.assertLess(abs(np.mean(np.abs(z) <= norm.ppf(.975)) - .95), .008)

    def test_invalid_inputs_and_unresolved_designs(self):
        for matrix in ([], [[np.nan]], [[np.inf]], [1, 2]):
            with self.assertRaises(ValueError):
                design_geometry(matrix)
        for rcond in (0, -1, np.nan, 1):
            with self.assertRaises(ValueError):
                design_geometry([[1]], rcond=rcond)
        with self.assertRaises(ValueError):
            fit_composition([[1], [2]], [1])
        with self.assertRaises(ValueError):
            fit_composition([[1], [2]], [1, 2], covariance=[[1, 2], [2, 1]])
        with self.assertRaises(ValueError):
            heldout_prediction([[1]], [1], [1, 2], joint_covariance=[[1, 0], [1, 1]])
        with self.assertRaises(ValueError):
            fixed_design_error_bound([[1, 1], [2, 2]], [1, 0])


if __name__ == "__main__":
    unittest.main()
