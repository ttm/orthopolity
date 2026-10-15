# Narrow-to-wide channel transfer: measured constraints help, with large errors

15 October 2026. The frozen comparison passes its two **relative-improvement**
rules and its permissive engineering accuracy rule. It does not establish
precise prediction, superiority over a material-specific calibration, or neutral
allocation. Reference measure is equal weight per sphere/gravel cohort, then
per run; neither log-orthopolic nor linear-orthopolic size allocation is tested.

## Chronology and inputs

The [protocol](grain-channel-protocol-2026-10-15.md), data receipts,
predictor-only audit, code and synthetic checks were committed at
`290acd9a9c37b630510b3d2177202e8b80827b5a` before old-response fitting.
Forecasts and their independent numerical verification were sealed at
`e86cffc` before evaluating the nine wide-channel responses. The forecast SHA-256
is `9d42556fb06a48787536d72125c8c13567d9940a0dbb1e2b43891209817ea49e`.
Published qualitative outcomes and wide-fitted constants were already known;
the constants were not used. One numerical target was accidentally displayed
during metadata inspection. The protocol calls it `gb_5_01`; the raw summary
spells the same S1-row-2 identity `gb_5_1`. No row was removed for this exposure.
Eight of nine target numbers were withheld before evaluation. This is an
archival, locally frozen transfer, not a blind or externally registered test.

The [FRDR source](https://doi.org/10.20383/103.01325) supplies old narrow and new
wide flume experiments and separate grain assays. Thirty retained originals
are checked against local SHA-256; 29 also match publisher digests, excluding
the checksum file itself. Missing water discharge removes three of the source's
32 old sphere/gravel rows, leaving 19 spheres for primary calibration and ten
gravel runs for sensitivity/benchmark calibration. All nine new runs qualify.

Width 0.065 m is supported by both original measurement programs, processing
code, tables and [Deal et al. 2026](https://doi.org/10.1029/2025JF008712), despite
5-cm README labels. Volume-equivalent diameter, independently measured repose,
settling and shape, archived theoretical sphere-settling speed, per-run bed
slope and the common pump calibration are explicit. Guo wall factors are
physical for all 38 included runs. Source-normalized flux and flux-inferred
stress are not used: measured mass flux is converted consistently using grain
density, width and diameter. The primary corrected stresses of all nine targets
lie within old sphere calibration support.

## Sealed prediction and outcomes

Each model fits its own nonnegative amplitude and motion threshold on old
data, with exponent 3/2 fixed. No wider-channel coefficient is fitted.

| Primary calibration: 19 narrow spheres | Sphere MAE | Gravel MAE | Balanced MAE |
|---|---:|---:|---:|
| Guo wall correction + measured shape | 0.05547 | 0.03955 | **0.04751** |
| Guo wall correction, unit shape factor | 0.05406 | 0.11161 | 0.08283 |
| Hydraulic radius + measured shape | 0.20637 | 0.21081 | 0.20859 |
| Depth-slope stress + measured shape | 0.06675 | 0.07102 | 0.06888 |

All errors are in dimensionless volume flux. The full model reduces balanced
MAE **42.64%** relative to unit shape and **77.22%** relative to hydraulic
radius, passing the separately declared 20% improvement rules. Its gain over
depth-slope stress is 31.02%. The depth-slope model extrapolates below its fitted
threshold and predicts zero for every target; this is retained, not repaired.
Shape slightly worsens sphere error and strongly improves gravel error, as the
cohort-specific scores show.

The primary fit has A=8.9361, t=0.066445, 19 active calibration runs, and RMSE
0.09964 (8.61% of maximum old sphere flux). No real fitting choices changed
after target evaluation. Primary sphere/gravel physical MAEs are respectively
0.01259 and 0.00639 kg/s.

![Sealed primary predictions and competing old-data fits](../results/grain-channel-transfer-2026-10-15/transfer.png)

The old-material-label benchmark fits Guo without shape separately to old
spheres and old gravel. Its MAE is **0.04297**, 9.56% below the full primary
model, using four fitted parameters rather than two. Pooling all 29 old runs
gives full-model MAE **0.03478**, versus 0.04326 for unit shape: a 19.61% gain,
slightly below the primary design's 20% margin if that same margin were applied
to the sensitivity. These results prevent a claim that measured properties
uniquely identify the mechanism or outperform every calibration alternative.

## Why the accuracy pass is weak

The frozen error tolerance is 20% of the largest old sphere flux, 1.15776.
That permits MAE up to **0.23155**, which exceeds the largest wide observation,
0.18134. Therefore even the zero-forecast rival has target errors below that
accuracy tolerance. The full model's 4.79% and 3.42% normalized cohort MAEs pass
the declared rule, but that rule is permissive in this lower-flux target range.
Do not describe this as measurement-precision agreement or quietly replace the
criterion after seeing outcomes.

For scale, primary MAE is **83.11% of the wide sphere mean** and **55.69% of
the wide gravel mean**. All four sphere targets are overpredicted. The lowest
sphere and gravel fluxes are overpredicted by factors **4.43 and 4.09**. These
post-evaluation descriptive ratios reveal limitations hidden by the old-maximum
normalization; they are not replacement decision rules.

The nine runs share grain batches, water-flow calibration and experimental
conditions. Input errors are not propagated, no population confidence interval
is claimed, and a small model ranking is not uncertainty-qualified. Repose is
a proxy for bulk resistance; settling drag and theoretical sphere drag do not
independently identify every grain-scale mechanism. The
[Chen, Durán and Pähtz critique](https://doi.org/10.5194/esurf-14-75-2026) and
[alternative geometry/shape treatment](https://doi.org/10.1017/jfm.2026.11928)
remain relevant. The present comparison does not adjudicate every competing
sediment theory.

## Verification, reproducibility and scientific value

Independent real-algebra Guo calculation, root-solving for the wall-friction
diagnostic, force-balance drag coefficients, multi-start two-parameter fitting
and separate scoring verify **2,467 quantities**, maximum relative difference
1.93e-8. Forecast-only verification checked 1,797 quantities before target
evaluation. Near-optimal solutions differ in predicted flux by at most 1.54e-8
of the relevant calibration maximum; numerical fit nonuniqueness does not
explain the reported model differences. These are numerical checks, not error
bars for the physical model.

Run `make grain-channel-transfer PY=build/main-venv-2026-10-09/bin/python
STUDY_OUTPUT_ROOT=build/reproductions/NEW` with `MPLCONFIGDIR=build/matplotlib`.
The target rebuilds predictions, evaluation, verification and figure from the
retained originals and compares their bytes. The prior registry entries remain
unchanged; the transfer is recorded as actual measurement with explicit limits.

This adds a concrete example of **independently specified constraints improving
a changed-geometry forecast**, while identifying low-flux failures and a weak
success tolerance. It adds no new sediment law and no direct evidence for
uniform resource allocation across sizes. The useful next extension is to
freeze shared-input uncertainty and a target-relevant tolerance on a separate
cohort; reusing these nine values to choose those settings would be exploratory.
