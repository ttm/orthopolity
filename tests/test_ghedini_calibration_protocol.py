"""Synthetic leakage and retention checks for the calibration-only gate."""
import copy
import importlib.util
import json
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "ghedini_calibration_runner", ROOT / "experiments/run_ghedini_cost_calibration.py")
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


class CalibrationProtocolChecks(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((ROOT / RUNNER.CONFIG).read_text())
        reference = math.sqrt(math.prod(self.config["diagnostic_domain_um3"]))
        self.groups = [dict(species=f"synthetic_{i}", volume_um3=volume, od=od,
                            mean_rate=(3e-9*(volume/reference)**.8+.4e-9)*(od/.4)**-.3,
                            sd_rate=.2e-9)
                       for i, volume in enumerate((2., 6., 20., 80., 300., 729.))
                       for od in (.04, .12, .28, .4)]

    def test_fold_membership_ignores_outcomes_and_flags_endpoint_species(self):
        baseline = RUNNER.make_folds(self.groups)
        changed = copy.deepcopy(self.groups)
        for group in changed:
            group["mean_rate"], group["sd_rate"] = -1e10, 1e12
        self.assertEqual(baseline, RUNNER.make_folds(changed))
        self.assertEqual(sum(f["extrapolation"] for f in baseline), 2)
        for fold in baseline:
            self.assertFalse(set(fold["training_ids"]) & set(fold["evaluation_ids"]))
            self.assertEqual(len(fold["training_ids"])+len(fold["evaluation_ids"]), 24)

    def test_species_and_condition_forecasts_ignore_heldout_means_and_sd(self):
        folds = RUNNER.make_folds(self.groups)
        for kind in ("species", "optical_density"):
            fold = next(f for f in folds if f["kind"] == kind)
            changed = copy.deepcopy(self.groups)
            for group in changed:
                if RUNNER.group_id(group) in fold["evaluation_ids"]:
                    group["mean_rate"], group["sd_rate"] = -1e10, 1e12
            for weighting in RUNNER.WEIGHTINGS:
                with self.subTest(kind=kind, weighting=weighting):
                    original = RUNNER.evaluate_fold(self.groups, fold, "additive", weighting, self.config)
                    altered = RUNNER.evaluate_fold(changed, fold, "additive", weighting, self.config)
                    self.assertEqual(original["fit"], altered["fit"])
                    self.assertEqual([p["predicted_rate"] for p in original["predictions"]],
                                     [p["predicted_rate"] for p in altered["predictions"]])
                    self.assertNotEqual(original["scores"], altered["scores"])

    def test_retained_outputs_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(RUNNER, "ROOT", Path(directory)):
            RUNNER.keep("retained/test.json", {"outcome": -1})
            RUNNER.keep("retained/test.json", {"outcome": -1})
            with self.assertRaisesRegex(ValueError, "Refusing to change"):
                RUNNER.keep("retained/test.json", {"outcome": 1})
            self.assertEqual(RUNNER.read("retained/test.json"), {"outcome": -1})

    def test_large_paired_gaps_do_not_qualify_overlapping_crossfit_ranges(self):
        scenarios = [dict(m_S=10., m_Q=20., relative_gap=1.),
                     dict(m_S=20., m_Q=40., relative_gap=1.)]
        paired, crossfit = RUNNER.moment_separation(scenarios, self.config["numerical_gate"])
        self.assertTrue(paired["passed"])
        self.assertFalse(crossfit["passed"])
        self.assertEqual(crossfit["value"], 0.)


if __name__ == "__main__":
    unittest.main()
