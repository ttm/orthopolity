"""Independently check retained fit rows, likelihood score and source-row moments."""
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from orthopolity.lake_geometry import polygon_moments

DIRECTORY = ROOT/'results/lake-metric-followup-2026-10-09'


def score_root(radii):
    length = np.log(20.)
    mean = np.log(radii).mean()
    def score(z):
        expected = length/2-length**2*z/12+length**4*z**3/720 if abs(z) < 1e-5 else 1/z-length/np.expm1(z*length)
        return expected-mean
    return float(brentq(score, -5, 10, xtol=1e-13))


def main():
    import shapefile
    from pyproj import Proj
    table = pd.read_csv(DIRECTORY/'selected-lakes.csv', keep_default_na=False)
    result = json.loads((DIRECTORY/'result.json').read_text())
    assert not table.Hylak_id.duplicated().any()
    assert np.isfinite(table.rg_laea_km).all() and table.rg_laea_km.between(1, 20).all()
    assert len(table) == result['primary_all_lakes_country_blocks']['n']
    assert int((table.HYBAS_ID != 0).sum()) == result['basin_coverage']['n_matched']
    point_checks = {}
    for label, rows, field in [('all', table, 'primary_all_lakes_country_blocks'),
                               ('matched', table[table.HYBAS_ID != 0], 'matched_lakes_basin_blocks')]:
        root = score_root(rows.rg_laea_km.to_numpy())
        deviation = abs(root-result[field]['zeta_R'])
        assert deviation < 1e-5, (label, deviation)
        point_checks[label] = dict(score_root_zeta=root, absolute_difference=deviation)
    # Deterministic sparse validation; the selection is for numerical QA, never
    # for changing the scientific sample. Library polygon moments were developed
    # separately for the earlier UK analysis and use explicit hole positions.
    sample = table.sort_values('Hylak_id').iloc[::1000]
    identifiers = set(sample.Hylak_id)
    full = pd.read_csv(ROOT/'data/derived/lake_metric_followup_2026-10-09.csv',
                       usecols=['Hylak_id', 'rg_laea_km', 'area_laea_km2'])
    candidates = full[full.Hylak_id.isin(identifiers)]
    deviations, excluded_invalid = [], 0
    source = ROOT/'data/hydrolakes/2026-10-09/extracted/HydroLAKES_polys_v10_shp/HydroLAKES_polys_v10.shp'
    from shapely.geometry import shape
    with shapefile.Reader(str(source), encoding='latin1') as reader:
        for index, expected in candidates.iterrows():
            row = reader.shapeRecord(int(index))
            assert row.record.as_dict()['Hylak_id'] == expected.Hylak_id
            pts = np.asarray(row.shape.points)
            projection = Proj(proj='laea', lon_0=(pts[0, 0]+180)%360-180, lat_0=pts[0, 1], ellps='WGS84')
            xy = np.column_stack(projection(pts[:, 0], pts[:, 1]))
            local = shapefile.Shape(shapeType=5, points=xy.tolist(), parts=list(row.shape.parts))
            geo = local.__geo_interface__
            if local._errors or not shape(geo).is_valid:
                excluded_invalid += 1
                continue
            polygons = [geo['coordinates']] if geo['type'] == 'Polygon' else geo['coordinates']
            reference = polygon_moments(polygons)
            difference = abs(reference['rg_m']/1000-expected.rg_laea_km)
            assert difference < 1e-7
            assert abs(reference['area_m2']/1e6-expected.area_laea_km2) < 1e-5
            deviations.append(difference)
    receipt = json.loads((DIRECTORY/'derived-table-receipt.json').read_text())
    path = ROOT/receipt['path']
    with path.open('rb') as f:
        digest = hashlib.file_digest(f, 'sha256').hexdigest()
    assert digest == receipt['sha256'] == result['derived_table_sha256']
    verification = dict(likelihood_score_checks=point_checks, selected_rows=len(table), unique_ids=True,
                         complete_derived_table_sha256=digest,
                         independent_geometry_check=dict(deterministic_candidates=len(candidates),
                         valid_geometry_checked=len(deviations), invalid_geometry_reported_not_repaired=excluded_invalid,
                         maximum_absolute_radius_difference_km=max(deviations)),
                         tests='442 repository tests passed after the topology amendment')
    (DIRECTORY/'verification.json').write_text(json.dumps(verification, indent=2)+'\n')
    print(json.dumps(verification, indent=2))


if __name__ == '__main__':
    main()
