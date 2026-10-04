# Two-archive nitrogen-stock observation gate

4 October 2026. **Do not freeze the proposed two-archive ecological equivalence
study on the evidence currently available.** The finite methods review in the
[natural-law route](natural-law-route.md) is complete. Neither raw nitrogen-stock
table was acquired or evaluated. This is an observation-design decision, not a
test result, a falsification of the allocation hypothesis or a new registry entry.

The proposed target was expected nitrogen concentration proportional to
logarithmic bin width across 200–500, 500–1000 and 1000–2000 µm sieve classes.
It requires a specified sampling population and enough measurement information
to distinguish its profile from alternatives within a meaningful tolerance.
Nominally matching size classes do not establish those conditions.

| Archive | What the review established | What prevents the proposed comparison now |
|---|---|---|
| [MALASPINA Leg 8](malaspina-observation-gate.md) | Elemental N assays, three common-net bounded classes, 43 station events with matching XML/KML coordinates, an investigators' processing manual | Relative class recovery and consequential processing backgrounds are unbounded in the reviewed records; completed corrections and a defensible sampling/dependence model remain unresolved |
| [BLOOFINZ-IO](bloofinz-observation-gate.md) | Haul dry mass, flow/depth measurements, chemical assays on a subset, four Lagrangian Cycles | Published N stocks reuse composition means; assay linkage, representativeness, mass/composition covariance and shared uncertainty are unresolved. Depth and organism-selection rules differ from MALASPINA |

The MALASPINA manual calls for class-specific filtration volumes to be logged.
Its 40 µm-filtered dilution water also leaves a possible particulate background
pathway before GF/F filtration. This identifies an uncertainty to resolve; it
does not demonstrate contamination or quantify a bias. The 43 station events
are not 43 established independent, complete nitrogen samples. The
[retained methods chapter](../data/law-route/2026-10-04/metadata/malaspina-processing-methods.pdf)
and [event metadata](../data/law-route/2026-10-04/metadata/malaspina-panmd.xml)
support the archive-specific audit.

BLOOFINZ measured composition in two daytime and two nighttime tows per Cycle,
then applied means grouped by Cycle, gear, size fraction and day/night to other
tow dry masses. Its stock units are mg N/m². Dividing by depth neither makes
these independent chemical assays nor matches their sampled layers to
MALASPINA's upper 200 m. The [retained processing description](../data/law-route/2026-10-04/metadata/bloofinz-description.pdf)
documents this construction. Shared composition estimates can support valid
inference, but only with justified representativeness and propagated uncertainty;
the mean of dry mass times composition generally differs from the product of
their marginal means.

## Why a precise interval would not settle this

A simple observation model illustrates the issue:

$$Y_{ij}=a_i e_j R_{ij}+b_j+\epsilon_{ij},$$

where $R$ is the target stock, $a$ a catch-wide gain, $e$ relative class recovery,
$b$ an additive processing background and $\epsilon$ random error. This is a
diagnostic model, not a fitted description of either archive. Unknown relative
gains or backgrounds allow different ecological profiles to produce the same
reported profile. Resampling observed rows cannot identify those effects.

A common gain constant across classes and blocks cancels from normalized
expected stocks. A varying catch-wide gain need not cancel from that target if
it is associated with composition. Within-catch normalization cancels a shared
gain but estimates a different quantity when subsequently averaged.

Every raw volume, laboratory duplicate or assay on every haul is **not** required.
Traceably normalized concentrations, a justified error model and adequately
bounded systematic effects can suffice. Mean-zero random assay variation can
contribute to uncertainty across biological blocks. If credible systematic-error
bounds become available, test all compatible corrected profiles: equivalence
requires them all to lie inside the declared margin; otherwise the result may
remain unresolved. Inventing convenient bounds or an arbitrary margin cannot
repair the current gap.

Counts, per-object costs and available resource budgets are not prerequisites
for this stock-pattern endpoint. They would be needed for the stronger claims
about abundance prediction and resource feasibility. Two cruises could test two
declared populations, not universality across ecosystems.

## What would reopen this route

Existing records would need to support:

1. MALASPINA's class corrections and consequential background/recovery bounds,
   through completed sample records or equivalent validated normalization/QC
   documentation, together with an independently declared sampling population
   and dependence model.
2. BLOOFINZ's original assay-to-tow linkage and fraction assays, or equivalent
   evidence sufficient to model the shared chemical factors, their selection
   and mass/composition association. A metadata-only tow listing cannot supply
   that chemical provenance.
3. A defensible comparison of depth, day/night and organism-selection scope,
   fixed before outcomes. Matching bin labels alone cannot supply it.

The bounded public-source review did not locate sufficient evidence. This does
not show that the investigators lacked these records. No investigators were
contacted and no new measurements were requested. The current route is closed
unless additional observation evidence changes this gate. An operational-catch
description could be a separate study, but would not establish the proposed
ecological law; none was executed as a substitute here.

## Reproduction and exposure

Six exact metadata/methods files, URLs, acquisition times, SHA-256 digests and
retrieval failures are retained in the [acquisition receipt](../data/law-route/2026-10-04/metadata/acquisition.json)
and adjacent files. The fixed-URL acquisition driver rejects redirects outside
its metadata allowlist and defaults to offline verification:

```bash
make law-observation-metadata PY=python3.11
make registry-verify PY=python3.11
```

The earlier [public-summary exposure note](../data/law-route/2026-10-04/review-exposure.json)
remains applicable. No new raw nitrogen-stock outcome exposure occurred in this
audit. The 22 registered studies and manuscript conclusions are unchanged.
