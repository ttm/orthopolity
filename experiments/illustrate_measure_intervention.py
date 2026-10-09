"""Deterministic worked examples of two reference-measure postulates.

No outcome data, fitting, random samples, acquisition or registry writes.
"""
from __future__ import annotations

import argparse
import json
import math

from orthopolity.measure_intervention import measure_forecasts


def examples():
    parameters = dict(edges=[1.0, math.sqrt(10.0), 10.0], degree=2.0,
                      budget=1000.0, cost_scale=1.0, size_scale=1.0)
    return {
        "kind": "deterministic mathematical examples; no empirical observations",
        "parameters": parameters,
        "cases": [dict(overhead=c, forecasts=measure_forecasts(**parameters, overhead=c))
                  for c in [0.0, 10.0, 1000.0]],
    }


def markdown_table(result):
    lines = [
        "| Overhead c | Small-bin resource S / Q | Small-bin counts S / Q | Total expected count S / Q |",
        "|---|---|---|---|",
    ]
    for case in result["cases"]:
        s, q = (case["forecasts"][key] for key in ["log_size", "log_cost"])
        lines.append(
            f'| {case["overhead"]:g} | '
            f'{s["resource_shares"][0]:.2%} / {q["resource_shares"][0]:.2%} | '
            f'{s["count_shares"][0]:.2%} / {q["count_shares"][0]:.2%} | '
            f'{s["total_count"]:.3f} / {q["total_count"]:.3f} |'
        )
    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = parser.parse_args()
    result = examples()
    print(markdown_table(result) if args.format == "markdown" else
          json.dumps(result, indent=2, allow_nan=False))
