# Existing-data route for the size-versus-cost comparison

Source and calibration inventory completed: 5 October 2026.

**The Ghedini phytoplankton experiment remains a useful lead.** Independent
respiration measurements were recovered, and the original experiment measured
size within coexisting communities. A discriminating forecast has not yet been
qualified. This audit supplies neither support nor a rejection of the allocation
law, and does not add a registered study.

The [reference-measure design](measure-intervention.md) compares equal resource
per logarithmic size (S) with equal resource per logarithmic physical cost (Q).
They agree under a power cost. The search target is independent cost information
capable of supporting departures from that form, with an observable consequence
in coexisting objects. A published power fit alone cannot rule out such
information in the underlying measurements.

## Recovered calibration

[Ghedini, Malerba and Marshall (2020)](https://doi.org/10.1098/rspb.2020.0995)
estimated community energy flux using separately measured monoculture rates.
Their [archive](https://doi.org/10.26180/5e30e9e2b02b3) contains three workbooks.
Its exact ZIP matches provider MD5 `af61d509937b76cb986d45683eea3617`
and length of 1,879,319 bytes.

After sheet-name and header inspection, checkpoint `51a2f6f` committed the
restricted calibration read before numerical inspection. Only columns A:I of
`species metabolism` were interpreted. The retained
[qualification report](../data/measure-candidates/2026-10-04/ghedini-calibration-qualification.json)
finds:

| Calibration feature | Retained finding |
|---|---|
| Rows and species | 231 rows, six species |
| Conditions | Darkness; dilution levels 10, 30, 70 and 100% |
| Sizes | One fixed volume per species, from 2.002 to 728.969 µm³ |
| Per-cell rate signs | 209 positive, 20 negative, one zero, one missing |
| Bulk/count identity | 230 pairs checked; maximum relative discrepancy 0.004143 |
| Replication fields | No culture, vial, replicate or dark-window identifier in selected columns |

No signed rate was removed. Negative readings do not establish a negative
expected metabolic cost. The bulk/count check measures arithmetic agreement,
not assay precision. Source spelling `synechoccus` is preserved.

The independent source is
[Malerba, White and Marshall (2017)](https://doi.org/10.1002/ecy.2032).
Its methods describe 21 species, two replicate samples, four dilutions of mother
cultures, and repeated dark periods between light treatments. The deposited
respiration sheet contains six species, rather than the complete 21-species
calibration. Thus 231 rows cannot be treated as 231 independent biological
replicates. A bounded repository search found no separately verified download
of the complete calibration. Missing identifiers are an uncertainty problem to
resolve or bound, rather than an automatic exclusion.

## Community measurements

The directly linked original experiment is
[Ghedini, Loreau and Marshall (2020)](https://doi.org/10.1002/ecy.3015), with
[its own archive](https://doi.org/10.26180/5e2a1a8d74be7). This is the same
community experiment, not an independent replication. Its 466,041-byte workbook
matches provider MD5 `6dc5a38875eb1eb9d44d08d7b020b95d`.
Methods describe community-specific microscopy: generally 20 cells per species
at each sampling, fewer when rare. Total biovolume sums species biovolumes.
The [six-sheet header inventory](../data/measure-candidates/2026-10-04/ghedini-original-experiment-headers.json)
identifies species size/density/biovolume, light, oxygen, mortality, nutrients
and derived energy-waste fields. Neither it nor the later paper's 15-sheet
inventory names individual-cell sizes, size ranges or size-variance fields.
Headers establish possible observables, not absence of further information in
unopened rows.

Species counts and mean sizes do not determine actual counts in an interior
size bin. A full profile needs a membership map from individual sizes,
transferable distributions or defensible ranges. Assigning every cell its taxon
mean would test a different representative-trait hypothesis. Six taxa alone are
not an exclusion criterion.

## A narrower observable

Let k be physical cell volume, N total count, and V total cell biovolume over a
fixed domain [a,b]. If physical costs are adequately represented by an
independently calibrated positive, increasing deterministic q(k), the two
continuous allocation rules imply

\[
m_S=\frac{E[V]}{E[N]}
=\frac{\int_a^b q(k)^{-1}\,dk}{\int_a^b[kq(k)]^{-1}\,dk},
\qquad
m_Q=\frac{E[V]}{E[N]}
=\frac{\int_a^b kq'(k)q(k)^{-2}\,dk}{q(a)^{-1}-q(b)^{-1}}.
\]

These follow by taking the first moment of the count densities in the
reference-measure note. Shared total allocation cancels. Power costs give equal
predictions; curvature can separate them. Community-specific mean sizes and
compatible abundance estimates can estimate V without recovering the full size
distribution. This tests one aggregate implication only.

The target is a ratio of expected totals, with an observation and dependence
model for pooled totals. It is not the average of community V/N ratios.
Observed totals must cover the same declared domain as the forecasts.
Calibration mean sizes alone do not bound all community cells; unsupported
extrapolation of q cannot fill that gap.

## Remaining finite gate

1. **Calibrate before community access.** Use positive expected dark-respiration
   cost with an explicit model for signed assay error. Establish sampling units
   or defensible dependence bounds. Compare a power curve with a low-flexibility
   monotone alternative using calibration alone. Validate transfer across whole
   species or independent cultures, not repeated dark windows. A common
   multiplicative density effect cancels from normalized forecasts;
   species-specific changes do not. An across-species mean curve is not a
   measured deterministic cost for every cell. Distinguish biological cost
   variation from assay error, and bound residual taxon/within-size variation
   or specify a joint size-cost model before treating it that way.
2. **Fix observable scope and domain.** Assess the mean-size implication's
   domain support and observation uncertainty. Choose domain, transfer
   assumptions, eligible sampling occasions and a meaningful forecast-separation
   margin before numerical community access. Significant curvature is
   insufficient. Materially overlapping forecast uncertainty means the
   comparison is uninformative.
3. **Freeze and evaluate only if qualified.** Commit costs, domain, moment
   forecasts, observation model and comparison rule before decoding community
   rows. Published summaries have already been seen. A later freeze protects
   computation against outcome-dependent revisions but cannot establish global
   blinding. No documented additive per-cell intervention was found, so these
   archives do not supply the causal −1/−2 response test.

No cost fit, bin assignment, moment forecast or community score was computed.
Reconstructed class energy use would not be an independently measured
allocation profile. Light and nutrient headings alone do not establish a
binding resource or eligible neutrality regime.

## Other screened sources

| Source | Current limitation for this comparison |
|---|---|
| [Fant and Ghedini (2024)](https://doi.org/10.1038/s41467-024-54307-w) | Monoculture/community respirometry is promising; relative density-dependent cost transfer needs qualification. Light/salinity changes do not identify a constant per-cell overhead. |
| [Padfield et al. (2018)](https://doi.org/10.1111/ele.13082) | Power-cost parameters are fitted from the evaluated community flux and size distribution, rather than independent discriminating calibration. |
| [Briddon et al. (2025)](https://doi.org/10.1098/rspb.2025.1146) | Competition histories change multiple traits. No identified additive overhead or qualified monotone size-cost curve was supplied by the screened design. |
| [Kordas et al. (2022)](https://doi.org/10.1038/s41467-022-29808-1) | Direct metabolic calibration is valuable, but the proposed model remains a power at each fixed temperature. Changing exponents alone does not separate S and Q. |
| [SeaFlow methods](https://doi.org/10.1038/s41597-019-0292-2) | Carbon is assigned by a pure-power volume conversion, making S and Q identical. |
| [Huete-Ortega et al. (2012)](https://pmc.ncbi.nlm.nih.gov/articles/PMC3297465/) | Fraction uptake/count ratios use the evaluated counts, so are not independent costs for an unconditional count forecast. |

This bounded screen is complete. Prioritize the recovered Ghedini calibration
and moment observable over expanding an unqualified dataset catalogue.

## Reproduction and exposure

Seven exact metadata snapshots, two provider-checksummed archives, receipts,
inspection plans, header inventories and calibration rows live in
`data/measure-candidates/2026-10-04/`. The directory names the start date;
original-experiment acquisition occurred on 5 October. Both archives retain
community outcome bytes. Numerical community rows remain uninterpreted.
Published results were read; the
[exposure record](../data/measure-candidates/2026-10-04/exposure.json) records
those limits. Header readers may buffer later bytes and parse unrelated shared
strings internally. They stop worksheet parsing at row 1 and emit no numerical
data rows. Tests exercise this boundary with malformed withheld rows and guarded
worksheet access.

```bash
make measure-candidates PY=python3.11    # offline source/header verification
make measure-calibration PY=python3.11  # independent calibration qualification only
PYTHONPATH=src python3.11 experiments/register_runs.py --verify
```

The registry remains 22 studies and 571 file references. The manuscript and PDF
remain unchanged because no new allocation study was evaluated.
