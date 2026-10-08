"""Does the verdict depend on which quantity is called the resource?

Exploratory and post hoc: these resources were examined after the pilot
results were known. The analysis motivates an a priori resource rule; it is
not confirmation of one.

Earthquakes. Equal resource per log size class with resource = coordinate
requires a survival exponent zeta = 1 in that quantity. Under
N(>=M) ∝ 10^(-bM), a quantity X ∝ 10^(cM) has zeta_X = b/c. Conversions:
  seismic moment, M0 ∝ 10^(1.5M) (Hanks & Kanamori 1979): zeta = 2b/3;
  rupture area, self-similar constant stress drop (Kanamori & Anderson 1975),
    A ∝ M0^(2/3) ∝ 10^M: zeta_A = b;
  rupture area, Wells & Coppersmith (1994) all-slip regression
    M = 4.07 + 0.98 log10 A: zeta_A = 0.98 b;
  rupture area for large continental events, Hanks & Bakun (2002)
    M = (4/3) log10 A + 3.07 above A ≈ 537 km^2 (M ≈ 6.7): zeta_A = 4b/3.
These are magnitude conversions, not measured rupture areas.

Flares. The direct test of equal fluence per log fluence (Hudson 1991,
alpha = 2) fits the fluence distribution itself, with the lower cutoff
chosen by minimum KS distance (Clauset et al. 2009). Background subtraction
here is a crude approximation, fluence minus background irradiance times
event duration; the catalogue has no background-subtracted fluence field.

Outputs results/resource_choice.json.
"""
from pathlib import Path
import json
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from orthopolity import rounded_gr_b                    # noqa: E402
from gof import fit_powerlaw, powerlaw_gof              # noqa: E402

RAW, OUT = ROOT / 'data' / 'raw', ROOT / 'results'
SPEC = json.loads((ROOT / 'configs' / 'pilot.json').read_text())
B = SPEC['bootstrap_replicates']
N_BOOT_GOF = 500
XMIN_QUANTILES = np.linspace(0.30, 0.97, 120)


def interval(draws):
    return [float(v) for v in np.percentile(draws, [2.5, 97.5])]


def block_resample(df, col, rng):
    groups = [g for _, g in df.groupby(col, sort=True)]
    return pd.concat([groups[i] for i in rng.integers(len(groups), size=len(groups))], ignore_index=True)


def earthquakes(rng):
    a = pd.read_csv(RAW / 'usgs_2010_2024.csv')
    a['date'] = pd.to_datetime(a.time, utc=True)
    a = a[(a.date < pd.Timestamp('2025-01-01', tz='UTC')) & a.magType.str.startswith('mw', na=False)].copy()
    a['year'] = a.date.dt.year
    conversions = {'seismic_moment': 1.5, 'rupture_area_self_similar': 1.0,
                   'rupture_area_wells_coppersmith': 1 / 0.98}
    out = []
    for cutoff in [5.5, 6.0, 6.5]:
        b, n = rounded_gr_b(a.mag, cutoff)
        draws = np.array([rounded_gr_b(block_resample(a, 'year', rng).mag, cutoff)[0] for _ in range(B)])
        row = dict(cutoff=cutoff, n=n, b=b, b_ci=interval(draws))
        for name, c in conversions.items():
            row[f'zeta_{name}'] = b / c
            row[f'zeta_{name}_ci'] = interval(draws / c)
        out.append(row)
    b, n = rounded_gr_b(a.mag, 6.7)
    draws = np.array([rounded_gr_b(block_resample(a, 'year', rng).mag, 6.7)[0] for _ in range(B)])
    large = dict(cutoff=6.7, n=n, b=b, b_ci=interval(draws),
                 zeta_rupture_area_hanks_bakun=4 * b / 3, zeta_rupture_area_hanks_bakun_ci=interval(4 * draws / 3),
                 note='Hanks-Bakun scaling is for continental strike-slip events; the catalogue mixes mechanisms.')
    return dict(cases=out, large_event_width_saturation=large,
                caveat='Areas are converted from magnitudes; no rupture area was measured. '
                       'Zeta of an area proxy is a reparametrization of b, so these rows share one estimate.')


def csn_xmin(x):
    """Lower cutoff minimizing the KS distance of the unbounded continuous power law."""
    x = np.sort(x)
    best = None
    for xmin in np.unique(np.quantile(x, XMIN_QUANTILES)):
        t = x[x >= xmin]
        alpha = 1 + len(t) / np.log(t / xmin).sum()
        cdf = 1 - (t / xmin) ** (1 - alpha)
        ks = np.max(np.abs(np.arange(1, len(t) + 1) / len(t) - cdf))
        if best is None or ks < best[0]:
            best = (ks, float(xmin))
    return best[1]


def flares(rng):
    a = pd.concat([pd.read_csv(RAW / f'noaa_{y}.csv') for y in SPEC['noaa']['years']], ignore_index=True)
    a = a[a.peak_saturated == 0].copy()
    a['month'] = pd.to_datetime(a.start_time).dt.strftime('%Y-%m')
    duration = (pd.to_datetime(a.end_time) - pd.to_datetime(a.start_time)).dt.total_seconds()
    resources = {
        'end_fluence_as_supplied': a.integrated_irrad_end,
        'end_fluence_minus_background_times_duration': a.integrated_irrad_end - a.background_irrad * duration,
        'peak_irradiance': a.xrsb_irrad,
    }
    out = {}
    for name, values in resources.items():
        d = a.assign(x=values)
        d = d[np.isfinite(d.x) & (d.x > 0)]
        xmin = csn_xmin(d.x.to_numpy())
        t = d[d.x >= xmin]
        hi = float(t.x.max()) * (1 + 1e-9)
        gof = powerlaw_gof(t.x.to_numpy(), xmin, hi, n_boot=N_BOOT_GOF, seed=SPEC['seed'])
        draws = []
        for _ in range(B):
            s = block_resample(t, 'month', rng)
            draws.append(fit_powerlaw(s.x.to_numpy(), xmin, hi)['params']['alpha'])
        out[name] = dict(n_positive=len(d), xmin=xmin, n_tail=len(t), alpha=gof['alpha'],
                         alpha_ci_month_blocks=interval(draws), ks=gof['ks'], gof_p=gof['p_value'],
                         equal_resource_alpha=2.0 if name != 'peak_irradiance' else None)
    out['note'] = ('Fluence is GOES 1-8 Angstrom band irradiance integrated over the event, not total flare '
                   'energy. Peak irradiance is the coordinate, not a resource; its exponent is listed for comparison.')
    return out


def main():
    rng = np.random.default_rng(SPEC['seed'])
    result = dict(status='Exploratory and post hoc; resources examined after the pilot results were known',
                  earthquakes=earthquakes(rng), flares=flares(rng))
    (OUT / 'resource_choice.json').write_text(json.dumps(result, indent=2))
    eq = result['earthquakes']['cases'][0]
    print(f"Earthquakes M>={eq['cutoff']}: b={eq['b']:.3f} {np.round(eq['b_ci'], 3).tolist()}; "
          f"zeta moment={eq['zeta_seismic_moment']:.3f}, zeta area (self-similar)={eq['zeta_rupture_area_self_similar']:.3f}")
    lg = result['earthquakes']['large_event_width_saturation']
    print(f"  M>=6.7: b={lg['b']:.3f}; Hanks-Bakun zeta_A={lg['zeta_rupture_area_hanks_bakun']:.3f} "
          f"{np.round(lg['zeta_rupture_area_hanks_bakun_ci'], 3).tolist()}")
    for name, r in result['flares'].items():
        if isinstance(r, dict):
            print(f"Flares {name}: xmin={r['xmin']:.3e} n={r['n_tail']} alpha={r['alpha']:.3f} "
                  f"{np.round(r['alpha_ci_month_blocks'], 3).tolist()} KS p={r['gof_p']:.3f}")


if __name__ == '__main__':
    main()
