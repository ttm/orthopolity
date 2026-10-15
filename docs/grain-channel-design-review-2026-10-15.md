# Independent review: grain properties and channel-width transfer

15 October 2026. This review precedes fitting the old transport responses and
evaluating the new cohort. It recommends a bounded prediction design; it does
not set a success threshold or report a transport result.

## What this study can establish

The proposed forecast transfers a fixed bed-load relation from narrow-channel
experiments to wider-channel experiments, using hydraulic geometry and separate
grain assays. It asks whether measured constraints predict throughput under an
unused condition. The source is [Deal et al. (2026)](https://doi.org/10.1029/2025JF008712),
with its [public archive](https://doi.org/10.20383/103.01325), following
[Deal et al. (2023)](https://doi.org/10.1038/s41586-022-05564-6).

This is not a neutral size-allocation test. The evaluation measure gives equal
weight to the two declared grain cohorts and then equal weight to runs within
each cohort. Neither **log-orthopolic** allocation per d ln size nor
**linear-orthopolic** allocation per d size follows from that measure. A useful
result would concern transfer of an independently specified constraint model;
it would not establish universal neutrality or a new transport law.

## Calibration, provenance and exposure

Use old narrow-channel spheres for primary calibration. The source lists 20
sphere and 12 gravel experiments; missing water discharge leaves 19 spheres and
10 gravel with the required hydraulic predictors. This eligibility decision
uses missing predictors, not transport fit quality. The nine new targets are
four sphere and five gravel experiments. Wide spheres isolate width transfer;
wide gravel additionally tests the shape correction. A pooled 29-run calibration
is a sensitivity, with the explicit qualification that grain differences then
help determine its fitted transport constants.

The source audit resolves a width conflict before response fitting: the new
channel is 0.065 m wide, supported by S1, the paper, both raw-data class
constructors and the original processing pipeline. The raw archive README's
5-cm description is stale. The hydraulic audit reports positive, physically
admissible Guo factors for all 29 eligible old and nine new runs; no invalid
square-root cases were removed.

Published qualitative outcomes are already known. During the geometry audit,
S1 row 2's mass flux, 0.0115909333333333 kg/s, was accidentally displayed.
Retain that observation and disclose the exposure: eight of nine numerical
targets remain withheld. This is a retrospective, locally frozen prediction,
not a blind or externally preregistered study. Do not import constants fitted
to the new experiments, transport-inferred stress, or target-calibrated wall
corrections.

## Fair predictions and their interpretation

Fit the amplitude and nonnegative motion threshold on old responses only,
with the 3/2 exponent fixed. Guo plus measured shape is the proposed full model.
Guo with unit shape, hydraulic radius plus shape, and no wall correction plus
shape are separate rivals. Each must fit its own two parameters using the same
calibration rows, loss and bounds. Switching corrections off while retaining
the full model's parameters is only a diagnostic. A calibration-only model
with separate parameters for each grain type is a useful optional benchmark
for whether measured properties outperform material labels.

Physical forecast accuracy and incremental shape benefit are distinct claims.
A gain against no wall correction may come entirely from geometry. Accurate
forecasts with little separation from unit shape support transfer without
identifying a shape advantage. The [Chen, Durán and Pähtz critique](https://esurf.copernicus.org/articles/14/75/2026/)
specifically raises limited composite-factor variation and confounded drag
and friction changes in the earlier evidence. The present experiment should
therefore test the composite correction without claiming to identify its
constituent mechanisms separately.

## Qualification and scoring before target evaluation

Freeze diameter conventions, viscosity, density, gravity, slope definitions,
repose-angle conversion and roughness before fitting. Verify the drag ratio
independently using C_D/C_o = (w_o/w_s)^2. Check physical parameter bounds and
report corrected-stress extrapolation before evaluating target flux.

Use cohort-balanced absolute error in dimensionless flux as a primary score,
with separate cohort scores, all nine errors and physical-unit diagnostics.
Near-threshold relative errors should not determine the primary result. Fix a
practical accuracy margin independently of target errors; successful absolute
prediction need not imply a significant advantage over every rival.

A forecast uncertainty exercise can assess whether width corrections produce
distinguishable predictions after old-data calibration. It may use old
responses after the protocol freeze, but reads only predictors for the new
cohort. Perturb primitive measurements, refit calibration parameters, and propagate shared grain-batch
and hydraulic systematic errors jointly across runs. Check both absolute
forecast precision and between-model separation. Strong geometry separation
does not qualify a weak shape contrast. With nine targets and shared assays,
individual runs do not supply nine independent replications of shape physics.
Uncertainty scenarios and any qualification rule must be frozen before this
exercise, and its results cannot be used to tune a preferred verdict.

Commit the protocol and implementation before old-response fitting, then
commit numerical forecasts before evaluating the nine targets. Retain all
eligible targets and distinguish a physical forecast failure, an unresolved
comparison and a successful transfer in the final report.
