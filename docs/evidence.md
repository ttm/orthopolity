# Empirical status

What has actually been tested, and what happened. Three systems have been examined so far. **Two
are clear failures, one is a qualified success with a well-defined domain of validity.**

> **Provenance and reproduction.** These results originate in an independent assessment
> commissioned by the author. **The analysis code, raw data snapshots and outputs are now in this
> repository** and reproduce offline:
>
> ```bash
> python -m pip install -r requirements.txt
> python experiments/fetch_data.py                      # verifies SHA-256 of every raw input
> PYTHONPATH=src python -m unittest discover -s tests -v # 8 accounting/estimator checks
> python experiments/run_pilot.py                       # regenerates results/
> ```
>
> Verified: the pipeline reproduces every number below from the frozen snapshots, agreeing to
> floating-point noise (~1e-15 relative). Recorded environment: Python 3.12.14, numpy 2.3.5,
> pandas 2.2.3, scipy 1.17.0, matplotlib 3.10.8.
>
> Numbers are exploratory percentile bootstrap intervals (600 resamples, seed 20260908),
> conditional on the stated catalogues, preprocessing, working models and block schemes. They do
> **not** cover measurement, selection, completeness or energy-conversion bias.

## Summary

| System | Resource | Prediction | Observation | Verdict |
|---|---|---|---|---|
| Earthquakes (USGS) | magnitude-derived energy proxy | $b = 1.5$ | $b = 0.998$ [0.973, 1.024] | **Decisive failure** |
| Solar flares (NOAA) | integrated soft-X-ray fluence | $\alpha = 1.858$ [1.697, 2.054] | $\alpha = 2.239$ [2.085, 2.399] | **Failure**, gap 0.382 [0.125, 0.620] |
| Ocean size spectrum | body mass (biomass) | $\Phi$ flat | flat over ~15 decades, fails at both ends | **Qualified success** |

## 1. Earthquakes — decisive failure

7,174 USGS events 2010–2024 at $M_w \geq 5.5$; 6,639 after restricting to moment-magnitude families.

With Gutenberg–Richter $N(\geq M) \propto 10^{-bM}$ and energy proxy $E \propto 10^{\gamma M_w}$:

$$\mathcal{O}(E) \propto E^{\,1 - b/\gamma}$$

Flat energy occupancy therefore **requires $b = \gamma$**. With $\gamma = 1.5$, that means $b = 1.5$.
The fitted value is $b = 0.998$, year-block interval [0.973, 1.024]. Thresholds of 6.0 and 6.5 give
0.984 and 0.977. Robust to the alternative USGS conversion $\gamma = 1.44$.

This is not a marginal miss. The observed $b$ is nowhere near the required value, and the
requirement follows from arithmetic rather than from a fitted model.

**Caveats that limit — but do not rescue — the result.** Moment magnitude and radiated-energy
magnitude measure different physical properties; event-specific radiative efficiency matters; there
is no declustering or regional completeness model. So this is a failure of *the magnitude-derived
energy-proxy version* of the hypothesis, not of an independently measured energy test. A fitted
$b \approx 1$ is still not evidence for a requirement of 1.5.

## 2. Solar flares — failure, with a warning about threshold shopping

NOAA GOES science-quality flare composite, 2022–2024, 10,501 events (1,441 missing end fluence).
Resource: integrated irradiance through flare end (J/m²). Training on 2022, evaluation on 2023–2024
— a genuine temporal prediction check, not a within-sample fit.

| Quantity | Estimate | 95% interval |
|---|---:|---:|
| Resource exponent $d$, 2022 | 0.858 | 0.697 – 1.054 |
| Predicted $\alpha = d+1$ | 1.858 | 1.697 – 2.054 |
| Observed $\alpha$, 2023–24 | 2.239 | 2.085 – 2.399 |
| **Gap** | **0.382** | **0.125 – 0.620** |

The interval excludes zero. Observed occupancy spans $\Phi \approx 0.507$ to $1.525$ across eight
equal-log bins.

**Missingness does not explain it.** A sensitivity analysis using rise-phase fluence only — a
different physical resource, but with no missing values in the domain — gives predicted 1.862,
observed 2.274, gap 0.411 [0.208, 0.604].

**The threshold sensitivity is itself the most important finding here.** Lower thresholds of
$10^{-6}$, $5{\times}10^{-6}$, $10^{-5}$, $3{\times}10^{-5}$ W/m² give gaps of
**−0.480, 0.191, 0.382, 0.960**. The sign flips. These are four views of one dataset, not four
results — and they show that a researcher free to choose a threshold can obtain agreement,
disagreement, or over-shoot at will. Any future analysis must fix the domain in advance.

## 3. Ocean size spectrum — the best case, and it is genuinely interesting

Re-expression of the Hatton et al. (2021) reconstructed upper-200 m biomass summary, 23
logarithmic body-mass bins, bacteria to whales. Resource = body mass, so total biomass per log
class *is* the resource spectrum. Reproduces the published abundance slope: −1.039 against −1.04.

**This is a re-expression of a published, model-assisted reconstruction — not an independent
replication, and not an organism-level census.**

The occupancy profile is the informative part:

```
log10 mass (g)    Φ
  -13.5         2.525  ██████████████████████████████████████████████████
  -12.5         2.501  ██████████████████████████████████████████████████
  -11.5         1.967  ███████████████████████████████████████
  -10.5         1.110  ██████████████████████     ┐
   -9.5         1.140  ██████████████████████     │
   -8.5         1.080  █████████████████████      │
   -7.5         0.991  ███████████████████        │
   -6.5         0.991  ███████████████████        │
   -5.5         0.705  ██████████████             │  plateau
   -4.5         0.683  █████████████              │  ~15 decades
   -3.5         0.683  █████████████              │  Φ ∈ [0.68, 1.14]
   -2.5         1.039  ████████████████████       │  ratio 1.7×
   -1.5         1.069  █████████████████████      │  slope −0.0059
   -0.5         1.069  █████████████████████      │
    0.5         0.725  ██████████████             │
    1.5         0.896  █████████████████          │
    2.5         0.878  █████████████████          │
    3.5         0.849  ████████████████           │
    4.5         0.855  █████████████████          ┘
    5.5         0.573  ███████████
    6.5         0.483  █████████
    7.5         0.124  ██
    8.5         0.065  █
```

| Range | Bins | $\Phi$ range | Ratio | Log-slope $s$ |
|---|---:|---|---:|---:|
| Full, as published | 23 | 0.065 – 2.525 | **38.8×** | −0.0392 |
| Plateau, $10^{-10.5}$–$10^{4.5}$ g | 16 | 0.683 – 1.140 | **1.7×** | −0.0059 |
| Plateau + upper shoulder | 18 | 0.483 – 1.140 | 2.4× | −0.0121 |

*(Sub-range slopes are a descriptive reading of the published re-expression, computed for this
document. Three steps removed from raw observation: Hatton et al. reconstruction → resource-spectrum
re-expression → these fits.)*

**The plateau is the result worth having.** The middle ~15 decades are near-flat: $\Phi$ confined
to a factor of 1.7, slope −0.006, which implies a total systematic drift of only **1.23× across
fifteen decades of body mass**. The failures are concentrated at the two boundaries — the bacterial
end (Φ ≈ 2.5) and the whale end (Φ ≈ 0.07). That is a **quantified domain of validity**, and it is
the shape of result worth publishing: not "orthopolity is true" but "it holds across fifteen decades
of the marine size spectrum, breaks at both ends, and here is where."

> **Correction.** An earlier version of this document claimed the full-range slope of −0.039 "sits
> inside" a tolerance of $|s| \leq 0.0485$ while $\Phi$ varied by 39×, and offered that as a case
> of the slope test passing while flatness failed. That was an error: the 0.0485 figure is the
> tolerance for a **two-decade** span, and the ocean spectrum spans **22 decades**. The slope
> tolerance scales as $\ln(F)/\ln(k_{\max}/k_{\min})$, so the correct value here is ±0.0044 — and
> a slope of −0.039 implies a **7.3× drift across the full range**, failing the slope criterion
> too. The full range fails *both* criteria, not just one.
>
> The general point survives and still matters — a spectrum can undulate with zero fitted slope, so
> a slope criterion alone is never sufficient — but the ocean is not an example of it. The point is
> now enforced by a unit test on synthetic data instead
> ([`test_wavy_spectrum_with_zero_slope_fails_on_departure`](../tests/test_gof.py)).

## 4. Distribution goodness of fit and flatness equivalence

Both tests that were previously missing now exist ([`src/gof.py`](../src/gof.py),
[`experiments/run_gof.py`](../experiments/run_gof.py), outputs in
[`results/gof.json`](../results/gof.json)). All fits use the domains declared in
[`configs/pilot.json`](../configs/pilot.json); **no domain is re-selected**, since choosing a range
after seeing a result would invalidate the p-values and is the threshold-shopping failure this
project treats as a dead end. Alternatives are fitted on the same truncated support so the
likelihood ratios compare like with like.

### Is the distribution even a power law?

Clauset–Shalizi–Newman procedure: MLE, KS statistic, parametric bootstrap p-value (500 synthetic
datasets), Vuong likelihood-ratio tests against truncated alternatives. Following CSN, **p ≤ 0.1
rules the power law out**; p > 0.1 is non-rejection, not support.

| System | $\alpha$ | n | KS | p | Verdict |
|---|---:|---:|---:|---:|---|
| Solar flares, peak irradiance | 2.274 | 1,306 | 0.0323 | **0.018** | **Power law ruled out** |
| Earthquakes, energy proxy | 1.662 | 6,639 | 0.1080 | 0.000 | ⚠️ Test invalid — see below |

Likelihood-ratio comparisons, both systems: the power law beats the exponential and the stretched
exponential decisively (p < 0.0001 in every case), and is **statistically indistinguishable from the
lognormal** (flare p = 0.41, earthquake p = 0.90). That is the classic CSN outcome — lognormal and
power law cannot be separated over a bounded range — and it means no claim of the form "this is a
power law rather than a lognormal" is supportable from these data.

⚠️ **The earthquake goodness-of-fit test should not be read as a result.** Magnitudes are rounded to
0.1, so the energy proxy takes only **32 distinct values** across 6,639 events. A continuous KS
statistic on data that heavily tied is inflated by the ties alone, and the small p-value reflects
discretisation rather than evidence about the underlying law. A discrete CSN treatment would be
required. The occupancy test below is unaffected and is far stronger evidence.

### Is the spectrum flat?

Flatness requires **both** criteria — slope equivalence by TOST, and bounded departure
$\max|\ln\Phi|$ within tolerance — because a spectrum can undulate with zero fitted slope. The
tolerance is a **declared design choice**, not a natural constant: a maximum drift by a factor $F$
across the domain gives $|s| \leq \ln F / \ln(k_{\max}/k_{\min})$. Results at two tolerances:

| System | slope | 90% CI | tol ±(F=1.25) | $\Phi$ ratio | Verdict (F=1.25) | Verdict (F=2) |
|---|---:|---|---:|---:|---|---|
| Solar flares | −0.2325 | [−0.529, −0.060] | 0.0554 | 3.0× | not flat | not flat |
| Earthquakes | +0.2720 | [+0.239, +0.323] | 0.0185 | 28.5× | not flat | not flat |
| Ocean, full range | −0.0392 | *no interval* | 0.0044 | 38.8× | not flat | not flat |
| Ocean, plateau ‡ | −0.0059 | *no interval* | 0.0065 | 1.7× | fails departure | **passes both** |

‡ The plateau subrange was chosen **after** inspecting the spectrum. It is exploratory, not
confirmatory, and cannot be counted as a passed test.

No interval is available for the ocean because the source is a binned model-assisted reconstruction
rather than individual observations: there is no sampling model to bootstrap. The module reports
this as *unavailable* rather than manufacturing a verdict.

**The plateau result depends on the declared tolerance**, and that is the honest situation rather
than a defect. At $F = 2$ it satisfies both criteria; at $F = 1.25$ its 1.7× spread fails the
departure bound. Anyone claiming the ocean spectrum is "flat" must say what flat means first.

## 5. What is still missing

- **A discrete goodness-of-fit treatment for the earthquake catalogue.** The continuous KS test is
  invalid on magnitudes rounded to 0.1; that row of the table is a placeholder, not a finding.
- **A sampling model for the ocean spectrum**, without which no interval and therefore no
  equivalence verdict is possible for the strongest positive case.
- **An externally declared tolerance.** The plateau passes at $F = 2$ and fails at $F = 1.25$.
  Choosing $F$ after seeing that is the same error as choosing a domain after seeing a fit.
- **No preregistration.** Every result so far is exploratory. The flare threshold sensitivity shows
  exactly how much that matters.
- **No independent positive candidate.** The one qualified success is a re-expression of someone
  else's reconstruction. A test on independently sampled data is the single highest-value next step.
- **No preregistered domain.** Every domain and resource here was chosen before results were seen
  *by the analyst*, but nothing was registered externally. The flare threshold sensitivity shows
  how much latitude that leaves.
- **Exported slope intervals have conditional coverage** — the log-slope diagnostic is undefined
  when a bootstrap resample produces an empty bin, so those intervals should not carry primary
  inference.

## 6. How this changes the overall assessment

Before these tests, orthopolity was an untested lens. It now has a **track record**, and the
statistics have made it less favourable rather than more:

- **Two systems fail the occupancy test outright**, at every tolerance examined.
- **The flare distribution is not a power law** by the standard test (p = 0.018), and in neither
  system can a power law be distinguished from a lognormal. Part of the explanandum has evaporated:
  some of what the framework set out to explain is not clearly there.
- **The one positive case is exploratory**: a post hoc subrange of a re-expression of someone else's
  model-assisted reconstruction, with no sampling model, passing at one declared tolerance and
  failing at another.

That is a thin evidential base, and it should be described as such. What survives is worth having
anyway: a quantified 15-decade plateau with sharp boundary failures, in a system where the resource
is unambiguous. The question this now supports is **not whether orthopolity is true, but where and
why equal-resource spectra occur** — and the answer so far is "rarely, and the boundaries are the
interesting part."
