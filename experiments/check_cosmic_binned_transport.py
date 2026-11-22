"""Fixed-bin endpoint diagnostics for log-orthopolic material development.

Accounting identities and finite-time localization residuals are not tests of
instantaneous physical drift, cadence convergence, or an independent forecast.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform

import numpy as np

try:
    from experiments import check_cosmic_material_inventory as inventory
except ModuleNotFoundError:
    import check_cosmic_material_inventory as inventory

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / 'configs/cosmic-transport-development-2026-11-22.json'
BLOCK = 262144
require = inventory.require
Invalid = inventory.InvalidBootstrap


def nullable_ratio(numerator, denominator):
    a, b = np.broadcast_arrays(np.asarray(numerator, float), np.asarray(denominator, float))
    value = np.divide(a, b, out=np.zeros_like(a), where=b != 0)
    return [float(x) if y != 0 else None for x, y in zip(value.flat, b.flat)]


def checked_edges(edges):
    edges = np.asarray(edges, dtype=np.float64)
    require(edges.ndim == 1 and 2 <= len(edges) <= 129 and np.all(np.isfinite(edges))
            and np.all(np.diff(edges) > 0), 'invalid_bin_edges')
    return edges


def coordinate_states(x, edges):
    """Generic fixture interface: NaN denotes diffuse, never a log mass."""
    x = np.asarray(x, dtype=np.float64)
    require(x.ndim == 1 and not np.any(np.isinf(x)), 'invalid_coordinates')
    hosted = ~np.isnan(x)
    require(np.all((x[hosted] >= edges[0]) & (x[hosted] < edges[-1])), 'host_outside_fixed_domain')
    state = np.zeros(len(x), dtype=np.int64)
    state[hosted] = np.searchsorted(edges, x[hosted], side='right')
    return state


def host_maps(counts, log2_edges):
    counts = np.asarray(counts)
    require(counts.ndim == 1 and counts.dtype.kind in 'iu' and len(counts) >= 2
            and counts[0] == 0 and np.all(counts[1:] > 0), 'invalid_host_counts')
    edges = checked_edges(log2_edges)
    limits = np.exp2(edges)
    require(np.all(counts[1:] >= limits[0]) and np.all(counts[1:] < limits[-1]),
            'host_outside_fixed_domain')
    states = np.zeros(len(counts), dtype=np.int64)
    states[1:] = np.searchsorted(limits, counts[1:], side='right')
    x = np.full(len(counts), np.nan)
    x[1:] = np.log2(counts[1:].astype(np.float64)) * np.log(2.)
    return states, x


def crossing_counts(matrix):
    """Positive-state endpoint crossings; state0 is excluded from every cut."""
    matrix = np.asarray(matrix)
    b = matrix.shape[0] - 1
    require(matrix.shape == (b + 1, b + 1), 'invalid_transfer_shape')
    up = np.zeros(b + 1, dtype=np.int64)
    down = np.zeros(b + 1, dtype=np.int64)
    for edge in range(1, b):
        up[edge] = matrix[1:edge + 1, edge + 1:].sum(dtype=np.int64)
        down[edge] = matrix[edge + 1:, 1:edge + 1].sum(dtype=np.int64)
    return up, down


def boundary_report(matrix, scale):
    up, down = crossing_counts(matrix)
    return dict(up_particle_counts=up.tolist(), down_particle_counts=down.tolist(),
                net_particle_counts=(up - down).tolist(), gross_particle_counts=(up + down).tolist(),
                current_mass_density_per_gyr=((up - down) * scale).tolist(),
                gross_mass_density_per_gyr=((up + down) * scale).tolist())


class PairAccumulator:
    def __init__(self, edges):
        self.edges = checked_edges(edges)
        self.width = np.diff(self.edges)
        self.bins = len(self.width)
        self.transfer = np.zeros((self.bins + 1, self.bins + 1), dtype=np.int64)
        self.factor2 = np.zeros_like(self.transfer)
        self.common = np.zeros_like(self.transfer)
        self.q_start = np.zeros(self.bins)
        self.q_end = np.zeros(self.bins)
        self.departure = np.zeros(self.bins)
        self.midpoint = np.zeros(self.bins)
        self.signed_displacement = 0.
        self.absolute_displacement = 0.
        self.particles = 0

    def add(self, x0, x1, state0=None, state1=None, common=None, factor2=None, midpoint_states=None):
        x0, x1 = np.asarray(x0, float), np.asarray(x1, float)
        require(x0.shape == x1.shape and x0.ndim == 1, 'pair_coordinate_shape_mismatch')
        s0 = coordinate_states(x0, self.edges) if state0 is None else state0
        s1 = coordinate_states(x1, self.edges) if state1 is None else state1
        for s, x in ((s0, x0), (s1, x1)):
            require(np.shape(s) == x.shape and np.asarray(s).dtype.kind in 'iu'
                    and np.all((s >= 0) & (s <= self.bins))
                    and np.array_equal(s == 0, np.isnan(x)), 'state_coordinate_mismatch')
        size = self.bins + 1
        keys = s0 * size + s1
        self.transfer += np.bincount(keys, minlength=size * size).reshape(size, size)
        hh = (s0 > 0) & (s1 > 0)
        if common is not None:
            common = np.asarray(common)
            require(common.shape == x0.shape and common.dtype == np.dtype(bool)
                    and not np.any(common & ~hh), 'invalid_common_hosted_subset')
            self.common += np.bincount(keys[common], minlength=size * size).reshape(size, size)
        a, z = s0[hh] - 1, s1[hh] - 1
        old, new = x0[hh], x1[hh]
        dx = new - old
        mid = (np.searchsorted(self.edges, old + dx / 2, side='right') - 1
               if midpoint_states is None else midpoint_states[hh] - 1)
        require(np.all((mid >= 0) & (mid < self.bins)), 'midpoint_outside_domain')
        # Centered moments keep each summand within one bin width. They avoid
        # cancellation of two large absolute logarithmic coordinate sums.
        self.q_start += np.bincount(a, weights=old - self.edges[a], minlength=self.bins)
        self.q_end += np.bincount(z, weights=new - self.edges[z], minlength=self.bins)
        self.departure += np.bincount(a, weights=dx, minlength=self.bins)
        self.midpoint += np.bincount(mid, weights=dx, minlength=self.bins)
        self.signed_displacement += float(dx.sum())
        self.absolute_displacement += float(np.abs(dx).sum())
        tail = np.abs(dx) >= np.log(2.) if factor2 is None else np.asarray(factor2)[hh]
        require(tail.shape == dx.shape and tail.dtype == np.dtype(bool), 'invalid_factor2_mask')
        self.factor2 += np.bincount(keys[hh][tail], minlength=size * size).reshape(size, size)
        self.particles += len(x0)

    def finish(self, interval_gyr, mass_per_volume):
        require(np.isfinite(interval_gyr) and interval_gyr > 0
                and np.isfinite(mass_per_volume) and mass_per_volume > 0, 'invalid_units_or_interval')
        t, w = self.transfer, self.width
        start, end = t.sum(axis=1), t.sum(axis=0)
        require(int(t.sum()) == self.particles, 'transfer_inventory_mismatch')
        hh0, hh1 = t[1:, 1:].sum(axis=1), t[1:, 1:].sum(axis=0)
        difference = hh1 - hh0
        above = np.cumsum(difference[::-1], dtype=np.int64)[::-1] - difference
        direct_displacement = w * above + self.q_end - self.q_start
        scale = mass_per_volume / interval_gyr
        direct = direct_displacement * scale / w
        departure = self.departure * scale / w
        midpoint = self.midpoint * scale / w
        boundary = boundary_report(t, scale)
        net = np.array(boundary['net_particle_counts'])
        source = t[0, 1:] - t[1:, 0]
        delta = end[1:] - start[1:]
        residual = delta - (net[:-1] - net[1:] + source)
        require(np.all(residual == 0), 'endpoint_continuity_failure')
        skip = t.copy()
        indices = np.arange(len(t))
        skip[np.abs(indices[:, None] - indices[None, :]) < 2] = 0
        skip[0, :] = 0
        skip[:, 0] = 0
        boundary['skip_bin'] = boundary_report(skip, scale)
        boundary['factor2'] = boundary_report(self.factor2, scale)
        boundary['common_hosted'] = boundary_report(self.common, scale)
        for key in ('skip_bin', 'factor2'):
            boundary[key]['fraction_of_gross_crossings'] = nullable_ratio(
                boundary[key]['gross_particle_counts'], boundary['gross_particle_counts'])
        summary = {}
        for name, approx in (('departure', departure), ('midpoint', midpoint)):
            k = direct - approx
            denominator = float(np.sum(w * (np.abs(direct) + np.abs(approx))))
            summary[name + '_relative_L1'] = float(np.sum(w * np.abs(k)) / denominator) if denominator else None
            summary[name + '_width_weighted_current_sum'] = float(np.sum(w * approx))
        summary.update(direct_width_weighted_current_sum=float(np.sum(w * direct)),
                       expected_width_weighted_current_sum=self.signed_displacement * scale,
                       direct_global_displacement_residual=float(direct_displacement.sum() - self.signed_displacement),
                       departure_global_displacement_residual=float(self.departure.sum() - self.signed_displacement),
                       midpoint_global_displacement_residual=float(self.midpoint.sum() - self.signed_displacement),
                       total_absolute_log_displacement=self.absolute_displacement,
                       interpretation='Finite-time localization residual; not a continuum closure error or uncertainty bound.')
        return dict(interval_gyr=float(interval_gyr), particle_mass_per_comoving_volume=float(mass_per_volume),
                    transfer_particle_counts=t.tolist(), transfer_mass_density=(t * mass_per_volume).tolist(),
                    stock_start_particle_counts=start.tolist(), stock_end_particle_counts=end.tolist(),
                    row_column_sums_verified=True, boundaries=boundary,
                    positive_bins=dict(
                        stock_change_particle_counts=delta.tolist(),
                        stock_change_rate_mass_density=(delta * scale).tolist(),
                        relative_stock_change=nullable_ratio(2 * delta, start[1:] + end[1:]),
                        diffuse_entry_particle_counts=t[0, 1:].tolist(), diffuse_exit_particle_counts=t[1:, 0].tolist(),
                        source_particle_counts=source.tolist(), source_mass_density_per_gyr=(source * scale).tolist(),
                        continuity_residual_particle_counts=residual.tolist(),
                        density_start_all=(start[1:] * mass_per_volume / w).tolist(),
                        density_start_HH=(hh0 * mass_per_volume / w).tolist(),
                        survival_fraction=nullable_ratio(hh0, start[1:]),
                        drift_HH_per_gyr=nullable_ratio(self.departure, hh0 * interval_gyr),
                        current_direct_cell_average=direct.tolist(), current_departure=departure.tolist(),
                        current_midpoint=midpoint.tolist(),
                        finite_time_localization_residual_departure=(direct - departure).tolist(),
                        finite_time_localization_residual_midpoint=(direct - midpoint).tolist()),
                    localization_summary=summary,
                    scope='HH is endpoint-conditioned. Diffuse exits have undefined logarithmic displacement. Matched HH density is not the full starting density.')


def analyze_pair_coordinates(x0, x1, edges, interval_gyr=1., mass_per_volume=1., common=None):
    accumulator = PairAccumulator(edges)
    accumulator.add(x0, x1, common=common)
    return accumulator.finish(interval_gyr, mass_per_volume)


def analyze_particle_pair(labels0, labels1, counts0, counts1, log2_edges, interval_gyr,
                          mass_per_volume, common):
    maps0, xmap0 = host_maps(counts0, log2_edges)
    maps1, xmap1 = host_maps(counts1, log2_edges)
    accumulator = PairAccumulator(np.asarray(log2_edges) * np.log(2.))
    # The fixed integer and half-integer log2 edges give exact squared cutoffs.
    squared_edges = np.exp2(2 * np.asarray(log2_edges)).astype(np.uint64)
    for begin in range(0, len(labels0), BLOCK):
        a, b = labels0[begin:begin + BLOCK], labels1[begin:begin + BLOCK]
        n0, n1 = counts0[a], counts1[b]
        # The selected counts are <2^26, so this exact integer factor test cannot overflow.
        tail = (n1 >= 2 * n0) | (n0 >= 2 * n1)
        midpoint_states = np.searchsorted(squared_edges, n0.astype(np.uint64) * n1.astype(np.uint64), side='right')
        accumulator.add(xmap0[a], xmap1[b], maps0[a], maps1[b], common[begin:begin + BLOCK],
                        tail, midpoint_states)
    return accumulator.finish(interval_gyr, mass_per_volume)


def epoch_stock(labels, counts, log2_edges, mass_per_volume):
    mapping, _ = host_maps(counts, log2_edges)
    size = len(log2_edges)
    stock = np.zeros(size, dtype=np.int64)
    for begin in range(0, len(labels), BLOCK):
        stock += np.bincount(mapping[labels[begin:begin + BLOCK]], minlength=size)
    hosts = np.bincount(mapping[1:], minlength=size)[1:]
    weighted_hosts = np.bincount(mapping[1:], weights=counts[1:].astype(float), minlength=size)[1:]
    require(np.array_equal(stock[1:], weighted_hosts), 'host_and_particle_stock_mismatch')
    width = np.diff(log2_edges) * np.log(2.)
    return dict(particle_counts=stock.tolist(), positive_host_counts=hosts.tolist(),
                mass_density=(stock * mass_per_volume).tolist(),
                positive_log_resource_density=(stock[1:] * mass_per_volume / width).tolist())


def cadence_report(first, second, coarsened):
    f = [np.array(p['boundaries']['net_particle_counts']) for p in (first, second, coarsened)]
    g = [np.array(p['boundaries']['gross_particle_counts']) for p in (first, second, coarsened)]
    s = [np.array(p['positive_bins']['source_particle_counts']) for p in (first, second, coarsened)]
    fd, gd, sd = f[0] + f[1] - f[2], g[0] + g[1] - g[2], s[0] + s[1] - s[2]
    compensation = fd[:-1] - fd[1:] + sd
    require(np.all(compensation == 0), 'cadence_source_current_compensation_failure')
    cf = [np.array(p['boundaries']['common_hosted']['net_particle_counts']) for p in (first, second, coarsened)]
    cg = [np.array(p['boundaries']['common_hosted']['gross_particle_counts']) for p in (first, second, coarsened)]
    cf_difference, cg_difference = cf[0] + cf[1] - cf[2], cg[0] + cg[1] - cg[2]
    require(np.all(cf_difference == 0) and np.all(cg_difference >= 0), 'common_hosted_cadence_identity_failure')
    denominator = int((cg[0] + cg[1]).sum())
    return dict(HH_net_adjacent_minus_coarsened_particle_counts=fd.tolist(),
                HH_gross_adjacent_minus_coarsened_particle_counts=gd.tolist(),
                diffuse_source_adjacent_minus_coarsened_particle_counts=sd.tolist(),
                source_current_compensation_residual_counts=compensation.tolist(),
                common_hosted_net_difference_particle_counts=cf_difference.tolist(),
                common_hosted_gross_omitted_crossings=cg_difference.tolist(),
                common_hosted_fraction_gross_crossings_omitted=float(cg_difference.sum() / denominator) if denominator else None,
                common_hosted_gross_omitted_fraction_by_boundary=nullable_ratio(cg_difference, cg[0] + cg[1]),
                common_hosted_resolved_gross_crossings=(cg[0] + cg[1]).tolist(),
                scope='Counts are integrated crossings, not summed rates. Full-population HH gross difference may be negative because diffuse excursions change conditioning. Only the fixed all-three-hosted subset has nonnegative omitted gross crossings.')


def checked_reference(record):
    require(isinstance(record, dict) and isinstance(record.get('path'), str), 'invalid_reference')
    path = ROOT / record['path']
    require(inventory.sha256(path) == record.get('sha256'), 'input_reference_hash_mismatch')
    return path


def read_plan(path):
    config = inventory.load_json(path)
    require(config.get('schema_version') == 1 and config.get('development_only') is True
            and config.get('validation_target_assigned') is False
            and config.get('outputs') == [97, 98, 99]
            and config.get('pairs') == [[97, 98], [98, 99], [97, 99]], 'invalid_development_plan')
    require(type(config.get('reader_max_rss_bytes')) is int and 0 < config['reader_max_rss_bytes'] <= 3 * 1024 ** 3,
            'invalid_memory_limit')
    grids = config.get('grids')
    require(isinstance(grids, list) and len(grids) == 3
            and {g['name'] for g in grids} == {'primary', 'fine', 'coarse'}, 'invalid_grids')
    for g in grids:
        edges = checked_edges(g['log2_edges'])
        step = {'primary': 1., 'fine': .5, 'coarse': 2.}[g['name']]
        require(np.array_equal(edges, np.arange(0., 26. + step / 2, step)), 'unapproved_fixed_grid')
    return config


def run(config_path, destination):
    config_path, destination = Path(config_path), Path(destination)
    plan = read_plan(config_path)
    destination.mkdir(parents=True, exist_ok=False)
    source = Path(__file__).read_bytes()
    (destination / 'analysis_source.py').write_bytes(source)
    (destination / 'config.json').write_bytes(config_path.read_bytes())
    result = dict(schema_version=1, outcome='failed', development_only=True,
                  validation_target_assigned=False, log_orthopolic_transport_validated=False,
                  reference_measure=plan['reference_measure'], config_sha256=inventory.sha256(config_path),
                  analysis_source_sha256=hashlib.sha256(source).hexdigest(),
                  started_utc=datetime.now(timezone.utc).isoformat(), grids={},
                  versions={'python': platform.python_version(), 'numpy': np.__version__})
    try:
        input_config = checked_reference(plan['input_config'])
        prior_path = checked_reference(plan['inventory_receipt'])
        for reference in plan['helper_sources']:
            checked_reference(reference)
        previous = inventory.load_json(prior_path)
        require(previous.get('outcome') == 'inventory_checks_passed', 'inventory_not_passed')
        provenance = {'files': {}}
        acquired, paths = inventory.complete_provenance(input_config, ROOT / plan['input_directory'], provenance)
        require(provenance['files'] == previous.get('files')
                and provenance['acquisition_receipt_sha256'] == previous.get('acquisition_receipt_sha256'),
                'inventory_acquisition_mismatch')
        result['input_provenance'] = provenance
        result['inventory_receipt_sha256'] = inventory.sha256(prior_path)
        expected = acquired['expected']
        estimate = 97 * expected['num_dm'] + 256 * 1024 ** 2
        require(estimate <= plan['reader_max_rss_bytes'], 'planned_memory_exceeds_limit')
        result['memory'] = dict(planned_upper_estimate_bytes=estimate, limit_bytes=plan['reader_max_rss_bytes'], scratch_bytes_written=0)
        import h5py
        result['versions'].update(h5py=h5py.__version__, hdf5=h5py.version.hdf5_version)
        reference_ids, labels, host_counts = None, {}, {}
        for output in plan['outputs']:
            ids, current_labels, current_counts, _ = inventory.load_epoch(output, paths, expected, h5py)
            if reference_ids is None:
                reference_ids = ids
            else:
                require(np.array_equal(reference_ids, ids), 'particle_id_set_changed_between_outputs')
                del ids
            labels[output], host_counts[output] = current_labels, current_counts
            require(inventory.peak_rss_bytes() <= plan['reader_max_rss_bytes'], 'memory_limit_exceeded')
        del reference_ids
        common = (labels[97] > 0) & (labels[98] > 0) & (labels[99] > 0)
        result['common_all_three_hosted_particles'] = int(common.sum())
        mass_solar = expected['mass_dm'] * 1e10 / expected['hubble']
        volume = (expected['boxsize'] / 1000 / expected['hubble']) ** 3
        factor = mass_solar / volume
        times = {o: inventory.cosmic_time_gyr(1 / (1 + expected['snapshots'][str(o)]['redshift']),
                  expected['omega_0'], expected['omega_L'], expected['hubble']) for o in plan['outputs']}
        result['units'] = dict(particle_mass_solar=mass_solar, volume_comoving_mpc3=volume,
                               stock='solar masses / comoving Mpc^3', log_resource_density='solar masses / comoving Mpc^3 / natural-log mass',
                               current='solar masses / comoving Mpc^3 / Gyr', drift='natural-log mass / Gyr',
                               time_convention=previous['units']['time_convention'])
        for grid in plan['grids']:
            edges = np.asarray(grid['log2_edges'], float)
            result['grids'][grid['name']] = report = dict(log2_edges=edges.tolist(), log_edges=(edges * np.log(2.)).tolist(), epoch_stocks={}, pairs={})
            for output in plan['outputs']:
                report['epoch_stocks'][str(output)] = epoch_stock(labels[output], host_counts[output], edges, factor)
            for left, right in plan['pairs']:
                pair = analyze_particle_pair(labels[left], labels[right], host_counts[left], host_counts[right],
                                             edges, times[right] - times[left], factor, common)
                require(pair['stock_start_particle_counts'] == report['epoch_stocks'][str(left)]['particle_counts']
                        and pair['stock_end_particle_counts'] == report['epoch_stocks'][str(right)]['particle_counts'],
                        'transfer_stock_marginal_mismatch')
                report['pairs'][f'{left}->{right}'] = pair
            report['cadence'] = cadence_report(*(report['pairs'][key] for key in ('97->98', '98->99', '97->99')))
            require(inventory.peak_rss_bytes() <= plan['reader_max_rss_bytes'], 'memory_limit_exceeded')
        # Shared physical cuts must give the same integer crossings on all grids.
        for key in ('97->98', '98->99', '97->99'):
            curves = {name: np.array(result['grids'][name]['pairs'][key]['boundaries']['net_particle_counts']) for name in ('primary', 'fine', 'coarse')}
            require(np.array_equal(curves['fine'][::2], curves['primary'])
                    and np.array_equal(curves['primary'][::2], curves['coarse']), 'shared_boundary_grid_mismatch')
        result['shared_boundary_grid_consistency'] = True
        result['outcome'] = 'development_accounting_passed'
        result['interpretation'] = 'Exact endpoint conservation and finite-time localization diagnostics. No threshold selects a plateau or qualifies physical local closure, stationarity, cadence convergence, or an independent log-orthopolic forecast.'
    except Invalid as exc:
        result['reason'] = str(exc)
    except (ImportError, OSError, ValueError, KeyError, TypeError, OverflowError) as exc:
        result['reason'] = 'analysis_exception_' + type(exc).__name__
    result['peak_resident_bytes'] = inventory.peak_rss_bytes()
    result['finished_utc'] = datetime.now(timezone.utc).isoformat()
    with (destination / 'transport.json').open('x', encoding='utf-8') as target:
        json.dump(result, target, indent=2, sort_keys=True, allow_nan=False)
        target.write('\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=DEFAULT_CONFIG)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    try:
        result = run(args.config, args.output_dir)
    except (OSError, Invalid, ValueError, KeyError, TypeError) as exc:
        reason = str(exc) if isinstance(exc, Invalid) else type(exc).__name__
        print(json.dumps({'outcome': 'failed', 'reason': reason}))
        return 1
    print(json.dumps({'outcome': result['outcome'], 'reason': result.get('reason')}))
    return 0 if result['outcome'] == 'development_accounting_passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
