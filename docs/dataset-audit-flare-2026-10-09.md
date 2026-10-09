# Solar-flare dataset availability audit, 2026-10-09

**The original RibbonDB dataset is reachable and downloaded.** The old handoff's download blocker does not apply to this session. This audit acquired data and inspected schema only; it did not fit distributions or run hypothesis tests.

The subsequent [registered run](flare-ribbons-run-2026-10-09.md) is now complete,
with its own pre-run exposure record and retained results.

## Verified acquisitions

Files, original HTTP headers, SHA-256 receipts, and schema summaries are in `data/dataset-audit/2026-10-09/flare/`.

| Dataset/file | Actual download | Suitability |
|---|---:|---|
| [RibbonDB v1.0 CSV](https://solarmuri.ssl.berkeley.edu/~kazachenko/RibbonDB/ribbondb_v1.0.csv) | HTTP 200; 655,830 bytes; 3,137 rows | Exact source requested by the original flare preregistration |
| [RibbonDB documentation](https://solarmuri.ssl.berkeley.edu/~kazachenko/RibbonDB/readme_ribbondb_v1.0.txt) | HTTP 200; 3,287 bytes | Units, selection, and variable definitions |
| [RibbonDB full archive](https://solarmuri.ssl.berkeley.edu/~kazachenko/RibbonDB/RibbonDB_v1.0.zip) | HTTP 200; 4,795,062 bytes | Contains CSV, IDL table, documentation, and paper; no spatial mask files |
| [SolarErupDB CSV](https://solarmuri.ssl.berkeley.edu/~kazachenko/SolarErupDB/SolarErupDB_Kazachenko2023_V1.0.csv) | HTTP 200; 214,084 bytes; 480 rows | Additional properties of a selected RibbonDB subset; not independent replication |
| [FlareDB Zenodo metadata](https://zenodo.org/api/records/16790538) and [event list](https://zenodo.org/api/records/16790538/files/FlareDB_event_list.pdf/content) | HTTP 200; 15,845 and 252,463 bytes | New imaging source, but masks/areas require derivation; event-list bytes downloaded, PDF not visually inspected |

The RibbonDB CSV SHA-256 is `1fc2b1a869a85a0668207f98438c452198df141b8d1d452dac19968136d18e00`.

Access distinction: the web browsing tool failed on Berkeley, sandbox Python reported DNS failures, and network-enabled Python had local certificate-trust failures. Network-enabled system `curl` succeeded with normal certificate verification. No TLS verification was disabled. A browsing-tool failure must not be reported as proof that the public host is down.

## RibbonDB: ready for the original registered input

[The original paper](https://arxiv.org/html/1704.05097) describes 3,137 C1.0-and-larger flares, April 2010–April 2016, within 45 degrees of the central meridian. AIA 1600 Å observations identify cumulative ribbon footprints. Relevant columns are:

- `S_RBN [cm^2]`: cumulative ribbon area, primary variable.
- `DS_RBN [cm^2]`: area uncertainty from ribbon-threshold variation.
- `PHI_RBN [Mx]` and `DPHI_RBN [Mx]`: unsigned reconnection flux and uncertainty, secondary variable.
- Times, GOES peak flux, latitude/longitude, active-region number, active-region area/flux, and area/flux fractions support eligibility and sensitivity checks.

All 3,137 area entries are finite and positive. There are two exact duplicate pairs except for `INDEX`: `20140414_0857_12036_C1.8` at indices 1941/1942 and `20141215_2116_12242_C4.5` at indices 2441/2442. The original downloaded data remain intact. Any deduplication or dependence-aware uncertainty procedure should be documented before outcome analysis, not silently introduced.

The CSV has spaces after delimiters. With the unchanged `pandas.read_csv` call in the original script at commit `f846670`, the literal primary column name is ` S_RBN [cm^2]`, including the leading space; secondary is ` PHI_RBN [Mx]`. The schema summaries use `skipinitialspace=True` only for inspection.

The recovered preregistration fits the marginal area distribution against exponents 2 and 7/3. This table meets that input requirement. It does not provide an independent linear extent: direct area-versus-length validation needs spatial data. Interpreting the marginal result as geometry also depends on the shared hypothesized linear-size distribution and measurement/selection assumptions. Do not manufacture length as the square root of area for that separate validation.

## Alternatives and limits

[SolarErupDB's paper](https://arxiv.org/html/2310.02878) describes a RibbonDB-derived sample selected by GOES class and reconnection-flux balance. The acquired table adds temperature, emission measure, fluence, duration, reconnection rate, and eruptivity. Its duration headers use seconds, while the article's variable summary describes minutes: honor the actual table schema and verify conversions. The host explicitly says its CSV/IDL files contain no spatial data.

[FlareDB](https://www.nature.com/articles/s41597-026-06607-7) provides observations for 151 substantial flares across 82 active regions in 2010–2025, with AIA UV and HMI patches. [Zenodo](https://zenodo.org/records/16790538) holds quick-look movies, not a ready ribbon-area catalogue. Its 24-second 1600 Å movie archive alone is 344,880,404 bytes; no large movie archive was downloaded. FITS files are described as individually available through [NJIT SolarDB](https://nature.njit.edu/solardb/), but individual FITS download access was not tested in this audit. This source needs a new extraction and selection protocol, not substitution into the original RibbonDB registration.

## Prior exposure and boundary

The auditing agent read the 2017 paper's abstract and methods and encountered its published reconnection-flux/energy frequency exponent of 1.6; no published ribbon-area frequency exponent was located or read. It also read the 2023 dataset's methodology and the 2026 FlareDB descriptor. No empirical area exponent, histogram, fitted tail, or hypothesis verdict was computed here. Record the running researcher's own prior exposure before any registered test.
