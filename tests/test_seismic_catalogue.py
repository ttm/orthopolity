import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from orthopolity.seismic_catalogue import load_published, load_relocations


PUBLISHED = (
    "1 1981 1 1 1 49 28.660 3301561 33.73430 -118.82670 1.870 2.27 NaN 1 1 0 1\n"
    "2 1981 1 1 4 13 55.710 3301565 33.25302 -115.96561 5.373 2.26 0.78128 0 1 1 1\n"
)
RELOCATED = (
    "1981 01 01 01 49 28.660 3301561 33.73430 -118.82670 1.870 2.27 "
    "21 31 0.22 0 162 56 135 14 0.700 2.200 99.000 99.000 le ct olr78\n"
    "1981 01 02 02 45 51.390 3301591 37.45050 -118.76667 1.550 2.08 "
    "6 61 0.83 0 323 0 0 0 22.000 25.600 99.000 99.000 re 3d\n"
)


class SeismicCatalogueParsing(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

    def parse(self, data, reader=load_published, name="catalogue.txt"):
        path = Path(self.temp.name) / name
        path.write_text(data, encoding="ascii")
        return reader(path)

    def test_published_membership_uses_event_index_and_preserves_root_nan(self):
        result = self.parse(PUBLISHED)
        self.assertEqual(result["event_id"].tolist(), [3301561, 3301565])
        self.assertEqual(result["published_cluster"].tolist(), [1, 1])
        self.assertTrue(np.isnan(result.loc[0, "log10_proximity"]))
        self.assertEqual(result.loc[1, "parent_index"], 1)
        self.assertEqual(result["source_line"].tolist(), [1, 2])
        self.assertTrue(result["mag_type"].isna().all())

    def test_relocated_and_ordinary_formats_preserve_all_error_fields(self):
        result = self.parse(RELOCATED, load_relocations)
        self.assertEqual(result["location_method"].tolist(), ["ct", "3d"])
        self.assertEqual(result.loc[0, "waveform_cluster"], 56)
        self.assertEqual(result.loc[0, "legacy_location_flag"], 162)
        self.assertEqual(result.loc[0, "abs_horizontal_error_km"], 0.7)
        self.assertEqual(result.loc[0, "abs_vertical_error_km"], 2.2)
        self.assertEqual(result.loc[0, "rel_horizontal_error_km"], 99)
        self.assertEqual(result.loc[1, "abs_horizontal_error_km"], 22)
        self.assertTrue(pd.isna(result.loc[1, "relocation_box"]))
        self.assertTrue(result["mag_type"].isna().all())

    def test_exact_id_join_does_not_use_row_order_or_cluster_number(self):
        published = self.parse(PUBLISHED)
        relocations = self.parse(RELOCATED, load_relocations)
        joined = published.merge(relocations, on="event_id", how="left",
                                 validate="one_to_one", suffixes=("_pub", "_rel"))
        self.assertEqual(joined.loc[0, "latitude_pub"], joined.loc[0, "latitude_rel"])
        self.assertTrue(pd.isna(joined.loc[1, "latitude_rel"]))

    def test_duplicate_ids_and_fractional_integer_tokens_rejected(self):
        for text in [PUBLISHED.replace("3301565", "3301561"),
                     PUBLISHED.replace("3301565", "3301565.0"),
                     PUBLISHED.replace("2 1981", "1 1981")]:
            with self.subTest(text=text), self.assertRaises(ValueError):
                self.parse(text)

    def test_broken_membership_and_flags_rejected(self):
        for text in [PUBLISHED.replace("0.78128 0 1 1 1", "0.78128 0 1 3 1"),
                     PUBLISHED.replace("0.78128 0 1 1 1", "0.78128 0 1 1 3"),
                     PUBLISHED.replace("0.78128 0 1 1 1", "0.78128 2 1 1 1"),
                     PUBLISHED.replace("NaN 1 1 0 1", "NaN 0 1 0 1")]:
            with self.subTest(text=text), self.assertRaises(ValueError):
                self.parse(text)

    def test_malformed_numeric_coordinate_and_calendar_rejected(self):
        for text in [PUBLISHED.replace("33.73430", "nan"),
                     PUBLISHED.replace("33.73430", "91"),
                     PUBLISHED.replace("2.27", "inf"),
                     PUBLISHED.replace("1981 1 1", "1981 2 30")]:
            with self.subTest(text=text), self.assertRaises(ValueError):
                self.parse(text)

    def test_missing_extra_and_unfinished_inputs_rejected(self):
        for text in ["", PUBLISHED + "\n", PUBLISHED + "broken line\n",
                     PUBLISHED.replace("0.78128 0 1 1 1", "0.78128 0 1 1")]:
            with self.subTest(text=text), self.assertRaises(ValueError):
                self.parse(text)
        with self.assertRaises(ValueError):
            self.parse(PUBLISHED, name="catalogue.txt.part")
        with self.assertRaises(ValueError):
            self.parse(RELOCATED.replace(" ct olr78", " gc olr78"), load_relocations)
        with self.assertRaises(ValueError):
            self.parse(RELOCATED.replace(" ct olr78", " ct"), load_relocations)

    def test_quality_flags_and_sentinels_are_not_eligibility_cuts(self):
        result = self.parse(RELOCATED.replace("le ct", "eq ct").replace(
            "0.700 2.200", "0.000 -1.000"), load_relocations)
        self.assertEqual(len(result), 2)
        self.assertEqual(result.loc[0, "event_type"], "eq")
        self.assertEqual(result.loc[0, "abs_horizontal_error_km"], 0)
        self.assertEqual(result.loc[0, "abs_vertical_error_km"], -1)

    def test_overflow_clock_fields_are_reported_without_changing_source(self):
        result = self.parse(PUBLISHED.replace("1 49 28.660", "1 60 1.180"))
        self.assertEqual(result.loc[0, "minute"], 60)
        self.assertEqual(result.loc[0, "second"], 1.180)
        self.assertFalse(result.loc[0, "clock_fields_valid"])
        self.assertTrue(result.loc[1, "clock_fields_valid"])


if __name__ == "__main__":
    unittest.main()
