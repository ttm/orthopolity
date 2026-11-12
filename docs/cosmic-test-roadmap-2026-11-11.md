# Cosmic-test roadmap and task ledger

Started 11 November 2026 at the lead author's request, from clean `main` at
`6a3ffa2`. This follows the completed [manuscript revision](manuscript-roadmap-2026-11-10.md)
and develops the next test proposed in [the cosmic appendix](cosmological-extension.md).

## Objective

Decide whether the proposed mechanism can predict a separate cosmic abundance
profile from independently specified inputs. The immediate deliverable is a
readiness decision with a physical model, bounded source audit, input/target
manifest and prospective comparison design. Execute a numerical cosmic test
only after the required inputs and observation model qualify.

The primary candidate is **log-orthopolic allocation of collisionless total-matter
mass among disjoint hosts in a dark-matter-only simulation**: equal mass per
logarithmic host-mass interval. These simulation particles represent the cosmic
total-matter inventory; physical cold-dark-matter-only mass is a separate reading.
Stellar number, stellar mass and subhalo populations remain separate hypotheses.
The already inspected COSMOS2015/GAMA/Aquarius/stellar-IMF slopes are exploratory
context, not newly withheld targets.

## Task ledger

| ID | Task and output | Completion condition | State |
|---|---|---|---|
| C1 | [Mechanism audit](cosmic-mechanism-audit-2026-11-11.md) | Conditional prediction, departures and failure cases compared with established assembly theory | Complete |
| C2 | [IllustrisTNG audit](cosmic-source-tng-2026-11-11.md) | Products, access, resource/membership fields, histories, splits and missing inputs identified | Complete; development candidate |
| C3 | [Quijote and CosmoSim audit](cosmic-source-alternatives-2026-11-11.md) | Same gates applied to both archive families | Complete; Quijote retained, MDR1 tree-only route closed |
| C4 | [Input/target design](cosmic-test-design-2026-11-11.md) | Absolute prediction, exposure controls and rivals specified | Complete as development design; validation parameters unfrozen |
| C5 | [Readiness verdict](cosmic-test-readiness-2026-11-11.md) | Every gate has an evidence status and a concrete next operation | Complete; development go, confirmation no-go |
| C6 | Reconcile status and verify deliverables | Terminology, equations, sources, local links and scope checked; next tasks explicit | Complete; 711 Python / 27 JS tests, manufactured checks and registry verification pass |

The source search is bounded to these three archive families. Inspect primary
documentation and metadata first. Do not expand it because an initial route
fails, fit a mass-function slope to choose its interval, or download large
particle catalogues before their input/target role is settled. Existing
closed source searches elsewhere in the repository stay closed.

## Qualification gates

| Gate | Required evidence |
|---|---|
| G1. Defined material | Mass/units, disjoint host assignment, diffuse component and completeness are explicit; host and subhalo mass are not double counted |
| G2. Observable transport | Histories identify material transfer, residence/drift and source/loss terms at adequate temporal resolution; a genealogy alone need not do so |
| G3. Model eligibility | Stationarity, local transport and any nearly constant drift/current regime are justified independently of the target profile |
| G4. Separate inputs and target | Current and drift cannot be reconstructed as the target's abundance times a fitted velocity; calibration/target access and dependencies are recorded |
| G5. Meaningful prediction | A normalization, integrated count or profile change is predicted with a complete scale and compared against declared established rivals |
| G6. Feasible reproducibility | Source versions, access, volumes, snapshot times, uncertainty, computation and reuse/citation terms support an executable protocol |

Partial documentation passes are not empirical qualification. A numerical
forecast freeze comes after a validated measurement design and before target
evaluation; no date or local Git commit can erase prior target exposure.

## Scientific decisions and stop rules

- Use existing public material only. A simulation result would first test the
  mechanism within that simulated universe; astronomical confirmation needs a
  separately qualified observational design.
- Conservation, dimensional scaling and a slope near minus two do not by
  themselves establish neutral log-orthopolic allocation.
- The local throughflow model must track the full declared host resource.
  Changes of host boundary, merger jumps, diffusion, diffuse accretion and
  changing cosmic epoch can invalidate its simple closure.
- A failure of the simple closure is a finding to retain. A more general
  model must supply independent inputs and a new prediction before it is used
  to explain that failure.
- Do not choose an equivalence tolerance or mass interval from validation
  outcomes. If calibration cannot support a defensible uncertainty model,
  record an unqualified test rather than a pass/fail abundance claim.

## Outcome and next action

Readiness work completed 12 November 2026. The conditional mechanism is sound,
but a main-branch history and a near-minus-two slope do not qualify material
transport. The next operation is a metadata-only `TNG50-4-Dark` manifest, capped
at 1 MiB, through existing authorized access. Exact development acquisition,
measurement qualification, independent-seed qualification and validation follow
only as their dependencies pass; the [D1–D5 queue](cosmic-test-readiness-2026-11-11.md#next-task-queue)
records those steps. No target has been assigned or opened. Manuscripts and
frozen study artifacts remain unchanged.

**12 November follow-up:** readiness was committed/pushed as `ad9bd13`. The
[executed D1 access gate](cosmic-metadata-access-2026-11-12.md) reached TNG with
verified TLS and received HTTP 403 requiring authentication. The author reports
no existing TNG access. D1 awaits access; its metadata manifest is incomplete.
The two recorded attempts consumed 55 response bytes in total. Resume within
the remaining 1,048,521-byte budget when authorized access is available; retain
D2–D5 dependencies and the bounded source-search scope.
