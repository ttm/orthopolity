# Italian magnitude validation, before real sequence fitting

The [source audit](seismic-candidate-audit-2026-10-10.md) found enough matched
CLASS/HORUS events to investigate, but only 699 direct moment estimates. The
next necessary check is whether the registered estimator is calibrated for
converted magnitudes. This protocol and its [configuration](../configs/italian_magnitude_validation_2026-10-10.json)
are to be committed before the simulation ensemble runs. They do not amend the
original physical predictions, introduce real sequence labels or authorize a
real response fit after a failed check.

The physical target is **log-orthopolic** allocation per logarithmic rupture
length: b=D2/2 versus b=1. Simulating b=1 and 1.5 tests their different magnitude
marginals for ideal planar/volumetric support. It does not validate estimation
of D2, physical clustering or the final regression.

## Published conversion and declared observation model

The [HORUS methods](https://doi.org/10.1785/0220200148), Table 9, give
`Mw_proxy = a + beta * M_source`:

| Source and period | a | beta |
|---|---:|---:|
| ML before 2011 | −0.164 | 1.066 |
| ML from 2011 | −0.030 | 1.035 |
| Md before April 2013 | −1.905 | 1.718 |
| Md from April 2013 | −1.132 | 1.718 |

The rounded post-2013 Md intercept is used as printed. The paper describes its
underlying +0.45 Md correction. We use neither a refitted coefficient nor
catalogue values to adjust these simulations. Table 7 supplies ML scatter
estimates 0.18 (the adopted earlier calibration) and 0.16 (2011–2018). A normal
error distribution is our stress-test assumption; the table supplies its scale,
not that distribution or a validated low-magnitude detection model.

HORUS equation 4 generates within-bin jitter from an exponential magnitude
distribution; its illustration uses b=1. The earlier audit deliberately retained
the `_o` files, without this randomization. The methods paper also reports
national b-values and histogram artefacts, now known background. No Italian
cluster-level Mc, b, D2 or regression has been calculated in this repository.

Each of 400 repetitions per cell generates 7,000 true magnitudes above a fixed
lower support, then converts backwards to the source scale, adds the declared
error, rounds that source to 0.1 and converts forwards. The simulated proxy is
rounded to 0.01, then the existing runner rounds it to 0.1. This represents
ordinary positive-magnitude rounding, not a reconstruction of the previously
audited negative-value catalogue/provenance differences. The lower supports
1, 1.5, 2 and 2.5 probe different alignments with the converted grid.

Cases cover a direct rounded-Mw control, all four noiseless conversions, and
the two ML conversions with scatter. Two additional sensitivities vary the
single shared post-2011 calibration slope by ±1.96 times its published 0.016
standard error while the observation pipeline uses the nominal slope. They
illustrate uncertainty omitted by an event bootstrap and are outside the gate.

The post-2011 coefficient covariance as printed is not a valid covariance
matrix: `abs(-0.0011) > 0.065*0.016`. This may reflect rounding or another
publication issue; we do not establish its cause. It prevents literal joint
normal coefficient simulation. No covariance repair is made. A marginal slope
sensitivity does not require the intercept/slope covariance.

## Estimator, independent check and stop rule

Apply the original MAXC+0.2, inclusive 200-event gate, Aki–Utsu estimate and
500-resample bootstrap SE. Resampling bin counts multinomially is distributionally
equivalent to resampling individual observations for this statistic. A normal
interval `b_hat ± 1.96 SE` is used only to diagnose SE calibration. The original
runner uses these SEs in Deming regression and does not output this per-cluster
interval as a physical hypothesis decision.

For each cell record bias, RMSE, eligibility rate, coverage, Monte Carlo errors
and a Wilson interval for coverage. The necessary validation gate requires
absolute mean bias ≤0.05, coverage ≥90% and eligibility ≥95% **in every nominal
cell**, including the declared scatter scenarios. These are engineering
criteria, not a familywise statistical rejection. Record every cell regardless
of whether the gate passes.

A separate, deterministic enumeration integrates the exponential distribution
(or its Gaussian convolution) over the original source bins, combines bins after
conversion and calculates the infinite-population registered-estimator limit.
This checks the mechanism independently of the sampled ensemble. It also
records the gap between the largest and second-largest bin probabilities:
sample MAXC can switch when the population mode is nearly tied.

For noiseless, singly converted complete exponential tails, the source lattice
admits an exact geometric estimate:
`b_grid = log(1 + 1/mean(k)) / (beta * 0.1 * log(10))`, where k counts original
source bins above the first accepted bin. This point estimate is reported as a
diagnostic. It is not automatically valid for noisy tails, mixtures or
source-dependent detection and is not promoted to a registered replacement.

**If any nominal cell fails, stop this bounded attempt before real Italian
sequence construction or Mc/b/D2 fitting.** A failed stress case does not prove
bias in every real mixture and says nothing about which physical prediction is
true. A revised estimator/cohort would need a new, separately validated design.
Passing this gate would still require clustering validation and a freeze before
real qualification. In either case, retain the result as simulation evidence,
preserve the source audit and all earlier empirical outcomes, and update the
paper with the resulting scope limit.
