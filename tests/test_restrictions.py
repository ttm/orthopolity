"""Optimization, feasibility, boundary, and prospective-response checks."""
import unittest

import numpy as np

from orthopolity.restrictions import proportional_fair_allocation, neutral_resource_projection


class RestrictionChecks(unittest.TestCase):
    def setUp(self):
        edges = np.geomspace(1, 64, 49)
        self.k = np.sqrt(edges[:-1] * edges[1:])
        self.w = np.diff(np.log(edges))
        self.q = np.vstack([self.k ** 2, self.k ** 3])

    def test_single_budget_has_analytic_equal_resource_solution(self):
        result = proportional_fair_allocation(self.q[:1], [3], self.w)
        np.testing.assert_allclose(self.q[0] * result["counts"], 3 * self.w / self.w.sum())
        self.assertLess(result["kkt_residual"], 1e-10)

    def test_two_active_budgets_and_independent_feasible_competitors(self):
        result = proportional_fair_allocation(self.q, [1, 8], self.w)
        np.testing.assert_allclose(result["resource_totals"], [1, 8], atol=1e-10)
        self.assertTrue(np.all(result["multipliers"] > 0))
        # Concavity plus KKT certify a global solution. Check independently
        # generated feasible allocations as an additional numerical safeguard.
        rng = np.random.default_rng(45)
        for _ in range(100):
            candidate = rng.lognormal(0, 2, len(self.k))
            candidate *= min(1 / (self.q[0] @ candidate), 8 / (self.q[1] @ candidate))
            self.assertLessEqual(float(self.w @ np.log(candidate)), result["objective"] + 1e-10)

    def test_severe_auxiliary_budget_leaves_primary_unused(self):
        result = proportional_fair_allocation(self.q, [1, 2], self.w)
        self.assertEqual(result["multipliers"][0], 0)
        self.assertLess(result["resource_totals"][0], .6)
        self.assertAlmostEqual(result["resource_totals"][1], 2)

    def test_more_than_two_budgets_and_redundant_constraint(self):
        # The third budget repeats the first and must not change the unique counts.
        result = proportional_fair_allocation(np.vstack([self.q, 2*self.q[0]]), [1, 8, 2], self.w)
        expected = proportional_fair_allocation(self.q, [1, 8], self.w)
        np.testing.assert_allclose(result["counts"], expected["counts"], rtol=1e-6)
        self.assertLess(result["kkt_residual"], 1e-7)

    def test_projection_neutral_active_boundary_and_infeasible(self):
        neutral = neutral_resource_projection(*self.q, 1, 20, self.w)
        np.testing.assert_allclose(neutral["probability"], self.w / self.w.sum())
        self.assertEqual(neutral["tilt_multiplier"], 0)
        active = neutral_resource_projection(*self.q, 1, 8, self.w)
        np.testing.assert_allclose(active["resource_totals"], [1, 8], atol=1e-10)
        self.assertGreater(active["tilt_multiplier"], 0)
        boundary = neutral_resource_projection(*self.q, 1, self.k[0], self.w)
        np.testing.assert_array_equal(boundary["probability"], np.eye(1, len(self.k))[0])
        self.assertIsNone(boundary["tilt_multiplier"])
        with self.assertRaisesRegex(ValueError, "infeasible"):
            neutral_resource_projection(*self.q, 1, .5, self.w)

    def test_intervention_log_ratio_is_predicted_from_changed_budget(self):
        before = neutral_resource_projection(*self.q, 1, 12, self.w)
        after = neutral_resource_projection(*self.q, 1, 8, self.w)
        log_ratio = np.log(after["probability"] / before["probability"])
        prediction = -(after["tilt_multiplier"] - before["tilt_multiplier"]) * self.k
        residual = log_ratio - prediction
        np.testing.assert_allclose(residual, residual[0], atol=2e-13)
        pf_before = proportional_fair_allocation(self.q, [1, 12], self.w)
        pf_after = proportional_fair_allocation(self.q, [1, 8], self.w)
        expected_ratio = (pf_before["multipliers"] @ self.q) / (pf_after["multipliers"] @ self.q)
        np.testing.assert_allclose(pf_after["counts"] / pf_before["counts"], expected_ratio)
        self.assertFalse(np.allclose(after["probability"], self.q[0]*pf_after["counts"],
                                     rtol=1e-4, atol=1e-6))

    def test_projection_primary_total_scaling_and_constant_cost_ratio(self):
        first = neutral_resource_projection(*self.q, 1, 8, self.w)
        doubled = neutral_resource_projection(*self.q, 2, 16, self.w)
        np.testing.assert_allclose(doubled["probability"], first["probability"])
        np.testing.assert_allclose(doubled["counts"], 2 * first["counts"])
        equal = neutral_resource_projection(self.q[0], 3*self.q[0], 1, 3, self.w)
        np.testing.assert_allclose(equal["probability"], self.w / self.w.sum())
        with self.assertRaises(ValueError):
            neutral_resource_projection(self.q[0], 3*self.q[0], 1, 2.99, self.w)

    def test_invalid_inputs(self):
        invalid = [
            lambda: proportional_fair_allocation([[1, 0]], [1]),
            lambda: proportional_fair_allocation([[1, 2]], [0]),
            lambda: proportional_fair_allocation([[1, 2]], [1], [1]),
            lambda: neutral_resource_projection([1, 2], [1], 1, 1),
            lambda: neutral_resource_projection([1], [1], 0, 1),
            lambda: neutral_resource_projection([1], [1], 1, np.nan),
        ]
        for call in invalid:
            with self.assertRaises(ValueError):
                call()


if __name__ == "__main__":
    unittest.main()
