"""Render a manuscript figure from retained class-exchange outputs only.

This presentation step reads existing analytic predictions and trajectories.
It neither changes the declared model nor reruns its deterministic or stochastic
evolution. Errors and bounds are divided by each phase's recorded initial error
solely to display their relative contraction on a common vertical axis.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def render(input_directory, output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    input_files = [input_directory / name for name in ("predictions.json", "trajectories.csv")]
    input_hashes = {path.name: digest(path) for path in input_files}
    source_hash = digest(__file__)
    provenance_path = output / "provenance.json"
    if provenance_path.exists():
        retained = json.loads(provenance_path.read_text())
        if retained["input_sha256"] != input_hashes or retained["source_sha256"] != source_hash:
            raise ValueError("retained figure inputs changed; preserve this output and choose another directory")
        if not all((output / name).exists() and digest(output / name) == checksum
                   for name, checksum in retained["artifact_sha256"].items()):
            raise ValueError("retained figure artifacts changed; preserve this output and choose another directory")
        print(json.dumps(dict(action="audited_existing_presentation", output=str(output))))
        return
    if output.exists() and any(output.iterdir()):
        raise ValueError("output directory is not empty; preserve it and choose another directory")

    forecast = json.loads(input_files[0].read_text())
    trajectories = {}
    with input_files[1].open(newline="") as stream:
        for row in csv.DictReader(stream):
            # Each class row repeats the same phase-level scalar error/bound.
            if int(row["class"]) == 0:
                trajectories.setdefault(row["phase"], []).append(row)
    phases = forecast["phases"]
    sizes = forecast["sizes"]
    colors = ("#285f9b", "#b9532e", "#398362")
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.titlesize": 10, "axes.labelsize": 10,
                         "xtick.labelsize": 9, "ytick.labelsize": 9,
                         "legend.fontsize": 8.5, "svg.fonttype": "none",
                         "svg.hashsalt": "class-exchange-manuscript-presentation"})
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 6.0), layout="constrained")
    for phase, color in zip(phases[:2], colors):
        axes[0, 0].plot(sizes, phase["stationary_resource_density"], color=color,
                        linewidth=1.7, label=phase["name"].capitalize())
        axes[0, 1].plot(sizes, phase["stationary_equivalent_abundance_density"], color=color,
                        linewidth=1.7, label=phase["name"].capitalize())
    axes[0, 0].set(xscale="log", xlabel="Class size k", ylabel="Resource / log width",
                    title="a  Stationary resource allocation")
    axes[0, 1].set(xscale="log", yscale="log", xlabel="Class size k",
                    ylabel="Equivalent abundance / log width", title="b  Abundance from independent q(k)")
    for ax in axes[0]:
        ax.legend(frameon=False, loc="best", handlelength=1.5)

    drift = forecast["stationary_opposing_drifts"]
    ax = axes[1, 0]
    ax.plot(sizes, drift["neutral_drift"], color=colors[0], linewidth=1.7,
            label="Neutral contribution")
    ax.plot(sizes, drift["constraint_drift"], color=colors[1], linewidth=1.7,
            label="Constraint contribution")
    ax.axhline(0, color="black", linestyle=":", linewidth=.8)
    ax.set(xscale="log", xlabel="Class size k", ylabel="Resource-share rate",
           title="c  Opposing stationary contributions")
    ax.margins(y=.27)
    ax.legend(frameon=False, loc="upper right", handlelength=1.5, fontsize=8)
    ax.text(.035, .025, "Net drift = 0", transform=ax.transAxes, fontsize=9,
            bbox=dict(facecolor="white", edgecolor="none", alpha=.8, pad=1))

    ax = axes[1, 1]
    for phase, color in zip(phases, colors):
        rows = trajectories[phase["name"]]
        initial = float(rows[0]["relative_l2"])
        tau = [float(row["relaxation_time"]) for row in rows]
        errors = [float(row["relative_l2"]) / initial for row in rows]
        bounds = [float(row["relative_l2_bound"]) / initial for row in rows]
        ax.plot(tau, errors, color=color, linewidth=1.7, label=phase["name"].capitalize())
        ax.plot(tau, bounds, color="black", linestyle="--", linewidth=1.0,
                label="Gap bound" if phase is phases[0] else "_nolegend_")
    ax.set(yscale="log", xlabel="Time since switch × spectral gap",
           ylabel="Relative L² error / initial error", title="d  Relaxation and constraint removal")
    ax.legend(frameon=False, loc="lower left", handlelength=1.5, fontsize=8)
    for ax in axes.flat:
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(alpha=.18)
    output.mkdir(parents=True, exist_ok=True)
    fig.savefig(output / "class-exchange.png", dpi=240, bbox_inches="tight", pad_inches=.06)
    fig.savefig(output / "class-exchange.svg", metadata={"Date": None}, bbox_inches="tight", pad_inches=.06)
    plt.close(fig)
    svg = output / "class-exchange.svg"
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines()) + "\n")
    provenance = dict(
        kind="presentation_of_retained_toy_model_outputs_without_resimulation",
        inputs={path.name: str(path.resolve()) for path in input_files},
        input_sha256=input_hashes, source=str(Path(__file__).relative_to(ROOT)),
        source_sha256=source_hash, matplotlib_version=matplotlib.__version__,
        display_transform="For each phase, divide retained relative_l2 and relative_l2_bound by its first recorded relative_l2",
        simulation_rerun=False,
        artifact_sha256={path.name: digest(path) for path in sorted(output.iterdir()) if path.is_file()})
    provenance_path.write_text(json.dumps(provenance, indent=2, allow_nan=False) + "\n")
    print(json.dumps(dict(action="rendered_retained_presentation", output=str(output))))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "results/class-exchange")
    parser.add_argument("--output", type=Path, default=ROOT / "build/reproductions/class-exchange-presentation")
    args = parser.parse_args()
    render(args.input.resolve(), args.output.resolve())
