# TNG development acquisition plan

20 November 2026. **D2 request list and limits fixed before numerical acquisition.**
The [executable manifest](../configs/cosmic-development-2026-11-20.json), SHA-256
`3955efd01d4d66d6a43db57c18878e424af4f65f618804f1f28d2502ae17e90d`,
contains the exact 27 requests, source hashes and limits. This plan turns the successful
[run/snapshot metadata acquisition](../data/cosmic-source-qualification/2026-11-19/tng50-4-dark-metadata/acquisition.json)
and [chunk-list acquisition](../data/cosmic-source-qualification/2026-11-19/tng50-4-dark-file-lists/acquisition.json)
into a bounded reader-development pilot. It follows the
[measurement design](cosmic-test-design-2026-11-11.md); it is not a validation
protocol or an abundance prediction.

## Scope and already known inputs

Designate the **whole `TNG50-4-Dark` run development-only**. Use outputs **97,
98 and 99**, the last three stored outputs selected from the schedule before
any numerical arrays were opened. They leave no later temporal target in this
run. A future prediction needs a separately qualified target and transfer rule;
no target is assigned here. Matched-resolution and hydro/DMO counterparts are
not independent realizations.

The resource is **log-orthopolic collisionless total-matter mass** assigned once
to disjoint FoF hosts or the diffuse reservoir. API metadata gives 19,683,000
DMO particles, four snapshot chunks and four group-catalogue chunks per output,
box side 35,000 comoving kpc/h, and particle mass 0.0186754872146347 in
$10^{10}M_\odot/h$. It reports $h=0.6774$, $\Omega_m=0.3089$,
$\Omega_\Lambda=0.6911$ and $\Omega_b=0.0486$. Verify these against actual headers
before using them in the reader.

| Output | API redshift | Full snapshot bytes reported by API | Full group-catalogue bytes reported by API |
|---|---:|---:|---:|
| 97 | 0.0239744283827625 | 629,924,736 | 8,261,432 |
| 98 | 0.00952166696794476 | 629,924,736 | 8,238,592 |
| 99 | 2.22044604925031e-16 | 1,259,797,120 | 8,207,696 |

The complete snapshots total **2,519,646,592 bytes**; the group catalogues total
**24,707,720 bytes**. These are observed API metadata, not downloaded-file
measurements or per-chunk sizes. Three complete populations of 64-bit IDs alone
require **472,392,000 bytes** ($3\times19{,}683{,}000\times8$), excluding HDF5
overhead. The retained
[HEAD inventory](../data/cosmic-source-qualification/2026-11-20/tng-selected-file-headers/acquisition.json)
observed HTTP 200 and lengths for 23 files, totalling **421,539,448 bytes**.
Four data-host HEAD requests timed out: snapshot 99 chunks 2/3 and offsets
97/99. Their sizes remain unknown. No response bodies were read. The observed
selected-ID chunks are about 39.4 MB each; the offset-98 file is 2,763,760 bytes.
The unknown sizes remain subject to the same hard streaming limits.
Reported redshift zero has floating-point roundoff; header `Time` is a scale
factor, not elapsed cosmic time.

## Exact request families and retained fields

Use only HTTPS URLs on the approved TNG service. Build the 24 chunk URLs from
the retained JSON lists, retaining their source hashes. Snapshot and catalogue
chunk numbers are **0–3** for each selected output.

| Product | Request selection | Reader consumes |
|---|---|---|
| Twelve snapshot chunks | Append the documented `dm=ParticleIDs` selector to each retained snapshot-chunk URL | `PartType1/ParticleIDs`; header particle counts, `MassTable`, `BoxSize`, `Time`, `Redshift`, cosmology and file count |
| Twelve group-catalogue chunks | Exact retained groupcat-chunk URLs, no added population filter | `Group/GroupLenType`, `Group/GroupMass`, catalogue headers; other downloaded fields remain unused |
| Three offset files | Documented `/api/TNG50-4-Dark/files/offsets.{97,98,99}.hdf5` endpoints | `Group/SnapByType` and file offsets required to map global group starts into snapshot chunks |

The API documents snapshot field selection and offset endpoints. The source
specifications define the inventory and offset fields. Keep those documentary
expectations separate from the binary schema check below.
[API reference](https://www.tng-project.org/data/docs/api/),
[field specifications](https://www.tng-project.org/data/docs/specifications/).

No coordinates, velocities, merger trees, subhalo selection, mass-function query
or alternate run is requested. Whole group catalogues are small enough to keep
their headers and length/mass fields together; receiving their unused subhalo
fields does not make those values validation inputs. Record this exposure as
development-only. Do not replace the inventory mass with `M200c`.

## Transfer, disk and memory limits

These are **hard acquisition limits**, not measured file sizes. They
allow for unknown selected-field overhead. They are fixed in the executable
manifest before the first body is read:

- **768 MiB (805,306,368 bytes)** aggregate response-body budget for D2, including
  error bodies, failed attempts and any explicitly permitted redirect bodies.
  This is a new numerical-acquisition budget; do not charge it to, or silently
  enlarge, the earlier 1 MiB D1 metadata budget.
- **64 MiB per ID-only snapshot chunk**, **16 MiB per groupcat chunk** and
  **8 MiB per offset file**, all additionally bounded by the remaining aggregate
  budget. A valid but larger file requires a recorded plan amendment; never
  increase the limit automatically.
- Require **4 GiB free workspace disk** before starting. Stream to temporary
  files, hash while writing, then rename only complete files. Keep raw material
  out of Git; retain checksums, sizes, sanitized provenance and receipts.
- Target a **3 GiB peak resident-memory ceiling** for the reader and **1 GiB
  derived/scratch storage**. Process one epoch or one pair at a time, reusing
  arrays. Avoid a dense host-by-host transition matrix; use sparse transitions
  or fixed mass-bin accounting. Stop before allocations exceed the plan.

An advertised `Content-Length` above its limit is a pre-read stop; a missing
length requires streaming enforcement. Partial files remain explicitly partial
and cannot be treated as valid HDF5 inputs. No automatic retries or recursive
downloads. A later retry carries forward all consumed bytes. For redirects,
inspect scheme and destination first; never forward the API key to another
host or persist credential-bearing URLs. Credentials remain outside files and
logs. Source-provided hashes, when available, are additional checks; local
SHA-256 records the exact received bytes, including generated cutouts whose
hash will differ from an unfiltered source file.

## Bootstrap without assuming the binary schema

Before acquiring the full selection, verify the implementation's URL/selector,
credential, redirect and byte-limit behavior offline, and inspect available
HEAD metadata. Exact returned field sizes need not be known if the limits above
are enforced. Retrieve **one offset file, one groupcat chunk and one ID-only
snapshot chunk from output 97** within those same limits. Inspect headers,
dataset names, shapes and dtypes before material analysis.

Require readable complete HDF5 files; the selected snapshot may contain header
metadata and `ParticleIDs`, but no additional particle-data fields. Require
64-bit integer IDs, six-component particle-count/mass arrays, consistent run
identity and units, and usable group/offset fields. The source snapshot header
may retain original particle counts after field selection; removing other
fields must not be interpreted as removing particles. Do not expect one chunk
to close the whole-box budget.

If a field is missing, selection is ignored, a limit is exceeded or a binary
header disagrees with the declared resource, stop with that specific finding.
Do not download a full snapshot as an automatic fallback. If the bootstrap
passes, finish the remaining allowlisted files and run whole-output checks.
This ordering permits schema discovery while keeping the entire run classified
as development and the acquisition bounded in advance.

## Reader integrity and development outputs

For each output, join the four chunks in documented file order; validate header
totals, ID uniqueness and a consistent full ID set across epochs. Require
19,683,000 represented particles unless a source discrepancy is resolved before
analysis. Use `GroupLenType[:,1]` and `Group/SnapByType` to assign every grouped
particle exactly once across chunk boundaries. Every remaining particle belongs
to the explicit diffuse reservoir. Check offset bounds, disjoint ranges and
integer inventory closure exactly. Compare catalogue `GroupMass` with
`GroupLenType[:,1] * MassTable[1]`, separating floating-point representation
error from missing material; a tolerance must follow dtype/rounding analysis,
not be tuned to hide a discrepancy.

Convert mass and volume using the verified $h$ factors. Derive interval durations
from header scale factors with a stated cosmological time convention; do not
substitute differences in redshift or scale factor for cosmic time. Preserve
all exact header values alongside any derived physical units.

Then report host/diffuse transfers and integer conservation for 97→98, 98→99
and the coarsened 97→99 interval. Record mass-weighted logarithmic host-mass
jumps, upward/downward contributions, diffuse entry/exit, and observed changes
in class stocks. Compare integrated transferred masses (or duration-weighted
currents) across the two resolved intervals with the coarsened endpoints to
expose missed reversals and reservoir excursions; do not add rates without
their interval durations.
Endpoint conservation is a reader identity, not proof of $J=vr$. Three epochs
can reveal a cadence problem but cannot establish convergence or instantaneous
residence times.

This pilot may establish a working material reader or identify an eligibility
failure. It does not choose a validation plateau, validate an abundance
forecast, establish observational confirmation or create an empirical registry
entry. Freeze any later scientific interval, residual tolerances, input-transfer
rule and separate target only after these development findings are retained.

## Reproduction environment

Acquisition uses the standard library. HDF5 inspection uses the optional
`cosmic` dependency, `h5py==3.12.1`. This session installs it in
`build/cosmic-tools` with `--no-deps`, retaining the existing Python 3.11.6 and
NumPy 2.3.5 environment. The installed wheel uses HDF5 1.12.2. Use
`PYTHONPATH=src:build/cosmic-tools` for these development checks; no historical
analysis dependency was replaced. The source/config snapshots and file hashes
in the acquisition directory identify the exact inputs to a later replay.

## Acquisition execution and amendments

The [first bootstrap attempt](../data/cosmic-development/2026-11-20/tng50-4-dark/acquisition.json)
stopped on its first API request with HTTP **406**, before any HDF5 file or
redirect. Its **57 response bytes** have SHA-256
`a5d55bea935e8c7176837edb49d58892bb4356c604fe8028bfa71c96ad81edd3`.
The locally reconstructed JSON `{"detail":"Could not satisfy the request Accept header."}`
matches that hash exactly. The client had requested `application/octet-stream`
from the API endpoint. This is a content-negotiation failure, not a material
schema finding. The failed source and receipt remain unchanged.

The explicit implementation amendment accepts any response type at the API
hop (`Accept: */*`), while the binary hop retains its binary preference and
HDF5 signature check. A fresh bootstrap attempt must name the prior receipt,
verify its source/config/budget chain, and carry the **57 bytes** into the
same 768 MiB cap. The file selection, role, limits and scientific inputs do
not change. There are no automatic retries.

The corrected bootstrap downloaded all three declared files. It consumed
**42,515,925 bytes cumulatively**, including the earlier 57-byte error.
Binary inspection found a documentary layout difference: the actual
`FileOffsets/SnapByType` array has shape **(4, 6)** (chunk, particle type),
whereas the online table describes (6, number of chunks). The reader explicitly
normalizes either distinguishable layout to (type, chunk), records the observed
orientation, and checks the resulting chunk boundaries against actual headers.
`Group/SnapByType` has the expected (18,976, 6) shape. This is a schema-discovery
amendment before full acquisition; it changes no resource, population or limit.

The [completed acquisition](../data/cosmic-development/2026-11-20/tng50-4-dark-attempt-02/acquisition.json)
retains all **27 files**, with **505,904,305 response bytes** cumulatively,
including the initial 57-byte error. The same cap leaves **299,402,063 bytes**.
The raw HDF5 material totals **505,904,248 bytes** and is ignored by Git;
source snapshots, exact hashes, sanitized receipts and schema observations
are retained. The bootstrap receipt was reconstructed from the unchanged first
three request records and its original stage/budget fields; its bytes reproduce
the validator's recorded SHA-256 exactly. It is retained as
`bootstrap_acquisition.json`. The updated client preserves that snapshot before
continuation automatically in future acquisitions.

**21 November reader amendment:** the
[initial material check](../data/cosmic-development/2026-11-20/tng50-4-dark-attempt-02/material-validation-initial.json)
stopped at an unsupported implementation assumption: `Nids_ThisFile` does not
equal the sum of memberships of groups stored in that catalogue chunk. The
[counter audit](../data/cosmic-development/2026-11-20/tng50-4-dark-attempt-02/group-counter-audit.json)
retains all twelve observations. At output 97, the first chunk stores groups
with 2,742,688 members but its header counter is 2,530,229. Summing each
quantity across the four files gives exactly 10,025,728, also the value of
every `Nids_Total`. The corresponding equal whole-output totals are
10,068,046 and 10,095,112 at outputs 98 and 99. The revised reader retains the
per-file differences and checks these exact global identities. It does not
assign an undocumented meaning to the per-file counter. The failed verdict and
its exact source remain retained; no physical tolerance or resource choice
changes.
