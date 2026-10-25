# Third-party data notice

`data/cell-division/2026-10-08/` retains the XML and original Figure 1/2 images
of Gangan, M. S., and Athale, C. A. (2017), *Threshold effect of growth rate on
population variability of Escherichia coli cell lengths*, Royal Society Open
Science 4, 160417, DOI [10.1098/rsos.160417](https://doi.org/10.1098/rsos.160417).
Copyright 2017 The Authors; [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
The figures are unchanged; JSON transcriptions, analytic forecasts and comparison
plots are identified as derived work in [the report](../docs/cell-division.md).
Europe PMC and the official NCBI open-access S3 archive supply these copies.
Dryad dataset/file metadata are retained as provenance; the raw workbook was
not downloaded. Source-specific terms do not become the package MIT licence.

`data/measure-candidates/2026-10-04/` retains provider metadata and two
biological archives. [Ghedini, Malerba and Marshall (2020)](https://doi.org/10.26180/5e30e9e2b02b3)
and [Ghedini, Loreau and Marshall (2020)](https://doi.org/10.26180/5e2a1a8d74be7)
are supplied under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/),
as recorded in their exact Figshare metadata. Authors, original source names,
checksums and receipts accompany the files. The package's MIT licence does not
relicense them. Extracted headers and the independent calibration ledger are
identified as derived inspection materials, with signed/missing rates preserved.

The group ledger in `data/ghedini-cost-calibration/2026-10-05/` and figures in
`results/ghedini-cost-calibration/` derive from those attributed Ghedini
calibration readings. Grouping, fitting and plotting are identified in
[the analysis report](../docs/ghedini-cost-calibration.md); source CC BY 4.0
attribution and terms continue to apply to the reproduced readings.

The frozen files in data/raw are third-party inputs, preserved byte-for-byte for
reproduction. Their source-specific terms do not become the licence of this package.
[Source details](SOURCES.md) and the [checksum manifest](snapshot_checksums.json) identify
the inputs. This revision does not change or relicense them.

The newly retained NOAA 2025 snapshot under `data/solar-validation/2026-10-02/`
is another third-party GOES XRS input. Its URL, bytes and retrieval metadata
are retained separately; the historical snapshot catalogue is unchanged.

`data/neutrality-audit/2026-10-03/` holds source metadata rather than raw
outcome tables. The plant repository metadata at the pinned commit reports no
explicit license; none is inferred from the paper's public data link. Dataset
terms shown by PANGAEA remain in the retained landing-page snapshots. These
metadata and any later source inputs do not acquire the package's MIT license.

`data/law-route/2026-10-04/metadata/` retains third-party PANGAEA event/schema
metadata, a Bode, Fernández Lamas and Mompeán (2012) methods chapter from CSIC,
and BCO-DMO dataset/event-log descriptions and deployment metadata. Original
notices, attributions and provider terms remain applicable; the package MIT
licence does not relicense these files. Exact sources and hashes are recorded
in the adjacent acquisition receipt. These are methods and metadata, not the
candidates' nitrogen-stock outcome tables.

`data/plant-sources/2026-10-03/` now retains ten exact third-party CSVs from
that same pinned `KerkhoffLab/PlantSizeDist` commit, referenced by
[Dillon et al. (2019)](https://doi.org/10.1002/ecs2.2856). The public data link
and article's open access do not establish a licence for the separate repository
files. No explicit source licence was found in the retained repository metadata;
the package MIT licence is not applied to them. Source attribution, checksums
and retrieval provenance accompany the files.

| Inputs | Source and recorded terms |
|---|---|
| NOAA annual flare CSVs and metadata | NOAA NCEI GOES XRS reports; the supplied metadata states redistribution and use are unrestricted. |
| USGS event catalogue | USGS ComCat. The repository records these as U.S. federal government data. |
| GLOSSAQUA Size, Sample, and DataSource tables | Ersoy et al. (2025). The author repository/archive and publisher-associated supplements give different licence statements; see below. |
| Three Sheldon/Hatton summary tables | Hatton et al. (2021), author repository at commit d8af6567faf1912862650423e392e1b3195a8732. Applicable archive/table terms remain unverified here; see below. |

## GLOSSAQUA: differing source statements

The [author repository](https://github.com/zeynepersoy/GLOSSAQUA_dataset) and
[archived release](https://zenodo.org/records/14701391) are reported as MIT,
Copyright (c) 2023 Zeynep Ersoy. The
[publisher-associated supplement deposited at Brunel](https://bura.brunel.ac.uk/handle/2438/32237)
instead labels the dataset and its individual tables CC BY-NC-SA 4.0.

These statements are recorded without claiming their scopes are equivalent or that the
permissive label overrides the dataset-specific notice. Before a release or submission
relying on a particular redistribution licence, establish which terms apply to the exact
frozen files and include the corresponding notices. The earlier unqualified statement that
all GLOSSAQUA data were MIT-licensed is superseded.

## Hatton summary tables

The existing repository includes three small summary tables from the authors' public
repository, with citation to [Hatton et al. (2021)](https://doi.org/10.1126/sciadv.abh3732)
and [the data archive](https://doi.org/10.5281/zenodo.5520055).

Previous checks found no licence file at the pinned GitHub commit; attempts to retrieve
archive terms during review were unsuccessful. That establishes an unresolved source-notice
question, not permission inferred from the absence of a licence and not evidence that the
archive is permanently unavailable. Open access to an article does not by itself identify
the terms for every separately deposited table.

The raw snapshots remain unchanged. If missing files need restoring, make restore-data
explicitly permits retrieval and requires the frozen checksums to match. The default
make data command verifies locally and does not download.

## Thermal-radiation source materials

The FIRAS monopole product and its metadata are obtained from
[NASA LAMBDA](https://lambda.gsfc.nasa.gov/product/cobe/firas_monopole_spect.html).
The supporting source article is Fixsen et al. (1996),
[arXiv:astro-ph/9605054](https://arxiv.org/abs/astro-ph/9605054),
*The Astrophysical Journal* 473, 576. Source bytes, attribution and retrieval
receipts are retained under `thermal-radiation/2026-10-06/`.
The repository's software licence is not asserted over third-party article
or source-document content. Derived calculations and the covariance
transcription identify the original measurement and document their scope.

## Linguistic source materials

The English EWT corpus is retained at Universal Dependencies release 2.18,
commit `b7711cce01cdd4f5fcc0a8199b8a50d951b16c0c`. Its annotations and database
are licensed CC BY-SA 4.0, while the underlying web texts retain the mixed
rights specified in the source README. That license is not asserted over
every original text. The source README and complete license are retained in
`linguistic-resources/2026-10-07/`.

The CMU pronunciation dictionary is retained at source commit
`74790861f652b15e4ac49015a90074ad62a27690`, with its BSD-style two-clause
license and README. The dictionary supplies canonical pronunciation-symbol
counts; it is not a recording of the corpus being spoken. The source manifest
and per-file receipts retain exact URLs, sizes, hashes and retrieval times.
The repository's software license does not replace these source terms.

## 9 October dataset continuation

HydroLAKES v1.0 is supplied under CC BY 4.0; attribute Messager et al. (2016)
and HydroSHEDS as specified in its technical documentation. The large archive
is locally retained and restored from its public source, not committed here.
UKCEH Spatial inventory of UK waterbodies v3.6 is supplied under the Open
Government Licence; attribute Taylor, P.J. (2021), UKCEH, and the underlying
Ordnance Survey contribution according to the retained publisher metadata.
The CaltechDATA Ridgecrest v2 deposit identifies CC0; that statement does not
extend automatically to every SCEDC product. Preserve SCEDC/SCSN and original
paper attribution for their catalogues. RibbonDB's retained README identifies
Kazachenko et al. (2017); no explicit blanket reuse licence was established by
this audit. Source-specific notices and metadata remain with each acquisition.

## HydroBASINS follow-up source

HydroBASINS standard level-3 v1.c is attributed to Lehner, B. and Grill, G.
(2013), *Global river hydrography and network routing: baseline data and new
approaches to study the world's large river systems*, Hydrological Processes
27(15), 2171–2186, https://doi.org/10.1002/hyp.9740. Data developed on behalf of
WWF with partner support; publisher: https://www.hydrosheds.org/products/hydrobasins.
The source uses the HydroSHEDS license agreement linked from the publisher.
The source archives are local, ignored downloads; the repository retains
checksums and derived analytical output. See `docs/hydrobasins-source-2026-10-09.md`.

## Southern California sequence qualification

Attribute Zaliapin and Ben-Zion (2020), doi:10.1029/2018JB017120, for published
sequence memberships, and SCEDC/SCSN with Hauksson, Yang and Shearer (2012),
doi:10.1785/0120120010, for the underlying relocated catalogue. Original source
descriptions are retained under `seismic-regional/2026-10-09/`; its manifest pins
three complete downloads. The large raw files remain local and are restored from
their public source URLs. No blanket CC0 or software-license permission is
inferred for these sources. The separate Ridgecrest CaltechDATA v2 deposit's CC0
statement does not apply to this regional catalogue or author-hosted clustering.

## Italian and Northern California candidate audit

CLASS 1.0 and HORUS identify CC BY 4.0 on their retained publisher pages.
Attribute CLASS to Latorre et al. (dataset 2022; paper 2023), and HORUS to
Lolli et al. (2020), using the DOIs in `data/SOURCES.md`. The derived Italian
crosswalk retains source-row numbers, event identifiers, original error and
magnitude fields, and explicit ambiguity/provenance flags. It is not a newly
endorsed publisher catalogue. For NCAeqDD, cite Waldhauser and Schaff (2008)
with version v202112.1 and retain NCEDC/NCSS/NCSN attribution. Its raw catalogue
remains local and ignored. No blanket reuse license was inferred for NCAeqDD;
the Italian sources' CC BY terms do not extend to it or to the retained author
manuscript. The repository software license does not replace source-specific terms.

## Heated-cantilever damping and fluctuation data (13 October 2026)

`cantilever/2026-10-13/` retains Alex Fontana and Ludovic Bellon's dataset for
*Linking fluctuation and dissipation in spatially extended out-of-equilibrium
systems*, Physical Review E 107, 034118 (2023), DOI
<https://doi.org/10.1103/PhysRevE.107.034118>. Pinned Zenodo version 7640708,
<https://doi.org/10.5281/zenodo.7640708>, is licensed CC BY 4.0 by its publisher
metadata. `data.mat`, `plots.m` and `Functions.zip` are unchanged original
files; scripts are retained for source auditing, not executed or relicensed.
The retained arXiv v2 HTML also carries CC BY 4.0. Metadata, acquisition receipts
and hashes identify the exact files. The derived audit, forecasts, verification
and plots are this project's reanalysis, with source conventions and failures
recorded in `docs/cantilever-results-2026-10-13.md`.

## RM8850 pure and mixed gas adsorption (13 October 2026)

`adsorption/2026-10-13/` retains Carsten Wedler's versioned archive,
<https://doi.org/10.5281/zenodo.17604326>, for Wedler et al. (2024),
*Binary Adsorption Equilibria of Three CO2+CH4 Mixtures on NIST Reference
Zeolite Y (RM 8850) at Temperatures from 298 to 353 K and Pressures up to
3 MPa*, <https://doi.org/10.1021/acs.jced.4c00358>. Publisher metadata identifies
CC BY 4.0. All twelve AIFs and the workbook are unchanged publisher originals;
the workbook is retained but not used for analysis. Retained article XML and
CoolProp/IDAES documentation keep their own notices and are not relicensed as
project software. Acquisitions and checksums identify each exact source. Derived
forecasts, plots and audits are this project's reanalysis, documented in
`docs/adsorption-results-2026-10-13.md`; they are not author-endorsed data.

## Protein-expression capacity assays (16 October 2026)

`biology-candidates/2026-10-16/borkowski2018/` retains the original source-data
workbook, supplementary methods PDF and article XML for Borkowski, O., Bricio,
C., Murgiano, M., Rothschild-Mancinelli, B., Stan, G.-B., and Ellis, T. (2018),
*Cell-free prediction of protein expression costs for growing cells*, Nature
Communications 9, 1457, <https://doi.org/10.1038/s41467-018-03970-x>.
Copyright the authors, 2018; the retained article specifies
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), with its stated
exception for separately credited third-party material. Source files are
unchanged. Publisher and Europe PMC workbook and supplement copies agree
byte-for-byte. Acquisition URLs and hashes are retained. Forecasts, scores and
figures are this project's reanalysis, not author-endorsed findings; the source
SD/SEM and incubation-description discrepancies are recorded in
`docs/burden-transfer-results-2026-10-16.md`.

## Human-source qualification and speech transfer (17 October 2026)

Attribute Harhen, N. C., and Bornstein, A. M. (2023),
<https://doi.org/10.1073/pnas.2216524120>, for the original foraging task and
article in `human-candidates/2026-10-17/foraging/`. Source code is retained
unchanged for the methods audit, not executed or relicensed as project software.
No blanket reuse license is inferred for that repository. No participant data
was acquired for this candidate.

Attribute Coupé, C., Oh, Y. M., Dediu, D., and Pellegrino, F. (2019),
*Different languages, similar encoding efficiency: Comparable information rates
across the human communicative niche*, Science Advances 5, eaaw2594,
<https://doi.org/10.1126/sciadv.aaw2594>, for the original speech data. Its
repository README assigns [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
to the data and BSD-3 to RMarkdown code; the archived article separately states
CC BY-NC 4.0. Preserve these distinct notices. Original files are unchanged;
the original BSD copyright, conditions and disclaimer are retained separately
in `human-candidates/2026-10-19/speech-notices/BSD-3.txt`.
Forecasts, errors and figures are this project's reanalysis, not author-endorsed
results. The source qualification and result reports retain measurement and
published-count discrepancies.

## Equalization source qualification (19 October 2026)

The sources in `physics-candidates/2026-10-19/relaxation/` retain their own
rights and attribution. Di Terlizzi et al., *Variance sum rule for entropy
production*, DOI 10.1126/science.adh1823: the unchanged arXiv v2 HTML declares
CC BY-SA 4.0; Dryad metadata identifies DOI 10.5061/dryad.h44j0zpsw.
Bachler, Ort, Krämer and Dittrich (2021), DOI 10.1021/acs.analchem.0c04939,
and Fernandes, Karra, Swindle and Morgan (2023), DOI 10.1039/D3RA00470H:
the unchanged article XML files retain their CC BY 4.0 notices.
The Southampton dataset metadata identifies CC BY 4.0 and DOI
10.5258/SOTON/D2378. Figshare metadata attributes the computational archive
for Li, Cao and Ng (2024), DOI 10.1038/s41467-024-46058-5; that archive was
not downloaded. Source pages, bibliographic metadata and existing rights
notices are not relicensed as project software. The qualification judgments
and analytic design are this project's work, not author-endorsed findings.

## Exchange qualification and membrane archive (19–20 October 2026)

`physics-candidates/2026-10-19/exchange-followup/` retains unchanged article XML
for Sun et al. (2024), *Reconfigurable droplet networks*,
<https://doi.org/10.1038/s41467-024-45214-1>, and Bachler et al. (2020),
*Microfluidic platform enables tailored translocation and reaction cascades in
nanoliter droplet networks*, <https://doi.org/10.1038/s42003-020-01489-w>.
Both retain their CC BY 4.0 notices. The inventories in
`physics-candidates/2026-10-20/exchange-qualification/` are original publisher,
BioStudies and DataCite metadata; their source notices remain applicable.

`chemistry-candidates/2026-10-20/membrane-diffusion/` retains data from Benstead,
Politi, Bergsman and Pozzo, *An automated sampling workflow for parallel
long-term membrane diffusion cell testing*,
<https://doi.org/10.1039/D5DD00523J>. Zenodo version 17238337,
<https://doi.org/10.5281/zenodo.17238337>, assigns CC BY 4.0 to the dataset.
The experimental ZIP matches Zenodo's MD5. Original source code, notebook,
README and the MIT license are retained from repository commit
`12be95974a58e1971483823948eff8802e06b729`; the original copyright and license
remain in `LICENSE`. Source code is inspected for methods, not executed.
Acquisition receipts distinguish retained raw files from inspected numerical
values. The design inventory and qualification judgments are this project's
work, not author-endorsed results. The article has separate CC BY-NC 3.0 terms;
no article body is retained here, and its terms do not replace the data license.

## Independent circuit forecast and thermal qualification (24–25 October 2026)

`physics-candidates/2026-10-24/rlc/` retains unchanged data by Danzer, M. A.,
Plank, C., and Rüther, T., *Impedance data for various electrochemical and
electrical systems*, <https://doi.org/10.5281/zenodo.10794584>, under CC BY 4.0
as specified in its metadata. The complete supplementary PDF belongs to
their 2024 article, *Electrochemical system analysis from impedance data to
system identification*, <https://doi.org/10.1016/j.xcrp.2024.102091>, whose
separate CC BY-NC 4.0 terms remain applicable. Source files are not relicensed
as project software. Forecasts, comparisons and source-unit qualifications
are this project's reanalysis, not author-endorsed findings.

`physics-candidates/2026-10-24/thermal/` retains unchanged metadata, methods and
the independent material workbook from Kling et al. (2022),
<https://doi.org/10.3390/pr10050959>, and the GEOFIT records
<https://doi.org/10.5281/zenodo.7436705> and
<https://doi.org/10.5281/zenodo.7436458>, which specify CC BY 4.0.
The project model report, deliverable pages and download-error receipts retain
their original attribution and rights; no blanket software or data license
is inferred for them. The large Sand HDF5 is not tracked; its URL and checksums
are retained. Only its schema and labels were decoded. Qualification notes and
derived schema inventories are this project's work.
