"""Structural audit only; no radius estimates, selection, or exponent fits.

Run from any directory with Python 3. Uses only the standard library.
"""
from collections import Counter
from pathlib import Path
import hashlib
import json
import math
import sqlite3
import struct
import zipfile


ROOT = Path(__file__).resolve().parent
ZIP = ROOT / "ukceh_lakes_v3_6.zip"
GPKG = ROOT / "uklakes_v3_6_poly.gpkg"


def unpack_geometry(blob):
    """Parse the 2D MultiPolygon WKB supplied by this GeoPackage."""
    assert blob[:2] == b"GP", "Not a GeoPackage geometry"
    envelope_code = (blob[3] >> 1) & 7
    offset = 8 + {0: 0, 1: 32, 2: 48, 3: 48, 4: 64}[envelope_code]
    endian = "<" if blob[offset] else ">"
    kind, npolys = struct.unpack_from(endian + "II", blob, offset + 1)
    assert kind == 6, f"Unexpected WKB type {kind}"
    offset += 9
    rings = []
    for _ in range(npolys):
        endian = "<" if blob[offset] else ">"
        kind, nrings = struct.unpack_from(endian + "II", blob, offset + 1)
        assert kind == 3, f"Unexpected child WKB type {kind}"
        offset += 9
        for _ in range(nrings):
            npoints = struct.unpack_from(endian + "I", blob, offset)[0]
            offset += 4
            coords = struct.unpack_from(endian + "d" * (2 * npoints), blob, offset)
            offset += 16 * npoints
            rings.append((npoints, coords[:2] == coords[-2:], all(map(math.isfinite, coords))))
    assert offset == len(blob), "Unparsed geometry bytes"
    return npolys, rings


def main():
    with zipfile.ZipFile(ZIP) as archive:
        assert archive.testzip() is None, "ZIP CRC failed"
        expected = archive.read("data/uklakes_v3_6_poly.gpkg")
    assert GPKG.read_bytes() == expected, "Extracted file differs from archive"
    connection = sqlite3.connect(f"file:{GPKG}?mode=ro", uri=True)
    assert connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    records = connection.execute("SELECT WBID, geom, POLY_AREA_HA, POLY_PERIMETER_KM FROM uklakes_v3_6_poly").fetchall()
    counts = Counter()
    for _, geometry, _, _ in records:
        npolys, rings = unpack_geometry(geometry)
        counts["geometry_records_parsed"] += 1
        counts["records_with_multiple_polygons"] += npolys > 1
        counts["polygons"] += npolys
        counts["rings"] += len(rings)
        counts["interior_rings"] += len(rings) - npolys
        counts["vertices_including_closing_duplicates"] += sum(r[0] for r in rings)
        counts["unclosed_rings"] += sum(not r[1] for r in rings)
        counts["rings_with_nonfinite_coordinates"] += sum(not r[2] for r in rings)
        counts["rings_fewer_than_four_vertices"] += sum(r[0] < 4 for r in rings)
    receipt = {
        "retrieved_client_date": "2026-10-09",
        "source_landing_page": "https://catalogue.ceh.ac.uk/documents/b6b92ce3-dcd7-4f0b-8e43-e937ddf1d4eb",
        "download_url": "https://data-package.ceh.ac.uk/data/b6b92ce3-dcd7-4f0b-8e43-e937ddf1d4eb.zip",
        "files": {p.name: {"bytes": p.stat().st_size, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in (ZIP, GPKG)},
        "archive_crc": "pass",
        "sqlite_integrity": "ok",
        "record_count": len(records),
        "unique_wbids": len({r[0] for r in records}),
        "null_geometry_count": sum(r[1] is None for r in records),
        "nonpositive_or_null_area_count": sum(r[2] is None or r[2] <= 0 for r in records),
        "nonpositive_or_null_perimeter_count": sum(r[3] is None or r[3] <= 0 for r in records),
        "geometry_columns": connection.execute("SELECT * FROM gpkg_geometry_columns").fetchall(),
        "schema": connection.execute('PRAGMA table_info("uklakes_v3_6_poly")').fetchall(),
        "geometry_structure": dict(counts),
        "not_checked": ["self-intersections or other topological validity", "physical completeness", "reservoir membership", "radius of gyration", "exponent or hypothesis test"],
    }
    (ROOT / "ukceh_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
