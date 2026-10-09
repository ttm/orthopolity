"""Describe the retained COBE/FIRAS product and thermal mode-energy law offline.

The monopole is a reconstructed published product. Temperature is fixed by its
construction, with no fitting, selected rows, new p-value, or independent-data
claim. The original residuals remain distinct from residuals recomputed using
modern exact SI constants and the displayed frequency grid.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform

import numpy as np
import scipy

from orthopolity.thermal_radiation import (
    C_LIGHT, H_PLANCK, K_BOLTZMANN, dimensionless_frequency,
    dimensionless_mode_energy, intensity_to_energy_per_mode, mode_density,
    planck_intensity, radiation_energy_density, rayleigh_jeans_intensity,
    suppression_factor,
)


ROOT = Path(__file__).resolve().parents[1]
MJY_SR_TO_SI = 1e-20
KJY_SR_TO_SI = 1e-23


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def write_columns(path, columns):
    with path.open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(columns)
        writer.writerows(zip(*columns.values(), strict=True))


def load_inputs(config):
    directory = ROOT / config["source_directory"]
    manifest_path = directory / config["source_manifest"]
    manifest = json.loads(manifest_path.read_text())
    hashes = {str(manifest_path.relative_to(ROOT)): digest(manifest_path)}
    for source in manifest["sources"]:
        path = directory / source["filename"]
        checksum = digest(path)
        if checksum != source["sha256"] or path.stat().st_size != source["size_bytes"]:
            raise ValueError(f"retained source failed pinned hash/size check: {path}")
        hashes[str(path.relative_to(ROOT))] = checksum
    spectrum_path = directory / config["spectrum_filename"]
    if str(spectrum_path.relative_to(ROOT)) not in hashes:
        raise ValueError("spectrum is not pinned in the source manifest")
    table = np.loadtxt(spectrum_path, comments="#")
    if table.shape != (config["expected_rows"], 5) or not np.isfinite(table).all():
        raise ValueError("unexpected source rows/columns or nonfinite source values")
    if np.any(np.diff(table[:, 0]) <= 0) or np.any(table[:, 0] <= 0) or np.any(table[:, 3] <= 0):
        raise ValueError("source frequencies must increase and marginal errors must be positive")
    correlation_path = directory / config["correlation_filename"]
    correlation = json.loads(correlation_path.read_text())
    article_path = directory / correlation["source_file"]
    if (str(article_path.relative_to(ROOT)) not in hashes
            or hashes[str(article_path.relative_to(ROOT))] != correlation["source_sha256"]):
        raise ValueError("covariance transcription does not match a pinned primary source")
    hashes[str(correlation_path.relative_to(ROOT))] = digest(correlation_path)
    q = np.asarray(correlation["q"], dtype=float)
    if q.shape != (len(table),) or not np.isfinite(q).all() or q[0] != 1:
        raise ValueError("correlation prescription needs one finite coefficient per channel lag and q[0]=1")
    lag = np.abs(np.arange(len(table))[:, None] - np.arange(len(table))[None, :])
    correlation_matrix = q[lag]
    np.linalg.cholesky(correlation_matrix)
    covariance = table[:, 3, None] * table[None, :, 3] * correlation_matrix
    return table, covariance, correlation_matrix, hashes


def convert(table, temperature):
    wavenumber, monopole, residual, sigma, galaxy = table.T
    frequency = 100 * C_LIGHT * wavenumber
    observed = monopole * MJY_SR_TO_SI
    model = np.asarray(planck_intensity(frequency, temperature))
    rj = np.asarray(rayleigh_jeans_intensity(frequency, temperature))
    sigma_si = sigma * KJY_SR_TO_SI
    columns = dict(
        row=np.arange(len(table)), wavenumber_cm_inverse=wavenumber, frequency_hz=frequency,
        monopole_MJy_sr=monopole, reported_residual_kJy_sr=residual,
        marginal_sigma_kJy_sr=sigma, modeled_galaxy_kJy_sr=galaxy,
        x=dimensionless_frequency(frequency, temperature),
        observed_intensity_si=observed, planck_intensity_si=model, rayleigh_jeans_intensity_si=rj,
        planck_MJy_sr=model / MJY_SR_TO_SI, rayleigh_jeans_MJy_sr=rj / MJY_SR_TO_SI,
        electromagnetic_mode_density_per_m3_per_hz=mode_density(frequency),
        planck_energy_density_per_m3_per_hz=radiation_energy_density(frequency, temperature),
        inferred_thermal_energy_per_mode_J=intensity_to_energy_per_mode(frequency, observed),
        observed_mode_energy_over_kBT=dimensionless_mode_energy(frequency, observed, temperature),
        planck_mode_energy_over_kBT=suppression_factor(dimensionless_frequency(frequency, temperature)),
        marginal_sigma_mode_energy_over_kBT=sigma_si / rj,
        original_residual_mode_energy_over_kBT=residual * KJY_SR_TO_SI / rj,
        reported_residual_over_marginal_sigma=residual / sigma,
        recomputed_residual_kJy_sr=(observed - model) / KJY_SR_TO_SI,
        reconstruction_discrepancy_kJy_sr=(observed - model) / KJY_SR_TO_SI - residual,
    )
    return columns


def mode_ratio_covariance(frequency_hz, temperature, covariance_kJy_sr_squared):
    """Propagate a per-Hz intensity covariance through the fixed-T linear map."""
    covariance = np.asarray(covariance_kJy_sr_squared, dtype=float)
    frequency = np.asarray(frequency_hz, dtype=float)
    if (frequency.ndim != 1 or np.any(frequency <= 0)
            or covariance.shape != (len(frequency), len(frequency))
            or not np.isfinite(covariance).all()
            or not np.allclose(covariance, covariance.T, rtol=1e-12, atol=0)):
        raise ValueError("covariance must be finite, symmetric, and match positive channel frequencies")
    jacobian = KJY_SR_TO_SI / rayleigh_jeans_intensity(frequency, temperature)
    return jacobian[:, None] * covariance * jacobian[None, :]


def figures(output, columns, theory, temperature):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.titlesize": 10, "axes.labelsize": 10,
                         "xtick.labelsize": 9, "ytick.labelsize": 9,
                         "legend.fontsize": 8, "svg.fonttype": "none",
                         "svg.hashsalt": "thermal-radiation-2026-10-06"})
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 6.2), layout="constrained")
    theory_color = "#285f9b"
    data_color = "#b9532e"
    x = columns["x"]
    ax = axes[0, 0]
    ax.plot(theory["x"][1:], theory["thermal_energy_over_kBT"][1:], color=theory_color,
            label="Quantum thermal energy")
    ax.axhline(1, color="black", linestyle="--", linewidth=1, label="Classical limit")
    ax.axvspan(float(x.min()), float(x.max()), color="gray", alpha=.15, label="FIRAS range")
    ax.set(xscale="log", yscale="log", xlabel="x = hν / (kBT)", ylabel="Thermal energy / (kBT)",
           title="a  Energy per electromagnetic mode")
    ax.legend(frameon=False, loc="lower left")

    frequency_GHz = columns["frequency_hz"] / 1e9
    ax = axes[0, 1]
    ax.errorbar(frequency_GHz, columns["monopole_MJy_sr"], yerr=columns["marginal_sigma_kJy_sr"] / 1000,
                fmt="o", ms=2.7, color=data_color, linewidth=.8, label="Reconstructed monopole", zorder=3)
    ax.plot(frequency_GHz, columns["planck_MJy_sr"], color=theory_color,
            label=f"Planck, T = {temperature:g} K", linewidth=1.4)
    ax.plot(frequency_GHz, columns["rayleigh_jeans_MJy_sr"], color="black", linestyle="--",
            label="Rayleigh–Jeans", linewidth=1)
    ax.set(yscale="log", xlabel="Frequency (GHz)", ylabel="Intensity (MJy/sr)",
           title="b  Published FIRAS monopole")
    ax.legend(frameon=False, loc="lower left")

    ax = axes[1, 0]
    ax.errorbar(frequency_GHz, columns["observed_mode_energy_over_kBT"],
                yerr=columns["marginal_sigma_mode_energy_over_kBT"], fmt="o", ms=2.7,
                color=data_color, linewidth=.8, label="Transformed product", zorder=3)
    ax.plot(frequency_GHz, columns["planck_mode_energy_over_kBT"], color=theory_color,
            linewidth=1.4, label="Planck mode energy")
    ax.axhline(1, color="black", linestyle="--", linewidth=1, label="Classical limit")
    ax.set(yscale="log", xlabel="Frequency (GHz)", ylabel="Inferred energy / (kBT)",
           title="c  Allocation per mode")
    ax.legend(frameon=False, loc="lower left")

    ax = axes[1, 1]
    ax.errorbar(frequency_GHz, columns["reported_residual_kJy_sr"],
                yerr=columns["marginal_sigma_kJy_sr"], fmt="o", ms=2.7,
                color=data_color, linewidth=.8, label="Published residual ±1σ")
    ax.axhline(0, color="black", linestyle=":", linewidth=.8)
    ax.set(xlabel="Frequency (GHz)", ylabel="Original residual (kJy/sr)",
           title="d  Original fitted residuals")
    ax.legend(frameon=False, loc="lower left")
    for ax in axes.flat:
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(alpha=.18)
    fig.suptitle("Published reconstructed product; correlated marginal errors", fontsize=10)
    fig.savefig(output / "thermal-radiation.png", dpi=240, bbox_inches="tight", pad_inches=.06)
    fig.savefig(output / "thermal-radiation.svg", metadata={"Date": None}, bbox_inches="tight", pad_inches=.06)
    plt.close(fig)
    svg = output / "thermal-radiation.svg"
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines()) + "\n")
    return matplotlib.__version__


def run(config_path, output):
    config = json.loads(config_path.read_text())
    table, covariance, correlation_matrix, input_hashes = load_inputs(config)
    config_hash = digest(config_path)
    source_hashes = {str(path.relative_to(ROOT)): digest(path) for path in
                     (Path(__file__), ROOT / "src/orthopolity/thermal_radiation.py")}
    provenance_path = output / "provenance.json"
    if provenance_path.exists():
        retained = json.loads(provenance_path.read_text())
        if (retained["config_sha256"] != config_hash or retained["source_sha256"] != source_hashes
                or retained["input_sha256"] != input_hashes):
            raise ValueError("retained inputs changed; preserve this run and choose another output directory")
        if not all((output / path).exists() and digest(output / path) == checksum
                   for path, checksum in retained["artifact_sha256"].items()):
            raise ValueError("retained artifacts changed; preserve this run and choose another output directory")
        print(json.dumps(dict(action="audited_existing_run", output=str(output))))
        return
    if output.exists() and any(output.iterdir()):
        raise ValueError("output directory is not empty; preserve it and choose another directory")
    temperature = config["temperature_kelvin"]
    columns = convert(table, temperature)
    if (not 0 < config["theory_x_min"] < config["theory_x_max"]
            or isinstance(config["theory_points"], bool) or not isinstance(config["theory_points"], int)
            or config["theory_points"] < 2):
        raise ValueError("theory grid needs positive increasing limits and at least two points")
    theory_x = np.r_[0., np.geomspace(config["theory_x_min"], config["theory_x_max"], config["theory_points"])]
    theory = dict(x=theory_x, thermal_energy_over_kBT=suppression_factor(theory_x),
                  classical_energy_over_kBT=np.ones_like(theory_x))
    covariance_mode = mode_ratio_covariance(columns["frequency_hz"], temperature, covariance)
    residual = columns["reported_residual_kJy_sr"]
    quadratic = float(residual @ np.linalg.solve(covariance, residual))
    diagonal_wrms = float(np.sqrt(np.sum((residual / table[:, 3])**2) / np.sum(1 / table[:, 3]**2)))
    peak_monopole_MJy_sr = float(np.max(columns["monopole_MJy_sr"]))
    discrepancy = columns["reconstruction_discrepancy_kJy_sr"]
    observed_ratio = columns["observed_mode_energy_over_kBT"]
    model_ratio = columns["planck_mode_energy_over_kBT"]
    summary = dict(
        run_id=config["run_id"], analysis_kind=config["analysis_kind"], rows=len(table),
        selection=config["selection"], exposure=config["exposure"], inference=config["inference"],
        temperature_kelvin=temperature, temperature_origin=config["temperature_origin"],
        exact_SI_constants=dict(h_J_s=H_PLANCK, kB_J_per_K=K_BOLTZMANN, c_m_per_s=C_LIGHT),
        units=dict(input_frequency="cm^-1 coordinate, converted to Hz by nu=100*c*wavenumber",
                   intensity="Input intensities are already per Hz (MJy/sr); no extra wavenumber Jacobian",
                   resource="Thermal excitation energy per electromagnetic mode, excluding zero-point energy",
                   reference_measure="Count of electromagnetic modes, including two polarizations"),
        frequency_GHz_range=[float(columns["frequency_hz"].min() / 1e9), float(columns["frequency_hz"].max() / 1e9)],
        x_range=[float(columns["x"].min()), float(columns["x"].max())],
        observed_mode_energy_over_kBT_range=[float(observed_ratio.min()), float(observed_ratio.max())],
        planck_mode_energy_over_kBT_range=[float(model_ratio.min()), float(model_ratio.max())],
        maximum_absolute_mode_ratio_difference=float(np.max(np.abs(observed_ratio - model_ratio))),
        maximum_absolute_reported_residual_kJy_sr=float(np.max(np.abs(residual))),
        maximum_absolute_reported_residual_over_marginal_sigma=float(np.max(np.abs(residual / table[:, 3]))),
        diagonal_weighted_residual_rms_kJy_sr=diagonal_wrms,
        diagonal_weighted_residual_rms_formula="sqrt(sum((reported_residual/marginal_sigma)^2)/sum(1/marginal_sigma^2))",
        diagonal_weighting_scope="Descriptive inverse-marginal-variance weighted RMS; channel correlations are retained separately and no independence or test interpretation is assigned",
        peak_tabulated_monopole_MJy_sr=peak_monopole_MJy_sr,
        diagonal_weighted_residual_rms_ppm_of_peak=1e6 * diagonal_wrms / (1000 * peak_monopole_MJy_sr),
        reconstruction_discrepancy_kJy_sr_range=[float(discrepancy.min()), float(discrepancy.max())],
        maximum_absolute_reconstruction_discrepancy_kJy_sr=float(np.max(np.abs(discrepancy))),
        reconstruction_caution="Displayed frequencies and intensities with modern exact SI constants do not reproduce the published monopole minus original residual exactly; discrepancies are preserved and no cause is inferred",
        covariance_audit=dict(
            formula="C_ij=sigma_i*sigma_j*q[abs(i-j)] from the published approximate lag prescription",
            original_residual_quadratic=quadratic,
            correlation_minimum_eigenvalue=float(np.linalg.eigvalsh(correlation_matrix)[0]),
            mode_covariance_transformation="D C D; D_ii=1e-23/B_RJ(nu_i,T), with input C in (kJy/sr)^2",
            marginal_variance_conversion_max_relative_error=float(np.max(np.abs(
                np.diag(covariance_mode) / columns["marginal_sigma_mode_energy_over_kBT"]**2 - 1))),
            scope="Descriptive quadratic for published original residuals and approximate covariance; no refit, new p-value, or reproduction claim for the original publication's chi-square"),
        interpretation="Classical equal thermal energy per mode is the x->0 limit; FIRAS samples quantum-suppressed modes and its reconstructed product is not an independent confirmation of the model used to construct it",
        fitted_parameters=0, new_goodness_of_fit_p_value=None,
    )
    output.mkdir(parents=True, exist_ok=True)
    (output / "config.json").write_bytes(config_path.read_bytes())
    write_columns(output / "spectrum.csv", columns)
    write_columns(output / "theory.csv", theory)
    indices_i, indices_j = np.indices(covariance.shape)
    write_columns(output / "covariances.csv", dict(
        row_i=indices_i.ravel(), row_j=indices_j.ravel(),
        lag=np.abs(indices_i - indices_j).ravel(), correlation=correlation_matrix.ravel(),
        residual_covariance_kJy_sr_squared=covariance.ravel(),
        mode_energy_over_kBT_covariance=covariance_mode.ravel()))
    write_json(output / "summary.json", summary)
    matplotlib_version = figures(output, columns, theory, temperature)
    write_json(provenance_path, dict(
        run_id=config["run_id"], generated_utc=datetime.now(timezone.utc).isoformat(),
        config_sha256=config_hash, source_sha256=source_hashes, input_sha256=input_hashes,
        runtime=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__,
                     matplotlib=matplotlib_version),
        offline=True, all_source_manifest_hashes_verified=True,
        artifact_sha256={path.name: digest(path) for path in sorted(output.iterdir()) if path.is_file()}))
    print(json.dumps(dict(action="generated_retrospective_description", output=str(output), rows=len(table),
                         x_range=summary["x_range"],
                         original_residual_quadratic=quadratic,
                         reconstruction_discrepancy_kJy_sr_range=summary["reconstruction_discrepancy_kJy_sr_range"]), indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/thermal_radiation_2026-10-06.json")
    parser.add_argument("--output", type=Path, default=ROOT / "build/reproductions/thermal-radiation")
    args = parser.parse_args()
    run(args.config.resolve(), args.output.resolve())
