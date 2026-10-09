# Calibration, unused observations, and a dimensionality intervention

2 October 2026. This round follows the [three additional profile tests](additional-profile-tests.md).
Its purpose is to replace an exponent-only interpretation with decisions whose
sampling behavior is measured and predictions whose resource definitions are
fixed before the evaluation outcomes are inspected.

## Three distinct scientific questions

1. **Can the observation procedure distinguish practical neutrality from a
   material departure?** The [calibration benchmark](profile-calibration.md)
   evaluates complete resource profiles, including clustered measurements,
   sparse bins, variable resource costs, and dependence. It retains the older
   percentile procedure as a comparison rather than modifying historical runs.
2. **Do measured costs predict an unused observation period?** The
   [solar validation](solar-validation.md) develops forecasts on the retained
   2022–2024 observations and evaluates 2025. The protocol, costs, pooled bins,
   reference measures, comparators, tolerance, and application gate must be
   frozen before acquiring the 2025 event values. Public availability is
   disclosed; this is not an externally blinded study or newly collected data.
3. **When does independently measured resource scaling identify an abundance
   exponent?** The [dimensionality intervention](dimensionality-intervention.md)
   specifies resource costs and restrictions separately from its outcome
   spectrum. Its evidence kind and allocation mechanism determine whether it
   tests a physical system, an engineered rule, or a simulated construction.

The three questions are complementary. A calibrated statistical method does not
establish a physical allocation principle. A successful forecast can support a
declared model without identifying a geometric dimension. A prescribed resource
allocation cannot independently demonstrate that natural systems select it.

## Interpretation and decision rules

For a number density per unit size, independently measured mean resource cost
and resource per logarithmic size interval obey

$$O(k)=kq(k)n(k),\qquad \alpha(k)-1=D_q(k)-\beta(k).$$

Here $D_q=d\log q/d\log k$ and $\beta=d\log O/d\log k$. Under allocation
neutrality, $\beta=0$. The research claim concerns the eligible conditions and
predictive consequences of that condition, beyond the accounting identity.
Input count, joint-feasibility dimension, and resource-cost scaling remain
distinct unless their connection is independently supported.

The primary profile margin is fixed before evaluation. A finite-bin equivalence
claim concerns those bins; it does not establish flatness within them or outside
the declared domain. Failure to establish equivalence is not evidence of a
material departure. Where calibration or observation assumptions fail, the
primary decision remains unresolved even if a nominal interval gives a more
definite answer.

The bounded-resource comparison uses a classical concentration result for
independent bounded summands, as stated in
[Hoeffding (1963)](https://doi.org/10.1080/01621459.1963.10500830).
Empirical maxima are not independently known population bounds. Ordinary
bootstrap inference for means also needs assumptions about the sampling law;
[Athreya (1987)](https://doi.org/10.1214/aos/1176350371) supplies a specific
infinite-variance failure case. These established results motivate the benchmark;
they are not new mathematical contributions of this project.

## Provenance

Each executed study retains its configuration, frozen source and input hashes,
resource units, seed streams or actual measurements, generated statistics,
decisions, and figures. The [append-only registry](run-registry.md) records its
evidence kind and lineage. Historical input snapshots, algorithms, and outputs
remain byte-for-byte unchanged.
The separately retained [independent audit](../results/solar-validation/independent-audit.json)
recomputes catalogue selection and frozen forecast scores directly from CSV,
checks acquisition ordering, and verifies the measured CPU charge partitions.
Its [algorithm](../experiments/audit_solar_validation.py) and all 28 read input
hashes are retained; it is explicitly a posthoc arithmetic check rather than
additional observations or an independent inferential analysis.

## Measured non-unit cost and allocation response

The runtime experiment completed 360 separately collected calibration jobs and 16
allocation trials, retaining 80 worker records, 104,133 completed validation jobs,
79 censored partial jobs and 63.7767 measured worker CPU seconds. All declared
timing checks passed. The independently calibrated finite-grid cost degrees
were 1.8701 and 2.6864, with nominal block-bootstrap intervals excluding one.
The whole measured mean-cost curves, rather than those slopes alone, supplied
the forecasts before any allocation trial.

Across the two kernels and two conditions, maximum absolute CPU-share errors
were 0.00346–0.00627 and completed-count total-variation errors were
0.00209–0.01241. Replacing the largest-class thread with a second smallest-class
thread predicted the CPU-share change $[0.2,0,0,0,-0.2]$; maximum observed
change errors were 0.00764 and 0.00771. A unit-cost-degree alternative produced
count errors of 0.126–0.273. No CPU quotas or target job counts enforced the
predicted shares.

This supports a resource-cost forecast in one engineered GIL/OS allocation
system. It does not identify a geometric dimension, a number of independent
inputs, an exact scheduler fairness theorem, or spontaneous neutrality in
natural systems. The resource-degree estimates describe this finite size grid;
their nominal intervals do not include all hardware or session variation.

## Calibration and the unused solar year

The benchmark evaluated **180,000 independently generated outer datasets** in
90 frozen conditions, after 18,000 separate development datasets. The 499
bootstrap draws within a dataset are internal uncertainty calculations, not
additional independent evaluations. It compared simultaneous centered-vector
bands, a naive two-sided extension of the historical percentile-maximum rule,
and a conservative known-bound reference.

The centered bands passed the declared operating-characteristic gate for dense
bounded independent blocks at 48 blocks, but failed it at 12 and 24. Its
minimum observed coverage of 93.95% at 48 does not establish exact nominal
95% coverage. With
twelve serially dependent blocks, minimum simultaneous coverage across profile
shapes was 7.8% and maximum wrong-departure rate was 43.75%. Twelve sparse
compound-Pareto blocks passed the numerical gate largely through conservatism:
99.55% of flat-target datasets remained unresolved. Passing a rate gate is not
the same as useful discrimination or proof of the application's assumptions.

The naive two-sided percentile-Delta extension failed the gate in every tested
family. This does not attribute a two-sided claim to the historical function:
its upper-bound component is separately retained and evaluated. The known-bound
reference supplied conservative coverage under its correct independent bounded
observation models; neither empirical maxima nor missing detection corrections
justify applying its theorem to arbitrary measured systems.

The solar protocol, method, forecasts and source snapshots were committed in
**390856c before acquiring any 2025 event bytes**. The frozen plan's SHA-256 is
`9c9a5954214a03a877cf97d3f0f8f4b87d21301affc44ce4271dc4c271ac6795`.
The new NOAA annual snapshot has 3,277 records across all twelve calendar
months; 356 meet the primary peak-domain and rise-fluence rules. Development
used the already inspected 1,509 eligible 2022–2024 events. Pooling was fixed
on development data and retains unequal logarithmic widths in six classes.

| Frozen forecast | 2025 count cross entropy (nats/event) ↓ | Count total variation ↓ | Resource-share total variation ↓ |
|---|---:|---:|---:|
| Neutral per logarithmic interval | 1.30165 | 0.12477 | 0.24005 |
| Neutral per linear interval | 2.19312 | 0.57265 | 0.64914 |
| Historical development counts | 1.26337 | 0.02165 | 0.04261 |

The logarithmic forecast outperformed the linear alternative in the declared
conditional score comparison. Historical counts had the better point score;
their gain of 0.03827 nats/event had nominal month-block interval
[-0.01663, 0.09437], including zero. The largest class's mean rise fluence was
0.619 times its development value, exposing a cost-transfer change separately
from resource allocation.

A posthoc independent catalogue audit found that the instrument mix changed:
development's 1,509 eligible peaks included 1,478 GOES-16 records, while 2025's
356 eligible peaks included 118 GOES-16 and 233 GOES-18 records. Thus the
cost-transfer change cannot isolate physical flare behavior from catalogue or
instrument composition. The audit rechecks the frozen scores rather than
refitting predictions or changing the primary sample.

The primary observed normalized resource densities were approximately
$(2.027,1.288,1.474,1.131,0.585,0.498)$, giving a point maximum log-departure of
0.7066, above the fixed $\ln1.5$ margin. The conditional simultaneous departure
band was [0, 1.9152], leaving its candidate decision unresolved. The formal
decision also remained **unresolved**, as declared before acquisition: this
design does not establish independent exchangeable months or physical resource
bounds. The end-fluence sensitivity retains 339 cases and its 4.78% missingness.
Neither a point departure nor a good count score supplies a population neutrality
verdict without the required observation assumptions.

## Reproduce and assess the contribution

```bash
make validation-round validation-round-registry registry-verify PY=python3.11
```

These commands audit/reuse the retained observations and outputs. The solar
analysis target does not acquire data, and the runtime target does not collect
new trials. New observations, source changes or changed hypotheses require a
separate run identifier and directories.
The complete repository suite passed **240 tests**, including 31 new checks of
the decision methods, pre-acquisition freeze guards and CPU measurements.

The round adds an executed calibration benchmark, a forecast evaluated on an
unused historical observation period, and a successful actual allocation
intervention with independently measured non-unit costs. Its strongest positive
evidence concerns the specified runtime mechanism. Its statistical failures
define conditions under which an allocation claim is not supported. A broader
natural principle still needs independently identified eligible natural systems,
useful calibrated observation designs, and successful restriction predictions
across those systems.
