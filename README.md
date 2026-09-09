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
| Earthquakes (USGS, 6,639 events) | $b = 1.5$ | $b = 0.998$ [0.973, 1.024] | **Decisive failure** ‡ |
| Solar flares (NOAA, 10,501 events) | $\alpha = 1.858$ | $\alpha = 2.239$, gap 0.382 [0.125, 0.620] | **Failure** |
| Ocean, upper 200 m | $\Phi$ flat | 21 of 23 bins unresolvable | **Indeterminate** |
| Ocean, full water column | $\Phi$ flat | plateau degrades from 1.7× to 4.3× | **Failure to transfer** |
| **GLOSSAQUA** — 1,300 spectra, 16 studies | NBSS slope −1.000 | **median −1.015**, robust across strata | **Holds in the mean, fails in the particular** |

Formal testing then made the picture *less* favourable, not more:

- Both failures are confirmed by **equivalence testing** at every tolerance examined.
- The flare distribution is **ruled out as a power law** by the Clauset–Shalizi–Newman test
  (p = 0.018), and in no tested system can a power law be distinguished from a **lognormal**
  (p = 0.41, p = 0.90). Part of the explanandum has evaporated.
- ‡ The earthquake catalogue, by contrast, fits Gutenberg–Richter well once tested correctly
  (discrete KS = 0.0077, p = 0.256; the earlier p = 0.000 was an artefact of magnitudes tied to a
  0.1 grid). Its distribution is exactly right and orthopolity fails on it anyway — a clean failure
  of the hypothesis with nothing else to blame.
- The one positive case is a **post hoc** subrange of a re-expression of someone else's
  model-assisted reconstruction, with no sampling model — and its verdict flips with the declared
  tolerance (passes at factor 2, fails at 1.25).

### The one surviving positive result

A **preregistered, blind** test on 1,300 published aquatic size spectra from 16 independent studies
(protocol committed before the analysis ran, commit `6df364f`) returns **not supported** on its
declared criteria — fewer than a quarter of individual spectra fall within tolerance even at the
loose setting.

But the median normalized-biomass-spectrum slope is **−1.015 where orthopolity predicts −1.000**,
a systematic drift of only 1.11× across three decades of body mass, with the median of per-study
medians at −1.005.

That centre then survived a deliberate attempt to kill it ([docs/evidence.md §6](docs/evidence.md)):

- **Not a reporting artefact.** There is a generic round-number preference in the literature, but
  −1.00 ranks only 3rd of 17 round values in local excess. No anchoring on the predicted value.
- **Not an attractor either.** I² = 88.4%, τ = 0.25 — individual systems genuinely differ, and the
  dispersion is real between-system variation rather than measurement error.
- **Robust across strata.** Freshwater −1.010 and marine −1.060; fish, macroinvertebrates and
  zooplankton separately. Every stratum with a valid interval is consistent with −1.

> **Orthopolity is a statement about the *expected value* of aquatic resource spectra.** It is real,
> independently reproducible, and violated by most individual systems. That is testable, modest and
> defensible — and it is a different claim from a natural law, let alone a cosmological principle.

### The claim predicts its own failure rate

Formalised as **(O-ensemble)** in [concept.md §3.1](docs/concept.md): across systems in a class,
the departure has E[s] = 0 and Var[s] = τ², with τ a property of the class.

That is not a retreat, because it forbids things. Given τ, it *predicts* how many individual
systems must fail a tolerance test — and the fitted τ = 0.255 reproduces the observed rate almost
exactly:

| Tolerance | Predicted pass rate | Observed | Ratio |
|---|---:|---:|---:|
| F = 1.25 | 0.080 | **0.078** | 0.99 |
| F = 2.00 | 0.237 | **0.238** | 1.01 |

So the median landing on −1 while only 7.8% of systems pass individually is not a hypothesis
half-working — it is one dispersion parameter doing both jobs. *(An internal consistency check, not
out-of-sample: τ is fitted to the same slopes. The out-of-sample test is the replication
prohibition.)*

**What it forbids:** an independent aquatic dataset must reproduce τ ≈ 0.257; two resources
satisfying (O) on the same systems must have equal dispersion and perfectly correlated departures;
and any dataset's pass rate must match its own fitted τ.

**And the one place it looked strained has resolved.** The pooled latent distribution is
heavier-tailed than the two-moment maximum-entropy form — but that is a pooling artefact. Fitting
strata separately, **freshwater alone is adequately Gaussian** (excess kurtosis −0.34), and a
two-component mixture built from the fitted habitat parameters reproduces 82% of the pooled excess
kurtosis. τ is confirmed as a *class* property: **0.228 freshwater against 0.383 marine**, which
sharpens the replication prohibition from one universal number to class-specific ones.

Details, caveats and provenance: [docs/evidence.md](docs/evidence.md).

## Reproduce

```bash
make install   # editable install, so `import gof` works without PYTHONPATH
make all       # verify checksums, run 49 tests, run every analysis
```

Or individually: `make data` (verify raw inputs), `make test`, `make pilot`, `make gof`,
`make independent`, `make ensemble`. Analyses read only from the checksummed `data/raw/` and never
fetch.

Raw snapshots are frozen and checksummed; `fetch_data.py` fails loudly rather than silently
replacing them if a remote source has changed. The pipeline reproduces every number above to
floating-point noise.

## What is in here

| Document | Contents |
|---|---|
| [docs/concept.md](docs/concept.md) | The concept restated precisely: formal setup, the (O)/(S) separation, the content condition, exponent conversions, the stock/flux distinction, and what fails to derive it. |
| [docs/evidence.md](docs/evidence.md) | What has actually been tested and what happened. Two failures, one qualified success, and what is still missing. |
| [docs/value.md](docs/value.md) | The case for pursuing it, the statistical requirements, and a staged plan. |
| [docs/criticism.md](docs/criticism.md) | The case against: category error, circularity, prior art, the failed tests, opportunity cost, and kill criteria. |
| [docs/not-worth-pursuing.md](docs/not-worth-pursuing.md) | Explicit register of deprioritised directions, with reasons — including what was deliberately left out. |
| [docs/roadmap.md](docs/roadmap.md) | Open work in priority order, with completed items and their commits. |
| [docs/references.md](docs/references.md) | Bibliography grouped by role in the argument. |

| Code and data | Purpose |
|---|---|
| [src/orthopolity.py](src/orthopolity.py) | Resource-spectrum accounting, bounded power-law MLE, conditional-mean estimator. No automatic range selection, no universal-law classification. |
| [tests/](tests/) | Eight checks: resource conservation, arithmetic-vs-median accounting, unit invariance, weighting, missingness, bin endpoints, known scaling, audio bounds. |
| [experiments/](experiments/) | `fetch_data.py` (checksummed retrieval), `run_pilot.py` (the three analyses). |
| [configs/pilot.json](configs/pilot.json) | Declared domains, resources, time splits, block schemes and limitations — fixed before analysis. |
| [data/](data/) | Frozen raw snapshots, provenance ([SOURCES.md](data/SOURCES.md)) and third-party rights ([NOTICE.md](data/NOTICE.md)). |
| [results/](results/) | Machine-readable estimates, bin totals, bootstrap draws, figures. |
| [tools/explore.py](tools/explore.py) | Interactive inspection aid. Deliberately outside `experiments/` — no result depends on it. |

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

1. ~~Port the pilot lab here so the results above are reproducible by others.~~ ✅ Done.
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

[docs/not-worth-pursuing.md](docs/not-worth-pursuing.md) records what was deliberately *excluded*
and why, so the omissions are visible rather than silent.
