"""Budget-determined allocation closures, not a claim about natural objectives.

Counts are continuous allocations or expectations. Costs and class weights are
fixed inputs, and multipliers are solved from budgets rather than profiles.
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import brentq, minimize
from scipy.special import logsumexp


def _positive_vector(values, name):
    result = np.asarray(values, dtype=float)
    if result.ndim != 1 or not result.size or np.any(~np.isfinite(result)) or np.any(result <= 0):
        raise ValueError(f"{name} must be a nonempty finite strictly positive vector")
    return result


def proportional_fair_allocation(costs, budgets, weights=None, *, tolerance=1e-9):
    """Maximize sum_j w_j log(N_j) with Q @ N <= B and N_j > 0.

    Strictly positive finite costs/budgets are required. One- and two-resource
    cases use exact active-set formulas and a bracketed scalar root; more
    resources use the convex dual. Redundant budgets can make multipliers
    nonunique even though strict concavity makes the count solution unique.
    """
    q = np.asarray(costs, dtype=float)
    if q.ndim == 1:
        q = q[None, :]
    if q.ndim != 2 or not q.size or np.any(~np.isfinite(q)) or np.any(q <= 0):
        raise ValueError("costs must be a nonempty finite strictly positive matrix")
    b = _positive_vector(budgets, "budgets")
    w = np.ones(q.shape[1]) if weights is None else _positive_vector(weights, "weights")
    if len(b) != q.shape[0] or len(w) != q.shape[1]:
        raise ValueError("cost, budget, and weight shapes disagree")
    if not np.isfinite(tolerance) or tolerance <= 0:
        raise ValueError("tolerance must be finite and positive")
    c = q / b[:, None]
    total_weight = float(w.sum())
    scaled_multiplier = None
    method = "single-active-budget analytic solution"
    for resource in range(len(b)):
        candidate = w / (total_weight * c[resource])
        if np.all(c @ candidate <= 1 + tolerance):
            scaled_multiplier = np.zeros(len(b))
            scaled_multiplier[resource] = total_weight
            break
    if scaled_multiplier is None and len(b) == 2:
        def difference(fraction):
            denominator = total_weight * (fraction * c[0] + (1 - fraction) * c[1])
            return float((c[0] - c[1]) @ (w / denominator))
        fraction = brentq(difference, 0, 1, xtol=1e-14, rtol=1e-14)
        scaled_multiplier = total_weight * np.array([fraction, 1 - fraction])
        method = "two-active-budget bracketed dual solution"
    elif scaled_multiplier is None:
        def dual_and_gradient(multiplier):
            denominator = multiplier @ c
            if np.any(denominator <= 0):
                return np.inf, np.full_like(multiplier, -1e100)
            return (float(multiplier.sum() - w @ np.log(denominator)),
                    1 - c @ (w / denominator))
        solved = minimize(dual_and_gradient, np.full(len(b), total_weight / len(b)),
                          jac=True, bounds=[(0, None)] * len(b), method="L-BFGS-B",
                          options={"ftol": 1e-15, "gtol": tolerance / 10, "maxiter": 10000,
                                   "maxls": 100})
        scaled_multiplier = solved.x
        method = "convex dual L-BFGS-B"
    multiplier = scaled_multiplier / b
    denominator = multiplier @ q
    counts = w / denominator
    totals = q @ counts
    normalized_slack = 1 - totals / b
    complementarity = scaled_multiplier * normalized_slack
    residual = max(float(np.maximum(-normalized_slack, 0).max()),
                   float(np.abs(complementarity).max() / total_weight))
    if residual > max(100 * tolerance, 1e-7):
        raise RuntimeError(f"allocation failed the feasibility/KKT check: {residual:g}")
    return {
        "counts": counts, "multipliers": multiplier, "resource_totals": totals,
        "budget_slack": b - totals, "normalized_budget_slack": normalized_slack,
        "active_constraints": scaled_multiplier > tolerance * total_weight,
        "objective": float(w @ np.log(counts)), "kkt_residual": residual,
        "duality_gap": float(multiplier @ (b - totals)), "method": method,
    }


def neutral_resource_projection(primary_cost, auxiliary_cost, primary_total,
                                auxiliary_budget, weights=None, *, tolerance=1e-10):
    """Minimize KL(P || P0) with sum(P)=1 and E_P[q2/q1] <= B2/R1.

    P0 is normalized class weight, and N_j=R1 P_j/q1_j. Primary resource is
    fixed exactly. At the minimum feasible auxiliary budget, the solution is
    supported only on minimum-ratio classes and has no finite tilt multiplier.
    An infeasible budget raises ValueError instead of returning an allocation.
    """
    q1 = _positive_vector(primary_cost, "primary_cost")
    q2 = _positive_vector(auxiliary_cost, "auxiliary_cost")
    w = np.ones(len(q1)) if weights is None else _positive_vector(weights, "weights")
    if len(q1) != len(q2) or len(q1) != len(w):
        raise ValueError("cost and weight shapes disagree")
    if not np.isfinite(primary_total) or primary_total <= 0:
        raise ValueError("primary_total must be finite and positive")
    if not np.isfinite(auxiliary_budget) or auxiliary_budget < 0:
        raise ValueError("auxiliary_budget must be finite and nonnegative")
    if not np.isfinite(tolerance) or tolerance <= 0:
        raise ValueError("tolerance must be finite and positive")
    ratio = q2 / q1
    target = auxiliary_budget / primary_total
    minimum = float(ratio.min())
    # Feasibility is exact for the declared finite costs; do not silently change
    # an infeasible requested budget within a numerical tolerance.
    if target < minimum:
        raise ValueError(f"auxiliary budget is infeasible with fixed primary total; minimum={primary_total * minimum:g}")
    reference = w / w.sum()
    log_reference = np.log(reference)
    neutral_mean = float(reference @ ratio)
    if target >= neutral_mean:
        probability = reference.copy()
        tilt, status = 0.0, "neutral; auxiliary bound inactive or at neutral threshold"
    elif target == minimum:
        selected = ratio == minimum
        probability = np.where(selected, reference, 0)
        probability /= probability.sum()
        tilt, status = None, "boundary; no finite tilt multiplier"
    else:
        def tilted(value):
            logits = log_reference - value * (ratio - minimum)
            return np.exp(logits - logsumexp(logits))
        upper = 1.0
        while float(tilted(upper) @ ratio) > target:
            upper *= 2
            if not np.isfinite(upper):
                raise RuntimeError("could not bracket the auxiliary-budget multiplier")
        tilt = brentq(lambda value: float(tilted(value) @ ratio) - target,
                      0, upper, xtol=1e-14, rtol=1e-14)
        probability = tilted(tilt)
        status = "active auxiliary bound; interior exponential tilt"
    counts = primary_total * probability / q1
    actual_auxiliary = float(primary_total * (probability @ ratio))
    mask = probability > 0
    relative_entropy = float(probability[mask] @
                             (np.log(probability[mask]) - log_reference[mask]))
    error = max(abs(float(probability.sum()) - 1),
                max(actual_auxiliary - auxiliary_budget, 0) / max(primary_total, auxiliary_budget))
    if error > 100 * tolerance:
        raise RuntimeError(f"projection failed feasibility check: {error:g}")
    return {
        "probability": probability, "reference_probability": reference, "counts": counts,
        "tilt_multiplier": tilt, "resource_totals": np.array([primary_total, actual_auxiliary]),
        "auxiliary_slack": auxiliary_budget - actual_auxiliary,
        "minimum_auxiliary_budget": primary_total * minimum,
        "neutral_auxiliary_total": primary_total * neutral_mean,
        "relative_entropy": relative_entropy, "feasibility_residual": error, "status": status,
    }
