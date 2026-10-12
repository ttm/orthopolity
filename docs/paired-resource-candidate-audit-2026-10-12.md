# Accessible resource-measurement candidates, 12 October 2026

The search followed the chemostat diagnosis: obtain resources measured in the
same experimental material as abundance, then evaluate an independent response.
The main distinction is **bulk chemistry versus group-specific, independently
measured cost**. A community total does not identify each species' resource
requirement. A quota calculated using the target abundance cannot independently
predict that abundance.

| Public source | What its metadata establish | Status in this continuation |
|---|---|---|
| [BCO-DMO 1005084](https://www.bco-dmo.org/dataset/1005084) and [1005186](https://www.bco-dmo.org/dataset/1005186) | Same experiment; culture counts and particulate P plus independently assayed single-cell C/N/P | Both complete CSVs, README files and live metadata acquired; [frozen pilot completed unsuccessfully](paired-phosphorus-results-2026-10-12.md) |
| [PANGAEA 961155](https://doi.org/10.1594/PANGAEA.961155), Helgoland mesocosms | Repeated bulk particulate C/N/P and cytometric group observations under temperature treatments | Metadata acquired; chemistry is community-level, not each group's quota; overlapping cytometry categories and changing filtration require an observation audit |
| [BCO-DMO 966570](https://www.bco-dmo.org/dataset/966570/description) and [968692](https://www.bco-dmo.org/dataset/968692/description), Narragansett Bay incubations | Community chemistry and flow-cytometric observations from related temperature/nutrient experiments | Metadata inspected; group-specific costs and an exact sample crosswalk remain to be established |
| [BCO-DMO 849153](https://www.bco-dmo.org/dataset/849153), sorted-cell elemental quotas | Taxon-resolved chemistry from sorted Prochlorococcus, Synechococcus and small eukaryotes across cruises | Promising natural-community route; must find matched ambient abundance and distinguish post-sort counting from the target field count |
| [BCO-DMO 820902](https://www.bco-dmo.org/dataset/820902), phytoplankton phosphorus treatments | Counts, growth and cellular phosphorus under different phosphorus forms/availability | Chemistry at an exponential-growth sampling point does not establish resource capacity or allocation among competitors |
| [BCO-DMO 923159](https://www.bco-dmo.org/dataset/923159/description), Synechococcus proteomes | Repeated relative protein measurements under nutrient and temperature conditions | Relative peak areas do not directly supply absolute resource costs; repeated samples cannot be counted as independent culture replicates |
| [Dryad dz08kps0p](https://doi.org/10.5061/dryad.dz08kps0p), nutrients and herbivore growth | Autotroph/herbivore experiment relevant to cross-trophic stoichiometry | Metadata retained only; no new outcome analysis or eligibility claim |

Only the first pair was downloaded as raw numerical data in this continuation.
No response model was fitted to the other candidates. Their metadata inspection
does not establish that their full files satisfy a future protocol. The
Helgoland and Dryad metadata receipts are in
`data/paired-resource-candidates/2026-10-12/ncedc/`; the directory name records
the searching agent, not a seismic subject. Other rows are primary-source web
metadata leads, without locally retained full data.

The paired-phosphorus archives remove the original access barrier and avoid
deriving quota from the count being predicted. They do not yield a successful
prediction: strict identity/completeness rules leave one calibration and one
test culture, and the independent assay/stock/count relationship fails to
transfer. This is recorded rather than hidden by a new fit or relabelling.

For a stronger natural-allocation test, the sorted-cell field archive is the
most direct remaining candidate because it measures group-specific chemistry.
Before any fit, its sorting denominators, ambient abundance crosswalk, taxon
coverage, resource-budget completeness and opportunity changes need auditing.
Even a successful stock/count check would remain a prerequisite; equal
allocation requires its own specified measure, constraints and prediction.
