# Sand transport: chronological design fails the discrimination gate

**The public data are available, but this proposed transfer is too weak under
the frozen variability scenarios.** At CV=0.5, selection of the generating law
is only 54.6–67.2%, versus the required 80% in every case. All six primary
scenarios fail. The stop rule was applied before reading or fitting numerical
sand-flux responses. Neither transport law is favored by this result.

The [source audit](natural-source-audit-2026-10-14.md),
[protocol](saltation-qualification-protocol-2026-10-14.md), implementation,
configuration and original sources were frozen at `bdc1b78` before the ensemble.
The published qualitative conclusions were known. This is simulation-based
design qualification using real wind predictors, not a new empirical result.

## Design and result

The accessible [Martin–Kok archive](https://zenodo.org/records/291798) contains
dated wind and sand measurements from three sites. The fixed Oceano split
uses the first ten recorded dates, 15–24 May 2015, for calibration, and the
last ten, 26 May–4 June, for prediction. Independent wind gates leave **107
calibration and 53 prediction intervals**, with at least one eligible interval
on each of the twenty dates. Weighting gives each date an equal share and
each eligible half-hour within that date an equal share of its weight.

The two known laws are Q=C(τ−t)+ and Q=C√τ(τ−t)+. Both C and t are fitted
anew for each model in each replicate. Models predict the same later-date
synthetic responses; selection uses smaller date-balanced MSE. There are
24 scenarios and 500 replicates each, **12,000 synthetic datasets**. At a fixed
noise level, scenarios share draws to make comparisons less noisy; they are
not 12,000 independently collected datasets.

| Generating law | Threshold (Pa) | CV=0 | CV=0.10 | CV=0.25 | CV=0.50 |
|---|---:|---:|---:|---:|---:|
| Linear | 0.04 | 100% | 98.0% | 78.0% | 65.4% |
| 3/2 | 0.04 | 100% | 88.8% | 62.4% | 58.0% |
| Linear | 0.08 | 100% | 93.0% | 76.0% | 67.2% |
| 3/2 | 0.08 | 100% | 81.2% | 57.6% | 54.6% |
| Linear | 0.12 | 100% | 83.4% | 67.8% | 59.0% |
| 3/2 | 0.12 | 100% | 74.8% | 55.2% | 56.2% |

The table gives correct-model selection fractions, not probabilities that a
physical law is true. No ties occurred. Primary Monte Carlo standard errors
are 2.10–2.23 percentage points, far smaller than the deficits from 80%.
All noiseless cases recover the generating model. Already at CV=0.25 every
scenario falls below the primary threshold; the declared CV=0.5 verdict is
not a borderline numerical result.

![Correct model selection across synthetic variability levels](../results/saltation-qualification-2026-10-14/selection.png)

Error bars show ±1.96 binomial Monte Carlo standard errors, only as a simulation
precision diagnostic. At 100% observed selection this approximation gives zero
width; it does not establish exact certainty. The dashed line is the declared
gate, which applies at CV=0.5 to every scenario.

## What this does and does not establish

The paper's approximately 50% within-stress-bin scatter motivates the primary
variability scenario, but the lognormal distribution, date factor and threshold
grid are assumptions. Independent dates, exact stress and fixed bed properties
are additional simplifications. Subinterval intermittency and changes in soil
conditions are omitted. All eligible wind rows are simulated even where real
sand records may be incomplete. This is a favorable completeness assumption,
not a mathematical upper bound on discrimination attainable by any analysis.

The result is specific to this split, model pair, fitting/scoring rule and
noise scenarios. It does not show that the whole archive or a better-supported
experiment could never distinguish the laws. We do not change the split or
noise model to obtain a favorable result, and we do not fit real targets after
this stop. The original workbook remains intact for a separately justified
future design.

There is also a conceptual limit: wind stress is a varying momentum-throughput
budget, not a size coordinate. This proposed study concerns constitutive
transport and resource incidence. **Neither log-orthopolic nor linear-orthopolic
allocation among coexisting sizes is tested.** Even successful selection would
not establish that allocation. Accordingly this finding stays in the research
record and is not added to the article's empirical evidence tally.

## Verification and next step

An independent implementation reconstructs the noise through product moments,
recalculates all **24,000 heldout model scores**, selection counts, Monte Carlo
errors and the gate, and independently refits **144 representative cases**
using weighted two-column least squares on each active-set interval. It checks
32,184 numbers, with maximum absolute discrepancy 2.85×10^-14. It uses saved
wind predictors and no production fitting helpers; this numerical agreement
does not certify the physical noise model or measurement independence.

The [full result](../results/saltation-qualification-2026-10-14/result.json),
[compact summary](../results/saltation-qualification-2026-10-14/summary.json)
and [verification](../results/saltation-qualification-2026-10-14/verification.json)
preserve every scenario, fitted parameter and score. Reproduce offline with
`make saltation-qualification PY=build/main-venv-2026-10-09/bin/python STUDY_OUTPUT_ROOT=NEW_DIRECTORY`.

The useful next advance is an independently measured particle cost or a
controlled change in available transport resource, together with grain-specific
incidence. Controlled sediment experiments and catchment water balance remain
listed in the source audit, with their unresolved requirements. A further
familiar exponent fit would provide less evidence than a prediction of a new
tradeoff from those independent measurements.
