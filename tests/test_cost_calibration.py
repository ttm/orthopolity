"""Synthetic numerical checks only; no archived measurements are fitted here."""
import copy
import json
import math
from pathlib import Path
import unittest
from unittest.mock import patch

import numpy as np
from scipy.integrate import quad

from orthopolity.cost_calibration import (
    fit_cost_curve, moment_predictions, predict_cost, summarize_calibration,
)


ROOT = Path(__file__).resolve().parents[1]


class CostCalibrationChecks(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((ROOT / "configs/ghedini_cost_calibration_2026-10-05.json").read_text())

    def synthetic_groups(self, *, A=3e-9, C=0., d=.8, beta=-.3):
        reference = math.sqrt(math.prod(self.config["diagnostic_domain_um3"]))
        groups = []
        for index, volume in enumerate((2., 6., 20., 80., 300., 729.)):
            for od in (.04, .12, .28, .4):
                rate = (A*(volume/reference)**d+C)*(od/.4)**beta
                groups.append(dict(species=f"synthetic_{index}", od=od, volume_um3=volume,
                                   mean_rate=rate, sd_rate=.05*rate, raw_count=4, usable_count=4))
        return groups

    def test_grouping_preserves_signed_zero_and_missing_readings(self):
        common = dict(species="test", optical_density=.4, volume_um3=10., cells_per_ul=2.)
        rows = [dict(common, source_row=i+2, oxygen_umol_per_min_per_cell=rate)
                for i, rate in enumerate((-3., 0., 6., None))]
        group = summarize_calibration(rows)[0]
        self.assertEqual((group["raw_count"], group["usable_count"], group["missing_count"]), (4, 3, 1))
        self.assertEqual(group["mean_rate"], 1.)
        self.assertAlmostEqual(group["sd_rate"], math.sqrt(21.))
        self.assertEqual((group["min_rate"], group["max_rate"]), (-3., 6.))
        self.assertEqual(group["source_rows"], [2, 3, 4, 5])
        self.assertEqual(group["missing_source_rows"], [5])
        self.assertEqual(group["mean_biovolume_um3_per_ul"], 20.)
        missing = summarize_calibration([rows[-1]])[0]
        self.assertIsNone(missing["mean_rate"])
        self.assertIsNone(missing["sd_rate"])
        self.assertEqual(missing["usable_source_rows"], [])

    def test_synthetic_power_and_additive_parameters_recovered(self):
        for model, C in (("power", 0.), ("additive", .8e-9)):
            for weighting in ("equal_groups", "species_rms"):
                with self.subTest(model=model, weighting=weighting):
                    groups = self.synthetic_groups(C=C)
                    result = fit_cost_curve(groups, model=model, weighting=weighting, config=self.config)
                    np.testing.assert_allclose([result["A"], result["d"], result["beta"]],
                                               [3e-9, .8, -.3], rtol=3e-5)
                    self.assertAlmostEqual(result["C"] / 1e-9, C / 1e-9, places=5)
                    self.assertLess(result["weighted_sse"], 1e-15)
                    self.assertFalse(result["bound_flags"]["technical"])
                    json.dumps(result, allow_nan=False)

    def test_nested_power_guarantees_no_larger_additive_loss(self):
        groups = self.synthetic_groups()
        for index, group in enumerate(groups):
            group["mean_rate"] += .1e-9*math.sin(index)
        groups[0]["mean_rate"] = -.1e-9
        power = fit_cost_curve(groups, model="power", config=self.config)
        additive = fit_cost_curve(groups, model="additive", config=self.config)
        self.assertLessEqual(additive["weighted_sse"], power["weighted_sse"])
        nested = [value for value in additive["starts"] if value.get("origin") == "nested_power"]
        self.assertEqual(len(nested), 1)
        self.assertEqual(nested[0]["weighted_sse"], power["weighted_sse"])
        self.assertEqual(nested[0]["solution"]["C"], 0.)
        volumes, ods = [g["volume_um3"] for g in groups], [g["od"] for g in groups]
        for fit in additive["near_optimal_candidates"]:
            residual = (predict_cost(fit, volumes, ods)-np.array([g["mean_rate"] for g in groups])) / 1e-9
            self.assertAlmostEqual(float(np.dot(residual, residual)), fit["weighted_sse"], places=9)
            self.assertLessEqual(fit["weighted_sse"], additive["weighted_sse"]*1.01+1e-12)

    def test_training_species_scales_and_equal_group_weights_ignore_row_counts(self):
        groups = self.synthetic_groups(C=.8e-9)
        training = [g for g in groups if g["od"] != .4]
        fit = fit_cost_curve(training, model="additive", weighting="species_rms", config=self.config)
        for species, scale in fit["training_scales"].items():
            values = [g for g in training if g["species"] == species]
            expected = math.sqrt(sum(g["mean_rate"]**2+g["sd_rate"]**2 for g in values)/len(values))
            self.assertAlmostEqual(scale/expected, 1.)
        changed = copy.deepcopy(training)
        for index, group in enumerate(changed):
            group["raw_count"] = group["usable_count"] = 10**(index % 5)
        repeat = fit_cost_curve(changed, model="additive", weighting="species_rms", config=self.config)
        self.assertEqual([fit[k] for k in ("A", "C", "d", "beta")],
                         [repeat[k] for k in ("A", "C", "d", "beta")])

    def test_separate_condition_fits_fix_beta_and_exclude_its_bounds(self):
        groups = [g for g in self.synthetic_groups(C=.8e-9) if g["od"] == .12]
        fit = fit_cost_curve(groups, model="additive", config=self.config, fit_density=False)
        self.assertEqual(fit["beta"], 0.)
        self.assertAlmostEqual(fit["d"], .8, places=5)
        self.assertTrue(all(not bound.startswith("beta:") for bound in fit["bound_flags"]["technical"]))
        with self.assertRaises(ValueError):
            fit_cost_curve(groups, config=self.config, fit_density=True)

    def test_power_moments_equal_exactly_and_additive_matches_size_quadrature(self):
        fit = dict(A=3e-9, C=0., d=1.2, beta=-.3, size_reference_um3=20., od_reference=.4)
        domain = [2., 100.]
        power = moment_predictions(fit, domain)
        self.assertEqual(power["m_S"], power["m_Q"])
        self.assertEqual(power["relative_gap"], 0.)
        fit["C"] = 2e-9
        actual = moment_predictions(fit, domain)
        def q(v):
            return 3.*(v/20.)**1.2+2.
        def derivative(v):
            return 3.*1.2*(v/20.)**.2/20.
        s = quad(lambda v: 1/q(v), *domain)[0] / quad(lambda v: 1/(v*q(v)), *domain)[0]
        qmoment = quad(lambda v: v*derivative(v)/q(v)**2, *domain)[0] / quad(lambda v: derivative(v)/q(v)**2, *domain)[0]
        np.testing.assert_allclose([actual["m_S"], actual["m_Q"]], [s, qmoment], rtol=1e-10)
        self.assertGreater(actual["m_Q"], actual["m_S"])

    def test_rate_units_and_volume_units_preserve_fit_shape_and_relative_gap(self):
        groups = self.synthetic_groups(C=.8e-9)
        baseline = fit_cost_curve(groups, model="additive", config=self.config)
        converted, config = copy.deepcopy(groups), copy.deepcopy(self.config)
        config["rate_scale_umol_min_cell"] *= 1e6
        config["diagnostic_domain_um3"] = [v*1e-3 for v in config["diagnostic_domain_um3"]]
        for group in converted:
            group["volume_um3"] *= 1e-3
            group["mean_rate"] *= 1e6
            group["sd_rate"] *= 1e6
        altered = fit_cost_curve(converted, model="additive", config=config)
        np.testing.assert_allclose([altered["A"] / 1e6, altered["C"] / 1e6, altered["d"], altered["beta"]],
                                   [baseline[k] for k in ("A", "C", "d", "beta")], rtol=2e-5)
        old = moment_predictions(baseline, self.config["diagnostic_domain_um3"])
        new = moment_predictions(altered, config["diagnostic_domain_um3"])
        np.testing.assert_allclose([new["m_S"]*1e3, new["m_Q"]*1e3, new["relative_gap"]],
                                   [old["m_S"], old["m_Q"], old["relative_gap"]], rtol=2e-5)

    def test_no_convergence_is_not_a_fit(self):
        with patch("orthopolity.cost_calibration.least_squares", side_effect=ValueError("synthetic failure")):
            with self.assertRaisesRegex(RuntimeError, "no optimization start converged"):
                fit_cost_curve(self.synthetic_groups(), config=self.config)

    def test_technical_degree_boundary_is_flagged_but_nested_zero_is_exempt(self):
        groups = self.synthetic_groups(d=5.)
        fit = fit_cost_curve(groups, model="power", config=self.config)
        self.assertIn("d:upper", fit["bound_flags"]["technical"])
        nested_fit = fit_cost_curve(self.synthetic_groups(), model="additive", config=self.config)
        nested = next(start["solution"] for start in nested_fit["starts"]
                      if start.get("origin") == "nested_power")
        self.assertTrue(nested["bound_flags"]["nested_zero_overhead"])
        self.assertFalse(nested["bound_flags"]["technical"])

    def test_validation_rejects_invalid_predictors_and_missing_means(self):
        fit = dict(A=3e-9, C=.8e-9, d=.8, beta=0., size_reference_um3=20., od_reference=.4)
        for volumes, ods in (([0., 2.], .4), ([1., math.nan], .4), ([1., 2.], 0.),
                             (["1", "2"], .4), ([True, False], .4)):
            with self.subTest(volumes=volumes, ods=ods), self.assertRaises(ValueError):
                predict_cost(fit, volumes, ods)
        for key, value in (("A", 0.), ("C", -1.), ("d", 0.), ("beta", math.inf)):
            with self.subTest(key=key), self.assertRaises(ValueError):
                predict_cost(dict(fit, **{key: value}), 10., .4)
        groups = self.synthetic_groups()
        groups[0]["mean_rate"] = None
        with self.assertRaises(ValueError):
            fit_cost_curve(groups, config=self.config)
        with self.assertRaises(ValueError):
            moment_predictions(fit, [10., 1.])


if __name__ == "__main__":
    unittest.main()
