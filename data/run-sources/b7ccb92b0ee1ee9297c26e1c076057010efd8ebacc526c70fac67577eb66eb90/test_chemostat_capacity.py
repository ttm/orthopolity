"""Synthetic checks only; real chemostat outcomes are not test fixtures."""
import importlib.util
from pathlib import Path
import unittest

import numpy as np

from orthopolity.chemostat_capacity import (nitrogen_share_segment, quota_calibration,
                                          ratio_intervals, redistribution_bound,
                                          segment_tv_range)


def runner():
    path = Path(__file__).resolve().parents[1]/"experiments/run_chemostat_capacity.py"
    spec = importlib.util.spec_from_file_location("capacity_runner", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestChemostatCapacity(unittest.TestCase):
    def test_constant_ratios_forbid_redistribution(self):
        bound = redistribution_bound([[2., 2.]]*3, [[7., 7.]]*3)
        self.assertEqual(bound["multiplier_span_upper"], 1.)
        self.assertEqual(bound["tv_upper"], 0.)

    def test_two_point_bound_is_sharp(self):
        for k in (1., 2., 9., 100.):
            initial = np.array([[1., 1.], [k, k]])
            bound = redistribution_bound(initial, initial)
            self.assertAlmostEqual(bound["multiplier_span_upper"], k)
            p = np.array([1., np.sqrt(k)])/(1.+np.sqrt(k))
            q = p/initial[:, 0]
            q /= q.sum()
            self.assertAlmostEqual(.5*np.abs(q-p).sum(), bound["tv_upper"])

    def test_price_changes_and_interval_uncertainty_are_bounded(self):
        rng = np.random.default_rng(4810)
        for _ in range(500):
            r0, rt = np.exp(rng.normal(size=(2, 4)))
            lo0, hi0 = r0*np.exp(-rng.random(4)), r0*np.exp(rng.random(4))
            lot, hit = rt*np.exp(-rng.random(4)), rt*np.exp(rng.random(4))
            bound = redistribution_bound(np.column_stack((lo0, hi0)), np.column_stack((lot, hit)))
            p = rng.dirichlet(np.ones(4))
            a0, b0, at, bt = np.exp(rng.normal(size=4))
            factor = (a0+b0*r0)/(at+bt*rt)
            q = p*factor
            q /= q.sum()
            self.assertLessEqual(.5*np.abs(q-p).sum(), bound["tv_upper"]+1e-12)

    def test_true_pool_ratio_and_shares_are_inside_envelopes(self):
        nitrogen, carbon = np.array([1., 2., 3., 8.]), np.array([3., 4., 15., 16.])
        intervals = ratio_intervals(nitrogen, carbon)
        endpoints = nitrogen_share_segment([2., 3., 4.], nitrogen)
        for mix in np.linspace(0, 1, 31):
            n = mix*nitrogen[2]+(1-mix)*nitrogen[3]
            c = mix*carbon[2]+(1-mix)*carbon[3]
            self.assertTrue(intervals[2, 0] <= c/n <= intervals[2, 1])
            stock = np.array([2.*nitrogen[0], 3.*nitrogen[1], 4.*n])
            shares = stock/stock.sum()
            value = segment_tv_range(endpoints, np.array([shares, shares]))
            self.assertLess(value["minimum"], 1e-10)

    def test_segment_minimum_can_be_interior(self):
        first = [[1., 0., 0.], [0., 1., 0.]]
        second = [[.5, .5, 0.], [.5, .5, 0.]]
        result = segment_tv_range(first, second)
        self.assertAlmostEqual(result["minimum"], 0.)
        self.assertAlmostEqual(result["maximum"], .5)
        self.assertAlmostEqual(result["minimizing_segment_positions"][0], .5)

    def test_disjoint_segments_have_known_distance(self):
        result = segment_tv_range([[1., 0., 0.], [0., 1., 0.]], [[0., 0., 1.]]*2)
        self.assertAlmostEqual(result["minimum"], 1.)
        self.assertAlmostEqual(result["maximum"], 1.)

    def test_dual_certificate_is_feasible_and_below_every_sampled_distance(self):
        rng = np.random.default_rng(9911)
        for _ in range(100):
            first, second = rng.dirichlet(np.ones(3), size=(2, 2))
            result = segment_tv_range(first, second)
            z = np.asarray(result["minimum_dual_vector"])
            self.assertTrue(np.all(np.abs(z) <= .5))
            d, a, b = first[0]-second[0], first[1]-first[0], -(second[1]-second[0])
            raw_lower = float(z@d+min(0., z@a)+min(0., z@b))
            self.assertLessEqual(result["minimum_lower_bound"], max(0., raw_lower)+1e-14)
            self.assertLessEqual(result["minimum_primal_dual_gap"], 1e-8)
            for u, v in rng.random((50, 2)):
                self.assertLessEqual(result["minimum_lower_bound"], .5*np.abs(d+u*a+v*b).sum()+1e-12)

    def test_invalid_inputs_fail_closed(self):
        for intervals in ([[0., 1.], [1., 1.]], [[2., 1.], [1., 1.]], [[np.nan, 1.]]*2):
            with self.assertRaises(ValueError):
                redistribution_bound(intervals, [[1., 1.]]*2)
        with self.assertRaises(ValueError):
            nitrogen_share_segment([0., 0., 0.], [1.]*4)
        with self.assertRaises(ValueError):
            segment_tv_range([[.3, .3], [.5, .5]], [[.5, .5]]*2)

    @staticmethod
    def synthetic_calibration():
        rows = []
        for index, species in enumerate(("Cr", "Ca", "Mo", "Co")):
            for time in (-4, 0, 1, 2, 3):
                rows.append({"Algae": species, "Time standardised to pulse [days]": time,
                             "N [pmol/cell]": 2.+max(time, 0), "C [pmol/cell]": 4.+2*max(time, 0),
                             "Cell volume [µm³]": 2., "source_row": len(rows)+2})
        return rows

    def test_calibration_uses_matching_days_and_preserves_source_rows(self):
        result = quota_calibration(self.synthetic_calibration())
        self.assertEqual(result["initial"]["nitrogen"], [1.]*4)
        self.assertEqual(result["final"][3]["nitrogen"], [2.5]*4)
        self.assertEqual(len(result["source_rows"]), 20)
        with self.assertRaises(ValueError):
            quota_calibration(self.synthetic_calibration()[:-1])
        with self.assertRaises(ValueError):
            quota_calibration(self.synthetic_calibration()+self.synthetic_calibration()[:1])

    def test_runner_preserves_missingness_and_detects_only_conditional_exceedance(self):
        records = []
        for category, vessel in (("Polycultures", "P"), ("Monocultures", "M")):
            for day in (0, 1, 2):
                records.append(dict(source_row=len(records)+2, category=category, chemostat=vessel,
                                    treatment="synthetic", decoded=True, time=day,
                                    biovolumes=[1., 0., 0.] if day == 0 else [0., 1., 0.]))
        config = dict(species=["Cr", "Ca", "Mo", "Co"], target_days=[1, 2, 3],
                      baseline_observation_day=0,
                      modes=["fixed_prepulse_densities", "measured_preliminary_density_changes"],
                      primary_category="Polycultures", secondary_category="Monocultures",
                      expected_main_records=6, expected_vessels_per_category=1,
                      primary_mode="measured_preliminary_density_changes", numerical_tolerance=1e-8,
                      run_id="synthetic", evidence_kind="synthetic", prior_exposure="synthetic",
                      interpretation_limit="synthetic")
        result = runner().analyse(config, quota_calibration(self.synthetic_calibration()), records)
        self.assertEqual(result["summary"]["primary"]["n_rows_exceeding"], 2)
        self.assertEqual(result["summary"]["primary"]["n_unscored"], 1)
        self.assertFalse(result["summary"]["statistical_rejection_claimed"])
        with self.assertRaises(ValueError):
            runner().analyse(config, quota_calibration(self.synthetic_calibration()), records+records[:1])


if __name__ == "__main__":
    unittest.main()
