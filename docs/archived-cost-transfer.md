# Archived biological resource-cost transfer

Status on 2 October 2026: complete and registered as
`archived-cost-transfer-2026-10-02`. Coefficients and all 30 held-out predictions
were frozen at 15:00:10 UTC and pushed in commit `a697be6`. No held-out quota
field had been converted at that point. Evaluation began at 15:00:43 UTC, and
an offline replay reproduced the fits, predictions and scores. No new cultures,
laboratory work or CPU measurements were performed. The
[ongoing research document](ongoing-research.md) records the cross-study state.

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

The study ran with these commands, in order:

```sh
python3.11 experiments/run_archived_cost_transfer.py --stage calibrate
MPLCONFIGDIR=build/matplotlib python3.11 experiments/run_archived_cost_transfer.py --stage evaluate
python3.11 experiments/run_archived_cost_transfer.py --stage audit
```

`make archived-cost-transfer PY=python3.11` repeats the offline audit. It
refits the training cultures, recomputes the conditional predictions and
rescores them against the retained outputs. Do not alter frozen config or
analysis sources to adapt the result. If a genuine implementation error is
identified after evaluation, retain this run and add a separate corrective
analysis with its own recorded scope and inputs.

## Result

The archive contains 52 cultures: 42 training cultures (9, 10, 12 and 11 at
16, 18, 20 and 22°C) and 10 validation cultures, all at 25°C. **The source CSV
contains no 27°C cultures**, although the methods describe them. The declared
27°C cells are therefore empty, not dropped; the figure title restates the
declared split. No quota or diameter is missing. Strains contribute two or three
validation cultures each: BL107 3, CC9311 3, CC9902 2, ROS8604 2.

Training slopes over measured diameters of 0.64–1.30 µm are finite descriptive
cost degrees, not exponents. The pooled free-power degrees are 2.74 (C), 2.39
(N) and 2.93 (P). Within-strain demeaned slopes are steeper (4.80, 3.95 and
3.64), because temperature changes diameter and quota together within a strain.
Leave-one-strain-out pooled degrees range over 2.65–3.48 (C), 2.05–3.35 (N)
and 2.76–3.65 (P). Each range is widest when CC9902, the smallest strain, is
removed.

Held-out equal-cell mean absolute log error (lower is better; the factor
`exp(error)` is in parentheses):

| Model | QC | QN | QP |
|---|---:|---:|---:|
| Fixed cubic, $q=ad^3$ | **0.133** (×1.14) | 0.221 (×1.25) | 0.226 (×1.25) |
| Pooled free power, $q=ad^D$ | 0.141 (×1.15) | 0.276 (×1.32) | 0.233 (×1.26) |
| Strain geometric mean | 0.199 (×1.22) | **0.207** (×1.23) | **0.147** (×1.16) |
| Strain temperature trend | 0.446 (×1.56) | 0.372 (×1.45) | 0.286 (×1.33) |

Root mean squared log error gives the same ranking for each element.

1. **Carbon follows measured size.** The geometric $d^3$ model, with one
   fitted intercept, gives the most accurate held-out carbon forecast.
2. **Nitrogen and phosphorus follow strain identity more than size.** Each
   strain's training mean, which ignores diameter, beats both diameter models;
   the cubic model is second. In these warmer cultures, diameter is not a
   reliable guide to N or P quota.
3. **Fitting the exponent does not improve transfer.** The free-power model
   never beats the fixed cubic degree.
4. **Temperature trends do not extrapolate.** Extending each strain's
   16–22°C trend to 25°C is worst for every element, under-predicting by 0.28–0.39
   mean log units. The diameter models instead over-predict by 0.06 (C), 0.13 (N)
   and 0.16 (P).

These are point errors from one published experiment: four strains, ten
validation cultures in four strain cells, one warmer temperature. Per-cell
errors range from 0.01 to 0.75 log units. Close differences, such as 0.207
versus 0.221 for nitrogen, are smaller than that spread and are not decisive.
No intervals or significance claims are made.

For the wider programme, the cost side transfers in part. A size-geometric
carbon cost carries to an unused temperature within a typical factor of 1.14.
Nitrogen and phosphorus costs need taxon-level or condition-level calibration,
not size allometry. The chemostat study accordingly uses directly assayed
per-species nitrogen quotas rather than a size rule. These quotas were never
transplanted into the chemostat taxa.
