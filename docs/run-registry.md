# Retained runs and reproducibility

The central [run registry](../results/run-registry.jsonl) connects each retained
study to its resource definitions, data, algorithms, configuration, seeds,
outputs, hardware metadata and parent studies. It is append-only JSONL: a new
result gets a new run identifier rather than replacing a previous record.

## What is recorded

Each schema-version-1 entry contains:

- `run_id` and `evidence_kind`: `simulation`, `constructed_prediction`, or
  `actual_measurement`. An actual-measurement entry can be incomplete; its
  summary must say so. Successful registration is not scientific validation.
- `resources`: names, independently declared definitions and physical or
  model units. Resource costs, budgets and outcome counts are distinct.
- `data_inputs`, `configs`, `algorithms.sources`, and `artifacts`: paths and
  SHA-256 digests. Sources/configurations have content-addressed byte copies
  under `data/run-sources/<sha256>/<filename>`, with their original paths
  retained as provenance. Future edits to live code cannot change these copies.
- `generated_seeds`: seed values and derivation rules. Deterministically
  generated arrays are described rather than advertised as observed data.
- `relationships`: references to already registered runs, preserving an
  ordered, acyclic lineage.
- `hardware_metadata` and `summary`: recorded execution facts, results and
  explicit unavailable fields. The canonical JSON entry has its own digest.

Registration audits all earlier entry digests and file references before
appending, takes a file lock, and flushes the appended record to disk. An exact
repeat is idempotent. Changed results under the same identifier, missing or
modified files, incomplete lines and unknown parents fail the audit. This is a
local integrity record, not an external timestamp service. Git provides another
retained history; neither mechanism proves external preregistration or blinding.

## Catalogue

The inverse-resource and linguistic studies completed on 7 October bring the
catalogue to **27 records and 677 file references**. The earlier records and
all their retained inputs and results remain intact.

- `inverse-resources-2026-10-06` is a constructed simulation: fixed constituent
  exponents, known offsets, analytic predictions, 20,000 correlated Gaussian
  replicates, partial identification and conditioning examples. It adds no
  natural observations. See [the demonstration](inverse-resources.md).
- `linguistic-resources-2026-10-07` is a retrospective empirical corpus study.
  Pinned text and pronunciation sources define independent symbolic features;
  the vocabulary, cost models and competitors were frozen before acquisition
  of the test corpus. All six forecasts, document uncertainty, omissions,
  duplicate exclusions and allocation discrepancies are retained. See
  [the report](linguistic-resources.md).

The corresponding make targets ending in `-registry` register or audit these
retained studies without rerunning or replacing their results.

`thermal-radiation-2026-10-06` brings the catalogue to 25 records and 628 file
references. It retains four downloaded FIRAS source documents and their
receipts, all 43 monopole rows, a traceable transcription of the published
approximate spectral correlations, the linear mode-energy conversion, original
residual diagnostics, theoretical curves and figures. The actual-measurement
classification refers to the published empirical input: this is a retrospective
description of a calibrated reconstructed product, with no new observations,
temperature fit, or independent test of its embedded Planck template.
`make thermal-radiation-registry PY=python3.11` registers/checks the retained
study without rerunning it. See [the report](thermal-radiation.md).

`class-exchange-2026-10-05`, completed and integrated 6 October, brings the
catalogue to 24 records and 603 file references. It retains fixed class weights,
independent costs, conductances, prescribed preferences, rate-derived predictions,
exact deterministic checkpoints, raw integer packet counts, and generated
figures. A separate algorithm bundle records the post-hoc compact manuscript
figure without resimulation. All earlier entries remain intact.
`make class-exchange-registry PY=python3.11` checks the execution receipts,
archives the exact sources and configuration, and registers or audits the run
idempotently. See [the model report](class-exchange.md).

The seven completed model-study workflows are registered retrospectively:
`models`, `dependence`, `attachment`, `restrictions`, `competition`, `forecast`,
and `interventions`, each with date suffix `2026-10-01`. Their algorithm snapshots
are labelled current sources at registration, because those original runs did
not retain execution-time source hashes. Their outputs/configurations are
retained; the later snapshots alone cannot prove which code originally ran.

`workload-pilot-2026-10-01` records the original actual-measurement pilot. Its
source hashes match the original prediction freeze. Missing detailed historical
hardware facts remain missing; the present host fingerprint is not substituted
for them.

`workload-transfer-precheck-2026-10-01` retains 72 calibration measurements from
an incomplete replication attempt. Before a comparison freeze or validation,
an exact-description check rejected the words “import” versus “imports” in the
resource descriptions. These measurements are not silently discarded or used
in the completed comparison.

`workload-transfer-2026-10-01b` records the clean transfer comparison: a separate
72-task calibration, two prospective forecasts, exactly the original quotas
and criteria, and 672 fresh validation attempts. Both measured runs reference
the original pilot. See [the comparison report](workload-transfer.md).

`scheduler-design-2026-10-01` records conditional allocation simulations and a
hardware qualification inspection. The simulations encode competing allocation
assumptions. No actual scheduler-allocation trial was executed on the current
host. See [the protocol and gate result](scheduler-allocation.md).

This catalogue covers this model and controlled-workload research programme.
Downloaded natural-system snapshots retain their separate checksum catalogue
and provenance in [data/SOURCES.md](../data/SOURCES.md).

The [additional profile tests](additional-profile-tests.md) extend the catalogue
to fifteen records. `aquatic-study-transfer-2026-10-01` and
`solar-resource-transfer-2026-10-01` reanalyse published/retained measurements
with zero newly collected observations. The evidence kind `actual_measurement`
describes their empirical inputs, rather than a new collection. Each retains
its exact source-row membership and fitting separation.

`resource-identification-2026-10-01` retains a completed numerical simulation
whose figure rendering was interrupted. Its exact original source/configuration
copies survive the plotting fix. `resource-identification-2026-10-01-final`
references it as a same-seed computational replay; its calibration/validation
arrays are verified identical. These two records represent one numerical
realization, with a resolved plotting interruption.

`make profile-test-registry PY=python3.11` idempotently registers these additional
records and verifies the complete archive. It does not regenerate their results.

The [2 October validation round](validation-round.md) adds three records,
bringing the catalogue to eighteen. `profile-calibration-2026-10-02` records
generated outer datasets and their decision-calibration results; development
source snapshots precede final output-integrity guard changes, with inference
parameters unchanged. `solar-validation-2026-10-02` records a forecast frozen
and committed before acquiring the public 2025 event values. Its snapshot,
acquisition attempts, source bytes, membership and formal ineligibility rule
are retained. It uses existing public measurements rather than newly collecting
solar observations or claiming global blindness.

`dimensionality-intervention-2026-10-02` records actual thread CPU measurements,
separate non-unit cost calibration, full forecasts and an executed runnable-worker
restriction. It is distinct from the earlier OS scarcity gate: this process's
verified GIL supplies a single Python-execution bottleneck. Incomplete jobs and
unassigned process CPU remain in its accounting. Concurrent development-benchmark
activity is disclosed; seed replay cannot regenerate actual CPU timings.

`make validation-round-registry PY=python3.11` registers these retained studies
idempotently. Registration verifies original source and configuration hashes,
checks each report's frozen-plan reference, archives exact algorithms, and audits
all prior records before appending. Sources, data and artifacts from earlier
records remain unchanged.

The [available-data programme](available-data-programme.md) adds
`archived-cost-transfer-2026-10-02`, bringing the catalogue to nineteen. It
reanalyses the published BCO-DMO 926311 Synechococcus quotas with zero new
observations. Its protocol was frozen before the CSV was acquired; coefficients
and predictions were frozen and pushed before any held-out quota field was
converted. See [the study](archived-cost-transfer.md).
`make available-data-registry PY=python3.11` registers it idempotently. The
assembler `experiments/register_available_data.py` computes no result, so it is
not archived as an analysis source. Later available-data studies can therefore
be appended without changing earlier entries.

`chemostat-resource-response-2026-10-02` is the twentieth record. It retains
frozen forecasts for twelve held-out chemostat communities from the published
Wojcik et al. archive, written before any held-out post-pulse value was decoded.
It also retains the two configuration amendments, the gated reader, the held-out
records, the evaluation, and a separately archived post-hoc report source.
Lineage links it to `restrictions-2026-10-01`, whose two-budget rule it tests on
measurements. See [the study](chemostat-response.md); its retained nitrogen-budget
unit erratum is documented there.

`dunaliella-size-budget-2026-10-02` is the twenty-first record. It retains
cross-fitted size-law and restoration forecasts for size-selected *Dunaliella*
lineages from Malerba et al. (2018). It also retains the partition declaration,
the protocol committed before any selected-lineage outcome was decoded, the
cell-volume amendment, the capacities and a post-hoc report source. Lineage links
it to `archived-cost-transfer-2026-10-02`, whose exponents it assigns
cross-taxon, and to `restrictions-2026-10-01`. See
[the study](dunaliella-size-budget.md).

The [plant biomass-profile study](plant-biomass-profile.md) adds record 22,
`plant-biomass-profile-2026-10-03`. It retains ten directly weighed plot sources,
source-exposure metadata, protocol and amendment, development-only forecasts,
every membership record, synthetic finite-census calibration and evaluation.
Protocol and algorithms were committed before formal fitting; forecasts and
calibration were pushed in `1258e80` before scoring. Earlier raw outcome exposure
prevents a blinding claim. Aboveground stock is measured directly, but $q(m)=m$
is definitional. Point stock/count comparisons transfer across locales;
ecological expected neutrality remains unresolved. Synthetic calibration is
separate from field evidence within this actual-measurement reanalysis record.

Record 23, `ghedini-cost-calibration-2026-10-05`, is a
[published respiration calibration diagnostic](ghedini-cost-calibration.md),
not an allocation study. The previously exposed monoculture readings are grouped
without clipping negative values; entire species and OD conditions are held
out. Commit `d49f0e6` retains the protocol and algorithms before fitting.
The power-plus-overhead family fails the fixed predictive/stability gate;
numerical community outcomes remain unopened. The record retains source and
exposure snapshots, groups/folds, every fit and prediction, conditional moment
sensitivities and two post-analysis figures. Registration requires exact
numerical replay and links to the earlier quota-calibration study. The registry
now verifies 23 records and 587 file references; record count is not a count of
independent tests of an allocation law.

## Hardware and threading

The new workload metadata records CPU model, architecture/logical CPU count,
RAM, OS version/build, Python, NumPy, BLAS build information and requested thread
environment. Its timestamp describes the collector process before calibration.
The host probe reads specific nonidentifying fields; it does not collect a
hostname, account name or hardware serial number.

Requested thread counts are separate from runtime verification. The current
Apple Accelerate installation has no verified worker thread count. CPU time is
still user plus system time across all child threads. An optional supported
`threadpoolctl` inspection describes loaded libraries in its collector process;
it cannot by itself establish the threading of another process. No dependency
or machine setting was changed to obtain these metadata.

## Audit and extend

Run an offline audit:

~~~bash
make registry-verify PY=python3.11
~~~

`make run-registry PY=python3.11` idempotently registers the eight reference
workflows, then audits the complete registry. It does not rerun them. To add a
new entry with retained source/configuration snapshots:

~~~bash
PYTHONPATH=src python3.11 experiments/register_runs.py --entry path/to/entry.json
~~~

Create a new measurement directory, output directory and run identifier for
every new collection. Leave registered raw data and outputs unchanged.
Reanalysis from archived sources can write to a fresh output directory and be
registered as a child analysis. The transfer and allocation drivers preserve
existing matching outputs on repeated execution; a source/configuration change
requires a new run. Other older study drivers can regenerate their outputs, so
use separate copies/directories when working with their registered results.

Integrity checks, source archives and seeds support reproducibility. They do
not guarantee identical performance on another machine, independence of repeated
launches, sampling coverage or the validity of the underlying physical claims.
