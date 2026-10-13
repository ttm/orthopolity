"""Synthetic numerical checks for the independently written verifier."""
import importlib.util
from pathlib import Path
import copy
import sys

import numpy as np
import unittest


PATH = Path(__file__).resolve().parents[1] / "experiments" / "verify_cantilever.py"
SPEC = importlib.util.spec_from_file_location("verify_cantilever", PATH)
VERIFIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER)


class CantileverVerificationTest(unittest.TestCase):
    @staticmethod
    def synthetic_replay():
        # The verifier does not import production code. This integration test
        # supplies invented measurements to both independently written paths.
        root = PATH.parents[1]
        spec = importlib.util.spec_from_file_location("cantilever_runner_for_verification_test", root / "experiments/run_cantilever.py")
        runner = importlib.util.module_from_spec(spec)
        prior_path = sys.path[:]
        try:
            sys.path.insert(0, str(root / "experiments"))
            spec.loader.exec_module(runner)
        finally:
            sys.path[:] = prior_path
        config = dict(analyses=[dict(name="primary", t0_K=300, all_phi=False, publisher_mask=False)],
                      modes={"C30": {"flexural": [1], "torsional": [1]},
                             "C30C": {"flexural": [1], "torsional": [1]}}, quadrature_order=256)
        archive = {}
        for sample, count in (("C30", 11), ("C30C", 7)):
            temperature = np.linspace(300, 480, count)
            delta = 2 * (temperature - 300)
            data = dict(AVG_TAVG=temperature, AVG_TAVG_ERR=np.full(count, 3.0), AVG_TMAX=300 + delta)
            for prefix in ("D", "T"):
                data[f"AVG_{prefix}_PHI"] = (1e-5 + 2e-8 * delta + 1e-10 * delta ** 2)[:, None]
                data[f"AVG_{prefix}_PHI_ERR"] = np.full((count, 1), 1e-6)
                data[f"AVG_{prefix}_TFLUC"] = (300 + 0.31 * delta)[:, None]
                data[f"AVG_{prefix}_TFLUC_ERR"] = np.full((count, 1), 8.0)
            archive[sample] = data
        sealed = runner.forecast(archive, config)
        result = runner.evaluate(sealed, archive)
        return result, config, archive, sealed

    def test_torsional_integral_has_analytic_first_moment(self):
        for number in (1, 2, 3):
            moments = VERIFIER.independent_moments("torsional", number)
            self.assertAlmostEqual(moments[0], 1, delta=1e-12)
            self.assertAlmostEqual(moments[1], 0.5 - 2 / ((2 * number - 1) * np.pi) ** 2, delta=1e-12)


    def test_qr_recovers_loss_law_and_ignores_invalid_rows(self):
        delta = np.array([0, 20, 40, 70, 110, 140.0])
        coefficient = np.array([1e-5, -2e-8, 4e-10])
        phi = np.polynomial.polynomial.polyval(delta, coefficient)
        phi[-1] = np.nan
        recovered, valid = VERIFIER.independent_fit(delta, phi, np.full(len(delta), 1e-7))
        np.testing.assert_allclose(recovered, coefficient, rtol=1e-12)
        assert valid.tolist() == [True, True, True, True, True, False]


    def test_direct_spatial_prediction_uniform_loss(self):
        for kind, number in (("flexural", 1), ("flexural", 5), ("torsional", 1)):
            moments = VERIFIER.independent_moments(kind, number)
            output = VERIFIER.independent_prediction(kind, number, [3e-5, 0, 0], 250, 300)
            self.assertAlmostEqual(output["phi"], 3e-5, delta=3e-16)
            self.assertAlmostEqual(output["temperature"], 300 + 250 * moments[1], delta=1e-9)


    def test_global_positive_loss_can_hide_local_negative_vertex(self):
        moments = VERIFIER.independent_moments("torsional", 1)
        local_coefficient = np.array([0.24, -1.0, 1.0])
        global_coefficient = local_coefficient * np.array([1.0, moments[1], moments[2]])
        assert np.polynomial.polynomial.polyval(1.0, global_coefficient) > 0
        gate = VERIFIER.independent_loss_minimum(global_coefficient, moments, 1.0)
        assert not gate["nonnegative"]
        self.assertAlmostEqual(gate["minimum"], -0.01)
        self.assertAlmostEqual(gate["minimum_at_delta"], 0.5)


    def test_integrated_nonuniform_loss_matches_known_moment_expression(self):
        moments = VERIFIER.independent_moments("flexural", 3)
        a, b, c = (2e-5, 1e-7, 3e-10)
        delta = 430
        expected = 300 + delta * (a * moments[1] + b * delta * moments[2] / moments[1]
                                  + c * delta ** 2 * moments[3] / moments[2]) / (a + b * delta + c * delta ** 2)
        actual = VERIFIER.independent_prediction("flexural", 3, [a, b, c], delta, 300)
        self.assertAlmostEqual(actual["temperature"], expected, delta=1e-8)

    def test_full_synthetic_replay(self):
        result, config, archive, sealed = self.synthetic_replay()
        verified = VERIFIER.verify_records(result, config, archive, sealed)
        self.assertTrue(verified["verified"])
        self.assertEqual(verified["checked_analysis_modes"], 4)
        self.assertEqual(verified["checked_analysis_targets"], 10)

    def test_replay_detects_score_and_membership_tampering(self):
        result, config, archive, sealed = self.synthetic_replay()
        changed = copy.deepcopy(result)
        changed["analyses"][0]["summary"]["scores"]["absolute_error_K"]["equal_preparation_mean"] += 1
        with self.assertRaises(ValueError):
            VERIFIER.verify_records(changed, config, archive, sealed)
        changed = copy.deepcopy(result)
        changed["analyses"][0]["cases"][0]["train_rows"][0] = 9
        with self.assertRaises(ValueError):
            VERIFIER.verify_records(changed, config, archive, sealed)
