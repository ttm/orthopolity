# Chemostat source audit, 2 October 2026

The published algal community archive can support a conditional test of resource
allocation forecasts after a measured nutrient intervention. The archive contains
chemically measured cellular nitrogen and carbon from separate preliminary
cultures, observed community composition before and after a pulse, and an
independent no-herbivore comparison. It does not directly measure nitrogen stocks
or uptake in the main community vessels. Transferring preliminary quotas to those
vessels is therefore an explicit assumption of any resource-profile analysis.

This audit inspected calibration measurements and main workbook headers,
identifiers, dates, times and missing-value element presence. Main post-pulse
biovolume and abundance values were not inspected or scored. The complete
published archive had to be downloaded and extracted to retain its original
bytes. The article's published findings and preliminary plots were already
encountered during candidate screening, so this workflow does not establish
global outcome blinding or prospective registration.

## Original sources and retrieval

The study is Wojcik et al., *Top-down control and species composition influence
nonlinearly the short-term response of experimental food webs to a nutrient
pulse perturbation*, [doi:10.1098/rspb.2025.1969](https://doi.org/10.1098/rspb.2025.1969).
The [Dryad dataset](https://doi.org/10.5061/dryad.51c59zwj5) links the authors'
[Zenodo software and data deposit](https://doi.org/10.5281/zenodo.14773023)
and a separate [figures deposit](https://doi.org/10.5281/zenodo.14773027).
Published methods are in the
[Figshare supplementary collection](https://doi.org/10.6084/m9.figshare.c.8172360).

All available sources are retained under
[`data/chemostat-sources/2026-10-02/`](../data/chemostat-sources/2026-10-02/).
The [acquisition receipt](../data/chemostat-sources/2026-10-02/acquisition.json)
records requested/final URLs, UTC start/completion times, HTTP headers, byte
counts, provider checksums, SHA-256 checksums and the TLS trust-store reference.
Certificate and hostname verification remained enabled. Successful source
retrieval completed at `2026-10-02T14:27:36.523761+00:00`.

Dryad version 5 metadata and its published file inventory were acquired. The API
download endpoint returned HTTP 401; the public website download links returned
HTTP 403. Original Dryad `data.zip` and `README.md` were consequently unavailable.
Failed requests, the initial sandbox DNS failure and a large-download read
timeout are retained in
[`retrieval-attempts.jsonl`](../data/chemostat-sources/2026-10-02/retrieval-attempts.jsonl).
The publicly downloadable author-owned Zenodo bundle was used instead.

| Retained original file | Bytes | SHA-256 |
| --- | ---: | --- |
| Zenodo `scripts_data_plankton_responses_Npulse.zip` | 98,674,395 | `0864e94ddf2df5d30fb47c16ba15c68bcfd282c48cdf1259eff12a118136fe90` |
| Figshare `rspb20251969_si_001.pdf` | 3,231,718 | `b6d98a589800ff9f561bca6986c4e68a685dbb474ee5e1b2fc8661c281ce195c` |

Both match the respective provider MD5 hashes. The Zenodo bundle has 64 file
members expanding to 101,943,147 bytes. Most of that size is an R workspace
(`.RData`); it was never imported. R project settings, saved histories, published
posterior objects, posterior predictions and original result figures are
retained as source bytes and are excluded from this audit's analysis inputs.

The unavailable Dryad zip has published SHA-256
`0ccac649474c40e86cd17eb361ed70fb3d117a4ea992e8d497c1ec3979b13124`,
which differs from the complete Zenodo bundle. These are different archive
packages. No byte-equivalence claim is made about their constituent data files
without a direct comparison. Every extracted Zenodo member has its own retained
checksum in the
[member inventory](../data/chemostat-sources/2026-10-02/archive-members.json).
Dryad metadata declares CC0; the linked Zenodo software deposit declares an MIT
license. Those source declarations are preserved without harmonizing them.

## Measurements and experimental conditions

The supplement's appendix S2.1, PDF page 8 (printed page 43), describes cellular
C and N assays in eight preliminary semi-continuous monoculture experiments:
four algal species, each experimentally replicated twice. Two 5 mL samples were
filtered through pre-combusted glass-fiber filters; C and N were measured using
a gas chromatograph. CASY particle counts and size spectra supplied cell density
and volume for per-cell normalization and biovolume calculation. Nitrogen is
thus chemically assayed and is not assigned from a volume allometry.

Those preliminary cultures had a 320 micromol N/L pulse, with 20% medium renewal
on sampling days. Their light and temperature conditions matched the community
chemostats, while semi-continuous renewal differed from continuous flow. Quota
variation after the pulse measures changing cellular nutrient content. It does
not by itself identify a minimum construction requirement or uptake rate.

Appendix S2.1, PDF page 6 (printed page 41), also describes ten preliminary
no-herbivore chemostats: four algal monocultures and one mixed culture, each with
two vessel replicates. Their pulse and experimental conditions followed the main
chemostat protocol. The mixed culture's mean total biovolume at the pulse was
used as a carrying-capacity comparison. A top-down control index computed from
that reference and a main vessel's pre-pulse biovolume is a measurement-derived
index. Feeding rates or nutrient states inferred by fitting the main outcome
series remain different quantities.

The published main protocol specifies 800 mL in a 1 L bottle, a dilution rate
of 0.2/day, nitrogen-reduced inflow at 80 micromol N/L and 50 micromol P/L, and a
pulse raising nitrogen to 400 micromol/L while preserving the N:P addition
ratio. The initial rotifer assemblage and pulse timing define the treatment.
An unchanged supply ratio does not establish an unchanged physiological
limitation, nor does washout establish a return to a neutral resource profile.

The rendered supplement pages 6, 8, 9 and 14 are retained in `pdf-review/`.
Page 8 confirms the assay protocol and page 9 confirms that the plotted C:N
ratio is molar, cell density is cells/mL and cell volume is cubic micrometers.
Page 14 documents the start of the species identification procedure. Rendering
used the bundled PDFium runtime; no source PDF was modified.

## Workbook schema and available replication

The three study workbooks are original extracted bytes under
`zenodo/extracted/scripts_data_plankton_responses_Npulse/data/`.
The machine-readable
[workbook audit](../data/chemostat-sources/2026-10-02/workbook-schema.json)
retains complete main metadata rows and per-vessel time coverage without
numerical outcome values. The
[audit summary](../data/chemostat-sources/2026-10-02/source-audit.json)
identifies the original input hashes and the audit algorithm hash.

| Workbook | Retained content | Limitation |
| --- | --- | --- |
| `Chemostat_experimental_timeseries.xlsx` | 456 records, 24 vessels, 16 columns | Three observed algal groups represent four species; main nutrient concentration and per-cell quotas absent |
| `algae_stoichiometry_preliminary_experiments.xlsx` | 20 records, four algae, five times; nine columns | No replicate identifier or separate assay error despite duplicate experiments described in the methods |
| `algae_no-rotifer_chemostat_preliminary_experiments.xlsx` | 140 records, vessel IDs and observed group biovolumes | One extra trailing column has an empty header; it is excluded from prepared records |

The stoichiometry table gives N and C in pmol/cell, cell volume in cubic
micrometers, density in cells/mL and biovolume in cubic micrometers/mL. All 20
records have those fields populated. Algal codes are `Cr` (Cryptomonas), `Ca`
(Chlamydomonas), `Mo` (Monoraphidium) and `Co` (Chlorella); times are -4, 0, 1,
2 and 3 days relative to the pulse. Records date from June 2023. They must not
be expanded into 40 independent measurements or assigned invented replicate
identities. The table alone does not identify whether its rows are averages
over the duplicate experiments described in the methods.

Main vessels `Bc1`-`Bc4`, `Ce1`-`Ce4` and `Le1`-`Le4` are the twelve rotifer
monoculture vessels from August-October 2022. Vessels `1`-`12` are the twelve
rotifer polyculture vessels from March 2023. Polyculture pulse timing is 13 days
for IDs `1,2,5,7,8,9` and 9 days for IDs `3,4,6,10,11,12`. Every vessel has a
time-zero observation and earlier observations. Calendar batch and treatment
therefore partially coincide, which matters when assessing transfer between
these sets.

The raw main archive extends beyond the article's 12-day response window:
monocultures include times through day 19, 9-day polycultures through day 16,
and 13-day polycultures through day 12. An analysis replicating the article's
response window should freeze a 12-day limit before scoring. One post-pulse row
has absent value elements for all three algal group biovolumes and all three
relative abundances. Total algal and total rotifer biovolume have no absent
value elements. This is a presence audit; it does not establish numerical
validity or evaluate textual missing-value markers in the main outcomes.

Preparatory JSON copies preserve raw cached workbook values, source row
numbers, units and input SHA-256 references:
[stoichiometry](../data/chemostat-sources/2026-10-02/preliminary-stoichiometry.json)
and [no-herbivore cultures](../data/chemostat-sources/2026-10-02/preliminary-no-herbivore.json).
Blank preliminary values remain JSON `null`. No workbook was rewritten.

## Identifiability for resource forecasts

The main group `Monoraphidium_Chlorella` pools two species with different
cellular sizes and quotas. Its resource total can be bounded using the two
independently calibrated resource-per-biovolume values. Selecting an internal
mixture from the validation outcomes would invalidate a claim of independently
specified costs. Cryptomonas and Chlamydomonas are observed separately.

Main vessels do not supply contemporaneous chemically measured nitrogen or
carbon per group. Preliminary resource-per-biovolume calibration can therefore
yield an externally calibrated resource proxy, with declared transfer and
pooling assumptions. The published `bayesian_predictions_*.csv` and
`fit_*.rds` are full-data model products. In particular, their dissolved
nitrogen trajectories are not independent resource observations and should
not be used as validation truth or independent eligibility criteria.

Supply, dilution, pre-pulse composition and preliminary traits can constrain
candidate forecasts. They do not identify all growth and grazing rates or a
unique recovery trajectory. Any kinetic calibration needs an explicit training
partition, with whole independent vessels reserved for validation. A useful
first claim is comparative prediction of three-group composition/resource
proxies under a known intervention, with finite-class uncertainty. This archive
alone cannot establish a broad power-law exponent or a universal neutrality law.

## Replay

```bash
python3.11 experiments/fetch_chemostat_sources.py --stage verify
python3.11 experiments/fetch_chemostat_sources.py --stage audit
```

Both commands reuse retained snapshots and make no network requests. Extraction
rejects traversal, absolute paths, duplicate entries, links and archives larger
than the declared expansion bound. Changed snapshots or regenerated audit
outputs with different bytes cause failure. The explicit `--stage acquire`
command permits first retrieval; it reuses a completed, verified acquisition.

Git does not track the 98.7 MB Zenodo bundle or its extracted 94.8 MB `.RData`
workspace. It does track every other extracted member (about 7.2 MB), the
supplement, receipts and audit outputs, so analyses that use the three
workbooks run from a clone. Their hashes are checked against the member
inventory. In a clone, `make restore-chemostat-bundle PY=python3.11` re-downloads
the bundle. It accepts the bundle only if its byte count, SHA-256 and provider
MD5 match the retained receipt, then re-extracts and checks every member. Only
then can the two replay commands above run. Restoration is not a new
acquisition.
