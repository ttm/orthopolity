# Authenticated TNG metadata qualification

20 November 2026; authenticated API acquisition ran on 19 November. **TNG
authentication now works.** Eleven JSON requests retrieved the run, all output
times, three selected snapshot descriptions and their six chunk lists. All
returned HTTP 200, complete JSON bodies and retained SHA-256 receipts. No
numerical particle or halo catalogue was requested in those acquisitions.

The [first receipt](../data/cosmic-source-qualification/2026-11-19/tng50-4-dark-metadata/acquisition.json)
records 17,762 new response bytes; the
[continuation](../data/cosmic-source-qualification/2026-11-19/tng50-4-dark-file-lists/acquisition.json)
records another 1,770. Including the earlier 55-byte authentication error,
the shared D1 budget is **19,587 / 1,048,576 bytes**, leaving **1,028,989 bytes**.
Prior-receipt hashes link the operations; source snapshots retain the acquisition
code used at each stage. The key was entered without terminal echo, sent only
in the API header, and not retained in files, receipts or program output.

## Defined development population

The **whole `TNG50-4-Dark` run is development-only**. Outputs **97, 98 and 99**
were chosen as the last three in the returned schedule, before any numerical
arrays were opened. This selection leaves no later temporal target in that run.
A future validation needs a separate qualified population and an explicit
transfer rule. No target has been assigned or sealed.

The resource remains **log-orthopolic collisionless total-matter mass**, among
disjoint FoF hosts and an explicit diffuse reservoir. The API describes a
uniform DMO box with **19,683,000 particles**, **100 outputs**, **four snapshot
chunks** and **four groupcat chunks** per output. Run values are:

| Quantity | Retained API value | Interpretation |
|---|---:|---|
| Box side | 35,000 | comoving kpc/h |
| Particle mass | 0.0186754872146347 | $10^{10}M_\odot/h$ |
| $h$ | 0.6774 | unit conversion |
| $\Omega_m,\Omega_\Lambda,\Omega_b$ | 0.3089, 0.6911, 0.0486 | DMO represents total matter, not cold dark matter alone |

With those declared units, the side is about 51.668 Mpc and particle mass about
$2.75694\times10^8M_\odot$. These are conversions of API metadata; actual HDF5
headers still need to agree. The source
[specifications](https://www.tng-project.org/data/docs/specifications/) define
the units and intended fields.

| Output | Redshift from API | Snapshot bytes, all fields | Groupcat bytes |
|---|---:|---:|---:|
| 97 | 0.0239744283827625 | 629,924,736 | 8,261,432 |
| 98 | 0.00952166696794476 | 629,924,736 | 8,238,592 |
| 99 | 2.22044604925031e-16 | 1,259,797,120 | 8,207,696 |

The full snapshot total is **2,519,646,592 bytes**; full groupcats total
**24,707,720 bytes**. ID arrays alone require **472,392,000 bytes** for three
complete populations of 64-bit integers, before file overhead. Do not equate
that calculation with a measured selected-field response size. The tiny
nonzero final redshift is preserved as returned, rather than silently rounded.
Scale factor may be derived as $1/(1+z)$; elapsed cosmic time requires a stated
cosmological conversion and cannot be replaced by a redshift difference.

Global FoF/Subfind counts returned with the metadata are exposed development
information. No mass-resolved profile, individual halo row or target endpoint
was queried. The file lists identify **24 exact chunk URLs**; receiving links
does not mean their file contents were downloaded.

## File access and remaining qualification

The official [API reference](https://www.tng-project.org/data/docs/api/)
distinguishes JSON file-list endpoints from HDF5 downloads and documents
`dm=ParticleIDs` selection plus offset-file endpoints. The retained lists were
followed only to JSON metadata. Original HTTP links were validated against
the exact TNG host/path and upgraded to HTTPS before authentication.

Three representative HEAD requests on 20 November identified HTTPS redirects
to **`data-eu.tng-project.org`** for an ID-only snapshot chunk, a groupcat chunk
and an offset file. The
[HEAD receipt](../data/cosmic-source-qualification/2026-11-20/tng-development-headers/acquisition.json)
retains only sanitized destination paths. Signed query values were not saved;
those requests read no bodies and did not follow the redirect. The subsequent
[27-file HEAD inventory](../data/cosmic-source-qualification/2026-11-20/tng-selected-file-headers/acquisition.json)
followed one validated redirect per request without forwarding the API key.
Twenty-three data-host responses returned HTTP 200 with lengths; four timed out.
No bodies were read, and the D1 byte count is unchanged. The exact known lengths
and unresolved four lengths are retained in the D2 executable manifest; all
numerical transfers remain subject to its independent hard streaming budget.

The [D2 development acquisition plan](cosmic-development-acquisition-2026-11-20.md)
specifies a small bootstrap, the complete 27-file selection, hard byte limits,
storage/memory limits and binary-schema checks. The metadata-only portion of D1
is complete. Its original full-schema requirement was unverified at that stage;
the subsequent bounded D2 bootstrap passed with its own binary observations.
The retained D1 receipts deliberately keep `complete_D1_manifest=false`,
preserving what was known at acquisition time. The
[21 November development report](cosmic-development-results-2026-11-21.md)
records the completed acquisition, exact inventories and measured cadence
losses. Physical transport eligibility remains separate from those checks.

## Preserved alternatives and checks

The [CAMELS/Abacus handoff](cosmic-source-pivot-2026-11-19.md) preserves the
author-authorized alternative-source review. CAMELS snapshots answered anonymous
HEAD requests, but the selected group files returned 403, so it remains an
incomplete fallback. No new archive family is being opened now that TNG access
is available.

Offline client tests check URL scope, shared budget, truncated/error responses,
credential-echo suppression, redirect refusal, continuation integrity and
retained body/source hashes. The session status records the final check count.
Authentication and metadata access establish neither local transport nor an
independent cosmic abundance prediction. Manuscripts, historical studies and
empirical registry entries are unchanged.
