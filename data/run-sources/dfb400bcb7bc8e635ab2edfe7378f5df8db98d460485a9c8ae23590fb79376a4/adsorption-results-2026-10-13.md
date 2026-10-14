# Pure-gas calibration predicts mixture competition

Study frozen 13 October 2026; verification and report completed 14 October.

**The common-capacity forecast passes the declared engineering rule at all
three temperatures.** Its balanced component MAE is 0.247 mmol/g, versus
0.620 when competition is omitted: a 60.1% improvement. Established IAST,
also calibrated only from pure gases, performs slightly better at 0.243.
This is a useful transfer of specified constraints in a chemical system,
not a new adsorption law or demonstrated advantage over IAST.

## Design, chronology and observations

The [protocol](adsorption-protocol-2026-10-13.md), source audit, inputs, model
and synthetic tests were committed at **`08efaa1` before real pure uptake was
fitted**. All mixture forecasts were committed at **`158a22c` before numerical
mixture responses were evaluated**. Publisher qualitative outcomes were known;
the design is locally frozen and retrospective, not blind or externally
preregistered. There was no change of model, cohort, fit or scoring rule after
evaluation. An independent verifier's diagnostic routine initially stopped
because a local function shadowed a numeric variable; that implementation
error was corrected without changing any frozen predictions or results.

The [author archive](https://zenodo.org/records/17604326) and
[paper](https://doi.org/10.1021/acs.jced.4c00358) provide absolute CO2 and CH4
uptake on binderless RM8850 zeolite Na-Y. The three common temperatures
(298, 333, 353 K) supply 72 pure calibration observations and 45 mixture
conditions, hence 90 component targets. All qualified rows are used. Mixture
composition is the measured equilibrium composition, not the feed ratio.
The AIF and article table values match exactly. The apparent table-count
discrepancy was eleven blank separators, not missing observations.

Resource is an effective common adsorption capacity at each temperature;
reference measure is **counting measure over gas species and vacancies**,
the discrete linear-orthopolic comparison. The independent-site model gives
q_i=Q b_i f_i/(1+sum_j b_j f_j). Affinities and capacity come from pure
curves; gas fugacities use fixed Peng–Robinson constants and k_ij=0. Equal
occupied allocation occurs only at equal b_i f_i, and is not imposed at
equal gas mole fractions. Finite capacity alone does not derive the model.

## Complete primary comparison

| Model | Balanced component MAE (mmol/g) | Total-loading MAE (mmol/g) | CO2 adsorbed-fraction MAE | Within reported U |
|---|---:|---:|---:|---:|
| Shared-capacity Langmuir | 0.24746 | 0.25543 | 0.04975 | 39/90 |
| No-competition ablation | 0.61997 | 1.20808 | 0.09402 | 20/90 |
| Separate-pure-capacity IAST | 0.24280 | 0.22859 | 0.04983 | 38/90 |

Balanced component MAE averages six temperature-by-gas MAEs equally, rather
than allowing the temperatures with more pressures to dominate. Total and
composition errors average temperatures equally. All three predictions use
only pure-gas calibration. IAST permits separate pure saturation capacities,
adding one pure-fit parameter per temperature, and solves an ideal adsorbed
solution. No mixture response is used for fitting any model.

| Temperature | CO2 MAE: shared / ablation / IAST | CH4 MAE: shared / ablation / IAST | Shared MAE as % of pure maxima (CO2 / CH4) |
|---|---|---|---|
| 298 K | 0.465 / 0.647 / 0.467 | 0.238 / 1.127 / 0.236 | 5.69 / 5.66 |
| 333 K | 0.301 / 0.482 / 0.294 | 0.163 / 0.686 / 0.159 | 4.02 / 5.13 |
| 353 K | 0.181 / 0.318 / 0.175 | 0.137 / 0.460 / 0.126 | 2.56 / 5.13 |

The frozen tolerance is component MAE <=10% of the corresponding **maximum
pure-gas loading**, not 10% relative error for every mixture observation.
All three shared fits pass the local identifiability and pure-fit gates;
all six mixture cells meet that tolerance. The 60.1% aggregate improvement
exceeds the required 20%. At individual points, discrepancies remain large:
only 43% of component predictions lie inside reported observation error bars.
Those bars are not full prediction intervals, and correlated composition,
uptake and calibration errors preclude an independent-binomial interpretation.

CO2 signed biases are +0.343, +0.301 and +0.181 mmol/g; CH4 biases are
-0.235, -0.130 and -0.020. Their partial cancellation makes total loading
look better than either component in some conditions; component MAE remains
the primary score. Every composition-sweep score and row residual is retained
in `result.json`.

![All primary component forecasts against the same mixture measurements](../results/adsorption-transfer-2026-10-13/adsorption.png)

Blue circles show shared capacity, orange open squares IAST, and gray crosses
the no-competition ablation. The diagonal denotes exact prediction. Horizontal
bars are reported expanded observation uncertainties, drawn once at the shared
forecast; their dependence is not represented by independent error bars.

## Calibration and coverage limitations

Effective common capacities are 7.891, 7.417 and 7.129 mmol/g. Separate pure
CO2 capacities are almost unchanged, whereas separate CH4 capacities are
5.969, 6.208 and 6.338. Thus this result does not establish temperature-invariant
physical sites or identical molecular footprints. The source's common cage
volume motivates the shared resource, but its more detailed cage model is
not identical to Langmuir. Neither published mixture-fit parameters nor its
pure-model parameter tables were used here.

Pure normalized RMSEs range from 0.82% to 4.29% of the corresponding maxima,
meeting the declared 5% engineering gate. Weighted residual sums nevertheless
show substantial discrepancy relative to the reported measurement errors.
The declared capacity-profile gate is numerical sensitivity, not a confidence
interval. Calibration adequacy at that tolerance should not be described as
metrologically exact fitting.

The frozen prediction artifact flags **29 upper IAST standard-state
extrapolations** (all CH4); the largest hypothetical pure fugacity is 115.7
times the largest measured pure fugacity. A separately labelled **post-response
coverage audit**, using only the sealed predictor arrays, additionally finds
12 mixture CO2 fugacities below pure calibration coverage and 11 lower IAST
standard-state extrapolations. At 298 K the lowest measured pure CO2 condition
already has fitted occupancy about 0.56; its dilute Henry region was not
measured. These lower-coverage counts were not frozen eligibility gates, and
no affected row is removed or refitted. Extrapolation relies on the chosen
pure-isotherm functional form; it is not independent validation of that form.

The fully recalibrated ideal-gas sensitivity gives shared MAE 0.26401,
ablation 0.63130 and IAST 0.25912 mmol/g. It also passes the engineering rule,
with 58.2% gain and 33/90 shared predictions within reported U. This checks
one convention, not all possible gas or adsorbed-phase nonidealities.

## Scientific contribution and next discrimination

This adds a real chemical intervention to the framework: calibration from
single species predicts how uptake changes when another species competes for
capacity. The advantage over omitting competition is substantial and remains
under the declared gas-phase sensitivity. Established IAST is equally useful
and slightly better on loading error. The test therefore demonstrates the
framework's constrained-allocation interpretation using known chemistry;
it does not establish a new prediction unavailable to adsorption theory.

To improve the scientific claim, another material or experiment should separate
shared interchangeable sites from heterogeneous cage filling using independent
low-coverage and saturation measurements. Alternatively, the next broader
natural-system study should force two independently specified resource models
to make different unused-response predictions. Adding examples that merely
recover established formulae would add less than that discrimination.

## Reproduce and verify

`make adsorption-transfer PY=build/main-venv-2026-10-09/bin/python
STUDY_OUTPUT_ROOT=build/UNUSED` verifies the source snapshots, replays forecasts
and evaluations in new directories, checks the committed forecast bytes, runs
independent verification and coverage audit, and regenerates the figure.
The original filenames retain the 13 October design date.

Independent code reparses sources, computes PR chemical potentials as numerical
derivatives of extensive residual Gibbs energy, eliminates capacity analytically
in pure fitting, solves IAST through adsorbed composition, and sums scores
separately. It verifies **3,294 numerical/logical entries**, with maximum scaled
difference 8.23e-8 and no discrepancies. This certifies numerical reproduction,
not the source metrology or the physical assumptions.
