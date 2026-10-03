import json
import unittest

import numpy as np

from orthopolity.plant_observation import calibrate_observation, rounded_expected_profile


class PlantObservationTests(unittest.TestCase):
    def test_exact_rounded_count_includes_boundary_cell_in_right_bin(self):
        # With a 0.01-g grid and a boundary at 0.03 g, the lower bin ends
        # at latent 0.025 g. The alpha=2 CDF gives (100-40)/(100-10)=2/3.
        profile = rounded_expected_profile([.01, .1], [.01, .03, .1], .01)
        np.testing.assert_allclose(profile["expected_count_shares"], [2/3, 1/3], atol=1e-13)
        self.assertAlmostEqual(sum(profile["normalized_expected_stock_shares"]), 1)
        self.assertAlmostEqual(sum(profile["unrounded_expected_count_shares"]), 1)
        self.assertGreater(profile["measurement_tv_from_unrounded_expected_stock"], .001)
        self.assertGreater(profile["expected_recorded_mass_per_object"], .01)
        self.assertLess(profile["expected_recorded_mass_per_object"], .1)

    def test_exact_fine_grid_rounding_effect_is_small_but_retained(self):
        edges = [.01, .01*np.sqrt(10), .1, .1*np.sqrt(10), 1., np.sqrt(10), 10., 10*np.sqrt(10), 100.]
        profile = rounded_expected_profile([.01, 100.], edges, .001)
        np.testing.assert_allclose(profile["unrounded_normalized_expected_stock_shares"], np.full(8, .125), atol=1e-13)
        self.assertGreater(profile["measurement_tv_from_unrounded_expected_stock"], .0001)
        self.assertLess(profile["measurement_tv_from_unrounded_expected_stock"], .002)
        self.assertAlmostEqual(sum(profile["expected_count_shares"]), 1, places=11)

    def test_one_object_share_expectation_is_count_probability_not_expected_stock(self):
        # For n=1 every normalized stock profile is one-hot. Its expectation
        # must equal bin COUNT probabilities, not normalized expected stocks.
        result = calibrate_observation({"domain": [.01, 1.], "sample_sizes": [1],
            "block_sizes": [1], "exponents": [2.0], "replicates": 2000,
            "null_reference_replicates": 100, "seed": 73})
        condition = result["conditions"][0]
        mean_shares = np.asarray(condition["summary"]["mean_normalized_census_stock_shares"])
        expectation = condition["rounded_expectation"]
        np.testing.assert_allclose(mean_shares, expectation["expected_count_shares"], atol=.035)
        self.assertGreater(condition["summary"]["normalization_bias_tv_from_rounded_expected_stock"], .4)
        shares = np.asarray(condition["raw"]["normalized_stock_shares"])
        np.testing.assert_array_equal(np.count_nonzero(shares, axis=1), np.ones(2000))
        self.assertEqual(condition["summary"]["any_empty_bin_frequency"], 1)
        self.assertEqual(result["ecological_neutrality_decision"], "unresolved")

    def test_replay_and_disjoint_condition_streams_are_order_independent(self):
        specification = {"domain": [.01, 10.], "sample_sizes": [40, 80],
            "block_sizes": [1, 5], "exponents": [2.0, 1.5],
            "replicates": 40, "null_reference_replicates": 50, "seed": 17}
        first = calibrate_observation(specification)
        self.assertEqual(first, calibrate_observation(specification))
        reversed_specification = {**specification, "sample_sizes": [80, 40],
                                 "block_sizes": [5, 1], "exponents": [1.5, 2.0]}
        reversed_result = calibrate_observation(reversed_specification)
        keyed = lambda result: {(row["n"], row["block_size"], row["exponent"]): row for row in result["conditions"]}
        self.assertEqual(keyed(first), keyed(reversed_result))
        reference = first["null_reference"][0]
        evaluation = first["conditions"][0]
        self.assertEqual(reference["seed_sequence_entropy"], [17, 40, 0])
        self.assertEqual(evaluation["seed_sequence_entropy"], [17, 40, 1, 200, 1])
        self.assertNotEqual(reference["raw"]["last_bin_share"][:40], evaluation["raw"]["last_bin_share"])
        # JSON forbids nonfinite numbers in this artifact.
        json.dumps(first, allow_nan=False)

    def test_perfect_blocks_inflate_realized_spread_and_iid_envelope_exceedance(self):
        result = calibrate_observation({"sample_sizes": [160], "block_sizes": [1, 20],
            "exponents": [2.0], "replicates": 300, "null_reference_replicates": 500,
            "seed": 616})
        iid, dependent = [row["summary"] for row in result["conditions"]]
        self.assertLess(iid["iid_envelope_exceedance_rate"], .12)
        self.assertGreater(dependent["iid_envelope_exceedance_rate"], .7)
        self.assertGreater(dependent["mean_realized_tv_from_log_neutral_template"],
                           iid["mean_realized_tv_from_log_neutral_template"]+.15)
        lo, hi = iid["iid_envelope_exceedance_wilson95"]
        self.assertLessEqual(lo, iid["iid_envelope_exceedance_rate"])
        self.assertGreaterEqual(hi, iid["iid_envelope_exceedance_rate"])

    def test_partial_final_cluster_keeps_declared_census_count(self):
        result = calibrate_observation({"domain": [.01, 1.], "sample_sizes": [21],
            "block_sizes": [20], "exponents": [2.0], "replicates": 20,
            "null_reference_replicates": 20})
        condition = result["conditions"][0]
        self.assertEqual(condition["independent_mass_draws_per_census"], 2)
        self.assertEqual(condition["last_block_size"], 1)
        shares = np.asarray(condition["raw"]["normalized_stock_shares"])
        np.testing.assert_allclose(shares.sum(axis=1), 1)
        self.assertTrue(np.all(np.count_nonzero(shares, axis=1) <= 2))

    def test_full_design_has_24_distinct_conditions_and_all_raw_statistics(self):
        result = calibrate_observation({"replicates": 20, "null_reference_replicates": 20})
        self.assertEqual(len(result["conditions"]), 24)
        self.assertEqual(len(result["null_reference"]), 4)
        entropies = {tuple(row["seed_sequence_entropy"]) for row in result["conditions"]}
        self.assertEqual(len(entropies), 24)
        for condition in result["conditions"]:
            raw = condition["raw"]
            self.assertEqual(len(raw["tv_from_log_neutral_template"]), 20)
            self.assertEqual(len(raw["any_empty_bin"]), 20)
            self.assertEqual(len(raw["last_bin_share"]), 20)
            shares = np.asarray(raw["normalized_stock_shares"])
            manual_tv = np.abs(shares-np.asarray(result["log_neutral_expected_stock_template"])).sum(axis=1)/2
            np.testing.assert_allclose(raw["tv_from_log_neutral_template"], manual_tv)

    def test_invalid_grid_and_colliding_stream_tags_are_rejected(self):
        for specification in ({"domain": [.0101, 100.]}, {"exponents": [1.5001]},
                              {"sample_sizes": [True]}, {"seed": -1},
                              {"replicates": 1}, {"block_sizes": [1, 1]},
                              {"undeclared": 1}):
            with self.subTest(specification=specification):
                with self.assertRaises(ValueError):
                    calibrate_observation(specification)


if __name__ == "__main__":
    unittest.main()
