"""Independent numerical checks for the frozen adsorption transfer.

This file deliberately does not import the production adsorption module. Its
Peng--Robinson chemical potentials are numerical derivatives of extensive
residual Gibbs energy; its binary IAST calculation solves for adsorbed
composition. The pure-data fit eliminates capacity analytically. These helpers
can be tested on synthetic inputs before any real-response exposure.
"""
from __future__ import annotations

import math
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.optimize import brentq, minimize, minimize_scalar


def _component_arrays(temperatures, pressures, acentric, composition):
    tc, pc, omega, y = [np.asarray(v, dtype=float) for v in
                        (temperatures, pressures, acentric, composition)]
    if tc.ndim != 1 or not (tc.shape == pc.shape == omega.shape == y.shape):
        raise ValueError("Aligned one-dimensional component inputs required")
    if len(tc) < 1 or not all(np.isfinite(v).all() for v in (tc, pc, omega, y)):
        raise ValueError("Finite component inputs required")
    if np.any(tc <= 0) or np.any(pc <= 0) or np.any(y < 0) or y.sum() <= 0:
        raise ValueError("Positive critical constants and nonnegative composition required")
    return tc, pc, omega, y / y.sum()


def residual_gibbs_rt(pressure_bar, temperature_K, composition,
                      critical_temperatures_K, critical_pressures_bar,
                      acentric_factors, kij=0.0):
    """Molar residual Gibbs energy / RT, using the largest physical PR root.

    A separate phase-eligibility assessment is required: selecting the vapor
    root is not a vapor-phase stability proof.
    """
    if not np.isfinite(pressure_bar) or pressure_bar < 0:
        raise ValueError("Nonnegative finite pressure required")
    if not np.isfinite(temperature_K) or temperature_K <= 0:
        raise ValueError("Positive finite temperature required")
    tc, pc, omega, y = _component_arrays(critical_temperatures_K,
                                        critical_pressures_bar,
                                        acentric_factors, composition)
    interaction = np.asarray(kij, dtype=float)
    if interaction.ndim == 0:
        interaction = np.full((len(y), len(y)), float(interaction))
        np.fill_diagonal(interaction, 0.0)
    if interaction.shape != (len(y), len(y)) or not np.isfinite(interaction).all():
        raise ValueError("Finite scalar or square interaction coefficients required")
    if not np.allclose(interaction, interaction.T, atol=1e-14, rtol=0):
        raise ValueError("Symmetric interaction matrix required")
    if not np.allclose(np.diag(interaction), 0, atol=1e-14, rtol=0):
        raise ValueError("Interaction matrix diagonal must be zero")
    if pressure_bar == 0:
        return 0.0
    # Divide attraction by R^2 and covolume by R; no numerical R is needed.
    kappa = 0.37464 + 1.54226 * omega - 0.26992 * omega ** 2
    alpha = (1 + kappa * (1 - np.sqrt(temperature_K / tc))) ** 2
    attraction = 0.45724 * tc ** 2 / pc * alpha
    cross = np.sqrt(np.outer(attraction, attraction)) * (1 - interaction)
    a = float(y @ cross @ y) * pressure_bar / temperature_K ** 2
    b = float(y @ (0.07780 * tc / pc)) * pressure_bar / temperature_K
    # Polynomial's coefficient order differs from np.roots used conventionally.
    polynomial = np.polynomial.Polynomial(
        [-a * b + b ** 2 + b ** 3, a - 2 * b - 3 * b ** 2,
         b - 1, 1.0])
    candidates = [float(z.real) for z in polynomial.roots()
                  if abs(z.imag) < 1e-9 and z.real > b]
    if not candidates:
        raise ValueError("No physical Peng--Robinson vapor root")
    z = max(candidates)
    sqrt2 = math.sqrt(2.0)
    # log1p avoids cancellation in both the dilute-gas limit and ratio.
    logarithm = math.log1p(2 * sqrt2 * b / (z + (1 - sqrt2) * b))
    return (z - 1 - math.log(z - b)
            - a / (2 * sqrt2 * b) * logarithm)


def pr_fugacity_coefficients(pressure_bar, temperature_K, composition,
                             critical_temperatures_K, critical_pressures_bar,
                             acentric_factors, kij=0.0, *, step=2e-4):
    """Differentiate N G^R/(N RT) with respect to each component amount.

    Five-point finite differences are independent of the analytic partial
    molar expression. A one-sided formula handles zero mole fractions.
    """
    _, _, _, amounts = _component_arrays(critical_temperatures_K,
                                         critical_pressures_bar,
                                         acentric_factors, composition)
    if not math.isfinite(step) or step <= 0:
        raise ValueError("Positive derivative step required")

    def extensive(values):
        total = float(sum(values))
        return total * residual_gibbs_rt(
            pressure_bar, temperature_K, values / total,
            critical_temperatures_K, critical_pressures_bar,
            acentric_factors, kij)

    output = []
    for i in range(len(amounts)):
        def displaced(offset):
            values = amounts.copy()
            values[i] += offset * step
            return extensive(values)

        if amounts[i] >= 2 * step:
            derivative = (displaced(-2) - 8 * displaced(-1)
                          + 8 * displaced(1) - displaced(2)) / (12 * step)
        else:
            derivative = (-25 * displaced(0) + 48 * displaced(1)
                          - 36 * displaced(2) + 16 * displaced(3)
                          - 3 * displaced(4)) / (12 * step)
        output.append(math.exp(derivative))
    return np.asarray(output)


def iast_binary(fugacities, capacities, affinities):
    """IAST from unequal-capacity Langmuir pure curves via composition root."""
    f, q, b = [np.asarray(v, dtype=float) for v in
               (fugacities, capacities, affinities)]
    if f.shape != (2,) or q.shape != (2,) or b.shape != (2,):
        raise ValueError("Binary inputs required")
    if not all(np.isfinite(v).all() for v in (f, q, b)):
        raise ValueError("Finite IAST inputs required")
    if np.any(f < 0) or np.any(q <= 0) or np.any(b <= 0):
        raise ValueError("Nonnegative fugacity and positive pure parameters required")
    if not f.any():
        return dict(loadings=np.zeros(2), adsorbed_fraction=None,
                    fictive_fugacities=np.zeros(2), spreading_pressure=0.0)
    if not np.all(f > 0):
        index = int(np.argmax(f))
        loading = np.zeros(2)
        loading[index] = q[index] * b[index] * f[index] / (1 + b[index] * f[index])
        fraction = np.zeros(2)
        fraction[index] = 1.0
        return dict(loadings=loading, adsorbed_fraction=fraction,
                    fictive_fugacities=f.copy(),
                    spreading_pressure=float(q[index] * np.log1p(b[index] * f[index])))

    log_bf = np.log(b * f)

    def condition(logit):
        # Work in logit space to retain accuracy for strongly selective systems.
        log_fraction = np.array([-np.logaddexp(0, -logit),
                                 -np.logaddexp(0, logit)])
        spreading = q * np.logaddexp(0, log_bf - log_fraction)
        return float(spreading[0] - spreading[1])

    bound = 4.0
    while condition(-bound) * condition(bound) > 0 and bound < 512:
        bound *= 2
    logit = brentq(condition, -bound, bound, xtol=1e-13,
                   rtol=4 * np.finfo(float).eps)
    fractions = np.exp([-np.logaddexp(0, -logit), -np.logaddexp(0, logit)])
    fictive = f / fractions
    pure = q / (1 + 1 / (b * fictive))
    total = 1 / np.sum(fractions / pure)
    return dict(loadings=fractions * total, adsorbed_fraction=fractions,
                fictive_fugacities=fictive,
                spreading_pressure=float(q[0] * np.log1p(b[0] * fictive[0])))


def independent_langmuir_fit(fugacities, loadings, uncertainties=None, *,
                              common_capacity=True,
                              capacity_bounds=(1e-10, 1e8),
                              affinity_bounds=(1e-12, 1e12)):
    """Fit pure curves by variable projection, without production code.

    At specified affinities each capacity is a linear weighted least-squares
    parameter, so eliminate it analytically. Uncertainties are standard-deviation
    denominators, not inverse-variance weights. The caller must supply frozen
    bounds if the primary analysis has narrower bounds.
    """
    f = [np.asarray(v, dtype=float) for v in fugacities]
    observed = [np.asarray(v, dtype=float) for v in loadings]
    sigma = ([np.ones_like(v) for v in observed] if uncertainties is None
             else [np.asarray(v, dtype=float) for v in uncertainties])
    if not len(f) or not (len(f) == len(observed) == len(sigma)):
        raise ValueError("Aligned sets of pure curves required")
    for x, y, s in zip(f, observed, sigma):
        if x.ndim != 1 or not (x.shape == y.shape == s.shape) or len(x) < 2:
            raise ValueError("At least two aligned observations per pure curve required")
        if not all(np.isfinite(v).all() for v in (x, y, s)):
            raise ValueError("Finite pure-curve observations required")
        if np.any(x < 0) or np.any(y < 0) or np.any(s <= 0) or not np.any(x > 0):
            raise ValueError("Invalid pure-curve observations or uncertainties")
    for bounds in (capacity_bounds, affinity_bounds):
        if not (len(bounds) == 2 and 0 < bounds[0] < bounds[1] < math.inf):
            raise ValueError("Finite positive ordered bounds required")
    log_bounds = tuple(math.log(v) for v in affinity_bounds)

    def profile(log_affinities, return_values=False):
        affinities = np.exp(log_affinities)
        shapes = [x * a / (1 + x * a) for x, a in zip(f, affinities)]
        numerator = [float(np.dot(t / s, y / s))
                     for t, y, s in zip(shapes, observed, sigma)]
        denominator = [float(np.dot(t / s, t / s)) for t, s in zip(shapes, sigma)]
        if common_capacity:
            capacities = np.full(len(f), np.clip(sum(numerator) / sum(denominator),
                                                 *capacity_bounds))
        else:
            capacities = np.clip(np.asarray(numerator) / denominator, *capacity_bounds)
        residuals = [(c * t - y) / s for c, t, y, s in
                     zip(capacities, shapes, observed, sigma)]
        objective = float(sum(np.dot(r, r) for r in residuals))
        if return_values:
            return dict(capacities=capacities, affinities=affinities,
                        objective=objective,
                        fitted=[c * t for c, t in zip(capacities, shapes)])
        return objective

    if not common_capacity:
        solutions = []
        for index in range(len(f)):
            single = independent_langmuir_fit(
                [f[index]], [observed[index]], [sigma[index]],
                capacity_bounds=capacity_bounds, affinity_bounds=affinity_bounds)
            solutions.append(single)
        return dict(capacities=np.array([r["capacities"][0] for r in solutions]),
                    affinities=np.array([r["affinities"][0] for r in solutions]),
                    objective=float(sum(r["objective"] for r in solutions)),
                    fitted=[r["fitted"][0] for r in solutions])
    if len(f) == 1:
        solution = minimize_scalar(lambda v: profile([v]), bounds=log_bounds,
                                   method="bounded", options={"xatol": 1e-13})
        if not solution.success:
            raise ValueError("Independent scalar pure fit failed")
        return profile([solution.x], return_values=True)
    start = np.array([-math.log(np.median(x[x > 0])) for x in f])
    start = np.clip(start, *log_bounds)
    candidates = []
    for shift in (-2.0, 0.0, 2.0):
        fit = minimize(profile, np.clip(start + shift, *log_bounds), method="Powell",
                       bounds=[log_bounds] * len(f),
                       options={"xtol": 1e-12, "ftol": 1e-13, "maxiter": 10000})
        if fit.success:
            candidates.append(fit)
    if not candidates:
        raise ValueError("Independent shared-capacity pure fit failed")
    selected = min(candidates, key=lambda result: result.fun)
    return profile(selected.x, return_values=True)


ROOT = Path(__file__).resolve().parents[1]


def source_columns(path, requested):
    """Read numeric AIF columns directly, independently of production parser."""
    header, records, in_loop = [], [], False
    for raw in Path(path).read_text(encoding="utf-8-sig").splitlines():
        text = raw.strip()
        if not text or text.startswith("#"):
            continue
        if text == "loop_":
            if in_loop:
                raise ValueError("Unexpected second AIF loop")
            in_loop = True
            continue
        if not in_loop:
            continue
        if text.startswith("_"):
            if records:
                raise ValueError("Unexpected header after AIF data")
            header.append(text)
        else:
            fields = text.split()
            if len(fields) != len(header):
                raise ValueError("Unexpected AIF column count")
            records.append([float(fields[header.index(name)]) for name in requested])
    if not records:
        raise ValueError("No source observations")
    result = np.asarray(records)
    if not np.isfinite(result).all():
        raise ValueError("Nonfinite source observations")
    return result


def independent_score(rows, model):
    """Scalar summations provide an independent implementation of scoring."""
    if not rows:
        raise ValueError("Empty scoring group")
    count = len(rows)
    errors = [[r["predictions"][model][j] - r["observed_mmol_g"][j]
               for j in range(2)] for r in rows]
    mean_absolute = [math.fsum(abs(e[j]) for e in errors) / count for j in range(2)]
    mean_signed = [math.fsum(e[j] for e in errors) / count for j in range(2)]
    total = math.fsum(abs(math.fsum(e)) for e in errors) / count
    fraction = math.fsum(abs(r["predictions"][model][0] / math.fsum(r["predictions"][model])
                            - r["observed_mmol_g"][0] / math.fsum(r["observed_mmol_g"]))
                         for r in rows) / count
    covered = sum(abs(errors[i][j]) <= r["expanded_U_mmol_g"][j]
                  for i, r in enumerate(rows) for j in range(2))
    return dict(component_mae_mmol_g=mean_absolute, component_bias_mmol_g=mean_signed,
                total_mae_mmol_g=total, adsorbed_CO2_fraction_mae=fraction,
                within_reported_U=covered, component_targets=2 * count)


def fit_diagnostics(fugacities, amounts, sigma, record):
    """Check diagnostics using analytic log-parameter derivatives."""
    capacities, affinities = np.asarray(record["capacities"]), np.asarray(record["affinities"])
    shared = record["shared"]
    fitted, jacobians, residuals = [], [], []
    for index, (f, q, u) in enumerate(zip(fugacities, amounts, sigma)):
        prediction = capacities[index] * affinities[index] * f / (1 + affinities[index] * f)
        fitted.append(prediction)
        residuals.append((prediction - q) / u)
        jacobian = np.zeros((len(f), 3 if shared else 4))
        jacobian[:, 0 if shared else index] = prediction / u
        jacobian[:, (1 if shared else 2) + index] = prediction / (1 + affinities[index] * f) / u
        jacobians.append(jacobian)
    jacobian = np.vstack(jacobians)
    singular = np.linalg.svd(jacobian, compute_uv=False)
    condition = float(singular[0] / singular[-1])
    covariance = np.linalg.pinv(jacobian.T @ jacobian)
    sd = np.sqrt(np.diag(covariance))
    correlation = covariance / np.outer(sd, sd)
    theta = np.log(np.concatenate((capacities[:1] if shared else capacities, affinities)))
    lower = np.log([1e-3] * (1 if shared else 2) + [1e-6] * 2)
    upper = np.log([1e3] * (1 if shared else 2) + [1e6] * 2)
    boundary = bool(np.any(theta - lower < 1e-4) or np.any(upper - theta < 1e-4))
    objective = float(sum(r @ r for r in residuals))
    profiles = []
    for factor in [.25, .5, 1., 2., 4.]:
        values = []
        for index, (f, q, u) in enumerate(zip(fugacities, amounts, sigma)):
            capacity = capacities[index] * factor

            def profile_objective(log_affinity):
                b = math.exp(log_affinity)
                error = (capacity * b * f / (1 + b * f) - q) / u
                return float(error @ error)

            solution = minimize_scalar(profile_objective, bounds=(math.log(1e-6), math.log(1e6)),
                                       method="bounded", options={"xatol": 1e-12})
            if not solution.success:
                raise ValueError("Capacity-profile scalar minimization failed")
            values.append(solution.fun)
        profiles.append(dict(capacity_factor=factor, weighted_sse=float(sum(values))))
    rmse = [float(np.sqrt(np.mean((predicted - q) ** 2))) for predicted, q in zip(fitted, amounts)]
    maxima = [float(max(q)) for q in amounts]
    return dict(optimizer_bound_hit=boundary, jacobian_condition=condition,
                parameter_correlation=correlation, weighted_sse=objective,
                n_parameters=3 if shared else 4, n_observations=sum(map(len, fugacities)),
                capacity_profile=profiles,
                locally_identified=bool(record["optimizer_success"] and not boundary and condition < 1e6
                    and all(profiles[index]["weighted_sse"] > objective + 3.84 for index in [1, 3])),
                rmse_mmol_g=rmse, normalized_rmse=[a / b for a, b in zip(rmse, maxima)],
                pure_max_mmol_g=maxima, max_fugacity_MPa=[float(max(f)) for f in fugacities],
                max_occupancy=[float(max(affinities[i] * f / (1 + affinities[i] * f)))
                               for i, f in enumerate(fugacities)],
                pure_fit_adequate=bool(all(a / b <= .05 for a, b in zip(rmse, maxima))))


def verify_result(result_path, predictions_path, config_path):
    """Replay only after the parent workflow has sealed its mixture forecasts."""
    result = json.loads(Path(result_path).read_text())
    forecast = json.loads(Path(predictions_path).read_text())
    config = json.loads(Path(config_path).read_text())
    for entry in config["inputs"]:
        if hashlib.sha256((ROOT / entry["path"]).read_bytes()).hexdigest() != entry["sha256"]:
            raise ValueError("Source hash mismatch: " + entry["path"])
    constants = np.asarray(config["critical_constants"], dtype=float)
    tc, pc_pa, omega = constants.T
    data = ROOT / "data/adsorption/2026-10-13"
    differences = []
    checked = 0
    maximum_scaled_error = 0.0

    def compare(expected, actual, label, rtol=2e-6, atol=2e-9):
        nonlocal checked, maximum_scaled_error
        if isinstance(expected, dict):
            for key, value in expected.items():
                compare(value, actual[key], label + "/" + key, rtol, atol)
            return
        if isinstance(expected, list) and expected and isinstance(expected[0], dict):
            if len(expected) != len(actual):
                differences.append(dict(path=label, reason="list_length_mismatch"))
                return
            for index, (first, second) in enumerate(zip(expected, actual)):
                compare(first, second, label + f"/{index}", rtol, atol)
            return
        if isinstance(expected, bool):
            checked += 1
            if not isinstance(actual, bool) or expected != actual:
                differences.append(dict(path=label, expected=expected, actual=actual))
            return
        first, second = np.asarray(expected), np.asarray(actual)
        if first.shape != second.shape:
            differences.append(dict(path=label, reason="shape_mismatch"))
            return
        checked += first.size
        first, second = first.astype(float), second.astype(float)
        if not np.isfinite(first).all() or not np.isfinite(second).all():
            differences.append(dict(path=label, reason="nonfinite"))
            return
        scale = np.maximum(np.maximum(abs(first), abs(second)), 1e-12)
        maximum_scaled_error = max(maximum_scaled_error, float(np.max(abs(first - second) / scale)))
        if not np.allclose(first, second, rtol=rtol, atol=atol):
            differences.append(dict(path=label, maximum_absolute_error=float(np.max(abs(first - second)))))

    def fugacities(temp, pressure, y, ideal):
        return pressure * np.asarray(y) * (np.ones(2) if ideal else
            pr_fugacity_coefficients(pressure * 10, temp, y, tc, pc_pa / 1e5, omega))

    if len(result["analyses"]) != len(forecast["analyses"]):
        raise ValueError("Result/forecast analysis count mismatch")
    models = ["shared", "ablation", "iast"]
    independent_fit_records = []
    for analysis, sealed_analysis in zip(result["analyses"], forecast["analyses"]):
        name = analysis["name"]
        if name != sealed_analysis["name"] or len(analysis["cases"]) != len(sealed_analysis["cases"]):
            raise ValueError("Result/forecast analysis identity mismatch")
        ideal = name == "ideal"
        if name not in ["ideal", "peng_robinson"]:
            raise ValueError("Unknown analysis")
        all_scores, adequate = {m: [] for m in models}, []
        for case, sealed in zip(analysis["cases"], sealed_analysis["cases"]):
            temp = case["temperature_K"]
            label = f"{name}/{temp}"
            for field in ["temperature_K", "shared_fit", "separate_fit", "pure_data"]:
                if case[field] != sealed[field]:
                    raise ValueError("Modified forecast field: " + label + "/" + field)
            fs, qs, us = [], [], []
            for index, gas in enumerate(["CO2", "CH4"]):
                original = source_columns(data / f"RM8850_{gas}_{temp}K_CW.aif",
                    ["_adsorp_pressure", "_adsorp_amount", "_adsorp_amount_uncertainty"])
                f = np.array([fugacities(temp, p, np.eye(2)[index], ideal)[index]
                              for p in original[:, 0]])
                fs.append(f); qs.append(original[:, 1]); us.append(original[:, 2] / 2)
                original_record = dict(fugacity_MPa=f, amount_mmol_g=original[:, 1],
                                       expanded_U_mmol_g=original[:, 2])
                compare(original_record, case["pure_data"][index], label + "/pure/" + gas,
                        rtol=2e-9, atol=2e-11)
            for shared, field in [(True, "shared_fit"), (False, "separate_fit")]:
                reconstructed = independent_langmuir_fit(fs, qs, us, common_capacity=shared,
                    capacity_bounds=(1e-3, 1e3), affinity_bounds=(1e-6, 1e6))
                compare(reconstructed["capacities"], case[field]["capacities"], label + "/" + field + "/capacities")
                compare(reconstructed["affinities"], case[field]["affinities"], label + "/" + field + "/affinities")
                compare(reconstructed["objective"], case[field]["weighted_sse"], label + "/" + field + "/weighted_sse")
                compare(fit_diagnostics(fs, qs, us, case[field]), case[field],
                        label + "/" + field + "/diagnostics", rtol=2e-5, atol=2e-8)
                independent_fit_records.append(dict(analysis=name, temperature_K=temp, model=field,
                    capacities=reconstructed["capacities"].tolist(), affinities=reconstructed["affinities"].tolist(),
                    weighted_sse=reconstructed["objective"]))
            source = source_columns(data / f"RM8850_CO2_CH4_{temp}K_CW.aif",
                ["_adsorp_pressure", "_adsorp_molefraction1", "_adsorp_amount1", "_adsorp_amount2",
                 "_adsorp_amount1_uncertainty", "_adsorp_amount2_uncertainty"])
            if len(source) != len(case["rows"]) or len(source) != len(sealed["rows"]):
                raise ValueError("Target row count mismatch")
            for number, (original, row, frozen) in enumerate(zip(source, case["rows"], sealed["rows"]), 1):
                for key, value in frozen.items():
                    if row[key] != value:
                        raise ValueError("Modified sealed prediction")
                row_label = label + f"/row/{number}"
                compare([number, original[0], original[1]], [row["row"], row["p_MPa"], row["y_CO2"]],
                        row_label + "/identity", rtol=0, atol=0)
                compare(original[2:4], row["observed_mmol_g"], row_label + "/observed", rtol=0, atol=0)
                compare(original[4:6], row["expanded_U_mmol_g"], row_label + "/uncertainty", rtol=0, atol=0)
                f = fugacities(temp, original[0], [original[1], 1 - original[1]], ideal)
                compare(f, row["fugacity_MPa"], row_label + "/fugacity", rtol=2e-9, atol=2e-11)
                q = np.asarray(case["shared_fit"]["capacities"])
                b = np.asarray(case["shared_fit"]["affinities"])
                expected = dict(shared=q * b * f / (1 + sum(b * f)),
                                ablation=q * b * f / (1 + b * f))
                iast = iast_binary(f, case["separate_fit"]["capacities"], case["separate_fit"]["affinities"])
                expected["iast"] = iast["loadings"]
                compare(expected, row["predictions"], row_label + "/prediction", rtol=2e-9, atol=2e-10)
                compare(iast["fictive_fugacities"], row["iast_f0_MPa"], row_label + "/iast_f0", rtol=2e-9)
                compare((iast["fictive_fugacities"] > [max(f) for f in fs]).tolist(),
                        row["iast_extrapolated"], row_label + "/extrapolation", rtol=0, atol=0)
            scores = {model: independent_score(case["rows"], model) for model in models}
            compare(scores, case["scores"], label + "/scores", rtol=2e-12, atol=2e-12)
            if len(case["rows"]) % 3:
                raise ValueError("Three equal-sized source sweeps required")
            n = len(case["rows"]) // 3
            for sweep in range(3):
                compare({model: independent_score(case["rows"][sweep*n:(sweep+1)*n], model) for model in models},
                        case["sweeps"][sweep], label + f"/sweep/{sweep}", rtol=2e-12, atol=2e-12)
            passed = bool(case["shared_fit"]["locally_identified"] and case["shared_fit"]["pure_fit_adequate"]
                          and all(error / max(amount) <= .10 for error, amount in
                                  zip(scores["shared"]["component_mae_mmol_g"], qs)))
            compare(passed, case["shared_transfer_adequate"], label + "/transfer_adequate")
            adequate.append(passed)
            for model in models:
                all_scores[model].append(scores[model])
        aggregate = {}
        for model in models:
            scores = all_scores[model]
            n = len(scores)
            aggregate[model] = dict(
                balanced_mae_mmol_g=math.fsum(math.fsum(s["component_mae_mmol_g"]) for s in scores) / (2*n),
                balanced_total_mae_mmol_g=math.fsum(s["total_mae_mmol_g"] for s in scores) / n,
                balanced_composition_mae=math.fsum(s["adsorbed_CO2_fraction_mae"] for s in scores) / n,
                within_reported_U=sum(s["within_reported_U"] for s in scores),
                component_targets=sum(s["component_targets"] for s in scores))
        gain = 1 - aggregate["shared"]["balanced_mae_mmol_g"] / aggregate["ablation"]["balanced_mae_mmol_g"]
        summary = dict(scores=aggregate, shared_improvement_over_ablation=gain,
                       adequate_temperatures=sum(adequate),
                       declared_joint_transfer_pass=bool(all(adequate) and gain >= .20))
        compare(summary, analysis["summary"], name + "/summary", rtol=2e-12, atol=2e-12)
    return dict(verified=not differences, checked_numbers=int(checked),
                maximum_scaled_difference=maximum_scaled_error,
                discrepancies=differences, independent_fits=independent_fit_records,
                method="Independent AIF parsing; PR Gibbs derivative; pure-fit variable projection; IAST composition root; scalar score summation",
                scope="Verifies source values, numerical forecasts, pure fits and scores; does not independently certify source metrology or physical assumptions")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/adsorption_2026-10-13.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("Use an unused verification output path")
    report = verify_result(args.result, args.predictions, args.config)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "independent_fits"}, indent=2))
    if not report["verified"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
