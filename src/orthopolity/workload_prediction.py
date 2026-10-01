"""Calibration-only replay forecasts for a full-grid workload experiment.

An opportunity tries *every* size in fresh children.  Its outcome is the
largest successful size, or zero.  Success at a particular size and survival
of that largest outcome are different targets when costs are nonmonotone.
No validation measurements enter these helpers.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping

import numpy as np


def _sizes(values) -> np.ndarray:
    raw = np.asarray(values)
    if (raw.ndim != 1 or raw.size == 0 or not np.issubdtype(raw.dtype, np.number)
            or not np.all(np.isfinite(raw)) or not np.all(raw == np.floor(raw))
            or np.any(raw <= 0) or np.any(np.diff(raw) <= 0)):
        raise ValueError("sizes must be a nonempty, strictly increasing positive integer grid")
    return raw.astype(np.int64)


def _positive_matrix(values, n_sizes: int, name: str) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    if (array.ndim != 2 or array.shape[0] == 0 or array.shape[1] != n_sizes
            or not np.all(np.isfinite(array)) or np.any(array <= 0)):
        raise ValueError(f"{name} must have shape (blocks, sizes) with finite positive costs")
    return array


def _from_matrices(sizes, memory, cpu, block_ids) -> dict:
    grid = _sizes(sizes)
    memory = _positive_matrix(memory, grid.size, "memory_costs")
    cpu = _positive_matrix(cpu, grid.size, "cpu_costs")
    if memory.shape != cpu.shape or len(block_ids) != memory.shape[0]:
        raise ValueError("paired cost matrices and block IDs must have the same block count")
    median_memory = np.median(memory, axis=0)
    median_cpu = np.median(cpu, axis=0)
    return {
        "sizes": grid.copy(), "block_ids": list(block_ids),
        "memory_costs": memory.copy(), "cpu_costs": cpu.copy(),
        "raw_median_memory_bytes": median_memory,
        "raw_median_cpu_seconds": median_cpu,
        "median_memory_bytes": np.maximum.accumulate(median_memory),
        "median_cpu_seconds": np.maximum.accumulate(median_cpu),
        "cost_nonmonotonicity": {
            "memory_blocks_with_decrease": int(np.any(np.diff(memory, axis=1) < 0, axis=1).sum()),
            "cpu_blocks_with_decrease": int(np.any(np.diff(cpu, axis=1) < 0, axis=1).sum()),
        },
    }


def calibration_profiles(rows: Iterable[Mapping], sizes) -> dict:
    """Build complete paired block profiles from successful calibration rows.

    Rows require ``block_id`` (``block`` is accepted), ``size``,
    ``peak_rss_bytes``, ``cpu_seconds``, ``numerical_valid`` and ``status``.
    Failed or incomplete calibration cannot be converted into a forecast.
    The caller must pass calibration rows, never validation measurements.
    """
    grid = _sizes(sizes)
    size_lookup = {int(size): index for index, size in enumerate(grid)}
    groups = {}
    success_statuses = {"ok", "success", "completed", "complete"}
    for row in rows:
        if row.get("split", "calibration") != "calibration":
            raise ValueError("forecast calibration must not contain rows from another data split")
        if "block_id" in row:
            block = row["block_id"]
        elif "block" in row:
            block = row["block"]
        else:
            raise ValueError("calibration row is missing block_id")
        try:
            hash(block)
        except TypeError as error:
            raise ValueError("block_id must be hashable") from error
        if (row.get("numerical_valid") is not True
                or row.get("completed", True) is not True
                or row.get("status") not in success_statuses):
            raise ValueError("all calibration runs must complete and be numerically valid")
        size = row.get("size")
        if size not in size_lookup:
            raise ValueError("calibration row has a size outside the declared grid")
        group = groups.setdefault(block, {})
        if size in group:
            raise ValueError("duplicate calibration size within a block")
        try:
            group[size] = (float(row["peak_rss_bytes"]), float(row["cpu_seconds"]))
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError("calibration row is missing valid measured costs") from error
    if not groups or any(len(group) != grid.size for group in groups.values()):
        raise ValueError("calibration requires at least one complete block with every grid size")
    costs = np.array([[group[int(size)] for size in grid] for group in groups.values()])
    return _from_matrices(grid, costs[:, :, 0], costs[:, :, 1], list(groups))


def resample_profiles(profile: Mapping, block_indices) -> dict:
    """Resample whole blocks, retaining pairing and within-resource size paths."""
    grid = _sizes(profile["sizes"])
    memory = _positive_matrix(profile["memory_costs"], grid.size, "memory_costs")
    cpu = _positive_matrix(profile["cpu_costs"], grid.size, "cpu_costs")
    indices = np.asarray(block_indices)
    if (indices.ndim != 1 or indices.size == 0
            or not np.issubdtype(indices.dtype, np.integer)
            or np.any(indices < 0) or np.any(indices >= memory.shape[0])):
        raise ValueError("block_indices must be a nonempty vector of valid integer indices")
    if memory.shape != cpu.shape:
        raise ValueError("memory and CPU profiles must have matching shapes")
    return _from_matrices(grid, memory[indices], cpu[indices],
                          [profile["block_ids"][int(index)] for index in indices])


def max_outcomes(success_matrix, sizes) -> np.ndarray:
    """Largest successful size per path, including zero and upper-grid outcomes.

    Leading dimensions are retained.  A high-size success counts even when
    one or more smaller sizes failed; the experiment does not stop early.
    """
    grid = _sizes(sizes)
    successes = np.asarray(success_matrix)
    if successes.ndim == 0 or successes.shape[-1] != grid.size:
        raise ValueError("success matrix must have a final axis matching the size grid")
    if not np.all((successes == 0) | (successes == 1)):
        raise ValueError("success matrix must contain only booleans or zeros and ones")
    return np.max(np.where(successes.astype(bool), grid, 0), axis=-1)


def outcome_profile(outcomes, sizes) -> dict:
    """Unconditioned PMF and largest-outcome survival on the declared support."""
    grid = _sizes(sizes)
    values = np.asarray(outcomes)
    support = np.r_[0, grid]
    if values.ndim != 1 or values.size == 0 or not np.all(np.isin(values, support)):
        raise ValueError("outcomes must be a nonempty vector on zero plus the declared grid")
    probability = np.mean(values[:, None] == support, axis=0)
    return {"size_support": support, "probability": probability,
            "survival_at_sizes": np.mean(values[:, None] >= grid, axis=0),
            "upper_censor_probability": float(probability[-1]),
            "mean_largest_size": float(np.mean(values))}


def budget_midpoints(cost_curve, *, lower_multiplier=.85, upper_multiplier=1.05) -> np.ndarray:
    """Budget strata below, between and above a monotone median cost curve.

    Equal adjacent costs can yield repeated midpoints; no artificial gap is
    inserted.  Budgets and costs remain in the same physical units.
    """
    costs = np.asarray(cost_curve, dtype=float)
    if (costs.ndim != 1 or costs.size == 0 or np.any(costs <= 0)
            or not np.all(np.isfinite(costs)) or np.any(np.diff(costs) < 0)):
        raise ValueError("cost_curve must be finite, positive and nondecreasing")
    if not (np.isfinite(lower_multiplier) and 0 < lower_multiplier < 1
            and np.isfinite(upper_multiplier) and upper_multiplier > 1):
        raise ValueError("multipliers must place endpoints below and above the curve")
    return np.r_[lower_multiplier * costs[0],
                 .5 * (costs[:-1] + costs[1:]), upper_multiplier * costs[-1]]


def _budgets(values, name: str) -> np.ndarray:
    values = np.atleast_1d(np.asarray(values, dtype=float))
    if values.ndim != 1 or values.size == 0 or not np.all(np.isfinite(values)) or np.any(values < 0):
        raise ValueError(f"{name} must be a nonempty finite nonnegative budget vector")
    return values


def forecast_largest(profile: Mapping, memory_budgets, cpu_budgets, *, mode="joint") -> dict:
    """Replay whole calibration paths under equally weighted paired budgets.

    ``joint`` retains measured memory/CPU dependence.  ``resource_independent``
    combines every memory block with every CPU block, retaining cross-size
    structure within each resource.  This is different from breaking the
    dependence between the assigned *budgets*.  ``median`` uses cumulative-max
    median costs.  The raw empirical paths are never monotonicized.
    """
    grid = _sizes(profile["sizes"])
    memory = _positive_matrix(profile["memory_costs"], grid.size, "memory_costs")
    cpu = _positive_matrix(profile["cpu_costs"], grid.size, "cpu_costs")
    if memory.shape != cpu.shape:
        raise ValueError("memory and CPU profiles must have matching shapes")
    mb = _budgets(memory_budgets, "memory_budgets")
    cb = _budgets(cpu_budgets, "cpu_budgets")
    if mb.shape != cb.shape:
        raise ValueError("memory and CPU budgets must describe the same paired opportunities")
    if mode == "joint":
        success = (memory[None] <= mb[:, None, None]) & (cpu[None] <= cb[:, None, None])
    elif mode == "resource_independent":
        success = ((memory[None, :, None, :] <= mb[:, None, None, None])
                   & (cpu[None, None, :, :] <= cb[:, None, None, None]))
        success = success.reshape(mb.size, -1, grid.size)
    elif mode == "memory_only":
        success = memory[None] <= mb[:, None, None]
    elif mode == "cpu_only":
        success = cpu[None] <= cb[:, None, None]
    elif mode == "median":
        # Recompute from the same raw calibration input; stale supplied median
        # columns cannot silently change this comparator or a bootstrap draw.
        mm = np.maximum.accumulate(np.median(memory, axis=0))
        cm = np.maximum.accumulate(np.median(cpu, axis=0))
        success = (mm[None, None] <= mb[:, None, None]) & (cm[None, None] <= cb[:, None, None])
    else:
        raise ValueError("unknown forecast mode")
    outcomes = max_outcomes(success, grid)
    support = np.r_[0, grid]
    per_probability = np.mean(outcomes[:, :, None] == support, axis=1)
    per_survival = np.mean(outcomes[:, :, None] >= grid, axis=1)
    per_success = np.mean(success, axis=1)
    inversions = np.any((~success[:, :, :-1]) & success[:, :, 1:], axis=-1)
    return {
        "mode": mode, "size_support": support,
        "probability": per_probability.mean(axis=0),
        "survival_at_sizes": per_survival.mean(axis=0),
        "per_budget_probability": per_probability,
        "per_budget_survival_at_sizes": per_survival,
        "per_size_success_probability": per_success.mean(axis=0),
        "per_budget_success_probability": per_success,
        "upper_censor_probability": float(per_probability[:, -1].mean()),
        "per_budget_upper_censor_probability": per_probability[:, -1],
        "mean_largest_size": float(outcomes.mean()),
        "per_budget_mean_largest_size": outcomes.mean(axis=1),
        "replay_paths_per_budget": int(outcomes.shape[1]),
        "nonmonotonicity": {
            "success_path_fraction": float(inversions.mean()),
            "per_budget_success_path_fraction": inversions.mean(axis=1),
            "largest_survival_minus_size_success": (per_survival - per_success).mean(axis=0),
        },
    }
