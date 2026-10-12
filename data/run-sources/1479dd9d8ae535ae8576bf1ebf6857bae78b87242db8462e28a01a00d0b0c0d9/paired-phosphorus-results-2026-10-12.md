# Independent phosphorus assays: the count-transfer pilot fails

**Completed 12 October 2026 on main.** The independently measured quota does
not improve the population prediction. One qualifying high-phosphorus culture
calibrates the relation and one different low-phosphorus culture tests it:
observed abundance is **34.9 million cells/mL**, compared with **5.55 million**
under fixed cost and **4.24 million** with the measured quota. Both miss the
declared factor-1.25 accuracy target. This is a small, conditional measurement
pilot, not a test of orthopolic allocation among coexisting groups.

## What was fixed before evaluation

The [original protocol](paired-phosphorus-protocol-2026-10-12.md), source bytes,
configuration and synthetic checks were committed at `83a8c36`. Its first run
stopped on missing cell volumes before calculating any count prediction. The
[dated amendment](paired-phosphorus-amendment-2026-10-12.md), committed at
`1569c4f`, removed that optional comparator. It preserved both cost predictions,
all source identities, eligibility gates and the accuracy margin. The original
stopped design and its code remain in git; no unsuccessful outcome was used
to choose the amendment. Three imaged volumes were missing in each of the
two otherwise qualifying samples.

Before the freeze, metadata, sample identifiers, missingness and duplicate-row
differences were inspected. Metadata included treatment biovolume constants,
which neither completed prediction uses. Raw data were accessible locally, so
this was a local analysis freeze rather than an externally secured holdout.
The first stopped execution computed the calibration phosphorus mean internally
without displaying it; no numerical response or quota summary reached the
analyst before the revised freeze. All published-source exposure remains
documented in the protocol.

## Data and sample audit

The [bulk culture archive](https://doi.org/10.26008/1912/bco-dmo.1005084.1)
and [single-cell XRMA archive](https://doi.org/10.26008/1912/bco-dmo.1005186.1)
are CC BY 4.0 datasets by Filella and colleagues from the same Synechococcus
WH8102 experiment. Phosphorus was measured by colorimetry in culture aliquots
and X-ray microanalysis in individual washed/dried cells; counts used a Coulter
Counter. XRMA quotas are not the bulk chemistry divided by the target count.
The live metadata identify validated version 1 files dated 13 and 18 August
2026. A stale search cache showed an earlier unvalidated XRMA description;
the retained live page and exact downloaded CSV govern this analysis.

There are 51 bulk rows and 397 XRMA rows, grouped into 12 culture/day samples.
The frozen gate requires unique matching identities, at least 20 cells and
complete phosphorus assays. Missingness is not assumed random. Explicit fields
disagree with IDs in 35 rows: all 34 rows of one high-P sample, and one row of
a mid-P sample. Two cell IDs are nonunique. Whole affected samples are
quarantined. No record is relabelled from its measured
values. The exact identifiers and all exclusions are retained in the result.

| Culture/day | XRMA cells | Missing P | Identity issue | Eligible |
|---|---:|---:|---|---|
| High-P / 1 / a | 33 | 2 | None | No |
| High-P / 1 / c | 35 | 0 | None | Calibration |
| High-P / 2 / b | 34 | 0 | EFB2 IDs conflict with high-P label | No |
| High-P / 2 / c | 34 | 2 | None | No |
| Low-P / 1 / a | 34 | 10 | None | No |
| Low-P / 1 / c | 32 | 18 | None | No |
| Low-P / 2 / b | 33 | 0 | None | Test |
| Low-P / 2 / c | 26 | 4 | Nonunique cell ID | No |
| Mid-P / 1 / a | 32 | 0 | Conflicting and nonunique ID | No |
| Mid-P / 1 / c | 34 | 2 | None | No |
| Mid-P / 2 / c | 35 | 1 | None | No |
| Mid-P / 4 / b | 35 | 1 | Nonunique cell ID | No |

Only the two eligible cultures' numerical quotas, bulk stocks and counts are
analysed. The remaining abundance outcomes stay unexamined. The ID-prefix
convention and same-day correspondence are inferred from the archive labels
and metadata, not confirmed by the original investigators. The sample gate
leaves one test culture; its 33 assayed cells do not supply 33 independent
population predictions. Eligibility also selects a nonrandom subset.

## Numerical result

For the calibration and test cultures, respectively:

| Independently measured quantity | High-P / 1 / c | Low-P / 2 / b |
|---|---:|---:|
| Total particulate P, micromoles/L | 7.677 | 0.782 |
| Mean XRMA P quota, fg/cell | 1.061143 | 1.389091 |
| Count, million cells/mL | 54.5 | 34.9 |
| Raw accounting prediction, million cells/mL | 224.084 | 17.437 |
| Raw prediction / observed count | 4.111641 | 0.499626 |

The stock falls to 0.101863 of its calibration value, but measured count falls
only to 0.640367. The XRMA quota rises by a factor of 1.309052, causing the
quota-adjusted count prediction to fall further. With subscript 0 denoting
calibration, the two predictions are `N_0 Q_1/Q_0` and
`N_0 (Q_1/Q_0)(q_0/q_1)`.

| Frozen prediction | Million cells/mL | Predicted / observed | Absolute log error | Factor-1.25 target |
|---|---:|---:|---:|---|
| Fixed phosphorus quota | 5.5515 | 0.15907 | 1.83842 | Missed |
| Independent XRMA quota | 4.2409 | 0.12151 | 2.10772 | Missed |

These are approximately 6.29-fold and 8.23-fold underpredictions. No target
count enters either prediction. The quota model has an additional independent
measurement, not a parameter fitted to that count.

## What fails, and what remains open

The relation between bulk stock, representative cell quota and cell count fails
to transfer under the chosen matches. This is visible even before asking about
equal allocation: raw phosphorus accounting implies 4.11 times the calibration
count and 0.50 times the test count. The required cross-method calibration
changes by a factor of 8.23. A constant calibration offset cannot reconcile
both point estimates.

This does not identify the cause. Possibilities include unrepresented
particulate phosphorus, preparation-dependent losses, unrepresentative single
cells, sample correspondence, or other assay effects. None has been tested here.
No uncertainty is available for bulk assays or the full observation process,
and no population-level or causal rejection follows from one selected test
culture. Different dilution rates accompany the phosphorus treatments.

The scientific gain is a concrete observation requirement: **independent cost
measurements must also be compatible with the stock and population they are
used to explain**. Independence prevents an algebraic tautology but does not
guarantee compatibility. Measured quotas cannot currently support a successful
count-transfer claim in this pilot, or repair the earlier chemostat forecast.
The title and general-law programme remain; their natural-system evidence is
not strengthened by this unsuccessful prediction.

The next useful step is a validated sample crosswalk and assay-comparison
study with replicated cultures, independently measured quotas, stock/count
closure and documented uncertainties. It should precede a new allocation
prediction. The [candidate audit](paired-resource-candidate-audit-2026-10-12.md)
records other accessible sources and the distinction between their bulk and
group-resolved measurements. No investigator was contacted in this task.

## Reproducibility

The complete source and result directories are
`data/paired-phosphorus/2026-10-12/` and
`results/paired-phosphorus-pilot-2026-10-12/`. Five synthetic checks preceded
evaluation. A separate verifier uses 40-digit Decimal arithmetic directly from
the original rows, importing none of the analysis module. It checks 16 numbers,
both accuracy flags, the improvement flag, the frozen source hashes and the
unchanged qualification ledger. Maximum relative numerical discrepancy is
`1.69e-16`.

```sh
make paired-phosphorus PY=build/main-venv-2026-10-09/bin/python
make registry-verify PY=build/main-venv-2026-10-09/bin/python
```

Use an empty reproduction directory. The new registry entry records an actual
measurement pilot, its two-stage freeze history and its restricted inference;
the previous 35 entries remain byte-for-byte unchanged.
