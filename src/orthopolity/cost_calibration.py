"""Signed-assay cost calibration and conditional moment diagnostics.

The working squared-error criterion is not an iid likelihood. Its solutions and
multistart ranges are deterministic sensitivity results, not confidence draws.
No empirical data are loaded by this module.
"""
from __future__ import annotations

import math
from numbers import Real
import statistics

import numpy as np
from scipy.integrate import quad
from scipy.optimize import least_squares


def _real(value, name, *, positive=False, nonnegative=False):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, Real):
        raise ValueError(f"{name} must be a finite real number")
    value = float(value)
    if not math.isfinite(value) or (positive and value <= 0) or (nonnegative and value < 0):
        raise ValueError(f"invalid {name}")
    return value


def summarize_calibration(rows):
    """Retain signed rates and missing memberships within species/OD groups.

    Each source row must have species, optical_density, volume_um3,
    oxygen_umol_per_min_per_cell (number or None), source_row, and cells_per_ul.
    Biovolume concentration is cell volume times cells per microlitre. SD is a
    sample SD of the retained readings, never a standard error; it is None for
    fewer than two usable rows. A wholly missing group retains mean_rate=None.
    """
    grouped, sources, species_sizes = {}, set(), {}
    for row in rows:
        species = row["species"]
        if not isinstance(species, str) or not species.strip():
            raise ValueError("species must be a nonempty string")
        od = _real(row["optical_density"], "optical density", positive=True)
        volume = _real(row["volume_um3"], "cell volume", positive=True)
        source = row["source_row"]
        if isinstance(source, bool) or not isinstance(source, (int, np.integer)) or source <= 0:
            raise ValueError("source_row must be a positive integer")
        if source in sources:
            raise ValueError("source rows must be unique")
        sources.add(source)
        if species in species_sizes and species_sizes[species] != volume:
            raise ValueError("this calibration requires one fixed cell volume per species")
        species_sizes[species] = volume
        rate = row["oxygen_umol_per_min_per_cell"]
        if rate is not None:
            rate = _real(rate, "signed respiration rate")
        concentration = _real(row["cells_per_ul"], "cell concentration", nonnegative=True) * volume
        _real(concentration, "biovolume concentration", nonnegative=True)
        grouped.setdefault((species, od), []).append((int(source), rate, concentration))
    if not grouped:
        raise ValueError("at least one calibration row is required")
    output = []
    for (species, od), members in sorted(grouped.items()):
        members.sort()
        usable = [(source, rate) for source, rate, _ in members if rate is not None]
        rates = [rate for _, rate in usable]
        output.append(dict(species=species, od=od, volume_um3=species_sizes[species],
            mean_rate=statistics.mean(rates) if rates else None,
            sd_rate=statistics.stdev(rates) if len(rates) > 1 else None,
            min_rate=min(rates) if rates else None, max_rate=max(rates) if rates else None,
            raw_count=len(members), usable_count=len(rates), missing_count=len(members)-len(rates),
            source_rows=[source for source, _, _ in members],
            usable_source_rows=[source for source, _ in usable],
            missing_source_rows=[source for source, rate, _ in members if rate is None],
            mean_biovolume_um3_per_ul=statistics.mean(value for _, _, value in members)))
    return output


def _references(config):
    domain = config["diagnostic_domain_um3"]
    if len(domain) != 2:
        raise ValueError("diagnostic domain needs two endpoints")
    lo = _real(domain[0], "domain lower", positive=True)
    hi = _real(domain[1], "domain upper", positive=True)
    if lo >= hi:
        raise ValueError("diagnostic domain must be increasing")
    reference = math.exp((math.log(lo) + math.log(hi)) / 2)
    return (reference, _real(config["od_reference"], "OD reference", positive=True),
            _real(config["rate_scale_umol_min_cell"], "rate scale", positive=True))


def _physical(fit):
    return (_real(fit["A"], "A", positive=True),
            _real(fit["C"], "C", nonnegative=True),
            _real(fit["d"], "d", positive=True),
            _real(fit["beta"], "beta"))


def predict_cost(fit, volumes, ods, config=None):
    """Predict positive conditional mean rates; no observed rates are inputs."""
    A, C, d, beta = _physical(fit)
    if "size_reference_um3" in fit and "od_reference" in fit:
        size_ref = _real(fit["size_reference_um3"], "size reference", positive=True)
        od_ref = _real(fit["od_reference"], "OD reference", positive=True)
    elif config is not None:
        size_ref, od_ref, _ = _references(config)
    else:
        raise ValueError("fit or config must declare fixed reference scales")
    raw_volumes, raw_ods = np.asarray(volumes), np.asarray(ods)
    if raw_volumes.dtype.kind not in "iuf" or raw_ods.dtype.kind not in "iuf":
        raise ValueError("volumes and ODs must be real numeric arrays")
    volumes, ods = np.broadcast_arrays(raw_volumes.astype(float), raw_ods.astype(float))
    if (np.any(~np.isfinite(volumes)) or np.any(volumes <= 0)
            or np.any(~np.isfinite(ods)) or np.any(ods <= 0)):
        raise ValueError("volumes and ODs must be positive and finite")
    try:
        with np.errstate(over="raise", divide="raise", invalid="raise"):
            result = (A * np.exp(d * (np.log(volumes) - math.log(size_ref))) + C)
            result = result * np.exp(beta * (np.log(ods) - math.log(od_ref)))
    except FloatingPointError as exc:
        raise ValueError("predicted cost exceeds the representable numerical range") from exc
    if np.any(~np.isfinite(result)) or np.any(result <= 0):
        raise ValueError("predicted cost must remain positive and finite")
    return result


def fit_cost_curve(groups, *, model="power", weighting="equal_groups", config, fit_density=True):
    """Fit group means without logging, clipping or replication-count weights.

    Equal-group residuals use the fixed rate scale for numerical conditioning;
    species-RMS residuals use only the supplied training groups. Returned SSE is
    dimensionless. Additive fits retain the exact fitted power curve as a C=0
    candidate, including its convergence and boundary diagnostics.
    """
    if model not in ("power", "additive") or weighting not in ("equal_groups", "species_rms"):
        raise ValueError("unsupported model or weighting")
    if not isinstance(fit_density, bool):
        raise ValueError("fit_density must be boolean")
    groups = list(groups)
    if not groups:
        raise ValueError("training groups cannot be empty")
    size_ref, od_ref, rate_scale = _references(config)
    volumes, ods, means, species, sd = [], [], [], [], []
    seen = set()
    for group in groups:
        name = group["species"]
        if not isinstance(name, str) or not name:
            raise ValueError("species must be a nonempty string")
        od = _real(group["od"], "optical density", positive=True)
        if (name, od) in seen:
            raise ValueError("training species/OD groups must be unique")
        seen.add((name, od))
        volumes.append(_real(group["volume_um3"], "cell volume", positive=True))
        ods.append(od)
        means.append(_real(group["mean_rate"], "signed group mean"))
        species.append(name)
        sd.append(None if group["sd_rate"] is None else
                  _real(group["sd_rate"], "sample SD", nonnegative=True))
    if len(set(volumes)) < 2:
        raise ValueError("cost shape needs at least two distinct training volumes")
    if fit_density and len(set(ods)) < 2:
        raise ValueError("a density exponent needs at least two training OD levels")
    if weighting == "species_rms" and any(value is None for value in sd):
        raise ValueError("species-RMS weighting requires a defined sample SD in each training group")
    scales = {}
    for name in sorted(set(species)):
        indices = [i for i, value in enumerate(species) if value == name]
        if weighting == "species_rms":
            # hypot then an RMS avoids overflowing rate**2 on a change of units.
            lengths = [math.hypot(means[i], sd[i]) for i in indices]
            largest = max(lengths)
            value = largest * math.sqrt(statistics.mean((x/largest)**2 for x in lengths)) if largest else 0.
            scales[name] = max(1e-15, value)
        else:
            scales[name] = rate_scale
    log_volume = np.log(np.asarray(volumes)) - math.log(size_ref)
    log_od = np.log(np.asarray(ods)) - math.log(od_ref)
    scaled_means = np.asarray(means) / rate_scale
    residual_weights = np.asarray([rate_scale / scales[name] for name in species])
    if not np.all(np.isfinite(scaled_means)) or not np.all(np.isfinite(residual_weights)):
        raise ValueError("training rates exceed the declared numerical scale")
    options = config["optimization"]
    names = ["log_scaled_amplitude", "d"] + (["scaled_overhead"] if model == "additive" else [])
    if fit_density:
        names.append("beta")
    bounds = [options["log_scaled_amplitude_bounds"], options["degree_bounds"]]
    if model == "additive":
        bounds.append(options["scaled_overhead_bounds"])
    if fit_density:
        bounds.append(options["od_exponent_bounds"])
    lower, upper = np.asarray(bounds, dtype=float).T
    if np.any(~np.isfinite(lower)) or np.any(~np.isfinite(upper)) or np.any(lower >= upper):
        raise ValueError("optimization bounds must be finite and increasing")
    if lower[1] <= 0 or (model == "additive" and lower[2] != 0):
        raise ValueError("degree must be positive and additive overhead must include zero")
    boundary_tolerance = _real(options["technical_boundary_relative_tolerance"], "boundary tolerance", positive=True)

    def unpack(parameters):
        parameters = dict(zip(names, parameters))
        return (math.exp(parameters["log_scaled_amplitude"]), parameters.get("scaled_overhead", 0.),
                parameters["d"], parameters.get("beta", 0.))

    def residuals(parameters):
        amp, overhead, degree, beta = unpack(parameters)
        with np.errstate(over="raise", invalid="raise"):
            expected = (amp * np.exp(degree * log_volume) + overhead) * np.exp(beta * log_od)
            return (expected - scaled_means) * residual_weights

    def flags(parameters):
        technical, nested_zero = [], model == "additive" and parameters[2] == 0
        for name, value, lo, hi in zip(names, parameters, lower, upper):
            tolerance = boundary_tolerance * max(1., abs(lo), abs(hi))
            if abs(value-lo) <= tolerance:
                if name == "scaled_overhead":
                    nested_zero = True
                else:
                    technical.append(name + ":lower")
            if abs(value-hi) <= tolerance:
                technical.append(name + ":upper")
        return dict(technical=technical, nested_zero_overhead=bool(nested_zero))

    def candidate(parameters, score, origin):
        amp, overhead, degree, beta = unpack(parameters)
        return dict(A=float(amp*rate_scale), C=float(overhead*rate_scale), d=float(degree), beta=float(beta),
                    model=model, weighting=weighting, fit_density=fit_density,
                    size_reference_um3=size_ref, od_reference=od_ref,
                    weighted_sse=float(score), bound_flags=flags(parameters), origin=origin)

    starts, candidates = [], []
    degree_starts = options["degree_starts"]
    beta_starts = options["od_exponent_starts"] if fit_density else [0.]
    overhead_starts = options["scaled_overhead_starts"] if model == "additive" else [0.]
    for degree in degree_starts:
        for beta in beta_starts:
            for overhead in overhead_starts:
                base = np.exp(degree * log_volume + beta * log_od)
                target = scaled_means - overhead * np.exp(beta * log_od)
                weighted_base = base * residual_weights
                amplitude = float(np.dot(weighted_base, target * residual_weights) / np.dot(weighted_base, weighted_base))
                amplitude = min(math.exp(upper[0]), max(math.exp(lower[0]), amplitude))
                initial = [math.log(amplitude), degree] + ([overhead] if model == "additive" else [])
                if fit_density:
                    initial.append(beta)
                if np.any(np.asarray(initial) < lower) or np.any(np.asarray(initial) > upper):
                    raise ValueError("optimization starts must lie within fixed bounds")
                diagnostic = dict(initial_parameters=dict(zip(names, map(float, initial))))
                try:
                    fit = least_squares(residuals, initial, bounds=(lower, upper),
                        max_nfev=options["max_nfev"], ftol=options["ftol"],
                        xtol=options["xtol"], gtol=options["gtol"])
                    score = float(np.dot(fit.fun, fit.fun))
                    converged = bool(fit.success and math.isfinite(score) and np.all(np.isfinite(fit.x)))
                    diagnostic.update(converged=converged, status=int(fit.status), nfev=int(fit.nfev),
                        message=str(fit.message), optimality=float(fit.optimality) if math.isfinite(fit.optimality) else None,
                        weighted_sse=score if math.isfinite(score) else None)
                    if converged:
                        result = candidate(fit.x, score, "multistart")
                        candidates.append(result)
                        diagnostic["solution"] = result
                except (ValueError, OverflowError, FloatingPointError) as exc:
                    diagnostic.update(converged=False, message=str(exc), weighted_sse=None)
                starts.append(diagnostic)
    if model == "additive":
        power = fit_cost_curve(groups, model="power", weighting=weighting, config=config, fit_density=fit_density)
        parameters = [math.log(power["A"] / rate_scale), power["d"], 0.]
        if fit_density:
            parameters.append(power["beta"])
        nested = candidate(parameters, power["weighted_sse"], "nested_power")
        candidates.append(nested)
        starts.append(dict(converged=True, origin="nested_power", weighted_sse=nested["weighted_sse"],
                           solution=nested, power_starts=power["starts"]))
    if not candidates:
        raise RuntimeError("no optimization start converged")
    best = min(candidates, key=lambda value: value["weighted_sse"])
    near = [value for value in candidates if value["weighted_sse"] <= best["weighted_sse"]*1.01 + 1e-12]
    return dict(best, training_scales=scales, training_group_count=len(groups), starts=starts,
                near_optimal_candidates=near,
                residual_scale="fixed_rate_scale" if weighting == "equal_groups" else "training_species_rms",
                weighted_sse_units="dimensionless")


def moment_predictions(fit, domain):
    """Integrate conditional mean-volume forecasts on a declared fixed domain.

    S count weight per log volume is 1/q_rel; Q weight is t/q_rel**2, where
    t=(V/V0)**d. Shared budget, common OD effects and resource units cancel.
    No uncertainty about individual cost or domain coverage is inferred here.
    """
    A, C, degree, _ = _physical(fit)
    reference = _real(fit["size_reference_um3"], "size reference", positive=True)
    if len(domain) != 2:
        raise ValueError("moment domain needs two endpoints")
    lo = _real(domain[0], "domain lower", positive=True)
    hi = _real(domain[1], "domain upper", positive=True)
    if lo >= hi:
        raise ValueError("moment domain must be increasing")
    # Relative normalization avoids any effect of physical rate units.
    scale = max(A, C)
    variable, overhead = A / scale, C / scale
    variable_share = variable / (variable + overhead)
    overhead_share = overhead / (variable + overhead)
    bounds = math.log(lo), math.log(hi)
    def weights(log_volume):
        t = math.exp(degree * (log_volume - math.log(reference)))
        q_relative = variable_share * t + overhead_share
        return 1. / q_relative, t / q_relative**2
    def moment(index):
        denominator = quad(lambda x: weights(x)[index], *bounds, epsabs=1e-10, epsrel=1e-10)[0]
        numerator = quad(lambda x: math.exp(x) * weights(x)[index], *bounds, epsabs=1e-10, epsrel=1e-10)[0]
        return _real(numerator / denominator, "conditional mean volume", positive=True)
    try:
        size_moment = moment(0)
        cost_moment = size_moment if C == 0 else moment(1)
    except (OverflowError, ZeroDivisionError) as exc:
        raise ValueError("moment integration exceeds the representable numerical range") from exc
    return dict(m_S=size_moment, m_Q=cost_moment, relative_gap=abs(cost_moment / size_moment - 1.))
