# Orthopolity

The revised [article](docs/paper.md) retains the title **Orthopolity: a general
law of resource allocation** and the ambition to establish it. Detailed
derivations, observation models and full empirical comparisons now reside in
[supporting material](docs/supporting-material.md). `make paper` builds both
PDFs. The [revision map](docs/manuscript-revision-2026-10-11.md) documents the
reorganization and interpretation corrections.

The latest [physics prediction](docs/cantilever-results-2026-10-13.md) forecasts
hot-cantilever thermal motion from colder-condition damping. Ten of eleven mode
fits are physically admissible; their 74.0 K mean error modestly improves on a
78.9 K geometry-only comparator, with large individual failures retained.
The design and forecasts were committed before numerical outcome evaluation;
published findings were already known. This strengthens the account of physical
constraints and failed transfer, without establishing universality. The suite
passes 558 tests; 38 registry entries verify offline. Reproduce with
`make cantilever-transfer PY=python3.11` in a fresh output directory.

Orthopolity expresses the general natural-law principle that Nature tends to
distribute resources equally among concentrations of those resources. The
[mathematical foundation](docs/resource-capacity.md) establishes inverse
resource-capacity bounds and exact inverse count--mean-resource relations across
complete partitions, including nested boxes. The article develops their
physical extension through mechanisms, known laws and empirical evidence.
The general physical scope remains a claim to establish through those connections.
The operative resource may be a nonlinear combination of several constituents.
The framework therefore supports both forward allocation predictions and inverse
inference of effective resources from observed distributions.
The starting points are [Fabbri's 2024 essay](https://ttm.github.io/2024/08/14/power.html)
and the supplied 2017 manuscript by Renato Fabbri and Osvaldo N. Oliveira Jr.

**Status:** [docs/status.md](docs/status.md) connects the registered tests,
current research programme and execution handoff. Work continues on `main`,
with both development histories preserved. The
[resource catalogue](docs/resource-catalogue.md) and
[proportional-growth programme](docs/research-program.md) remain available alongside
the mechanism, resource-transfer and empirical studies below.

**System and medium constraints matter.** The proposed tendency and the observed
distribution are distinct: structure, competing processes, and initial or boundary
conditions can prevent a clear equal-allocation signature. A supported tree or a
caught apple still experiences gravity. Similarly, many non-neutral distributions
do not by themselves establish that orthopolity has no evidence in Nature.
The [research brief](docs/research-brief.md#the-tendency-and-the-constraints-of-the-system)
develops this distinction, including age and height as motivating examples and
the task of predicting how constraints shape distributions.

**Current direction:** the [research brief](docs/research-brief.md), established
5 October and extended 6 October 2026, organizes the work around the general-law
proposal, effective resources and forward/inverse inference. It sets six connected lines of work and an article
structure. Specific derivations and empirical findings retain their stated scope.
The [handoff](docs/ongoing-research.md) records current execution status.

The **9 October dataset continuation** recovered the separately developed
registered-test protocols from Git and [verified accessible data sources](docs/accessible-datasets-2026-10-09.md).
The original [flare-ribbon test](docs/flare-ribbons-run-2026-10-09.md) now runs:
area density exponent 3.163 [2.962, 3.457], excluding both proposed values under
its implemented uncertainty model and yielding the registered verdict
*inconclusive*. Lake polygons, relocated earthquake catalogues and a wildfire
API sample are retained for follow-up designs.

The [lake continuation](docs/lake-gyration-results-2026-10-09.md) is also complete.
Global HydroLAKES gives survival exponent 1.930: it passes the declared ordinary
bootstrap equivalence margin, while spatial equivalence remains unestablished.
A separately frozen UK replication gives 1.441; its spatial interval includes 2.
Both runs retain their original decision rules, limitations and reproduction
commands. The development branch is merged into `main`.

The [local-geometry and catchment follow-up](docs/lake-metric-followup-results-2026-10-09.md)
weakens that original agreement: ζ = **1.859**, iid interval [1.844, 1.874],
catchment interval [1.785, 1.924]. The spatial interval excludes exact 2 but
overlaps the [1.9, 2.1] equivalence band; the frozen decision remains
**inconclusive**. Two local projections agree closely. Incomplete basin coverage,
invalid source topologies and an iid adequacy diagnostic further qualify inference.

The [seismic qualification](docs/seismic-qualification-results-2026-10-10.md)
has also run on available Southern California catalogues. Of 40 sequences with
enough raw events, **six** pass quality, completeness and location-resolution
gates; the registered minimum is ten. The test stops before b or D2 fitting and
does not favour either hypothesis. Source bytes, exclusions and deterministic
samples are retained for reproduction.

A [new source audit](docs/seismic-candidate-audit-2026-10-10.md) acquired complete
Italian CLASS/HORUS and Northern California catalogues. It links 295,193 Italian
records to magnitude provenance while quarantining ambiguous identifiers. Only
699 have direct moment-tensor provenance, so a viable comparison needs validated
proxy calibration and a frozen physical sequence definition before fitting.
The [Italian magnitude validation](docs/italian-magnitude-validation-results-2026-10-10.md)
now fails its synthetic prerequisite: 45 of 56 required cases fail, including
30 of 32 noiseless proxy cases. Converted magnitude bins invalidate the original
uniform-bin estimator in these scenarios. The bounded attempt stops before real
Italian sequence construction or response fitting; neither physical hypothesis
is favoured. The manuscript incorporates these limits and the completed geometry tests.

The **8 October biological mechanism and transfer** now connects growth/division
to mass allocation across logarithmic cell sizes. A known lineage/population
sampling relation determines the constraint envelope from birth measurements.
In a [published-summary comparison](docs/cell-division.md), birth-calibrated
predictions match separate bacterial population mean lengths within 2.72% and
0.447%, without target fitting. Variability is overpredicted; the declared
two-endpoint superiority criterion is not met. The study retains all four
forecasts and explicitly treats length as a mass proxy.
Replay it with `make cell-division PY=python3.11`.

The **8 October geometric foundation** makes the elementary box argument explicit:
each complete subdivision represents the same volume, with more units at smaller
volume per unit. A coverage theorem handles missing and repeated resource accounting.
It also restricts which nonlinear effective resources can remain unchanged when
objects are subdivided. These are exact mathematical results with stated premises;
coexisting size classes require their own allocation conditions.

The [effective-resource formulation](docs/effective-resources.md) explains
nonlinear composition, constituent budgets, and what a distribution identifies.
A worked inverse example recovers a composite resource from two environments
and predicts a third. The manuscript also develops city-size Pareto/Zipf scaling
as a conditional inverse target, with its comparison measure and domain explicit.

The **7 October inverse-resource study** now supplies a general identification
and transfer result, correlated uncertainty and conditioning bounds, and a
[reproducible synthetic demonstration](docs/inverse-resources.md).
The [linguistic application](docs/linguistic-resources.md) infers a combined
letter/phoneme cost from three genres and freezes it before evaluating two
withheld genres. Its prediction improves over fitted letter power by 0.1843
nats per retained token; a lexical frequency baseline remains much stronger,
and observed resource allocation remains uneven. This is a completed inverse
application with an explicit predictive gain and explanatory limits.
The article distinguishes rank-frequency Zipf scaling from letter expenditure
over word types, and compares its contribution with
[established inverse methods](docs/contribution-positioning.md).

Reproduce the new studies offline with
`make inverse-resources linguistic-resources PY=python3.11`.
The retained registry now contains 33 records and 813 file references.
All 480 tests pass, including magnitude-estimator validation, source identity checks, seismic qualification and local lake geometry
checks. Earlier detailed empirical accounts remain available in
[the supporting report](docs/empirical-studies.md); their conclusions are
unchanged.

The [scientific manuscript](docs/paper.md) now includes the first complete
mechanism demonstration and a worked physical realization (6 October revision).
The [class-exchange study](docs/class-exchange.md) proves equalization, derives a
nonuniform state in which neutral and constraint flows cancel, and predicts
recovery after release. Its simulation preserves resource and verifies the
convergence bound across all three phases. The
[electromagnetic derivation](docs/physical-realizations.md) establishes equal
radial throughput and equal energy per radial thickness, with absorption and
causal recovery, then maps the retained empirical successes and departures.
The [thermal-radiation study](docs/thermal-radiation.md) now derives equal classical
energy per mode and its quantum departure, then expresses the published FIRAS
spectrum in those physical units. It retains all 43 channels, correlated
uncertainties, original fitted residuals, and the product's reconstruction
assumptions. Reproduce it offline with
`make thermal-radiation PY=python3.11`.
The [scientific-strength assessment](docs/scientific-assessment.md) develops the
resource-symmetry argument, a concrete research design, and a stronger mathematical
restriction on ensemble averaging.

The [model comparison study](docs/model-study.md) develops a shared resource and
geometry formulation and compares constructed allocation models with preferential
attachment, random graphs, conservative exchange with saving, multiplicative growth,
dependent resource feasibility, and spherical radiation. Six stochastic model families
produce 16 allocation scenarios plus a transport comparison. These simulations test
mathematical compatibility and prospective prediction templates; they are not new
empirical evidence for a universal principle.

The [follow-up research programme](docs/research-programme.md) separates resource
cost from joint feasibility and tests predictions under changed dependence,
attachment dynamics, and resource budgets. It includes an
[independent empirical protocol](docs/empirical-protocol.md) with calibration and
observation templates. Its first controlled implementation is the
[measured workload pilot](docs/workload-pilot.md): separate cost calibration,
frozen forecasts, and later execution under assigned memory/CPU quotas. This
tests operational cost-model transfer; autonomous resource allocation remains
an empirical question.

The [fresh-launch comparison](docs/workload-transfer.md) found a transfer
boundary: the original forecast fails its unchanged tolerance in two of four
conditions; local recalibration recovers one. A [central run registry](docs/run-registry.md)
retains inputs, algorithms, seeds, outputs, hardware facts and lineage, including
an incomplete attempt. The [CPU-allocation protocol](docs/scheduler-allocation.md)
adds discriminating intervention predictions; the current host does not meet
its scarcity requirement, so its allocation results remain conditional simulations.

[Additional tests on retained data](docs/additional-profile-tests.md) evaluate
solar full-profile forecasts across years, aquatic slope predictions across
entire excluded studies, and growth/removal simulations with matching fitted
exponents but unequal resource profiles. They add empirical discrimination and
an explicit limit on exponent-based identification, with source and uncertainty
caveats retained.

The [validation round](docs/validation-round.md) adds complete-profile decision
calibration, a frozen forecast evaluated on newly acquired 2025 solar records,
and an actual runtime allocation intervention with independently measured cost
degrees 1.870 and 2.686. The runtime forecasts predict full CPU/job profiles
and their restriction response accurately. Solar neutrality remains unresolved;
its formal eligibility rule was fixed before acquisition. Statistical calibration
failures, instrument changes and engineered-runtime scope are retained.

Resume ongoing work from [docs/ongoing-research.md](docs/ongoing-research.md),
which records current decisions, acquisition status and exact next steps.

The [next-dataset audit](docs/next-dataset-audit.md) identifies directly harvested
plant biomass and chemical stocks in plankton sieve fractions for tests of
resource profiles among coexisting classes. It retains source metadata and
measurement limits, including a raw plant-outcome exposure during inspection.
The [plant biomass-profile study](docs/plant-biomass-profile.md) is now complete:
five Ohio plots trained forecasts for five Colorado plots. Logarithmic neutrality
ranks second for biomass (TV 0.493 versus Pareto 0.470), while trained models
predict counts better. Finite-census normalization and dependence calibration
leave ecological neutrality unresolved. A large excluded ramet and all missing
masses remain in the ledger. Prior raw exposure makes this retrospective.

The [scoped natural-law route](docs/natural-law-route.md) next examined chemical
nitrogen stocks in two plankton archives. Its completed
[observation-design audit](docs/plankton-observation-gate.md) does not justify
the proposed ecological equivalence test: relative measurement effects, shared
chemical estimates and sampling compatibility remain unresolved. Six methods
and metadata sources are retained; no raw nitrogen outcomes were evaluated.

A subsequent [cost-intervention design](docs/measure-intervention.md) distinguishes
equal resource per logarithmic size from equal resource per logarithmic cost.
The rules agree exactly for power costs but predict different responses to a
physical per-object overhead: pointwise abundance-response slopes of −1 and −2.
The note and analytic calculator sharpen a conditional test; they add no
natural-system observations or empirical support.

The [existing-data candidate audit](docs/measure-candidate-audit.md) recovered
independent respiration measurements for six phytoplankton species and verified
the linked coexisting-community archive. Community-specific size measurements
may support a narrower mean-size prediction even without individual-cell
distributions. Cost uncertainty, transfer and size-domain coverage still need
qualification. Numerical community outcomes remain unopened; this audit adds
no allocation-law verdict.

The subsequent [respiration calibration gate](docs/ghedini-cost-calibration.md)
is complete and registered. A power-plus-overhead cost improves held-out
predictions under species-RMS weights but ties a power under equal-group
weights. The implied size-log and cost-log mean-size sensitivity ranges overlap,
and some fits make the predictions identical. The frozen gate fails, so this
route does not qualify a community discrimination test. Community outcomes
remain closed; the analysis adds no natural-law verdict.

Further empirical work follows the [available-data programme](docs/available-data-programme.md):
published resource measurements and interventions, separate calibration records,
and evaluation on whole held-out communities or studies. New experimental
measurements are not planned. Its first completed study, an
[archived quota transfer](docs/archived-cost-transfer.md), predicts held-out
warmer Synechococcus cultures. A size-geometric carbon cost transfers within a
typical factor of 1.14; nitrogen and phosphorus quotas follow strain identity
more closely than cell size. The [chemostat resource-response study](docs/chemostat-response.md)
froze forecasts for twelve held-out food-web chemostats before decoding their
post-pulse values. None beat persistence. The two-budget cost-ratio rule failed:
measured C:N ratios cap its redistribution below every observed departure, and
its direction held only at the chance rate. A [size-budget study](docs/dunaliella-size-budget.md)
of size-selected algal lineages regrown in one medium supports the budget
closure behind the hypothesis. Carrying capacity in biovolume is flat across a
10-fold size range, so cell number scales inversely with cell volume. A frozen
equal-biovolume forecast predicts unseen selection treatments best.

The [predictive reliability benchmarks](docs/predictive-benchmarks.md) extend this
programme to capacity-only family selection, training uncertainty, omitted
resources, negative dependence, and calibrated intervention sampling. They show
both successful bounded forecasts and explicit failures, while separating
prediction from identified asymptotic dimension and resource neutrality.

## What the hypothesis says

Choose the objects, an additive resource $q$, a size coordinate $k$, an observation domain,
and a reference measure for the size classes. Equal resource per logarithmic interval means

$$\frac{dR}{d\ln k}=\bar q(k)\frac{dN}{d\ln k}=C.$$

With $\bar q(k)\propto k^d$, this implies a count density $dN/dk\propto k^{-(d+1)}$.
Equal resource per *linear* interval instead implies $dN/dk\propto k^{-d}$.
The difference is substantive: the original essay's uniform allocation does not uniquely
select the logarithmic version used in the ecological analyses.

Conservation alone gives neither hypothesis. Resource symmetry can instead be proposed
as a physical law: exchangeable allocations across declared cost classes imply equal
expected resource shares. A deeper mechanism is optional; empirical support and an
independently specified scope are essential. Equal expectation does not by itself imply
equal snapshots or convergence over time. The [concept note](docs/concept.md) states
the assumptions and counterexamples.

## What the evidence supports

| Source | Finding | Interpretation |
|---|---|---|
| USGS earthquakes | $b=0.998$ versus 1.5 required by the selected energy proxy | Disagreement with that proxy version; not a direct radiated-energy test |
| NOAA solar flares | Predicted exponent 1.858 versus estimated 2.239 on the selected range | Disagreement with the joint resource-scaling and allocation model |
| Published ocean reconstruction | Broad plateau with substantial shape and reconstruction uncertainty | Re-expression of existing evidence; no independent confirmation |
| GLOSSAQUA aquatic spectra | Median normalized biomass slope −1.015, study-block departure interval [−0.100, 0.010] | Location near −1; planned equivalence not established |

The aquatic dataset contains 1,300 estimates from 16 study identifiers, with 78% of estimates
from two studies. Reported-slope tolerance fractions are point-estimate diagnostics, not
fractions of statistically equivalent ecosystems. Known invalid size bounds affect 377
records; corrected sensitivities are reported explicitly.

The earlier claims of a verified ensemble principle, near-perfect failure-rate prediction,
Gaussian adequacy, a decisive two-resource ensemble test, and an 8% temporal-variance bound
have been withdrawn. Mean-zero slopes do not imply a flat mean resource spectrum.
See [the evidence ledger](docs/evidence.md) and [revision audit](docs/source-audit.md).

## Reproduce

Python 3.11 or later is required. A virtual environment keeps dependencies isolated:

~~~bash
python3 -m venv .venv
. .venv/bin/activate
make install
make all
~~~

The pinned analysis dependencies are in [requirements.txt](requirements.txt).
To use an existing interpreter, pass its path, for example:

~~~bash
make all PY=/path/to/python
~~~

The pipeline verifies frozen input checksums, runs the test suite, and regenerates analyses.
Data verification is offline; restoring missing snapshots is an explicit separate action:

~~~bash
make data
make restore-data
~~~

The manuscript typesets to PDF with a TeX installation providing `pdflatex`; no Pandoc is
needed, since `tools/md2tex.py` converts the Markdown subset the manuscript uses:

~~~bash
make paper
~~~

This writes [docs/paper.pdf](docs/paper.pdf), which is committed for convenience; regenerate
it whenever the manuscript changes, so the tracked PDF matches its Markdown source.

Results contain estimated quantities, diagnostic plots, and declared limitations. Successful
reproduction verifies computation from the frozen inputs; it does not validate sampling
assumptions, data labels, novelty, or the physical hypothesis. The historical analysis plan
is preserved in [configs/prereg_2026-09-09.json](configs/prereg_2026-09-09.json);
Git records commit order, not independently verified blinding or external preregistration.

Run the exploratory model study separately:

~~~bash
make models PY=python3.11
~~~

Reproduce the class-exchange demonstration and its manuscript figure, or audit
the retained run and all earlier records:

~~~bash
make class-exchange class-exchange-report PY=python3.11
make class-exchange-registry PY=python3.11
~~~

Reproductions go to `build/reproductions/`; the retained simulation and figure
have separate source/input receipts. The [report](docs/class-exchange.md) gives
the proofs, predictions, executed results, and interpretation.

The earlier exploratory model study uses
[configs/model_study_2026-10-01.json](configs/model_study_2026-10-01.json).
Retained results, profiles, and figures are in `results/models/`; new reproductions
write to `build/reproductions/models/`. The model source
catalogue records which predictions are exact, asymptotic, or approximate.

Run the three follow-up benchmarks together, or use the `dependence`, `attachment`,
and `restrictions` targets separately:

~~~bash
make followup PY=python3.11
~~~

Configurations are in `configs/`; retained outputs are in `results/dependence/`,
`results/attachment/`, and `results/restrictions/`. New reproductions write to
the corresponding directories under `build/reproductions/`. The research programme links
the theory, model-specific reports, and empirical design.

Run the predictive-reliability and observation-design benchmarks:

~~~bash
make robustness PY=python3.11
~~~

Retained results are in `results/competition/`, `results/forecast/`, and
`results/interventions/`; reproductions write under `build/reproductions/`.
They generate simulated observations; no independent
natural-system validation is implied by successful reproduction.

Analyse the recorded actual workload measurements:

~~~bash
make workload-report PY=python3.11
~~~

The [pilot report](docs/workload-pilot.md) links 72 calibration and 672 validation
task attempts, the prediction freeze, and the numerical results. To collect a
new hardware/session replication, use a new measurement and output directory
as described there. Existing measurements and frozen predictions are preserved.
Reanalysis writes under `build/reproductions/workload-pilot/`, preserving the
registered result bytes. Set `STUDY_OUTPUT_ROOT` to another fresh destination
to direct model/workload-pilot reproductions elsewhere.

Inspect the completed transfer comparison and audit the retained runs:

~~~bash
make workload-transfer-report registry-verify PY=python3.11
~~~

The [transfer report](docs/workload-transfer.md) gives commands for a new
collection with original quotas, a prospective local comparator, and its own
data/output directories. `make scheduler-allocation PY=python3.11` reuses the
retained gate/design and checks eligibility before any actual trial. The
[allocation protocol](docs/scheduler-allocation.md) explains the current
hardware qualification and commands for collection on an eligible host.

Reproduce/reuse the additional empirical and simulation tests:

~~~bash
make profile-tests profile-test-registry registry-verify PY=python3.11
~~~

The [comparison report](docs/additional-profile-tests.md) links specifications,
raw-input membership records, frozen predictions, results and limitations.
The registry now retains eighteen records, including incomplete attempts and
a simulation replay that adds no independent evidence.

Audit/reuse the new calibration and measured validation studies offline:

~~~bash
make validation-round validation-round-registry registry-verify PY=python3.11
~~~

The solar protocol was committed before downloading its validation year. The
runtime audit reuses measured timings; collecting another realization requires
a new run. The calibration data retain all outer statistics, seed recipes,
and example full inputs; inner bootstrap draws are reproducible computations.

## Repository guide

| Path | Purpose |
|---|---|
| [docs/research-brief.md](docs/research-brief.md) | Active scientific purpose, mathematical target, six lines of work, and article structure |
| [docs/class-exchange.md](docs/class-exchange.md) | Proved class equalization, constrained equilibrium, recovery bound, stochastic simulation and reproduction |
| [docs/physical-realizations.md](docs/physical-realizations.md) | Electromagnetic transport, absorption, causal recovery, shell stocks, and empirical evidence map |
| [docs/paper.md](docs/paper.md) | Scientific manuscript: formulation, methods, results, limitations, references |
| [docs/source-audit.md](docs/source-audit.md) | Direct assessment of the original PDF and blog, and corrections to this repository |
| [docs/concept.md](docs/concept.md) | Definitions, reference measures, exponent conversions, and ensemble counterexample |
| [docs/evidence.md](docs/evidence.md) | Numerical provenance and current interpretations |
| [docs/value.md](docs/value.md) / [docs/criticism.md](docs/criticism.md) | Reasons to pursue a limited study and limits on its contribution |
| [docs/not-worth-pursuing.md](docs/not-worth-pursuing.md) | Claims and directions the present evidence does not justify |
| [docs/roadmap.md](docs/roadmap.md) | Remaining scientific and submission work |
| [docs/status.md](docs/status.md) | Start here: intent, history, results, assessment, next steps |
| [docs/preregistered-tests.md](docs/preregistered-tests.md) | Pre-registered tests: status, results, instructions for the pending ones |
| [docs/glossary.md](docs/glossary.md) | Etymology and word forms (orthopolity, orthopolic), reference measures, resource exponents |
| [docs/research-program.md](docs/research-program.md) | Testable formulation, mechanism, prior art, pre-registered tests and falsification criteria |
| [docs/resource-catalogue.md](docs/resource-catalogue.md) | Orthopolic resources inferred for 59 power laws, the rules they follow, and predictions to test |
| [docs/zeta-compilation.md](docs/zeta-compilation.md) | Provisional compilation of published exponents across 49 systems |
| [docs/references.md](docs/references.md) | Annotated literature and primary sources |
| [docs/model-study.md](docs/model-study.md) / [docs/model-sources.md](docs/model-sources.md) | Cross-model simulations, resource interpretations, primary model references, and next discriminating tests |
| [docs/research-programme.md](docs/research-programme.md) | Follow-up theory, dependence and transfer benchmarks, predictive restrictions, and independent empirical protocol |
| [docs/predictive-benchmarks.md](docs/predictive-benchmarks.md) / [docs/predictive-claims.md](docs/predictive-claims.md) | Forecast reliability, identifiability, competing resources, observation design, and claim ledger |
| [docs/workload-pilot.md](docs/workload-pilot.md) | Actual memory/CPU calibration, frozen predictions, executed quota interventions, and replication instructions |
| [docs/workload-transfer.md](docs/workload-transfer.md) | Original forecasts versus prospective local recalibration on 672 fresh outcomes under unchanged quotas and criteria |
| [docs/run-registry.md](docs/run-registry.md) | Append-only study records, source/configuration archives, resources, hardware metadata and lineage |
| [docs/scheduler-allocation.md](docs/scheduler-allocation.md) | Gated measurement protocol, competing allocation predictions and current hardware qualification |
| [docs/additional-profile-tests.md](docs/additional-profile-tests.md) | Solar year transfer, aquatic study transfer, and exponent versus full-profile identification tests |
| [docs/validation-round.md](docs/validation-round.md) | Three-way decision calibration, unused-year solar forecasts, and measured non-unit-cost allocation intervention |
| [docs/plant-biomass-profile.md](docs/plant-biomass-profile.md) | Directly weighed coexisting stocks, geographic forecast transfer, finite-census normalization and dependence limits |
| [docs/scientific-assessment.md](docs/scientific-assessment.md) | Current scientific strength, prior-work comparison and remaining novelty requirements |
| [src/](src/) / [tests/](tests/) | Accounting, distribution fitting, equivalence diagnostics, meta-analysis, and regression checks |
| [experiments/](experiments/) / [results/](results/) | Reproducible analyses and outputs |
| [data/SOURCES.md](data/SOURCES.md) / [data/NOTICE.md](data/NOTICE.md) | Input provenance and source-specific notices |
| [tools/explore.py](tools/explore.py) | Optional inspection and sonification aid; not empirical evidence |

The supplied private manuscript is not redistributed. The earlier wording and results remain
available in Git history; the current documents supersede their interpretation.
