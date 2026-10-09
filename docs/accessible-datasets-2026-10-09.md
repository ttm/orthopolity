# Continuing the registered tests with accessible data

Updated 9 October 2026. The user's quoted handoff was recovered from Git commit
`f84667064f0477325ab05b3689c36d7a0b7a8c23` (`origin/main` in this checkout).
This checkout's active branch, `py314-and-package-names`, contains a different
research history. The original protocols were read from Git and preserved;
this continuation does not merge or replace either history.

**Data access is no longer the general blocker.** The original RibbonDB input
was downloaded and its registered test completed. Other full datasets and
explicitly limited access samples are retained under
`data/dataset-audit/2026-10-09/`, with checksums and acquisition details.

| Dataset | Access demonstrated here | Test and readiness |
|---|---|---|
| [RibbonDB v1.0](dataset-audit-flare-2026-10-09.md) | Full 656 KB CSV, 3,137 rows; documentation and archive | **Original test run:** area α = 3.163 [2.962, 3.457]. Registered verdict inconclusive; excludes both 2 and 7/3 under the implemented uncertainty model. |
| [UKCEH UK waterbody inventory v3.6](dataset-audit-lakes-2026-10-09.md) | Full 8.59 MB ZIP; 41,830 polygon features; structural checks pass | Small regional lake replication. Needs format/CRS adapter and a separately declared protocol; sample within R = 1–20 km is not yet known. |
| [HydroLAKES v1.0](dataset-audit-lakes-2026-10-09.md) | Official server returned ZIP bytes; advertised size 820.3 MB; only first 4 KB saved | Exact original lake source. Full download/hash and projection/dependence review remain. |
| [Ridgecrest AWR v2](dataset-audit-seismic-2026-10-09.md) | Full 19.73 MB CSV; 222,864 events; publisher checksum verified | Magnitude–hypocentre candidate. Needs physical cluster definition and eligibility checks. |
| [Ridgecrest QTM](dataset-audit-seismic-2026-10-09.md) | Full 4.46 MB archive; 111,918 detections, 46,512 marked relocated | Alternative with location-error fields. Relocation components do not supply the required qualifying physical clusters. |
| [USFS FPA FOD v7](dataset-audit-wildfire-2026-10-09.md) | Successful 1,000-record API sample plus metadata; full inventory advertised at ~2.66 million fires | New-domain candidate: burned-area allocation and transfer across years. Needs complete cohorts and a new protocol; no fit run. |

The [flare result report](flare-ribbons-run-2026-10-09.md) retains the exact
implementation, pre-run exposure, uncertainty assumptions and reproduction
command. In particular, the original GOF diagnostic uses a different support
from the primary exponent fit; neither p-value establishes the whole procedure's
adequacy. No result from the alternative datasets was used to select a preferred
resource interpretation.

## Next scientific work

1. For the original lake hypothesis, acquire the full HydroLAKES source. Preserve
   the registered radius range and decision rule. Inspect the distance projection
   and spatial uncertainty implementation before issuing a physical interpretation.
2. Use the small UKCEH polygon source for a separately declared regional replication,
   accounting for reservoirs, basin splits, mapping history and actual radius
   eligibility. Compute radius from geometry rather than from square root of area.
3. For seismicity, freeze a defensible physical clustering procedure before fitting
   b or D2. The original rule needs at least ten qualified clusters and sufficient
   dimension contrast; hundreds of thousands of detections alone do not satisfy it.
4. Register wildfire area allocation as a new test only after defining the resource,
   population and observation period. Include model alternatives, goodness of fit,
   dependence and a withheld-year prediction; merely finding a power law is not a
   discriminating result.

The earlier "hosts unreachable" status reflected the execution environment.
Approved network access through system `curl` retrieved public files without
disabling certificate verification. Some browser/API routes still fail; successful
payload downloads, metadata-only access and partial samples are distinguished in
the linked audits. Dryad WUMI and LAGOS remain candidates, not verified full payloads.

This work adds one completed registered analysis and several usable data routes.
It does not add empirical support for either flare prediction.
