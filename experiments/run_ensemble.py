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
  4. Span dependence. If the concentration at -1 is an averaging effect, then
     spectra spanning more decades should sit closer to it and scatter less.
     If the dispersion is intrinsic, span should not matter.

Estimators live in src/meta.py and are unit-tested; this script only selects
data and reports.
"""
from pathlib import Path
import sys, json, csv, io
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from meta import (random_effects, digit_preference, round_number_excess,  # noqa: E402
                  latent_shape, predicted_pass_fraction)
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
    r = random_effects([x['slope'] for x in g], [x['se'] for x in g])
    r.update(n_total=len(d),
             all_spectra_sd=float(np.std([x['slope'] for x in d], ddof=1)),
             interpretation=('scatter is real between-system heterogeneity'
                             if r['I_squared'] > 0.75 else
                             'scatter consistent with estimation noise'))
    return r


# ------------------------------------------------- 2. anchoring
def anchoring(d):
    s = np.array([x['slope'] for x in d])
    dig = digit_preference(s, decimals=2)
    exc = round_number_excess(s, target=PREDICTED, grid=0.01, step=0.10,
                              window=4, lo=-2.0, hi=-0.1)
    return dict(fraction_reported_on_2dp_grid=float(np.mean(np.abs(s - np.round(s, 2)) < 1e-9)),
                digit_preference=dig, round_number_excess=exc,
                interpretation=('-1.00 stands out beyond generic round-number preference'
                                if exc['stands_out'] else
                                'excess at -1.00 is within the range of generic '
                                'round-number preference'))


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


def span_dependence(d):
    """Does the departure from -1 shrink as the reported size range widens?

    Aggregated to one point per study. At spectrum level a single study
    contributing hundreds of spectra at one span dominates the correlation
    entirely, which is pseudo-replication rather than evidence.
    """
    dec = np.array([x['span'] for x in d]) / np.log(10)
    dep = np.abs(np.array([x['slope'] for x in d]) - PREDICTED)
    st = np.array([x['study'] for x in d])

    per_study = []
    for u in sorted(set(st)):
        m = st == u
        per_study.append(dict(study=u, n=int(m.sum()),
                              median_span_decades=float(np.median(dec[m])),
                              median_abs_departure=float(np.median(dep[m]))))
    xs = np.array([p['median_span_decades'] for p in per_study])
    ys = np.array([p['median_abs_departure'] for p in per_study])
    rho_s, p_s = spearmanr(xs, ys)
    rho_r, p_r = spearmanr(dec, dep)

    edges = np.quantile(dec, [0, .25, .5, .75, 1.0])
    strata = []
    for i in range(4):
        m = (dec >= edges[i]) & ((dec <= edges[i + 1]) if i == 3 else (dec < edges[i + 1]))
        if m.sum() < 20:
            continue
        ns = len(set(st[m]))
        med, ci = boot_median(dep[m], st[m])
        sub = [x for x, k in zip(d, m) if k and np.isfinite(x['se']) and x['se'] > 0]
        tau = (random_effects([x['slope'] for x in sub], [x['se'] for x in sub])['tau']
               if len(sub) >= 10 else None)
        strata.append(dict(quartile=i + 1, span_decades=[float(edges[i]), float(edges[i + 1])],
                           n=int(m.sum()), n_studies=int(ns),
                           median_abs_departure=med,
                           ci=(ci if ns >= MIN_STUDIES_FOR_CI else None),
                           degenerate=bool(ns < MIN_STUDIES_FOR_CI), tau=tau))

    sig = bool(rho_s < 0 and p_s < 0.05)
    return dict(per_study=per_study, strata=strata,
                study_level=dict(n_studies=len(per_study), spearman_rho=float(rho_s),
                                 spearman_p=float(p_s)),
                spectrum_level=dict(spearman_rho=float(rho_r), spearman_p=float(p_r),
                                    warning='pseudo-replicated: dominated by whichever study '
                                            'contributes the most spectra at one span'),
                interpretation=('wider spans sit closer to the prediction, consistent with an '
                                'averaging effect' if sig else
                                'no evidence at study level that span drives the concentration '
                                'at -1'),
                confound_note='Span is not randomly assigned: plankton studies span more decades '
                              'than fish studies, so span is partly a proxy for taxon.')


def latent_and_prohibition(d):
    """R1: the shape (O-ensemble) predicts, and the individual failure rate it forbids."""
    g = [x for x in d if np.isfinite(x['se']) and x['se'] > 0]
    shape = latent_shape([x['slope'] for x in g], [x['se'] for x in g])
    tau = shape['families'][shape['best_family']]['tau']

    span = np.array([x['span'] for x in d])
    dep = np.array([x['slope'] for x in d]) - PREDICTED
    checks = []
    for F in (1.25, 2.0):
        tol = np.log(F) / span
        obs = float(np.mean(np.abs(dep) <= tol))
        for fam in ('gaussian', shape['best_family']):
            nu = shape['families'][fam].get('nu')
            pr = predicted_pass_fraction(tol, tau=shape['families'][fam]['tau'],
                                         family=fam, nu=nu)
            checks.append(dict(tolerance_factor=F, family=fam,
                               predicted_fraction=pr['mean_predicted_fraction'],
                               observed_fraction=obs,
                               ratio=float(obs / pr['mean_predicted_fraction'])))
    return dict(latent_shape=shape, tau_used=tau, pass_fraction_checks=checks,
                prohibition=dict(
                    statement='Two resources measured on the same systems cannot both be '
                              'orthopolar unless their departures have equal dispersion and '
                              'are perfectly correlated across systems.',
                    derivation='If both spectra are flat then s1 - s2 = d2 - d1, a constant, '
                               'so Var[s1] = Var[s2] and corr(s1,s2) = 1. Unequal tau refutes '
                               'at least one.',
                    replication='tau is a property of the class, so an independent aquatic '
                                f'dataset must reproduce tau = {tau:.3f}. A materially '
                                'different tau refutes (O-ensemble) for that class.'))


def figure(res, d):
    fig, axs = plt.subplots(1, 4, figsize=(17, 4), layout='constrained')
    s = np.array([x['slope'] for x in d])

    ax = axs[0]
    ax.hist(s, bins=np.arange(-2.5, 0.75, 0.02), color='#4b5563')
    ax.axvline(PREDICTED, color='crimson', lw=1.5, label='Prediction (-1)')
    ax.set(xlabel='NBSS slope', ylabel='Spectra', xlim=(-2.5, 0.5),
           title=f"Slope distribution (n={len(s)})\n"
                 f"$I^2$={res['heterogeneity']['I_squared']:.1%}, "
                 f"$\\tau$={res['heterogeneity']['tau']:.2f}")
    ax.legend(fontsize=7)

    ax = axs[1]
    ex = res['anchoring']['round_number_excess']['per_value']
    ks = sorted(float(k) for k in ex)
    vs = [ex[str(k)]['excess_ratio'] for k in ks]
    cols = ['crimson' if abs(k - PREDICTED) < 1e-9 else '#9ca3af' for k in ks]
    ax.bar(ks, vs, width=.07, color=cols)
    ax.axhline(1, ls='--', color='#666', lw=1)
    ax.set(xlabel='Round slope value', ylabel='Count / local baseline',
           title='Round-number excess\n(red = predicted value)')

    ax = axs[2]
    st = {k: v for k, v in res['stratification']['habitat'].items() if v['ci']}
    st.update({k: v for k, v in res['stratification']['species'].items() if v['ci']})
    labs = list(st)
    y = np.arange(len(labs))
    ax.errorbar([st[l]['median_slope'] for l in labs], y,
                xerr=[[st[l]['median_slope'] - st[l]['ci'][0] for l in labs],
                      [st[l]['ci'][1] - st[l]['median_slope'] for l in labs]],
                fmt='o', color='black', capsize=3)
    ax.axvline(PREDICTED, color='crimson', lw=1.5)
    ax.set(yticks=y, yticklabels=[f"{l[:22]} ({st[l]['n_studies']} st.)" for l in labs],
           xlabel='Median NBSS slope', title='By habitat and taxon')
    ax.tick_params(axis='y', labelsize=7)

    ax = axs[3]
    sp = res['span_dependence']['strata']
    x = np.arange(len(sp))
    ax.errorbar(x, [q['median_abs_departure'] for q in sp],
                yerr=[[q['median_abs_departure'] - (q['ci'][0] if q['ci'] else q['median_abs_departure']) for q in sp],
                      [(q['ci'][1] if q['ci'] else q['median_abs_departure']) - q['median_abs_departure'] for q in sp]],
                fmt='o-', color='black', capsize=4)
    ax.set(xticks=x,
           xticklabels=[f"{q['span_decades'][0]:.1f}-\n{q['span_decades'][1]:.1f}" for q in sp],
           xlabel='Reported size range (decades)', ylabel='Median |departure from -1|',
           title=f"Span dependence\n"
                 f"study-level $\\rho$={res['span_dependence']['study_level']['spearman_rho']:+.2f}")
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
               span_dependence=span_dependence(d),
               R1=latent_and_prohibition(d),
               stratification=dict(habitat=stratify(d, 'habitat'),
                                   species=stratify(d, 'species'),
                                   organisation=stratify(d, 'org')))
    (OUT / 'ensemble.json').write_text(json.dumps(res, indent=2, default=float))
    figure(res, d)

    h = res['heterogeneity']
    print(f"\n=== 1. HETEROGENEITY (n={h['k']}/{h['n_total']} with usable uncertainty) ===")
    print(f"  observed sd {h['observed_sd']:.3f} vs median reported SE {h['median_se']:.3f}")
    print(f"  Q={h['Q']:.0f} on {h['df']} df (p={h['Q_p_value']:.2g})   "
          f"I^2={h['I_squared']:.1%}   tau={h['tau']:.3f}")
    print(f"  random-effects mean {h['random_effects_mean']:+.4f} "
          f"CI[{h['random_effects_ci'][0]:+.4f},{h['random_effects_ci'][1]:+.4f}]")
    print(f"  -> {h['interpretation']}")

    a = res['anchoring']
    print(f"\n=== 2. ANCHORING AT THE PREDICTED VALUE ===")
    print(f"  {a['fraction_reported_on_2dp_grid']:.1%} of slopes lie exactly on the 2-decimal grid")
    dg, ex = a['digit_preference'], a['round_number_excess']
    print(f"  second-decimal digits {dg['counts']}  chi2={dg['chi2']:.1f} on {dg['df']} df "
          f"(p={dg['p_value']:.2g}, uniform={dg['uniform']})")
    print(f"  excess ratio at -1.00: {ex['excess_at_target']:.2f}x local baseline")
    print(f"  median excess at the other {ex['n_other_round_values']} round values: "
          f"{ex['median_excess_elsewhere']:.2f}x")
    print(f"  -1.00 ranks {ex['rank_of_target']} of {ex['n_other_round_values']+1} round values")
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

    sp = res['span_dependence']
    print(f"\n=== 4. SPAN DEPENDENCE ===")
    print(f"  {'span (decades)':<20}{'n':>6}{'st.':>5}{'med |dep|':>11}{'95% CI':>20}{'tau':>8}")
    for s in sp['strata']:
        tau = f"{s['tau']:.3f}" if s['tau'] is not None else '  --'
        ci = (f"  [{s['ci'][0]:+.3f},{s['ci'][1]:+.3f}]" if s['ci']
              else f"  {'(1 study: no CI)':>18}")
        print(f"  {s['span_decades'][0]:>7.2f}-{s['span_decades'][1]:<12.2f}{s['n']:>6}"
              f"{s['n_studies']:>5}{s['median_abs_departure']:>11.3f}{ci}{tau:>8}")
    print(f"  study-level (n={sp['study_level']['n_studies']}): "
          f"Spearman rho={sp['study_level']['spearman_rho']:+.3f} "
          f"(p={sp['study_level']['spearman_p']:.2g})   <-- the valid test")
    print(f"  spectrum-level: rho={sp['spectrum_level']['spearman_rho']:+.3f} "
          f"(p={sp['spectrum_level']['spearman_p']:.2g})  [{sp['spectrum_level']['warning']}]")
    print(f"  -> {sp['interpretation']}")

    r1 = res['R1']
    ls = r1['latent_shape']
    print(f"\n=== 5. LATENT SHAPE: what (O-ensemble) predicts (n={ls['n']}) ===")
    print(f"  {'family':<18}{'mu':>9}{'tau':>8}{'nu':>6}{'logL':>11}{'dAIC':>9}")
    for fam, v in ls['families'].items():
        print(f"  {fam:<18}{v['mu']:>9.4f}{v['tau']:>8.4f}"
              f"{(str(v['nu']) if v['nu'] else '-'):>6}{v['loglike']:>11.1f}"
              f"{ls['delta_aic_vs_gaussian'][fam]:>+9.1f}")
    rz = ls['gaussian_standardised_residuals']
    print(f"  gaussian standardised residuals: sd={rz['sd']:.3f} skew={rz['skew']:+.3f} "
          f"excess kurtosis={rz['excess_kurtosis']:+.3f}")
    print(f"  best={ls['best_family']}  -> maximum-entropy (two-moment) form "
          f"{'IS' if ls['maxent_consistent'] else 'is NOT'} adequate")

    print(f"\n=== 6. DOES THE ENSEMBLE CLAIM PREDICT THE INDIVIDUAL FAILURE RATE? ===")
    print(f"  {'F':>5}{'family':<20}{'predicted':>11}{'observed':>11}{'obs/pred':>10}")
    for c in r1['pass_fraction_checks']:
        print(f"  {c['tolerance_factor']:>5.2f}  {c['family']:<18}"
              f"{c['predicted_fraction']:>11.3f}{c['observed_fraction']:>11.3f}"
              f"{c['ratio']:>10.2f}")
    print(f"\n  PROHIBITION: {r1['prohibition']['statement']}")
    print(f"  REPLICATION: {r1['prohibition']['replication']}")


if __name__ == '__main__':
    main()
