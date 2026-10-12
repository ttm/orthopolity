"""Independent verifier tests use explicit synthetic arithmetic, not field data."""
import copy
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))
from verify_field_resources import verify_records, decimal_value


def fixture():
    quota = dict(Cruise_ID="NH1418", Station="1", Depth="5", Date="2014-09-20",
                 Latitude="12", Longitude="-154", Prochlorococcus_POC="2",
                 Prochlorcoccus_PON="4", Prochlorococcus_POP="1",
                 Synechococcus_POC="3", Synechococcus_PON="6", Synechococcus_POP="0.5")
    bulk = dict(Cruise="NH1418", Station="1.0", Depth="5.0", ISO_DateTime_UTC="2014-09-20T03:00:00",
                Latitude="12", Longitude="-154", Prochlorococcus="100000", Synechococcus="50000",
                POC="1", PON=".35", POP="nd")
    match = dict(quota_row=2, cruise="NH1418", station="1", depth_m="5", quota_date="2014-09-20",
                 quota_lat="12", quota_lon="-154", status="primary", bulk_dataset="829895",
                 candidate_bulk_rows=[2], bulk_row=2, bulk_date="2014-09-20T03:00:00",
                 bulk_lat="12", bulk_lon="-154", date_offset_days=0,
                 latitude_difference_degrees="0", longitude_difference_degrees="0")
    qualification = dict(records=[match], status_counts={"primary": 1},
                         numerical_responses_examined=False, coordinate_tolerance_degrees="0.02")
    elements = []
    for element, q1, q2, s1, s2, stock, total in (
            ("C", 2, 3, .2, .15, .35, 1),
            ("N", 4, 6, .4, .3, .7, .35),
            ("P", 1, .5, .1, .025, .125, None)):
        terms = [dict(group="Prochlorococcus", quota_fmol_cell=q1, count_cells_ml=100000, stock_uM=s1),
                 dict(group="Synechococcus", quota_fmol_cell=q2, count_cells_ml=50000, stock_uM=s2)]
        elements.append(dict(element=element, terms=terms, omitted=[], bulk_uM=total,
                             partial_stock_uM=stock, status="scored" if total else "unscored",
                             unscored_reason=None if total else "missing"))
    elements[0].update(partial_over_bulk=.35, exceeds_bulk=False,
                       maximum_common_minimum_retention=1, minimum_symmetric_relative_allowance=0)
    elements[1].update(partial_over_bulk=2, exceeds_bulk=True,
                       maximum_common_minimum_retention=.5, minimum_symmetric_relative_allowance=1/3)
    full = dict(samples=1, stations=1, scored_elements=2, exceeding_elements=1, samples_with_excess=1,
                by_element={"C": {"scored": 1, "exceeding": 0}, "N": {"scored": 1, "exceeding": 1},
                            "P": {"scored": 0, "exceeding": 0}})
    empty = dict(samples=0, stations=0, scored_elements=0, exceeding_elements=0, samples_with_excess=0,
                 by_element={e: {"scored": 0, "exceeding": 0} for e in ("C", "N", "P")})
    result = dict(run_id="synthetic", qualification=copy.deepcopy(qualification),
                  samples=[dict(**match, elements=elements)],
                  summaries=dict(primary=full, date_offset_only=empty, combined_sensitivity=copy.deepcopy(full)))
    config = dict(run_id="synthetic", coordinate_tolerance_degrees="0.02", expected_quota_rows={"primary": [2]})
    return result, qualification, config, [quota], {"829895": [bulk]}


class FieldResourcesVerificationTest(unittest.TestCase):
    def test_explicit_synthetic_arithmetic_passes(self):
        checked = verify_records(*fixture())
        self.assertTrue(checked["verified"])
        self.assertEqual(checked["checked_elements"], 3)
        self.assertGreater(checked["independently_checked_numbers"], 20)

    def test_changed_stock_rejected(self):
        values = fixture()
        values[0]["samples"][0]["elements"][0]["partial_stock_uM"] *= 1.01
        with self.assertRaisesRegex(ValueError, "Independent calculation mismatch"):
            verify_records(*values)

    def test_changed_excess_flag_rejected(self):
        values = fixture()
        values[0]["samples"][0]["elements"][1]["exceeds_bulk"] = False
        with self.assertRaisesRegex(ValueError, "Changed categorical value"):
            verify_records(*values)

    def test_removed_group_rejected(self):
        values = fixture()
        values[0]["samples"][0]["elements"][0]["terms"].pop()
        with self.assertRaisesRegex(ValueError, "Changed list membership"):
            verify_records(*values)

    def test_changed_omission_reason_rejected(self):
        values = fixture()
        values[0]["samples"][0]["elements"][2]["unscored_reason"] = "no_valid_group"
        with self.assertRaisesRegex(ValueError, "Changed categorical value"):
            verify_records(*values)

    def test_changed_summary_rejected(self):
        values = fixture()
        values[0]["summaries"]["primary"]["by_element"]["N"]["exceeding"] = 0
        with self.assertRaisesRegex(ValueError, "Changed categorical value"):
            verify_records(*values)

    def test_changed_metadata_rejected(self):
        values = fixture()
        values[0]["samples"][0]["bulk_date"] = "2014-09-21T03:00:00"
        with self.assertRaisesRegex(ValueError, "Changed categorical value"):
            verify_records(*values)

    def test_changed_source_coordinates_rejected(self):
        values = fixture()
        values[4]["829895"][0]["Latitude"] = "12.03"
        with self.assertRaisesRegex(ValueError, "Bulk metadata mismatch"):
            verify_records(*values)

    def test_extra_bulk_candidate_rejected(self):
        values = fixture()
        values[4]["829895"].append(copy.deepcopy(values[4]["829895"][0]))
        with self.assertRaisesRegex(ValueError, "Nonunique selected bulk"):
            verify_records(*values)

    def test_decimal_parser_retains_distinct_invalid_reasons(self):
        self.assertEqual(decimal_value("<0.1"), (None, "unparseable"))
        self.assertEqual(decimal_value("inf"), (None, "nonfinite"))
        self.assertEqual(decimal_value("nd"), (None, "missing"))
        self.assertEqual(decimal_value("0"), (None, "nonpositive"))
        self.assertEqual(decimal_value("-1", count=True), (None, "negative"))


if __name__ == "__main__":
    unittest.main()
