# Earthquake catalogue availability, 9 October 2026

Two complete public catalogues were downloaded and checked; the regional catalogue
is also reachable. This audit calculated no b-values, completeness thresholds,
correlation dimensions, or productivity fits. Acquisition details, hashes and
structural counts are retained in
[`audit-summary.json`](../data/dataset-audit/2026-10-09/seismic/audit-summary.json)
and [`manifest.json`](../data/dataset-audit/2026-10-09/seismic/manifest.json).

| Source | Verified payload | Scientific use and remaining requirement |
|---|---|---|
| [Ridgecrest AWR hypocentre catalogue v2](https://data.caltech.edu/records/5af05-cah73) | Complete 19,728,609-byte CSV; 222,864 events; publisher MD5 matches | Time, latitude, longitude, depth, GaMMA magnitude and relocation quality. No cluster labels or per-event location-error estimates. CC0. |
| [SCEDC Ridgecrest QTM](https://service.scedc.caltech.edu/ftp/QTMcatalog-ridgecrest/ridgecrest_qtm.tar.gz) | Complete 4,460,469-byte archive; decompresses successfully; 111,918 rows | Time, magnitude, 3D locations and error fields. Only 46,512 rows are marked successfully relocated; do not use all detections as equivalently precise hypocentres. |
| [SCEDC regional relocated catalogue](https://service.scedc.caltech.edu/ftp/catalogs/hauksson/Socal_DD/) | HTTP 206; first 1,000,000 bytes saved from a 152,809,713-byte file | Broadest route to multiple physical clusters. Mixed ordinary and relocated record formats require explicit filtering. Full file not acquired. |
| [NCEDC 2024 routine catalogue](https://www.ncedc.org/pub/catalogs/NCSS-catalogs/2024.ehpcsv) | First 4,000 bytes acquired | Useful transport/schema fallback; not established here as a double-difference relocated catalogue. |

The first catalogue spans 2019-04-04 through 2023-05-01. All event IDs are unique,
and all magnitude/location values are finite. These checks establish usable
structure, not magnitude completeness or homogeneous calibration. The retained
QTM rows cover July 2019. Its GrowClust components are relocation groups, not
automatically the physical clusters needed by the hypothesis. None contains
3,000 raw events, before completeness filtering.

The exact recovered protocol is
`f846670:configs/prereg_2026-10-08_volumetric_seismicity.json`. It requires at
least **ten qualifying clusters** and a D2 range of at least 0.5. Its synthetic
checks indicate roughly 3,000 complete events for volumetric clusters and
1,000 for planar ones. A large catalogue alone does not meet those conditions.
Freeze the catalogue version, quality filters, magnitude handling and physical
clustering procedure before calculating either response. No such choices have
been made in this audit.

The [SCEDC Cahuilla source](https://scedc.caltech.edu/data/cahuilla-swarm.html) explicitly
does not supply calculated magnitudes; it is not a turnkey source for this test.
Preserve SCEDC and original-paper attribution when using its products. The CC0
statement above applies specifically to the CaltechDATA v2 deposit.

The retained regional sample is **not** a scientific cohort. It starts at the
beginning of the source file and excludes its final partial record when counting
rows. Exact download URLs and access distinctions are in the JSON audit.
