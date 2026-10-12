# Field quotas and bulk chemistry: a compatible C/N prerequisite

**Completed 12 October 2026.** Independently assayed cyanobacterial quotas and
ambient abundance imply partial carbon and nitrogen stocks below filtered bulk
chemistry in all **18 primary element comparisons**, from nine nominally matched
sampling records at eight stations. This establishes compatibility with a
necessary stock bound, not complete-community closure, equal allocation, or a
new predictive success for the general law.

The [protocol](field-resources-protocol-2026-10-12.md), raw sources,
metadata-only qualification, code and 13 synthetic tests were committed at
**`52d2cc2` before the numerical comparison**. Public methods and published
findings were already exposed. No model parameters or retention coefficients
were fitted. The [literal frozen result](../results/field-resources-2026-10-12/result.json)
also includes nine Pacific phosphorus comparisons using the archive's stated
unit; **a post-run unit concern prevents their physical interpretation** below.
Neither the frozen calculation nor its selection rules have been changed.

## Available sources and sample identity

The study retains five complete publisher CSVs and their metadata, with receipt
URLs, dates and hashes. It uses Lomas and Martiny's independently sorted-cell
quotas [BCO-DMO 849153](https://www.bco-dmo.org/dataset/849153), Pacific bulk/counts
[829895](https://www.bco-dmo.org/dataset/829895), and the AE1319 part of Atlantic
bulk/counts [538091](https://www.bco-dmo.org/dataset/538091). These are earlier
public measurements, not newly collected data. Lomas et al.'s
[original paper](https://doi.org/10.1038/s43247-021-00212-9) already studies
stoichiometry and models community contributions; this audit does not claim
priority for combining those measurements.

The quotas use direct post-sort counts, distinct from ambient seawater counts.
This avoids defining a cost from the abundance it is supposed to explain.
Preparation and shared cytometry methods still permit systematic errors;
sorting purity and group representativeness are not established by this audit.
Only Prochlorococcus and Synechococcus are used because eukaryotic gates do not
have an established correspondence across files.

Of 96 quota records, nine satisfy exact cruise/station/depth, the same reported
calendar date, and latitude/longitude differences each at most 0.02 degrees.
Eight further records satisfy all but the date, differing by exactly one day;
they remain a separate sensitivity. Three records have larger coordinate
discrepancies, three lack exact depths, six have nonunique quota identities,
and 67 lack a qualified bulk source. These categories are disjoint in the
[full ledger](../data/field-resources/2026-10-12/qualification-before-response.json).
The Indian Ocean bulk source samples 3 m water, unlike quota depths 20–82 m,
and was not joined by proximity. Similar cruise names were not treated as aliases.

Matching published metadata is not proof of a common bottle or aliquot. The
quota dates lack time zones. Date-offset sensitivity does not establish which
date convention is right, and primary same-day status cannot resolve it.

## Conditional stock bound and results

For each available positive quota and nonnegative abundance, calculate

`S_e = 10^-6 sum_j N_j q_je` in micromol/L,

where N is cells/mL and q is fmol/cell. Missing taxa are omitted with explicit
reasons, so S estimates only the included groups' stock, conditional on
representativeness. Bulk B includes other living and nonliving material, but
comes from GF/F filtration whereas counts describe whole water. Complete
capture would require S<=B. If every included group retains at least fraction
r of its elemental stock, the necessary bound is rS<=B.

| Analysis | Element | Scored records | Partial/bulk range | Records with S>B |
|---|---|---:|---:|---:|
| Primary, same reported date | C | 9 | 0.06690–0.43971 | 0 |
| Primary, same reported date | N | 9 | 0.03971–0.27166 | 0 |
| Additional date-offset records | C | 8 | 0.13555–1.05544 | 1 |
| Additional date-offset records | N | 7 | 0.10993–0.81144 | 0 |

Only three of the nine primary records include both cyanobacterial groups for
C and N; the remaining six contain only Synechococcus. Thus these low partial
fractions cannot establish full-community closure or recovery. Missing quotas
are related to difficulty sorting scarce populations. One sensitivity N record
has neither group's quota and remains unscored. All point values, coverage and
omission reasons are retained. Repeated elements and depths are not independent
replicates, and no population confidence interval or hypothesis test is inferred.

The sole C/N excess is Pacific station 7 at 5 m, whose quota and bulk records
are dated 23 and 24 September 2014 respectively. Prochlorococcus alone gives
`161000 cells/mL × 11.21 fmol/cell × 10^-6 = 1.80481 micromol/L`, versus
bulk C of `1.71 micromol/L`. S/B=**1.05544**. Its maximum compatible common
minimum elemental retention is `min(1,B/S)`=**0.94747**. Alternatively, adjusting
the aggregate S downward and B upward by **2.6974% each** reaches equality.
That is the algebraic allowance `(S-B)/(S+B)`, not a measured error bar or
a common error on each underlying count and quota. Other particulate material
would tighten the retention bound. This slight excess in a
date-discordant record identifies no unique mechanism and no rejection of the law.

## Post-run phosphorus unit qualification

The frozen protocol already excluded Atlantic P because its metadata report
micromol/kg while counts and C/N use volume units. Pacific metadata, including
the retained JSON-LD `variableMeasured` record, explicitly label POP
**microMolar (uM)**. The frozen calculation followed that label: it gives three
primary P ratios 0.0001368–0.0005820 and six date-offset ratios
0.0002139–0.0012984, all below one. Its literal summaries therefore contain
21 primary and 21 additional scored C/N/P comparisons, with only the carbon
excess described above.

Inspecting those numerical results exposed a unit concern. Primary Pacific
bulk P values are 17.65, 29.41 and 28.35 under that label, while bulk C is 1.99,
3.01 and 3.96 micromol/L. The implied bulk molar C:P is approximately
0.102–0.140, far below the scale in the original study's stoichiometric analysis.
This is a diagnostic concern, **not proof of the correct replacement unit**.
An nM interpretation would multiply S/B by 1,000, changing physical conclusions
for some sensitivity records. We have neither silently applied that correction
nor accepted the weak bound under the printed label as qualified P evidence.
All nine P comparisons remain unit-unqualified pending source clarification.

This qualification was made after response exposure and is explicitly an
interpretive restriction, not a replacement frozen primary analysis. The C/N
subset and all original values remain visible. The absence of a P claim is not
presented as a preregistered decision. No source author has been contacted.

## Scientific consequence and next discriminating work

These public archives supply independent group-specific costs and nominally
matched abundance. Their primary C/N values clear a conservative stock
compatibility check, a useful advance beyond the failed culture-assay transfer.
The check establishes neither assay accuracy nor a binding resource, and has
limited power because it covers only part of the community.

A natural-community allocation test still needs independently justified
opportunities and constraints, or an intervention predicting abundance changes
from resource measurements without fitting the target. Treating the two named
taxa as equally weighted opportunities would be a new hypothesis, not something
established by sorting their cells. Enlarging the current audit by guessing
aliases, fixing dates, changing units or transferring quotas would not solve
that identification problem. Resolve sampling conventions and phosphorus units
before an expanded field prediction, while keeping this complete audit intact.

## Reproduction

```bash
make field-resources PY=build/main-venv-2026-10-09/bin/python \
  STUDY_OUTPUT_ROOT=build/field-reproduction
make field-resources-registry PY=build/main-venv-2026-10-09/bin/python
```

The first command requires a new output directory and replays the frozen sources;
the second verifies/archives retained artifacts without changing older records.
Independent Decimal verification checks original row membership, term coverage,
arithmetic, flags and summaries without importing the calculation module.
It reproduces **391 numerical quantities** across 43 element records (42 scored,
one unscored), with maximum relative discrepancy **2.98e-15**. Ten additional
synthetic/tamper tests check that altered values, flags, membership, metadata
and summaries are rejected. The verifier establishes computational agreement;
it does not validate the source's phosphorus unit label.
