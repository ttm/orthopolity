# Frozen speech-capacity transfer across language families

17 October 2026. Commit this document, configuration, algorithms, verifier,
tests and source receipts before decoding calibration durations. Commit verified
forecasts before decoding any non-Indo-European numerical duration. This is
retrospective archival validation with known published summaries, not an unseen
discovery or external preregistration.

## Question, resource and reference measure

Does a common inferred information capacity transfer from seven Indo-European
languages to ten languages from eight other source-defined families? Conditional
syllable entropy ID comes from independent written corpora; NS is canonical
syllables in a translated message; D is measured speech duration after removing
pauses longer than 150 ms. Test Dhat=b NS ID with C=1/b in bits per second.
Equal capacity is the hypothesis, not an independently imposed budget. C is
inferred and neither entropy nor duration measures metabolic expenditure.

Reference measure is counting: equal families, languages within family,
speakers within language, and each speaker's available texts. This is neither
log-orthopolic nor linear-orthopolic size allocation. The primary estimand is
language-level geometric mean duration (equivalently mean log-duration bias),
not individual reading accuracy or a universal demographic parameter.

## Fixed source and cohort

Use `InfoRateData.csv` at repository commit
`00798db1687a429349370e40e1a726deb35c1ef6`, SHA-256
`f4dde6def980ed4c461ad8fd666af64cbbaa967a2ac73702855fc70484c0732a`.
Publisher S1 bytes match. All 2,288 rows remain, despite the paper's unexplained
2,265 count. Exact rows/columns, download receipts and predictor-only inspection
are in the [source qualification](human-source-qualification-2026-10-17.md).

Calibration: CAT, DEU, ENG, FRA, ITA, SPA, SRP (789 readings).
Targets: CMN/YUE (Sino-Tibetan), FIN/HUN (Uralic), EUS (Basque), JPN (Japanese),
KOR (Korean), THA (Tai-Kadai), TUR (Turkic), VIE (Austroasiatic), 1,499 readings.
Preserve publication family labels. Each language has ten speakers and all 15
text identities at language level. Missing speaker/text cells are not imputed.
Age and sex are not fitted; automatic acoustic measurements are not predictors.

Stop on a changed source hash, cohort/identity count, duplicate
language/speaker/text, inconsistent within-language entropy or canonical
language/text count, or nonpositive/nonfinite required numeric value. No
outcome-based filtering. Missing benchmark text coverage stops prediction.
Individual numeric target Duration fields are converted only after sealing.
Predictor inspection already identifies Basque, Japanese, Thai and Vietnamese
outside calibration ID support [5.29,7.09]; retain all without clipping.

## Five models, all fixed before calibration

Use natural logarithms and weighted squared log-duration error. Training weights
give equal languages, then speakers, then available texts (one training family).
Fit no target-specific parameter. Store every target's log-duration forecast.

1. Conditional information: log Dhat=log NS+log ID+a. The fitted a is the
   weighted mean of log D-log NS-log ID; C=exp(-a).
2. Constant syllabic rate: log Dhat=log NS+a, with its own fitted a.
3. Unigram information: log Dhat=log NS+log ShE+a, with its own fitted a.
4. Fitted density power: log Dhat=log NS+a+gamma log ID, weighted least squares
   with unconstrained gamma. It has only seven distinct language-level inputs;
   retain extrapolation and unstable forecasts. Stop if the design is singular.
5. Same-text duration: for each text, average training log D with equal
   languages represented for that text, then equal available speakers.
   Predict that duration for every target translation of the same text.

The fifth comparator distinguishes independent entropy's contribution from
shared message identity. Published 39 bits/s is exposed context, never a fixed
calibration constant. No clipping, nonlinear post-fit correction or alternative
split chosen after seeing target errors.

## Evaluation and decision rules

For each language compute e_l as mean(log Dhat-log D), first averaging each
speaker's available readings, then speakers. Primary E is the family-balanced
mean of |e_l| (equal languages within each family). Report all language signs,
exp(e_l), family errors, maximum |e_l| and equal-language sensitivity. Also
report the hierarchical mean of individual |log Dhat-log D|. That secondary
metric does not allow within-language cancellation and cannot replace E.

Three requirements define the descriptive joint rule:

- E_conditional <= log(1.20). This bounds an average multiplicative discrepancy,
  not every language or every reading to within 20%.
- E_conditional is at least 20% lower than E_syllabic.
- E_conditional is no more than 1.10 times the lowest E among unigram,
  fitted-power and same-text models. This is a declared competitiveness
  tolerance, not statistical noninferiority or a claim of beating those models.

Report separately whether conditional entropy reduces E by at least 10% versus
unigram entropy (contextual-information advantage). Report every comparison
regardless of its sign. A zero comparator error makes its relative gain
undefined and the associated gain criterion fail; a zero best-benchmark error
requires zero primary error for competitiveness. No confidence interval or
population-level significance is inferred from these few families.

## Verification and interpretation

Synthetic data must recover conditional-capacity and constant-syllabic worlds,
the unconstrained power, hierarchical weights and the primary/reading error
distinction. Poisoned target durations must not affect calibration or forecasts.
An independent verifier uses separately parsed source fields and Decimal
arithmetic for weighted means, centered power regression and error aggregation.
Verify forecasts before sealing and results after evaluation.

Use Python 3.11. Run `experiments/run_speech_capacity.py --stage predict
--freeze-commit DESIGN --output results/speech-capacity-forecast-2026-10-17`,
then verify and commit forecasts. Evaluate with `--stage evaluate
--freeze-commit DESIGN --prediction-commit FORECAST --predictions
results/speech-capacity-forecast-2026-10-17/predictions.json --output
results/speech-capacity-2026-10-17`. Set PYTHONPATH=src.

Publication aggregates and the equal-information-rate interpretation are known.
The source's entropy estimates are rounded and uncertain; uncertainty is not
propagated. Translated texts, related languages, selected speakers and rehearsed
reading limit generalization. A positive result supports transfer of this known
capacity account, not unique evidence for orthopolity or neutral allocation.
A failure remains attached to this specified measurement and transfer model;
explanations fitted to these target durations will be exploratory.
