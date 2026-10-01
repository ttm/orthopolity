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
