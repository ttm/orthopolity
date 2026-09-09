"""R9: how much of tau is between ecosystems, and how much is one ecosystem
varying over time?

EXPLORATORY, not preregistered. Raised by the R8 source check: Gaedke's slopes
span -1.23 to -0.82 within a single lake across one season, so tau cannot be
read as "ecosystems differ by this much" until the two are separated.

The primary subset happens to contain the two designs that isolate each
component:
  Arranz et al. 2022  639 sites x 1 occasion each  -> between-site only
  Gaedke 1993           1 site  x 377 occasions    -> within-site only
Studies with several sites AND repeat visits are fitted jointly as a check.
"""
from pathlib import Path
import sys, json, csv, io
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from meta import variance_components, random_effects                   # noqa: E402

OUT = ROOT / 'results'


def num(s):
    s = (s or '').strip().strip('"')
    try:
        return float(s) if s not in ('', 'NA') else np.nan
    except ValueError:
        return np.nan


def load():
    sz = list(csv.DictReader(io.StringIO((ROOT / 'data/raw/GLOSSAQUA_Size.txt').read_text('utf-8')),
                             delimiter=' ', quotechar='"'))
    sm = list(csv.DictReader(io.StringIO((ROOT / 'data/raw/GLOSSAQUA_Sample.txt')
                                         .read_bytes().decode('latin-1')),
                             delimiter='\t', quotechar='"'))
    meta_by_site = {r['SiteID'].strip().strip('"'): r for r in sm}
    out = []
    for r in sz:
        if r['XaxisParameterType'].strip() != 'body mass':
            continue
        if r['SizeSpectrumMethod'].strip() != 'Normalized biomass spectrum (linear)':
            continue
        sl, lo, hi = num(r['Slope']), num(r['SizeRangeMinimum']), num(r['SizeRangeMaximum'])
        if not np.isfinite([sl, lo, hi]).all() or not (0 < lo < hi):
            continue
        cl, cu = num(r['SlopeConfIntLow']), num(r['SlopeConfIntUp'])
        se = (cu - cl) / (2 * 1.96) if np.isfinite([cl, cu]).all() and cu > cl else num(r['SlopeSE'])
        site = r['SiteID'].strip().strip('"')
        md = meta_by_site.get(site, {})
        out.append(dict(study=r['StudyID'].strip().strip('"'), site=site,
                        slope=sl, se=se,
                        hab=(md.get('Habitat') or '?').strip().strip('"')))
    return out


def main():
    d = load()
    res = dict(status='EXPLORATORY, not preregistered', components={})

    # Between-site: Arranz, 639 sites each seen once, all with reported errors.
    a = [x for x in d if x['study'] == 'StudyID_122']
    ra = random_effects([x['slope'] for x in a], [x['se'] for x in a])
    res['components']['between_site_arranz'] = dict(
        source='Arranz et al. 2022, 639 lakes, one occasion each',
        n=len(a), n_sites=len({x['site'] for x in a}),
        tau=ra['tau'], mu=ra['random_effects_mean'], median_se=ra['median_se'],
        raw_sd=ra['observed_sd'],
        interpretation='Each lake seen once, so this is between-site dispersion with '
                       'measurement error removed. It still contains any single-occasion '
                       'temporal deviation, so it is an upper bound on the purely spatial part.')

    # Within-site: Gaedke, one lake, 377 occasions. No reported errors.
    g = [x for x in d if x['study'] == 'StudyID_07']
    sl = np.array([x['slope'] for x in g])
    res['components']['within_site_gaedke'] = dict(
        source='Gaedke 1993, Lake Constance, one site, 377 occasions over 10 years',
        n=len(g), n_sites=len({x['site'] for x in g}),
        raw_sd=float(sl.std(ddof=1)), median=float(np.median(sl)),
        range=[float(sl.min()), float(sl.max())],
        errors_reported=int(np.isfinite([x['se'] for x in g]).sum()),
        interpretation='One lake, so all dispersion is temporal. No errors are reported, '
                       'so this raw SD is an UPPER bound on true temporal variation.')

    # Joint fit where a study has several sites and repeat visits.
    joint = []
    for s in sorted({x['study'] for x in d}):
        v = [x for x in d if x['study'] == s and np.isfinite(x['se']) and x['se'] >= 0]
        if len(v) < 20:
            continue
        sites = np.array([x['site'] for x in v])
        _, counts = np.unique(sites, return_counts=True)
        if (counts > 1).sum() < 2:
            continue
        vc = variance_components([x['slope'] for x in v], [x['se'] for x in v], sites)
        vc['study'] = s
        joint.append(vc)
    res['components']['joint_fits'] = joint

    tb = ra['tau']
    tw_ub = float(sl.std(ddof=1))
    frac_within = float(tw_ub ** 2 / tb ** 2)
    res['decomposition'] = dict(
        pooled_freshwater_tau=0.228,
        between_site_tau=tb, within_site_sd_upper=tw_ub,
        within_site_variance_share_upper=frac_within,
        implied_between_site_lower=float(np.sqrt(max(tb ** 2 - tw_ub ** 2, 0.0))),
        verdict=('dispersion is predominantly between ecosystems'
                 if frac_within < 0.25 else 'temporal variation is a major share'),
        note='Between-site and within-site are estimated from different studies and '
             'different ecosystems, so these are bounds rather than a partition of one '
             'variance. Subtracting them assumes the temporal component in Arranz lakes '
             'matches that in Lake Constance, which is an assumption, not a measurement.')
    (OUT / 'variance.json').write_text(json.dumps(res, indent=2, default=float))

    c = res['components']
    print('\n=== R9: WHERE THE DISPERSION LIVES ===\n')
    b = c['between_site_arranz']
    print(f"BETWEEN-SITE  {b['source']}")
    print(f"  n={b['n']} sites={b['n_sites']}  raw SD={b['raw_sd']:.3f}  median SE={b['median_se']:.3f}"
          f"  -> latent tau={b['tau']:.3f}  (mu={b['mu']:+.3f})")
    w = c['within_site_gaedke']
    print(f"\nWITHIN-SITE   {w['source']}")
    print(f"  n={w['n']} site={w['n_sites']}  raw SD={w['raw_sd']:.3f}  "
          f"range {w['range'][0]:.2f} to {w['range'][1]:.2f}  errors reported: {w['errors_reported']}")

    print('\nJOINT FITS (studies with several sites and repeat visits):')
    if not joint:
        print('  none: no study in the primary subset has both')
    for v in joint:
        if v['separable']:
            print(f"  {v['study']:<12} n={v['n']:>4} sites={v['n_groups']:>3} "
                  f"tau_between={v['tau_between']:.3f} tau_within={v['tau_within']:.3f} "
                  f"({v['fraction_between']:.0%} between)")
        else:
            print(f"  {v['study']:<12} n={v['n']:>4} sites={v['n_groups']:>3} "
                  f"total={v['total_latent_sd']:.3f}  -- {v['note']}")

    dec = res['decomposition']
    print(f"\nDECOMPOSITION of the pooled freshwater tau = {dec['pooled_freshwater_tau']}")
    print(f"  between-site tau           {dec['between_site_tau']:.3f}")
    print(f"  within-site SD (upper)     {dec['within_site_sd_upper']:.3f}")
    print(f"  within-site share of variance (upper bound)  "
          f"{dec['within_site_variance_share_upper']:.1%}")
    print(f"  -> {dec['verdict']}")
    print(f"\n  {dec['note']}")


if __name__ == '__main__':
    main()
