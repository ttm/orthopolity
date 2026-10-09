"""Archive the completed retrospective FIRAS description, without a new fit."""
from __future__ import annotations

import json
from pathlib import Path

from orthopolity.run_registry import (
    archive_reference, file_reference, hash_file, register_run, verify_registry,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = Path("results/thermal-radiation")
CONFIG = "configs/thermal_radiation_2026-10-06.json"


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
        raise ValueError("Retained configuration differs from executed configuration")
    for group, prefix in (("source_sha256", Path()), ("input_sha256", Path()),
                          ("artifact_sha256", OUTPUT)):
        for name, digest in provenance[group].items():
            if hash_file(ROOT, (prefix / name).as_posix()) != digest:
                raise ValueError(f"Changed retained {group}: {name}")
    source_directory = ROOT / config["source_directory"]
    manifest = json.loads((source_directory / config["source_manifest"]).read_text())
    for source in manifest["sources"]:
        receipt = json.loads((source_directory / (source["filename"] + ".receipt.json")).read_text())
        if receipt != source:
            raise ValueError(f"Acquisition receipt differs from manifest: {source['filename']}")
    algorithms = [archive_reference(ROOT, name) for name in provenance["source_sha256"]]
    algorithms.extend(archive_reference(ROOT, name) for name in (
        "experiments/fetch_thermal_radiation.py",
        "experiments/register_thermal_radiation.py",
        "tests/test_thermal_radiation.py",
    ))
    inputs = [file_reference(ROOT, p.relative_to(ROOT).as_posix())
              for p in sorted(source_directory.iterdir()) if p.is_file()]
    artifacts = [file_reference(ROOT, p.relative_to(ROOT).as_posix())
                 for p in sorted((ROOT / OUTPUT).iterdir()) if p.is_file()]
    entry = dict(
        schema_version=1, run_id=run_id, evidence_kind="actual_measurement",
        resources=[dict(name="Thermal electromagnetic excitation energy per mode",
            definition="Above-ground-state photon energy per independently counted electromagnetic mode, including polarization; inferred from the published reconstructed FIRAS radiance using vacuum mode density",
            units="J per mode and dimensionless E/(k_B T); source per-Hz radiance in MJy/sr and residuals in kJy/sr")],
        data_inputs=inputs,
        configs=[archive_reference(ROOT, CONFIG),
                 archive_reference(ROOT, "docs/thermal-radiation-protocol.md")],
        algorithms=[dict(name="Exact thermal mode calculations and retrospective published-product transformation with approximate correlated residual covariance",
                         sources=algorithms)],
        artifacts=artifacts,
        generated_seeds=dict(seed=None, derivation="Deterministic analytic and tabular calculations; no random observations or simulations"),
        hardware_metadata=dict(runtime=provenance["runtime"],
            recording_scope="Execution software versions; detailed hardware and thread counts not recorded",
            cpu_model=None, total_ram_bytes=None, runtime_thread_count_verified=False),
        relationships=[dict(run_id="class-exchange-2026-10-05", type="extends_physical_equality_and_constraint_examples")],
        summary=dict(
            measurement_scope="Reanalysis of a published calibrated and reconstructed product, not new measurements or an independent reproduction of full FIRAS calibration/sky fitting",
            selection=summary["selection"], exposure=summary["exposure"],
            inference=summary["inference"], rows=summary["rows"],
            temperature_kelvin=summary["temperature_kelvin"],
            temperature_origin=summary["temperature_origin"],
            x_range=summary["x_range"],
            observed_mode_energy_over_kBT_range=summary["observed_mode_energy_over_kBT_range"],
            covariance_audit=summary["covariance_audit"],
            reconstruction_discrepancy_kJy_sr_range=summary["reconstruction_discrepancy_kJy_sr_range"],
            interpretation=summary["interpretation"],
        ),
    )
    print(json.dumps(register_run(ROOT, entry), indent=2))
    print(json.dumps(verify_registry(ROOT), indent=2))


if __name__ == "__main__":
    main()
