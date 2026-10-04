"""Analytic expected-stock forecasts under two explicitly fixed measures.

These are consequences of assumed neutrality, not empirical observations or
evidence for either hypothesis. On a fixed size domain [a, b], the hypotheses
are uniform expected resource per log size and per log whole-object cost,
respectively. The cost is q(k) = cost_scale * ((k / size_scale)**degree + overhead).
"""
from __future__ import annotations

import math
from numbers import Real
from typing import Iterable


def _scalar(value: Real, name: str, *, allow_zero: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name} must be a real number, excluding booleans")
    try:
        result = float(value)
    except (OverflowError, ValueError) as exc:
        raise ValueError(f"{name} must be finite") from exc
    if not math.isfinite(result) or result < 0 or (result == 0 and not allow_zero):
        raise ValueError(f"{name} must be finite and {'nonnegative' if allow_zero else 'positive'}")
    return result


def _positive_finite(values: Iterable[float]) -> None:
    if any(not math.isfinite(value) or value <= 0 for value in values):
        raise ValueError("costs, interval widths and forecasts must be representable positive finite numbers")


def _forecast(resources: list[float], counts: list[float]) -> dict:
    total_resource = math.fsum(resources)
    total_count = math.fsum(counts)
    resource_shares = [value / total_resource for value in resources]
    count_shares = [value / total_count for value in counts]
    _positive_finite([*resources, *counts, total_resource, total_count,
                      *resource_shares, *count_shares])
    return dict(resource_totals=resources, resource_shares=resource_shares,
                count_totals=counts, count_shares=count_shares,
                total_resource=total_resource, total_count=total_count)


def measure_forecasts(
    edges: Iterable[Real], *, degree: Real, overhead: Real = 0.0,
    budget: Real = 1.0, cost_scale: Real = 1.0, size_scale: Real = 1.0,
) -> dict:
    """Integrate the two conditional forecasts over fixed adjacent size bins.

    ``edges`` must contain at least two strictly increasing positive finite
    sizes. ``size_scale`` has the same size units; ``overhead`` is dimensionless.
    ``cost_scale`` is resource per object and ``budget`` is total resource over
    the full domain. The degree is positive, and overhead is nonnegative.

    The ``log_size`` and ``log_cost`` results each contain per-bin
    ``resource_totals``, ``resource_shares``, ``count_totals``, ``count_shares``,
    and the scalars ``total_resource`` and ``total_count``. Counts are expected
    abundances and need not be integers. All outputs are ordinary Python floats
    and lists. Resource totals sum to the supplied budget up to roundoff.

    At zero overhead the two forecasts coincide exactly. Small positive
    overhead uses a continuous, cancellation-resistant formula. Nonfinite or
    unrepresentable costs, widths or forecasts raise ``ValueError``; this
    calculator does not silently return overflowed or underflowed results.
    """
    degree = _scalar(degree, "degree")
    overhead = _scalar(overhead, "overhead", allow_zero=True)
    budget = _scalar(budget, "budget")
    cost_scale = _scalar(cost_scale, "cost_scale")
    size_scale = _scalar(size_scale, "size_scale")
    try:
        bins = [_scalar(value, "edge") for value in edges]
    except TypeError as exc:
        raise ValueError("edges must be an iterable of real numbers") from exc
    if len(bins) < 2 or any(lo >= hi for lo, hi in zip(bins, bins[1:])):
        raise ValueError("at least two strictly increasing edges are required")

    try:
        variable_costs = [(edge / size_scale)**degree for edge in bins]
        full_costs = [value + overhead for value in variable_costs]
        _positive_finite([*variable_costs, *full_costs,
                          *(cost_scale * value for value in full_costs)])
        log_widths = []
        for lo, hi in zip(bins, bins[1:]):
            relative_width = (hi - lo) / lo
            log_widths.append(math.log1p(relative_width) if math.isfinite(relative_width)
                              else math.log(hi) - math.log(lo))
        log_span = math.fsum(log_widths)
        deltas = [hi - lo for lo, hi in zip(variable_costs, variable_costs[1:])]
        _positive_finite([*log_widths, log_span, *deltas])
        abundance_scale = budget / cost_scale
        _positive_finite([abundance_scale])

        # The inverse difference is formed without subtracting two reciprocals.
        inverse_differences = [(delta / hi) / lo for delta, lo, hi in
                               zip(deltas, full_costs, full_costs[1:])]
        if overhead == 0:
            counts = [abundance_scale * (difference / degree / log_span)
                      for difference in inverse_differences]
            resources = [budget * (width / log_span) for width in log_widths]
            return dict(log_size=_forecast(resources, counts),
                        log_cost=_forecast(resources.copy(), counts.copy()))

        cost_widths = [math.log1p(delta / lo) for delta, lo in zip(deltas, full_costs)]
        cost_span = math.fsum(cost_widths)
        _positive_finite([*cost_widths, cost_span, *inverse_differences])
        size_integrals = []
        for delta, lo, hi_full in zip(deltas, variable_costs, full_costs[1:]):
            relative_delta = delta / lo
            t = (overhead / hi_full) * relative_delta
            ratio = math.log1p(t) / t if t else 1.0
            # This is integral d(log k)/(v(k)+overhead), with the c->0
            # limit built in. It avoids subtraction of nearly equal logs.
            size_integrals.append(ratio * relative_delta / hi_full / degree)
        size_counts = [abundance_scale * (value / log_span) for value in size_integrals]
        cost_counts = [abundance_scale * (value / cost_span) for value in inverse_differences]
        size_resources = [budget * (width / log_span) for width in log_widths]
        cost_resources = [budget * (width / cost_span) for width in cost_widths]
        return dict(log_size=_forecast(size_resources, size_counts),
                    log_cost=_forecast(cost_resources, cost_counts))
    except (OverflowError, ZeroDivisionError) as exc:
        raise ValueError("costs and forecasts exceed the representable numerical range") from exc
