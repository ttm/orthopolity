# Bounded chemistry audit for an allocation intervention

27 October 2026. **No candidate in this bounded search is ready for a new
confirmatory allocation test.** Three source families were examined after six
search queries. Public files exist, but complete independently determined
inputs and independently observed allocations have not both been established.
This is an eligibility result, not evidence against the general law or a claim
that suitable data do not exist.

The intended resource is a declared chemical amount or binding-site inventory;
the comparison measure is physical phase volume or fixed site/species counting,
**neither log-orthopolic nor linear-orthopolic size allocation**. Association
constants are equilibrium constraints, not automatically additive resource costs.
Renaming an affinity or a fitted free energy as the resource would not supply
the independent resource-composition prediction sought in article section 2.3.

## 1. Supramolecular speciation and competitive displacement

**Source:** Soloviev and Hunter (2024), *Musketeer: a software tool for the analysis
of titration data*, [doi:10.1039/d4sc03354j](https://doi.org/10.1039/d4sc03354j).
The [author-repository article](https://api.repository.cam.ac.uk/server/api/core/bitstreams/4d135310-062d-4dc6-aabe-ca93d8da4f3f/content)
is accessible and states that example CSVs and saved fits accompany the paper.
The publisher landing page returned HTTP 403; a numerical supplement download
was not verified in this audit.

This is the strongest chemical lead. Its H-bonded duplex example uses five
separately measured pair/dimer affinities to constrain ten species, but still
fits the duplex affinity and signal coefficients to the denaturation response.
Its competing-ligand example likewise fits an unknown site inventory and a
competing affinity. A modeled species population is not an independent
observation of that population. A qualifying extension would need separate
duplex/observation calibration plus another concentration or denaturant cohort,
with those parameters fixed before its responses. Published fit preferences,
fitted parameters and reported model inadequacies are already exposed; raw
CSV responses and saved fits were not opened.

**Decision:** methods lead, not a selected test. The next bounded follow-up
would establish whether separate calibrations and an additional cohort are
actually deposited. Do not substitute a fit of this same denaturation curve.

## 2. Protein-complex competition with pairwise measurements

**Source:** Zhang et al. (2024), [Quantitative analysis of MBW complex formation
in the context of trichome patterning](https://doi.org/10.3389/fpls.2024.1331156).
The [public repository](https://github.com/MathModelTrichome/MBW-Complex-Formation)
lists reaction-network code, stoichiometric matrices and a complex-combination
table; the paper links supplementary material.

Pairwise binding assays precede competition assays, but absolute protein
concentrations were not determined. Signals are normalized to experiment
maxima, and competition fits allow pairwise affinities to vary inside earlier
intervals. Additional interactions are fitted to the competition observations.
The repository's displayed-complex table is not established as an independently
measured whole-species inventory. The reported failure of the simple competition
model and preference for extensions were exposed during methods review.

**Decision:** fails the present absolute-allocation/independent-observation gate.
It could support a separate binding-signal analysis, but would reproduce the
measurement and model-selection limitations already encountered elsewhere.

## 3. Condensate volume and electrochemical partitioning

**Source:** [Biomolecular condensates regulate cellular electrochemical
equilibria](https://pmc.ncbi.nlm.nih.gov/articles/PMC11490381/), with
[author-deposited data](https://github.com/Dailabwustl/Condensate-electrochemical-potential-of-cell)
and [Zenodo version 1.0.0](https://doi.org/10.5281/zenodo.12769620).
The repository lists figure-specific experimental workbooks. A HEAD request to
the [Figure 1 workbook](https://raw.githubusercontent.com/Dailabwustl/Condensate-electrochemical-potential-of-cell/main/Figure%201_Raw%20Data.xlsx)
returned HTTP 200, content length 12,745 bytes; no workbook cells were decoded.
Zenodo metadata is accessible and declares CC BY 4.0, but returned an empty
file list; its separate file-inventory endpoint returned 403. Thus public
GitHub download availability is verified, not a complete versioned-archive audit.

The published association between condensate volume fraction and cytoplasmic
pH is exposed. It motivates a volume intervention, but pH is an intensive
measurement affected by buffering and protonation. Complete independently
measured ion/buffer inventories, phase volumes, boundary exchange and observation
calibration have not been established here. The living-cell experiment also
does not by itself provide a closed conserved budget. The raw full article
could not be reopened through the browser due to a challenge page.

**Decision:** accessible data, insufficient qualification for the intended
allocation test. No conversion of pH into an unmeasured total proton resource
is justified. A chemically closed in-vitro cohort would require separate
documentation before this lead could advance.

## Search boundary and exposure record

The six searches were: partition coefficient/phase-volume ratio/Zenodo;
competitive binding/mass balance/data availability; partitioning/volume
fraction/data availability/Zenodo/condensates; phase-volume ratio/partition/
dataset/extraction; competitive binding/Musketeer/data/GitHub; and the exact
Musketeer DOI with `suppdata`. Only the three families above received detailed
qualification. Search snippets also surfaced other condensate papers; their
numerical data were not opened or adopted as additional candidates.

The existing zeolite study was not rerun. No numerical target arrays from any
new candidate were decoded, no allocation resource was selected from an observed
exponent, and no fitted correction was treated as an independent input. Published
abstracts, methods, model preferences and some fitted numerical summaries are
known: this is not global blinding. The audit creates no empirical registry run.
