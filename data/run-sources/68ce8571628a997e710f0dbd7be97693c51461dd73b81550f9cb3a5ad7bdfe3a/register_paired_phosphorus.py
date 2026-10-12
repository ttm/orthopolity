"""Append the limited paired-assay pilot without modifying prior studies."""
import json
from pathlib import Path

from orthopolity.run_registry import archive_reference, file_reference, register_run, verify_registry
from verify_paired_phosphorus import verify

ROOT = Path(__file__).resolve().parents[1]
BASE = "data/paired-phosphorus/2026-10-12"
DIRECTORY = "results/paired-phosphorus-pilot-2026-10-12"


def main():
    directory = ROOT / DIRECTORY
    result = json.loads((directory / "result.json").read_text())
    execution = json.loads((directory / "execution.json").read_text())
    if verify(directory) != json.loads((directory / "verification.json").read_text()):
        raise ValueError("Independent verification differs")
    config = "configs/paired_phosphorus_2026-10-12.json"
    sources = [item["path"] for item in execution["sources"] if item["path"] != config]
    sources += ["experiments/verify_paired_phosphorus.py", "experiments/register_paired_phosphorus.py",
                "tests/test_paired_phosphorus_verification.py", "docs/paired-phosphorus-results-2026-10-12.md"]
    entry = dict(schema_version=1, run_id=result["run_id"], evidence_kind="actual_measurement",
        resources=[dict(name="Particulate phosphorus and independent single-cell phosphorus quota",
            units="Bulk micromoles/L, single-cell fg/cell, cell count per mL",
            definition="Finite counting measure over monoculture cells; conditional accounting transfer, not equal allocation")],
        data_inputs=[file_reference(ROOT, p.relative_to(ROOT).as_posix(), role="Retained source or pre-response audit")
                     for p in sorted((ROOT / BASE).iterdir()) if p.is_file()],
        configs=[archive_reference(ROOT, config)],
        algorithms=[dict(name="Frozen conditional fixed/measured-cost predictions and independent Decimal verification",
                         sources=[archive_reference(ROOT, p) for p in sources])],
        artifacts=[file_reference(ROOT, p.relative_to(ROOT).as_posix()) for p in sorted(directory.iterdir()) if p.is_file()],
        generated_seeds=dict(generated_empirical_data=False, randomized_analysis=False),
        hardware_metadata=dict(python=execution["python"], runtime_thread_count_verified=False),
        relationships=[dict(run_id="chemostat-capacity-followup-2026-10-10", type="new_cohort_measurement_prerequisite_followup")],
        summary=dict(n_calibration_cultures=1, n_test_cultures=1,
                     observed_cells_ml=result["targets"][0]["sample"]["observed_cells_ml"],
                     predictions=result["targets"][0]["models"],
                     initial_freeze="83a8c36", amended_freeze=execution["freeze_commit"],
                     initial_attempt="Stopped at missing optional volume input before count evaluation",
                     inference_scope=result["inference_scope"],
                     conclusion="Both predictions miss pilot accuracy target; measured quota does not improve; raw accounting offset does not transfer"))
    print(json.dumps(register_run(ROOT, entry), indent=2))
    print(json.dumps(verify_registry(ROOT), indent=2))


if __name__ == "__main__":
    main()
