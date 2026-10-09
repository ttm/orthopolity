"""Area moments of 2D GeoPackage polygons, including holes and all components.

This deliberately small reader supports standard 2D Polygon/MultiPolygon WKB.
It validates structure and moments, but does not establish topological validity.
"""
import math
import sqlite3
import struct
from pathlib import Path

import numpy as np


def unpack_gpkg(blob, expected_srs=27700):
    """Return polygons, each represented by [exterior, interior, ...] arrays."""
    if not isinstance(blob, bytes) or len(blob) < 8 or blob[:3] != b"GP\x00":
        raise ValueError("Expected a version-0 GeoPackage geometry")
    flags = blob[3]
    envelope = (flags >> 1) & 7
    if flags & 0xf0 or envelope not in (0, 1):
        raise ValueError("Only nonempty standard 2D GeoPackage geometries supported")
    header_endian = "<" if flags & 1 else ">"
    if struct.unpack_from(header_endian + "i", blob, 4)[0] != expected_srs:
        raise ValueError("Unexpected geometry coordinate reference system")
    offset = 8 + (32 if envelope else 0)

    def take(fmt):
        nonlocal offset
        size = struct.calcsize(fmt)
        if offset + size > len(blob):
            raise ValueError("Truncated WKB geometry")
        values = struct.unpack_from(fmt, blob, offset)
        offset += size
        return values

    def header():
        order, = take("B")
        if order not in (0, 1):
            raise ValueError("Invalid WKB byte order")
        endian = "<" if order else ">"
        kind, count = take(endian + "II")
        return endian, kind, count

    def polygon(endian, count):
        if count < 1 or count > (len(blob) - offset) // 4:
            raise ValueError("Invalid WKB ring count")
        rings = []
        for _ in range(count):
            n, = take(endian + "I")
            if n < 4 or n > (len(blob) - offset) // 16:
                raise ValueError("Invalid WKB vertex count")
            points = np.asarray(take(endian + "dd" * n)).reshape(n, 2)
            if not np.isfinite(points).all() or not np.array_equal(points[0], points[-1]):
                raise ValueError("Rings must be finite and closed")
            rings.append(points)
        return rings

    endian, kind, count = header()
    if kind == 3:
        polygons = [polygon(endian, count)]
    elif kind == 6:
        if count < 1 or count > (len(blob) - offset) // 9:
            raise ValueError("Invalid WKB polygon count")
        polygons = []
        for _ in range(count):
            endian, child_kind, nrings = header()
            if child_kind != 3:
                raise ValueError("Expected 2D Polygon within MultiPolygon")
            polygons.append(polygon(endian, nrings))
    else:
        raise ValueError("Expected standard 2D Polygon or MultiPolygon")
    if offset != len(blob):
        raise ValueError("Unparsed geometry bytes")
    return polygons


def polygon_moments(polygons):
    """Return area, centroid and area-weighted radius for full multipolygon.

    Interior rings are subtracted by their WKB position, independently of ring
    orientation. Coordinates must share a planar metric CRS. No repair is done.
    """
    if not polygons or any(not polygon for polygon in polygons):
        raise ValueError("At least one nonempty polygon required")
    origin = np.asarray(polygons[0][0], float)[0]
    if origin.shape != (2,) or not np.isfinite(origin).all():
        raise ValueError("Finite 2D coordinates required")
    totals = []
    for polygon in polygons:
        component = []
        for i, ring in enumerate(polygon):
            points = np.asarray(ring, float)
            if points.ndim != 2 or points.shape[1] != 2 or len(points) < 4:
                raise ValueError("A ring needs at least four 2D vertices")
            if not np.isfinite(points).all() or not np.array_equal(points[0], points[-1]):
                raise ValueError("Rings must be finite and closed")
            p = points[:-1] - origin
            q = np.roll(p, -1, axis=0)
            cross = p[:, 0] * q[:, 1] - q[:, 0] * p[:, 1]
            area = float(cross.sum() / 2)
            if area == 0:
                raise ValueError("Zero-area ring")
            first = ((p + q) * cross[:, None]).sum(axis=0) / 6
            polar = float(((p * p + p * q + q * q).sum(axis=1) * cross).sum() / 12)
            sign = (1 if area > 0 else -1) * (1 if i == 0 else -1)
            component.append(sign * np.array([area, first[0], first[1], polar]))
        combined = np.sum(component, axis=0)
        if combined[0] <= 0:
            raise ValueError("Holes exhaust polygon area")
        totals.append(combined)
    area, mx, my, polar = np.sum(totals, axis=0)
    center = np.array([mx, my]) / area
    radius2 = float(polar / area - np.dot(center, center))
    if not np.isfinite([area, *center, radius2]).all() or radius2 <= 0:
        raise ValueError("Nonpositive or nonfinite area moment")
    centroid = origin + center
    return dict(area_m2=float(area), centroid_e_m=float(centroid[0]),
                centroid_n_m=float(centroid[1]), rg_m=math.sqrt(radius2))


def read_ukceh(path):
    """Read the frozen inventory without writing to the source GeoPackage."""
    path = Path(path).resolve()
    with sqlite3.connect(path.as_uri() + "?mode=ro", uri=True) as connection:
        schema = connection.execute("SELECT table_name, column_name, geometry_type_name, "
                                    "srs_id, z, m FROM gpkg_geometry_columns").fetchall()
        expected = [("uklakes_v3_6_poly", "geom", "MULTIPOLYGON", 27700, 0, 0)]
        if schema != expected:
            raise ValueError("Unexpected UKCEH GeoPackage geometry schema")
        rows, identifiers = [], set()
        for wbid, blob in connection.execute("SELECT WBID, geom FROM uklakes_v3_6_poly ORDER BY WBID"):
            if wbid is None or wbid in identifiers:
                raise ValueError("Missing or duplicate WBID")
            identifiers.add(wbid)
            try:
                moment = polygon_moments(unpack_gpkg(blob))
            except ValueError as error:
                raise ValueError(f"WBID {wbid}: {error}; no selective exclusion permitted") from error
            rows.append(dict(WBID=wbid, **moment))
    return rows


def spatial_grid(centroids, side_m=100000.0):
    """Integer cells anchored at EPSG:27700 (0,0); floor handles negatives."""
    xy = np.asarray(centroids, float)
    if xy.ndim != 2 or xy.shape[1] != 2 or not np.isfinite(xy).all():
        raise ValueError("Every selected lake requires a finite 2D centroid")
    if not np.isfinite(side_m) or side_m <= 0:
        raise ValueError("Positive finite grid size required")
    return np.floor(xy / side_m).astype(np.int64)
