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


def chemostat_summary(result):
    variants = {row["variant_id"]: row for row in result["evaluation"]["variants"]}
    nominal = variants["nitrogen-midpoint"]
    return {"primary_equal_vessel_mean_time_weighted_total_variation": {
                variant: {model: summary["equal_vessel_mean_time_weighted_total_variation"]
                          for model, summary in row["primary"].items()} for variant, row in variants.items()},
            "verdicts": [dict(pair=row["pair"], verdict=row["verdict"]) for row in result["evaluation"]["verdicts"]],
            "cost_ratio_ordinal_endpoint": nominal["ordinal"],
            "two_budget_capacity": nominal["two_budget_capacity"],
            "observed_recovery_status": nominal["recovery"]["observed"]}


def size_budget_summary(result):
    return {outcome: {"mean_absolute_log_error": {fold: {endpoint: values[endpoint]["mean_absolute_log_error"]
                                                      for endpoint in ("E1", "E2")}
                                               for fold, values in evaluation["folds"].items()},
                      "verdicts": {endpoint: [dict(pair=row["pair"], verdict=row["verdict"]) for row in rows]
                                   for endpoint, rows in evaluation["verdicts"].items()}}
            for outcome, evaluation in result["evaluation"].items()}


def plant_profile_summary(result):
    evaluation = result["evaluation"]
    return {"equal_plot_mean_scores": evaluation["equal_plot_mean_scores"],
            "ranking_by_stock_tv": evaluation["ranking_by_stock_tv"],
            "differences_from_log_neutral": evaluation["differences_from_log_neutral"],
            "coverage": {plot: {key: row[key] for key in
                         ("raw_count", "in_domain_count", "below_count", "above_count",
                          "raw_mass", "below_mass", "above_mass", "count_coverage", "mass_coverage")}
                         for plot, row in evaluation["observed_profiles"].items()},
            "ecological_neutrality_decision": evaluation["ecological_neutrality_decision"]}


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
    "chemostat-response": {
        "config": "configs/chemostat_response_2026-10-02.json",
        "amendments": ["configs/chemostat_response_2026-10-02_amendment-1.json",
                       "configs/chemostat_response_2026-10-02_amendment-2.json"],
        "data": "data/chemostat-response/2026-10-02",
        "results": "results/chemostat-response",
        "plan": "frozen-forecasts.json",
        "result_plan_key": "frozen_forecasts",
        "plan_inputs": True,
        "kind": "actual_measurement",
        "resources": [
            {"name": "Algal nitrogen-stock proxy",
             "definition": "Published group biovolume times separately assayed pre-pulse N per cell volume from preliminary monocultures; a transferred stock proxy, not a measured vessel stock, uptake flux or requirement",
             "units": "pmol N per mL (nmol N/L)"},
            {"name": "Algal carbon-stock proxy",
             "definition": "Published group biovolume times separately assayed pre-pulse C per cell volume; carbon sensitivity of the same proxy",
             "units": "pmol C per mL (nmol C/L)"},
            {"name": "Algal biovolume reference",
             "definition": "Published group biovolume without resource conversion; reference variant only",
             "units": "cubic micrometres per mL"}],
        "algorithm": "Gated finite-group resource-response forecasts frozen before held-out decoding, with a development-fitted two-budget cost-ratio model",
        "source_provenance": "Digests equal the sources recorded in the frozen forecasts before any held-out post-pulse value was decoded",
        "posthoc": [{"name": "Post-hoc diagnostics and figures specified after evaluation; computes no forecast, score or verdict",
                     "source": "experiments/report_chemostat_response.py"}],
        "seeds": {"status": "Deterministic analysis and grid fits; no random seed"},
        "summary": chemostat_summary,
        "parents": [("restrictions-2026-10-01", "tests_two_budget_rule_on_published_measurements")],
    },
    "dunaliella-size-budget": {
        "config": "configs/dunaliella_size_budget_2026-10-02.json",
        "config_keys": ["partition_reference", "amendment_reference"],
        "data": "data/dunaliella-size-budget/2026-10-02",
        "results": "results/dunaliella-size-budget",
        "plan": "frozen-forecasts.json",
        "result_plan_key": "frozen_forecasts",
        "plan_inputs": True,
        "kind": "actual_measurement",
        "resources": [
            {"name": "Carrying-capacity biovolume",
             "definition": "Maximum across-plate mean of the authors' OD-calibrated total biovolume during 12 days of regrowth in one shared F/2 medium; the budget-limited stock of each separately grown lineage",
             "units": "cubic micrometres per microlitre"},
            {"name": "Carrying-capacity optical density",
             "definition": "The same estimator on manually blank-corrected optical density at 750 nm; common-scale sensitivity without treatment-specific calibration",
             "units": "OD750"},
            {"name": "Cell volume",
             "definition": "Mean microscopy prolate-spheroid volume (pi/6) L W^2 per lineage and pre-trial history; the size coordinate, not a resource quota",
             "units": "cubic micrometres"}],
        "algorithm": "Cross-fitted size-law and restoration forecasts for held-out selection treatments, protocol frozen before decoding selected lineages",
        "source_provenance": "Digests equal the sources recorded with the retained forecasts; the protocol and partition commits precede any decoding of small- or large-selected outcomes",
        "posthoc": [{"name": "Post-hoc diagnostics and figure specified after evaluation; computes no forecast, score or verdict",
                     "source": "experiments/report_dunaliella_size_budget.py"}],
        "seeds": {"status": "Deterministic least-squares analysis; no random seed"},
        "summary": size_budget_summary,
        "parents": [("archived-cost-transfer-2026-10-02", "uses_assigned_cross_taxon_cost_exponents"),
                    ("restrictions-2026-10-01", "tests_budget_closure_and_restoration_on_published_measurements")],
    },
    "plant-biomass-profile": {
        "config": "configs/plant_biomass_profile_2026-10-03.json",
        "amendments": ["configs/plant_biomass_profile_2026-10-03_amendment-1.json"],
        "data": "data/plant-biomass-profile/2026-10-03",
        "results": "results/plant-biomass-profile",
        "plan": "frozen-forecasts.json",
        "result_plan_key": "frozen_forecasts",
        "plan_inputs": True,
        "kind": "actual_measurement",
        "resources": [{"name": "Aboveground plant dry mass",
                       "definition": "Directly harvested and weighed ramet/stem-cluster dry mass; bin stock is its sum, with q(m)=m an identity rather than an independently tested cost law. No limiting nutrient or opportunity budget is measured",
                       "units": "grams"}],
        "algorithm": "Retrospective Ohio-to-Colorado transfer of five development-only count and expected-stock templates, with separate synthetic finite-census and dependence calibration",
        "source_provenance": "Protocol and algorithm commits precede formal fitting/scoring; forecasts and calibration were committed and pushed before scoring. Raw plant outcomes had been exposed earlier, as retained in exposure.json; no blinding claim",
        "posthoc": [{"name": "Presentation figure from retained outputs; computes no fit, forecast, score or verdict",
                     "source": "experiments/report_plant_biomass_profile.py"}],
        "seeds": {"master_seed": 2026100301,
                  "recipe": "NumPy SeedSequence: reference [seed,n,0]; census [seed,n,block,int(100*exponent),1]",
                  "scope": "Synthetic calibration only; deterministic empirical fitting and scoring"},
        "summary": plant_profile_summary,
        "parents": [("profile-calibration-2026-10-02", "extends_finite_census_observation_diagnostics"),
                    ("dunaliella-size-budget-2026-10-02", "examines_coexisting_stocks_after_separate_lineage_budget_closure")],
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
    plan_name = specification.get("plan", "frozen-plan.json")
    plan = json.loads((directory / plan_name).read_text())
    result = json.loads((output / "study.json").read_text())
    plan_reference = file_reference(ROOT, (directory / plan_name).relative_to(ROOT).as_posix())
    if checked_reference(result[specification.get("result_plan_key", "frozen_plan")])["sha256"] != plan_reference["sha256"]:
        raise ValueError("Result belongs to a different frozen plan")
    if result["run_id"] != plan["run_id"] or result.get("status") != "complete":
        raise ValueError("Only a complete report of the frozen run can be registered")
    config = archive_reference(ROOT, specification["config"])
    if config["sha256"] != checked_reference(plan["config_reference"])["sha256"]:
        raise ValueError("Configuration differs from freeze")
    configs = [config]
    amendments = specification.get("amendments", [])
    if [reference["path"] for reference in plan.get("amendment_references", [])] != amendments:
        raise ValueError("Amendments differ from those recorded at the freeze")
    for path, reference in zip(amendments, plan.get("amendment_references", [])):
        archived = archive_reference(ROOT, path)
        if archived["sha256"] != checked_reference(reference)["sha256"]:
            raise ValueError("Amendment differs from freeze")
        configs.append(archived)
    for key in specification.get("config_keys", []):
        reference = checked_reference(plan[key])
        archived = archive_reference(ROOT, reference["path"])
        if archived["sha256"] != reference["sha256"]:
            raise ValueError(f"{key} differs from freeze")
        configs.append(archived)
    inputs = retained_files(directory)
    if specification.get("plan_inputs"):
        known = {reference["path"] for reference in inputs}
        inputs += [checked_reference(reference) for reference in plan["input_references"].values()
                   if reference["path"] not in known]
    sources = []
    for reference in plan["source_references"]:
        snapshot = archive_reference(ROOT, checked_reference(reference)["path"])
        if snapshot["sha256"] != reference["sha256"]:
            raise ValueError("Source archive differs from the frozen source")
        sources.append(snapshot)
    entry = {
        "schema_version": 1, "run_id": plan["run_id"], "evidence_kind": specification["kind"],
        "resources": specification["resources"],
        "data_inputs": inputs,
        "generated_seeds": specification["seeds"],
        "algorithms": [{"name": specification["algorithm"], "sources": sources,
                        "source_provenance": specification.get("source_provenance", "Digests equal the sources recorded in the frozen plan before acquisition/evaluation")}]
                      + [{"name": item["name"], "sources": [archive_reference(ROOT, item["source"])],
                          "source_provenance": "Content-addressed snapshot at registration; presentation and labelled post-hoc diagnostics only"}
                         for item in specification.get("posthoc", [])],
        "configs": configs, "artifacts": retained_files(output),
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
