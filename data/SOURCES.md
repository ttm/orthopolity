# Source data

1. NOAA NCEI, *L2 XRS flare report*, science-quality composite, annual files for
   2022, 2023 and 2024, version 1.0.1. [Source directory](https://data.ngdc.noaa.gov/platforms/solar-space-observing-satellites/goes/multi/l2/data/xrsf-l2-flrpt_science/csv/).
   Metadata and original fields are preserved. NOAA's metadata states that
   these data may be redistributed and used without restriction. Irradiance
   is W/m², integrated irradiance is J/m². End fluence has missing values.
2. USGS, *FDSN Event Web Service / ComCat*, worldwide earthquakes from
   2010-01-01 through 2024-12-31, minimum reported magnitude 5.5.
   [API documentation](https://earthquake.usgs.gov/fdsnws/event/1/).
   The query URL is in `experiments/fetch_data.py`. Moment magnitudes are
   filtered during analysis, not in the raw download. The energy proxy is an
   analysis transformation, not a USGS observed field.
3. Hatton, Heneghan, Bar-On and Galbraith (2021), *The global ocean size spectrum
   from bacteria to whales*, Science Advances 7, eabh3732.
   [Article](https://doi.org/10.1126/sciadv.abh3732),
   [associated archive](https://doi.org/10.5281/zenodo.5520055),
   [authors' repository](https://github.com/ryanheneghan/sheldon_revisited).
   The included 253-row table is the authors' output for reconstructed upper-200-m
   biomass by group and mass bin. It is not individual-organism raw data.
   Attribution and original third-party rights are retained; no new license
   to third-party materials is granted by this package.

4. Hatton et al. (2021), full-water-column companion table
   (`summary_biomass_table_long.csv`) and per-group uncertainty factors
   (`group_standard_errors.csv`), from the same repository and commit as (3).
   Note: the column named `log10_Standard_Error` does **not** contain a log10
   standard error. It is a multiplicative factor f, with the published 95%
   interval being exactly [estimate/f, estimate*f]; verified for all 253 rows.
5. Ersoy, Z., et al. (2025), *GLOSSAQUA: A global dataset of size spectra across
   aquatic ecosystems*, Ecology 106, e70050.
   [Repository](https://github.com/zeynepersoy/GLOSSAQUA_dataset) and
   [archived release](https://zenodo.org/records/14701391) declare MIT;
   Copyright (c) 2023 Zeynep Ersoy. The
   [published metadata](https://bura.brunel.ac.uk/bitstream/2438/32237/8/Ersoy_et_al_2025_Metadata_S1.pdf)
   instead describes the dataset as CC BY-NC-SA 4.0. The scope of these differing
   statements is unresolved; see [NOTICE.md](NOTICE.md). Files `GLOSSAQUA_Size.txt`,
   `GLOSSAQUA_Sample.txt`, `GLOSSAQUA_DataSource.txt`. In this snapshot the Size
   file is quoted, space-separated UTF-8; Sample is tab-separated and decoded
   as Latin-1 by the analysis; DataSource is tab-separated and UTF-8 compatible.
   Do not apply one delimiter/encoding to all three. `GLOSSAQUA_Size.txt`
   holds published size-spectrum *fit parameters* per sample, not individual
   organism measurements. The historical retrieval URL uses mutable `HEAD`;
   this local snapshot is identified by its SHA-256 checksums. Upstream does
   publish a `v1.0.0` release, but no equivalence between this snapshot and that
   release is asserted. A retrieval URL is not a commit pin.

All source files are preserved byte-for-byte and hashed. New views, estimates,
figures and audio are analysis outputs and are labeled separately.

## Candidate metadata audit: 3 October 2026

`neutrality-audit/2026-10-03/` retains seven metadata snapshots: GitHub repository,
commit and two equivalent tree inventories for `KerkhoffLab/PlantSizeDist` at
`defccc3dcbbbf3ba57ff1572377de88fba83ff7f`, plus PANGAEA landing pages for
816451 (MALASPINA fraction stocks), 983551 (PELACUS dry-mass stocks), and 911575
(A Coruña ratios, excluded as a stock source). HTTP receipts, exact URLs and
SHA-256 digests are in `acquisition.json`. No numerical outcome table is retained
in this directory. `exposure.json` records raw plant rows emitted during a
separate failed header-only inspection; it contains no outcome values.
See [the dataset audit](../docs/next-dataset-audit.md). Verify these snapshots
offline with `python3.11 experiments/fetch_neutrality_metadata.py --stage verify`.

## First-party controlled workload measurements

`workload-pilot/2026-10-01/` contains measurements generated locally by
`experiments/run_workload_pilot.py` and the fresh-process matrix worker. The
calibration and validation JSONL records are actual observed CPU, peak-resident
memory, numerical checks, and cooperative quota outcomes. The calibration
manifest and frozen forecast contain SHA-256 hashes of inputs and source files.
This directory is separate from the downloaded empirical snapshots in `raw/`.
See [the pilot report](../docs/workload-pilot.md) for resource units, assigned
conditions, sampling limitations, and reproduction instructions. These records
describe controlled task acceptance rather than autonomous resource allocation.

`workload-transfer/2026-10-01b/` retains a separate 72-task calibration, a
comparison freeze and 672 fresh validation attempts. It keeps the original
pilot's tasks, numerical quota values and criteria. Original and prospective
locally recalibrated forecasts are scored against the same new outcomes.
`workload-transfer/2026-10-01/` retains an earlier calibration whose description
guard failed before any freeze/validation; it is registered as incomplete.
See [the transfer report](../docs/workload-transfer.md).

`scheduler-allocation/2026-10-01/` contains hardware qualification metadata and
a registry entry. Current hardware did not qualify for actual allocation
trials. Conditional generated resource-share simulations are separately
labelled in `results/scheduler-allocation/`; they are not measured CPU shares.

`run-sources/<sha256>/` contains content-addressed source/configuration copies
for the [central run registry](../docs/run-registry.md). These preserve each
record's bytes when working source changes. Retrospectively registered model
sources are explicitly distinguished from original execution-time source
manifests. The registry is `results/run-registry.jsonl`; its offline audit checks
all entry and retained-file hashes.

## Retrospective profile tests and identification simulations

`solar-resource-transfer/2026-10-01/` retains calibration-only bin pooling,
2022–2023 measured fluence costs, frozen count/resource forecasts and complete
row/flare membership manifests for training and 2024 evaluation. It reuses the
NOAA snapshots above; fluence at the observer is not total flare energy.

`aquatic-study-transfer/2026-10-01/` retains the exact GLOSSAQUA row selection,
units/specifications, reported uncertainty route and leave-study-out analysis
specification. Direct standard errors define the primary sample; confidence
bounds assuming a 95% Gaussian interval form an explicitly unverified sensitivity.
No missing errors or invalid size bounds are imputed. Neither empirical test
collects new observations or claims previously seen data were blinded.

`resource-identification/2026-10-01/` and its `2026-10-01-final/` replay retain
generated calibration/evaluation cohort counts, exact log-size sums and mass
totals, seeds, frozen stationary laws and source digests. The first rendering
interruption is recorded with original exact sources. The final replay has
identical numerical arrays and counts as the same simulation realization.
These generated cohorts are separate from natural-system measurements.
See [the additional-test reports](../docs/additional-profile-tests.md).

## Calibration and unused-observation validation: 2 October 2026

`profile-calibration/2026-10-02/` retains separate generated development and
evaluation samples, 90 conditions, 18,000 development and 180,000 evaluation
datasets, population targets, frozen seed recipes and original development
source bytes. Every outer dataset's means, bounds, decisions and zero flags are
retained; eight full block-vector examples per condition are retained, and the
remaining inputs regenerate from the recorded source, NumPy version and seeds.
The internal bootstrap indices are regenerated rather than stored.

`solar-validation/2026-10-02/` contains a new immutable NOAA 2025 annual flare
snapshot, obtained after protocol checkpoint `390856c`. The raw SHA-256 is
`287c9ee0961e221368f3580c6e159e8dc17ef7607d02442dabf3ab48fa8c6c88`.
The acquisition receipt retains the exact URL, access time, response metadata,
verified TLS context and both the initial failed sandbox retrieval and successful
approved retrieval. It does not change the historical `raw/` checksum catalogue.
Development and evaluation membership, source snapshots, the frozen application
gate and decisions are retained. Instrument composition differs across periods;
resource-cost changes cannot uniquely be attributed to physical flare behavior.

`dimensionality-intervention/2026-10-02/` contains 360 actual job-cost calibration
measurements and sixteen actual allocation trials, with 80 worker records,
104,133 complete jobs and 79 partial jobs. Thread CPU seconds, complete/partial
job charges, overhead and enclosing process CPU are separate fields. Original
source/configuration bytes and full forecasts were frozen before allocation.
The measured CPython/GIL execution mechanism is an engineered system; no CPU
quota or target completed count enforces its observed class shares.

The [validation-round report](../docs/validation-round.md) links resources,
algorithms, outcomes, explicit limitations and offline audit commands.

## Directly weighed plant sources and profile transfer: 3 October 2026

`plant-sources/2026-10-03/` retains ten exact CSVs and an acquisition receipt
from [KerkhoffLab/PlantSizeDist](https://github.com/KerkhoffLab/PlantSizeDist),
commit `defccc3dcbbbf3ba57ff1572377de88fba83ff7f`. Each file matches its
published Git blob SHA-1; the receipt also retains SHA-256, bytes, exact URLs,
retrieval times and response metadata. CR-only source endings are preserved.
`fetch_plant_sources.py --stage verify` checks all bytes without decoding masses.

[Dillon et al. (2019)](https://doi.org/10.1002/ecs2.2856) describe exhaustive
aboveground harvests, drying at at least 60°C for over a week, and weighing to
0.001 g. Objects are ramets/stem clusters, including inseparable bunched grasses.
Five BFEC plots train models; five RMBL plots evaluate them. Forest/desert
allometric inputs are excluded. The recorded masses are used without imposing
a new rounding rule. No binding resource, uptake flux or opportunity budget
is supplied. The author repository reports no explicit licence.

`plant-biomass-profile/2026-10-03/` retains synthetic calibration, the fixed
forecasts, all-record development/evaluation ledgers and registration. The
source-exposure record in `neutrality-audit/2026-10-03/exposure.json` is an input;
this is retrospective after raw exposure, although protocols and forecasts
precede formal scoring. Eight half-decade bins on 0.01–100 g retain empty
classes. Missing and excluded masses remain explicit. The generated calibration
uses its recorded independent random streams; it supplies no new field data.
See [the study report](../docs/plant-biomass-profile.md).

## Plankton observation gate: 4 October 2026

`law-route/2026-10-04/metadata/` retains six exact source files: PANGAEA
816451 metadata XML and event KML; Bode, Fernández Lamas and Mompeán's (2012)
six-page MALASPINA processing chapter from the CSIC repository; BCO-DMO 956590
and 943418 description PDFs; and RR2201 deployment metadata. The
[receipt](law-route/2026-10-04/metadata/acquisition.json) records URLs, byte
lengths, SHA-256 digests, response metadata and acquisition times. Failed
retrievals remain in `retrieval-attempts.jsonl`. Python's certificate-chain
failure for CSIC was resolved through macOS system curl with TLS certificate
and hostname verification enabled; verification was not disabled.

The acquisition driver requests only six allowlisted methods/metadata URLs,
refuses redirects outside that list and defaults to offline byte verification:
`make law-observation-metadata PY=python3.11`. XML and KML identify the same 43
station labels and coordinates; this is not an independent nitrogen-sample
count. No candidate nitrogen-stock table was requested. The
[observation assessment](../docs/plankton-observation-gate.md) closes the
current two-archive law-test gate without a new registry record. The prior
public-summary exposure note in the parent directory remains applicable.

## Size-versus-cost candidate inventory: 4–5 October 2026

`measure-candidates/2026-10-04/` retains seven exact API metadata responses
and receipts with URLs, UTC retrieval times, lengths, SHA-256 and verified TLS.
Sources are three Figshare candidate deposits, a Padfield author repository
description, Hengill and SeaFlow DataCite records, and the original Ghedini
experiment deposit. Metadata line endings are preserved.

| Retained biological archive | Provider identifier and integrity |
|---|---|
| [Ghedini, Malerba and Marshall (2020)](https://doi.org/10.26180/5e30e9e2b02b3) | File 22484462; 1,879,319 bytes; MD5 `af61d509937b76cb986d45683eea3617`; three XLSX members |
| [Ghedini, Loreau and Marshall (2020)](https://doi.org/10.26180/5e2a1a8d74be7) | File 21286929; 466,041 bytes; MD5 `6dc5a38875eb1eb9d44d08d7b020b95d`; one XLSX |

Both providers record CC BY 4.0. Archive bytes include community outcomes,
but numerical community rows remain uninterpreted. Inspection includes sheet
names and row-1 text headers, followed by a separately checkpointed A:I read of
the independent species-metabolism sheet. All 231 calibration rows, including
signed and missing rates, remain in the derived ledger. No cost fit or law score
was computed during this inventory.

The [audit](../docs/measure-candidate-audit.md) records methods, observation
limits, an aggregate-moment target and the remaining gate. The two offline
commands `make measure-candidates PY=python3.11` and
`make measure-calibration PY=python3.11` verify sources/headers and replay
calibration qualification. Published-summary exposure is recorded separately.
The two papers reuse the same community experiment.

## Published respiration calibration diagnostic: 5 October 2026

`ghedini-cost-calibration/2026-10-05/` contains the derived species-by-OD group
ledger, fold membership, frozen plan and registry receipt. It references the
unchanged Ghedini calibration JSON and provider-verified source ZIP above.
Content-addressed snapshots retain configuration, algorithms and the prior
exposure record. No further source or numerical community row was acquired.

Protocol checkpoint `d49f0e6` preceded fitting. Positive expected power and
power-plus-overhead costs were fitted to all signed group means. Whole-species
and whole-condition predictions plus deterministic moment sensitivities are
retained in `results/ghedini-cost-calibration/`. Two scientific PNGs plot all
usable signed readings and descriptive SDs; their separate post-analysis
source is archived. The failed gate supplies a calibration qualification
result, not an allocation-law verdict. See
[the report](../docs/ghedini-cost-calibration.md).

## Thermal radiation and FIRAS: 6 October 2026

`thermal-radiation/2026-10-06/` retains four exact public source files with
retrieval receipts and SHA-256 hashes: the NASA LAMBDA version 1 monopole table,
its product description and download page, and Fixsen et al. (1996)'s arXiv
article. `correlation.json` transcribes its 43 lag coefficients from Section 3.3,
printed page 11, with the primary PDF checksum. The table's 43 rows contain a
2.725 K blackbody reconstruction plus original fitted residuals, marginal
uncertainties, and the modeled Galactic spectrum. They are not raw independent
measurements. All rows and columns are preserved by the retrospective analysis.
Published conclusions and table values were seen before final computation;
there is no blinding claim. No new observations were collected.

The download listing says 1 March 2003, whereas the file header says initial
release May 2005; both remain in the source bytes. Numerical conversions use
exact SI constants and preserve their discrepancy from the posted reconstruction.
`make thermal-sources PY=python3.11` verifies sources offline;
`make thermal-radiation PY=python3.11` reproduces the calculation and figure.
See [the report](../docs/thermal-radiation.md) and
[specification](../docs/thermal-radiation-protocol.md).
