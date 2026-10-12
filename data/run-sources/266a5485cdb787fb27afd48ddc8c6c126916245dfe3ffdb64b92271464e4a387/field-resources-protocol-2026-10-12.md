# Independently assayed field quotas: conditional stock compatibility

**Local design freeze, 12 October 2026, before calculating numerical field-stock
comparisons.** Commit this protocol, code, configuration, raw sources, metadata
audit and synthetic checks before evaluation. This is a bounded observational
diagnostic, not a prospective experiment or externally registered test.

## Purpose and scope

Can separately measured elemental quotas and ambient cell counts describe a
partial standing stock consistent with matched bulk particulate chemistry?
This qualifies an observation prerequisite for later resource-allocation work.
It does not test equal allocation, establish a new ecological scaling law, or
identify the resource supply available for growth. The reference measure counts
individual cells; no log-size measure or equal opportunities among taxa is
assumed. The measured particulate stock is not a carrying capacity.

Unlike setting quota equal to bulk stock divided by ambient abundance, the
sorted-cell assays divide measured chemistry by **direct post-sort counts**.
Ambient abundance is measured in separate seawater samples. Their combination
is not an algebraic identity, although errors can be shared. Preparation,
fixation, sorting, purity, gating and cell representativeness remain assumptions.
Even exact station/depth/date matches need not represent the same bottle.

## Sources, units and exposure

The retained publisher files and landing pages have SHA256 hashes and download
receipts in `data/field-resources/2026-10-12/acquisition.json`. They are publicly
available, CC BY 4.0, and credited to their original investigators through the
linked metadata:

| BCO-DMO source | Use | Limitation |
|---|---|---|
| [849153](https://www.bco-dmo.org/dataset/849153), Lomas and Martiny, v1, 2 June 2021 | 96 sorted-cell quota records, fmol/cell | Direct post-sort denominator; scarce groups could not always be sorted; live metadata say not validated |
| [829895](https://www.bco-dmo.org/dataset/829895), Lomas and Martiny, v1, 19 November 2020 | NH1418 Pacific ambient cells/mL and bulk C/N/P in micromol/L | Whole-water counts versus filtered bulk; proxy `*_POC_cell` columns are excluded |
| [538091](https://www.bco-dmo.org/dataset/538091), Lomas et al., v2, 5 February 2021 | AE1319 Atlantic ambient cells/mL and bulk C/N in micromol/L | Metadata give POP in micromol/kg: exclude Atlantic P without a density/unit audit |
| [723191](https://www.bco-dmo.org/dataset/723191), Lomas and Twining, v2, 22 February 2018 | Indian Ocean abundance candidate retained | Derived biomass columns are not independent quotas; no row dates |
| [734915](https://www.bco-dmo.org/dataset/734915), Martiny and Lomas, v3, 9 September 2020 | Indian Ocean bulk candidate retained | Underway 3 m sampling does not match quota depths 20–82 m; exclude this join |

The [original study, Lomas et al. (2021)](https://doi.org/10.1038/s43247-021-00212-9)
already analyses field stoichiometry and models taxon contributions to bulk
stoichiometry. We claim neither new measurements nor the first combination of
field quotas and abundance. The contribution here is a reproducible, explicitly
conditional compatibility audit for the orthopolic research programme.

Before freezing, raw CSV bytes were downloaded and parsed as strings to inspect
identifiers, missingness and metadata. Numeric depths and coordinates were
inspected. The published article's findings, ranges and models were exposed.
No raw numerical quota, ambient count, bulk chemistry, stock ratio or score
was displayed or summarized before this freeze. This is not a sealed holdout;
source selection and the scientific question were informed by public methods.

The quota archive concentrates cells on 0.2-micrometre filters and filters sorted
cells onto GF75 material. Bulk archives use GF/F filters. Nominal pore sizes
do not specify an elemental recovery fraction. We do not transfer a published
retention coefficient from another campaign or assume perfect capture.

## Nominal sample matches, fixed before responses

Use only exact reported cruise, station and numerical depth, with a unique
quota identity including date and exactly one bulk candidate at that
cruise/station/depth. Require absolute latitude and longitude differences each
at most **0.02 degrees**, computed with decimal arithmetic. This is a matching
tolerance for rounded locations, not a geodesic distance or evidence that
waters are homogeneous. Compare signed longitude values as supplied; do not
reinterpret the quota metadata's verbal longitude label.

- **Primary:** same reported calendar date. Quota dates lack time zones; no
  conversion to UTC is inferred from bulk timestamp labels.
- **Sensitivity only:** the same identity and coordinate gates, with bulk date
  exactly one calendar day earlier or later. Show these additional rows
  separately and in a combined summary; do not relabel them as primary.
- Quarantine nonunique identities, reused bulk rows, larger coordinate/date
  discrepancies and absent exact depths. No nearest-depth matching, averaging
  across dates, guessed cruise aliases or correction of source coordinates.

The metadata audit predicts nine primary sampling records (eight stations) and
eight additional date-offset records (12 stations combined). All 96 quota rows
remain in the ledger, including other cruises without a qualified bulk join.
The configuration fixes their source row numbers, with header on CSV line 1.
A mismatch stops evaluation before calculating responses.

## Fixed calculation and interpretation

Include only Prochlorococcus and Synechococcus. The sorted eukaryote gate does
not establish correspondence with ambient pico/nanoeukaryote definitions.
For each element with a positive finite bulk value, use each taxon with positive
finite quota and nonnegative finite ambient abundance. Retain missingness and
invalid-value reasons for every omitted term; do not impute missing quotas as
zero. Unparseable or censored tokens are recorded as unparseable, never replaced
by a detection limit. Zero abundance is valid. An all-missing group set is unscored. No C:N:P
ratio is calculated across groups with unequal coverage.

For available groups j and element e, calculate the inferred **partial**
whole-water standing stock, in micromol/L:

`S_e = 10^-6 sum_j N_j [cells/mL] q_je [fmol/cell]`.

The factor combines 1,000 mL/L and 10^-9 micromol/fmol. Missing groups, other
organisms and detritus imply that S is not the complete community stock. It is
a lower partial estimate only conditional on representative, accurate inputs;
sorting's abundance-related missingness is not random sampling.

Let B_e be filtered bulk chemistry. With complete elemental capture and accurate
compatible inputs, the necessary inequality is `S_e <= B_e`. More generally,
if every included group's fraction of elemental stock retained is at least r,
then `r S_e <= B_e`. Report:

- partial/bulk ratio S/B and the descriptive point flag S>B;
- `r_max = min(1, B/S)`, the greatest common minimum elemental retention
  compatible with the inequality;
- `epsilon_min = max(0, (S-B)/(S+B))`, the minimum symmetric relative
  adjustment to the **two aggregate quantities S and B** for
  `(1-epsilon)S <= (1+epsilon)B`.

For valid S=0, report r_max=1 and epsilon_min=0. These are necessary bounds,
not measured recoveries or confidence limits. Other particulate matter consumes
part of B, so the bound can be conservative. Epsilon is not a common error on
N, q and B separately. No tolerance is selected to turn a discrepancy into a
pass; all ratios are reported. No p-values, pooled independent-replicate tests,
fitted retention, calibrated prices, or optimized opportunity weights are used.

Report C and N for both campaigns; P only for NH1418. Summarize primary,
date-offset-only and combined records by element and sample. Depths share
stations; assay errors and selection preclude treating the record count as an
independent inferential sample size. A compatible point comparison establishes
neither closure nor allocation. An excess identifies a joint measurement or
retention requirement, not which input is wrong and not failure of the law.

## Verification and reproducibility

Before real evaluation, synthetic checks cover unit conversion, feasible and
excess stocks, zero counts, missing groups, excluded Atlantic P, duplicate and
mismatched identities, exact tolerance boundaries and date offsets. Run the
metadata stage and commit its output with the sources:

```bash
PYTHONPATH=src python experiments/run_field_resources.py --stage audit \
  --output data/field-resources/2026-10-12/qualification-before-response.json
PYTHONPATH=src python -m unittest discover -s tests -p 'test_field_resources.py'
```

Then evaluate once into a fresh result directory using the recorded freeze:

```bash
PYTHONPATH=src python experiments/run_field_resources.py --stage evaluate \
  --freeze-commit FREEZE_COMMIT --output results/field-resources-2026-10-12
```

Independently recompute selected row arithmetic from decimal source strings
without importing the analysis module; check sample membership, coverage and
all reported flags and summaries. Record any error as an amendment rather than
silently rerunning with new rules. Archive execution sources, update the run
registry without replacing prior records, and state the outcome and its scope
in the results report. Integrate only its scientific implication in the article.
