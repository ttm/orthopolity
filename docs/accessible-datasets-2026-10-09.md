# Continuing the registered tests with accessible data

Updated 9 October 2026. The user's quoted handoff was recovered from Git commit
`f84667064f0477325ab05b3689c36d7a0b7a8c23` (`origin/main` in this checkout).
The initial audit ran on `py314-and-package-names`, which contained a different
research history. At the user's subsequent request, both histories were merged
into `main`; further work takes place there. Original protocols and retained
implementation snapshots remain preserved.

**Data access is no longer the general blocker.** The original RibbonDB input
was downloaded and its registered test completed. Other full datasets and
explicitly limited access samples are retained under
`data/dataset-audit/2026-10-09/`, with checksums and acquisition details.

| Dataset | Access demonstrated here | Test and readiness |
|---|---|---|
| [RibbonDB v1.0](dataset-audit-flare-2026-10-09.md) | Full 656 KB CSV, 3,137 rows; documentation and archive | **Original test run:** area α = 3.163 [2.962, 3.457]. Registered verdict inconclusive; excludes both 2 and 7/3 under the implemented uncertainty model. |
| [UKCEH UK waterbody inventory v3.6](dataset-audit-lakes-2026-10-09.md) | Full 8.59 MB ZIP; 41,830 polygons; 148 meet the fixed radius range | Separate frozen replication run: ζ = 1.441; ordinary interval excludes 2, spatial interval includes it. |
| [HydroLAKES v1.0](dataset-audit-lakes-2026-10-09.md) | Full 820.3 MB archive downloaded and verified; 1,427,688 polygons | Original calculation run on 119,683 eligible lakes: ζ = 1.930; ordinary equivalence passes, spatial equivalence not established. |
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

1. The [original and regional lake runs](lake-gyration-results-2026-10-09.md)
   are complete. Specify a follow-up for physical distance, full polygon geometry,
   adequacy and hydrological dependence; preserve the completed primary result.
2. Interpret the UK difference with its sampling limits and overlapping geography.
   It cannot isolate the effects of projection, geometry, mapping and cohort.
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

This work adds the completed original flare and global-lake calculations, a
separately frozen UK replication and several usable data routes. The global
lake ordinary-bootstrap result supplies conditional exponent agreement, with
the spatial and geometric limits stated in the report. Neither flare prediction
is supported by its implemented analysis.
