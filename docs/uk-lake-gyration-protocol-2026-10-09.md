# UK lake radius replication: fixed before calculation

This is a separate regional replication of the log-orthopolic territory
prediction, not a replacement for the original global HydroLAKES test.
Commit this note, [configuration](../configs/uk_lake_gyration_2026-10-09.json),
runner and geometry tests before computing UK radii. The commit timestamp is
the authoritative freeze. Metadata, feature/ring counts and source documentation
have already been inspected; no UK radius, eligible sample, block count or
exponent has been computed.

The input is the retained UKCEH v3.6 GeoPackage, identified by the configuration's
SHA-256. Its 41,830 mapped waterbodies are observations, including any separately
mapped basins. Use uniform area within each full multipolygon, subtract holes,
and include separation between components when computing radius about the
full centroid. Keep supplied EPSG:27700 coordinates in metres. This avoids
deriving radius from area but does not claim geodesic distance exactness.

Select inclusively **1 ≤ R ≤ 20 km**, matching the original amended radius
range. Fit a bounded power law, reporting survival exponent ζ = α − 1.
The prediction is ζ = 2; equivalence band [1.9, 2.1]. Use seed 20261009 and
independent random streams for 1,000 iid resamples, 1,000 spatial-block resamples,
and 1,000 parametric bounded-KS goodness-of-fit draws with refitting.

Spatial blocks are fixed 100 km squares anchored at British National Grid
(0,0), assigned by each full geometry centroid after radius selection.
Resample the occupied cells uniformly, preserving all selected waterbodies
in each sampled cell. No alternative grid size or origin will be chosen after
seeing results. This sensitivity does not prove independence among blocks.

The result is **insufficient** below 100 eligible lakes or ten occupied blocks,
or if either interval is unavailable. Otherwise, both intervals wholly within
the band give conditional exponent agreement; either interval disjoint from
the band gives an exponent departure; remaining outcomes are inconclusive.
Report that exponent decision separately from distribution adequacy. If the
iid KS diagnostic has p ≤ 0.1, make no positive support claim and describe
the fitted exponent as a summary of a distribution that failed that diagnostic.
Non-rejection does not validate the sampling model.

Invalid binary structure, missing identifiers or nonphysical area moments abort
the run. No outcome-dependent exclusion, polygon repair, merging of basins,
classification by lake name or inferred reservoir removal is permitted.
Topological validity beyond structural/moment checks remains unverified.

Constraints include historical mapping, selective updates, omission of small
ponds, an unknown reservoir mixture, possible basin splitting and area-based
detection of elongated features. This UK inventory is not an independent
geographical holdout from the global inventory. An exponent result alone does
not identify territorial competition or an allocation mechanism.

Before real data, validate rectangle moments under rigid motion and scaling,
hole subtraction, separated components, binary geometry reading and invalid
inputs. Check bounded simulated exponents 2 and 2.3, eligibility boundaries,
empty selections and increased uncertainty for spatially correlated samples.
These checks use synthetic geometry only.

Run from the repository root with the merged numerical dependencies:

```sh
PYTHONPATH=src python experiments/run_uk_lake_gyration.py \
  --output results/uk-lake-gyration-2026-10-09/result.json
```

Retain the full derived table locally, its checksum, run environment, protocol
commit, result bytes and all declared outcomes, including insufficient results.
