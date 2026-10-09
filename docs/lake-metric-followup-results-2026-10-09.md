# Global lake follow-up: local geometry removes the earlier iid equivalence

**Completed 9 October 2026, on `main`.** The apparent global agreement does
not survive the change to local physical-distance geometry. The full-polygon
survival exponent is **ζ = 1.8588**, with iid interval **[1.8443, 1.8739]**.
The matched-catchment estimate is **1.8585 [1.7851, 1.9244]**. Its interval
excludes exact ζ=2, but overlaps the declared practical-equivalence band
[1.9,2.1]. The frozen follow-up decision is therefore **inconclusive**, rather
than either equivalence or a robust departure from that entire band.

This is an outcome-exposed follow-up: the earlier global and UK results were
known. It is not a new independent confirmation or a general-law refutation.
The tested reading is territory allocation per **d ln R**, with radius-density
exponent α=ζ+1. Exponent agreement alone would not identify that mechanism.

## Results

All **1,427,688** original HydroLAKES features were processed. The inclusive
1–20 km range and equivalence band were held fixed.

| Geometry / population | Selected lakes | ζ | Iid 95% interval | Spatial 95% interval |
|---|---:|---:|---|---|
| Original EPSG:6933, largest ring | 119,683 | 1.9295 | [1.9185, 1.9408] | Country: [1.5945, 2.0296] |
| Local LAEA, largest exterior ring | 70,199 | 1.8614 | [1.8477, 1.8760] | Country: [1.6105, 1.9600] |
| Local LAEA, full lake geometry — primary | 70,486 | 1.8588 | [1.8443, 1.8739] | Country: [1.6071, 1.9539] |
| Local LAEA, catchment-matched lakes | 70,455 | 1.8585 | [1.8429, 1.8726] | Basin: [1.7851, 1.9244] |
| Local geodesic AEQD, full geometry | 70,486 | 1.8588 | [1.8444, 1.8726] | Country: [1.6073, 1.9453] |

The original result and its literal decision remain preserved. The table
compares completed calculations, not a menu from which to select a favourable
method. All follow-up choices were frozen before its fitted outcomes.

![Geometry and interval comparison](../results/lake-metric-followup-2026-10-09/interval-comparison.png)

The local-largest-ring comparison attributes most of the exponent change to
the projection and consequent radius selection; accounting for holes has a
smaller effect. Relative to the original selection, 3,676 lakes enter and
52,873 leave. The full source contains 216,330 hole rings and exactly one
exterior ring per feature; 29,112 selected lakes contain holes.

LAEA and AEQD select **exactly the same lakes**. Their exponent estimates differ
by about 0.00000021, and their maximum selected radius discrepancy is only
9 parts per million. The longest centre-to-vertex distance in a selected lake
is 85.31 km, below the declared 200 km limit. Local projected areas differ from
independent geodesic polygon areas by at most about 1.8 parts per million on
the selected sample. These checks make residual local projection distortion a
poor explanation for the new exponent. They do not establish mapping
completeness or intrinsic geodesic exactness.

## Spatial and distribution qualifications

The official **HydroBASINS level-3 v1.c** files were reachable. All nine
regional archives supply 292 major drainage regions. The deterministic outlet
join matches **70,455 of 70,486 lakes (99.956%)**, occupying **246 basins**.
There are 31 unmatched outlets and no ambiguous multiple matches. Unmatched
lakes remain in the global estimate; the basin interval explicitly describes
the matched population. Its point estimate differs from the all-lake estimate
by only 0.00023, but the declared complete-coverage gate still fails.

The largest occupied basin contains 7.17% of matched lakes. By contrast, the
largest Country block contains 53.67% of selected lakes. Different grouping
scales give different intervals; neither grouping guarantees independence
between blocks or accounts for mapping error.

**379 selected lake geometries (0.54%) are topologically invalid under GEOS.**
None triggers the corrected orphan-hole conversion check. Their signed moments
are retained, as declared; no lake is silently repaired or excluded. The
all-valid-topology gate therefore fails. The basin overlay's separate,
predeclared linework repair was needed for 209 of 292 basin features; source
archives were unchanged. A pre-fit audit found no basin conversion errors or
raw longitude jumps over 180°.

The bounded, refitted **iid** KS diagnostic gives D=0.004618 and
p=0.01399 (13 of 1,000 simulated statistics at least as large). This is a small
absolute CDF discrepancy but fails the declared diagnostic threshold. Spatial
dependence prevents interpreting its p-value as a calibrated spatial rejection.
It is another reason to describe a fitted exponent without claiming positive
power-law support.

![Observed and fitted bounded survival](../results/lake-metric-followup-2026-10-09/survival.png)

The declared `Lake_type == 1` point-only sensitivity gives ζ=1.9752 for 66,074
lakes. This means **not flagged as reservoir or regulated** in this source,
not independently verified natural lakes. No interval was declared for this
sensitivity, and its near-2 estimate does not replace the primary outcome.
Any further classification analysis must disclose that this result is known.

## Audit and validation

- Local freeze **`60d4243`** committed the
  [protocol](lake-metric-followup-protocol-2026-10-09.md), config, implementation,
  source receipts and synthetic worlds before new real-data geometry.
- Review then identified a topology diagnostic that could accept pyshp's
  automatic reinterpretation of orphan holes. The first geometry pass was
  interrupted **before any exponent fit**. Amendment **`964a7b0`** records the
  correction, regression test, interrupted log and partial-table checksum.
  Some real radii had been calculated but no new fitted outcomes were inspected.
- All **442 repository tests pass**, including 12 new checks of local geometry,
  date-line/polar handling, holes/components, basin joins, estimator agreement,
  synthetic worlds and spatial dependence. Synthetic ζ=2 and ζ=2.3 recover
  2.0016 and 2.3014, with the expected declared decisions.
- Independent likelihood-score roots agree with both retained point estimates
  within 0.00000011. A deterministic 71-lake check using the earlier UK polygon
  moment implementation agrees within 4.1×10⁻¹⁴ km. All 71 QA geometries were
  valid; that numerical check does not erase the 379 invalid source geometries.
- The complete derived table's SHA256 is
  `e361263dd5c60c092b29c079f32a72673db140b47ca0ab9dbbdfbce8b74b22c7`.
  The successful run took 602 seconds. Source ZIP/CRC/digest checks pass.

The [result directory](../results/lake-metric-followup-2026-10-09/) retains
the full selected table, unmatched outlets, results, diagnostics, runtime,
figures, synthetic checks, amendment and logs. The large full derived table
and original source archives remain local and restorable. The run is appended
to the immutable registry; earlier scientific outputs remain unchanged.

## Reproduction

Use Python 3.11 and the pinned requirements. From a fresh checkout:

```sh
make install PY=python3.11
make restore-hydrolakes restore-hydrobasins PY=python3.11
MPLCONFIGDIR=build/matplotlib make lake-metric-followup PY=python3.11
```

The analysis itself is offline. Output goes to
`build/reproductions/lake-metric-followup/`; the complete table is regenerated
under `data/derived/`. A cached rerun uses:

```sh
PYTHONPATH=src MPLCONFIGDIR=build/matplotlib python3.11 \
  experiments/run_lake_metric_followup.py \
  --output build/reproductions/lake-metric-followup
```

The optional original-radius comparison also needs the original full table at
`results/lake-gyration-2026-10-09/implementation/data/derived/hydrolakes_rg.csv`.
Regenerate it using that directory's archived Latin1 runner and the restored
HydroLAKES shapefile; its checksum is retained in the new result. Absence of
that optional historical table skips only the historical radius-ratio/cohort
comparison, not the new scientific analysis.

`experiments/verify_lake_metric_followup.py` audits the retained result against
the complete derived table and source geometries. `experiments/plot_lake_metric_comparison.py`
regenerates the comparison figure; `make metric-followup-registry` verifies and
registers the retained run without replacing earlier entries.

Source attribution and mapping limitations are in the
[HydroBASINS source audit](hydrobasins-source-2026-10-09.md) and
[original lake report](lake-gyration-results-2026-10-09.md).

The useful conclusion is methodological and empirical: the original narrow
iid agreement depended on its distance representation. With local geometry,
neither the iid nor spatial interval establishes practical equivalence to 2.
The accessible data have resolved that question without establishing a general
resource-allocation law or a fully qualified rejection of the equivalence band.
