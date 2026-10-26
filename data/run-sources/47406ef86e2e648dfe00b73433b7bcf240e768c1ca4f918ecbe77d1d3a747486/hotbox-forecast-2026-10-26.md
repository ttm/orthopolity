# Thermal forecasts sealed before interior release

26 October 2026. The original all-position design **69deda5** stopped at missing
calibration/control sensor 8_f. The [availability amendment](hotbox-transfer-amendment-2026-10-26.md)
was pushed as **631402e**, followed by numerical verifier repair **a18fbec**.
The latter is the operative design commit. No target interior temperatures have
been numerically decoded at this stage.

The [forecast](../results/hotbox-forecast-2026-10-26/predictions.json) contains
**210 target means**, four fixed point predictions each, and conditional
transfer/geometric observation envelopes. All 14 retained calibration profiles
pass joint monotonic feasibility. Nominal resistance fractions span
**0.201219–0.841417**. Every target has a transfer envelope, but only **174/210**
forecasts pass the input range/drift gates before target checking:

| Target case | Nominal temperature difference | Input-qualified means | Input range failures (positions) | Drift failures |
| --- | ---: | ---: | --- | --- |
| 1 | 50°C | 39/42 | 13 | none |
| 2 | 45°C | 30/42 | 12, 13, 14, 15 | 12 |
| 3 | 40°C | 24/42 | 10, 11, 12, 13, 14, 15 | none |
| 4 | 35°C | 39/42 | 12 | none |
| 5 | 30°C | 42/42 | none | none |

All 28 selected case-4 anchors are constant over their archived records.
Position 12's g reading is approximately −47.795°C, far outside the stated
internal calibration range. It is retained with its failed flag. Neither
constant records nor a passing drift screen establishes experimental
equilibration. No input-based replacement, correction or extra exclusion is made.

The unfit case-7 control has maximum c..g within-position mean spread
**0.160516°C** and maximum absolute geometric residual **0.091467°C**;
none of its 42 geometric residuals exceeds the conditional 0.30°C allowance.
Its absolute means range **21.0368–21.4057°C**, despite nominal chamber
setpoints of 20/20°C. No offsets are inferred or subtracted from the targets.

The independent rational/convexity verifier checks **2,975 numerical quantities**
and 636 logical conditions. Separate split-line source parsing checks
**50,680 permitted temperature cells and 1,267 clock cells**, with 2,120 numerical
summary/identity comparisons. Both maximum discrepancies are **1.43e−14**.
The roundoff repair changes no input summary, forecast, coefficient or envelope;
only the recorded design commit differs from the preceding draft forecast.

The complete-cohort verdict is already constrained to **qualification incomplete**
by input failures. Releasing the fixed target vector remains useful for the
predeclared descriptive model comparison and qualified-profile diagnostics.
It cannot turn this into a clean full-cohort confirmation. Physical depth and
thermal resistance are neither log-orthopolic nor linear-orthopolic size allocation.
