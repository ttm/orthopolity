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

**Two conclusions, and the second is the one worth having.**

First, a warning: the **full-range fitted slope of −0.039 sits inside** the illustrative tolerance
of $|s| \leq \ln(1.25)/\ln(100) \approx 0.0485$ — while $\Phi$ varies by a factor of **39**. The
slope test passes and the equality claim fails, on the same data. This is exactly why a slope test
alone is inadequate: it averages a 2.5 at one end against a 0.065 at the other. **A flat fitted
slope is not flatness.**

Second, and more positively: the middle ~15 decades really are near-flat, with $\Phi$ confined to a
factor of 1.7 and a slope of −0.006. The failures are concentrated at the two boundaries — the
bacterial end (Φ ≈ 2.5) and the whale end (Φ ≈ 0.07). That is a **quantified domain of validity**,
which is precisely the shape of result worth publishing: not "orthopolity is true" but "it holds
across fifteen decades of the marine size spectrum and breaks at both ends, and here is where."

## 4. What is still missing

- **No Clauset–Shalizi–Newman goodness-of-fit testing has been done.** The lab fits a bounded
  power law *descriptively* and says so. No KS bootstrap $p$-values, no likelihood-ratio comparison
  against lognormal, exponential or stretched exponential. Mandatory before any confirmatory claim.
- **No equivalence testing.** Failure to reject flatness is not support for flatness; see
  [value.md §4](value.md).
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

## 5. How this changes the overall assessment

Before these tests, orthopolity was an untested lens. It is now a hypothesis with a **track record**:
one qualified success with a mapped domain of validity, and two failures — one of them decisive, and
neither rescued by obvious corrections. That is considerably more informative than the essay's
collection of confirming illustrations, and it points the work toward the only question that now
looks answerable: **not whether orthopolity is true, but where and why it holds.**
