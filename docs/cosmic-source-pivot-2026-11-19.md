# Cosmic source alternatives: preserved access findings

19 November 2026; records the alternative-source work begun on 16 November.
The author asked to park TNG while registration remained pending and continue
with another public source. That instruction authorized a bounded extension of
the original three-archive audit to **CAMELS and AbacusSummit**. It did not reopen
earlier unrelated searches or relax the scientific qualification gates.

**Decision:** CAMELS remains a fallback with incomplete access qualification.
Its public directory and snapshot endpoints worked anonymously, but the selected
group-catalogue endpoints returned HTTP 403. Complete anonymous access to the
material inputs was therefore **not verified**. On 19 November the author supplied
TNG credentials, allowing the original authenticated metadata gate to resume.
That request's outcome belongs in its own acquisition record; possession of a
credential alone is not evidence of successful data access.

The intended resource remains **log-orthopolic collisionless total-matter mass**
in a dark-matter-only simulation, assigned once to disjoint hosts or an explicit
diffuse reservoir. Access findings neither confirm nor reject that allocation.

## CAMELS: listing access succeeded, group access did not

CAMELS officially offers a direct URL route separately from its Binder signup
route. The documentation also warns of an earlier FoF/Subfind catalogue bug
affecting several suites, including Illustris DM CV, and states that current
public catalogues are corrected. These statements identify a candidate source;
they do not establish that every linked file is currently retrievable.
[Official access documentation](https://camels.readthedocs.io/en/latest/data_access.html).

The chosen development candidate was `IllustrisTNG_DM/L25n256/CV/CV_0`, with
the last three stored outputs selected before opening any numerical arrays.
The anonymous directory GET returned **HTTP 200**, retaining **18,571 bytes**
under a **65,536-byte** listing cap, with TLS certificate and hostname
verification enabled. The directory lists 34 snapshots; its last stored outputs
are **086, 088 and 090**, so an assumed output 089 would be incorrect.
The [listing receipt](../data/cosmic-source-qualification/2026-11-16/camels-cv0-directory/receipt.json)
and [file manifest](../data/cosmic-source-qualification/2026-11-16/camels-cv0-directory/file-manifest.json)
preserve URLs, hashes, timestamps and the six HEAD responses.

| Output | Snapshot HEAD | Snapshot Content-Length | Group HEAD | Group size in directory listing |
|---|---|---:|---|---:|
| 086 | 200 | 207,171,198 bytes | 403 | 38,550,864 bytes |
| 088 | 200 | 207,087,718 bytes | 403 | 38,963,632 bytes |
| 090 | 200 | 207,235,513 bytes | 403 | 39,384,848 bytes |

The snapshot lengths match the directory metadata. Each group response instead
advertised a 153-byte HTML error response; that is **not** its catalogue length.
The six listed data files total 738,393,773 bytes, but that total is only an
inventory calculation, not a successful-download measurement. HEAD requests
read no bodies. No HDF5 file, particle array, halo-mass row or target distribution
was opened. The group HTTP status alone does not diagnose whether the cause is
an account requirement, server permissions or another archive condition.

CAMELS documentation describes N-body particles as the represented total-matter
inventory. For this DMO suite the intended membership reader uses catalogue
`/IDs/ID`, segmented by `Group/GroupLen`, joined to snapshot
`/PartType1/ParticleIDs`; it must not assume the hydrodynamic TNG snapshot order.
The documentation describes lossless particle-ID compression and snapshot
headers for masses, box size, times and cosmology. Actual field presence, ID
uniqueness/persistence, complete membership including fuzz, integer-mass closure
and cadence adequacy remain untested.
[Simulation description](https://camels.readthedocs.io/en/latest/description.html),
[membership tutorial](https://camels.readthedocs.io/en/latest/examples/particles_subhalos.html),
[snapshot schema](https://camels.readthedocs.io/en/latest/snapshots.html).

## AbacusSummit: reserve candidate with a different observation model

The documentation review did not verify an anonymous file manifest. Its access
instructions describe Globus transfers and Binder signup. Routine material
histories use fixed hash-selected particle subsamples, typically 3% A and 7% B;
secondary epochs omit field-particle samples. Sample closure therefore cannot
be reported as full-material closure. The CompaSO host convention also differs
from the present ordinary-FoF measurement contract. A usable version would need
an explicit sampling/error model, reservoir accounting and a declared represented
mass component. This route was retained as a reserve, without numerical downloads.
[Access documentation](https://abacussummit.readthedocs.io/en/latest/data-access.html),
[data products](https://abacussummit.readthedocs.io/en/latest/data-products.html),
[halo definition](https://abacussummit.readthedocs.io/en/latest/compaso.html).

## Current scope

Resume the original TNG **metadata-only** operation with the author's newly
available credential, preserving its shared byte budget and target-exposure
rules. Do not discard the earlier [authentication finding](cosmic-metadata-access-2026-11-12.md)
or treat the new credential as qualification of transport, stationarity or
independent prediction inputs.

Keep CAMELS as a fallback. Before any future CAMELS numerical acquisition,
resolve access to its required group memberships, verify the exact file/header
inventory and freeze a development-only acquisition budget. Do not silently
substitute a different suite or mass convention. No validation target has been
assigned or sealed, and no new cosmic empirical result is claimed.

No background polling, account creation, provider contact or further source
search was performed as part of preserving this handoff. Manuscripts, historical
study inputs/results and the empirical registry are unchanged.
