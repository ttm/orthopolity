"""Lossless field parsing for the published Southern California cluster audit.

These readers validate structure; they do not filter earthquake quality, estimate
completeness, or treat waveform relocation components as physical clusters.
The archived source descriptions specify the columns. In the 1981--2018 source,
the final processing-box label occurs on ``ct`` rows only. Magnitude type is not
supplied by either file and is therefore explicitly missing.
"""

from pathlib import Path
import re

import numpy as np
import pandas as pd


_TIME = ["year", "month", "day", "hour", "minute", "second"]
_LOCATION = ["event_id", "latitude", "longitude", "depth_km", "mag"]
PUBLISHED_COLUMNS = [
    "event_index", *_TIME, *_LOCATION, "log10_proximity",
    "background_largest", "background_first", "parent_index", "published_cluster",
]
RELOCATION_COLUMNS = [
    *_TIME, *_LOCATION, "pick_count", "nearest_station_km", "rms_sec",
    "daynight_flag", "legacy_location_flag", "waveform_cluster",
    "waveform_cluster_size", "differential_time_count",
    "abs_horizontal_error_km", "abs_vertical_error_km",
    "rel_horizontal_error_km", "rel_vertical_error_km",
    "event_type", "location_method", "relocation_box",
]
_INTEGER = re.compile(r"[+-]?[0-9]+\Z")


def _read(path, columns, integer_columns, string_columns=(), optional_box=False):
    """Validate widths and integer tokens before pandas can coerce either."""
    path = Path(path)
    if path.name.endswith(".part"):
        raise ValueError(f"Refusing incomplete download: {path}")
    integer_positions = [columns.index(name) for name in integer_columns]
    nrows = 0
    with path.open(encoding="ascii") as stream:
        for nrows, line in enumerate(stream, 1):
            fields = line.split()
            if optional_box:
                valid = (len(fields) == 26 and fields[24] == "ct") or (
                    len(fields) == 25 and fields[24] in {"1d", "3d", "xx"})
            else:
                valid = len(fields) == len(columns)
            if not valid:
                raise ValueError(f"{path}:{nrows}: unexpected field count or method")
            for position in integer_positions:
                if _INTEGER.fullmatch(fields[position]) is None:
                    raise ValueError(
                        f"{path}:{nrows}: non-integer {columns[position]}")
    if nrows == 0:
        raise ValueError(f"Empty catalogue: {path}")
    dtypes = {name: "float64" for name in columns}
    dtypes.update({name: "int64" for name in integer_columns})
    dtypes.update({name: "string" for name in string_columns})
    try:
        frame = pd.read_csv(path, sep=r"\s+", names=columns, dtype=dtypes,
                            keep_default_na=False, na_values=["NaN", ""],
                            encoding="ascii")
    except (ValueError, TypeError) as error:
        raise ValueError(f"Invalid numeric field in {path}: {error}") from error
    if len(frame) != nrows:
        raise ValueError(f"Row count changed while reading {path}")
    frame.insert(0, "source_line", np.arange(1, len(frame) + 1))
    frame["mag_type"] = pd.Series(pd.NA, index=frame.index, dtype="string")
    _validate_common(frame, path)
    return frame


def _validate_common(frame, path):
    if (frame["event_id"] <= 0).any() or frame["event_id"].duplicated().any():
        raise ValueError(f"Event IDs must be unique positive integers: {path}")
    numeric = frame[["latitude", "longitude", "depth_km", "mag", "second"]]
    if not np.isfinite(numeric.to_numpy()).all():
        raise ValueError(f"Non-finite location, magnitude or time: {path}")
    if not frame["latitude"].between(-90, 90).all() or not frame[
            "longitude"].between(-180, 180).all():
        raise ValueError(f"Coordinates outside geographic bounds: {path}")
    # The published source has a minute=60 record. Preserve it and expose the
    # defect without either inventing a timestamp or silently removing an event.
    frame["clock_fields_valid"] = (
        frame["hour"].between(0, 23) & frame["minute"].between(0, 59)
        & frame["second"].between(0, 61, inclusive="left"))
    # A leap second is retained as recorded; no normalized timestamp is invented.
    try:
        pd.to_datetime(frame[["year", "month", "day"]], errors="raise")
    except (ValueError, OverflowError) as error:
        raise ValueError(f"Invalid calendar date: {path}") from error


def load_published(path):
    """Read the 17-column Zaliapin--Ben-Zion 2020 clustered catalogue.

    ``published_cluster`` references the published event index of the largest
    event, not its SCSN event ID. ``log10_proximity`` may contain the documented
    NaN for a root. The input's magnitude floor is not estimated here.
    """
    integers = ["event_index", *_TIME[:-1], "event_id", "background_largest",
                "background_first", "parent_index", "published_cluster"]
    frame = _read(path, PUBLISHED_COLUMNS, integers)
    if (frame["event_index"] <= 0).any() or frame["event_index"].duplicated().any():
        raise ValueError("Published event indices must be unique and positive")
    for flag in ["background_largest", "background_first"]:
        if not frame[flag].isin([0, 1]).all():
            raise ValueError(f"Invalid published {flag} flag")
    indices = set(frame["event_index"])
    if not frame["published_cluster"].isin(indices).all():
        raise ValueError("Published cluster references an absent event index")
    if not frame["parent_index"].isin(indices | {0}).all():
        raise ValueError("Published parent references an absent event index")
    if np.isinf(frame["log10_proximity"].to_numpy()).any():
        raise ValueError("Infinite published normalized proximity")
    leaders = frame.set_index("event_index").loc[frame["published_cluster"]]
    if not (leaders["published_cluster"].to_numpy() == frame[
            "published_cluster"].to_numpy()).all() or not (
            leaders["background_largest"].to_numpy() == 1).all():
        raise ValueError("Inconsistent published cluster leader reference")
    return frame


def load_relocations(path):
    """Read the 25/26-column original Hauksson 1981--2018 release.

    All ordinary and relocated events, 0/99 error sentinels, event-type flags,
    and original precision are retained. Relative errors describe positions
    within waveform components, which need not coincide with seismic sequences.
    ``legacy_location_flag`` is preserved as an opaque integer because the
    2011 format's superseded description does not explain the 2018 values.
    """
    integers = [*_TIME[:-1], "event_id", "pick_count", "daynight_flag",
                "legacy_location_flag", "waveform_cluster", "waveform_cluster_size",
                "differential_time_count"]
    strings = ["event_type", "location_method", "relocation_box"]
    frame = _read(path, RELOCATION_COLUMNS, integers, strings, optional_box=True)
    numeric = ["nearest_station_km", "rms_sec", "abs_horizontal_error_km",
               "abs_vertical_error_km", "rel_horizontal_error_km",
               "rel_vertical_error_km"]
    if not np.isfinite(frame[numeric].to_numpy()).all():
        raise ValueError("Non-finite relocation quality field")
    return frame
