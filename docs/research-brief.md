# Orthopolity: research direction

Established 5 October 2026 from the investigators' clarification of the project's
purpose. This brief sets the active direction for the repository and article.
The [handoff](ongoing-research.md) records execution status; the
[evidence ledger](evidence.md) and individual studies record findings.

## Scientific purpose

The central proposition is that **Nature tends to distribute resources equally
among concentrations of those resources**. The investigators take this tendency
as the starting point of orthopolity. The research task is to give it a precise
mathematical expression, explain its mechanisms where possible, demonstrate its
realizations, and characterize its departures and domain of application.

Earlier development deliberately allowed broad exploration. The present phase
organizes that work toward an article about the principle and the natural laws
it may yield. Repeated assessments of whether the project is worth pursuing are
no longer the organizing task. Specific equations, derivations, and empirical
claims remain accountable to their assumptions and evidence. A failed model is
information about that formulation; a successful example establishes the result
for its stated setting.

## The tendency and the constraints of the system

The proposed principle concerns a resource-equalizing tendency. In an orthopolity
model, the observed distribution is the outcome of that tendency together with the construction of
the system, the surrounding medium, other processes, and initial and boundary
conditions. Many distributions and effective laws can therefore depart from the
equal-allocation form. The programme must explain how constraints shape those
outcomes, including cases in which the tendency has no clear visible signature.

The investigators' gravity analogy captures this distinction. A standing tree
is subject to gravity while its structure and anchorage support it. An apple
thrown upward initially rises while gravity acts; catching it, or its becoming
lodged against a ceiling, supplies an interaction that can prevent its return to
the ground. The observed support or motion does not erase the gravitational
contribution. The analogy distinguishes a physical contribution from the net
outcome of all contributions and conditions.

Human age and height distributions are motivating examples for this constrained
account. An age-distribution model must address birth history, survival, and
migration; a height-distribution model must address development, biological
variation, and environmental conditions, with the sampled population specified.
For an orthopolity application, also identify the resource, concentrations, and
comparison measure. These examples motivate worked explanations; this brief
does not supply completed allocation models of either distribution.

Keep three levels explicit:

1. **Underlying tendency:** the resource-equalizing action proposed by orthopolity.
2. **Neutral signature:** equal resource per declared measure under conditions
   where the specified neutral model applies.
3. **Constrained outcome:** the distribution predicted when the system's
   mechanisms and conditions are included. It need not have a flat resource
   profile or a power-law abundance distribution.

Absence of a clear neutral signature in a particular phenomenon is not, by
itself, absence of evidence for orthopolity throughout Nature. Counting many
non-neutral distributions does not settle that broader question. Each finding
must identify the proposition and physical conditions it actually addresses.
Conversely, explaining a departure requires identifying the relevant constraint
and showing its effect. A failed forecast remains a failed forecast of the
specified model; an unexplained departure remains an open explanatory task.

Develop combined models that predict both the constrained profile and its
response to changing a constraint. Where the model predicts recovery of the
neutral form, derive the conditions and timescale of that recovery. This makes
constraints a central part of the physical theory and its demonstrations.

## Mathematical target

Every application must identify the resource, its concentrations, and the units
among which allocation is compared. A concentration may be an object, a region,
a mode, or an aggregate. Equality among individual concentrations and equality
among classes of concentrations are distinct statements; the choice belongs in
the physical formulation.

For a finite collection of non-overlapping allocation units, let $R_i$ be the
additive resource assigned to unit $i$, with finite expectation, and let $w_i>0$
specify its reference weight. Define $R_{\mathrm{tot}}=\sum_i R_i$. A common
equal-allocation target is

$$\frac{E[R_i]}{w_i}=C,\qquad
C=\frac{E[R_{\mathrm{tot}}]}{\sum_i w_i}.$$

Equal weights express equal expected shares. Unequal weights can represent bin
widths, volumes, or other physically justified measures. They must be specified
independently of the allocation being explained. Expected allocation, realized
allocation, and long-time allocation require separate statements.

For classes indexed by size $k$, the existing
[continuous formulation](concept.md) expresses the neutral allocation form as

$$\mathcal O_\mu(k)=\bar q(k)\frac{dN}{d\mu}(k)=C,$$

where $\bar q$ is mean resource per object and $\mu$ is the declared class measure.
This yields inverse-cost abundance. Under $\bar q(k)\propto k^d$, allocation per
linear size gives $dN/dk\propto k^{-d}$, while allocation per logarithmic size
gives $dN/dk\propto k^{-(d+1)}$. These are existing mathematical consequences to
build on; the physical formulation must explain which comparison is relevant.

The word **tends** also needs mathematical content. Depending on the system,
develop a symmetry statement about expectations, a concentration bound for
typical allocations, a stable dynamical attractor, or a coarse-grained scaling
regime. State which is established in each example. In a dynamical formulation,
define an allocation discrepancy and derive its evolution, stationary states,
and relaxation conditions from the governing equations.

## Six connected lines of work

| Line | Required contribution | Starting material |
|---|---|---|
| Mathematical formulation | Define concentrations, resources, comparison measures, and the meaning of tendency; state propositions and their assumptions | [Concept](concept.md), [resource dimensionality](resource-dimensionality.md), [model formulation](model-study.md) |
| Explanation | Identify symmetries, exchange rules, transport constraints, or other mechanisms that select the allocation and predict its departures | Resource-symmetry and restriction arguments in the [scientific assessment](scientific-assessment.md) |
| Toy models | Demonstrate a mechanism, its approach to the predicted state, and a controlled change that produces a departure | [Model suite](model-study.md), [dependence and restriction benchmarks](research-programme.md) |
| Known physical laws | Derive explicit instances or limits from established equations, including gravity, electromagnetism, relativity, and quantum mechanics where applicable | [Existing transport example and model sources](model-sources.md); broader derivations remain to be developed |
| Positive empirical cases | Show measured resource profiles or predicted responses, with a clear mapping to the relevant proposition | [Size-selected algae](dunaliella-size-budget.md) (budget closure); [ocean and aquatic evidence](evidence.md) (suggestive profiles, unresolved equivalence); [cost transfer](archived-cost-transfer.md) (cost calibration) |
| Departures and boundaries | Establish where the specified relation fails, then derive and test an explanation where the available evidence permits | [Chemostats](chemostat-response.md), [plants](plant-biomass-profile.md), [physical proxies](paper.md), [observation limits](profile-calibration.md) |

Each contribution should connect to an article section. Method calibration and
source audits serve a concrete derivation or empirical case; they should not
become an indefinitely expanding substitute for developing the principle.

## Physical derivations to develop

The following are research tasks, not completed demonstrations.

| Setting | Derivation to pursue | Physical distinction to resolve |
|---|---|---|
| Symmetric exchange and diffusion | Derive stationary resource shares and convergence from an explicit exchange operator; introduce a measured or prescribed asymmetry | Equality per node, per volume, and per size class need not coincide |
| Classical statistical mechanics | Work out resource sharing among degrees of freedom under explicit equilibrium and Hamiltonian assumptions | Equality among modes must be connected explicitly to the proposed concentrations |
| Electromagnetism | Extend the spherical radiation example from its governing conservation equation, geometry, and boundary conditions; include loss or anisotropy | Transported power, field flux, and stored energy require distinct observables |
| Gravitation | Examine Gauss-type field relations and self-gravitating equilibrium or transport models for a precisely defined allocation statement | Identify whether the relevant quantity is mass, field flux, or energy, and whether the comparison uses disjoint regions or nested surfaces |
| Relativity | Formulate any resource current, observer, and integration domain explicitly; derive the proposed relation in a specified spacetime | Determine which conservation or symmetry statement is available in that geometry |
| Quantum mechanics | Examine mode occupations and resource per mode in a specified state or ensemble, including limiting regimes | Separate occupation probabilities from resource-weighted allocations and account for the mode measure |

For each case, supply the governing equations, resource and units, comparison
measure, derivation, equality target, departure prediction, and primary sources.
Record whether it realizes the same allocation statement or a related invariant.
The article can connect several such statements through a broader principle
while keeping their physical meanings explicit.

## Empirical synthesis

Use existing data, consistent with the standing available-data programme. First
synthesize the retained studies around the propositions they address. The algal
study supplies a positive equal-biovolume capacity forecast across separately grown lineages;
the radiation model supplies a transport example; ocean and aquatic spectra
address allocation across size classes. Their roles should be visible in the
argument, with each study's existing evidential status retained.

For departures, separate an observed discrepancy, a proposed explanation, and a
tested explanation. Predict how a restriction changes the resource profile when
its mechanism is available. When the cause is unresolved, state the unresolved
question and the observation or calculation that would distinguish explanations.
Retain negative results, alternative models, exposure histories, and uncertainty.

The completed plankton and respiration-calibration audits remain useful records
of particular routes. Their closure does not block mathematical development,
other physical realizations, or synthesis of the evidence already available.
Revisit those routes only with a specific new source or changed observation
information, as recorded in the [handoff](ongoing-research.md).

## Article structure and immediate sequence

Develop the article around:

1. The physical intuition: resources and their concentrations.
2. A precise principle and its mathematical consequences.
3. Mechanisms and minimal dynamical demonstrations.
4. Realizations and limits within established physical theories.
5. Positive empirical cases and quantitative predictions.
6. System and medium constraints, explained departures, and the resulting scope
   of the principle; introduce the tendency/signature distinction at the outset.

The first substantive deliverable is complete, integrated 6 October 2026:
[class exchange](class-exchange.md) supplies a proved equalizing mechanism,
a constrained fixed point sustained by opposing flows, a recovery bound,
and a reproducible stochastic demonstration. The
[electromagnetic realization](physical-realizations.md) derives throughput,
shell stocks, absorption, and causal recovery, followed by the empirical
evidence map. Manuscript Sections 2.6–2.7 present the results.

The second physical milestone, also completed 6 October, is
[thermal radiation](thermal-radiation.md): classical energy equipartition per
mode, its quantum departure, independent mode counting, and a reproducible
transformation of the published FIRAS spectrum with correlated errors and
explicit reconstruction provenance. Manuscript Sections 2.8–2.9 present it.

Next, connect a mechanism to available data with independently identified
kinetics or constraints, and develop gravity or relativity with a physically
specified comparison measure. Continue
the broader physical programme through actual derivations and primary-source
review. The [handoff](ongoing-research.md) records execution priorities.

Revise the manuscript's motivation and structure as this argument develops;
editorial and theoretical advances do not require a new empirical study.
Change scientific conclusions when the supporting argument or evidence changes,
and regenerate the PDF whenever its Markdown source changes. Registered study
inputs, protocols, algorithms, and outputs remain immutable.

## Working practice

Future work should start from this research direction and the current handoff.
Use criticism to improve an equation, demonstration, explanation, or empirical
claim. Prioritize a coherent physical account and a readable scientific article.
Report what each result establishes, connect it to the central proposition, and
identify the next concrete contribution. Distinguish established results,
working postulates, and proposed extensions without repeatedly reopening the
decision to pursue orthopolity.
