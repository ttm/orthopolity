# orthopolity

A critical working repository for **orthopolity**: the hypothesis that an additive resource occupies
each logarithmic size class equally, so that objects costing more of it are proportionally rarer —
and that this generates the power-law distributions seen throughout nature.

Source essay: [The Orthopolity cosmological principle and the Natural distribution
law](https://ttm.github.io/2024/08/14/power.html) (R. Fabbri, 2024).

## The claim, stated so it can be attacked

$$\mathcal{O}(k) \;=\; \bar q(k)\,\frac{dN}{d\ln k} \;=\; C \qquad \text{on a declared domain } [k_{\min}, k_{\max}]$$

where $\bar q(k) = E[q \mid k]$ is the conditional **arithmetic** mean resource at scale $k$.

Three things follow that the source essay does not separate, and all three matter:

- **Orthopolity alone does not produce a power law.** It gives $dN/d\ln k \propto 1/\bar q$ for any
  $\bar q$ whatsoever. The power law needs a second, independent assumption — a scale-free cost
  $\bar q \propto k^{d}$ — and that assumption supplies the exponent. With $\bar q = e^k$ the
  hypothesis holds exactly and yields an exponential.
- **Orthopolity is empirically empty unless $\bar q$ is measured independently of abundance.** For
  any distribution, setting $\bar q := C/(dN/d\ln k)$ satisfies it by construction. The entire
  research programme lives in specifying the resource beforehand.
- **Nothing derives it.** Conservation fixes an integral, not its spread across scales; scale
  covariance gives a power function but not a flat spectrum; maximum entropy with a fixed additive
  mean gives an *exponential*. Orthopolity is a conjecture, not a consequence.

## Empirical status

Three systems tested. **Two clear failures, one qualified success.**

| System | Prediction | Observation | Verdict |
|---|---|---|---|
| Earthquakes (USGS, 6,639 events) | $b = 1.5$ | $b = 0.998$ [0.973, 1.024] | **Decisive failure** |
| Solar flares (NOAA, 10,501 events) | $\alpha = 1.858$ | $\alpha = 2.239$, gap 0.382 [0.125, 0.620] | **Failure** |
| Ocean size spectrum (23 log-mass bins) | $\Phi$ flat | flat over ~15 decades, fails at both ends | **Qualified success** |

The universal reading is dead. What survives is conditional — and the ocean result is genuinely
interesting: $\Phi$ stays within a factor of 1.7 across fifteen decades of body mass before breaking
down at the bacterial and whale ends. That is a **quantified domain of validity**, which is the
shape of result worth publishing.

Details, caveats and provenance: [docs/evidence.md](docs/evidence.md).

## What is in here

| Document | Contents |
|---|---|
| [docs/concept.md](docs/concept.md) | The concept restated precisely: formal setup, the (O)/(S) separation, the content condition, exponent conversions, the stock/flux distinction, and what fails to derive it. |
| [docs/evidence.md](docs/evidence.md) | What has actually been tested and what happened. Two failures, one qualified success, and what is still missing. |
| [docs/value.md](docs/value.md) | The case for pursuing it, the statistical requirements, and a staged plan. |
| [docs/criticism.md](docs/criticism.md) | The case against: category error, circularity, prior art, the failed tests, opportunity cost, and kill criteria. |
| [docs/not-worth-pursuing.md](docs/not-worth-pursuing.md) | Explicit register of deprioritised directions, with reasons — including what was deliberately left out. |
| [docs/references.md](docs/references.md) | Bibliography grouped by role in the argument. |

No code in this repository yet. A pilot lab exists privately; porting it is the next step.

## Summary of the assessment

**In favour.** The equipartition reading of power laws is correct and underused. There is one novel,
falsifiable question the field does not routinely ask: *what is the conserved quantity being
equipartitioned, and can it be measured separately?* The two-resource constraint gives the framework
genuine forbidding power. And the ocean spectrum shows the hypothesis holding across fifteen decades
before failing — a real result about a real boundary.

**Against.** It is not a cosmological principle. The central derivation is an identity read in two
directions. The power law does not follow from the principle alone, and nothing more basic implies
the principle. The closest prior work — the Sheldon spectrum (Hatton et al. 2021) — is 2021, is
absent from the essay, and already has a mechanistic model attached (Cuesta–Delius–Law 2018). Two of
three empirical tests failed.

**Net.** Worth pursuing as a **conditional** hypothesis about where equal-resource spectra occur and
where they break — not as a universal law, and not as cosmology. The research question that fits the
evidence: *under what independently specified conditions does an additive resource have approximately
equal occupancy across logarithmic size intervals?*

## Next steps

1. Port the pilot lab here so the results above are reproducible by others.
2. Add the missing statistics: full Clauset–Shalizi–Newman goodness-of-fit testing, and equivalence
   testing against a declared tolerance. **Neither exists yet**; nothing is confirmatory until they do.
3. Run one independently sampled ecological test with the domain and resource fixed in advance,
   keeping earthquakes as a known negative control.
4. Attack the ocean boundary failures — predict their sign and size from independently measured
   covariates. This is the only step that would make orthopolity important rather than merely useful.

Detailed in [docs/value.md §7](docs/value.md).

## A note on these documents

They are an adversarial assessment: the strongest honest version of both the case for the idea and
the case against it, including the argument that time would be better spent elsewhere. Where they
disagree with the source essay, the disagreement is stated explicitly rather than smoothed over.
