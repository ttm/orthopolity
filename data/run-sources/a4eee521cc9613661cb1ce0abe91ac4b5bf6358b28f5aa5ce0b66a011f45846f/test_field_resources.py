import copy
import unittest

from orthopolity.field_resources import audit, analyse, evaluate_element, QUOTAS, SCHEMAS


def fixture():
    q = dict(Cruise_ID="NH1418", Station="1", Depth="5", Date="2014-09-20",
             Latitude="12", Longitude="-154")
    q.update({field: "2" for fields in QUOTAS.values() for field in fields.values()})
    b = dict(Cruise="NH1418", Station="1.0", Depth="5.0", ISO_DateTime_UTC="2014-09-20T03:00:00",
             Latitude="12", Longitude="-154", Prochlorococcus="100000", Synechococcus="50000",
             POC="1", PON="1", POP="1")
    return q, b


class FieldResourcesTest(unittest.TestCase):
    def test_units_and_feasible_world(self):
        q, b = fixture()
        r = evaluate_element(q, b, SCHEMAS["NH1418"], "C")
        self.assertAlmostEqual(r["partial_stock_uM"], .3)
        self.assertFalse(r["exceeds_bulk"])
        self.assertEqual(r["maximum_common_minimum_retention"], 1)
        self.assertEqual(r["minimum_symmetric_relative_allowance"], 0)

    def test_excess_world_and_rescaling(self):
        q, b = fixture()
        b["POC"] = ".1"
        r = evaluate_element(q, b, SCHEMAS["NH1418"], "C")
        self.assertAlmostEqual(r["partial_over_bulk"], 3)
        self.assertAlmostEqual(r["maximum_common_minimum_retention"], 1/3)
        self.assertAlmostEqual(r["minimum_symmetric_relative_allowance"], .5)
        q["Prochlorococcus_POC"], q["Synechococcus_POC"], b["POC"] = "20", "20", "1"
        changed = evaluate_element(q, b, SCHEMAS["NH1418"], "C")
        self.assertAlmostEqual(changed["partial_over_bulk"], r["partial_over_bulk"])

    def test_partial_missingness_and_all_missing(self):
        q, b = fixture()
        q["Prochlorococcus_POC"] = "nd"
        r = evaluate_element(q, b, SCHEMAS["NH1418"], "C")
        self.assertAlmostEqual(r["partial_stock_uM"], .1)
        self.assertEqual(r["omitted"][0]["quota_reason"], "missing")
        b["Synechococcus"] = "nd"
        r = evaluate_element(q, b, SCHEMAS["NH1418"], "C")
        self.assertEqual(r["status"], "unscored")
        self.assertIsNone(r["partial_stock_uM"])

    def test_zero_counts_and_invalid_bulk(self):
        q, b = fixture()
        b["Prochlorococcus"] = b["Synechococcus"] = "0"
        r = evaluate_element(q, b, SCHEMAS["NH1418"], "C")
        self.assertEqual(r["status"], "scored")
        self.assertEqual(r["partial_over_bulk"], 0)
        self.assertEqual(r["maximum_common_minimum_retention"], 1)
        b["POC"] = "0"
        self.assertEqual(evaluate_element(q, b, SCHEMAS["NH1418"], "C")["status"], "unscored")

    def test_invalid_terms_are_not_zero_imputations(self):
        q, b = fixture()
        q["Prochlorococcus_POC"], b["Synechococcus"] = "-1", "inf"
        r = evaluate_element(q, b, SCHEMAS["NH1418"], "C")
        self.assertEqual(r["status"], "unscored")
        self.assertEqual([r["quota_reason"] or r["count_reason"] for r in r["omitted"]],
                         ["nonpositive", "nonfinite"])

    def test_censored_or_unparseable_values_are_not_silently_converted(self):
        q, b = fixture()
        q["Prochlorococcus_POC"] = "<0.1"
        b["POC"] = "bad"
        r = evaluate_element(q, b, SCHEMAS["NH1418"], "C")
        self.assertEqual(r["omitted"][0]["quota_reason"], "unparseable")
        self.assertEqual(r["status"], "unscored")
        self.assertEqual(r["unscored_reason"], "unparseable")

    def test_metadata_only_does_not_inspect_responses(self):
        q, b = fixture()
        for key in (k for fields in QUOTAS.values() for k in fields.values()):
            q[key] = object()
        for key in ("POC", "PON", "POP", "Prochlorococcus", "Synechococcus"):
            b[key] = object()
        self.assertEqual(audit([q], {"829895": [b]})["records"][0]["status"], "primary")

    def test_textual_station_in_unqualified_cruise_is_retained(self):
        q, _ = fixture()
        q.update(Cruise_ID="NBPier", Station="Pier")
        self.assertEqual(audit([q], {})["records"][0]["status"], "no_qualified_bulk_source")

    def test_coordinate_boundary_and_date_offsets(self):
        q, b = fixture()
        b["Longitude"] = "-154.02"
        b["ISO_DateTime_UTC"] = "2014-09-21T03:00:00"
        self.assertEqual(audit([q], {"829895": [b]})["records"][0]["status"], "date_offset_sensitivity")
        b["Longitude"] = "-154.02001"
        self.assertEqual(audit([q], {"829895": [b]})["records"][0]["status"], "coordinate_discrepancy")
        b["Longitude"], b["ISO_DateTime_UTC"] = "-154", "2014-09-18T03:00:00"
        self.assertEqual(audit([q], {"829895": [b]})["records"][0]["status"], "date_discrepancy")

    def test_duplicate_identities_and_nearest_depth_rejected(self):
        q, b = fixture()
        self.assertEqual(audit([q, q], {"829895": [b]})["status_counts"], {"nonunique_quota_identity": 2})
        self.assertEqual(audit([q], {"829895": [b, b]})["status_counts"], {"nonunique_bulk_identity": 1})
        b["Depth"] = "5.01"
        self.assertEqual(audit([q], {"829895": [b]})["status_counts"], {"no_exact_station_depth": 1})

    def test_reused_bulk_is_quarantined(self):
        q, b = fixture()
        another = copy.deepcopy(q)
        another["Date"] = "2014-09-19"
        self.assertEqual(audit([q, another], {"829895": [b]})["status_counts"], {"reused_bulk_identity": 2})

    def test_atlantic_phosphorus_and_proxy_columns_never_used(self):
        q, _ = fixture()
        q["Cruise_ID"] = "AE1319"
        b = dict(cruise_id="AE1319", station="1", depth="5", date="2014-09-20",
                 lat="12", lon="-154", Pro="100000", Syn="50000", POC="1", PON="1", POP=object())
        config = dict(run_id="synthetic", coordinate_tolerance_degrees="0.02", expected_quota_rows={"primary": [2]})
        result = analyse([q], {"538091": [b]}, config)
        self.assertEqual([e["element"] for e in result["samples"][0]["elements"]], ["C", "N"])
        self.assertEqual(result["summaries"]["primary"]["scored_elements"], 2)

    def test_changed_qualification_stops_before_response(self):
        q, b = fixture()
        q["Prochlorococcus_POC"] = object()
        config = dict(run_id="synthetic", coordinate_tolerance_degrees="0.02", expected_quota_rows={"primary": []})
        with self.assertRaisesRegex(ValueError, "Changed pre-response qualification"):
            analyse([q], {"829895": [b]}, config)


if __name__ == "__main__":
    unittest.main()
