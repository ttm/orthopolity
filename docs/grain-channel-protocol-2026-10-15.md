# Narrow-to-wide sediment transport: frozen transfer protocol

15 October 2026. Commit this protocol, code, configuration, source receipts,
predictor audit and synthetic tests **before fitting old sediment responses**.
Commit all resulting forecasts before evaluating the nine wider-channel
responses. This is retrospective: published qualitative results and fitted
wide-cohort constants are known. An accidental metadata read exposed the first
wide sphere target (S1 row 2, `gb_5_01`, 0.0115909333333333 kg/s). Retain all
nine predetermined targets; only eight are numerically withheld. Neither the
published wide-fitted constants nor that exposed value enters calibration.

## Question, physical statement and reference measure

Can independently measured grain properties and hydraulic geometry transfer a
bed-load transport relation from a narrow channel to a wider one? In particular,
does the shape correction improve forecasts beyond the hydraulic correction?
The established constitutive relation is

$$q^*=A[ F_{\rm shape}F_{\rm wall}HS/(r_fD)-t]_+^{3/2},
\qquad q^*=\dot m/[\rho_sW\sqrt{g r_fD^3}],\quad r_f=\rho_s/\rho_f-1.$$

The throughput model needs both a stress-partition rule and a grain response;
momentum conservation alone supplies neither. Boundary force conservation is
an exact accounting constraint. It does not prove uniform boundary stress.
Reference measure for calibration/evaluation: equal weight per included grain
cohort, then per run. This is **neither log-orthopolic nor linear-orthopolic size
allocation**; there is no measured abundance distribution over grain sizes.
An advantage would support a bounded, established constraint-transfer model,
not establish universal neutral allocation or novelty over sediment mechanics.

## Sources and fixed cohort

Use [Deal et al. 2026](https://doi.org/10.1029/2025JF008712) and the
[FRDR archive](https://doi.org/10.20383/103.01325), CC BY 4.0, retained under
`data/grain-channel/2026-10-15/`. Check local SHA-256 and the repository's
publisher checksums. The archive also supplies the original
[Deal et al. 2023](https://doi.org/10.1038/s41586-022-05564-6) measurements.
The [independent design review](grain-channel-design-review-2026-10-15.md)
records the competing interpretation and limited identifying power.

Take the published S3 narrow sphere/gravel cohort, not a new response-selected
subset. Of 20 sphere and 12 gravel rows, three lack Q: `gb_s1_e4`, `ng_s2_e2`,
`ng_s3_e3`. Exclude these from every model based on predictors alone; no
imputation. Primary calibration is the remaining **19 spheres**. Sensitivity
calibration pools those with **10 narrow gravel runs**, material-balanced.
All **four wide sphere and five wide gravel runs** are targets. Match S3 to
raw source identities by H, S, Q and grain type, requiring uniqueness; never
match by flux. The publication's prior cohort selection remains inherited.

## Qualified conventions

- Width is 0.0105 m narrow, **0.065 m wide**. Both original wide measurement
  class constructors, the main processing code, S1/S3 and the article agree.
  The README's 5-cm description and run names conflict and are treated as stale
  labels, not an alternative silently selected by prediction performance.
- H and water-surface gradient S come from ruler measurements; Q is water
  discharge. Narrow source discharge is L/s despite the broad SI description;
  divide by 1,000. Wide Q is the common independent pump calibration mean
  of 3.07480994, 2.76582836 and 2.68489553 L/s, not nine independent flow assays.
- Density is the separate grain assay; fluid density is 995 kg/m3 for these
  runs. Use g=9.81 m/s2, nu=1e-6 m2/s and kappa=0.41. The standalone grain
  calculator's 990-kg/m3 convention is not substituted into flume buoyancy.
- **D is the archived volume-equivalent sphere diameter**, as in the actual
  source pipeline. Paper prose describes D50; do not claim that these are
  separate median-diameter measurements. Guo roughness uses ks=2D. This is a
  fixed roughness approximation, not a measured wall/bed stress partition.
- For shape, use separately measured Corey factor, settling velocity and
  repose angle, plus archived theoretical equivalent-sphere settling speed:
  C*=CSF (w0/ws)^2; mu*=(tan(repose)-Sbed)/(tan(24 degrees)-Sbed).
  The source theoretical w0 is a fixed model input, not a settling observation
  or a quantity inferred from sediment flux. Use the **per-run measured bed
  gradient**, not the publication pipeline's common 3.5/1.26-degree slopes.
  This deliberate pre-fit implementation follows the physical slope formula;
  it is a transfer test, not exact replication of the published figure.
- Guo is Equation 13; hydraulic-radius factor is R/H. Vanoni–Brooks is retained
  as a predictor diagnostic, not another primary model. For negative Guo
  radicands record the real part of the full complex expression as the source
  does, but **stop physical qualification**. Require radicand >=0 and R/H<=FG<=1
  for all included runs. All 38 included rows satisfy this before response fits.
- Read measured **mass_flux**, not feed flux. Convert mass to volume using
  sediment density and the same D/W convention in both cohorts. Do not use
  precomputed q8, flux-inferred stress, Fqs or source fitted coefficients.
  Wide raw q8 used rounded grain diameter/density; rebuilding from measured
  mass prevents mixing that normalization with the precise assay predictors.

Water depth and equilibrium bed slope are measured state variables, not both
externally controlled interventions. This is a conditional equilibrium forecast,
not a claim that forcing, geometry and sediment feedback are causally separable.

## Fits, benchmarks and software qualification

Fit A>=0 and 0<=t<=max(calibration stress) separately for every candidate to
the same allowed calibration observations. Minimize material-balanced squared
dimensionless-flux residuals. Profile A exactly at each t; search 33 nodes in
every active-set interval and refine every local grid minimum with bounded
scalar optimization, retaining all boundaries. Record active count, threshold
boundary, SSE and profile changes at +/-1% of the calibration stress range.
An independent two-parameter optimizer must verify the optimum and forecasts;
materially different equal-score solutions preclude a unique-transfer claim.

Four candidates receive their own calibration fits: **Guo+shape**, **Guo+unity**,
**hydraulic-radius+shape**, and **depth-slope+shape** (no wall correction).
Additionally fit Guo+unity separately to old spheres and old gravel, carrying
those two material labels to the corresponding wide targets. This benchmark
has four parameters and no new-cohort adjustment. All fits and all individual
forecasts remain in the record regardless of performance. Flag extrapolation
before outcomes. No parameter retuning, outlier removal or model substitution.

Before real fitting, verify noiseless recovery with zero/positive thresholds,
scaling/order invariance, momentum accounting, the complex-domain convention,
drag-ratio algebra, material weights and source-reader response isolation by
poisoning response/derived-stress columns. These software checks do not assert
statistical power for nine correlated runs.

## Evaluation and interpretation

Primary score: average of sphere MAE and gravel MAE in dimensionless flux.
Also retain each physical mass-flux error, cohort bias, per-cohort MAE and
every alternative's score. Normalize both cohort MAEs by the **largest old
sphere flux**, fixed during calibration and sealed with forecasts.

Pragmatic accuracy requires primary calibration RMSE and both target-cohort
MAEs <=20% of that normalization, and at least three active calibration points.
Declare **shape advantage** only with accuracy and >=20% lower balanced MAE
than separately calibrated Guo+unity. Declare **geometry advantage** separately
with accuracy and >=20% lower MAE than hydraulic-radius+shape. These are openly
chosen engineering tolerances, not source precision, significance thresholds,
or proof of a general law. Report continuous scores even if the gates fail.
Compare the material-label benchmark honestly; improvement over depth-slope
alone cannot be called evidence for shape.

No confidence intervals or population-level significance claims: grain-batch
errors, pump calibration and repeated conditions are shared. Assay and
hydraulic uncertainty is not propagated here, so small model rankings cannot
establish mechanism identification or robustness. This finite-cohort check
must earn a later uncertainty/independent-data extension; it cannot use its own
responses to choose the next model and call that confirmation. Known criticism
of the composite grain factor and competing wall corrections remain relevant
regardless of the outcome.

## Reproduce

Use the repository Python 3.11 environment, `PYTHONPATH=src` and
`MPLCONFIGDIR=build/matplotlib`. Run `audit_grain_channel.py --stage verify`
and `python -m unittest discover -s tests -p test_grain_channel.py`; commit design. Then run
`run_grain_channel.py --stage predict --freeze-commit DESIGN --output NEW`,
commit forecasts, and run `--stage evaluate --freeze-commit DESIGN
--prediction-commit FORECAST --predictions PATH --output NEW`. Independently
verify, update status and preserve the source/confounding qualifications.
