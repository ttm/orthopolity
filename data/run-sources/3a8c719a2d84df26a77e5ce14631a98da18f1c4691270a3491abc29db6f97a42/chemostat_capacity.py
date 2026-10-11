"""Certified conditional redistribution bounds; no empirical fitting.

The bounds allow arbitrary nonnegative two-resource prices at both times.
They do not establish that preliminary-culture quotas describe mixed vessels.
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import linprog


def _positive(values, name):
    result = np.asarray(values, dtype=float)
    if not np.all(np.isfinite(result)) or np.any(result <= 0):
        raise ValueError(f"{name} must be positive and finite")
    return result


def ratio_intervals(nitrogen, carbon):
    """Three-group C:N intervals from Cr, Ca, Mo, Co densities.

Any Mo/Co volume mixture has a ratio between its constituent ratios;
the mixture need not be the same at the two observations.
"""
    n = _positive(nitrogen, "Nitrogen densities")
    c = _positive(carbon, "Carbon densities")
    if n.shape != (4,) or c.shape != (4,):
        raise ValueError("Four species in Cr, Ca, Mo, Co order are required")
    r = c/n
    return np.array([[r[0], r[0]], [r[1], r[1]], [min(r[2:]), max(r[2:])]])


def redistribution_bound(initial_intervals, final_intervals):
    """Conservative TV bound for every price pair and admitted ratio choice.

For i != j, f_i/f_j <= max(1,r0_i/r0_j) max(1,rt_j/rt_i).
The returned multiplier span bound K implies TV <= (sqrt(K)-1)/(sqrt(K)+1).
This is sharp over unrestricted starting shares; for an observed starting
profile and linked mixture choices it can be conservative.
"""
    r0 = _positive(initial_intervals, "Initial ratio intervals")
    rt = _positive(final_intervals, "Final ratio intervals")
    if r0.ndim != 2 or r0.shape[1] != 2 or r0.shape != rt.shape or len(r0) < 2:
        raise ValueError("Matching group-by-two interval arrays are required")
    if np.any(r0[:, 0] > r0[:, 1]) or np.any(rt[:, 0] > rt[:, 1]):
        raise ValueError("Interval endpoints must be ordered")
    spans = np.ones((len(r0), len(r0)))
    for i in range(len(r0)):
        for j in range(len(r0)):
            if i != j:
                spans[i, j] = max(1., r0[i, 1]/r0[j, 0])*max(1., rt[j, 1]/rt[i, 0])
    if not np.all(np.isfinite(spans)):
        raise ValueError("Multiplier bound overflow")
    k = float(np.max(spans))
    root = np.sqrt(k)
    return dict(multiplier_span_upper=k, tv_upper=float((root-1)/(root+1)),
                pairwise_span_upper=spans.tolist(),
                initial_ratio_intervals=r0.tolist(), final_ratio_intervals=rt.tolist())


def nitrogen_share_segment(volumes, species_densities):
    """Endpoints of all three-group N shares over an unknown Mo/Co mixture.

The parameter along the share segment is not the biovolume mixture fraction.
"""
    volume = np.asarray(volumes, dtype=float)
    density = _positive(species_densities, "Species nitrogen densities")
    if (volume.shape != (3,) or density.shape != (4,)
            or not np.all(np.isfinite(volume)) or np.any(volume < 0)
            or np.sum(volume) <= 0):
        raise ValueError("Three nonnegative finite volumes with positive sum are required")
    endpoints = []
    for pooled in (density[2], density[3]):
        stock = volume*np.array([density[0], density[1], pooled])
        endpoints.append(stock/np.sum(stock))
    return np.asarray(endpoints)


def segment_tv_range(first_segment, second_segment):
    """Exact minimum and maximum TV between two probability segments.

Minimum: a linear program in the two segment positions and absolute residuals.
Maximum: a corner of the position square by convexity. The minimum mixes need
not attain the conservative theoretical upper bound; this only makes the
resulting exceedance check more conservative.
"""
    first = np.asarray(first_segment, dtype=float)
    second = np.asarray(second_segment, dtype=float)
    if (first.ndim != 2 or first.shape[0] != 2 or first.shape != second.shape
            or not np.all(np.isfinite(first)) or not np.all(np.isfinite(second))
            or np.any(first < 0) or np.any(second < 0)
            or not np.allclose(first.sum(axis=1), 1., rtol=0., atol=1e-12)
            or not np.allclose(second.sum(axis=1), 1., rtol=0., atol=1e-12)):
        raise ValueError("Two pairs of probability-vector endpoints are required")
    n = first.shape[1]
    delta = first[0]-second[0]
    direction = np.column_stack((first[1]-first[0], -(second[1]-second[0])))
    inequalities = np.vstack((np.column_stack((direction, -np.eye(n))),
                              np.column_stack((-direction, -np.eye(n)))))
    solution = linprog(np.r_[0., 0., np.full(n, .5)], A_ub=inequalities,
                      b_ub=np.r_[-delta, delta],
                      bounds=[(0., 1.), (0., 1.)]+[(0., None)]*n,
                      method="highs")
    if not solution.success:
        raise RuntimeError("Mixture-envelope optimization failed: "+solution.message)
    positions = np.clip(solution.x[:2], 0., 1.)
    witness_first = first[0]+positions[0]*(first[1]-first[0])
    witness_second = second[0]+positions[1]*(second[1]-second[0])
    witness_tv = .5*float(np.sum(np.abs(witness_first-witness_second)))
    if abs(witness_tv-solution.fun) > 1e-8:
        raise RuntimeError("Mixture-envelope objective and witness disagree")
    # A primal optimum is an upper bound on minimum TV. For exclusion we
    # instead use a feasible dual vector: for every |z_j| <= 1/2,
    # z.d + min(0,z.A) + min(0,z.B) <= min_{u,v in [0,1]} TV(d+uA+vB).
    # Clipping ensures feasibility even if the solver returns tiny violations.
    multipliers = solution.ineqlin.marginals
    dual = np.clip(multipliers[n:]-multipliers[:n], -.5, .5)
    lower = float(np.dot(dual, delta)+min(0., np.dot(dual, direction[:, 0]))
                  +min(0., np.dot(dual, direction[:, 1])))
    lower = max(0., lower-1e-12)  # Numerical guard, much below decision tolerance.
    if lower > witness_tv+1e-8 or witness_tv-lower > 1e-8:
        raise RuntimeError("Mixture-envelope primal and dual certificates disagree")
    maximum = max(.5*float(np.sum(np.abs(a-b))) for a in first for b in second)
    return dict(minimum=witness_tv, maximum=maximum,
                minimum_lower_bound=lower, minimum_dual_vector=dual.tolist(),
                minimum_primal_dual_gap=witness_tv-lower,
                minimizing_segment_positions=positions.tolist(),
                minimizing_initial_shares=witness_first.tolist(),
                minimizing_final_shares=witness_second.tolist())


def quota_calibration(rows, species=("Cr", "Ca", "Mo", "Co")):
    """Read exactly the published 4-species by 5-day preliminary table."""
    expected = {(s, t) for s in species for t in (-4, 0, 1, 2, 3)}
    values = {}
    for row in rows:
        key = (row["Algae"], row["Time standardised to pulse [days]"])
        if key not in expected or key in values:
            raise ValueError("Unexpected or duplicate preliminary species/time")
        n, c, v = _positive([row["N [pmol/cell]"], row["C [pmol/cell]"],
                             row["Cell volume [µm³]"]], "Measured quotas and volume")
        values[key] = dict(nitrogen=float(n/v), carbon=float(c/v),
                           source_row=row["source_row"])
    if set(values) != expected:
        raise ValueError("Incomplete preliminary quota table")
    initial = {resource: [float(np.median([values[s, t][resource] for t in (-4, 0)]))
                          for s in species] for resource in ("nitrogen", "carbon")}
    final = {t: {resource: [values[s, t][resource] for s in species]
                 for resource in ("nitrogen", "carbon")} for t in (1, 2, 3)}
    return dict(species=list(species), units="pmol per cubic micrometre",
                initial=initial, final=final,
                source_rows=[dict(species=s, day=t, **values[s, t])
                             for s in species for t in (-4, 0, 1, 2, 3)])
