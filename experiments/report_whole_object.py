"""Render retained analytic whole-object forecasts without rerunning kinetics.

The figure compares stationary resource shares and the finite-budget channel
limit. It contains no simulated observations or empirical data. The only display
transforms are extracting covariance diagonals and subtracting the fixed equal
log-bin resource share, one third, from the retained means.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / "results/whole-object-assembly-2026-10-31"


def render(prediction, output_directory):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    retained = json.loads(prediction.read_text())
    cases = {row["name"]: row for row in retained["cases"]}
    budgets = np.array([row["budget"] for row in retained["asymptotic_channel"]])
    means = np.array([row["mean_shares"] for row in retained["asymptotic_channel"]])
    variances = np.array([np.diag(row["share_covariance"])
                          for row in retained["asymptotic_channel"]])
    if (means.shape != (len(budgets), 3) or variances.shape != means.shape
            or not np.all(np.diff(budgets) > 0)):
        raise ValueError("Expected ordered three-class asymptotic forecasts")
    if not np.allclose(means[:, 0], means[:, 1], rtol=0., atol=1e-14):
        raise ValueError("Combined class-1/class-2 mean label no longer applies")
    if not np.allclose(variances[:, 0], variances[:, 1], rtol=0., atol=1e-14):
        raise ValueError("Combined class-1/class-2 variance label no longer applies")

    blue, pale_blue = "#285f9b", "#8bb4dc"
    orange, pale_orange = "#b9532e", "#e9b194"
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 9,
        "axes.titlesize": 10, "axes.labelsize": 9,
        "xtick.labelsize": 8.5, "ytick.labelsize": 8.5,
        "legend.fontsize": 8, "svg.fonttype": "none",
        "svg.hashsalt": "whole-object-assembly-2026-10-31",
    })
    fig = plt.figure(figsize=(7.4, 6.6), layout="constrained")
    grid = fig.add_gridspec(2, 2, height_ratios=(1.15, 1.))
    top = fig.add_subplot(grid[0, :])
    lower = [fig.add_subplot(grid[1, i]) for i in range(2)]
    x = np.arange(3, dtype=float)
    width = .18
    series = [
        ("channel_baseline", "Channels: baseline", blue, ""),
        ("channel_bias", "Channels: association ×2", pale_blue, "//"),
        ("mass_action_baseline", "Mass action: baseline", orange, ""),
        ("mass_action_bias", "Mass action: association ×2", pale_orange, "//"),
    ]
    for index, (key, label, color, hatch) in enumerate(series):
        top.bar(x + (index - 1.5)*width,
                cases[key]["stationary_mean_shares"], width=width,
                label=label, color=color, edgecolor="white", linewidth=.65,
                hatch=hatch, zorder=3)
    top.axhline(1/3, color="#444444", linestyle="--", linewidth=1.2,
                label="Equal resource per log bin", zorder=4)
    top.set(xticks=x, xticklabels=["1", "2", "4"],
            xlabel="Object mass (monomer units)", ylabel="Expected fraction of total mass",
            ylim=(0, .93),
            title=f"a  Same budget, different kinetics (B = {retained['budget']})")
    top.legend(loc="upper left", ncol=2, frameon=False,
               columnspacing=1.6, handlelength=1.7)
    top.text(.01, .52, "Association ×2 changes only\nthe dimer-to-tetramer forward rate.",
             transform=top.transAxes, fontsize=8, color="#444444", va="top")

    classes = [(0, "Mass classes 1 and 2", blue, "o", "-"),
               (2, "Mass class 4", orange, "D", "--")]
    for column, label, color, marker, line in classes:
        lower[0].plot(budgets, means[:, column] - 1/3, color=color,
                      marker=marker, markersize=4, linestyle=line,
                      linewidth=1.5, label=label)
        lower[1].plot(budgets, variances[:, column], color=color,
                      marker=marker, markersize=4, linestyle=line,
                      linewidth=1.5, label=label)
    lower[0].axhline(0, color="#444444", linestyle=":", linewidth=1.1)
    lower[0].set(title="b  Channel means approach equality",
                 xlabel="Total mass budget B", ylabel="Mean mass share − 1/3",
                 ylim=(-.095, .063))
    lower[0].legend(loc="lower right", frameon=False, handlelength=1.8)

    limiting_variance = retained["limiting_share_covariance"][0][0]
    lower[1].axhline(limiting_variance, color="#444444", linestyle=":", linewidth=1.2,
                     label="Limit = 1/18")
    lower[1].set(title="c  Channel snapshots retain variance",
                 xlabel="Total mass budget B", ylabel="Variance of mass share",
                 ylim=(0, .205))
    lower[1].legend(loc="upper right", frameon=False, handlelength=1.8)
    for ax in lower:
        ax.set_xscale("log", base=2)
        ax.set_xticks([4, 12, 48, 192], labels=["4", "12", "48", "192"])
    for ax in [top, *lower]:
        ax.spines[["top", "right"]].set_visible(False)
        ax.set_axisbelow(True)
        ax.grid(axis="y", color="#d9d9d9", linewidth=.6)
    fig.supxlabel("Analytic stationary predictions; log-orthopolic comparison in physical object mass",
                  fontsize=8, color="#444444")
    output_directory.mkdir(parents=True, exist_ok=True)
    png = output_directory / "whole-object-assembly.png"
    svg = output_directory / "whole-object-assembly.svg"
    fig.savefig(png, dpi=260, bbox_inches="tight", pad_inches=.06,
                metadata={"Software": "orthopolity whole-object analytic presentation"})
    fig.savefig(svg, bbox_inches="tight", pad_inches=.06, metadata={"Date": None})
    plt.close(fig)
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines()) + "\n")
    print(json.dumps({"kind": "presentation_of_retained_analytic_forecasts",
                      "prediction_sha256": hashlib.sha256(prediction.read_bytes()).hexdigest(),
                      "artifacts": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                    for p in (png, svg)},
                      "simulation_rerun": False}, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prediction", type=Path, default=DEFAULT / "predictions.json")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT)
    args = parser.parse_args()
    render(args.prediction.resolve(), args.output_dir.resolve())
