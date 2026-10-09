"""Pre-registered test: b-value against hypocentre correlation dimension.

Implements configs/prereg_2026-10-08_volumetric_seismicity.json. Regional
catalogues were not reachable when the test was registered; run this where
they are:

  1. Obtain a relocated catalogue with hypocentres and a cluster identifier,
     for example the Southern California relocated catalogue (Hauksson, Yang
     and Shearer 2012, updated; SCEDC) with clusters from nearest-neighbour
     declustering (Zaliapin and Ben-Zion 2013) or a published swarm list.
     Record the catalogue version and cluster definition in the
     preregistration before computing anything.
  2. Save a CSV with columns cluster, mag and either x_km, y_km, z_km or
     latitude, longitude, depth_km.
  3. python experiments/run_volumetric_b.py --input <file>.csv

Correlation dimension is fitted between the 200th-closest pair distance (and
three times the median location error, if a loc_err_km column is given) and
0.1 of the 90th-percentile pair distance; clusters whose range spans less than
a factor of 3 are excluded (Amendment 1 of the preregistration).

Writes results/volumetric_b.json. --synthetic {territory,fdsoc} runs the
pipeline on simulated clusters, for checking only.
"""
from pathlib import Path
import argparse
import json
import sys

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from scipy.spatial.distance import pdist

ROOT = Path(__file__).resolve().parents[1]
SEED, N_BOOT, N_BOOT_REG = 20261008, 500, 1000
MIN_EVENTS, MIN_CLUSTERS, MIN_D2_RANGE = 200, 10, 0.5
D2_CAP = 3000          # hypocentres used for the correlation integral (computational cap)
MIN_SCALING_RATIO = 3  # Amendment 1: r_max / r_min of the fitted range
KM_PER_DEG = 111.195


def b_value(m, mc, rng, n_boot=N_BOOT):
    """Aki-Utsu maximum likelihood with 0.1 binning correction, bootstrap SE."""
    est = lambda x: np.log10(np.e) / (x.mean() - (mc - 0.05))        # noqa: E731
    b = est(m)
    se = np.std([est(rng.choice(m, len(m))) for _ in range(n_boot)], ddof=1)
    return float(b), float(se)


def completeness(m):
    """Maximum-curvature magnitude + 0.2."""
    vals, cnt = np.unique(np.round(m, 1), return_counts=True)
    return float(vals[np.argmax(cnt)] + 0.2)


def fit_range(d, loc_err=0.0):
    """Amendment 1: from the 200th-closest pair distance (and 3x location error) to 0.1 of
    the 90th-percentile pair distance. Synthetic planes and volumes give 2 and 3 within 0.1."""
    lo = max(d[min(199, len(d) - 1)], 3 * loc_err)
    return lo, 0.1 * np.quantile(d, 0.9)


def correlation_dimension(xyz, r_range=None, loc_err=0.0):
    d = np.sort(pdist(xyz))
    d = d[d > 0]                                    # duplicated hypocentres from resampling
    lo, hi = r_range or fit_range(d, loc_err)
    if hi < MIN_SCALING_RATIO * lo:
        return np.nan, (lo, hi)
    r = np.geomspace(lo, hi, 15)
    c = np.searchsorted(d, r) / len(d)
    return float(np.polyfit(np.log(r), np.log(c), 1)[0]), (lo, hi)


def d2_with_se(xyz, rng, n_boot=N_BOOT, loc_err=0.0):
    if len(xyz) > D2_CAP:
        xyz = xyz[rng.choice(len(xyz), D2_CAP, replace=False)]
    d2, r_range = correlation_dimension(xyz, loc_err=loc_err)
    if not np.isfinite(d2):
        return np.nan, np.nan
    boots = [correlation_dimension(xyz[rng.integers(len(xyz), size=len(xyz))], r_range)[0] for _ in range(n_boot)]
    return d2, float(np.nanstd(boots, ddof=1))


def coordinates(g):
    if {'x_km', 'y_km', 'z_km'} <= set(g.columns):
        return g[['x_km', 'y_km', 'z_km']].to_numpy(float)
    depth = g['depth_km'] if 'depth_km' in g else g['depth']
    lat0, lon0 = g.latitude.mean(), g.longitude.mean()
    return np.column_stack([KM_PER_DEG * np.cos(np.radians(lat0)) * (g.longitude - lon0),
                            KM_PER_DEG * (g.latitude - lat0), depth]).astype(float)


def deming(x, y, vx, vy):
    """Errors-in-variables slope and intercept with error-variance ratio vy/vx."""
    delta = np.mean(vy) / np.mean(vx)
    sxx, syy = np.var(x, ddof=1), np.var(y, ddof=1)
    sxy = np.cov(x, y, ddof=1)[0, 1]
    slope = (syy - delta * sxx + np.sqrt((syy - delta * sxx) ** 2 + 4 * delta * sxy ** 2)) / (2 * sxy)
    return float(slope), float(np.mean(y) - slope * np.mean(x))


def analyse(cat, rng, n_boot_d2=N_BOOT):
    rows = []
    for cid, g in cat.groupby('cluster'):
        m = np.round(g.mag.to_numpy(float), 1)
        mc = completeness(m)
        above = g[m >= mc - 1e-9]
        if len(above) < MIN_EVENTS:
            continue
        loc_err = float(above.loc_err_km.median()) if 'loc_err_km' in above else 0.0
        d2, d2_se = d2_with_se(coordinates(above), rng, n_boot_d2, loc_err)
        if not np.isfinite(d2):
            continue                                # scaling range too short (Amendment 1)
        b, b_se = b_value(np.round(above.mag.to_numpy(float), 1), mc, rng)
        rows.append(dict(cluster=str(cid), n=len(above), mc=mc, b=b, b_se=b_se, D2=d2, D2_se=d2_se))
    t = pd.DataFrame(rows)
    out = dict(clusters=rows, n_clusters=len(t))
    if len(t) < MIN_CLUSTERS or t.D2.max() - t.D2.min() < MIN_D2_RANGE:
        out['verdict'] = 'inconclusive (too few clusters or too narrow a D2 range)'
        return out
    x, y, vx, vy = t.D2.to_numpy(), t.b.to_numpy(), t.D2_se.to_numpy() ** 2, t.b_se.to_numpy() ** 2
    slope, icpt = deming(x, y, vx, vy)
    bs = []
    for _ in range(N_BOOT_REG):
        i = rng.integers(len(t), size=len(t))
        if np.ptp(x[i]) > 0:
            bs.append(deming(x[i], y[i], vx[i], vy[i]))
    bs = np.array(bs)
    s_ci = np.percentile(bs[:, 0], [2.5, 97.5]).tolist()
    i_ci = np.percentile(bs[:, 1], [2.5, 97.5]).tolist()
    mb = [rng.choice(y, len(y)).mean() for _ in range(N_BOOT_REG)]
    mb_ci = np.percentile(mb, [2.5, 97.5]).tolist()
    out.update(slope=slope, slope_ci95=s_ci, intercept=icpt, intercept_ci95=i_ci, mean_b=float(y.mean()),
               mean_b_ci95=mb_ci, D2_range=[float(x.min()), float(x.max())])
    terr = s_ci[0] <= 0.5 <= s_ci[1] and not (s_ci[0] <= 0 <= s_ci[1]) and i_ci[0] <= 0 <= i_ci[1]
    fdsoc = s_ci[0] <= 0 <= s_ci[1] and not (s_ci[0] <= 0.5 <= s_ci[1]) and mb_ci[0] <= 1 <= mb_ci[1]
    out['verdict'] = 'supports H_territory' if terr else 'supports H_fdsoc' if fdsoc else 'inconclusive'
    return out


def synthetic(kind, rng, n_clusters=14, n=7000):
    frames = []
    for c in range(n_clusters):
        thick = 0.05 if c % 2 == 0 else 30.0                    # planes (D = 2) and volumes (D = 3)
        xyz = np.column_stack([rng.uniform(0, 30, n), rng.uniform(0, 30, n), rng.uniform(0, thick, n)])
        d_true = 2 if thick < 1 else 3
        b = d_true / 2 if kind == 'territory' else 1.0
        m = 1.0 + rng.exponential(np.log10(np.e) / b, n)
        frames.append(pd.DataFrame(dict(cluster=c, mag=np.round(m, 1), x_km=xyz[:, 0], y_km=xyz[:, 1], z_km=xyz[:, 2])))
    return pd.concat(frames, ignore_index=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--input')
    ap.add_argument('--synthetic', choices=['territory', 'fdsoc'])
    ap.add_argument('--output', default=str(ROOT / 'results' / 'volumetric_b.json'))
    args = ap.parse_args(argv)
    rng = np.random.default_rng(SEED)
    if args.synthetic:
        res = analyse(synthetic(args.synthetic, rng), rng, n_boot_d2=50)
        print(json.dumps({k: v for k, v in res.items() if k != 'clusters'}, indent=1))
        return res
    if not args.input or not Path(args.input).exists():
        sys.exit('Catalogue not found. See the instructions at the top of this script.')
    res = dict(preregistration='configs/prereg_2026-10-08_volumetric_seismicity.json', input=args.input,
               **analyse(pd.read_csv(args.input), rng))
    Path(args.output).write_text(json.dumps(res, indent=2))
    print(json.dumps({k: v for k, v in res.items() if k != 'clusters'}, indent=1))
    return res


if __name__ == '__main__':
    main()
