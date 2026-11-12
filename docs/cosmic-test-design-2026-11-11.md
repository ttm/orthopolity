# Cosmic transport: measurement and prediction design

Started 11 November; integrated 12 November 2026. This is a **development design,
not a frozen validation protocol**. Archive files, calibration estimates, target
identifiers and numerical acceptance thresholds remain to be qualified. The
[readiness decision](cosmic-test-readiness-2026-11-11.md) governs execution.

The question is concrete: **can independently measured material flow predict
how many hosts occupy each mass interval?** The candidate is log-orthopolic
allocation of collisionless total-matter mass in a dark-matter-only simulation.
Its simplest prediction is equal mass per equal logarithmic host-mass interval,
with the amount predicted from current and residence time. A distribution that
looks flat after choosing a mass interval is not that test.

## 1. Material and measurement contract

Use a complete periodic box, comoving volume $V_c$, physical particle masses
$m_p$, cosmic time $t$ and disjoint friends-of-friends (FoF) hosts. Let the mass
coordinate of host $h$ be exactly $M_h=\sum_{p\in h}m_p$. Use solar masses,
Mpc cubed and one declared time unit after converting the archive's $h$ factors.
Do not replace this inventory with a spherical-overdensity mass or a
resolution-corrected mass. Those require a separate observation map.

Each particle has one host assignment or an explicit diffuse/unresolved state.
For a positive-host assignment define $x_p(t)=\ln[M_{h_p(t)}/M_0]$, with fixed
reference mass $M_0$. The diffuse state has no logarithmic host mass. Hosts
outside the test interval remain in the inventory, so boundary flows can be
measured. Nested subhalos are not additional resource containers.

For fixed edges $x_i$ and widths $w_i=x_{i+1}-x_i$, the class stock is

$$R_i(t)=\frac{1}{V_c}\sum_p m_p\,
\mathbf1\{x_i\le x_p(t)<x_{i+1}\}.$$

The indicator is zero for diffuse/unresolved particles, whose $x_p$ is undefined.

Its density per logarithmic width is $R_i/w_i$. In the continuum,
$n=dN/(dV_c\,dM)$ and $r=M^2n$; $R_i=\int_{x_i}^{x_{i+1}}r(x)\,dx$.
These are mass stocks, not host counts. The exact measured count counts hosts
once each; dividing a stock by a bin's representative mass is only an
approximation and is not the observation model here.

Join persistent particle IDs across epochs. With states including all host
mass bins and the diffuse state, retain the full transferred-mass matrix

$$T_{ij}=\frac{1}{V_c}\sum_p m_p\,
\mathbf1\{p\text{ starts in }i\text{ and ends in }j\}.$$

Check unique IDs, disjoint memberships, constant total particle inventory,
row/column sums, header mass budgets, and catalogue/integer-mass agreement.
Track catalogue precision separately from true missing mass. A checksum records
file identity; conservation checks record whether the reader interpreted it
correctly.

For particles in positive-mass hosts at both endpoints, define the signed
endpoint current through $b$ by

$$F_b=\frac{1}{V_c\Delta t}\sum_{p\in H\to H}m_p
\big[\mathbf1\{x_p(t+\Delta t)\ge b\}
-\mathbf1\{x_p(t)\ge b\}\big].$$

Let $S_i$ be diffuse-to-host mass entering bin $i$ minus host-to-diffuse mass
leaving it, divided by $V_c\Delta t$. Then the endpoint identity is

$$\frac{R_i(t+\Delta t)-R_i(t)}{\Delta t}
=F_{x_i}-F_{x_{i+1}}+S_i.$$

This is an exact accounting check, including host-to-host jumps across many
bins. It is **not evidence of local transport or a successful forecast**.
Unobserved excursions can cancel at the endpoints. Without adequate cadence,
endpoint data do not identify gross crossing rates or residence times; an
excursion through diffuse matter can also be invisible.

## 2. Development measurements and eligibility

The [mechanism audit](cosmic-mechanism-audit-2026-11-11.md) derives the conditions
for $\partial_t r+\partial_xJ=s$, $J=vr$, and $r=J/v$. Development must assess:

1. **Resolution and assignment:** membership closure, particle-number limits,
   FoF bridging/reassignment, bin-width sensitivity and numerical resolution.
2. **Time resolution and locality:** full mass-weighted jump distributions,
   upward/downward transfers and residence estimates. Compare adjacent outputs
   with their coarsened pairs; three development epochs are a first diagnostic,
   not proof of convergence. A small main-progenitor step does not bound the
   secondary material's jump.
3. **Sources and stationarity:** diffuse exchange and changes in $R_i$ relative
   to current; boundary supply must sustain any proposed stationary interval.
4. **Drift and residual flux:** estimate the small-step material drift using
   particle-mass weights, not an unweighted halo-growth average. Assess the
   discrepancy from $J=vr$ on development data; retain any residual $K$ and
   bound its contribution to the predicted profile. Coarse endpoint drift is
   not automatically the instantaneous drift.

An approximate-neutrality tolerance can be tied to the sufficient bound
$\sup r/\inf r\le\exp[(\epsilon_s+\epsilon_t+\epsilon_v)L]$ when the local
closure applies. Its terms can cancel, so exceeding this sufficient bound is
not itself proof that neutrality fails. A general residual flux needs the
additional term derived in the mechanism audit. Neither the interval nor the
tolerance may be selected by inspecting a validation plateau.

Freeze numerical resolution, cadence, residual and precision thresholds after
development and before validation. If development cannot bound the local
approximation, stop this local-flow route. An endpoint transition model may
still be useful, but it requires a separately stated mechanism and prediction.

## 3. Input/target manifest and exposure controls

| Role | Allowed information | Use and restriction |
|---|---|---|
| Source metadata | Run/version, cosmology, box, headers, epoch list, field schema, file sizes and seed provenance | Qualify access and computation; record any public aggregate counts already exposed |
| Reader development | Selected complete particle-ID/membership histories, masses and headers from development outputs | Establish accounting, cadence and resource conventions; all derived abundance profiles are development only |
| Calibration | Whole development realizations or a declared pre-target time window | Estimate $J$, $v$, source/residual terms, transfer uncertainty, eligible interval and rival parameters |
| Validation inputs | Fixed cosmology/volume/epoch and the predeclared transferred calibration rule | Predict $J_2$ and $v_2$ with uncertainty; the default design admits no target-endpoint trajectories |
| Validation target | Complete host counts and integer mass stocks at fixed edges, from reserved realizations or a reserved future epoch | Open only after input mapping, predictions, uncertainty, scoring and protocol hashes are retained |
| Forbidden calibration leakage | Target masses, target memberships, transitions ending in the target, target-derived current, fitted target amplitude | These reveal or encode the response; do not call their reconstruction an independent forecast |

No actual validation target has yet been assigned or sealed. The already
published appendix examples and public aggregate counts remain exposed.

```mermaid
flowchart LR
  A[Archive metadata] --> B[Development histories]
  B --> C[Qualify material and transport]
  C --> D[Freeze inputs and forecast]
  D --> E[Open reserved abundance target]
  E --> F[Score absolute predictions and rivals]
```

**TNG:** use `TNG50-4-Dark` first for a smaller technical pilot; `TNG100-3-Dark`
is a documented larger candidate. Do not reserve a future target until exact
epochs and exposure history are recorded. A future epoch in the same box tests
a conditional temporal prediction and shares its initial conditions. Resolution
variants and hydro/DMO counterparts are not independent realizations.

**Quijote:** standard massless-neutrino fiducial seeds offer a possible independent
realization split. Keep every epoch and matched-seed variant in one partition;
exclude paired-fixed variants from the proposed ordinary-seed design. Assign
whole seeds from metadata before opening numerical catalogues. Its sparse stored
epochs still need to qualify the drift measurement. Do not transfer a TNG
calibration to Quijote merely because both archives use FoF hosts: cosmology,
resolution, output cadence and implementation differ. Calibrate within the
selected suite or validate an explicit cross-suite transfer law first.

## 4. Predictions, rivals and scoring

The stationary source-free model predicts, from independent inputs,

$$\widehat n_2(M)=\frac{\widehat J_2}{\widehat v_2(\ln(M/M_0))M^2},\qquad
\widehat N_{i,2}=V_{c,2}\int_{M_i}^{M_{i+1}}\widehat n_2(M)\,dM.$$

For constant drift, $\widehat C_2=\widehat J_2/\widehat v_2$ gives

$$\widehat N_{i,2}=V_{c,2}\widehat C_2
\left(\frac1{M_i}-\frac1{M_{i+1}}\right),\qquad
\widehat R_{i,2}=\widehat C_2\ln\frac{M_{i+1}}{M_i}.$$

Thus both absolute count and resource are predicted. Normalizing each model
to the observed target mass would erase the amplitude test. For two qualified
constant-drift states, the additional prediction is
$C_2/C_1=(J_2/v_2)/(J_1/v_1)$. Reusing $C_1$ is a declared persistence baseline,
not an independently measured change in transport.

| Model | Input and comparison role |
|---|---|
| Neutral local flow | Independent constant current and drift; predicts flat log-resource density and absolute abundance |
| Variable-drift local flow | Independently calibrated $v(x)$; tests whether a measurable departure from constant residence time improves prediction |
| Direct transfer/persistence | Development mean profile for an independent realization, or the last pre-target profile for a temporal forecast; same volume/unit conventions |
| Conventional halo mass function | Cosmology and power spectrum plus fixed external/development parameters; requires a qualified map to the target's exact mass convention |

Press--Schechter is an analytic baseline, not the only rival. A FoF fit such as
Warren et al. uses linking length 0.2 but includes a particle-number mass
correction; applying it directly to our uncorrected integer inventory would
still mismatch observables. Fix a forward observation map and its uncertainty
on development data, or qualify a compatible fit. Tinker spherical-overdensity
fits require a different map. Neither mapping may be fitted to the target.
[Warren et al., mass correction and fit](https://arxiv.org/pdf/astro-ph/0506395),
[Tinker et al., spherical-overdensity model](https://arxiv.org/abs/0803.2706).

Retain absolute residuals for every fixed bin and total interval, predicted
uncertainty, coverage and a frozen predictive score against each rival.
Counts and mass stocks from the same hosts are dependent; they are not two
independent replications. Estimate covariance and cosmic variance from whole
development realizations or justified spatial blocks, with additional mass,
cadence, finite-volume and transport-transfer uncertainty. Independent-halo
Poisson errors alone are not justified by the design. Choose the primary score,
equivalence margin, target count and power criterion from development precision
before unsealing. These numerical choices remain unresolved here.

## 5. Executed mathematical checks and next acquisition

Run `make cosmic-transport-design PY=build/main-venv-2026-10-09/bin/python`.
The [checker](../experiments/check_cosmic_transport_design.py) uses manufactured
data only. It verifies finite-class budget balance, constant-drift neutrality,
nonneutral stationary solutions with variable drift or an interior source,
a nonstationary constant-coefficient case, long secondary-material merger jumps,
endpoint accounting, hidden return crossings and finite-interval count/mass
quadratures. Maximum cascade error is below $6.2\times10^{-11}$ in the existing
Python 3.11 environment. The sufficient bound and Press--Schechter derivatives
received independent mathematical review; they are not numerical tests in that
script. None of these checks establishes cosmic eligibility.

The next operation is **metadata only**, first for `TNG50-4-Dark`: run and
snapshot descriptions, output times, fields/offsets, chunk inventory and reported
sizes, capped at 1 MiB total response content. Use an existing authorized access
route; record exact URLs, retrieval time, byte counts and hashes, omitting
credentials. No account creation, provider contact, particle or host-mass arrays
are part of this operation. Stop on access failure or incomplete required
metadata; an environmental DNS failure is not an archive authentication verdict.

Then prepare an exact development acquisition manifest with three adjacent
epochs, ID/membership/header fields, expected bytes, memory/disk budget and
checksums. Do not acquire it until those bounds are known. A separate Quijote
metadata manifest can establish candidate independent seed coverage; it does
not bypass the TNG measurement lessons or Quijote's own cadence gate. The
[source reports](cosmic-source-tng-2026-11-11.md) and
[alternative-source report](cosmic-source-alternatives-2026-11-11.md) retain
field names, access evidence and citation requirements.
