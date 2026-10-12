import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))
from verify_paired_phosphorus import verify
from orthopolity.paired_phosphorus import analyse, P_MOLAR_MASS


class PhosphorusVerificationTest(unittest.TestCase):
    def test_decimal_verifier_rejects_changed_prediction(self):
        source = ROOT / "results/paired-phosphorus-pilot-2026-10-12"
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            (directory / "execution.json").write_bytes((source / "execution.json").read_bytes())
            result = json.loads((source / "result.json").read_text())
            result["targets"][0]["models"]["measured_quota"]["predicted_cells_ml"] *= 1.01
            (directory / "result.json").write_text(json.dumps(result))
            with self.assertRaisesRegex(ValueError, "Independent calculation mismatch"):
                verify(directory)

    def test_decimal_verifier_rejects_changed_accuracy_flag(self):
        source = ROOT / "results/paired-phosphorus-pilot-2026-10-12"
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            (directory / "execution.json").write_bytes((source / "execution.json").read_bytes())
            result = json.loads((source / "result.json").read_text())
            result["targets"][0]["models"]["measured_quota"]["within_pilot_factor"] = True
            (directory / "result.json").write_text(json.dumps(result))
            with self.assertRaisesRegex(ValueError, "Wrong pilot accuracy flag"):
                verify(directory)

    def test_complete_pipeline_ignores_quarantined_values_and_volumes(self):
        cells, bulk = [], []
        stock = 200 / (1e6 * P_MOLAR_MASS)
        for treatment, label, index, day, bottle, quota, count in (
                ("High-P", "High P", 1, 1, "c", 2, 100),
                ("Low-P", "Low P", 3, 2, "b", 4, 50),
                ("High-P", "High P", 1, 1, "a", "NA", "quarantined")):
            cells.extend(dict(SampleID=f"BIO5_EFB_EFB{index}_T{day}_{bottle.upper()}_{i}",
                              exp=label, time=str(day), rep=bottle, P_fg_cell=str(quota),
                              Volume_um3=object()) for i in range(1, 21))
            bulk.append(dict(treatment=treatment, day=str(day), bottle=bottle,
                             TPP_value_uM=str(stock), cell=str(count)))
        config = dict(run_id="synthetic", minimum_cells=20,
                      expected_eligible_keys=[["High-P", 1, "c"], ["Low-P", 2, "b"]],
                      calibration_key=["High-P", 1, "c"], pilot_factor=1.25)
        result = analyse(cells, bulk, config)
        target = result["targets"][0]
        self.assertAlmostEqual(target["models"]["measured_quota"]["predicted_cells_ml"], 50)
        self.assertTrue(target["measured_improves_on_fixed"])
        self.assertAlmostEqual(result["calibration"]["raw_predicted_over_observed"], 1)


if __name__ == "__main__":
    unittest.main()
