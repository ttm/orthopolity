# HydroLAKES continuation: execution and reporting plan

This note is fixed before any real lake radius or exponent calculation on
9 October 2026. It clarifies reporting; it does not replace the original
registration or introduce a revised primary estimator.

The complete original HydroLAKES v1.0 archive is acquired: 820,295,132 bytes,
SHA-256 `9ef63498569dd7ccd0b8d8852da026e009a75f42d293f00e483f3b9fcfe8e1f9`.
ZIP integrity passes. The actual DBF contains 1,427,688 records and no basin-ID
column. The [acquisition record](../data/hydrolakes/2026-10-09/acquisition.json)
and [schema](../data/hydrolakes/2026-10-09/schema.json) retain these checks.

Run exact copies of the original script, configuration and statistical helper
from `f846670`, kept in `results/lake-gyration-2026-10-09/implementation/`.
Preserve EPSG:6933, largest ring, ignored holes, inclusive R = 1–20 km,
bounded MLE, 1,000 iid bootstrap draws, optional 500 Country-block draws and
the script's existing verdict. Freeze the source hashes and inspection history
in `before-run.json`, then commit this record before execution.

The registration calls for basin uncertainty if a basin field exists and
describes a two-interval support rule. The actual source lacks that field and
the script uses only the iid interval in its verdict. Report the literal script
verdict with its incomplete spatial qualification; do not present a positive
verdict as completed confirmation. Its Country interval is a sensitivity,
not the registered HydroBASINS calculation.

Interpretation also retains projection-dependent distances, omitted geometry,
area-based inventory detection, possible repeated hydrological structure and
the lack of a goodness-of-fit gate. `Lake_type == 1` means not flagged as
reservoir/regulated. No cause of a departure will be claimed from this analysis.

The separately specified UKCEH replication uses its supplied metric coordinates,
all components and holes, fixed spatial blocks and an adequacy diagnostic. It
has a separate cohort, data source and protocol. It does not repair or replace
the global registration, and may overlap geographically with HydroLAKES.

Large archive and extracted geometries are retained locally but excluded from
Git. Restoration must use the recorded public URL and verify SHA-256 before
extraction. Original and derived artifact hashes, software versions, exit status
and result bytes will be retained after the run.

## Execution amendment: DBF decoding

The first attempt stopped on a non-UTF-8 lake-name byte before any table or fit
was produced. Some early radii were computed inside the failed process but were
not inspected. The DBF language-driver byte is 87/0x57, which
[GDAL interprets as ISO-8859-1](https://gdal.org/en/stable/drivers/vector/shapefile.html#encoding).
Repeat with explicit `latin1` decoding. This preserves every byte distinctly,
all numeric fields, geometry and Country group equality; it does not assert
that every displayed name has the intended typography. No error replacement,
row omission or scientific estimator change is permitted. The original failed
attempt, source and [amendment](../results/lake-gyration-2026-10-09/encoding-amendment.json)
are retained. The adapted snapshot changes one Reader argument; the active
runner exposes the same correction as `--encoding latin1`.
