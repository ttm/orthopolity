"""Reproduce a conservative class-resource exchange and constraint intervention.

All analytic predictions are written before stochastic trajectories are drawn.
The process is a specified toy model, not fitted data or empirical validation.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform

import numpy as np
import scipy
from scipy.stats import binom

from orthopolity.class_exchange import (
    advance_quanta, equilibrium, generator, relative_l2, spectral_gap,
    transition_matrix,
)


ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def design(config):
    """Instantiate fixed classes, independent costs, and prescribed kinetics."""
    for name, minimum in (("classes", 2), ("intervals_per_phase", 2),
                          ("resource_quanta", 1), ("replicates", 2), ("seed", 0)):
        value = config[name]
        if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
            raise ValueError(f"{name} must be an integer >= {minimum}")
    for name in ("size_min", "size_max", "diffusivity",
                 "potential_sigma_log_size", "phase_relaxation_times"):
        if not np.isfinite(config[name]) or config[name] <= 0:
            raise ValueError(f"{name} must be finite and positive")
    if config["size_min"] >= config["size_max"]:
        raise ValueError("size_min must be below size_max")
    if (not np.isfinite(config["resource_degree"])
            or not np.isfinite(config["potential_center_log_size"])):
        raise ValueError("degree and potential center must be finite")
    initial = config["initial_class"]
    n = config["classes"]
    if isinstance(initial, bool) or not isinstance(initial, int) or not 0 <= initial < n:
        raise ValueError("initial_class must select a declared class")
    edges = np.linspace(np.log(config["size_min"]), np.log(config["size_max"]), n + 1)
    widths = np.diff(edges)
    centers = (edges[:-1] + edges[1:]) / 2
    sizes = np.exp(centers)
    q = sizes ** config["resource_degree"]
    if not np.isfinite(q).all() or np.any(q <= 0):
        raise ValueError("independent per-object resource is not representable")
    conductances = np.zeros((n, n))
    for i in range(n - 1):
        conductances[i, i + 1] = conductances[i + 1, i] = (
            config["diffusivity"] / (centers[i + 1] - centers[i]))
    potential = ((centers - config["potential_center_log_size"])
                 / config["potential_sigma_log_size"]) ** 2 / 2
    matrices = [generator(widths, conductances), generator(widths, conductances, potential)]
    targets = [equilibrium(widths), equilibrium(widths, potential)]
    gaps = [spectral_gap(matrix, target) for matrix, target in zip(matrices, targets)]
    start = np.zeros(n)
    start[initial] = 1
    phases = []
    offset = 0.
    for name, choice in (("neutral", 0), ("constrained", 1), ("released", 0)):
        duration = config["phase_relaxation_times"] / gaps[choice]
        phases.append(dict(name=name, matrix=matrices[choice], target=targets[choice],
                           gap=gaps[choice], duration=duration, offset=offset, initial=start.copy()))
        start = transition_matrix(matrices[choice], duration) @ start
        offset += duration
    return dict(edges=edges, widths=widths, sizes=sizes, q=q, potential=potential,
                conductances=conductances, phases=phases)


def predictions(config, model):
    phases = model["phases"]
    neutral = phases[0]["matrix"]
    constrained = phases[1]["matrix"]
    target = phases[1]["target"]
    neutral_drift = neutral @ target
    constraint_drift = (constrained - neutral) @ target
    return dict(
        status="analytic_predictions_from_fixed_inputs_before_stochastic_simulation",
        model_scope="Conditional constructive toy mechanism; no empirical or universal-law claim",
        state="Fixed-class resource shares; microscopic quanta carry equal resource",
        reference_measure="w_i = log(k_right/k_left), fixed before generating trajectories",
        independent_cost="q_i = k_i**resource_degree; equivalent object abundance R_i/q_i",
        count_scope="R_i/q_i may be noninteger and is not a conserved closed object census",
        generator_orientation="A[j,i] = (G[i,j]/w[i])*exp(max(V[i]-V[j],0)); columns sum to zero",
        equilibrium_formula="pi_i = w_i exp(-V_i) / sum_j w_j exp(-V_j)",
        contraction_formula="E(t) <= E(0) exp(-gap*t), E^2=sum((p-pi)^2/pi)",
        finite_quantum_law="Counts(t) ~ Multinomial(M,p(t)) for this all-in-one-class initial condition",
        finite_quantum_covariance="Cov(count_i/M,count_j/M)=(delta_ij*p_i-p_i*p_j)/M",
        constraint_removal="Both deterministic and stochastic states carry forward unchanged at switches",
        log_edges=model["edges"].tolist(), sizes=model["sizes"].tolist(),
        reference_weights=model["widths"].tolist(), independent_q=model["q"].tolist(),
        constrained_potential=model["potential"].tolist(),
        conductances=model["conductances"].tolist(),
        stationary_opposing_drifts=dict(
            neutral_drift=neutral_drift.tolist(), constraint_drift=constraint_drift.tolist(),
            neutral_l2=float(np.linalg.norm(neutral_drift)),
            constraint_l2=float(np.linalg.norm(constraint_drift)),
            cancellation_l2=float(np.linalg.norm(neutral_drift + constraint_drift))),
        phases=[dict(name=phase["name"], start_time=phase["offset"], duration=phase["duration"],
                     gap=phase["gap"], initial_share=phase["initial"].tolist(),
                     stationary_share=phase["target"].tolist(),
                     stationary_resource_density=(phase["target"] / model["widths"]).tolist(),
                     stationary_equivalent_abundance=(phase["target"] / model["q"]).tolist(),
                     stationary_equivalent_abundance_density=(
                         phase["target"] / model["q"] / model["widths"]).tolist(),
                     initial_relative_l2=float(relative_l2(phase["initial"], phase["target"])),
                     endpoint_relative_l2_bound=float(relative_l2(phase["initial"], phase["target"])
                         * np.exp(-phase["gap"] * phase["duration"])),
                     column_generator=phase["matrix"].tolist()) for phase in phases])


def simulate(config, model):
    rng = np.random.default_rng(config["seed"])
    total = config["resource_quanta"]
    counts = np.zeros((config["replicates"], config["classes"]), dtype=np.int64)
    counts[:, config["initial_class"]] = total
    resource = model["phases"][0]["initial"].copy()
    records = []
    for phase_index, phase in enumerate(model["phases"]):
        times = np.linspace(0, phase["duration"], config["intervals_per_phase"] + 1)
        transition = transition_matrix(phase["matrix"], times[1])
        start_error = float(relative_l2(resource, phase["target"]))
        for checkpoint, local_time in enumerate(times):
            if checkpoint:
                resource = transition @ resource
                counts = advance_quanta(counts, transition, rng)
            shares = counts / total
            theoretical_variance = resource * np.maximum(1 - resource, 0) / total
            # Exact marginal pointwise intervals; neither simultaneous bands nor mean uncertainty.
            lower = binom.ppf(.025, total, np.clip(resource, 0, 1)) / total
            upper = binom.ppf(.975, total, np.clip(resource, 0, 1)) / total
            if not np.all(counts.sum(axis=1) == total):
                raise AssertionError("quantum total changed")
            records.append(dict(
                phase=phase["name"], phase_index=phase_index, checkpoint=checkpoint,
                time=phase["offset"] + float(local_time), local_time=float(local_time),
                relaxation_time=float(local_time * phase["gap"]), expected=resource.copy(),
                mean=shares.mean(axis=0), variance=shares.var(axis=0, ddof=1),
                theoretical_variance=theoretical_variance, lower=lower, upper=upper,
                sample=shares[0].copy(), counts=counts.copy(),
                error=float(relative_l2(resource, phase["target"])),
                bound=start_error * np.exp(-phase["gap"] * local_time)))
    return records


def trajectory_csv(path, records, model):
    with path.open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(("phase", "checkpoint", "time", "phase_time", "relaxation_time", "class",
                         "size", "reference_width", "q", "expected_resource_share", "mean_resource_share",
                         "sample_resource_share", "replicate_variance", "analytic_variance",
                         "pointwise_95_lower", "pointwise_95_upper", "equivalent_abundance",
                         "relative_l2", "relative_l2_bound"))
        for record in records:
            for i, size in enumerate(model["sizes"]):
                writer.writerow((record["phase"], record["checkpoint"], record["time"], record["local_time"],
                    record["relaxation_time"], i, size, model["widths"][i], model["q"][i],
                    record["expected"][i], record["mean"][i], record["sample"][i],
                    record["variance"][i], record["theoretical_variance"][i],
                    record["lower"][i], record["upper"][i], record["expected"][i] / model["q"][i],
                    record["error"], record["bound"]))


def figures(output, config, model, records, forecast):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import TwoSlopeNorm

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "svg.fonttype": "none",
                         "svg.hashsalt": config["run_id"]})
    fig, axes = plt.subplots(2, 3, figsize=(13.4, 8.0), layout="constrained")
    sizes = model["sizes"]
    colors = ("#285f9b", "#b9532e", "#398362")
    time = np.array([r["time"] for r in records])
    # Eliminate duplicated switch times for the heatmap only.
    distinct = np.concatenate(([True], np.diff(time) > 0))
    density_ratio = np.array([r["expected"] for r in records]) / model["phases"][0]["target"]
    ax = axes[0, 0]
    mesh = ax.pcolormesh(time[distinct], sizes, np.log10(np.maximum(density_ratio[distinct].T, 1e-3)),
                         shading="nearest", cmap="coolwarm", norm=TwoSlopeNorm(0, vmin=-3, vmax=1.5),
                         rasterized=True)
    ax.set(yscale="log", xlabel="Time (model units)", ylabel="Class size k",
           title="a  Class-resource evolution")
    fig.colorbar(mesh, ax=ax, label="log₁₀(resource / neutral share)", fraction=.045)
    for phase in model["phases"][1:]:
        ax.axvline(phase["offset"], color="black", linestyle=":", linewidth=.8)
    for phase in model["phases"]:
        ax.text(phase["offset"] + phase["duration"] / 2, .98, phase["name"],
                transform=ax.get_xaxis_transform(), ha="center", va="top", fontsize=8)

    for phase, color in zip(model["phases"][:2], colors):
        axes[0, 1].plot(sizes, phase["target"] / model["widths"], color=color, label=phase["name"])
        axes[0, 2].plot(sizes, phase["target"] / model["q"] / model["widths"], color=color,
                        label=phase["name"])
    axes[0, 1].set(xscale="log", xlabel="Class size k", ylabel="Stationary resource / log width",
                    title="b  Resource allocation across classes")
    axes[0, 2].set(xscale="log", yscale="log", xlabel="Class size k",
                    ylabel="Equivalent abundance / log width",
                    title=f"c  Independent cost q = k^{config['resource_degree']:g}")
    axes[0, 2].text(.04, .07, f"Neutral abundance ∝ k$^{{{-config['resource_degree']:g}}}$\n"
                     "Total resource normalized to one",
                     transform=axes[0, 2].transAxes, fontsize=8)
    for ax in axes[0, 1:]:
        ax.legend(frameon=False)

    drifts = forecast["stationary_opposing_drifts"]
    ax = axes[1, 0]
    ax.plot(sizes, drifts["neutral_drift"], color=colors[0], label="Neutral contribution")
    ax.plot(sizes, drifts["constraint_drift"], color=colors[1], label="Constraint contribution")
    ax.axhline(0, color="black", linestyle=":", linewidth=.8)
    ax.set(xscale="log", xlabel="Class size k", ylabel="Resource-share rate",
           title="d  Opposing drifts at constrained equilibrium")
    ax.legend(frameon=False, fontsize=8)
    ax.text(.04, .025, "Net drift = 0; neutral dynamics remain active", transform=ax.transAxes, fontsize=8,
            bbox=dict(facecolor="white", edgecolor="none", alpha=.8, pad=1))

    ax = axes[1, 1]
    middle = int(np.argmin(np.abs(np.log(sizes) - config["potential_center_log_size"])))
    ax.fill_between(time, [r["lower"][middle] for r in records], [r["upper"][middle] for r in records],
                    color="#d0dce9", label="Exact 95% interval for one realization")
    ax.plot(time, [r["expected"][middle] for r in records], color=colors[0], label="Analytic expectation")
    ax.plot(time, [r["sample"][middle] for r in records], color="gray", linewidth=.65, alpha=.6,
            label="One quantum realization")
    ax.plot(time, [r["mean"][middle] for r in records], color="black", linestyle="--", linewidth=.85,
            label=f"Mean of {config['replicates']} realizations")
    for phase in model["phases"][1:]:
        ax.axvline(phase["offset"], color="black", linestyle=":", linewidth=.8)
    ax.set(xlabel="Time (model units)", ylabel="Resource share",
           title=f"e  Finite resource quanta, class k = {sizes[middle]:.2f}")
    ax.legend(frameon=False, fontsize=7, loc="lower right")

    ax = axes[1, 2]
    for phase, color in zip(model["phases"], colors):
        rows = [r for r in records if r["phase"] == phase["name"]]
        initial = rows[0]["error"]
        ax.plot([r["relaxation_time"] for r in rows], [r["error"] / initial for r in rows],
                color=color, label=phase["name"])
    tau = np.linspace(0, config["phase_relaxation_times"], 100)
    ax.plot(tau, np.exp(-tau), "k--", linewidth=1, label="Spectral-gap upper bound")
    ax.set(yscale="log", xlabel="Time since switch × current spectral gap",
           ylabel="Relative L² error / initial error", title="f  Convergence, constraint, and release")
    ax.legend(frameon=False, fontsize=8)
    for ax in axes.flat:
        ax.spines[["top", "right"]].set_visible(False)
        if ax is not axes[0, 0]:
            ax.grid(alpha=.18)
    fig.suptitle("Resource exchange among fixed logarithmic classes\n"
                 "Specified toy dynamics • constraint added and removed • state preserved at both switches",
                 fontsize=12)
    fig.savefig(output / "class-exchange.png", dpi=180)
    fig.savefig(output / "class-exchange.svg", metadata={"Date": None})
    svg = output / "class-exchange.svg"
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines()) + "\n")
    plt.close(fig)


def run(config_path, output):
    config = json.loads(config_path.read_text())
    sources = [Path(__file__), ROOT / "src/orthopolity/class_exchange.py"]
    source_hashes = {str(path.relative_to(ROOT)): digest(path) for path in sources}
    manifest_path = output / "provenance.json"
    if manifest_path.exists():
        retained = json.loads(manifest_path.read_text())
        if retained["config_sha256"] != digest(config_path) or retained["source_sha256"] != source_hashes:
            raise ValueError("retained inputs changed; preserve this run and choose another output directory")
        if not all((output / path).exists() and digest(output / path) == checksum
                   for path, checksum in retained["artifact_sha256"].items()):
            raise ValueError("retained artifacts changed; preserve this run and choose another output directory")
        print(json.dumps(dict(action="audited_existing_run", output=str(output))))
        return
    if output.exists() and any(output.iterdir()):
        raise ValueError("output directory is not empty; preserve it and choose another directory")
    model = design(config)
    forecast = predictions(config, model)
    output.mkdir(parents=True, exist_ok=True)
    (output / "config.json").write_bytes(config_path.read_bytes())
    write_json(output / "predictions.json", forecast)
    forecast_hash = digest(output / "predictions.json")
    records = simulate(config, model)
    trajectory_csv(output / "trajectories.csv", records, model)
    np.savez_compressed(output / "quantum-counts.npz",
                        counts=np.array([r["counts"] for r in records]),
                        time=np.array([r["time"] for r in records]),
                        phase=np.array([r["phase"] for r in records]))
    phase_summaries = []
    for phase in model["phases"]:
        rows = [r for r in records if r["phase"] == phase["name"]]
        end = rows[-1]
        phase_summaries.append(dict(name=phase["name"], spectral_gap=phase["gap"], duration=phase["duration"],
            initial_relative_l2=rows[0]["error"], final_relative_l2=end["error"], final_bound=end["bound"],
            maximum_bound_excess=float(max(r["error"] - r["bound"] for r in rows)),
            mean_absolute_resource_share_error=float(np.mean(np.abs(end["mean"] - end["expected"]))),
            final_stationary_l1_error=float(np.sum(np.abs(end["expected"] - phase["target"]))),
            final_resource_share=end["expected"].tolist(), final_monte_carlo_mean=end["mean"].tolist(),
            final_replicate_variance=end["variance"].tolist(),
            final_exact_marginal_variance=end["theoretical_variance"].tolist()))
    summary = dict(kind=config["kind"], run_id=config["run_id"], predictions_sha256=forecast_hash,
        resource_total_normalization=1, resource_quanta=config["resource_quanta"], replicates=config["replicates"],
        maximum_deterministic_total_error=float(max(abs(r["expected"].sum() - 1) for r in records)),
        all_stochastic_totals_conserved=all(np.all(r["counts"].sum(axis=1) == config["resource_quanta"]) for r in records),
        minimum_stochastic_count=int(min(r["counts"].min() for r in records)),
        maximum_state_discontinuity_at_switch=float(max(
            np.max(np.abs(records[i]["expected"] - records[i - 1]["expected"]))
            for i in range(1, len(records)) if records[i]["checkpoint"] == 0)),
        stochastic_states_preserved_at_switch=all(np.array_equal(records[i]["counts"], records[i - 1]["counts"])
            for i in range(1, len(records)) if records[i]["checkpoint"] == 0),
        stationary_opposing_drifts=forecast["stationary_opposing_drifts"], phases=phase_summaries,
        uncertainty="Exact pointwise binomial marginal intervals for one finite-quantum realization; not simultaneous bands or confidence intervals for fitted theory",
        evidence_scope="Constructive consequence of the declared dynamics; not new natural observations")
    # np.bool_ is not JSON serializable.
    summary["all_stochastic_totals_conserved"] = bool(summary["all_stochastic_totals_conserved"])
    write_json(output / "summary.json", summary)
    figures(output, config, model, records, forecast)
    write_json(manifest_path, dict(run_id=config["run_id"], generated_utc=datetime.now(timezone.utc).isoformat(),
        config_sha256=digest(config_path), source_sha256=source_hashes,
        runtime=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__),
        predictions_written_before_stochastic_simulation=True,
        artifact_sha256={path.name: digest(path) for path in sorted(output.iterdir()) if path.is_file()}))
    print(json.dumps(dict(action="generated", output=str(output), phases=[
        {key: phase[key] for key in ("name", "spectral_gap", "duration", "final_relative_l2", "final_bound")}
        for phase in phase_summaries],
                         opposing_drift_cancellation=forecast["stationary_opposing_drifts"]["cancellation_l2"]), indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/class_exchange_2026-10-05.json")
    parser.add_argument("--output", type=Path, default=ROOT / "build/reproductions/class-exchange")
    args = parser.parse_args()
    run(args.config.resolve(), args.output.resolve())
