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

**Natural (orthopolic) distribution.** The project's name for the normalized
neutral inverse-resource profile, $p_\mu(k)=1/[Z\bar q(k)]$, where
$Z=\int_D d\mu/\bar q$ is finite and positive. The physical resource, objects,
domain and reference measure must be independently specified. Power-law costs
give a power-law density relative to $dk$: exponent $d+1$ under log-orthopolic allocation and
$d$ under linear-orthopolic allocation when $\bar q\propto k^d$. Other cost laws
give other profiles. This is a resource-based family, not a new standard name
for every power law or every distribution found in nature. Its occurrence is
a substantive claim to test, not a consequence of naming it natural.

**Normal (Gaussian) distribution.** The bell-shaped density of a Gaussian
random variable, not a sinusoidal relation. A central limit theorem gives one
route to it through centered and scaled sums under specified assumptions;
dependence on many variables alone is insufficient. Normal fluctuations can
coexist with an orthopolic allocation or a power-law mean relation. The term
does not assert that most raw observations in nature are Gaussian. See
supporting S3.9 for the aggregation/allocation distinction and its examples.

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
