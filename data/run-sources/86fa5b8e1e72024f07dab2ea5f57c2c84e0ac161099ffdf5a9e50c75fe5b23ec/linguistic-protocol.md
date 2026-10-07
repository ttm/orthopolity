# Linguistic resource transfer: frozen analysis specification

7 October 2026. This is a retrospective study of a familiar public corpus,
motivated by the user's suggestion of word length and phonetic resources.
Published corpus metadata and linguistic regularities are already known. It is
not an external preregistration, a new data collection, or a globally blind test.
The official test split will first be downloaded and decoded after the present
protocol, implementation, configuration, and training fit have been hashed in
`data/linguistic-resources/2026-10-07/freeze.json`.

## Sources and units

Use Universal Dependencies English EWT release 2.18, immutable commit
`b7711cce01cdd4f5fcc0a8199b8a50d951b16c0c`, and CMUdict commit
`74790861f652b15e4ac49015a90074ad62a27690`. Preserve source bytes, receipts,
README files and licenses. EWT annotations/database rights are CC BY-SA 4.0;
the underlying web texts have mixed rights and are not thereby relicensed.
CMUdict's retained license applies to its pronunciation dictionary.

The observations are word occurrences. The concentrations are distinct written
word types, with counting measure on a fixed vocabulary. Extract Unicode letter
runs with internal straight or curly apostrophes from the original `# text`
sentence, after NFC normalization. Lowercase, normalize curly apostrophes, and
retain only ASCII letters and internal apostrophes. Punctuation and digits
delimit words; hyphens split words; contractions remain single words. This avoids
UD syntactic pieces such as `ca` and `n't`. No stemming or lemmatization.
Count letters $L$ excluding apostrophes. Count pronunciation symbols $P$ in the
unnumbered canonical CMUdict entry, excluding alternate numbered entries; stress
digits modify a symbol and do not contribute additional phonemes. Orthography
and dictionary pronunciation are measured independently of the target counts.
Neither feature measures sonority, acoustic energy, speaking duration, or
physical articulatory work.

## Training and the held-out environments

Fit on official training-split `email`, `weblog`, and `newsgroup` sentences only.
Choose the vocabulary from this subset alone: at least five occurrences and a
canonical dictionary pronunciation. The primary transfer target is official
test-split `reviews` and `answers`, whose genres are absent from fitting. The
secondary target is official test-split `email`, `weblog`, and `newsgroup`.
The development split is unused. The training file includes other genres;
their metadata/text hashes may be parsed for exclusion audits but their counts
must not enter vocabulary selection, parameter estimation, or model selection.

Exclude a test sentence if its exact original text occurs anywhere in the
official training file, including training genres omitted from fitting. Preserve
its sentence ID, document ID, text hash and excluded counts in a ledger. Retain
all other test sentences, including repetitions within the test set. Audit
document-ID overlap with both fitted and complete training sets. If overlap
exists, report it and retain it; do not silently change the frozen sample.

## Fixed model family and competitors

On the same fixed vocabulary, fit the constrained family

$$p(w)=\frac{L_w^{-\theta_L}P_w^{-\theta_P}}
 {\sum_vL_v^{-\theta_L}P_v^{-\theta_P}},\qquad\theta_L,\theta_P\geq0.$$

Interpret $Q_w\propto L_w^{\theta_L}P_w^{\theta_P}$ as an inferred candidate
effective symbolic cost under neutral equal allocation. This parameterization
does not identify a unique physical resource or an independently measured
constraint profile. Words with the same $(L,P)$ necessarily receive equal
predicted frequencies; lexical, semantic and contextual differences are outside
this model and must not be relabeled as measured constraints.

Compare exactly six forecasts: uniform word types; fixed inverse letter count
$1/L$; fitted nonnegative letter power; fitted nonnegative composite power;
fitted $\exp(-\lambda L)$ with $\lambda\geq0$; and a training unigram with fixed
additive smoothing 0.5. Fit by conditional multinomial likelihood on training
tokens, using deterministic convex optimization and its projected-gradient
check. Preserve fitted coefficients, boundary flags, information eigenvalues,
conditioning and feature correlation. Do not refit any model after test access.
No fitted Zipf exponent, new vocabulary, alternative pronunciation, or selected
tail will be introduced after viewing the transfer result.

## Scores, uncertainty and exclusions

The primary score is held-out mean negative log probability, nats per retained
token, conditional on this fixed vocabulary. The primary contrast is composite
minus letter-power loss; negative favors the composite. Report all models,
both transfer groups and every genre, including coverage, excluded mass, and
document counts. Exclusions distinguish non-ASCII letter runs, dictionary absence,
training count below five, and unseen training types. Retain per-document count
and loss totals, plus per-type counts and probabilities.

Use 2,000 paired document bootstrap resamples (seed 20261007) for conditional
95% percentile intervals of loss differences. Resample complete documents with
replacement within each reported group; recompute token-weighted ratio-of-sums
scores. No token-iid uncertainty or refitting in the bootstrap. These intervals
condition on the frozen training fit and observed corpus collection, assume
documents exchangeable within the reported group, and do not capture author,
thread, website or training uncertainty. Report zero-token documents and any
bootstrap replicate with no retained tokens.

Describe word-type count total variation, letter-resource shares $N_wL_w$ and
composite-resource shares $N_wQ_w$ against uniform word-type shares. Also report
their allocation by letter length with the type multiplicity made explicit.
These are descriptive finite-corpus profiles, not equivalence tests. A common
feature pair creates an exact structural equality in the candidate forecast;
observed heterogeneity within those pairs is retained.

## Outcomes and archival policy

Retain every score, exclusion and failed transfer. Any implementation repair
after test exposure must be disclosed and the original executed files retained;
it cannot restore unseen-outcome status. Produce an offline replay, source and
algorithm SHA-256 provenance, fixed-fit manifest, numeric tables and a figure.
The empirical result evaluates this restricted resource candidate. A result
against it neither identifies all relevant linguistic resources nor adjudicates
the unrestricted general-law proposal.

Sources: [UD English EWT](https://universaldependencies.org/treebanks/en_ewt/),
[pinned EWT source](https://github.com/UniversalDependencies/UD_English-EWT/tree/b7711cce01cdd4f5fcc0a8199b8a50d951b16c0c),
[pinned CMUdict source](https://github.com/cmusphinx/cmudict/tree/74790861f652b15e4ac49015a90074ad62a27690).
