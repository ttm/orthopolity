# Cosmic-test readiness decision

12 November 2026; work began 11 November. The
[author-requested task ledger](cosmic-test-roadmap-2026-11-11.md) is complete
through the readiness decision. **Proceed with bounded material-transport
development; do not yet run a confirmatory cosmic abundance test.** The exact
next operation is a metadata manifest for a small TNG development run.

The positive result is a usable test design: measure material flow independently,
then predict the absolute host counts and mass per logarithmic interval in a
separate target. The missing evidence is whether gravitational assembly actually
satisfies the local, nearly stationary, nearly constant-residence-time regime
needed for that prediction. A near-minus-two abundance slope cannot establish
those conditions.

This candidate concerns **log-orthopolic collisionless total-matter allocation
in dark-matter-only simulations**, among disjoint FoF hosts. The simulated
particles represent the total-matter budget, including the cosmological baryon
share evolved collisionlessly. Physical cold-dark-matter mass alone, stellar
mass, stars per galaxy and observed galaxy counts require separate mappings.

## Findings that determine the decision

- **Conditional mathematics passes.** Constant positive local drift and constant
  through-current give $r=M^2n=J/v=C$. The
  [mechanism audit](cosmic-mechanism-audit-2026-11-11.md) quantifies departures
  due to sources, time dependence and variable drift. It also gives a
  Press--Schechter counterexample to inferring neutrality from self-similarity
  alone. The proposed natural-law status in the article remains a proposal;
  these deductions do not turn its cosmic extension into an observed law.
- **Genealogy is insufficient.** A main-progenitor mass history need not measure
  the motion of all its matter. Minor mergers can produce long jumps for the
  secondary material. Persistent particle IDs and disjoint memberships are the
  appropriate starting point.
- **There are two promising, complementary archives.** TNG's documented output
  sequence makes it the first technical transport candidate. Quijote's member-ID
  catalogues and many standard realizations make it a possible independent-seed
  prediction candidate. Actual cadence adequacy, file access and material closure
  remain unverified for both. Their calibrations are not interchangeable.
- **The inspected CosmoSim route fails this input requirement.** MDR1 FoF trees
  supply selected genealogy without complete particle-transfer weights. Close
  that route unless a specific public membership-history product is identified;
  do not broaden the archive search merely to find a convenient slope.

## Gate matrix

“Documented” below means the official schema supports a candidate, not that
downloaded files passed a measurement or scientific check. Detailed evidence is
in the [TNG audit](cosmic-source-tng-2026-11-11.md) and
[Quijote/CosmoSim audit](cosmic-source-alternatives-2026-11-11.md).

| Gate | IllustrisTNG DMO | Quijote standard fiducial | CosmoSim MDR1 FoF trees |
|---|---|---|---|
| G1. Defined material | Particle inventory and disjoint FoF fields documented; actual closure untested | Member-ID schema documented; header mass budget and closure untested | Host mass present; selected descendant population is not a complete earlier inventory |
| G2. Observable transport | IDs, memberships and 100 outputs documented; locality/residence resolution untested | IDs and memberships documented; five late epochs leave cadence unqualified | No complete transferred-mass weights or member-ID history in inspected product |
| G3. Model eligibility | Sources, stationarity, jumps and drift unmeasured | Same; sparse cadence is an additional concern | Not assessable through genealogy alone |
| G4. Separate target | Temporal split can be designed; no actual target sealed, independence limited by common box | Independent standard-seed split can be designed; no actual seeds assigned | No qualified material-input/target pairing |
| G5. Complete prediction | Absolute count/resource formulas specified; inputs and compatible rival map unfrozen | Same, with within-suite calibration required | Not executable through this product |
| G6. Reproducibility | Public docs; authorized API/file access and exact field/epoch/byte manifest pending | Public docs; authorized listing/access, exact seed/epoch inventory and sizes pending | Public metadata; bulk access unresolved, but resolving it would not supply absent fields |
| Decision | Develop measurement first | Retain as candidate after its own measurement gates | Stop genealogy-only route |

The source search is bounded to these three archive families. Earlier closed
repository searches stay closed. A simulation success would first establish a
result within that simulated universe and its host definition; observational
confirmation remains a separate task.

## What is ready to execute, and what is not

The [measurement and prediction design](cosmic-test-design-2026-11-11.md) now
specifies material stocks, endpoint transfers, diffuse sources, input/target
roles, absolute forecasts and comparison models. Exact particle balance is a
reader check; the local closure and its transfer to a new target are additional
claims. No target endpoint may supply its own forecast through $J=vr$.

The new [manufactured checker](../experiments/check_cosmic_transport_design.py)
passes in Python 3.11 and is included in `make all` as
`make cosmic-transport-design`. Its constant-drift cascade converges to the
neutral profile; variable drift, interior supply and transients produce the
expected departures. It also checks merger jumps, endpoint accounting, missed
return crossings and integrated count/mass formulas. These are model and
measurement checks with invented inputs, not empirical evidence.

Before any validation freeze, resolve the actual source inventory, mass/time
resolution, eligible interval, closure-error bounds, target identifiers,
independent $J_2,v_2$ mapping, conventional-model observation map, uncertainty,
sample size and scoring thresholds. Do not fill those blanks with values chosen
after seeing target abundance. The design explicitly remains unfrozen.

## Next task queue

| ID | Action | Stop/completion condition | Status |
|---|---|---|---|
| D1 | Obtain `TNG50-4-Dark` run/snapshot metadata through existing authorized access; cap total response content at 1 MiB | Exact headers/times/fields/chunks/sizes retained with URLs and hashes; no particle or host-mass arrays | Next; access route not established |
| D2 | Freeze a development-only acquisition manifest for three adjacent epochs and ID/membership/header fields | Exact paths, field selection, bytes, memory/disk bounds and exposure roles known | Depends on D1 |
| D3 | Implement the reader and measure material closure, jumps, sources and cadence sensitivity | Integrity checks pass and local-closure uncertainty can be bounded, or a specific failure is retained | Depends on D2 |
| D4 | Qualify Quijote standard fiducial membership inventory and independent seeds if D3 supports further development | Its own cadence/closure gates pass; no unvalidated TNG-to-Quijote transfer | Conditional follow-up |
| D5 | Freeze and execute a separate absolute-abundance prediction against declared rivals | All G1–G6 pass before target exposure; retain every outcome | Not ready; scientific gates pending |

D1 requires an existing working access route. The audit obtained no successful
API metadata or binary sample; local DNS failure and a browser retrieval failure
do not establish an archive HTTP authentication response. No account was created,
credential solicited in chat, provider contacted or large dataset acquired.
Access would enable D1; it would not by itself satisfy the scientific gates.

## Verification and repository scope

Independent review checked the mechanism identities, sufficient-bound wording,
Press--Schechter derivatives, mass-ratio direction and the source qualification
claims. The existing Python 3.11 environment executes the manufactured checks;
their largest stationary-cascade absolute error is below $6.2\times10^{-11}$.
All **711 Python tests**, **27 JavaScript tests**, **303 local links / 2 anchors**
and the **46-run / 1,168-reference registry** pass. Terminology and whitespace
checks include untracked deliverables. Commands were
`make test cosmic-transport-design PY=build/main-venv-2026-10-09/bin/python`
and `make registry-verify PY=build/main-venv-2026-10-09/bin/python`; local build
logs retain their output. Full analysis regeneration was not repeated for this
development-design change; the successful 10 November `make all` baseline
remains in [status](status.md).

No cosmic empirical run or registry entry is added. Main/supporting manuscript
sources, their PDFs, frozen protocols, inputs, forecasts and numerical results
are unchanged. This completes readiness work and leaves the next development
operation concrete; it does not report cosmic confirmation or rejection.
