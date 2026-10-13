# Cantilever prediction design review

**Date:** 12 October 2026. **Status:** design advice, not a frozen protocol.
No numerical `TFLUC`, `PHI`, or `TTHEO` arrays were inspected for this review.
The published methods and qualitative results were read, including the reported
problematic modes. This is consequently a retrospective replication opportunity,
not a previously unknown confirmatory experiment.

## Scientific target and independence

The proposed target is a nonequilibrium departure: can the measured temperature
dependence of mechanical damping predict mode energies without fitting those
energies? The comparison measure counts specified mechanical modes. The resource
is mean harmonic energy, with potential energy per coordinate
`k_B T_fluc / 2`. The physical temperature field and mechanical strain profiles
determine which local baths contribute to each mode.

Fontana and Bellon's [paper](https://arxiv.org/html/2208.08356) derives a
dissipation-weighted temperature and supplies the [public dataset](https://zenodo.org/records/7640708).
Its fluctuation temperatures use equilibrium normalization. Its damping,
frequency and fluctuation estimates come from the same spectra. Thus the proposed
analysis tests transfer between observables conditional on the source calibration;
it does not newly validate equilibrium equipartition or provide statistically
independent measurements. The source already reports imperfect predictions for
some modes. Those modes must remain in the comparison.

The relevant new work would be an executable audit of the prediction, including
the physical admissibility of its inferred local loss, comparisons against
simpler predictions, and the consequences of withholding damping observations.
It would not be a discovery of the extended fluctuation-dissipation relation.

## A closed prediction formula

Let `z=x/L`, `T0=295 K`, and `Delta=Tmax-T0=2(Tavg-T0)` under the declared
linear temperature profile. Normalize the squared mechanical strain profile:

\[
\rho(z)=\frac{\psi(z)^2}{\int_0^1\psi(u)^2\,du},
\qquad \mu_r=\int_0^1z^r\rho(z)\,dz,\quad \mu_0=1.
\]

For flexure, `psi` is proportional to the second derivative of the deflection
eigenfunction; for torsion it is proportional to the first derivative. The
normalization removes the arbitrary eigenfunction amplitude. Reference positions
and mode numbering must be fixed from the source geometry, never chosen from the
fluctuation target.

Suppose the local loss law at this mode's frequency is

\[
d(z;\Delta)=A+B\Delta z+C\Delta^2z^2.
\]

Then the measured global loss is

\[
\Phi(\Delta)=\int_0^1d(z;\Delta)\rho(z)\,dz
=A+B\mu_1\Delta+C\mu_2\Delta^2.
\]

Fit only the damping observations to
`Phi=a+b Delta+c Delta^2`. The inversion gives
`A=a`, `B=b/mu_1`, `C=c/mu_2`. Consequently

\[
T_{\rm pred}=T_0+\Delta
\frac{a\mu_1+b\Delta\mu_2/\mu_1+c\Delta^2\mu_3/\mu_2}
{a+b\Delta+c\Delta^2}.
\]

This expression makes the target separation explicit: no fluctuation amplitude
appears in the inferred spatial weighting. Do not use the publisher's `TTHEO`
array as an input, fitting target, model selector or numerical validation oracle.
It may only be compared after independently generated forecasts and outcomes are
sealed, if that comparison is separately declared.

If the fit instead uses `h=Tavg-T0`, write `Phi=a+b_h h+c_h h^2` and use

\[
T_{\rm pred}=T_0+2h
\frac{a\mu_1+b_hh\mu_2/\mu_1+c_hh^2\mu_3/\mu_2}
{a+b_hh+c_hh^2}.
\]

Mixing these two coefficient conventions introduces a factor-of-two error.

## Physical admissibility is a prediction requirement

A positive fitted global loss does not ensure positive local dissipation.
The local polynomial must be nonnegative throughout every thermal interval used
for either calibration or prediction. For nonnegative heating up to `Delta_max`,
this is equivalent to checking

\[
g(t)=a+(b/\mu_1)t+(c/\mu_2)t^2\ge0,
\qquad 0\le t\le\Delta_{\max}.
\]

Check both endpoints and, when the quadratic coefficient is positive, its vertex
if that vertex lies inside the interval. A finite grid alone is insufficient to
guarantee this condition. Also require positive predicted global loss.

When these conditions hold, the normalized loss is a probability weight and
necessarily `T0 <= Tpred <= Tmax`. Violation of this envelope is an implementation
or physical-model problem, not a surprising prediction to accept uncritically.
In numerical checks, tolerances should scale with the fitted loss magnitude.

Two defensible choices must be distinguished before seeing outcomes:

- Unconstrained quadratic fitting followed by an admissibility gate. A rejected
  mode is a model-qualification failure and remains in the final accounting.
- A predeclared constrained fit guaranteeing nonnegative local loss. This is a
  different estimator and must be described as such. Nonnegative coefficients
  are sufficient but unnecessarily restrictive; positive loss can decrease with
  temperature.

Do not clip a fitted loss to zero or drop an adverse temperature interval after
seeing the target. Either action changes the prediction family.

## Comparators that locate the explanatory gain

Use three parameter-free alternatives at every scored condition:

1. **Spatial-average proxy:** `Tpred=Tavg`. All modes receive the same mean
   harmonic energy at the imposed mean physical temperature.
2. **Cold-clamp limit:** `Tpred=T0`. Dissipation is concentrated at the cold clamp.
3. **Uniform local loss:** `Tpred=T0+Delta*mu_1`. The temperature field is weighted
   only by mechanical strain energy; local loss is temperature independent.

The third is essential. Beating the first two alone may reflect the ordinary
mode geometry without showing that inference from the damping-temperature curve
adds predictive value. Describe the first as an unweighted-temperature proxy;
equilibrium equipartition does not itself require this rule in a body with a
temperature gradient.

For torsional mode `m`, a uniform rectangular beam gives
`rho(z)=2 cos^2((m-1/2) pi z)`. In particular,
`mu_1=1/2-2/pi^2` for the first torsional mode. This is a useful independent
analytic check of numerical integration. Flexural moments should be checked by
quadrature refinement and independent evaluation of the clamped-free mode shape.

## What is actually withheld

Two different analyses have different evidential meanings:

- Fitting all `PHI` observations and then predicting `TFLUC` is a separation of
  target observables. Shared spectra, thermometry and baseline calibration mean
  the estimates can remain correlated.
- Leaving out a complete measurement condition from the damping fit before
  forecasting its `TFLUC` is stronger. If heating powers recur on upward and
  downward ramps, withhold the entire repeated-power group, provided power-group
  identifiers are available independently of the target. This reduces direct
  sharing of the withheld spectral fit.

With the proposed 11 C30 and 7 C30C conditions, a quadratic has few residual
degrees of freedom, especially after exclusions or grouped withholding. Record
the rank and condition number of every calibration design. Do not hide singular
or physically inadmissible folds by averaging only the successful predictions.
Whether these rows represent unique powers must be settled from metadata before
choosing the split. No claimed independence follows merely from calling rows
training and test sets.

Equilibrium normalization points are calibration anchors, not scored successes.
Use the source's experimental identifiers to identify them, rather than selecting
them because the fluctuation temperatures happen to be near `T0`.

## Errors, uncertainty and reporting

Freeze weighting and uncertainty treatment before unmasking the numerical target.
Reported damping errors can define weighted least squares, conditional on the
temperature estimates. Temperature uncertainty then remains an explicit additional
limitation; treating fitted temperatures as exact does not produce full physical
prediction intervals.

Fluctuation errors include shared calibration and systematic effects. Without the
joint covariance, diagonal normalized residuals are diagnostics, not valid
independent chi-square statistics or evidence for a nominal significance level.
Likewise, independently perturbing all published error bars in a Monte Carlo
calculation cannot establish the unknown covariance structure.

Report absolute prediction errors in kelvin by specimen, mode and condition.
For a single descriptive aggregate, average within each mode, then within each
specimen, then across specimens; this prevents a specimen with more rows or modes
from dominating silently. Compare every model on identical eligible target rows.
Retain an explicit denominator of all attempted modes and folds, including
physical-admissibility failures. A scatter plot with the physical temperature
envelope is more informative than a binary overall verdict.

Interpretation should distinguish agreement of the damping model with its own
input data, admissibility of the inferred local loss, predictive error in the
fluctuation target, and improvement over each simpler comparator. These are
different questions. A failure can challenge the assumed spatially uniform
quadratic loss or linear thermal profile without refuting local thermal physics.
A success supports this constrained physical realization; it does not establish
universal equal allocation.

## 13 October addendum: low-temperature calibration and hot-condition prediction

The proposed primary analysis now fits the lowest `ceil(2N/3)` heating
conditions and withholds the hottest remainder from both damping calibration and
fluctuation assessment: eight calibration and three target conditions for C30,
five calibration and two target conditions for C30C. This is a stronger test than
the all-condition fit because it asks the local loss law to extrapolate. The
all-condition damping-to-fluctuation calculation remains a clearly labelled
secondary replication diagnostic.

The following details should be settled in the frozen protocol:

- Choose and record the split once from heater or temperature predictors alone.
  Preserve physical condition identity across modes. If the archive provides
  only mode-specific temperature estimates, document precisely which estimate
  orders common physical conditions. Do not choose different physical target
  rows for different modes merely because noisy temperature estimates reorder
  them. If repeated heater powers can be identified, keep each power group on
  one side of the split. A tie at the boundary needs a predetermined rule.
- State whether the rows are distinct experimental powers, aggregated powers,
  or individual conditions whose replicate identifiers were lost. Without this
  information, describe withholding reported conditions rather than claiming
  independent experimental replicates or a before/after coating intervention.
- Use only calibration-row loss angles in the fit. In the fluctuation formula,
  the denominator at a target temperature is the **predicted**
  `a+b Delta+c Delta^2`, not the observed target loss angle. Substituting the
  latter would leak the withheld response and change the prediction.
- Retain all eleven published mode cases, including source-reported problematic
  ones. Require finite predictor values, enough distinct temperatures for rank
  three, positive physical damping inputs, and at least one residual degree of
  freedom. A standardized quadratic design reduces numerical ill-conditioning;
  record its singular values or condition number and target extrapolation
  leverage. These diagnostics do not establish that extrapolation is reliable.
- Fit weighting must be fixed before target inspection. If inverse reported
  variance weights are used, require finite positive uncertainty values and
  specify what happens if this requirement fails; do not silently invent an
  uncertainty floor. Quadratic disagreement with the calibration observations
  should be reported rather than used to remove an inconvenient mode.
- Check local-loss positivity from `T0` through the largest local temperature
  in the full declared prediction domain, not just the calibration range.
  A fit positive on the calibration interval but negative in the withheld range
  has failed its physical extrapolation. Preserve this failure even if some
  individual target temperatures still give plausible ratios.
- Never exclude a finite observed fluctuation temperature because it lies
  outside `[T0,Tmax]`. That envelope constrains the model, not which target
  observations are allowed to contradict it.

For each mode, report three separate outcomes: physical eligibility over the
declared domain, prediction error in heldout damping, and prediction error in
heldout fluctuation temperature. Absolute relative errors are a readable damping
diagnostic when the observed loss is positive; retain the corresponding raw
loss errors and units. Use absolute errors in kelvin for the fluctuation target.
Also report paired differences in absolute error against each of the three
fixed comparators; a negative difference then has the straightforward meaning
that the damping-based forecast was closer on that condition.

For a descriptive overall fluctuation score, first average over target conditions
within each mode, next over modes within each preparation, and finally over the
two preparations. This gives equal preparation weight without implying that
conditions or modes are independent replicates. Show the mode-level results and
the full number attempted. If some fitted modes are inadmissible, do not present
an error score on the survivors as overall predictive success. Report the
admissible fraction separately and label any same-row comparator calculation as
conditional on that subset. There is no need to create an arbitrary numerical
penalty to conceal undefined physical predictions.

This design can discriminate three possibilities. Accurate extrapolated damping
and fluctuation predictions support the specified transfer. Accurate damping but
poor fluctuation predictions challenge the conversion from global loss to its
local spatial profile or another observation assumption. Poor damping
extrapolation or negative inferred local loss already defeats the proposed
quadratic transfer before fluctuation data are consulted. Retaining these cases
is scientifically more informative than selecting the subset with a successful
temperature forecast.

Only partial uncertainty propagation is possible from the reduced archive.
Linear-fit coefficient covariance conditional on reported temperatures and
damping errors may be reported with that explicit scope. It cannot supply a
full uncertainty statement when the shared spectral fits, baseline normalization,
temperature calibration and drift covariances are unavailable. Use no nominal
independent-sample significance test or population-level claim from the handful
of heldout conditions. Published error bars and sensitivity analyses remain
useful descriptive information.
