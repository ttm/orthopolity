# Equal-resource spectra hold in the mean and fail in the particular

**A preregistered cross-domain test of resource equipartition across scale**

> **Status: working draft.** Every number is taken from `results/*.json` and reproduces via
> `make all`. Section numbering follows a conventional manuscript; format for a specific venue
> before submission. Author list, funding and acknowledgements are placeholders.

---

## Abstract

Power-law size distributions admit an accounting reading: if a conserved resource is spread equally
across logarithmic size classes, objects that cost more of it must be proportionally rarer. This
equivalence is not new — Gaedke (1993) states it plainly, citing Sheldon et al. (1972) — but its
domain of validity has not been mapped, and it has not been tested as a claim about individual
systems rather than about averages.

We separate the equipartition condition from the scale-invariance assumption usually bundled with
it, show that neither conservation, scale covariance, nor maximum entropy selects equipartition, and
state a falsifiable ensemble form. We then test it in five systems under a protocol registered
before analysis.

It fails decisively for earthquakes and solar flares. For earthquakes the failure is unusually
clean: the Gutenberg–Richter law fits the catalogue well under a discrete test (KS = 0.0077,
p = 0.256), so there is no distributional irregularity to absorb the blame. For the ocean size
spectrum the data cannot decide, with 21 of 23 bins carrying departures smaller than the published
reconstruction uncertainty.

Across 1,300 published aquatic size spectra from 16 independent studies, the hypothesis is **not
supported at the level of individual systems** — 7.8% fall within a factor-1.25 tolerance — while
the ensemble median lands at −1.015 against a predicted −1.000. That is not a hypothesis half
working. Fitting the dispersion (τ = 0.235 between sites) *predicts* the individual pass rate to
within 1–2% at two tolerances, and the dispersion is real: 88% of variance is genuine heterogeneity,
of which at most 8% is one ecosystem varying over time.

Separately, we document a defect that limits any meta-analysis of published scaling exponents: one
database method label covers at least two estimands differing by 1 in exponent, verified against the
source papers.

---

## 1. Introduction

Power-law distributions are ubiquitous and over-explained. Newman (2005) catalogues roughly eight
distinct generating mechanisms; Mitzenmacher (2004) more. When many unrelated processes converge on
one functional form, it is reasonable to suspect that a constraint rather than a mechanism is doing
the work.

One such constraint has an appealingly simple statement. Let objects hold some additive resource,
and let that resource be spread equally across logarithmic size classes. Then abundance must fall as
the inverse of per-object cost. In the size-spectrum literature this is familiar: Gaedke (1993)
writes that "an equal distribution of biomass over all size classes corresponds to a zero slope of a
line fitted to a Sheldon-type size spectrum … and to a slope of −1 of the normalized spectrum,"
citing Sheldon et al. (1972, 1977). Damuth's (1981) energetic equivalence rule is the same accounting
applied to metabolic rate. **The equivalence is old. We claim no priority over it.**

What has not been established is where it holds. Three questions are open:

1. **Is it a claim about systems or about averages?** Reported size-spectrum slopes vary widely.
   Whether that variation refutes the claim or is required by it depends on a dispersion parameter
   nobody has estimated.
2. **What does it forbid?** A constraint that accommodates every observation is not a hypothesis.
3. **Does it extend beyond ecology?** The accounting is domain-neutral. Whether the empirical
   pattern is has not been tested.

We address all three. Our contribution is not the identity but its **domain of validity**, its
**quantified dispersion**, and a **falsifiable ensemble formulation** that predicts its own rate of
individual failure.

---

## 2. Theory

### 2.1 The equipartition condition

Let objects be indexed by a positive scale coordinate $k$ with reference $k_0$, and write
$u = \ln(k/k_0)$. Let $q$ be an additive per-object resource and $\bar q(k) = E[q \mid k]$ the
**conditional arithmetic mean** resource at scale $k$. The arithmetic mean is required: only it
preserves the sum on which the accounting rests, so fitting OLS to $\log q$ — which estimates the
geometric mean — silently breaks the identity. The resource spectrum is

$$\mathcal{O}(k) = \frac{dR}{du} = \bar q(k)\,\frac{dN}{du}.$$

**(O)** $\;\mathcal{O}(k) = C$ on a declared finite domain $[k_{\min}, k_{\max}]$.

This concerns the **stock** of resource resident at each scale, not a **flux** through scales — a
distinction §2.4 shows is not pedantic.

### 2.2 (O) does not by itself give a power law

(O) yields $dN/du \propto 1/\bar q(k)$ for *any* $\bar q$. A power law requires a second, independent
assumption:

**(S)** $\;\bar q(k) = q_0 (k/k_0)^{d}$, whence

$$\frac{dN}{d\ln k} \propto k^{-d}, \qquad \frac{dN}{dk} \propto k^{-(d+1)}.$$

The exponent comes entirely from (S). With $\bar q(k) = e^{k}$, (O) holds exactly and produces an
**exponential**. Much of what is credited to equipartition is in fact scale invariance, which is
standard and well understood.

Exponent conversions must never be skipped: under (O)+(S) the log-histogram slope is $-d$, the
density exponent is $d+1$, the complementary cumulative exponent is $d$ far below the upper cutoff
(and is *not* an exact monomial near a finite upper boundary), and the rank–size exponent is $1/d$.
Section 4.6 shows what happens when this bookkeeping is neglected in practice.

### 2.3 The content condition, and when a test is clean

For **any** positive $dN/du$, setting $\bar q(k) := C/(dN/du)$ makes (O) true identically. **(O) is
empirically empty unless $\bar q$ is specified independently of abundance.** Every claim must state
whether its resource was measured independently or inferred from the distribution it explains.

A special case gives maximal content. When the resource *is* the coordinate — $q = k = m$ for
biomass spectra — then $\bar q(m) = m$ exactly, so $d \equiv 1$ **by definition**. (S) carries no
estimation error and the test isolates (O) alone. This is not a tautology: $\bar q$ is fixed by the
definition of the resource, not read off the abundance. The forbidden move remains
$\bar q := C/(dN/du)$.

The contrast matters empirically. In our solar-flare test the resource (fluence) differs from the
coordinate (peak irradiance), so $d$ was fitted at 0.858 with a 95% interval of [0.697, 1.054] — wide
enough that the observed discrepancy mixes failure of (O) with error in (S). Biomass tests have no
such confound, and their negative results are correspondingly more informative.

### 2.4 Nothing more basic implies (O)

Three routes that resemble derivations all fail.

**Conservation** fixes an integral, not its spread across scales. Turbulence settles this: in the
Kolmogorov inertial range $E(k) \propto k^{-5/3}$, so energy per logarithmic wavenumber is
$kE(k) \propto k^{-2/3}$ — decidedly not flat — while the energy *flux* is constant. Constant
throughput coexists with radically unequal occupancy.

**Scale covariance** yields a power function under regularity assumptions but does not force the
resource-spectrum exponent to zero.

**Maximum entropy** depends on constraints *and* reference measure. Maximising entropy over finitely
many equally weighted classes with normalisation and a fixed mean resource gives
$p_j \propto e^{-\lambda q_j}$, not $1/q_j$.

(O) is therefore a conjecture, not a consequence. It must not be presented as following from
conservation or symmetry.

### 2.5 The ensemble form

Our evidence (§4) says (O) is false of individual systems and true on average. That requires a
weaker hypothesis stated in its own right rather than as a retreat:

> **(O-ensemble)** Across systems within a class, the departure
> $s = -\,d\ln\mathcal{O}/d\ln k$ satisfies $E[s] = 0$ and $\mathrm{Var}[s] = \tau^2$, with $\tau$ a
> property of the class, not of the system.

Three features make this refutable.

**A shape prediction.** Constraining only a mean and a variance, maximum entropy makes the latent
distribution of $s$ Gaussian. Heavier tails mean the constraint set is richer than two moments.
Testing this requires deconvolution: observed spread is latent dispersion *convolved with*
measurement error.

**A predicted individual failure rate.** Given $\tau$ and a per-system tolerance $c$, the fraction
expected to pass individually is fixed — $2\Phi(c/\tau) - 1$ in the Gaussian case. A hypothesis that
holds only on average still says exactly how badly individual systems must fail.

**A prohibition on two resources at once.** If two resources both satisfy (O) on the same systems and
coordinate, then $s_1 - s_2 = d_2 - d_1$ is constant, so

$$\mathrm{Var}[s_1] = \mathrm{Var}[s_2], \qquad \mathrm{corr}(s_1, s_2) = 1.$$

Measuring two candidate resources on one set of systems and finding unequal dispersion refutes
(O-ensemble) for at least one. This is the cleanest decisive test available and requires no new
instrument.

---

## 3. Methods

### 3.1 Systems and data

| System | Source | n | Resource | Coordinate |
|---|---|---:|---|---|
| Solar flares | NOAA GOES XRS flare report, 2022–24 | 10,501 | integrated soft-X-ray fluence | peak irradiance |
| Earthquakes | USGS ComCat, 2010–24, $M_w \geq 5.5$ | 6,639 | magnitude-derived energy proxy | same |
| Ocean spectrum | Hatton et al. (2021), upper 200 m and full column | 23 bins | body mass | body mass |
| Aquatic spectra | GLOSSAQUA (Ersoy et al. 2025) | 1,300 | body mass | body mass |

All raw inputs are frozen with SHA-256 manifests; the retrieval script fails rather than silently
replacing a changed remote file.

### 3.2 Preregistration and its limits

The GLOSSAQUA analysis was registered before computation: datasets, inclusion criteria, the exponent
mapping for each published convention, tolerance factors, bootstrap scheme and success criteria were
committed to version control, and only categorical design columns were inspected beforehand. **No
slope value was read before the protocol was fixed.**

Two honest qualifications. The registration is a public commit, not a third-party registry.
Follow-up analyses in §4.5–4.8 are exploratory and labelled as such throughout: preliminary values
were seen while assessing feasibility.

### 3.3 Diagnostics

**Resource-spectrum accounting.** Sum the resource per logarithmic bin — equivalently, count times
*arithmetic* mean. Empty bins are retained, the final bin edge is included, and missing resource is
treated as missing rather than zero. Normalising by $C = R_{\text{domain}}/\ln(k_{\max}/k_{\min})$
makes the width-weighted mean of $\Phi = \mathcal{O}/C$ equal to one *by construction*; that is not
evidence of flatness.

**Goodness of fit.** Clauset–Shalizi–Newman with a parametric bootstrap, comparing against truncated
lognormal, exponential and stretched-exponential alternatives fitted on the same support. We depart
from standard practice in one respect: **the lower bound is declared, never fitted.** Selecting
$x_{\min}$ by minimising KS is legitimate elsewhere but incompatible with a protocol whose point is a
declared domain, and our threshold sensitivity (§4.2) shows what that latitude buys.

For catalogues on a fixed grid a continuous KS statistic is invalid, since ties inflate it. On the
rounded magnitude grid the Gutenberg–Richter law is exactly geometric: with $k = (M-M_0)/\Delta$ an
integer, $N(\geq M) \propto 10^{-bM}$ means $P(K=k) = (1-q)q^k$, $q = 10^{-b\Delta}$. We test on $k$.

**Equivalence testing.** Flatness requires **both** slope equivalence by TOST *and* bounded departure
$\max|\ln\Phi|$ within tolerance, because a spectrum can undulate with zero fitted slope. Tolerance
is a declared design choice: a maximum drift by factor $F$ across the domain gives
$|s| \leq \ln F/\ln(k_{\max}/k_{\min})$. **The tolerance scales with domain width**; applying a
two-decade tolerance to a 22-decade spectrum understates drift by an order of magnitude.

**Dispersion.** DerSimonian–Laird random effects for $\tau^2$ and $I^2$; latent-shape fitting by
convolving each candidate family with reported measurement errors; and a nested variance-components
model with known errors that reports components as confounded rather than inventing a split when
every group is observed once.

### 3.4 Reproducibility

Implementation is a tested Python package (54 unit tests) covering conservation, arithmetic-versus-
median accounting, unit invariance, missingness refusal, bin endpoints, density normalisation,
exponent recovery, goodness-of-fit discrimination, equivalence criteria, latent-shape recovery and
variance-component recovery. `make all` verifies every checksum, runs the tests and regenerates every
result.

---

## 4. Results

### 4.1 Earthquakes: decisive failure against a well-fitting distribution

With Gutenberg–Richter $N(\geq M) \propto 10^{-bM}$ and energy proxy $E \propto 10^{\gamma M_w}$, the
occupancy exponent is $1 - b/\gamma$, so flat energy occupancy **requires $b = \gamma$**. With
$\gamma = 1.5$ that means $b = 1.5$. The fitted value is $b = 0.998$, 95% interval
[0.973, 1.024], stable across thresholds and robust to the alternative conversion $\gamma = 1.44$.

The discrete goodness-of-fit test makes this failure unusually clean:

| Threshold | n | $b$ | KS | $p$ |
|---|---:|---:|---:|---:|
| $M \geq 5.5$ | 6,639 | 0.998 | 0.0077 | **0.256** |
| $M \geq 6.0$ | 2,076 | 0.984 | 0.0205 | 0.034 |
| $M \geq 6.5$ | 679 | 0.977 | 0.0381 | 0.026 |

At the declared threshold Gutenberg–Richter is **not ruled out**. The distribution is exactly the
form it should be, and equipartition fails on it by a wide margin — a failure of (O) with no
distributional irregularity to blame. (A continuous KS test on the same data gives 0.108 and
p = 0.000; that rejection is entirely an artefact of magnitudes tied to a 0.1 grid.)

Rejection at *higher* thresholds, where power is lower, indicates real upper-tail structure; a finite
maximum magnitude is marginally preferred throughout (ΔAIC −0.7 to −1.3), reported descriptively
since the truncation point is a boundary parameter.

### 4.2 Solar flares: failure, and a warning about domain choice

Training on 2022 and evaluating on 2023–24 — a genuine temporal prediction check — the resource
exponent $d = 0.858$ predicts $\alpha = 1.858$ [1.697, 2.054]. Observed: $\alpha = 2.239$
[2.085, 2.399] on the paired evaluation sample (n = 1,168). **Gap 0.382, interval
[0.125, 0.620], excluding zero.** Switching to rise-phase fluence, which has no missing values in the
domain, gives a gap of 0.411 [0.208, 0.604], so missingness does not explain it.

The peak-irradiance distribution is itself **ruled out as a power law** (α = 2.274 on all 1,306
in-domain evaluation events, KS = 0.032, p = 0.018). It beats exponential and stretched-exponential
decisively (p < 10⁻¹³) but is **indistinguishable from a lognormal** (Vuong p = 0.41).

Most importantly, lower thresholds of $10^{-6}$, $5{\times}10^{-6}$, $10^{-5}$ and
$3{\times}10^{-5}$ W/m² give gaps of **−0.480, 0.191, 0.382, 0.960**. The sign flips. A researcher
free to choose a threshold can obtain agreement, disagreement or over-shoot at will — which is why
§3.3 declares domains rather than fitting them.

### 4.3 Ocean spectrum: the data cannot decide

Re-expressing the Hatton et al. (2021) reconstruction reproduces the published abundance slope
(−1.039 against −1.04). The occupancy profile is a broad plateau with roll-off at both ends: over
15 decades of body mass $\Phi$ stays within a factor of **1.7**, while across the full 22 decades it
spans a factor of **38.8**.

Propagating the published per-group uncertainties — the interval is exactly
$[\text{est}/f,\ \text{est}\times f]$, verified for all 253 rows — gives the decisive result:
**only 2 of 23 bins have departures larger than the reconstruction uncertainty** at $F = 1.25$
(3 of 23 for the full water column). The boundary failures, and the plateau's flatness, are both
largely below the noise floor.

Applying the identical pipeline without tuning, the plateau does **not** transfer to the full water
column: the $\Phi$ ratio degrades from 1.7 to **4.3**. The flat trend survives the change of domain;
the equality does not.

### 4.4 Aquatic spectra: not supported for systems, centred for the ensemble

The preregistered test covers 1,300 normalised biomass spectra from 16 studies with independent
authors, ecosystems and instruments.

**By the declared criteria the verdict is *not supported*.** Only **7.8%** of spectra fall within
their own factor-1.25 tolerance, and **23.8%** at factor 2.

**Yet the centre is almost exactly right.** Median slope **−1.015** against a predicted −1.000;
median of per-study medians −1.005; random-effects pooled mean **−1.0113, 95% CI [−1.033, −0.990]**.

### 4.5 The centre is not an artefact

*Exploratory.* Three checks.

**The scatter is real.** From per-spectrum errors derived from reported intervals (747 of 1,300):
Q = 6,425 on 746 df, **I² = 88.4%**, τ = 0.252. Individual systems genuinely differ.

**No anchoring on the predicted value.** The literature does over-report round numbers — the
second-decimal digit distribution is non-uniform, χ² = 46.3 on 9 df, p = 5×10⁻⁷ — but the excess at
−1.00 (1.86× local baseline) is unremarkable against the other round values (1.46× median), ranking
only **3rd of 17**.

**It holds across strata.** Freshwater −1.010 [−1.019, −0.979]; marine −1.060 [−1.350, −0.827]; fish
−1.011; macroinvertebrates −1.000; zooplankton −0.990. Every stratum with a valid interval is
consistent with −1. (Strata with fewer than four study blocks receive no interval: with one study the
block bootstrap has zero width.)

### 4.6 The database label does not identify the estimand

*Exploratory, and a finding in its own right.*

Comparing across the two other published conventions in the same database — whose study sets are
**disjoint** — freshwater τ came out 0.228, 0.462 and 0.355, with mean departures +0.003, +0.397 and
+0.516. Reading the sources explains why.

Perkins et al. (2018) is filed under *Normalized abundance spectrum*. Its Methods regress "the log₁₀
of the total number (N) of all organisms in each size-bin" after "logarithmic binning", **without
dividing by bin width**, and state that the M–N slope equals "the individual size distribution
exponent + 1". Its orthopolity prediction is therefore **−1, not −2**, and its −0.798 is a departure
of +0.20 rather than +1.20.

Applying both mappings across the subset, **11 of 15 studies fit −1 better and 4 fit −2**. Girón
(2023) at −2.016 and Perkins at −0.798 carry the same label while differing by almost exactly 1 in
exponent.

We **exclude the subset as unusable rather than re-map it**: choosing each study's mapping by which
prediction it matches would manufacture the agreement. The implication is general — **compilations of
published scaling exponents cannot be pooled on their method labels** without per-study verification.

By contrast the primary subset shows no such contamination: **zero** studies within 0.3 of either
adjacent estimand, against 3 and 4 in the contaminated one. The two studies carrying 78% of the
evidence were read directly and both use the convention their label claims. Arranz et al. (2022)
computes "normalized scores … as the biomass index divided by interval" on log₂ bins and names −1 as
"the theoretical expected value"; Gaedke (1993) states the equivalence outright. Every summary
statistic in the database reproduces Arranz's published Table 1 to two decimals (n 639, mean −1.004
vs −1.00, SD 0.279 vs 0.28, min/max −1.741/−0.269 vs −1.74/−0.27).

### 4.7 Shape: two moments suffice within a class

*Exploratory.* Fitting latent families convolved with reported errors: Gaussian τ = 0.255; Laplace
ΔAIC +18.6; **Student t (ν = 8) ΔAIC −7.4**, with Gaussian standardised residuals well centred
(skew −0.07) but carrying excess kurtosis **+1.13**. The two-moment maximum-entropy form is
inadequate for the *pooled* sample.

This is a pooling artefact. Fitting strata separately, **freshwater alone is adequately Gaussian**
(τ = 0.228, excess kurtosis −0.34), while marine is heavier (τ = 0.383) and is itself a mixture of
reef, shelf and open ocean. A two-component mixture built from the fitted habitat parameters alone
reproduces excess kurtosis **+0.926** against the pooled **+1.132** — about 82%. The shape prediction
of §2.5 holds within a class; testing it on a pool violates its own scope condition, and τ is
confirmed as a *class* property (0.228 freshwater against 0.383 marine).

### 4.8 The hypothesis predicts its own failure rate

*Exploratory, and the sharpest result here.* The tension in §4.4 — median on −1 while 7.8% of systems
pass — is not a hypothesis half working. Given τ, (O-ensemble) *predicts* the pass rate:

| Tolerance | Predicted | Observed | Ratio |
|---|---:|---:|---:|
| $F = 1.25$ | 0.080 | **0.078** | 0.99 |
| $F = 2.00$ | 0.237 | **0.238** | 1.01 |

One dispersion parameter reproduces the observed failure rate to within 1–2% at both tolerances. We
label this an **internal consistency check, not an out-of-sample prediction** — τ is fitted to the
same slopes. It is nonetheless non-trivial: one number must reconcile the shape of the departure
distribution with a heterogeneous set of per-study tolerances derived from reported size ranges.

### 4.9 The dispersion is between ecosystems

*Exploratory.* The subset contains the two designs that isolate each component:

| Component | Study | Design | Estimate |
|---|---|---|---:|
| Between-site | Arranz et al. (2022) | 639 lakes × 1 occasion | **τ = 0.235** |
| Within-site (temporal) | Gaedke (1993) | 1 lake × 377 occasions, 10 yr | **SD = 0.067** |

Temporal variation is at most **8.2% of the variance**. Lakes genuinely differ in how equally biomass
is spread across size classes; a single lake stays comparatively fixed through a season. Two studies
with both several sites and repeat visits agree on direction (74% and 81% between-site) though both
are small.

Arranz report SD = 0.28 across 639 lakes; our latent τ of 0.235 is necessarily smaller and smaller by
about the right amount — an external check on the deconvolution, since τ was fitted to nothing they
published.

### 4.10 Span dependence: underpowered

*Exploratory.* Wider-spanning studies sit closer to −1 at study level (Spearman ρ = −0.549,
p = 0.028, n = 16), consistent with an averaging mechanism. Within taxa nothing reaches significance
and signs disagree (fish ρ = −0.50, p = 0.39; macroinvertebrates −0.21, p = 0.79; zooplankton +0.40,
p = 0.60). This is a power failure, not a null result: span is partly a proxy for taxon and four or
five study blocks per taxon cannot separate them.

We note a methodological trap here. At *spectrum* level the same test gives ρ = −0.427 with
p = 8×10⁻⁵⁹ — apparently overwhelming, and almost entirely one study contributing 377 spectra at a
single span value. Pseudo-replication converts a marginal signal into spurious certainty.

---

## 5. Discussion

### 5.1 What holds

Equipartition of an additive resource across logarithmic size classes describes the **expected value**
of aquatic size spectra, robustly. The centre sits within 0.015 of prediction, survives checks for
reporting artefacts, holds separately in freshwater and marine systems and across three taxonomic
groups, and its conventions are verified against the sources. Within a homogeneous class the
dispersion is Gaussian with τ ≈ 0.23, and that single parameter predicts how often individual systems
fail a tolerance test.

### 5.2 What does not

The universal reading is dead. Earthquakes and solar flares fail decisively, and the earthquake case
is the strongest evidence in the paper precisely because its distribution is textbook-correct. The
claim about individual systems is also dead: τ ≈ 0.235 is real between-ecosystem variation, not
measurement noise.

And the framework does not explain observed power laws in the way its motivation suggests. The flare
distribution is not a power law by the standard test, and in no system tested can a power law be
distinguished from a lognormal. Part of the explanandum is not clearly there.

### 5.3 The mean without the dispersion is not an explanation

The central open problem is now sharp: **why should the expected slope be −1 when individual
ecosystems scatter with τ ≈ 0.235?** Averaging is a candidate on marginal and confounded evidence
(§4.10). Any mechanism proposed must reproduce both the location and the measured spread; an account
of the mean alone is incomplete.

### 5.4 What would refute (O-ensemble)

1. **Replication.** An independent dataset must reproduce the class-specific τ — ≈ 0.235 for
   temperate lake fish communities. Crucially, what must replicate is the **between-site** component:
   a study visiting few sites many times will find a smaller τ for reasons unrelated to the
   hypothesis.
2. **Two resources at once.** Unequal dispersion, or imperfectly correlated departures, for two
   resources measured on the same systems refutes at least one. No new instrument required.
3. **Pass rates** inconsistent with a dataset's own fitted τ.

### 5.5 Limitations

- **Coverage.** GLOSSAQUA is 87% freshwater and 80% fish. The strata that would test generality
  hardest are the smallest.
- **Two studies carry 78%** of the primary evidence. Their conventions are verified and their
  statistics reproduce exactly, but the result is not broadly distributed across sources.
- **The replication prohibition is untested.** The intended out-of-sample test (PSSdb, Dugenne et al.
  2024) was unreachable during this work.
- **Bounds, not a partition.** The variance components come from different studies in different
  ecosystems; treating Lake Constance as representative of Ontario lakes is an assumption.
- **Preregistration is partial.** §4.5–4.10 are exploratory. The tolerance factors were chosen by the
  analysts, not registered externally, and the ocean plateau passes at $F = 2$ while failing at
  $F = 1.25$.
- **No discrete alternative comparison** has been fitted on the earthquake support.
- **Ocean uncertainty** propagation assumes independence across groups and bins, which will overstate
  precision if errors are correlated.

### 5.6 Relation to prior work

The equivalence is Gaedke's (1993) and Sheldon's (1972). Damuth's (1981) energetic equivalence rule
is the same accounting on metabolic rate, with its own documented failures (Isaac et al. 2013).
Hatton et al. (2021) provide the modern ocean reconstruction; Cuesta et al. (2018) a mechanistic
plankton model any new theory must beat. Our contribution is the domain map, the dispersion estimate,
the ensemble formulation with its prohibitions, and the methodological finding of §4.6.

---

## 6. Conclusions

Resource equipartition across logarithmic scale is not a universal law and not a property of
individual systems. It is a well-characterised regularity in the **expected value** of aquatic size
spectra, with a measured between-ecosystem dispersion of τ ≈ 0.235 that predicts the rate at which
individual systems depart from it. It fails cleanly outside ecology in the two physical systems
tested.

Stated as an ensemble hypothesis it forbids specific things and can be refuted by a study that
measures two resources on one set of systems. That test requires no new instrument and would be
decisive.

---

## Data and code availability

All analyses reproduce from frozen, checksummed snapshots via `make all` at
<https://github.com/ttm/orthopolity>. Raw inputs: NOAA NCEI GOES XRS flare reports (unrestricted);
USGS ComCat (public domain); Hatton et al. (2021) summary tables; GLOSSAQUA (MIT licence). The
preregistration is `configs/prereg_2026-09-09.json`, committed before the analyses it governs.

## References

*(To be formatted for the target venue; see `docs/references.md` for the full annotated list.)*

Arranz, I., et al. (2022) *Ecology* 103, e3608 · Clauset, A., Shalizi, C. R., & Newman, M. E. J.
(2009) *SIAM Review* 51, 661 · Cuesta, J. A., Delius, G. W., & Law, R. (2018) *J. Math. Biol.* 76, 67
· Damuth, J. (1981) *Nature* 290, 699 · Dugenne, M., et al. (2024) *ESSD* 16, 2971 · Ersoy, Z., et
al. (2025) *Ecology* 106, e70050 · Gaedke, U. (1993) *Limnol. Oceanogr.* 38, 112 · Hatton, I. A., et
al. (2021) *Sci. Adv.* 7, eabh3732 · Isaac, N. J. B., Storch, D., & Carbone, C. (2013) *Glob. Ecol.
Biogeogr.* 22, 1 · Mitzenmacher, M. (2004) *Internet Math.* 1, 226 · Newman, M. E. J. (2005)
*Contemp. Phys.* 46, 323 · Perkins, D. M., et al. (2018) *Ecol. Lett.* 21, 1721 · Sheldon, R. W.,
Prakash, A., & Sutcliffe, W. H. (1972) *Limnol. Oceanogr.* 17, 327 · Sprules, W. G., & Barth, L. E.
(2016) *Can. J. Fish. Aquat. Sci.* 73, 477
