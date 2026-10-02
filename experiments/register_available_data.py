"""Register completed available-data studies without rerunning or collecting observations.

Each study retains a frozen plan, an evaluation report and its acquisition
directory. Registration checks the report against that plan, archives the
frozen analysis sources and configuration, and appends one registry entry.
This assembler computes no result, so it is not archived as an analysis
source; adding a later study here leaves earlier entries reproducible.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from orthopolity.run_registry import (
    archive_reference, file_reference, register_run, verify_registry,
)


ROOT = Path(__file__).resolve().parents[1]


def cost_summary(result):
    return {resource: {"eligible_validation_cultures": score["eligible_validation_rows"],
                       "strain_temperature_cells": score["observed_cells"],
                       "ranking_by_primary_error": score["ranking_by_primary_error"],
                       "equal_cell_mean_absolute_log_error": {
                           model: summary["equal_cell_mean_absolute_log_error"]
                           for model, summary in score["models"].items()}}
            for resource, score in result["scores"].items()}


STUDIES = {
    "archived-cost-transfer": {
        "config": "configs/archived_cost_transfer_2026-10-02.json",
        "data": "data/archived-cost-transfer/2026-10-02",
        "results": "results/archived-cost-transfer",
        "kind": "actual_measurement",
        "resources": [
            {"name": f"Cellular {element} quota",
             "definition": f"{code}: published bulk {element} assay divided by flow-cytometric cell count in nutrient-replete Synechococcus batch culture; a retained stock, not an uptake flux or construction requirement",
             "units": f"fmol {symbol} per cell"}
            for element, code, symbol in [("carbon", "QC", "C"), ("nitrogen", "QN", "N"), ("phosphorus", "QP", "P")]],
        "algorithm": "Frozen diameter-conditional and strain-specific log-quota forecasts for whole held-out warmer cultures",
        "seeds": {"status": "Deterministic least-squares analysis; no random seed"},
        "summary": cost_summary,
        "parents": [],
    },
}


def checked_reference(reference):
    actual = file_reference(ROOT, reference["path"])
    if actual["sha256"] != reference["sha256"]:
        raise ValueError(f"Frozen bytes changed: {reference['path']}")
    return reference


def retained_files(directory):
    return [file_reference(ROOT, path.relative_to(ROOT).as_posix())
            for path in sorted(directory.rglob("*"))
            if path.is_file() and path.name not in {"registry-entry.json", ".DS_Store"}]


def register_study(name):
    specification = STUDIES[name]
    directory, output = ROOT / specification["data"], ROOT / specification["results"]
    plan = json.loads((directory / "frozen-plan.json").read_text())
    result = json.loads((output / "study.json").read_text())
    plan_reference = file_reference(ROOT, (directory / "frozen-plan.json").relative_to(ROOT).as_posix())
    if checked_reference(result["frozen_plan"])["sha256"] != plan_reference["sha256"]:
        raise ValueError("Result belongs to a different frozen plan")
    if result["run_id"] != plan["run_id"] or result.get("status") != "complete":
        raise ValueError("Only a complete report of the frozen run can be registered")
    config = archive_reference(ROOT, specification["config"])
    if config["sha256"] != checked_reference(plan["config_reference"])["sha256"]:
        raise ValueError("Configuration differs from freeze")
    sources = []
    for reference in plan["source_references"]:
        snapshot = archive_reference(ROOT, checked_reference(reference)["path"])
        if snapshot["sha256"] != reference["sha256"]:
            raise ValueError("Source archive differs from the frozen source")
        sources.append(snapshot)
    entry = {
        "schema_version": 1, "run_id": plan["run_id"], "evidence_kind": specification["kind"],
        "resources": specification["resources"],
        "data_inputs": retained_files(directory),
        "generated_seeds": specification["seeds"],
        "algorithms": [{"name": specification["algorithm"], "sources": sources,
                        "source_provenance": "Digests equal the sources recorded in the frozen plan before acquisition/evaluation"}],
        "configs": [config], "artifacts": retained_files(output),
        "relationships": [{"run_id": run_id, "type": relationship}
                          for run_id, relationship in specification["parents"]],
        "hardware_metadata": {"recorded_environment": plan.get("environment", {}),
                              "scope": "Software environment recorded by the frozen plan; no additional host facts probed"},
        "summary": {"interpretation": result["interpretation"],
                    "statistical_scope": result["statistical_scope"],
                    "results": specification["summary"](result),
                    "report": (output / "study.json").relative_to(ROOT).as_posix(),
                    "registration_scope": "Retrospective analysis of existing public measurements; zero new observations"},
    }
    path = directory / "registry-entry.json"
    encoded = json.dumps(entry, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    if path.exists() and path.read_text() != encoded:
        raise ValueError("Retained registration differs; use a new run identifier")
    registered = register_run(ROOT, entry)
    if not path.exists():
        path.write_text(encoded)
    return registered


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study", choices=list(STUDIES))
    arguments = parser.parse_args()
    names = [arguments.study] if arguments.study else list(STUDIES)
    print(json.dumps([register_study(name) for name in names], indent=2))
    print(json.dumps(verify_registry(ROOT), indent=2))


if __name__ == "__main__":
    main()
