# The case for exploring orthopolity

> The honest case. Not the maximal case. See [criticism.md](criticism.md) for the other side —
> the two documents are meant to be read together.

## 1. What is genuinely right

Strip the overclaims and something correct remains:

- **The equipartition reading of power laws is real and underused.** "A power law is what
  equal sharing looks like when you count containers instead of resource" is a true statement
  about a large class of distributions, and most people who work with power laws every day do
  not habitually think in those terms.
- **The inversion is pedagogically excellent.** *Uniform in one accounting = maximally unequal
  in another.* Same system, two ledgers, opposite intuitions. This is a genuinely good teaching
  device and it is not widely deployed.
- **The dimensional reading of $\alpha$ is correct.** $\alpha$ as the dimensionality of the
  resource is right, and identical to box-counting dimension. Correct, if not new.
- **The instinct to demote mechanism-first explanations has merit.** Preferential attachment,
  Yule–Simon, random multiplicative growth, SOC, and optimisation all generate power laws.
  Newman catalogues around eight; Mitzenmacher more. When many unrelated mechanisms converge on
  one form, suspecting that a constraint rather than a mechanism is doing the work is a
  reasonable research instinct. Maximum-entropy treatments (Jaynes; Frank, *The common patterns
  of nature*) took the same instinct somewhere real.

## 2. The one novel testable claim

Everything worth pursuing reduces to this:

> Given a system with distribution $p(k)$, there exists an **independently measurable** resource
> $r(k)$ whose total is equal across classes: $N p(k) r(k) = \text{const}$.

Why this is worth doing:

- **It is not the same test everyone else runs.** The field tests *"is this a power law?"*
  (Clauset–Shalizi–Newman) and *"which mechanism generated it?"*. Almost nobody asks *"what is
  the conserved quantity being equipartitioned, and can I measure it separately?"*
- **It can fail.** Subject to the content condition in [concept.md §5](concept.md), it is a
  real claim with a real way of being wrong.
- **It is a different plot.** Total resource per logarithmic class, checked for flatness, with
  confidence bands. That is a diagnostic the literature does not routinely produce.
- **Success would be informative, and so would failure.** Identifying the equipartitioned
  quantity in a system where nobody had named it is a genuine finding. Showing that no candidate
  resource equipartitions is equally publishable and equally interesting.

## 3. Proof that the programme can work: it already did, once

**Damuth's law / the energetic equivalence rule** is orthopolity, discovered in ecology in 1981
and named in 1991. Population density $N \propto M^{-3/4}$; metabolic rate $B \propto M^{3/4}$;
total energy flux per species is independent of body size. Independently measured resource,
falsifiable equipartition claim, decades of testing, partial failures, an active literature.

This cuts both ways and both ways matter:

- **For the programme:** the method demonstrably produces real science. There is a template
  to copy — and copying it is the fastest route to credibility.
- **Against novelty:** the central idea has been in print for 45 years in another field. See
  [criticism.md §5](criticism.md).

The right move is to treat Damuth as the **positive control**. A framework claiming generality
that cannot reproduce the one case known to work has no business being applied elsewhere.

## 4. The reframing is worth the effort on its own

Even if no new empirical result emerges, the following is a defensible contribution:

- Separating **equipartition (O)** from **scale invariance (S)** as independent ingredients,
  with the exponential counterexample showing they are genuinely independent.
- The **content condition** — that $r$ must be specified independently of $p$ — stated as a
  methodological rule. This is sharper than most of what is said about power-law explanations,
  and it cleanly separates the tautological uses from the substantive ones.
- Recognising **energetic equivalence, box-counting dimension, and Zipf's equal-measure-per-octave
  as one identity** wearing three disciplinary costumes. Cross-field unification is a legitimate
  and citable contribution when done with full attribution.

That is a short methods-and-synthesis paper. It is real, it is honest, and it is achievable.

## 5. Where the interesting empirical work is

Ranked by expected value:

1. **Damuth replication.** Positive control. Known answer, known partial failures. Calibrates
   the diagnostic before it is trusted anywhere else.
2. **Cities.** Zipf's law for cities is solid (Gabaix). Candidate equipartitioned resources:
   total economic output, total energy consumption, total commuting time, total infrastructure
   length per size class. Some of these are measurable from open data.
3. **Expertise and attention.** The essay's speculative "people and knowledge" section is
   actually the most testable thing in it, and it cites no data. Citation counts, chess Elo,
   GitHub contributions, Stack Exchange reputation, streaming play counts. The candidate
   resource — *time invested* — is independently measurable in several of these.
4. **Firm sizes and wealth.** Well-trodden, strong priors, hard to say anything new — but the
   equipartition question ("what is equally shared across wealth decades?") is not the question
   usually asked, and the answer has obvious interest beyond the technical.

## 6. Who would actually care

- **Complex systems / statistical physics** — if framed as a constraint-based account of
  power-law universality with real tests. Physica A, Entropy, Journal of Complex Networks,
  arXiv physics.soc-ph or nlin.AO.
- **Macroecology** — if the framework generalises energetic equivalence beyond metabolism in a
  way that predicts something. This audience is the most likely to engage seriously and the
  most likely to spot errors early, which is a feature.
- **Scientometrics and urban science** — receptive to cross-domain scaling arguments.
- **Teaching** — the uniform/power-law inversion is a good lecture regardless of how the
  research programme resolves.

Nobody in cosmology will care, and pursuing that audience is a net negative. See
[criticism.md §1](criticism.md).

## 7. What a credible version looks like

Milestones, in order. Each is a stopping point where the work has standalone value:

1. **Restate the claim falsifiably.** Separate (O) from (S); state the content condition; fix
   the errata. → A clean position paper. *Done in [concept.md](concept.md).*
2. **Build the equipartition diagnostic.** Total resource per log class, flat-line test,
   bootstrap bands. Alongside full Clauset–Shalizi–Newman fitting — MLE for $\alpha$, KS
   goodness-of-fit, likelihood-ratio tests against lognormal, exponential, stretched exponential.
   Skipping CSN is not an option; it is the price of admission.
3. **Run the positive control** (Damuth). Reproduce a known result, including its known failures.
4. **Test three or four fresh systems**, preregistering the candidate resource *before* fitting.
5. **Publish the negatives.** Systems where no candidate resource equipartitions. This is what
   distinguishes a research programme from a manifesto, and it is the single highest-credibility
   thing the repository can contain.
6. **Attack the friction function.** Derive one deviation from first principles for one system
   and predict its shape. If this works even once, it is the strongest possible result and the
   principle stops being an accounting identity and starts being physics.

Steps 1–3 are perhaps two to four months of part-time work and yield something publishable.
Step 6 is open-ended and may not resolve.
