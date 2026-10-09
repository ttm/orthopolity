# Predictive reliability, competing resources, and observation design

1 October 2026. This continuation follows the initial [research programme](research-programme.md).
It adds three executed benchmarks and a [claim ledger](predictive-claims.md).
All observations in these benchmarks are generated from declared mathematical
models. Their purpose is to evaluate predictions and their limits before an
independent empirical study.

## What changed scientifically

The first dependence study assumed the model family was known. The new
[forecast study](forecast-study.md) selects candidates using capacity observations
without using realized outputs, and adds a nonparametric forecast. Separate
capacity stages estimate parameters and select families; a third independent
sample evaluates output prediction. Bootstrap uncertainty is assessed against
population targets instead of treated as automatically calibrated.

The [competition study](competition-study.md) extends fixed-marginal resources to
negative coupling. Its examples show why input count, cost elasticity, and
joint-feasibility elasticity cannot be identified without assumptions. The
[intervention design study](intervention-design.md) quantifies how sampling and
calibration affect discrimination between two resource-restriction closures.

## Findings

* **Accurate finite forecasts do not uniquely identify dimension.** Across the
  complete-resource forecasting scenarios, selected-model mean log-profile errors
  are 0.028–0.029. Gaussian truth selects Gaussian in 15 of 24 repetitions,
  Student-4 in seven, and common shocks in two. The resulting bounded forecasts
  can be close while their unlimited tail dimensions differ. Student-10, absent
  from the candidate list, is also approximated successfully over the declared
  range. No unlimited tail exponent is inferred from this performance.
* **An omitted resource produces a falsifiable failure.** Adding a third,
  unobserved independent requirement raises selected-model and nonparametric
  output-profile errors to approximately 0.843 and 0.855. Both methods miss the
  actual output population profile and CDF in all 24 repetitions, even when
  their uncertainty bands cover the measured two-capacity population.
* **Competition changes dimension and support.** With two unit-Pareto inputs,
  Gaussian correlation $-0.5$ gives limiting feasibility index four. Fully
  opposed inputs have bounded feasible size, $S(k)=2/k-1$ on $[1,2]$, and density
  $2/k^2$. Their primary resource per log size is exactly constant for $q(K)=K$.
  The varying survival elasticity is reconciled by the finite derivative
  correction, rather than interpreted as the additive cost dimension.
* **Observation design changes the sample requirements.** Under exact costs,
  frozen PF/KL predictions, and the chosen calibrated unique-acceptance criterion,
  the first tested sample size meeting the 0.90 conditional lower-bound target
  for both truths is 50,000 objects per cohort, or 10,000 resource-proportional
  opportunities per cohort. These are model- and criterion-specific calculations,
  not universal sample-size requirements. Forced likelihood choice and candidate
  adequacy are reported separately; an extra allocation objective can make both
  candidates fail while one remains the closer forced choice.

The resource-cost law is held fixed within each comparison. No fitted abundance
exponent is used to redefine the resource. Availability minima are still defined
as bottlenecks in the simulated forecasting data; prospective prediction here
tests statistical performance, not empirical realization of that mechanism.

## Interpretation for Orthopolity

The positive contribution is now an operational prediction programme: independently
identify resource requirements and availability, forecast complete profiles and
intervention responses, and retain failures when an assumption is inadequate.
The exponent can be a meaningful conditional dimension. Establishing which
dimension it represents requires the measured cost, joint availability law,
support, realization mechanism, and allocation target.

The negative-coupling example also qualifies a simple "dependencies reduce the
number of inputs" interpretation. Positive and negative dependence have different
consequences. Bounded density powers and asymptotic survival indices answer
different questions. A correctly predicted feasible-size distribution does not
alone establish resource neutrality: neutrality remains a separate endpoint.

The copula, proportional-fairness, and likelihood mathematics are established.
The claim ledger identifies the possible original contribution in independent
calibration, predictive performance, intervention response, or evidence that a
specified class of natural systems selects neutrality. These simulated results
do not establish a natural law or the proposed broad cosmological principle.

## Reproduce and proceed empirically

~~~bash
make robustness PY=python3.11
make test PY=python3.11
~~~

Individual targets are `competition`, `forecast`, and `interventions`. Each study
has its own configuration, numerical record, CSV output, and PNG/SVG figures.
The corresponding result directories are `results/competition/`,
`results/forecast/`, and `results/interventions/`.
New `make` reproductions write under `build/reproductions/`, preserving the
registered retained artifacts.
The complete test suite passes all 131 tests, including 23 new checks for these
three studies. The generated figures were rendered and visually inspected.

The [empirical protocol](empirical-protocol.md) remains the next observation step.
Use these benchmarks to choose sampling, tolerances, and alternative models for
a specified real system. The forecast coverage estimates use only 24 outer
repetitions per scenario and have wide Monte Carlo uncertainty. The intervention
calculation assumes independent multinomial opportunities, known primary costs
and propensities, and one frozen calibration/error pattern. Real clustering,
censoring, calibration uncertainty, and resource completeness need their own
measurement-specific design. No real validation data have yet been collected.
