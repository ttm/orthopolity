# Availability amendment before thermal target release

26 October 2026. The original [protocol](hotbox-transfer-protocol-2026-10-26.md)
and implementation were committed and pushed as **69deda5** before numerical
access. Its forecast command stopped at the nonfinite-value gate, with no
forecast file or target interior release. This is retained as **failure of
the original 15-position qualification**, not counted as a passing study.

An input-only diagnostic found that sensor **8_f** contains 181 nonfinite
values in both the case-6 calibration and case-7 control. All other permitted
calibration/control c..g and target c/g input cells are finite. All seven
clocks run from 60 to 10,860 seconds in 60-second steps. The diagnostic did
not decode any target d/e/f values; the missingness decision is independent
of their performance. The [availability receipt](../results/hotbox-qualification-2026-10-26/availability.json)
records the separate check.

The amended study excludes **position 8 as a whole**, across calibration,
control and every target case. This preserves the complete five-sensor
monotonic-profile condition at each retained position and avoids imputing
the missing calibration or replacing it with another forcing. It is a
restricted cohort, not an evaluation of all 15 positions. Keep original
position identifiers: 1–7 and 9–15. No spatial remapping is permitted.

This amendment supersedes only the original cohort and corresponding counts:
14 positions, 280 permitted input summaries (50,680 temperature cells),
**210 target means** (38,010 target temperature cells). The seven clocks,
three-hour averaging, models, comparisons, accuracy scenario, geometry
sensitivities, range/drift rules, missing-data stop rule and interpretation
remain unchanged. Any additional missingness in the revised selected inputs
or later targets stops that stage. There is no iterative exclusion of failed
forecasts or unqualified results.

Freeze and push this amendment, configuration, runner, verifier and synthetic
tests before rerunning the input stage. Then independently verify and commit
the 210 numerical forecasts before releasing their targets. The original
protocol remains unchanged in the repository as well as in git history.
This is an openly amended retrospective study with locally withheld outcomes;
it is not external preregistration. The reference coordinate remains physical
depth/thermal resistance, neither log-orthopolic nor linear-orthopolic size
allocation.

## Verification repair, still before target interior release

The amended design was pushed as **631402e**. Its input stage produced all
210 forecasts, and independent source extraction agreed within 1.43e−14°C.
The arithmetic verifier then rejected constant-series means lying up to
1.43e−14°C outside their identical minimum and maximum because of floating-point
summation. The verifier now allows 1e−10°C solely for that numerical range check;
a synthetic check retains rejection of a substantive mismatch. No physical
error allowance, qualification threshold, coefficient or forecast calculation
changes. Re-freeze the verifier and rerun the same inputs before target release.

Input inspection also shows constant c/g sequences in case 4 and one input far
outside the stated calibration range. These remain in the fixed cohort and are
flagged; flat archived sequences cannot independently establish equilibration.
No target interior values have been decoded in diagnosing this verifier issue.
