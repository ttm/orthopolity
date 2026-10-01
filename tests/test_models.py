"""Structural and distribution checks for the simulation models."""

import unittest

import numpy as np

from orthopolity.models import (
    bounded_multiplicative_growth,
    conservative_exchange,
    erdos_renyi_degrees,
    inverse_cost_samples,
    joint_feasibility_samples,
    preferential_attachment_degrees,
)


class ModelChecks(unittest.TestCase):
    def test_preferential_attachment_edge_budget_and_reproducibility(self):
        n, m = 2000, 3
        degree = preferential_attachment_degrees(n, m, np.random.default_rng(74))
        edges = m * (m + 1) // 2 + m * (n - m - 1)
        self.assertEqual(int(degree.sum()), 2 * edges)
        self.assertTrue(np.all((degree >= m) & (degree < n)))
        # Growth concentrates degree well above the mean even from a regular seed.
        self.assertGreater(degree.max(), 5 * degree.mean())
        np.testing.assert_array_equal(
            degree, preferential_attachment_degrees(n, m, np.random.default_rng(74)))

    def test_preferential_attachment_complete_seed(self):
        np.testing.assert_array_equal(
            preferential_attachment_degrees(5, 4, np.random.default_rng(2)),
            np.full(5, 4))

    def test_erdos_renyi_extremes_and_sparse_degree_statistics(self):
        n = 6000
        np.testing.assert_array_equal(
            erdos_renyi_degrees(n, 0, np.random.default_rng(4)), np.zeros(n))
        np.testing.assert_array_equal(
            erdos_renyi_degrees(20, 19, np.random.default_rng(4)), np.full(20, 19))
        degree = erdos_renyi_degrees(n, 6, np.random.default_rng(4))
        self.assertEqual(int(degree.sum()) % 2, 0)
        self.assertTrue(np.all((degree >= 0) & (degree < n)))
        self.assertAlmostEqual(degree.mean(), 6, delta=.25)
        self.assertAlmostEqual(degree.var(), 6 * (1 - 6 / (n - 1)), delta=.65)
        np.testing.assert_array_equal(
            degree, erdos_renyi_degrees(n, 6, np.random.default_rng(4)))

    def test_conservative_exchange_and_saving(self):
        n = 40000
        exchange = conservative_exchange(n, 60, np.random.default_rng(59))
        saving = conservative_exchange(n, 60, np.random.default_rng(59), saving=.5)
        for resource in (exchange, saving):
            self.assertGreaterEqual(resource.min(), 0)
            self.assertAlmostEqual(resource.sum(), n, delta=1e-8)
        self.assertAlmostEqual(np.mean(exchange <= 1), 1 - np.exp(-1), delta=.015)
        self.assertAlmostEqual(exchange.var(), 1, delta=.075)
        self.assertLess(saving.var(), .4 * exchange.var())
        np.testing.assert_array_equal(
            conservative_exchange(20, 10, np.random.default_rng(4), saving=1),
            np.ones(20))

    def test_multiplicative_growth_has_boundary_atom(self):
        samples = bounded_multiplicative_growth(
            40000, 1, -.1, .3, np.random.default_rng(81))
        self.assertTrue(np.all(samples >= 1))
        # One-step boundary probability is Phi(1/3), independently computable.
        self.assertAlmostEqual(np.mean(samples == 1), .63055866, delta=.01)
        np.testing.assert_array_equal(
            bounded_multiplicative_growth(20, 0, -.1, .3, np.random.default_rng(8)),
            np.ones(20))

    def test_feasibility_fixed_marginals_and_joint_prediction(self):
        n, resources = 60000, 4
        for theta in (0, .4, 1):
            result = joint_feasibility_samples(
                n, resources, theta, np.random.default_rng(935))
            log_capacity = result['log_capacities']
            np.testing.assert_array_equal(result['size'], result['capacities'].min(axis=1))
            self.assertTrue(np.all(result['size'] >= 1))
            # The specified law has Exp(1) log marginal capacities.
            np.testing.assert_allclose(log_capacity.mean(axis=0), 1, atol=.025)
            np.testing.assert_allclose(
                np.mean(log_capacity >= 1, axis=0), np.exp(-1), atol=.008)
            gamma = resources - (resources - 1) * theta
            self.assertAlmostEqual(np.log(result['size']).mean(), 1 / gamma, delta=.015)
            self.assertAlmostEqual(
                np.mean(result['size'] >= np.exp(.5)), np.exp(-gamma * .5), delta=.008)
            if theta == 1:
                np.testing.assert_array_equal(
                    result['capacities'],
                    np.repeat(result['capacities'][:, :1], resources, axis=1))

    def test_inverse_cost_control_known_cdfs(self):
        n = 50000
        # alpha=2 on [1, 10] has CDF(2)=(1-1/2)/(1-1/10).
        samples = inverse_cost_samples(n, 1, 10, 1, 0, np.random.default_rng(61))
        self.assertTrue(np.all((samples >= 1) & (samples <= 10)))
        self.assertAlmostEqual(np.mean(samples <= 2), .5 / .9, delta=.01)
        # alpha=1 is uniform in log scale; alpha=0 is uniform in size.
        logarithmic = inverse_cost_samples(n, 1, 100, 2, 2, np.random.default_rng(61))
        uniform = inverse_cost_samples(n, 1, 10, 2, 3, np.random.default_rng(61))
        self.assertAlmostEqual(np.mean(logarithmic <= 10), .5, delta=.01)
        self.assertAlmostEqual(uniform.mean(), 5.5, delta=.03)

    def test_invalid_model_parameters(self):
        rng = np.random.default_rng(2)
        invalid = (
            lambda: preferential_attachment_degrees(2, 2, rng),
            lambda: erdos_renyi_degrees(5, 5, rng),
            lambda: conservative_exchange(3, 10, rng),
            lambda: conservative_exchange(4, 10, rng, saving=-.1),
            lambda: bounded_multiplicative_growth(10, 2, 0, 1, rng),
            lambda: joint_feasibility_samples(10, 3, 1.1, rng),
            lambda: inverse_cost_samples(10, 0, 1, 2, 0, rng),
        )
        for call in invalid:
            with self.assertRaises(ValueError):
                call()


if __name__ == '__main__':
    unittest.main()
