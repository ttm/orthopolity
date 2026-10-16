# Protein burden: frozen assay-to-cell transfer

16 October 2026. Freeze this protocol, implementation, tests, configuration and
source receipts before numerical calibration. Freeze forecasts and their
verification in a second commit before opening the ten target cell responses.
This is retrospective archival validation. The original paper's qualitative
successes, correlations and several published model constants are known.
Individual numerical target observations have not been displayed or fitted.

## Question and physical scope

Can a separately performed cell-extract assay predict the expression capacity
of living bacteria after changing the protein being expressed? Calibrate on
twelve initiation-sequence variants of one protein, then predict ten different
protein constructs. The assay measures a normalized reporter production rate,
not an absolute ribosome, amino-acid or energy cost. Its inferred workload is a
restricted effective-resource hypothesis. Reference measure is equal weight per
gene family, then per construct. This is neither log-orthopolic nor
linear-orthopolic allocation across size classes.

Source: Borkowski et al. (2018), *Cell-free prediction of protein expression
costs for growing cells*, DOI [10.1038/s41467-018-03970-x](https://doi.org/10.1038/s41467-018-03970-x).
Publisher original workbook and methods supplement are retained; copies from
Europe PMC match byte-for-byte. No new biological experiment is proposed.

## Cohorts and response separation

Use only the `Figure1` worksheet of the original workbook:

* Calibration: rows 35–46, Rand1–Rand12. Extract-assay triplicates C:E and
  living-cell triplicates K:M. These constructs express the same mKate protein
  with different initiation sequences. Arithmetic means define each observation.
* Prediction inputs: rows 55–64, extract-assay triplicates C:E. Identities are
  Viob, V1, V2, V3, URA3, aspA, Leu2, SuhB, Ste12, atf1. Each protein is fused
  to mKate and uses the BCD2 initiation sequence.
* Withheld outcomes: the same rows, K:M. Decode these only after forecasts are
  committed. Source means N and spread O are opened then for an audit of the
  reported summaries, never to change the prediction or exclusions.
* The empty insert/mKate-only construct at row 54 is excluded by design: it is
  not a new protein. No other construct is excluded. The four Viob constructs
  constitute one family; the other six each constitute one family. Primary
  errors therefore average over seven families. Ordinary ten-construct scores
  remain descriptive sensitivity outputs.

Labels in both source blocks must match exactly after removing spaces. All
required triplicates must be finite. Calibration means must have 0 < x < 1 and
y > 0; target assay means must have 0 < x <= 1. Failure stops before outcome
evaluation; do not clip, silently omit, or substitute rows. Predictions outside
calibration assay support stay in the cohort and are flagged. Replicate values
are already normalized by the source; do not normalize again. No precomputed
author predictions, other media, weak-BCD21 outcomes, growth rates, operon
outcomes, or fitted mechanistic constants enter this comparison.

## Fixed resource hypothesis and alternatives

Let x be extract-assay capacity relative to its no-construct control and y the
analogous living-cell capacity. If reporter output tracks a common free pool
and total bound demand is linear in that pool, x=1/(1+L) defines workload
L=(1-x)/x. Assume this workload transfers to cells through one common factor k:

$$\hat y=\frac{1}{1+kL},\qquad k\ge0.$$

This follows a conditional mass-action budget model. Conservation alone does
not imply it, and it does not establish equal resource shares. Here k is an
empirical environment-transfer parameter; it is not a separately assayed
physical resource price. Saturated initiation, ribosome exclusion/queues,
construct-dependent mRNA stability and metabolic activity can invalidate the
assumed transfer. A change in genetic construct is the intervention, while
its extract assay supplies the independently obtained predictor.

Fit k by equal-weight squared error over the twelve calibration means. Bound
the search by max(0,max((1/y-1)/L)); beyond this value every prediction lies
below its observation and error cannot decrease. Search linear and logarithmic
grids and refine every sampled local minimum, retaining boundaries. Independent
verification uses multi-start least squares in log(1+k).

Fit and retain four alternatives on the same calibration means:

1. Linear burden: y=1-k(1-x), k>=0 by constrained one-parameter least squares.
2. Affine empirical transfer: y=a+bx by unconstrained ordinary least squares.
3. Constant capacity: the mean calibration y, ignoring the new assay.
4. Direct assay transfer: y=x, no fitted parameter.

Do not clip any forecast to [0,1]; retain and count physically negative
forecasts. Affine and linear alternatives have no claim to physical validity
outside their calibration range, but remain prediction benchmarks. All models
have their own calibration fits and no target-dependent adjustment.

## Decisions, uncertainty and interpretation

Primary accuracy requires family-balanced MAE <= **0.10 normalized-capacity
units**. This is an absolute ten-percentage-point engineering tolerance tied
to the unit control, not a fraction of the largest calibration response.
Predictive advantage requires at least **20% lower family-balanced MAE** than
each of the four alternatives separately. The joint rule requires accuracy and
all four advantages; report every individual result. These are declared
practical criteria, not statistical tests. Report signed bias, maximum error,
ordinary construct MAE, extrapolation and source-summary discrepancies too.

Three normalized measurements share reference controls; source labels say STD
while figure captions say standard error. Recompute sample SD from triplicates
and compare reported spread to both SD and SEM after opening targets. No
population confidence interval, independent-replicate claim or automatic
measurement-precision agreement is permitted. Calibration-input uncertainty,
batch effects and correlated errors are not propagated in this first transfer.

The extract statistic is a maximum rate, whereas the cell statistic is a rate
per optical density near mid-exponential growth. Fluorescence is a proxy for
protein production. The methods also contain a 29/37 degree incubation
description conflict. These conventions are inherited without inventing a
temperature correction. The source's own translation model is established
prior work and is not claimed as a discovery of this project.

A successful transfer would support the stated effective-workload relation in
this finite cohort. Beating the constant benchmark alone demonstrates useful
assay information, not the reciprocal form. Failure against the affine or
linear alternatives limits the resource model's added value. None of these
outcomes independently establishes neutral allocation or the general law.

## Execution

Use Python 3.11. Run the synthetic tests before calibration; they recover the
reciprocal and linear worlds, check budget balance and bounds, and poison target
cells to verify separation. Verify sources, commit the design, run `predict`,
independently verify and commit the forecasts, then run `evaluate`. Keep a
separate independent verification, exact offline replay, report and registry
entry. Update `docs/status.md` even if eligibility fails. Preserve all earlier
studies and untracked files unrelated to this study.
