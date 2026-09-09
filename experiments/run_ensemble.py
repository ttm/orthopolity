"""Is the GLOSSAQUA ensemble result an attractor or an artefact?

EXPLORATORY, NOT PREREGISTERED. Preliminary values (the scatter-to-SE ratio and
the rounded-slope counts) were inspected while assessing feasibility, before
this was written. It is a follow-up to the preregistered test in
configs/prereg_2026-09-09.json, not a confirmatory test, and is labelled as
such wherever its results appear.

Three questions:
  1. Heterogeneity. Is the between-spectrum scatter real, or estimation noise?
  2. Anchoring. Is there an excess of slopes at exactly -1.00 beyond the
     generic preference for round numbers?
  3. Stratification. Does the result hold across habitats and taxa?
"""
from pathlib import Path
import sys, json, csv, io
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
RAW, OUT = ROOT / 'data' / 'raw', ROOT / 'results'
PRE = json.loads((ROOT / 'configs' / 'prereg_2026-09-09.json').read_text())
SEED = PRE['common']['seed']
PREDICTED = -1.0
rng = np.random.default_rng(SEED)


def num(s):
    s = (s or '').strip().strip('"')
    if s in ('', 'NA', 'NaN', 'None'):
        return np.nan
    try:
        return float(s)
    except ValueError:
        return np.nan


def load():
    sz = list(csv.DictReader(io.StringIO((RAW / 'GLOSSAQUA_Size.txt').read_text('utf-8')),
                             delimiter=' ', quotechar='"'))
    sm = list(csv.DictReader(io.StringIO((RAW / 'GLOSSAQUA_Sample.txt').read_bytes().decode('latin-1')),
                             delimiter='\t', quotechar='"'))
    meta = {r['SiteID'].strip().strip('"'): r for r in sm}
    out = []
    for r in sz:
        if r['XaxisParameterType'].strip() != 'body mass':
            continue
        if r['SizeSpectrumMethod'].strip() != 'Normalized biomass spectrum (linear)':
            continue
        sl, lo, hi = num(r['Slope']), num(r['SizeRangeMinimum']), num(r['SizeRangeMaximum'])
        if not np.isfinite([sl, lo, hi]).all() or not (0 < lo < hi):
            continue
        m = meta.get(r['SiteID'].strip().strip('"'), {})
        cl, cu = num(r['SlopeConfIntLow']), num(r['SlopeConfIntUp'])
        se = (cu - cl) / (2 * 1.96) if np.isfinite([cl, cu]).all() and cu > cl else np.nan
        if not np.isfinite(se):
            sd = num(r['SlopeSD']); se2 = num(r['SlopeSE'])
            se = se2 if np.isfinite(se2) else np.nan
        out.append(dict(study=r['StudyID'].strip().strip('"'), slope=sl, se=se,
                        span=np.log(hi / lo),
                        habitat=(m.get('Habitat') or 'unknown').strip().strip('"'),
                        species=(m.get('SpeciesType') or 'unknown').strip().strip('"'),
                        org=(m.get('BiologicalOrganisation') or 'unknown').strip().strip('"')))
    return out


def boot_median(vals, studies, n=2000):
    uniq = np.unique(studies)
    idx = {u: np.flatnonzero(studies == u) for u in uniq}
    d = np.empty(n)
    for i in range(n):
        pick = np.concatenate([idx[u] for u in rng.choice(uniq, len(uniq))])
        d[i] = np.median(vals[pick])
    return float(np.median(vals)), [float(v) for v in np.quantile(d, [.025, .975])]


# ------------------------------------------------- 1. heterogeneity
def heterogeneity(d):
    g = [x for x in d if np.isfinite(x['se']) and x['se'] > 0]
    y = np.array([x['slope'] for x in g])
    se = np.array([x['se'] for x in g])
    w = 1 / se ** 2
    mu = float((w * y).sum() / w.sum())
    Q = float((w * (y - mu) ** 2).sum())
    df = len(y) - 1
    C = float(w.sum() - (w ** 2).sum() / w.sum())
    tau2 = max(0.0, (Q - df) / C) if C > 0 else np.nan
    I2 = max(0.0, (Q - df) / Q) if Q > 0 else np.nan
    return dict(n_with_uncertainty=len(g), n_total=len(d),
                fixed_effect_mean=mu, Q=Q, df=df, I_squared=I2,
                tau=float(np.sqrt(tau2)), tau_squared=tau2,
                median_reported_se=float(np.median(se)),
                observed_sd=float(np.std([x['slope'] for x in d])),
                sd_to_se_ratio=float(np.std([x['slope'] for x in d]) / np.median(se)),
                interpretation=('scatter is real between-system heterogeneity'
                                if I2 > 0.75 else 'scatter consistent with estimation noise'))


# ------------------------------------------------- 2. anchoring
def anchoring(d):
    s = np.array([x['slope'] for x in d])
    r2 = np.round(s, 2)
    on_grid = float(np.mean(np.abs(s - r2) < 1e-9))
    # second-decimal digit distribution
    dig = np.round(np.abs(r2) * 100).astype(int) % 10
    counts = np.array([(dig == k).sum() for k in range(10)])
    exp = counts.sum() / 10
    chi2 = float(((counts - exp) ** 2 / exp).sum())

    # local excess at each round (0.10) value, excluding the round points themselves
    grid = {}
    for v in np.round(np.arange(-2.0, 0.001, 0.01), 2):
        grid[v] = int((np.abs(r2 - v) < 1e-9).sum())
    rounds = np.round(np.arange(-1.9, -0.09, 0.1), 2)
    ex = {}
    for v in rounds:
        nb = [grid.get(round(v + k * 0.01, 2), 0) for k in (-4, -3, -2, -1, 1, 2, 3, 4)]
        base = np.mean(nb)
        ex[float(v)] = dict(count=grid.get(float(v), 0), local_baseline=float(base),
                            excess_ratio=float(grid.get(float(v), 0) / base) if base > 0 else np.nan)
    others = [v['excess_ratio'] for k, v in ex.items() if abs(k + 1.0) > 1e-9
              and np.isfinite(v['excess_ratio'])]
    at_pred = ex[-1.0]['excess_ratio']
    return dict(fraction_reported_on_2dp_grid=on_grid,
                second_decimal_counts=counts.tolist(), second_decimal_chi2=chi2,
                second_decimal_note='10 bins, 9 df; chi2 > 21.7 rejects uniformity at p<0.01',
                excess_at_round_values={str(k): v for k, v in ex.items()},
                excess_ratio_at_minus_1=at_pred,
                median_excess_ratio_other_round_values=float(np.median(others)),
                n_other_round_values=len(others),
                rank_of_minus_1=int(sum(o >= at_pred for o in others) + 1),
                interpretation=('-1.00 stands out beyond generic round-number preference'
                                if at_pred > np.quantile(others, 0.9) else
                                'excess at -1.00 is within the range of generic round-number preference'))


# ------------------------------------------------- 3. stratification
MIN_STUDIES_FOR_CI = 4


def stratify(d, key, min_n=30):
    """Median slope per stratum with a study-block bootstrap interval.

    A block bootstrap over fewer than MIN_STUDIES_FOR_CI studies produces a
    degenerate or near-degenerate interval (with one study it has zero width),
    so no verdict is issued for those strata rather than a spurious one.
    """
    out = {}
    for lab in sorted({x[key] for x in d}):
        g = [x for x in d if x[key] == lab]
        if len(g) < min_n:
            continue
        v = np.array([x['slope'] for x in g])
        st = np.array([x['study'] for x in g])
        ns = len(set(st))
        med, ci = boot_median(v, st)
        rec = dict(n=len(g), n_studies=int(ns), median_slope=med,
                   departure=med - PREDICTED)
        if ns < MIN_STUDIES_FOR_CI:
            rec.update(ci=None, consistent_with_prediction=None,
                       note=f'only {ns} study block(s); no valid interval')
        else:
            rec.update(ci=ci, consistent_with_prediction=bool(ci[0] <= PREDICTED <= ci[1]))
        out[lab] = rec
    return out


def figure(res, d):
    fig, axs = plt.subplots(1, 3, figsize=(13.5, 4), layout='constrained')
    s = np.array([x['slope'] for x in d])
    ax = axs[0]
    ax.hist(s, bins=np.arange(-2.5, 0.75, 0.02), color='#4b5563')
    ax.axvline(PREDICTED, color='crimson', lw=1.5, label='Orthopolity prediction (-1)')
    ax.set(xlabel='NBSS slope', ylabel='Spectra', xlim=(-2.5, 0.5),
           title=f"Slope distribution (n={len(s)})\n$I^2$={res['heterogeneity']['I_squared']:.1%}"
                 f", $\\tau$={res['heterogeneity']['tau']:.2f}")
    ax.legend(fontsize=7)

    ax = axs[1]
    ks = sorted(float(k) for k in res['anchoring']['excess_at_round_values'])
    vs = [res['anchoring']['excess_at_round_values'][str(k)]['excess_ratio'] for k in ks]
    cols = ['crimson' if abs(k + 1) < 1e-9 else '#9ca3af' for k in ks]
    ax.bar(ks, vs, width=.07, color=cols)
    ax.axhline(1, ls='--', color='#666', lw=1)
    ax.set(xlabel='Round slope value', ylabel='Count / local baseline',
           title='Round-number excess\n(red = the predicted value)')

    ax = axs[2]
    st = {k: v for k, v in res['stratification']['habitat'].items() if v['ci']}
    labs = list(st)
    y = np.arange(len(labs))
    ax.errorbar([st[l]['median_slope'] for l in labs], y,
                xerr=[[st[l]['median_slope'] - st[l]['ci'][0] for l in labs],
                      [st[l]['ci'][1] - st[l]['median_slope'] for l in labs]],
                fmt='o', color='black', capsize=4)
    ax.axvline(PREDICTED, color='crimson', lw=1.5)
    ax.set(yticks=y, yticklabels=[f"{l}\n(n={st[l]['n']}, {st[l]['n_studies']} st.)" for l in labs],
           xlabel='Median NBSS slope', title='By habitat')
    for a in axs:
        a.spines[['top', 'right']].set_visible(False)
    fig.savefig(OUT / 'ensemble.png', dpi=180)
    plt.close(fig)


def main():
    plt.rcParams.update({'font.size': 9, 'font.family': 'DejaVu Sans'})
    d = load()
    res = dict(status='EXPLORATORY follow-up, not preregistered; preliminary values were seen '
                      'during feasibility assessment before this analysis was written',
               n=len(d), predicted_slope=PREDICTED,
               heterogeneity=heterogeneity(d), anchoring=anchoring(d),
               stratification=dict(habitat=stratify(d, 'habitat'),
                                   species=stratify(d, 'species'),
                                   organisation=stratify(d, 'org')))
    (OUT / 'ensemble.json').write_text(json.dumps(res, indent=2, default=float))
    figure(res, d)

    h = res['heterogeneity']
    print(f"\n=== 1. HETEROGENEITY (n={h['n_with_uncertainty']}/{h['n_total']} with usable uncertainty) ===")
    print(f"  observed sd {h['observed_sd']:.3f} vs median reported SE {h['median_reported_se']:.3f} "
          f"(ratio {h['sd_to_se_ratio']:.1f}x)")
    print(f"  Q={h['Q']:.0f} on {h['df']} df   I^2={h['I_squared']:.1%}   tau={h['tau']:.3f}")
    print(f"  -> {h['interpretation']}")

    a = res['anchoring']
    print(f"\n=== 2. ANCHORING AT THE PREDICTED VALUE ===")
    print(f"  {a['fraction_reported_on_2dp_grid']:.1%} of slopes lie exactly on the 2-decimal grid")
    print(f"  second-decimal digit counts {a['second_decimal_counts']}  chi2={a['second_decimal_chi2']:.1f} "
          f"({a['second_decimal_note']})")
    print(f"  excess ratio at -1.00: {a['excess_ratio_at_minus_1']:.2f}x local baseline")
    print(f"  median excess at the other {a['n_other_round_values']} round values: "
          f"{a['median_excess_ratio_other_round_values']:.2f}x")
    print(f"  -1.00 ranks {a['rank_of_minus_1']} of {a['n_other_round_values']+1} round values")
    print(f"  -> {a['interpretation']}")

    print(f"\n=== 3. STRATIFICATION (median slope, study-block CI; prediction {PREDICTED}) ===")
    for key in ('habitat', 'species', 'organisation'):
        print(f"  [{key}]")
        for lab, v in res['stratification'][key].items():
            if v['ci'] is None:
                print(f"    {lab[:38]:<38} n={v['n']:>4} ({v['n_studies']:>2} st.) "
                      f"median={v['median_slope']:+.3f}  -- {v['note']}")
                continue
            flag = 'consistent' if v['consistent_with_prediction'] else 'INCONSISTENT'
            print(f"    {lab[:38]:<38} n={v['n']:>4} ({v['n_studies']:>2} st.) "
                  f"median={v['median_slope']:+.3f} CI[{v['ci'][0]:+.3f},{v['ci'][1]:+.3f}]  {flag}")


if __name__ == '__main__':
    main()
