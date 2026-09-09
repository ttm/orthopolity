"""R7 and R5: is the heavy tail a mixture over classes, and is span a proxy for taxon?

EXPLORATORY, not preregistered. Follow-ups to evidence.md sections 6.4-6.5.

R7. The pooled latent slope distribution is heavier-tailed than the two-moment
    maximum-entropy form. If that is because the pool mixes classes with
    different tau, then (a) tau should differ across strata, (b) the Gaussian
    should be adequate *within* a stratum, and (c) a mixture built from the
    fitted per-stratum taus should reproduce the pooled excess kurtosis.

R5. Wider-spanning studies sit closer to -1, but span is partly a proxy for
    taxon. Testing the relation within taxon separates them, at whatever power
    four or five study blocks per taxon allows.
"""
from pathlib import Path
import sys, json, csv, io
import numpy as np
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from meta import latent_shape, random_effects                          # noqa: E402
sys.path.insert(0, str(ROOT / 'experiments'))
from run_ensemble import load, PREDICTED                               # noqa: E402

OUT = ROOT / 'results'
MIN_N, MIN_STUDIES = 60, 3
rng = np.random.default_rng(20260909)


def per_stratum_shape(d, key):
    out = {}
    for lab in sorted({x[key] for x in d}):
        g = [x for x in d if x[key] == lab]
        u = [x for x in g if np.isfinite(x['se']) and x['se'] > 0]
        ns = len({x['study'] for x in g})
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
                        gaussian_adequate=ls['maxent_consistent'],
                        excess_kurtosis=ls['gaussian_standardised_residuals']['excess_kurtosis'],
                        I_squared=re['I_squared'])
    return out


def mixture_check(d, strata, key):
    """Does a mixture of the fitted per-stratum Gaussians reproduce the pooled tail?"""
    parts = [(v['tau'], v['mu'], v['n']) for v in strata.values() if v.get('tau')]
    if len(parts) < 2:
        return dict(note='fewer than two fitted strata; mixture not identifiable')
    taus = np.array([p[0] for p in parts])
    mus = np.array([p[1] for p in parts])
    w = np.array([p[2] for p in parts], float)
    w /= w.sum()
    draw = rng.choice(len(parts), size=400_000, p=w)
    sim = rng.normal(mus[draw], taus[draw])
    z = (sim - sim.mean()) / sim.std()
    pooled = latent_shape([x['slope'] for x in d if np.isfinite(x['se']) and x['se'] > 0],
                          [x['se'] for x in d if np.isfinite(x['se']) and x['se'] > 0])
    return dict(stratifier=key, n_components=len(parts),
                tau_range=[float(taus.min()), float(taus.max())],
                tau_ratio=float(taus.max() / taus.min()),
                mixture_excess_kurtosis=float(((z ** 4).mean() - 3.0)),
                pooled_excess_kurtosis=pooled['gaussian_standardised_residuals']['excess_kurtosis'],
                pooled_best_family=pooled['best_family'])


def span_within_taxon(d, key='species'):
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


def main():
    d = load()
    strata = {k: per_stratum_shape(d, k) for k in ('habitat', 'species')}
    res = dict(status='EXPLORATORY follow-up, not preregistered',
               R7=dict(per_stratum=strata,
                       mixture={k: mixture_check(d, strata[k], k) for k in strata}),
               R5=dict(span_within_taxon=span_within_taxon(d),
                       note='Four or five study blocks per taxon is very low power; a null '
                            'result here does not resolve the confound, it only shows the '
                            'available data cannot.'))
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
                  f"gaussian_ok={v['gaussian_adequate']}")
    print('\n  mixture reconstruction of the pooled tail:')
    for key, m in res['R7']['mixture'].items():
        if 'note' in m:
            print(f"    [{key}] {m['note']}"); continue
        print(f"    [{key}] {m['n_components']} components, tau {m['tau_range'][0]:.3f}-"
              f"{m['tau_range'][1]:.3f} ({m['tau_ratio']:.2f}x)  "
              f"mixture exkurt={m['mixture_excess_kurtosis']:+.3f} vs "
              f"pooled {m['pooled_excess_kurtosis']:+.3f}")

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
