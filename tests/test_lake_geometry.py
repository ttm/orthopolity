import copy
import importlib.util
import struct
import unittest
from pathlib import Path

import numpy as np

from orthopolity.goodness_of_fit import fit_powerlaw, sample_powerlaw
from orthopolity.lake_geometry import polygon_moments, spatial_grid, unpack_gpkg


def rectangle(width, height, center=(0, 0)):
    points = np.array([[-width/2, -height/2], [width/2, -height/2],
                       [width/2, height/2], [-width/2, height/2],
                       [-width/2, -height/2]])
    return points + center


def geometry_blob(polygons, endian='<', envelope=False):
    order = 1 if endian == '<' else 0
    flags = order + (2 if envelope else 0)
    header = b'GP\x00' + bytes([flags]) + struct.pack(endian+'i', 27700)
    if envelope:
        points = np.concatenate([p[0] for p in polygons])
        header += struct.pack(endian+'4d', points[:, 0].min(), points[:, 0].max(),
                              points[:, 1].min(), points[:, 1].max())
    wkb = bytes([order]) + struct.pack(endian+'II', 6, len(polygons))
    for polygon in polygons:
        wkb += bytes([order]) + struct.pack(endian+'II', 3, len(polygon))
        for ring in polygon:
            wkb += struct.pack(endian+'I', len(ring))
            wkb += np.asarray(ring, dtype=endian+'f8').tobytes()
    return header + wkb


class LakeGeometryChecks(unittest.TestCase):
    def test_rectangle_moments_and_rigid_motion(self):
        ring = rectangle(2, 4)
        angle = 0.71
        rotation = np.array([[np.cos(angle), -np.sin(angle)],
                             [np.sin(angle), np.cos(angle)]])
        for points in (ring, ring[::-1], ring @ rotation + [430000, 610000]):
            result = polygon_moments([[points]])
            self.assertAlmostEqual(result['area_m2'], 8, places=8)
            self.assertAlmostEqual(result['rg_m']**2, 20/12, places=8)

    def test_scaling(self):
        first = polygon_moments([[rectangle(2, 4)]])
        scaled = polygon_moments([[rectangle(20, 40)]])
        self.assertAlmostEqual(scaled['area_m2']/first['area_m2'], 100)
        self.assertAlmostEqual(scaled['rg_m']/first['rg_m'], 10)

    def test_hole_subtraction_independent_of_orientation(self):
        outer, inner = rectangle(4, 4), rectangle(2, 2)
        for hole in (inner, inner[::-1]):
            result = polygon_moments([[outer, hole]])
            self.assertAlmostEqual(result['area_m2'], 12)
            self.assertAlmostEqual(result['rg_m']**2, 10/3)

    def test_separated_components_include_parallel_axis_term(self):
        result = polygon_moments([[rectangle(2, 2, (-5, 0))],
                                  [rectangle(2, 2, (5, 0))]])
        self.assertAlmostEqual(result['area_m2'], 8)
        self.assertAlmostEqual(result['centroid_e_m'], 0)
        self.assertAlmostEqual(result['centroid_n_m'], 0)
        self.assertAlmostEqual(result['rg_m']**2, 25+2/3)

    def test_binary_geometry_endianness_envelope_and_components(self):
        polygons = [[rectangle(4, 4), rectangle(2, 2)],
                    [rectangle(1, 1, (10, 10))]]
        for endian in ('<', '>'):
            for envelope in (False, True):
                recovered = unpack_gpkg(geometry_blob(polygons, endian, envelope))
                for p, q in zip(polygons, recovered):
                    for r, s in zip(p, q):
                        np.testing.assert_array_equal(r, s)

    def test_invalid_binary_and_open_geometry_rejected(self):
        blob = geometry_blob([[rectangle(2, 2)]])
        for bad in (blob[:-1], blob+b'\x00', b'', blob[:4]+struct.pack('<i', 4326)+blob[8:]):
            with self.assertRaises(ValueError):
                unpack_gpkg(bad)
        with self.assertRaises(ValueError):
            polygon_moments([[rectangle(2, 2)[:-1]]])
        with self.assertRaises(ValueError):
            polygon_moments([[rectangle(2, 2), rectangle(4, 4)]])

    def test_spatial_grid_origin_boundaries_and_missing_locations(self):
        xy = [[-1, 0], [0, 0], [99999, 100000], [100000, 100000]]
        np.testing.assert_array_equal(spatial_grid(xy), [[-1, 0], [0, 0], [0, 1], [1, 1]])
        with self.assertRaises(ValueError):
            spatial_grid([[np.nan, 0]])


class RegionalLakeStatistics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).resolve().parents[1] / 'experiments/run_uk_lake_gyration.py'
        spec = importlib.util.spec_from_file_location('uk_lake_run', path)
        cls.runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.runner)

    def test_bounded_estimator_recovers_both_simulated_worlds(self):
        rng = np.random.default_rng(711)
        for zeta in (2, 2.3):
            values = sample_powerlaw(30000, zeta+1, 1, 20, rng)
            estimate = fit_powerlaw(values, 1, 20)['params']['alpha']-1
            self.assertAlmostEqual(estimate, zeta, delta=0.06)

    def test_eligibility_and_interval_rules(self):
        decide = self.runner.exponent_decision
        self.assertEqual(decide([1.94, 2.06], [1.91, 2.09], 100, 10), 'supports H_territory')
        self.assertEqual(decide([2.2, 2.4], [1.8, 2.5], 100, 10), 'against H_territory')
        self.assertEqual(decide([1.8, 2.2], [1.7, 2.3], 100, 10), 'inconclusive')
        self.assertEqual(decide([1.94, 2.06], [1.91, 2.09], 99, 10), 'insufficient')
        self.assertEqual(decide([1.94, 2.06], [1.91, 2.09], 100, 9), 'insufficient')
        self.assertEqual(decide([1.94, 2.06], None, 100, 10), 'insufficient')

    def test_empty_radius_selection_is_insufficient(self):
        result = self.runner.analyse([0.2, 0.3], [[0, 0], [1, 1]])
        self.assertEqual(result['n_selected'], 0)
        self.assertEqual(result['exponent_verdict'], 'insufficient')

    def test_block_resampling_reflects_correlated_observations(self):
        config = copy.deepcopy(self.runner.CONFIG)
        config['analysis'].update(iid_bootstrap_draws=100, block_bootstrap_draws=100,
                                  gof_bootstrap_draws=20)
        radii = np.repeat(np.r_[np.full(10, 1.2), np.full(10, 3.0)], 100)
        xy = np.column_stack((np.repeat(np.arange(20)*100000+50000, 100),
                              np.zeros(2000)))
        result = self.runner.analyse(radii, xy, config)
        iid = np.diff(result['iid_ci95'])[0]
        block = np.diff(result['block_ci95'])[0]
        self.assertGreater(block, 2*iid)
        self.assertEqual(result['n_occupied_blocks'], 20)


if __name__ == '__main__':
    unittest.main()
