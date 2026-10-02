# Archived biological resource-cost transfer

Status on 2 October 2026: the protocol and analysis sources are frozen, the
versioned public CSV is retained, and calibration/evaluation are paused for the
repository checkpoint. No new cultures, laboratory work, or CPU measurements are
performed. The [ongoing research document](ongoing-research.md) records the
cross-study continuation state.

## Question and scope

Can independently published carbon, nitrogen, and phosphorus quotas be predicted
from cell diameter across an unused temperature range? This tests the cost side
of the resource framework. It does not test allocation neutrality, restriction,
recovery, or community abundance, and these quotas will not be assigned to
different organisms in the separate chemostat study.

The source is Harcourt, Garcia, and Martiny's
[BCO-DMO dataset 926311, version 1](https://doi.org/10.26008/1912/bco-dmo.926311.1),
dated 30 April 2024 and licensed CC-BY-4.0. The
[method description](https://www.bco-dmo.org/dataset/926311/description)
specifies four Synechococcus strains and triplicate cultures at 16, 18, 20, 22,
25, and 27°C. The title says 16–25°C; the explicit methods include 27°C, which
the predeclared validation split includes.

QC, QN, and QP are retained elemental quotas in femtomoles per counted cell.
They combine bulk elemental assays with flow-cytometry enumeration. Diameter is
derived from forward scatter calibrated against microscopy and a stage
micrometer. The organisms were grown in nutrient-replete media. These quantities
are not elemental uptake fluxes, energy requirements, or direct measurements
of a resource-network dimension. The source reports analyzer failures and lost
replicates; missing values are retained without imputation.

## Frozen procedure

The [config](../configs/archived_cost_transfer_2026-10-02.json) fixes the split:
16/18/20/22°C cultures for training, and whole 25/27°C cultures for validation.
The local [protocol freeze](../data/archived-cost-transfer/2026-10-02/frozen-plan.json)
occurred at **2026-10-02 14:29:40.499313 UTC**. Original CSV acquisition started
at **14:30:01.042228 UTC** and finished at **14:30:03.448416 UTC**.

The Git checkpoint follows acquisition and precedes numerical fitting. It must
not be represented as a pre-acquisition Git checkpoint. This is a local
retrospective protocol, not external preregistration or a guarantee of external
blinding. Published metadata and methods had already been inspected.

Four log-quota prediction models are fixed for each resource:

1. Geometric $q=a d^3$, with its intercept fitted using training cultures.
2. Pooled free-power $q=a d^D$, with both parameters fitted using training cultures.
3. A separate training geometric mean quota for each strain.
4. A separate training log-quota versus temperature trend for each strain.

All four fits use the same resource-specific training rows with positive quota
and diameter. The parser's training view never converts held-out quota fields;
the predictor view never accesses any quota column. A second immutable file
will retain coefficients and every validation prediction before conversion of
validation quota fields. Forecasts condition on measured validation diameter,
strain, and temperature; they do not forecast diameter itself.

Primary error is the mean absolute log-quota error within each strain-temperature
cell, followed by equal weighting across observed cells. Root mean squared log
error, per-cell errors, every scored culture, and missingness will also be
retained. No bootstrap confidence or significance claims are planned. Training
diagnostics compare pooled slopes, strain-demeaned slopes, and descriptive
leave-one-strain-out pooled slopes. Four strains and a narrow diameter range
cannot establish an asymptotic exponent or a universal dimension.

## Retained source and reproducibility

The original CSV has **15,990 bytes**, MD5
`0dea9ff74bffe353e442495b23312ac3`, matching the repository-published checksum,
and SHA-256
`4192fd69842c7ce4dc9a66a689a32f3c393bf833f7126119efaa5989babbc766`.
The [acquisition receipt](../data/archived-cost-transfer/2026-10-02/926311_v1_syn-batch-cultures.csv.receipt.json)
retains requested/final URLs, HTTP headers, dates, byte counts, checksums, and
verified TLS/hostname configuration. Both metadata pages and exact frozen
analysis-source copies are retained alongside it.

Seven tests passed before the freeze, including a sentinel held-out quota that
raises if converted, duplicate culture rejection, an analytically known cost
degree, and equal-cell scoring under unequal replicate counts.

After the repository checkpoint, the exact continuation commands are:

```sh
python3.11 experiments/run_archived_cost_transfer.py --stage calibrate
MPLCONFIGDIR=build/matplotlib python3.11 experiments/run_archived_cost_transfer.py --stage evaluate
python3.11 experiments/run_archived_cost_transfer.py --stage audit
```

Do not alter frozen config or analysis sources to adapt the result. If a genuine
implementation error is identified after evaluation, retain this run and add a
separate corrective analysis with its own recorded scope and inputs.
