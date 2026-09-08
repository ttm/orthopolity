# The case against orthopolity — and against spending time on it

> The strongest honest version of the objections, including the opportunity-cost argument.
> Read with [value.md](value.md). If the objections in §1–§4 are not answered, the rest of the
> programme does not get off the ground.

## 1. It is not a cosmological principle (fatal to the current framing)

Homogeneity and isotropy are **spacetime symmetries** — invariance of the metric under
translation and under rotation. They are what force the FLRW metric, and they are tested against
CMB anisotropy and galaxy redshift surveys. They are statements about the geometry of the
universe.

Orthopolity is a statistical statement about how a conserved quantity partitions among
containers. It is a different kind of object entirely. Calling it "a third cosmological
principle, together with Isotropy and Homogeneity" is a category error, and it is the first
sentence of the abstract.

Worse, the nearest correct version **contradicts** the framing. The genuine third symmetry is
dilation, and exact scale invariance is *in tension with* large-scale homogeneity — that is
precisely the historical fractal-universe debate (Pietronero, Sylos Labini) against the measured
transition to homogeneity at roughly 70–100 Mpc/h. Scale invariance and homogeneity cannot both
hold at all scales. So orthopolity cannot be a companion principle to homogeneity; at cosmological
scales it is a rival to it, and one that lost.

**Cost of keeping the framing:** a physicist stops reading at the abstract. Everything downstream
— including the parts that are correct — is discarded with it. This single framing choice
probably costs more than every other problem in this document combined.

## 2. The central derivation is an identity presented as a discovery

$N p(k) r(k) = C$ and $p(k) \propto 1/r(k)$ are the same equation. The essay states the first as
its concluding "most impressive consequence" and the second as its opening postulate, with the
examples in between, creating the impression that one was derived from the other. Nothing was
derived. A referee will see this immediately, and finding a circularity at the core is
disproportionately damaging to how everything else is read.

## 3. The power law does not follow from the principle

Shown in [concept.md §4](concept.md): (O) gives $p \propto 1/r$ for *any* $r$. With $r(k) = e^k$,
orthopolity holds exactly and produces an exponential distribution.

So the headline claim — orthopolity ⟹ the "Natural distribution law" — is false as written. The
power law needs scale-invariant labelling as a separate assumption, and that assumption is
carrying the exponent. Once separated, the honest description of the remaining contribution
shrinks considerably: the power law comes from scale invariance, which is standard, and
orthopolity contributes the equipartition reading.

## 4. As stated, it is unfalsifiable

Postulate 2 says deviations "are the result of other natural laws," illustrated by an apple that
stays stuck in the tree while gravity still acts. That analogy is doing exactly the wrong work:
it explains in advance why no observation can count against the principle.

Combined with the content condition ([concept.md §5](concept.md)) — that (O) can be made true by
definition for any distribution by choosing $r := C/(Np)$ — the current formulation has **no
empirical content at all**. Any distribution is orthopolity plus unmeasured friction. "Friction"
names the residual; it does not model it.

This is the objection that must be answered first, and it is answerable: specify $r$
independently, before fitting. But until that is done in a concrete system, there is nothing
to defend.

## 5. Substantial prior art, unacknowledged

The word "orthopolity" appears nowhere in the literature. The content appears repeatedly:

- **Energetic equivalence rule** (Damuth 1981; named by Nee et al. 1991). Constant total energy
  per size class. This *is* orthopolity, in ecology, 45 years old, with an active literature
  including its own paradoxes and failures — observed size–density exponents cluster around
  −0.5 to −0.6 rather than the predicted −0.75.
- **Box-counting dimension** (Mandelbrot). $N(l) \propto l^{-D}$ is the essay's boxes argument
  and the definition of fractal dimension. The $\alpha$-as-dimensionality reading is not an
  analogy to it; it is it.
- **Scale invariance ⟹ power law.** The unique-solution argument for $f(ax) = g(a)f(x)$ is
  textbook, and it is the deepest version of the essay's intuition.
- **Maximum-entropy derivations.** Power laws from a constraint on $\langle \ln x \rangle$;
  see Frank's *The common patterns of nature* and the maxent-plus-symmetry literature.
- **Equal measure per octave** in Zipf's law has been observed for decades.

Not fatal — synthesis is legitimate — but it means the honest claim is *"these four known
results are one identity in different clothes"*, not *"here is a new natural law."* Publishing
the latter when the former is true is the fastest way to lose the referees who know the ecology
literature, and they are the same people most likely to find the framework useful.

## 6. The statistical terrain is hostile, and the essay is not equipped for it

Power-law claims are held to an unusually high standard, for good reason:

- **Clauset–Shalizi–Newman (2009)** showed that least-squares fits to log-log plots give
  substantially wrong exponents and, worse, give no evidence the data is a power law at all.
  The essay's evidence is straight lines on log-log axes. That is precisely the discredited
  method.
- **Lognormal is usually indistinguishable** from a power law over realistic ranges — often
  fitting better. Mitzenmacher's history of generative models is largely about how easily these
  are confused.
- **Broido & Clauset (2019), "Scale-free networks are rare"** found that across ~1000 networks,
  strong scale-free structure is uncommon. If the phenomenon being explained is less universal
  than assumed, a universality-claiming framework is explaining something that partly is not there.
- **Stumpf & Porter, "Critical truths about power laws"**: a power law needs both a mechanism
  and statistical validation, and most published ones have neither.

None of this sinks the idea, but it does mean every empirical claim costs real work. There is no
cheap path.

## 7. The name is a liability

"Orthopolity" parses as *ortho-* (straight, correct) + *polity* (a political community or form of
government) — it reads as "correct governance." It carries a political connotation the concept
does not have, gives no hint of equipartition or scale, and will be misremembered. Given that the
framework's most attention-grabbing claim already touches inequality, a name that sounds like a
prescription for how society should be organised invites exactly the misreading most likely to
discredit it.

## 8. Opportunity cost — the honest accounting

The question was whether this is worth time and energy. A direct answer:

**Low expected value:**
- Pursuing the cosmological framing. Unpublishable in physics, and a reputational cost that
  transfers to unrelated work. Strictly negative.
- Adding more illustrative examples. The essay already has more examples than evidence, and
  roughly half of them are identities carrying no weight ([concept.md §8](concept.md)).
- Further conceptual elaboration before any empirical test. The concept is not
  under-elaborated; it is under-tested. More prose does not fix that.

**Moderate expected value:**
- The reframing and synthesis paper. Real but bounded — this is a methods note, not a discovery,
  and it should be written as one.

**Highest expected value:**
- One rigorous empirical test with an independently specified resource, CSN-validated, published
  with its negative results. This is the only activity that can convert the idea from an
  interesting reading into a finding.

The asymmetry is stark: the cheapest and most tempting activities are worth the least. The
expensive one is worth nearly everything. If time is limited, doing only step 3 of
[value.md §7](value.md) and skipping the rest is a better use of it than the reverse.

## 9. Failure modes to guard against

- **Confirmation by illustration.** Collecting more systems that "look power-law" adds no
  evidence. Only independently specified resources do.
- **Retrofitting $r$.** The moment $r$ is chosen because it makes the line flat, the result is
  vacuous. Preregister the candidate resource.
- **Explaining away every deviation as friction.** Without a friction model derived from
  something, this is unfalsifiability by another name.
- **Escalating the claim to compensate for thin evidence.** The cosmological framing is already
  an instance of this pattern.

## 10. Kill criteria — when to stop

Stated in advance, because a research programme without them becomes unfalsifiable in practice
even if its claims are falsifiable in principle:

1. **If, across five or six systems, no independently specified resource equipartitions better
   than chance** — the principle has no content beyond the tautology. Stop.
2. **If every case that works turns out to be already covered by a named existing result**
   (energetic equivalence, box dimension, Zipf's equal measure) — it is a relabelling. Write a
   review, cite generously, stop.
3. **If CSN testing shows the target distributions are not power laws** in the first place —
   the explanandum has partly evaporated. Reassess what is left to explain.
4. **If the friction function resists first-principles derivation across several attempts** —
   accept that orthopolity is an accounting identity, not physics, and scope the claims down
   permanently to match.

Meeting a kill criterion and stopping is a successful outcome. It is information. The failure
mode is meeting one and continuing anyway.
