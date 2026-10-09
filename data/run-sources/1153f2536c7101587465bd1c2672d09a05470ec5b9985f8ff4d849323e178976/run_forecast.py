"""Capacity-only family selection, bootstrap coverage and misspecification.

Independent stages: capacity fitting, capacity selection, realized output.
Truth is available only for simulation scoring and is never used for selection.
All numerical coverage results target population laws rather than noisy output
realizations. Bootstrap bands are approximate and selection can affect coverage.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import time
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import scipy
from scipy.stats import binomtest

from orthopolity.dependence import capacity_samples, joint_survival
from orthopolity.figures import save_figure
from orthopolity.forecast import (
    FAMILIES, bounded_bootstrap_cdf_distance, bounded_population_cdf_distance,
    bounded_resource_moments, empirical_survival, fit_capacity_candidates,
    lookup_prediction, resource_prediction_from_survival, select_capacity_candidate,
    sup_bootstrap_radius,
)

ROOT = Path(__file__).resolve().parents[1]


def build_bank(config):
    edges = np.geomspace(*config["domain"], config["bins"]+1)
    xx = np.unique(np.r_[np.geomspace(*config["domain"], config["prediction_survival_grid_size"]), config["selection_thresholds"]])
    bank = dict(edges=edges.tolist(), log_widths=np.diff(np.log(edges)).tolist(), survival_grid=xx.tolist())
    audit = {}
    for family in FAMILIES:
        parameters = [0.] if family == "independent" else config["parameter_grid"]
        survival, resource = [], []
        for parameter in parameters:
            fun = lambda values: joint_survival(values, 2, family, parameter, df=4)
            survival.append(fun(xx).tolist())
            resource.append(resource_prediction_from_survival(edges, fun, order=12)["means"].tolist())
        bank[family] = dict(parameter_grid=parameters, survival=survival, resource_means=resource)
        if family != "independent":
            parameter = config["interpolation_audit_parameter"]
            estimated = lookup_prediction(bank, family, parameter)
            fun = lambda values: joint_survival(values, 2, family, parameter, df=4)
            expected = resource_prediction_from_survival(edges, fun, order=24)
            midpoints = np.sqrt(xx[:-1]*xx[1:])
            predicted_midpoints = np.interp(np.log(midpoints), np.log(xx), estimated["survival"])
            error = float(np.max(abs(predicted_midpoints-fun(midpoints))))
            audit[family] = dict(maximum_midpoint_absolute_survival_error=error,
                                maximum_absolute_profile_error=float(np.max(abs(estimated["phi"]-expected["phi"]))))
            if error > config["interpolation_audit_absolute_tolerance"]:
                raise ArithmeticError("prediction interpolation failed the frozen audit tolerance")
        print(f"Built and audited {family} forward grid", flush=True)
    return bank, audit


def log_rmse(observed, prediction):
    observed, prediction = np.asarray(observed), np.asarray(prediction)
    return float(np.sqrt(np.mean(np.log(observed/prediction)**2))) if np.all(observed > 0) and np.all(prediction > 0) else None


def coverage_summary(records, key):
    successes = sum(bool(row[key]) for row in records)
    n = len(records)
    interval = binomtest(successes, n).proportion_ci(confidence_level=.95, method="exact")
    return dict(covered=successes, repetitions=n, fraction=successes/n,
                binomial_95_interval=[float(interval.low),float(interval.high)])


def study(config, bank):
    edges = np.asarray(bank["edges"])
    grid = np.asarray(bank["survival_grid"])
    thresholds = np.asarray(config["selection_thresholds"])
    threshold_index = np.searchsorted(grid, thresholds)
    truth_grid = np.geomspace(*config["domain"], config["oracle_cdf_grid_size"])
    rows=[]
    for case_index, scenario in enumerate(config["scenarios"]):
        started=time.perf_counter()
        truth_capacity = lambda values: joint_survival(values, 2, scenario["family"], scenario["parameter"], df=scenario["df"])
        truth_output = lambda values: truth_capacity(values)/np.asarray(values) if scenario.get("hidden_independent_resource",False) else truth_capacity(values)
        capacity_curve, output_curve = truth_capacity(truth_grid), truth_output(truth_grid)
        capacity_profile = resource_prediction_from_survival(edges, truth_capacity)["phi"]
        output_profile = resource_prediction_from_survival(edges, truth_output)["phi"]
        interpolated_capacity = lambda values: np.interp(np.log(values), np.log(truth_grid), capacity_curve)
        interpolated_output = lambda values: np.interp(np.log(values), np.log(truth_grid), output_curve)
        # Audit the fine oracle interpolant at every seventeenth cell midpoint.
        audit_x=np.sqrt(truth_grid[:-1:17]*truth_grid[1::17])
        oracle_error=float(np.max(abs(interpolated_output(audit_x)-truth_output(audit_x))))
        repetitions=[]
        for rep in range(config["outer_replicates"]):
            rng=lambda stream:np.random.default_rng(np.random.SeedSequence([config["seed"],case_index,rep,stream]))
            fitting=capacity_samples(config["training_capacity_samples"],2,scenario["family"],scenario["parameter"],rng(0),df=scenario["df"])
            selection=capacity_samples(config["selection_capacity_samples"],2,scenario["family"],scenario["parameter"],rng(1),df=scenario["df"])
            realized=capacity_samples(config["realized_output_samples"],2,scenario["family"],scenario["parameter"],rng(2),df=scenario["df"]).min(axis=1)
            if scenario.get("hidden_independent_resource",False):
                hidden=np.exp(rng(3).exponential(size=len(realized)))
                realized=np.minimum(realized,hidden)
            parameters=fit_capacity_candidates(fitting)
            predictions={family:lookup_prediction(bank,family,parameters[family]) for family in FAMILIES}
            chosen,scores=select_capacity_candidate({f:predictions[f]["survival"][threshold_index] for f in FAMILIES},selection.min(axis=1),thresholds)
            prediction=predictions[chosen]
            training_min=fitting.min(axis=1)
            np_profile=bounded_resource_moments(training_min,edges)["phi"]
            np_curve=empirical_survival(training_min,grid)
            actual=bounded_resource_moments(realized,edges)["phi"]
            actual_curve=empirical_survival(realized,grid)
            ntrain=len(fitting)
            sort_index=np.argsort(training_min)
            sorted_min=training_min[sort_index]
            bootstrap_rng=rng(4)
            selected_profiles,selected_curves,np_profiles,np_cdf_distances=[],[],[],[]
            bootstrap_selection=Counter()
            for draw in range(config["bootstrap_replicates"]):
                indices=bootstrap_rng.integers(ntrain,size=ntrain)
                selection_indices=bootstrap_rng.integers(len(selection),size=len(selection))
                fitted=fit_capacity_candidates(fitting[indices])
                forecast={family:lookup_prediction(bank,family,fitted[family]) for family in FAMILIES}
                selected,_=select_capacity_candidate({f:forecast[f]["survival"][threshold_index] for f in FAMILIES},selection[selection_indices].min(axis=1),thresholds)
                bootstrap_selection[selected]+=1
                selected_profiles.append(forecast[selected]["phi"])
                selected_curves.append(forecast[selected]["survival"])
                np_profiles.append(bounded_resource_moments(training_min[indices],edges)["phi"])
                frequencies=np.bincount(indices,minlength=ntrain)[sort_index]
                np_cdf_distances.append(bounded_bootstrap_cdf_distance(sorted_min,frequencies,edges[-1]))
            model_profile_radius=sup_bootstrap_radius(prediction["phi"],selected_profiles,config["confidence"])
            model_curve_radius=sup_bootstrap_radius(prediction["survival"],selected_curves,config["confidence"])
            nonparam_profile_radius=sup_bootstrap_radius(np_profile,np_profiles,config["confidence"])
            nonparam_cdf_radius=float(np.quantile(np_cdf_distances,config["confidence"],method="higher"))
            model_on_truth_grid=np.interp(np.log(truth_grid),np.log(grid),prediction["survival"])
            coverage=dict(
                selected_profile_capacity=bool(np.max(abs(prediction["phi"]-capacity_profile))<=model_profile_radius),
                selected_profile_output=bool(np.max(abs(prediction["phi"]-output_profile))<=model_profile_radius),
                selected_cdf_capacity=bool(np.max(abs(model_on_truth_grid-capacity_curve))<=model_curve_radius),
                selected_cdf_output=bool(np.max(abs(model_on_truth_grid-output_curve))<=model_curve_radius),
                nonparametric_profile_capacity=bool(np.max(abs(np_profile-capacity_profile))<=nonparam_profile_radius),
                nonparametric_profile_output=bool(np.max(abs(np_profile-output_profile))<=nonparam_profile_radius),
                nonparametric_cdf_capacity=bool(bounded_population_cdf_distance(training_min,interpolated_capacity,edges[-1])<=nonparam_cdf_radius),
                nonparametric_cdf_output=bool(bounded_population_cdf_distance(training_min,interpolated_output,edges[-1])<=nonparam_cdf_radius))
            repetitions.append(dict(replicate=rep,parameters=parameters,chosen_family=chosen,capacity_selection_scores=scores,
                bootstrap_family_counts=dict(bootstrap_selection),coverage=coverage,
                band_radii=dict(selected_profile=model_profile_radius,selected_bounded_cdf=model_curve_radius,
                                nonparametric_profile=nonparam_profile_radius,nonparametric_bounded_cdf=nonparam_cdf_radius),
                forecast_errors=dict(selected_profile_log_rmse=log_rmse(actual,prediction["phi"]),nonparametric_profile_log_rmse=log_rmse(actual,np_profile),
                    selected_survival_rmse=float(np.sqrt(np.mean((actual_curve-prediction["survival"])**2))),
                    nonparametric_survival_rmse=float(np.sqrt(np.mean((actual_curve-np_curve)**2)))),
                profiles=dict(output=actual.tolist(),selected=prediction["phi"].tolist(),nonparametric=np_profile.tolist()),
                curves=dict(selected=prediction["survival"].tolist(),nonparametric=np_curve.tolist(),output=actual_curve.tolist()),
                empty_training_resource_bins=int(np.sum(np_profile==0)),empty_output_resource_bins=int(np.sum(actual==0))))
        summaries={key:coverage_summary([rep["coverage"] for rep in repetitions],key) for key in repetitions[0]["coverage"]}
        error_summary={key:float(np.mean([r["forecast_errors"][key] for r in repetitions if r["forecast_errors"][key] is not None])) for key in repetitions[0]["forecast_errors"]}
        row=dict(scenario=scenario,selected_family_counts=dict(Counter(r["chosen_family"] for r in repetitions)),
                 mean_forecast_errors=error_summary,coverage=summaries,
                 truth=dict(fine_grid=truth_grid.tolist(),capacity_survival=capacity_curve.tolist(),output_survival=output_curve.tolist(),
                            capacity_profile=capacity_profile.tolist(),output_profile=output_profile.tolist(),maximum_audited_oracle_interpolation_error=oracle_error),
                 repetitions=repetitions)
        rows.append(row)
        print(json.dumps(dict(scenario=scenario["id"],seconds=round(time.perf_counter()-started,2),selection=row["selected_family_counts"],
                              errors=error_summary,profile_coverage=summaries["selected_profile_output"]["fraction"],np_cdf_coverage=summaries["nonparametric_cdf_output"]["fraction"])),flush=True)
    return rows


def plots(rows,bank,config,out):
    plt.rcParams.update({"font.family":"DejaVu Sans","font.size":9,"svg.fonttype":"none"})
    fig,axes=plt.subplots(2,3,figsize=(14,8),layout="constrained")
    centers=np.sqrt(np.asarray(bank["edges"][:-1])*np.asarray(bank["edges"][1:]))
    for ax,row in zip(axes.flat,rows):
        selected=np.mean([r["profiles"]["selected"] for r in row["repetitions"]],axis=0)
        nonparam=np.mean([r["profiles"]["nonparametric"] for r in row["repetitions"]],axis=0)
        ax.plot(centers,row["truth"]["output_profile"],"k-",lw=2,label="True output population")
        ax.plot(centers,selected,"o--",ms=4,label="Capacity-selected forecast")
        ax.plot(centers,nonparam,"s:",ms=4,label="Nonparametric capacity forecast")
        ax.set(xscale="log",yscale="log",xlabel="Size K",ylabel="Resource per log size / mean",title=row["scenario"]["id"].replace("_"," "))
        ax.legend(fontsize=7,frameon=False)
    ax=axes.flat[-1]
    positions=np.arange(len(rows));width=.19
    for offset,key,label in [(-1.5,"selected_profile_output","Selected profile"),(-.5,"selected_cdf_output","Selected bounded CDF"),(.5,"nonparametric_profile_output","Nonparametric profile"),(1.5,"nonparametric_cdf_output","Nonparametric bounded CDF")]:
        ax.bar(positions+offset*width,[r["coverage"][key]["fraction"] for r in rows],width,label=label)
    ax.axhline(config["confidence"],ls="--",color="gray",lw=1)
    ax.set(ylim=(0,1.06),ylabel="Population-target coverage",title=f"Training bands: {config['outer_replicates']} repetitions per case")
    ax.set_xticks(positions,["Gaussian","Student4","Student10","Shock","Hidden"],rotation=20)
    ax.legend(fontsize=7,frameon=True,framealpha=.95,loc="lower left")
    for ax in axes.flat:
        ax.spines[["top","right"]].set_visible(False);ax.grid(alpha=.15,axis="y")
    fig.suptitle("Capacity-only forecasts, uncertainty and model failures\nNo realized output is used for fitting or selection; numerical simulation, not empirical evidence",fontsize=12)
    for ext in ("png","svg"):save_figure(fig,out/f"forecast-study.{ext}",dpi=155)
    plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config",type=Path,default=ROOT/"configs/forecast_study_2026-10-01.json")
    parser.add_argument("--output",type=Path,default=ROOT/"results/forecast")
    args=parser.parse_args()
    specification=args.config.read_bytes();config=json.loads(specification)
    bank,audit=build_bank(config)
    rows=study(config,bank)
    out=args.output;out.mkdir(parents=True,exist_ok=True)
    report=dict(kind="exploratory known-marginal forecasting and bootstrap calibration; no natural observations",config=config,
        config_sha256=hashlib.sha256(specification).hexdigest(),versions=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,matplotlib=matplotlib.__version__),
        stage_separation="capacity fitting, held-out capacity selection, independent realized outputs; bootstrap resamples both capacity stages",
        uncertainty="separate simultaneous sup bands for bounded profile and bounded continuous CDF; approximate bootstrap, empirical population-target coverage, no claimed joint 95% band",
        numerical_prediction_bank=bank,interpolation_audit=audit,scenarios=rows,
        limitations=["unit-Pareto marginal law remains known", "selection concerns only declared exceedance events, not the entire copula",
                     "Student-10 generating family absent from candidates", "hidden third requirement is absent from measured capacity predictors",
                     "bottleneck realization imposed by construction", "24 outer repetitions give wide coverage uncertainty", "no prediction of an unbounded finite resource expectation"])
    (out/"forecast-study.json").write_text(json.dumps(report,indent=2,allow_nan=False)+"\n")
    with (out/"profiles.csv").open("w",newline="") as handle:
        writer=csv.writer(handle,lineterminator="\n");writer.writerow(["scenario_id","replicate","chosen_family","center","selected_phi","nonparametric_phi","output_phi","population_output_phi"])
        centers=np.sqrt(np.asarray(bank["edges"][:-1])*np.asarray(bank["edges"][1:]))
        for row in rows:
            for rep in row["repetitions"]:
                for j,center in enumerate(centers):writer.writerow([row["scenario"]["id"],rep["replicate"],rep["chosen_family"],center,rep["profiles"]["selected"][j],rep["profiles"]["nonparametric"][j],rep["profiles"]["output"][j],row["truth"]["output_profile"][j]])
    plots(rows,bank,config,out)
    print(f"Saved {len(rows)} scenarios to {out}")


if __name__=="__main__":main()
