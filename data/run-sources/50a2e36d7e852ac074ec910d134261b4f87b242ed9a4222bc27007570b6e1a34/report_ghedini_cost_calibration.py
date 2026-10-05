"""Render retained calibration readings and fitted curves without refitting.

Only study.json, its frozen plan/config, the calibration JSON and the group
ledger are read. No workbook or community outcome is opened. Existing figures
are immutable: a rerun must produce exactly the same bytes.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "results/ghedini-cost-calibration"
RATE_UNIT = 1e-9
WEIGHTING_LABELS = {"equal_groups": "Equal group weights", "species_rms": "Species RMS weights"}
POWER, ADDITIVE, INK, RAW = "#2369a0", "#d96724", "#26333e", "#79838c"


def read_json(path):
    return json.loads(path.read_text())


def checked_json(reference):
    path = ROOT / reference["path"]
    if hashlib.sha256(path.read_bytes()).hexdigest() != reference["sha256"]:
        raise ValueError(f"Retained input changed: {reference['path']}")
    return read_json(path)


def inputs():
    study = read_json(OUTPUT / "study.json")
    plan = checked_json(study["frozen_plan"])
    config = checked_json(plan["config_reference"])
    rows = checked_json(plan["input_references"]["calibration_rows"])
    groups = checked_json(plan["input_references"]["group_ledger"])
    if study["run_id"] != plan["run_id"] or plan["run_id"] != config["run_id"]:
        raise ValueError("Retained calibration inputs identify different runs")
    if study["community_numerical_rows_read"]:
        raise ValueError("This presentation is scoped to the calibration-only study")
    source_rows = {row["source_row"] for row in rows}
    ledger_rows = [source for group in groups for source in group["source_rows"]]
    if source_rows != set(ledger_rows) or len(ledger_rows) != len(rows):
        raise ValueError("Raw readings and group memberships disagree")
    return study, config, rows, groups


def curve(fit, volumes, od):
    """Evaluate retained physical parameters; no optimization or curve choice."""
    return ((fit["A"] * (volumes / fit["size_reference_um3"])**fit["d"] + fit["C"])
            * (od / fit["od_reference"])**fit["beta"] / RATE_UNIT)


def render(study, config, rows, groups, weighting, plt):
    from matplotlib.lines import Line2D
    from matplotlib.ticker import FixedLocator, FuncFormatter

    ods = sorted({group["od"] for group in groups})
    if len(ods) != 4:
        raise ValueError("This retained presentation requires four declared OD levels")
    usable = [row for row in rows if row["oxygen_umol_per_min_per_cell"] is not None]
    fits = study["fits"][weighting]["full"]
    domain = config["diagnostic_domain_um3"]
    volumes = np.geomspace(*domain, 400)
    # Both files use the same scale, including every raw reading, every SD
    # endpoint and both weighting-specific fitted curves over the fixed domain.
    values = [row["oxygen_umol_per_min_per_cell"] / RATE_UNIT for row in usable]
    for group in groups:
        if group["mean_rate"] is not None:
            values.extend((group["mean_rate"] + sign * (group["sd_rate"] or 0.)) / RATE_UNIT
                          for sign in (-1, 1))
    for weighted in study["fits"].values():
        for fit in weighted["full"].values():
            for od in ods:
                values.extend(curve(fit, volumes, od))
    minimum, maximum = min(values), max(values)
    ylimits = (min(-.15, minimum * 1.3), max(.15, maximum * 1.3))

    figure, axes = plt.subplots(2, 2, figsize=(11.6, 8.6), sharex=True, sharey=True)
    figure.subplots_adjust(left=.105, right=.975, bottom=.17, top=.825, hspace=.26, wspace=.13)
    figure.suptitle(f"Ghedini monoculture calibration | {WEIGHTING_LABELS[weighting]}",
                     x=.105, y=.97, ha="left", fontsize=16, fontweight="bold", color=INK)
    figure.text(.105, .93, "Full calibration fits; cell volume is the recorded mean for each species.",
                fontsize=10.5, color="#53616e")
    handles = [Line2D([], [], color=RAW, marker="o", linestyle="none", markersize=4, alpha=.65,
                      label="Signed readings"),
               Line2D([], [], color=INK, marker="D", linestyle="none", markersize=5,
                      label="Mean ± sample SD"),
               Line2D([], [], color=POWER, linewidth=3, label="Power cost"),
               Line2D([], [], color=ADDITIVE, linewidth=2, linestyle="--", label="Additive cost")]
    figure.legend(handles=handles, loc="upper left", bbox_to_anchor=(.098, .906),
                  ncol=4, frameon=False, handlelength=2.7, columnspacing=2.2)

    def signed_tick(value, position):
        return f"{value:g}".replace("-", "−")

    for panel, (axis, od) in enumerate(zip(axes.flat, ods)):
        selected = [row for row in usable if row["optical_density"] == od]
        group_rows = sorted((group for group in groups if group["od"] == od),
                            key=lambda group: group["volume_um3"])
        axis.set_xscale("log")
        axis.set_yscale("symlog", linthresh=.1, linscale=.7)
        axis.set_xlim(domain[0] / 1.3, domain[1] * 1.3)
        axis.set_ylim(*ylimits)
        axis.xaxis.set_major_locator(FixedLocator([2, 10, 100, 700]))
        axis.xaxis.set_major_formatter(FuncFormatter(lambda value, position: f"{value:g}"))
        axis.yaxis.set_major_locator(FixedLocator([-100, -10, -1, -.1, 0, .1, 1, 10, 100]))
        axis.yaxis.set_major_formatter(FuncFormatter(signed_tick))
        axis.grid(axis="y", which="major", color="#e6eaed", linewidth=.65)
        axis.axhline(0, color="#aab4bc", linewidth=1., zorder=1)
        axis.scatter([row["volume_um3"] for row in selected],
                     [row["oxygen_umol_per_min_per_cell"] / RATE_UNIT for row in selected],
                     s=15, color=RAW, alpha=.55, linewidths=0, zorder=2)
        axis.plot(volumes, curve(fits["power"], volumes, od), color=POWER, linewidth=3.3, zorder=3)
        axis.plot(volumes, curve(fits["additive"], volumes, od), color=ADDITIVE,
                  linewidth=1.9, linestyle=(0, (5, 3)), zorder=4)
        for group in group_rows:
            if group["mean_rate"] is None:
                continue
            axis.errorbar(group["volume_um3"], group["mean_rate"] / RATE_UNIT,
                          yerr=None if group["sd_rate"] is None else group["sd_rate"] / RATE_UNIT,
                          fmt="D", markersize=4.7, color=INK, markerfacecolor="white",
                          markeredgewidth=1.1, elinewidth=1., capsize=3., capthick=1., zorder=5)
        axis.set_title(f"{chr(97+panel)}   OD₇₅₀ = {od:g}", loc="left", fontsize=11, fontweight="bold", pad=9)
        nonpositive = sum(row["oxygen_umol_per_min_per_cell"] <= 0 for row in selected)
        axis.text(.025, .95, f"{len(selected)} readings; {nonpositive} ≤ 0", transform=axis.transAxes,
                  va="top", fontsize=8.5, color="#53616e")

    figure.supxlabel("Recorded mean cell volume (µm³; logarithmic scale)", y=.103, fontsize=11)
    figure.supylabel("Respiration (10⁻⁹ µmol O₂ min⁻¹ cell⁻¹; signed symlog scale)", x=.024, fontsize=11)
    missing = len(rows) - len(usable)
    figure.text(.105, .058,
                f"All {len(usable)} usable signed readings shown; {missing} missing reading retained in the ledger. No jitter or clipping.",
                fontsize=8.8, color="#53616e")
    figure.text(.105, .033,
                "Bars describe reading variation, not standard errors. Repeated readings are not independent biological replicates.",
                fontsize=8.8, color="#53616e")
    buffer = io.BytesIO()
    figure.savefig(buffer, format="png", dpi=180, facecolor="white",
                   metadata={"Software": "orthopolity retained calibration report"})
    plt.close(figure)
    return buffer.getvalue()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true", help="Require existing PNGs and reproduce their exact bytes")
    args = parser.parse_args()
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcdefaults()
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9.5,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "axes.edgecolor": "#aab4bc", "axes.linewidth": .8,
                         "axes.labelcolor": INK, "text.color": INK,
                         "xtick.color": "#53616e", "ytick.color": "#53616e"})
    study, config, rows, groups = inputs()
    artifacts = []
    for weighting in WEIGHTING_LABELS:
        path = OUTPUT / f"calibration-{weighting.replace('_', '-')}.png"
        body = render(study, config, rows, groups, weighting, plt)
        if args.verify and not path.exists():
            raise ValueError(f"Missing retained figure: {path.relative_to(ROOT)}")
        if path.exists() and path.read_bytes() != body:
            raise ValueError(f"Refusing to change retained figure: {path.relative_to(ROOT)}")
        if not path.exists():
            path.write_bytes(body)
        artifacts.append(dict(path=str(path.relative_to(ROOT)), sha256=hashlib.sha256(body).hexdigest()))
    print(json.dumps(dict(artifacts=artifacts, matplotlib=matplotlib.__version__,
                          refitted=False, community_rows_read=False), indent=2))


if __name__ == "__main__":
    main()
