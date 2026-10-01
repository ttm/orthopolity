# Independent resource prediction: an empirical protocol

1 October 2026. This is a prospective design, not a completed experiment or an
external preregistration. No natural-system observations have been added. The
domain, equipment, sampling plan, and analysis thresholds must be fixed for the
chosen setting before validation outcomes are inspected.

The first [controlled workload implementation](workload-pilot.md) is now
executed. It supplies actual cost measurements and later quota-acceptance
outcomes under a saved prediction freeze. The general protocol below remains
applicable to future independently chosen systems; the controlled pilot does
not test autonomous neutral allocation.

## Question and observable

Can independently measured resource availability and independently calibrated
resource requirements predict the distribution of realized feasible sizes, and
its response to a change in dependence or a resource budget?

For opportunity $i$, record available budgets $B_{1i},B_{2i}$ before observing its
outcome. Calibrate monotone requirement functions $q_1(k),q_2(k)$ on separate units.
These define capacities $X_{ai}=q_a^{-1}(B_{ai})$. The proposed bottleneck model
predicts

$$K_i^*=\min(X_{1i},X_{2i}),\qquad
S_*(k)=P(B_1\ge q_1(k),B_2\ge q_2(k)).$$

The observed outcome $K_i$ must be measured by a physical or operational success
criterion. It must not be entered in the dataset as the minimum of the calculated
capacities. If units select a smaller size, or another resource limits them, that
is evidence about the applicability of the bottleneck model. A variable with
definition $K=\min X_a$ supplies a mathematical benchmark, not this empirical test.

If $S_*(k)\sim k^{-\kappa}$ with sufficient density regularity, then the predicted
density exponent is $\kappa+1$. If the primary cost scales as $k^{d_1}$, the
predicted primary resource per log size scales as $k^{d_1-\kappa}$. Neutrality
therefore requires $\kappa=d_1$. Joint feasibility and resource-cost dimension
are distinct measurable quantities; their equality is a testable condition.

On a finite band with changing survival elasticity, predict the full profile
directly from $S_*$ rather than substituting that elasticity as a density
exponent. If $\kappa(k)=-d\ln S_*/d\ln k$, then the resource-profile elasticity is
$d\ln q_1/d\ln k-\kappa+d\ln\kappa/d\ln k$. This derivative correction matters
when dependence produces a crossover rather than an exact power law.

## An accessible candidate pilot

Pending information about available laboratory or field measurements, a concrete
candidate is a fixed numerical workload with two measured resources: memory and
processing time. Repeated matrix workloads at declared integer sizes offer a
controlled implementation. The task, implementation, thread count, precision,
warm-up policy, machine, and success criterion must be frozen. Cost curves are
measured rather than assumed to follow ideal quadratic or cubic formulas.

1. On calibration trials, measure memory consumption, processing time, failure
   probability, and their uncertainty across the declared sizes. Account for
   process overhead and distinguish peak resident memory, virtual address
   limits, wall time, and CPU time. A configured limit and the measured cost must
   refer to the same quantity. The
   [Python resource documentation](https://docs.python.org/3.11/library/resource.html)
   distinguishes processor-time limits, address-space limits, and resource-usage
   measurements; platform semantics must be checked for the chosen implementation.
2. Assign paired resource budgets independently of workload outcomes. Keep each
   budget marginal fixed and change the pairing between conditions. Use a
   separate experiment to lower one budget while holding the other fixed.
3. For each assigned pair, execute trials at a fixed set of candidate sizes and
   record the largest successful observed size, with censored results when the
   search reaches its bounds. Success must be determined by the actual workload
   result and the declared limits. Do not substitute an analytic capacity for
   execution. Randomize trial order and record repeated measurements to detect
   thermal, cache, scheduling, and batch effects.
4. Generate predictions from the calibration data and assigned budgets before
   examining validation sizes. Allow the observation model to include measured
   stochastic costs; deterministic inverse costs are an approximation whose
   adequacy must be checked.

This pilot would test an operational resource-feasibility model in a controlled
system. A successful result would not establish spontaneous equal allocation or
a general principle of Nature: the budgets and workload opportunities are
experimentally assigned. A physical or biological application must separately
identify its population, resource budgets, costs, and observed units. The same
prediction design can be adapted once those measurements are available.

## Data separation and records

Use distinct calibration and validation batches. If a copula or other joint-law
model is estimated, train it on capacity observations without using validation
unit sizes. Freeze its parameter-estimation rule, then evaluate size predictions
on held-out opportunities. A direct prediction using known assigned budgets is
also valid; it tests the cost and bottleneck mapping rather than generalization
of a fitted availability distribution.

Header-only templates are provided at
[resource-calibration.csv](../data/templates/resource-calibration.csv) and
[resource-opportunities.csv](../data/templates/resource-opportunities.csv).
They contain no observations. Costs and budgets must use the same documented
units. The metadata skeleton is
[empirical-protocol_2026-10-01.json](../configs/empirical_protocol_2026-10-01.json).
Unset fields represent work required before an actual experiment, not implicit
approval of a particular protocol. The calibration template describes two
resources; a real study may require more.

Each opportunity is an independently defined exposure. Specify whether one
observation represents a single task, a complete batch, or a nested size search.
Repeated sizes within one opportunity are not independent population samples.
Keep failed and censored trials. Define handling of zero-size failures separately
from the positive-size spectrum.

## Predictions and decision criteria to freeze

Primary prediction: the complete validation survival profile $S_*(k)$ on a domain
defined by instrument bounds and calibration support. Secondary predictions:
resource profiles, intervention-induced profile ratios, and scaling dimensions
on bands specified independently of validation outcomes. Estimate uncertainty
at the level of independent opportunities or batches, retaining repeated-trial
dependence and calibration uncertainty.

Compare at least the joint-resource bottleneck prediction, each single-resource
prediction, and an independence approximation using the same measured marginals.
For a paired-budget intervention, the marginal predictions stay fixed while the
joint prediction changes. Include a declared alternative for extra limits or
stochastic completion if justified before outcome inspection. Ordinary
correlation alone must not substitute for the measured joint availability law.

Before collecting validation data, use simulation to choose sample size, domain,
and tolerances against explicit alternatives: a nonbinding second resource,
miscalibrated costs, an unmeasured bottleneck, stochastic failures, and censoring.
Numerical thresholds are deliberately unset until the actual measurement error
and detectable intervention effect are known. A provisional threshold chosen
without them would be arbitrary. Record an absolute profile-error tolerance and
a criterion for improvement over the strongest prespecified comparator.

Evidence supporting the model consists of accurate prospective full-profile and
intervention predictions from separately measured resources and costs. Evidence
against its applicability includes systematic errors outside the calibrated
uncertainty, a missing intervention response, or superior prediction by a
prespecified alternative. Resource neutrality is a separate endpoint: prediction
of feasible sizes does not itself show that $\kappa=d_1$.

## An allocation test after feasibility

The two-budget benchmark compares proportional fairness with minimum relative
entropy. An empirical allocation experiment requires counts across fixed classes
and actual resource use for the same population. Its conditions must establish
whether the primary resource total is fixed or merely bounded; the closures have
different implications when that budget is not exhausted.

Calibrate costs independently, measure or assign the auxiliary budget, and predict
each closure's complete response with multipliers determined by budgets. Include
slack-budget and infeasible conditions as applicability diagnostics. Test the
predicted log-profile ratio as well as a slope. Choosing whichever objective
fits each observed condition is exploratory model selection, not prospective
confirmation of one allocation law.

## What can be completed now

The [forecast benchmark](forecast-study.md) now assesses capacity-only family
selection and training uncertainty. The [intervention design](intervention-design.md)
quantifies sampling requirements for the declared two-budget comparison. These
are design precedents; a chosen real system still requires calibration for its
own costs, observation design, clustering, censoring, and detectable alternatives.

The repository supplies the mathematical targets, model comparisons, metadata
and data templates, and this observation design. The workload pilot completes
one controlled measurement and prospective forecast exercise. Selecting an
autonomously allocating system, calibrating its measurements, registering a
concrete analysis if desired, and collecting independent allocation outcomes
remain future work. Existing heterogeneous ecological summaries do not provide
the paired capacities and independent cost calibration required by this design.
