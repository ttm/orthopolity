# Scientific strength and a concrete route forward

Assessment: 28 September 2026; consistency review and external-assessment addendum:
29 September 2026. This is a research assessment and proposed design,
not a completed validation study or a preregistration. It supplements the
[manuscript](paper.md) and [remaining work](roadmap.md).

## Verdict

The current contribution is modest as original science, useful as a critical
synthesis, and comparatively strong in transparency and reproducible accounting.
It does not establish a new allocation law. Better wording alone cannot supply
novelty or independent evidence. A natural law need not have a deeper mechanistic
explanation: a precise allocation postulate with independently specified scope
and successful empirical predictions is a legitimate route. A mechanism would
provide additional explanatory content, but is not a prerequisite for a law.

| Dimension | Assessment | Reason |
|---|---|---|
| Mathematical formulation | Sound and useful, limited originality | Inverse-cost abundance follows from the allocation postulate; the substantive physical claim is that the postulate applies to specified systems. |
| Empirical support for the broad hypothesis | Weak | The physical cases disagree with specified versions; aquatic equivalence is unresolved; the ocean reconstruction is reused evidence. |
| Reproducibility and disclosure | A substantial asset | Frozen inputs, explicit estimands, tests, and disclosed corrections make the work inspectable. They do not validate the sampling model. |
| Generalization | Not established | Convenience sources, study concentration, uncertain metadata, and differing resources prevent a general population claim. |
| Potential for stronger research | Credible but conditional | A validated method with demonstrated utility, or a successful independent prediction, could add scientific content. |

The aquatic result illustrates the distinction. The primary sample has 1,300
reported slopes but only 16 study identifiers, with 78% of estimates from two
studies. Its median is close to the predicted value, but the study-block interval
does not establish the planned equivalence. Known invalid range metadata affect
377 records. These facts support a careful assessment of the evidence, not a
universal conclusion. See [the numerical ledger](evidence.md) and
[the stored analysis](../results/independent.json).

## What the closest work already does

A targeted literature check sets the minimum comparison; it is not an exhaustive
priority search.

| Existing work | Implication for this project |
|---|---|
| [Edwards et al. (2017)](https://doi.org/10.1111/2041-210X.12641), with [public simulation code](https://github.com/andrew-edwards/fitting-size-spectra), and [Edwards et al. (2020)](https://doi.org/10.3354/meps13230) | Estimator comparisons, reliable slope intervals, and correct handling of bins already have substantial methodological treatment. |
| [Cuesta, Delius and Law (2018)](https://arxiv.org/abs/1607.04158) | Mechanistic size-spectrum models already exist; an allocation identity is not their replacement. |
| [Mehner et al. (2018)](https://doi.org/10.1002/ecy.2347) | Independently estimated trophic transfer efficiency has already been compared with observed spectrum slopes. A mechanistic slope prediction alone is not a new research category. |
| [Atkinson et al. (2024)](https://www.nature.com/articles/s41467-023-44406-5) | Environmental drivers and the distinction between snapshots and ecosystem averages are already studied. Another pooled slope near −1 adds little by itself. |
| [Wesner et al. (2024)](https://doi.org/10.1111/2041-210X.14312) | Hierarchical modelling of size spectra is established work. Adding random effects does not, alone, establish novelty. |
| [Dugenne et al. (2024), PSSdb](https://essd.copernicus.org/articles/16/2971/2024/) | Published data products include binned particle spectra as well as fitted parameters. They offer a possible profile-level application, subject to access and sampling audits. Particle biovolume includes detrital material and is not automatically organism biomass. |

The plausible methodological increment is a demonstrated improvement in deciding
whether an entire declared resource profile is practically flat under realistic
sampling. Whether that increment is novel enough still needs a dedicated comparison
with functional equivalence and survey-inference methods as well as ecological work.

## A mathematical strengthening available now

The manuscript gives examples showing that zero mean slope does not imply a flat
arithmetic mean spectrum. The following proposition makes the restriction general
within the exact power-spectrum model. This is an application of standard
convexity, not a claim to a new mathematical principle.

**Proposition.** On a common nondegenerate logarithmic domain, let

$$O_i(u)=A_i e^{\beta_i u},\qquad
H(u)=\sum_{i=1}^n w_i O_i(u),$$

where $A_i>0$, $w_i>0$, and $\sum_i w_i=1$. The amplitudes and weights do not vary
with $u$. Then $H$ is constant on an open interval if and only if every
$\beta_i=0$.

**Proof.** Differentiating the finite sum twice gives

$$H''(u)=\sum_i w_i A_i\beta_i^2 e^{\beta_i u}.$$

Every term is nonnegative. If any slope is nonzero, this derivative is strictly
positive everywhere, so $H$ cannot be constant. Conversely, zero slopes give a
constant sum. Normalizing each system to unit total on the common domain only
replaces $A_i$ by another positive constant and preserves the result.

There is also an exact curvature identity. Set

$$p_i(u)=\frac{w_iA_i e^{\beta_i u}}{H(u)}.$$

Then

$$\frac{d\ln H}{du}=\sum_i p_i(u)\beta_i,\qquad
\frac{d^2\ln H}{du^2}=\operatorname{Var}_{p(u)}(\beta).$$

Thus heterogeneous exact power slopes produce strictly positive log-curvature.
Identical nonzero slopes give a non-flat power spectrum with zero log-curvature.
These are different statements from curvature of $H$ itself.

**Approximate restriction.** For $h>0$ and $[u_0-h,u_0+h]$ within the common domain,

$$\frac{H(u_0-h)+H(u_0+h)}{2H(u_0)}
=\sum_i p_i(u_0)\cosh(h\beta_i).$$

If the left side is at most $F\ge1$, then

$$\sqrt{\sum_i p_i(u_0)\beta_i^2}
\le \frac{\operatorname{arcosh}(F)}{h}.$$

To see this, apply Jensen's inequality to the convex function
$x\mapsto\cosh(h\sqrt{x})$ on $x\ge0$. Its power series has nonnegative
coefficients, including those of its second derivative. A global
$\max H/\min H\le F$ is sufficient for the premise. The different condition
$\phi\in[1/F,F]$ supplies a ratio bound of $F^2$, so the displayed bound then
uses $\operatorname{arcosh}(F^2)$.

This bounds a **midpoint-resource-weighted root mean square slope**. It does not
bound the ordinary between-system variance estimated in this repository.
Total normalization can give steep spectra very small midpoint weights.

The scope restrictions matter. Fitted noisy slopes are not exact spectra. General
curved profiles can cancel: $1+\epsilon\sin u$ and $1-\epsilon\sin u$, with
$0<\epsilon<1$, have a flat arithmetic mean. Changing which systems contribute
at each size also violates the fixed-weight premise. Consequently this proposition
strengthens the logical argument but establishes no additional empirical result.

## Recommended route: validate decisions about complete profiles

A focused candidate paper is **“When do size spectra support resource
equipartition? Calibration of profile equivalence under heterogeneous sampling.”**
That is a proposed research question, not a claim that a novel method has already
been established.

### 1. Define one primary scientific target

For finitely many fixed bins of logarithmic widths $w_j>0$, define the nonnegative
population resource density $O_j$ as resource per log-width, with exposure and
inclusion probabilities handled by the sampling design. Assume finite, positive
total resource, so $0<C<\infty$. Let

$$C=\frac{\sum_j w_jO_j}{\sum_j w_j},\qquad
\phi_j=O_j/C,\qquad
\Delta=\max_j |\ln\phi_j|.$$

A zero population resource bin has infinite $\Delta$. Practical equivalence means
$\Delta<\ln F$, for a scientifically justified and prospectively fixed $F>1$.
This is a statement about the declared binned profile. It does not certify
within-bin flatness or make the endpoint-drift tolerance an equivalent target.

Given calibrated bounds for $\Delta$, report three outcomes: equivalence if its
upper bound is below the margin, material departure if its lower bound is above
the margin, and unresolved otherwise. Define each error probability in advance.
Use slope as a secondary description. If an ensemble is the target, declare
whether it averages normalized profiles equally by system or weights their raw
resources; these can give different answers.

### 2. Audit and benchmark the method already present

[flatness_equivalence](../src/orthopolity/goodness_of_fit.py) already accepts
whole-spectrum replicates and uses their maximum log-departure. The needed advance
is validation, not merely adding a profile screen. Its percentile upper bound is
approximate; nonsmooth maxima, sparse bins, correlated errors, and small numbers
of independent blocks make coverage a substantive research question. Unit tests
that verify decisions on chosen arrays do not establish repeated-sampling error
control.

Build a simulation benchmark with known population profiles and a separate
observation process. Include flat profiles, departures just inside and outside
the margin, gradients, symmetric humps with near-zero fitted slopes, local
deficits, and mixtures of exact powers. Vary cluster count, domain width, binning,
resource variability, and sampling intensity. Include size-dependent detection
both with correctly specified inclusion probabilities and with deliberately
misspecified corrections. An unidentified detection process cannot be repaired
by a bootstrap.

Compare the present procedure with calibrated simultaneous confidence bands or
another justified method, and with common slope-only and non-rejection rules.
Clearly distinguish rules that test different targets. Report false equivalence
at and outside the boundary, power well inside it, coverage, unresolved fractions,
and sensitivity to misspecification. For example, 2,000 independently simulated
datasets per core scenario give a Monte Carlo standard error of about 0.005 for
a probability near 0.05; report binomial intervals and expand near ambiguous
decision boundaries. Inner bootstrap draws are not independent simulation trials.

Freeze scenarios, margins, metrics, and permitted tuning before the final benchmark.
Use separate development and evaluation seeds. Retain failures: the contribution
could be showing when a seemingly reasonable test is unreliable and providing a
validated remedy or an explicit limit on use.

### 3. Establish utility on audited measurements

Choose one ecological population and one resource. Obtain organism measurements
or bin totals with sampling volumes, instrument ranges, site/visit identifiers,
and enough independent sampling units to assess uncertainty. PSSdb is a candidate
to investigate, not a verified ready-to-use replacement for the current inputs.
Choose its resource definition explicitly if using particle biovolume.

For the existing aquatic compilation, build a source-to-record audit of units,
bin conventions, estimands, ranges, dependence, and error coverage. Resolve the
377 suspect ranges from primary evidence or exclude them from range-dependent
inference. Compare record-weighted and study-weighted targets, with removal of
dominant studies as a disclosed sensitivity. These improve credibility but cannot
recover absent profile shapes from slopes alone.

Demonstrate whether the validated method changes a substantive interpretation,
how often it leaves the question unresolved, and what observations would resolve
it. A simulation calibrated only under convenient assumptions plus a decorative
real-data example would remain a limited contribution.

### 4. Require a clear increment before calling the paper strong

Proceed as original methods research if the literature comparison identifies a
gap, the benchmark quantifies that gap, the proposed procedure has acceptable
error control under its stated design, and an audited application demonstrates
scientific utility. If these conditions fail, retain the present work as a
critical synthesis. Neither a favourable empirical answer nor a new estimator
is required, but a useful result beyond existing work is.

## Alternative route: test resource symmetry as a candidate law

The proposed rationale is that, in the absence of restrictions that favour one
resource cost over another, resource allocation should not distinguish those
costs. This can be developed as a physical symmetry postulate. Its scientific
standing does not depend on first deriving it from a deeper mechanism.

For a finite set of $K$ declared classes with fixed positive per-object costs
$q_i$, let $R_i=q_iN_i$ and $\sum_i R_i=R>0$. Suppose the probability law of
$(R_1,\ldots,R_K)$ is invariant under all permutations of its components, with
the cost classes held fixed. This is an assumption of exchangeable resource
allocations, not just a change of names for the pairs $(q_i,R_i)$. Then

$$E[R_i]=\frac{R}{K},\qquad E[N_i]=\frac{R}{Kq_i}.$$

The proof is immediate: permutation symmetry makes all expected resources equal,
and their sum fixes their common value. The hypothesis is substantive because
it selects resource allocations as the symmetric quantities. A symmetry of
object counts would give equal expected counts and unequal expected resources.
Where integer counts or indivisible objects prevent exact resource symmetry,
an approximation or a suitable large-population limit must be specified.

Exchangeability implies equality in expectation. It does not imply a nearly
equal allocation in each realization or relaxation toward equality. A system
that assigns all divisible resource to one uniformly chosen class has this symmetry but
is maximally uneven in every snapshot. Long-time equality requires an additional
condition connecting time averages to expectations, or its own empirical
postulate. This distinction specifies what the proposed phrase "tends to allocate"
will predict.

In the continuum, the corresponding statement is

$$dE[R(q)]=C\,d\mu(q),\qquad
\frac{dE[N(q)]}{d\mu(q)}=\frac{C}{q}.$$

Here $dE[R(q)]$ denotes the expected resource measure, and $\mu$ declares the
classes that are to receive equal shares. Equal-width cost intervals use
$d\mu=dq$, giving count density $dE[N]/dq\propto q^{-1}$. Equal-ratio intervals
use $d\mu=d\ln q$, giving $dE[N]/dq\propto q^{-2}$. These are different physical
symmetries with different predictions. On an interval, logarithmic allocation
requires a positive lower and finite upper cutoff for finite total resource.
Linear allocation on $(0,b]$ can have finite resource, but its $q^{-1}$ count
density has infinite total count; a positive lower cutoff makes both finite.
Changing units alone does not select the logarithmic version.

Specifying the transformations that express indifference has a precedent in
[Jaynes' treatment of prior probabilities](https://bayes.wustl.edu/etj/articles/prior.pdf).
That inferential argument does not itself establish a physical allocation law;
the postulate here concerns actual systems, not only an observer's knowledge.

A strong test would identify eligible systems through independently measured
conditions, fix the resource measure and statistical target, and evaluate the
predicted allocation with adequate precision. Restrictions cannot be defined
afterward as whatever caused a departure. Weakening a measured source of bias
could provide an additional experiment, if convergence toward the neutral
prediction is explicitly part of the hypothesis. This route can strengthen
the natural-law claim through evidence even without proposing microscopic dynamics.

## Mechanistic extension: predict a departure or a dynamical response

A stronger ecological theory paper would derive a conditional prediction from
independently supported processes, such as feeding, growth, mortality, or resource
input. The predicted observable could be profile curvature, response to a
perturbation, relaxation time, or a cutoff, as well as slope. It must differ
quantitatively from predictions of established size-spectrum models.

Fit permitted parameters on development systems. Freeze the resource, domain,
prediction, uncertainty model, comparators, and score, then evaluate on genuinely
untouched systems or future observations. Split at the level at which transfer
is claimed: random rows from the same sites do not test transfer to new sites.
Compare calibration and predictive performance with established models and simple
baselines. Use design-based simulation to choose independent sample size; the
number of recorded slopes is not a substitute for that calculation.

Constructing dynamics whose stationary state is flat is easy if flatness is
imposed through the transition rules or boundary conditions. Scientific content
requires independent support for those rules and successful consequences beyond
the stationary distribution. The current data do not supply that support.

## Additional assessment: invariance, Benford digits, and discriminating tests

An external assessment supplied on 29 September agrees that the current discovery
claim is limited and proposes three routes: a prediction with non-unit cost
exponent, an advance rule identifying eligible systems, and a dynamical mechanism.
These are useful research leads, with the following corrections.

**A missing mechanism does not disqualify a law.** The corrected position above
still applies. A rule identifying eligible systems, fixed independently of their
allocation, is a particularly valuable refinement. "Systems that redistribute
resources" versus "systems that release resource in bursts" is a candidate
classification to test, not an established explanation. Stock, event-total, and
flux measurements must remain distinct. Conservation or redistribution alone
does not select logarithmic resource allocation.

**Scale invariance selects a measure, not a finite probability on all positive
sizes.** For a locally finite nonzero Borel resource measure, invariance under
all positive multiplicative rescalings selects $dR=C\,dk/k$. Its total mass on
$(0,\infty)$ is infinite. A log-uniform probability on a bounded domain is the
normalized restriction of this measure; its fixed endpoints break global scale
invariance. Covariance when changing measurement units is a weaker requirement
and does not uniquely select this measure. Scale priors and physical resource
distributions also play different scientific roles.

**Benford digits are a conditional, weaker diagnostic.** Under logarithmic
resource equipartition on $[a,b]$, sampling in proportion to resource gives
the following density with respect to $dk$:

$$p_R(k)=\frac{1}{k\ln(b/a)},\qquad a\le k\le b.$$

Thus $U=\log_{10}K$ is uniform over a finite interval. Exact base-10 Benford
significands require the fractional part of $U$ to be uniform. For this
interval-uniform model, that holds when $\log_{10}(b/a)$ is a positive integer;
the starting phase need not be an integer. Its leading-digit probabilities are
then $P(D=j)=\log_{10}(1+1/j)$ for $j=1,\ldots,9$. Arbitrary finite endpoints
give different digit probabilities and must be included in the null model.
[Hill (1995)](https://doi.org/10.1090/S0002-9939-1995-1233974-8) develops invariance
on significands; [Wojcik (2013)](https://arxiv.org/abs/1307.3620) explicitly relates
the problem to uniformity modulo one. These results do not identify a finite
scale-invariant probability on all positive real numbers.

The converse fails even for the full significand distribution. Let $U=J+V$,
where $V$ is uniform on $[0,1)$ and independent of $J$, with $P(J=0)=0.9$ and
$P(J=1)=0.1$. Then $10^U$ is exactly Benford, but its two decades have 90% and
10% of the probability. If this is the resource-weighted size distribution,
resource allocation across those decades is unequal. A digit test discards
information retained by a complete log-size profile and cannot independently
confirm equipartition. Sampling objects equally instead of weighting by resource
would test a different prediction again.

**A non-unit cost exponent is useful only relative to a fixed coordinate.**
For $\bar q(k)=q_0(k/k_0)^d$ and count density exponent $\alpha=d+1$, transform
to $z=(k/k_0)^c$, $c>0$. Then

$$d'=d/c,\qquad \alpha'=1+(\alpha-1)/c.$$

Choosing $c=d>0$ gives $d'=1$ and $\alpha'=2$ without changing the logarithmic
allocation hypothesis. If resources vary among objects at fixed $k$, this
transformation uses the mean-cost coordinate; it is not equivalent to sorting
objects by their individual realized resource values.

In a predeclared physical coordinate, independently measuring $d\ne1$ can
distinguish $\alpha=d+1$ from a fixed $\alpha=2$ baseline. It is not the only
discriminating test. Complete profiles, independently specified applicability
conditions, and predicted responses to interventions can distinguish hypotheses
even when $d=1$. A successful novel prediction must also be compared with
credible alternatives: Zipf behaviour can arise from other models, including
the latent-variable construction of
[Schwab, Nemenman and Mehta (2014)](https://doi.org/10.1103/PhysRevLett.113.068102).

The flare pilot estimates $d=0.858$ with interval $[0.697,1.054]$, which includes
one. It is a useful test with separately measured size and resource, but does
not establish a non-unit cost exponent. Its reported mismatch concerns the
selected joint allocation, mean-cost, temporal-transfer, and count-distribution
model. The domain was exploratory; the temporal split is not a prospective
replication.

**Novelty and free parameters still require qualification.** Applying equality
to resources is already present in biomass-spectrum work; it cannot be credited
as a new move here without further evidence. Zipf rank-size exponent one gives
count-density exponent two away from cutoffs, and becomes a resource statement
only after defining what resource each object carries. Likewise, a spectrum
$S(f)\propto1/f$ gives constant $fS(f)$ per logarithmic frequency in a declared
band: its resource is the integrated power or variance defined by that spectrum,
not automatically a count of objects. These are useful connections, but rewriting
known regularities does not independently validate their common explanation.

Conditional on a fixed resource law, measure, and domain, the allocation
hypothesis adds no separately fitted abundance exponent. That is more precise
than calling the complete analysis parameter-free: cost exponents, observation
models, and uncertainty may still require estimation. The useful objective is
an independently specified prediction that distinguishes competing accounts,
not merely obtaining a non-unit fitted exponent or a Benford digit histogram.

## What has and has not been accomplished here

This assessment supplies a sharper mathematical restriction, a comparison with
nearby research, and a concrete design with success and stopping criteria. It
does not add an independent dataset, complete the calibration benchmark, establish
a physical mechanism, or turn the existing evidence into confirmation.

The next computational step is the calibration benchmark, followed by one audited
profile-level application. In parallel, a test of the proposed law needs an
independently defined neutral regime and a choice among expected, typical, and
long-time allocation. A convincing negative result or a method that prevents
incorrect conclusions can also make the scientific contribution stronger.
