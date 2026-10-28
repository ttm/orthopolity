# An independent prediction of allocation

28 October 2026. **Predict a complete allocation in a new condition from
independently specified resource requirements.** This operationalizes article
[section 2.3](paper.md#23-effective-resources-constraints-and-transferable-predictions)
without requiring a power-law size distribution. It is a design specification,
not a dataset-specific registration or new empirical result. The aim remains
to establish the general law's physical reach; successful accounting alone
does not establish its allocation premise.

## Objects, measure and claim

Fix classes $j$, conditions $s$, and the observable amount before
inspecting target allocations. Let $N_{js}$ denote its predicted mean (or
deterministic ideal amount); an observation model connects it to measured
amounts or realized counts. Fix positive reference weights $w_{js}$ from
geometry or a declared counting measure. Size bins require an explicit choice:
log-orthopolic widths are $\Delta\log x$; linear-orthopolic widths are $\Delta x$.
Mode degeneracies, species counts and compartment volumes are other measures,
**neither log-orthopolic nor linear-orthopolic size allocation**. Changing the
measure after seeing the allocation changes the hypothesis.

Let $q_{js}>0$ be independently measured requirements or a restricted physical
composition, for example $q_{js}=Q_0\prod_\ell X_{js\ell}^{\theta_\ell}$.
Define units, constituents and the admissible parameter family first. For
heterogeneous objects, average the combined requirement, not the constituents
separately. Let $a_{js}>0$ describe a previously specified constraint mechanism;
use $a=1$ when claiming unmodified equality. Structural exclusions must be
declared before outcomes and accounted for in the system boundary.

The substantive hypothesis and its normalized prediction are

$$
\frac{q_{js}N_{js}}{w_{js}}=C_s a_{js},\qquad
p_{js}=\frac{w_{js}a_{js}/q_{js}}{\sum_k w_{ks}a_{ks}/q_{ks}}.
$$

An arbitrary fitted $a$ or $q$ can reproduce any positive allocation. Neither
is allowed. A constraint parameter may be calculated from independently
measured conserved inputs; it may not be inferred from the target profile.
An effective weight derived from an equilibrium distribution is not thereby
a separately conserved physical resource. For example, $p\propto e^{-\beta E}$
corresponds algebraically to $q\propto e^{+\beta E}$ under equal reference
weights and $a=1$; it does not imply equal allocation of physical energy $E$.

## Transfer and absolute prediction

If resource parameters need calibration, fit them only in earlier conditions.
For the product family, reference-class ratios obey

$$
\log\frac{p_{js}/(w_{js}a_{js})}{p_{rs}/(w_{rs}a_{rs})}
=-\sum_\ell\theta_\ell\log\frac{X_{js\ell}}{X_{rs\ell}}.
$$

Identification depends on these **within-condition contrasts**: a target
contrast outside the calibration row space is not identified without extra
assumptions. Record conditioning and propagated uncertainty. Absolute $Q_0$
is not identified by proportions. An intervention must change relative
requirements or constraints to distinguish allocation profiles; multiplying
all costs by the same factor leaves proportions unchanged.

When $q$ is an additive resource requirement with independently calibrated
absolute scale (including $Q_0$), and an independent measurement
supplies the complete budget $B_s=\sum_jq_{js}N_{js}$, the stronger forecast is

$$
N_{js}=\frac{B_s w_{js}a_{js}}{q_{js}\sum_k w_{ks}a_{ks}}.
$$

Here $B_s$ must not be reconstructed from target amounts. Include inaccessible
stores, losses and boundary exchange, or explicitly test only a qualified
subsystem. A proportion test alone does not verify conservation or absolute
resource demand. Common cost scaling now predicts a change in total amount
at fixed $B_s$, providing a second possible intervention.

## Public-data gate, comparison and falsifier

Select a source only when it deposits independent input measurements,
observation calibration, class coverage and a separate target allocation.
Fix inclusion, system boundary, error model and an actual numerical acceptance
threshold before target access. Account for correlated calibration error and
compositional dependence; use a count likelihood for counts, including zeros,
rather than pseudocount log regressions. Published results already read are
exposure, even when numerical target arrays remain locally withheld.

Compare physically motivated resource alternatives and the strongest relevant
domain model. Require divergent forecasts in the chosen intervention, not
merely different names for the same equation. Shared predictions establish
compatibility or transfer, not unique support over established theory.

Freeze and push the dataset-specific protocol and verified implementation
before calibration; then freeze and push numerical forecasts before target
release. Declare one whole-profile discrepancy statistic, its uncertainty
calibration, and a practical error tolerance. Report absolute accuracy and
relative model performance separately. Adequate power to discriminate the
fixed alternatives is an eligibility requirement.

**Falsifier:** a gate-qualified target allocation outside the fixed acceptance
region rejects this resource-and-allocation claim in the declared domain.
An omitted constraint proposed afterwards is a new hypothesis requiring a new
test. Failed input/observation qualification yields an inconclusive test, with
the failure retained; it does not turn a bad forecast into support. A successful
transfer establishes a scoped prediction. Generality requires independently
successful transfers across materially different systems.

The [physics](physics-allocation-source-audit-2026-10-28.md) and
[chemistry](chemistry-allocation-source-audit-2026-10-27.md) audits record the
first bounded search under this specification.
