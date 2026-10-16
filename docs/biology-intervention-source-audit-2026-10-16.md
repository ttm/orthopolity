# Biological intervention candidates and selected assay transfer

16 October 2026. The previous sediment work is committed and pushed through
`0ef8aba`. This audit starts the biological part of the author-directed sequence.
Earlier cell-cycle, chemostat, paired-phosphorus and field-stock results remain
unchanged. No individual numerical biological target response was inspected
during this audit.

## Selected accessible archive

[Borkowski et al. (2018)](https://doi.org/10.1038/s41467-018-03970-x)
provides a small source workbook with extract and living-cell reporter assays.
The original 45,841-byte workbook, 1,980,736-byte methods supplement and article
XML are retained in `data/biology-candidates/2026-10-16/borkowski2018/` with
URLs and SHA-256 in `acquisition.json`. The workbook and supplement downloaded
from the current publisher host match the Europe PMC copies byte-for-byte.
The old Springer CDN hostname failed DNS resolution and NCBI's supplementary
route returned an HTML challenge. These failures do not make the data unavailable.

Only worksheet names, string labels, numeric-cell presence and formula absence
were inspected. The useful blocks have three measurements per construct. Twelve
initiation variants of mKate provide calibration. Ten new protein/mKate fusions
with a common BCD2 initiation design provide separate assay inputs and withheld
cell responses. Four constructs share the Viob protein family. Repeated
conditions, source summary panels and the empty insert must not inflate the
independent biological coverage.

The [frozen protocol](burden-transfer-protocol-2026-10-16.md) compares a reciprocal
free-pool relation against linear, affine, constant and direct-assay predictions.
The extract assay is independently performed, but its inferred workload is a
proxy. The learned environment factor is not an independent absolute resource
measurement. This deliberately bounded transfer can establish predictive value
of the assay and separately assess the reciprocal relation's added value.
Its reference measure is counting over gene families and constructs, neither
log-orthopolic nor linear-orthopolic size allocation.

## Why the initially considered mechanistic transfer was narrowed

The paper also predicts a strong-to-weak initiation-sequence intervention using
a ribosome-flow model. Supplementary Figure 4 says initiation strengths and
translation efficiency were inferred jointly from simulated reporter and
construct outputs. These are not direct independent kinetic assays. The source
uses a single elongation proxy for many distinct translation processes, assumes
mRNA abundances from promoter classes, and supplies nominal gene sizes with
fusion/footprint conventions needing further qualification. A literal queue
model replication would require those conventions and the original software
to be resolved before fitting. Do not call its assigned constants independently
measured ribosome costs or claim that the current study tests congestion.

Additional source issues remain explicit: workbook headings say STD while
captions say standard error; extract assays take maximum production rates,
whereas cell assays use mid-exponential rates per optical density; incubation
descriptions include both 29 and 37 degrees. The present design retains the
source's normalization and compares reported spread to recomputed SD and SEM
only after forecast sealing. Published qualitative outcomes, correlations
(including the source's transfer successes), and model constants were already
visible in article prose. This is not a blind or prospective experiment.

## Other leads retained without new response analysis

* [Hofmann et al. (2021), DOI 10.1111/ele.13695](https://onlinelibrary.wiley.com/doi/full/10.1111/ele.13695):
  six phytoplankton species, nine dissolved resources, monocultures and all
  pairwise mixtures at two temperatures. Archive DOI
  [10.5061/dryad.h70rxwdhd](https://doi.org/10.5061/dryad.h70rxwdhd).
  Resource-depletion slopes are calibration estimates, and mixture species
  biomass is apportioned using cell-volume fractions. Published summaries
  already reveal that a complete-overlap comparator is strong. Numerical
  records were not downloaded; source compatibility and the published
  competition equations need qualification. This is a viable next ecological
  candidate, not yet an eligible frozen prediction.
* [Greulich et al. (2015), DOI 10.15252/msb.20145949](https://pmc.ncbi.nlm.nih.gov/articles/PMC4380930/):
  nutrient-dependent antibiotic growth inhibition combines prior growth laws
  with drug kinetics. Published qualitative response reversals are exposed.
  Drug transport/binding parameters and physiological inputs would need a
  response-independent calibration audit; no numerical dataset was opened.
* [Borkowski's source model predecessor, Ceroni et al. (2015)](https://doi.org/10.1038/nmeth.3339)
  supplies software, with a documented 25 June 2015 correction restoring
  missing files. A future mechanistic replay must acquire the corrected version.

The next empirical outcome belongs to the explicitly selected assay-transfer
protocol. These alternative leads do not authorize post-outcome selection of
a more favorable model, normalization, sample or physical interpretation.
