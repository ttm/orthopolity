"""Register the field audit, preserving its literal outputs and P unit caveat."""
import json
from pathlib import Path

from orthopolity.run_registry import archive_reference, file_reference, register_run, verify_registry
from verify_field_resources import verify

ROOT = Path(__file__).resolve().parents[1]
BASE = "data/field-resources/2026-10-12"
DIRECTORY = "results/field-resources-2026-10-12"


def main():
    directory = ROOT / DIRECTORY
    result = json.loads((directory / "result.json").read_text())
    execution = json.loads((directory / "execution.json").read_text())
    if verify(directory) != json.loads((directory / "verification.json").read_text()):
        raise ValueError("Independent verification differs")
    # Once registered, audit the original snapshots. Later prose corrections
    # must not replace historical source digests or trigger a new empirical run.
    registry = ROOT / "results/run-registry.jsonl"
    if registry.exists():
        retained = [json.loads(line) for line in registry.read_text().splitlines()]
        if any(entry["run_id"] == result["run_id"] for entry in retained):
            checked = verify_registry(ROOT)
            print(json.dumps(dict(run_id=result["run_id"], appended=False,
                                  source_scope="Original registered snapshots"), indent=2))
            print(json.dumps(checked, indent=2))
            return
    config = "configs/field_resources_2026-10-12.json"
    sources = [item["path"] for item in execution["sources"] if item["path"] != config]
    sources += ["experiments/verify_field_resources.py", "experiments/register_field_resources.py",
                "tests/test_field_resources_verification.py", "docs/field-resources-results-2026-10-12.md"]
    entry = dict(schema_version=1, run_id=result["run_id"], evidence_kind="actual_measurement",
        resources=[dict(name="Independent cyanobacterial C/N/P quotas, ambient counts and filtered bulk stocks",
            units="fmol/cell times cells/mL times 1e-6 = micromol/L; Pacific P label is unit-unqualified",
            definition="Finite cell counting measure; partial standing-stock compatibility, not equal allocation or available supply")],
        data_inputs=[file_reference(ROOT, p.relative_to(ROOT).as_posix(), role="Retained source, receipt or pre-response metadata audit")
                     for p in sorted((ROOT / BASE).iterdir()) if p.is_file()],
        configs=[archive_reference(ROOT, config)],
        algorithms=[dict(name="Frozen metadata joins and conditional stock bounds with independent Decimal verification",
                         sources=[archive_reference(ROOT, p) for p in sources])],
        artifacts=[file_reference(ROOT, p.relative_to(ROOT).as_posix()) for p in sorted(directory.iterdir()) if p.is_file()],
        generated_seeds=dict(generated_empirical_data=False, randomized_analysis=False),
        hardware_metadata=dict(python=execution["python"], runtime_thread_count_verified=False),
        relationships=[dict(run_id="paired-phosphorus-pilot-2026-10-12", type="different_cohort_measurement_prerequisite")],
        summary=dict(freeze_commit=execution["freeze_commit"], literal_frozen_summaries=result["summaries"],
            primary_carbon_nitrogen=dict(samples=9, stations=8, scored=18, exceeding=0),
            additional_date_offset_carbon_nitrogen=dict(samples=8, scored=15, exceeding=1),
            post_response_qualification="All nine Pacific phosphorus comparisons remain unit-unqualified; printed uM label produces suspicious bulk C:P. No factor-1000 correction was applied. Atlantic P was excluded before execution.",
            scope=result["scope"],
            conclusion="Primary C/N partial stocks fit conservative bulk bound; incomplete coverage prevents closure and unspecified opportunities prevent an allocation test"))
    print(json.dumps(register_run(ROOT, entry), indent=2))
    print(json.dumps(verify_registry(ROOT), indent=2))


if __name__ == "__main__":
    main()
