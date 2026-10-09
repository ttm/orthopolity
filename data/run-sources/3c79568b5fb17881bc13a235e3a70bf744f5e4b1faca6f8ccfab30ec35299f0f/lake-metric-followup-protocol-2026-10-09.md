# Global lake geometry and hydrological follow-up

This is a **follow-up after seeing the original global and UK outcomes**, not a
new independent confirmation. The original global survival exponent was 1.9295,
with iid interval [1.9185, 1.9408] and Country interval [1.5945, 2.0296].
EPSG:6933 preserves area but distorts distance. The original largest-ring
calculation also omitted holes and secondary components. The present choices,
implementation and synthetic checks must be committed before computing the new
real-data radii. That commit is the local freeze, not external preregistration.

## Geometry and observation unit

Use every feature of the pinned HydroLAKES v1.0 archive, preserving its IDs,
Latin1 DBF labels and mapping units. Do not join split lake basins or infer new
reservoir labels. For each feature, centre a WGS84 ellipsoidal Lambert azimuthal
equal-area (LAEA) projection on its first source vertex, a deterministic point
on the feature. Use every ring: clockwise shells add area and moments;
counterclockwise holes subtract, following the
[ESRI specification](https://downloads.esri.com/support/whitepapers/ao_/shapefile.pdf).
Compute the full area-weighted planar second moment about its centroid.

[PROJ LAEA](https://proj.org/en/stable/operations/projections/laea.html) supplies
the ellipsoidal equal-area projection. Distances are local approximations;
this is **not** an exact intrinsic geodesic radius of gyration. For every lake,
also compute WGS84 azimuthal-equidistant coordinates from
[geodesic inverse distances and azimuths](https://pyproj4.github.io/pyproj/stable/api/geod.html),
and a LAEA largest-exterior-ring radius. Both sensitivities get their own
inclusive 1–20 km selections. Their cohorts are not chosen using old radii.
Straight segments connect mapped vertices. Record independent signed geodesic
polygon area as a discretization/projection diagnostic.

Reject malformed, unclosed, nonfinite, zero-area rings, nonpositive full
moments, invalid coordinates and duplicate IDs by stopping the run; no repair
or silent exclusions. Check full selected geometry topology using GEOS after
projecting, and report invalid counts without removing observations. A positive
geometry interpretation requires all selected topologies valid, every selected
vertex within 200 km of its projection centre, and maximum relative AEQD/LAEA
radius discrepancy no larger than 0.001. Report failed gates transparently.

## Spatial uncertainty and decision

Acquire all nine official standard HydroBASINS v1.c level-3 regional files;
retain source URLs, hashes, license and schema before analysis. Join each
source outlet (Pour_long, Pour_lat) to a closed basin polygon in WGS84;
boundary/overlap ties choose the smallest HYBAS_ID. Unmatched outlets remain
unmatched. No nearest-neighbour assignment or post-fit join tuning.

Before lake outcomes, source inspection found 209 of 292 basin geometries have
GEOS-invalid topology, predominantly self-touching grid rings. For the **basin
overlay only**, apply Shapely 2.1.2 `make_valid(method='linework')` to invalid
features, retain polygonal parts, and require valid nonempty output. Preserve
the original archives. This is separate from the no-repair lake geometry rule.
Query equivalent outlet longitudes λ and λ±360 and deduplicate point/basin
pairs: a few source coastline vertices extend slightly beyond 180°. No other
coordinate nudging is permitted. Lake projection centres are likewise reduced
modulo 360; geodesic operations handle wrapped source longitudes.

Fit the bounded radius-density power law on 1–20 km, with survival parameter
ζ = α−1. Territory allocation per **d ln R** predicts ζ=2; the established
practical equivalence band is [1.9,2.1]. Use 1,000 iid and 1,000 basin-cluster
bootstrap draws, percentile 95% intervals, seed 202610091 and independent
streams. Sample occupied basins uniformly, retaining all their lakes and
multiplicities. Report both global and matched-only point/iid results; the basin
interval describes the matched cohort. Country resampling on all selected
lakes is a fixed sensitivity, retaining unequal cluster sizes.

Require ≥100 lakes and ≥10 occupied basins. Matched-cohort equivalence needs
both intervals inside the band; robust departure needs both intervals wholly
below it or both wholly above it. Otherwise call it inconclusive. A positive
**global** reading additionally requires 100% spatial-join coverage and all
geometry gates. Missing coverage cannot silently change the population.

Run the existing bounded, refitted parametric KS bootstrap with 1,000 iid
simulations. This is a descriptive diagnostic, not calibrated for spatial
dependence. If p≤0.1, suppress positive power-law support language; nonrejection
does not establish adequacy. Record KS distance and compare empirical/fitted
survival curves. No adaptive cutoffs or alternate basin levels will be chosen.

## Validation and reporting

Before real data, test analytic hole/component moments; polar and date-line
geodesic shapes; AEQD against PROJ; malformed input; boundary/overlap/unmatched
basin joins; estimator against the existing MLE; true ζ=2 and ζ=2.3 worlds;
and increased uncertainty when lake sizes are clustered. Commit this protocol,
the config, code, tests and synthetic results before the new run.

Keep full derived tables locally with a checksum; retain selected fitting
tables, unmatched outlet IDs, geometry diagnostics, source manifest, runtime,
logs and plots. Append the run to the immutable registry. Report selection
changes and original-projection comparisons after freezing the new methods.
No result here alone establishes an orthopolic allocation mechanism.
