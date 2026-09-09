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
| Ocean, upper 200 m | body mass (biomass) | $\Phi$ flat | 21 of 23 bins unresolvable | **Indeterminate** |
| Ocean, full water column | body mass (biomass) | $\Phi$ flat | plateau degrades to 4.3× | **Failure to transfer** |
| **GLOSSAQUA, 1,300 spectra** | body mass (biomass) | NBSS slope −1.000 | **median −1.015**, 7.8% individually flat | **Ensemble yes, systems no** |

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

> ⚠️ **Superseded in part by §5.** Propagating the published uncertainties shows that 21 of these
> 23 bins have departures too small to resolve, so the boundary failures described below are mostly
> below the noise floor, and the plateau's flatness is not established either. Read this section
> with §5.

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

⚠️ **The earthquake row above is an artefact, now superseded.** Magnitudes are rounded to 0.1, so
the energy proxy takes only **32 distinct values** across 6,639 events, and a continuous KS
statistic on data that heavily tied is inflated by the ties alone. The correct discrete treatment
follows.

### The discrete test, which reverses that result

On the rounded magnitude grid the Gutenberg–Richter law is *exactly* a geometric distribution: with
$k = (M - M_0)/\Delta$ an integer, $N(\geq M) \propto 10^{-bM}$ means $P(K=k) = (1-q)q^k$ with
$q = 10^{-b\Delta}$. A power law in the magnitude-derived energy proxy is the same hypothesis, so
testing it on $k$ is the valid procedure ([`discrete_gr_gof`](../src/gof.py), CSN with a parametric
bootstrap).

| Threshold | n | b | KS | p | Verdict |
|---|---:|---:|---:|---:|---|
| **M ≥ 5.5** | 6,639 | 0.998 | 0.0077 | **0.256** | **Not ruled out** |
| M ≥ 6.0 | 2,076 | 0.984 | 0.0205 | 0.034 | ruled out |
| M ≥ 6.5 | 679 | 0.977 | 0.0381 | 0.026 | ruled out |

At the declared threshold the continuous test's KS of 0.108 becomes **0.0077**, and p goes from
0.000 to **0.256**. The Gutenberg–Richter law describes this catalogue well; the earlier rejection
was entirely the ties.

**This strengthens the earthquake negative result rather than weakening it.** The distribution is
exactly the form it should be, and orthopolity still fails on it by a wide margin (§1). The
occupancy failure is therefore a clean failure of (O), with no distributional irregularity to
absorb the blame — which is precisely the situation §5.1 of [concept.md](concept.md) describes as
the most informative kind of test.

Rejection at the *higher* thresholds, where there is less data and so less power, points to real
structure in the upper tail rather than to noise. A truncated version with a finite maximum
magnitude is marginally preferred at every threshold (ΔAIC −0.7 to −1.3), consistent with a finite
largest earthquake, though the truncation point is a boundary parameter so that comparison is
descriptive only.

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

## 5. Preregistered independent tests

Protocol declared and **committed before any of these analyses were computed**
([`configs/prereg_2026-09-09.json`](../configs/prereg_2026-09-09.json), commit `6df364f`); run by
[`experiments/run_independent.py`](../experiments/run_independent.py). The git history is the
preregistration record. Blinding is recorded per test rather than claimed uniformly.

### Test A — GLOSSAQUA: 1,300 published size spectra, 16 studies (blind)

The first genuinely independent test: different authors, ecosystems, instruments and methods from
the Hatton et al. reconstruction. Only the categorical design columns were inspected before the
protocol was fixed; no slope value was read.

With body mass as the resource, orthopolity predicts specific values in each published convention —
normalized biomass spectrum **−1**, normalized abundance spectrum **−2**, MLE exponent **−2**
(derivations in the protocol). The primary subset is the normalized biomass spectrum.

| Subset | n | studies | median slope | predicted | median departure | 95% CI |
|---|---:|---:|---:|---:|---:|---|
| **NBSS (primary)** | 1,300 | 16 | **−1.015** | −1.000 | **−0.015** | [−0.100, +0.010] |
| All mapped methods | 3,597 | 34 | −1.371 | — | +0.167 | [+0.032, +0.495] |

**The central tendency is almost exactly right.** The median of the per-study medians is
**−1.005** against a predicted −1.000, implying a systematic drift of only **1.11× across the
median 3.1-decade range**. Independently, across sixteen research groups, the ensemble sits on the
orthopolity value.

**The dispersion says individual systems are not flat.** By the declared criteria the verdict is
**NOT SUPPORTED**:

- Only **7.8%** of spectra are individually within tolerance at F = 1.25, and **23.8%** at F = 2.
- Only **6 of 16** studies have a median within 0.1 of the prediction; the rest range from −1.69
  to +0.45.
- Two studies supply **1,016 of 1,300 spectra (78%)**, and both happen to sit near −1. The
  apparent per-spectrum precision is largely those two studies. This is why the interval is
  bootstrapped over study blocks, and why it is wide.

> **The honest reading: orthopolity describes the ensemble average of aquatic size spectra and
> fails as a description of individual ones.** That distinction is a result in its own right, and
> it is the kind of "where it works" boundary worth publishing — but it is not the law the essay
> claims.

**An internal inconsistency worth flagging.** The conventions disagree with each other. An NBSS
slope of −1.015 implies a normalized-abundance slope of −2.015, but the observed median there is
−1.717 — a gap of 0.3 that the mapping cannot absorb. The subsets are different studies with
different ecosystems and size ranges, so this need not be an error, but it means published slopes
from different conventions should not be pooled naively. The primary NBSS subset is the one to
trust.

Of 6,559 body-mass records, 2,790 were dropped solely because `SizeRangeMinimum`/`Maximum` are
absent upstream — a coverage limitation, not a selection made here.

### Tests B and C — ocean spectra with published uncertainty propagated

The gap flagged earlier ("no sampling model, therefore no verdict") is now closed. The published
95% interval is exactly [estimate/f, estimate×f] with f a per-group factor, verified for all 253
rows. Drawing 20,000 lognormal replicates per group per bin gives slope intervals and a verdict.

| Domain | Range | slope | 95% CI | tol (F=1.25) | Φ ratio | Verdict |
|---|---|---:|---|---:|---:|---|
| Upper 200 m | full | −0.0392 | [−0.058, −0.026] | 0.0044 | 38.8× | not flat |
| Upper 200 m | plateau ‡ | −0.0059 | [−0.036, +0.018] | 0.0065 | 1.7× | not flat |
| Full water column (blind) | full | −0.0529 | [−0.070, −0.038] | 0.0044 | 109.3× | not flat |
| Full water column (blind) | plateau ‡ | −0.0025 | [−0.029, +0.023] | 0.0065 | 4.3× | not flat |

‡ Post hoc subrange; exploratory, not confirmatory.

Two findings, and the first is the more important:

**Most of the ocean spectrum's departures are not resolvable at all.** Only **2 of 23 bins** have a
departure that clears the reconstruction uncertainty at F = 1.25, and **1 of 23** at F = 2. The
per-group uncertainty factors run from 2.98 to 11.39 — the bacterial end, where Φ ≈ 2.5, is
dominated by a group whose published interval spans a factor of 3.86 either way. **The "boundary
failures" identified in §3 are mostly below the noise floor**, and so is the plateau's flatness.
The data cannot support the claim in either direction, which is a stronger and more useful
statement than either the positive or the negative reading.

**The plateau does not transfer cleanly to the full water column.** Applying the identical pipeline
and the same plateau boundaries without tuning, the Φ ratio degrades from 1.7× to **4.3×**, while
the fitted slope stays near zero (−0.0025). The flat *trend* survives the change of domain; the
*equality* does not.

## 6. Is the ensemble result real? Attractor, artefact, or neither

> ⚠️ **Exploratory, not preregistered.** Preliminary values were seen during feasibility assessment
> before this analysis was written. Run by
> [`experiments/run_ensemble.py`](../experiments/run_ensemble.py), output in
> [`results/ensemble.json`](../results/ensemble.json).

§5 left one question: the ensemble median lands on the predicted value while individual spectra
scatter widely. Is that a real regularity, or an artefact of the field reporting what it expects?
Three tests on the 1,300-spectrum NBSS subset.

### 6.1 The scatter is real, not estimation noise

Deriving a standard error per spectrum from its reported confidence interval (747 of 1,300 have
one) and running a random-effects decomposition:

| Quantity | Value |
|---|---:|
| Observed SD of slopes | 0.273 |
| Median reported SE | 0.159 |
| Cochran's Q | 6,425 on 746 df |
| **I²** | **88.4%** |
| **τ** (between-system SD of true slopes) | **0.252** |

**88% of the variance is genuine between-system heterogeneity.** Aquatic systems really do have
different size-spectrum slopes, spread with a standard deviation of about 0.25 around the centre.
Orthopolity is *not* an attractor pinning individual systems to −1.

### 6.2 The centre is not an artefact of anchoring

If the field simply reported the Sheldon value it expected, there would be a spike at exactly −1.00
beyond the generic human preference for round numbers. There is a round-number preference — the
second-decimal digit distribution is not uniform (χ² = 46.3 on 9 df, p < 0.01, with digit 0 at 198
against an average of ~130) — but it is not specific to the predicted value:

| | Excess over local baseline |
|---|---:|
| At −1.00 | 1.86× |
| Median across the other 16 round values | 1.46× |
| **Rank of −1.00 among 17 round values** | **3rd** |

−1.00 is elevated, but so is every round value, and −1.00 is not even the most elevated. **No
evidence of anchoring on the predicted value.** The central tendency is not manufactured by
reporting habits.

### 6.3 The centre holds across habitats and taxa

Median slope by stratum, with study-block bootstrap intervals. Strata with fewer than four study
blocks get no interval rather than a spurious one — with a single study the block bootstrap has
zero width, which would otherwise have produced meaningless "inconsistent" verdicts.

| Stratum | n | studies | median | 95% CI | vs −1.000 |
|---|---:|---:|---:|---|---|
| Freshwater | 1,075 | 5 | −1.010 | [−1.019, −0.981] | consistent |
| Marine | 225 | 11 | −1.060 | [−1.340, −0.833] | consistent |
| Fish | 688 | 5 | −1.011 | [−1.665, −0.987] | consistent |
| Macroinvertebrate | 63 | 4 | −1.000 | [−1.000, −0.640] | consistent |
| Zooplankton | 139 | 4 | −0.990 | [−1.074, −0.514] | consistent |
| Community | 890 | 13 | −1.000 | [−1.100, −0.900] | consistent |

**Every stratum with a valid interval is consistent with the prediction.** Freshwater and marine
systems, and fish, macroinvertebrates and zooplankton separately, all centre on −1.

Note the composition, which limits the reach of the claim: GLOSSAQUA is dominated by freshwater
fish (3,127 of 3,576 sites freshwater; 2,855 fish). The marine and non-fish strata are much
smaller and their intervals much wider.

### 6.4 Does the concentration at −1 come from averaging?

If systems land near −1 because a wider size range averages over more of the spectrum, then studies
spanning more decades should sit closer to the prediction. If the dispersion is intrinsic, span
should not matter.

| Span (decades) | n | studies | median \|departure\| | τ |
|---|---:|---:|---:|---:|
| 0.90 – 2.79 | 325 | 5 | 0.190 | 0.311 |
| 2.79 – 3.06 | 325 | 4 | 0.192 | 0.272 |
| 3.06 – 35.0 | 273 | 9 | 0.200 | 0.211 |
| 35.0 (one study) | 377 | 1 | 0.049 | — |

**At study level — the only valid test here — Spearman ρ = −0.549, p = 0.028 (n = 16).** Wider-
spanning studies do sit closer to the prediction, and τ declines across the well-sampled quartiles
(0.311 → 0.272 → 0.211). That is consistent with an averaging mechanism.

Three reasons to treat it as suggestive rather than established:

- **n = 16 studies, p = 0.028.** One marginal test.
- **The quartile medians are flat** across the well-sampled range (0.190, 0.192, 0.200). The
  correlation comes from including the widest-spanning studies, not from a gradient within the bulk.
- **Span is not randomly assigned.** Plankton studies span more decades than fish studies, so span
  is partly a proxy for taxon, and the confound is not resolved here.

> **A methodological note worth keeping.** At *spectrum* level the same test gives ρ = −0.427 with
> p = 8×10⁻⁵⁹ — an apparently overwhelming result that is almost entirely one study contributing
> 377 spectra at a single span value of 35 decades. Pseudo-replication turns a marginal signal into
> a spurious certainty. Both numbers are reported in
> [`results/ensemble.json`](../results/ensemble.json), with the spectrum-level one flagged.

### 6.5 The shape: two moments are not enough

(O-ensemble) as stated ([concept.md §3.1](concept.md)) constrains only a mean and a variance, so
maximum entropy makes the latent slope distribution Gaussian. Fitting each candidate latent shape
*convolved with the reported measurement errors* (747 spectra with usable errors):

| Latent family | μ | τ | logL | ΔAIC |
|---|---:|---:|---:|---:|
| Gaussian | −1.0114 | 0.2553 | −181.5 | 0.0 |
| Laplace | −1.0167 | 0.2683 | −190.8 | +18.6 |
| **Student t, ν = 8** | −1.0118 | 0.2566 | −176.8 | **−7.4** |

Standardised residuals under the Gaussian fit have sd 0.997 and skew −0.066 — well centred and
symmetric — but **excess kurtosis +1.13**. The latent distribution is heavier-tailed than Gaussian.

**So the two-moment maximum-entropy form is not adequate**, on moderate evidence (ΔAIC = −7.4 is
suggestive, not decisive; the rule of thumb for strong preference is 10). Something beyond a mean
and a variance is structuring the dispersion.

The natural candidate is consistent with the hypothesis rather than against it: **a mixture over
classes**. Pooling freshwater with marine, and fish with plankton, mixes subgroups with different
τ, and a mixture of Gaussians with unequal variances is exactly heavy-tailed. That is testable —
τ estimated separately per stratum — and is filed as R7.

### 6.6 The claim predicts its own failure rate

This is the sharpest result in the repository.

The apparent tension in §5 — the median lands on −1, yet only 7.8% of spectra pass individually —
looked like a hypothesis half-working. It is not. Given τ, (O-ensemble) *predicts* the individual
pass rate, because it says exactly how far systems must scatter.

| Tolerance | Latent | Predicted pass rate | Observed | Ratio |
|---|---|---:|---:|---:|
| F = 1.25 | Gaussian | 0.080 | **0.078** | 0.99 |
| F = 2.00 | Gaussian | 0.237 | **0.238** | 1.01 |
| F = 1.25 | Student t | 0.088 | 0.078 | 0.89 |
| F = 2.00 | Student t | 0.259 | 0.238 | 0.92 |

**A single dispersion parameter reproduces the observed failure rate to within 1–2% at both
tolerances.** The "failure" of individual systems in §5 is not evidence against the ensemble
claim — it is precisely what the ensemble claim requires.

> **Stated honestly about its status:** this is an internal consistency check, not an out-of-sample
> prediction. τ was fitted to the same slopes. It is a non-trivial check nonetheless — one number
> has to reconcile the shape of the departure distribution with a heterogeneous set of per-study
> tolerances derived from reported size ranges, at two different tolerance factors, and it does.
> The out-of-sample version is the replication prohibition below, which requires new data.

### 6.7 What the hypothesis now forbids

With τ measured, (O-ensemble) makes three refutable commitments:

1. **Replication.** τ is a class property, so an independent aquatic dataset must reproduce
   **τ ≈ 0.257**. A materially different value refutes it for that class. This is R4 (PSSdb).
2. **Two resources at once.** If two resources both satisfy (O) on the same systems, then
   Var[s₁] = Var[s₂] and corr(s₁, s₂) = 1. Unequal dispersion refutes at least one of them. This is
   the cleanest decisive test available and needs no new instrument — only two resource definitions
   on one set of systems.
3. **Pass rates.** Any dataset whose individual pass rate is inconsistent with its fitted τ refutes
   the claim.

That is a small theory that forbids specific things, which is the minimum for the work to be
scientific rather than descriptive.

### 6.8 The heavy tail is largely a mixture over classes (R7)

§6.5 found the pooled latent distribution heavier-tailed than the two-moment maximum-entropy form,
and suggested the obvious explanation: pooling classes with different τ. Fitting each stratum
separately ([`experiments/run_strata.py`](../experiments/run_strata.py)) supports it.

| Stratum | n | studies | μ | **τ** | Best latent | Excess kurtosis | Gaussian adequate? |
|---|---:|---:|---:|---:|---|---:|---|
| **Freshwater** | 645 | 5 | −0.997 | **0.228** | Gaussian | −0.34 | **yes** |
| Marine | 102 | 11 | −1.109 | **0.383** | Laplace | +1.91 | no |
| Fish | 671 | 5 | −1.011 | 0.260 | Student t | +1.23 | no |

Three things follow.

**Within a homogeneous class, the maximum-entropy form works.** Freshwater — the largest and
cleanest stratum — is adequately Gaussian, with excess kurtosis of −0.34. The two-moment prediction
of [concept.md §3.1](concept.md) is not wrong; it was being tested on a pooled sample that violates
its own scope condition.

**A mixture of the fitted strata reproduces most of the pooled tail.** Building a two-component
mixture from the fitted habitat parameters alone gives excess kurtosis **+0.926** against the pooled
**+1.132** — about 82% of it, from nothing but the τ difference between freshwater and marine.

**τ really is a class property**, as the hypothesis asserts rather than assumes: freshwater 0.228
against marine 0.383, a 1.68× difference. This sharpens the replication prohibition of §6.7. The
commitment is not a universal τ ≈ 0.257 but **class-specific values — τ ≈ 0.23 for freshwater and
≈ 0.38 for marine** — which is both more useful and easier to refute.

Marine and Fish remain heavy-tailed, and both are themselves heterogeneous: "Marine" spans coral
reef, continental shelf and open ocean across 11 studies, and "Fish" spans fresh and salt water. The
mixture explanation predicts exactly that, and finer strata would test it — but n = 102 for marine
is already thin.

### 6.9 The span/taxon confound cannot be resolved with this data (R5)

§6.4 found wider-spanning studies closer to −1 (ρ = −0.549, p = 0.028) but flagged span as partly a
proxy for taxon. Testing within taxon:

| Taxon | studies | span range | ρ | p |
|---|---:|---|---:|---:|
| Fish | 5 | 0.9 – 3.0 decades | −0.500 | 0.391 |
| Macroinvertebrate | 4 | 3.0 – 5.3 | −0.211 | 0.789 |
| Zooplankton | 4 | 2.6 – 9.9 | +0.400 | 0.600 |

Nothing significant, and the signs disagree. **This is a power failure, not a null result**: four or
five study blocks per taxon cannot detect a correlation of the pooled size. The honest position is
that the confound stands unresolved — the pooled relationship may be a genuine averaging effect or
may be taxon acting through span, and this data cannot say which. Resolving it needs studies that
vary span at fixed taxon, which is R5's standing requirement.

### 6.10 The replication prohibition, tested once and failed (R4-partial)

§6.7 committed to a class-specific τ that independent data must reproduce. PSSdb, the intended test,
is unreachable — see the roadmap for the access attempt. The nearest available substitute is a
comparison **across published conventions inside GLOSSAQUA**, whose method subsets turn out to share
**no studies at all**, so the primary sources genuinely differ even though the compilation does not.

| Convention | Habitat | n | studies | τ | μ (departure) | E[s] = 0? |
|---|---|---:|---:|---:|---:|---|
| Normalised biomass spectrum | Freshwater | 645 | 3 | **0.228** | **+0.003** | yes |
| Normalised biomass spectrum | Marine | 102 | 8 | 0.383 | −0.109 | no |
| Normalised abundance spectrum | Freshwater | 1,881 | 14 | **0.462** | **+0.397** | no |
| Maximum likelihood | Freshwater | 401 | 4 | **0.355** | **+0.516** | no |

**It does not replicate.** Freshwater τ ranges over 0.228 / 0.462 / 0.355 — a factor of 2.02 — and
two of the three conventions have a mean departure far from zero, violating the central clause of
(O-ensemble) outright.

**What this does and does not establish.** Method and study population are *perfectly* confounded:
the subsets share zero studies, so a discrepancy cannot be attributed to the convention rather than
to the systems, or the reverse. Two readings survive:

- **The mapping is wrong for those conventions.** An NBSS slope of −1.0 implies a
  normalised-abundance slope of exactly −2.0 ([concept.md §6](concept.md)), a relation with no free
  parameters. The observed offsets are both positive and both near +0.4 to +0.5, which looks more
  like a systematic convention mismatch than like scattered biological difference. If published
  "normalised" spectra are not all normalised the same way, the label cannot be trusted without
  checking each primary source.
- **Or the hypothesis fails on those systems**, and the NBSS subset is the unrepresentative one.

Nothing here separates them, and the honest consequence is the same either way:

> **The primary result rests on one convention and 16 studies, and the first attempt to corroborate
> it across conventions failed.** Any meta-analysis pooling published size-spectrum slopes — this
> one included — needs primary-source verification of each study's convention before its exponents
> can be compared.

This is the strongest caution in the repository against the result it is most tempted to believe.

### 6.11 Primary-source check: the database label does not identify the estimand

§6.10 left two readings — wrong mapping, or failed hypothesis. Checking the primary sources
resolves it, and the answer is the first.

**Perkins et al. (2018), *Ecology Letters***, is listed in GLOSSAQUA under
*Normalized abundance spectrum (linear)*. Its Methods say:

> "M-N relationships were derived after **logarithmic binning** of individual body mass, M. The
> range of log₁₀ M values for each site was divided into n equal size-bins (on a logarithmic
> scale), and the **log₁₀ of the total number (N) of all organisms in each size-bin** was regressed
> against the central value of each bin"

and, decisively:

> "the M-N slope (**equal to the individual size distribution exponent + 1**; Reuman et al. 2009)"

That is counts per **logarithmic** bin, *not* divided by bin width. Biomass per log class is then
$m \cdot dN/d\ln m \propto m^{1+s}$, so orthopolity predicts **s = −1, not −2**. Under the correct
mapping Perkins' −0.798 is a departure of **+0.20** — inside one τ of the NBSS result — rather than
the +1.20 the label implied.

Applying both candidate mappings to all 15 studies in the subset:

| Study | n | median | dep vs −2 | dep vs −1 | Better fit |
|---|---:|---:|---:|---:|---|
| Girón 2023 | 2 | −2.016 | **−0.016** | −1.016 | −2 (true normalised) |
| Arranz et al. 2023 | 1,167 | −1.860 | **+0.140** | −0.860 | −2 (true normalised) |
| MacGarvey & Kirk 2018 | 12 | −1.742 | +0.258 | −0.742 | −2 |
| Pomeranz 2023 | 23 | −0.844 | +1.156 | **+0.156** | −1 (M–N) |
| Perkins et al. 2018 ✔ | 31 | −0.798 | +1.202 | **+0.202** | −1 (M–N, *verified*) |
| Quintana 2023 | 73 | −0.426 | +1.574 | +0.574 | −1 |

**Eleven of fifteen studies fit the −1 mapping better; four fit −2.** Girón at −2.016 and Perkins at
−0.798 carry the *same* database label while differing by almost exactly 1 in exponent — the
signature of two distinct estimands filed under one name.

**What follows, and what deliberately does not.** The subset is **excluded as unusable** pending
per-study verification. Re-mapping each study to whichever prediction fits it better would
manufacture agreement and is the retrofitting listed as a dead end in
[not-worth-pursuing.md](not-worth-pursuing.md); the point of the check is that the label cannot be
trusted, not that a better label can be inferred from the answer.

Three consequences:

1. **The §6.10 replication failure is explained by a data defect, not by the hypothesis.** It was
   never a test of (O-ensemble); it was a test of whether a metadata field means one thing.
2. **The primary NBSS result is not impugned** — but neither is it verified. The same check has not
   been run on its 16 studies, and it should be before publication.
3. **The methodological warning is now evidenced rather than suspected.** Compilations of published
   size-spectrum exponents cannot be pooled on their method labels. This applies to GLOSSAQUA, to
   this analysis, and to any meta-analysis of scaling exponents that trusts a convention field.

### 6.12 Verifying the primary subset (R8): conventions confirmed

The two studies carrying 78% of the primary evidence have now been read directly. Both use the
convention their label claims, and the mapping to −1 is correct.

**Arranz et al. (2022), *Ecology* — 49.2% of spectra.** Methods, verbatim:

> "we classified body mass into a geometric series of size intervals in which the lower boundary of
> each interval differed by a factor of two… Then, **normalized scores (normalized corrected BPUE)
> were calculated as the biomass index divided by interval**. The NBS slope was calculated using
> ordinary least squares (OLS) to regress log₂(normalized corrected BPUE) on log₂(body mass class)."

Biomass per bin **divided by bin width**, on log₂ bins — the normalised biomass size spectrum
exactly. And they state the reference value themselves: *"the slopes based on simple OLS regressions
varied around **the theoretical expected value of −1**"*.

**Gaedke (1993), *Limnology & Oceanography* — 29.0%.** More than confirmation; the paper states the
orthopolity identity outright:

> "an **equal distribution of biomass over all size classes** corresponds to a zero slope of a line
> fitted to a Sheldon-type size spectrum… and to a **slope of −1 of the normalized spectrum**"

Reported results: entire-range seasonal average **−1.00**; reduced spectrum seasonal average −0.97.

**Extraction fidelity.** Every summary statistic GLOSSAQUA carries for Arranz reproduces the
published Table 1 to two decimals:

| | GLOSSAQUA | Paper Table 1 |
|---|---:|---:|
| n | 639 | 639 |
| mean | −1.004 | −1.00 |
| median | −0.989 | −0.99 |
| SD | 0.279 | 0.28 |
| min / max | −1.741 / −0.269 | −1.74 / −0.27 |

Gaedke likewise: the GLOSSAQUA median of −1.020 sits between the two seasonal averages the paper
reports, and its minimum of −1.23 is exactly the paper's early-spring value.

**An independent corroboration of τ.** Arranz report SD = 0.28 across 639 lakes. The latent τ
estimated here for freshwater is **0.228** — necessarily smaller than the raw SD, because the
deconvolution removes measurement error, and smaller by about the right amount. τ was not fitted to
anything Arranz published; the agreement is a genuine external check on the random-effects
machinery.

**A qualification this reading appeared to force — since tested and withdrawn.** Gaedke's slopes
range from −1.23 to −0.82 **within a single lake**, a spread of 0.37, which looked large enough to
mean τ was measuring repeat-measurement noise rather than real differences between ecosystems.
Fitting the decomposition (§6.13) shows otherwise: that *range* over 377 observations corresponds to
an SD of only **0.067**, against a between-site τ of 0.235. Temporal variation is about **8% of the
variance**. Inferring a standard deviation from a range was the error; τ does mean what it appeared
to mean.

*(The two PDFs are not redistributed here; they are paywalled. The quotations above are the
verification record.)*

### 6.13 Where the dispersion actually lives (R9)

The primary subset happens to contain the two designs that isolate each component:

| Component | Study | Design | Estimate |
|---|---|---|---:|
| **Between-site** | Arranz et al. 2022 | 639 lakes × 1 occasion | **τ = 0.235** |
| **Within-site (temporal)** | Gaedke 1993 | 1 lake × 377 occasions, 10 years | **SD = 0.067** |

Arranz's design gives between-site dispersion with measurement error removed (raw SD 0.279, median
reported SE 0.165 → latent τ 0.235). Gaedke's gives pure temporal variation, and reports no errors,
so 0.067 is an **upper** bound on it.

> **Temporal variation is at most 8.2% of the variance.** The dispersion is predominantly *between
> ecosystems*, so τ ≈ 0.23 does mean what §6 took it to mean: lakes genuinely differ from each other
> in how equally biomass is spread across size classes, and one lake re-measured through a season
> stays comparatively fixed.

Two studies in the subset have both several sites and repeat visits, and can be fitted jointly as a
check. Both are small, and both agree on the direction: StudyID_10 (n = 27, 5 sites) gives 74%
between-site; StudyID_105 (n = 24, 6 sites) gives 81%.

**What this is not.** The two components come from different studies in different ecosystems, so
these are bounds, not a partition of one variance. Treating Lake Constance's temporal variability as
representative of 639 Ontario lakes is an assumption. A study measuring many sites *and* repeat
visits with reported errors would settle it properly; none in this subset is large enough to.

**Consequence for the prohibition.** [concept.md §3.1](concept.md) commits to τ replicating within a
class. That commitment can now be stated more sharply: what must replicate is the **between-site**
component, τ ≈ 0.235 for temperate lake fish communities, and a replication attempt must not confound
it with sampling design — a study visiting few sites many times will find a smaller τ for reasons
that have nothing to do with the hypothesis.

### 6.14 What the tests together say

Neither of the two hypotheses that motivated this analysis survives:

- **Not an artefact.** No anchoring on the predicted value; the centre holds independently across
  habitats and taxa.
- **Not an attractor.** Individual systems genuinely differ, with τ ≈ 0.25.
- **Possibly an averaging effect**, on suggestive but marginal evidence (§6.4).
- **The failed cross-convention replication was a data defect, not a result** (§6.11). One
  database label covers at least two estimands differing by 1 in exponent, verified against a
  primary source. The subset is excluded rather than re-mapped.
- **A two-moment constraint after all, within class.** The pooled distribution is heavier-tailed
  than the maximum-entropy form (§6.5), but that is a pooling artefact: freshwater alone is
  adequately Gaussian, and a mixture of the fitted habitat τ values reproduces 82% of the pooled
  excess kurtosis (§6.8).

The random-effects pooled mean is **−1.0113, 95% CI [−1.0329, −0.9897]** — an interval that
contains the prediction while properly accounting for the heterogeneity. And the fitted dispersion
reproduces the individual failure rate to within 1–2% (§6.6), so the ensemble and individual
results are one coherent picture rather than two conflicting ones.

> **What is left is a real, reproducible, non-artefactual regularity in the *expected value* of
> aquatic size spectra, with substantial genuine dispersion around it.** Orthopolity holds in the
> mean and fails in the particular — and the failure in the particular is a fact about nature, not
> about measurement.

That is a weaker claim than a law and a stronger one than a convention. It also poses a sharper
question than the programme has faced so far: *why should the mean be −1 if individual systems
range over ±0.5?* An account of the mean without an account of the dispersion is incomplete.

## 7. What is still missing

Revised as items were closed; the roadmap tracks them with identifiers.

- **Better-constrained ocean data (R6).** With 21 of 23 bins unresolvable, no ocean verdict is
  possible until the reconstruction uncertainty shrinks. Independently sampled spectra with real
  sampling models — PSSdb, or the individual-organism sources behind GLOSSAQUA — are the route.
- **Marine and non-fish coverage (R4).** The ensemble is 87% freshwater and 80% fish, so the strata
  that would test generality hardest are the smallest. This is also the out-of-sample test of the
  τ ≈ 0.257 replication prohibition, and therefore the highest-value outstanding item.
- **A mechanism for the mean.** §6 establishes that the centre is neither a reporting artefact nor
  an attractor, and that both the centre and the dispersion are real. Nothing explains *why* the
  mean should sit at −1 while individual systems scatter with τ ≈ 0.26. This is the central open
  question.
- **Finer marine strata.** Marine remains heavy-tailed (excess kurtosis +1.91) and is itself a
  mixture of coral reef, shelf and open ocean, but n = 102 is already thin for splitting further.
- **The span/taxon confound (R5), still open.** Tested and underpowered: at four or five study
  blocks per taxon nothing reaches significance and the signs disagree (§6.9). Needs studies that
  vary span at fixed taxon.
- **An externally declared tolerance.** F = 1.25 and F = 2 were chosen by the analyst, not
  registered with anyone. The ocean plateau passes at one and fails at the other, so this is not a
  cosmetic point.
- **A lognormal comparison on the discrete earthquake support.** The valid discrete test shows
  Gutenberg–Richter is not ruled out at M ≥ 5.5, but no alternative has been fitted on that same
  discrete support; the earlier continuous comparison is withdrawn (§4).

**Closed since earlier versions of this document:** CSN goodness-of-fit and equivalence testing
(§4); preregistration, which §5 now has (commit `6df364f`); a sampling model for the ocean spectrum,
supplied by propagating the published per-group uncertainties (§5); and a discrete treatment for the
earthquake catalogue (§4).

## 8. How this changes the overall assessment

Five systems examined, three under a preregistered protocol, plus a follow-up on the one positive
result. The strong claims are gone and one modest claim has survived a serious attempt to kill it.

**Dead.** The universal reading. The claim about individual systems — τ ≈ 0.25 says they genuinely
differ. The earthquake and flare cases, decisively. The ocean plateau, which does not transfer to
the full water column and whose departures are anyway unresolvable in 21 of 23 bins. And the claim
that orthopolity explains observed power laws, since the flare distribution is not a power law and
no tested system distinguishes a power law from a lognormal.

**Alive.** Across 16 independent studies and 1,300 published spectra, the median normalized biomass
spectrum slope is −1.015 where orthopolity predicts −1.000. That centre survives every check
applied to it: it is not an artefact of round-number reporting, and it holds separately in
freshwater and marine systems and in fish, macroinvertebrates and zooplankton.

**The claim that fits the evidence.** Orthopolity is a statement about the *expected value* of
aquatic resource spectra. It is real, independently reproducible, and violated by most individual
systems. That is worth publishing, worth a mechanism, and is not a natural law — still less a
cosmological principle.
