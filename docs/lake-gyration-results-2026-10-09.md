# Lake-radius results, 9 October 2026

**The global estimate is close to the territory prediction under the original
equivalence rule. Spatial uncertainty prevents claiming robust confirmation.**
The separate UK replication gives a lower point estimate, but its spatial
interval also includes 2. Neither result settles a universal allocation claim.

All exponents below are **survival exponents** ζ for radius of gyration;
the corresponding density exponent is α = ζ + 1. The hypothesis is
log-orthopolic territory allocation with ζ = 2, and the predeclared equivalence
band is [1.9, 2.1].

| Analysis | Eligible lakes | ζ | Ordinary 95% interval | Spatial 95% interval |
|---|---:|---:|---|---|
| HydroLAKES original global pipeline | 119,683 | 1.92951 | [1.91852, 1.94083] | [1.59451, 2.02960], Country blocks |
| UKCEH regional replication | 148 | 1.44132 | [1.19125, 1.71437] | [1.16567, 2.00870], fixed 100 km cells |

## Global: conditional equivalence, incomplete spatial qualification

The full 1,427,688-feature HydroLAKES v1.0 archive was downloaded, hashed and
checked. The original script at `f846670` was frozen in `d3f471c` before the
first calculation. Its first attempt failed on a non-UTF-8 lake-name field.
The failure is retained; `c54cf24` recorded a one-line lossless text-decoding
correction before the successful run. Geometry, numeric fields, selection,
estimators, bootstrap and decision rule were preserved. The
[execution plan](lake-gyration-run-plan-2026-10-09.md) describes that history.

The original calculation uses the largest polygon ring in EPSG:6933, ignoring
holes and other exterior components, and selects inclusive radius 1–20 km.
The bounded MLE is 1.92951. Its 1,000-draw iid interval lies inside [1.9, 2.1],
so the literal script verdict is **supports H_territory**. Exact 2 is outside
that narrow interval: the passing criterion is practical equivalence within
the predeclared margin, not exact equality.

The source has no HydroBASINS identifier. The original registration's
two-interval spatial support requirement is therefore not completed by this
script. Its explicitly unregistered 500-draw Country-block interval extends
well below 1.9, so that sensitivity does not establish equivalence. All selected
lakes have country labels; there are 166 countries, with 54.9% of selected lakes
in the largest group. Resampling such unequal countries is not equivalent to
basin resampling or a calibrated hydrological dependence model.

The predeclared `Lake_type == 1` sensitivity retains 115,240 lakes and gives
ζ = **2.00407**. This means not flagged as reservoir/regulated, not verified
natural status; the original script supplies no interval for that sensitivity.
The area–radius OLS slope is 1.79026. It is descriptive and does not identify
a mechanism or establish an exact exponent-conversion identity with scatter.

Projection distortions, antimeridian handling, omitted geometry, inventory
inclusion by area and the absence of an original goodness-of-fit gate remain
unresolved. No new geometry or fit was chosen after inspecting this outcome.

## UK: lower estimate, spatial rejection not established

The separate [UK protocol](uk-lake-gyration-protocol-2026-10-09.md), code and
synthetic checks were committed in `c4ebb71` before UK radius calculation.
All 41,830 input features were processed. Full multipolygons, including holes
and component separation, were measured in supplied EPSG:27700 coordinates.
The same radius interval selects 148 features across 29 fixed 100 km cells,
passing the minimum gates of 100 features and ten occupied blocks.

The frozen rule calls a departure if **either** uncertainty interval is wholly
outside [1.9, 2.1]. The ordinary interval does that, so the recorded verdict is
**against H_territory**. The spatial interval includes 2, however. Report this
as a departure under that rule, not as a spatially robust rejection.
The bounded-power-law iid KS diagnostic gives p = 0.934; it does not reject
that fitted form but does not validate independence or territorial allocation.

The source lacks reservoir classification, includes split basins and has a
historical mapping footprint. The UK and global sources can overlap. Their
different results cannot be attributed solely to geography: projection,
geometry treatment, mapping and cohort also differ.

## Reproduction and audit

The [global result](../results/lake-gyration-2026-10-09/result.json) and
[UK result](../results/uk-lake-gyration-2026-10-09/result.json) retain every
declared outcome. Their directories also contain execution versions/hashes,
selected fitting tables and independent likelihood-score checks. Both point
estimates agree with an independently solved score equation to the bounded
optimizer's numerical precision. All original source IDs are unique and all
computed global radii are finite and positive.

The full global derived table (87.5 MB) and large geometries are kept locally
outside Git; their hashes and a verified restoration path are retained. The
UK derived table is likewise regenerable, while its original GeoPackage is
tracked. Numerical libraries were NumPy 2.3.5 and SciPy 1.17.0 on Python 3.11.6;
the global reader used pandas 2.3.3, pyshp 3.1.6 and pyproj 3.7.2. The successful
global run took 89.6 seconds; the UK run took 3.0 seconds.

```sh
# Install the usual project requirements; global geometry additionally needs:
python -m pip install pyshp==3.1.6 pyproj==3.7.2
make restore-hydrolakes PY=python   # explicit network acquisition only if absent
make lake-gyration uk-lake-gyration PY=python
make geometry-registry registry-verify PY=python
```

Reproductions write to `build/reproductions/`; retained result bytes remain
unchanged. The merged suite passes **430 tests**, including eleven new geometry
and sampling checks. The frozen UK synthetic worlds recover 1.99648 for true
2 and 2.29596 for true 2.3, with the intended decisions. The central registry now
contains **31 runs and 751 verified file references**. Its global-lake record
checks the retained fitting table and acquisition metadata; restoring and
verifying the large archive is a separate explicit step.

The next substantive test should resolve global geometry and hydrological
dependence using a separately declared follow-up. The remaining earthquake
test still needs a physically defensible cluster definition and sufficient
complete events before fitting b or D2.
