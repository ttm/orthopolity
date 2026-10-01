import unittest

import numpy as np
from scipy.integrate import quad

from orthopolity.resource_identification import (
    binned_deviance, bounded_log_mean, bounded_power_mle, coordinate_prediction,
    curvature, exponential_moment, hazard_extrema, inverse_cdf_table, log_cdf,
    log_density, matched_curvature, population_summary, removal_hazard, sample_cohorts,
)


class ResourceIdentificationTests(unittest.TestCase):
    def setUp(self):
        self.width = np.log(64)
        self.model = matched_curvature(self.width, 1.)

    def test_moments_match_independent_quadrature(self):
        for order in range(4):
            expected = quad(lambda u: u**order*np.exp(-u), 0, self.width)[0]
            self.assertAlmostEqual(float(exponential_moment(order, self.width, 1)), expected, places=12)

    def test_modulation_preserves_normalization_and_population_mle(self):
        neutral = population_summary(self.model, 0, 1, 12)
        curved = population_summary(self.model, .8, 1, 12)
        self.assertAlmostEqual(curved['probability_integral'], 1, places=12)
        self.assertAlmostEqual(neutral['mean_log_size'], curved['mean_log_size'], places=12)
        self.assertAlmostEqual(curved['population_bounded_power_mle'], 2, places=11)
        self.assertGreater(curved['binned_max_log_departure'], np.log(1.5))
        self.assertLess(neutral['binned_max_log_departure'], 1e-12)

    def test_positive_hazard_solves_stationary_transport(self):
        grid = np.linspace(.001, self.width-.001, 300)
        step = 1e-5
        derivative = (np.log(log_density(grid+step, self.model, .8))-
                      np.log(log_density(grid-step, self.model, .8)))/(2*step)
        np.testing.assert_allclose(derivative, -removal_hazard(grid, self.model, .8), atol=2e-10, rtol=0)
        extrema = hazard_extrema(self.model, .8)
        self.assertGreater(extrema['minimum'], 0)
        dense = removal_hazard(np.linspace(0, self.width, 10001), self.model, .8)
        self.assertLessEqual(extrema['minimum'], dense.min()+1e-12)
        self.assertGreaterEqual(extrema['maximum'], dense.max()-1e-12)

    def test_continuous_mle_including_zero_and_negative_log_rate(self):
        rates = np.array([-2., -.5, 0., 1e-6, .5, 1., 2., 10.])
        recovered = bounded_power_mle(bounded_log_mean(rates, self.width), self.width)
        np.testing.assert_allclose(recovered, rates+1, atol=3e-10, rtol=0)
        with self.assertRaises(ValueError):
            bounded_power_mle(0, self.width)

    def test_cdf_matches_independent_integrals_and_sampler_audit(self):
        for upper in np.linspace(0, self.width, 7):
            expected = quad(lambda u: float(log_density(u, self.model, .8)), 0, upper)[0]
            self.assertAlmostEqual(float(log_cdf(upper, self.model, .8)), expected, places=12)
        table = inverse_cdf_table(self.model, .8, 65537)
        self.assertLess(table['maximum_midpoint_cdf_error'], 1e-8)
        self.assertTrue(np.all(np.diff(table['probabilities']) > 0))

    def test_sampler_preserves_all_objects_and_exact_log_sum(self):
        rng = np.random.default_rng(3)
        samples = sample_cohorts(self.model, 0, 100, 3, 12, rng)
        np.testing.assert_array_equal(samples['counts'].sum(axis=-1), 100)
        expected_uniform = np.random.default_rng(3).random((3, 100))
        expected_u = -np.log1p(-expected_uniform*(1-np.exp(-self.width)))
        np.testing.assert_allclose(samples['log_sums'], expected_u.sum(axis=1), atol=1e-12, rtol=0)
        np.testing.assert_allclose(samples['exponent'], bounded_power_mle(expected_u.mean(axis=1), self.width))
        np.testing.assert_allclose(samples['resource_bin_totals'].sum(axis=-1), np.exp(expected_u).sum(axis=1), atol=1e-10, rtol=0)

    def test_complete_profile_deviance_retains_zero_bins(self):
        value = binned_deviance(np.array([[10, 0], [5, 5]]), [.5, .5])
        np.testing.assert_allclose(value, [20*np.log(2), 0], atol=1e-12, rtol=0)
        with self.assertRaises(ValueError):
            binned_deviance([[0, 0]], [.5, .5])

    def test_coordinate_change_transports_cost_and_mle_together(self):
        transformed = coordinate_prediction(2., 1., 3.)
        self.assertAlmostEqual(transformed['density_exponent'], 4/3)
        self.assertAlmostEqual(transformed['physical_cost_exponent'], 1/3)
        # Direct likelihood fits on exactly corresponding observed sizes.
        log_sizes = np.array([.2, .6, 1.4, 2.9])
        alpha = float(bounded_power_mle(log_sizes.mean(), self.width))
        mapped = float(bounded_power_mle(3*log_sizes.mean(), 3*self.width))
        self.assertAlmostEqual(mapped, 1+(alpha-1)/3, places=12)


if __name__ == '__main__':
    unittest.main()
