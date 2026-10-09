"""Freeze and replay a retrospective birth-to-population summary comparison."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import scipy

from orthopolity.cell_division import density, summary_predictions

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/cell_division_2026-10-08.json"
BASE = ROOT / "data/cell-division/2026-10-08"


def checksum(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


def predictions(config):
    result = {}
    for medium, row in config["calibration"].items():
        mean, variance = row["birth_mean"], row["birth_variance"]
        result[medium] = {
            "birth_population": summary_predictions(mean, variance),
            "birth_lineage": summary_predictions(mean, variance, "lineage"),
            "fixed_birth_population": summary_predictions(mean, 0),
            "division_population": summary_predictions(row["division_mean"] / 2, row["division_variance"] / 4),
        }
    return result


def verify(freeze):
    for name, sha in freeze["files"].items():
        if checksum(ROOT / name) != sha:
            raise ValueError("Changed frozen file: " + name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=["freeze", "evaluate"], required=True)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/cell-division")
    args = parser.parse_args()
    config = json.loads(CONFIG.read_text())
    forecast = predictions(config)
    freeze_path = BASE / "freeze.json"
    if args.stage == "freeze":
        if freeze_path.exists():
            verify(json.loads(freeze_path.read_text()))
            print("Existing freeze verified; unchanged")
            return
        if (BASE / "figure1.jpg").exists() or (BASE / "targets.json").exists():
            raise ValueError("Target already acquired: cannot create the declared freeze")
        write_json(BASE / "predictions.json", forecast)
        names = [CONFIG, ROOT / "docs/cell-division-protocol.md", Path(__file__),
                 ROOT / "src/orthopolity/cell_division.py", ROOT / "tests/test_cell_division.py",
                 ROOT / "experiments/fetch_cell_division.py", BASE / "predictions.json"]
        names += [p for p in BASE.iterdir() if p.is_file() and p not in names]
        write_json(freeze_path, dict(run_id=config["run_id"],
            frozen_at_utc=datetime.now(timezone.utc).isoformat(),
            exposure=config["exposure"],
            files={p.relative_to(ROOT).as_posix(): checksum(p) for p in sorted(set(names))}))
        print(json.dumps(forecast, indent=2))
        return

    freeze = json.loads(freeze_path.read_text())
    verify(freeze)
    if forecast != json.loads((BASE / "predictions.json").read_text()):
        raise ValueError("Predictions do not reproduce")
    receipt = json.loads((BASE / "figure1.jpg.receipt.json").read_text())
    if checksum(BASE / "figure1.jpg") != receipt["sha256"]:
        raise ValueError("Target image changed")
    if datetime.fromisoformat(receipt["retrieval_started_utc"]) <= datetime.fromisoformat(freeze["frozen_at_utc"]):
        raise ValueError("Target retrieval predates freeze")
    targets = json.loads((BASE / "targets.json").read_text())
    if targets["source_sha256"] != receipt["sha256"]:
        raise ValueError("Transcription source mismatch")
    scores, diagnostics, observed, decisions = {}, {}, {}, {}
    for medium, row in config["calibration"].items():
        target = targets["measurements"][medium]
        observed[medium] = dict(mean=target["mean"], cv=np.sqrt(target["variance"]) / target["mean"])
        scores[medium] = {name: {endpoint: float(abs(np.log(value[endpoint] / observed[medium][endpoint])))
                               for endpoint in config["endpoints"]}
                          for name, value in forecast[medium].items()}
        diagnostics[medium] = dict(
            division_to_twice_birth_mean=row["division_mean"] / (2 * row["birth_mean"]),
            division_to_birth_cv=(np.sqrt(row["division_variance"]) / row["division_mean"]) /
                                 (np.sqrt(row["birth_variance"]) / row["birth_mean"]))
        decisions[medium] = all(scores[medium]["birth_population"][e] < scores[medium]["birth_lineage"][e]
                                for e in config["endpoints"])
    summary = dict(run_id=config["run_id"], exposure=config["exposure"],
                   predictions=forecast, observed=observed, scores=scores,
                   calibration_diagnostics=diagnostics,
                   population_improves_both_endpoints_over_lineage=decisions,
                   uncertainty="No sampling uncertainty estimated from rounded fitted moments; no significance test",
                   empirical_scope="Published lognormal summaries of cell length; independent experimental settings, not independently measured biomass or verified common growth")
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    write_json(out / "summary.json", summary)
    write_json(out / "config.json", config)
    fig, axes = plt.subplots(2, 2, figsize=(9, 6), layout="constrained")
    labels = ["Population", "Lineage", "Fixed birth", "Division / 2"]
    colors = ["#0072B2", "#D55E00", "#777777", "#009E73"]
    for col, medium in enumerate(config["calibration"]):
        row = config["calibration"][medium]
        x = np.geomspace(.5, 12, 800)
        ax = axes[0, col]
        for sampling, color, label in [("population", colors[0], "Population forecast"),
                                       ("lineage", colors[1], "Lineage comparator")]:
            ax.plot(x, density(x, row["birth_mean"], row["birth_variance"], sampling),
                    color=color, label=label)
        ax.set(title=medium + ": predicted profiles", xlabel="Cell length proxy (µm)", ylabel="Probability density (µm⁻¹)", xlim=(.5, 8))
        ax.legend(fontsize=8)
        ax = axes[1, col]
        for i, name in enumerate(config["models"]):
            vals = [forecast[medium][name][e] / observed[medium][e] for e in config["endpoints"]]
            ax.plot([0 + (i - 1.5) * .07, 1 + (i - 1.5) * .07], vals, "o", color=colors[i], label=labels[i])
        ax.axhline(1, color="black", lw=1)
        ax.set(xticks=[0, 1], xticklabels=["Mean", "CV"], ylabel="Predicted / published", ylim=(.5, 1.8))
        ax.legend(fontsize=8, ncols=2)
    fig.savefig(out / "cell-division.png", dpi=180, metadata={"Software": "orthopolity cell-division-summary"})
    fig.savefig(out / "cell-division.pdf", metadata={"CreationDate": None, "ModDate": None})
    plt.close(fig)
    provenance = dict(run_id=config["run_id"], python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__,
                      freeze_sha256=checksum(freeze_path), frozen_files=freeze["files"],
                      source_hashes={p.relative_to(ROOT).as_posix(): checksum(p) for p in sorted(BASE.iterdir()) if p.is_file()},
                      outputs={p.name: checksum(p) for p in sorted(out.iterdir()) if p.is_file() and p.name != "provenance.json"})
    write_json(out / "provenance.json", provenance)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
