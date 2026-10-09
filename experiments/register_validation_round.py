"""Register the new validation round without collecting or rerunning observations."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from orthopolity.run_registry import (
    archive_reference, file_reference, register_run, verify_registry,
)


ROOT = Path(__file__).resolve().parents[1]
STUDIES = {
    "profile-calibration": {
        "config": "configs/profile_calibration_2026-10-02.json",
        "kind": "simulation",
        "resources": [{"name": "Simulated additive resource",
                       "definition": "Known-population bin resource totals generated under the archived observation laws; no physical measurements",
                       "units": "simulation resource units"}],
        "algorithm": "Complete-profile equivalence/departure decisions and outer repeated-sampling calibration",
        "parents": [("resource-identification-2026-10-01-final", "extends_decision_calibration")],
    },
    "solar-validation": {
        "config": "configs/solar_validation_2026-10-02.json",
        "kind": "actual_measurement",
        "resources": [{"name": "Rise-window XRS fluence",
                       "definition": "Supplied start-to-peak integrated irradiance at the observer without additional background subtraction; not total radiated flare energy",
                       "units": "J/m²"},
                      {"name": "End-window XRS fluence",
                       "definition": "Supplied start-to-end integrated irradiance; complete-case sensitivity with missingness retained",
                       "units": "J/m²"}],
        "algorithm": "Frozen measured-cost forecasts and gated complete-profile decisions on an unused solar year",
        "parents": [("solar-resource-transfer-2026-10-01", "new_observation_period"),
                    ("profile-calibration-2026-10-02", "uses_calibrated_decision_benchmark")],
    },
    "dimensionality-intervention": {
        "config": "configs/dimensionality_intervention_2026-10-02.json",
        "kind": "actual_measurement",
        "resources": [{"name": "Thread CPU time",
                       "definition": "Measured CPU seconds consumed by Python worker threads, including partial jobs and worker accounting; independently calibrated completed-job CPU cost is a separate estimator",
                       "units": "CPU seconds"}],
        "algorithm": "Independently calibrated non-unit workload costs and frozen allocation predictions under a runnable-opportunity restriction",
        "parents": [("workload-transfer-2026-10-01b", "new_allocation_and_dimension_measurement")],
    },
}


def checked_reference(reference):
    """Check a frozen digest, retaining its optional provenance fields."""
    actual = file_reference(ROOT, reference["path"])
    if actual["sha256"] != reference["sha256"]:
        raise ValueError(f"Frozen bytes changed: {reference['path']}")
    return reference


def sources_from_plan(plan):
    references = plan.get("sources", plan.get("source_references"))
    if references is None and "source_sha256" in plan:
        references = [{"path": path, "sha256": digest}
                      for path, digest in plan["source_sha256"].items()]
    if not isinstance(references, list) or not references:
        raise ValueError("The frozen plan must retain an explicit source bundle")
    archived = []
    for reference in references:
        checked_reference(reference)
        snapshot = archive_reference(ROOT, reference["path"])
        if snapshot["sha256"] != reference["sha256"]:
            raise ValueError("Source archive differs from the frozen source")
        archived.append(snapshot)
    return archived


def retained_files(directory):
    return [file_reference(ROOT, path.relative_to(ROOT).as_posix())
            for path in sorted(directory.rglob("*"))
            if path.is_file() and path.name != "registry-entry.json"]


def unique_references(references):
    retained = {}
    for reference in references:
        checked_reference(reference)
        previous = retained.get(reference["path"])
        if previous is not None and previous["sha256"] != reference["sha256"]:
            raise ValueError("Conflicting input digests")
        retained.setdefault(reference["path"], reference)
    return list(retained.values())


def register_study(name):
    specification = STUDIES[name]
    directory = ROOT / "data" / name / "2026-10-02"
    output = ROOT / "results" / name
    plan = json.loads((directory / "frozen-plan.json").read_text())
    result = json.loads((output / "study.json").read_text())
    plan_reference = file_reference(ROOT, (directory / "frozen-plan.json").relative_to(ROOT).as_posix())
    reported_freeze = result.get("frozen_plan", result.get("frozen_plan_sha256"))
    if isinstance(reported_freeze, dict):
        checked_reference(reported_freeze)
        if reported_freeze["sha256"] != plan_reference["sha256"]:
            raise ValueError("Result belongs to a different frozen plan")
    elif isinstance(reported_freeze, str):
        if reported_freeze != plan_reference["sha256"]:
            raise ValueError("Result belongs to a different frozen plan")
    else:
        raise ValueError("The result must retain its frozen-plan digest")
    if result.get("run_id", plan["run_id"]) != plan["run_id"]:
        raise ValueError("Result and frozen plan have different run identifiers")
    config = archive_reference(ROOT, specification["config"])
    expected_config = plan.get("config_reference", plan.get("config_sha256"))
    if isinstance(expected_config, str) and expected_config == specification["config"]:
        expected_config = plan.get("config_sha256")
    if isinstance(expected_config, dict):
        checked_reference(expected_config)
        if config["sha256"] != expected_config["sha256"]:
            raise ValueError("Configuration differs from freeze")
    elif isinstance(expected_config, str):
        if config["sha256"] != expected_config:
            raise ValueError("Configuration differs from freeze")
    else:
        raise ValueError("The frozen plan must retain the configuration digest")
    sources = sources_from_plan(plan)
    sources.append(archive_reference(ROOT, "experiments/register_validation_round.py"))
    algorithms = [{"name": specification["algorithm"], "sources": sources}]
    audit_inputs = []
    if name == "solar-validation":
        audit_path = "experiments/audit_solar_validation.py"
        if not (ROOT / audit_path).is_file() or not (output / "independent-audit.json").is_file():
            raise ValueError("Retain the independent posthoc catalogue audit before registration")
        audit = json.loads((output / "independent-audit.json").read_text())
        if audit.get("status") != "passed" or audit.get("audited_run_id") != plan["run_id"]:
            raise ValueError("Independent audit does not pass for this frozen study")
        checked_reference(audit["audit_source_reference"])
        if audit["audit_source_reference"]["path"] != audit_path:
            raise ValueError("Independent audit uses a different source")
        audit_inputs = audit["input_references"]
        algorithms.append({"name": "Posthoc independent catalogue/accounting audit; no forecast refitting",
                           "sources": [archive_reference(ROOT, audit_path)]})
    inputs = (list(plan.get("data_inputs", [])) +
              list(plan.get("development_inputs", [])) +
              list(plan.get("benchmark_references", [])) + audit_inputs + retained_files(directory))
    environment = plan.get("hardware_metadata", plan.get("environment", plan.get("versions", {})))
    entry = {
        "schema_version": 1, "run_id": plan["run_id"],
        "evidence_kind": specification["kind"],
        "resources": specification["resources"],
        "data_inputs": unique_references(inputs),
        "generated_seeds": {"configuration": plan.get("config", {}),
                            "scope": "Seed streams are in the frozen configuration; physical CPU timings are actual observations, not seed-reproducible values"},
        "algorithms": algorithms,
        "configs": [config], "artifacts": retained_files(output),
        "relationships": [{"run_id": run_id, "type": relationship}
                          for run_id, relationship in specification["parents"]],
        "hardware_metadata": {"recorded_environment": environment,
                              "scope": "Only metadata retained by the original collector; no newly probed historical host facts"},
        "summary": {"scope": result.get("scope", result.get("interpretation", result.get("conclusion_scope", "See retained report"))),
                    "report": (output / "study.json").relative_to(ROOT).as_posix()},
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
