# Heated cantilevers: an energy forecast with limited transfer

**13 October 2026.** The locally frozen cold-to-hot prediction is partly useful,
but does not establish reliable transfer across the selected modes. Ten of
11 primary mode fits are physically admissible. On their 26 hot-condition
targets, balanced mean absolute temperature error is **74.00 K**, versus
**78.77 K** for the spatial-average proxy, **78.94 K** for uniform local loss
and **163.39 K** for the cold-clamp limit. The modest average improvement hides
large mode-specific failures and excludes one physically invalid fit. It is not
an overall confirmation or a significance claim.

## What was predicted and what was already known

The [protocol](cantilever-protocol-2026-10-13.md), code, predictor audit and
synthetic tests were committed at **0428b64** before real damping fits. Forecasts
were committed at **6733362** before scoring numerical fluctuation responses.
The [source audit](physics-candidate-audit-2026-10-12.md) considered Johnson
noise, optical traps and other cantilever archives before selecting the
[Fontana–Bellon dataset](https://zenodo.org/records/7640708). The source's
[published findings](https://doi.org/10.1103/PhysRevE.107.034118), including
problematic modes, were already known. This is retrospective archival transfer,
not a previously unknown empirical confirmation.

We fit damping at the eight colder C30 conditions and five colder C30C
conditions, then forecast damping and thermal motion at the three/two hotter
conditions respectively. No fluctuation amplitude or publisher `TTHEO` curve
enters fitting. The same split applies to every mode. Eleven published mode
cases give 28 potential mode-condition targets. The two preparations are the
same cantilever before/after coating according to the source, not independent
specimens; the reduced archive does not retain ramp/replicate identifiers.

The reference measure counts specified mechanical modes. The resource is mean
harmonic energy; potential energy per coordinate is `k_B*T_fluc/2`. Extended
fluctuation–dissipation physics predicts a dissipation-weighted temperature.
Our specified local loss is spatially homogeneous at fixed temperature and
quadratic in that temperature. A linear thermal profile and known mode shapes
then turn a damping curve into a thermal-motion forecast. These additional
physical assumptions do the predictive work; orthopolity alone supplies no
new fluctuation–dissipation theorem.

## Complete primary outcome

Errors average target conditions within each mode. The aggregate then averages
modes within preparation, and the two preparation means equally. Damping errors
include all fitted cases, including the inadmissible thermal prediction.

| Preparation / mode | Physical local loss | Damping mean absolute relative error | Thermal MAE (K) |
|---|---|---:|---:|
| C30 flexural 1 | admissible | 27.51% | 86.16 |
| C30 flexural 2 | admissible | 12.78% | 11.25 |
| C30 flexural 3 | admissible | 34.98% | 255.57 |
| C30 flexural 4 | admissible | 1.76% | 11.39 |
| C30 flexural 5 | admissible | 2.86% | 6.51 |
| C30 torsional 1 | admissible | 23.72% | 21.25 |
| C30C flexural 1 | admissible | 5.15% | 52.88 |
| C30C flexural 2 | admissible | 2.76% | 30.75 |
| C30C flexural 3 | admissible | 3.26% | 180.85 |
| C30C flexural 4 | **negative inferred local loss** | 17.74% | unqualified |
| C30C torsional 1 | admissible | 2.56% | 66.11 |

The balanced heldout damping error is **11.78%**. C30 modes 4 and 5 forecast
both damping and thermal motion closely. C30 mode 3 fails both. C30C mode 3
has a close damping forecast but a large thermal discrepancy, and the torsional
mode has only 2.56% damping error with a 66.11 K thermal discrepancy. A global
loss curve can therefore transfer while its inferred spatial weighting does not.
This distinguishes a failure of damping extrapolation from a failure of the
additional spatial/observation assumptions; it does not identify which assumption
is responsible.

For C30C flexural 4, the inferred local loss reaches −0.00016359 within the
full prediction domain, despite positive global damping. Its finite algebraic
temperatures are retained for audit but not treated as physical predictions.
This case remains in the denominator of 11 attempts.

![Heldout cantilever forecasts, observations and mode-specific errors](../results/cantilever-transfer-2026-10-13/cantilever.png)

## Fixed sensitivities, not replacement analyses

All comparisons below use identical rows within each analysis. Their different
coverage prevents treating the first and third thermal scores as a clean paired
improvement. Only the first row is the primary result.

| Analysis | Admissible modes / targets | Thermal MAE | Spatial mean | Uniform loss | Cold clamp |
|---|---:|---:|---:|---:|---:|
| Primary, archive 300 K | 10/11; 26/28 | 74.00 K | 78.77 K | 78.94 K | 163.39 K |
| Paper 295 K, observations unchanged | 10/11; 26/28 | 74.47 K | 78.77 K | 79.77 K | 167.14 K |
| Publisher calibration-row mask | 11/11; 28/28 | 67.85 K | 75.02 K | 75.92 K | 170.10 K |
| All damping rows, secondary | 11/11; 28/28 | 70.61 K | 75.02 K | 75.92 K | 170.10 K |

The archived plotting script masks the first C30C flexural-4 damping datum,
without explaining why. Applying that prespecified mask changes this mode's
local loss to admissible and its thermal MAE to 21.12 K; its hot damping error
becomes 2.12%. It does not fix the other problematic modes. The all-damping
secondary has no heldout damping claim and still shows substantial thermal errors.
No sensitivity was promoted after seeing its outcome.

In the primary, the loss-informed forecast improves over uniform local loss
by 11.55 K within C30, but worsens by 1.67 K within the admissible C30C subset.
Thus even the modest pooled advantage is not a consistent gain across the two
preparations. Comparator errors across **all** 28 targets are also retained
(75.02 K spatial mean, 75.92 K uniform loss, 170.10 K cold clamp); comparing
those directly with the 26-target primary score would mix different cohorts.

## Source conventions and a response hidden by the published plot range

Before fitting, the predictor audit found that the paper states a 295 K base,
but the archived code draws 300 K and `2*TAVG-TMAX` is 300 K apart from one
299.141 K row. Primary predictions use 300 K and reconstruct the linear profile
from TAVG. The fixed 295 K sensitivity does **not** rescale the supplied
fluctuation temperatures or resolve their raw normalization. The small effect
of this sensitivity is not proof that the calibration discrepancy is harmless.

After evaluation, inspection of the large C30C flexural-3 residual found an
important plotting limitation: its final archived fluctuation temperature is
**161.12 ± 81.79 K**, while the forecast is **466.39 K**. The preceding observation
is 393.17 ± 56.38 K, versus 449.60 K predicted. `plots.m` maps column 3 directly
to mode 3 but restricts this panel to 250–550 K; the final central point and its
whole displayed error bar fall below that plotting range. The array and the
plot therefore give different visual impressions. The independent verifier
confirmed the mapping and values. No response mask or justified numerical
correction was found. We retain the point, label this limitation, and make no
new claim that it establishes a physical violation of local thermal theory.
The raw time series or author clarification would be needed to resolve it.

The source also supplies a C30C flexural-1 observation of 292.38 ± 39.71 K.
No finite response was discarded for lying below the model's base temperature.
Physical admissibility constrains predictions, not which observations may
contradict them.

## Scientific contribution and limits

This adds a concrete natural-physics forecast and an executable distinction
between global damping, inferred local dissipation and mode energy. It supports
some particular transfers and demonstrates why global agreement alone cannot
justify a resource-allocation explanation. The stronger extrapolation design,
local-positivity gate, geometry-only comparator and complete archived-point audit
are the added work. The underlying physical relation and experimental data are
Fontana and Bellon's contribution.

The result strengthens the article's account of specified departures and failed
predictions. It is not decisive evidence for universal neutral allocation.
Spectral fits, thermometry, equilibrium normalization and drift share errors;
no joint covariance is supplied. TAVG uncertainty is retained but not propagated
as though independent. Error bars and differences are descriptive, without
nominal p-values or full prediction intervals. Equilibrium normalization already
assumes equipartition. The cohort and published conclusions were selected
retrospectively, so local git freezes improve auditability without erasing exposure.

A further physics experiment should identify the spatial coupling independently
of the energy response, or supply full measurement/calibration data sufficient
to test it. Merely adding fit flexibility after these outcomes would not supply
that independence. The requested next domain is chemistry; its candidate screen
should prioritize independently specified stoichiometry, chemical potentials or
transport constraints with an unused concentration/response target.

## Reproduction and retained evidence

- `make cantilever-sources PY=python3.11`: verify pinned source bytes offline.
- `make cantilever-transfer PY=python3.11`: reproduce both stages under the
  committed design and sealed forecasts in a fresh build directory, then run
  independent verification. Retained outputs are never overwritten.
- `make cantilever-registry PY=python3.11`: append/audit the retained study.
- `make all PY=python3.11`: run the full repository tests and original analyses.

[Forecasts](../results/cantilever-forecast-2026-10-13/predictions.json),
[results](../results/cantilever-transfer-2026-10-13/result.json), execution
receipts and [independent verification](../results/cantilever-transfer-2026-10-13/verification.json)
retain all four analyses. Verification uses independent QR fitting, adaptive
spatial integration and explicit extremum checks, not the production formulas
as a numerical oracle. It also checks source/forecast hashes, cohort membership,
all errors and aggregates. Dataset credit: Alex Fontana and Ludovic Bellon,
CC BY 4.0, Zenodo version 7640708. Derived forecasts and plots are this project's
reanalysis; source files remain unchanged.
