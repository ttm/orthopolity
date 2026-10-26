# Public wall-profile transfer: useful improvement, failed accuracy scenario

26 October 2026. **The transferred profile improves mean error, but the fixed
resistance representation is insufficient under the declared error scenario.**
The complete-cohort outcome is **qualification incomplete**: input failures
were recorded before target release and remain failures afterwards.

| Prediction | MAE over all 210 means | Largest absolute error |
| --- | ---: | ---: |
| Case-6 resistance-profile transfer | 1.7473°C | 38.3270°C |
| Geometry plus fixed case-6 residual | 1.9096°C | 42.3367°C |
| Homogeneous geometric conduction | 2.1873°C | 43.1304°C |
| Persistence of case-6 temperatures | 4.1412°C | 14.3850°C |

The primary reduces MAE by **20.12%** against geometric conduction, **8.50%**
against the fixed-additive rival, and **57.81%** against persistence. Its
worst error nevertheless exceeds persistence's. The largest errors involve
unqualified inputs; they are retained, not deleted or repaired. The primary
beats both geometric and additive forecasts in four of five experiments;
case 4's geometric MAE (2.1356°C) is slightly lower than the primary (2.1438°C).
These are descriptive comparisons from five conditions of one wall, not
independent samples of 210 walls or 38,010 experiments.

| Case / nominal difference | Transfer MAE | Means passing frozen range/drift gates | Outside transfer envelope, all | Outside, passing gates |
| --- | ---: | ---: | ---: | ---: |
| 1 / 50°C | 0.8590°C | 39/42 | 13/42 | 13/39 |
| 2 / 45°C | 2.7524°C | 30/42 | 23/42 | 15/30 |
| 3 / 40°C | 2.6483°C | 24/42 | 24/42 | 13/24 |
| 4 / 35°C | 2.1438°C | 39/42 | 20/42 | 17/39 |
| 5 / 30°C | 0.3329°C | 42/42 | 3/42 | 3/42 |
| **All** | **1.7473°C** | **174/210** | **83/210** | **61/174** |

Thus even the 174 observations whose profiles pass the prespecified checks
do not all fit their conditional marginal envelopes. Case 5 is the only
complete experiment passing those checks: its transfer improves mean error
from geometric 0.7576°C to 0.3329°C, while **three of 42** observations still
fall outside the frozen transfer bounds. Passing the checks is not independent
proof of equilibration or certification of the stated sensor accuracy.

## What was predicted

The [protocol](hotbox-transfer-protocol-2026-10-26.md) conditions on insulation
sensors c/g and learns a cold-to-hot resistance fraction from case 6, the
smallest nonzero forcing. It predicts d/e/f in five stronger-forcing cases
without fitting their interior readings. A geometric-plus-additive rival
fits the same calibration exactly but predicts a different response to forcing.
Steady source-free one-dimensional conduction with a fixed normalized resistance
profile gives the primary forecast, including arbitrary fixed depth dependence
of conductivity. The representation need not remain valid when conductivity's
spatial shape changes with temperature or when lateral transport matters.

The reported ±0.15°C sensor accuracy is used only as a conditional bounded-error
scenario, with no independence assumption or reduction by the 181 time samples.
Calibration and target-anchor errors are propagated before target release;
the target measurement allowance is then included. Outside-envelope counts
are incompatibilities with that scenario, not statistical rejection at a
specified confidence level or proof of a particular alternative mechanism.

Homogeneous geometric forecasts exceed their sensor-only ±0.30°C residual
allowance for **173/210** means. Allowing each nominal sensor position to move
by at most 0.5, 1, or 5 mm leaves **160, 147, or 74** exceedances, respectively.
Those are illustrative placement scenarios, not documented installation
tolerances. The transfer model absorbs fixed geometric/profile differences
through calibration, but its remaining errors cannot uniquely be attributed
to convection, changing conductivity, observation error or incomplete equilibrium.

## Observation limitations retained

The [original public archive](https://doi.org/10.5281/zenodo.8204755) and
[methods](https://doi.org/10.54337/aau544775163) are available and checksummed.
The first 15-position design **69deda5** failed because calibration/control
sensor 8_f is entirely missing. The [dated amendment](hotbox-transfer-amendment-2026-10-26.md)
excluded the whole position 8 before target interior release; this is explicitly
an amended 14-position study. No other positions were excluded and no values
were imputed. Original qualification failure and receipt remain in the repository.

The source's internal calibration range is −10 to 50°C. Some anchors are outside
it; case-4 position 12 g is approximately −47.795°C. All 28 selected case-4
anchor series and all 42 released interior series are constant throughout
their archived 181 readings. These treated records do not provide 181 independent
replicates or independent evidence of temporal stability. The earlier three-hour
window needed to reproduce the source's equilibration criterion is unavailable.
The unfit zero-forcing control was [reported before targets](hotbox-forecast-2026-10-26.md);
its small residuals were not used to estimate corrective offsets.

The [source article](https://doi.org/10.1016/j.enbuild.2025.116646) already reports
convection and increased heat transfer. Those qualitative and aggregate outcomes
were exposed before this design. This study tests the frozen quantitative
transfer on locally withheld readings; it does not independently discover
convection or establish global blinding.

## Verification and scientific contribution

Operative design **a18fbec** follows the availability amendment and a numerical
roundoff repair of the independent verifier. Forecasts were pushed as **0db6966**
before all **38,010 target interior cells** were decoded. Independent exact-rational
and convexity calculations check 2,975 forecast quantities. Separate split-line
parsing with compensated sums verifies **88,690 temperature cells and 1,267 clocks**,
then reconstructs all 210 observed summaries, residuals, qualification flags,
sensitivities, scores and verdict with **4,934 numerical comparisons**. Maximum
difference is **1.43e−14**. No target parameter was refitted; dynamic data remain unopened.

This adds an explicit example of **predictive improvement without adequate
absolute accuracy**, and shows why observation qualification must precede a
physical explanation. The coordinate is physical depth or thermal resistance,
neither log-orthopolic nor linear-orthopolic size allocation. Temperatures do
not measure a complete energy budget or conserved heat throughput here.
The result sharpens an application boundary; it does not uniquely confirm or
refute the general law. It is kept in supporting material without expanding
the main article's empirical claim.
