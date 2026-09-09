# The case for exploring orthopolity

> The honest case, revised after empirical testing. Read with [criticism.md](criticism.md) and
> [evidence.md](evidence.md).

## 1. What is genuinely right

Strip the overclaims and something correct remains:

- **The equipartition reading of power laws is real and underused.** "A power law is what equal
  sharing looks like when you count objects instead of resource" is true of a large class of
  distributions, and most people who work with power laws do not habitually think in those terms.
- **The inversion is pedagogically excellent.** *Uniform in one accounting = maximally unequal in
  another.* Same system, two ledgers, opposite intuitions.
- **The dimensional reading of the exponent is correct.** $d$ as the dimensionality of the
  resource is right, and identical to box-counting dimension.
- **The instinct to demote mechanism-first explanations has merit.** Preferential attachment,
  Yule–Simon, multiplicative growth, SOC and optimisation all generate power laws; Newman
  catalogues around eight, Mitzenmacher more. When many unrelated mechanisms converge on one form,
  suspecting a constraint rather than a mechanism is a reasonable instinct. Maximum-entropy
  treatments (Jaynes; Frank) took the same instinct somewhere real.

## 2. The one novel testable claim

Everything worth pursuing reduces to:

> Given a system, there exists an **independently measurable** resource whose total is equal across
> logarithmic size classes: $\bar q(k)\,dN/d\ln k = \text{const}$.

Why it is worth doing:

- **It is not the test everyone else runs.** The field asks *"is this a power law?"* (Clauset–
  Shalizi–Newman) and *"which mechanism generated it?"*. Almost nobody asks *"what is the conserved
  quantity being equipartitioned, and can I measure it separately?"*
- **It can fail, and it has.** Two of three systems tested failed outright; see
  [evidence.md](evidence.md). A framework that only ever confirms is worthless; this one does not.
- **It is a different plot.** Resource per logarithmic class with uncertainty, tested for flatness
  *and* bounded departure. The literature does not routinely produce it.
- **The two-resource constraint gives it teeth.** Resources with different scaling exponents cannot
  both be orthopolar over the same domain ([concept.md §10](concept.md)). So the framework forbids
  things, which is the minimum requirement for a scientific claim.

## 3. The reframed question — and why it is now the right one

> **Under what independently specified conditions does an additive resource have approximately
> equal occupancy across logarithmic size intervals?**

The empirical results make this the only sensible framing. Orthopolity is not universal — the
earthquake test rules that out cleanly. But the ocean spectrum is near-flat across fifteen decades
before failing at both boundaries. The interesting object is therefore **the boundary of validity**,
not the principle.

A working title that matches the evidence: **"Resource allocation across scale: tests of
equal-resource spectra."** Orthopolity can remain the name of the hypothesis, with credit to earlier
formulations and explicit separation of established results from proposed extensions.

## 4. Statistical requirements — non-negotiable

These are the price of admission, and skipping any of them invalidates the result:

1. **Full Clauset–Shalizi–Newman treatment.** ✅ *Implemented* in [`src/gof.py`](../src/gof.py) —
   MLE, KS goodness-of-fit, parametric bootstrap $p$-values, and Vuong likelihood-ratio tests
   against truncated lognormal, exponential and stretched exponential. Note the deliberate
   departure from standard practice: the lower bound is **declared, never fitted**, because
   selecting $x_{\min}$ by minimising KS is the same threshold shopping the protocol forbids.
2. **Equivalence testing against a declared tolerance.** ✅ *Implemented.* *Failure to reject
   flatness is not support for flatness.* Declare in advance the tolerable resource drift — for illustration, no more than
   a factor 1.25 across two decades implies $|s| \leq \ln(1.25)/\ln(100) \approx 0.0485$ — and
   require the interval to sit entirely inside it. The tolerance is a design choice, not a natural
   constant.
3. **A bounded-departure criterion alongside the slope.** A wavy spectrum can have zero fitted
   slope. The ocean result demonstrates this concretely: slope −0.039, inside tolerance, while
   $\Phi$ spans a factor of 39 ([evidence.md §3](evidence.md)). Report $\max|\ln\Phi|$ or a
   curvature bound as well.
4. **Correct accounting.** Sum the resource (equivalently, count × *arithmetic* mean, never median);
   retain empty bins; include the final bin edge; treat missing $q$ as missing, not zero; and
   distinguish "no event observed" from "no observation effort".
5. **Dependence-aware bootstrap.** Blocks should follow real structure — observing periods, active
   regions, geographic units, independent communities.
6. **Preregister the domain and resource.** The flare threshold sensitivity — gaps of −0.480, 0.191,
   0.382, 0.960 across four thresholds — shows that a free choice of domain can produce any answer
   wanted.

## 5. Where the interesting empirical work is

Ranked by expected value, revised in light of results:

1. **An independently sampled ecological test.** Now clearly the highest priority: the strongest
   existing evidence is a *post hoc* subrange of a re-expression of someone else's model-assisted
   reconstruction, with no sampling model and a verdict that flips with the declared tolerance. It
   cannot confirm anything on its own. The Pelagic Size Structure database (Dugenne et
   al. 2024) and GLOSSAQUA (Ersoy et al. 2025) offer comparisons across places, instruments and
   ecosystems. This is the highest-value single step available.
2. **Characterise the ocean boundary failures.** Why Φ ≈ 2.5 at the bacterial end and 0.07 at the
   whale end? If turnover time, resource supply or boundary conditions predict the sign and size of
   those departures, "friction" stops being a euphemism and becomes a model. This is the most
   direct route to a real contribution.
3. **Explain the earthquake failure conditionally.** $b \approx 1$ against a required 1.5 is a
   large, stable discrepancy. A theory that predicts *which* systems fail, established independently
   of this failure, would be worth more than another success.
4. **Expertise and attention.** The essay's most speculative section is its most testable, and it
   cites no data. Citation counts, chess Elo, repository contributions, reputation scores — with
   *time invested* as an independently measurable candidate resource.

## 6. Who would actually care

- **Complex systems / statistical physics** — Physical Review E for a substantive contribution;
  arXiv physics.soc-ph or nlin.AO.
- **Macroecology** — most likely to engage seriously, most likely to find errors early, and where
  the strongest result already lives.
- **PLOS ONE** — a plausible route for technically sound empirical work including negative results.
- **Teaching** — the uniform/power-law inversion is a good lecture regardless of outcome.

Nobody in cosmology will care. A software paper is premature: JOSS expects substantial, used
research software with more than six months of public development history, which this repository
does not have.

## 7. What a credible version looks like

Each milestone is a stopping point with standalone value:

1. **Restate the claim falsifiably.** ✅ *Done — [concept.md](concept.md).*
2. **Port the pilot lab into this repository.** ✅ *Done* — accounting functions, estimators, unit
   tests, checksummed raw snapshots and all outputs are here and reproduce offline. See
   [evidence.md](evidence.md).
3. **Add the missing statistics.** ✅ *Done* — see [evidence.md §4](evidence.md). The results were
   unfavourable: two occupancy failures confirmed at every tolerance, the flare distribution ruled
   out as a power law, and lognormal indistinguishable everywhere.
4. **Run an independently sampled positive candidate** with the domain and resource fixed in
   advance, retaining a known negative control (earthquakes).
5. **Publish the failures alongside the successes.** Two already exist. This is what distinguishes
   a research programme from a manifesto.
6. **Attack the boundary failures.** Predict the form or parameters of the departure from
   independently measured covariates. If this works even once, orthopolity stops being an accounting
   identity and starts being physics.

Steps 2–4 are perhaps four to six weeks of focused work and yield something publishable. Step 6 is
open-ended and may not resolve — but it is the only one that would make the concept important
rather than merely useful.
