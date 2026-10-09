"""Local WGS84 lake geometry and deterministic hydrological point matching.

The moments use straight segments between projected source vertices. They are
locally metric approximations, not intrinsic geodesic surface moments.
"""
import numpy as np


def signed_ring_moments(rings):
    """ESRI winding: clockwise shells add area, counterclockwise holes subtract.

    All components contribute their parallel-axis terms. No ring repair or
    automatic reversal is allowed. Topological validity is a separate check.
    """
    totals, shells = [], []
    for ring in rings:
        p = np.asarray(ring, float)
        if (p.ndim != 2 or p.shape[1] != 2 or len(p) < 4
                or not np.isfinite(p).all() or not np.array_equal(p[0], p[-1])):
            raise ValueError('Every ring must be finite, 2D and closed')
        a, b = p[:-1], p[1:]
        cross = a[:, 0]*b[:, 1] - b[:, 0]*a[:, 1]
        area = -cross.sum()/2
        if area == 0:
            raise ValueError('Zero-area ring')
        first = -((a+b)*cross[:, None]).sum(axis=0)/6
        polar = -((a*a+a*b+b*b).sum(axis=1)*cross).sum()/12
        moment = np.array([area, *first, polar])
        totals.append(moment)
        if area > 0:
            shells.append(moment)
    if not shells:
        raise ValueError('No clockwise exterior ring')

    def finish(moment):
        area, mx, my, polar = moment
        if area <= 0:
            raise ValueError('Nonpositive net area')
        center = np.array([mx, my])/area
        radius2 = polar/area - center @ center
        if not np.isfinite([area, *center, radius2]).all() or radius2 <= 0:
            raise ValueError('Nonpositive or nonfinite area moment')
        return dict(area_m2=float(area), rg_m=float(np.sqrt(radius2)),
                    cx_m=float(center[0]), cy_m=float(center[1]))

    return dict(full=finish(np.sum(totals, axis=0)),
                largest=finish(max(shells, key=lambda m: m[0])),
                n_shells=len(shells), n_holes=len(totals)-len(shells))


def local_geometry(points, parts, check_topology=False):
    """LAEA primary, geodesic AEQD sensitivity, centred at first source vertex."""
    from pyproj import Geod, Proj
    pts = np.asarray(points, float)
    if (pts.ndim != 2 or pts.shape[1] != 2 or not len(pts)
            or not np.isfinite(pts).all() or np.any(np.abs(pts[:, 1]) > 90)):
        raise ValueError('Valid WGS84 coordinates required')
    starts = list(parts)
    if not starts or starts[0] != 0 or starts != sorted(set(starts)) or starts[-1] >= len(pts):
        raise ValueError('Invalid ring offsets')
    spans = list(zip(starts, starts[1:]+[len(pts)]))
    lon, lat = pts[0]
    lon = (lon+180) % 360-180
    projection = Proj(proj='laea', lon_0=lon, lat_0=lat, ellps='WGS84', units='m')
    xy = np.column_stack(projection(pts[:, 0], pts[:, 1]))
    rings = [xy[s:e] for s, e in spans]
    primary = signed_ring_moments(rings)
    geod = Geod(ellps='WGS84')
    azimuth, _, distance = geod.inv(np.full(len(pts), lon), np.full(len(pts), lat),
                                   pts[:, 0], pts[:, 1])
    angle = np.deg2rad(azimuth)
    aeqd = np.column_stack((distance*np.sin(angle), distance*np.cos(angle)))
    alternative = signed_ring_moments([aeqd[s:e] for s, e in spans])
    geodesic_area = -sum(geod.polygon_area_perimeter(pts[s:e, 0], pts[s:e, 1])[0]
                         for s, e in spans)
    if geodesic_area <= 0:
        raise ValueError('Nonpositive signed geodesic area')
    out = dict(rg_laea_km=primary['full']['rg_m']/1000,
               rg_aeqd_km=alternative['full']['rg_m']/1000,
               rg_laea_largest_km=primary['largest']['rg_m']/1000,
               area_laea_km2=primary['full']['area_m2']/1e6,
               area_geodesic_km2=geodesic_area/1e6,
               max_center_distance_km=float(distance.max()/1000),
               n_shells=primary['n_shells'], n_holes=primary['n_holes'])
    out['topology_valid'] = None
    if check_topology and 1 <= out['rg_laea_km'] <= 20:
        # pyshp's ring organisation uses ESRI winding and containment. Projected
        # coordinates prevent geographic date-line edges from confusing GEOS.
        import shapefile
        from shapely.geometry import shape
        shp = shapefile.Shape(shapeType=5, points=xy.tolist(), parts=starts)
        out['topology_valid'] = bool(shape(shp.__geo_interface__).is_valid)
    return out


class BasinIndex:
    """Boundary-inclusive outlet join; ties choose the smallest HYBAS_ID."""
    def __init__(self, shapes, identifiers):
        from shapely import STRtree
        self.ids = np.asarray(identifiers, dtype=np.int64)
        if len(shapes) != len(self.ids) or len(set(self.ids)) != len(self.ids):
            raise ValueError('One unique basin ID per geometry required')
        self.tree = STRtree(shapes)

    def match(self, longitudes, latitudes):
        from shapely import points
        lon, lat = np.asarray(longitudes, float), np.asarray(latitudes, float)
        if (lon.ndim != 1 or lat.shape != lon.shape or not np.isfinite([lon, lat]).all()
                or np.any(np.abs(lon) > 180) or np.any(np.abs(lat) > 90)):
            raise ValueError('Aligned valid outlet coordinates required')
        # Some source coastline vertices extend slightly past 180 degrees.
        # Query equivalent longitudes, deduplicating the same point/basin pair.
        shifted = np.concatenate((lon-360, lon, lon+360))
        pairs = self.tree.query(points(shifted, np.tile(lat, 3)), predicate='intersects')
        pairs[0] %= len(lon)
        pairs = np.unique(pairs, axis=1)
        result = np.full(len(lon), np.iinfo(np.int64).max, dtype=np.int64)
        multiplicity = np.zeros(len(lon), dtype=np.int64)
        np.minimum.at(result, pairs[0], self.ids[pairs[1]])
        np.add.at(multiplicity, pairs[0], 1)
        result[multiplicity == 0] = 0
        return result, multiplicity
