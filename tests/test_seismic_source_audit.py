"""Guard source joins against missing/duplicate identities and provenance confusion."""
import unittest
import gzip
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

from orthopolity.seismic_source_audit import positive_ids, source_times, crosswalk, read_nocal


def horus(ids, origin=False):
    frame = pd.DataFrame(dict(event_id=positive_ids(pd.Series(ids)), source_row=np.arange(len(ids))+2,
        Year=2009, Mo=1, Da=1, Ho=0, Mi=0, Se=0., Lat=42., Lon=13., Depth=5., event_type=''))
    if origin:
        frame = frame.assign(mt_source='TDMT', mt_mw=3., mt_error=.1, final_source='Mw TDMT', final_mw=3., final_error=.1)
    else:
        frame = frame.assign(Mw=3., sigMw=.1)
    return frame


def locations(class_ids, ingv_ids):
    return pd.DataFrame(dict(id_class=positive_ids(pd.Series(class_ids)),
        id_ingv=positive_ids(pd.Series(ingv_ids)), origintime='2009-01-01T00:00:00'))


class SourceAudit(unittest.TestCase):
    def test_nocal_prose_header_is_not_parsed_as_csv(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'catalog.gz'
            with gzip.open(path,'wt') as stream:
                stream.write('CATALOGUE\nA prose "quotation is not a CSV field\n\n')
                stream.write('1984 1 1 0 0 0.0 38.0 -121.0 -1.0 0.1 0.05 90 0.2 1.5 123\n')
                stream.write('1984 1 2 0 0 0.0 38.1 -121.1 2.0 -1 -1 -1 -1 1.6 124\n')
            rows=read_nocal(path)
            self.assertEqual(rows.event_id.tolist(),[123,124])
            self.assertEqual(rows.ev_95_km.tolist(),[.2,-1])
            self.assertEqual(rows.depth_km.iloc[0],-1)

    def test_zero_and_blank_ids_never_match_each_other(self):
        out = crosswalk(locations([1,2], [0,10]), horus([0,10]), horus([0,10], True))
        self.assertEqual(out.join_status.tolist(), ['missing_ingv_id','matched_catalogue_and_provenance'])
        self.assertTrue(pd.isna(out.horus_source_row.iloc[0]))

    def test_all_duplicate_ingv_occurrences_are_quarantined(self):
        out = crosswalk(locations([1,2,3], [10,10,20]), horus([10,20]), horus([10,20], True))
        self.assertEqual(len(out),3)
        self.assertEqual(out.join_status.tolist(), ['ambiguous_class_identifiers']*2+['matched_catalogue_and_provenance'])

    def test_repeated_class_id_with_different_ingv_ids_is_also_ambiguous(self):
        out = crosswalk(locations([1,1], [10,20]), horus([10,20]), horus([10,20], True))
        self.assertTrue(out.ambiguous_class_id.all())
        self.assertTrue(out.horus_mw.isna().all())

    def test_duplicate_horus_ids_do_not_expand_rows_or_keep_first(self):
        out = crosswalk(locations([1], [10]), horus([10,10]), horus([10], True))
        self.assertEqual(len(out),1)
        self.assertEqual(out.join_status.iloc[0], 'no_unique_horus_match')

    def test_missing_provenance_is_not_a_direct_magnitude(self):
        out = crosswalk(locations([1], [10]), horus([10]), horus([20], True))
        self.assertEqual(out.join_status.iloc[0], 'no_unique_provenance_match')
        self.assertFalse(out.has_direct_mt_provenance.iloc[0])

    def test_proxy_label_is_distinguished_even_when_mt_column_is_present(self):
        origin = horus([10],True).assign(final_source='Md,Ml')
        out = crosswalk(locations([1], [10]), horus([10]), origin)
        self.assertFalse(out.has_direct_mt_provenance.iloc[0])
        self.assertTrue(out.has_proxy_provenance.iloc[0])

    def test_invalid_clock_is_not_normalized_into_another_event(self):
        frame = horus([10,20,30])
        frame.loc[0,'Mi']=60
        frame.loc[1,'Se']=60
        times=source_times(frame)
        self.assertTrue(times.iloc[:2].isna().all())
        self.assertEqual(str(times.iloc[2]), '2009-01-01 00:00:00+00:00')

    def test_bad_numeric_identifiers_are_rejected(self):
        for values in [[1.5],[-1],[np.inf],['bad']]:
            with self.assertRaises(ValueError):
                positive_ids(pd.Series(values))


if __name__ == '__main__':
    unittest.main()
