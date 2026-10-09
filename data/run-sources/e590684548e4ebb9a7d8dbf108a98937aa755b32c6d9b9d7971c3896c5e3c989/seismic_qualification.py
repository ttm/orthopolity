"""Qualification gates for the registered hypocentre-dimension experiment.

This module calculates magnitude completeness and the *availability* of a
resolved distance interval. It never estimates b, a correlation slope, or a
hypothesis verdict. Cluster membership and quality filters belong to the
separately frozen input protocol.
"""

import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist


MIN_EVENTS = 200
D2_CAP = 3000
MIN_SCALING_RATIO = 3
MAGNITUDE_FLOOR = 2.0
KM_PER_DEG = 111.195
REQUIRED_COLUMNS = (
    "event_id", "latitude", "longitude", "depth_km", "mag", "loc_err_km"
)


def absolute_location_error(horizontal_km, vertical_km):
    """Combine positive, finite absolute errors in kilometres in quadrature.

    Zero or missing reported errors are not treated as perfect precision.
    The caller is responsible for using absolute, rather than relative,
    catalogue error fields and for converting their units to kilometres.
    """
    horizontal = np.asarray(horizontal_km, dtype=float)
    vertical = np.asarray(vertical_km, dtype=float)
    horizontal, vertical = np.broadcast_arrays(horizontal, vertical)
    if (not np.isfinite(horizontal).all() or not np.isfinite(vertical).all()
            or np.any(horizontal <= 0) or np.any(vertical <= 0)):
        raise ValueError("Absolute location errors must be finite and positive")
    result = np.hypot(horizontal, vertical)
    if not np.isfinite(result).all():
        raise ValueError("Combined absolute location errors must be finite")
    return result


def coordinates(frame):
    """Use the original runner's local conversion, with depths in kilometres."""
    lat = frame["latitude"].to_numpy(dtype=float)
    lon = frame["longitude"].to_numpy(dtype=float)
    depth = frame["depth_km"].to_numpy(dtype=float)
    if not len(lat) or not np.isfinite(np.column_stack([lat, lon, depth])).all():
        raise ValueError("Nonempty finite hypocentres required")
    if np.any(np.abs(lat) > 90) or np.any(np.abs(lon) > 180):
        raise ValueError("Latitude or longitude outside degree bounds")
    return np.column_stack([
        KM_PER_DEG * np.cos(np.radians(lat.mean())) * (lon - lon.mean()),
        KM_PER_DEG * (lat - lat.mean()),
        depth,
    ])


def scaling_range(pair_distances_km, loc_err_km):
    """Return the amended interval and eligibility, without any C(r) slope.

    Zero distances are excluded exactly as in the registered runner. The
    200th-positive-pair floor and the inclusive factor-three boundary are
    unchanged. A degenerate cloud returns an explicit rejection.
    """
    distances = np.asarray(pair_distances_km, dtype=float)
    if distances.ndim != 1 or not np.isfinite(distances).all() or np.any(distances < 0):
        raise ValueError("Pair distances must be a finite nonnegative vector")
    if not np.isfinite(loc_err_km) or loc_err_km <= 0:
        raise ValueError("Location error must be finite and positive")
    positive = np.sort(distances[distances > 0])
    out = {
        "n_pairs": int(len(distances)),
        "n_positive_pairs": int(len(positive)),
        "n_zero_pairs": int(len(distances) - len(positive)),
        "pair_floor_km": None,
        "error_floor_km": float(3 * loc_err_km),
        "pair_q90_km": None,
        "geometry_only_ratio": None,
        "r_min_km": None,
        "r_max_km": None,
        "scaling_ratio": None,
        "radii_km": [],
        "range_eligible": False,
        "range_reason": "degenerate_geometry",
    }
    if not len(positive):
        return out
    pair_floor = float(positive[min(199, len(positive) - 1)])
    q90 = float(np.quantile(positive, 0.9))
    lo, hi = max(pair_floor, 3 * loc_err_km), 0.1 * q90
    eligible = bool(hi >= MIN_SCALING_RATIO * lo)
    out.update(
        pair_floor_km=pair_floor,
        pair_q90_km=q90,
        geometry_only_ratio=float(hi / pair_floor),
        r_min_km=float(lo),
        r_max_km=float(hi),
        scaling_ratio=float(hi / lo),
        radii_km=np.geomspace(lo, hi, 15).tolist() if eligible else [],
        range_eligible=eligible,
        range_reason=None if eligible else "scaling_range_too_short",
    )
    return out


def qualify_cluster(frame, seed):
    """Return a JSON-safe qualification ledger for one frozen cluster.

    Pass ``np.random.SeedSequence([202610092, int(cluster_id)])`` for the
    declared per-cluster stream. The function also accepts an integer seed.
    Rows are sorted by the string representation of their unique event IDs
    before selection; the sample IDs therefore survive input-row permutation.
    No malformed row is silently discarded. All error values must be finite
    and positive, including rows below completeness.
    """
    out = {
        "eligible": False,
        "reasons": [],
        "n_input": int(len(frame)),
        "n_complete": 0,
        "n_sampled": 0,
        "n_above_magnitude_floor": 0,
        "mc_maxcurv_plus02": None,
        "mc": None,
        "magnitude_floor": MAGNITUDE_FLOOR,
        "median_location_error_km": None,
        "n_unique_hypocentres_sampled": None,
        "sampled_event_ids": [],
    }
    missing = sorted(set(REQUIRED_COLUMNS) - set(frame.columns))
    if missing:
        out["reasons"] = ["missing_columns"]
        out["missing_columns"] = missing
        return out
    if not len(frame):
        out["reasons"] = ["empty_cluster"]
        return out
    raw_ids = frame["event_id"]
    ids = raw_ids.astype(str)
    if raw_ids.isna().any() or ids.str.strip().eq("").any():
        out["reasons"].append("invalid_event_ids")
    if ids.duplicated().any():
        out["reasons"].append("duplicate_event_ids")
    if "cluster" in frame and (frame["cluster"].isna().any()
                              or frame["cluster"].nunique() != 1):
        out["reasons"].append("mixed_or_missing_cluster_ids")
    numeric = {}
    for column in REQUIRED_COLUMNS[1:]:
        try:
            numeric[column] = frame[column].to_numpy(dtype=float)
        except (TypeError, ValueError):
            out["reasons"].append(f"nonnumeric_{column}")
            continue
        bad = ~np.isfinite(numeric[column])
        out[f"n_nonfinite_{column}"] = int(bad.sum())
        if bad.any():
            out["reasons"].append(f"nonfinite_{column}")
    if "loc_err_km" in numeric:
        n_nonpositive = int((numeric["loc_err_km"] <= 0).sum())
        out["n_nonpositive_loc_err_km"] = n_nonpositive
        if n_nonpositive:
            out["reasons"].append("nonpositive_loc_err_km")
    for column, limit in (("latitude", 90), ("longitude", 180)):
        if column in numeric and np.any(np.abs(numeric[column]) > limit):
            out["reasons"].append(f"out_of_bounds_{column}")
    if out["reasons"]:
        return out

    # Work from copies so the caller's input and scientific fields are intact.
    ordered = pd.DataFrame(numeric)
    ordered["event_id"] = ids.to_numpy()
    ordered = ordered.sort_values("event_id", kind="stable").reset_index(drop=True)
    m = np.round(ordered["mag"].to_numpy(), 1)
    values, counts = np.unique(m, return_counts=True)
    mc_raw = float(values[np.argmax(counts)] + 0.2)
    mc = max(MAGNITUDE_FLOOR, mc_raw)
    complete = ordered.loc[m >= mc - 1e-9].reset_index(drop=True)
    out.update(
        n_complete=int(len(complete)),
        n_above_magnitude_floor=int(np.count_nonzero(m >= MAGNITUDE_FLOOR - 1e-9)),
        mc_maxcurv_plus02=mc_raw,
        mc=mc,
    )
    if len(complete) < MIN_EVENTS:
        out["reasons"] = ["fewer_than_200_complete_events"]
        return out
    loc_err = float(complete["loc_err_km"].median())
    xyz = coordinates(complete)
    if len(complete) > D2_CAP:
        rng = np.random.default_rng(seed)
        index = np.sort(rng.choice(len(complete), D2_CAP, replace=False))
    else:
        index = np.arange(len(complete))
    xyz = xyz[index]
    out.update(
        median_location_error_km=loc_err,
        n_sampled=int(len(index)),
        sampled_event_ids=complete.iloc[index]["event_id"].tolist(),
        n_unique_hypocentres_sampled=int(len(np.unique(xyz, axis=0))),
    )
    interval = scaling_range(pdist(xyz), loc_err)
    out.update(interval)
    out["eligible"] = interval["range_eligible"]
    if interval["range_reason"]:
        out["reasons"] = [interval["range_reason"]]
    return out
