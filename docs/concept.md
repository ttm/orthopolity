# Orthopolity: a precise statement of the concept

> Status: critical reconstruction. This document restates the idea from
> [the source essay](https://ttm.github.io/2024/08/14/power.html) in a form that can be
> attacked, tested, and cited. Where it diverges from the essay, the divergence is flagged.
>
> **Revision note.** An earlier version of this document stated orthopolity in the
> *linear*-bin convention (equal resource per unit $k$). That is a different hypothesis from
> the one with empirical precedent, and it disagrees by one in the exponent with the
> size-spectrum literature. Corrected throughout to the logarithmic convention. See §6.

## 1. The idea in one sentence

**An additive resource occupies each logarithmic size class equally; therefore objects that
cost more of it are proportionally rarer.**

The essay's phrasing — "the equal distribution of resources along unit load: more resources on
the unit makes it less frequent" — is the same claim. The reformulation makes the conserved
quantity, the classes, and the *measure* explicit, because that is where all the content lives.

## 2. Formal setup

Declare, **before inspecting any abundance pattern**:

| Symbol | Meaning |
|---|---|
| object | the thing being counted (an organism, an event, a city, a word) |
| $k > 0$ | the scale coordinate, with reference $k_0$; $\;u = \ln(k/k_0)$ |
| $q$ | the additive per-object resource (energy, biomass, time, money) |
| $\bar q(k) = E[q \mid k]$ | the **conditional arithmetic mean** resource at scale $k$ |
| $dN/du$ | objects per unit log scale |
| $[k_{\min}, k_{\max}]$ | the declared finite observation domain |

$\bar q$ is a conditional mean, not a deterministic function: real objects at the same scale
use different amounts. It must be the **arithmetic** mean, because only the arithmetic mean
preserves the sum that the whole accounting rests on. Fitting OLS to $\log q$ estimates the
*geometric* mean and silently breaks the identity.

The **resource spectrum** is

$$\mathcal{O}(k) \;=\; \frac{dR}{du} \;=\; \bar q(k)\,\frac{dN}{du}.$$

## 3. The orthopolity hypothesis

**(O)** $\;\mathcal{O}(k) = C$ for all $k$ in the declared domain.

This is the whole claim. Note what it is *not*: it is a statement about the **stock** of resource
resident at each scale, not about a **flux** through scales. See §8.

### 3.1 The ensemble form

(O) as stated is a claim about a system. The evidence says it is false at that level and true on
average ([evidence.md §5–6](evidence.md)), which requires a weaker hypothesis stated in its own
right rather than as a retreat:

> **(O-ensemble)** Across systems within a class, the resource-spectrum departure
> $s = -\,d\ln\mathcal{O}/d\ln k$ has
> $$E[s] = 0, \qquad \mathrm{Var}[s] = \tau^2,$$
> with $\tau$ a property of the class, not of the system.

Three things make this a hypothesis rather than a description.

**It has a shape prediction.** Constraining only a mean and a variance, maximum entropy makes the
latent distribution of $s$ **Gaussian**. Any heavier tail means the constraint set is richer than
two moments — which is a finding, not a nuisance. Testing this requires deconvolution: the observed
spread of published slopes is the latent dispersion *convolved with measurement error*, so the
comparison is against Gaussian ⊛ reported errors, never against the raw histogram.

**It predicts the individual failure rate.** Given $\tau$ and a per-system tolerance $c$, the
fraction of systems expected to pass individually is fixed — $2\Phi(c/\tau) - 1$ in the Gaussian
case. So (O-ensemble) *forbids* particular pass rates. A hypothesis that holds only on average is
still refutable, because it says exactly how badly individual systems must fail.

**It forbids two resources at once.** Sharpening [§10](#10-two-constraints-that-sharpen-the-hypothesis):
if two resources both satisfy (O) on the same systems and coordinate, then $s_1 - s_2 = d_2 - d_1$
is a constant, so

$$\mathrm{Var}[s_1] = \mathrm{Var}[s_2] \quad\text{and}\quad \mathrm{corr}(s_1, s_2) = 1.$$

Measuring two candidate resources on one set of systems and finding unequal $\tau$, or imperfectly
correlated departures, refutes (O-ensemble) for at least one of them. This is the cleanest available
route to a decisive test.

**What would refute it.** A class whose $\tau$ does not replicate on independent data; a pass rate
inconsistent with the fitted $\tau$; two resources with unequal dispersion; or $E[s] \neq 0$.

## 4. Orthopolity alone does not give a power law

(O) yields $dN/du \propto 1/\bar q(k)$ for **whatever $\bar q$ is**. The power law needs a second,
independent ingredient:

**(S) Scale-invariant cost.** $\;\bar q(k) = q_0 (k/k_0)^{d}$.

$$\textbf{(O)} + \textbf{(S)} \;\implies\; \frac{dN}{d\ln k} \propto k^{-d}, \qquad \frac{dN}{dk} \propto k^{-(d+1)}$$

The exponent comes *entirely from (S)*. In the essay's boxes, $k$ is side length, $q \propto k^3$,
and $d = 3$ is Euclidean dimension inserted by hand — equivalently the box-counting dimension of
a space-filling set. The essay's postulate 4 ("$\alpha$ is the dimensionality of $r$") is correct
but is a statement about (S), not about orthopolity.

**Counterexample.** Let $\bar q(k) = e^{k}$. Then (O) holds exactly and gives $dN/du \propto e^{-k}$:
a perfectly orthopolar *exponential*. So "Orthopolity ⟹ the Natural distribution law" is false as
written. The valid claim is:

> Orthopolity applied to a scale-free cost yields a power law.

Two ingredients, separable, and worth separating: much of what the essay credits to orthopolity is
being done by scale invariance, which is old and well understood.

## 5. The content condition

For **any** positive $dN/du$, define $\bar q(k) := C \big/ (dN/du)$. Then (O) holds identically.

So orthopolity is **empirically empty until $\bar q$ is specified independently of abundance** —
measured directly, or derived from theory, but never read off the distribution it is meant to explain.

| | Status |
|---|---|
| $\bar q$ inferred from abundance | Tautology. No content. Not evidence. |
| $\bar q$ measured independently, then $\mathcal{O}$ tested for flatness | Falsifiable claim. Real content. |

Note the converse trap, too: choosing the resource to *be* the scale variable is a legitimate
physical choice (as in the Sheldon spectrum, where resource = body mass). The tautology arises
specifically when the resource is defined from inverse abundance.

Every empirical claim in this repository must state which row it is in.

### 5.1 The cleanest case: when the resource *is* the scale variable

There is a special case where the test has maximal content, and it is worth naming because it
explains why the ecological evidence is sharper than everything else in this repository.

Take the resource to be body mass and the scale coordinate to be body mass: $q = k = m$. Then

$$\bar q(m) = E[q \mid m] = m \quad\text{exactly},$$

so in the form $\bar q = q_0 (k/k_0)^d$ we have $d \equiv 1$ **by definition**. Assumption (S) is
not an approximation, not a fit, and carries no estimation error.

**Consequence: such a test is a pure test of (O) alone.** The two ingredients that
[§4](#4-orthopolity-alone-does-not-give-a-power-law) separates are normally entangled in any
measurement — a failure could be (O) breaking or (S) being mis-estimated. Here (S) is exact, so
every departure is attributable to (O).

This is not a tautology, despite $q$ and $k$ being the same variable. The content condition of §5
is satisfied because $\bar q$ is fixed by *definition of the resource*, not inferred from the
abundance it is meant to explain — the forbidden move is defining $\bar q := C/(dN/du)$, which is
a different thing entirely. What remains empirical, and can fail, is whether total mass is actually
equipartitioned across logarithmic mass classes.

**The contrast is stark in this repository's own results.** In the solar-flare test the resource
(fluence) is distinct from the coordinate (peak irradiance), so $d$ had to be *fitted*: 0.858 with
a 95% interval of [0.697, 1.054]. That interval is wide enough to matter, and the observed gap of
0.382 therefore mixes a failure of (O) with uncertainty in (S). The biomass tests have no such
confound. Two consequences follow:

- **Biomass-spectrum evidence is stronger per observation** than the flare or earthquake evidence,
  and should be weighted accordingly — see the revised table in §11.
- **A negative result is more informative there too.** When the ocean plateau fails to transfer to
  the full water column, (O) is what failed; there is no fitted exponent to blame.

The general lesson: **prefer tests in which the resource is the coordinate, or in which $\bar q(k)$
is known analytically rather than estimated.** Where $d$ must be fitted, report its interval and
propagate it, because a gap smaller than the uncertainty in $d$ is not evidence about (O) at all.

## 6. Measure: the exponent shifts by one

Orthopolity is defined against a measure, and the choice is not cosmetic — the two versions are
**different hypotheses about the world**:

- Equal resource per **linear** bin $dk$: $\;\bar q \cdot dN/dk = C$
- Equal resource per **logarithmic** bin $d\ln k$: $\;\bar q \cdot dN/d\ln k = C$

**This repository uses the logarithmic convention throughout**, because that is the one with
empirical precedent (Sheldon spectra, energetic equivalence, all size-spectrum work).

Conversions, which must never be skipped:

| Representation | Exponent under (O)+(S) |
|---|---|
| Logarithmic histogram $dN/d\ln k$ | $-d$ |
| Probability density $dN/dk$ | $\alpha = d + 1$ |
| Complementary cumulative (CCDF) | $d$, far below the upper cutoff |
| Rank–size | $1/d$ |

Near a finite upper boundary the CCDF acquires a subtraction term and is **not** an exact monomial.
A log-histogram, a density, a CCDF and a rank plot must never share an exponent label without
conversion.

## 7. Normalisation forces cutoffs — and proves nothing

$$C = \frac{R_{\text{domain}}}{\ln(k_{\max}/k_{\min})}, \qquad \Phi(k) = \frac{\mathcal{O}(k)}{C}$$

A nonzero constant allocation across infinitely many logarithmic intervals requires infinite
resource, so physical endpoints are part of the model, not housekeeping.

**Critically: this normalisation makes the width-weighted mean of $\Phi$ equal to one by
construction. It does not make $\Phi$ flat.** Flatness is the separate, testable question.
Reporting that $\Phi$ averages to 1 is not evidence of anything.

## 8. Stock is not flux — the turbulence counterexample

In the Kolmogorov inertial range, $E(k) \propto k^{-5/3}$, so energy per logarithmic wavenumber
is $k E(k) \propto k^{-2/3}$ — decidedly **not** flat. Yet the energy *flux* through scales is
constant. Constant throughput coexists with radically unequal occupancy.

Any intuition of the form "the resource is conserved, therefore it is equally distributed" dies
here. Conservation fixes an integral; it does not fix how the integral is spread over scales.

## 9. What does *not* select equal allocation

Three plausible-sounding derivations fail:

1. **Scale covariance.** Exact scale covariance yields a power function under regularity
   assumptions. It does not determine that the resource spectrum has exponent zero.
2. **Conservation.** Fixes an integral, not its distribution among scales (§8).
3. **Maximum entropy.** Depends on both constraints *and* reference measure. Maximising entropy
   over finitely many equally weighted classes with normalisation and fixed mean resource gives
   $p_j \propto e^{-\lambda q_j}$ — **not** $1/q_j$. Constraining a logarithmic moment can
   generate a power law; constraining an ordinary additive mean generates an exponential.

> **The open problem, stated precisely: what dynamics or symmetry selects equal allocation among
> resource classes?** Nothing currently on offer supplies it. Until something does, orthopolity is
> an accounting identity plus an empirical conjecture, not a derived law.

## 10. Two constraints that sharpen the hypothesis

**Two-resource constraint.** If two resources both have flat spectra for the same objects and
coordinate, their mean per-object costs must have a constant ratio — hence $d_1 = d_2$. Resources
with **different scaling exponents cannot both** satisfy the hypothesis over the same domain. So
"which resource?" is not a free choice: at most one resource dimension per system can be orthopolar.
This is a genuine restriction and a source of falsifiable predictions.

**Intervention ratio.** Under an intervention,

$$\frac{n_2(k)}{n_1(k)} = \frac{C_2}{C_1}\,\frac{\bar q_1(k)}{\bar q_2(k)}$$

The normalisation $C_2/C_1$ cancels **only** when the resource budget and the logarithmic domain
are both unchanged. Omitting it is a common error.

## 11. Which of the essay's examples carry evidential weight

Not all of them do, and mixing them weakens the case.

| Example | Kind of claim | Evidential weight |
|---|---|---|
| Ideal boxes, $L^3/l^3$ | Geometric identity | **None.** Good pedagogy, no empirical content. |
| Sound: $f = 1/T$ | Definitional | **None.** Frequency *is* the reciprocal of period. |
| Sound: $f = v/\lambda$ | Definitional | **None.** |
| Stevens' law | Stimulus→response function | **None — category mismatch.** Not a frequency distribution over objects. The essay half-notices this and should drop it. |
| Zipf, words | Empirical distribution | **Moderate.** Real, but needs the rank/pdf exponents disentangled and full CSN testing. |
| City populations | Empirical distribution | **High**, if the resource is stated. $d$ would have to be fitted, so its interval must be propagated (§5.1). |
| *Solar flares, earthquakes* (this repository) | Empirical, $\bar q$ distinct from $k$ | **Moderate.** $d$ is fitted — 0.858 [0.697, 1.054] for flares — so a departure mixes failure of (O) with error in (S). |
| Knowledge / expertise | Speculative | **None as stated** — no data. Genuinely testable, though. |
| *Sheldon ocean spectrum, GLOSSAQUA* (absent from essay) | Empirical, **resource = coordinate** | **Highest.** $d \equiv 1$ exactly, so these are pure tests of (O) with no fitted exponent to absorb blame (§5.1). |
| *Damuth / energetic equivalence* (absent from essay) | Empirical, independent $\bar q$ | **High**, with a caveat: it is a species-population relation, not community abundance per log size bin. |

Roughly half the essay's illustrations are identities restated. Identities cannot support a law.

## 12. What is assumed, derived, and empirical

| Component | Status |
|---|---|
| (O) equal resource per log class | **Assumed.** The hypothesis itself. |
| $dN/du \propto 1/\bar q$ | **Derived** — trivially; it is (O) rearranged. |
| (S) $\bar q \propto k^{d}$ | **Assumed**, separately. Supplies the exponent. **Exact, with $d = 1$, whenever the resource is the coordinate** (§5.1); fitted otherwise, and then its interval must be propagated. |
| $dN/dk \propto k^{-(d+1)}$ | **Derived** from (O)+(S). |
| $d$ = dimensionality of the resource | **Interpretation** of (S). Equals box-counting dimension. |
| Conservation / maxent / scale covariance ⟹ (O) | **False.** See §9. |
| Deviations = "friction" | **Not a model.** A name for the residual until something predicts it. |
| (O) holding in any given system | **Empirical.** Tested; see [evidence.md](evidence.md). |

## 13. Errata in the source essay

1. **Sign error in the central equation.** In *Equality of resources distributed*:
   `P(k) = N * p(k) = N * C * k^{\alpha}` should read $k^{-\alpha}$.
2. **Rank and pdf exponents conflated.** The Zipf section writes $f \propto \rho^{-\alpha}$ with
   $\rho$ = *rank*, and treats that $\alpha$ as the pdf exponent. See the conversion table in §6.
3. **Stevens' law sign and category.** Written $\Psi(I) = k I^{-\alpha}$ with negative $\alpha$;
   conventionally $\Psi = k I^{\beta}$, $\beta > 0$. And it is a response function, not a
   distribution — see §11.
4. **Measure unspecified** throughout — see §6.
5. **"Uniform ⟹ Power" presented as a consequence.** It is (O) rearranged, not a derivation.

## 14. The strongest available framing

Not "a third cosmological principle alongside homogeneity and isotropy" — those are spacetime
symmetries and orthopolity is not one; see [criticism.md §1](criticism.md).

The defensible framing is the symmetry triad **translation → rotation → dilation**, with the
honest description:

> Orthopolity is an **equipartition hypothesis about resource stock across logarithmic scale**.
> Combined with a scale-free cost it generates the power-law family. Its empirical content is the
> claim that a specific, independently measurable resource is the equipartitioned one — and its
> scientific value lies in mapping the domain where that is true.

The research question, stated so it can be answered:

> **Under what independently specified conditions does an additive resource have approximately
> equal occupancy across logarithmic size intervals?**
