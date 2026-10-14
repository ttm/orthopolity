# Natural-system follow-up: measured particle costs before another fit

The [saltation design gate](saltation-qualification-results-2026-10-14.md)
has failed and its real response fitting is stopped. A further methods scan
found accessible particle-tracking data, but has not established a qualified
new allocation test. This note records the actual gaps rather than treating
availability as sufficient evidence.

## Strongest new lead: spherical and irregular grains

Su et al. (2026), *Deep learning-based particle tracking velocimetry (PTV) for
spherical and non-spherical particles: Application to sediment transport*,
[doi:10.1029/2025WR042825](https://doi.org/10.1029/2025WR042825), has a public
[versioned archive](https://zenodo.org/records/19312642), CC BY 4.0.
Its `datasets.xlsx` (113,216 bytes) and publisher inventory are downloaded,
with acquisition receipts, SHA-256 and verified publisher MD5 under
`data/natural-candidates/2026-10-14/su2026/`. Other files remain metadata-only:
Figure 14 data (9,164 bytes), Figure 15 data (76,296 bytes), and two small code
archives. No original workbook was modified or source code executed.

Methods describe seven conditions for each grain type, short near-wall
videos and independently collected outlet sediment. Hydraulic stress is
estimated from flow geometry and slope with a wall correction. **Equilibrium
acceptance requires outlet flux close to supplied feed.** Predicting that same
accepted outlet flux from feed would largely reproduce an admission criterion.
Separate videos are not automatically independent replicated experiments.

The retained schema audit identifies velocity profiles, shear rate, granular
temperature and rotational velocity, alongside stress/flux comparisons and
detector validation. Figure 10 has corrected Shields stress and flux labels;
Figures 11–12 have sphere velocity/shear/temperature profiles; Figure 13 has
gravel rotation/shear labels. This establishes accessible observables. It does
not establish separately assayed per-particle collision costs or a complete
size-specific incidence distribution. Some panels contain simulations or
literature comparisons, so panel provenance must be resolved before any fit.

**Exposure:** the methods search returned published Table 1 aggregate outcomes.
A subsequent text-cell schema pass also exposed Table1 B2:H8's slash-separated
numerical pairs. They are retained in the audit and must not later be described
as unseen or blind targets. Typed numerical figure arrays have not been
analyzed or fitted. Inspecting text cells alone is not a reliable blinding
procedure: numbers can be encoded as text.

A possible future prediction would calibrate a transport mechanism on spheres
and forecast irregular-grain incidence or independent trap flux using separately
measured shape/collision costs. The present audit has not qualified those costs.
Estimating them from the same irregular-grain response would remove the intended
independence. A separate protocol must resolve this before numerical calibration.

## Other candidates and their specific limits

| Source | Reachable material | Missing prerequisite |
|---|---|---|
| [Frey–Ducottet / Dudill trajectories, Zenodo 14624102](https://zenodo.org/records/14624102) | Two MAT trajectory files, 285,510 and 39,248 bytes, plus a 2,336-byte README; coarse beads under low/high fine feed | Only coarse 5-mm particles are tracked; two short clips; independent hydraulic and outlet-flux measurements are not in this small archive |
| [Ashley et al. plane bed / bedforms](https://api.figshare.com/v2/articles/11413038), [methods](https://doi.org/10.1029/2020JF005647) | Eight CSVs totaling 577,748 bytes; two ten-second clips per condition; bed manually flattened while flow boundaries are held | Tracks lack per-particle size and independently measured resource cost; only two condition blocks and no separate outlet flux in this archive |
| [Dingle–Venditti gravel/sand experiments](https://zenodo.org/records/6261166), [methods](https://doi.org/10.1029/2023JF007117) | Small workbooks with controlled feed and size-fraction output | Fluid velocity and settling velocity are computed, not independently measured grain velocities; some initial availability is assumed; separate washload and suspended-bed-material flux cannot be measured |
| [Staudt et al., PANGAEA 901393](https://doi.pangaea.de/10.1594/PANGAEA.901393) | Mixture sizes, fluid profiles, bed level and bulk suspended concentration | Inventory does not identify size-resolved suspended incidence or separately measured particle costs |
| [WIND-O-V](https://dataverse.ird.fr/dataset.xhtml?persistentId=doi:10.23708/PW2FVY&version=1.3) | Metadata describes independent soil sizes, wind and transported material | The 281.4-kB ODS is explicitly restricted; it does not meet the current public-download requirement |

These are metadata/methods findings, not fitted results. Only the Su publisher
inventory and main workbook were downloaded during this follow-up. The first
two trajectory archives remain concrete accessible leads if their original
experimental records can supply the missing independent quantities.

## Interpretation and source-convention note

Computing transported volume as count times particle volume times speed from
the same trajectories checks an identity. A prediction of unused incidence
requires costs and opportunities specified independently of that incidence.
Neutral **log-orthopolic** size allocation would compare resource per d ln size;
neutral **linear-orthopolic** allocation would compare it per d size. Neither
choice follows automatically from having particle tracks. A conditional
transport forecast can still be useful, but needs an explicit physical model
and should not be promoted to a neutral-allocation test.

A further review of the original saltation workbook's Notes!B15 shows that
its wind angle is referenced to the dominant wind during saltation. Thus the
direction convention uses transport context even though our reader accesses
only wind columns. The Reynolds stress measurement remains distinct from sand
measurement, but the published preprocessing is not wholly response-agnostic.
This is an additional qualification of a study already stopped at its synthetic
gate; no filters, simulations or verdict were changed after this observation.

Next priority: establish an independent shape/collision-cost source for the
Su archive, or find a particle-tracking experiment with both measured costs
and size-specific incidence under an unused intervention. Until then, preserve
the completed results and avoid adding another bulk-flux exponent comparison
to the article as if it established general allocation.
