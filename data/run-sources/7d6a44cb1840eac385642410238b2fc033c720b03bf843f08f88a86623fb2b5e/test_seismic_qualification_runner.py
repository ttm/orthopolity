import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'experiments'))
spec = importlib.util.spec_from_file_location('seismic_qualification_runner', ROOT/'experiments/qualify_volumetric_seismicity.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def source(n=5):
    return pd.DataFrame(dict(event_id=np.arange(1, n+1), latitude=34., longitude=-117., depth_km=5.,
        mag=2.5, event_type='le', location_method='ct', abs_horizontal_error_km=.1,
        abs_vertical_error_km=.2, rel_horizontal_error_km=.001, rel_vertical_error_km=.002,
        waveform_cluster=3, waveform_cluster_size=n, relocation_box='box1'))


class SeismicQualificationRunner(unittest.TestCase):
    def test_source_join_requires_every_id_and_agreement(self):
        relocated = source()
        pub = relocated[['event_id', 'latitude', 'longitude', 'depth_km', 'mag']].copy()
        joined, difference = runner.join_sources(pub, relocated)
        self.assertEqual(len(joined), 5)
        self.assertEqual(set(difference.values()), {0.})
        with self.assertRaises(ValueError):
            runner.join_sources(pub, relocated.iloc[:-1])
        relocated.loc[0, 'depth_km'] += .01
        with self.assertRaises(ValueError):
            runner.join_sources(pub, relocated)

    def test_quality_keeps_all_rows_and_accepts_both_earthquake_codes(self):
        frame = source()
        frame['published_cluster'] = 1
        frame.loc[1, 'event_type'] = 'eq'
        frame.loc[2, 'location_method'] = '3d'
        frame.loc[3, 'abs_vertical_error_km'] = 0
        frame.loc[4, 'event_type'] = 're'
        frame.loc[4, 'abs_horizontal_error_km'] = 99
        table, reasons = runner.quality_table(frame)
        self.assertEqual(len(table), 5)
        self.assertEqual(table.quality_pass.tolist(), [True, True, False, False, False])
        self.assertIn('unusable_absolute_horizontal_error', table.iloc[4].quality_reasons)
        self.assertEqual(reasons['not_cross_correlation_relocated'], 1)
        self.assertAlmostEqual(table.iloc[0].loc_err_km, np.sqrt(.05))

    def test_necessary_count_gate_stops_before_any_estimator(self):
        frame = source()
        frame['published_cluster'] = 1
        frame['event_index'] = frame.event_id
        for field, value in [('year', 2000), ('month', 1), ('day', 1), ('hour', 0),
                             ('minute', 0), ('second', 0.), ('clock_fields_valid', True)]:
            frame[field] = value
        table, _ = runner.quality_table(frame)
        with tempfile.TemporaryDirectory() as directory:
            result = runner.analyse(table, Path(directory))
            ledger = pd.read_csv(Path(directory)/'cluster-ledger.csv')
        self.assertEqual(result['n_resolution_qualified_clusters'], 0)
        self.assertFalse(result['b_D2_or_regression_computed'])
        self.assertEqual(ledger.iloc[0].reason, 'fewer_than_200_raw_events')
        self.assertTrue(pd.isna(ledger.iloc[0].mc))


if __name__ == '__main__':
    unittest.main()
