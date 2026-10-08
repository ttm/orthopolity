# Glossary

## Orthopolity

**Etymology.** A coined word: *ortho-* + *pol-* + *-ity*.

- *Ortho-*, from Greek *orthós* (ὀρθός): straight, right, upright. In *orthogonal* it contributes
  the notion of a right angle.
- *Pol-*, from Greek *pólos* (πόλος): pivot, axis, pole; through Latin *polus* into English *pole*.
- *-ity*: an English suffix for a state, condition or quality, as in *polarity*, *regularity*,
  *uniformity*.

Read together: approximately, *the condition or property of orthogonal poles*.

**Meaning in this project.** A resource is allocated equally across classes of objects, with
respect to a declared reference measure, so that classes whose objects hold or require more of
the resource contain fewer objects. Formally, with object size $k$, mean resource per object
$\bar q(k)$, and abundance $n_\mu=dN/d\mu$:

$$\mathcal O_\mu(k)=\bar q(k)\,n_\mu(k)=C .$$

## Word forms

| Form | Use |
|---|---|
| **orthopolity** | the noun: the condition, the hypothesis, or the framework |
| **orthopolic** | the adjective: an orthopolic system, an orthopolic resource |
| **orthopolically** | the adverb: a resource allocated orthopolically |

*Orthopolitic* is not a form of the word. Do not use it.

## Related terms

**Reference measure.** What "equal" is counted against. It must be stated, because it changes
the predicted exponent.

| Term | Equal resource per | With $\bar q\propto k^d$, abundance density $dN/dk\propto$ |
|---|---|---|
| **log-orthopolic** | logarithmic size interval, $d\ln k$ | $k^{-(d+1)}$ |
| **linear-orthopolic** | linear size interval, $dk$ | $k^{-d}$ |
| **discretely orthopolic** | predefined class | class count $\propto 1/\bar q_j$ |

**Orthopolic resource.** For an observed density $dN/dk\propto k^{-\alpha}$, the resource
$q\propto k^d$ that makes the system orthopolic. Its **resource exponent** is $d=\alpha-1$ under
the logarithmic measure and $d=\alpha$ under the linear measure. Example: $p(k)\propto k^{-3}$ is
linear-orthopolic in a resource scaling as $k^3$ (a volume, if $k$ is a length) and
log-orthopolic in a resource scaling as $k^2$ (an area).

**Final resource.** A resource built from simpler ones, for example a product of independent
inputs whose deterministic cost exponents add: $q=q_1q_2$ with $q_i\propto k^{d_i}$ gives
$d=d_1+d_2$. This holds for deterministic cost laws, not for products of independent random
variables, whose tails do not simply add (see [concept.md](concept.md)).

**Survival exponent $\zeta$.** For $P(Q>q)\propto q^{-\zeta}$ in the resource itself; a system
that is log-orthopolic in its own coordinate has $\zeta=1$, Zipf's law.
