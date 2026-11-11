"""Render an exact finite log-orthopolic example, without empirical inputs.

The four equally weighted classes lie on a logarithmic size grid. Each object
in class j has cost q_j = k_j. The figure illustrates a prescribed allocation;
it is not a simulation, a fitted distribution, or evidence of its occurrence.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


SIZES = (1, 2, 4, 8)
COUNTS = (8, 4, 2, 1)
RESOURCE_PER_CLASS = 8
TOTAL_RESOURCE = 32


def render(output_dir: Path) -> None:
    """Save a deterministic PNG and SVG of the integer allocation."""
    costs = SIZES
    class_resources = tuple(n * q for n, q in zip(COUNTS, costs))
    assert class_resources == (RESOURCE_PER_CLASS,) * len(SIZES)
    assert sum(class_resources) == TOTAL_RESOURCE
    assert all(b == 2 * a for a, b in zip(SIZES, SIZES[1:]))

    style = {
        "font.family": "DejaVu Sans",
        "font.size": 11,
        "axes.labelsize": 11,
        "svg.hashsalt": "orthopolity-explanation-2026-11-10",
        "svg.fonttype": "none",
        "text.color": "#24333e",
        "axes.labelcolor": "#24333e",
        "xtick.color": "#24333e",
        "ytick.color": "#24333e",
    }
    with plt.rc_context(style):
        fig, ax = plt.subplots(figsize=(7.4, 4.8))
        fig.subplots_adjust(left=0.105, right=0.97, bottom=0.24, top=0.76)
        fig.text(0.105, 0.94, "More resource per object, fewer objects",
                 fontsize=15, weight="bold", va="top")
        fig.text(0.105, 0.865,
                 "A finite log-orthopolic grid: four equally weighted size classes",
                 fontsize=10.5, va="top")

        for x, (size, count, cost) in enumerate(zip(SIZES, COUNTS, costs)):
            for index in range(count):
                # All blocks have equal width; their height and area encode cost.
                ax.add_patch(Rectangle((x - 0.32, index * cost), 0.64, cost,
                                       facecolor="#c4dfe9", edgecolor="#294d60",
                                       linewidth=1.15, zorder=3))
                ax.text(x, (index + 0.5) * cost, str(cost),
                        ha="center", va="center", fontsize=11, zorder=4)
            label = f"{count} object" + ("s" if count != 1 else "")
            ax.text(x, RESOURCE_PER_CLASS + 0.32, label,
                    ha="center", va="bottom", fontsize=11, weight="bold")
            ax.text(x, -1.3, f"{count} × {cost} = {RESOURCE_PER_CLASS}",
                    ha="center", va="top", fontsize=12, weight="bold")

        ax.set_xlim(-0.65, 3.65)
        ax.set_ylim(0, 9.3)
        ax.set_xticks(range(len(SIZES)), [str(k) for k in SIZES])
        ax.tick_params(axis="x", length=0, pad=8)
        ax.set_yticks([0, 2, 4, 6, 8])
        ax.set_ylabel("Resource in each class")
        ax.set_axisbelow(True)
        ax.grid(axis="y", color="#dce2e5", linewidth=0.7)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.spines["bottom"].set_color("#87959e")
        ax.tick_params(axis="y", length=0)

        fig.text(0.105, 0.09,
                 "Tick labels: object size k.  Each outlined block: one object with resource q = k.",
                 fontsize=10)
        fig.text(0.105, 0.045,
                 "Count × resource per object = 8 in every class.  Total resource = 32.",
                 fontsize=10)
        output_dir.mkdir(parents=True, exist_ok=True)
        stem = output_dir / "orthopolity-explanation"
        fig.savefig(stem.with_suffix(".png"), dpi=240,
                    metadata={"Software": "orthopolity explanatory figure"})
        fig.savefig(stem.with_suffix(".svg"),
                    metadata={"Date": None, "Creator": "orthopolity explanatory figure"})
        # Matplotlib adds trailing spaces in path data; normalize source whitespace.
        svg_path = stem.with_suffix(".svg")
        svg_path.write_text("\n".join(line.rstrip() for line in
                                      svg_path.read_text(encoding="utf-8").splitlines())
                            + "\n", encoding="utf-8")
        plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path,
                        default=Path(__file__).resolve().parents[1] / "docs" / "figures")
    args = parser.parse_args()
    render(args.output_dir)
    print(json.dumps({
        "kind": "exact illustrative allocation; no empirical inputs",
        "measure": "four equally weighted classes on a logarithmic size grid",
        "sizes": SIZES,
        "costs": SIZES,
        "counts": COUNTS,
        "resource_per_class": RESOURCE_PER_CLASS,
        "total_resource": TOTAL_RESOURCE,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
