# Biological assay transfer: useful inputs, failed resource-model advantage

16 October 2026. **The frozen reciprocal resource-pool prediction fails its
joint rule.** Its family-balanced error is 0.10184, just above the declared
0.10 normalized-capacity tolerance. Directly transferring the independent
extract assay gives lower error, 0.09464. Assay information transfers; the
fitted reciprocal correction adds no advantage in this cohort.

Reference measure is equal weight per gene family, then per construct: seven
families and ten constructs. This is neither log-orthopolic nor linear-orthopolic
size allocation. It tests a specified effective-workload relation under a
genetic-construct change, not an absolute biological resource budget.

## Chronology and physical inputs

The [protocol](burden-transfer-protocol-2026-10-16.md), source receipts, algorithms
and synthetic checks were committed at **b1dcb08** before numerical calibration.
Forecasts and their separate numerical verification were committed at **bef1f23**
before opening all ten numerical target responses. The prediction SHA-256 is
`d8cc39bdeb8bddebba72afb5c40d9eb5af241c3fd625b9bc1d0060ac9ff3926f`.
Published qualitative outcomes and correlations were known. This is a locally
frozen retrospective comparison, not a prospective or globally blind experiment.

[Borkowski et al. (2018)](https://doi.org/10.1038/s41467-018-03970-x) provides
three normalized measurements for each construct in cell extract and living
bacteria. Twelve mKate initiation variants supply calibration. Ten different
protein/mKate fusions supply separately measured extract predictors and the
withheld cell targets. No target was dropped. The empty insert was excluded in
advance. Four related Viob constructs share one family weight.

The assay measures reporter production capacity. Workload L=(1-x)/x is inferred
from extract capacity x under a linear free-pool budget assumption. The model
predicts cell capacity y=1/(1+kL). The fitted environment factor is **k=0.78346**,
with calibration RMSE **0.05543**. Neither L nor k is a directly measured
ribosome inventory, translation residence time or energy cost. Calibration
assay means span 0.59855–0.84955; new assays span 0.47471–0.87667. Five of ten
predictor values lie outside calibration support: Viob, Leu2, SuhB, Ste12 and
atf1. These were flagged before outcomes and retained.

## Complete fixed comparison

| Model | Family-balanced MAE (primary) | Ten-construct MAE | Maximum error |
|---|---:|---:|---:|
| Reciprocal resource pool | **0.10184** | 0.09322 | 0.18446 |
| Direct assay, y=x | **0.09464** | 0.08867 | 0.19494 |
| Linear burden | 0.10950 | 0.09870 | 0.20908 |
| Affine transfer | 0.10603 | 0.09635 | 0.20017 |
| Constant calibration capacity | 0.20210 | 0.16837 | 0.44332 |

The resource model improves on constant capacity by **49.61%**, on linear
burden by **7.00%**, and on affine transfer by **3.95%**. It is **7.60% worse**
than direct assay transfer. Only the constant-model comparison meets the frozen
20% gain requirement. The reciprocal model narrowly fails the primary absolute
accuracy criterion. Its ordinary ten-construct average falls below 0.10, but
that sensitivity does not replace the predeclared family weighting. The lack
of advantage over direct transfer holds under both weightings.

![Sealed protein-burden forecasts and all declared alternatives](../results/burden-transfer-2026-10-16/transfer.png)

The reciprocal model's signed family-balanced bias is +0.03589. The largest
absolute error is atf1, overpredicted by 0.18446 capacity units; aspA is
underpredicted by 0.13894. No model produces a physically negative forecast
in this cohort. These are descriptive errors, not confidence bounds.

## Source and measurement audit

The ten source means exactly match means recomputed from the triplicates.
Every reported spread matches **sample SD**, to numerical precision, rather
than SEM. The article captions say standard error. We retain this discrepancy
and use recomputed SD descriptively; we do not silently reinterpret the printed
error bars as measurement confidence intervals.

Normalized measurements share controls and experimental batches. Three values
per construct do not create three independent biological interventions. The
four Viob sequences are related; calibration spans only one protein. Shared
input uncertainty and covariance are unpropagated. The extract statistic is a
maximum production rate, whereas the cell statistic is a mid-exponential rate
per optical density. Fluorescence is a production proxy, and the source's
29/37-degree incubation descriptions remain unresolved. These limitations
preclude precise causal attribution of the forecast failures.

## What this adds and what would improve it

The independent assay is a useful predictor across a genetic-construct change.
Direct transfer y=x is exactly the reciprocal model at k=1. The comparison
therefore shows that the calibration-derived common environment correction
does not improve prediction; it does not reject the reciprocal functional
family. Neither result identifies an absolute resource cost or establishes
the proposed biological mechanism. The failed frozen rule gives a concrete
failure boundary for this specified fitted transfer, not a rejection of the
general law across biology.

A stronger follow-up needs separate measurements of mRNA abundance, translation
initiation or residence times, and reporter calibration under the same growth
conditions. Alternatively, the [retained ecological lead](biology-intervention-source-audit-2026-10-16.md)
offers monoculture resource depletion and mixed-species responses, subject to
its own compatibility audit. Reusing these ten outcomes to tune a new cost
function or environment correction would be exploratory. In the requested
domain order, a human/language intervention is now the next priority.

## Reproduction and verification

Six new synthetic and access-control tests recover both candidate worlds,
exercise the independent verifier and ensure poisoned outcomes cannot affect
forecasts. Verification uses a separately decoded, numerically masked workbook,
41-start least squares in log(1+k), centered affine regression and explicit
family-first averaging. It checks **195 quantities** before outcomes and
**334 quantities** after evaluation; the largest absolute difference is
**6.25e-9**. Numerical agreement does not quantify physical uncertainty.

Run `make burden-transfer PY=build/main-venv-2026-10-09/bin/python
STUDY_OUTPUT_ROOT=build/reproductions/NEW` with `MPLCONFIGDIR=build/matplotlib`.
It reconstructs the forecasts, scores, verification and figure and compares
their bytes. The registry appends this actual-measurement study without
altering any earlier run.
