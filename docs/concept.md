# Orthopolity: a precise statement of the concept

> Status: critical reconstruction. This document restates the idea from
> [the source essay](https://ttm.github.io/2024/08/14/power.html) in a form that can be
> attacked, tested, and cited. Where the reconstruction diverges from the essay, the
> divergence is flagged explicitly.

## 1. The idea in one sentence

**A conserved resource is shared equally across size classes of the containers that hold it;
therefore containers holding more of it are proportionally rarer.**

The essay's phrasing — "the equal distribution of resources along unit load: more resources
on the unit makes it less frequent" — is the same claim. The reformulation above makes the
conserved quantity and the classes explicit, because that is where all the content lives.

## 2. Formal setup

Let

- $U = \{u_i\}_{i=1}^{N}$ be a set of $N$ **units** (containers): rooms, people, cities,
  species, words, files, firms.
- $r$ be a single scalar **resource**: volume, energy, time, attention, money, information.
- $k$ index a **class** of units — all units holding the same resource amount, written $r(k)$.
- $p(k)$ be the fraction of units in class $k$, over a support $[k_{\min}, k_{\max}]$.

The essay's two-index notation $q(i,j) = m(j,i) = u_i(r_j) = r_j(u_i)$ collapses to $r(k)$ once
a single resource is fixed. The full two-index machinery is only needed for the compound-resource
case (the essay's postulate 4), which is not yet developed anywhere.

## 3. The orthopolity condition

**(O) Orthopolity.** The total resource held by a class is the same for every class:

$$N \cdot p(k) \cdot r(k) = C \qquad \text{for all } k \in [k_{\min}, k_{\max}]$$

Immediately, $p(k) \propto 1 / r(k)$. This *is* the essay's postulate 1. It is not derived from
it — postulate 1 and the "most impressive consequence" in the essay's final section are the same
equation read in two directions.

## 4. Orthopolity alone does not give a power law

This is the central correction.

(O) yields $p \propto 1/r$ **whatever $r$ is**. To get a power law you need a second,
independent ingredient:

**(S) Scale-invariant labelling.** $r(k) = c \, k^{\alpha}$.

$$\textbf{(O)} + \textbf{(S)} \implies p(k) = C' k^{-\alpha}$$

The exponent $\alpha$ comes *entirely from (S)*, not from (O). In the essay's boxes, $k$ is the
side length, $r = k^3$, and $\alpha = 3$ is Euclidean dimension inserted by hand — equivalently,
the box-counting dimension of a space-filling set. This is why the essay's postulate 4
("one useful interpretation of $\alpha$ is the dimensionality of $r$") is correct but is a
statement about (S), not about orthopolity.

**Counterexample.** Let $r(k) = e^{k}$. Then (O) holds exactly and gives $p(k) \propto e^{-k}$:
a perfectly orthopolar *exponential* distribution. So the claim "Orthopolity ⟹ the Natural
distribution law" is false as stated. The valid claim is:

> Orthopolity applied to a scale-free resource yields a power law.

Two ingredients, separable, and worth separating: much of what the essay attributes to
orthopolity is really doing the work of scale invariance, which is old and well understood
(power laws are the unique solutions of $f(ax) = g(a) f(x)$).

## 5. The content condition — the most important methodological point

For **any** strictly positive $p(k)$, define $r(k) := C / (N\, p(k))$. Then (O) holds identically.

So orthopolity is **empirically empty until $r$ is specified independently of $p$** — measured
directly, or derived from theory, but never read off the distribution it is meant to explain.

This gives a clean criterion:

| | Status |
|---|---|
| $r$ fitted or inferred from $p$ | Tautology. No content. Not evidence. |
| $r$ measured independently, then $N p r$ tested for constancy | Falsifiable claim. Real content. |

**Damuth's law is the exemplar of the good case.** Metabolic rate $B \propto M^{3/4}$ is measured
independently of population density $N \propto M^{-3/4}$; the product $N \cdot B$ being
size-independent is then a genuine, checkable assertion — one which holds approximately and
[measurably fails in places](https://onlinelibrary.wiley.com/doi/full/10.1111/j.1466-8238.2012.00782.x).
That failure is what makes it science.

Every future empirical claim in this repository must state which row of that table it is in.

## 6. Measure and binning: the exponent shifts by one

Orthopolity is defined against a measure, and the essay does not say which. Its own closing
exercise ("what happens when $k$ is continuous?") is exactly where this bites.

- Equal resource per **linear** bin $dk$: $\;p(k)\, r(k) = C$
- Equal resource per **logarithmic** bin $d(\ln k)$: $\;p(k)\, k\, r(k) = C$

The two differ by one in the exponent. Any statement of (O) must fix the measure, or it is
ambiguous by exactly the amount that is usually under dispute.

## 7. Normalisation forces cutoffs

$\int k^{-\alpha} dk$ diverges at $0$ for $\alpha \ge 1$ and at $\infty$ for $\alpha \le 1$. No
single $\alpha$ normalises on $(0, \infty)$. So $k_{\min}$ and $k_{\max}$ are not housekeeping —
they are where the physics lives, and total resource $C \times (\text{number of classes})$ depends
on them. The essay's postulate 3 gestures at this; it needs to be load-bearing instead.

## 8. Which of the essay's examples actually carry evidential weight

Not all of them do, and mixing them weakens the case.

| Example | Kind of claim | Evidential weight |
|---|---|---|
| Ideal boxes, $L^3/l^3$ | Geometric identity | **None.** Good pedagogy, no empirical content. |
| Sound: $f = 1/T$ | Definitional | **None.** Frequency *is* the reciprocal of period. |
| Sound: $f = v/\lambda$ | Definitional | **None.** |
| Stevens' law | Stimulus→response function | **None — category mismatch.** Not a frequency distribution over containers. The essay half-notices this and should drop it. |
| Zipf, words | Empirical distribution | **Moderate.** Real, but needs CSN testing and the rank/pdf exponents disentangled. |
| City populations | Empirical distribution | **High.** Genuine power law, independent resource candidates exist, directly testable. |
| Knowledge / expertise | Speculative | **None as stated** — no data. But genuinely testable (citations, chess ratings, repo contributions, reputation scores). |
| *Damuth / energetic equivalence* (absent from essay) | Empirical, independent $r$ | **Highest.** The strongest precedent and the obvious positive control. |

Roughly half the essay's illustrations are identities restated. Identities cannot support a law.

## 9. What is assumed, derived, and empirical

| Component | Status |
|---|---|
| (O) equipartition of resource across classes | **Assumed.** The principle itself. |
| $p \propto 1/r$ | **Derived** — trivially, it is (O) rearranged. |
| (S) $r \propto k^{\alpha}$ | **Assumed**, separately. Does the real work. |
| $p(k) \propto k^{-\alpha}$ | **Derived** from (O)+(S). |
| $\alpha$ = dimensionality of $r$ | **Interpretation** of (S). Equals box-counting dimension. |
| Deviations = "friction" | **Not a model.** Currently a name for the residual. |
| Any given system satisfying (O) | **Empirical.** Untested so far. |

## 10. Errata in the source essay

Concrete and fixable:

1. **Sign error in the central equation.** In *Equality of resources distributed*:
   `P(k) = N * p(k) = N * C * k^{\alpha}` should read $k^{-\alpha}$.
2. **Rank and pdf exponents conflated.** The Zipf section writes $f \propto \rho^{-\alpha}$ with
   $\rho$ = *rank*, $\alpha \approx 1$, and treats that $\alpha$ as the same object as the pdf
   exponent in $p(k) = C k^{-\alpha}$. They differ by one (Zipf rank exponent 1 ↔ pdf exponent 2).
   If rank-frequency goes as $\rho^{-\beta}$, the frequency pdf goes as $f^{-(1 + 1/\beta)}$.
   This is the most-checked error in the power-law literature.
3. **Stevens' law sign and category.** Written $\Psi(I) = k I^{-\alpha}$ with $\alpha \in [-2,-0.3]$;
   Stevens' law is conventionally $\Psi = k I^{\beta}$ with $\beta > 0$. Beyond the double negative,
   it is a response function, not a distribution — see §8.
4. **Measure unspecified** throughout — see §6.

## 11. The strongest available framing

Not "a third cosmological principle alongside homogeneity and isotropy" — those are spacetime
symmetries (invariance of the metric under translation and rotation) and orthopolity is not one.
See [criticism.md §1](criticism.md).

The defensible framing is the symmetry triad **translation → rotation → dilation**. Scale
invariance is the genuine third member, and power laws are exactly its invariant functions.
Orthopolity is then best described as:

> an **equipartition accounting identity** which, combined with dilation symmetry, generates
> the power-law family — and whose empirical content is the claim that a specific,
> independently measurable resource is the equipartitioned one.

That last clause is the whole research programme. See [value.md](value.md).
