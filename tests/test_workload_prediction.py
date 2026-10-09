"""Checks of whole-block replay, censoring and separated resource comparators."""
import unittest

import numpy as np

from orthopolity.workload_prediction import (
    budget_midpoints, calibration_profiles, forecast_largest, max_outcomes,
    outcome_profile, resample_profiles,
)


def calibration_rows():
    sizes = [1, 2, 4]
    memory = [[1, 10, 3], [10, 1, 3]]
    cpu = [[10, 1, 3], [1, 10, 3]]
    return [{"block_id": block, "size": size,
             "peak_rss_bytes": memory[block][index], "cpu_seconds": cpu[block][index],
             "numerical_valid": True, "status": "ok"}
            for block in range(2) for index, size in enumerate(sizes)]


class WorkloadPredictionChecks(unittest.TestCase):
    def setUp(self):
        self.sizes = [1, 2, 4]
        self.profile = calibration_profiles(calibration_rows(), self.sizes)

    def test_raw_cost_paths_retained_medians_projected_separately(self):
        np.testing.assert_array_equal(self.profile["memory_costs"], [[1, 10, 3], [10, 1, 3]])
        np.testing.assert_array_equal(self.profile["raw_median_memory_bytes"], [5.5, 5.5, 3])
        np.testing.assert_array_equal(self.profile["median_memory_bytes"], [5.5, 5.5, 5.5])
        self.assertEqual(self.profile["cost_nonmonotonicity"]["memory_blocks_with_decrease"], 2)

    def test_resource_independence_breaks_pairing_but_preserves_size_paths(self):
        joint = forecast_largest(self.profile, [2], [2])
        independent = forecast_largest(self.profile, [2], [2], mode="resource_independent")
        np.testing.assert_array_equal(joint["probability"], [1, 0, 0, 0])
        np.testing.assert_allclose(independent["probability"], [.5, .25, .25, 0])
        np.testing.assert_allclose(independent["survival_at_sizes"], [.5, .25, 0])
        np.testing.assert_allclose(independent["per_size_success_probability"], [.25, .25, 0])
        self.assertEqual(independent["replay_paths_per_budget"], 4)

    def test_largest_survival_accounts_for_failed_smaller_sizes(self):
        result = forecast_largest(self.profile, [3], [3])
        np.testing.assert_array_equal(result["probability"], [0, 0, 0, 1])
        np.testing.assert_array_equal(result["survival_at_sizes"], [1, 1, 1])
        np.testing.assert_array_equal(result["per_size_success_probability"], [0, 0, 1])
        self.assertEqual(result["upper_censor_probability"], 1)
        self.assertEqual(result["nonmonotonicity"]["success_path_fraction"], 1)
        # The deterministic monotone median comparator is a different model.
        median = forecast_largest(self.profile, [3], [3], mode="median")
        np.testing.assert_array_equal(median["probability"], [1, 0, 0, 0])

    def test_paired_budget_targets_pool_once_without_conditioning_on_success(self):
        result = forecast_largest(self.profile, [0, 3], [0, 3])
        np.testing.assert_array_equal(result["per_budget_probability"], [[1, 0, 0, 0], [0, 0, 0, 1]])
        np.testing.assert_array_equal(result["per_budget_survival_at_sizes"], [[0, 0, 0], [1, 1, 1]])
        np.testing.assert_allclose(result["probability"], [.5, 0, 0, .5])
        self.assertEqual(result["mean_largest_size"], 2)
        # Closing the inequalities at the exact budget is intentional.
        self.assertEqual(result["per_budget_upper_censor_probability"][1], 1)

    def test_single_resources_and_whole_block_resampling(self):
        for mode in ("memory_only", "cpu_only"):
            result = forecast_largest(self.profile, [2], [2], mode=mode)
            np.testing.assert_allclose(result["probability"], [0, .5, .5, 0])
        sampled = resample_profiles(self.profile, [1, 1, 0])
        np.testing.assert_array_equal(sampled["memory_costs"], [[10, 1, 3], [10, 1, 3], [1, 10, 3]])
        np.testing.assert_array_equal(sampled["cpu_costs"], [[1, 10, 3], [1, 10, 3], [10, 1, 3]])
        np.testing.assert_array_equal(sampled["median_memory_bytes"], [10, 10, 10])
        self.assertEqual(sampled["block_ids"], [1, 1, 0])

    def test_outcomes_and_profiles_keep_zero_and_upper_censor(self):
        outcomes = max_outcomes([[False, False, False], [False, True, False], [False, False, True]], self.sizes)
        np.testing.assert_array_equal(outcomes, [0, 2, 4])
        result = outcome_profile(outcomes, self.sizes)
        np.testing.assert_allclose(result["probability"], [1/3, 0, 1/3, 1/3])
        np.testing.assert_allclose(result["survival_at_sizes"], [2/3, 2/3, 1/3])
        self.assertAlmostEqual(result["upper_censor_probability"], 1/3)
        with self.assertRaises(ValueError):
            outcome_profile([3], self.sizes)
        with self.assertRaises(ValueError):
            max_outcomes([[0, np.nan, 1]], self.sizes)

    def test_calibration_rejects_incomplete_invalid_duplicate_and_nonfinite(self):
        rows = calibration_rows()
        invalid_sets = [rows[:-1], rows + [rows[0]], []]
        for field, value in [("numerical_valid", False), ("completed", False), ("status", "memory_limit"),
                             ("cpu_seconds", 0), ("peak_rss_bytes", np.inf), ("size", 3)]:
            modified = [dict(row) for row in rows]
            modified[0][field] = value
            invalid_sets.append(modified)
        for invalid in invalid_sets:
            with self.subTest(rows=invalid):
                with self.assertRaises(ValueError):
                    calibration_profiles(invalid, self.sizes)
        for sizes in ([2, 1, 4], [1, 1, 4], [1, 2.5, 4], [0, 1, 2]):
            with self.assertRaises(ValueError):
                calibration_profiles(rows, sizes)

    def test_budgets_midpoints_and_invalid_domains(self):
        np.testing.assert_allclose(budget_midpoints([10, 20, 40]), [8.5, 15, 30, 42])
        np.testing.assert_allclose(budget_midpoints([10, 10]), [8.5, 10, 10.5])
        for curve in ([10, 9], [0, 1], [1, np.nan]):
            with self.assertRaises(ValueError):
                budget_midpoints(curve)
        for memory, cpu in [([-1], [2]), ([np.inf], [2]), ([2], []), ([1, 2], [2])]:
            with self.assertRaises(ValueError):
                forecast_largest(self.profile, memory, cpu)
        for indices in ([2], [-1], [0.0], []):
            with self.assertRaises(ValueError):
                resample_profiles(self.profile, indices)

    def test_extra_validation_columns_cannot_enter_calibration_predictor(self):
        rows = calibration_rows()
        for row in rows:
            row["validation_peak_rss_bytes"] = 1000000
            row["validation_cpu_seconds"] = 1000000
        modified = calibration_profiles(rows, self.sizes)
        expected = forecast_largest(self.profile, [2], [2])
        actual = forecast_largest(modified, [2], [2])
        np.testing.assert_array_equal(actual["probability"], expected["probability"])

    def test_explicit_validation_or_other_split_rows_rejected(self):
        rows = calibration_rows()
        for split in ("validation", "training", None):
            modified = [dict(row, split="calibration") for row in rows]
            modified[-1]["split"] = split
            with self.assertRaises(ValueError):
                calibration_profiles(modified, self.sizes)
        calibration_profiles([dict(row, split="calibration") for row in rows], self.sizes)


if __name__ == "__main__":
    unittest.main()
