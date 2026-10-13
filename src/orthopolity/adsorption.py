"""Pure-to-mixture adsorption models; units MPa, K, mmol/g.

Counting measure over two species and vacancies. Langmuir and IAST are
established conditional models, not consequences of conservation alone.
"""
import shlex
from pathlib import Path

import numpy as np
from scipy.optimize import brentq, least_squares, minimize_scalar


def read_aif(path, columns):
    """Convert only requested loop columns; target uptake may stay unparsed."""
    names, rows, active = [], [], False
    for raw in Path(path).read_text(encoding='utf-8-sig').splitlines():
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        if line == 'loop_':
            if active:
                raise ValueError('Multiple loops need explicit qualification')
            active = True
        elif active and line.startswith('_'):
            names.append(line)
        elif active:
            tokens = shlex.split(line)
            if len(tokens) != len(names):
                raise ValueError('Malformed AIF row')
            rows.append([float(tokens[names.index(c)]) for c in columns])
    result = np.asarray(rows, dtype=float)
    if result.ndim != 2 or not np.all(np.isfinite(result)):
        raise ValueError('Missing/nonfinite requested data')
    return result


def fugacity(temperature, pressure, fractions, constants, ideal=False):
    """PR1976 vapor root, classical mixing with k_ij=0; return MPa."""
    y = np.asarray(fractions, dtype=float)
    if (temperature <= 0 or pressure < 0 or y.shape != (2,) or
            np.any(y < 0) or not np.isclose(y.sum(), 1, atol=1e-12, rtol=0)):
        raise ValueError('Invalid thermodynamic state')
    if ideal or pressure == 0:
        return pressure*y
    tc, pc, omega = np.asarray(constants, dtype=float).T
    r = 8.31446261815324
    kappa = .37464+1.54226*omega-.26992*omega**2
    a = .45724*r*r*tc*tc/pc*(1+kappa*(1-np.sqrt(temperature/tc)))**2
    b = .07780*r*tc/pc
    cross = np.sqrt(a[:, None]*a[None, :])
    am, bm = y@cross@y, y@b
    p = pressure*1e6
    aa, bb = am*p/(r*temperature)**2, bm*p/(r*temperature)
    roots = np.roots([1, -(1-bb), aa-3*bb**2-2*bb, -(aa*bb-bb**2-bb**3)])
    real = [z.real for z in roots if abs(z.imag) < 1e-9 and z.real > bb]
    if not real:
        raise ValueError('No physical vapor root')
    z = max(real)
    # Restrict to a single physical root: no untested phase-stability claim.
    if len(real) != 1:
        raise ValueError('Multiple physical EOS roots; phase qualification required')
    log_phi = (b/bm*(z-1)-np.log(z-bb)
        - aa/(2*np.sqrt(2)*bb)*(2*(cross@y)/am-b/bm)
        * np.log((z+(1+np.sqrt(2))*bb)/(z+(1-np.sqrt(2))*bb)))
    return pressure*y*np.exp(log_phi)


def langmuir(f, capacity, affinity):
    f = np.asarray(f, dtype=float)
    return capacity*affinity*f/(1+affinity*f)


def competitive(f, capacity, affinities):
    activity = np.asarray(f)*np.asarray(affinities)
    return capacity*activity/(1+activity.sum(axis=-1, keepdims=True))


def iast(f, capacities, affinities):
    """Analytic Langmuir spreading integrals, scalar pressure root."""
    f, q, b = (np.asarray(x, dtype=float) for x in (f, capacities, affinities))
    if np.any(f < 0) or np.any(q <= 0) or np.any(b <= 0):
        raise ValueError('Invalid IAST inputs')
    present = f > 0
    if not present.any():
        return np.zeros(2), np.zeros(2)
    if present.sum() == 1:
        return np.where(present, langmuir(f, q, b), 0), f.copy()
    def balance(pi):
        return np.sum(f*b/np.expm1(np.minimum(pi/q, 700)))-1
    hi = max(q*np.log1p(b*f))*2
    while balance(hi) > 0:
        hi *= 2
    pi = brentq(balance, hi*1e-14, hi, xtol=1e-13, rtol=1e-13)
    f0 = np.expm1(pi/q)/b
    x = f/f0
    total = 1/np.sum(x/langmuir(f0, q, b))
    return x*total, f0


def fit_pure(fugacities, amounts, uncertainties, shared=True):
    """Fixed multistart weighted fit; uncertainties are reported expanded U."""
    fs, qs, us = [list(map(np.asarray, x)) for x in (fugacities, amounts, uncertainties)]
    if len(fs) != 2 or any(np.any(u <= 0) for u in us):
        raise ValueError('Two gases and positive uncertainties required')
    nparam = 3 if shared else 4
    lower = np.log([1e-3]*(1 if shared else 2)+[1e-6]*2)
    upper = np.log([1e3]*(1 if shared else 2)+[1e6]*2)
    def unpack(theta):
        vals = np.exp(theta)
        return (np.repeat(vals[0], 2), vals[1:]) if shared else (vals[:2], vals[2:])
    def residual(theta):
        cap, aff = unpack(theta)
        return np.concatenate([(langmuir(f, cap[i], aff[i])-qs[i])/(us[i]/2)
                               for i, f in enumerate(fs)])
    fits = []
    for scale in [1.01, 2., 10.]:
        for affinity in [.1, 1., 10.]:
            caps = [max(map(np.max, qs))*scale] if shared else [max(q)*scale for q in qs]
            start = np.clip(np.log(caps+[affinity/np.median(f) for f in fs]), lower+1e-5, upper-1e-5)
            fits.append(least_squares(residual, start, bounds=(lower, upper),
                xtol=1e-12, ftol=1e-12, gtol=1e-12, max_nfev=3000))
    fit = min(fits, key=lambda x: np.sum(x.fun*x.fun))
    cap, aff = unpack(fit.x)
    sv = np.linalg.svd(fit.jac, compute_uv=False)
    bound = bool(np.any(fit.x-lower < 1e-4) or np.any(upper-fit.x < 1e-4))
    covariance = np.linalg.pinv(fit.jac.T@fit.jac)
    sd = np.sqrt(np.diag(covariance))
    corr = covariance/np.outer(sd, sd)
    profiles = []
    # Deterministic capacity sensitivity, not a confidence interval: U has
    # cross-point covariance that is unavailable. A broad profile flags weak
    # identification even if an optimizer returns an interior estimate.
    for factor in [.25, .5, 1., 2., 4.]:
        chosen = cap*factor
        objectives = []
        for i in range(2):
            obj = lambda logb: np.sum(((langmuir(fs[i], chosen[i], np.exp(logb))-qs[i])/(us[i]/2))**2)
            opt = minimize_scalar(obj, bounds=(np.log(1e-6), np.log(1e6)), method='bounded', options={'xatol':1e-12})
            objectives.append(float(opt.fun))
        profiles.append(dict(capacity_factor=factor, weighted_sse=float(sum(objectives))))
    sse = float(fit.fun@fit.fun)
    identified = bool(fit.success and not bound and sv[0]/sv[-1] < 1e6
        and all(p['weighted_sse'] > sse+3.84 for p in [profiles[1], profiles[3]]))
    predicted = [langmuir(f, cap[i], aff[i]) for i, f in enumerate(fs)]
    rmse = [float(np.sqrt(np.mean((p-q)**2))) for p, q in zip(predicted, qs)]
    ranges = [float(max(q)) for q in qs]
    return dict(capacities=cap.tolist(), affinities=aff.tolist(), shared=shared,
        optimizer_success=bool(fit.success), optimizer_bound_hit=bound,
        jacobian_condition=float(sv[0]/sv[-1]), parameter_correlation=corr.tolist(),
        weighted_sse=sse, n_parameters=nparam, n_observations=sum(map(len, fs)),
        capacity_profile=profiles, locally_identified=identified,
        rmse_mmol_g=rmse, normalized_rmse=[a/b for a,b in zip(rmse,ranges)],
        pure_max_mmol_g=ranges, max_fugacity_MPa=[float(max(f)) for f in fs],
        max_occupancy=[float(max(aff[i]*f/(1+aff[i]*f))) for i,f in enumerate(fs)],
        pure_fit_adequate=bool(all(a/b <= .05 for a,b in zip(rmse,ranges))))
