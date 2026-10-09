"""Archive the frozen bacterial published-summary transfer and preserve prior runs."""
from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path

from orthopolity.run_registry import archive_reference, file_reference, hash_file, register_run, verify_registry

ROOT = Path(__file__).resolve().parents[1]
CONFIG = "configs/cell_division_2026-10-08.json"
OUTPUT = Path("results/cell-division")


def main():
    config = json.loads((ROOT / CONFIG).read_text())
    base = Path(config["source_directory"])
    freeze = json.loads((ROOT / base / "freeze.json").read_text())
    provenance = json.loads((ROOT / OUTPUT / "provenance.json").read_text())
    summary = json.loads((ROOT / OUTPUT / "summary.json").read_text())
    if any(record["run_id"] != config["run_id"] for record in [freeze, provenance, summary]):
        raise ValueError("Run identifiers disagree")
    if json.loads((ROOT / OUTPUT / "config.json").read_text()) != config:
        raise ValueError("Configuration changed")
    if provenance["freeze_sha256"] != hash_file(ROOT, (base / "freeze.json").as_posix()):
        raise ValueError("Freeze changed")
    if provenance["frozen_files"] != freeze["files"]:
        raise ValueError("Execution used a different freeze")
    for group in ["frozen_files", "source_hashes"]:
        for name, digest in provenance[group].items():
            if hash_file(ROOT, name) != digest:
                raise ValueError("Changed input: " + name)
    for name, digest in provenance["outputs"].items():
        if hash_file(ROOT, (OUTPUT / name).as_posix()) != digest:
            raise ValueError("Changed output: " + name)
    manifest = json.loads((ROOT / base / "sources-evaluation.json").read_text())
    for source in manifest["sources"]:
        name = source["filename"]
        receipt = json.loads((ROOT / base / (name + ".receipt.json")).read_text())
        if receipt != source or hash_file(ROOT, (base / name).as_posix()) != source["sha256"]:
            raise ValueError("Changed source receipt: " + name)
        if name == "figure1.jpg" and datetime.fromisoformat(source["retrieval_started_utc"]) <= datetime.fromisoformat(freeze["frozen_at_utc"]):
            raise ValueError("Target retrieval predates freeze")
    algorithms = [archive_reference(ROOT, name) for name in freeze["files"] if name.endswith(".py")]
    algorithms.append(archive_reference(ROOT, "experiments/register_cell_division.py"))
    entry = dict(
        schema_version=1, run_id=config["run_id"], evidence_kind="actual_measurement",
        resources=[dict(name="Cell length as an additive-size proxy",
            definition="Theory concerns additive mass; empirical input is published fitted length moments with no width or mass calibration",
            units="Micrometres; not independently measured biomass")],
        data_inputs=[file_reference(ROOT, p.relative_to(ROOT).as_posix()) for p in sorted((ROOT / base).iterdir()) if p.is_file()],
        configs=[archive_reference(ROOT, CONFIG), archive_reference(ROOT, "docs/cell-division-protocol.md")],
        algorithms=[dict(name="Analytic birth-law moments, sampling comparator, fixed-birth and division sensitivities", sources=algorithms)],
        artifacts=[file_reference(ROOT, p.relative_to(ROOT).as_posix()) for p in sorted((ROOT / OUTPUT).iterdir()) if p.is_file()],
        generated_seeds=dict(seed=None, derivation="Deterministic analytic moments and density grids; no random draws"),
        hardware_metadata=dict(runtime={k: provenance[k] for k in ["python", "numpy", "scipy"]},
            recording_scope="Software versions; detailed hardware and thread counts not recorded",
            cpu_model=None, total_ram_bytes=None, runtime_thread_count_verified=False),
        relationships=[],
        summary=dict(**summary, protocol_interpretation_clarification="The frozen protocol's word rejects is too strong: failure of descriptive both-endpoint superiority is not statistical model rejection. No sampling uncertainty or model-rejection threshold was specified."),
    )
    print(json.dumps(register_run(ROOT, entry), indent=2))
    print(json.dumps(verify_registry(ROOT), indent=2))


if __name__ == "__main__":
    main()
