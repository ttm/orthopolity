import copy
import math
import unittest

from orthopolity.paired_phosphorus import P_MOLAR_MASS, predict, qualify


class PhosphorusTest(unittest.TestCase):
    def test_measured_cost_recovers_independent_synthetic_count(self):
        # A different quota and stock change population in opposing directions.
        calibration = dict(observed_cells_ml=1000, tpp_uM=2, mean_p_fg=10, mean_volume_um3=1)
        target = dict(tpp_uM=1, mean_p_fg=2, mean_volume_um3=2)
        predictions = predict(calibration, target)
        self.assertEqual(predictions, dict(fixed_quota=500, volume_scaled_quota=250, measured_quota=2500))
        # Target counts and any quota derived from them are unavailable inputs.
        target["observed_cells_ml"] = object()
        self.assertEqual(predict(calibration, target), predictions)

    def test_prediction_respects_stock_and_cost_units(self):
        calibration = dict(observed_cells_ml=100, tpp_uM=3, mean_p_fg=7, mean_volume_um3=2)
        target = dict(tpp_uM=5, mean_p_fg=9, mean_volume_um3=3)
        expected = predict(calibration, target)
        for field in ("tpp_uM", "mean_p_fg", "mean_volume_um3"):
            first, second = copy.deepcopy(calibration), copy.deepcopy(target)
            first[field] *= 1e6
            second[field] *= 1e6
            for model, value in predict(first, second).items():
                self.assertTrue(math.isclose(value, expected[model]))
        # One micromole per litre is 10^6 femtomoles per millilitre.
        self.assertAlmostEqual(1 * P_MOLAR_MASS * 1e6 / P_MOLAR_MASS, 1e6)

    def cells(self):
        return [dict(SampleID=f"BIO5_EFB_EFB3_T2_B_{i}", exp="Low P", time="2", rep="b",
                     P_fg_cell="not parsed during qualification") for i in range(1, 21)]

    def bulk(self):
        return [dict(treatment="Low-P", day="2", bottle="b", cell=object(), TPP_value_uM=object())]

    def test_qualification_does_not_read_response_numbers(self):
        self.assertTrue(qualify(self.cells(), self.bulk())[0]["eligible"])

    def test_missing_or_ambiguous_cell_excludes_whole_sample(self):
        for change, reason in ((dict(P_fg_cell="NA"), "incomplete_phosphorus_assay"),
                               (dict(SampleID="BIO5_EFB_EFB2_T2_B_1"), "identifier_field_conflict"),
                               (dict(SampleID="BIO5_EFB_EFB3_T2_B_2"), "nonunique_cell_identifier")):
            cells = self.cells()
            cells[0].update(change)
            result = qualify(cells, self.bulk())[0]
            self.assertFalse(result["eligible"])
            self.assertIn(reason, result["exclusion_reasons"])

    def test_ambiguous_bulk_join_is_rejected(self):
        result = qualify(self.cells(), self.bulk() * 2)[0]
        self.assertIn("bulk_match_not_unique", result["exclusion_reasons"])


if __name__ == "__main__":
    unittest.main()
