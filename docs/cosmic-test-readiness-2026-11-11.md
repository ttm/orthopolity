# Cosmic-test readiness decision

Decision dated 12 November 2026; execution updated 21 November. The
[author-requested task ledger](cosmic-test-roadmap-2026-11-11.md) is complete
through the readiness decision. **Proceed with bounded material-transport
development; do not yet run a confirmatory cosmic abundance test.** Metadata,
bounded acquisition and the first inventory/endpoint diagnostics now pass.
The next operation is D3's mass-bin/current qualification below.

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
  prediction candidate. TNG access and selected-output inventory closure now pass;
  its cadence and local-transport adequacy remain unqualified. Quijote's own
  access and material checks remain pending. Their calibrations are not
  interchangeable.
- **The inspected CosmoSim route fails this input requirement.** MDR1 FoF trees
  supply selected genealogy without complete particle-transfer weights. Close
  that route unless a specific public membership-history product is identified;
  do not broaden the archive search merely to find a convenient slope.

## Gate matrix: TNG development update 21 November

“Documented” below means the official schema supports a candidate, not that
downloaded files passed a measurement or scientific check. Detailed evidence is
in the [TNG audit](cosmic-source-tng-2026-11-11.md),
[Quijote/CosmoSim audit](cosmic-source-alternatives-2026-11-11.md) and
[executed TNG development report](cosmic-development-results-2026-11-21.md).

| Gate | IllustrisTNG DMO | Quijote standard fiducial | CosmoSim MDR1 FoF trees |
|---|---|---|---|
| G1. Defined material | Exact ID/membership closure passes for TNG50-4-Dark outputs 97/98/99; catalogue masses compatible with final rounding | Member-ID schema documented; header mass budget and closure untested | Host mass present; selected descendant population is not a complete earlier inventory |
| G2. Observable transport | Endpoint material joins work; measured coarsening losses leave locality/residence resolution unqualified | IDs and memberships documented; five late epochs leave cadence unqualified | No complete transferred-mass weights or member-ID history in inspected product |
| G3. Model eligibility | Global jumps and diffuse transfers measured; mass-bin sources, stationarity and local drift residuals remain unmeasured | Sources, stationarity, jumps and drift unmeasured; sparse cadence is an additional concern | Not assessable through genealogy alone |
| G4. Separate target | Whole TNG50-4-Dark run development-only; no validation target assigned or sealed | Independent standard-seed split can be designed; no actual seeds assigned | No qualified material-input/target pairing |
| G5. Complete prediction | Absolute count/resource formulas specified; inputs and compatible rival map unfrozen | Same, with within-suite calibration required | Not executable through this product |
| G6. Reproducibility | Authorized acquisition completed; exact manifest, raw hashes, source snapshots, failure/amendment records and diagnostics retained | Public docs; authorized listing/access, exact seed/epoch inventory and sizes pending | Public metadata; bulk access unresolved, but resolving it would not supply absent fields |
| Decision | D2 complete; continue D3 mass-bin/current qualification | Retain as candidate after its own measurement gates | Stop genealogy-only route |

The original source search was bounded to these three archive families. The
author's later [CAMELS/Abacus extension](cosmic-source-pivot-2026-11-19.md) is
retained separately; no additional family is opened. Earlier closed
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
| D1 | Obtain `TNG50-4-Dark` run/snapshot metadata through existing authorized access; cap total response content at 1 MiB | Exact headers/times/fields/chunks/sizes retained with URLs and hashes; no particle or host-mass arrays | Authenticated JSON phase completed 19 November; binary bootstrap verified 20 November |
| D2 | Freeze a development-only acquisition manifest for three adjacent epochs and ID/membership/header fields | Exact paths, field selection, bytes, memory/disk bounds and exposure roles known | Complete: 27 files acquired within fixed budget; bootstrap passed |
| D3 | Implement the reader and measure material closure, jumps, sources and cadence sensitivity | Integrity checks pass and local-closure uncertainty can be bounded, or a specific failure is retained | Partial: whole-inventory checks and endpoint/cadence diagnostics pass; mass-bin currents, sources and local-closure residuals still needed |
| D4 | Qualify Quijote standard fiducial membership inventory and independent seeds if D3 supports further development | Its own cadence/closure gates pass; no unvalidated TNG-to-Quijote transfer | Conditional follow-up |
| D5 | Freeze and execute a separate absolute-abundance prediction against declared rivals | All G1–G6 pass before target exposure; retain every outcome | Not ready; scientific gates pending |

D1 requires a working access route. The initial audit obtained no successful
API metadata or binary sample; its DNS and browser failures established no HTTP
authentication status. The subsequent [12 November access gate](cosmic-metadata-access-2026-11-12.md)
reached the archive with verified TLS and retained an actual **HTTP 403** response
requiring session/API-key authentication. The author reports no existing TNG
access. The operation consumed **55 bytes** of the shared 1 MiB response budget.
No account was created, credential solicited in chat, provider contacted or large
dataset acquired. Access would enable D1; it would not by itself satisfy the
scientific gates.

**19–20 November update:** the supplied credential successfully retrieved all
eleven planned JSON metadata responses. The [new record](cosmic-metadata-qualification-2026-11-20.md)
and [D2 plan](cosmic-development-acquisition-2026-11-20.md) supersede the access
wait. Cumulative metadata content is 19,587 bytes. The bounded binary bootstrap
passed, including the explicitly recorded offset-array transpose relative to
the online specification. No transport gate is inferred from authentication
or schema success. The entire selected run is development-only.

**21 November update:** the [development findings](cosmic-development-results-2026-11-21.md)
establish exact inventory closure and identical particle populations across the
three acquired outputs. Coarsening loses 29.10% of resolved absolute log-mass
variation among particles hosted throughout, and 32.30% of gross reservoir
exchange. D3's next step is fixed development mass-bin accounting and a direct
current-versus-drift comparison, not D4 or a confirmatory abundance forecast.

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
