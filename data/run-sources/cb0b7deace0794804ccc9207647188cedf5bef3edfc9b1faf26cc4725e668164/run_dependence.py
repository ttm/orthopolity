"""Known-model forward benchmark: fixed marginals, varied dependence/capacity.

Capacity training and sampled-size validation use independent seed streams.
Families, marginal laws, and Student degrees of freedom are known. No size
exponent is fitted. Simulated validation verifies construction, not Nature.
"""
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
from scipy.stats import kendalltau

from orthopolity.figures import save_figure
from orthopolity.dependence import (
    asymptotic_dimension, capacity_samples, estimate_dependence_parameter,
    finite_dimension, forward_resource_profile, joint_survival,
    student_bivariate_survival_check, student_tail_coefficient,
)
from orthopolity.spectrum import resource_spectrum

ROOT = Path(__file__).resolve().parents[1]


def run(config):
    rows = []
    for index, scenario in enumerate(config["scenarios"]):
        family, m, parameter = scenario["family"], scenario["resources"], scenario["parameter"]
        df, cap = scenario.get("df", 4), scenario.get("capacity_cap")
        rng = lambda stream: np.random.default_rng(np.random.SeedSequence([config["seed"], index, stream]))
        # Fit before a potential cap intervention, from independent capacity
        # measurements. No validation-size information enters this fit.
        training = capacity_samples(config["capacity_training_samples"], m, family, parameter, rng(0), df=df)
        trained = estimate_dependence_parameter(training, family)
        observed_tau = float(kendalltau(training[:, 0], training[:, 1]).statistic)
        edges = np.geomspace(*scenario["domain"], config["bins"]+1)
        widths, centers = np.diff(np.log(edges)), np.sqrt(edges[:-1]*edges[1:])
        arguments = dict(resources=m, family=family, df=df, cap=cap, cost_exponent=config["cost_exponent"])
        expected = forward_resource_profile(edges, parameter=parameter, **arguments)
        trained_prediction = forward_resource_profile(edges, parameter=trained, **arguments)
        profiles, survival, atoms = [], [], []
        survival_grid = np.geomspace(edges[0], edges[-1], 17)
        for rep in range(config["replicates"]):
            capacity = capacity_samples(config["validation_samples"], m, family, parameter, rng(10+rep), df=df, cap=cap)
            sizes = capacity.min(axis=1)
            profiles.append(resource_spectrum(sizes, sizes**config["cost_exponent"], edges)["occupancy"])
            survival.append(np.mean(sizes[:, None] >= survival_grid[None, :], axis=0))
            atoms.append(float(np.mean(sizes == cap)) if cap is not None else 0)
        raw = np.asarray(profiles)
        mean = raw.mean(axis=0)
        normalizer = np.dot(mean, widths)/widths.sum()
        phi = mean/normalizer
        tail_x = np.asarray(config["tail_thresholds"])
        tail_p = joint_survival(tail_x, m, family, parameter, df=df)
        dimension = finite_dimension(tail_x, m, family, parameter, df=df)
        reference_p = joint_survival(survival_grid, m, family, parameter, df=df, cap=cap)
        training_p = joint_survival(survival_grid, m, family, trained, df=df, cap=cap)
        observed_p = np.mean(survival, axis=0)
        numerical_check = None
        if family == "student":
            check_x = np.array([2, 10, 1000.])
            check_low = joint_survival(check_x, m, family, parameter, df=df, order=64)
            check_high = joint_survival(check_x, m, family, parameter, df=df, order=128)
            numerical_check = dict(check_thresholds=check_x.tolist(), maximum_relative_order_difference=float(np.max(abs(check_low/check_high-1))),
                                   resource_profile_relative_order_difference=float(np.max(abs(expected["phi"]/forward_resource_profile(edges, parameter=parameter, normal_order=128, **arguments)["phi"]-1))))
            if m == 2:
                independent = np.array([student_bivariate_survival_check(x, parameter, df) for x in check_x])
                numerical_check["maximum_relative_conditional_integral_difference"] = float(np.max(abs(check_high/independent-1)))
        row = dict(scenario=scenario, status="known-model construction with independent capacity training and output validation",
            training=dict(samples=config["capacity_training_samples"], fitted_parameter=trained, observed_pair_kendall_tau=observed_tau,
                          observed_marginal_survival_at_2=np.mean(training >= 2, axis=0).tolist(),
                          assumption="family, unit-Pareto margins and Student df known; pre-cap training"),
            resource=dict(cost_exponent=config["cost_exponent"], definition="q(K)=K**cost_exponent, fixed across scenarios"),
            asymptotic=dict(uncapped_joint_survival_dimension=asymptotic_dimension(m, family, parameter),
                           applies_to_capped_intervention=False if cap is not None else True,
                           predicted_pair_kendall_tau=float(2/np.pi*np.arcsin(parameter)) if family in ("gaussian", "student") else None,
                           student_bivariate_tail_coefficient=student_tail_coefficient(parameter, df) if family == "student" and m == 2 else None),
            uncapped_tail_reference=dict(thresholds=tail_x.tolist(), survival=tail_p.tolist(), finite_joint_feasibility_dimension=dimension.tolist(),
                                        status="numerical or exact predictions; deep tails are not validated by finite sampled counts"),
            profile=dict(edges=edges.tolist(), center=centers.tolist(), pooled_phi=phi.tolist(), known_model_forward_phi=expected["phi"].tolist(),
                         capacity_training_forward_phi=trained_prediction["phi"].tolist(),
                         run_quantile_10=np.quantile(raw/normalizer, .1, axis=0).tolist(),run_quantile_90=np.quantile(raw/normalizer, .9, axis=0).tolist()),
            prediction_errors=dict(log_profile_rmse_known=float(np.sqrt(np.mean(np.log(phi/expected["phi"])**2))),
                                   log_profile_rmse_capacity_training=float(np.sqrt(np.mean(np.log(phi/trained_prediction["phi"])**2))),
                                   maximum_absolute_survival_error_known=float(np.max(abs(observed_p-reference_p))),
                                   maximum_absolute_survival_error_capacity_training=float(np.max(abs(observed_p-training_p)))),
            survival=dict(thresholds=survival_grid.tolist(),observed=observed_p.tolist(),known_model=reference_p.tolist(),capacity_training=training_p.tolist()),
            cap_atom=dict(observed=float(np.mean(atoms)),predicted=float(joint_survival(cap,m,family,parameter,df=df)) if cap is not None else None),
            empty_resource_bin_occurrences=int(np.sum(raw == 0)),numerical_quadrature_check=numerical_check)
        rows.append(row)
        print(json.dumps(dict(scenario=scenario["id"],parameter_training=trained,profile_rmse=row["prediction_errors"]["log_profile_rmse_known"],finite_dimension_at_10=float(dimension[1]))), flush=True)
    return rows


def plot(rows, out):
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "svg.fonttype": "none"})
    fig, axes = plt.subplots(2, 2, figsize=(11, 8), layout="constrained")
    groups = [([r for r in rows if r["scenario"]["resources"]==2 and "capacity_cap" not in r["scenario"]], "A  Two fixed Pareto marginals"),
              ([r for r in rows if r["scenario"]["resources"]==4], "B  Four fixed Pareto marginals"),
              ([r for r in rows if "capacity_cap" in r["scenario"]], "C  Capacity ceiling: atom retained")]
    for ax, (group, title) in zip(axes.flat, groups):
        for row in group:
            pp, ss = row["profile"], row["scenario"]
            label=f"{ss['family']} ({ss['parameter']:g})"
            line,=ax.plot(pp["center"],pp["pooled_phi"],"o-",ms=3,label=label)
            ax.plot(pp["center"],pp["known_model_forward_phi"],"--",color=line.get_color())
            ax.fill_between(pp["center"],pp["run_quantile_10"],pp["run_quantile_90"],color=line.get_color(),alpha=.12)
        ax.axhline(1,color="gray",lw=.8,ls=":")
        ax.set(xscale="log",yscale="log",xlabel="Feasible size K",ylabel="Fixed resource per log size / mean",title=title)
        ax.legend(fontsize=7,frameon=False)
    ax=axes.flat[-1]
    for row in rows:
        ss=row["scenario"]
        if ss["resources"]!=2 or ss["family"] not in ("gaussian","student") or "capacity_cap" in ss: continue
        xx=np.geomspace(2,1e6,70)
        yy=finite_dimension(xx,2,ss["family"],ss["parameter"],df=ss.get("df",4))
        line,=ax.plot(xx,yy,label=f"{ss['family']} ({ss['parameter']:g})")
        ax.axhline(row["asymptotic"]["uncapped_joint_survival_dimension"],ls=":",color=line.get_color(),lw=.9)
    ax.set(xscale="log",xlabel="Threshold (forward calculations)",ylabel="Joint-survival local elasticity",title="D  Finite range and asymptotic dimension")
    ax.legend(fontsize=7,frameon=False)
    for ax in axes.flat:
        ax.spines[["top","right"]].set_visible(False); ax.grid(alpha=.2)
    fig.suptitle("Fixed marginal resources, different joint tails\nDashed: forward profile; bands: run quantiles, not confidence bands",fontsize=12)
    for ext in ("png","svg"): save_figure(fig, out/f"dependence-study.{ext}", dpi=155)
    plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config",type=Path,default=ROOT/"configs/dependence_study_2026-10-01.json")
    parser.add_argument("--output",type=Path,default=ROOT/"results/dependence")
    args=parser.parse_args()
    config=json.loads(args.config.read_text())
    rows=run(config)
    out=args.output;out.mkdir(parents=True,exist_ok=True)
    report=dict(kind="exploratory forward benchmark of known copula constructions; not natural-system evidence",config=config,
                versions=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,matplotlib=matplotlib.__version__),
                profile_target="mean raw resource density over equal validation exposures; normalized once in the declared bounded domain",
                uncertainty="six independent validation runs; run quantiles are not confidence bands; training uncertainty is not propagated",
                predictions="no abundance exponent is fitted; deterministic exact/numerical forward profiles, with independently fitted capacity parameters as a second comparison",
                limitations=["family and marginal laws known in the training step", "realized size equals the bottleneck by construction", "uncapped Pareto capacity means are infinite", "capping introduces a genuine endpoint atom and eliminates an asymptotic tail"],scenarios=rows)
    (out/"dependence-study.json").write_text(json.dumps(report,indent=2,allow_nan=False)+"\n")
    with (out/"profiles.csv").open("w",newline="") as handle:
        writer=csv.writer(handle, lineterminator="\n");writer.writerow(["scenario_id","family","resources","parameter","cap","lower","upper","pooled_phi","known_model_phi","capacity_training_phi"])
        for row in rows:
            pp,ss=row["profile"],row["scenario"]
            for i,(lo,hi) in enumerate(zip(pp["edges"][:-1],pp["edges"][1:])):
                writer.writerow([ss["id"],ss["family"],ss["resources"],ss["parameter"],ss.get("capacity_cap",""),lo,hi,pp["pooled_phi"][i],pp["known_model_forward_phi"][i],pp["capacity_training_forward_phi"][i]])
    plot(rows,out)
    print(f"Saved {len(rows)} forward scenarios to {out}")


if __name__=="__main__":main()
