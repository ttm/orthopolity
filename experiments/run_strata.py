"""Exploratory habitat/taxon summaries and method-convention sensitivity.

Family rankings do not establish Gaussian adequacy. A mixture fitted to the
same data cannot establish that pooling caused the pooled distribution shape.
Cross-method subsets differ in populations and may encode different estimands;
these comparisons are not replication tests.
"""
from pathlib import Path
import sys, json, csv, io
import numpy as np
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from meta import latent_shape, random_effects                          # noqa: E402
sys.path.insert(0, str(ROOT / 'experiments'))
from run_ensemble import load, PREDICTED, INVALID_SPAN_STUDIES                               # noqa: E402

OUT = ROOT / 'results'
MIN_N, MIN_STUDIES = 60, 3
rng = np.random.default_rng(20260909)


def per_stratum_shape(d, key):
    out = {}
    for lab in sorted({x[key] for x in d}):
        g = [x for x in d if x[key] == lab]
        u = [x for x in g if np.isfinite(x['se']) and x['se'] > 0]
        ns = len({x['study'] for x in u})
        if len(u) < MIN_N or ns < MIN_STUDIES:
            out[lab] = dict(n=len(g), n_with_se=len(u), n_studies=ns,
                            note='too few for a latent-shape fit')
            continue
        ls = latent_shape([x['slope'] for x in u], [x['se'] for x in u])
        re = random_effects([x['slope'] for x in u], [x['se'] for x in u])
        out[lab] = dict(n=len(g), n_with_se=len(u), n_studies=ns,
                        tau=ls['families']['gaussian']['tau'],
                        mu=ls['families']['gaussian']['mu'],
                        best_family=ls['best_family'],
                        delta_aic=ls['delta_aic_vs_gaussian'],
                        gaussian_best_by_aic=ls['gaussian_best_by_aic'],
                        inference_note=ls['inference_note'],
                        excess_kurtosis=ls['gaussian_standardised_residuals']['excess_kurtosis'],
                        I_squared=re['I_squared'])
    return out


def mixture_check(d, strata, key):
    """Compare like-for-like standardized *observed* residual moments.

    Each retained observation keeps its stratum and supplied error. Expected
    second/fourth moments are computed analytically for the fitted normal
    mixture, with the same centering/scaling as the observed residuals.
    """
    fitted = {label: v for label, v in strata.items() if 'tau' in v}
    if len(fitted) < 2:
        return dict(note='fewer than two fitted strata; no mixture comparison')
    g = [x for x in d if x[key] in fitted and np.isfinite(x['se']) and x['se'] > 0]
    y = np.array([x['slope'] for x in g])
    errors = np.array([x['se'] for x in g])
    pooled = latent_shape(y, errors, families=('gaussian',))
    ref = pooled['families']['gaussian']
    denominator = np.sqrt(ref['tau'] ** 2 + errors ** 2)
    means = (np.array([fitted[x[key]]['mu'] for x in g]) - ref['mu']) / denominator
    variances = (np.array([fitted[x[key]]['tau'] ** 2 for x in g]) + errors ** 2) / denominator ** 2
    centered = means - means.mean()
    m2 = np.mean(variances + centered ** 2)
    m4 = np.mean(3 * variances ** 2 + 6 * variances * centered ** 2 + centered ** 4)
    taus = [v['tau'] for v in fitted.values()]
    return dict(stratifier=key, n_components=len(fitted), n_matched=len(g),
                component_counts={lab: sum(x[key] == lab for x in g) for lab in fitted},
                tau_range=[float(min(taus)), float(max(taus))],
                tau_ratio=float(max(taus) / min(taus)),
                mixture_excess_kurtosis=float(m4 / m2 ** 2 - 3),
                pooled_excess_kurtosis=pooled['gaussian_standardised_residuals']['excess_kurtosis'],
                interpretation='In-sample observed-residual moment comparison with matched '
                               'stratum weights and measurement errors; no causal attribution '
                               'or test of absolute distributional fit.')


def span_within_taxon(d, key='species'):
    d = [x for x in d if x['study'] not in INVALID_SPAN_STUDIES]
    out = {}
    for lab in sorted({x[key] for x in d}):
        g = [x for x in d if x[key] == lab]
        studies = sorted({x['study'] for x in g})
        if len(studies) < 4:
            continue
        xs, ys = [], []
        for s in studies:
            v = [x for x in g if x['study'] == s]
            xs.append(np.median([x['span'] for x in v]) / np.log(10))
            ys.append(np.median([abs(x['slope'] - PREDICTED) for x in v]))
        if max(xs) / max(min(xs), 1e-9) < 1.5:
            out[lab] = dict(n_studies=len(studies), note='no span variation within taxon')
            continue
        rho, p = spearmanr(xs, ys)
        out[lab] = dict(n_studies=len(studies), n_spectra=len(g),
                        span_range_decades=[float(min(xs)), float(max(xs))],
                        spearman_rho=float(rho), spearman_p=float(p),
                        significant=bool(p < 0.05))
    return out


def cross_method_replication():
    """Descriptive comparisons under provisional method-to-exponent mappings."""
    import csv as _csv
    sz = list(_csv.DictReader(io.StringIO((ROOT / 'data/raw/GLOSSAQUA_Size.txt').read_text('utf-8')),
                              delimiter=' ', quotechar='"'))
    sm = list(_csv.DictReader(io.StringIO((ROOT / 'data/raw/GLOSSAQUA_Sample.txt').read_bytes()
                                          .decode('latin-1')), delimiter='\t', quotechar='"'))
    meta_by_site = {r['SiteID'].strip().strip('"'): r for r in sm}

    def num(s):
        s = (s or '').strip().strip('"')
        try:
            return float(s) if s not in ('', 'NA') else np.nan
        except ValueError:
            return np.nan

    predicted = {'Normalized biomass spectrum (linear)': -1.0,
                 'Normalized abundance spectrum (linear)': -2.0,
                 'Maximum Likelihood': -2.0}
    subsets = {m: [] for m in predicted}
    for r in sz:
        if r['XaxisParameterType'].strip() != 'body mass':
            continue
        m = r['SizeSpectrumMethod'].strip()
        if m not in predicted:
            continue
        sl, lo, hi = num(r['Slope']), num(r['SizeRangeMinimum']), num(r['SizeRangeMaximum'])
        if not np.isfinite([sl, lo, hi]).all() or not (0 < lo < hi):
            continue
        cl, cu = num(r['SlopeConfIntLow']), num(r['SlopeConfIntUp'])
        se = (cu - cl) / (2 * 1.96) if np.isfinite([cl, cu]).all() and cu > cl else num(r['SlopeSE'])
        md = meta_by_site.get(r['SiteID'].strip().strip('"'), {})
        subsets[m].append(dict(study=r['StudyID'].strip().strip('"'), dep=sl - predicted[m],
                               se=se, hab=(md.get('Habitat') or '?').strip().strip('"')))

    nbss = {x['study'] for x in subsets['Normalized biomass spectrum (linear)']}
    out = dict(overlap={}, fits=[])
    for m, v in subsets.items():
        s = {x['study'] for x in v}
        out['overlap'][m] = dict(n_studies=len(s), shared_with_nbss=len(s & nbss),
                                 new=len(s - nbss))
    for m, v in subsets.items():
        for hab in ('Freshwater', 'Marine'):
            g = [x for x in v if x['hab'] == hab and np.isfinite(x['se']) and x['se'] > 0]
            ns = len({x['study'] for x in g})
            if len(g) < MIN_N or ns < MIN_STUDIES:
                continue
            ls = latent_shape([x['dep'] for x in g], [x['se'] for x in g], families=('gaussian',))
            gg = ls['families']['gaussian']
            out['fits'].append(dict(method=m, habitat=hab, n=len(g), n_studies=ns,
                                    tau=gg['tau'], mu=gg['mu']))
    fw = [f for f in out['fits'] if f['habitat'] == 'Freshwater']
    if len(fw) > 1:
        taus = [f['tau'] for f in fw]
        out['freshwater_comparison'] = dict(
            n_methods=len(fw), tau_values=taus,
            tau_ratio=float(max(taus) / min(taus)),
            mu_values=[f['mu'] for f in fw],
            interpretation='No replication verdict: estimands and study populations '
                           'have not been harmonized.')
    out['confound'] = ('Method labels may encode incompatible estimands. Method and '
                       'study population are perfectly confounded: the three subsets '
                       'share no studies. A discrepancy cannot be attributed to the convention '
                       'rather than to the systems, or the reverse.')
    return out


def main():
    d = load()
    strata = {k: per_stratum_shape(d, k) for k in ('habitat', 'species')}
    res = dict(status='EXPLORATORY follow-up, not preregistered',
               R7=dict(per_stratum=strata,
                       mixture={k: mixture_check(d, strata[k], k) for k in strata}),
               R4_partial=cross_method_replication(),
               R5=dict(span_within_taxon=span_within_taxon(d),
                       span_metadata_exclusions=INVALID_SPAN_STUDIES,
                       note='Only four or five study blocks are available per taxon. Nonsignificance '
                            'does not establish absence of an association or identify low '
                            'power as its cause.'))
    (OUT / 'strata.json').write_text(json.dumps(res, indent=2, default=float))

    print('\n=== R7: LATENT SHAPE WITHIN STRATA ===')
    for key, st in strata.items():
        print(f'  [{key}]')
        for lab, v in st.items():
            if 'tau' not in v:
                print(f"    {lab[:34]:<34} n={v['n']:>4} ({v['n_studies']} st.)  {v['note']}")
                continue
            print(f"    {lab[:34]:<34} n={v['n_with_se']:>4} ({v['n_studies']} st.)  "
                  f"mu={v['mu']:+.3f} tau={v['tau']:.3f}  best={v['best_family']:<13}"
                  f"exkurt={v['excess_kurtosis']:+.2f}  "
                  f"gaussian_best_by_aic={v['gaussian_best_by_aic']}")
    print('\n  mixture reconstruction of the pooled tail:')
    for key, m in res['R7']['mixture'].items():
        if 'note' in m:
            print(f"    [{key}] {m['note']}"); continue
        print(f"    [{key}] {m['n_components']} components, tau {m['tau_range'][0]:.3f}-"
              f"{m['tau_range'][1]:.3f} ({m['tau_ratio']:.2f}x)  "
              f"mixture exkurt={m['mixture_excess_kurtosis']:+.3f} vs "
              f"pooled {m['pooled_excess_kurtosis']:+.3f}")

    cm = res['R4_partial']
    print('\n=== R4-partial: CROSS-METHOD DESCRIPTIVE COMPARISON ===')
    print('  study overlap:')
    for m, v in cm['overlap'].items():
        print(f"    {m[:40]:<42}{v['n_studies']:>3} studies, {v['shared_with_nbss']:>3} shared "
              f"with NBSS, {v['new']:>3} new")
    print(f"  {'method':<42}{'habitat':<12}{'n':>6}{'st.':>5}{'tau':>8}{'mu':>9}")
    for f in cm['fits']:
        print(f"    {f['method'][:40]:<42}{f['habitat']:<12}{f['n']:>6}{f['n_studies']:>5}"
              f"{f['tau']:>8.3f}{f['mu']:>+9.3f}")
    fr = cm.get('freshwater_comparison')
    if fr:
        print(f"\n  freshwater tau across {fr['n_methods']} conventions: "
              f"{[round(v,3) for v in fr['tau_values']]}  (ratio {fr['tau_ratio']:.2f}x)")
        print(f"  freshwater mu:  {[round(v,3) for v in fr['mu_values']]}")
        print(f"  {fr['interpretation']}")
    print(f"  CONFOUND: {cm['confound']}")

    print('\n=== R5: SPAN vs |DEPARTURE| WITHIN TAXON (study level) ===')
    for lab, v in res['R5']['span_within_taxon'].items():
        if 'spearman_rho' not in v:
            print(f"    {lab[:34]:<34} {v['note']}"); continue
        print(f"    {lab[:34]:<34} {v['n_studies']} studies, span "
              f"{v['span_range_decades'][0]:.1f}-{v['span_range_decades'][1]:.1f} dec  "
              f"rho={v['spearman_rho']:+.3f} p={v['spearman_p']:.3f}  "
              f"{'significant' if v['significant'] else 'not significant'}")
    print(f"\n  {res['R5']['note']}")


if __name__ == '__main__':
    main()
