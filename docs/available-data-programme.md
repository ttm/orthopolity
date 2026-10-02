# Resource prediction using available data

2 October 2026. The current research constraint is to use available empirical
data. No new laboratory, field or hardware measurements are planned. Published
experiments and observational records provide the empirical evidence; numerical
models can support prediction and statistical calibration. Earlier experimental
designs remain methodological context rather than work awaiting execution.

This is a metadata-screened research plan, not an executed study or frozen
analysis protocol. No numerical outcome files from the new candidates below
have been downloaded or analyzed. Published summaries and methods have been
read, so any ensuing analysis must disclose retrospective development rather
than claim global blinding. The eighteen existing registry records are unchanged.

## What the available records can test

Resource-cost scaling, allocation response, and recovery are separate endpoints.
A dataset need not support all three to provide useful evidence. Costs measured
in separate cultures can predict resource stocks in a community, with uncertainty
about transfer. External nutrient inputs constrain a dynamical model but do not
by themselves determine internal resource availability or abundance.

Hold out complete vessels, lineages or studies rather than random timepoints.
Parameters learned from development responses are trained parameters, not
independently measured conditions. A held-out unit's pre-intervention profile may
serve as a declared initial condition for a change forecast; that forecast does
not independently predict baseline neutrality.

## Candidate records and their scope

| Candidate | Existing information | Suitable first endpoint | Main qualification |
|---|---|---|---|
| [Nutrient-pulsed chemostats, Dryad 51c59zwj5](https://datadryad.org/dataset/doi:10.5061/dryad.51c59zwj5) | Separate preliminary cellular C/N and volume records; community time series from 24 vessels; documented pulse and dilution | Held-out finite-group resource-stock response | Nutrient trajectories and feeding interactions include fitted latent quantities; only three algal groups are distinguished |
| [Synechococcus cultures, BCO-DMO 926311](https://www.bco-dmo.org/dataset/926311/description) | Chemical C/N/P measurements, cell counts, independently assessed sizes and biological replicates | Cost curves and transfer across strains or temperatures | Separate nutrient-replete cultures supply neither mixed-community allocation nor deprivation/restoration |
| [Dunaliella size-selection study](https://pubmed.ncbi.nlm.nih.gov/30068687/), [Dryad 4mh47r7](https://doi.org/10.5061/dryad.4mh47r7) | Archived size-selection and nutrient-deprivation/recovery records | Recovery forecasts conditional on size and nutrient history, subject to file audit | Separate lineages do not constitute a coexisting size spectrum; direct nutrient costs need verification |

These datasets are complementary tests, not one combined population. In
particular, Synechococcus quotas cannot be transplanted into the taxonomically
different chemostat algae without evidence for that transfer.

Existing [aquatic study transfer](aquatic-study-transfer.md) and
[solar validation](solar-validation.md) remain useful comparisons. The retained
GLOSSAQUA fits do not supply raw resource profiles or paired intervention
trajectories. Solar fluence is directly recorded, but the completed study's
observation gate and instrument-composition limits remain unresolved. More
reanalysis must not silently remove those limits.

## First candidate: audit the chemostat records

The Dryad README names `algae_stoichiometry_preliminary_experiments.xlsx`,
`algae_no-rotifer_chemostat_preliminary_experiments.xlsx` and
`Chemostat_experimental_timeseries.xlsx`. Preliminary records list cellular
nitrogen/carbon, volume and density. Their assay methods and sample separation
must be checked in the [published supplement](https://doi.org/10.6084/m9.figshare.c.8172360)
before treating them as independent resource calibration.

The main time series combines Monoraphidium and Chlorella. For biovolume $A_j$
and a separately calibrated nutrient-to-volume ratio $\rho_j=q_{Nj}/V_j$,
the reconstructed stock is $R_{Nj}=\rho_j A_j$. For the pooled group, carry the
envelope between the two species' calibrated ratios; do not choose a mixture
weight to recover the desired validation profile. Condition-dependent quotas,
transfer uncertainty and correlations in the calibration remain in that envelope.

The supplied `bayesian_predictions*.csv` contain fitted nutrient trajectories.
They are not measured validation inputs. Published top-down-control summaries
also depend on biomass comparisons and require a provenance audit before being
used as explanatory variables. Documented forcing, measured initial state,
separately calibrated traits and development-only kinetic estimates must retain
distinct labels.

With three observed algal groups, the initial target is a finite resource-stock
response, not a broad power-law exponent. Defining logarithmic size intervals
around sparse species representatives does not establish a continuous spectrum.
Any neutrality test requires independently justified size support, observation
coverage and reference weights; otherwise it remains outside this first endpoint.

## Analysis sequence

1. **Retain and audit source files.** Record versions, retrieval receipts,
   checksums, units, assay methods, measurement/inference provenance, pooled
   groups and missingness. Inspect calibration separately from evaluation.
2. **Define development and evaluation units.** Allocate whole vessels using
   identifiers and treatment metadata before examining their response values.
   Prespecify a harder withheld-treatment test if the calibration supports it.
3. **Fit only on development records.** Estimate trait transfer and necessary
   kinetics from the permitted preliminary/development files. Preserve latent
   resource states and unidentifiable parameters as uncertainty rather than
   presenting fitted values as external measurements.
4. **Freeze predictions and comparators.** Compare separately justified resource
   models with baseline persistence and development-only mean responses. Record
   all allowed initial conditions, cost conversions, missingness rules, support,
   tolerances and decision procedures. Do not reuse full-data posterior fits.
5. **Evaluate complete held-out trajectories.** Score composition and absolute
   stocks separately; account for irregular sampling and vessel dependence.
   Use independently simulated observation laws to check uncertainty and useful
   discrimination. If uncertainty remains inadequate, retain an unresolved
   category alongside descriptive forecast scores.
6. **Test another existing study.** Repeat the endpoint that its measurements
   support. Distinguish within-study replication, between-study transfer and
   transfer across different mechanisms; do not treat them as interchangeable.

## Recovery and the broader claim

Recovery toward baseline and recovery toward resource neutrality are different.
A community can return to a nonneutral baseline. A pulse is not automatically a
restriction/restoration cycle, and washout does not guarantee equilibrium recovery.
The observed window can support a return trajectory without establishing its
eventual destination. All these endpoints must be declared separately.

The first attainable claim is that separately calibrated resource traits and
documented forcing predict redistribution in held-out biological communities.
Predicting neutrality from resource budgets is a stronger endpoint, requiring
the relevant independent measurements and an allocation rule that outperforms
its rivals. Missing inputs narrow the claim; they are not supplied by inverting
the abundance spectrum. Eligible systems are selected by measurement and design
criteria, including cases in which every prediction fails.

Executed analyses will receive new identifiers in the [run registry](run-registry.md),
with retained data, algorithms, development/evaluation manifests, frozen
predictions and results. This planning document is not an additional run.
