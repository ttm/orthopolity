# Frozen thermal-profile transfer using public wall experiments

26 October 2026. **Design before numerical calibration and target access.**
The author requests existing public data only; no new laboratory experiment is
assumed. The [retained archive](storage-source-audit-2026-10-25.md) supplies seven
steady wall experiments. This study asks whether a temperature profile learned
at the smallest nonzero forcing predicts five stronger-forcing profiles.

It tests a specified transport representation and its boundary. It is not a
closed resource-allocation intervention, a new discovery of convection, or unique
evidence for the general law. The reference coordinate is physical depth or
calibrated thermal resistance, **neither log-orthopolic nor linear-orthopolic size
allocation**. Temperature is an intensive variable; these measurements alone do
not establish uniform heat throughput or measure a complete energy budget.

## Sources and prior exposure

- Veit and Johra's [public dataset](https://doi.org/10.5281/zenodo.8204755), CC BY
  4.0, is retained unchanged with SHA-256
  `d1e706a46be13d4aca2c220ce979e3e1da94d6245d349b6100d1aa4c1d769ad0`.
- [Report 317](https://doi.org/10.54337/aau544775163), pp. 13–14, maps the sensors
  and experimental conditions; [report 304](https://doi.org/10.54337/aau488363266),
  pp. 23–24, describes calibration. Their retained acquisition receipt records
  PDF URLs and hashes. No redistribution of those PDFs is required.
- The [later primary article](https://doi.org/10.1016/j.enbuild.2025.116646)
  already reports convection and increased heat transfer. These conclusions,
  including the aggregate increase up to 90%, are exposed. Numerical temperature
  arrays and experimental temperature plots have not been inspected locally.

Earlier schema work tokenized CSV cells without numerical conversion. This is
local withholding of archived outcomes, not external blinding or external
preregistration. Freeze and push this design and implementation before opening
calibration numbers; freeze and push actual forecasts before target release.

## Fixed split and observation model

Use all 15 measured wall positions and all 181 one-minute readings in each
steady file. Report the arithmetic three-hour mean per sensor; these are not
181 independent replicates. Use internal insulation sensors c and g as anchors,
and d, e, f as held-out interior sensors. Their nominal depths from the hot
surface are (0.069, 0.125, 0.182, 0.239, 0.296) m. Restricting the interval to
insulation avoids treating the unequal OSB layers as the same material.

- Calibration: case 6, nominal hot/cold temperatures 20/0°C.
- Targets: cases 1–5, nominal temperatures 30/−20, 20/−25, 20/−20,
  20/−15, 20/−10°C. Read their c/g anchors before forecasting; keep d/e/f shut.
- Unfit control: case 7, nominal 20/20°C, c through g. Report local differences
  without estimating or subtracting sensor offsets from them. Chamber setpoints
  do not prove that the wall itself is exactly isothermal.
- Do not decode the four dynamic files or steady sensors a, b, h, i.

The forecast stage converts 54,300 permitted temperature cells and seven clocks;
the release adds 40,725 target cells, summarized to **225 target means**. No
missing-value imputation, spatial selection, outlier deletion or post-release
parameter fitting is permitted. Schema, nonfinite selected values or nonuniform
60-second spacing stop the numerical pipeline rather than silently adapting it.

## Predictions and informative competitors

Write C and G for the mean c/g readings, M for an interior reading, and index
the calibration experiment by 6. Define a cold-to-hot resistance fraction

$$\widehat\beta_{pj}=(M_{pj6}-G_{p6})/(C_{p6}-G_{p6}).$$

The primary forecast is

$$\widehat M_{pjs}=G_{ps}+\widehat\beta_{pj}(C_{ps}-G_{ps}).$$

Steady, source-free, one-dimensional conduction with fixed positive conductivity
k(x) gives this form: temperature drop is proportional to the integral of 1/k
along the path. The fraction is independent of forcing even when k varies with
depth. A common scalar multiplier of conductivity between experiments also
cancels. Thus this tests invariance of the *normalized resistance profile*, not
constancy of total conductivity, total heat flux or the absence of convection.
Temperature-dependent shape, lateral transport, evolving material state, sensor
offsets or incomplete equilibration can change the profile. No residual uniquely
identifies any of them.

Freeze three comparisons using the same inputs:

1. Homogeneous conduction: beta_geo=(x_g−x_j)/(x_g−x_c).
2. Fixed additive correction: geometric forecast plus the case-6 geometric
   residual. This and the primary forecast reproduce calibration exactly;
   the primary scales that residual with forcing while this rival retains it.
3. Persistence: the case-6 interior temperature itself.

Retain nominal ratio estimates without clipping, even if error-compatible
temperatures could be monotone while the nominal means are not. Such point
forecasts are descriptive and need not be a physical resistance fit. One
calibration forcing cannot identify both a true resistance fraction and a
fixed sensor offset. The comparison and bounded scenario expose that ambiguity.

## Conditional uncertainty and qualification

Use epsilon=0.15°C as a *conditional simultaneous bounded-error scenario*,
motivated by report 317's accuracy statement. It is not measured joint coverage,
a standard error, a confidence interval or a Gaussian noise model. Means retain
the full allowance; correlated systematic errors do not shrink with 181 samples.
The [JCGM guide](https://doi.org/10.59161/JCGM100-2008E), sections 5.2 and F.1.2,
discusses common-instrument correlations. Our interval calculation assumes no
independence and is distinct from its probabilistic uncertainty propagation.

Report 304 calibrates internal/hot sensors over −10 to 50°C, whereas report 317
states a blanket accuracy. A profile is range-qualified only when every used
reading's ±epsilon interval is inside −10 to 50°C, both in calibration and in
that target. Keep all outside-range results as unqualified diagnostics.

Require absolute difference between the last 60 and first 60 reading means
at most 0.30°C for every c..g sensor in calibration and that target. This is
a frozen drift diagnostic, not proof of equilibration. The source's criterion
compares with a preceding three-hour window which is not provided. Never use
agreement with the forecast as a stationarity or selection criterion.

Calibration must have C6−G6>2epsilon; otherwise stop before target interior release. Check joint
existence of latent temperatures C≥D≥E≥F≥G in their five ±epsilon intervals.
Descending greedy selection from upper bounds is exact for this condition.
If infeasible, retain nominal forecasts, mark calibration unqualified and give
no physical transfer interval for that position; do not choose another case.

For each physically feasible calibration, enumerate all eight combinations of
C6, G6, M6 errors at ±epsilon. Their ratio extrema enclose beta. Intersect
with [0,1]. Enumerate those beta endpoints and target anchor error endpoints
to bound the true predicted temperature; expand by epsilon for target
observation error. These are conservative *marginal* envelopes: their extrema
need not be jointly attainable across sensors or cases. An outside-envelope
observation contradicts the conditional scenario; every point inside only
means **not excluded by marginal bounds**, not joint model confirmation.

The homogeneous geometric forecast has sensor-only residual bound 2epsilon=
0.30°C. Report separately placement scenarios δ=0.5, 1 and 5 mm for each depth,
using the extra allowance 2δ|C−G|/0.227. The coordinate table's millimetre
rounding is not evidence of installation accuracy. Report the necessary
allowance δ_required=0.227 max(|residual|−0.30,0)/(2|C−G|) when C differs from G.
These sensitivities do not fix temperature-dependent conductivity or lateral
transport; none is presented as independently measured placement uncertainty.

## Scores, outcomes and interpretation

Report all 225 point residuals and qualification flags, MAE and maximum absolute
error for each model, overall and separately for each of the five experiments.
Equal weight per target mean gives equal weight to each experiment. Do not
pool signed residuals that can cancel across heights. Positions 1–3, 4–6,
7–9, 10–12, 13–15 are the five horizontal rows; any row summary is descriptive,
not a whole-wall area-weighted estimate. No p-value or independent-replicate
confidence interval is claimed from the spatial or temporal observations.

The overall outcome is qualification incomplete if any profile fails a range,
drift or calibration gate. Otherwise it is a conditional transfer departure
if any target is outside its frozen marginal envelope, and not excluded by
marginal bounds otherwise. Always report outside-envelope counts both among
all available envelopes and among qualified profiles, without changing the
cohort or erasing unqualified failures. An MAE gain over geometric interpolation
is descriptive; also report the fixed-additive rival, even if it wins.

The no-gradient control is unfit: report c..g spread and geometric residuals
with the same error allowance, but do not use it to rescue or correct targets.
A failure challenges this specified representation and observation scenario;
it neither rejects all conduction nor establishes a new allocation mechanism.
An accurate transfer demonstrates this conditional prediction, shared with
established heat-transport theory, rather than unique general-law evidence.

## Reproduction and release

Run synthetic tests before calibration. Commit and push the protocol, config,
runner, independent verifier and tests. Then run:

```sh
PYTHONPATH=src build/main-venv-2026-10-09/bin/python experiments/run_hotbox_transfer.py \
  --stage forecast --design-commit DESIGN_COMMIT \
  --output results/hotbox-forecast-2026-10-26/predictions.json
build/main-venv-2026-10-09/bin/python experiments/verify_hotbox_transfer.py \
  --prediction results/hotbox-forecast-2026-10-26/predictions.json \
  --output results/hotbox-forecast-2026-10-26/verification.json
```

Review input qualification without reading targets. Commit and push the actual
forecasts and verification. Only then run `--stage evaluate` with the same
design commit, `--prediction`, a separate `--prediction-commit`, and an output
in `results/hotbox-transfer-2026-10-26/`. Independently audit released source
summaries and evaluation; retain all failed checks and qualifications in the
result note. Forecast and result replay must reproduce committed bytes.
