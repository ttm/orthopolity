"""Reproduce fixed-design composite-resource identification and transfer.

Analytic predictions precede every random draw.  This is a specified synthetic
experiment, not an empirical discovery or a test of a general natural law.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import gzip
import hashlib
import io
import json
from pathlib import Path
import platform

import numpy as np
import scipy
from scipy.stats import norm

from orthopolity.inverse_resources import (
    design_geometry, fit_composition, fixed_design_error_bound,
    heldout_prediction, target_weights,
)


ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def design(config):
    """Resolve the declared three-environment design without random sampling."""
    matrix = np.asarray(config["constituent_exponents"], dtype=float)
    theta = np.asarray(config["coefficient_truth"], dtype=float)
    alternative = np.asarray(config["heldout_alternative_coefficient"], dtype=float)
    offsets = np.asarray(config["known_constraint_slopes"], dtype=float)
    errors = np.asarray(config["slope_standard_errors"], dtype=float)
    correlation = np.asarray(config["slope_correlation"], dtype=float)
    if (matrix.shape != (3, 2) or theta.shape != (2,) or alternative.shape != (2,)
            or offsets.shape != (3,) or errors.shape != (3,) or correlation.shape != (3, 3)):
        raise ValueError("this demonstration needs three environments and two constituents")
    if (config["calibration_environments"] != [0, 1] or config["heldout_environment"] != 2):
        raise ValueError("calibration must be environments 0,1 and held-out environment 2")
    if (not all(np.isfinite(value).all() for value in
                (matrix, theta, alternative, offsets, errors, correlation))
            or np.any(errors <= 0) or not np.allclose(np.diag(correlation), 1)):
        raise ValueError("finite design and positive marginal errors with unit correlation diagonal required")
    for key, minimum in (("replicates", 2), ("seed", 0)):
        if isinstance(config[key], bool) or not isinstance(config[key], int) or config[key] < minimum:
            raise ValueError(f"{key} must be an integer >= {minimum}")
    for key in ("near_collinear_epsilon", "slope_perturbation_l2"):
        if not np.isfinite(config[key]) or config[key] <= 0:
            raise ValueError(f"{key} must be finite and positive")
    if not 0 < config["interval_probability"] < 1:
        raise ValueError("interval_probability must lie strictly between zero and one")
    covariance = errors[:, None] * correlation * errors[None, :]
    truth = matrix @ theta + offsets
    fit = fit_composition(matrix[:2], truth[:2], offsets=offsets[:2],
                          covariance=covariance[:2, :2], rcond=config["rank_rcond"])
    forecast = heldout_prediction(matrix[:2], matrix[2], truth, offsets=offsets,
                                  joint_covariance=covariance, rcond=config["rank_rcond"])
    alternative_truth = truth.copy()
    alternative_truth[-1] = matrix[-1] @ alternative + offsets[-1]
    return dict(matrix=matrix, theta=theta, alternative=alternative, offsets=offsets,
                covariance=covariance, truth=truth, alternative_truth=alternative_truth,
                fit=fit, forecast=forecast,
                critical_value=float(norm.ppf((1 + config["interval_probability"]) / 2)))


def structural_examples(config):
    """Exact partial-identification and perturbation consequences."""
    deficient = np.array([[1., 1.], [2., 2.]])
    compatible = np.array([[1., .5], [.25, 1.25]])
    target = np.array([3., 3.])
    geometry = design_geometry(deficient, rcond=config["rank_rcond"])
    weights = target_weights(deficient, target, rcond=config["rank_rcond"])
    try:
        target_weights(deficient, [1., 0.], rcond=config["rank_rcond"])
    except ValueError:
        unidentifiable_target_rejected = True
    else:
        raise AssertionError("rank-deficient design unexpectedly identified a component")
    epsilon = config["near_collinear_epsilon"]
    perturbation = np.array([0., config["slope_perturbation_l2"]])
    conditions = []
    for name, matrix in (("separated", np.array([[1., 1.], [1., 2.]])),
                         ("nearly_proportional", np.array([[1., 1.], [1., 1. + epsilon]]))):
        item = design_geometry(matrix, rcond=config["rank_rcond"])
        effect = item["pseudoinverse"] @ perturbation
        conditions.append(dict(name=name, design=matrix.tolist(), rank=item["rank"],
            singular_values=item["singular_values"].tolist(), condition_number=item["condition_number"],
            corrected_slope_perturbation=perturbation.tolist(),
            coefficient_perturbation=effect.tolist(),
            coefficient_perturbation_l2=float(np.linalg.norm(effect)),
            coefficient_error_bound=fixed_design_error_bound(matrix, perturbation,
                                                             rcond=config["rank_rcond"])))
    return dict(partial_identification=dict(design=deficient.tolist(), rank=geometry["rank"],
        compatible_coefficients=compatible.tolist(),
        identical_corrected_slopes=(deficient @ compatible.T).T.tolist(),
        identified_target=target.tolist(), target_weights=weights.tolist(),
        target_prediction=float(weights @ (deficient @ compatible[0])),
        unidentifiable_target=[1., 0.],
        unidentifiable_target_rejected=unidentifiable_target_rejected), conditioning=conditions)


def predictions(config, model):
    forecast, fit = model["forecast"], model["fit"]
    shift = float(model["alternative_truth"][-1] - model["truth"][-1])
    noncentrality = shift / forecast["standard_error"]
    cutoff = model["critical_value"]
    alternative_coverage = float(norm.cdf(cutoff - noncentrality) - norm.cdf(-cutoff - noncentrality))
    return dict(run_id=config["run_id"], scope=config["scope"],
        status="analytic_predictions_from_fixed_inputs_before_stochastic_simulation",
        model="b=alpha-v=D theta; two calibration environments, one held-out environment",
        design=model["matrix"].tolist(), known_constraint_slopes=model["offsets"].tolist(),
        true_slopes=model["truth"].tolist(), true_corrected_slopes=(model["truth"] - model["offsets"]).tolist(),
        joint_corrected_slope_covariance=model["covariance"].tolist(),
        exact_recovered_coefficients=fit["theta"].tolist(),
        coefficient_covariance=fit["covariance"].tolist(),
        calibration_estimator=fit["estimator"].tolist(),
        heldout_weights=forecast["weights"].tolist(), contrast_weights=forecast["contrast_weights"].tolist(),
        heldout_mean_prediction=forecast["prediction"],
        contrast_variance=forecast["variance"], contrast_standard_error=forecast["standard_error"],
        prediction_variance=forecast["prediction_variance"],
        shared_composition_expected_z_mean=0., shared_composition_expected_z_variance=1.,
        interval_probability=config["interval_probability"], standard_normal_critical_value=cutoff,
        expected_coverage_monte_carlo_standard_error=float(np.sqrt(
            config["interval_probability"] * (1 - config["interval_probability"]) / config["replicates"])),
        changed_heldout_composition=dict(coefficient=model["alternative"].tolist(),
            true_slopes=model["alternative_truth"].tolist(), mean_residual=shift,
            expected_z_mean=noncentrality, expected_z_variance=1.,
            expected_interval_coverage=alternative_coverage,
            expected_two_sided_rejection_probability=1 - alternative_coverage),
        **structural_examples(config))


def simulate(config, model):
    rng = np.random.default_rng(config["seed"])
    noise = rng.multivariate_normal(np.zeros(3), model["covariance"], size=config["replicates"])
    observed = model["truth"] + noise
    alternative = model["alternative_truth"] + noise
    corrected_calibration = observed[:, :2] - model["offsets"][:2]
    estimated = corrected_calibration @ model["fit"]["estimator"].T
    predicted = corrected_calibration @ model["forecast"]["weights"] + model["offsets"][-1]
    residual = observed[:, -1] - predicted
    alternative_residual = alternative[:, -1] - predicted
    z = residual / model["forecast"]["standard_error"]
    alternative_z = alternative_residual / model["forecast"]["standard_error"]
    return dict(replicate=np.arange(config["replicates"]), alpha_1=observed[:, 0],
        alpha_2=observed[:, 1], alpha_3_shared=observed[:, 2], alpha_3_changed=alternative[:, 2],
        theta_1=estimated[:, 0], theta_2=estimated[:, 1], predicted_alpha_3=predicted,
        z_shared=z, z_changed=alternative_z)


def write_replicates(path, columns):
    # Fix gzip metadata so equal environments/seeds produce byte-identical output.
    with path.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            with io.TextIOWrapper(compressed, encoding="utf-8", newline="") as stream:
                writer = csv.writer(stream)
                writer.writerow(columns)
                writer.writerows(zip(*columns.values(), strict=True))


def summarize(config, model, forecast, columns):
    estimates = np.column_stack((columns["theta_1"], columns["theta_2"]))
    scenarios = {}
    for name, key in (("shared_composition", "z_shared"), ("changed_heldout_composition", "z_changed")):
        z = columns[key]
        coverage = float(np.mean(np.abs(z) <= model["critical_value"]))
        scenarios[name] = dict(z_mean=float(np.mean(z)), z_sample_variance=float(np.var(z, ddof=1)),
            interval_coverage=coverage, two_sided_rejection_fraction=1 - coverage,
            mean_residual=float(np.mean(z) * model["forecast"]["standard_error"]))
    return dict(run_id=config["run_id"], kind=config["kind"], scope=config["scope"],
        seed=config["seed"], replicates=config["replicates"],
        exact_recovered_coefficients=forecast["exact_recovered_coefficients"],
        heldout_identity="b3=3*b1-b2; alpha3=3*(alpha1-v1)-(alpha2-v2)+v3",
        true_heldout_slope=float(model["truth"][-1]),
        predicted_heldout_mean=forecast["heldout_mean_prediction"],
        contrast_standard_error=forecast["contrast_standard_error"],
        coefficient_mean=estimates.mean(axis=0).tolist(),
        coefficient_sample_covariance=np.cov(estimates, rowvar=False).tolist(),
        coefficient_analytic_covariance=forecast["coefficient_covariance"],
        **scenarios, changed_heldout_expected_rejection_probability=forecast[
            "changed_heldout_composition"]["expected_two_sided_rejection_probability"],
        partial_identification=forecast["partial_identification"], conditioning=forecast["conditioning"],
        interpretation="Coverage and power are synthetic checks under the specified Gaussian error model; rejection diagnoses incompatibility with the declared shared composition and other fixed assumptions, not a universal-law verdict",
        paired_errors_between_scenarios=True,
        uncertainty_scope="Known joint slope covariance and exact fixed design/offsets; no constituent-exponent measurement uncertainty or latent heterogeneous moment estimated")


def figures(output, config, model, forecast, columns):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9,
        "axes.titlesize": 10, "svg.fonttype": "none", "svg.hashsalt": config["run_id"]})
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 6.0), layout="constrained")
    blue, orange = "#285f9b", "#b9532e"
    ax = axes[0, 0]
    ax.plot(columns["theta_1"][:1500], columns["theta_2"][:1500], ".", ms=1.7, alpha=.2, color=blue)
    ax.plot(*model["theta"], marker="+", color="black", ms=10, mew=1.6)
    ax.set(xlabel="Estimated θ₁", ylabel="Estimated θ₂", title="a  Shared composition recovered")

    ax = axes[0, 1]
    shared = columns["z_shared"]
    shifted = columns["z_changed"]
    ax.hist(shared, bins=55, density=True, color=blue, alpha=.65, label="Shared composition")
    ax.hist(shifted, bins=55, density=True, color=orange, alpha=.5, label="Changed held-out composition")
    grid = np.linspace(min(shared.min(), shifted.min()), max(shared.max(), shifted.max()), 400)
    ax.plot(grid, norm.pdf(grid), color=blue)
    ax.plot(grid, norm.pdf(grid - forecast["changed_heldout_composition"]["expected_z_mean"]), color=orange)
    for value in (-model["critical_value"], model["critical_value"]):
        ax.axvline(value, color="black", linestyle=":", lw=.8)
    ax.set(xlabel="Standardized held-out residual", ylabel="Density", title="b  Transfer tests a shared resource")
    ax.legend(frameon=False, fontsize=7)

    ax = axes[1, 0]
    x = np.linspace(-.25, 1.75, 100)
    ax.plot(x, 1.5 - x, color=blue, label="θ₁ + θ₂ = 1.5")
    ax.plot([1, .25], [.5, 1.25], "o", color=orange)
    ax.set(xlabel="θ₁", ylabel="θ₂", title="c  One identified combination")
    ax.text(.04, .06, "Target 3θ₁ + 3θ₂ = 4.5\nIndividual coefficients unresolved",
            transform=ax.transAxes, fontsize=8)
    ax.legend(frameon=False, fontsize=8)

    ax = axes[1, 1]
    conditions = forecast["conditioning"]
    ax.bar([0, 1], [row["coefficient_perturbation_l2"] for row in conditions], width=.48,
           color=[blue, orange], label="Actual coefficient error")
    ax.plot([0, 1], [row["coefficient_error_bound"] for row in conditions], "_", ms=22,
            mew=1.8, color="black", label="Fixed-design bound")
    ax.set_xticks([0, 1], ["Separated", "Nearly proportional"])
    ax.set(yscale="log", ylabel="Coefficient error ‖δθ‖₂", title="d  Identifiability needs precision")
    ax.text(.04, .96, "Same slope error: ‖δb‖₂ = 0.001", transform=ax.transAxes,
            va="top", fontsize=8)
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    for ax in axes.flat:
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(alpha=.15)
    fig.suptitle("Synthetic fixed-design inverse-resource demonstration", fontsize=11)
    fig.savefig(output / "inverse-resources.png", dpi=220, bbox_inches="tight", pad_inches=.06)
    fig.savefig(output / "inverse-resources.svg", metadata={"Date": None}, bbox_inches="tight", pad_inches=.06)
    plt.close(fig)
    svg = output / "inverse-resources.svg"
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines()) + "\n")
    return matplotlib.__version__


def run(config_path, output):
    config = json.loads(config_path.read_text())
    source_paths = (Path(__file__), ROOT / "src/orthopolity/inverse_resources.py",
                    ROOT / "tests/test_inverse_resources.py")
    source_hashes = {str(path.relative_to(ROOT)): digest(path) for path in source_paths}
    provenance_path = output / "provenance.json"
    if provenance_path.exists():
        retained = json.loads(provenance_path.read_text())
        if retained["config_sha256"] != digest(config_path) or retained["source_sha256"] != source_hashes:
            raise ValueError("retained inputs changed; preserve this run and choose another output directory")
        if not all((output / path).exists() and digest(output / path) == checksum
                   for path, checksum in retained["artifact_sha256"].items()):
            raise ValueError("retained artifacts changed; preserve this run and choose another output directory")
        print(json.dumps(dict(action="audited_existing_run", output=str(output))))
        return
    if output.exists() and any(output.iterdir()):
        raise ValueError("output directory is not empty; preserve it and choose another directory")
    model = design(config)
    forecast = predictions(config, model)
    output.mkdir(parents=True, exist_ok=True)
    (output / "config.json").write_bytes(config_path.read_bytes())
    write_json(output / "predictions.json", forecast)
    forecast_hash = digest(output / "predictions.json")
    columns = simulate(config, model)
    write_replicates(output / "replicates.csv.gz", columns)
    summary = summarize(config, model, forecast, columns)
    summary["predictions_sha256"] = forecast_hash
    write_json(output / "summary.json", summary)
    matplotlib_version = figures(output, config, model, forecast, columns)
    write_json(provenance_path, dict(run_id=config["run_id"], generated_utc=datetime.now(timezone.utc).isoformat(),
        config_sha256=digest(config_path), source_sha256=source_hashes, input_sha256={},
        runtime=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__,
                     matplotlib=matplotlib_version),
        predictions_written_before_stochastic_simulation=True,
        empirical_inputs=False, retrospective_configuration=True,
        exposure="Mathematical example and analytic expectations known before simulation; no empirical holdout or external preregistration claimed",
        artifact_sha256={path.name: digest(path) for path in sorted(output.iterdir()) if path.is_file()}))
    print(json.dumps(dict(action="generated_synthetic_demonstration", output=str(output),
        exact_recovered_coefficients=summary["exact_recovered_coefficients"],
        contrast_standard_error=summary["contrast_standard_error"],
        shared=summary["shared_composition"], alternative=summary["changed_heldout_composition"]), indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/inverse_resources_2026-10-06.json")
    parser.add_argument("--output", type=Path, default=ROOT / "build/reproductions/inverse-resources")
    args = parser.parse_args()
    run(args.config.resolve(), args.output.resolve())
