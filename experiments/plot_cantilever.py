"""Plot sealed cantilever forecasts and outcomes; never fit or read source MAT data.

Only the retained primary result is read. Invalid local-loss models retain their
raw algebraic forecasts in the upper panels and an explicit failure column below.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "results/cantilever-transfer-2026-10-13/result.json"
OUTPUT = RESULT.with_name("cantilever-presentation.png")
COLORS = {"F1": "#0072B2", "F2": "#D89000", "F3": "#C43B3B",
          "F4": "#008567", "F5": "#9951A0", "T1": "#30343B"}


def label(case):
    return ("F" if case["kind"] == "flexural" else "T") + str(case["mode"])


def plot(result_path=RESULT, output_path=OUTPUT):
    body = Path(result_path).read_bytes()
    result = json.loads(body)
    analyses = [a for a in result["analyses"] if a["name"] == "primary"]
    if len(analyses) != 1:
        raise ValueError("Expected exactly one retained primary analysis")
    primary = analyses[0]
    if primary["all_phi"] or primary["publisher_mask"]:
        raise ValueError("Expected the primary withheld-condition, unmasked result")
    cases = primary["cases"]
    if {c["sample"] for c in cases} != {"C30", "C30C"}:
        raise ValueError("Unexpected preparation inventory")
    ordered = sorted(cases, key=lambda c: (c["sample"], c["kind"] != "flexural", c["mode"]))
    t0 = primary["t0_K"]
    summary = primary["summary"]

    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 10,
        "axes.titlesize": 12, "axes.labelsize": 10,
        "xtick.labelsize": 9, "ytick.labelsize": 9,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.edgecolor": "#64666A", "axes.linewidth": .7,
        "grid.color": "#DBDEE3", "grid.linewidth": .6,
        "savefig.facecolor": "white",
    })
    fig = plt.figure(figsize=(10.8, 7.8))
    grid = fig.add_gridspec(2, 2, height_ratios=(1.6, 1), hspace=.48, wspace=.20,
                           left=.085, right=.98, bottom=.185, top=.87)
    panels = [fig.add_subplot(grid[0, i]) for i in range(2)]
    errors = fig.add_subplot(grid[1, :])

    all_rows = [r for c in cases for r in c["rows"]]
    lower = min(r["observed_temperature_K"] - r["observed_temperature_error_K"] for r in all_rows)
    upper = max(max(r["observed_temperature_K"] + r["observed_temperature_error_K"],
                    r["tmax_model_K"]) for r in all_rows)
    y_limits = (50 * np.floor((lower - 15) / 50), 50 * np.ceil((upper + 25) / 50))

    for ax, sample, letter in zip(panels, ("C30", "C30C"), ("a", "b")):
        group = [c for c in ordered if c["sample"] == sample]
        rows = group[0]["rows"]
        temperatures = np.array([r["tavg_K"] for r in rows])
        pad = max(3., .09 * np.ptp(temperatures))
        x_limits = (temperatures.min() - pad, temperatures.max() + pad)
        xx = np.linspace(*x_limits, 100)
        ax.fill_between(xx, t0, 2 * xx - t0, color="#F0F2F4", zorder=0)
        ax.plot(xx, 2 * xx - t0, color="#B6BCC4", lw=.8, zorder=1)
        ax.axhline(t0, color="#B6BCC4", lw=.8, zorder=1)
        handles = []
        for case in group:
            name = label(case)
            color = COLORS[name]
            valid = case["fit"]["admissible"]
            rr = sorted(case["rows"], key=lambda row: row["tavg_K"])
            x = [r["tavg_K"] for r in rr]
            observed = [r["observed_temperature_K"] for r in rr]
            sigma = [r["observed_temperature_error_K"] for r in rr]
            ax.errorbar(x, observed, yerr=sigma, fmt="o", ms=4.7, color=color,
                        ecolor=color, alpha=.82, elinewidth=.85, capsize=2,
                        markeredgecolor="white", markeredgewidth=.5, zorder=3)
            predicted = [r.get("temperature_prediction_K") for r in rr]
            if all(value is not None for value in predicted):
                ax.plot(x, predicted, color=color, lw=1.7, ls="-" if valid else "--",
                        marker=None if valid else "D", ms=5, mfc="white", mew=1.1,
                        zorder=4)
            handles.append(Line2D([], [], color=color, lw=1.7,
                                  ls="-" if valid else "--", label=name if valid else name + "†"))
        ax.set(xlim=x_limits, ylim=y_limits,
               xlabel=r"Mean physical temperature $T_{\rm avg}$ (K)")
        ax.set_title(f"({letter})  {sample}", loc="left", weight="bold", pad=8)
        ax.grid(axis="y", zorder=0)
        ax.legend(handles=handles, loc="upper left", ncol=3, frameon=False,
                  fontsize=9, handlelength=1.6, columnspacing=1.15, borderaxespad=.5)
        if sample == "C30":
            ax.set_ylabel(r"Fluctuation temperature $T_{\rm fluc}$ (K)")
        else:
            ax.tick_params(labelleft=False)
        if any(not c["fit"]["admissible"] for c in group):
            ax.text(.97, .96, "† F4: invalid local loss\nDashed line is raw algebra",
                    transform=ax.transAxes, ha="right", va="top", fontsize=8.7,
                    color="#4A4E55", linespacing=1.35)

    x_positions = np.arange(len(ordered))
    uniform_maes = []
    qualified_maes = []
    for index, case in enumerate(ordered):
        rows = case["rows"]
        # These absolute errors are retained result fields, not recomputed models.
        comparator = float(np.mean([r["uniform_local_loss_all_targets_error_K"] for r in rows]))
        uniform_maes.append(comparator)
        model = case["temperature_mae_K"]
        if case["fit"]["admissible"] and model is not None:
            qualified_maes.append(model)
            errors.plot([index-.12, index+.12], [model, comparator], color="#B3BBC5", lw=1.1,
                        zorder=1)
            errors.plot(index-.12, model, "o", color="#173C63", ms=6, zorder=3)
        else:
            errors.axvspan(index-.40, index+.40, facecolor="#FAEAEA", alpha=.8,
                           hatch="///", edgecolor="#E4C9C9", lw=0, zorder=0)
            errors.text(index, 130., "Invalid\nlocal loss", rotation=90,
                        ha="center", va="center", color="#923F3F", fontsize=9)
        errors.plot(index+.12, comparator, "s", color="#7C8795", mfc="white", mew=1.2,
                    ms=5.5, zorder=3)

    split_at = sum(c["sample"] == "C30" for c in ordered) - .5
    errors.axvline(split_at, color="#AEB5BD", lw=.8, ls="--")
    errors.set_xlim(-.6, len(ordered)-.4)
    errors.set_ylim(0, 1.15 * max(uniform_maes + qualified_maes))
    errors.set_xticks(x_positions, [label(case) + ("†" if not case["fit"]["admissible"] else "")
                                  for case in ordered])
    errors.set_ylabel("Mean absolute error (K)")
    errors.set_title("(c)  Heldout errors by mode", loc="left", weight="bold", pad=10)
    errors.grid(axis="y", zorder=0)
    errors.legend(handles=[
        Line2D([], [], marker="o", ls="", color="#173C63", ms=6, label="Damping-based forecast"),
        Line2D([], [], marker="s", ls="", color="#7C8795", mfc="white", mew=1.2, ms=5.5,
               label="Uniform local loss")], loc="upper right", frameon=False,
        fontsize=9.2, ncol=2, columnspacing=1.5)
    for sample in ("C30", "C30C"):
        indices = [i for i, c in enumerate(ordered) if c["sample"] == sample]
        midpoint = (indices[0] + indices[-1]) / 2
        errors.text(midpoint, -.24, sample, transform=errors.get_xaxis_transform(),
                    ha="center", va="top", fontsize=10, weight="bold")

    fig.suptitle("Thermal-noise forecasts from cooler-condition damping", x=.085, y=.975,
                 ha="left", fontsize=15, weight="bold")
    fig.text(.085, .934, "Frozen hot-condition test: C30, 8 calibration → 3 target conditions; "
             "C30C, 5 → 2.", fontsize=10.3, color="#404750")
    fig.text(.085, .902, "Points: measurements with reported uncertainties. Lines: sealed forecasts. "
             "Shading: positive-loss temperature bounds.", fontsize=9.1, color="#535C66")
    scores = summary["scores"]
    mae = scores["absolute_error_K"]["equal_preparation_mean"]
    uniform = scores["uniform_local_loss_absolute_error_K"]["equal_preparation_mean"]
    fig.text(.085, .070,
             f"Admissible subset: {summary['admissible_modes']}/{summary['attempted_modes']} modes, "
             f"{summary['qualified_temperature_targets']}/{summary['attempted_targets']} targets. "
             f"Equal-preparation MAE: {mae:.1f} K; uniform local loss: {uniform:.1f} K on the same targets.",
             fontsize=9.1, color="#303842")
    fig.text(.085, .044,
             "F = flexural; T = torsional. † C30C F4 is a physical-model failure, retained and excluded from qualified error scores.",
             fontsize=8.5, color="#59616B")
    fig.text(.085, .022, "Error bars are not independent confidence intervals.",
             fontsize=8.5, color="#59616B")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=240, metadata={
        "Software": "orthopolity experiments/plot_cantilever.py",
        "Description": "Primary frozen cantilever study; retained result SHA256 "
                       + hashlib.sha256(body).hexdigest(),
    })
    plt.close(fig)
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result", type=Path, default=RESULT)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    print(plot(args.result, args.output))
