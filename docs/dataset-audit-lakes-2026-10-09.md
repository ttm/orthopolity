# Lake polygon availability audit — 2026-10-09

The original HydroLAKES download is reachable from this environment when network access is enabled. A smaller alternative has also been downloaded and structurally checked: UKCEH's **41,830-waterbody UK inventory**, an **8.59 MB ZIP** containing actual lake geometries. Neither dataset was used to estimate radii, fit exponents, or evaluate the hypothesis during this audit.

**Subsequent continuation:** the full HydroLAKES archive was acquired and both
the global calculation and a separately frozen UK replication have now run.
See the [lake result report](lake-gyration-results-2026-10-09.md). The partial
download statements below describe the initial availability audit.

The recovered registration is at git commit `f846670`, file `configs/prereg_2026-10-08_lake_gyration.json`. Its amendment selects **1–20 km radius of gyration**, and its prediction is a **survival exponent** of 2 (density exponent 3). Changing from global HydroLAKES to a regional inventory would require a separately declared replication or amendment; this audit does not make that change.

## Verified small alternative: UKCEH Spatial inventory of UK waterbodies v3.6

- [Publisher record and citation](https://catalogue.ceh.ac.uk/documents/b6b92ce3-dcd7-4f0b-8e43-e937ddf1d4eb): Taylor, P.J. (2021), DOI `10.5285/b6b92ce3-dcd7-4f0b-8e43-e937ddf1d4eb`.
- [Direct ZIP download](https://data-package.ceh.ac.uk/data/b6b92ce3-dcd7-4f0b-8e43-e937ddf1d4eb.zip).
- Open Government Licence; attribution to UKCEH and Ordnance Survey is required by the publisher. The package includes supporting documentation and machine-readable metadata.

Measured from the downloaded artifact:

| Property | Verified value |
| --- | --- |
| Compressed archive | 8,587,716 bytes; ZIP CRC passes |
| GeoPackage | 29,741,056 bytes; SQLite integrity check passes |
| Features / distinct WBIDs | 41,830 / 41,830 |
| Geometry | 2D `MULTIPOLYGON`, EPSG:27700 (British National Grid, metres) |
| Attributes | `WBID`, `NAME`, `POLY_AREA_HA` (hectares), `POLY_PERIMETER_KM` (kilometres) |
| Missing geometry, missing/nonpositive area or perimeter | Zero |
| Geometry contents | 41,839 polygons, 45,061 rings, 3,222 interior rings |
| Multipart features | Five |
| Coordinate structure | 1,254,053 vertices including closing duplicates; all rings closed, finite, at least four vertices |

These are structural checks, not a claim that every polygon is topologically valid or that the inventory is complete. Self-intersections were not checked.

The bundled publisher documentation says outlines mostly reflect OS data from approximately 1993, with selective later revisions; newer reservoirs may be absent, ponds below 1 ha are poorly represented, and some large lakes have been split into separate basins. It supplies **no reservoir/natural-lake classification**. Consequently the registered natural-only sensitivity cannot be performed using this file alone. Lake names are not an adequate replacement for a classification. The national coverage and basin splits also need explicit treatment in a regional test.

Actual polygons allow direct area-weighted second moments and thus radius of gyration; substituting `sqrt(area)` would force an area–radius relation and would not perform the intended test. The original script reads a WGS84 shapefile, while this archive contains a projected GeoPackage: a format/CRS adapter is necessary. It must respect interiors and multipart choices declared in advance. The number of features that would survive the registered radius range has deliberately **not** been calculated, so 41,830 is not the eventual test sample size.

Local artifacts are under `data/dataset-audit/2026-10-09/lakes/`. `ukceh_receipt.json` records sizes, hashes, schema, and checks. Reproduce the structural audit with:

```sh
python3 data/dataset-audit/2026-10-09/lakes/verify_ukceh.py
```

SHA-256 of `ukceh_lakes_v3_6.zip`:

```text
edfd526159a0a9005a51da57d01866cae78899c76c7e4872af196631a3a4b674
```

## Original primary: HydroLAKES v1.0

The [official product page](https://www.hydrosheds.org/products/hydrolakes) still provides [the registered shapefile ZIP](https://data.hydrosheds.org/file/hydrolakes/HydroLAKES_polys_v10_shp.zip). A real HTTP GET returned `200`, advertised **820,295,132 bytes**, and yielded a valid ZIP prefix. Only the first **4,096 bytes** were saved, then the transfer was intentionally stopped. The full archive has **not** been downloaded or checked. `hydrolakes_availability.json`, `hydrolakes.headers.txt`, and `hydrolakes_first4096.bin` preserve this limited verification.

The [official technical documentation](https://data.hydrosheds.org/file/technical-documentation/HydroLAKES_TechDoc_v10.pdf) describes 1,427,688 lakes and reservoirs, a 10 ha area cutoff, heterogeneous mapping sources/resolutions, and CC BY 4.0 licensing. It distinguishes reservoirs/regulated lakes using links to GRanD. The ten-hectare inclusion rule should not be mistaken for uniform global detection completeness.

The previous access failure is therefore not evidence that this dataset has disappeared. In this session the default shell sandbox could not resolve external hosts; enabled network access plus `curl` succeeded. A Python request initially also failed because its default trust store lacked an issuer, and a later correctly verified Python request received HTTP 403. No TLS checks were disabled. A byte-range attempt was ignored despite advertised range support, so range support should not be assumed.

Before a confirmatory run, finish downloading and hashing this exact primary source and follow the recovered registration. One scientific interpretation issue merits a declared sensitivity: EPSG:6933 preserves area but not distances, making the registered radius a projection-dependent measure. A local metric projection may be a useful sensitivity, especially at high latitude. The original largest-ring code also omits additional outer components; preserve the registered primary and record any amendment rather than silently changing it.

## Further candidate, not payload-verified

[LAGOS-US LOCUS](https://lagoslakes.org/lagos-research-platforms/lagos-us/) supplies geometries for 479,950 CONUS lakes/reservoirs of at least 1 ha. Its RESERVOIR extension classifies the subset of 137,465 features of at least 4 ha, with classification uncertainty. This is attractive for a natural-lake sensitivity, but no LOCUS polygon payload was downloaded in this audit. The browser's EDI repository request returned 403. It remains a candidate rather than an availability-verified recommendation.
