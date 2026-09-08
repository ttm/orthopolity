# orthopolity

A critical working repository for **orthopolity**: the proposal that a conserved resource is
shared equally across size classes of the containers holding it, so that containers holding more
of it are proportionally rarer — and that this generates the power-law distributions seen
throughout nature.

Source essay: [The Orthopolity cosmological principle and the Natural distribution
law](https://ttm.github.io/2024/08/14/power.html) (R. Fabbri, 2024).

## The claim, stated so it can be attacked

$$N \cdot p(k) \cdot r(k) = C \qquad \text{for all classes } k$$

where $p(k)$ is the fraction of units holding resource amount $r(k)$. Equivalently
$p \propto 1/r$.

Two things follow that the source essay does not separate, and both matter:

- **Orthopolity alone does not produce a power law.** It gives $p \propto 1/r$ for any $r$
  whatsoever. The power law requires a second, independent assumption — that $r$ scales as a
  power of the class label. That assumption supplies the exponent.
- **Orthopolity is empirically empty unless $r$ is measured independently of $p$.** For any
  distribution, setting $r := C/(Np)$ satisfies it by construction. The entire research
  programme lives in specifying $r$ beforehand.

## What is in here

| Document | Contents |
|---|---|
| [docs/concept.md](docs/concept.md) | The concept restated precisely: formal setup, what is assumed vs. derived, the measure ambiguity, which of the essay's examples carry evidential weight, and errata in the source. |
| [docs/value.md](docs/value.md) | The honest case for pursuing it: what is genuinely right, the one novel testable claim, the precedent that the method works, and a staged research plan. |
| [docs/criticism.md](docs/criticism.md) | The case against: the cosmological-principle category error, the circularity, the unfalsifiability, 45 years of prior art, the statistical terrain — plus opportunity cost and explicit kill criteria. |
| [docs/references.md](docs/references.md) | Bibliography, grouped by the role each work plays in the argument. |

No code yet. The documentation comes first deliberately: the concept needs to be falsifiable
before anything is measured, or the measurements cannot mean anything.

## Summary of the assessment

**In favour.** The equipartition reading of power laws is correct and underused. *Uniform in one
accounting equals maximally unequal in another* is a genuinely good and underdeployed way to see
these distributions. There is one novel, falsifiable question here that the field does not
routinely ask: *what is the conserved quantity being equipartitioned, and can it be measured
separately?* And there is proof the method works — Damuth's energetic equivalence rule is exactly
this, and it produced decades of real ecology.

**Against.** It is not a cosmological principle; homogeneity and isotropy are spacetime
symmetries and this is not one, and the nearest correct version — dilation symmetry — is in
tension with homogeneity rather than a companion to it. The central derivation is an identity
read in two directions. The power law does not follow from the principle alone. As stated, with
deviations attributed to unmodelled "friction", nothing can disconfirm it. And the core idea has
been in print since 1981 under a different name in another field.

**Net.** Worth pursuing as an equipartition identity unifying results across fields, plus a new
diagnostic — not as a new law of nature, and not as cosmology. The cheapest activities here
(more examples, more conceptual prose, escalating the framing) are worth the least. The expensive
one — a single rigorous empirical test with an independently specified resource, statistically
validated, negative results included — is worth nearly everything.

## Next steps

1. Build the equipartition diagnostic: total resource per logarithmic class, tested for flatness
   with bootstrap bands — alongside full Clauset–Shalizi–Newman power-law fitting.
2. Run Damuth's law as a positive control, reproducing its known failures as well as its successes.
3. Test three or four further systems with the candidate resource **preregistered** before fitting.
4. Publish the negative results.

Detailed in [docs/value.md §7](docs/value.md).

## A note on these documents

They are written as an adversarial assessment — the strongest honest version of both the case for
the idea and the case against it, including the argument that the time would be better spent
elsewhere. They are meant to be stress-testing, not advocacy. Where they disagree with the source
essay, the disagreement is stated explicitly rather than smoothed over.
