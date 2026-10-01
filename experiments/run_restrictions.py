"""Deterministic two-budget closure comparison; no empirical validation claim."""
from __future__ import annotations

import argparse
import csv
import json
import platform
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import scipy

from orthopolity.figures import save_figure
from orthopolity.restrictions import proportional_fair_allocation, neutral_resource_projection

ROOT = Path(__file__).resolve().parents[1]


def _serializable(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {key: _serializable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_serializable(item) for item in value]
    return value


def primary_profile(counts, cost, widths):
    resource = cost * counts
    probability = resource / resource.sum()
    return {
        "class_resource_totals": resource,
        "probability": probability,
        "relative_log_resource_density": probability * widths.sum() / widths,
    }


def study(config):
    edges = np.geomspace(*config["domain"], config["classes"] + 1)
    k = np.sqrt(edges[:-1] * edges[1:])
    widths = np.diff(np.log(edges))
    q = np.vstack([k ** config["primary_cost_exponent"], k ** config["auxiliary_cost_exponent"]])
    primary = config["primary_budget"]
    ratio = q[1] / q[0]
    reference = widths / widths.sum()
    cases = []
    for auxiliary in config["auxiliary_budgets"]:
        pf = proportional_fair_allocation(q, [primary, auxiliary], widths)
        pf["profile"] = primary_profile(pf["counts"], q[0], widths)
        pf["effective_priced_cost"] = pf["multipliers"] @ q
        exponents = np.array([config["primary_cost_exponent"], config["auxiliary_cost_exponent"]])
        pf["effective_cost_local_scaling_exponent"] = ((pf["multipliers"] @ (exponents[:, None] * q)) /
                                                      pf["effective_priced_cost"])
        pf["continuum_linear_density_local_exponent"] = 1 + pf["effective_cost_local_scaling_exponent"]
        difference = exponents[1] - exponents[0]
        pf["priced_cost_crossover_k"] = float((pf["multipliers"][0] / pf["multipliers"][1]) ** (1 / difference)) \
            if np.all(pf["multipliers"] > 0) and difference != 0 else None
        pf["effective_resource_class_allocation_max_error"] = float(np.max(np.abs(
            pf["effective_priced_cost"] * pf["counts"] - widths)))
        compatible = bool(abs(pf["resource_totals"][0] / primary - 1) < 1e-8)
        kl = None
        infeasible = auxiliary < primary * ratio.min()
        if not infeasible:
            kl = neutral_resource_projection(*q, primary, auxiliary, widths)
            kl["profile"] = primary_profile(kl["counts"], q[0], widths)
        cases.append({
            "auxiliary_budget": auxiliary, "proportional_fairness": pf,
            "relative_entropy": kl,
            "same_fixed_primary_total": compatible and not infeasible,
            "relative_entropy_feasible": not infeasible,
            "scope": ("Both closures use the full primary total; shapes can be compared."
                      if compatible and not infeasible else
                      "PF leaves primary budget unused; KL still fixes it exactly."
                      if not infeasible else
                      "KL infeasible with fixed primary total; PF has only upper budgets."),
            "profile_log_rmse_between_closures": float(np.sqrt(np.mean(np.log(
                pf["profile"]["relative_log_resource_density"] /
                kl["profile"]["relative_log_resource_density"]) ** 2)))
                if kl is not None and np.all(kl["probability"] > 0) else None,
        })
    scope_candidates = [case["auxiliary_budget"] for case in cases
                        if case["relative_entropy_feasible"] and not case["same_fixed_primary_total"]]
    requested_scope = config.get("scope_budget")
    scope_budget = (requested_scope if requested_scope in scope_candidates else
                    scope_candidates[0] if scope_candidates else None)
    before_budget, after_budget = config["intervention"]
    before = next(case for case in cases if case["auxiliary_budget"] == before_budget)
    after = next(case for case in cases if case["auxiliary_budget"] == after_budget)
    if not before["same_fixed_primary_total"] or not after["same_fixed_primary_total"]:
        raise ValueError("the intervention must compare two cases with the same fixed primary total")
    pf_before, pf_after = before["proportional_fairness"], after["proportional_fairness"]
    kl_before, kl_after = before["relative_entropy"], after["relative_entropy"]
    pf_ratio = np.log(pf_after["counts"] / pf_before["counts"])
    pf_prediction = np.log((pf_before["multipliers"] @ q) / (pf_after["multipliers"] @ q))
    kl_ratio = np.log(kl_after["probability"] / kl_before["probability"])
    delta_tilt = kl_after["tilt_multiplier"] - kl_before["tilt_multiplier"]
    # The additive constant comes from the two normalized probability models.
    # Neither slope nor multipliers are fitted to observed intervention profiles.
    from scipy.special import logsumexp
    logits_before = np.log(reference) - kl_before["tilt_multiplier"] * ratio
    logits_after = np.log(reference) - kl_after["tilt_multiplier"] * ratio
    intercept = float(logsumexp(logits_before) - logsumexp(logits_after))
    kl_prediction = intercept - delta_tilt * ratio
    return {
        "interpretation": "Constructed optimization predictions, not evidence that natural systems choose either objective.",
        "configuration": config,
        "environment": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
                        "matplotlib": matplotlib.__version__},
        "class_definition": {"edges": edges, "centers": k, "log_widths": widths,
                             "costs": q, "cost_ratio": ratio, "reference_probability": reference},
        "thresholds": {
            "minimum_auxiliary_budget_with_fixed_primary": float(primary * ratio.min()),
            "neutral_auxiliary_total": float(primary * (reference @ ratio)),
            "pf_primary_binding_lower_auxiliary_threshold": float(primary / (reference @ (1 / ratio))),
            "finite_class_costs": "Midpoint costs are exact finite-model inputs, not within-bin integrals.",
        },
        "cases": cases,
        "scope_figure_budget": scope_budget,
        "priced_cost_interpretation": {
            "effective_cost": "q_eff(k)=lambda1*q1(k)+lambda2*q2(k)",
            "local_dimension": "D_eff=sum_a(lambda_a*d_a*q_a)/q_eff for costs q_a=k^d_a",
            "default_power_expression": "D_eff=(2*lambda1*k^2+3*lambda2*k^3)/(lambda1*k^2+lambda2*k^3)"
                if config["primary_cost_exponent"] == 2 and config["auxiliary_cost_exponent"] == 3 else None,
            "crossover": "k=(lambda1/lambda2)^(1/(d2-d1)) when both prices are positive and exponents differ; default d1=2,d2=3 gives k=lambda1/lambda2",
            "density_relation": "For the smooth logarithmic-class closure, linear-size density has local exponent 1+D_eff; this is not a fitted finite-class power law.",
            "allocation_identity": "q_eff_j*N_j=w_j follows from the imposed weighted-log objective, not conservation alone.",
        },
        "intervention": {
            "before_budget": before_budget, "after_budget": after_budget,
            "pf_priced_cost_crossover_before": pf_before["priced_cost_crossover_k"],
            "pf_priced_cost_crossover_after": pf_after["priced_cost_crossover_k"],
            "relative_entropy_delta_tilt": float(delta_tilt), "relative_entropy_intercept": intercept,
            "relative_entropy_log_ratio": kl_ratio,
            "relative_entropy_prescribed_log_ratio": kl_prediction,
            "proportional_fairness_log_ratio": pf_ratio,
            "proportional_fairness_prescribed_log_ratio": pf_prediction,
            "relative_entropy_prediction_max_error": float(np.max(np.abs(kl_ratio - kl_prediction))),
            "proportional_fairness_prediction_max_error": float(np.max(np.abs(pf_ratio - pf_prediction))),
            "cross_closure_log_ratio_rmse": float(np.sqrt(np.mean((kl_ratio - pf_ratio) ** 2))),
        },
    }


def figures(result, output):
    k = np.asarray(result["class_definition"]["centers"])
    cost_ratio = np.asarray(result["class_definition"]["cost_ratio"])
    before, after = result["configuration"]["intervention"]
    colors = {before: "#28669b", after: "#ba5c22"}
    cases = {case["auxiliary_budget"]: case for case in result["cases"]}
    fig, axes = plt.subplots(1, 3, figsize=(13.4, 4.4), layout="constrained")
    for ax, key, title in zip(axes[:2], ["proportional_fairness", "relative_entropy"],
                              ["A  Proportional fairness", "B  Relative entropy"]):
        for budget in (before, after):
            profile = cases[budget][key]["profile"]["relative_log_resource_density"]
            ax.plot(k, profile, lw=2.3, color=colors.get(budget), label=f"Auxiliary budget {budget:g}")
        ax.axhline(1, color="#888888", lw=1, ls="--", label="Neutral primary profile")
        ax.set(xscale="log", yscale="log", xlabel="Class size k", ylabel="Relative primary resource per log width", title=title)
        ax.legend(frameon=False, fontsize=8.5)
    response = result["intervention"]
    axes[2].plot(cost_ratio, response["proportional_fairness_log_ratio"], lw=2.3, color="#28669b", label="PF: ratio of priced costs")
    axes[2].plot(cost_ratio, response["relative_entropy_log_ratio"], lw=2.3, color="#ba5c22", label="KL: straight line in cost ratio")
    axes[2].set(xlabel=r"Auxiliary / primary cost, $q_2/q_1$", ylabel="Log resource ratio: after / before", title="C  Budget-predicted intervention")
    axes[2].legend(frameon=False, fontsize=8.5)
    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(alpha=.18)
    fig.suptitle("Two imposed closures, same active budgets — no empirical data", fontsize=11)
    for suffix in ("png", "svg"):
        save_figure(fig, output / f"profiles.{suffix}", dpi=190)
    plt.close(fig)

    scope_budget = result["scope_figure_budget"]
    if scope_budget is None:
        # A rerun with another configuration must not leave a stale scope image.
        for suffix in ("png", "svg"):
            (output / f"scope.{suffix}").unlink(missing_ok=True)
        return
    fig, axes = plt.subplots(1, 2, figsize=(9.8, 4.2), layout="constrained")
    budgets = np.array(sorted(cases))
    axes[0].plot(budgets, [cases[b]["proportional_fairness"]["resource_totals"][0] for b in budgets],
                 "o-", color="#28669b", label="PF: primary use")
    feasible = np.array([b for b in budgets if cases[b]["relative_entropy_feasible"]])
    axes[0].plot(feasible, np.ones_like(feasible) * result["configuration"]["primary_budget"],
                 "s--", color="#ba5c22", label="KL: primary fixed")
    axes[0].axvline(result["thresholds"]["minimum_auxiliary_budget_with_fixed_primary"],
                    color="#777777", ls=":", label="KL minimum feasible budget")
    axes[0].set(xscale="log", xlabel="Auxiliary budget", ylabel="Primary resource used", title="A  Equality versus upper bounds")
    axes[0].legend(frameon=False, fontsize=8)
    for model, label, style in [("proportional_fairness", f"PF at auxiliary budget {scope_budget:g}", "-"),
                                 ("relative_entropy", f"KL at auxiliary budget {scope_budget:g}", "--")]:
        axes[1].plot(k, cases[scope_budget][model]["profile"]["relative_log_resource_density"], style, lw=2, label=label)
    axes[1].set(xscale="log", yscale="log", xlabel="Class size k", ylabel="Profile normalized by actual primary use", title="B  Different constraints at severe restriction")
    axes[1].legend(frameon=False, fontsize=8)
    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(alpha=.18)
    fig.suptitle("Scope check: these severe-restriction allocations use different primary totals", fontsize=10)
    for suffix in ("png", "svg"):
        save_figure(fig, output / f"scope.{suffix}", dpi=190)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/restriction_study_2026-10-01.json")
    parser.add_argument("--output", type=Path, default=ROOT / "results/restrictions")
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    result = study(config)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "study.json").write_text(json.dumps(_serializable(result), indent=2, allow_nan=False) + "\n")
    with (args.output / "profiles.csv").open("w", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["auxiliary_budget", "closure", "center", "log_width", "primary_cost", "auxiliary_cost",
                         "count", "primary_class_resource", "relative_log_resource_density", "primary_total_used"])
        k = result["class_definition"]["centers"]
        widths = result["class_definition"]["log_widths"]
        q = result["class_definition"]["costs"]
        for case in result["cases"]:
            for closure in ("proportional_fairness", "relative_entropy"):
                solved = case[closure]
                if solved is None:
                    continue
                for j in range(len(k)):
                    writer.writerow([case["auxiliary_budget"], closure, k[j], widths[j], q[0, j], q[1, j],
                                     solved["counts"][j], solved["profile"]["class_resource_totals"][j],
                                     solved["profile"]["relative_log_resource_density"][j], solved["resource_totals"][0]])
    figures(result, args.output)
    print(json.dumps({"thresholds": result["thresholds"],
                      "intervention_cross_closure_log_ratio_rmse": result["intervention"]["cross_closure_log_ratio_rmse"],
                      "maximum_pf_kkt_residual": max(case["proportional_fairness"]["kkt_residual"] for case in result["cases"]),
                      "outputs": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()
