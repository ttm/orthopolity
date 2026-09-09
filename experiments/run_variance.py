"""Exploratory descriptions of spatial and repeated-site slope variation.

One observation per lake mixes spatial and single-occasion variation. Repeated
observations in a different lake cannot partition or bound that mixture.
Joint random-intercept fits additionally assume independent within-site errors.
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
    res['components']['cross_sectional_arranz'] = dict(
        source='Arranz et al. 2022, 639 lakes, one occasion each',
        n=len(a), n_sites=len({x['site'] for x in a}),
        tau=ra['tau'], mu=ra['random_effects_mean'], median_se=ra['median_se'],
        raw_sd=ra['observed_sd'],
        interpretation='Cross-sectional dispersion after subtracting the supplied sampling '
                       'variances under the fitted model. Spatial differences and '
                       'single-occasion temporal deviations cannot be separated.')

    # Within-site: Gaedke, one lake, 377 occasions. No reported errors.
    g = [x for x in d if x['study'] == 'StudyID_07']
    sl = np.array([x['slope'] for x in g])
    res['components']['within_site_gaedke'] = dict(
        source='Gaedke 1993, Lake Constance, one site, 377 occasions over 10 years',
        n=len(g), n_sites=len({x['site'] for x in g}),
        raw_sd=float(sl.std(ddof=1)), median=float(np.median(sl)),
        range=[float(sl.min()), float(sl.max())],
        errors_reported=int(np.isfinite([x['se'] for x in g]).sum()),
        interpretation='Observed variation among repeated measurements in one lake; it '
                       'combines temporal changes, sampling error and other measurement '
                       'differences. Temporal dependence is not modeled. It cannot bound '
                       'temporal variation in the other study.')

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

    res['comparison'] = dict(
        cross_sectional_latent_tau=ra['tau'], repeated_site_observed_sd=float(sl.std(ddof=1)),
        note='Different ecosystems, taxa, sampling designs and error availability. These '
             'quantities are descriptive comparisons, not components of one variance. '
             'No temporal variance share or between-site lower bound is identified.')
    for fit in joint:
        fit['assumptions'] = ('Independent Gaussian site effects and independent within-site '
                              'residuals with known measurement variances; neither serial '
                              'dependence nor uncertainty in reported errors is modeled.')
    (OUT / 'variance.json').write_text(json.dumps(res, indent=2, default=float))

    c = res['components']
    print('\n=== R9: WHERE THE DISPERSION LIVES ===\n')
    b = c['cross_sectional_arranz']
    print(f"CROSS-SECTIONAL  {b['source']}")
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

    print(f"\n  {res['comparison']['note']}")


if __name__ == '__main__':
    main()
