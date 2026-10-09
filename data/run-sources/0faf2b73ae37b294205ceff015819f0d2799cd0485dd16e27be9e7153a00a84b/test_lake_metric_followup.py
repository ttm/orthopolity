import unittest
import numpy as np

from orthopolity.geodesic_lake_geometry import BasinIndex, local_geometry, signed_ring_moments
from orthopolity.goodness_of_fit import fit_powerlaw, sample_powerlaw
from orthopolity.lake_followup_statistics import decision, fit_mean_log, intervals


def rectangle(width, height, center=(0, 0)):
    return np.array([[-width/2, -height/2], [-width/2, height/2],
                     [width/2, height/2], [width/2, -height/2],
                     [-width/2, -height/2]]) + center


class LocalLakeGeometry(unittest.TestCase):
    def test_holes_and_components_analytic(self):
        result = signed_ring_moments([rectangle(4, 4), rectangle(2, 2)[::-1]])
        self.assertAlmostEqual(result['full']['area_m2'], 12)
        self.assertAlmostEqual(result['full']['rg_m']**2, 10/3)
        result = signed_ring_moments([rectangle(2, 2, (-5, 0)), rectangle(2, 2, (5, 0))])
        self.assertAlmostEqual(result['full']['rg_m']**2, 25+2/3)
        self.assertAlmostEqual(result['largest']['rg_m']**2, 2/3)

    def test_invalid_winding_and_ring_rejected(self):
        for rings in ([rectangle(2, 2)[::-1]], [rectangle(2, 2)[:-1]],
                      [rectangle(2, 2), rectangle(4, 4)[::-1]]):
            with self.assertRaises(ValueError):
                signed_ring_moments(rings)

    def test_geodesic_disk_at_equator_pole_and_dateline(self):
        from pyproj import Geod
        geod = Geod(ellps='WGS84')
        for lon, lat in [(0, 0), (179.99, 40), (-120, 89.99)]:
            angles = np.linspace(0, 360, 361)
            lons, lats, _ = geod.fwd(np.full(len(angles), lon), np.full(len(angles), lat),
                                     angles, np.full(len(angles), 10000.))
            pts = np.column_stack((lons, lats))
            pts[-1] = pts[0]
            result = local_geometry(pts, [0], check_topology=True)
            self.assertAlmostEqual(result['rg_laea_km'], 10/np.sqrt(2), delta=.001)
            self.assertAlmostEqual(result['rg_aeqd_km']/result['rg_laea_km'], 1, delta=1e-5)
            self.assertAlmostEqual(result['area_laea_km2']/result['area_geodesic_km2'], 1, delta=1e-5)
            self.assertTrue(result['topology_valid'])

    def test_aeqd_matches_proj_on_irregular_polygon(self):
        from pyproj import Proj
        pts = np.array([[179.9, 60], [179.9, 60.2], [-179.8, 60.25],
                        [-179.7, 60], [179.9, 60]])
        result = local_geometry(pts, [0])
        proj = Proj(proj='aeqd', lon_0=pts[0, 0], lat_0=pts[0, 1], ellps='WGS84')
        reference = signed_ring_moments([np.column_stack(proj(pts[:, 0], pts[:, 1]))])
        self.assertAlmostEqual(result['rg_aeqd_km'], reference['full']['rg_m']/1000, places=9)

    def test_local_hole_and_separate_components(self):
        from pyproj import Proj
        proj = Proj(proj='laea', lon_0=20, lat_0=70, ellps='WGS84')
        rings = [rectangle(10000, 10000), rectangle(2000, 2000)[::-1], rectangle(4000, 4000, (15000, 0))]
        pts = np.concatenate([np.column_stack(proj(r[:, 0], r[:, 1], inverse=True)) for r in rings])
        result = local_geometry(pts, [0, 5, 10], check_topology=True)
        expected = signed_ring_moments(rings)
        self.assertEqual(result['n_shells'], 2)
        self.assertEqual(result['n_holes'], 1)
        self.assertTrue(result['topology_valid'])
        self.assertAlmostEqual(result['rg_laea_km'], expected['full']['rg_m']/1000, delta=.001)

    def test_outlet_boundary_overlap_and_no_match(self):
        from shapely.geometry import box
        index = BasinIndex([box(0, 0, 2, 2), box(1, 0, 3, 2)], [20, 10])
        ids, counts = index.match([.5, 1.5, 3, 5], [1, 1, 2, 1])
        np.testing.assert_array_equal(ids, [20, 10, 10, 0])
        np.testing.assert_array_equal(counts, [1, 2, 1, 0])
        with self.assertRaises(ValueError):
            index.match([0], [np.nan])

    def test_basin_join_handles_equivalent_date_line_longitudes(self):
        from shapely.geometry import box
        index = BasinIndex([box(179.5, 0, 180.5, 1)], [10])
        ids, counts = index.match([-179.8, 179.8], [.5, .5])
        np.testing.assert_array_equal(ids, [10, 10])
        np.testing.assert_array_equal(counts, [1, 1])

    def test_orphan_hole_cannot_pass_topology_via_library_repair(self):
        from pyproj import Proj
        proj = Proj(proj='laea', lon_0=20, lat_0=40, ellps='WGS84')
        rings = [rectangle(6000, 6000), rectangle(6000, 6000, (12000, 0)),
                 rectangle(1000, 1000, (6000, 5000))[::-1]]
        pts = np.concatenate([np.column_stack(proj(r[:, 0], r[:, 1], inverse=True)) for r in rings])
        result = local_geometry(pts, [0, 5, 10], check_topology=True)
        self.assertGreater(result['topology_conversion_errors'], 0)
        self.assertFalse(result['topology_valid'])


class LakeFollowupInference(unittest.TestCase):
    def test_sufficient_statistic_matches_existing_mle(self):
        rng = np.random.default_rng(55)
        for zeta in [-2, 0, 2, 2.3]:
            radii = sample_powerlaw(2000, zeta+1, 1, 20, rng)
            expected = fit_powerlaw(radii, 1, 20)['params']['alpha']-1
            self.assertAlmostEqual(fit_mean_log(np.log(radii).mean()), expected, delta=1e-5)

    def test_known_worlds_and_reproducibility(self):
        for zeta in [2., 2.3]:
            rng = np.random.default_rng(202610091)
            r = sample_powerlaw(20000, zeta+1, 1, 20, rng)
            result = intervals(r, np.arange(len(r)) % 100, 91, draws=200)
            self.assertAlmostEqual(result['zeta_R'], zeta, delta=.05)
            expected = 'conditional exponent equivalence' if zeta == 2 else 'robust exponent departure under declared resampling'
            self.assertEqual(decision(result), expected)
            self.assertEqual(result, intervals(r, np.arange(len(r)) % 100, 91, draws=200))

    def test_block_dependence_widens_interval(self):
        rng = np.random.default_rng(7)
        sizes = sample_powerlaw(100, 3, 1, 20, rng)
        radii = np.repeat(sizes, 100)
        result = intervals(radii, np.repeat(np.arange(100), 100), 55, draws=300)
        self.assertGreater(np.diff(result['block_ci95'])[0], 3*np.diff(result['iid_ci95'])[0])

    def test_decision_requires_both_intervals_and_gates(self):
        result = dict(n=1000, n_blocks=30, iid_ci95=[1.7, 1.8], block_ci95=[1.5, 2.05])
        self.assertEqual(decision(result), 'inconclusive')
        result['block_ci95'] = [1.6, 1.85]
        self.assertIn('robust exponent departure', decision(result))
        result['n_blocks'] = 9
        self.assertEqual(decision(result), 'insufficient')


if __name__ == '__main__':
    unittest.main()
