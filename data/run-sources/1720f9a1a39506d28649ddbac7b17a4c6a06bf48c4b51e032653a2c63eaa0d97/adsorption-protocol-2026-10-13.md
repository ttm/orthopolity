# Frozen pure-to-mixture adsorption transfer — 13 October 2026

Freeze this document, source audit, configuration, predictor audit, model,
runner, fetcher and synthetic tests in git **before fitting real pure uptake**.
Then commit the complete forecasts before evaluating any numerical mixture
uptake. Record both full commit hashes. Published qualitative outcomes are
already exposed; this is an archival transfer audit, not blind confirmation.

## Physical statement and reference measure

Resource: effective adsorption capacity Q, in mmol of one-molecule occupied
sites per gram, inferred only from pure curves at the same temperature.
Reference measure: **counting measure over CO2, CH4 and vacancies**, the
discrete counterpart of linear-orthopolic classes, not logarithmic size bins.
For independent interchangeable sites, the known competitive Langmuir model is

$$q_i=Q\frac{b_i f_i}{1+\sum_j b_j f_j},\qquad
q_0=\frac{Q}{1+\sum_j b_j f_j},\qquad q_0+\sum_iq_i=Q.$$

The independent-site mechanism, reservoir fugacities and calibrated affinities
specify the allocation. Conservation alone does not. Equal occupied shares
require equal activities b_i f_i. Binding affinity is not relabelled as an
additive resource. Per-temperature capacities test within-temperature transfer;
they do not establish a single invariant site count across temperatures.

## Cohort and gas-phase convention

Use every AIF row at 298, 333 and 353 K: 12 pure observations per gas per
temperature; 18, 18 and 9 binary conditions. Retain all three composition
sweeps and both component responses. No outlier deletion, selective pressure
window or post-fit temperature exclusion. Use absolute uptake, equilibrium
composition and nominal temperature as qualified in the source audit.

Primary gas model: Peng–Robinson (1976), classical quadratic a mixing and
linear b mixing, k_CO2,CH4=0. Constants (Tc in K, Pc in Pa, acentric factor):
CO2 (304.1282, 7377300, 0.22394); CH4 (190.564, 4599200, 0.01142).
Pure calibration uses pure-gas fugacity at total pure pressure; mixture
forecast uses mixture fugacity coefficient times equilibrium mole fraction
times total pressure. A state with multiple physical cubic roots stops
before interpretation and requires an explicitly dated qualification.
The ideal-gas sensitivity repeats **both** calibration and prediction using
partial pressures. It cannot replace the primary after seeing outcomes.

## Fixed fits and competing predictions

At each temperature jointly fit pure curves q=Q b f/(1+b f), with a common
positive Q and separate positive affinities. Weighted nonlinear least squares
uses sigma=reported U/2, with no covariance interpretation. Optimize logarithms
within Q=[0.001,1000] mmol/g and b=[1e-6,1e6] MPa^-1. Use the nine deterministic
starts implemented in the frozen module, fixed tolerances, and the smallest
weighted residual sum of squares. Separately fit two positive capacities and
two affinities to the same pure observations and weights for IAST.

Record convergence, bound contact, weighted residuals, Jacobian condition and
parameter correlation, pure residual RMSE, maximum fitted occupancy, and
capacity sensitivity at factors 0.25, 0.5, 1, 2, 4, reoptimizing affinities.
Call the fit *locally identified* only if converged, away from bounds, Jacobian
condition <10^6, and halving/doubling capacity increases weighted SSE by >3.84.
This is a numerical sensitivity gate, **not a confidence interval**: the
threshold borrows a conventional one-parameter scale but covariance is unknown.
It does not establish global uniqueness. Pure fit is pragmatically adequate
only when RMSE is at most 5% of that gas's largest observed pure loading for
both gases. Failed fits remain visible; forecasts from converged but inadequate
models are retained as diagnostics, never promoted as qualified confirmations.

Seal three predictions for every mixture row:

1. **Shared capacity:** competitive Langmuir above, using only joint pure fits.
2. **Competition ablation:** each same fitted pure isotherm at its component
   mixture fugacity, without the shared denominator. Same inputs/parameters.
3. **Established benchmark:** IAST from the separately fitted pure Langmuir
   capacities. Integrate with respect to d ln f:
   Pi_i=Q_i ln(1+b_i f_i^0); solve common Pi with sum_i f_i/f_i^0=1.
   Set x_i=f_i/f_i^0 and q_total^-1=sum_i x_i/q_i^0(f_i^0).
   Retain and flag every hypothetical f_i^0 above calibration coverage.

IAST with equal capacities equals competitive Langmuir and is a software check,
not a distinct comparator. The separate-capacity benchmark has one additional
pure-fit parameter per temperature. No benchmark is fitted to mixture targets.
Classical attribution: Langmuir (1918), doi:10.1021/ja02242a004;
Myers and Prausnitz (1965), doi:10.1002/aic.690110125;
Peng and Robinson (1976), doi:10.1021/i160057a011.

## Evaluation and decision

After forecast commit, verify mixture amounts against the paper's Table 7.
Mismatch stops evaluation; do not silently pick a favorable version. Preserve
each observation, U, forecast, signed/absolute residual and source row identity.
Report MAE and bias separately for each gas, temperature and composition sweep;
also report total-loading MAE and adsorbed CO2 fraction MAE. Primary score is
the mean of the **six temperature-by-gas MAEs**, giving each equal weight.
U agreement counts are descriptive (observation error bars alone are not
prediction intervals). No p-values, resampled confidence intervals or claim
of 90 independent replicates.

A temperature passes the pragmatic shared-capacity transfer criterion only
if calibration is locally identified and adequate, and mixture component MAE
is at most 10% of its corresponding largest pure loading for **both** gases.
The joint primary criterion additionally requires all three temperatures to
pass and at least 20% improvement in balanced MAE over the competition ablation.
These are declared engineering tolerances, not a universal-law theorem or a
claim of significance. Compare IAST honestly even if it wins. Failure cannot
uniquely separate heterogeneous sites, unequal effective footprints, gas EOS
error, adsorbed-phase nonideality or source measurement dependence.

Validate synthetic shared-capacity recovery, unequal-capacity misspecification,
unsaturated nonidentification, pure/zero limits, site conservation, permutation
symmetry and IAST equality before real fitting. An independently implemented
Gibbs derivative and adsorbed-composition solver verify the sealed forecasts
and scores. All fitting, curve-family choices and tolerances remain unchanged
after outcomes; any new model belongs to a later exploratory study.

## Reproduction sequence

Use Python 3.11 with the repository scientific environment and PYTHONPATH=src.
Verify sources; run the synthetic test modules; commit design; run
`experiments/run_adsorption.py --stage predict --freeze-commit DESIGN --output NEW`;
commit those forecasts; run the same driver with `--stage evaluate`, the same
`--freeze-commit`, `--prediction-commit FORECAST`, `--predictions PATH` and a
new output directory. Verify independently, produce the presentation figure,
inspect it, then register immutable artifacts and update status/manuscripts.
