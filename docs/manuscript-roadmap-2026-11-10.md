# Roadmap: a clear natural-law proposal and a cosmological extension

Agreed with the lead author on 10 November 2026; completed 11 November 2026. Baseline: clean `main` at
`3bb224d`, after the complete replay and manuscript evidence review. This plan
implements the author's requested presentation and theoretical exploration;
it does not reopen the closed empirical searches in [status.md](status.md).

## Intended result

The main article will explicitly **propose orthopolity as a natural law** and
explain it through one concrete picture before developing the mathematics.
An orthopolic umbrella will connect exact accounting, allocation mechanisms,
physically predicted departures and exploratory interpretations, with their
different evidential roles visible. Gaussian aggregation will be presented as
a complementary explanation that can coexist with resource allocation.

Supporting material will develop **orthopolity as a cosmological conjecture**:
finite-domain log-orthopolic allocation of stellar number or mass among cosmic
structures. It will distinguish this proposal from the cosmological constant
Lambda and from the standard spatial cosmological principle. Published
astronomical distributions will supply signs and departures for exploration;
they are not a newly executed empirical test.

## Sequence and completion criteria

| Phase | Work and repository destination | Completion criterion | State |
|---|---|---|---|
| 1. Record scope | This roadmap, current roadmap and status | Author's intent, baseline and evidence boundaries are explicit | Complete |
| 2. Explain the law | Main opening and Section 2; a deterministic figure in `docs/figures/` with source in `experiments/` | A reader can follow count × resource per object = class resource before formal notation; log/linear measures and normalized densities are unambiguous | Complete |
| 3. Organize the umbrella | Main mechanisms/discussion and glossary | Exact realizations, conditional predictions and suggestive readings are distinguished; Gaussian aggregation is not treated as an exclusive alternative | Complete |
| 4. Develop cosmic implications | `cosmological-extension.md`, supporting S6 and references | Stars per galaxy, complete inventory, richness/mass distributions, published signs and departures, conditional mechanism and second prediction are stated with primary sources | Complete |
| 5. Reconcile repository guidance | README, current roadmap, scope notes and evidence review | Current entry points agree; older results and historical decisions remain identifiable | Complete |
| 6. Verify and render | Figure replay, terminology, manuscript converter, source/link checks, registry verification and both PDFs | No altered frozen study results; equations reviewed; builds and visual inspection pass; final status records results | Complete |

The roadmap is a working record: update states and the outcome below as work
finishes. The prior [evidence review](manuscript-evidence-review-2026-11-10.md)
remains the numerical claim map; new conceptual claims receive a separate
addendum rather than changing its historical comparisons silently.

## Scientific decisions fixed before writing

1. **Status of the law.** State the natural-law proposal directly. Exact
   mathematical conclusions retain their hypotheses; the proposed general
   physical reach is not described as already established universally.
2. **Meaning of equality.** Specify objects, resource, domain, reference measure
   and whether the target is a snapshot, expectation or time average. With
   resource cost proportional to `k^d`, log-orthopolic allocation predicts
   linear count density proportional to `k^(-d-1)`; linear-orthopolic allocation
   predicts `k^(-d)`. A normalized density changes the normalization constant.
3. **Illustration.** Four equally weighted geometric classes have sizes/costs
   `(1, 2, 4, 8)`, counts `(8, 4, 2, 1)`, resource `(8, 8, 8, 8)` and total 32.
   This is a constructed finite log-orthopolic grid, not measured data or a
   continuous-bin integration result.
4. **Umbrella.** An independently specified mechanism or resource makes a
   physical interpretation substantive. Choosing `q=1/p` after seeing a
   distribution only constructs equality. It becomes a test through independent
   inputs and an additional prediction, preserving the repository convention.
5. **Cosmic scope.** Fix epoch, volume, finite size interval and disjoint object
   inventory. Stellar number, stellar mass and dark-matter mass are different
   resources; stellar mass does not automatically measure star counts. Nested
   descriptions of the same matter cannot be added as separate shares.
6. **Published signs.** Treat GAMA, COSMOS2015, the stellar initial mass function
   and Aquarius as literature examples with reported regimes and qualifications.
   The Aquarius result is a simulation. No new catalogue fit, frozen forecast,
   registration or observational confirmation is claimed.
7. **Physical content.** A finite-domain mass-flow model may derive a neutral
   profile under explicit stationary/source/transport assumptions. Deriving a
   profile in that model does not establish its assumptions for cosmic assembly.
   A useful next test must predict an amplitude, profile change or transfer from
   independent inputs, and compare with established assembly models.

## Verification and preservation

Use the existing Python 3.11 environment. Check deterministic figure outputs,
arithmetic, manuscript conversion, terminology and local links. Rebuild both
PDFs through `make paper`, review warnings, render the changed pages and inspect
the complete documents for layout regressions. Verify the retained run registry.
Run broader tests if code changes justify them; the completed baseline `make all`
already passes 711 Python tests and 27 JavaScript tests. Do not rerun or change
historical analyses merely for an editorial revision.

Preserve all frozen inputs, forecasts, protocols, registered results and their
negative outcomes. Work on `main`. Commit/push are separate delivery actions;
this roadmap does not imply a new release or external submission.

## Outcome

All six manuscript-revision phases are complete. The main article and
supporting S6 implement the approved structure; the standalone cosmic report
and explanatory PNG/SVG are retained with source. Independent review corrected
normalized-density labels, additive-resource premises and three condensed-study
scope phrases. Supporting S1--S5 remain byte-identical to baseline.

The final 13-page article and 77-page supplement pass visual review and repeat
byte-identically. Eight targeted tests, registry verification and local links
pass; [the review record](manuscript-revision-review-2026-11-11.md) supplies the
commands, hashes and limits. This completes the agreed revision, not the
proposed future cosmic validation. Qualifying independent public inputs and a
separate target is the next scientific phase. No new empirical run is claimed.
