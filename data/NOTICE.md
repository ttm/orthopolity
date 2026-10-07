# Third-party data notice

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
