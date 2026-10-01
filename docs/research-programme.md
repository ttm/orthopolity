# Resource dimensionality: theory and perturbation benchmarks

1 October 2026. This programme follows the [first cross-model study](model-study.md)
and develops the dimensionality proposal through independent forward predictions,
changes in mechanism, and explicit resource restrictions. The computational
studies use specified models. They supply no new observations of natural systems.

The [predictive reliability continuation](predictive-benchmarks.md) adds
capacity-only model selection, uncertainty assessment, omitted-resource failures,
negative dependence, and calibrated sampling designs for budget interventions.

The later [controlled workload pilot](workload-pilot.md) adds actual hardware
cost measurements and prospective quota-acceptance predictions. Its assigned
resource conditions evaluate operational transfer rather than spontaneous
neutral allocation.

The [fresh-launch transfer comparison](workload-transfer.md) then finds two
original-forecast failures under unchanged quotas/criteria and recovery of one
with prospective local recalibration. The [run registry](run-registry.md)
retains the complete programme and incomplete attempt. A [gated CPU-allocation
protocol](scheduler-allocation.md) supplies competing restriction predictions;
the present host fails its scarcity qualification, so no actual allocation
trial was executed.

## The central hypothesis and its operational targets

The general organizing relation is $H(k)=G(k)h(k)$. A constant aggregate $H$ and
a homogeneous independently identified weight $G$ imply a power law for $h$.
Physical interpretation requires declaring whether the aggregate is resource
stock, capacity, occupancy, representation of a hierarchy, or transported flux.

The new [dimensionality note](resource-dimensionality.md) separates cost
elasticity from joint-feasibility elasticity. If a feasible-size survival law has
index $\kappa$, its density has index $\kappa+1$ under the stated regularity
conditions. A primary cost $q_1(k)\sim k^{d_1}$ then gives resource per log size
proportional to $k^{d_1-\kappa}$. Neutrality requires matching the two indices.
Dependence can change joint feasibility without changing the cost law or the
individual capacity marginals.

This formulation makes the exponent interpretation conditional and testable.
Measuring capacities and costs independently supplies a prediction for size and
resource profiles. Observing a power law and assigning a matching resource weight
supplies a representation instead. Both are legitimate operations with different
scientific targets.

## The five authorized next steps

| Step | Deliverable | What it establishes |
|---|---|---|
| Precise dimensionality hypothesis | [Theory and dependence study](resource-dimensionality.md) | Explicit cost, feasibility, and tail assumptions; bridge to resource spectra |
| Fixed-marginal dependence benchmark | [Source](../src/orthopolity/dependence.py), [runner](../experiments/run_dependence.py), [configuration](../configs/dependence_study_2026-10-01.json) | Forward predictions across common shocks, Gaussian and Student dependence, resource counts, and caps |
| Transfer across mechanisms | [Attachment study](attachment-study.md) | Fixed wedge resource under uniform, sublinear, linear, superlinear, and affine growth |
| Predictive restrictions | [Two-budget study](restriction-study.md) | Budget-determined profile and intervention predictions, including slack and infeasible conditions |
| Independent empirical test design | [Protocol](empirical-protocol.md), [metadata skeleton](../configs/empirical_protocol_2026-10-01.json), [data templates](../data/templates/) | Separate cost calibration, measured availability, observed outcomes, and validation criteria |

Configs and seed streams are explicit local specifications; they are not external
preregistrations. Simulation families are known constructions, not independently
identified mechanisms of natural populations. No abundance-derived resource
weight is substituted to make a failed comparison flat.

## Findings from the executed benchmarks

The dependence study contains twelve scenarios with six independent validation
runs each. Gaussian and Student constructions with latent correlation 0.5 have
the same theoretical Kendall correlation, one third, but two-input limiting
feasibility dimensions of $4/3$ and 1. Their calculated local dimensions at size
threshold 10 are 1.418 and 1.217. The full forward resource profiles reproduce
the simulated bounded-domain profiles with log-RMSE 0.0028–0.0134. Forecasts from
separate capacity training have log-RMSE 0.0041–0.0210; their parameter-estimation
uncertainty is not included in validation-run shading. This establishes the
importance of the joint-tail law, rather than a single generic dependence
coefficient, within these specified constructions.

The attachment study contains five kernels at three nested graph sizes, with
eight independent growth histories per kernel. At 50,000 vertices, the largest
vertex holds a mean of 0.46% of full wedge resource under sublinear attachment
and 95.52% under superlinear attachment. The fixed degree domain retains all
sublinear wedges and a mean of approximately $10^{-6}$ of superlinear wedges.
Both full-resource concentration and excluded tails are reported. A normalized
profile on a bounded domain alone can hide most of a system's resource.

The two-budget study predicts a response to reducing the auxiliary budget from
12 to 8, with primary total fixed at one in both closures. Its distinct log-profile
responses differ by RMSE 0.17065. At an auxiliary budget of two, proportional
fairness uses primary resource 0.4732 while relative entropy fixes it at one;
that case diagnoses different constraints rather than comparing equivalent
resource totals. At auxiliary budget 0.5 the fixed-primary closure is infeasible.
For proportional fairness, scarcity prices define the effective cost rather than
being fitted from profiles; its active-budget crossover moves from approximately
50.3 to 8.0 under the declared intervention.

All three studies retain full output, model assumptions, configuration, and
package versions in their result directories. These findings are computational
properties of the specified models. They do not identify a universal natural
objective, establish empirical bottleneck realization, or prove that all
fractional exponents measure the number of independent inputs.

## Reproduction

~~~bash
make followup PY=python3.11
make test PY=python3.11
~~~

The combined target runs the three studies. Individual targets are `dependence`,
`attachment`, and `restrictions`. Outputs are written respectively to
`results/dependence/`, `results/attachment/`, and `results/restrictions/`.
New `make` reproductions write under `build/reproductions/` to preserve these
registered artifacts.
The first study remains available through `make models`. Existing empirical
analyses and the historical manuscript are separate targets.

The full repository suite passed 108 tests in the review environment. Additional
export checks verified finite numerical records, profile normalization, resource
and exposure accounting, and header-only empirical templates. Figures were
rendered and visually inspected. These checks verify the computations and report
consistency; they do not validate the models on natural-system observations.

## Scientific interpretation

The immediate theoretical aim is to specify when an exponent measures a stable
joint resource dimension, when the relevant dimension varies with scale, and how
it connects to the independently measured dimension of resource use. Complete
profiles and intervention responses are necessary because equal asymptotic
indices need not imply identical finite-range distributions.

The transfer study tests a fixed resource across several generating rules. It
can identify conditional compatibility and predicted departures. The restriction
study compares two additional allocation assumptions rather than deducing a
unique constrained distribution from conservation alone. A primary equality
constraint and a primary upper bound are different scientific models.

The next empirical claim should be prospective prediction from measured resources
and costs. The protocol supplies a concrete candidate using numerical workloads
and a transferable observation design. Real-system selection, measurement
calibration, sample-size design, and validation observations remain future work.
An outcome defined computationally as a bottleneck cannot independently validate
the bottleneck hypothesis in Nature.

These results develop a theory programme aligned with the original ambition.
They do not establish a universal resource principle. A stronger original paper
would need a genuinely new conditional result, a demonstrably useful predictive
method, or successful independent predictions beyond known model properties.
The broader philosophical use of "cosmological principle" remains a proposed
interpretation of the programme, with empirical status determined separately.
