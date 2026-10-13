"""Independently replay the frozen cantilever forecast.

The verifier uses adaptive integration and a QR fit; it does not import the
production cantilever module or read the publisher's TTHEO predictions.  Its
numerical helpers can be tested with synthetic data before response exposure.
"""
import argparse
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import subprocess

import numpy as np
from scipy.integrate import quad
from scipy.io import loadmat
from scipy.optimize import brentq


ROOT = Path(__file__).resolve().parents[1]


@lru_cache(maxsize=None)
def independent_mode(kind, number):
    """Return normalized curvature/torsional strain without production code."""
    if number < 1 or int(number) != number:
        raise ValueError("Mode number must be a positive integer")
    if kind == "torsional":
        frequency = (number - 0.5) * math.pi

        def squared_strain(z):
            return math.cos(frequency * z) ** 2

    elif kind == "flexural":
        beta = brentq(lambda x: math.cos(x) + 1.0 / math.cosh(x),
                      (number - 1) * math.pi, number * math.pi,
                      xtol=5e-15, rtol=4 * np.finfo(float).eps)
        sigma = (math.cosh(beta) + math.cos(beta)) / (math.sinh(beta) + math.sin(beta))

        def squared_strain(z):
            argument = beta * z
            curvature = (math.cosh(argument) + math.cos(argument)
                         - sigma * (math.sinh(argument) + math.sin(argument)))
            return curvature * curvature

    else:
        raise ValueError("Unknown mechanical mode")
    normalization = quad(squared_strain, 0.0, 1.0, epsabs=1e-12, epsrel=1e-12, limit=250)[0]

    def density(z):
        return squared_strain(z) / normalization

    return density


def independent_moments(kind, number):
    density = independent_mode(kind, number)
    return np.array([quad(lambda z: z ** power * density(z), 0.0, 1.0,
                          epsabs=1e-12, epsrel=1e-12, limit=250)[0]
                     for power in range(4)])


def independent_fit(delta, phi, uncertainty):
    """Fit global loss by QR, retaining only finite positive loss/error pairs."""
    delta, phi, uncertainty = [np.asarray(v, dtype=float) for v in (delta, phi, uncertainty)]
    if not (delta.shape == phi.shape == uncertainty.shape) or delta.ndim != 1:
        raise ValueError("Expected aligned one-dimensional fit inputs")
    valid = np.isfinite(delta) & np.isfinite(phi) & (phi > 0) & np.isfinite(uncertainty) & (uncertainty > 0)
    if valid.sum() < 4:
        raise ValueError("Fewer than four valid calibration points")
    x, y, error = delta[valid], phi[valid], uncertainty[valid]
    scale = max(1.0, float(np.max(np.abs(x))))
    design = np.column_stack((np.ones(len(x)), x / scale, (x / scale) ** 2))
    weighted = design / error[:, None]
    if np.linalg.matrix_rank(weighted) < 3:
        raise ValueError("Calibration quadratic is rank deficient")
    q, r = np.linalg.qr(weighted, mode="reduced")
    coefficient = np.linalg.solve(r, q.T @ (y / error)) / np.array([1.0, scale, scale ** 2])
    return coefficient, valid


def independent_loss_minimum(global_coefficient, moments, maximum_delta):
    """Find the local polynomial minimum over the entire physical interval."""
    a, b, c = np.asarray(global_coefficient, dtype=float)
    _, mu1, mu2, _ = moments
    local = np.array([a, b / mu1, c / mu2])
    if maximum_delta < 0 or not np.all(np.isfinite(local)):
        raise ValueError("Nonfinite loss or negative temperature interval")
    points = [0.0, float(maximum_delta)]
    if local[2] > 0:
        vertex = -local[1] / (2 * local[2])
        if 0 < vertex < maximum_delta:
            points.append(float(vertex))
    values = [float(np.polynomial.polynomial.polyval(point, local)) for point in points]
    selected = int(np.argmin(values))
    scale = max(abs(local[0]), abs(local[1] * maximum_delta),
                abs(local[2] * maximum_delta ** 2), 1e-30)
    return dict(local_coefficients=local, minimum=values[selected],
                minimum_at_delta=points[selected], scale=scale,
                nonnegative=values[selected] >= -1e-10 * scale)


def polynomial_extrema(coefficients, domain):
    a, b, c = (float(v) for v in coefficients)
    locations = [0.0, float(domain)]
    if c:
        stationary = -b / (2 * c)
        if 0 < stationary < domain:
            locations.append(stationary)
    values = [math.fsum((a, b * x, c * x * x)) for x in locations]
    selected = min(range(len(values)), key=values.__getitem__)
    return values[selected], locations[selected], max(abs(v) for v in values)


def independent_fit_record(delta, phi, sigma, moments, domain):
    """Reconstruct fit qualification, diagnostics and physical gate independently."""
    delta, phi, sigma = (np.asarray(v, dtype=float) for v in (delta, phi, sigma))
    output = dict(status="ineligible", eligible=False, admissible=False, reasons=[],
                  coefficients=None, input_count=len(delta), fit_count=0,
                  distinct_delta_count=0, rank=None, condition_number=None,
                  normalization_delta_K=float(domain), local_minimum=None,
                  local_minimum_location=None, local_scale=None, local_tolerance=None,
                  global_minimum=None, global_minimum_location=None, train_diagnostics=None)
    qualifications = [
        (not all(np.isfinite(v).all() for v in (delta, phi, sigma)), "nonfinite_training_values"),
        (np.any(delta < 0), "negative_training_temperature_increment"),
        (np.any(delta > domain), "training_temperature_outside_domain"),
        (np.any(phi <= 0), "nonpositive_training_loss"),
        (np.any(sigma <= 0), "nonpositive_training_uncertainty"),
        (len(delta) < 4, "fewer_than_four_training_points"),
    ]
    output["reasons"] = [reason for failed, reason in qualifications if failed]
    if output["reasons"]:
        return output
    output["distinct_delta_count"] = len(set(delta))
    if output["distinct_delta_count"] < 3:
        output["reasons"].append("fewer_than_three_distinct_temperatures")
        return output
    coefficient, valid = independent_fit(delta, phi, sigma)
    if not valid.all():
        raise ValueError("Independent fit unexpectedly discarded an accepted row")
    design = np.column_stack((np.ones(len(delta)), delta / domain, (delta / domain) ** 2))
    weighted = design * (min(sigma) / sigma)[:, None]
    singular = np.linalg.svd(weighted, compute_uv=False)
    output["rank"] = int(np.linalg.matrix_rank(weighted))
    output["condition_number"] = float(singular[0] / singular[-1])
    if output["rank"] != 3:
        output["reasons"].append("rank_deficient_weighted_design")
        return output
    local = coefficient / np.array([1.0, moments[1], moments[2]])
    local_minimum, local_location, local_scale = polynomial_extrema(local, domain)
    global_minimum, global_location, _ = polynomial_extrema(coefficient, domain)
    if local_minimum < -1e-10 * local_scale:
        output["reasons"].append("negative_local_loss_on_prediction_domain")
    if global_minimum <= 0:
        output["reasons"].append("nonpositive_global_loss_on_prediction_domain")
    fitted = np.polynomial.polynomial.polyval(delta, coefficient)
    residual = phi - fitted
    standardized = residual / sigma
    output.update(status="inadmissible" if output["reasons"] else "admissible",
                  eligible=True, admissible=not output["reasons"],
                  coefficients=coefficient.tolist(), fit_count=len(delta),
                  local_minimum=local_minimum, local_minimum_location=local_location,
                  local_scale=local_scale, local_tolerance=1e-10 * local_scale,
                  global_minimum=global_minimum, global_minimum_location=global_location,
                  train_diagnostics=dict(fitted_loss=fitted.tolist(), residuals=residual.tolist(),
                                         standardized_residuals=standardized.tolist(),
                                         mean_absolute_error=float(np.abs(residual).mean()),
                                         root_mean_squared_error=float(np.sqrt(np.mean(residual ** 2))),
                                         weighted_residual_sum_squares=float(sum(v * v for v in standardized)),
                                         degrees_of_freedom=len(delta) - 3,
                                         scope="Conditional fit diagnostics, not independent-sample significance tests"))
    return output


def independent_prediction(kind, number, global_coefficient, delta, baseline):
    """Integrate local heating and dissipation directly, avoiding moment ratios."""
    delta = float(delta)
    moments = independent_moments(kind, number)
    a, b, c = np.asarray(global_coefficient, dtype=float)
    local = np.array([a, b / moments[1], c / moments[2]])
    density = independent_mode(kind, number)
    scale = max(abs(local[0]), abs(local[1] * delta), abs(local[2] * delta ** 2), 1e-30)

    def weighted_density(z):
        return np.polynomial.polynomial.polyval(delta * z, local) / scale * density(z)

    denominator = quad(weighted_density, 0.0, 1.0, epsabs=1e-12, epsrel=1e-12, limit=250)[0]
    numerator = quad(lambda z: (baseline + delta * z) * weighted_density(z),
                     0.0, 1.0, epsabs=1e-10, epsrel=1e-12, limit=250)[0]
    return dict(phi=denominator * scale,
                temperature=numerator / denominator if denominator != 0 else float("nan"))


def compare_number(actual, expected, discrepancies, path, *, atol=2e-8, rtol=2e-8):
    """Check independently calculated values with tolerances for integration."""
    if isinstance(actual, bool) or not isinstance(actual, (float, int)):
        raise ValueError(f"Non-numerical result at {path}")
    if not math.isfinite(actual) or not math.isfinite(float(expected)):
        raise ValueError(f"Nonfinite value at {path}")
    difference = abs(actual - expected)
    relative = difference / max(abs(expected), 1e-30)
    if difference > atol + rtol * abs(expected):
        raise ValueError(f"Independent mismatch at {path}: {actual} versus {expected}")
    discrepancies.append(dict(absolute=float(difference), relative=float(relative)))


def compare_tree(actual, expected, discrepancies, path="result", *, subset=False):
    """Compare categorical structure exactly and independent floating arithmetic."""
    if isinstance(expected, dict):
        if not isinstance(actual, dict) or (not subset and set(actual) != set(expected)) or not set(expected).issubset(actual):
            raise ValueError(f"Changed dictionary fields at {path}")
        for key, value in expected.items():
            compare_tree(actual[key], value, discrepancies, path + "." + key, subset=subset)
    elif isinstance(expected, list):
        if not isinstance(actual, list) or len(actual) != len(expected):
            raise ValueError(f"Changed list membership at {path}")
        for index, value in enumerate(expected):
            compare_tree(actual[index], value, discrepancies, f"{path}[{index}]", subset=subset)
    elif isinstance(expected, (float, np.floating)):
        compare_number(actual, expected, discrepancies, path, atol=1e-12)
    elif type(actual) is not type(expected) or actual != expected:
        raise ValueError(f"Changed categorical value at {path}: {actual} versus {expected}")


def source_column(sample, field, mode):
    values = np.asarray(sample[field], dtype=float)
    count = len(sample["AVG_TAVG"])
    return values.reshape(count, -1)[:, mode - 1]


def as_nullable(value):
    value = float(value)
    return value if math.isfinite(value) else None


def independent_audit(archive):
    audit = {}
    for sample, ntrain in (("C30", 8), ("C30C", 5)):
        data = archive[sample]
        temp = [float(v) for v in data["AVG_TAVG"]]
        if not all(math.isfinite(v) and v >= 300 for v in temp):
            raise ValueError("Invalid independent temperature predictor")
        ordered = sorted(range(len(temp)), key=lambda i: (temp[i], i))
        if temp[ordered[ntrain - 1]] == temp[ordered[ntrain]]:
            raise ValueError("Unresolved temperature tie across split")
        audit[sample] = dict(n_conditions=len(temp),
                            train_rows=[i + 1 for i in ordered[:ntrain]],
                            target_rows=[i + 1 for i in ordered[ntrain:]],
                            tavg_K=temp,
                            tavg_error_K=[float(v) for v in data["AVG_TAVG_ERR"]],
                            archived_tmax_K=[float(v) for v in data["AVG_TMAX"]],
                            implied_base_K=[2 * t - float(hi) for t, hi in zip(temp, data["AVG_TMAX"])])
    return audit


def independent_balanced(cases, field):
    per_sample = {}
    for case in cases:
        available = [row[field] for row in case["rows"] if row.get(field) is not None]
        if available:
            per_sample.setdefault(case["sample"], []).append(math.fsum(available) / len(available))
    means = {key: math.fsum(values) / len(values) for key, values in per_sample.items()}
    return dict(by_preparation=means,
                equal_preparation_mean=math.fsum(means.values()) / len(means) if means else None)


def independently_score(case, archive):
    """Calculate every retained outcome and error from its original source cell."""
    prefix = "D" if case["kind"] == "flexural" else "T"
    data = archive[case["sample"]]
    temperature = source_column(data, f"AVG_{prefix}_TFLUC", case["mode"])
    temperature_error = source_column(data, f"AVG_{prefix}_TFLUC_ERR", case["mode"])
    phi = source_column(data, f"AVG_{prefix}_PHI", case["mode"])
    phi_error = source_column(data, f"AVG_{prefix}_PHI_ERR", case["mode"])
    expected = dict(sample=case["sample"], rows=[])
    for row in case["rows"]:
        index = row["row"] - 1
        observed = as_nullable(temperature[index])
        observed_phi = as_nullable(phi[index])
        predicted = row["temperature_prediction_K"]
        predicted_phi = row["phi_prediction"]
        qualifies = bool(case["fit"]["admissible"] and predicted is not None and observed is not None)
        errors = dict(observed_temperature_K=observed,
                      observed_temperature_error_K=as_nullable(temperature_error[index]),
                      observed_phi=observed_phi,
                      observed_phi_error=as_nullable(phi_error[index]),
                      qualified_temperature_target=qualifies,
                      absolute_error_K=abs(predicted - observed) if qualifies else None,
                      phi_absolute_error=abs(predicted_phi - observed_phi)
                      if predicted_phi is not None and observed_phi is not None else None)
        errors["phi_absolute_relative_error"] = (errors["phi_absolute_error"] / observed_phi
                                                 if errors["phi_absolute_error"] is not None and observed_phi > 0 else None)
        for name, comparator in row["comparators_K"].items():
            difference = abs(comparator - observed) if observed is not None else None
            errors[f"{name}_absolute_error_K"] = difference if qualifies else None
            errors[f"{name}_all_targets_error_K"] = difference
            errors[f"difference_vs_{name}_K"] = errors["absolute_error_K"] - difference if qualifies else None
        expected["rows"].append(errors)
    expected["temperature_mae_K"] = independent_balanced([expected], "absolute_error_K")["equal_preparation_mean"]
    expected["phi_mean_absolute_relative_error"] = independent_balanced([expected], "phi_absolute_relative_error")["equal_preparation_mean"]
    return expected


def verify_records(recorded, config, archive, sealed=None):
    """Replay every configured mode, target, comparator, gate and score."""
    discrepancies = []
    if recorded["schema_version"] != 1 or recorded["run_id"] != "cantilever-transfer-2026-10-13":
        raise ValueError("Changed cantilever run identity")
    sealed_numbers = []
    if sealed is not None:
        compare_tree(recorded, sealed, sealed_numbers, "prediction_seal", subset=True)
    audit = independent_audit(archive)
    compare_tree(recorded["predictor_audit"], audit, discrepancies, "predictor_audit")
    if len(recorded["analyses"]) != len(config["analyses"]):
        raise ValueError("Changed analysis membership")
    checked_modes = checked_targets = 0
    for analysis, setting in zip(recorded["analyses"], config["analyses"]):
        base_path = "analyses." + setting["name"]
        compare_tree(analysis, setting, discrepancies, base_path, subset=True)
        expected_cases = []
        for sample_name, modes in config["modes"].items():
            sample = archive[sample_name]
            temp = np.asarray(sample["AVG_TAVG"], dtype=float)
            delta = 2 * (temp - setting["t0_K"])
            domain = float(max(delta))
            for kind, numbers in modes.items():
                prefix = "D" if kind == "flexural" else "T"
                for number in numbers:
                    moments = independent_moments(kind, number)
                    phi = source_column(sample, f"AVG_{prefix}_PHI", number)
                    sigma = source_column(sample, f"AVG_{prefix}_PHI_ERR", number)
                    candidates = (list(range(1, len(temp) + 1)) if setting["all_phi"]
                                  else audit[sample_name]["train_rows"])
                    masked = ([1] if setting["publisher_mask"] and sample_name == "C30C"
                              and kind == "flexural" and number == 4 else [])
                    candidates = [row for row in candidates if row not in masked]
                    used = [row for row in candidates if math.isfinite(phi[row - 1]) and math.isfinite(sigma[row - 1])]
                    missing = [row for row in candidates if row not in used]
                    indices = np.array(used, dtype=int) - 1
                    fit = independent_fit_record(delta[indices], phi[indices], sigma[indices], moments, domain)
                    rows = []
                    for row in audit[sample_name]["target_rows"]:
                        index = row - 1
                        prediction = (independent_prediction(kind, number, fit["coefficients"],
                                                             delta[index], setting["t0_K"])
                                      if fit["coefficients"] is not None else None)
                        rows.append(dict(row=row, tavg_K=float(temp[index]),
                                         tavg_error_K=as_nullable(sample["AVG_TAVG_ERR"][index]),
                                         delta_K=float(delta[index]),
                                         tmax_model_K=float(setting["t0_K"] + delta[index]),
                                         phi_prediction=as_nullable(prediction["phi"]) if prediction else None,
                                         temperature_prediction_K=as_nullable(prediction["temperature"]) if prediction else None,
                                         comparators_K=dict(spatial_average=float(temp[index]),
                                                            cold_clamp=float(setting["t0_K"]),
                                                            uniform_local_loss=float(setting["t0_K"] + delta[index] * moments[1]))))
                    expected_cases.append(dict(sample=sample_name, kind=kind, mode=number,
                                               moments=moments.tolist(), train_rows=used,
                                               missing_train_rows=missing, masked_train_rows=masked,
                                               fit=fit, rows=rows))
        compare_tree(analysis["cases"], expected_cases, discrepancies, base_path + ".cases", subset=True)
        scored = []
        for actual_case, expected_case in zip(analysis["cases"], expected_cases):
            expected_score = independently_score(expected_case, archive)
            compare_tree(actual_case, expected_score, discrepancies, base_path + ".scores", subset=True)
            scored.append(dict(expected_score, admissible=expected_case["fit"]["admissible"]))
        fields = ["absolute_error_K", "phi_absolute_relative_error"]
        for name in ("spatial_average", "cold_clamp", "uniform_local_loss"):
            fields += [f"{name}_absolute_error_K", f"{name}_all_targets_error_K", f"difference_vs_{name}_K"]
        expected_summary = dict(attempted_modes=len(scored),
                                admissible_modes=sum(case["admissible"] for case in scored),
                                attempted_targets=sum(len(case["rows"]) for case in scored),
                                qualified_temperature_targets=sum(row["qualified_temperature_target"] for case in scored for row in case["rows"]),
                                scores={field: independent_balanced(scored, field) for field in fields},
                                interpretation="Scores on admissible modes are conditional; invalid local-loss fits remain model failures. No inferential p-values or population replication claim.")
        compare_tree(analysis["summary"], expected_summary, discrepancies, base_path + ".summary")
        checked_modes += len(scored)
        checked_targets += sum(len(case["rows"]) for case in scored)
    return dict(verified=True, independently_checked_numbers=len(discrepancies),
                checked_prediction_seal_numbers=len(sealed_numbers),
                maximum_absolute_discrepancy=max((d["absolute"] for d in discrepancies), default=0),
                maximum_relative_discrepancy=max((d["relative"] for d in discrepancies), default=0),
                checked_analysis_modes=checked_modes, checked_analysis_targets=checked_targets,
                all_mode_membership_physical_gates_comparators_and_scores_checked=True,
                method="Independent roots/adaptive quadrature, QR weighted fits, analytic local/global extrema, direct spatial integration and source-cell outcome replay; no production-module import or publisher TTHEO use")


def verify_execution(directory):
    """Require every recorded source/input byte to match its execution freeze."""
    execution = json.loads((Path(directory) / "execution.json").read_text())
    for item in execution["sources"]:
        frozen = subprocess.check_output(["git", "show", f"{execution['freeze_commit']}:{item['path']}"], cwd=ROOT)
        if hashlib.sha256(frozen).hexdigest() != item["sha256"] or (ROOT / item["path"]).read_bytes() != frozen:
            raise ValueError(f"Source differs from execution freeze: {item['path']}")
    for item in execution["inputs"]:
        if hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError(f"Changed cantilever input: {item['path']}")
    return execution


def verify(directory):
    directory = Path(directory)
    execution = verify_execution(directory)
    config_path = "configs/cantilever_2026-10-13.json"
    required = {config_path, "docs/cantilever-protocol-2026-10-13.md",
                "src/orthopolity/cantilever.py", "experiments/run_cantilever.py",
                "experiments/fetch_cantilever.py", "tests/test_cantilever.py",
                "tests/test_cantilever_runner.py", "data/cantilever/2026-10-13/predictor-audit.json"}
    if not required.issubset(item["path"] for item in execution["sources"]):
        raise ValueError("Incomplete recorded design source manifest")
    config = json.loads((ROOT / config_path).read_text())
    if config["inputs"] != execution["inputs"]:
        raise ValueError("Changed input inventory")
    prediction_path = execution["predictions"]["path"]
    prediction_body = (ROOT / prediction_path).read_bytes()
    prediction_commit = execution["prediction_commit"]
    if (prediction_body != subprocess.check_output(["git", "show", f"{prediction_commit}:{prediction_path}"], cwd=ROOT)
            or hashlib.sha256(prediction_body).hexdigest() != execution["predictions"]["sha256"]):
        raise ValueError("Changed committed prediction seal")
    subprocess.run(["git", "merge-base", "--is-ancestor", execution["freeze_commit"], prediction_commit], cwd=ROOT, check=True)
    recorded = json.loads((directory / "result.json").read_text())
    sealed = json.loads(prediction_body)
    archive = loadmat(ROOT / "data/cantilever/2026-10-13/data.mat", simplify_cells=True)
    output = verify_records(recorded, config, archive, sealed)
    audit = json.loads((ROOT / "data/cantilever/2026-10-13/predictor-audit.json").read_text())
    if recorded["predictor_audit"] != audit:
        raise ValueError("Changed frozen predictor audit")
    output.update(input_checksums_verified=True, execution_freeze_verified=True,
                  committed_prediction_seal_verified=True)
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    verified = verify(args.directory)
    body = json.dumps(verified, sort_keys=True, indent=2, allow_nan=False) + "\n"
    if args.write:
        destination = args.directory / "verification.json"
        if destination.exists() and destination.read_text() != body:
            raise ValueError("Refusing to replace changed cantilever verification")
        destination.write_text(body)
    print(body)
