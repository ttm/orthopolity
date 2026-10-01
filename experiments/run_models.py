"""Exploratory simulations with resource definitions fixed by model semantics.

Built-in neutral samplers, independent generative comparators, and transported
flux are labelled separately. Outputs assess model compatibility, not Nature.
No range is selected from observed slopes and no general-law p-value is computed.
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
from scipy.stats import binom

from orthopolity.figures import save_figure
from orthopolity.models import (
    bounded_multiplicative_growth,
    conservative_exchange,
    erdos_renyi_degrees,
    inverse_cost_samples,
    joint_feasibility_samples,
    preferential_attachment_degrees,
)
from orthopolity.spectrum import bounded_power_mle, resource_spectrum

ROOT = Path(__file__).resolve().parents[1]


def normalize_profile(values, widths):
    values = np.asarray(values, dtype=float)
    total = np.dot(values, widths)
    return values / (total / widths.sum()) if total > 0 else np.full_like(values, np.nan)


def profile_slope(values, centers):
    """Descriptive whole-domain log slope; never silently discard empty bins."""
    if np.any(values <= 0) or np.any(~np.isfinite(values)):
        return None
    return float(np.polyfit(np.log(centers), np.log(values), 1)[0])


def power_resource_profile(edges, tilt):
    widths = np.diff(np.log(edges))
    if abs(tilt) < 1e-12:
        return np.ones(len(widths))
    integral = (edges[1:] ** tilt - edges[:-1] ** tilt) / tilt
    return normalize_profile(integral / widths, widths)


def discrete_profile(edges, degrees, probabilities, resource):
    # Direct bin sums preserve tiny tail masses: cumulative weighted histogram
    # differencing can round nonzero masses to zero after a much larger bin.
    totals = np.array([
        np.sum((probabilities * resource)[
            (degrees >= lo) & ((degrees < hi) if j < len(edges)-2 else (degrees <= hi))
        ])
        for j, (lo, hi) in enumerate(zip(edges[:-1], edges[1:]))
    ])
    widths = np.diff(np.log(edges))
    return normalize_profile(totals / widths, widths)


def crossover_samples(n, lo, hi, ratio, rng):
    """Exact rejection sampler for p(x) proportional to 1/[x^3(1+ratio*x)]."""
    chunks, have = [], 0
    while have < n:
        candidates = inverse_cost_samples(max(1024, 2 * (n - have)), lo, hi, 2, 0, rng)
        keep = rng.random(len(candidates)) < (1 + ratio * lo) / (1 + ratio * candidates)
        accepted = candidates[keep]
        chunks.append(accepted)
        have += len(accepted)
    return np.concatenate(chunks)[:n]


def collect_profile(model, resource_name, samples, resource_values, edges, prediction,
                    parameters, status, population_prediction=None, fit_continuous=False):
    widths = np.diff(np.log(edges))
    centers = np.sqrt(edges[:-1] * edges[1:])
    profiles, counts, slopes, exponent_fits, totals, inclusion = [], [], [], [], [], []
    for x, q in zip(samples, resource_values):
        spec = resource_spectrum(x, q, edges)
        profiles.append(spec["occupancy"])
        counts.append(spec["count"])
        slopes.append(profile_slope(spec["occupancy"], centers))
        totals.append(float(np.sum(q)))
        inclusion.append(int(spec["count"].sum()))
        if fit_continuous:
            selected = x[(x >= edges[0]) & (x <= edges[-1])]
            exponent_fits.append(bounded_power_mle(selected, edges[0], edges[-1]))
    raw = np.asarray(profiles)
    # Aggregate raw profiles from runs with equal initial population/exposure, then
    # normalize ONCE. This is resource weighting, not equal normalized systems.
    mean = raw.mean(axis=0)
    phi = normalize_profile(mean, widths)
    scale = np.dot(mean, widths) / widths.sum()
    scaled_runs = raw / scale
    valid_slopes = [s for s in slopes if s is not None]
    result = dict(
        model=model, resource=resource_name, status=status, parameters=parameters,
        domain=[float(edges[0]), float(edges[-1])], bins=len(widths),
        prediction=prediction, population_prediction=population_prediction,
        profile=dict(lower=edges[:-1].tolist(), upper=edges[1:].tolist(),
                     center=centers.tolist(), log_width=widths.tolist(),
                     pooled_phi=phi.tolist(),
                     run_quantile_10=np.quantile(scaled_runs, .1, axis=0).tolist(),
                     run_quantile_90=np.quantile(scaled_runs, .9, axis=0).tolist()),
        mean_included_objects=float(np.mean(inclusion)),
        empty_bin_occurrences=int(np.sum(np.asarray(counts) == 0)),
        zero_resource_bin_occurrences=int(np.sum(raw == 0)),
        descriptive_pooled_log_resource_slope=profile_slope(phi, centers),
        descriptive_profile_max_min=float(phi.max() / phi.min()) if phi.min() > 0 else None,
        replicate_slopes=slopes,
        replicate_slope_quantiles_10_90=np.quantile(valid_slopes, [.1, .9]).tolist() if valid_slopes else None,
        sample_mean_full_finite_run_resource_total=float(np.mean(totals)),
        continuous_density_exponent_fits=exponent_fits or None,
    )
    if population_prediction is not None:
        expected = np.asarray(population_prediction["profile"])
        result["population_prediction"]["descriptive_binned_slope"] = profile_slope(expected, centers)
        result["profile_log_rmse_to_prediction"] = float(np.sqrt(np.mean(np.log(phi / expected) ** 2))) if phi.min() > 0 and expected.min() > 0 else None
    return result


def simulate(config):
    seed, reps, bins = config["seed"], config["replicates"], config["bins"]
    n = config["continuous_samples"]
    rows = []
    def rng(stream, rep):
        return np.random.default_rng(np.random.SeedSequence([seed, stream, rep]))
    def edges(key):
        return np.geomspace(*config[key], bins + 1)
    for index, (d, tilt, domain, name) in enumerate([
        (1, 0, "continuous_domain", "inverse_cost_d1"),
        (2, 0, "quadratic_domain", "inverse_cost_d2"),
        (1, .6, "continuous_domain", "tilted_allocation"),
    ]):
        e = edges(domain)
        xs = [inverse_cost_samples(n, e[0], e[-1], d, tilt, rng(10 + index, rep)) for rep in range(reps)]
        rows.append(collect_profile(name, f"q(x)=x^{d}", xs, [x ** d for x in xs], e,
            dict(density_exponent=d + 1 - tilt, resource_tilt=tilt), dict(d=d, allocation_tilt=tilt),
            "allocation imposed in sampler", {"profile": power_resource_profile(e, tilt).tolist(), "kind": "exact bounded population"}, True))

    e = edges("network_domain")
    nodes, m = config["network_nodes"], config["attachment_edges"]
    xs = [preferential_attachment_degrees(nodes, m, rng(20, rep)).astype(float) for rep in range(reps)]
    k = np.arange(m, int(e[-1]) + 1, dtype=float)
    pk = 2 * m * (m + 1) / (k * (k + 1) * (k + 2))
    for resource_name, q_fun, tilt in [("degree / edge incidences", lambda x: x, -1),
                                     ("centered wedges k(k-1)/2", lambda x: x * (x - 1) / 2, 0)]:
        rows.append(collect_profile("preferential_attachment", resource_name, xs, [q_fun(x) for x in xs], e,
            dict(asymptotic_density_exponent=3, asymptotic_resource_tilt=tilt), dict(nodes=nodes, m=m),
            "independent growth dynamics; asymptotic compatibility", {
                "profile": discrete_profile(e, k, pk, q_fun(k)).tolist(),
                "kind": "limiting discrete degree law; not finite-graph exact"}))
    xs = [erdos_renyi_degrees(nodes, 2 * m, rng(21, rep)).astype(float) for rep in range(reps)]
    # Isolated nodes have zero edge/wedge resource; positive-size spectrum excludes
    # them explicitly, without inventing a logarithm for zero degree.
    isolate_fraction = float(np.mean([np.mean(x == 0) for x in xs]))
    xs = [x[x > 0] for x in xs]
    k = np.arange(1, int(e[-1]) + 1, dtype=float)
    pk = binom.pmf(k, nodes - 1, 2 * m / (nodes - 1))
    for resource_name, q_fun in [("degree / edge incidences", lambda x: x),
                               ("centered wedges k(k-1)/2", lambda x: x * (x - 1) / 2)]:
        rows.append(collect_profile("erdos_renyi", resource_name, xs, [q_fun(x) for x in xs], e,
            dict(degree_distribution="Binomial(n-1,p), not a power law"),
            dict(nodes=nodes, mean_degree=2*m, excluded_isolate_fraction=isolate_fraction),
            "independent random-graph comparator", {
                "profile": discrete_profile(e, k, pk, q_fun(k)).tolist(), "kind": "exact ensemble degree law"}))

    e = edges("exchange_domain")
    for index, saving in enumerate(config["saving_fractions"]):
        xs = [conservative_exchange(config["exchange_agents"], config["exchange_sweeps"], rng(30 + index, rep), saving=saving) for rep in range(reps)]
        resource_integral = ((e[:-1] + 1) * np.exp(-e[:-1]) - (e[1:] + 1) * np.exp(-e[1:]))
        reference = {"profile": normalize_profile(resource_integral / np.diff(np.log(e)), np.diff(np.log(e))).tolist(),
                     "kind": "large-population stationary exponential; finite fixed-sum law differs"} if saving == 0 else None
        rows.append(collect_profile("conservative_exchange" if saving == 0 else "saving_exchange", "money q(x)=x", xs, xs, e,
            dict(resource_total=config["exchange_agents"], stationary_shape="exponential" if saving == 0 else "peaked / gamma-like; no exact gamma claim"),
            dict(agents=config["exchange_agents"], sweeps=config["exchange_sweeps"], saving=saving,
                 full_mean=float(np.mean([np.mean(x) for x in xs])), full_variance=float(np.mean([np.var(x) for x in xs])),
                 maximum_total_error=float(max(abs(x.sum() - config["exchange_agents"]) for x in xs))),
            "independent conserved-resource dynamics", reference))

    e = edges("growth_domain")
    sigma = config["growth_diffusion"]
    for index, drift in enumerate(config["growth_drifts"]):
        tail = -2 * drift / sigma ** 2
        xs = [bounded_multiplicative_growth(config["growth_agents"], config["growth_steps"], drift, sigma, rng(40 + index, rep)) for rep in range(reps)]
        rows.append(collect_profile("floor_multiplicative_growth", "size/wealth q(x)=x", xs, xs, e,
            dict(asymptotic_survival_exponent=tail, asymptotic_density_exponent=tail + 1,
                 asymptotic_resource_tilt=1-tail),
            dict(agents=config["growth_agents"], steps=config["growth_steps"], drift=drift, diffusion=sigma,
                 floor_atom_fraction=float(np.mean([np.mean(x == 1) for x in xs]))),
            "independent multiplicative dynamics; stationary tail comparison, not exact full profile",
            {"profile": power_resource_profile(e, 1-tail).tolist(), "kind": "asymptotic tail reference"}, True))

    e = edges("feasibility_domain")
    for index, theta in enumerate(config["shared_rates"]):
        outcomes = [joint_feasibility_samples(n, 2, theta, rng(50 + index, rep)) for rep in range(reps)]
        xs = [out["size"] for out in outcomes]
        # Each resource holds the SAME one-dimensional marginal availability law.
        # The resource actually audited across realized object size is q=x, fixed
        # for all dependence settings; no exponent-derived resource is substituted.
        d_joint = 2 - theta
        probabilities = [np.mean(out["capacities"] >= 2, axis=0) for out in outcomes]
        rows.append(collect_profile("joint_feasibility", "realized capacity q(x)=x", xs, xs, e,
            dict(survival_exponent=d_joint, density_exponent=d_joint+1, resource_tilt=1-d_joint,
                 marginal_survival_at_2=.5),
            dict(resources=2, shared_rate=theta, observed_marginal_survival_at_2=np.mean(probabilities, axis=0).tolist()),
            "constructed common-shock resource mechanism; marginal laws held fixed",
            {"profile": power_resource_profile(e, 1-d_joint).tolist(), "kind": "exact joint-feasibility population"}, True))

    e = edges("crossover_domain")
    for index, ratio in enumerate(config["crossover_ratios"]):
        xs = [crossover_samples(n, e[0], e[-1], ratio, rng(60 + index, rep)) for rep in range(reps)]
        rows.append(collect_profile("compound_cost_crossover", "effective cost x^2(1+b*x)", xs,
            [x*x*(1+ratio*x) for x in xs], e,
            dict(crossover=1/ratio, effective_dimension="2+b*x/(1+b*x)", resource_tilt=0),
            dict(surface_coefficient=1, volume_coefficient=ratio),
            "allocation imposed in sampler; crossover is a proposed test template",
            {"profile": np.ones(bins).tolist(), "kind": "exact compound-cost neutral population"}))
    return rows


def transport(config):
    r = np.asarray(config["transport_radii"], dtype=float)
    rate, cap = config["transport_loss_rate"], config["transport_angular_cap_cosine"]
    area = 4 * np.pi * r*r
    cap_fraction = (1-cap)/2
    lossless, lossy, cap_samples = [], [], []
    for rep in range(config["replicates"]):
        rng = np.random.default_rng(np.random.SeedSequence([config["seed"], 70, rep]))
        life = rng.exponential(1/rate, config["transport_rays"])
        cosine = rng.uniform(-1, 1, config["transport_rays"])
        lossless.append(np.ones_like(r))
        lossy.append(np.asarray([np.mean(life >= x) for x in r]))
        cap_samples.append(np.full_like(r, np.mean(cosine >= cap)))
    mean_lossy = np.mean(lossy, axis=0)
    return dict(
        status="analytic lossless flux construction; Monte Carlo absorption and angular coverage; nested surfaces reuse photons",
        radii=r.tolist(), sphere_area=area.tolist(),
        lossless_intensity=(1/area).tolist(), lossless_power=np.mean(lossless, axis=0).tolist(),
        lossy_intensity=(mean_lossy/area).tolist(), lossy_power=mean_lossy.tolist(),
        predicted_lossy_power=np.exp(-rate*r).tolist(),
        angular_cap_fraction=cap_fraction, observed_cap_power=np.mean(cap_samples, axis=0).tolist(),
        stock_energy_per_linear_radius_for_unit_speed=np.ones_like(r).tolist(),
        stock_energy_per_log_radius_for_unit_speed=r.tolist(),
        parameters=dict(ray_count=config["transport_rays"], loss_rate=rate, cap_cosine=cap),
        maximum_lossy_power_error=float(np.max(abs(mean_lossy-np.exp(-rate*r)))),
        lossless_intensity_slope=float(np.polyfit(np.log(r),np.log(1/area),1)[0]),
    )


def plots(rows, flux, config, out):
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "svg.fonttype": "none"})
    fig, axes = plt.subplots(2, 3, figsize=(14, 8), layout="constrained")
    panels = [
        ("A  Declared allocation controls", [r for r in rows if r["model"].startswith("inverse_cost") or r["model"]=="tilted_allocation"], "Size x"),
        ("B  One network, two declared resources", [r for r in rows if r["model"]=="preferential_attachment"], "Degree k"),
        ("C  Conservation and saving", [r for r in rows if r["model"] in ("conservative_exchange", "saving_exchange")], "Money x"),
        ("D  Multiplicative growth, fixed resource", [r for r in rows if r["model"]=="floor_multiplicative_growth"], "Size x"),
        ("E  Same marginal resources, changed dependence", [r for r in rows if r["model"]=="joint_feasibility"], "Feasible size x"),
    ]
    for ax, (title, subset, xlabel) in zip(axes.flat, panels):
        for row in subset:
            x=np.asarray(row["profile"]["center"]); y=np.asarray(row["profile"]["pooled_phi"])
            if row["model"]=="preferential_attachment": label=row["resource"]
            elif row["model"]=="joint_feasibility": label=f"shared rate {row['parameters']['shared_rate']:g}"
            elif row["model"] in ("conservative_exchange", "saving_exchange"): label=f"saving {row['parameters']['saving']:g}"
            elif row["model"]=="floor_multiplicative_growth": label=f"tail exponent {row['prediction']['asymptotic_survival_exponent']:g}"
            else: label=row["model"].replace("_", " ")
            line,=ax.plot(x,y,"o-",ms=3,lw=1.4,label=label)
            ax.fill_between(x,row["profile"]["run_quantile_10"],row["profile"]["run_quantile_90"],color=line.get_color(),alpha=.12)
            if row["population_prediction"] is not None:
                ax.plot(x,row["population_prediction"]["profile"],"--",color=line.get_color(),lw=1)
        ax.axhline(1,color="#777777",ls=":",lw=.9)
        ax.set(xscale="log",yscale="log",title=title,xlabel=xlabel,ylabel="Resource per log interval / mean")
        ax.legend(fontsize=7,frameon=False)
    ax=axes.flat[-1]
    r=np.asarray(flux["radii"])
    ax.plot(r,flux["lossless_power"],"o-",label="Analytic lossless sphere power")
    ax.plot(r,flux["lossy_power"],"o-",label="Surviving power, with absorption")
    ax.plot(r,flux["predicted_lossy_power"],"--",label="Independent loss prediction")
    ax.set(xscale="log",yscale="log",title="F  Light transport across nested spheres",xlabel="Radius r",ylabel="Power crossing sphere / source power")
    ax.legend(fontsize=7,frameon=False)
    for ax in axes.flat:
        ax.spines[["top","right"]].set_visible(False)
        ax.grid(alpha=.2,which="both")
    fig.suptitle(f"Exploratory model comparisons - {config['replicates']} independent runs\nDashed: model prediction; bands: run 10-90% quantiles, not confidence intervals",fontsize=11)
    for ext in ("png","svg"):
        save_figure(fig, out/f"model-study.{ext}", dpi=160)
    plt.close(fig)

    fig,axes=plt.subplots(1,2,figsize=(10,4),layout="constrained")
    grid=np.geomspace(*config["crossover_domain"],500)
    for row in (r for r in rows if r["model"]=="compound_cost_crossover"):
        b=row["parameters"]["volume_coefficient"]
        axes[0].plot(grid,2+b*grid/(1+b*grid),label=f"b={b:g}, crossover={1/b:g}")
        axes[0].axvline(1/b,ls=":",lw=.9)
        axes[1].plot(row["profile"]["center"],row["profile"]["pooled_phi"],"o-",label=f"b={b:g}")
    axes[0].set(xscale="log",xlabel="Size x",ylabel="Independent effective cost dimension",title="Predicted cost crossover")
    axes[1].axhline(1,color="grey",ls=":")
    axes[1].set(xscale="log",ylim=(.85,1.15),xlabel="Size x",ylabel="Resource per log interval / mean",title="Neutral allocation imposed in sampler")
    for ax in axes: ax.legend(frameon=False); ax.spines[["top","right"]].set_visible(False)
    fig.suptitle("A proposed intervention template; generated neutrality is not physical validation",fontsize=10)
    for ext in ("png","svg"): save_figure(fig, out/f"model-crossovers.{ext}", dpi=160)
    plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config",type=Path,default=ROOT/"configs/model_study_2026-10-01.json")
    parser.add_argument("--output",type=Path,default=ROOT/"results/models")
    args=parser.parse_args()
    config=json.loads(args.config.read_text())
    rows=simulate(config); flux=transport(config)
    for index, row in enumerate(rows, start=1):
        row["scenario_id"] = f"s{index:02d}_{row['model']}"
    out=args.output; out.mkdir(parents=True,exist_ok=True)
    import scipy
    report=dict(kind="exploratory simulated compatibility, not empirical validation",config=config,
                versions=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,matplotlib=matplotlib.__version__),
                resource_aggregation="mean raw resource density across independent runs, normalized once on each declared domain",
                uncertainty=config["uncertainty"],scenarios=rows,transport=flux)
    (out/"model-study.json").write_text(json.dumps(report,indent=2,allow_nan=False)+"\n")
    with (out/"profiles.csv").open("w",newline="") as handle:
        writer=csv.writer(handle, lineterminator="\n");writer.writerow(["scenario_id","model","resource","parameters_json","lower","upper","center","pooled_phi","run_q10","run_q90","prediction_phi"])
        for row in rows:
            p=row["profile"]
            for i in range(len(p["center"])):
                pred=row["population_prediction"]["profile"][i] if row["population_prediction"] else ""
                writer.writerow([row["scenario_id"],row["model"],row["resource"],json.dumps(row["parameters"],sort_keys=True),p["lower"][i],p["upper"][i],p["center"][i],p["pooled_phi"][i],p["run_quantile_10"][i],p["run_quantile_90"][i],pred])
    plots(rows,flux,config,out)
    for row in rows:
        slope=row["descriptive_pooled_log_resource_slope"]
        fitted=np.mean(row["continuous_density_exponent_fits"]) if row["continuous_density_exponent_fits"] else None
        print(json.dumps(dict(model=row["model"],resource=row["resource"],resource_slope=slope,
                              fitted_density_exponent=None if fitted is None else float(fitted),
                              prediction=row["prediction"])))
    print(f"Saved {len(rows)} allocation scenarios and transport comparison to {out}")


if __name__=="__main__":
    main()
