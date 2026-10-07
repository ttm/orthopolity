"""Archive the completed, frozen linguistic resource transfer comparison."""
from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path

from orthopolity.run_registry import (
    archive_reference, file_reference, hash_file, register_run, verify_registry,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = Path("results/linguistic-resources")
CONFIG = "configs/linguistic_resources_2026-10-07.json"


def main():
    config = json.loads((ROOT / CONFIG).read_text())
    directory = Path(config["source_directory"])
    provenance = json.loads((ROOT / OUTPUT / "provenance.json").read_text())
    summary = json.loads((ROOT / OUTPUT / "summary.json").read_text())
    freeze = json.loads((ROOT / directory / "freeze.json").read_text())
    manifest = json.loads((ROOT / directory / "sources.json").read_text())
    if any(item["run_id"] != config["run_id"] for item in (provenance, summary)):
        raise ValueError("Run identifiers disagree")
    if json.loads((ROOT / OUTPUT / "config.json").read_text()) != config:
        raise ValueError("Retained configuration differs from executed configuration")
    if provenance["freeze_sha256"] != hash_file(ROOT, (directory / "freeze.json").as_posix()):
        raise ValueError("Training freeze changed")
    if provenance["frozen_files"] != freeze["files"]:
        raise ValueError("Execution used a different freeze")
    for group in ("frozen_files", "source_hashes"):
        for name, checksum in provenance[group].items():
            if hash_file(ROOT, name) != checksum:
                raise ValueError(f"Changed {group}: {name}")
    for name, checksum in provenance["outputs"].items():
        if hash_file(ROOT, (OUTPUT / name).as_posix()) != checksum:
            raise ValueError(f"Changed retained output: {name}")
    for source in manifest["sources"]:
        name = source["filename"]
        receipt = json.loads((ROOT / directory / (name + ".receipt.json")).read_text())
        if receipt != source:
            raise ValueError(f"Source receipt differs from manifest: {name}")
        if hash_file(ROOT, (directory / name).as_posix()) != source["sha256"]:
            raise ValueError(f"Source differs from receipt: {name}")
        if source["stage"] == "test" and datetime.fromisoformat(source["retrieved_at_utc"]) <= datetime.fromisoformat(freeze["frozen_at_utc"]):
            raise ValueError("Recorded test acquisition does not follow training freeze")
    sources = [archive_reference(ROOT, name) for name in freeze["files"] if name.endswith(".py")]
    sources.append(archive_reference(ROOT, "experiments/register_linguistic_resources.py"))
    entry = dict(
        schema_version=1, run_id=config["run_id"], evidence_kind="actual_measurement",
        resources=[dict(
            name="Written letters and canonical dictionary phoneme counts",
            definition="Per-token symbolic counts L and P; Q proportional to L**thetaL * P**thetaP is inferred on calibration genres under neutral type allocation",
            units="Letters or pronunciation symbols per word; effective symbolic-cost scale is unidentified, not acoustic energy or sonority")],
        data_inputs=[file_reference(ROOT, path.relative_to(ROOT).as_posix())
                     for path in sorted((ROOT / directory).iterdir()) if path.is_file()],
        configs=[archive_reference(ROOT, CONFIG), archive_reference(ROOT, "docs/linguistic-protocol.md")],
        algorithms=[dict(name="Training-only vocabulary and nonnegative symbolic-cost inference with frozen cross-genre predictions",
                         sources=sources)],
        artifacts=[file_reference(ROOT, path.relative_to(ROOT).as_posix())
                   for path in sorted((ROOT / OUTPUT).iterdir()) if path.is_file()],
        generated_seeds=dict(seed=config["bootstrap_seed"],
            derivation="Paired document bootstrap of held-out loss differences with fixed trained forecasts; no token-iid or training uncertainty"),
        hardware_metadata=dict(
            runtime={key: provenance[key] for key in ("python", "numpy", "scipy")},
            recording_scope="Execution software versions; detailed hardware and thread counts not recorded",
            cpu_model=None, total_ram_bytes=None, runtime_thread_count_verified=False),
        relationships=[dict(run_id="inverse-resources-2026-10-06",
                            type="empirical_application_of_inverse_resource_framework")],
        summary=dict(
            interpretation="Retrospective public-corpus transfer test of a restricted symbolic resource candidate; no new speech measurements or general-law verdict",
            exposure=summary["exposure"],
            diagnostics=summary["diagnostics"], parameters=summary["parameters"],
            coverage=summary["coverage"], scores=summary["scores"],
            exact_training_duplicate_sentences=summary["exact_training_duplicate_sentences"],
            all_training_document_overlap=summary["all_training_document_overlap"],
            feature_limitation=summary["feature_limitation"],
            uncertainty=summary["bootstrap"]),
    )
    print(json.dumps(register_run(ROOT, entry), indent=2))
    print(json.dumps(verify_registry(ROOT), indent=2))


if __name__ == "__main__":
    main()
