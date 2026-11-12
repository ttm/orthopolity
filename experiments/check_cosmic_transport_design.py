"""Check cosmic transport design identities and counterexamples, without data.

Reference measure: logarithmic host mass. These manufactured finite-class and
material-packet examples test the proposed measurement/model logic, not whether
gravitational assembly satisfies it. No catalogue is read and no fit is made.
"""
from __future__ import annotations

import json
import math

import numpy as np
from scipy.integrate import quad, solve_ivp


def cascade_rhs(stock, widths, speed, inlet, sources):
    """Open finite-class throughflow; sources are resource/time per class."""
    outward = speed * stock / widths
    incoming = np.concatenate(([inlet], outward[:-1]))
    return incoming - outward + sources


def main():
    widths = np.full(4, math.log(2))
    inlet = 3.0
    initial = np.array([2.0, 1.0, 0.5, 9.0])
    cases = {
        "constant_drift": (np.full(4, 0.5), np.zeros(4)),
        "variable_drift": (np.array([0.5, 1.0, 2.0, 4.0]), np.zeros(4)),
        "interior_source": (np.full(4, 0.5), np.array([0.0, 0.5, 0.0, 0.0])),
    }
    cascade_results = {}
    for name, (speed, sources) in cases.items():
        solution = solve_ivp(
            lambda t, stock: cascade_rhs(stock, widths, speed, inlet, sources),
            (0.0, 100.0), initial, method="DOP853", rtol=1e-11, atol=1e-12,
        )
        assert solution.success, solution.message
        # Independent stationary balance: flux increases by each class source.
        stationary_flux = inlet + np.cumsum(sources)
        expected_density = stationary_flux / speed
        density = solution.y[:, -1] / widths
        error = float(np.max(np.abs(density - expected_density)))
        assert error < 1e-9, (name, error)
        # Total stock changes only by inlet, interior sources and terminal outflow.
        for stock in solution.y.T:
            derivative = cascade_rhs(stock, widths, speed, inlet, sources)
            budget_derivative = inlet + sources.sum() - speed[-1] * stock[-1] / widths[-1]
            assert abs(derivative.sum() - budget_derivative) < 1e-11
        cascade_results[name] = {
            "stationary_resource_density": expected_density.tolist(),
            "stationary_flux": stationary_flux.tolist(),
            "ode_max_absolute_error": error,
        }
    assert np.ptp(cascade_results["constant_drift"]["stationary_resource_density"]) == 0
    assert np.ptp(cascade_results["variable_drift"]["stationary_resource_density"]) > 0
    assert np.ptp(cascade_results["interior_source"]["stationary_resource_density"]) > 0

    # Constant coefficients alone do not force a transient profile to be flat.
    transient = solve_ivp(
        lambda t, stock: cascade_rhs(stock, widths, np.full(4, 0.5), inlet, np.zeros(4)),
        (0.0, 0.2), np.zeros(4), method="DOP853", rtol=1e-12, atol=1e-14,
    )
    assert transient.success
    early_density = transient.y[:, -1] / widths
    assert np.all(np.diff(early_density) < 0)

    # Minor merger: all 100 main-host units and one satellite unit join mass 101.
    # A main-branch history records only the short main-host displacement.
    mass = np.ones(101)
    old_host = np.concatenate((np.full(100, 100.0), [1.0]))
    new_host = np.full(101, 101.0)
    main_jump = math.log(101 / 100)
    satellite_jump = math.log(101)
    assert satellite_jump > 400 * main_jump
    edges = np.exp(np.linspace(math.log(0.5), math.log(128.0), 9))
    before = np.histogram(old_host, bins=edges, weights=mass)[0]
    after = np.histogram(new_host, bins=edges, weights=mass)[0]
    # Unit time and unit comoving volume. Net crossing through each boundary.
    crossing = np.array([
        np.sum(mass * ((new_host >= boundary).astype(int)
                       - (old_host >= boundary).astype(int)))
        for boundary in edges
    ])
    assert np.array_equal(after - before, crossing[:-1] - crossing[1:])
    assert before.sum() == after.sum() == 101
    assert np.any(crossing[1:-1] > 0)
    # Endpoint closure is exact by construction; it cannot validate a forecast.
    held_in_same_bin = np.all(after == before)
    assert not held_in_same_bin

    # Equal endpoints hide an excursion. Net flux is identified, gross flux is not.
    boundary = 2.0
    path = np.array([1.0, 4.0, 1.0])
    above = (path >= boundary).astype(int)
    endpoint_net = int(above[-1] - above[0])
    resolved_gross = int(np.abs(np.diff(above)).sum())
    assert endpoint_net == 0 and resolved_gross == 2

    # Independent quadrature of a finite-interval amplitude/count prediction.
    j2, v2, lower, upper = 7.0, 2.0, 4.0, 32.0
    count_quad = quad(lambda m: j2 / (v2 * m * m), lower, upper,
                      epsabs=1e-12, epsrel=1e-12)[0]
    mass_quad = quad(lambda m: j2 / (v2 * m), lower, upper,
                     epsabs=1e-12, epsrel=1e-12)[0]
    count_formula = (j2 / v2) * (1 / lower - 1 / upper)
    mass_formula = (j2 / v2) * math.log(upper / lower)
    assert abs(count_quad - count_formula) < 1e-12
    assert abs(mass_quad - mass_formula) < 1e-12

    # Main-branch accretion and material drift must not be substituted silently.
    # This is a conditional algebraic counterexample, not an astronomical fit.
    growth_exponent = 1.1
    drift_exponent = growth_exponent - 1
    abundance_exponent = 2 + drift_exponent
    high_to_low_resource_ratio_two_decades = 100 ** (-drift_exponent)
    assert math.isclose(abundance_exponent, 2.1)
    assert high_to_low_resource_ratio_two_decades < 1

    print(json.dumps({
        "kind": "Manufactured transport/measurement checks; no empirical inputs or verdict",
        "reference_measure": "logarithmic host mass; log-orthopolic neutrality is the tested ideal",
        "cascade_cases": cascade_results,
        "constant_coefficients_transient_density": early_density.tolist(),
        "minor_merger": {
            "main_displacement_ln_mass": main_jump,
            "satellite_displacement_ln_mass": satellite_jump,
            "mass_before": int(before.sum()),
            "mass_after": int(after.sum()),
            "net_boundary_crossing_mass": crossing.tolist(),
            "endpoint_budget_identity_is_not_forecast_validation": True,
        },
        "undersampled_excursion": {"endpoint_net": endpoint_net, "resolved_gross": resolved_gross},
        "finite_interval_prediction": {"count_per_volume": count_formula,
                                       "mass_per_volume": mass_formula},
        "conditional_growth_substitution": {
            "input_growth_exponent": growth_exponent,
            "predicted_abundance_exponent": abundance_exponent,
            "high_to_low_resource_ratio_two_decades": high_to_low_resource_ratio_two_decades,
            "not_a_qualified_material_drift_estimate": True,
        },
    }, indent=2))


if __name__ == "__main__":
    main()
