import json
import unittest

import numpy as np
import pandas as pd

from orthopolity.seismic_qualification import (
    absolute_location_error, coordinates, qualify_cluster, scaling_range,
)


def synthetic_cluster(n=4000, dimensions=3, seed=72):
    rng = np.random.default_rng(seed)
    xyz = rng.uniform(0, 30, (n, 3))
    if dimensions == 2:
        xyz[:, 2] = 5
    # Below-floor events give an unambiguous MAXC; the complete cohort's
    # independent magnitudes are distributed across bins to preserve it.
    mag = 2 + np.arange(n) % 11 / 10
    mag[:n // 4] = 1
    return pd.DataFrame({
        "event_id": [f"event-{i:06}" for i in range(n)],
        "cluster": 7,
        "latitude": 34 + xyz[:, 1] / 111.195,
        "longitude": -117 + xyz[:, 0] / (111.195 * np.cos(np.radians(34))),
        "depth_km": xyz[:, 2],
        "mag": mag,
        "loc_err_km": 0.001,
    })


class SeismicQualification(unittest.TestCase):
    def test_errors_are_absolute_positive_and_in_kilometres(self):
        np.testing.assert_allclose(absolute_location_error([0.3, 3], [0.4, 4]), [0.5, 5])
        for bad in (0, -1, np.nan, np.inf):
            with self.assertRaises(ValueError):
                absolute_location_error(bad, 0.1)
            with self.assertRaises(ValueError):
                absolute_location_error(0.1, bad)

    def test_projection_matches_registered_formula(self):
        frame = pd.DataFrame({"latitude": [33, 35], "longitude": [-118, -116],
                              "depth_km": [2, 4]})
        expected = [[-111.195 * np.cos(np.radians(34)), -111.195, 2],
                    [111.195 * np.cos(np.radians(34)), 111.195, 4]]
        np.testing.assert_allclose(coordinates(frame), expected)

    def test_cap_is_independent_of_row_order_and_seed_changes_sample(self):
        frame = synthetic_cluster(5000)
        a = qualify_cluster(frame, np.random.SeedSequence([202610092, 7]))
        b = qualify_cluster(frame.sample(frac=1, random_state=14),
                            np.random.SeedSequence([202610092, 7]))
        c = qualify_cluster(frame, np.random.SeedSequence([202610092, 8]))
        self.assertEqual(a, b)
        self.assertEqual(a["n_sampled"], 3000)
        self.assertNotEqual(a["sampled_event_ids"], c["sampled_event_ids"])
        self.assertEqual(a["sampled_event_ids"], sorted(a["sampled_event_ids"]))
        self.assertEqual(len(set(a["sampled_event_ids"])), 3000)
        json.dumps(a, allow_nan=False)

    def test_invalid_errors_never_fall_back_to_zero_resolution(self):
        for bad in (np.nan, np.inf, 0, -0.1, "missing"):
            frame = synthetic_cluster(400)
            frame["loc_err_km"] = frame["loc_err_km"].astype(object)
            frame.loc[0, "loc_err_km"] = bad  # Even below Mc must be valid.
            result = qualify_cluster(frame, 1)
            self.assertFalse(result["eligible"])
            self.assertTrue(any("loc_err_km" in reason for reason in result["reasons"]))
            self.assertIsNone(result["mc"])
            json.dumps(result, allow_nan=False)

    def test_schema_ids_and_coordinates_have_explicit_rejections(self):
        cases = []
        frame = synthetic_cluster(400)
        cases.append((frame.drop(columns="loc_err_km"), "missing_columns"))
        frame = synthetic_cluster(400)
        frame.loc[1, "event_id"] = frame.loc[0, "event_id"]
        cases.append((frame, "duplicate_event_ids"))
        frame = synthetic_cluster(400)
        frame.loc[0, "latitude"] = 91
        cases.append((frame, "out_of_bounds_latitude"))
        frame = synthetic_cluster(400)
        frame.loc[0, "depth_km"] = np.nan
        cases.append((frame, "nonfinite_depth_km"))
        frame = synthetic_cluster(400)
        frame.loc[0, "cluster"] = 8
        cases.append((frame, "mixed_or_missing_cluster_ids"))
        for frame, reason in cases:
            result = qualify_cluster(frame, 1)
            self.assertFalse(result["eligible"])
            self.assertIn(reason, result["reasons"])

    def test_completeness_floor_and_inclusive_200_event_gate(self):
        frame = synthetic_cluster(400)
        frame["mag"] = 1.0
        frame.loc[200:, "mag"] = 2 + np.arange(200) % 11 / 10
        at_boundary = qualify_cluster(frame, 1)
        self.assertEqual(at_boundary["mc_maxcurv_plus02"], 1.2)
        self.assertEqual(at_boundary["mc"], 2)
        self.assertEqual(at_boundary["n_complete"], 200)
        self.assertNotIn("fewer_than_200_complete_events", at_boundary["reasons"])
        self.assertEqual(at_boundary["n_sampled"], 200)
        frame.loc[200, "mag"] = 1
        below_boundary = qualify_cluster(frame, 1)
        self.assertEqual(below_boundary["n_complete"], 199)
        self.assertEqual(below_boundary["reasons"], ["fewer_than_200_complete_events"])

    def test_maxcurv_can_raise_the_floor_and_ties_choose_lowest_bin(self):
        frame = synthetic_cluster(800)
        frame["mag"] = np.tile([2.5, 2.6, 2.7, 2.8], 200)
        result = qualify_cluster(frame, 1)
        self.assertAlmostEqual(result["mc"], 2.7)
        self.assertEqual(result["n_complete"], 400)

    def test_coincident_cloud_and_zero_pair_handling(self):
        frame = synthetic_cluster(400)
        frame[["latitude", "longitude", "depth_km"]] = [34, -117, 5]
        result = qualify_cluster(frame, 1)
        self.assertFalse(result["eligible"])
        self.assertEqual(result["reasons"], ["degenerate_geometry"])
        self.assertEqual(result["n_positive_pairs"], 0)
        self.assertEqual(result["n_unique_hypocentres_sampled"], 1)
        positive = np.r_[np.ones(200), np.full(1800, 40.)]
        a = scaling_range(positive, 0.01)
        b = scaling_range(np.r_[np.zeros(100), positive], 0.01)
        self.assertEqual(a["r_min_km"], b["r_min_km"])
        self.assertEqual(a["r_max_km"], b["r_max_km"])
        self.assertEqual(b["n_zero_pairs"], 100)

    def test_factor_three_gate_is_inclusive_with_fifteen_radii(self):
        pairs = np.r_[np.ones(200), np.full(1800, 30.)]
        result = scaling_range(pairs, 0.01)
        self.assertEqual(result["scaling_ratio"], 3)
        self.assertTrue(result["range_eligible"])
        self.assertEqual(len(result["radii_km"]), 15)
        self.assertEqual(result["radii_km"][0], 1)
        self.assertEqual(result["radii_km"][-1], 3)
        self.assertFalse(scaling_range(pairs, 0.34)["range_eligible"])
        for bad in (0, np.nan, np.inf):
            with self.assertRaises(ValueError):
                scaling_range(pairs, bad)

    def test_synthetic_plane_and_volume_resolve_without_fitting_exponents(self):
        for dimension in (2, 3):
            result = qualify_cluster(synthetic_cluster(4000, dimension), 42)
            self.assertTrue(result["eligible"], result["reasons"])
            self.assertGreaterEqual(result["scaling_ratio"], 3)
            self.assertEqual(result["n_complete"], 3000)
            self.assertFalse({"b", "D2", "slope", "verdict"} & set(result))
        frame = synthetic_cluster(4000)
        frame["loc_err_km"] = 1
        unresolved = qualify_cluster(frame, 42)
        self.assertEqual(unresolved["reasons"], ["scaling_range_too_short"])
        self.assertEqual(unresolved["error_floor_km"], 3)
        self.assertGreaterEqual(unresolved["geometry_only_ratio"], 3)
        self.assertLess(unresolved["scaling_ratio"], 3)


if __name__ == "__main__":
    unittest.main()
