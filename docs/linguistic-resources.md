# Linguistic resources: an inverse model transferred across genres

7 October 2026. Run `linguistic-resources-2026-10-07`.

A two-feature symbolic resource inferred from email, weblog and newsgroup text
improves word-frequency prediction in held-out reviews and answers. Its fixed
forecast improves mean conditional negative log probability by 0.1843 nats per
token over a fitted letter-only power model. A lexical unigram remains much
more accurate, and the observed resource allocation remains far from uniform
over word types. The result therefore supports transfer of a restricted
composite-resource candidate, without identifying a physical linguistic
resource or establishing neutral allocation in language.

## Resource, concentrations and the relation to Zipf's law

A word type is a distinct written form; a token is one occurrence. For type
$w$, the candidate letter expenditure is $N_wL_w$, where $N_w$ is its token
count and $L_w$ its letter count. On counting measure over word types, neutral
letter allocation would imply $p(w)\propto 1/L_w$. When types are grouped by
length, the neutral resource share of length $L$ is $M_L/M$, with $M_L$ types
of that length and $M$ types in the vocabulary. It is not a flat profile over
length classes.

Zipf's law uses frequency rank as its coordinate. Under the smooth
approximation $f(r)\propto r^{-\zeta}$, token expenditure per log rank is
$r f(r)$, while letter expenditure is $r f(r)L(r)$. Exact $\zeta=1$ makes
the first quantity constant, not the second unless length is constant. This
study does not fit a Zipf exponent or select a rank tail. The user's linguistic
suggestion motivates a directly measured resource candidate and an independent
transfer test; the abbreviation tendency alone does not determine this model.

The composite candidate is

$$Q_w=Q_0L_w^{\theta_L}P_w^{\theta_P},\qquad
 p_\theta(w)=\frac{L_w^{-\theta_L}P_w^{-\theta_P}}
 {\sum_{v\in\mathcal V}L_v^{-\theta_L}P_v^{-\theta_P}},\qquad
 \theta_L,\theta_P\geq0,$$

where $P_w$ counts pronunciation symbols in the canonical CMU dictionary entry.
Letters and phonemes describe different features of a written word and its
dictionary pronunciation. They do not measure sonority, sound energy, duration,
or articulatory work. The corpus contains text, not recorded speech. The
absolute scale $Q_0$ cancels from probabilities and is unidentified. No unknown
word-specific constraint profile is fitted. Consequently, semantic, contextual
and lexical discrepancies remain unexplained discrepancies of this candidate.
Context-dependent information has an established relationship with word length
in [Piantadosi, Tily and Gibson (2011)](https://doi.org/10.1073/pnas.1012551108).

## Data and exposure

The retained inputs are [Universal Dependencies English EWT](https://universaldependencies.org/treebanks/en_ewt/),
release 2.18 at commit `b7711cce01cdd4f5fcc0a8199b8a50d951b16c0c`, and
[CMUdict](https://github.com/cmusphinx/cmudict/tree/74790861f652b15e4ac49015a90074ad62a27690)
at commit `74790861f652b15e4ac49015a90074ad62a27690`. Source receipts retain
immutable URLs, byte sizes, retrieval timestamps and SHA-256 hashes. The
sources include both licenses and README files: EWT annotations/database
rights are CC BY-SA 4.0, while the underlying web texts retain mixed rights.
Keeping those notices does not relicense the underlying text.

The [protocol](linguistic-protocol.md), algorithm, configuration, tests,
training sources and fitted forecasts were hashed at 13:39:25 UTC on 7 October
2026 in [freeze.json](../data/linguistic-resources/2026-10-07/freeze.json).
The pinned official test file was acquired at 13:39:49 UTC, after that freeze,
and then decoded. No algorithm or fitted parameter changed after acquisition.
This is a retrospective analysis of a familiar public corpus, with a locally
held-out result, not external preregistration, new data collection, or a claim
of globally unseen data. The development split was unused.

Words are extracted from each original `# text` sentence rather than UD's
syntactic token pieces. NFC-normalized Unicode letter runs with internal
apostrophes are lowercased; curly apostrophes are normalized; only ASCII-letter
words with internal apostrophes are retained. Hyphens split words; contractions
remain single words. Letters exclude apostrophes, and stress digits do not
add pronunciation symbols. Alternate numbered pronunciations are unused.

The selected training genres contain 7,188 sentences in 83 documents, with
99,050 ASCII word occurrences. A type enters the vocabulary if it occurs at
least five times in those genres and has a canonical dictionary pronunciation.
This leaves 2,623 types and 83,635 training tokens. The remaining official
training genres supply exact-text hashes for duplication checks but contribute
no fitting counts. Across the full training file there are 12,544 sentences
and 540 documents.

The official test file has 2,077 sentences. Removing exact original-text
matches against the complete training file excludes 93 sentences, containing
110 candidate word occurrences and 105 vocabulary tokens. Their sentence and
document IDs, text hashes and counts remain in the
[duplicate ledger](../results/linguistic-resources/duplicate-exclusions.csv).
There is no test document-ID overlap with either the complete training set or
the fitting subset. Repetitions internal to the test file remain as specified.

| Evaluation group | Documents | Sentences | Retained tokens | Candidate word occurrences | Coverage |
|---|---:|---:|---:|---:|---:|
| Primary: reviews + answers | 253 | 960 | 7,329 | 9,439 | 77.65% |
| Secondary: email + weblog + newsgroup | 63 | 1,024 | 9,618 | 12,121 | 79.35% |

These denominators follow exact-text exclusion. The primary omitted tokens
comprise 321 dictionary-absent occurrences, 890 dictionary words unseen in
fitting genres, 898 dictionary words below the training threshold, and one
non-ASCII letter run. The secondary omissions are respectively 475, 855, 1,173
and zero. Reasons are mutually exclusive in that order; all are retained in
[word-exclusions.csv](../results/linguistic-resources/word-exclusions.csv).
The scores condition on membership in the frozen vocabulary and do not assess
prediction of omitted words.

## Frozen fit and competing forecasts

Conditional multinomial fitting gives

$$\widehat Q_w\propto L_w^{0.515253}P_w^{1.827530}.$$

The letter-only model has exponent 1.701248; the exponential letter model has
coefficient 0.481615. Neither composite coefficient reaches its nonnegative
boundary. The projected-gradient maximum is $6.86\times10^{-10}$, and the
per-token information eigenvalues are 0.043018 and 0.501279, giving condition
number 11.65. The unweighted log-feature correlation is 0.8710. Thus the two
features are correlated but the fitted information is nonsingular in this
sample. These diagnostics are conditional on the declared feature family;
they are not uncertainty intervals for a physical resource law.

There are only 83 distinct $(L,P)$ feature pairs among 2,623 word types. Every
type with the same pair receives the same model probability, even when their
observed frequencies differ. The training unigram retains lexical identity
and uses fixed additive smoothing 0.5. It has substantially greater flexibility
than the resource models and serves as a predictive benchmark rather than a
resource interpretation.

| Frozen forecast | Primary loss | Secondary loss |
|---|---:|---:|
| Uniform word types | 7.872074 | 7.872074 |
| Fixed inverse letters | 7.405038 | 7.457176 |
| Fitted letter power | 7.239009 | 7.327707 |
| Fitted composite power | 7.054704 | 7.188966 |
| Fitted exponential letters | 7.194500 | 7.303954 |
| Training unigram | 6.136038 | 6.199363 |

Loss is mean negative log probability in nats per retained token; lower is
better. The predeclared primary contrast, composite minus letter-power loss,
is $-0.184305$, with conditional 95% paired document-bootstrap interval
$[-0.196656,-0.169626]$. Secondary transfer gives $-0.138741$ with interval
$[-0.151243,-0.125072]$. The composite also beats the fixed inverse-letter and
exponential-letter forecasts on these samples. The lexical unigram beats the
composite by 0.918666 nats per primary token, preserving a substantial failure
of the two-feature model to explain word identity.

| Genre | Composite minus letter-power loss | Conditional 95% interval |
|---|---:|---:|
| Answers | -0.192147 | [-0.212819, -0.165249] |
| Reviews | -0.176520 | [-0.188086, -0.164407] |
| Email | -0.148549 | [-0.173731, -0.129465] |
| Weblog | -0.136289 | [-0.155084, -0.116739] |
| Newsgroup | -0.125376 | [-0.153049, -0.092567] |

These are overlapping descriptive subgroup checks, not five independent
replications. Each interval uses 2,000 paired document resamples, seed
20261007, recomputing token-weighted ratio-of-sums losses. No document or
bootstrap replicate has zero retained tokens. The intervals condition on the
frozen training fit and observed corpus collection; they do not include
training uncertainty, word-feature measurement uncertainty, or dependence
among authors, threads or websites. Sampling documents as exchangeable within
the stated group is an assumption, not established by document-ID separation.

## Allocation interpretation and limits

The held-out gain shows that independent pronunciation information adds
transferable predictive structure to the restricted inverse model. It does
not uniquely identify the proposed cost: another model with contextual or
lexical features can predict the same counts, and these constituents do not
measure all linguistic resources. Ordinary lexical frequency provides a much
stronger forecast here.

The observed primary letter-resource shares have total variation 0.692929
from uniform word-type allocation. Reweighting by the inferred composite cost
gives 0.689375, still far from neutral. The corresponding secondary values are
0.581770 and 0.577365. These descriptive distances include finite-corpus zeros
and are not population equivalence tests. Aggregating by length produces a
closer-looking composite profile, but aggregation can conceal word-level
heterogeneity; both resolutions are retained. The composite resource distance
is actually larger than the letter-resource distance in every separate genre,
which also precludes interpreting the pooled change as uniform improvement
of allocation at every resolution.

![Frozen linguistic forecasts and resource allocation profiles. Panel a reports primary conditional loss for all six forecasts. Panel b aggregates observed resource shares by letter length; the dashed reference is the share of vocabulary types at each length, corresponding to equal resource allocation per type.](../results/linguistic-resources/linguistic-resources.png)

The result realizes an empirical inference-and-transfer workflow: choose the
resource family and measure, infer composition in one environment, preserve
the fit, and assess a different environment against competitors. It supports
that restricted transfer claim. Establishing a physical linguistic resource,
neutrality after measured constraints, or a distinctive Zipf mechanism needs
additional independently specified observations and predictions. Failure of
the present two-feature candidate to explain lexical variation does not
identify those missing resources or constraints automatically.

## Reproduction and retained artifacts

Ten meaningful tests cover original-text parsing, contractions and Unicode,
training-only selection, canonical pronunciation, identifiable synthetic
coefficient recovery, a constrained optimum, normalization, exclusions,
paired document resampling and source mutation rejection. All pass.

```bash
PYTHONPATH=src python3.11 -m unittest discover -s tests -p test_linguistic_resources.py -v
python3.11 experiments/fetch_linguistic_resources.py
PYTHONPATH=src python3.11 experiments/run_linguistic_resources.py --stage evaluate
MPLCONFIGDIR=build/matplotlib PYTHONPATH=src python3.11 experiments/run_linguistic_resources.py --stage evaluate --output-dir build/reproductions/linguistic-resources
```

The first evaluation of a fresh output directory recomputes training and
requires exact equality with the frozen fit before decoding the held-out
corpus. Existing output directories are audited against hashes, never silently
overwritten. Offline verification checks pinned source membership and URLs,
receipt/manifest equality, sizes and hashes, followed by every frozen algorithm
and fit hash. The result directory contains 12 deterministic artifacts: config,
summary, coverage, document totals, scores, vocabulary and forecasts, type and
length profiles, both exclusion ledgers, and PNG/SVG figures. All 12 reproduced
byte for byte in a fresh offline run. The provenance file additionally records
completion time and runtime versions and is not expected to match in its
timestamp. Source receipts, fit and freeze remain under
`data/linguistic-resources/2026-10-07/`; results and output hashes remain under
`results/linguistic-resources/`.
