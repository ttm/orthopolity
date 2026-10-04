# Third-party data notice

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
