# Speech-capacity transfer: independent entropy improves duration forecasts

Study executed 17 October 2026; report completed 19 October 2026.
**The frozen cross-family prediction passes all declared rules.** A common
information capacity calibrated on seven Indo-European languages predicts ten
languages from eight other families with primary log error **0.074115**,
versus **0.154397** for a constant syllabic rate. Conditional entropy also
improves on unigram entropy, a fitted entropy power and same-text duration.
This supports transfer of an established information-capacity account; it does
not uniquely establish orthopolity or a causal resource mechanism.

The reference measure is counting: equal source-defined families, languages
within family, speakers within language, then each speaker's available texts.
This is neither log-orthopolic nor linear-orthopolic size allocation. The primary
estimand is language-level geometric mean duration, not the duration of every
individual reading.

## Chronology and source

The [protocol](speech-capacity-protocol-2026-10-17.md), configuration, algorithms,
independent verifier, tests and source receipts were committed at **eeab4d3**
before decoding any numerical calibration duration. Verified forecasts were
committed at **26b78d8** before decoding the 1,499 numerical target durations.
The prediction SHA-256 is
`a7a82815eef2d04bc3a582997d774df933aae33a3bee148d5542d1b9fe0fb31c`.
The published equal-information-rate interpretation, approximate **39 bits/s**
aggregate and reported correlations were already known. This is a locally
frozen retrospective validation, not a blind discovery, external preregistration
or prospective experiment. The published aggregate was not used as the fitted
capacity.

The original source is Coupé, C., Oh, Y. M., Dediu, D., and Pellegrino, F. (2019),
*Different languages, similar encoding efficiency: Comparable information rates
across the human communicative niche*, **Science Advances 5**, eaaw2594,
[doi:10.1126/sciadv.aaw2594](https://doi.org/10.1126/sciadv.aaw2594).
The [pinned original repository](https://github.com/keruiduo/SupplMatInfoRate/tree/00798db1687a429349370e40e1a726deb35c1ef6)
and publisher supplementary S1 supply byte-identical `InfoRateData.csv` files:
96,064 bytes, SHA-256
`f4dde6def980ed4c461ad8fd666af64cbbaa967a2ac73702855fc70484c0732a`.

The archive contains **2,288 readings**, whereas the article states **2,265**.
The [source audit](human-source-qualification-2026-10-17.md) found no explanation
for the 23-row difference. All archived rows were retained. Seven calibration
languages—Catalan, German, English, French, Italian, Spanish and Serbian—supply
**789 readings from 70 speakers**. The test cohort supplies **1,499 readings
from 100 speakers in ten languages and eight families**. Every language has
ten speakers and all 15 text identities at language level. Relative to complete
speaker-by-text coverage, calibration lacks **261 cells** and testing lacks
**one Turkish cell**. Available texts are averaged within speaker; missing cells
are not imputed or treated as zero. This weighting avoids overweighting more
complete speakers, but does not remove possible text-coverage bias.

## Prediction fixed before outcomes

The predictor `ID` is conditional syllable entropy estimated from independent
written corpora, using the previous syllable within a word or a word-onset null.
`ShE` is unigram syllable entropy without that context. Neither is calculated
from speech duration. `NS` is the canonical syllable count of a translated text.
The response `D` is measured duration after removing manually identified pauses
longer than 150 ms; it is neither total elapsed reading time nor pure phonation
time.

The primary model is

$$
\widehat D=\frac{NS\,ID}{C}.
$$

Training by weighted squared log-duration error gives **C=40.396703 bits/s**.
This is an inferred common capacity, not an independently imposed information
budget or a measurement of metabolic expenditure. The four frozen alternatives
use constant syllabic rate, unigram entropy, a fitted power of conditional
entropy, or the training duration of the same text. Each is calibrated only
on the seven training languages. The constant syllabic rate is **6.848752
syllables/s**; the fitted-power exponent is **0.440188** rather than the primary
model's fixed exponent 1. The power regression has only seven distinct
language-level entropy inputs.

Training conditional entropy spans **5.29–7.09 bits/syllable**. Four test
languages lie outside that interval: Basque **4.83**, Japanese **5.03**, Thai
**7.19**, and Vietnamese **8.02**. These extrapolations were identified before
target-duration access and retained without clipping. No target-specific fit,
outcome-dependent exclusion or post-fit correction was applied.

## Complete model comparison

For each language, first average the signed residual
`log(predicted duration / observed duration)` over available texts within
speaker and then over speakers. Call this mean `e_l`. The primary error `E`
averages `|e_l|` over languages within family and then over the eight families.
The reading error instead takes the absolute value before averaging, so
opposite individual errors cannot cancel within a language. All errors below
use natural logarithms.

| Model | Family-balanced language error E (primary) | Equal-language sensitivity | Family-balanced reading error | Maximum language absolute log error |
|---|---:|---:|---:|---:|
| Conditional information capacity | **0.074115** | 0.074386 | **0.110054** | 0.183522 (Thai) |
| Constant syllabic rate | 0.154397 | 0.152238 | 0.176108 | 0.381531 (Thai) |
| Unigram information capacity | 0.144894 | 0.147134 | 0.167662 | 0.328852 (Thai) |
| Fitted entropy power | 0.094382 | 0.096759 | 0.132953 | 0.294370 (Thai) |
| Same-text duration | 0.102055 | 0.101381 | 0.149678 | 0.189005 (Hungarian) |

The primary error corresponds to `exp(E)=1.076930`, an average multiplicative
discrepancy factor under the declared log metric. It is not an arithmetic
percentage error or a guarantee that each language is within 7.7%. The reading
error is larger, **0.110054**, corresponding to factor **1.116338**. Conditional
capacity has the lowest error under both these metrics and under equal-language
weighting; the primary decision still uses the frozen family-balanced metric.

All frozen requirements pass:

- **Accuracy:** 0.074115 is below `log(1.20)=0.182322`.
- **Syllabic-rate advantage:** the primary error is **52.00% lower**, exceeding
  the required 20% reduction.
- **Competitiveness:** 0.074115 is below 1.10 times the best of the three other
  benchmarks, the fitted power; that threshold is **0.103820**. This is a
  descriptive tolerance, not a statistical noninferiority test.
- **Separate contextual-information comparison:** the primary error is
  **48.85% lower** than unigram entropy, exceeding the declared 10% reduction.

The primary error is also **21.47% lower** than the fitted power and **27.38%
lower** than same-text duration. These latter gains are reported comparisons,
not additional requirements selected after seeing the result. The same-text
benchmark matters because all languages read translations of the same messages;
the observed advantage is not accounted for by transferring message identity
alone in this cohort.

![Speech-capacity transfer and all frozen alternatives](../results/speech-capacity-2026-10-17/transfer.png)

## Every target language and the limits of the average

The duration ratio is `exp(e_l)`: predicted divided by observed geometric mean
duration with the stated within-language weights. Ratios below 1 mean that the
model predicts speech that is too fast. An asterisk marks entropy extrapolation.

| Language | Source family | Mean signed log error e_l | Duration ratio | Reading log error |
|---|---|---:|---:|---:|
| Mandarin (CMN) | Sino-Tibetan | +0.003714 | 1.003721 | 0.088712 |
| Cantonese (YUE) | Sino-Tibetan | −0.107136 | 0.898404 | 0.109997 |
| Finnish (FIN) | Uralic | −0.029652 | 0.970783 | 0.063973 |
| Hungarian (HUN) | Uralic | −0.161389 | 0.850961 | 0.164911 |
| Basque (EUS)* | Basque | −0.109113 | 0.896629 | 0.128087 |
| Japanese (JPN)* | Japanese | −0.001647 | 0.998354 | 0.051895 |
| Korean (KOR) | Korean | −0.026310 | 0.974033 | 0.083453 |
| Thai (THA)* | Tai-Kadai | −0.183522 | 0.832334 | 0.184926 |
| Turkish (TUR) | Turkic | −0.078084 | 0.924887 | 0.116852 |
| Vietnamese (VIE)* | Austroasiatic | +0.043295 | 1.044246 | 0.101421 |

Family errors are **0.055425** for Sino-Tibetan and **0.095520** for Uralic.
Each other family contains one test language, so its error is the absolute
signed log error shown above. These eight errors average to the primary result.
Thai is the largest language-level miss: the predicted duration is **16.77%
shorter** than observed, a multiplicative discrepancy factor of **1.201441**.
That narrowly exceeds a factor 1.20 for this language; the frozen rule bounds
the average, not every language. The largest individual conditional-model error
is **0.452336** in absolute log units, factor **1.571981**, for a Hungarian
reading of P0. This post-evaluation descriptive maximum does not alter the
decision rule.

## Scientific contribution and remaining limits

Independent written-corpus entropy improves prediction of measured speech
duration across a fixed language-family split. A single capacity calibrated
on one family transfers better than all four declared alternatives, including
a two-parameter power and a shared-message benchmark. This is a concrete
advantage of specifying informational cost before the target response is used.

The equal-capacity interpretation is already part of the original publication.
The present contribution is a reproducible, locally frozen transfer comparison
with explicit competing predictions and complete error reporting. It does not
distinguish orthopolity from the established information-rate account, establish
neutral allocation, demonstrate a conserved metabolic resource, or identify
the causal mechanism behind similar capacities. Equal capacity is the tested
hypothesis, rather than a budget imposed independently by the experiment.

Rounded corpus entropy estimates and their uncertainty are not propagated.
Canonical syllable counts need not equal each speaker's realized articulation.
Shared translated texts, related languages, selected speakers and rehearsed
reading limit generalization to spontaneous communication. Source-defined
family labels determine the weights; eight families do not support a precise
population-level significance claim. Uneven calibration text coverage and the
unresolved 2,288/2,265 source discrepancy remain qualifications. No confidence
interval is inferred from the many related readings.

Further work should use an independent corpus and a distinct prediction, such
as an explicitly modeled change in production constraints. These target
durations are now exposed: a new correction fitted to Thai, Hungarian or other
residuals would be exploratory until tested elsewhere. The earlier human-foraging
candidate remains stopped at [design qualification](human-source-qualification-2026-10-17.md);
its programmed blocks did not supply the proposed cost intervention or a
distinct allocation prediction, and participant outcomes were not accessed.

## Verification and reproduction

Eight synthetic and access-control tests precede the design freeze. They
recover conditional-capacity and constant-syllabic worlds, exercise the fitted
power, distinguish language-mean from reading errors, verify hierarchical
weighting, and ensure poisoned held-out durations cannot affect forecasts.
The independent verifier uses separate source parsing, 50-digit Decimal
arithmetic, nested means and centered power regression. It checks **17,658
numeric quantities** before target evaluation and **25,472** afterwards. The
largest final absolute numerical difference is **1.45e-14**. Code review finds
the runner and verifier consistent with the frozen weighting and decision
rules; numerical agreement is not a measure of source or physical uncertainty.

The result SHA-256 is
`9cbcb4e84e725f67ab99ac626d924067fc8b1cb4e3a275bb1517b7701ec35ded`.
An offline replay on 19 October reproduces forecasts, scores, independent
verification and the figure **byte-for-byte**. Reproduce into a new directory:

```sh
MPLCONFIGDIR=build/matplotlib make speech-capacity \
  PY=build/main-venv-2026-10-09/bin/python \
  STUDY_OUTPUT_ROOT=build/reproductions/NEW
```

The frozen source, design and forecast checks run before evaluation. The full
[result](../results/speech-capacity-2026-10-17/result.json) retains every target
and every model's language/family scores; the
[verification record](../results/speech-capacity-2026-10-17/verification.json)
records input and output hashes.
