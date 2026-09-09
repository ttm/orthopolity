# Remaining work

The repository now contains a complete critical manuscript, corrected definitions, a direct
audit of the supplied essay, and reproducible exploratory analyses. It is a research draft,
not a submission-ready announcement of a new law.

## Completed in this revision

- Read the 2017 manuscript and 2024 essay directly; distinguish their linear allocation from
  the logarithmic hypothesis.
- Rewrite [paper.md](paper.md) around defensible results and prior art.
- Correct the ensemble, variance, preregistration, and interpretation claims.
- Correct likelihood, flatness, convolution, and pass-rate calculations with regression tests.
- Preserve the historical protocol and raw snapshots while disclosing retrospective changes.
- Identify impossible StudyID_07 size bounds and report an explicit exclusion sensitivity.
- Align the supporting documents with the revised assessment.

## Work needed before a journal submission

1. **Resolve source conventions and units.** Audit every contributing study's estimand, bin
   definition, axis units, size bounds, sample identifiers, and reported error coverage.
   StudyID_07 requires a documented correction; the observed slope cannot supply one.
2. **Choose the article's scope and venue.** The current contribution is a critical synthesis
   and exploratory assessment. A stronger original-research claim requires new predictive
   evidence. Select a venue only after comparing its current scope and novelty expectations.
3. **Verify declarations.** Agree authorship, contributions, funding, acknowledgements, and
   any required assistance disclosure. Do not copy declarations from the 2017 manuscript.
4. **Finalize data notices.** Resolve inconsistent GLOSSAQUA licence metadata between author
   and publisher deposits, and verify applicable terms for the frozen Hatton summary tables.
   The code's package metadata does not license third-party inputs.
5. **Format and render the manuscript.** Apply the chosen venue's reference and layout rules,
   validate all bibliographic entries, and inspect the final figures and rendered document.

These are submission requirements, not reasons to leave the present scientific assessment
unwritten. The Markdown manuscript already states the contribution and its limits.

## Optional work for a stronger empirical paper

A new study needs independently justified resource and coordinate choices, a defined
population of systems, validated raw or binned resource totals, a declared domain and
equivalence margin, and a model of the actual sampling design. Hold out new observations
or register a future analysis before inspection. Test complete profiles as well as slopes.

A multi-site design with repeat visits can estimate spatial and temporal components when
its assumptions and sample size permit. Comparing variance estimates from different taxa
and studies is not a substitute.

An ensemble question must specify its target: mean slope, median slope, mean normalized
profile, or resource-weighted aggregate. The present data do not make those interchangeable.

## Historical leads

Earlier work investigated PSSdb as a possible additional source and recorded access failures.
Those failures describe particular attempts, not a permanent outage or proof that all routes
are exhausted. Recheck access when a concrete analysis design warrants it. A new dataset is
not automatically an independent replication if its conventions, coverage, or dependence
differ.

Earlier numbered roadmap entries and conclusions are retained in Git history. Claims that
Gaussian adequacy, a universal dispersion parameter, or a temporal variance bound were
“completed” are superseded by [source-audit.md](source-audit.md).
