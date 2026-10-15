"""Hydraulics-only predictors for a retrospective narrow-to-wide transfer.

Deal et al. (2023, 2026); Guo (2015). No source response is converted by
``read_predictors``. Scalar source conventions are explicit in the protocol.
"""
import csv
import math

import numpy as np
from scipy.optimize import minimize_scalar
from scipy.special import lambertw

G, NU, KAPPA = 9.81, 1e-6, .41
MODELS = ('guo_shape', 'guo_unity', 'radius_shape', 'depth_shape')


def table(path):
    with open(path, newline='') as f:
        return list(csv.DictReader(f))


def number(value):
    if value == '':
        return None
    x = float(value)
    return x if math.isfinite(x) else None


def wall_factors(width, depth, slope, discharge, diameter):
    """Return all hydraulic factors, including invalid-domain diagnostics.

    For a negative Guo radicand, return the real part of the complete complex
    expression, matching the published convention; never silently clip it.
    """
    if not all(math.isfinite(x) and x > 0 for x in
               (width, depth, slope, discharge, diameter)):
        raise ValueError('Hydraulic inputs must be positive and finite')
    alpha = width / depth
    radius = width * depth / (width + 2 * depth)
    velocity = discharge / (width * depth)
    friction = G * radius * slope / velocity**2
    reynolds = radius * velocity / NU
    roughness = 15 * depth / diameter
    beta = (.75 - 1 / math.pi**2) / KAPPA
    phi = math.exp(-(alpha / math.pi)**1.5)
    psi = math.sqrt(2 / alpha) * ((math.log(roughness) - 1) / KAPPA
        - (1 + phi)**3 / (12 * KAPPA)
        + (1 + math.sqrt(phi)) / 2 * (1 + math.sin(math.pi * phi)
                                     / (math.pi * (1 + phi))))
    radicand = (beta**2 + psi**2) * (1 + alpha / 2) * friction - 1
    numerator = ((beta - psi * complex(radicand)**.5)**2).real
    guo = 1 - numerator / ((beta**2 + psi**2)**2 * (1 + alpha / 2) * friction)
    fwall = .018409368 / float(lambertw(.224072094 * (reynolds / friction)**(1/3)).real)**2
    return dict(alpha=alpha, radius=radius, velocity=velocity, friction=friction,
                reynolds=reynolds, relative_roughness=roughness,
                radicand=radicand, guo=guo, radius_factor=radius/depth,
                vanoni_brooks=1-fwall/friction/(1+alpha/2))


def shape_factor(corey, settling, sphere_settling, repose_degrees, bed_gradient):
    mu0 = math.tan(math.radians(24))
    mu = math.tan(math.radians(repose_degrees))
    if min(corey, settling, sphere_settling) <= 0 or bed_gradient >= min(mu, mu0):
        raise ValueError('Invalid grain resistance/settling inputs')
    cstar = corey * (sphere_settling / settling)**2
    mustar = (mu - bed_gradient) / (mu0 - bed_gradient)
    return dict(cstar=cstar, mustar=mustar, shape=cstar/mustar)


def read_predictors(base):
    """Read published cohort identities and primitive predictors, never flux.

    S3 contributes its pre-existing cohort and W,H,S,Q,D,rf only. Match to raw
    summaries using hydraulic coordinates, not source transport/derived stress.
    """
    raw = base/'02_data/source_data'
    old = table(raw/'Deal_2023_exp_data.txt')
    wide = {g: table(raw/f'{g}_5_data_WF.csv') for g in ('gb', 'ng')}
    properties = {}
    for cohort, suffix in [('narrow', ''), ('wide', '_WF')]:
        props = {}
        for label in ('1_var_density', '2_var_shape', '3_var_ARS',
                      '4_var_settling_velocities', '5_var_VES_settling_velocity'):
            props[label] = {r['']: r for r in table(raw/f'{label}{suffix}.csv')}
        properties[cohort] = props
    source = table(base/'02_data/deal_dataset_S3.csv')
    rows, excluded = [], []
    for source_row, r in enumerate(source, 2):
        if r['data_source'] not in ('Deal et al., 2023', 'New experiments') or r['grain_kind'] not in ('sphere', 'gravel'):
            continue
        p = {k: number(r[k]) for k in ('W', 'H', 'S', 'Q', 'D', 'rf')}
        cohort = 'narrow' if r['data_source'] == 'Deal et al., 2023' else 'wide'
        grain = 'gb' if r['grain_kind'] == 'sphere' else 'ng'
        candidates = []
        for raw_row, candidate in enumerate(old if cohort == 'narrow' else wide[grain], 2):
            if cohort == 'narrow' and candidate['grain_kind'] != grain:
                continue
            h = number(candidate['flow_depth'])
            s = number(candidate['water_slope'])
            if cohort == 'wide' and s is not None:
                s = math.tan(math.radians(s))
            q = number(candidate['discharge'])
            if cohort == 'narrow' and q is not None:
                q /= 1000
            if (h is not None and s is not None
                    and math.isclose(h, p['H'], rel_tol=1e-12)
                    and math.isclose(s, p['S'], rel_tol=1e-12)
                    and (cohort == 'wide' or (q is None and p['Q'] is None)
                         or (q is not None and p['Q'] is not None
                             and math.isclose(q, p['Q'], rel_tol=1e-12)))):
                candidates.append((raw_row, candidate))
        if len(candidates) != 1:
            raise ValueError(f'Nonunique hydraulic source match: S3 row {source_row}')
        raw_row, c = candidates[0]
        identity = c['names' if cohort == 'narrow' else 'name']
        missing = [k for k, v in p.items() if v is None]
        if missing:
            excluded.append(dict(id=identity, source_row=source_row, missing=missing))
            continue
        props = properties[cohort]
        density = float(props['1_var_density'][grain]['total_grain_ro'])
        fluid_density = float(c['fluid_density']) if cohort == 'narrow' else 995.
        if not math.isclose(p['rf'], density / fluid_density - 1, rel_tol=1e-12):
            raise ValueError('Density provenance mismatch')
        diameter = float(props['2_var_shape'][grain]['dn'])
        if not math.isclose(diameter, p['D'], rel_tol=1e-12):
            raise ValueError('Grain diameter provenance mismatch')
        bed = float(c['bed_slope'])
        if cohort == 'wide':
            bed = math.tan(math.radians(bed))
        s = shape_factor(float(props['2_var_shape'][grain]['CSF']),
                         float(props['4_var_settling_velocities'][grain]['vel_mean']),
                         float(props['5_var_VES_settling_velocity'][grain]['ws_sphere']),
                         float(props['3_var_ARS'][grain]['mean_angle']), bed)
        wall = wall_factors(p['W'], p['H'], p['S'], p['Q'], p['D'])
        raw_name = 'Deal_2023_exp_data.txt' if cohort == 'narrow' else f'{grain}_5_data_WF.csv'
        row = dict(id=identity, cohort=cohort, grain=r['grain_kind'], source_row=source_row,
                   raw_file=raw_name, raw_row=raw_row, **p, density=density,
                   fluid_density=fluid_density, bed_gradient=bed, **s, wall=wall)
        row['stress_depth'] = p['H'] * p['S'] / (p['rf'] * p['D'])
        row['mass_per_dimensionless_flux'] = density * p['W'] * math.sqrt(G*p['rf']*p['D']**3)
        row['qualified_hydraulics'] = (wall['radicand'] >= 0
            and wall['radius_factor'] <= wall['guo'] <= 1)
        rows.append(row)
    if len({r['id'] for r in rows}) != len(rows):
        raise ValueError('Repeated run identity')
    return dict(rows=rows, excluded=excluded)


def stress(row, model):
    if model not in MODELS:
        raise ValueError('Unknown model')
    wall = row['wall']['guo'] if model.startswith('guo') else (
        row['wall']['radius_factor'] if model.startswith('radius') else 1.)
    shape = row['shape'] if model.endswith('shape') else 1.
    return row['stress_depth'] * wall * shape


def transport(stresses, amplitude, threshold):
    return amplitude * np.maximum(np.asarray(stresses)-threshold, 0)**1.5


def fit_transport(stresses, responses, weights):
    """Profile nonnegative amplitude over a fixed, densely bracketed threshold.

    Search each active-set interval at 33 equally spaced nodes, refine every
    local grid minimum, retain all boundaries. The independent verifier uses
    a separate two-parameter optimizer. No wide-response-dependent choices.
    """
    x, y, w = map(lambda v: np.asarray(v, dtype=float), (stresses, responses, weights))
    if (x.ndim != 1 or y.shape != x.shape or w.shape != x.shape or len(x) < 3
            or not all(np.isfinite(v).all() for v in (x, y, w))
            or np.any(x <= 0) or np.any(y < 0) or np.any(w <= 0) or not np.any(y > 0)):
        raise ValueError('Invalid calibration inputs')
    w = w / w.sum()
    def profile(t):
        h = np.maximum(x-t, 0)**1.5
        den = np.sum(w*h*h)
        a = np.sum(w*h*y)/den if den else 0.
        return float(np.sum(w*(a*h-y)**2)), float(a)
    knots = np.r_[0., np.unique(x)]
    nodes = np.unique(np.concatenate([np.linspace(lo, hi, 33) for lo, hi in zip(knots[:-1], knots[1:])]))
    scores = [profile(t)[0] for t in nodes]
    candidates = list(zip(scores, nodes))
    for i in range(1, len(nodes)-1):
        if scores[i] <= scores[i-1] and scores[i] <= scores[i+1]:
            fit = minimize_scalar(lambda t: profile(t)[0], bounds=(nodes[i-1], nodes[i+1]),
                                  method='bounded', options={'xatol': 1e-14})
            candidates.append((float(fit.fun), float(fit.x)))
    score, threshold = min(candidates)
    return dict(amplitude=profile(threshold)[1], threshold=float(threshold), mse=score,
                threshold_at_zero=bool(threshold == 0),
                active_calibration_count=int(np.sum(x > threshold)),
                threshold_profile=[dict(threshold=float(t), mse=profile(t)[0], amplitude=profile(t)[1])
                    for t in np.unique(np.clip(threshold + np.array([-1, 0, 1])*.01*(x.max()-x.min()), 0, x.max()))],
                stress_range=[float(x.min()), float(x.max())])


def weights(rows):
    """Equal material weight, then equal run weight within each material."""
    kinds = {r['grain'] for r in rows}
    return np.array([1 / (len(kinds)*sum(x['grain'] == r['grain'] for x in rows)) for r in rows])
