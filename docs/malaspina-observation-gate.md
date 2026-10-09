# MALASPINA Leg 8: observation gate

4 October 2026. This is a methods and metadata audit for the
[scoped-law route](natural-law-route.md), not a frozen protocol, empirical result
or registry record. Raw nitrogen-stock observations were not acquired, decoded,
plotted or scored in this audit. The existing public-summary exposure qualification
remains in force.

## Decision

**The gate for expected water-column nitrogen allocation is not met.** The
sources establish chemically assayed size-fraction samples and an intended
processing procedure. They leave class-specific observation effects and the
sampling/dependence model unresolved for the proposed equivalence test.
A descriptive operational-catch comparison remains possible, but would
answer a narrower question and requires its own explicit protocol.

This is a conclusion about the reviewed public evidence, not proof that the
original investigators lacked logs or laboratory quality controls. No new
measurements or contact with the investigators was undertaken.

## Sources and bounded search

The retained [PANGAEA 816451 metadata](https://doi.pangaea.de/10.1594/PANGAEA.816451)
and [earlier source audit](next-dataset-audit.md) identify the chemical variables,
nominal classes and cruise coverage. The previously reviewed
[Leg 8 paper](https://doi.org/10.1093/plankt/fbt011) supplies the actual cruise
methods. Its outcome tables were not reopened for this audit.

A targeted methods-manual search located the original investigators' chapter:
Bode, Fernández Lamas and Mompeán (2012), *Procesado de muestras de plancton para
el análisis de isótopos estables*, pp. 617–622 of the MALASPINA methods book.
The old IEO handle `10508/3314` redirects to the
[official CSIC record](https://digital.csic.es/handle/10261/316565). The
[six-page methods PDF](https://digital.csic.es/bitstream/10261/316565/2/Bode_MalaspinaLibroBlanco_2012_617-622.pdf)
was read, including the processing diagram on p. 621. Its SHA-256 is
`d162ac01b02f728edfb55baa58a88c2f4f790d42bb973991c64cc5d82f476297`
(126,866 bytes). These are method instructions, not completed tow or QC records.

The [NOAA/NCEI companion metadata, accession 0277883](https://www.ncei.noaa.gov/archive/archive-management-system/OAS/bin/prd/jquery/accession/details/277883)
describes Leg 8 amino-acid isotope acquisition and pooling. It supplies no
elemental-N stock uncertainty or independent repeat-haul design. No companion
data downloads were requested.

The search was restricted to this identified manual, linked metadata and the
companion acquisition description. Unrelated experiments and generic instrument
precision were not substituted for Leg 8 observations.

Exact copies of the [metadata XML](../data/law-route/2026-10-04/metadata/malaspina-panmd.xml),
[event KML](../data/law-route/2026-10-04/metadata/malaspina-events.kml) and
[methods chapter](../data/law-route/2026-10-04/metadata/malaspina-processing-methods.pdf)
are retained with a [checksum receipt](../data/law-route/2026-10-04/metadata/acquisition.json).

## What the processing instructions establish

The chapter distinguishes 300 µm MULTINET and 200 µm WP2 mesoplankton sources.
It therefore cannot by itself verify the exact gear and split used for each
Leg 8 sample. The diagram illustrates one quarter of a MULTINET collector as
the isotope portion. That fraction is not evidence of a quarter split for every
Leg 8 200 µm tow.

The isotope portion is brought to 250 mL and homogenized; 50 mL is removed for
formalin preservation. The remainder is sieved into nominal classes. Each
retained class is again brought to 250 mL before GF/F filtration. If filtration
stops before the full volume, the actual volume is to be recorded. Thus a
common initial split and a class-specific filter aliquot are distinct corrections.
The recommended log includes sampled column, coordinates, start/end times,
sample code, filtered and aliquot volumes, filter identity/weight and observations.
Completed logs are not supplied by the reviewed sources.

Page 621 specifies seawater filtered through **40 µm** for bringing
each fraction to volume. This does not remove all smaller particulate material
that can subsequently be retained by a GF/F filter. A matched processing blank
or another validated correction could quantify its contribution to assayed nitrogen. This is a
plausible additive-background pathway, **not demonstrated contamination**. An
additive background can pull class stocks toward a common floor, while differing
class aliquots and rinsing can alter that effect. Its magnitude cannot be inferred
from these instructions.

The chapter's sampling-QC section describes cleanliness and states that there
are no sampling-specific quality controls. It does not document elemental-N
blank correction, detection limits, concentration repeatability or recovery.
Isotope reference standards and isotope-ratio precision do not fill these gaps.

## Gate ledger

| Requirement | Established | Unresolved consequence |
|---|---|---|
| Resource identity | Elemental N assay and reported mg/m³ variables | The concentration's complete scaling and background correction cannot be reconstructed |
| Within-catch classes | 200–500, 500–1000, 1000–2000 µm common-net classes; gelatinous exclusions | Nominal sieve retention is not a measured transfer from true size classes to captured stocks |
| Water-volume normalization | Reported concentration units and net geometry | The reviewed records do not trace the reported values through actual volume and aliquot corrections |
| Splitting and filtration | Intended portion removal and class-volume logging are documented | Actual Leg 8 initial split and class aliquot/recovery factors remain unverified |
| Analytical uncertainty | Chemical assay instrument identified | N blanks, limits, duplicate errors and matched rinse/process blanks are not documented |
| Replication | Single January–March 2011 Leg 8 transect, largely near 24°N; upper 200 m sampling | Complete eligible tow count, biological repeats or defensible independent blocks are not established |

Exclude the separate-net 40–200 µm class and the upper tail. The actual Leg 8
methods define the latter as >2000 µm despite the archive's 2000–5000 µm label.
The bounded three-class domain supplies only two independent profile contrasts.

The full metadata XML and event KML contain **43 unique event labels**, with
matching coordinates after removing the KML names' parenthetical station suffix.
Direct event `dateTime` fields run from `2011-01-29T11:23:00` to
`2011-03-13T21:33:00`, as reported, and latitudes span 24.4865–27.1285°N.
These supersede the earlier landing-page excerpt listing only three events.
They establish station coverage, not the number of complete assayed catches or
independent blocks. The 1,161 published data points count recorded values,
not ecological replicates. Event timestamps need not be actual net-haul times:
some fall outside the paper's 10:00–16:00 GMT sampling window. They must not
drive a day/night eligibility filter without a tow-log join. Nested campaign
dates likewise must not be substituted for direct event dates.

The companion isotope study selected four stations per geographic zone and
pooled their material for amino-acid analysis. Pooled isotope composites and
repeated instrument injections do not establish biological replicate catches.
The full-expedition 2016 paper also includes Leg 8; it is not automatically an
independent replication of these samples.

## Implication for the proposed target

Direct stocks are sufficient in principle to test an expected-stock allocation
pattern; class quotas are not a prerequisite for that endpoint. Counts and
independent quotas are additional requirements for predicting abundance, and
opportunity budgets for explaining feasibility. None should be inferred from
dissolved nutrient concentration, isotope signatures or the observed stock total.

Shared water-volume or initial-split error can cancel in an individual catch's
normalized shares, provided the same factor truly applies to all classes. It does
not resolve class-specific recovery, additive blanks, or unequal sampling weights,
and it does not identify normalized expected water-column stocks. Averaging
normalized catches targets a different estimand from normalizing expected stocks.

Before a law-test freeze, seek existing documentation sufficient to justify
relative class corrections, bound consequential processing backgrounds and
declare the sampling population and dependence. Completed tow/sample records
and N QC would help, but every raw volume or duplicate assay is not mandatory:
traceably normalized concentrations and a justified error model can suffice.
Mean-zero assay noise can contribute to uncertainty estimated across biological
blocks; systematic class effects require separate justification or bounds.
Repeat hauls or adequately justified sampling blocks could supply replication;
analytical aliquots and sieve classes cannot. Calibration cannot support a
practical-equivalence verdict by assigning convenient unmeasured error bounds.

No additional raw-N outcome exposure occurred during this audit. The previous
published dry-weight/isotope Table I exposure remains described in the
[route document](natural-law-route.md); it is not an unseen-outcome guarantee.
