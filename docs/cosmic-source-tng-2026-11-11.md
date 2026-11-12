# IllustrisTNG source qualification — 11 November 2026

**Decision: suitable in principle for a material-accounting development study;
not ready for a confirmatory cosmic test.** Public documentation describes the
particle identities and disjoint host assignments needed to reconstruct mass
transfers. It does not supply an independently calibrated current and drift, a
sealed abundance target, or evidence that the local transport assumptions hold.
An API key would resolve an access requirement, not those scientific requirements.

The proposed reading is **log-orthopolic collisionless total-matter mass in a
dark-matter-only (DMO) simulation**, allocated across disjoint friends-of-friends
(FoF) hosts. It is not a measurement of physical cold-dark-matter mass alone.
This report qualifies a source; it reports no fitted exponent, measured current,
or empirical confirmation. See the [task ledger](cosmic-test-roadmap-2026-11-11.md)
for the larger test and its gates.

## Access and exposure record

Official documentation was inspected on 11 November 2026. The data service
requires registration/login; API examples authenticate with an `api-key` header.
The service supports metadata, field selection and particle cutouts. No account
was registered, person contacted, key requested, or credential used during this
audit. [Official API documentation](https://www.tng-project.org/data/docs/api/)

Attempts to inspect the no-key simulation endpoints for `TNG100-3-Dark` and
`TNG50-4-Dark` through the browsing tool returned an inaccessible-resource result.
A local no-key request failed at DNS resolution. These outcomes do **not** establish
an HTTP authentication status or demonstrate successful anonymous data access.
No API metadata response or HDF5 sample was obtained. Field qualification below
is therefore documentary, not a verified binary-schema audit.

**12 November follow-up:** the [bounded access probe](cosmic-metadata-access-2026-11-12.md)
subsequently reached this API with the system CA bundle and retained HTTP 403,
“Failed session auth (and no API-Key sent).” Its 55-byte response confirms the
authentication requirement. No successful run/snapshot metadata or binary sample
was obtained, and the author reports no existing access. The source qualification
below remains documentary.

The public overview includes global object counts alongside run metadata. Those
tables were exposed during source selection, but no mass-resolved abundance
array, particle array, or merger tree was downloaded or inspected. Global counts
from that page must not become an allegedly unexposed target. The overview also
offers direct downloads, an API and server-side analysis through JupyterLab.
[Public data overview](https://www.tng-project.org/data/)

## Candidate resource and products

DMO initial conditions contain total-matter particles. Hydrodynamic runs split
that initial matter into dark matter and gas according to the cosmic baryon
fraction. Thus the DMO resource includes the matter represented by both
components, evolved collisionlessly. TNG adopts
`Ωm=0.3089`, `ΩΛ=0.6911`, `Ωb=0.0486`, `h=0.6774`,
`σ8=0.8159`, and `ns=0.9667`.
[Official background and initial conditions](https://www.tng-project.org/data/docs/background/)

The first technical candidate is `TNG100-3-Dark`; `TNG50-4-Dark` is a cheaper
development pilot. Smaller or coarser does not mean scientifically adequate:
mass resolution, usable dynamic range and cosmic variance still need assessment.

| Documented product | TNG100-3-Dark | TNG50-4-Dark |
|---|---:|---:|
| Internal run name | `L75n455TNG_DM` | `L35n270TNG_DM` |
| Particle number | 94,196,375 | 19,683,000 |
| Comoving side | 75 Mpc/h | 35 Mpc/h |
| Snapshot chunks | 4 | 4 |
| Approximate full snapshot | 5.7 GB | 1.2 GB |
| Approximate average group catalogue | 40 MB | 10 MB |
| Approximate all-snapshot storage | 0.4 TB | 0.1 TB |

Runs have 100 snapshots, including full and reduced-field outputs. Snapshot 99
is at redshift zero; examples of full outputs include 50 (`z≈1`), 67 (`z≈0.5`)
and 91 (`z≈0.1`). Exact time intervals must come from metadata. Required fields
are `PartType1/ParticleIDs`; header `MassTable`, `BoxSize`, `Time`, `Redshift`,
and cosmology; catalogue `GroupLenType`, `GroupMass`; and offsets
`Group/SnapByType` with file offsets. IDs persist; particles are ordered by
group/subgroup rather than position. Group lengths and offsets recover
membership across arbitrary file boundaries. Mass units are `10^10 M☉/h`;
box units are comoving `kpc/h`; `Time` is scale factor. `GroupMass` sums member
masses. [Product sizes, units and field definitions](https://www.tng-project.org/data/docs/specifications/)

Use the exact header side to calculate
`Vc=(BoxSize/(1000 h))³ Mpc³`, and
`mp=MassTable[1] × 10^10/h M☉`.
The inventory mass of host `i` is `Mi=GroupLenType[i,1] mp`.
Check agreement with catalogue `GroupMass` allowing its documented floating-point
representation. Use the integer inventory for conservation bookkeeping. A
spherical-overdensity mass such as `M200c` is a different boundary and cannot
silently replace this particle partition.

Subhalos lie within FoF groups: `SubhaloGrNr` identifies the parent. A FoF group
can have no retained subhalo, so requiring a central subhalo would change the
host population. The finder minima (32 FoF particles and 20 bound subhalo
particles) are catalogue rules, not demonstrated completeness thresholds for
this test. Counting FoF hosts and their subhalos together double-counts resource.
[Official group/subgroup FAQ](https://www.tng-project.org/data/docs/faq/)

The public helper supports selected-field particle reads and whole-halo reads,
so a membership analysis need not acquire coordinates and velocities. Its
SubLink helpers load trees or branches and count mergers; this is genealogical
information, not a material-transfer estimator.
[Official analysis scripts](https://www.tng-project.org/data/docs/scripts/)

For scale only, the uncompressed `uint64` ID payload is approximately 0.754 GB
per TNG100-3-Dark snapshot or 0.157 GB per TNG50-4-Dark snapshot, calculated as
eight bytes times the documented particle number. These are lower bounds for
selected-field storage, not measured download sizes or memory estimates. Sorting,
membership maps, catalogues and additional epochs add overhead.

## What independently identifiable material accounting would require

Declare every FoF host to be a disjoint container and include a separate
outside-FoF reservoir. Let `hp(t)` be particle `p`'s container at time `t`.
Persistent particle IDs and independently reconstructed membership at consecutive
epochs then identify a complete transition matrix,

```text
Tij = mp/Vc × number of particles with hp(t)=i and hp(t+Δt)=j.
```

This matrix includes mergers, fragmentation, stripping, exchange and transfers
to or from the unresolved/diffuse reservoir. Its row and column sums can be
checked against the inventory at each epoch. Particle identity, not a selected
descendant link, supplies the conservation evidence.

Merger trees are insufficient for that purpose. SubLink selects a descendant
from shared particles using a binding-energy-sensitive score and can skip an
output. LHaloTree also selects descendants and can bridge outputs. These links
do not encode every donor/recipient particle count or the diffuse reservoir.
Their subhalo masses and identities are not an FoF transfer matrix. The release
does provide both snapshots and trees, allowing this distinction to be tested
rather than assumed.
[Public-release paper](https://arxiv.org/abs/1812.05609),
[tree specifications](https://www.tng-project.org/data/docs/specifications/#sec4)

For material remaining in resolved hosts, define
`xp(t)=ln(Mhp(t)/M0)`. A signed crossing current through a fixed boundary `b`
can be estimated from particle paths:

```text
Jb = mp/(Vc Δt) × Σp [1{xp(t)<b≤xp(t+Δt)}
                     − 1{xp(t+Δt)<b≤xp(t)}].
```

Transfers involving the outside reservoir need separate accounting; assigning
that reservoir a fictitious positive host mass would hide sources and sinks.
This finite-interval current is measurable in principle, but it does not by
itself establish a local drift equation. Large merger jumps, reversals between
outputs and host-finder relabelling can invalidate a local `J=v r` approximation.
Spatial particle velocities are not the drift in log host mass. Time resolution,
jump sizes and source terms need explicit development checks.

The log-orthopolic target is `r(M,t)=M² n(M,t)`, with
`n=dN/(dVc dM)`. Both the current above and any mass-weighted drift calculated
from the same transitions depend on endpoint host masses. Consequently,
**using transitions into the target snapshot to predict that snapshot's
abundance is not an independent forecast**. Re-expressing target occupancy as
current divided by drift does not solve this problem.

A viable design would learn a transport rule and its uncertainty from a declared
development history, freeze the mass interval, time window, eligibility criteria
and prediction, and then evaluate a withheld whole-volume abundance target.
Neither target-bin occupancy nor the target endpoint membership may enter its
calibration. A later epoch in the same volume is a conditional temporal forecast;
it shares initial conditions and is not an independent realization. Separate
volumes require verified initial-condition provenance. Resolution variants and
hydrodynamic/DMO counterparts must not be treated as independent samples. Random
halo rows do not create independence in a shared assembly history.

The source can therefore identify **material transfers independently of a
separately sealed abundance target**, if the calibration/target separation is
made real. It cannot deliver an independent `J` for that target merely by
renaming information computed from its own particles and host masses. Predictive
transport across an epoch or volume remains a model assumption to test.

## Reuse and next gate

The project requests citation of its public-release paper and the introductory
papers appropriate to the selected simulation; supplementary products can add
their own citations. TNG100 and TNG50 have different introductory-paper lists.
The background page also warns that numerical convergence depends on the
quantity and regime. No general redistribution licence for downloaded data was
verified in the inspected pages. Preserve source URLs and citation requirements;
check any intended redistribution separately from analysis access.
[Official citation and convergence guidance](https://www.tng-project.org/data/docs/background/)

| Gate | Present status |
|---|---|
| Conserved resource and disjoint containers | Documented DMO particle inventory supports a candidate; actual closure untested |
| Access and exact schema | Login/key requirement documented; no successful API or binary inspection |
| Complete material transfers | Reconstructible in principle from particle IDs and memberships; not supplied by trees alone |
| Local transport, weak sources, stationarity | Not measured; no eligibility decision |
| Independent calibration and withheld target | Not selected or frozen |
| Resolution and time convergence | Not tested; catalogue minima are insufficient |
| Forecast and comparator | Not frozen; no counts or normalization forecast issued |

**Bounded next operation:** with an already authorized working credential,
inspect only run/snapshot metadata and available-field descriptions for one
development candidate, with an aggregate response cap of 1 MiB. Record exact
box, cosmology, output times, availability of particle IDs and membership
offsets, and documented file sizes. Stop if authentication fails or required
metadata are absent; do not register or contact the collaboration automatically.
No target mass arrays, target trees or target particle memberships belong in
that operation. Before any subsequent development acquisition, freeze a
development-only field/epoch/byte manifest and specify how the whole-volume
target remains unexposed.

This leaves a **go** for bounded source and transport development, and a
**no-go** for confirmation now. Even a later successful simulation prediction
would establish a scoped result within that simulation and its mass convention,
not observational confirmation of a universal cosmological law.
