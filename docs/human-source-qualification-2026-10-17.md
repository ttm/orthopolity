# Human-source qualification: stop foraging, qualify a speech-capacity transfer

17 October 2026. No participant foraging outcomes or numerical speech durations
were decoded during this qualification. Original metadata, source programs,
published articles and receipts are retained under
`data/human-candidates/2026-10-17/`.

## Foraging does not provide the proposed intervention

Harhen and Bornstein (2023), [original article](https://doi.org/10.1073/pnas.2216524120),
and the [pinned task repository](https://github.com/noraharhen/Harhen-Bornstein-2023-Overharvesting-as-Rational-Learning/tree/780c5b117dff0eec2a85d8e9c9473b7eaf7dfc0f)
are accessible. The tree lists original participant files; none was acquired.
The program sets five 360,000-ms blocks, compensates digging delay for response
time, and uses a common 10,000-ms travel schedule. Published methods describe
one temporally correlated mixture of three patch types throughout these blocks.
This is not an independently assigned between-block cost intervention.

Code inspection also exposes a block-ending condition at 20 visited planets
alongside elapsed time (`task.js`, line 418), which would need reconciliation
before treating every block as an identical realized time budget. We did not
run the source program or infer how often this condition occurred.

The more fundamental issue is the missing distinct prediction. Marginal-value
theory compares incremental reward per additional time. It does not assert
equal accumulated reward or equal time allocation across patches. Time-budget
accounting alone does not determine behavior. Defining effective costs or
opportunity weights from realized visits or rewards would use the target to
specify the prediction. The authors already compare marginal-value, temporal-
difference and adaptive structure-learning accounts.

**Decision: stop before participant-data access.** This is a design qualification
finding, not an empirical rejection. A future experiment needs an explicit
resource-allocation mechanism with numerical responses distinguishable from
those rivals, plus independently randomized cost/depletion changes. A possible
evaluation measure is counting over prespecified participants and conditions;
it is neither log-orthopolic nor linear-orthopolic size allocation.

Published qualitative outcomes, aggregate tests/model comparisons and parameter
distribution summaries were exposed by web searches. No individual fitted
parameter array or participant outcome file was inspected. The initial Python
download failed local certificate verification; system curl subsequently
acquired the sources with TLS verification enabled.

## Independent speech predictors support a narrower test

Coupé et al. (2019), [original article](https://doi.org/10.1126/sciadv.aaw2594),
and [repository at 00798db1687a429349370e40e1a726deb35c1ef6](https://github.com/keruiduo/SupplMatInfoRate/tree/00798db1687a429349370e40e1a726deb35c1ef6)
supply canonical syllable counts, independently estimated written-corpus
entropies and measured pause-filtered speech durations. `ID` uses the previous
syllable within a word (or word-onset null); `ShE` omits that context. Neither
uses measured speech duration. Duration excludes manually identified pauses
longer than 150 ms; it is not total elapsed reading time or pure phonation time.
Canonical counts do not measure each speaker's realized articulations.

The publisher's S1 CSV and GitHub CSV agree byte-for-byte: 96,064 bytes,
SHA-256 `f4dde6def980ed4c461ad8fd666af64cbbaa967a2ac73702855fc70484c0732a`.
Both have **2,288 rows**, versus the article's stated **2,265**. The source R
setup does not explain a 23-row exclusion. All required columns are complete;
309 missing ages do not affect this analysis. There are no duplicate
language/speaker/text identities, and canonical counts and entropies are
consistent within their declared groups. Retain the discrepancy and every row.

The predictor-only audit finds 17 languages, 170 speakers and 15 text identities.
Seven Indo-European languages supply 789 calibration readings; ten languages
from eight other source-defined families supply 1,499 target readings. Each
language has ten speakers, with unequal text coverage in some calibration
languages. Training ID spans 5.29–7.09; Basque, Japanese, Thai and Vietnamese
extrapolate. These identities and predictor values were inspected before the
design, without converting or emitting any numeric Duration field.

The [frozen comparison](speech-capacity-protocol-2026-10-17.md) asks whether a
single inferred information capacity transfers across families, using independent
entropy inputs. It includes a same-text duration rival because the recordings
share translated messages. Success would support a bounded, established
information-capacity account; it would not distinguish orthopolity from that
account or identify metabolic costs. The approximately 39 bits/s published
aggregate, speech-rate/entropy ranges and reported correlations were already
known and must not be called independent calibration measurements.
