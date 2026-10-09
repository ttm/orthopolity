"""Independent solutions, conservation, constraint release, and quantum noise."""
import unittest

import numpy as np

from orthopolity.class_exchange import (
    advance_quanta, equilibrium, evolve, generator, relative_l2, spectral_gap,
    transition_matrix,
)


class ClassExchangeTests(unittest.TestCase):
    def test_two_class_closed_form_and_orientation(self):
        # Rates 0->1 = 3 and 1->0 = 2; p0(t)=2/5+(p0(0)-2/5) exp(-5t).
        matrix = generator([2, 3], [[0, 6], [6, 0]])
        np.testing.assert_allclose(matrix, [[-3, 2], [3, -2]])
        times = np.array([0, .01, .3, 2])
        result = evolve(matrix, [7, 3], times)
        p0 = .4 + .3 * np.exp(-5 * times)
        np.testing.assert_allclose(result[:, 0], 10 * p0, atol=2e-13)
        np.testing.assert_allclose(result[:, 1], 10 * (1 - p0), atol=2e-13)
        self.assertAlmostEqual(spectral_gap(matrix, equilibrium([2, 3])), 5)

    def test_nonuniform_measure_and_detailed_balance(self):
        weights = np.array([.1, .3, .6])
        conductances = np.array([[0, 2, 1], [2, 0, 4], [1, 4, 0]])
        potential = np.array([.8, -.1, .5])
        matrix = generator(weights, conductances, potential)
        pi = equilibrium(weights, potential)
        expected = weights * np.exp(-potential)
        np.testing.assert_allclose(pi, expected / expected.sum())
        np.testing.assert_allclose(equilibrium(weights), weights)
        np.testing.assert_allclose(matrix.sum(axis=0), 0, atol=1e-13)
        np.testing.assert_allclose(matrix @ pi, 0, atol=1e-13)
        np.testing.assert_allclose(matrix * pi, (matrix * pi).T, atol=1e-13)
        trajectory = evolve(matrix, [0, 2, 0], [0, .01, 1, 20])
        self.assertTrue(np.all(trajectory >= 0))
        np.testing.assert_allclose(trajectory.sum(axis=1), 2, atol=1e-12)
        np.testing.assert_allclose(trajectory[-1] / 2, pi, atol=1e-12)

    def test_constraint_adds_only_downhill_rates_and_opposes_neutral_drift(self):
        weights = [.2, .3, .5]
        conductances = [[0, 2, 0], [2, 0, 1], [0, 1, 0]]
        potential = np.array([2, 0, 1])
        neutral = generator(weights, conductances)
        constrained = generator(weights, conductances, potential)
        driver = constrained - neutral
        for source in range(3):
            for destination in range(3):
                if source != destination:
                    self.assertGreaterEqual(driver[destination, source], 0)
                    if potential[source] <= potential[destination]:
                        self.assertEqual(driver[destination, source], 0)
        pi = equilibrium(weights, potential)
        self.assertGreater(np.linalg.norm(neutral @ pi), .1)
        np.testing.assert_allclose(neutral @ pi, -(driver @ pi), atol=1e-13)

    def test_potential_shift_changes_neither_rates_nor_equilibrium(self):
        weights = [2., 3.]
        conductances = [[0, 4], [4, 0]]
        potential = np.array([2., -1.])
        np.testing.assert_allclose(generator(weights, conductances, potential),
                                   generator(weights, conductances, potential + 103))
        np.testing.assert_allclose(equilibrium(weights, potential), equilibrium(weights, potential + 103))

    def test_disconnected_components_block_global_equalization(self):
        matrix = generator([1, 1, 1], [[0, 1, 0], [1, 0, 0], [0, 0, 0]])
        pi = equilibrium([1, 1, 1])
        self.assertEqual(spectral_gap(matrix, pi), 0)
        result = evolve(matrix, [1, 0, 0], [30])[-1]
        np.testing.assert_allclose(result, [.5, .5, 0], atol=1e-12)
        self.assertGreater(relative_l2(result, pi), .5)

    def test_constraint_release_uses_actual_constrained_state(self):
        weights = [1, 1, 1]
        conductances = [[0, 1, 0], [1, 0, 1], [0, 1, 0]]
        neutral = generator(weights, conductances)
        constrained = generator(weights, conductances, [1, 0, 2])
        actual = evolve(constrained, [1, 0, 0], [.3])[-1]
        released = evolve(neutral, actual, [0, .1, 30])
        np.testing.assert_array_equal(released[0], actual)
        self.assertGreater(relative_l2(released[0], equilibrium(weights)), .1)
        self.assertGreater(np.linalg.norm(actual - equilibrium(weights, [1, 0, 2])), .01)
        np.testing.assert_allclose(released[-1], equilibrium(weights), atol=1e-12)

    def test_weighted_gap_bound_for_nonuniform_stationary_measure(self):
        weights = [.2, .3, .1, .4]
        conductances = [[0, 1, 0, 0], [1, 0, 2, 0], [0, 2, 0, 1], [0, 0, 1, 0]]
        potential = [0, 1, -.5, 2]
        matrix = generator(weights, conductances, potential)
        pi = equilibrium(weights, potential)
        gap = spectral_gap(matrix, pi)
        times = np.linspace(0, 4 / gap, 15)
        result = evolve(matrix, [1, 0, 0, 0], times)
        error = relative_l2(result, pi)
        self.assertTrue(np.all(error <= error[0] * np.exp(-gap * times) + 1e-12))

    def test_quantum_conservation_and_stationary_multinomial_moments(self):
        rng = np.random.default_rng(72618)
        total = 400
        replicates = 20000
        pi = equilibrium([1, 2, 3])
        matrix = generator([1, 2, 3], [[0, 1, 1], [1, 0, 1], [1, 1, 0]])
        # Start at stationarity, then use an actual nontrivial transition.
        initial = rng.multinomial(total, pi, size=replicates)
        final = advance_quanta(initial, transition_matrix(matrix, .4), rng)
        self.assertTrue(np.all(final >= 0))
        np.testing.assert_array_equal(final.sum(axis=1), np.full(replicates, total))
        expected_variance = total * pi * (1 - pi)
        mean_z = (final.mean(axis=0) - total * pi) / np.sqrt(expected_variance / replicates)
        self.assertLess(np.max(np.abs(mean_z)), 5)
        np.testing.assert_allclose(final.var(axis=0, ddof=1), expected_variance, rtol=.05)
        covariance = np.cov(final, rowvar=False)
        expected_covariance = total * (np.diag(pi) - np.outer(pi, pi))
        np.testing.assert_allclose(covariance, expected_covariance, atol=2)

    def test_quantum_transient_matches_independent_two_state_law(self):
        rng = np.random.default_rng(431)
        counts = np.tile([250, 0], (10000, 1))
        transition = transition_matrix(generator([2, 3], [[0, 6], [6, 0]]), .13)
        final = advance_quanta(counts, transition, rng)
        p = .4 + .6 * np.exp(-5 * .13)
        mean = 250 * p
        variance = 250 * p * (1 - p)
        self.assertLess(abs(final[:, 0].mean() - mean), 5 * np.sqrt(variance / len(final)))
        self.assertLess(abs(final[:, 0].var(ddof=1) / variance - 1), .06)
        np.testing.assert_array_equal(advance_quanta([3, 9], np.eye(2), rng), [3, 9])

    def test_invalid_inputs_rejected(self):
        for weights, conductances, potential in (
                ([0, 1], [[0, 1], [1, 0]], None),
                ([1, 1], [[0, 1], [2, 0]], None),
                ([1, 1], [[1, 1], [1, 0]], None),
                ([1, 1], [[0, -1], [-1, 0]], None),
                ([1, 1], [[0, 1], [1, 0]], [0, float("nan")]),
                ([1, 1], [[0, 1], [1, 0]], [0])):
            with self.assertRaises(ValueError):
                generator(weights, conductances, potential)
        with self.assertRaises(ValueError):
            transition_matrix([[-1, 1], [1, -1]], -1)
        with self.assertRaises(ValueError):
            spectral_gap([[-1, 1], [1, -1]], [.2, .8])
        with self.assertRaises(ValueError):
            evolve([[-1, 1], [1, -1]], [-1, 2], [1])
        with self.assertRaises(ValueError):
            advance_quanta([1.5, 2.5], np.eye(2), np.random.default_rng(1))


if __name__ == "__main__":
    unittest.main()
