# BLOOFINZ-IO: observation gate for a chemical-stock replication

Metadata audit dated **4 October 2026**, before acquisition or inspection of
the candidate's numerical stock outcomes. This is an archive eligibility audit,
not a registered result or a test of neutrality.

**Decision: the proposed ecological replication gate is not met.**
BCO-DMO 956590 provides size-fraction dry mass and chemical analyses from a
subset of tows. Its published nitrogen stocks for all Cycle tows reuse averaged
chemical composition. It therefore does **not** qualify as independent,
directly assayed nitrogen stock on every haul. Shared chemical estimates can
still support inference if their provenance, uncertainty and relation to dry
mass are modeled. The reviewed records do not yet justify that model or the
common sampling scope. A narrower derived-stock analysis remains possible
under an explicit protocol; it would not automatically replicate the proposed
water-column stock target.

The archive is version 1, dated 28 March 2025, covering 31 January–2 March 2022
in the Argo Basin off northwestern Australia. The controlling source is its
[official description](https://www.bco-dmo.org/dataset/956590/description), also
available as the [official methods PDF](https://www.bco-dmo.org/dataset/956590/Dataset_description.pdf).
Exact copies of the [dataset description](../data/law-route/2026-10-04/metadata/bloofinz-description.pdf),
[event-log description](../data/law-route/2026-10-04/metadata/bloofinz-event-log-description.pdf)
and [deployment page](../data/law-route/2026-10-04/metadata/bloofinz-deployment.html)
are retained with a [checksum receipt](../data/law-route/2026-10-04/metadata/acquisition.json).

## What was measured and what was calculated

| Quantity | Observation and processing | Consequence for inference |
|---|---|---|
| Fraction dry mass | Dried material weighed; preweighed filter mass subtracted | A haul-specific gravimetric observation |
| Tow volume and depth | Mouth-mounted flowmeters; hydrowire depth sensor and frame-mounted logger | Documented denominators for converting sampled mass to an integrated stock |
| Elemental composition | Dried material scraped, ground and weighed into EA-IRMS subsamples | Chemical measurements exist, but only for a subset of Cycle tows |
| Published class nitrogen stock | Class dry mass multiplied by averaged class nitrogen percentage | Derived stock with a chemical factor shared across several haul rows |

The processing section is explicit: percentage carbon, percentage nitrogen,
C:N and isotopes were measured in **two daytime and two nighttime tows per
Cycle**, with no transect-station chemical assays. Averages were computed
separately by **Cycle, net type, size fraction and day/night**, with two
observations per average, then applied to all Cycle tow dry masses. The
nitrogen fields are **mg N/m²**, not mg N/m³. These are nitrogen contained in
collected organisms, not measurements of the available environmental nitrogen
budget. [Source: processing and parameter definitions.](https://www.bco-dmo.org/dataset/956590/description)

A schematic reconstruction of the documented processing is

\[
DW_{h,j}=\frac{m_{h,j}D_h}{f_h V_h},\qquad
N_{h,j}=DW_{h,j}\frac{\overline{pN}_{c(h),g(h),t(h),j}}{100}.
\]

Here `m` is the recovered dry mass, `D` the tow depth, `V` the filtered
volume, `f` the analyzed fraction, and the composition mean is indexed by
Cycle, gear, day/night and size class. This is an interpretation of the methods,
not a calculation from outcomes. For the 202 µm nets, the biomass subsample
was one quarter of the original split catch. Dividing the published areal
stock by tow depth would give a derived depth-averaged concentration under
this integration convention; it would preserve the shared chemical factor.
Neither that conversion nor row withholding creates independent chemistry.
Matched dry mass times its own assayed nitrogen fraction can measure stock.
Replacing that fraction by a shared mean requires accounting for uncertainty
and any dry-mass/composition association: a product of marginal means does not
in general estimate the mean of their product. A new chemical assay on every
tow is not a universal requirement.

## Gear, depth and sampling blocks

The 1 m ring net used 202 µm mesh across the full euphotic zone. A 60 cm Bongo
carried separate 202 µm and 50 µm nets across the upper mixed layer. These
are different depth supports. The primary cruise overview specifies nominal
sampling to **150 m for the ring net** and **30 m for the Bongo**, while the
archive retains each tow's measured `Depth`. Gear cannot be pooled merely
because the sieve labels agree. [Cruise overview, methods.](https://doi.org/10.1016/j.dsr2.2025.105564)

Day and night sampling followed a drogued drifter for 3–4 days in each of four
Lagrangian Cycles. Repeated tows describe the same evolving water parcel;
they are not a matching number of independent environments. Day/night
differences were intentionally sampled to estimate vertical migrant biomass.
The archive's `Cycle` field is a **Cycle_day identifier**. A block assignment
must recover its relation to the four experiments instead of treating every
distinct field value as an independent Cycle. The two nets on a Bongo also
have different meshes, so the instrument's generic description of paired
replicate sampling does not establish identical-fraction replicates here.
[Dataset design](https://www.bco-dmo.org/dataset/956590/description),
[cruise overview](https://doi.org/10.1016/j.dsr2.2025.105564).

## Assay and processing uncertainty

The described laboratory system is a PDZ Europa ANCA-GSL elemental analyzer
with a PDZ Europa 20-20 isotope ratio mass spectrometer. Acetanilide, USGS41
and facility standards were used on every run for elemental and isotope
corrections. The available metadata does **not** quantify candidate-specific
nitrogen blanks, detection limits, replicate precision, recovery or covariance
among fractions. The facility's isotope precision is not uncertainty in
elemental nitrogen mass; numerical rounding is not an error estimate.
[Dataset methods](https://www.bco-dmo.org/dataset/956590/description),
[UC Davis solids method](https://stableisotopefacility.ucdavis.edu/carbon-and-nitrogen-solids).

Biomass fractions were rinsed with isotonic ammonium formate to remove sea
salts, then dried at 60°C. Because the rinse contains carbon and nitrogen,
residual reagent and losses during processing are relevant questions for
filter/wash blanks and recovery controls. This is a chemical-method inference;
the audit found no evidence demonstrating an actual bias or its size.
Preweighed-filter subtraction controls filter mass, but alone does not
quantify elemental contamination. [Documented sample preparation.](https://www.bco-dmo.org/dataset/956590/description)

The source flags retention problems in the **50 µm net's** two smallest
fractions: 0.05–0.1 mm may be underestimated and 0.1–0.2 mm overestimated.
Excluding that net removes the specifically flagged fractions; it does not
validate capture or sieving efficiency of the 202 µm net. A quantified
observation calibration suitable for ecological equivalence remains absent.
[Problem description.](https://www.bco-dmo.org/dataset/956590/description)

## Compatibility with MALASPINA

| Requirement | BLOOFINZ-IO assessment |
|---|---|
| Bounded common fractions | Nominal 200–500, 500–1000 and 1000–2000 µm classes agree; omit larger fractions and the 50 µm net |
| Collection threshold | 202 µm mesh versus MALASPINA's nominal 200 µm mesh; sieve bounds are not a measured capture-efficiency curve |
| Depth support | Ring and Bongo strata differ; comparison needs an explicit matching depth population |
| Chemical observation | Many BLOOFINZ rows use a shared nitrogen percentage; row-wise stocks cannot be treated as independent direct assays |
| Organism selection | BLOOFINZ metadata gives no gelatinous-removal rule; MALASPINA removed large gelatinous organisms |

MALASPINA's three bounded common-net classes are the comparison proposed in
the [earlier archive audit](next-dataset-audit.md#complement-chemically-assayed-plankton-size-fractions).
Its open-upper-fraction ambiguity is avoided by ending at 2000 µm. Neither
ending there nor matching labels resolves different depth sampling or
gelatinous selection. The bulk BLOOFINZ stock schema offers no taxonomic
breakdown for retrospectively removing an unmatched organism group.
[MALASPINA Leg 8 methods](https://doi.org/10.1093/plankt/fbt011),
[MALASPINA archive](https://doi.pangaea.de/10.1594/PANGAEA.816451),
[BLOOFINZ methods and schema](https://www.bco-dmo.org/dataset/956590/description).

## What a metadata-only frame can recover

A future explicitly bounded projection could use only these original-schema
fields, leaving every stock and composition field excluded:

```text
Cruise,Tow_ID,Haul,Station,Cycle,ISO_DateTime_UTC,ISO_DateTime_Local,
Time_of_day,Lat,Long,Net_type,Mesh_size,Depth,Tow_Duration,Vol
```

`Time_of_day` is 1 for day and 2 for night. `Tow_ID` counts ring and Bongo
deployments for preservation, biomass and gut fluorescence; `Haul` additionally
counts live-net deployments. The [cruise event-log description](https://www.bco-dmo.org/dataset/943418/description)
could support a deployment join. Neither source identifies the assayed subset
or supplies fraction-specific split records or raw assay-quality controls.

The curation notes name an imported workbook,
`BCO_DOM_BLOOFINZ-IO_mesozooplankton_size_fractionated_biomass_data.xlsx`,
but the described public data-file list links the standardized CSV, not an
original assay workbook. Percentage-nitrogen fields exist; their schema does
not establish whether their presence identifies original assays or copied
means. Inferring assay identities from values would be an outcome-dependent
choice and is not authorized by this audit. [Curation and parameter metadata.](https://www.bco-dmo.org/dataset/956590/description)

## Gate and exposure record

Before treating BLOOFINZ as direct chemical-stock replication, recover a
documented assay-tow mapping, the original fraction assays and an uncertainty
model consistent with the shared means, or equivalent documentation supporting
valid correction and uncertainty bounds. Independently resolve gear/depth
support and organism-selection compatibility. These gaps close the current
two-archive gate; a metadata-only tow projection would not resolve the missing
assay linkage. Four Cycles in one cruise also bound how broadly any successful
comparison could generalize. Absence of raw assay duplicates alone is not a
universal exclusion rule, and the audit does not show that the investigators
lacked quality controls.

This audit opened official description/PDF metadata and primary method
descriptions, not the candidate CSV, tabular data views, ERDDAP numerical
queries or stock-result plots. Search snippets included unrelated published
ecological results; no numerical 956590 stock outcomes were inspected. No
forecast, neutrality finding, simulated calibration or registry entry is
created here.
