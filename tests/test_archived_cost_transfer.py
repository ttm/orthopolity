import csv
import tempfile
import unittest
from pathlib import Path

import numpy as np

from orthopolity.archived_cost_transfer import (fit_models, numeric, predict,
                                               predictions, read_cultures, score_evaluation)


class ArchivedCostTransferTests(unittest.TestCase):
    def setUp(self):
        self.config = dict(training_temperatures_degC=[16, 18, 20, 22],
                           validation_temperatures_degC=[25, 27], strains=["a", "b"],
                           coordinate="Cell_Diameter_um", resources=["QC"],
                           models=["fixed_cubic", "pooled_free_power", "strain_geometric_mean", "strain_temperature_trend"])
        self.rows = [dict(culture_id=f"{s}:{t}", strain=s, temperature_degC=t, split="training",
                          diameter_um=(t-10)*(.2 if s == "a" else .4),
                          quotas={"QC": 2*((t-10)*(.2 if s == "a" else .4))**2.5})
                     for s in ["a", "b"] for t in [16, 18, 20, 22]]

    def test_missing_and_nonfinite(self):
        for v in ["", "N/A", "NaN", "NA"]:
            self.assertIsNone(numeric(v))
        with self.assertRaises(ValueError):
            numeric("inf")

    def test_validation_quotas_not_converted_during_training_or_prediction(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "source.csv"
            path.write_text("Rep,Temp,Strain,Cell_Diameter_um,QC\n1,16,a,2,3\n1,25,a,2,DO_NOT_PARSE\n")
            rows = read_cultures(path, self.config, view="training")
            self.assertEqual(rows[0]["quotas"]["QC"], 3.)
            self.assertIsNone(rows[1]["quotas"]["QC"])
            self.assertIsNone(read_cultures(path, self.config, view="predictors")[0]["quotas"]["QC"])
            with self.assertRaises(ValueError):
                read_cultures(path, self.config, view="evaluation")

    def test_duplicate_and_unspecified_temperature_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "source.csv"
            header = "Rep,Temp,Strain,Cell_Diameter_um,QC\n"
            path.write_text(header + "1,16,a,2,3\n1,16,a,2,4\n")
            with self.assertRaisesRegex(ValueError, "Duplicate"):
                read_cultures(path, self.config, view="training")
            path.write_text(header + "1,99,a,2,3\n")
            with self.assertRaisesRegex(ValueError, "Unspecified temperature"):
                read_cultures(path, self.config, view="training")

    def test_known_cost_degree_and_conditional_predictions(self):
        fitted = fit_models(self.rows, self.config)
        self.assertAlmostEqual(fitted["QC"]["models"]["pooled_free_power"]["coefficient"], 2.5)
        self.assertAlmostEqual(fitted["QC"]["diagnostics"]["within_strain_demeaned_cost_degree"], 2.5)
        row = dict(culture_id="held", strain="a", temperature_degC=25, split="validation", diameter_um=3)
        self.assertAlmostEqual(np.exp(predict(row, fitted["QC"], "pooled_free_power")), 2*3**2.5)
        self.assertEqual(len(predictions([row], fitted, self.config)), 1)

    def test_training_rejects_validation_membership(self):
        rows = [dict(self.rows[0], split="validation")]
        with self.assertRaisesRegex(ValueError, "only training"):
            fit_models(rows, self.config)

    def test_equal_cell_scoring_does_not_weight_extra_replicates(self):
        rows = [dict(culture_id="a1", strain="a", temperature_degC=25, split="validation", diameter_um=1, quotas={"QC": 1}),
                dict(culture_id="a2", strain="a", temperature_degC=25, split="validation", diameter_um=1, quotas={"QC": 1}),
                dict(culture_id="b1", strain="b", temperature_degC=25, split="validation", diameter_um=1, quotas={"QC": 1})]
        forecasts = [dict(culture_id=r["culture_id"], resource="QC",
                          predicted_log_quota={m: 0. if r["strain"] == "a" else 2. for m in self.config["models"]},
                          predicted_quota_fmol_per_cell={m: 1. if r["strain"] == "a" else np.exp(2.) for m in self.config["models"]}) for r in rows]
        scores = score_evaluation(rows, forecasts, self.config)["QC"]
        self.assertAlmostEqual(scores["models"]["fixed_cubic"]["equal_cell_mean_absolute_log_error"], 1.)
        self.assertEqual(scores["observed_cells"], 2)

    def test_missing_held_quota_excluded_in_every_model(self):
        fitted = fit_models(self.rows, self.config)
        rows = [dict(culture_id="held1", strain="a", temperature_degC=25, split="validation", diameter_um=3, quotas={"QC": 3}),
                dict(culture_id="held2", strain="b", temperature_degC=25, split="validation", diameter_um=3, quotas={"QC": None})]
        score = score_evaluation(rows, predictions(rows, fitted, self.config), self.config)["QC"]
        self.assertEqual(score["eligible_validation_rows"], 1)
        self.assertEqual(len(score["excluded"]), 1)


if __name__ == "__main__":
    unittest.main()
