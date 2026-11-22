# TNG development inventory and cadence findings

21 November 2026. **The bounded acquisition and whole-inventory reader work.**
All three outputs contain the same 19,683,000 unique particle IDs, and every
particle is assigned exactly once to a resolved FoF host or the diffuse
reservoir. Measured endpoint changes also show substantial information loss
when the middle output is omitted. This completes acquisition and the first
part of D3; local transport and an independent abundance prediction remain
unqualified.

The resource is **log-orthopolic collisionless total-matter mass**. The whole
`TNG50-4-Dark` run remains development-only. No exponent, plateau, validation
target or empirical registry entry is selected by this work. These are
simulation diagnostics, not a confirmation of the proposed natural law.

## Acquisition and integrity

The [fixed manifest](../configs/cosmic-development-2026-11-20.json) and
[acquisition plan](cosmic-development-acquisition-2026-11-20.md) precede the
numerical download. The [completed receipt](../data/cosmic-development/2026-11-20/tng50-4-dark-attempt-02/acquisition.json)
records all 27 files: twelve ID-only snapshot chunks, twelve group-catalogue
chunks and three offset files. Raw files total **505,904,248 bytes**; cumulative
response content is **505,904,305 bytes**, including the preserved 57-byte
initial format error. This leaves **299,402,063 bytes** under the unchanged
768 MiB cap. D1 metadata retains its separate 19,587-byte total.

The [bootstrap verdict](../data/cosmic-development/2026-11-20/tng50-4-dark-attempt-02/bootstrap-validation.json)
checks the selected fields, headers and chunk boundaries. The
[material verdict](../data/cosmic-development/2026-11-20/tng50-4-dark-attempt-02/material-validation.json)
checks all raw hashes, offsets, disjoint memberships, unique IDs, equality of
the ID sets and the whole-output catalogue counters. The
[unit audit](../data/cosmic-development/2026-11-20/tng50-4-dark-attempt-02/snapshot-unit-audit.json)
independently verifies identical cgs code-unit factors in all twelve snapshot
chunks. The reader uses about **0.96 GiB peak resident memory**, below its 3 GiB
limit, and writes no derived scratch arrays.

| Output | FoF hosts | Particles in hosts | Diffuse particles | Fraction in hosts | Integer closure residual |
|---|---:|---:|---:|---:|---:|
| 97 | 18,976 | 10,025,728 | 9,657,272 | 50.9360% | 0 |
| 98 | 18,888 | 10,068,046 | 9,614,954 | 51.1510% | 0 |
| 99 | 18,824 | 10,095,112 | 9,587,888 | 51.2885% | 0 |

Each particle represents about **275.694 million solar masses**; the comoving
box side is about **51.668 Mpc**. Inventory mass is integer particle count
times the verified particle mass, using the declared h conversion. Across all
56,688 catalogue entries, the largest relative difference between `GroupMass`
and count times particle mass is **5.6702e-8**. Every entry falls within the
declared float32 final-rounding allowance, **5.961e-8**. That compatibility does
not identify the catalogue's accumulation algorithm; the exact count-based
inventory remains the operative resource.

Two schema findings and one client correction are retained rather than erased:
the API required a compatible Accept header; the actual file-offset array is
stored as (chunk, type), transposed relative to the documentation; and
`Nids_ThisFile` cannot be treated as the membership sum of groups stored in
the same catalogue chunk. The failed reader verdict, original reader source,
[counter audit](../data/cosmic-development/2026-11-20/tng50-4-dark-attempt-02/group-counter-audit.json)
and explicit amendments remain linked from the acquisition plan. The corrected
counter check requires exact whole-output agreement. No physical tolerance
was changed to obtain the result.

## Endpoint changes and cadence

For a particle hosted at both endpoints, the diagnostic is the logarithm of
the ratio of its endpoint host masses. Equal particle masses make particle
weighting equivalent to material-mass weighting. The host labels themselves
are not matched across outputs: “hosted at both endpoints” includes particles
remaining in a host whose mass changes. It does not mean that all such
particles switched hosts. Diffuse particles have no assigned logarithmic host
mass and are reported separately.

| Interval | Duration, Gyr | Diffuse → host particles | Host → diffuse particles | Net gain in hosted particles | Factor ≥2 host-mass change, among particles hosted at both endpoints |
|---|---:|---:|---:|---:|---:|
| 97 → 98 | 0.203586 | 335,184 | 292,866 | 42,318 | 1.2892% |
| 98 → 99 | 0.136488 | 277,680 | 250,614 | 27,066 | 1.2581% |
| 97 → 99 | 0.340075 | 426,098 | 356,714 | 69,384 | 1.7574% |

Durations use the declared flat matter-plus-Lambda cosmic-time convention,
omitting radiation at these low redshifts. The two unequal durations add to
the coarsened interval. The table reports integrated particle transfers;
rates must be weighted by their durations before combining intervals.
The factor-two statistic includes either an increase by at least two or a
decrease to at most one-half of the earlier host mass.

Among the **9,569,584 particles hosted at all three outputs**:

- **3,198,908 (33.43%)** reverse the direction of their host-mass change.
- The sum of absolute log changes over both adjacent intervals is
  **1,208,781.434**, versus **857,001.508** between the outer endpoints.
  Omitting output 98 therefore loses **29.10%** of the resolved variation.

Reservoir excursions give a separate exact accounting check. There are
**99,430 host → diffuse → host** paths and **87,336 diffuse → host → diffuse**
paths. Adjacent intervals contain **1,156,344** gross particle transitions
between host and diffuse states; the outer endpoints retain **782,812**.
The difference is exactly twice the number of excursions. Coarsening thus
loses **32.30%** of the resolved gross exchange while preserving the net stock
change. These counts are transitions, so one particle may contribute twice.

These findings demonstrate losses at the coarser cadence. They do not show
that the finer cadence has converged, nor that each endpoint jump is an
instantaneous physical trajectory. Occasional large changes and reservoir
exchange cannot be discarded merely because most endpoint mass ratios are
small.

## Next gate and repository scope

D3 is **partially complete**. Next fix development mass bins and measure their
stocks, full endpoint transfer counts, cumulative boundary currents and
diffuse source terms. Check row/column conservation and compare the direct
endpoint current with the stated drift approximation. Then assess stationarity,
nonlocal contributions and cadence uncertainty over explicit intervals. These
remain development diagnostics; thresholds or intervals selected here must
not be presented as independent evidence.

D4's independent-source qualification remains conditional on those findings.
D5 still requires separately calibrated inputs, a declared transfer rule,
competing predictions and a separate abundance target fixed before exposure.
The present results establish neither a universal cosmological constant nor
the physical equality J=vr.

Validation: **819 Python tests and 27 JavaScript tests pass** in the existing
Python 3.11 environment with the isolated HDF5 dependency. Independent review
checked the joins, units, mass-rounding interpretation, pair partitions,
net stock changes and coarsening identities. The historical registry remains
**46 runs / 1,168 references**. No manuscript, PDF, prior empirical result,
frozen historical input or registry entry changed. Full historical analysis
regeneration was not repeated; the 10 November `make all` baseline remains.
