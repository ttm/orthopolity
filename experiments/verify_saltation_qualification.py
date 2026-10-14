"""Independent numerical verification of synthetic saltation qualification.

No production saltation helpers are imported and no workbook is opened. The
only responses reconstructed here are synthetic. Active-set fits use weighted
two-column least squares, not the production stationary-threshold formula.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
REPRESENTATIVE_REPLICATES = (0, 17, 499)


def predicted_flux(stresses, coefficient, threshold, exponent):
    """Evaluate the two declared laws without importing their implementation."""
    x = np.asarray(stresses, dtype=float)
    if exponent == 0:
        multiplier = np.ones_like(x)
    elif exponent == 0.5:
        multiplier = np.sqrt(x)
    else:
        raise ValueError("Only the two frozen exponents are supported")
    return coefficient * multiplier * np.clip(x - threshold, 0, None)


def balanced_weights(dates):
    groups = {day: [i for i, value in enumerate(dates) if value == day]
              for day in sorted(set(dates))}
    weights = np.empty(len(dates))
    for indices in groups.values():
        weights[indices] = 1.0 / len(groups) / len(indices)
    return weights


def weighted_mse(observed, fitted, weights):
    return math.fsum(float(w) * (float(y) - float(p)) ** 2
                     for y, p, w in zip(observed, fitted, weights))


def independent_fit(stresses, response, weights, exponent):
    """Enumerate hinge intervals and solve their two linear coefficients.

    Within an active set, y = C*x**(a+1) + D*x**a, with threshold
    -D/C. Interior feasible unconstrained least-squares solutions and all
    one-column boundary fits contain a global constrained optimum. Every
    candidate is scored against all rows, including inactive observations.
    """
    x, y, w = [np.asarray(v, dtype=float) for v in
               (stresses, response, weights)]
    if (x.ndim != 1 or len(x) < 2 or x.shape != y.shape or x.shape != w.shape
            or not all(np.isfinite(v).all() for v in (x, y, w))
            or np.any(x <= 0) or np.any(y < 0) or np.any(w <= 0)):
        raise ValueError("Finite, aligned physical fitting arrays required")
    multiplier = predicted_flux(x, 1.0, 0.0, exponent) / x
    boundaries = sorted({0.0, *map(float, x)})
    candidates = []
    for threshold in boundaries:
        shape = predicted_flux(x, 1.0, threshold, exponent)
        design = (np.sqrt(w) * shape)[:, None]
        coefficient = max(0.0, float(np.linalg.lstsq(
            design, np.sqrt(w) * y, rcond=None)[0][0]))
        candidates.append((coefficient, threshold))
    for lower, upper in zip(boundaries[:-1], boundaries[1:]):
        active = x > lower
        design = np.column_stack((multiplier[active] * x[active],
                                  multiplier[active]))
        design *= np.sqrt(w[active])[:, None]
        coefficients, _, rank, _ = np.linalg.lstsq(
            design, np.sqrt(w[active]) * y[active], rcond=None)
        if rank != 2 or coefficients[0] <= 0:
            continue
        threshold = float(-coefficients[1] / coefficients[0])
        if lower < threshold < upper:
            candidates.append((float(coefficients[0]), threshold))
    scored = [dict(coefficient=c, threshold=t, exponent=float(exponent),
                   mse=weighted_mse(y, predicted_flux(x, c, t, exponent), w))
              for c, t in candidates]
    return min(scored, key=lambda candidate: candidate["mse"])


def independent_factors(generator, dates, total_cv, replicates):
    """Rebuild the frozen draw order using explicit standard-normal draws."""
    unique_dates = sorted(set(dates))
    positions = np.array([unique_dates.index(day) for day in dates])
    # Product moments, computed independently of the production log-variance
    # subtraction, determine the interval factor's variance.
    day_cv = total_cv / 2.0
    day_log_variance = math.log1p(day_cv * day_cv)
    residual_cv_squared = ((total_cv * total_cv - day_cv * day_cv)
                           / (1.0 + day_cv * day_cv))
    interval_log_variance = math.log1p(residual_cv_squared)
    day_standard = generator.standard_normal((replicates, len(unique_dates)))
    interval_standard = generator.standard_normal((replicates, len(dates)))
    day_logs = (math.sqrt(day_log_variance) * day_standard
                - day_log_variance / 2.0)
    interval_logs = (math.sqrt(interval_log_variance) * interval_standard
                     - interval_log_variance / 2.0)
    return np.exp(day_logs[:, positions] + interval_logs)


def verify_result(result_path, config_path):
    result_path, config_path = Path(result_path), Path(config_path)
    result = json.loads(result_path.read_text())
    config = json.loads(config_path.read_text())
    if result["run_id"] != config["run_id"]:
        raise ValueError("Result/configuration identity mismatch")
    if (result["actual_flux_values_read"] is not False
            or result["evidence_kind"] != "synthetic_design_qualification"):
        raise ValueError("Unexpected result evidence kind")
    calibration, prediction = (result["calibration_predictors"],
                               result["prediction_predictors"])
    if not calibration or not prediction:
        raise ValueError("Both predictor subsets are required")
    for group in (calibration, prediction):
        if len({row["date"] for row in group}) < config["minimum_days_per_split"]:
            raise ValueError("Insufficient eligible day support")
        for row in group:
            if (row["site"] != config["primary_site"]
                    or not math.isfinite(row["tau"]) or row["tau"] <= 0
                    or abs(row["theta"]) > config["max_abs_theta_degrees"]
                    or abs(row["zL"]) > config["max_abs_zL"]):
                raise ValueError("Saved predictor violates eligibility")
    if max(row["date"] for row in calibration) >= min(row["date"] for row in prediction):
        raise ValueError("Temporal subsets overlap or are reversed")
    records = calibration + prediction
    if len({(r["site"], r["date"], r["StartTime"]) for r in records}) != len(records):
        raise ValueError("Duplicate saved observation")
    dates = [row["date"] for row in records]
    stresses = np.array([row["tau"] for row in records])
    n = len(calibration)
    calibration_weights = balanced_weights(dates[:n])
    prediction_weights = balanced_weights(dates[n:])
    generator = np.random.Generator(np.random.PCG64(config["seed"]))
    checked = 0
    largest_absolute = largest_scaled = 0.0
    discrepancies = []
    representative_fits = []

    def compare(expected, actual, label, rtol=1e-10, atol=1e-14):
        nonlocal checked, largest_absolute, largest_scaled
        expected, actual = np.asarray(expected), np.asarray(actual)
        if expected.shape != actual.shape:
            discrepancies.append(dict(label=label, reason="shape mismatch"))
            return
        checked += int(expected.size)
        difference = np.abs(expected - actual)
        if difference.size:
            largest_absolute = max(largest_absolute, float(np.max(difference)))
            largest_scaled = max(largest_scaled, float(np.max(
                difference / np.maximum(1.0, np.abs(expected)))))
        if not np.allclose(expected, actual, rtol=rtol, atol=atol):
            discrepancies.append(dict(label=label, maximum_absolute_difference=
                                      float(np.max(difference))))

    expected_keys = [(cv, threshold, exponent)
                     for cv in config["noise_cv"]
                     for threshold in config["thresholds_Pa"]
                     for exponent in config["exponents"]]
    actual_keys = [(s["noise_cv"], s["threshold_Pa"], s["generating_exponent"])
                   for s in result["scenarios"]]
    if actual_keys != expected_keys:
        raise ValueError("Unexpected scenario order or coverage")
    reconstructed_rates = []
    scenario_index = 0
    for cv in config["noise_cv"]:
        factors = independent_factors(generator, dates, cv, config["replicates"])
        for threshold in config["thresholds_Pa"]:
            for truth in config["exponents"]:
                scenario = result["scenarios"][scenario_index]
                scenario_index += 1
                label = f"cv={cv}/threshold={threshold}/truth={truth}"
                repetitions = config["replicates"]
                parameters = np.asarray(scenario["calibration_parameters"], dtype=float)
                saved_scores = np.asarray(scenario["test_mse"], dtype=float)
                if (parameters.shape != (repetitions, 2, 2)
                        or saved_scores.shape != (repetitions, 2)
                        or not np.isfinite(parameters).all()
                        or not np.isfinite(saved_scores).all()):
                    raise ValueError("Unexpected saved simulation arrays")
                if (np.any(parameters[:, :, 0] < 0)
                        or np.any(parameters[:, :, 1] < 0)
                        or np.any(parameters[:, :, 1] > max(stresses[:n]))):
                    raise ValueError("Saved fit is outside physical bounds")
                baseline = predicted_flux(stresses, 1.0, threshold, truth)
                scores = np.empty_like(saved_scores)
                correct = ties = 0
                for replicate in range(repetitions):
                    observed = baseline * factors[replicate]
                    for model, exponent in enumerate(config["exponents"]):
                        coefficient, fitted_threshold = parameters[replicate, model]
                        predicted = predicted_flux(stresses[n:], coefficient,
                                                   fitted_threshold, exponent)
                        scores[replicate, model] = weighted_mse(
                            observed[n:], predicted, prediction_weights)
                        if replicate in REPRESENTATIVE_REPLICATES:
                            fit = independent_fit(stresses[:n], observed[:n],
                                                  calibration_weights, exponent)
                            fit_label = label + f"/replicate={replicate}/model={exponent}"
                            compare([fit["coefficient"], fit["threshold"]],
                                    parameters[replicate, model], fit_label + "/parameters",
                                    rtol=5e-8, atol=1e-10)
                            independent_prediction = predicted_flux(
                                stresses[n:], fit["coefficient"], fit["threshold"], exponent)
                            compare(independent_prediction, predicted,
                                    fit_label + "/predictions", rtol=5e-8, atol=1e-10)
                            compare(fit["mse"], weighted_mse(observed[:n],
                                    predicted_flux(stresses[:n], coefficient,
                                                   fitted_threshold, exponent), calibration_weights),
                                    fit_label + "/calibration_mse", rtol=1e-8, atol=1e-14)
                            representative_fits.append(dict(scenario=label,
                                replicate=replicate, model_exponent=exponent, **fit))
                    left, right = scores[replicate]
                    tolerance = config["tie_relative_tolerance"] * max(left, right, 1e-300)
                    if abs(left - right) <= tolerance:
                        ties += 1
                    else:
                        selected = config["exponents"][0 if left < right else 1]
                        correct += int(selected == truth)
                compare(scores, saved_scores, label + "/all_test_mse")
                compare([correct, ties, repetitions],
                        [scenario["correct"], scenario["ties"], scenario["replicates"]],
                        label + "/selection_counts", rtol=0, atol=0)
                rate = correct / repetitions
                compare(rate, scenario["correct_fraction"], label + "/correct_fraction",
                        rtol=0, atol=0)
                compare(math.sqrt(rate * (1-rate) / repetitions),
                        scenario["monte_carlo_standard_error"], label + "/monte_carlo_se")
                if cv == config["primary_noise_cv"]:
                    reconstructed_rates.append(rate)
    passed = all(rate >= config["required_correct_fraction"] for rate in reconstructed_rates)
    expected_gate = dict(passed=passed,
        required_correct_fraction=config["required_correct_fraction"],
        primary_noise_cv=config["primary_noise_cv"],
        minimum_correct_fraction=min(reconstructed_rates),
        action="eligible_for_separate_real_response_protocol" if passed else "stop_before_real_response_fitting")
    if expected_gate != result["gate"]:
        discrepancies.append(dict(label="gate", reason="reconstructed gate mismatch"))
    return dict(verified=not discrepancies, checked_numbers=checked,
        maximum_absolute_difference=largest_absolute,
        maximum_scaled_difference=largest_scaled, discrepancies=discrepancies,
        scenarios_checked=len(expected_keys), scores_checked=len(expected_keys) * config["replicates"] * 2,
        independent_fits=representative_fits,
        representative_replicates=list(REPRESENTATIVE_REPLICATES), gate=expected_gate,
        actual_flux_values_read=False,
        inputs=[dict(name=path.name,
                     sha256=hashlib.sha256(path.read_bytes()).hexdigest())
                for path in (result_path, config_path)],
        method="Independent PCG64 draw reconstruction, product-moment noise, scalar weighted score sums, and active-set weighted two-column least squares",
        scope="Checks all saved synthetic prediction scores, selection counts and gate; independently fits three replicates per scenario. Uses saved wind predictors and does not certify workbook extraction, metrology, temporal independence, or noise realism.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--config", type=Path,
                        default=ROOT / "configs/saltation_qualification_2026-10-14.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("Use an unused verification output path")
    report = verify_result(args.result, args.config)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps({key: value for key, value in report.items()
                      if key != "independent_fits"}, indent=2))
    if not report["verified"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
