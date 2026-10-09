"""Pre-registered test: lake radius of gyration as a two-dimensional territory.

Implements configs/prereg_2026-10-08_lake_gyration.json. HydroLAKES was not
reachable when the test was registered; run this where it is:

  1. Download HydroLAKES_polys_v10_shp.zip (Messager et al. 2016, CC BY 4.0)
     from https://www.hydrosheds.org/products/hydrolakes and unzip it; record
     the checksum and provenance in data/SOURCES.md.
  2. pip install pyshp pyproj
  3. python experiments/run_lake_gyration.py --shapefile <path>/HydroLAKES_polys_v10.shp
     (computes radii of gyration into data/derived/hydrolakes_rg.csv, then analyses)
     or, once that table exists: --table data/derived/hydrolakes_rg.csv

Radius of gyration is computed from each polygon's outer ring after projecting
to EPSG:6933 (equal area). Lakes are selected on the radius itself, 1-20 km
(Amendment 1: selecting on area biased the radius fit in synthetic checks). Writes results/lake_gyration.json. --synthetic runs
the analysis on a simulated table, for checking only.
"""
from pathlib import Path
import argparse
import json
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from gof import fit_powerlaw                        # noqa: E402

PREREG = json.loads((ROOT / 'configs' / 'prereg_2026-10-08_lake_gyration.json').read_text())
SEED, N_BOOT = 20261008, 1000
RG_RANGE = (1.0, 20.0)              # km, Amendment 1 of the preregistration (select on R itself)
MARGIN = PREREG['decision_rule']['equivalence_margin']


def ring_gyration(x, y):
    """Area and radius of gyration of a simple polygon ring (any orientation)."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    x, y = x - x.mean(), y - y.mean()                # reduce round-off
    x1, y1 = np.roll(x, -1), np.roll(y, -1)
    cross = x * y1 - x1 * y
    a = cross.sum() / 2
    if abs(a) < 1e-300:
        return 0.0, 0.0
    cx = ((x + x1) * cross).sum() / (6 * a)
    cy = ((y + y1) * cross).sum() / (6 * a)
    ixx = ((y * y + y * y1 + y1 * y1) * cross).sum() / 12     # ∫ y^2 dA (signed with a)
    iyy = ((x * x + x * x1 + x1 * x1) * cross).sum() / 12     # ∫ x^2 dA
    rg2 = (ixx + iyy) / a - (cx * cx + cy * cy)
    return abs(a), float(np.sqrt(max(rg2, 0.0)))


def table_from_shapefile(path, out):
    import shapefile                                  # pyshp
    try:
        from pyproj import Transformer
        tr = Transformer.from_crs('EPSG:4326', 'EPSG:6933', always_xy=True)
        project, projection = (lambda lon, lat: tr.transform(lon, lat)), 'EPSG:6933'
    except ImportError:
        sys.exit('pyproj is required for the pre-registered EPSG:6933 projection (pip install pyproj).')
    rows = []
    with shapefile.Reader(str(path)) as shp:
        fields = [f[0] for f in shp.fields[1:]]
        for sr in shp.iterShapeRecords():
            rec = dict(zip(fields, sr.record))
            pts = np.asarray(sr.shape.points)
            parts = list(sr.shape.parts) + [len(pts)]
            best = (0.0, 0.0)
            for s, e in zip(parts[:-1], parts[1:]):     # outer ring = largest-area ring; holes ignored
                px, py = project(pts[s:e, 0], pts[s:e, 1])
                best = max(best, ring_gyration(px, py))
            rows.append(dict(Hylak_id=rec.get('Hylak_id'), Lake_area=rec.get('Lake_area'),
                             Lake_type=rec.get('Lake_type'), Country=rec.get('Country'),
                             area_proj_km2=best[0] / 1e6, rg_km=best[1] / 1e3))
    t = pd.DataFrame(rows)
    out.parent.mkdir(parents=True, exist_ok=True)
    t.to_csv(out, index=False)
    return t, projection


def fit_zeta(r, lo, hi):
    return fit_powerlaw(r, lo, hi)['params']['alpha'] - 1


def analyse(t, rng, n_boot=N_BOOT):
    r_lo, r_hi = RG_RANGE
    s = t[(t.rg_km >= r_lo) & (t.rg_km <= r_hi)]
    r = s.rg_km.to_numpy()
    zeta = fit_zeta(r, r_lo, r_hi)
    boot = np.array([fit_zeta(rng.choice(r, len(r)), r_lo, r_hi) for _ in range(n_boot)])
    ci = [float(v) for v in np.percentile(boot, [2.5, 97.5])]
    D = float(np.polyfit(np.log(s.rg_km), np.log(s.Lake_area), 1)[0])
    out = dict(n=len(r), rg_range_km=[float(r_lo), float(r_hi)],
               zeta_R=zeta, zeta_R_ci95=ci, area_radius_dimension_D=D,
               implied_zeta_A_if_territory=2 / D)
    intervals = [ci]
    if 'Country' in s and s.Country.notna().any():       # not pre-registered: country-block bootstrap
        groups = [g.rg_km.to_numpy() for _, g in s.groupby('Country')]
        bb = [fit_zeta(np.concatenate([groups[i] for i in rng.integers(len(groups), size=len(groups))]), r_lo, r_hi)
              for _ in range(min(n_boot, 500))]
        out['country_block_ci95_not_preregistered'] = [float(v) for v in np.percentile(bb, [2.5, 97.5])]
    band = (2 - MARGIN, 2 + MARGIN)
    if all(band[0] <= a and b <= band[1] for a, b in intervals):
        out['verdict'] = 'supports H_territory'
    elif any(b < band[0] or a > band[1] for a, b in intervals):
        out['verdict'] = 'against H_territory'
    else:
        out['verdict'] = 'inconclusive'
    if 'Lake_type' in s:
        nat = s[s.Lake_type == 1].rg_km.to_numpy()
        if len(nat) > 100:
            out['natural_lakes_only_zeta_R'] = fit_zeta(nat, r_lo, r_hi)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--shapefile')
    ap.add_argument('--table')
    ap.add_argument('--synthetic', type=float, help='simulate radii with this zeta (checking only)')
    ap.add_argument('--output', default=str(ROOT / 'results' / 'lake_gyration.json'))
    ap.add_argument('--n-boot', type=int, default=N_BOOT)
    args = ap.parse_args(argv)
    rng = np.random.default_rng(SEED)
    projection = None
    if args.synthetic:
        rg = 0.3 * (1 - rng.random(200000)) ** (-1 / args.synthetic)
        t = pd.DataFrame(dict(rg_km=rg, Lake_area=1.9 * rg ** 2 * np.exp(rng.normal(0, 0.2, len(rg))), Lake_type=1))
        res = analyse(t, rng, args.n_boot)
        print(json.dumps(res, indent=1))
        return res
    if args.shapefile:
        t, projection = table_from_shapefile(args.shapefile, ROOT / 'data' / 'derived' / 'hydrolakes_rg.csv')
    elif args.table and Path(args.table).exists():
        t = pd.read_csv(args.table)
    else:
        sys.exit('Lake data not found. See the instructions at the top of this script.')
    res = dict(preregistration='configs/prereg_2026-10-08_lake_gyration.json', projection=projection or 'from table',
               **analyse(t, rng, args.n_boot))
    Path(args.output).write_text(json.dumps(res, indent=2))
    print(json.dumps(res, indent=1))
    return res


if __name__ == '__main__':
    main()
