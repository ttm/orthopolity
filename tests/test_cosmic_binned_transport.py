"""Manufactured transfers exercise accounting and endpoint conditioning."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('binned_transport', ROOT / 'experiments/check_cosmic_binned_transport.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
try:
    import h5py
except ImportError:
    h5py = None


class EndpointTests(unittest.TestCase):
    def analyze(self, a, b, edges=(0., 1., 2., 3.), **kwargs):
        return MODULE.analyze_pair_coordinates(a, b, edges, **kwargs)

    def test_long_jump_has_exact_cell_overlap_and_distinct_localizations(self):
        r = self.analyze([.25], [2.25])
        p = r['positive_bins']
        self.assertEqual(r['boundaries']['net_particle_counts'], [0, 1, 1, 0])
        np.testing.assert_allclose(p['current_direct_cell_average'], [.75, 1., .25])
        np.testing.assert_allclose(p['current_departure'], [2., 0., 0.])
        np.testing.assert_allclose(p['current_midpoint'], [0., 2., 0.])
        self.assertEqual(p['continuity_residual_particle_counts'], [0, 0, 0])
        self.assertEqual(r['boundaries']['skip_bin']['gross_particle_counts'], [0, 1, 1, 0])
        self.assertEqual(r['boundaries']['factor2']['gross_particle_counts'], [0, 1, 1, 0])
        s = r['localization_summary']
        for k in ('direct', 'departure', 'midpoint'):
            self.assertAlmostEqual(s[k + '_width_weighted_current_sum'], 2.)

    def test_same_bin_motion_has_cell_current_but_no_edge_crossing(self):
        r = self.analyze([.2], [.8])
        self.assertEqual(r['boundaries']['net_particle_counts'], [0, 0, 0, 0])
        np.testing.assert_allclose(r['positive_bins']['current_direct_cell_average'], [.6, 0., 0.])
        self.assertEqual(r['positive_bins']['stock_change_particle_counts'], [0, 0, 0])
        self.assertAlmostEqual(r['localization_summary']['departure_relative_L1'], 0.)

    def test_downward_jump_keeps_negative_current(self):
        r = self.analyze([2.25], [.25])
        self.assertEqual(r['boundaries']['net_particle_counts'], [0, -1, -1, 0])
        np.testing.assert_allclose(r['positive_bins']['current_direct_cell_average'], [-.75, -1., -.25])
        np.testing.assert_allclose(r['positive_bins']['current_departure'], [0., 0., -2.])

    def test_sources_and_exit_censoring_use_matched_HH_density(self):
        r = self.analyze([.2, .2, np.nan], [np.nan, .7, 1.2])
        p = r['positive_bins']
        self.assertEqual(p['diffuse_entry_particle_counts'], [0, 1, 0])
        self.assertEqual(p['diffuse_exit_particle_counts'], [1, 0, 0])
        self.assertEqual(p['source_particle_counts'], [-1, 1, 0])
        self.assertEqual(p['continuity_residual_particle_counts'], [0, 0, 0])
        self.assertEqual(p['survival_fraction'], [.5, None, None])
        np.testing.assert_allclose(p['density_start_all'], [2., 0., 0.])
        np.testing.assert_allclose(p['density_start_HH'], [1., 0., 0.])
        self.assertAlmostEqual(p['drift_HH_per_gyr'][0], .5)
        self.assertAlmostEqual(p['current_departure'][0], .5)

    def test_empty_bins_and_zero_denominators_are_null(self):
        r = self.analyze([np.nan, .25], [np.nan, .25])
        self.assertEqual(r['positive_bins']['drift_HH_per_gyr'], [0., None, None])
        self.assertIsNone(r['localization_summary']['departure_relative_L1'])
        self.assertEqual(r['boundaries']['skip_bin']['fraction_of_gross_crossings'], [None] * 4)
        self.assertEqual(r['positive_bins']['relative_stock_change'], [0., None, None])

    def test_half_open_edges_and_domain_failures(self):
        np.testing.assert_array_equal(MODULE.coordinate_states(np.array([np.nan, 0., 1., 2.]), np.array([0., 1., 2., 3.])), [0, 1, 2, 3])
        for bad in (-.01, 3., np.inf, -np.inf):
            with self.subTest(bad=bad), self.assertRaises(MODULE.Invalid):
                self.analyze([bad], [.5])

    def test_nonuniform_widths_match_independent_clipped_integral(self):
        edges = np.array([0., .3, 1., 2.5, 3.])
        a, b = np.array([.1, .9, 2.8, .5]), np.array([2.7, .4, .2, 1.8])
        r = self.analyze(a, b, edges=edges, interval_gyr=2., mass_per_volume=3.)
        expected = np.array([(np.clip(b - lo, 0, hi - lo) - np.clip(a - lo, 0, hi - lo)).sum()
                             for lo, hi in zip(edges[:-1], edges[1:])]) * 3 / 2 / np.diff(edges)
        np.testing.assert_allclose(r['positive_bins']['current_direct_cell_average'], expected, atol=1e-14)
        for key in ('direct', 'departure', 'midpoint'):
            self.assertAlmostEqual(r['localization_summary'][key + '_width_weighted_current_sum'], (b - a).sum() * 1.5)

    def test_small_crossing_converges_in_absolute_localization_residual(self):
        errors = []
        for epsilon in (.1, .01, .001):
            r = self.analyze([1 - epsilon], [1 + epsilon])
            errors.append(sum(abs(x) for x in r['positive_bins']['finite_time_localization_residual_departure']))
        np.testing.assert_allclose(errors, [.2, .02, .002], atol=1e-14)
        # Relative residual need not shrink for a lone crossing; no convergence claim from this fixture.

    def test_block_aggregation_matches_single_batch(self):
        a = np.array([.1, 1.5, np.nan, 2.9, .4])
        b = np.array([2.2, .4, 2., np.nan, .9])
        whole = self.analyze(a, b)
        acc = MODULE.PairAccumulator([0., 1., 2., 3.])
        acc.add(a[:2], b[:2]); acc.add(a[2:], b[2:])
        split = acc.finish(1., 1.)
        self.assertEqual(whole['transfer_particle_counts'], split['transfer_particle_counts'])
        np.testing.assert_allclose(whole['positive_bins']['current_direct_cell_average'], split['positive_bins']['current_direct_cell_average'])

    def test_common_hosted_subset_rejects_diffuse_members(self):
        with self.assertRaisesRegex(MODULE.Invalid, 'invalid_common_hosted_subset'):
            self.analyze([np.nan], [.5], common=np.array([True]))

    def test_exact_integer_power_edges_and_factor_two_tail(self):
        counts0 = np.array([0, 4, 8], dtype=np.uint64)
        counts1 = np.array([0, 8, 4], dtype=np.uint64)
        r = MODULE.analyze_particle_pair(np.array([1, 2]), np.array([1, 2]), counts0, counts1,
                                        np.arange(0., 6.), 1., 1., np.ones(2, bool))
        mapping, _ = MODULE.host_maps(counts0, np.arange(0., 6.))
        self.assertEqual(mapping.tolist(), [0, 3, 4])
        self.assertEqual(sum(r['boundaries']['factor2']['gross_particle_counts']), 2)
        self.assertEqual(r['boundaries']['net_particle_counts'], [0] * 6)

    def test_midpoint_ties_use_exact_product_in_both_directions(self):
        labels = np.array([1])
        for left, right in ((64, 4096), (4096, 64)):
            pair = MODULE.analyze_particle_pair(
                labels, labels, np.array([0, left]), np.array([0, right]),
                np.arange(15), 1., 1., np.ones(1, dtype=bool))
            current = pair['positive_bins']['current_midpoint']
            self.assertEqual(np.flatnonzero(current).tolist(), [9])  # 2**9 = 512
            self.assertAlmostEqual(current[9], np.log2(right / left))

    def test_host_stock_counts_hosts_once_and_particles_by_membership(self):
        r = MODULE.epoch_stock(np.array([1, 1, 2, 2, 2, 2, 0]), np.array([0, 2, 4]), [0., 1., 2., 3.], 10.)
        self.assertEqual(r['particle_counts'], [1, 0, 2, 4])
        self.assertEqual(r['positive_host_counts'], [0, 1, 1])
        self.assertEqual(r['mass_density'], [10., 0., 20., 40.])
        with self.assertRaisesRegex(MODULE.Invalid, 'host_and_particle_stock_mismatch'):
            MODULE.epoch_stock(np.array([1]), np.array([0, 2]), [0., 1., 2.], 1.)


class CadenceTests(unittest.TestCase):
    def analyze_three(self, x0, x1, x2, dt0=2., dt1=3.):
        arrays = [np.asarray(x, float) for x in (x0, x1, x2)]
        common = np.all(np.isfinite(np.array(arrays)), axis=0)
        pairs = [MODULE.analyze_pair_coordinates(arrays[a], arrays[b], [0., 1., 2., 3.],
                 interval_gyr=dt, common=common) for a, b, dt in ((0, 1, dt0), (1, 2, dt1), (0, 2, dt0 + dt1))]
        return pairs, MODULE.cadence_report(*pairs)

    def test_hidden_return_has_nonnegative_common_gross_loss(self):
        _, r = self.analyze_three([.5], [2.5], [.5])
        self.assertEqual(r['common_hosted_net_difference_particle_counts'], [0] * 4)
        self.assertEqual(r['common_hosted_gross_omitted_crossings'], [0, 2, 2, 0])
        self.assertEqual(r['common_hosted_fraction_gross_crossings_omitted'], 1.)

    def test_diffuse_excursion_can_give_negative_HH_gross_difference(self):
        _, r = self.analyze_three([.5], [np.nan], [2.5])
        self.assertEqual(r['HH_gross_adjacent_minus_coarsened_particle_counts'], [0, -1, -1, 0])
        self.assertEqual(r['diffuse_source_adjacent_minus_coarsened_particle_counts'], [-1, 0, 1])
        self.assertEqual(r['source_current_compensation_residual_counts'], [0, 0, 0])
        self.assertIsNone(r['common_hosted_fraction_gross_crossings_omitted'])

    def test_unequal_intervals_combine_integrated_currents_not_rates(self):
        pairs, r = self.analyze_three([.5], [1.5], [2.5], dt0=2., dt1=3.)
        currents = [np.array(p['boundaries']['current_mass_density_per_gyr']) for p in pairs]
        np.testing.assert_allclose(2 * currents[0] + 3 * currents[1], 5 * currents[2])
        self.assertFalse(np.allclose(currents[0] + currents[1], currents[2]))
        self.assertEqual(r['common_hosted_gross_omitted_crossings'], [0] * 4)


class DriverTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name)
        self.input = self.path / 'input.json'
        self.input.write_text('{}')
        self.receipt = self.path / 'inventory.json'
        self.receipt.write_text(json.dumps({'outcome': 'inventory_checks_passed', 'files': {},
                                           'acquisition_receipt_sha256': 'test', 'units': {'time_convention': 'fixture'}}))
        ref = lambda p: {'path': str(p), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
        self.config = dict(schema_version=1, development_only=True, validation_target_assigned=False,
            reference_measure='log-orthopolic collisionless total-matter development', outputs=[97, 98, 99],
            pairs=[[97, 98], [98, 99], [97, 99]], reader_max_rss_bytes=3 * 1024 ** 3,
            input_config=ref(self.input), inventory_receipt=ref(self.receipt), input_directory=str(self.path),
            helper_sources=[], grids=[{'name': n, 'log2_edges': np.arange(0., 26. + s / 2, s).tolist()}
                                     for n, s in [('primary', 1.), ('fine', .5), ('coarse', 2.)]])
        self.config_path = self.path / 'plan.json'
        self.destination = self.path / 'results'

    def save(self):
        self.config_path.write_text(json.dumps(self.config))

    def test_modified_input_stops_with_retained_failure(self):
        self.save(); self.input.write_text('{"changed":true}')
        with patch.object(MODULE.inventory, 'complete_provenance') as probe:
            r = MODULE.run(self.config_path, self.destination)
        self.assertEqual(r['reason'], 'input_reference_hash_mismatch')
        probe.assert_not_called()
        self.assertTrue((self.destination / 'analysis_source.py').exists())
        self.assertEqual(json.loads((self.destination / 'transport.json').read_text())['outcome'], 'failed')

    def test_existing_output_is_not_overwritten(self):
        self.save(); self.destination.mkdir(); marker = self.destination / 'transport.json'; marker.write_text('preserve')
        with self.assertRaises(FileExistsError):
            MODULE.run(self.config_path, self.destination)
        self.assertEqual(marker.read_text(), 'preserve')

    def test_plan_rejects_changed_grid_or_validation_role(self):
        for field, value in [('validation_target_assigned', True), ('reader_max_rss_bytes', 4 * 1024 ** 3)]:
            with self.subTest(field=field):
                changed = copy.deepcopy(self.config); changed[field] = value
                self.config_path.write_text(json.dumps(changed))
                with self.assertRaises(MODULE.Invalid): MODULE.read_plan(self.config_path)
        self.config['grids'][0]['log2_edges'][1] = .9; self.save()
        with self.assertRaises(MODULE.Invalid): MODULE.read_plan(self.config_path)

    @unittest.skipIf(h5py is None, 'optional cosmic HDF5 dependency not installed')
    def test_driver_checks_all_grids_with_known_complete_inventory(self):
        self.save()
        expected = dict(num_dm=12, mass_dm=.125, boxsize=35000., hubble=.6774, omega_0=.3089, omega_L=.6911,
                        snapshots={str(o): {'redshift': z} for o, z in ((97, .024), (98, .0095), (99, 0.))})
        def provenance(a, b, result):
            result['files'] = {}; result['acquisition_receipt_sha256'] = 'test'
            return {'expected': expected}, {}
        def load(output, *args):
            count = {97: 2, 98: 4, 99: 8}[output]
            hosts = 8 // count
            labels = np.r_[np.repeat(np.arange(1, hosts + 1), count), [0] * 4].astype(np.uint32)
            return np.arange(12, dtype=np.uint64), labels, np.r_[0, [count] * hosts].astype(np.uint64), {}
        with patch.object(MODULE.inventory, 'complete_provenance', side_effect=provenance), \
             patch.object(MODULE.inventory, 'load_epoch', side_effect=load), \
             patch.object(MODULE.inventory, 'peak_rss_bytes', return_value=1000):
            r = MODULE.run(self.config_path, self.destination)
        self.assertEqual(r['outcome'], 'development_accounting_passed', r.get('reason'))
        self.assertTrue(r['shared_boundary_grid_consistency'])
        self.assertFalse(r['log_orthopolic_transport_validated'])
        for grid in r['grids'].values():
            self.assertEqual(grid['cadence']['common_hosted_fraction_gross_crossings_omitted'], 0.)
            for pair in grid['pairs'].values():
                self.assertTrue(all(x == 0 for x in pair['positive_bins']['continuity_residual_particle_counts']))


if __name__ == '__main__':
    unittest.main()
