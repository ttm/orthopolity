"""Pre-registered test: flare ribbon areas, space-filling territory or fractal area.

Implements configs/prereg_2026-10-08_flare_ribbons.json. The ribbon database
was not reachable when the test was registered; run this where it is:

  1. Download the RibbonDB flare table (Kazachenko et al. 2017, ApJ 845, 49;
     reported host http://solarmuri.ssl.berkeley.edu/~kazachenko/RibbonDB/).
  2. Save it as CSV, one row per flare, under data/raw/ (record its SHA-256 in
     data/snapshot_checksums.json and its provenance in data/SOURCES.md).
  3. Before running, record in the preregistration's prior_exposure whether
     a published ribbon-area index has been read.
  4. python experiments/run_flare_ribbons.py --input data/raw/<file>.csv \\
         --column <ribbon area column> [--secondary <reconnection flux column>]

Writes results/flare_ribbons.json. --synthetic ALPHA runs the pipeline on a
simulated sample, for checking only.
"""
from pathlib import Path
import argparse
import json
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from gof import csn_powerlaw, powerlaw_gof, fit_powerlaw, fit_lognormal, vuong   # noqa: E402

PREREG = json.loads((ROOT / 'configs' / 'prereg_2026-10-08_flare_ribbons.json').read_text())
H = {k: v['alpha_area'] for k, v in PREREG['hypotheses'].items() if isinstance(v, dict)}
SEED, N_BOOT, N_GOF = 20261008, 2000, 500


def verdict(lo, hi, gof_p):
    inside = {k: bool(lo <= v <= hi) for k, v in H.items()}
    if gof_p <= 0.1:
        return inside, 'inconclusive (power law rejected)'
    if inside['H_territory'] and not inside['H_fractal']:
        return inside, 'supports H_territory'
    if inside['H_fractal'] and not inside['H_territory']:
        return inside, 'supports H_fractal'
    return inside, 'inconclusive'


def analyse(x, rng, n_boot=N_BOOT, n_gof=N_GOF):
    x = np.asarray(x, float)
    x = x[np.isfinite(x) & (x > 0)]
    fit = csn_powerlaw(x)
    boot = np.array([csn_powerlaw(rng.choice(x, len(x)))['alpha'] for _ in range(n_boot)])
    lo, hi = (float(v) for v in np.percentile(boot, [2.5, 97.5]))
    tail = x[x >= fit['x_min']]
    top = float(tail.max()) * (1 + 1e-9)
    gof = powerlaw_gof(tail, fit['x_min'], top, n_boot=n_gof, seed=SEED)
    ln = vuong(tail, fit_powerlaw(tail, fit['x_min'], top), fit_lognormal(tail, fit['x_min'], top),
               fit['x_min'], top)
    inside, v = verdict(lo, hi, gof['p_value'])
    return dict(n=len(x), **fit, alpha_ci95=[lo, hi], gof_p=gof['p_value'],
                lognormal_comparison=dict(favours=ln['favours'], p_value=ln['p_value']),
                hypotheses_in_interval=inside, verdict=v)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--input')
    ap.add_argument('--column')
    ap.add_argument('--secondary')
    ap.add_argument('--synthetic', type=float, help='simulate a Pareto sample with this alpha (checking only)')
    ap.add_argument('--output', default=str(ROOT / 'results' / 'flare_ribbons.json'))
    ap.add_argument('--n-boot', type=int, default=N_BOOT)
    args = ap.parse_args(argv)
    rng = np.random.default_rng(SEED)
    if args.synthetic:
        core = (1 - rng.random(3000)) ** (-1 / (args.synthetic - 1))
        keep = rng.random(3000) < np.clip(np.log(core) / np.log(3), 0.05, 1)   # incomplete small events
        result = dict(synthetic_alpha=args.synthetic, primary=analyse(core[keep], rng, args.n_boot, 200))
        print(json.dumps(result['primary'], indent=1))
        return result
    if not args.input or not Path(args.input).exists():
        sys.exit('Ribbon data not found. See the instructions at the top of this script.')
    table = pd.read_csv(args.input)
    result = dict(preregistration='configs/prereg_2026-10-08_flare_ribbons.json', input=args.input,
                  primary=dict(column=args.column, **analyse(table[args.column], rng, args.n_boot)))
    if args.secondary:
        result['secondary'] = dict(column=args.secondary, **analyse(table[args.secondary], rng, args.n_boot))
    Path(args.output).write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=1))
    return result


if __name__ == '__main__':
    main()
