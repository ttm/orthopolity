"""Preregistered independent tests. Protocol: configs/prereg_2026-09-09.json.

Nothing here may be tuned after seeing output. Any change creates a new
hypothesis and the original protocol stays in the git record.
"""
from pathlib import Path
import sys, json, csv, io
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from gof import flatness_equivalence                                   # noqa: E402

RAW, OUT = ROOT / 'data' / 'raw', ROOT / 'results'
PRE = json.loads((ROOT / 'configs' / 'prereg_2026-09-09.json').read_text())
SEED = PRE['common']['seed']
TOLS = PRE['common']['tolerance_factors']
MAP = {k: v['predicted_slope'] for k, v in PRE['test_A_glossaqua']['exponent_mapping'].items()
       if not k.startswith('_')}
ROLE = {k: v['role'] for k, v in PRE['test_A_glossaqua']['exponent_mapping'].items()
        if not k.startswith('_')}


def _num(s):
    s = (s or '').strip().strip('"')
    if s in ('', 'NA', 'NaN', 'None'):
        return np.nan
    try:
        return float(s.replace(',', '.') if s.count(',') == 1 and '.' not in s else s)
    except ValueError:
        return np.nan


# ---------------------------------------------------------------- test A
def glossaqua():
    txt = (RAW / 'GLOSSAQUA_Size.txt').read_text(encoding='utf-8')
    rows = list(csv.DictReader(io.StringIO(txt), delimiter=' ', quotechar='"'))
    rng = np.random.default_rng(SEED)
    kept, dropped = [], {'axis_not_body_mass': 0, 'method_excluded': 0, 'bad_numbers': 0}

    for r in rows:
        if r['XaxisParameterType'].strip() != 'body mass':
            dropped['axis_not_body_mass'] += 1; continue
        m = r['SizeSpectrumMethod'].strip()
        if m not in MAP:
            dropped['method_excluded'] += 1; continue
        sl, lo, hi = _num(r['Slope']), _num(r['SizeRangeMinimum']), _num(r['SizeRangeMaximum'])
        if not np.isfinite([sl, lo, hi]).all() or not (0 < lo < hi):
            dropped['bad_numbers'] += 1; continue
        kept.append(dict(study=r['StudyID'].strip(), method=m, role=ROLE[m],
                         slope=sl, departure=sl - MAP[m], span=np.log(hi / lo)))

    out = dict(n_records=len(rows), n_kept=len(kept), dropped=dropped,
               n_studies=len({k['study'] for k in kept}), subsets={})

    for label, sel in [('primary_NBSS', lambda k: k['role'] == 'PRIMARY'),
                       ('all_mapped_methods', lambda k: True)]:
        g = [k for k in kept if sel(k)]
        if len(g) < 10:
            out['subsets'][label] = dict(n=len(g), note='too few records'); continue
        s = np.array([k['departure'] for k in g])
        span = np.array([k['span'] for k in g])
        studies = np.array([k['study'] for k in g])
        uniq = np.unique(studies)
        idx = {u: np.flatnonzero(studies == u) for u in uniq}

        draws = np.empty(2000)
        for i in range(2000):
            pick = np.concatenate([idx[u] for u in rng.choice(uniq, len(uniq))])
            draws[i] = np.median(s[pick])
        ci = [float(v) for v in np.quantile(draws, [.025, .975])]

        res = dict(n=len(g), n_studies=int(len(uniq)),
                   median_departure=float(np.median(s)), median_departure_ci=ci,
                   median_span_decades=float(np.median(span) / np.log(10)),
                   median_slope=float(np.median([k['slope'] for k in g])))
        for F in TOLS:
            tol = np.log(F) / span
            frac = float(np.mean(np.abs(s) <= tol))
            med_tol = float(np.median(tol))
            res[f'F_{F}'] = dict(
                fraction_equivalent=frac, median_tolerance=med_tol,
                pooled_inside=bool(ci[0] > -med_tol and ci[1] < med_tol))
        # declared success criteria
        pooled_ok = res[f'F_{TOLS[0]}']['pooled_inside']
        frac_ok = res[f'F_{TOLS[1]}']['fraction_equivalent'] >= 0.50
        res['verdict'] = ('supported' if (pooled_ok and frac_ok) else
                          'partially supported' if (pooled_ok or frac_ok) else 'not supported')
        res['implied_drift_at_median_span'] = float(np.exp(abs(np.median(s)) * np.median(span)))
        out['subsets'][label] = res

    by_method = {}
    for m in sorted(MAP):
        g = [k for k in kept if k['method'] == m]
        if g:
            by_method[m] = dict(n=len(g), predicted=MAP[m],
                                median_slope=float(np.median([k['slope'] for k in g])),
                                median_departure=float(np.median([k['departure'] for k in g])))
    out['by_method'] = by_method
    return out


# ------------------------------------------------------------- tests B, C
def ocean_uncertainty(table, label, n_draws=20000):
    fac = {r['Group']: float(r['log10_Standard_Error'])
           for r in csv.DictReader(open(RAW / 'sheldon_group_standard_errors.csv'))}
    rows = list(csv.DictReader(open(RAW / table)))
    mids = sorted({float(r['log10_Size_Midpoint_g']) for r in rows})
    est = np.zeros((len(mids), len(fac)))
    sig = np.zeros(len(fac))
    groups = sorted(fac)
    gi = {g: i for i, g in enumerate(groups)}
    mi = {m: i for i, m in enumerate(mids)}
    for r in rows:
        est[mi[float(r['log10_Size_Midpoint_g'])], gi[r['Group']]] = \
            float(r['Biomass_Pg_wet_weight_estimate'])
    for g in groups:
        sig[gi[g]] = np.log(fac[g]) / 1.96

    rng = np.random.default_rng(SEED)
    k = 10.0 ** np.array(mids)
    pos = est > 0
    phis = np.empty((n_draws, len(mids)))
    for d in range(n_draws):
        b = np.zeros_like(est)
        b[pos] = np.exp(np.log(est[pos]) + rng.normal(0, 1, pos.sum()) * np.tile(sig, (len(mids), 1))[pos])
        tot = b.sum(axis=1)
        phis[d] = tot / tot.mean()

    point = est.sum(axis=1)
    point = point / point.mean()
    plateau = (np.array(mids) >= -10.5) & (np.array(mids) <= 4.5)

    def block(sel, name):
        c, p = k[sel], point[sel]
        draws = np.array([np.polyfit(np.log(c), np.log(np.maximum(phis[d][sel], 1e-300)), 1)[0]
                          for d in range(n_draws)])
        return {f'tolerance_{F}': flatness_equivalence(c, p, tolerance_factor=F,
                                                       slope_draws=draws) for F in TOLS} | \
               dict(label=name, slope_draws_sd=float(draws.std()))

    ln = np.log(np.maximum(phis, 1e-300))
    per_bin = []
    for j, m in enumerate(mids):
        q = np.quantile(ln[:, j], [.025, .975])
        per_bin.append(dict(log10_mass_g=m, phi=float(point[j]),
                            ln_phi_ci=[float(q[0]), float(q[1])],
                            resolvable_at_1_25=bool(q[0] > np.log(1.25) or q[1] < -np.log(1.25)),
                            resolvable_at_2=bool(q[0] > np.log(2.0) or q[1] < -np.log(2.0))))
    return dict(source=table, label=label, n_draws=n_draws,
                full_range=block(np.ones(len(mids), bool), 'All bins'),
                plateau=block(plateau, 'Post hoc plateau (exploratory)'),
                per_bin=per_bin,
                caveat=PRE['test_B_ocean_uncertainty']['model_caveat'])


def figure(res):
    fig, axs = plt.subplots(1, 3, figsize=(13, 3.9), layout='constrained')
    a = res['glossaqua']['subsets']['primary_NBSS']
    ax = axs[0]
    ax.axvline(0, color='black', lw=1)
    ax.axvspan(-a['F_1.25']['median_tolerance'], a['F_1.25']['median_tolerance'],
               color='#627c90', alpha=.25, label='Median tolerance (F=1.25)')
    ax.errorbar([a['median_departure']], [0], xerr=[[a['median_departure'] - a['median_departure_ci'][0]],
                [a['median_departure_ci'][1] - a['median_departure']]], fmt='o', color='crimson',
                capsize=4, label='Median departure')
    ax.set(xlabel='Departure from orthopolity slope', yticks=[],
           title=f"GLOSSAQUA NBSS\nn={a['n']} spectra, {a['n_studies']} studies")
    ax.legend(fontsize=7)
    for ax, key, t in [(axs[1], 'ocean_top200', 'Ocean, upper 200 m'),
                       (axs[2], 'ocean_allwater', 'Ocean, full water column')]:
        r = res[key]
        m = [b['log10_mass_g'] for b in r['per_bin']]
        p = [b['phi'] for b in r['per_bin']]
        lo = [np.exp(b['ln_phi_ci'][0]) for b in r['per_bin']]
        hi = [np.exp(b['ln_phi_ci'][1]) for b in r['per_bin']]
        ax.fill_between(m, lo, hi, color='#627c90', alpha=.25, label='95% reconstruction uncertainty')
        ax.plot(m, p, 'o-', color='black', ms=3, label='Estimate')
        ax.axhspan(1 / 1.25, 1.25, color='crimson', alpha=.12, label='Tolerance F=1.25')
        ax.axhline(1, ls='--', color='#999', lw=1)
        ax.set(yscale='log', xlabel='Log10 body mass (g)', ylabel='$\\Phi$', title=t)
        ax.legend(fontsize=6)
    for ax in axs:
        ax.spines[['top', 'right']].set_visible(False)
    fig.savefig(OUT / 'independent.png', dpi=180)
    plt.close(fig)


def main():
    plt.rcParams.update({'font.size': 9, 'font.family': 'DejaVu Sans'})
    res = dict(protocol='configs/prereg_2026-09-09.json',
               glossaqua=glossaqua(),
               ocean_top200=ocean_uncertainty('sheldon_summary_biomass_top200_table_long.csv',
                                              'Upper 200 m'),
               ocean_allwater=ocean_uncertainty('sheldon_summary_biomass_allwater_table_long.csv',
                                                'Full water column'))
    (OUT / 'independent.json').write_text(json.dumps(res, indent=2, default=float))
    figure(res)

    g = res['glossaqua']
    print(f"\n=== TEST A: GLOSSAQUA (preregistered, blind) ===")
    print(f"{g['n_records']} records -> {g['n_kept']} kept from {g['n_studies']} studies; dropped {g['dropped']}")
    for name, s in g['subsets'].items():
        if 'n_studies' not in s:
            continue
        print(f"\n  [{name}] n={s['n']} spectra, {s['n_studies']} studies, "
              f"median span {s['median_span_decades']:.1f} decades")
        print(f"    median slope {s['median_slope']:+.3f}, median departure {s['median_departure']:+.4f} "
              f"CI {[round(v,4) for v in s['median_departure_ci']]}")
        for F in TOLS:
            d = s[f'F_{F}']
            print(f"    F={F}: tol=±{d['median_tolerance']:.4f}  pooled_inside={d['pooled_inside']}  "
                  f"fraction_equivalent={d['fraction_equivalent']:.3f}")
        print(f"    implied drift across median span: {s['implied_drift_at_median_span']:.2f}x")
        print(f"    >>> VERDICT: {s['verdict'].upper()}")
    print("\n  by method:")
    for m, d in g['by_method'].items():
        print(f"    {m:<42} n={d['n']:>5} predicted={d['predicted']:+.1f} "
              f"median={d['median_slope']:+.3f} departure={d['median_departure']:+.3f}")

    for key, t in [('ocean_top200', 'TEST B: ocean upper 200 m (uncertainty propagated)'),
                   ('ocean_allwater', 'TEST C: ocean full water column (blind)')]:
        r = res[key]
        print(f"\n=== {t} ===")
        for sub in ('full_range', 'plateau'):
            e = r[sub][f'tolerance_{TOLS[0]}']
            ci = e['slope_ci']
            print(f"  {sub:11} slope={e['slope']:+.4f} CI[{ci[0]:+.4f},{ci[1]:+.4f}] "
                  f"tol=±{e['slope_tolerance']:.4f} ratio={e['phi_ratio']:.1f}x -> {e['verdict']}")
            e2 = r[sub][f'tolerance_{TOLS[1]}']
            print(f"  {'':11} at F=2: {e2['verdict']}")
        n125 = sum(b['resolvable_at_1_25'] for b in r['per_bin'])
        n2 = sum(b['resolvable_at_2'] for b in r['per_bin'])
        print(f"  bins whose departure is resolvable above reconstruction uncertainty: "
              f"{n125}/{len(r['per_bin'])} at F=1.25, {n2}/{len(r['per_bin'])} at F=2")


if __name__ == '__main__':
    main()
