# The case against orthopolity — and against spending time on it

> The strongest honest version of the objections, revised after empirical testing. Read with
> [value.md](value.md) and [evidence.md](evidence.md).

## 1. It is not a cosmological principle (fatal to the current framing)

Homogeneity and isotropy are **spacetime symmetries** — invariance of the metric under translation
and rotation. They force the FLRW metric and are tested against CMB anisotropy and galaxy surveys.
They are statements about the geometry of the universe.

Orthopolity is a statistical statement about how a resource partitions across logarithmic size
classes. Different category. Calling it "a third cosmological principle, together with Isotropy and
Homogeneity" is a category error, and it is the first sentence of the abstract.

Worse, the nearest correct version **contradicts** the framing. The genuine third symmetry is
dilation, and exact scale invariance is *in tension with* large-scale homogeneity — the historical
fractal-universe debate (Sylos Labini, Pietronero) against the measured transition to homogeneity at
roughly 70–100 Mpc/h. They cannot both hold at all scales. Orthopolity is not a companion to
homogeneity; at cosmological scales it is a rival that lost.

**Cost:** a physicist stops reading at the abstract, and everything downstream — including the
correct parts and the real empirical results — goes with it. This single choice probably costs more
than every other problem here combined.

## 2. The central derivation is an identity presented as a discovery

$\bar q \cdot dN/d\ln k = C$ and $dN/d\ln k \propto 1/\bar q$ are the same equation. The essay
states the first as its concluding "most impressive consequence" and the second as its opening
postulate, with examples in between, creating the impression that one was derived from the other.
Nothing was derived. A referee sees this immediately, and a circularity at the core is
disproportionately damaging to how everything else is read.

## 3. The power law does not follow from the principle

(O) gives $dN/du \propto 1/\bar q$ for *any* $\bar q$. With $\bar q(k) = e^k$, orthopolity holds
exactly and produces an exponential ([concept.md §4](concept.md)). The power law requires
scale-invariant cost as a separate assumption, and that assumption carries the exponent. Once
separated, the residual contribution shrinks: the power law comes from scale invariance, which is
standard; orthopolity contributes the equipartition reading.

## 4. Nothing selects equal allocation

Three routes that sound like derivations all fail ([concept.md §9](concept.md)):

- **Conservation** fixes an integral, not its spread across scales. The turbulence case settles
  this: constant energy *flux* coexists with energy occupancy $\propto k^{-2/3}$, which is not flat.
- **Scale covariance** yields a power function; it does not force the resource-spectrum exponent
  to zero.
- **Maximum entropy** with normalisation and a fixed mean resource over equally weighted classes
  gives $p_j \propto e^{-\lambda q_j}$, *not* $1/q_j$.

So there is no derivation of orthopolity from anything more basic. It is a conjecture. That is not
fatal — conjectures are respectable — but it must not be presented as a consequence of conservation
or of symmetry, because it is neither.

## 5. As originally stated, it was unfalsifiable

Postulate 2 said deviations "are the result of other natural laws," illustrated by an apple stuck in
a tree while gravity still acts. That analogy explains in advance why no observation can count
against the principle. Combined with the content condition — (O) is true by definition for any
distribution if $\bar q := C/(dN/du)$ — the original formulation had **no empirical content at all**.

This is now partly answered: the reformulation in [concept.md](concept.md) is falsifiable, and it
has in fact been falsified twice ([evidence.md](evidence.md)). But "friction" remains a name for the
residual rather than a model, and any future appeal to it without an independently predicted form
reintroduces the problem.

## 6. Substantial prior art, and the closest case was missed

The word "orthopolity" appears nowhere in the literature. The content appears repeatedly:

- **The Sheldon spectrum** (Hatton et al. 2021) — approximately equal ocean biomass per logarithmic
  body-mass class, bacteria to whales. This is the orthopolity accounting exactly, measured, with
  resource = body mass. It is the closest prior work and it is absent from the essay.
- **Cuesta, Delius & Law (2018)** — a scale-invariant plankton model connecting the Sheldon spectrum
  to physiological scaling and coexistence. This is the mechanistic bridge a new theory would need
  to *beat*, not a gap to fill.
- **Energetic equivalence** (Damuth 1981; named by Nee et al. 1991). Constant total energy per size
  class, 45 years old, with its own active literature and documented failures — observed size–density
  exponents cluster nearer −0.5 to −0.6 than the predicted −0.75.
- **Box-counting dimension** (Mandelbrot). $N(l) \propto l^{-D}$ is the essay's boxes argument, and
  $d$-as-dimensionality is not an analogy to it; it is it.
- **Scale invariance ⟹ power law** — textbook, and the deepest version of the intuition.
- **Maximum-entropy derivations** — Jaynes; Frank; Visser on Zipf's law and maximum entropy.

Not fatal — synthesis is legitimate — but the honest claim is *"these results are one identity in
different clothes"*, not *"here is a new natural law."* Note also that Damuth cannot simply be
relabelled: it is a species-population relation, whereas orthopolity as stated is community
abundance per log size class. Species richness within size classes introduces another factor.

## 7. Two of three empirical tests failed, and the statistics made it worse

This is the most important entry in this document.

- **Earthquakes:** flat energy occupancy requires $b = \gamma = 1.5$; observed $b = 0.998$
  [0.973, 1.024], robust across thresholds and across two energy conversions. Decisive.
- **Solar flares:** predicted $\alpha = 1.858$, observed 2.239, gap 0.382 [0.125, 0.620], excluding
  zero — and unchanged when the missing-data problem is removed by switching to rise-phase fluence.
- **Ocean:** near-flat over ~15 decades, but $\Phi$ spans a factor of 39 across the full range.

Formal testing then weakened it further ([evidence.md §4](evidence.md)): both failures are confirmed
by equivalence testing at every tolerance examined; the flare distribution is not a power law at all;
and the one positive case is a *post hoc* subrange with no sampling model, which passes at a declared
tolerance factor of 2 and fails at 1.25.

The universal reading is dead. What survives is conditional, exploratory, and a much smaller claim
than the essay makes.

## 8. The statistical terrain is hostile, and the work is not yet done

- **Clauset–Shalizi–Newman (2009)**: least-squares on log-log plots gives wrong exponents and no
  evidence of a power law at all. CSN testing has now been run
  ([evidence.md §4](evidence.md)), and **the flare distribution is ruled out as a power law**
  (p = 0.018).
- **Lognormal is usually indistinguishable** from a power law over realistic ranges — confirmed
  here in both systems tested (p = 0.41 and p = 0.90). No claim of the form "power law rather than
  lognormal" is supportable from these data.
- **Broido & Clauset (2019)**: strong scale-free structure is rare across ~1000 networks. The
  explanandum may be less universal than assumed.
- **Stumpf & Porter**: a power law needs both mechanism and statistical validation; most published
  ones have neither.
- **Curvature is real, not friction.** GAMA stellar mass functions need a double-Schechter form with
  a characteristic mass and exponential cutoff. A resource model must explain that structure rather
  than call it unspecified friction.
- **A flat fitted slope is not flatness.** Demonstrated in this project's own best case
  ([evidence.md §3](evidence.md)).

## 9. The name is a liability

"Orthopolity" parses as *ortho-* (correct) + *polity* (a political community) — it reads as "correct
governance." It carries a political connotation the concept does not have, gives no hint of
equipartition or scale, and will be misremembered. Given that the framework's most attention-grabbing
claim already touches inequality, a name that sounds like a prescription for social organisation
invites exactly the misreading most likely to discredit it.

## 10. Opportunity cost — the honest accounting

**Negative value:**
- The cosmological framing. Unpublishable in physics, with reputational cost that transfers to
  unrelated work.
- More illustrative examples. Roughly half the existing ones are identities carrying no evidential
  weight ([concept.md §11](concept.md)).
- Further conceptual elaboration before the missing statistics exist. The concept is not
  under-elaborated; it is under-tested.

**Moderate value:**
- The reframing and synthesis. Real but bounded — a methods note, not a discovery.

**Highest value:**
- Porting the lab so the results are reproducible, adding CSN and equivalence testing, and running
  one independently sampled test with a preregistered domain.
- Explaining the ocean boundary failures from independently measured covariates. This is the only
  activity that would make orthopolity important rather than merely useful.

The asymmetry is stark: the cheapest and most tempting activities are worth the least.

## 11. Failure modes to guard against

- **Retrofitting the resource.** The moment $\bar q$ is chosen because it flattens the line, the
  result is vacuous.
- **Threshold shopping.** The flare gaps run −0.480, 0.191, 0.382, 0.960 across four lower bounds.
  A free choice of domain produces any conclusion wanted.
- **Reporting that Φ averages to one.** True by construction. Not evidence.
- **Confirmation by illustration.** More systems that "look power-law" add nothing.
- **Explaining every deviation as friction** without an independently predicted form.
- **Escalating the claim to compensate for thin evidence.** The cosmological framing is already an
  instance.

## 12. Kill criteria

Now written against actual results rather than hypotheticals:

1. **If the independently sampled ecological test fails** — that is, if the plateau does not survive
   in data that is not a re-expression of Hatton et al. — then the count stands at three failures and
   zero independent successes. Stop, and publish the negative result.
2. ⚠️ **Partly met already.** CSN testing rules the flare distribution out as a power law
   (p = 0.018), and no tested system distinguishes a power law from a lognormal. Part of the
   explanandum has evaporated. This does not end the programme — the occupancy question is separate
   from the shape question — but any claim that orthopolity *explains observed power laws* must now
   first establish that the power laws are there.
3. **If the ocean boundary failures resist explanation** from independently measured covariates
   across several attempts, accept that orthopolity is an accounting identity with a contingent
   empirical range, and scope every claim down permanently to match.
4. **If every case that works turns out already covered by a named result** — Sheldon spectrum,
   energetic equivalence, box dimension — it is a relabelling. Write a review, cite generously, stop.

Meeting a kill criterion and stopping is a successful outcome. It is information. The failure mode
is meeting one and continuing anyway.
