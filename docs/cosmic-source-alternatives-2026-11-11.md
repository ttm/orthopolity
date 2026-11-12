# Cosmic material-flow source audit: Quijote and CosmoSim

Date: 11 November 2026. Scope: official documentation and product metadata for
two archive families. No halo-mass rows, particle arrays, fitted slopes or target
distributions were downloaded or inspected; no account was registered and no
provider was contacted. Public documentation sometimes displays approximate
catalogue mass ranges; these were not used to choose a test interval.

**Decision:** Quijote's published `FoF_id` schema is the stronger candidate for
a material-membership qualification exercise. It offers particle identities and
many standard realizations. Its documented time sampling does not yet establish
the local drift approximation required by the proposed mechanism. CosmoSim's
documented MDR1 FoF trees supply genealogy, but not the material-transfer weights
required for that mechanism. Neither audit produces a confirmatory-ready test.

This is an alternative-source assessment alongside the separate IllustrisTNG
audit. It changes no empirical result or manuscript claim.

## What must be measured

The reference measure is **log-orthopolic mass allocation**. Let
$n(M,t)=dN/(V_c\,dM)$, where $M$ is the physical mass of a disjoint
particle set and $V_c$ is comoving volume. The resource density is
$r(M,t)=M^2n(M,t)=d\rho_c/d\ln M$. A halo's catalogue mass must equal the sum
of the particles assigned to it. The particles outside the selected population
must remain in an explicit reservoir; including both host and nested subhalo
masses would double count the resource.

For the proposed local equation in $x=\ln(M/M_0)$,
$\partial_t r+\partial_x J=s$, $J=vr$, particle identities can support
measurements of transferred mass. They do not, by themselves, prove locality,
stationarity, negligible sources or a constant material drift. The derivative
of a main-branch halo mass is not the drift of all the material. Nor is computing
$J=vr$ from the withheld mass distribution an independent prediction of that
distribution.

Use solar masses, a declared cosmic-time unit and comoving cubic megaparsecs
consistently. For catalogues in $M_\odot/h$, divide numerical masses by
$h$; a box of side $L\,\mathrm{Mpc}/h$ has
$V_c=(L/h)^3\,\mathrm{Mpc}^3$. Physical particle mass is not multiplied by
the scale factor. Proper-volume densities would introduce expansion terms and
would require a separately stated equation.

## Quijote: strongest published membership schema

The selected design candidate is the **standard, massless-neutrino fiducial
ensemble**, not paired-fixed, massive-neutrino or parameter-variation products.
The official table lists 15,000 standard realizations with $512^3$ particles,
2LPT initial conditions, $\Omega_m=0.3175$, $\Omega_b=0.049$,
$h=0.6711$, $n_s=0.9624$, $\sigma_8=0.834$, $M_\nu=0$ and
$w=-1$. Fiducial realizations differ in their initial random seed; parameter
variants share seeds with fiducial runs. Paired-fixed directories use the `NCV`
prefix. [Official structure and types](https://quijote-simulations.readthedocs.io/en/latest/types.html).

Boxes have side $1\,\mathrm{Gpc}/h$. The ordinary stored epochs are
$z=3,2,1,0.5,0$, plus initial conditions at $z=127$.
[Official features](https://quijote-simulations.readthedocs.io/en/latest/features.html).
The resource here would be the mass of the collisionless matter represented by
the simulation. A dark-matter-only implementation with a nonzero cosmological
baryon fraction does not separately track physical baryonic and cold-dark-matter
particles. Before freezing the protocol, verify the header mass budget against
$\Omega_m\rho_{\mathrm{crit},0}V_c$; do not relabel that numerical mass as
an independently measured $(\Omega_m-\Omega_b)$ resource. A rescaled
cold-dark-matter interpretation would require an explicit additional assumption.

### Exact products and fields

| Product | Relevant schema or location | What it supplies |
| --- | --- | --- |
| `Halos/FoF_id` | Official example `/Halos/FoF_id/s8_p/145/`; `readfof.FoF_catalog(..., read_IDs=True)` | `GroupIDs` concatenates member particle IDs; `GroupLen` gives segment lengths; `GroupMass * 1e10` gives mass in $M_\odot/h$. |
| `Halos/FoF` | Same catalogue reader without IDs | Insufficient alone for material transfer; do not combine its masses with `FoF_id` memberships. |
| Snapshots and ICs | Documented fiducial path `/Snapshots/fiducial/0/`; header plus `ID  ` block | Particle identity, count, mass, redshift, cosmology and box metadata. |

The `FoF_id` catalogue was rerun on compressed snapshots and can differ from
`FoF`. Its existence is explicitly documented; the example above is not a
verified inventory of fiducial realization 0. The selected fiducial paths and
all epoch files still need a manifest. Cumulative `GroupLen` offsets identify
membership slices. The `PID` column in the separate Rockstar product is a
parent-halo identifier, not a material particle identifier.
[Official halo catalogue schema](https://quijote-simulations.readthedocs.io/en/latest/halos.html).

Snapshot particle IDs persist across epochs within a realization, including the
initial conditions. Headers expose `massarr`, `nall`, `boxsize`, `omega_m`,
`omega_l`, `hubble` and `redshift`. The documented conversions are
`massarr * 1e10` to $M_\odot/h$ and `boxsize / 1e3` to
$\mathrm{Mpc}/h$. Ordinary snapshot numbers `000` through `004` correspond
to the five late epochs, but actual headers must determine the mapping. Current
documentation describes integer IDs and warns that future releases might omit
them. Position and velocity preconditioning is lossy; particle IDs are not
lossily compressed. [Official snapshot schema](https://quijote-simulations.readthedocs.io/en/latest/snapshots.html).

Joining `GroupIDs` to snapshot IDs should therefore identify the same numerical
particle across time; confirm ID conventions, uniqueness, type and membership
closure on the development partition before trusting the join. An equal integer
ID in two different realizations does not identify the same physical particle.
This distinction matters when assigning independent calibration and test runs.

### Access and feasibility

The documented transfer collection is
`c42757fe-d570-11e9-98e2-0a63aa6b37da`. Official instructions use Globus login;
local transfers need a destination endpoint, ordinarily Globus Connect Personal.
The alternate Binder route requests a registration form, is ephemeral, and is
unsuitable for heavy computations. Public documentation is anonymous, but this
audit did not establish an anonymous file listing or download route. No login,
registration or access workaround was attempted.
[Official access instructions](https://quijote-simulations.readthedocs.io/en/latest/access.html).

Published schema availability and executable access are separate gates. The
former is documented; the latter remains unverified here. No measured file
sizes or complete epoch inventory are available from this audit. For planning
only, $512^3$ four-byte IDs occupy 512 MiB per epoch before compression;
five complete ID populations occupy 2.5 GiB. Member-ID payload can be smaller,
but catalogue metadata, assignment arrays, working memory and transfer overhead
must be budgeted separately. This is arithmetic from the documented schema,
not an observed download size. Full position/velocity arrays may be unnecessary
if the membership catalogue and header suffice.

Follow the [Quijote citation instructions](https://quijote-simulations.readthedocs.io/en/latest/citation.html)
if data are used. The site's [MIT notice](https://quijote-simulations.readthedocs.io/en/latest/license.html)
explicitly covers software and associated documentation; this audit does not
infer an additional data-redistribution license from that wording.

### Scientific qualification still needed

On a development partition only, verify disjoint FoF membership, particle-mass
closure, and the diffuse/unresolved reservoir at each epoch. Consecutive
membership sets can yield an endpoint transfer matrix, including losses and
splits that a single descendant link can miss. This is a useful input product,
but the five stored late epochs do not reveal all intervening crossings,
returns or residence times. They cannot automatically establish an
instantaneous local current or constant drift. Large merger jumps and FoF
bridging changes must be measured, not absorbed into a desired power-law fit.

Independent standard seeds offer a clean possible split: freeze entire
realizations as development/calibration versus withheld target, and keep all
epochs of each realization together. Any matched-seed parameter variants and
members of a paired-fixed pair must stay within one partition. Nearby spatial
subvolumes and later snapshots of the same realization are not independent
realizations. Fit neither the mass interval nor the resource definition to a
withheld mass-function slope.

**Qualification outcome:** retain Quijote for membership and finite-interval
transport development. Do not launch the local $J/v$ amplitude test until
cadence, jump terms, source terms and independently estimated drift pass a
predeclared gate. If only a nonlocal transfer model is supported, write that as
a different mechanism before exposing its target; do not claim it has verified
the local mechanism.

## CosmoSim: MDR1 FoF genealogy is insufficient for material current

MDR1 is the selected member of this archive family because its current metadata
explicitly lists a top-level FoF merger-tree product. MDR1 uses a
$1000\,\mathrm{Mpc}/h$ box and $2048^3$ particles; the overview lists
WMAP5 parameters $\Omega_m=0.27$, $\Omega_\Lambda=0.73$,
$\Omega_b=0.047$, $\sigma_8=0.82$, $n_s=0.95$. Bolshoi has the same
listed cosmological parameters and particle count, with a
$250\,\mathrm{Mpc}/h$ box. Both advertise particle data in the overview.
That advertisement does not establish a currently accessible particle-membership
history. The value of $h$, particle mass and exact outputs would still need
a product header or release-specific metadata.
[Official simulation overview](https://www.cosmosim.org/cms/data/simulations/).

| Product | Verified metadata | Limitation for this test |
| --- | --- | --- |
| [`mdr1.fofmtree`](https://www.cosmosim.org/metadata/mdr1/fofmtree/) | 181,523,200 rows, 21 columns; `fofid`, `foftreeid`, `descendantid`, `mainleafid`, `lastprogid`, `treerootid`, `treesnapnum`, `np`, `mass` and geometric fields. `mass` is total FoF mass in $M_\odot/h$. | No member-particle IDs or inter-node transferred-mass weights are listed. |
| [`mdr1.treesnapnums`](https://www.cosmosim.org/metadata/mdr1/treesnapnums/) | 39 metadata rows; fields `treesnapnum`, `snapnum`, `aexp`, `zred`. | The tree index differs from the catalogue snapshot index; the row count is not evidence of 39 particle-membership outputs. |
| [`mdr1.redshifts`](https://www.cosmosim.org/metadata/mdr1/redshifts/) and [`mdr1.fof`](https://www.cosmosim.org/metadata/mdr1/fof/) | Named in current archive navigation. | No numerical halo rows queried. The FoF schema fetch timed out twice; no exact member-ID product was established. |

The tree release selects top-level groups through descendants exceeding
$2\times10^{12}\,M_\odot/h$ at $z=0$; it excludes substructure. Thus
it is not a complete earlier-epoch halo inventory. Its DOI is
[10.17876/cosmosim/mdr1/011](https://doi.org/10.17876/cosmosim/mdr1/011), and its
metadata states CC0 1.0 with requested simulation/database acknowledgements.
These are properties of the documented tree product, not evidence that a
complete transfer matrix is present.
[Tree release metadata](https://www.cosmosim.org/metadata/mdr1/fofmtree/).

The [tree tutorial](https://www.cosmosim.org/cms/data/data-structure/merger-trees/)
explains descendant links and main branches; its example uses terminal tree
index 39. Resolve this against the 39-row mapping before choosing epochs,
rather than inferring output coverage from an index. Genealogy cannot determine
how much mass moved through each link, escaped to diffuse matter, or was
reassigned elsewhere. Weighting every progenitor by its entire mass imposes a
transfer rule rather than measures it.

### Access, scale and split limits

CosmoSim advertises anonymous guest queries with a 30-second limit and transient,
public guest results; registered users have longer queues and private user
tables. [Official access overview](https://www.cosmosim.org/cms/data/).
The scripted route documents `https://www.cosmosim.org/tap` and an API token
obtained after registration. [Official TAP instructions](https://www.cosmosim.org/cms/tech-docs/access-via-tap/).
Only documentation was read here; no query job or account was created. Public
metadata access should not be confused with a verified anonymous bulk export.

The tree row count makes a whole-table export inappropriate for an initial
qualification. Exact export bytes, raw snapshot sizes, membership-file
locations and available particle epochs remain unverified. Historical
publication of particle data is not a current manifest. MDR1 and Bolshoi also
differ in volume and resolution; treating them as exchangeable calibration and
test realizations would need an explicit transfer prediction. The inspected
metadata does not establish a same-setup ensemble with independent seeds.

**Qualification outcome:** stop the MDR1 genealogy-only route for this
material-current test. Reopen it only if a specific published product supplies
unique particle-to-host memberships across adequate epochs, particle masses,
the complete population including reservoirs, and a defensible independent
test partition. A halo catalogue can support a mass-function description
without satisfying any of these material-flow requirements.

## Bounded next action and stopping rule

The strongest next source action is a **metadata-only Quijote manifest** for
standard fiducial `FoF_id` and matching snapshot headers: exact paths, epoch
coverage, available seed IDs, sizes, checksums/version identifiers and access
requirements. Obtain it only through an already available authorized route;
this audit authorizes no registration or provider contact. Then freeze a
development/target split before any numerical catalogue is opened.

If that manifest cannot be obtained, record access pending without downgrading
the published schema. If memberships are missing, mass closure fails, or
available cadence cannot bound the nonlocal contribution, stop the proposed
local-flow test. Record the product or mechanism limitation and keep the target
withheld. Neither archive's present status supports a new cosmic confirmation,
and neither is a disproof of log-orthopolic allocation.
