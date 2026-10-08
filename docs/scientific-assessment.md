# Scientific strength and a concrete route forward

**Role in the current programme:** this document retains dated assessments,
mathematical developments, and study-specific findings. The
[research brief of 5 October 2026](research-brief.md) sets the active research
purpose and priorities; the assessments here describe the work evaluated at
their respective dates.

**8 October geometric-foundation update:** the manuscript now leads with an
exact resource-capacity and complete-hierarchy foundation, developed from the
investigators' nested-box intuition. The [supporting derivation](resource-capacity.md)
proves inverse threshold bounds, equal resource at every complete level,
coverage/overlap corrections and subdivision restrictions on nonlinear
composites. This strengthens the conceptual organization and makes the
mathematical/physical distinction precise. The component accounting facts are
established mathematics; this revision adds no new empirical observation.
The potentially substantial contribution lies in the generalization and
its independently supported consequences, whose scope remains to be established.

**7 October inverse-resource update:** the manuscript now combines the general-law proposal,
worked mechanisms and physical realizations with a conditional identification
and transfer result and an executed inverse-resource application. The
[synthetic demonstration](inverse-resources.md) verifies recovery, uncertainty,
partial identification and instability under its specified model.
The [linguistic comparison](linguistic-resources.md) infers
$Q\propto L^{0.5153}P^{1.8275}$ on calibration genres; its frozen forecast
improves loss over letter power by 0.1843 nats per token in withheld genres.
The lexical baseline remains much better, allocation remains uneven, and
symbolic counts do not identify acoustic or physical effort.

This is a scientific increment beyond reframing: a testable identification
result and a measured predictive gain for a restricted composite. The linear
algebra and exponential-family fitting use established methods; their novelty
is not asserted. The [prior-work comparison](contribution-positioning.md)
locates the proposed allocation framework relative to inverse optimization,
inverse statistical mechanics and linguistic efficiency. The general law's
broader empirical scope and physically identified effective resources remain
open research tasks. Earlier empirical results keep their original status.
The historical verdicts below refer to earlier versions of the work.

Assessment: 28 September 2026; consistency review and external-assessment addendum:
29 September 2026; constructive rereading: 30 September 2026.
Scientific-strength and prior-work addendum: 3 October 2026, before the plant
study's formal evaluation; plant-result judgment appended after evaluation on the same date.
Reference-measure discrimination addendum: 4 October 2026.
Independent respiration-calibration result: 5 October 2026.
This is a research assessment and proposed design,
not a completed validation study or a preregistration. It supplements the
[manuscript](paper.md) and [remaining work](roadmap.md).

## Historical verdict: 28 September 2026

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
| Potential for stronger research | Credible but conditional | A validated method, a substantive theoretical extension, or a successful independent prediction could add scientific content. The constructive rereading below develops the source's hierarchy, versatility, and constraint ideas. |

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

## Constructive rereading of the original sources

The private 2017 essay, *A simple model that explains why inequality is
ubiquitous*, and the [2024 essay](https://ttm.github.io/2024/08/14/power.html)
motivate a broader programme than the current manuscript develops. The earlier
assessment concentrated on making the allocation claim precise and checking its
evidence. That work remains useful, but it underdeveloped the positive theory.
The source intuition is that abundance reflects opportunities to realize units
at different resource costs, while environmental restrictions shape departures.
Its mathematical simplicity does not by itself make that physical interpretation
scientifically empty.

Three developments deserve separate treatment. They are proposed reconstructions,
not results already established empirically by the sources or this repository.

### 1. Capacity, occupancy, and conservative hierarchies

Section 3.1 of the 2017 essay (p. 7) does more than count how many cubes could fit:
it explicitly assumes the same occupancy probability at different sizes. Write
the number of available opportunities at level or class $j$ as $M_j=B/q_j$ and
their mean occupancy probability as $s_j$. Then

$$E[N_j]=s_j M_j,\qquad q_jE[N_j]=B s_j.$$

Equal occupancy gives inverse-cost expected abundance. Independence among
occupancy indicators is unnecessary for this expectation identity. The physical
content is whether opportunities and occupancy really have the stated structure.
Measuring both independently would turn the source's geometric intuition into a
test; defining occupancy afterward as observed abundance divided by capacity
would not. If the classes compete for one disjoint budget $B$, their simultaneous
occupation must be feasible: the full capacity $B/q_j$ cannot be realized in
every class at once. For this simplified model, the expected budget already
requires $\sum_j s_j\le1$; further geometric constraints may apply.

The source examples also suggest a different, exact case: a complete conservative
hierarchy. At each level $\ell$, the units partition the same underlying resource,
so $\sum_i q_{\ell i}=B$. In a balanced $b$-ary hierarchy with equal resource
subdivision,

$$N_\ell=b^\ell,\qquad q_\ell=B b^{-\ell},\qquad
N_\ell q_\ell=B.$$

Here capacity is realized by the partition itself. Every level represents the
same total resource, and counts vary inversely with unit cost. Geometric spacing
of costs makes levels equally spaced in log cost. Without such spacing, equal
resource per level does not imply equal resource per log interval. Unequal
partitions preserve each level's total but need not produce a simple pooled
size spectrum.

This is a structural explanation for a specified class of representations.
Different levels reuse the same underlying resource; summing them as though they
were disjoint physical allocations would double count it. Complete hierarchies
and competing populations therefore need different sampling models. The
hierarchy identity is elementary and is not claimed as new mathematics; its
value here is to recover a legitimate part of the intuition and an independently
specifiable applicability condition. The original examples do not establish
that arbitrary collections of household objects form such a hierarchy.

### 2. Versatility as a conditional allocation model

Section 5 of the 2017 essay (p. 10) proposes that a broad range of engagements
can support sensing and group versatility. One explicit development is to model
representation across $K$ predefined task or cost classes through positive,
continuous counts or expected counts $N_j$. For costs $q_j>0$ and budget $B>0$,
consider the objective

$$\max_{N_j>0}\sum_{j=1}^K\log N_j
\quad\text{subject to}\quad \sum_j q_jN_j\le B.$$

This rewards representation of every declared class with diminishing returns.
The first-order condition $1/N_j=\lambda q_j$ and the binding budget give

$$N_j=\frac{B}{Kq_j},\qquad q_jN_j=\frac{B}{K}.$$

Thus the source's versatility idea admits a precise conditional route to equal
resource allocation. The objective maximizes the geometric mean of representation;
it does not prove a general statement about maximizing the occupied size range.
Logarithmic utility is an additional assumption, not a consequence of ignorance
or conservation. Other utility functions need not give the same allocation.
The result concerns a continuous relaxation, not exact integer populations or
guaranteed occupancy in individual realizations. Class choice matters: splitting
one class into two equally weighted classes changes the objective.

This is established proportional-fairness mathematics; see
[Kelly, Maulloo and Tan (1998)](https://doi.org/10.1057/palgrave.jors.2600523).
It supplies a constructive precedent, not a new discovery to claim here.
With independently specified positive importance weights $w_j$, maximizing
$\sum_j w_j\log N_j$ gives

$$q_jN_j=B\frac{w_j}{\sum_i w_i}.$$

Changing task importance therefore predicts a change in resource shares, if the
model applies. For several resource budgets $\sum_j q_{aj}N_j\le B_a$, the
same optimization gives, for finite positive budgets, a bounded feasible set,
and strict feasibility,

$$N_j=\frac{w_j}{\sum_a\lambda_a q_{aj}},\qquad \lambda_a\ge0.$$

Each class must have a positive denominator at a finite optimum. Multipliers
are constrained by budgets and complementary slackness; redundant constraints
can make the multipliers nonunique. They express relative
scarcity and convert different resource costs into a common effective cost.
The equality concerns this priced aggregate cost per unit weight, not each
resource separately. This is one principled development of compound resources; multiplying quantities
of unrelated resources without a supported production model is unnecessary.
A scientific contribution would require evidence for the objective and predictions
that improve on existing allocation models.

### 3. Restrictions that predict departures

The source's restrictions can also be developed from a neutral resource reference
distribution. On a finite declared domain with $0<\mu(D)<\infty$, let
$P_0=d\mu/\mu(D)$, $P=dR_1/R_1$, and let $q_1(k),q_2(k)>0$ be the conditional
mean costs of an object in two resources. Accounting gives

$$\frac{R_2}{R_1}=E_P[q_2/q_1],\qquad
\frac{N}{R_1}=E_P[1/q_1].$$

In particular, both resources can be exactly neutral relative to the same
class measure only if $q_2/q_1$ is constant on the occupied domain. Distinct
resource scalings supply a concrete source of incompatibility between neutrality
claims; this is an accounting result, not a new empirical law.

One possible additional model chooses the feasible $P$ minimizing
$D_{\mathrm{KL}}(P\Vert P_0)$. For fixed $R_1$ and an active upper bound
$R_2\le B_2$, an interior solution has

$$dP=Z^{-1}\exp[-\lambda q_2/q_1]dP_0,\qquad \lambda\ge0.$$

The multiplier is set by the measured budget ratio $B_2/R_1$. For logarithmic
classes, $q_1=a k^d$ and $q_2=b k^e$ give

$$\frac{dN}{dk}\propto k^{-(d+1)}
\exp[-\lambda(b/a)k^{e-d}].$$

For $e>d$ the auxiliary restriction suppresses the upper end of the size range;
for $e<d$ it suppresses the lower end. For $e=d$ the resource costs are
proportional and the second budget supplies no additional shape constraint if
feasible. If object count is fixed too, its constraint requires an additional
factor $\exp[-\lambda_N/q_1]$. Appropriate integrability is required; a compact
size interval bounded away from zero avoids the power-law endpoint problems.

This is a proposed closure using standard maximum-relative-entropy mathematics,
not a deduction that physical systems minimize relative entropy. The choice of
reference probability and level of description is substantive; see
[Banavar and Maritan (2007)](https://arxiv.org/abs/cond-mat/0703622).
The versatility optimization and this resource-probability model can yield
different constrained profiles. They are alternatives to assess, not interchangeable
proofs of one uniquely determined physical theory.

An informative test would measure the resource costs independently, change an
auxiliary budget, and predict the new full profile using the changed budget.
For this relative-entropy model, when the costs, primary budget, and domain remain
fixed and no further moment constraints are imposed,

$$\log\frac{dP_{\lambda_2}}{dP_{\lambda_1}}(k)
=\text{constant}-(\lambda_2-\lambda_1)\frac{q_2(k)}{q_1(k)}.$$

The expression presumes the auxiliary-budget constraint is the only varying
shape constraint. Such an intervention can discriminate models even with a unit
primary cost exponent. Restrictions and resource functions must be identified
before observing the target profile; an arbitrary fitted correction can explain
any distribution and makes no prediction.

### Revised assessment of the possible contribution

As written, the manuscript remains a useful critical synthesis with modest
original discovery content and exploratory evidence that does not establish a
broad law. The rereading changes the assessment of its developmental direction:
a statistical calibration paper is one option, but does not exhaust the source.
A theory of neutral allocation, hierarchical representation, and specific
resource constraints is a credible alternative closer to its central ambition.

A strong theoretical contribution would need a substantive new result or a
distinctive explanatory connection beyond the standard identities and optimization
results above. A strong empirical contribution could come from predicting a
departure and its response to a changed restriction on untouched observations,
with comparison against existing accounts. Establishing a broad natural law
requires broader independent evidence still. Neither a microscopic mechanism
nor a non-unit exponent is mandatory for scientific strength.

The focused next step for this theoretical route is to choose one physical
setting, specify how its classes and resources are measured, justify one model
of the restrictions, and derive a prospective prediction. Hierarchy, allocation,
and field or throughput analogies can share a conceptual motivation while
retaining their different observables. Adding all analogies to one evidence
count would not establish universality.

## What has and has not been accomplished here

This assessment supplies a sharper mathematical restriction, a comparison with
nearby research, a concrete design with success and stopping criteria, and
conditional models developing the original intuition. It
does not add an independent dataset, complete the calibration benchmark, establish
a physical mechanism, or turn the existing evidence into confirmation.

For the methodological route, the next computational step is the calibration
benchmark, followed by one audited profile-level application. For the constructive
theory route, it is the focused prediction described above. A test of the proposed law needs an
independently defined neutral regime and a choice among expected, typical, and
long-time allocation. A convincing negative result or a method that prevents
incorrect conclusions can also make the scientific contribution stronger.

## Cross-model programme and broader principle: 1 October 2026

The [first model study](model-study.md), with its [primary-source catalogue](model-sources.md),
develops the dimensionality direction through six stochastic model families,
sixteen allocation scenarios, and a spherical-transport comparison. Constructed
controls are distinguished from independent generative dynamics. The study
recovers parameter-predicted multiplicative and joint-feasibility exponents,
shows the effect of dependence with unchanged resource marginals, and compares
the same preferential-attachment graph through edge incidence and independently
defined wedge counts. The latter approaches log-resource neutrality asymptotically,
with explicit finite-degree corrections. Conservative exchange and random graphs
supply non-flat comparators; compound costs and absorption supply intervention
templates. These results add theoretical compatibility checks, not empirical
confirmation of a general law.

A broader organizing relation is $H(k)=G(k)h(k)$: an intensity or density times an
independently defined resource cost or geometric support. Constant $H$ and a
homogeneous $G$ yield a power law. Allocation, capacity, hierarchy, and transport
can share this form while retaining different physical invariants and measurement
models. The source's light-bulb example is legitimate conserved throughput across
enclosing spheres; its shell-resident stock is equal per linear radial thickness.

An outcome-defined class is legitimate for description and mathematical analysis.
Independent prediction is needed when its defining outcome is offered as evidence
for a more general physical tendency. Selecting power-law ranges and testing an
independently specified resource prediction differs from selecting precisely the
ranges where that prediction holds. A balancing weight can be constructed for
any positive density; identifying a meaningful resource and invariant supplies
the additional scientific content.

The term "cosmological principle" may retain the author's explicit broad
philosophical sense of a proposed principle governing Nature or Reality. That
usage is distinct from the conventional cosmological principle and does not
constrain the project to spacetime-only questions. The general principle and its
derived laws remain hypotheses whose empirical and explanatory standing must be
established. This clarification broadens the constructive programme without
changing the assessment of the existing empirical evidence.

## Executed dimensionality and restriction benchmarks: 1 October 2026

The [follow-up programme](research-programme.md) implements the proposed next
computational steps. Its [dimensionality note](resource-dimensionality.md)
distinguishes cost elasticity $D_q$ from joint-feasibility survival elasticity
$\kappa$. For smooth survival $S$, the exact local bridge is

$$\alpha=1+\kappa-\frac{d\log\kappa}{d\log k},\qquad
\beta=D_q-\kappa+\frac{d\log\kappa}{d\log k}.$$

Only constant elasticity, or suitable asymptotic regularity, removes the
derivative correction. This supplies an operational connection between resource
availability, cost, and allocation while preserving their distinct dimensions.

Twelve dependence scenarios test fixed Pareto marginals, common shocks, Gaussian
and Student joint laws, two/four resources, and capacity ceilings. Exact or
deterministically integrated profiles are compared with separately simulated
outputs and independently trained capacity forecasts. Gaussian and Student
models with the same Kendall dependence have different joint-tail dimensions;
finite-range behaviour differs further. The observed size is still the bottleneck
by construction, so the physical mechanism has not been independently tested.

The [attachment benchmark](attachment-study.md) keeps centered wedges fixed
across five growth kernels and increasing graph sizes. Exact finite references
are restricted to kernels with deterministic normalizers; nonlinear cases receive
limiting or concentration predictions. Full resource totals and excluded tails
remain visible. The [restriction benchmark](restriction-study.md) solves two
budget-driven closures and their distinct intervention responses. Scarcity prices
give proportional fairness an independently budget-determined compound cost and
scale-dependent dimension, conditional on the additional optimization objective.
Slack primary budgets and fixed-primary infeasibility are explicit diagnostics.

The [empirical protocol](empirical-protocol.md) separates cost calibration,
availability measurements, and independently observed unit sizes. It includes
a candidate controlled workload experiment and header-only data templates.
Measurement-specific tolerances, sample-size design, and real validation
observations remain future work. The new work sharpens conditional prediction;
its mathematics draws on established probability and optimization models and
does not yet constitute discovery of a new universal law.

## Predictive reliability and observation design: 1 October 2026

The [next benchmark round](predictive-benchmarks.md) evaluates unknown-family
forecasting, competing resources, and finite-sample discrimination of allocation
models. Its [claim ledger](predictive-claims.md) identifies established results
and the independent evidence needed for a further contribution.

Capacity-only model selection predicts bounded resource profiles accurately in
complete-resource simulations, including a generating family absent from the
candidate list. Accurate bounded forecasts nevertheless fail to identify a
unique unlimited tail dimension. An omitted third resource causes both selected
and nonparametric forecasts to miss the actual output population targets in
all 24 repetitions. These results give the proposed mechanism a concrete failure
condition, while the bottleneck realization itself remains imposed.

Negative coupling of two unchanged Pareto resource marginals gives a feasibility
index greater than two; fully opposed inputs instead yield a bounded neutral
profile whose survival elasticity varies. The finite derivative correction
accounts for that example exactly. Thus input count, cost dimension, and
feasibility dimension coincide only under additional assumptions. Dependencies
do not generally act as a fractional reduction of input count.

The intervention study also supplies an observation-design calculation. Under
its frozen predictions and calibrated unique-acceptance criterion, the first
tested sample size meeting the target is 50,000 uniform objects per cohort or
10,000 resource-proportional opportunities per cohort. These are conditional
requirements for this model comparison. An extra allocation objective or a
miscalibrated cost can make both frozen candidates fail even when forced
likelihood selection strongly prefers one. This distinction preserves failures
instead of turning every observed allocation into confirmation.

All new observations are simulated. The strongest next empirical contribution
would measure costs and availability separately, freeze full-profile and
intervention predictions, and compare them with independently observed outcomes.
Testing whether a declared natural regime selects resource neutrality remains
an additional endpoint beyond successful feasibility prediction.

## Executed controlled measurement pilot: 1 October 2026

The [workload pilot](workload-pilot.md) adds actual measurements to the resource
prediction programme: 72 fresh-process calibration tasks followed by 672
validation task attempts under four assigned memory/CPU quota conditions.
Calibrated costs, complete forecasts, quota pairings, analysis code hashes,
and exploratory error tolerances were saved before validation. Each observed
size is the largest numerically verified, quota-completed workload in a fully
executed fixed grid; no fitted inverse cost supplies its observed value.

The paired-calibration forecast's maximum absolute survival errors are 0.0238,
0, 0, and 0.0357 in aligned, opposed, permuted, and CPU-tightened conditions.
All are within the frozen conditional tolerance of $1/28$. Reversing quota
pairings removes completion at the three largest sizes despite unchanged quota
marginals. Single-resource forecasts miss opposed profiles by up to 0.4286;
an independent-budget approximation misses them by up to 0.1837. These are
finite-profile prospective errors on one machine/session, not a guarantee of
equivalence or generalization.

The outcome criterion explicitly applies both quotas, using cooperative
checkpoints rather than operating-system hard limits. Prediction success
therefore supports transfer of measured workload costs and the observation
pipeline. It does not discover the joint-quota rule or show spontaneous neutral
allocation. Median costs and independent resource-cost replay remain competitive
in this design, so no unique cost-dependence law is identified. Total peak RSS
includes substantial process overhead; neither its scaling nor the completion
spectrum establishes an unlimited resource dimension.

The [fresh-launch replication](workload-transfer.md) now separates transfer of
this original forecast from prospective local recalibration. The stronger
allocation test still needs independently meaningful costs, observed autonomous
allocations, and a restriction intervention whose complete response is predicted
in advance. The pilot supplies a concrete measurement precedent for that study.

## Transfer boundary and retained run history: 1 October 2026

The follow-up collects 72 new calibration tasks and 672 fresh validation
attempts on the same machine/date. It preserves the original numerical quota
pairs, task definitions, forecasts and four exploratory tolerances of $1/28$.
A separate local-cost forecast is frozen before validation and scored against
the same new outcomes. Maximum errors of the original forecasts are 0.130952,
0, 0 and 0.107143. Locally recalibrated errors are 0, 0, 0 and 0.047619. Thus
the original forecast fails two conditions; recalibration recovers aligned
prediction while CPU tightening still fails the unchanged criterion.

The aligned loss of completion at size 1944 is consistent with independently
measured median CPU rising from 0.243998 to 0.261692 seconds, above the unchanged
highest aligned allowance of 0.256198 seconds. The study does not identify the
cause of that cost change. Conditional paired uncertainty supports the aligned
recalibration improvement, but the CPU-tightened gain interval includes zero.
Joint and resource-independent cost predictions still coincide. No uniquely
identified cost-dependence mechanism or natural allocation law follows.

This failure is scientifically useful: a successful first pilot did not predict
stable accuracy across later launches. Independent resource calibration can
improve a prospective prediction without guaranteeing that its cost model
captures all variation. The remaining discrepancy supplies a target for a
declared model extension or different-session replication.

The [central registry](run-registry.md) retains eleven study records with
resource definitions, units, data, seeds, archived algorithms/configurations,
results, hardware metadata and lineage. An earlier calibration attempt failed
a resource-description check before a freeze/validation and remains registered
as incomplete. Retrospective source snapshots and original prospective source
manifests are distinguished; neither local freezing nor Git implies external
preregistration.

A [CPU-allocation protocol](scheduler-allocation.md) moves toward policy-selected
allocation with baseline and opportunity-restriction predictions. It directly
measures class CPU shares, retaining partial-job CPU and overhead, with
calibrated count-times-cost as a secondary check. The current host has 10 logical
CPUs and no independently visible restriction establishing scarcity with three
workers. Its hardware gate therefore prevents actual allocation trials. The
executed competing-model simulations remain conditional constructions. A future
eligible-host measurement could test an engineered allocation policy; a broad
natural-law claim still requires independently defined natural systems and
predictive restriction tests.

## Tests from existing measurements and simulated models: 1 October 2026

The [additional profile studies](additional-profile-tests.md) supply tests
without further workload hardware. A retained NOAA flare catalogue supports
costs-only full-profile prediction from 2022–2023 into 2024, with logarithmic
and linear reference measures and a historical-count comparator specified
separately. Primary count-profile TV errors are 0.167, 0.685 and 0.022,
respectively. The log forecast substantially improves on the linear forecast;
the historical-count advantage over log neutrality is smaller and uncertain
under paired month-block resampling. Measured cost transfer and catalogue
missingness remain separate diagnostics. This is a retrospective fitting
holdout, and no calibrated resource-equivalence verdict is obtained.

GLOSSAQUA permits prediction of reported slopes in a wholly excluded study.
The fixed −1 location has better descriptive scores than the training-estimated
location, but primary nominal 95% coverage is only 66.96%. Directly reported
standard errors give 103 records across eight studies; confidence-interval
conversion, under an unverified 95% assumption, is a separate sensitivity.
Most of the primary relative gain comes from two studies. Source inspection
confirms large reported errors were faithfully copied but does not validate
their uncertainty calibration. These results concern center transport rather
than full resource-profile neutrality or an arithmetic ensemble principle.

A stationary growth/removal simulation gives two populations with the same
population power-law MLE exponent 2 and the same independent physical mass
cost, while their resource profiles differ materially. At 10,000 objects,
92.35% of curved-profile cohorts remain exponent-compatible and 100% fail
the full neutral-profile screen. A changed constant-removal rate also produces
a pure power exponent 2.4 while physical mass cost dimension stays one. The
explicit mechanisms predict the departures. This establishes a concrete
identification limit for scalar fitted exponents and a calibrated observation
design, rather than discovering a new law or refuting an unrestricted regime
whose applicability has not been independently specified.

The studies improve the scientific programme through empirical alternatives,
source auditing, fitting separation and explicit power calculations. The
broader principle still needs an independently justified eligible regime and
successful complete-profile/restriction predictions. All data, costs,
algorithms, seeds, predictions and results are retained in fifteen registry
records; the plotting replay adds no independent evidence.

## Executed decision calibration and allocation intervention: 2 October 2026

The [validation round](validation-round.md) now completes a 90-condition
calibration benchmark with 180,000 independently generated evaluation datasets,
a frozen forecast on previously unused 2025 solar records, and an actual
non-unit-resource-cost allocation experiment. The registry retains eighteen
study records with their inputs, algorithms, decisions and lineage.

Calibration is a substantive finding rather than a blanket certification.
Centered simultaneous bands pass the declared dense-bounded operational gate
at 48 independent blocks, but their worst-shape coverage is 93.95%, below the
nominal 95%. Under the serially dependent observation family, twelve blocks
give 43.75% false departures at the true margin. Incorrect detection weighting
at 48 blocks gives 36.80% false equivalence in a just-outside profile; correcting
the observation weighting removes observed false equivalence in that comparison.
Sparse heavy-tail cases can pass a coverage gate by remaining uninformative.
The conservative known-bound reference is valid under its independent bounded
sampling assumptions, which are not supplied by empirical sample maxima.

The solar methods, measured costs, six pooled classes, three forecasts, margin
and application gate were committed before downloading 2025 event values.
Logarithmic neutrality predicts eligible counts better than linear neutrality,
with count TV 0.1248 versus 0.5727; historical counts have TV 0.0216 and a better
point log score whose smaller advantage remains uncertain. The measured resource
profile departs from the fixed practical margin at the point estimate, but its
conditional interval and formal observation gate leave neutrality unresolved.
The instrument mixture also changes between development and validation, so a
cost-transfer change cannot be attributed uniquely to natural flare physics.
Public-data acquisition ordering does not establish external blinding.

The strongest positive evidence is the actual runtime intervention. Independent
CPU calibration yields cost degrees 1.870 and 2.686. Before validation, full
cost curves predict CPU and job profiles under equal and restricted runnable
opportunities. Actual CPU-share maximum errors are 0.0035–0.0063, job-share
TV errors are 0.0021–0.0124, and restriction-response errors are below 0.0078.
Unit-degree and equal-job-service alternatives are poorer descriptive forecasts.
Changed opportunities alter apparent count slopes despite fixed task costs;
measured allocation tilt explains why an abundance slope need not equal the
independent cost dimension. Partial work and unassigned process CPU are retained.

This is a useful independently calibrated forecast in an engineered GIL/OS
allocation system. Its mathematical relation and interval methods are established
tools; no new fairness theorem, spatial dimension, input-count interpretation or
universal natural law follows. A stronger paper can build around the measured
conditional prediction and documented inference failures, after comparing its
scientific increment with the relevant prior work. Natural-system selection of
neutrality still requires independent eligibility conditions, a justified
observation design and predictive responses to measured restrictions.

## Executed available-data tests: 2 October 2026

Three retrospective studies of published measurements add registry records
19–21; no new observations were collected.

The [archived quota transfer](archived-cost-transfer.md) froze four log-quota
models before converting held-out Synechococcus quotas at 25°C. A fixed $d^3$
carbon cost with one fitted intercept transfers best (mean absolute log error
0.133, a typical factor of 1.14). Strain means beat diameter models for nitrogen
and phosphorus. A fitted free exponent never beats the fixed cubic degree, and
extrapolated temperature trends are worst for every element. Cost calibration
can therefore transfer for one resource while failing as a size law for others
in the same cells.

The [chemostat resource-response study](chemostat-response.md) is the first
test of the two-budget allocation rule on measured costs. Separately assayed
pre-pulse N and C per cell volume converted the algal biovolumes of twelve
held-out food-web chemostats into resource-stock proxies. All forecasts were
frozen, with 120 held-out rows gated undecoded.

The pulse redistributed resource composition by 0.25 TV on average, about 1.5
times the pre-pulse variation around baseline. No forecast reduced that error
appreciably:

- development-vessel response 0.243 against persistence 0.247, not
  distinguished;
- transfer from ungrazed cultures worse than persistence;
- equal group stock 0.260.

The two-budget rule, with measured C:N ratios of 7.3–13.6, could move a
vessel's composition by at most 0.05–0.12 TV. Every observed departure was
larger (0.29–0.49). Its parameter-free direction, that the highest-C:N group
loses most share, held in 4 of 12 vessels, the chance count. No vessel
returned to its baseline composition within 12 days.

These results constrain the programme without testing neutrality itself.
Measured cost ratios between coexisting groups can be too similar for a
budget-closure rule to produce the redistribution actually observed. In grazed
communities, short-term allocation is not explained by stoichiometric cost
ratios alone. A test of allocation neutrality still requires an independently
eligible system with directly measured resource stocks, adequate size support
and observed recovery. The failed predictions are retained as evidence.

The [size-budget study](dunaliella-size-budget.md) tests the accounting identity
behind the hypothesis, $N\,q(V)=R$, on 30 *Dunaliella* lineages artificially
selected for size and regrown in one shared medium. Its protocol was frozen
before any small- or large-selected outcome was decoded. Across a 10.4-fold
range of mean cell volume, carrying capacity in total biovolume is constant to
within 3%. Cell number at capacity therefore scales as $V^{-1.02}$.

A pre-frozen equal-biovolume law ($d=1$) predicted each held-out selection
treatment with errors of 0.124 and 0.179 log units. It outperformed a law
fitted within part of the size range and an equal-cell-number law (errors
1.5–2.1). A carbon exponent assigned from *Synechococcus* ($d=0.91$) performed
comparably; the nitrogen exponent ($d=0.80$) did not.

Regrowth after N deprivation nearly restored capacity. After P deprivation,
control and large lineages overshot by 25–31% while small lineages did not.
This is the clearest positive evidence so far that a shared budget fixes total
resource and leaves abundance inversely proportional to per-object cost. Here
that cost is geometric. The lineages grew separately and no quota or binding
resource was measured, so the result supports budget closure, not neutrality
across a coexisting size spectrum.

## Scientific contribution and prior-work comparison: 3 October 2026

This assessment precedes the plant study's formal evaluation and claims no new
plant result. The programme now has stronger conditional forecasts than the
original exploratory analysis, but its present contribution remains **modest
as original science, strong in transparency, and weak as evidence for a general
neutrality law**. The 295 software tests and 21 registered records establish
implementation and provenance; they are not 295 scientific validations or 21
independent confirmations.

The strongest positive case is the [runtime intervention](dimensionality-intervention.md):
separately measured CPU costs predict allocation and its response to changed
opportunities in one engineered mechanism. The [Dunaliella study](dunaliella-size-budget.md)
adds successful transfer of an equal-biovolume forecast across selected lineages.
Its observed near-equality of carrying biovolume is the empirical finding;
the inverse count–volume relation is derived by dividing that biovolume by mean
cell volume, rather than supplied by a second independent count measurement.
The cultures grew separately, and neither a binding nutrient nor per-cell
nutrient costs was measured. The resource-budget interpretation consequently
remains conditional, and the result cannot establish community neutrality.

The [chemostat study](chemostat-response.md) supplies a useful negative result:
the frozen cost-ratio rule fails its score, attainable redistribution and
direction tests, and no forecast improves appreciably on persistence. In
[solar validation](solar-validation.md), logarithmic neutrality beats linear
neutrality on count forecasts, but historical frequencies predict better and
the calibrated observation gate leaves neutrality unresolved. These results
constrain particular hypotheses; they do not support a broad affirmative law.

The mathematics clarifies reference measures, accounting and consequences of
symmetry assumptions. Conservation does not select equal allocation.
Exchangeability assumes a symmetry that must be tested in actual systems, and
the mixture-curvature result applies standard convexity. Useful clarification
does not by itself constitute a new mathematical theory.

Two close predecessors sharpen the novelty requirement. [Marshall et al.
(2022)](https://doi.org/10.1073/pnas.2200713119) independently measured metabolic
scaling in evolved *E. coli* and used it to predict maximum density and
biovolume across resource levels. Cost-to-capacity predictions therefore already
have direct experimental precedents with independently measured costs.
[Fogarty and Small (2014)](https://arxiv.org/abs/1407.5079) developed equivalence
tests for complete functional observations using bootstrap methods. Together
with the ecological spectrum-estimation benchmarks cited above, this means
that whole-profile testing or cost-based forecasting alone cannot establish
methodological priority. This is a targeted comparison, not an exhaustive
priority search.

The forthcoming plant application addresses an important measurement gap:
directly weighed stocks of coexisting plants. However, [Dillon et al.
(2019)](https://esajournals.onlinelibrary.wiley.com/doi/10.1002/ecs2.2856) already
found Weibull distributions superior to Pareto distributions at every site.
Detecting curvature alone would add little. Potential new value lies in an
audited biomass-profile target, transferred forecasts, calibrated observation
limits and the distinction between realized stocks and ecological expectations.
The [documented outcome exposure](next-dataset-audit.md#outcome-exposure-incident)
makes the application retrospective; freezing subsequent scoring prevents
score-driven revision but cannot restore blinding.

The best present framing is a **reproducible critical evaluation of resource
equipartition**, with conditional forecasting successes, explicit counterexamples
and demonstrated inference limits. A stronger original contribution needs
either a discriminating natural-system prediction with independently declared
eligibility, measured costs and adequate independent replication, or a methods
advance that improves calibrated decisions against established alternatives
and changes a substantive interpretation. A deeper mechanism is not compulsory
for a law; independently specified scope and successful discriminating
predictions are. Additional datasets help when they resolve those requirements.

## Plant result and updated judgment: 3 October 2026

The completed [plant study](plant-biomass-profile.md) now observes directly
weighed aboveground stocks among coexisting ramets. It closes the earlier
measurement gap, but does not supply a calibrated test of expected ecological
neutrality. The five Ohio development plots predict five Colorado evaluation
plots after disclosed raw outcome exposure. Logarithmic neutrality ranks second
for realized biomass discrepancy (0.493 TV versus Pareto 0.470); all three
trained models predict counts better than both neutrality templates. Each
evaluation plot favors a different biomass model. These are descriptive
comparisons, without ecological superiority or equivalence inference.

Coverage is consequential: a 112.55 g ramet above the development-fixed 100 g
limit holds 24.50% of one evaluation plot's known mass. Thirty unknown masses
remain explicit. Neither the domain nor these outcomes is changed after
scoring. The q(m)=m conversion defines measured stock and tests no independent
physiological cost law.

The clearest additional methodological finding is that normalized expected
stocks and mean normalized census shares differ. Under iid m⁻² masses on
0.01–100 g, each half-decade bin has 12.5% of expected stock before rounding, but the largest
bin averages only 3.13% of normalized stock at 160 ramets. The mean realized
TV is 0.441. Perfect repeated blocks of twenty produce 97.8–99.9% exceedance
of an iid 95% envelope at counts 160–1280 despite a neutral marginal law.
This illustrates a serious observation-model failure, not measured ecological
dependence or a new statistical theorem. The plant decision remains unresolved.

The overall judgment therefore remains **modest original scientific
contribution, strong transparency, weak evidence for a general natural law**.
The new contribution is an auditable stock/count transfer comparison with
explicit finite-census and dependence limits. A focused critical synthesis or
methods application is defensible; a major discovery or broad confirmation of
orthopolity is not. Further effort should resolve independently specified
eligibility and observation design, or demonstrate a methods improvement
against established alternatives, rather than accumulating weakly identified
examples. Registry size and software test counts remain engineering evidence.

## Reference-measure discrimination: 4 October 2026

The completed [plankton observation audit](plankton-observation-gate.md) leaves
the proposed two-archive ecological test unjustified. The subsequent
[cost-intervention note](measure-intervention.md) advances the design question:
what observation could distinguish competing meanings of resource neutrality?

For independently fixed monotone cost $q(k)$, equal expected resource per
logarithmic size and per logarithmic cost coincide precisely when $q$ is a power
on the declared band. An additive physical per-object cost breaks that
equivalence. Relative to their common power-cost baseline, the predicted
pointwise log abundance response against log cost multiplier has slope −1 for
the size reference and −2 for the current-cost reference. Exact integrated
forecasts allow comparison on fixed bins without midpoint-cost approximations.
The analytic calculator is checked against independent quadrature, unit changes,
bin merging and limits; its examples contain no empirical observations.

This is an explicit experimental-design consequence of established accounting
and change-of-variable ideas, with no claim of mathematical priority. The work
has sharpened a falsifiable conditional prediction. It has not identified an
eligible natural regime, established that the regime survives a cost change,
or supplied an independent measured cost curve with a suitable observation
design. Those empirical requirements determine whether this becomes useful
science about nature. The overall strength assessment therefore remains unchanged.

## Independent curvature calibration: 5 October 2026

The [Ghedini calibration diagnostic](ghedini-cost-calibration.md) executes a
concrete independent-cost qualification, using published monoculture respiration
for six species at four assay conditions. Protocol and algorithms were committed
before fitting; calibration readings had already been exposed. Signed and
missing readings remain explicit, and whole species/conditions are held out.

The frozen gate fails. Under equal-group weights the power-plus-overhead
model effectively ties a power, with near-zero overhead and coincident S/Q
mean-size predictions. Species-RMS weights give real interior predictive gains
and a distinct conditional mean-size contrast, but the two weightings together
give overlapping prediction ranges and a zero minimum paired gap. A weakly
qualified curvature estimate cannot justify unmasking communities to decide
between the reference measures. The numerical community outcomes stay closed.

This adds a reproducible negative calibration qualification to the identification
argument: power costs make the rules indistinguishable, and the reviewed
independent calibration does not supply a robust distinction. It is neither
evidence against every non-power cost nor an allocation-law test. The broader
judgment remains modest original contribution and weak evidence for a natural
law. Another curve or favorable weighting on these same observations would
not strengthen that evidence without a separately declared hypothesis and
independent validation. Close this particular discrimination route pending
additional calibration evidence; retain the completed argument and result.
