"""Goodness-of-fit and equivalence tests on the three pilot systems.

Distribution fits use the domains declared in configs/pilot.json. No domain is
re-selected here: choosing a range after seeing a result is the failure mode
this project treats as a dead end, and it would invalidate the p-values.

Outputs results/gof.json and results/gof.png.
"""
from pathlib import Path
import sys, json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from orthopolity import resource_spectrum, rounded_gr_b          # noqa: E402
from gof import compare_alternatives, flatness_equivalence        # noqa: E402

RAW, OUT = ROOT / 'data' / 'raw', ROOT / 'results'
SPEC = json.loads((ROOT / 'configs' / 'pilot.json').read_text())
RNG = np.random.default_rng(SPEC['seed'])
B = SPEC['bootstrap_replicates']
N_BOOT_GOF = 500
TOLERANCES = [1.25, 2.0]


def blocks(df, col):
    g = [b for _, b in df.groupby(col, sort=True)]
    return pd.concat([g[i] for i in RNG.integers(len(g), size=len(g))], ignore_index=True)


def slope_of(s):
    if np.any(s['phi'] <= 0):
        return np.nan
    return float(np.polyfit(np.log(s['center']), np.log(s['phi']), 1)[0])


def equivalence_block(centers, phi, draws, label):
    return {f'tolerance_{t}': flatness_equivalence(centers, phi, tolerance_factor=t,
                                                   slope_draws=draws)
            for t in TOLERANCES} | {'label': label}


def noaa():
    lo, hi = SPEC['noaa']['primary_peak_flux_domain_W_m2']
    a = pd.concat([pd.read_csv(RAW / f'noaa_{y}.csv').assign(year=y)
                   for y in SPEC['noaa']['years']], ignore_index=True)
    a = a[np.isfinite(a.xrsb_irrad) & (a.xrsb_irrad > 0) & (a.peak_saturated == 0)].copy()
    a['month'] = pd.to_datetime(a.time).dt.strftime('%Y-%m')
    a['duration_s'] = (pd.to_datetime(a.end_time) - pd.to_datetime(a.start_time)).dt.total_seconds()
    ev = a[(a.year >= 2023) & (a.xrsb_irrad >= lo) & (a.xrsb_irrad <= hi)].copy()

    gof = compare_alternatives(ev.xrsb_irrad.to_numpy(), lo, hi,
                               n_boot=N_BOOT_GOF, seed=SPEC['seed'])

    pair = ev[np.isfinite(ev.integrated_irrad_end) & (ev.integrated_irrad_end > 0)
              & (ev.duration_s > 0)].copy()
    edges = np.geomspace(lo, hi, int(np.ceil(np.log10(hi / lo) * SPEC['noaa']['bins_per_decade'])) + 1)
    s = resource_spectrum(pair.xrsb_irrad, pair.integrated_irrad_end, edges)
    draws = np.array([slope_of(resource_spectrum(t.xrsb_irrad, t.integrated_irrad_end, edges))
                      for t in (blocks(pair, 'month') for _ in range(B))])
    return dict(distribution=gof,
                equivalence=equivalence_block(s['center'], s['phi'], draws,
                                              'End fluence occupancy, 2023-2024'),
                n_events=int(len(ev)), n_paired=int(len(pair)))


def usgs():
    a = pd.read_csv(RAW / 'usgs_2010_2024.csv')
    a['date'] = pd.to_datetime(a.time, utc=True)
    a = a[(a.date < pd.Timestamp('2025-01-01', tz='UTC'))
          & a.magType.str.startswith('mw', na=False)].copy()
    a['year'] = a.date.dt.year
    a['energy_proxy_J'] = 10 ** (4.8 + 1.5 * a.mag)

    mag_edges = np.arange(5.45, 9.5, 0.5)
    e_lo, e_hi = 10 ** (4.8 + 1.5 * mag_edges[0]), 10 ** (4.8 + 1.5 * mag_edges[-1])
    inside = a[(a.energy_proxy_J >= e_lo) & (a.energy_proxy_J <= e_hi)]
    gof = compare_alternatives(inside.energy_proxy_J.to_numpy(), e_lo, e_hi,
                               n_boot=N_BOOT_GOF, seed=SPEC['seed'])

    edges = 10 ** (4.8 + 1.5 * mag_edges)
    s = resource_spectrum(a.energy_proxy_J, a.energy_proxy_J, edges)
    draws = np.array([slope_of(resource_spectrum(t.energy_proxy_J, t.energy_proxy_J, edges))
                      for t in (blocks(a, 'year') for _ in range(B))])
    b, n = rounded_gr_b(a.mag, 5.5)
    return dict(distribution=gof,
                equivalence=equivalence_block(s['center'], s['phi'], draws,
                                              'Magnitude-derived energy occupancy'),
                gutenberg_richter_b=b, n_events=int(n),
                note='Energy is inferred from magnitude, so the power-law form is '
                     'largely imposed by the conversion; the goodness-of-fit test '
                     'here is far weaker evidence than the occupancy test.')


def ocean():
    f = pd.read_csv(OUT / 'ocean_reexpression.csv')
    k = 10 ** f.log10_mass_g.to_numpy()
    phi = f.phi.to_numpy()
    plateau = (f.log10_mass_g >= -10.5) & (f.log10_mass_g <= 4.5)
    return dict(
        full_range=equivalence_block(k, phi, None, 'All 23 published bins'),
        plateau=equivalence_block(k[plateau.to_numpy()], phi[plateau.to_numpy()], None,
                                  'Post hoc subrange 1e-10.5 to 1e4.5 g'),
        note='No distribution test: the source is a binned model-assisted '
             'reconstruction, not individual observations, so there is no sampling '
             'model and no interval is available. The plateau subrange was chosen '
             'AFTER inspecting the spectrum and is exploratory, not confirmatory.')


def figure(res):
    fig, axs = plt.subplots(1, 3, figsize=(12.5, 3.8), layout='constrained')
    for ax, (key, title) in zip(axs, [('noaa', 'Solar flares'), ('usgs', 'Earthquakes'),
                                      ('ocean', 'Ocean size spectrum')]):
        if key == 'ocean':
            e = res['ocean']['full_range']['tolerance_1.25']
            f = pd.read_csv(OUT / 'ocean_reexpression.csv')
            ax.plot(f.log10_mass_g, f.phi, 'o-', color='black', ms=3)
            ax.set_xlabel('Log10 body mass (g)')
        else:
            e = res[key]['equivalence']['tolerance_1.25']
            src = 'noaa_end_spectrum.csv' if key == 'noaa' else 'usgs_spectrum.csv'
            d = pd.read_csv(OUT / src)
            ax.plot(np.log10(d.center), d.phi, 'o-', color='black', ms=3)
            ax.set_xlabel('Log10 scale coordinate')
        ax.axhline(1, ls='--', color='#999', lw=1)
        ax.axhspan(1 / 1.25, 1.25, color='#627c90', alpha=.18,
                   label='Declared tolerance (factor 1.25)')
        ax.set(ylabel='Resource occupancy $\\Phi$',
               title=f"{title}\nratio {e['phi_ratio']:.1f}x, slope {e['slope']:+.3f}")
        ax.set_yscale('log')
        ax.spines[['top', 'right']].set_visible(False)
        ax.legend(fontsize=7)
    fig.savefig(OUT / 'gof.png', dpi=180)
    plt.close(fig)


def main():
    plt.rcParams.update({'font.size': 9, 'font.family': 'DejaVu Sans'})
    res = dict(
        protocol=dict(
            domains='Declared in configs/pilot.json; never re-selected here',
            gof_bootstrap=N_BOOT_GOF, slope_bootstrap=B, seed=SPEC['seed'],
            tolerances=TOLERANCES,
            criteria='Flatness requires BOTH slope equivalence (TOST) and bounded '
                     'departure (max |ln Phi| within tolerance).'),
        noaa=noaa(), usgs=usgs(), ocean=ocean())
    (OUT / 'gof.json').write_text(json.dumps(res, indent=2, default=float))
    figure(res)

    print('\n=== POWER-LAW GOODNESS OF FIT (declared domains) ===')
    for k in ('noaa', 'usgs'):
        g = res[k]['distribution']
        gf = g['goodness_of_fit']
        print(f"{k.upper():6} alpha={gf['alpha']:.3f} n={gf['n']} KS={gf['ks']:.4f} "
              f"p={gf['p_value']:.3f} -> {'RULED OUT' if gf['ruled_out'] else 'not ruled out'}")
        for c in g['comparisons']:
            print(f"       vs {c['against']:<22} LR={c['loglike_ratio']:+9.1f} "
                  f"p={c['p_value']:.4f}  favours {c['favours']}")

    print('\n=== FLATNESS EQUIVALENCE (tolerance factor 1.25) ===')
    for k, e in (('noaa', res['noaa']['equivalence']), ('usgs', res['usgs']['equivalence']),
                 ('ocean full', res['ocean']['full_range']),
                 ('ocean plateau', res['ocean']['plateau'])):
        t = e['tolerance_1.25']
        ci = t['slope_ci']
        cis = f"[{ci[0]:+.4f},{ci[1]:+.4f}]" if ci else "no interval"
        print(f"{k:14} slope={t['slope']:+.4f} {cis} tol=±{t['slope_tolerance']:.4f} | "
              f"ratio={t['phi_ratio']:5.1f}x depart_ok={t['departure_within_tolerance']!s:<5} | "
              f"{t['verdict']}")


if __name__ == '__main__':
    main()
