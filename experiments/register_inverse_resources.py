"""Archive the completed synthetic inverse-resource demonstration."""
from __future__ import annotations

import json
from pathlib import Path

from orthopolity.run_registry import (
    archive_reference, file_reference, hash_file, register_run, verify_registry,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = Path("results/inverse-resources")
CONFIG = "configs/inverse_resources_2026-10-06.json"


def main():
    provenance = json.loads((ROOT / OUTPUT / "provenance.json").read_text())
    summary = json.loads((ROOT / OUTPUT / "summary.json").read_text())
    config = json.loads((ROOT / CONFIG).read_text())
    if any(item["run_id"] != config["run_id"] for item in (provenance, summary)):
        raise ValueError("Run identifiers disagree")
    if provenance["config_sha256"] != hash_file(ROOT, CONFIG):
        raise ValueError("Configuration changed since execution")
    if (ROOT / CONFIG).read_bytes() != (ROOT / OUTPUT / "config.json").read_bytes():
        raise ValueError("Retained configuration differs from executed configuration")
    for name, checksum in provenance["source_sha256"].items():
        if hash_file(ROOT, name) != checksum:
            raise ValueError(f"Executed source changed: {name}")
    for name, checksum in provenance["artifact_sha256"].items():
        if hash_file(ROOT, (OUTPUT / name).as_posix()) != checksum:
            raise ValueError(f"Retained artifact changed: {name}")
    if summary["predictions_sha256"] != hash_file(ROOT, (OUTPUT / "predictions.json").as_posix()):
        raise ValueError("Analytic predictions changed")
    algorithms = [archive_reference(ROOT, name) for name in provenance["source_sha256"]]
    algorithms.append(archive_reference(ROOT, "experiments/register_inverse_resources.py"))
    entry = dict(
        schema_version=1, run_id=config["run_id"], evidence_kind="simulation",
        resources=[dict(
            name="Shared product of two dimensionless constituent requirements",
            definition="Q=Q0*X**theta1*Y**theta2; known constituent size exponents and constraint slopes",
            units="Declared effective resource units; constituent and abundance exponents are dimensionless")],
        data_inputs=[],
        configs=[archive_reference(ROOT, CONFIG)],
        algorithms=[dict(name="Fixed-design identification, correlated Gaussian slope errors and held-out contrasts",
                         sources=algorithms)],
        artifacts=[file_reference(ROOT, path.relative_to(ROOT).as_posix())
                   for path in sorted((ROOT / OUTPUT).iterdir()) if path.is_file()],
        generated_seeds=dict(seed=config["seed"],
            derivation="NumPy default_rng joint Gaussian draws; paired errors in the shared and changed composition scenarios"),
        hardware_metadata=dict(runtime=provenance["runtime"],
            recording_scope="Execution software versions; detailed hardware and thread counts not recorded",
            cpu_model=None, total_ram_bytes=None, runtime_thread_count_verified=False),
        relationships=[],
        summary=dict(
            interpretation=summary["interpretation"],
            exposure=provenance["exposure"],
            heldout_identity=summary["heldout_identity"],
            exact_recovered_coefficients=summary["exact_recovered_coefficients"],
            shared_composition=summary["shared_composition"],
            changed_heldout_composition=summary["changed_heldout_composition"],
            uncertainty_scope=summary["uncertainty_scope"],
            partial_identification=summary["partial_identification"],
            conditioning=summary["conditioning"]),
    )
    print(json.dumps(register_run(ROOT, entry), indent=2))
    print(json.dumps(verify_registry(ROOT), indent=2))


if __name__ == "__main__":
    main()
