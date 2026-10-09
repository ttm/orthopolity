"""Independent distribution and numerical-integration checks for capacities."""
import unittest

import numpy as np

from orthopolity.dependence import (
    asymptotic_dimension, capacity_samples, estimate_dependence_parameter,
    finite_dimension, forward_resource_profile, joint_survival,
    student_bivariate_survival_check, student_tail_coefficient,
)


class DependenceChecks(unittest.TestCase):
    def test_fixed_marginals_across_families(self):
        for family in ("independent", "common_shock", "gaussian", "student"):
            x = capacity_samples(40000, 3, family, .5, np.random.default_rng(130))
            np.testing.assert_allclose(np.mean(x >= 2, axis=0), .5, atol=.012)
            np.testing.assert_allclose(np.mean(x >= 5, axis=0), .2, atol=.009)
            np.testing.assert_allclose(np.log(x).mean(axis=0), 1, atol=.025)

    def test_exact_independent_and_shared_joint_laws(self):
        thresholds = np.array([1, 2, 10, 100.])
        np.testing.assert_allclose(joint_survival(thresholds, 4, "independent"), thresholds**-4)
        np.testing.assert_allclose(joint_survival(thresholds, 4, "independent", 1), thresholds**-4)
        np.testing.assert_allclose(joint_survival(thresholds, 4, "common_shock", .5), thresholds**-2.5)
        np.testing.assert_allclose(joint_survival(thresholds, 4, "common_shock", 1), thresholds**-1)
        for family in ("gaussian", "student"):
            np.testing.assert_allclose(joint_survival(thresholds, 1, family, .5), thresholds**-1)

    def test_gaussian_prediction_against_known_quadrant_probability(self):
        # At Pareto threshold 2 the latent Gaussian threshold is zero.
        rho = .5
        expected = .25+np.arcsin(rho)/(2*np.pi)
        self.assertAlmostEqual(joint_survival(2, 2, "gaussian", rho), expected, places=10)
        self.assertAlmostEqual(joint_survival(10, 4, "gaussian", 0), 1e-4, places=12)

    def test_student_mixture_against_independent_conditional_integral(self):
        for rho in (0, .5):
            for x in (1.2, 2, 10, 1000):
                expected = student_bivariate_survival_check(x, rho)
                np.testing.assert_allclose(joint_survival(x, 2, "student", rho), expected, rtol=2e-5, atol=2e-8)
        self.assertAlmostEqual(student_tail_coefficient(.5, 4), .25316999510032273, places=10)
        self.assertGreater(joint_survival(100, 2, "student", 0), 5 * 100**-2)

    def test_forward_resource_integrals_and_cap_atom(self):
        edges = np.geomspace(1, 16, 9)
        result = forward_resource_profile(edges, 2, "independent")
        np.testing.assert_allclose(result["resource_totals"], 2*(1/edges[:-1]-1/edges[1:]), rtol=1e-11)
        capped = forward_resource_profile(edges, 2, "independent", cap=16)
        self.assertAlmostEqual(capped["resource_totals"].sum(), 2-1/16, places=10)
        # Shared marginal has infinite uncapped mean, but its capped mean is
        # 1+log(cap), with an endpoint atom which must remain in the last bin.
        shared = forward_resource_profile(edges, 2, "common_shock", 1, cap=16)
        self.assertAlmostEqual(shared["resource_totals"].sum(), 1+np.log(16), places=10)

    def test_clipping_samples_matches_atom_probability(self):
        x = capacity_samples(60000, 2, "gaussian", .5, np.random.default_rng(18), cap=8)
        self.assertTrue(np.all((x >= 1) & (x <= 8)))
        self.assertAlmostEqual(np.mean(x.min(axis=1) == 8), joint_survival(8, 2, "gaussian", .5), delta=.004)
        self.assertEqual(joint_survival(8.1, 2, "gaussian", .5, cap=8), 0)

    def test_training_fits_use_capacity_information(self):
        for family, truth in (("common_shock", .5), ("gaussian", .5), ("student", .5)):
            x = capacity_samples(18000, 2, family, truth, np.random.default_rng(113))
            self.assertAlmostEqual(estimate_dependence_parameter(x, family), truth, delta=.04)

    def test_finite_dimension_differs_from_asymptotic(self):
        self.assertAlmostEqual(float(finite_dimension(10, 2, "common_shock", .5)), 1.5, places=8)
        self.assertGreater(float(finite_dimension(10, 2, "gaussian", .5)), asymptotic_dimension(2, "gaussian", .5))
        self.assertEqual(asymptotic_dimension(4, "gaussian", .5), 1.6)
        self.assertEqual(asymptotic_dimension(4, "student", .5), 1)
        with self.assertRaises(ValueError):
            finite_dimension(8, 2, "gaussian", .5, cap=8)

    def test_reproducibility_and_invalid_parameters(self):
        for family in ("independent", "common_shock", "gaussian", "student"):
            np.testing.assert_array_equal(
                capacity_samples(10, 2, family, .5, np.random.default_rng(5)),
                capacity_samples(10, 2, family, .5, np.random.default_rng(5)))
        for call in (
            lambda: capacity_samples(10, 0, "gaussian", .5, np.random.default_rng(5)),
            lambda: capacity_samples(10, 2, "student", 1.1, np.random.default_rng(5)),
            lambda: capacity_samples(10, 2, "student", .5, np.random.default_rng(5), cap=1),
            lambda: joint_survival(0, 2, "student", .5),
            lambda: forward_resource_profile([1, 3, 2], 2, "independent"),
        ):
            with self.assertRaises(ValueError):
                call()


if __name__ == "__main__":
    unittest.main()
