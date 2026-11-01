"""Small independently solvable reaction systems; no study-budget outcomes."""
import unittest

import numpy as np
from scipy.linalg import expm

from orthopolity.whole_object_kinetics import (
    COSTS, generator, generator_stationary, gillespie_endpoints, states_for_budget,
)


class WholeObjectKineticsTests(unittest.TestCase):
    def test_reachable_states_and_exact_resource_conservation(self):
        expected = [(0, 0, 1), (0, 2, 0), (2, 1, 0), (4, 0, 0)]
        np.testing.assert_array_equal(states_for_budget(4), expected)
        for budget in range(8):
            states, matrix = generator(budget)
            np.testing.assert_array_equal(states @ COSTS, np.full(len(states), budget))
            np.testing.assert_array_equal(matrix.sum(axis=0), np.zeros(len(states)))
            self.assertEqual(len(set(map(tuple, states))), len(states))

    def test_channel_two_state_law_and_column_orientation(self):
        states, matrix = generator(2, forward=(2, 7), reverse=(3, 5))
        np.testing.assert_array_equal(states, [[0, 1, 0], [2, 0, 0]])
        np.testing.assert_array_equal(matrix, [[-3, 2], [3, -2]])
        np.testing.assert_allclose(generator_stationary(matrix), [.4, .6])
        for time in (0., .01, .4, 2.):
            probability = expm(time * matrix) @ [0., 1.]
            dimer_probability = .4 * (1 - np.exp(-5 * time))
            np.testing.assert_allclose(probability, [dimer_probability, 1-dimer_probability])

    def test_mass_action_uses_falling_factorial_not_pair_combinations(self):
        _, matrix2 = generator(2, "mass_action", forward=(2, 7), reverse=(3, 5))
        _, matrix3 = generator(3, "mass_action", forward=(2, 7), reverse=(3, 5))
        np.testing.assert_array_equal(matrix2, [[-3, 4], [3, -4]])
        np.testing.assert_array_equal(matrix3, [[-3, 12], [3, -12]])
        np.testing.assert_allclose(generator_stationary(matrix2), [4/7, 3/7])
        np.testing.assert_allclose(generator_stationary(matrix3), [.8, .2])

    def test_second_reaction_has_whole_object_stoichiometry(self):
        states, matrix = generator(4, "mass_action", forward=(2, 7), reverse=(3, 5))
        index = {tuple(state): i for i, state in enumerate(states)}
        dimers, tetramer = index[(0, 2, 0)], index[(0, 0, 1)]
        self.assertEqual(matrix[tetramer, dimers], 14)
        self.assertEqual(matrix[dimers, tetramer], 5)

    def test_zero_budget_and_zero_duration(self):
        states, matrix = generator(0, "mass_action")
        np.testing.assert_array_equal(states, [[0, 0, 0]])
        np.testing.assert_array_equal(generator_stationary(matrix), [1.])
        final, events = gillespie_endpoints([0, 0, 0], 100., replicates=3)
        np.testing.assert_array_equal(final, np.zeros((3, 3), dtype=int))
        np.testing.assert_array_equal(events, [0, 0, 0])
        initial = np.array([[2, 0, 0], [0, 1, 0]])
        final, events = gillespie_endpoints(initial, 0.)
        np.testing.assert_array_equal(final, initial)
        np.testing.assert_array_equal(events, [0, 0])

    def test_gillespie_endpoints_match_independent_two_state_formula(self):
        size = 6000
        time = .23
        final, events = gillespie_endpoints(
            [3, 0, 0], time, "mass_action", forward=(.5, 1), reverse=(2, 1),
            replicates=size, rng=np.random.default_rng(83107))
        # Three monomers associate at rate .5*3*2=3; dissociation rate is 2.
        probability = .6 * (1 - np.exp(-5*time))
        measured = final[:, 1].mean()
        standard_error = np.sqrt(probability * (1-probability) / size)
        self.assertLess(abs(measured-probability), 6*standard_error)
        np.testing.assert_array_equal(final @ COSTS, np.full(size, 3))
        self.assertTrue(np.all(events >= 0))

    def test_per_replicate_initial_states_and_random_seed_replay(self):
        initial = np.array([[2, 0, 0], [0, 1, 0]] * 100)
        first = gillespie_endpoints(initial, .2, rng=np.random.default_rng(9203))
        second = gillespie_endpoints(initial, .2, rng=np.random.default_rng(9203))
        for actual, expected in zip(first, second):
            np.testing.assert_array_equal(actual, expected)
        np.testing.assert_array_equal(initial[:2], [[2, 0, 0], [0, 1, 0]])
        np.testing.assert_array_equal(first[0] @ COSTS, np.full(200, 2))

    def test_stationary_solver_rejects_invalid_or_nonunique_generators(self):
        invalid = [[], [1, 2], [[0, 1], [0, 0]], [[-1, -1], [1, 1]],
                   [[0, 0], [0, 0]], [[float("nan")]]]
        for matrix in invalid:
            with self.subTest(matrix=matrix), self.assertRaises(ValueError):
                generator_stationary(matrix)

    def test_rejects_invalid_budgets_and_rates(self):
        for budget in (-1, 2.5, True, np.bool_(False), float("nan"), 2**64):
            with self.subTest(budget=budget), self.assertRaises(ValueError):
                states_for_budget(budget)
        for rates in ((1,), (1, 2, 3), (0, 1), (-1, 1), (True, 1),
                      (np.nan, 1), (np.inf, 1), ("1", 1)):
            for argument in ("forward", "reverse"):
                with self.subTest(rates=rates, argument=argument), self.assertRaises(ValueError):
                    generator(2, **{argument: rates})
        with self.assertRaises(ValueError):
            generator(2, "unknown")

    def test_rejects_invalid_simulation_inputs_and_event_cap(self):
        cases = [dict(initial=[1, -1, 0]), dict(initial=[2., 0., 0.]),
                 dict(initial=[True, 0, 0]), dict(initial=[1, 0]),
                 dict(initial=[[2, 0, 0], [1, 0, 0]]), dict(replicates=0),
                 dict(initial=[[2, 0, 0]], replicates=2), dict(duration=-1),
                 dict(duration=np.inf), dict(duration=True), dict(rng=3),
                 dict(max_events=False)]
        for overrides in cases:
            kwargs = dict(initial=[2, 0, 0], duration=1.)
            kwargs.update(overrides)
            with self.subTest(overrides=overrides), self.assertRaises(ValueError):
                gillespie_endpoints(**kwargs)
        with self.assertRaises(RuntimeError):
            gillespie_endpoints([2, 0, 0], 100., max_events=1,
                                rng=np.random.default_rng(123))


if __name__ == "__main__":
    unittest.main()
