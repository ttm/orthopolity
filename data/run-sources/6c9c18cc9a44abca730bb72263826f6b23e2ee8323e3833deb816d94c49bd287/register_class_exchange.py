"""Archive a completed class-exchange demonstration without rerunning it."""
from __future__ import annotations

import json
from pathlib import Path

from orthopolity.run_registry import (
    archive_reference, file_reference, hash_file, register_run, verify_registry,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = Path("results/class-exchange")
PRESENTATION = Path("results/class-exchange-presentation")
CONFIG = "configs/class_exchange_2026-10-05.json"


def main():
    provenance = json.loads((ROOT / OUTPUT / "provenance.json").read_text())
    summary = json.loads((ROOT / OUTPUT / "summary.json").read_text())
    config = json.loads((ROOT / CONFIG).read_text())
    run_id = config["run_id"]
    if any(record["run_id"] != run_id for record in (provenance, summary)):
        raise ValueError("Run identifiers disagree")
    if provenance["config_sha256"] != hash_file(ROOT, CONFIG):
        raise ValueError("Configuration changed since execution")
    if (ROOT / CONFIG).read_bytes() != (ROOT / OUTPUT / "config.json").read_bytes():
        raise ValueError("Retained configuration differs from the executed configuration")
    for name, digest in provenance["artifact_sha256"].items():
        if hash_file(ROOT, (OUTPUT / name).as_posix()) != digest:
            raise ValueError(f"Retained artifact changed: {name}")
    if summary["predictions_sha256"] != hash_file(ROOT, (OUTPUT / "predictions.json").as_posix()):
        raise ValueError("Predictions differ from the executed forecast")
    sources = []
    for name, digest in provenance["source_sha256"].items():
        if hash_file(ROOT, name) != digest:
            raise ValueError(f"Executed source changed: {name}")
        sources.append(archive_reference(ROOT, name))
    sources.append(archive_reference(ROOT, "experiments/register_class_exchange.py"))
    presentation = json.loads((ROOT / PRESENTATION / "provenance.json").read_text())
    report_source = "experiments/report_class_exchange.py"
    if presentation["source_sha256"] != hash_file(ROOT, report_source):
        raise ValueError("Presentation source changed since rendering")
    for name, digest in presentation["input_sha256"].items():
        if hash_file(ROOT, (OUTPUT / name).as_posix()) != digest:
            raise ValueError(f"Presentation input changed: {name}")
    for name, digest in presentation["artifact_sha256"].items():
        if hash_file(ROOT, (PRESENTATION / name).as_posix()) != digest:
            raise ValueError(f"Presentation artifact changed: {name}")
    artifacts = [file_reference(ROOT, path.relative_to(ROOT).as_posix())
                 for directory in (OUTPUT, PRESENTATION)
                 for path in sorted((ROOT / directory).iterdir()) if path.is_file()]
    entry = dict(
        schema_version=1, run_id=run_id, evidence_kind="simulation",
        resources=[dict(
            name="Class resource in equal packets",
            definition="Unit total shared among fixed logarithmic size classes by declared conservative jump kinetics; equivalent object counts R_i/q_i are not packet counts",
            units="Normalized model resource units; model time is uncalibrated")],
        data_inputs=[], configs=[archive_reference(ROOT, CONFIG)],
        algorithms=[dict(name="Reversible class exchange with added downhill transport and state-preserving release",
                         sources=sources),
                    dict(name="Post-hoc manuscript figure from retained trajectories without resimulation",
                         sources=[archive_reference(ROOT, report_source)])],
        artifacts=artifacts,
        generated_seeds=dict(seed=config["seed"],
            derivation="NumPy default_rng; independent packet destinations drawn by source class at exact matrix-exponential checkpoints; fixed order in archived runner"),
        hardware_metadata=dict(
            recording_scope="Software versions retained at execution; detailed hardware and thread counts were not recorded",
            runtime=provenance["runtime"], cpu_model=None, total_ram_bytes=None,
            runtime_thread_count_verified=False),
        relationships=[dict(run_id="models-2026-10-01", type="extends_class_allocation_mechanism")],
        summary=dict(
            interpretation="Constructive toy dynamics with analytic equilibria, convergence bounds, opposing component drifts, and finite-packet fluctuations; no new natural observations",
            prediction_order="Rate-derived predictions written before simulated trajectories; no external preregistration",
            all_stochastic_totals_conserved=summary["all_stochastic_totals_conserved"],
            stochastic_states_preserved_at_switch=summary["stochastic_states_preserved_at_switch"],
            drift_cancellation_l2=summary["stationary_opposing_drifts"]["cancellation_l2"],
            phases=[{key: phase[key] for key in ("name", "spectral_gap", "final_relative_l2", "final_bound")}
                    for phase in summary["phases"]]),
    )
    print(json.dumps(register_run(ROOT, entry), indent=2))
    print(json.dumps(verify_registry(ROOT), indent=2))


if __name__ == "__main__":
    main()
