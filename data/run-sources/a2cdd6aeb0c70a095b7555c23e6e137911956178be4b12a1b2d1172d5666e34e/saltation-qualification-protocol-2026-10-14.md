# Saltation transfer: pre-response discrimination gate — 14 October 2026

Commit this protocol, source audit, configuration, predictor inventory, model,
runner and synthetic tests before running the scenario ensemble. This is a
locally frozen design qualification, not an empirical model comparison. Numerical
wind predictors and response missingness were inspected; numerical sand flux,
height and activity arrays were not. The published conclusion favoring linear
stress scaling and its qualitative scatter are known.

## Question and physical scope

Can this archive distinguish two fixed wind-to-sand-flux laws on later dates?
At one site, compare Q=C(τ−t)+ and Q=C√τ(τ−t)+, where the positive part is
zero below threshold. Each model estimates its own nonnegative C and threshold
t using calibration only. Constant air density is absorbed into C; no comparison
of C across sites is intended. These are the established linear and asymptotic
3/2 stress laws compared by Martin and Kok (2017), not new laws of our own.

The resource-incidence bridge is momentum balance: for airborne particle
incidence n per ground area, τ_ex=n mean(Δp/T), while mass transport is
Q=n m V under the relevant averages. Variable budget, particle speed and momentum
transfer per hop determine the constitutive relation. This is not a measurement
of equal allocation among particle sizes. **Neither log-orthopolic nor
linear-orthopolic size allocation is tested.** The observation measure gives
equal weight to each eligible date and, within it, each eligible 30-minute
interval. A successful qualification would permit a separate, bounded transfer
study; it would not establish the general-law claim.

## Fixed predictors and chronological split

Use unbinned Zenodo 291798, Oceano worksheet, columns A:I only. Select Oceano
because it has 20 distinct recorded dates versus four at Jericoacoara and two
at Rancho Guadalupe; require at least five dates with eligible predictors on
each side. The paper's counts of active-transport days are different and are
not the sampling frame for this audit.

Calibration comprises the first ten distinct recorded dates, 15–24 May 2015.
Prediction comprises the remaining ten, 26 May–4 June 2015. There is no record
for 25 May. This split is fixed before wind eligibility and never moved because
of missing observations or activity. Retain finite τ>0, |θ|≤20 degrees and
|z/L|≤0.15, consistent with the source's wind regime. Use no fQ filter. A missing
height is not a missing zero flux. No flux-derived threshold, normalized flux,
excess stress or published full-cohort fit enters the calculation.

The pre-response simulation uses **all eligible wind rows**, including rows
whose real flux may be missing. This is a favorable complete-response design
scenario, not an assertion of empirical completeness. Real-data feasibility
would need a separately frozen missingness gate before any response fit.
Failure even under this scenario ends this design. Shared trap calibration,
uncertain stress and unavailable response covariance are not repaired by a
row-wise random split.

## Synthetic worlds and calibration

For each generating exponent a∈{0,0.5} and threshold t∈{0.04,0.08,0.12} Pa,
generate Q=τ^a(τ−t)+ on the retained wind predictors. C=1 merely fixes units:
weighted least squares and model ordering are invariant to a common flux scale.
The threshold grid is a declared plausible scenario set within predictor
coverage, not an estimate from sand responses.

Use total multiplicative coefficients of variation 0, 0.1, 0.25 and 0.5;
500 replicates per scenario; NumPy default_rng seed 20261014. A mean-one
lognormal day factor has CV_day=CV_total/2. An independent interval factor has
log-variance log(1+CV_total²)−log(1+CV_day²). Thus the product's marginal CV is
exactly the declared total, with positive within-date dependence. Generate all
calibration dates followed by all prediction dates in workbook order. Use
common noise draws across truths and thresholds within a CV level. Zero latent
flux remains zero. No real flux value or reported flux uncertainty is read.

The paper reports roughly 50% within-stress-bin variability, greater near the
threshold. CV=0.5 is a transparent approximation to that description, not a
source-fitted noise law. Across-date persistence, wind error, changing bed
conditions, subinterval intermittency and variable thresholds are omitted.
Applying a threshold to a mean wind stress is not equivalent to averaging a
threshold process. This deliberately limited simulation cannot establish the
physical adequacy of either model.

In every replicate, refit both C and t for both candidate laws, minimizing
date-balanced original-unit squared error. Constrain C≥0 and 0≤t≤maximum
calibration stress. The solver profiles C and evaluates every active-set
interval's stationary threshold and both endpoints. It therefore does not
depend on a chosen local optimizer start. Zero responses, thresholds at zero,
the no-flux boundary and exact recovery under both laws are tested before the
ensemble. An independent interval-wise least-squares solver checks the results.

## Decision and reporting

Score each model by date-balanced heldout MSE on the same prediction rows.
The generating model is selected only if its score is strictly smaller, outside
a relative tie tolerance 10^-12. Ties count as failures to select correctly.
Numerical failure stops the ensemble and requires a documented implementation
correction; it cannot silently drop a replicate.

Require at least **80% correct selection in every one of the six CV=0.5
scenarios**, both generating laws at every threshold. Other CV values describe
sensitivity; they cannot replace the primary level after inspection. Report
each count, selection proportion and binomial Monte Carlo standard error.
The latter concerns simulation sampling, not empirical uncertainty or the
posterior probability that one law is true. Shared random numbers make the
scenario estimates related. A borderline point-estimate pass remains borderline.

On failure, **stop before reading or fitting the real response arrays**. Preserve
the qualification result and public source; do not rescue the proposed test by
choosing another split, threshold grid, noise level, binning or activity filter.
On passage, freeze a separate actual-response protocol before calibration.
Neither outcome rejects or confirms a physical law. Do not add a failed
source-design qualification to the article's empirical evidence tally.

## Reproduction

Use Python 3.11 and PYTHONPATH=src. Run
`experiments/fetch_saltation.py --stage verify`, then the saltation tests.
Commit this design and run
`experiments/qualify_saltation.py --freeze-commit COMMIT --output NEW_DIRECTORY`.
The runner verifies every frozen source against that commit, refuses to
overwrite a result directory and records implementation/source checksums.
