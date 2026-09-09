# Not worth pursuing

An explicit register of directions judged **not** worth time and energy, with reasons. Two purposes:
to stop the same ideas being re-proposed, and to record what was deliberately left out of this
repository so the omissions are visible rather than silent.

Anything here can be moved back if an argument changes. Nothing here is forbidden — it is
**deprioritised, with the reason stated** so the decision can be revisited on evidence rather than
enthusiasm.

---

## Part A — Deprioritised from the source essay and its framing

### A1. The cosmological-principle framing ❌ *Negative value*
Homogeneity and isotropy are spacetime symmetries; orthopolity is not one. The nearest correct
version — dilation symmetry — is in tension with large-scale homogeneity rather than a companion to
it. Beyond being wrong, it costs the reader before any correct material is reached.
→ [criticism.md §1](criticism.md)

### A2. More illustrative examples ❌
The essay already has more examples than evidence, and roughly half carry no evidential weight:
$f = 1/T$ and $f = v/\lambda$ are definitional identities, the ideal boxes are geometry, and
Stevens' law is a stimulus–response function rather than a distribution over objects. Adding a
tenth confirming illustration adds nothing; one independently sampled test is worth all of them.
→ [concept.md §11](concept.md)

### A3. Stevens' law and the Weber–Fechner connection ❌
Category mismatch. A deterministic response function, not a frequency distribution over containers.
The essay raises the question itself ("or do $I$ and $\Psi(I)$ not relate as quantities in
containers?") and the answer is no. Drop it rather than defend it.

### A4. Further conceptual elaboration before the statistics exist ❌
The concept is not under-elaborated; it is under-tested. No Clauset–Shalizi–Newman goodness-of-fit
testing and no equivalence testing exist anywhere in this project yet. Additional prose cannot
substitute.

### A5. "Friction" as an explanatory category ⚠️ *Only with a predicted form*
An unconstrained correction $\Phi(k)$ reproduces every positive spectrum, so naming the residual
explains nothing. This becomes worthwhile **only** as a specific prediction from independently
measured covariates — for example, whether turnover time or resource supply predicts the sign and
size of the ocean boundary departures. That version is high value ([value.md §5](value.md)); the
general version is not.

### A6. Renaming existing scaling relations ❌
Recognising that the Sheldon spectrum, energetic equivalence and box-counting dimension share an
identity is worth a synthesis paper with full attribution. Presenting that recognition as the
discovery of a new law is not, and will be caught immediately by the ecologists most likely to
find the framework useful.

---

## Part B — Deliberately not imported from the private material

The private assessment and pilot lab contain substantial value, incorporated into
[concept.md](concept.md), [value.md](value.md), [criticism.md](criticism.md) and
[evidence.md](evidence.md). The following were reviewed and **left out on purpose**.

### B1. Sonification of the resource spectrum ⚠️ *Interesting, separate project*
The lab maps $\Phi = 1$ to 440 Hz with one octave per factor of two, clipped to 110–1760 Hz, empty
bins silent, no autoplay. It is carefully built and honestly labelled as an inspection aid with no
evidence that it improves inference.

Left out because it is **orthogonal to whether orthopolity is true**. Establishing that an
audiovisual encoding helps requires its own experiment — visual-only against audio-only against
combined, with known simulated departures, counterbalanced order, accuracy and response time. That
is a legitimate study in audiovisual analytics and a reasonable thing for the author to want to do,
but it is a *different paper with a different literature*, and attaching it to a contested physical
hypothesis weakens both. Pleasantness or consonance are not evidence about a distribution.

### B2. The interactive Matplotlib viewer ⚠️ *Premature*
Sound architectural advice accompanies it — a single analysis representation carrying dataset
identity, unit, scale, resource, selection, model and provenance, with plots and sounds consuming
that same object rather than quietly recomputing a different sample. Worth following **when the
analysis layer is stable**. Building interfaces before then risks the specific failure the advice
warns about: two views silently normalising away a discrepancy.

### B3. A JOSS software paper ❌ *Ineligible*
JOSS expects substantial, used research software with more than six months of public development
history. This repository is days old. Revisit only if the lab becomes genuinely used by others.

### B4. The dark-sector / cosmological-energy speculation ❌ *Negative value*
Would require specified physical degrees of freedom, an action or stress-energy description,
conservation, stable perturbations and quantitative cosmological predictions — with existing stored
field or binding energy not double-counted. $E = \rho V$ yields negative pressure only under
specific thermodynamic and conservation assumptions that cannot be silently omitted. Thermodynamic
approaches to gravity (Jacobson) establish a research context, not support for orthopolity.
This is A1's problem in a more expensive form.

### B5. The structure / information / energy conversion idea ❌
Physical configurations contribute to energy, and information erasure has thermodynamic constraints,
but there is no universal conversion of bits into joules. Landauer's bound concerns irreversible
processing, not a universal energy content of a bit. Retain as a separate speculative interest if
desired; it does not belong in the orthopolity programme.

### B6. The "civilisation is not evil" thesis ❌ *Different discipline, different evidence*
A deviation from a Pareto baseline does not establish that institutions caused more equal
allocation: the baseline, the exponent and the generating processes all require independent
justification, and an impersonal mechanism does not establish a moral verdict in either direction.
A defensible version needs an explicit institutional counterfactual and causal evidence — a
social-science study, not a resource-spectrum result.

This one carries a specific risk worth naming: the framework's most attention-grabbing claim already
touches inequality, and attaching a moral conclusion to it invites the reading most likely to
discredit the technical work. Keep the accounting result and the political interpretation apart.

### B7. Multiplying pilot systems before the statistics exist ⚠️ *Sequencing, not merit*
Three systems have been tested; a fourth adds little while CSN testing, equivalence testing and
preregistration are all still missing. Depth on the existing three — especially the ocean boundary
failures — is worth more than breadth. Reverse this once [value.md §7](value.md) steps 2–3 are done.

---

## Part C — Methodological dead ends

Practices that produce results which look like support but are not:

| Practice | Why it fails |
|---|---|
| Defining the resource from inverse abundance | (O) becomes true by construction. → [concept.md §5](concept.md) |
| Reporting that $\Phi$ averages to 1 | True by construction of the normalisation. → [concept.md §7](concept.md) |
| Testing flatness by fitted slope alone | A wavy spectrum has zero slope. The ocean case: slope −0.039 inside tolerance while $\Phi$ spans 39×. → [evidence.md §3](evidence.md) |
| Treating non-rejection of flatness as support | Requires equivalence testing against a declared tolerance. |
| Choosing the domain after seeing results | Flare gaps run −0.480 to 0.960 across four thresholds. |
| Count × median resource | Objects using 1, 1, 100 total 102; count × median gives 3. Use the sum. |
| OLS on $\log q$ for the conditional mean | Estimates the geometric mean and breaks the accounting identity. Use a Gamma quasi-likelihood. |
| Discarding empty bins, or dropping the final bin edge | Silently manufactures flatness. |
| Treating missing $q$ as zero $q$ | Missingness in the flare data depends on event size. |
| Sharing an exponent label across log-histogram, density, CCDF and rank plots | They differ by one or by inversion. → [concept.md §6](concept.md) |

---

## Summary

The pattern across all three parts: **the cheapest and most appealing activities are worth the
least.** Escalating the framing, adding examples, building interfaces and extending the claim into
cosmology or politics are all easier than porting the lab, adding the missing statistics, and
running one preregistered test on independently sampled data. Only the last group can change what
is known.
