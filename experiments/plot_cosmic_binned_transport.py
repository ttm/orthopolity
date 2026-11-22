"""Plot fixed-bin endpoint-current diagnostics without selecting a mass interval.

The figure shows log-orthopolic collisionless total-matter development
diagnostics. Endpoint-conditioned currents do not establish physical closure.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import numpy as np


PAIRS = ("97->98", "98->99", "97->99")
SERIES = (
    ("current_direct_cell_average", "Endpoint current: cell average", "#202020", "-", 1.9),
    ("current_departure", "Drift placed in departure bin", "#0072B2", "--", 1.6),
    ("current_midpoint", "Moment placed in midpoint bin", "#D55E00", ":", 1.9),
)
DESCRIPTION = (
    "Log-orthopolic collisionless total-matter development diagnostics. "
    "Only particles hosted at both endpoints contribute to these currents; "
    "diffuse exchange is separate. The figure does not establish physical "
    "local closure or an independent abundance prediction."
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_plot_data(path):
    result = json.loads(path.read_text())
    if (result.get("outcome") != "development_accounting_passed"
            or result.get("development_only") is not True
            or result.get("log_orthopolic_transport_validated") is not False):
        raise ValueError("Expected passed development accounting with unqualified transport")
    primary = result["grids"]["primary"]
    edges = np.asarray(primary["log2_edges"], dtype=float)
    # This figure belongs to the fixed primary grid, not an adaptive selection.
    if not np.array_equal(edges, np.arange(27, dtype=float)):
        raise ValueError("Expected the complete fixed primary grid from zero through 26")
    pairs = []
    for name in PAIRS:
        pair = primary["pairs"][name]
        interval = float(pair["interval_gyr"])
        if not np.isfinite(interval) or interval <= 0:
            raise ValueError("Invalid interval duration")
        values = {}
        for key, *_ in SERIES:
            array = np.asarray(pair["positive_bins"][key], dtype=float)
            if array.shape != (26,) or not np.all(np.isfinite(array)):
                raise ValueError("Invalid or incomplete current array")
            values[key] = array
        pairs.append((name, interval, values))
    return edges, pairs


def render(input_path, output_directory):
    edges, pairs = read_plot_data(input_path)
    output_directory.mkdir(parents=True, exist_ok=False)
    with plt.rc_context({
        "font.family": "DejaVu Sans", "font.size": 10,
        "axes.spines.top": False, "axes.spines.right": False,
        "svg.hashsalt": "orthopolity-cosmic-binned-transport-primary-v1",
        "savefig.facecolor": "white", "figure.facecolor": "white",
    }):
        fig, axes = plt.subplots(3, 1, figsize=(11.2, 9.1), sharex=True, sharey=True)
        handles = []
        for index, (ax, (name, interval, values)) in enumerate(zip(axes, pairs)):
            ax.axhline(0, color="#9B9B9B", lw=.7, zorder=1)
            for key, label, color, style, width in SERIES:
                handle = ax.stairs(values[key], edges, baseline=None,
                                   color=color, linestyle=style, linewidth=width,
                                   label=label, zorder=3)
                if index == 0:
                    handles.append(handle)
            ax.set_title(f"({chr(97 + index)})  {name.replace('->', ' → ')}"
                         f"     Δt = {interval:.6f} Gyr", loc="right", fontsize=10.5)
            ax.set_ylabel("Current\n" + r"[$M_\odot\,\mathrm{Mpc}^{-3}\,\mathrm{Gyr}^{-1}$]")
            ax.grid(axis="y", alpha=.16, linewidth=.65)
            formatter = ScalarFormatter(useMathText=True)
            formatter.set_powerlimits((0, 0))
            ax.yaxis.set_major_formatter(formatter)
            ax.set_xlim(edges[0], edges[-1])
            ax.margins(y=.13)
        axes[-1].set_xticks([0, 4, 8, 12, 16, 20, 24, 26])
        axes[-1].set_xlabel(r"Host mass / particle mass: $\log_2(M/m_p)=\log_2 N_{\rm host}$")
        fig.suptitle("Endpoint current and two localization approximations", y=.98, fontsize=15)
        fig.text(.5, .945,
                 "TNG50-4-Dark · Primary log-mass bins · Log-orthopolic total-matter candidate",
                 ha="center", fontsize=10, color="#444444")
        fig.legend(handles, [series[1] for series in SERIES], loc="upper center",
                   bbox_to_anchor=(.5, .927), frameon=False, ncol=3, fontsize=9)
        fig.text(.5, .027,
                 "Only particles hosted at both endpoints contribute; diffuse exchange is separate.\n"
                 "Development diagnostics: physical local closure and an independent prediction remain unqualified.",
                 ha="center", fontsize=9, color="#444444")
        fig.subplots_adjust(top=.855, bottom=.105, left=.105, right=.975, hspace=.37)
        stem = output_directory / "endpoint-current-primary"
        png, svg = stem.with_suffix(".png"), stem.with_suffix(".svg")
        fig.savefig(png, dpi=180, metadata={"Software": "orthopolity", "Description": DESCRIPTION})
        fig.savefig(svg, metadata={"Date": None, "Creator": "orthopolity", "Description": DESCRIPTION})
        plt.close(fig)
        # Matplotlib leaves spaces at the ends of multiline path coordinates.
        svg.write_bytes(b'\n'.join(line.rstrip() for line in svg.read_bytes().splitlines()) + b'\n')
    receipt = {
        "kind": "Fixed-domain development-current figure",
        "input_sha256": digest(input_path),
        "plot_source_sha256": digest(Path(__file__)),
        "grid": "primary", "pairs": list(PAIRS),
        "development_only": True, "log_orthopolic_transport_validated": False,
        "matplotlib_version": matplotlib.__version__, "numpy_version": np.__version__,
        "artifacts": {path.name: digest(path) for path in (png, svg)},
    }
    (output_directory / "figure-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    receipt = render(args.input, args.output_dir)
    print(json.dumps({"artifacts": list(receipt["artifacts"]), "grid": receipt["grid"]}))


if __name__ == "__main__":
    main()
