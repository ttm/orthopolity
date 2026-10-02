# Frozen forecasts for NOAA solar flares in 2025

This study fixes resource-cost forecasts and a full-profile assessment before
this analysis acquires or inspects NOAA's 2025 event bytes. Development uses
the already inspected 2022–2024 snapshots. The 2025 catalogue describes already
measured public observations: a local forecast freeze does not make this
prospective observation, external preregistration, or independently verified
global blinding.

The complete conditional count and measured resource profiles are the targets.
The sampling assumptions required for a formal neutrality verdict are not
established in this observational design. That application gate is fixed before
acquisition, so the formal verdict remains **unresolved** regardless of the
conditional candidate band or point estimate. Frozen forecasts can still be
scored and their transfer limitations measured.

## Fixed measurements, domain and costs

The coordinate is unsaturated finite positive peak XRS irradiance in W/m² in
the original closed interval $[10^{-5},10^{-3}]$. The primary resource is supplied
start-to-peak integrated XRS-B irradiance in J/m². Supplied start-to-end
fluence is a separate sensitivity. Neither is total radiated flare energy.
No extra background subtraction, detection-completeness correction, exposure
correction, declustering or overlap correction is applied.

Resource-specific complete cases require finite positive fluence and a positive
corresponding event-window duration. All source rows and exclusions are retained
in membership manifests. End-fluence missingness is reported independently.
If primary fluence is missing among eligible peak events, the complete-case
resource profile cannot establish a catalogue-wide statement.

Eight fine quarter-decade bins are initially specified. Starting from the upper
edge, neighboring bins are merged downward until each pooled class has at least
20 complete development events for both resources. Any undersupported lowest
remainder merges into its neighbor. Pooling depends only on 2022–2024 support,
keeps the outer domain, and preserves actual logarithmic and linear widths.
No pooling, cutoff change, smoothing or exclusion is chosen from 2025 outcomes.

The development support yields six classes. The first five span quarter decades;
the last spans three quarter decades. Development rise/end counts in the eight
fine classes are [820, 323, 199, 95, 43, 17, 7, 5] and
[728, 288, 181, 89, 42, 17, 7, 5]. The last three fine classes are pooled.

For arithmetic mean development cost $\bar q_j$, the frozen forecasts are

$$p_j^{\log}\propto\Delta\log k_j/\bar q_j,\qquad
p_j^{\mathrm{linear}}\propto\Delta k_j/\bar q_j,\qquad
p_j^{\mathrm{history}}=N_j^{\mathrm{dev}}/\sum_l N_l^{\mathrm{dev}}.$$

Each count-share vector sums to one. The neutral forecasts learn measured costs
without fitting abundance. Historical counts are an explicit competing model.
Predicted resource shares are $p_j\bar q_j/\sum_l p_l\bar q_l$. The forecast
conditions on the eligible 2025 event total; it predicts neither the annual
event rate nor total fluence. No power-law resource-cost curve is assumed.

## Fixed margin and application gate

The profile is

$$\phi_j=\frac{\sum_{i\in j}q_i/\sum_iq_i}
{\Delta\log k_j/\sum_l\Delta\log k_l},\qquad
\Delta=\max_j|\log\phi_j|.$$

The exploratory operational margin is **$F=1.5$**, fixed before acquisition.
Approximate neutrality requires every class to have $2/3\le\phi_j\le1.5$, or
$\Delta\le\log1.5$. This allows a sustained 50% excess or 33% deficit as the
boundary of the declared coarse approximation. It is a transparent practical
choice, not a margin derived from instrument accuracy, an established natural
law, or the unseen evaluation outcomes. Any future scientific application
should justify its own margin independently.

The candidate method is a centered-bootstrap simultaneous band for the complete
log profile, with 499 bootstrap resamples to match its simulation calibration.
The candidate benchmark is completed and retained before the solar freeze.
Twelve validation calendar months provide resource-total vectors across all
six classes. Potentially seasonal, serially dependent months and heavy-tailed
fluence do not automatically satisfy the method's assumptions. Development
diagnostics report month support, the largest monthly contribution per class
and year-to-year variation; they do not prove exchangeability.

The application gate independently records that independent exchangeable
validation months and a defensible physical bound on monthly resource totals
are unavailable. An observed maximum is not a physical upper bound. Simulation
success cannot establish sampling assumptions for the solar catalogue.
Therefore conditional candidate labels are reported with the formal verdict
unresolved, rather than being promoted into a calibrated observational test.
Empty evaluation resource classes remain empty and prevent a finite log-profile
band. No class is dropped to obtain a verdict.

## Forecast scores and uncertainty

Count cross entropy and total variation compare complete predicted and observed
count-share vectors. Resource-share TV compares observed fluence fractions with
the frozen resource forecast. A positive TV interval is not a neutrality-null
test; empirical distances are positive from sampling variation even under
equality, and ordinary resampling does not generate the neutral null.

Four thousand score bootstrap draws independently resample 12 complete
calendar-month vectors within each development year and within the evaluation
year. The same draws are shared across forecasts and resource definitions.
The paired historical-minus-log-neutral count cross-entropy difference assesses
forecast ranking. Unsupported development cost draws are recorded as invalid,
rather than smoothed or dropping their classes. Intervals are explicitly
conditional nominal summaries, separate from the application-gated neutrality
verdict. Measured mean-cost transfer by class is a separate endpoint.

## Freeze, acquisition and reproducibility

The [configuration](../configs/solar_validation_2026-10-02.json),
[module](../src/orthopolity/solar_validation.py) and
[driver](../experiments/run_solar_validation.py) implement distinct `freeze`,
`acquire` and `analyse` stages. The freeze saves all forecasts, development
summaries, fixed widths/margin, candidate benchmark references, the solar
application gate, exact source/configuration digests and byte copies. It fails
if validation bytes already exist in the new run directory. Acquisition is
an explicit later step and refuses changed frozen sources or inputs.

The source is NOAA's
[annual 2025 v1-0-1 report](https://data.ngdc.noaa.gov/platforms/solar-space-observing-satellites/goes/multi/l2/data/xrsf-l2-flrpt_science/csv/sci_xrsf-l2-flrpt_geo_y2025_v1-0-1.csv).
Only its directory listing was seen before the freeze. Downloaded event bytes,
SHA-256, access UTC, response headers, redirect information and failed attempts
are retained under `data/solar-validation/2026-10-02/`. This new snapshot never
replaces historical inputs or their checksum catalogue.

Replaying `analyse` uses the retained 2025 file entirely offline and verifies
saved artifacts. Replaying `acquire` after a matching receipt performs no
download. Different sources, configurations or outcomes require another run.
The tests cover pre-acquisition freeze enforcement, source-byte guards,
archived sources, failure logs, acquisition replay, missingness, zero-bin JSON
and nonpromotion of an ineligible conditional verdict.

The completed benchmark is retained in
[study.json](../results/profile-calibration/study.json). The
[solar freeze](../data/solar-validation/2026-10-02/frozen-plan.json), saved at
2026-10-02 08:55:48 UTC, has SHA-256
`9c9a5954214a03a877cf97d3f0f8f4b87d21301affc44ce4271dc4c271ac6795`.
Development contains 1,509 primary and 1,357 end-fluence complete cases.
The freeze and implementation can be verified without acquiring validation data:

~~~bash
PYTHONPATH=src MPLCONFIGDIR=build/matplotlib python3.11 \
  experiments/run_solar_validation.py --stage freeze \
  --benchmark-gate results/profile-calibration/study.json \
  --benchmark-study results/profile-calibration/study.json
PYTHONPATH=src MPLCONFIGDIR=build/matplotlib python3.11 \
  -m unittest discover -s tests -p test_solar_validation.py
~~~

Results will be added after the approved acquisition and analysis. Until then
this report records the fixed protocol rather than evaluation findings.
