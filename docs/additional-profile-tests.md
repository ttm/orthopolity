# Additional tests from retained data and simulated populations

1 October 2026. These three studies extend the resource-dimensionality programme
with empirical prediction on retained observations and a controlled test of
what exponent agreement identifies. They require no additional workload hardware
or newly collected natural-system observations.

| Test | Independently specified resource/prediction | Observations used | Result |
|---|---|---|---|
| [Solar temporal transfer](solar-resource-transfer.md) | Measured fluence costs; log-resource versus linear-resource neutrality and historical count shape | 573 training flares in 2022–2023, 936 held-out-by-fitting 2024 flares | Logarithmic forecast beats linear; historical counts predict better at the point estimate, with uncertain smaller advantage |
| [Aquatic study transfer](aquatic-study-transfer.md) | Fixed NBSS slope −1 versus a center fitted only to other studies | Primary 103 fits/8 studies; sensitivities 747/11 and 923/15 | Fixed center wins relatively, but primary nominal 95% coverage is only 66.96%; source errors and conventions remain material |
| [Exponent identification](resource-identification.md) | Fixed mass cost $q(x)=x$ and explicit growth/removal mechanisms | 36,000 null-calibration cohorts and 18,000 independently generated evaluation cohorts | A curved profile shares the neutral population MLE exponent; full-profile testing detects what an exponent screen misses |

The empirical holdouts are fitting separations on previously inspected data.
They are not blinded prospective validation. The simulation separates its null
calibration draws from evaluation draws and reports Monte Carlo uncertainty.
The final replay after a plotting correction reproduces exactly the first
numerical realization; it does not double the evidence.

## What these tests add

The solar comparison measures a resource directly and predicts whole bin shares
without fitting a cost power law. It tests the reference measure empirically:
the primary count total-variation errors are 0.167 for logarithmic neutrality,
0.685 for linear neutrality and 0.022 for historical counts. Logarithmic
neutrality also predicts the resource-width profile directly. Temporal cost
changes and event-window definitions remain separate sources of discrepancy.
An ordinary bootstrap interval for a nonnegative distance does not supply a
calibrated flatness rejection or equivalence verdict.

The aquatic comparison tests transport of a fixed slope center to a whole
excluded study. Its primary mean log-score gain for −1 is 1.4712, but its median
per-study gain is 0.0391 and two studies account for about 94% of the aggregate.
Poor predictive coverage prevents calling either Gaussian forecast well
calibrated. Checking one original source confirmed that large reported errors
were faithfully extracted, while their calibration remains unresolved. Centered
slopes do not imply equal resource profiles in individual systems or their
arithmetic aggregate.

The simulated counterexample separates a fitted exponent from a distributional
law. The neutral and curved populations both have population power-law MLE
$\alpha=2$ under the same coordinate and physical mass resource, yet the curved
population's binned resource maximum/minimum ratio is 1.9434. At 10,000 objects,
92.35% of the curved cohorts pass the exponent-compatibility screen and 100%
are rejected by the complete neutral-profile screen. A non-power distribution
can share a power-family fitted exponent. The shifted-removal pure-power case
also changes abundance exponent to 2.4 without changing physical cost dimension
one. The specified removal mechanism predicts both departures.

This supports a concrete methodological conclusion: independently identify the
resource and coordinate, predict complete profiles and restriction responses,
and compare those predictions with alternatives. It does not establish that a
matching exponent identifies a geometric dimension or that Nature generally
selects the neutral allocation regime. The empirical comparisons provide useful
scope constraints and candidates for further validation.

## Reproduce and audit

~~~bash
make profile-tests PY=python3.11
make registry-verify PY=python3.11
~~~

Existing matching outputs are audited/reused; these commands preserve registered
bytes. `make profile-test-registry PY=python3.11` idempotently registers the new
studies and simulation replay. The [registry documentation](run-registry.md)
explains resource definitions, exact inputs, archived code/configuration, seeds,
outputs, evidence kinds and lineage. Fifteen records are now retained, including
incomplete/interrupted attempts. The older records and downloaded snapshots
remain unchanged.

Further scientific work should target the unresolved model: a calibrated
full-profile empirical neutrality test with independently justified dependence
and measurement errors, a new temporal/source cohort, or a restriction
intervention whose predicted response distinguishes neutrality from its rivals.
