"""Run the frozen local-metric global lake follow-up; no network access.

--synthetic 2 (or 2.3) uses no real data. --derive calculates all source geometries
before fitting. Without --derive the checksum-pinned derived table is required.
"""
import argparse
import csv
import hashlib
import json
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from orthopolity.geodesic_lake_geometry import BasinIndex, local_geometry
from orthopolity.goodness_of_fit import powerlaw_gof, sample_powerlaw
from orthopolity.lake_followup_statistics import decision, fit_mean_log, intervals

CONFIG_PATH = ROOT/'configs/lake_metric_followup_2026-10-09.json'
CONFIG = json.loads(CONFIG_PATH.read_text())
TABLE = ROOT/'data/derived/lake_metric_followup_2026-10-09.csv'
SOURCE = ROOT/'data/hydrolakes/2026-10-09/extracted/HydroLAKES_polys_v10_shp/HydroLAKES_polys_v10.shp'
BASINS = ROOT/'data/hydrobasins/2026-10-09'


def sha(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''):
            result.update(block)
    return result.hexdigest()


def read_basins():
    import shapefile
    from shapely import make_valid
    from shapely.geometry import shape
    manifest = json.loads((BASINS/'acquisition.json').read_text())
    geometries, identifiers = [], []
    for item in manifest['archives']:
        path = ROOT/item['path']
        if sha(path) != item['sha256']:
            raise ValueError(f'Basin checksum mismatch: {path}')
        with shapefile.Reader(str(path)) as reader:
            for row in reader.iterShapeRecords():
                geometry = shape(row.shape.__geo_interface__)
                # Retain polygonal pieces of the deterministic linework repair;
                # dangling zero-area lines cannot define a basin interior.
                if not geometry.is_valid:
                    geometry = make_valid(geometry, method='linework')
                    def polygons(g):
                        if g.geom_type == 'Polygon':
                            return [g]
                        if hasattr(g, 'geoms'):
                            return [p for child in g.geoms for p in polygons(child)]
                        return []
                    from shapely.geometry import MultiPolygon
                    geometry = MultiPolygon(polygons(geometry))
                if not geometry.is_valid or geometry.is_empty:
                    raise ValueError('Basin repair did not yield valid polygonal coverage')
                geometries.append(geometry)
                identifiers.append(row.record.as_dict()['HYBAS_ID'])
    return BasinIndex(geometries, identifiers)


def derive():
    import shapefile
    from fetch_hydrolakes import main as verify
    verify([])  # Offline raw-archive and extracted-member checks before computation.
    start = time.monotonic()
    TABLE.parent.mkdir(parents=True, exist_ok=True)
    identifiers = set()
    temporary = TABLE.with_suffix('.partial.csv')
    with shapefile.Reader(str(SOURCE), encoding='latin1') as reader, temporary.open('w', newline='') as f:
        writer = None
        for i, row in enumerate(reader.iterShapeRecords(), 1):
            rec = row.record.as_dict()
            identifier = rec['Hylak_id']
            if identifier is None or identifier in identifiers:
                raise ValueError('Missing or duplicate lake ID')
            identifiers.add(identifier)
            try:
                geometry = local_geometry(row.shape.points, row.shape.parts, check_topology=True)
            except Exception as error:
                raise ValueError(f'Hylak_id={identifier}: {error}; no exclusion permitted') from error
            result = {key: rec[key] for key in ['Hylak_id', 'Lake_area', 'Lake_type', 'Country', 'Pour_long', 'Pour_lat']}
            result.update(geometry)
            if writer is None:
                writer = csv.DictWriter(f, fieldnames=list(result))
                writer.writeheader()
            writer.writerow(result)
            if i % 50000 == 0:
                print(f'Geometry: {i:,} features, elapsed {time.monotonic()-start:.1f}s', flush=True)
    if len(identifiers) != 1427688:
        raise ValueError('Unexpected HydroLAKES feature count')
    temporary.replace(TABLE)
    receipt = dict(path=str(TABLE.relative_to(ROOT)), sha256=sha(TABLE), n=len(identifiers),
                   config_sha256=sha(CONFIG_PATH), generated_utc=datetime.now(timezone.utc).isoformat())
    TABLE.with_suffix('.receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')


def quantiles(values):
    return dict(zip(['min', 'p01', 'median', 'p99', 'max'],
                    np.percentile(np.asarray(values, float), [0, 1, 50, 99, 100]).tolist()))


def analyse(table, output):
    lo, hi = CONFIG['rg_range_km']
    selected = table.rg_laea_km.between(lo, hi)
    sample = table[selected].copy()
    basin, multiplicity = read_basins().match(sample.Pour_long, sample.Pour_lat)
    sample['HYBAS_ID'] = basin
    sample['basin_matches'] = multiplicity
    sample.to_csv(output/'selected-lakes.csv', index=False)
    sample[sample.HYBAS_ID == 0][['Hylak_id', 'Pour_long', 'Pour_lat']].to_csv(output/'unmatched-outlets.csv', index=False)
    n_boot, seed = CONFIG['bootstrap_draws'], CONFIG['seed']
    print(f'Fitting {len(sample):,} primary selected lakes', flush=True)
    full = intervals(sample.rg_laea_km, sample.Country, seed, n_boot)
    matched = sample[sample.HYBAS_ID != 0]
    hydrological = intervals(matched.rg_laea_km, matched.HYBAS_ID, seed+1, n_boot)
    verdict = decision(hydrological, CONFIG['equivalence_band'], CONFIG['minimum_lakes'], CONFIG['minimum_blocks'])
    alternatives = {}
    for offset, column in enumerate(['rg_aeqd_km', 'rg_laea_largest_km'], 2):
        mask = table[column].between(lo, hi)
        alternative = table[mask]
        alternatives[column] = intervals(alternative[column], alternative.Country, seed+offset, n_boot)
        alternatives[column]['entered_relative_to_primary'] = int((mask & ~selected).sum())
        alternatives[column]['left_relative_to_primary'] = int((selected & ~mask).sum())
    goodness = powerlaw_gof(sample.rg_laea_km.to_numpy(), lo, hi, CONFIG['gof_draws'], seed+4)
    goodness['interpretation'] = 'Descriptive iid diagnostic; not spatially calibrated.'
    geometry = dict(n_invalid_selected_topology=int((sample.topology_valid != True).sum()),
                    selected_max_center_distance_km=float(sample.max_center_distance_km.max()),
                    full_source_max_center_distance_km=float(table.max_center_distance_km.max()),
                    selected_aeqd_over_laea=quantiles(sample.rg_aeqd_km/sample.rg_laea_km),
                    selected_laea_over_geodesic_area=quantiles(sample.area_laea_km2/sample.area_geodesic_km2),
                    selected_laea_over_source_area=quantiles(sample.area_laea_km2/sample.Lake_area),
                    full_source_holes=int(table.n_holes.sum()), full_source_shells=int(table.n_shells.sum()),
                    selected_with_holes=int((sample.n_holes > 0).sum()),
                    selected_with_multiple_shells=int((sample.n_shells > 1).sum()))
    coverage = dict(n_matched=len(matched), n_unmatched=len(sample)-len(matched),
                    fraction=len(matched)/len(sample), n_multiple_matches=int((multiplicity > 1).sum()))
    gates = dict(complete_basin_coverage=len(matched) == len(sample),
                 valid_selected_topology=geometry['n_invalid_selected_topology'] == 0,
                 local_extent_at_most_200km=geometry['selected_max_center_distance_km'] <= 200,
                 relative_projection_discrepancy_at_most_0_001=bool(np.max(np.abs(sample.rg_aeqd_km/sample.rg_laea_km-1)) <= .001),
                 iid_gof_not_rejected=not goodness['ruled_out'])
    nat = sample[sample.Lake_type == 1]
    output_result = dict(data_kind='Outcome-exposed global follow-up', config_sha256=sha(CONFIG_PATH),
                        derived_table_sha256=sha(TABLE), n_input=len(table),
                        primary_all_lakes_country_blocks=full, matched_lakes_basin_blocks=hydrological,
                        matched_exponent_verdict=verdict, global_positive_interpretation_allowed=all(gates.values()) and verdict == 'conditional exponent equivalence',
                        qualification_gates=gates, basin_coverage=coverage, geometry=geometry,
                        alternatives=alternatives, goodness_of_fit=goodness,
                        lake_type_1=dict(n=len(nat), zeta_R=fit_mean_log(np.log(nat.rg_laea_km).mean()), note='Not certified natural lakes; point estimate only'))
    original_path = ROOT/'results/lake-gyration-2026-10-09/implementation/data/derived/hydrolakes_rg.csv'
    if original_path.exists():
        original = pd.read_csv(original_path, usecols=['Hylak_id', 'rg_km'])
        if original.Hylak_id.duplicated().any() or set(original.Hylak_id) != set(table.Hylak_id):
            raise ValueError('Original/full-current ID mismatch')
        original_ids = set(original.loc[original.rg_km.between(lo, hi), 'Hylak_id'])
        new_ids = set(sample.Hylak_id)
        joined = sample.merge(original, on='Hylak_id', validate='one_to_one')
        output_result['original_comparison'] = dict(n_original_selected=len(original_ids),
             entered=len(new_ids-original_ids), left=len(original_ids-new_ids),
             current_selected_laea_over_epsg6933_radius=quantiles(joined.rg_laea_km/joined.rg_km),
             original_table_sha256=sha(original_path))
    (output/'result.json').write_text(json.dumps(output_result, indent=2, allow_nan=False)+'\n')
    plot(sample.rg_laea_km.to_numpy(), full['zeta_R'], output)
    return output_result


def plot(radii, zeta, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    x = np.sort(radii)
    lo, hi = CONFIG['rg_range_km']
    grid = np.geomspace(lo, hi, 250)
    survival = lambda z: (grid**(-z)-hi**(-z))/(lo**(-z)-hi**(-z))
    fig, ax = plt.subplots(figsize=(7, 4.6), constrained_layout=True)
    ax.plot(x, (len(x)-np.arange(len(x)))/len(x), label='HydroLAKES: full local geometry', lw=1.5)
    ax.plot(grid, survival(zeta), label=f'Bounded fit: ζ = {zeta:.3f}', ls='--')
    ax.plot(grid, survival(2), label='Territory prediction: ζ = 2', ls=':')
    ax.set(xscale='log', yscale='log', xlabel='Local area-weighted radius of gyration (km)',
           ylabel='Fraction above radius, conditional on 1–20 km', ylim=(1/len(x), 1), xlim=(1, 20))
    ax.legend(fontsize=9)
    fig.savefig(output/'survival.png', dpi=180)
    fig.savefig(output/'survival.svg')
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--derive', action='store_true')
    parser.add_argument('--synthetic', type=float)
    parser.add_argument('--output', type=Path, default=ROOT/'results/lake-metric-followup-2026-10-09')
    args = parser.parse_args()
    start = time.monotonic()
    if args.synthetic is not None:
        rng = np.random.default_rng(CONFIG['seed'])
        radii = sample_powerlaw(20000, args.synthetic+1, 1, 20, rng)
        result = intervals(radii, np.arange(len(radii)) % 100, CONFIG['seed'], CONFIG['bootstrap_draws'])
        result.update(data_kind='Synthetic only', true_zeta_R=args.synthetic, verdict=decision(result))
        print(json.dumps(result, indent=2))
        return
    args.output.mkdir(parents=True, exist_ok=True)
    if args.derive:
        derive()
    receipt = json.loads(TABLE.with_suffix('.receipt.json').read_text())
    if sha(TABLE) != receipt['sha256'] or sha(CONFIG_PATH) != receipt['config_sha256']:
        raise ValueError('Derived table/config checksum mismatch')
    table = pd.read_csv(TABLE, keep_default_na=False)
    # CSV stores booleans on selected rows and empty strings elsewhere.
    table['topology_valid'] = table.topology_valid.map({'True': True, 'False': False, '': None})
    result = analyse(table, args.output)
    import pyproj, scipy, shapefile, shapely
    execution = dict(completed_utc=datetime.now(timezone.utc).isoformat(), seconds=time.monotonic()-start,
                     python=platform.python_version(), platform=platform.platform(), numpy=np.__version__,
                     scipy=scipy.__version__, pandas=pd.__version__, pyproj=pyproj.__version__,
                     PROJ=pyproj.proj_version_str, pyshp=shapefile.__version__, shapely=shapely.__version__)
    (args.output/'execution.json').write_text(json.dumps(execution, indent=2)+'\n')
    (args.output/'derived-table-receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
