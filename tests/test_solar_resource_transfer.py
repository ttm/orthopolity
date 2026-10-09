import csv
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from orthopolity.solar_resource_transfer import (
    RESOURCES, fixed_edges, pooled_edges, catalogue, monthly_statistics,
    aggregate, forecast, score, stratified_month_indices, bootstrap,
)


class SolarResourceTransferTests(unittest.TestCase):
    def test_reference_measure_changes_prediction_with_same_measured_cost(self):
        prediction = forecast([2, 8], [10, 30], np.array([1., 2., 8.]))
        np.testing.assert_allclose(prediction["log_resource_neutral"]["count_share"], [2/3, 1/3])
        np.testing.assert_allclose(prediction["log_resource_neutral"]["resource_share"], [1/3, 2/3])
        np.testing.assert_allclose(prediction["linear_resource_neutral"]["count_share"], [.4, .6])
        np.testing.assert_allclose(prediction["linear_resource_neutral"]["resource_share"], [1/7, 6/7])

    def test_neutral_shape_uses_costs_without_learning_abundance(self):
        first = forecast([2, 8], [10, 30], np.array([1., 2., 8.]))
        second = forecast([2, 8], [300, 2], np.array([1., 2., 8.]))
        self.assertEqual(first["log_resource_neutral"], second["log_resource_neutral"])
        self.assertEqual(first["linear_resource_neutral"], second["linear_resource_neutral"])
        self.assertNotEqual(first["historical_count_shape"], second["historical_count_shape"])

    def test_resource_unit_conversion_does_not_change_shape(self):
        first = forecast([2, 8], [10, 30], np.array([1., 2., 8.]))
        second = forecast([2000, 8000], [10, 30], np.array([1., 2., 8.]))
        for model in first:
            for profile in first[model]:
                np.testing.assert_allclose(first[model][profile], second[model][profile])

    def test_unsupported_cost_bin_is_not_imputed(self):
        with self.assertRaisesRegex(ValueError, "Each fixed training bin"):
            forecast([2, np.nan], [10, 0], np.array([1., 2., 8.]))

    def test_pooling_requires_both_resources_and_preserves_outer_domain(self):
        edges = np.array([1., 2., 4., 8., 16.])
        pooled = pooled_edges([[20, 20, 0, 4], [20, 20, 0, 9]], edges, 20)
        np.testing.assert_equal(pooled, [1, 2, 16])

    def test_lowest_undersupported_remainder_is_merged(self):
        pooled = pooled_edges([[1, 1, 11, 40]], np.array([1., 2., 4., 8., 16.]), 10)
        np.testing.assert_equal(pooled, [1, 8, 16])

    def test_pooling_cannot_create_evidence_from_one_supported_class(self):
        with self.assertRaisesRegex(ValueError, "Fewer than two"):
            pooled_edges([[1, 1, 10]], np.array([1., 2., 4., 8.]), 10)

    def test_zero_evaluation_bin_remains_in_score(self):
        predictions = forecast([1, 1], [1, 1], np.array([1., 2., 4.]))
        scores = score(predictions, {"counts": [20, 0], "resource_sums": [20, 0]})
        self.assertAlmostEqual(scores["log_resource_neutral"]["count_total_variation"], .5)
        self.assertAlmostEqual(scores["log_resource_neutral"]["resource_share_total_variation"], .5)

    def test_month_resampling_preserves_separate_training_years(self):
        stats = {"years": [2022, 2023]}
        indices = stratified_month_indices(stats, np.random.default_rng(7))
        self.assertEqual(len(indices), 24)
        self.assertTrue(np.all(indices[:12] < 12))
        self.assertTrue(np.all((indices[12:] >= 12) & (indices[12:] < 24)))

    def test_bootstrap_pairs_resources_and_is_reproducible(self):
        stats = {"months": [f"2024-{i:02d}" for i in range(1, 13)], "years": [2024],
                 "all_counts": np.tile([4, 2], (12, 1)), "counts": np.tile([4, 2], (12, 1)),
                 "resource_sums": np.tile([4., 8.], (12, 1))}
        training = {resource: stats for resource in RESOURCES}
        first = bootstrap(training, training, np.array([1., 2., 4.]), replicates=8, seed=7)
        second = bootstrap(training, training, np.array([1., 2., 4.]), replicates=8, seed=7)
        self.assertEqual(first[0], second[0])
        self.assertEqual(first[0][RESOURCES[0]], first[0][RESOURCES[1]])
        self.assertEqual(first[2], {resource: 0 for resource in RESOURCES})

    def test_catalogue_retains_boundary_missingness_and_exclusions(self):
        fieldnames = ["time", "start_time", "end_time", "flare_id", "xrsb_irrad",
                      "peak_saturated", "integrated_irrad_peak", "integrated_irrad_end"]
        default = dict(time="2024-01-01 00:02:00", start_time="2024-01-01 00:01:00",
                       end_time="2024-01-01 00:03:00", peak_saturated="0",
                       integrated_irrad_peak="1", integrated_irrad_end="2")
        rows = [dict(default, flare_id="a", xrsb_irrad="8"),
                dict(default, flare_id="b", xrsb_irrad="2", integrated_irrad_end=""),
                dict(default, flare_id="c", xrsb_irrad="2", peak_saturated="1"),
                dict(default, flare_id="d", xrsb_irrad="0.5")]
        with tempfile.TemporaryDirectory() as directory:
            with (Path(directory) / "noaa_2024.csv").open("w", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=fieldnames)
                writer.writeheader(); writer.writerows(rows)
            data = catalogue(directory, [2024], np.array([1., 2., 8.]))
        self.assertEqual(data[0]["bin"], 1)
        self.assertFalse(data[1]["valid_integrated_irrad_end"])
        self.assertEqual(data[2]["peak_selection"], "saturated_or_unknown")
        self.assertEqual(data[3]["peak_selection"], "outside_fixed_domain")
        rise = aggregate(monthly_statistics(data, RESOURCES[0], np.array([1., 2., 8.]), [2024]))
        end = aggregate(monthly_statistics(data, RESOURCES[1], np.array([1., 2., 8.]), [2024]))
        np.testing.assert_equal(rise["counts"], [0, 2])
        np.testing.assert_equal(end["counts"], [0, 1])

    def test_frozen_reference_detects_changed_input_bytes(self):
        path = Path(__file__).resolve().parents[1] / "experiments/run_solar_resource_transfer.py"
        spec = importlib.util.spec_from_file_location("solar_transfer_driver_test", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            file = root / "raw.csv"
            file.write_text("original")
            with patch.object(module, "ROOT", root):
                ref = module.reference(file)
                module.verify_references([ref])
                file.write_text("changed")
                with self.assertRaisesRegex(ValueError, "Frozen input changed"):
                    module.verify_references([ref])


if __name__ == "__main__":
    unittest.main()
