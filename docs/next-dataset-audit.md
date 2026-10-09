# Next dataset: measured stocks in coexisting size classes

3 October 2026. This completes the dataset-screening step in the
[research handoff](ongoing-research.md). It is an acquisition/methods audit,
not an evaluated study, frozen prediction, or additional registry record.
Published methods and results were read. The plant-source inspection also
exposed raw outcomes, as documented below.

## Decision

**Lead candidate: directly harvested plant dry mass.** It provides individual
measured masses and a census of coexisting objects within each plot. This permits
a direct test of the *realized aboveground biomass profile*. Chemical stocks in
MALASPINA sieve fractions provide a complementary candidate with a different
resource and observation process. Neither dataset measures the independent
available budgets needed to test a resource-feasibility mechanism.

The next work is a plant-specific protocol and implementation, with its
retrospective source exposure declared. Preserve the unused MALASPINA outcome
tables for a separately frozen chemical-stock study. Do not transfer a plant
result, cost law, or error model into the plankton analysis.

## What makes a dataset useful

The classes must coexist within a declared sampling unit. The resource must be
additive and observed without choosing a size conversion to flatten abundance.
Specify class boundaries, size coordinate, reference measure and missing tails
independently of evaluation scores. A complete mass census can satisfy these
requirements even when the resource is also the size coordinate: $q(m)=m$ is
an identity and the class masses remain measured, rather than an abundance-fitted
weight.

Direct stock measurements remove one identification problem; they do not supply
an allocation mechanism. A stock profile alone establishes neither an exhausted
budget nor a limiting nutrient. Also distinguish equality in a realized census
from equality of expected stocks under an ecological sampling process. The
second endpoint needs an observation law and appropriately replicated communities.

## Lead: harvested herbaceous plant communities

[Dillon et al. (2019)](https://doi.org/10.1002/ecs2.2856) harvested all aboveground
plants in five BFEC and five RMBL plots at peak biomass, dried them at least
60°C for over a week, and weighed each to the nearest 0.001 g. Objects are
stems or inseparable stem clusters, generally ramets. Forest and desert masses
use allometry and are excluded. Roots, elemental quotas, limiting-resource
stocks and restoration trajectories are absent.

The [author repository](https://github.com/KerkhoffLab/PlantSizeDist) is pinned
at `defccc3dcbbbf3ba57ff1572377de88fba83ff7f` (10 July 2019). Its import/fitting
scripts use the following fields as masses in grams. Repository metadata reports
no explicit license; public availability does not relicense these inputs.

| Files under `Data/` | Mass field | Suggested role based on locale |
|---|---|---|
| `BFECPrairie1.csv`, `BFECPrairie2.csv`, `BFECPrairie3.csv` | `mass.g` | Development |
| `BFECWetland1.csv`, `BFECWetland2.csv` | `Weight` | Development |
| `RMBLAlpine1.csv`, `RMBLAlpine2.csv`, `RMBLAlpine3.csv` | `biomass` | Evaluation |
| `RMBLGrassSage.csv`, `RMBLWetMeadow.csv` | `biomass` | Evaluation |

This is a proposed whole-location transfer split, **not a blinded holdout** or
a frozen analysis protocol. Ten plots are nested in two geographic locales and
several habitats; ramets are not independent ecological replicates. Use source
file and row for object identifiers rather than inventing biological identities.

Before formal scoring, implement and freeze these choices:

1. Declare the population, units, positivity/missingness rules, mass support,
   log-bin widths and endpoint convention. Preserve every excluded object's
   count and mass and report coverage; empty classes must remain in the profile.
2. Sum measured mass within each class. For a common domain $[a,b]$, the
   logarithmically neutral integrated stock share is
   $\ln(b_j/a_j)/\ln(b/a)$. Linear neutrality instead gives
   $(b_j-a_j)/(b-a)$. These differ even with the same measured resource.
3. Compare both fixed hypotheses with a development-only empirical profile and
   fitted Pareto/Weibull alternatives. Fitting a distribution separately to
   each evaluation plot would describe that plot, not forecast its profile.
4. Score whole profiles, counts and stock coverage separately. Equal plot
   weighting and pooled-mass weighting answer different questions; choose a
   primary endpoint and retain the other explicitly.
5. Develop the observation model on synthetic inputs before choosing any
   equivalence threshold. Include the mass measurement grid, stem grouping,
   dependence and finite counts. Under a count law proportional to $m^{-2}$,
   finite-sample mass shares fluctuate, and normalizing by the random census
   total can introduce bias. Normalized expected stocks and expected normalized
   census shares are different estimands. A flat expected spectrum does not
   imply that every small census is flat. Independent-ramet bootstrapping cannot
   supply uncertainty about ecological replication by itself.

A useful first result can be descriptive forecast scores plus an unresolved
ecological neutrality decision. Neither a low profile error nor a near-zero
fitted slope establishes equal expected allocation without a justified model.

### Outcome-exposure incident

The attempted header-only reader used binary `readline()`, which terminates on
LF. Some source CSVs have CR-only line endings, so the apparent header included
numeric rows and these were emitted into a research agent's tool context.
Exposure is confirmed for `BFECWetland1.csv` and `RMBLWetMeadow.csv`.
Conservatively treat both wetlands and all five RMBL files as exposed. All ten
URLs were requested; prairie outputs contained headers only. The output was
truncated, so its exact row coverage cannot be reconstructed here.

Retrieval was stopped. No outcome summaries, fits or scores were computed and
no raw CSV files were saved. The precise exposure time was not captured; the
incident was reported at **08:03:16 UTC on 3 October 2026**. The reporting time
is not represented as the retrieval time. The
[exposure record](../data/neutrality-audit/2026-10-03/exposure.json) retains the
faulty command and tool-trace identifiers.

Any plant study must disclose this exposure. A later commit can demonstrate
that scoring rules preceded formal evaluation; it cannot establish that plant
outcomes were unseen. Future header readers must terminate on either CR or LF
and be checked against synthetic files with both conventions before acquisition.

## Complement: chemically assayed plankton size fractions

[PANGAEA 816451](https://doi.pangaea.de/10.1594/PANGAEA.816451), from MALASPINA
Leg 8, retains chemically measured N and C and weighed dry mass in mg/m³ by
sieve fraction. Use 200–500, 500–1000 and 1000–2000 µm, collected with the
200 µm net. Exclude 40–200 µm because it uses another net. Exclude the largest
fraction because methods say >2000 µm while metadata labels it 2000–5000 µm.
Large gelatinous organisms were removed. The bounded-domain stock weights for
logarithmic neutrality are approximately `(0.39794, 0.30103, 0.30103)`;
linear weights are `(1/6, 5/18, 5/9)`, not equal thirds.

**Nitrogen is the preferred primary stock.** The
[later full-expedition methods](https://bmourino.webs.uvigo.es/j-plankton-res-2016-mompean.pdf)
report unacidified carbon assays. That warns against calling all measured C
organic; it does not verify the exact Leg 8 pretreatment. Reported isotope
precision is not an error estimate for elemental-stock concentrations.
Net retention, sieve classification and water-volume normalization need a
specific method audit before interpreting catch profiles as water-column
neutrality. Use raw class stocks, not the authors' derived individual-carbon
coordinate. No class counts or opportunity budgets are supplied.

This can test three *operational sieve classes* on a restricted domain. It is
not a full ecosystem spectrum, a count-law test, or a resource-budget prediction.
The numeric outcome table has not been fetched or decoded during this audit.

## Other candidates and exclusions

| Archive | What is observed | Decision and limit |
|---|---|---|
| [PELACUS, PANGAEA 983551](https://doi.pangaea.de/10.1594/PANGAEA.983551) | Gravimetric fraction stocks from spring cruises, 2000–2024; metadata documents sieves up to 5000 µm | Useful dry-mass replication on common-net bins, with whole-year withholding. Chemical C/N and counts are absent; sampling depth and geography vary. |
| [BIOS-SCOPE, BCO-DMO 964826](https://www.bco-dmo.org/dataset/964826) | Chemically assayed particulate C/N, blank-derived uncertainty | Only two contiguous bounded fractions; a missing middle range and open upper tail narrow the domain. Includes nonliving particles. Blank uncertainty is not community replication. |
| [East Pacific Rise, BCO-DMO 948709](https://www.bco-dmo.org/dataset/948709) | Chemical C/N in four bounded particle fractions and an open upper fraction | Particle-stock endpoint only. Few depths/dates and detection limits constrain inference. Linked gene-copy abundance is not object abundance. |
| [Field-sorted quotas, BCO-DMO 849153](https://www.bco-dmo.org/dataset/849153) | Chemical C/N/P per sorted cell | Taxonomic gates lack calibrated size-bin support and ambient counts in this archive. Companion counts require joins and pooled-gate reconciliation; do not invent log widths. |
| [SXRF cells, BCO-DMO 841583](https://www.bco-dmo.org/dataset/841583), [956540](https://www.bco-dmo.org/dataset/956540) | Cell sizes and elemental quotas for selected cells | Selected-cell frequencies lack community abundance weights. Carbon in these records is derived from volume. |
| [Monthly A Coruña, PANGAEA 911575](https://doi.pangaea.de/10.1594/PANGAEA.911575) | Size-fraction C:N and stable-isotope ratios | No retained absolute resource stocks. Ratios cannot supply resource shares. |

These are independent possible studies, not interchangeable inputs for one
population. A negative result from one resource is not repaired by switching to
another resource, coordinate or observation domain after evaluation.

## Retained state and reproduction

[Metadata receipts](../data/neutrality-audit/2026-10-03/acquisition.json) identify
the pinned plant commit/tree, repository metadata and three PANGAEA landing-page
snapshots. Each has its original URL, retrieval time, HTTP metadata, length and
SHA-256. The metadata driver requests only an explicit allowlist; it does not
request CSVs or dataset table views. Other sources above have linked primary
metadata but no retained byte receipt in this checkpoint.

```bash
python3.11 experiments/fetch_neutrality_metadata.py --stage verify
```

Network acquisition is a separate explicit action:

```bash
python3.11 experiments/fetch_neutrality_metadata.py --stage acquire
```

The verified baseline is 295 tests and 21 registered studies with 539 retained
file references. This audit adds no empirical result. No manuscript conclusion
changes at this checkpoint.
