# Ongoing research: resume here

Last updated: 5 October 2026. This is the mutable handoff document for ongoing
work. It records the current objective, decisions, completed work and exact next
steps. Immutable executed studies belong in the run registry; this document does
not replace their frozen protocols or results.

## Objective and standing instructions

Execute the [available-data programme](available-data-programme.md), beginning
with the published nutrient-pulsed chemostat records. Keep work resumable across
coding sessions. The user authorizes implementation, public-data retrieval,
analysis, documentation, and commit/push. No new laboratory, field or hardware
measurements: all empirical evidence must come from existing data. Simulations
may calibrate methods and clarify model predictions.

Preserve all previously registered inputs, algorithms and outputs. Never repair
a failed forecast by changing its frozen costs, reference, sample, or threshold.
Separate measured traits, assigned inputs, development-fitted parameters and
latent quantities. Published outcome summaries have been read; this is
retrospective validation, not global blinding or prospective data collection.

## Current state

- Branch: `py314-and-package-names`, pushed to `origin`. All four
  available-data allocation/transfer studies and the subsequent respiration
  calibration diagnostic are complete and registered. Registry: 23 records, 587
  retained file references. All 352 tests pass. Run the suite with
  `make test PY=python3.11`.
- [Archived cost transfer](archived-cost-transfer.md) (`archived-cost-transfer-2026-10-02`):
  a size-geometric carbon cost predicts held-out 25°C *Synechococcus* quotas
  best; strain identity predicts N and P better than size.
- [Chemostat response](chemostat-response.md) (`chemostat-resource-response-2026-10-02`):
  negative. No frozen forecast beat persistence on held-out food webs. The
  two-budget cost-ratio rule failed on score, size and direction, and no vessel
  recovered by day 12.
- [*Dunaliella* size budget](dunaliella-size-budget.md) (`dunaliella-size-budget-2026-10-02`):
  positive for budget closure with a geometric cost. In one shared medium,
  capacity in biovolume is flat across a 10.4-fold volume range, so cell
  number scales as $V^{-1.02}$. A frozen equal-biovolume forecast ($d=1$)
  predicted held-out treatments best (errors 0.124 and 0.179). Restoration
  after P deprivation left a size-dependent overshoot.
- Retained errata, none of which changes a score:
  - The chemostat nitrogen-budget field holds nmol/L, not µmol/L.
  - The *Dunaliella* archive's cell-size folder overstates volume by exactly 8
    ($(4\pi/3)LW^2$ from full axes). The study uses the correct copy.
- [Next-dataset audit](next-dataset-audit.md), completed 3 October: harvested
  herbaceous plant plots provide directly weighed aboveground dry mass among
  coexisting ramets. MALASPINA sieve fractions provide a separate chemical N/C
  stock candidate. Seven source-metadata snapshots and their receipts are
  retained in `data/neutrality-audit/2026-10-03/`. The audit itself evaluated no
  study; the subsequent plant study below closes its direct-stock measurement gap.
- **Plant-source exposure:** a header-only binary reader emitted numerical
  rows from CR-only CSVs. Both BFEC wetlands and all five RMBL files are
  conservatively treated as exposed. No fits or scores were computed. Any
  plant analysis is retrospective after raw outcome exposure; no later freeze
  can restore an unseen-outcome claim. See the audit and `exposure.json`.
  Plankton outcome tables have not been retrieved or decoded in this audit.
- [Plant biomass profile](plant-biomass-profile.md)
  (`plant-biomass-profile-2026-10-03`): ten directly weighed plot files, five
  BFEC development plots and five RMBL evaluation plots after raw exposure.
  Logarithmic neutrality ranks second for primary biomass TV (0.493 versus
  Pareto 0.470); all three trained count models outperform both neutral models.
  Every plot favors a different biomass template. Thirty missing masses and
  all exclusions remain in the ledger; a 112.55 g ramet above the frozen domain
  contains 24.50% of one plot's known mass. Synthetic calibration distinguishes
  normalized expected stocks from average normalized census shares and exposes
  severe iid-envelope failures under dependence. Ecological neutrality remains
  unresolved. Exact offline replay and isolated missing-manifest recovery pass.
- [Scientific assessment](scientific-assessment.md): modest original scientific
  contribution, strong transparency, weak evidence for a general natural law.
  Close prior metabolic cost/capacity work and existing spectrum methods narrow
  novelty. More records alone do not improve identification.
- [Two-archive plankton observation gate](plankton-observation-gate.md), completed
  4 October: the reviewed public evidence does not justify freezing the proposed
  nitrogen-stock equivalence study. MALASPINA has 43 station events, but relative
  class corrections/backgrounds and sampling dependence remain unresolved.
  BLOOFINZ derives many stocks using shared chemical composition means; chemical
  provenance/uncertainty and depth/organism-selection compatibility remain
  unresolved. Six exact metadata/methods files and receipts are retained.
  Neither raw nitrogen-stock table was acquired or evaluated. No new registry
  record, empirical verdict or manuscript revision results from this audit.
- [Reference-measure intervention design](measure-intervention.md), completed
  4 October: size-log and cost-log allocation agree under power costs but
  diverge under a physical additive cost. The pointwise abundance-response
  predictions have slopes −1 and −2 against the log cost multiplier. Exact bin
  integrals and an independently checked calculator provide a concrete test
  design. The three deterministic examples add no empirical observations and
  are not a registered study. Natural-regime eligibility and persistence through
  a cost change remain unestablished.
- [Size-versus-cost candidate audit](measure-candidate-audit.md), completed
  5 October: recovered 231 respiration rows from separate monoculture assays for six
  Ghedini community species. Signed and missing readings are retained. The rows
  include repeated dark periods, not 231 independent biological replicates.
  Seven metadata snapshots and two provider-checksummed archives are retained.
  The original community experiment measured size within each community and
  its headers name species size/count/biovolume fields. That opens a possible
  aggregate mean-size test without inventing taxon bins. Cost uncertainty,
  transfer and domain coverage still need qualification. No cost curve was
  fitted during that inventory. Published summaries have been seen.
- [Respiration calibration gate](ghedini-cost-calibration.md)
  (`ghedini-cost-calibration-2026-10-05`), completed 5 October: signed
  species-by-OD means, power versus power plus positive overhead, six whole-species
  and four whole-OD holdouts, two fit weightings and separate-OD sensitivity.
  Protocol/algorithms committed in `d49f0e6` before fitting. Equal-group fits
  effectively tie and give power-equivalent S/Q predictions. Species-RMS fits
  improve raw species-holdout RMSE by 35.7% but fail on the smallest-species
  extrapolation; the interior standardized score improves. Across the declared
  sensitivity set, S means span 3.408–45.038 µm³ and Q means 3.408–187.360 µm³,
  with zero minimum paired gap. The frozen qualification gate fails. Registered
  as a calibration diagnostic, not an allocation study. Exact numerical replay
  and figure reproduction pass. Numerical community rows remain uninterpreted;
  manuscript/PDF and earlier registered studies remain unchanged.

## Next actions, in priority order

The [scoped natural-law route](natural-law-route.md) proposed a finite
two-archive gate. That gate is complete and currently closes the proposed
ecological law test. The Leg 8 review exposed published dry-mass/isotope
summaries, recorded separately from the registered plant exposure input.
No later freeze can establish global blinding.

1. **Reopen the plankton route only on additional observation evidence.** The
   [completed gate](plankton-observation-gate.md) identifies the required changes:
   traceable class corrections or defensible bias bounds and sampling/dependence
   for MALASPINA; original assay linkage or equivalent evidence supporting the
   shared chemical estimates for BLOOFINZ; a declared compatible depth and
   organism-selection scope. These are evidence requirements, not a demand for
   every raw laboratory record or new measurements. A metadata-only tow listing
   cannot resolve the chemical gaps. Do not acquire outcomes, invent calibration
   bounds or substitute a descriptive catch comparison as a law verdict. The
   bounded public-source review is finished; avoid repeating it or automatically
   expanding a catalogue of similarly inadequate archives. Stock regularity
   itself does not require opportunity budgets; a feasibility explanation does.
2. **Preserve the failed curvature qualification; reopen on new evidence.** The
   [measure-intervention note](measure-intervention.md) supplies the cost-change
   comparison; repeating its algebra or adding more arbitrary simulations is
   unnecessary. An existing-data application needs coexisting objects, an
   independently calibrated non-power cost curve on a fixed size domain, an
   outcome-independent eligibility rule and sufficient observation information.
   A causal comparison additionally needs a documented physical cost change
   and an explicit assumption about which regime conditions persist. Bulk bin
   stock/count ratios do not supply boundary costs; separately grown monocultures
   do not supply coexistence. The [candidate audit](measure-candidate-audit.md)
   and [completed numerical gate](ghedini-cost-calibration.md) now close the
   recovered Ghedini additive-cost route. No model/weight/domain/margin change
   may rescue that run. Additional independent calibration evidence could
   justify a new protocol, but finding another fitting family on the same
   observations would not itself strengthen the evidence. The full 21-species
   source calibration was not recovered as a separate public table during the
   bounded public-source screen. Do not repeat the catalogue or that search
   without a specific new source lead.
   Community-specific mean sizes may support the ratio-of-expected-totals
   prediction for biovolume/count. It needs the same independently supported
   size domain as the cost forecast. Write the observable/domain/transfer and
   eligibility specification before reading numerical community rows. Do not
   require every individual size if a justified aggregate implication suffices,
   and do not substitute fixed taxon means for physical size distributions.
   No additive physical cost intervention is documented in these archives.
   Do not fit cost or regime membership to rescue either forecast. Preserve the plant
   finite-census/dependence findings as synthetic diagnostics. A generic
   sensitivity-analysis addition also overlaps the existing profile-calibration
   code and needs a concrete improvement before becoming a separate project.
3. **Manuscript.** [`docs/paper.md`](paper.md) now reports the plant comparison,
   Figure 3, outcome exposure and narrower scientific contribution. Revise it again only when
   a new registered study changes a conclusion. Rebuild with `make paper`, which
   needs TeX; the PDF is byte-reproducible from the manuscript's commit date.
4. Never edit a registered study. A corrective analysis gets a new run
   identifier and its own frozen protocol.

## Resume commands

```bash
git status --short --branch
PYTHONPATH=src python3.11 experiments/register_runs.py --verify
python3.11 experiments/fetch_neutrality_metadata.py --stage verify
make law-observation-metadata PY=python3.11
make measure-intervention PY=python3.11   # deterministic mathematical examples only
make measure-candidates measure-calibration PY=python3.11   # offline source/calibration qualification; no community score
make ghedini-cost-calibration ghedini-cost-calibration-report PY=python3.11  # exact replay; community outcomes closed
make archived-cost-transfer chemostat-response dunaliella-size-budget PY=python3.11   # offline audits
make plant-sources plant-biomass-profile PY=python3.11
```

A clone lacks the 98.7 MB chemostat bundle. These audits do not need it.
Run `make restore-chemostat-bundle PY=python3.11` only to replay the chemostat
source audit.

## Current files and ownership boundaries

- Size-versus-cost candidate inventory: `experiments/fetch_measure_candidates.py`
  separates acquisition from offline checksum/header replay; its default never
  interprets numerical data rows. `experiments/inspect_measure_calibration.py`
  reads only the independent calibration sheet A:I, stops on selected formulas
  and replays the retained qualification. Sources, plans, receipts, exposure and
  inspection outputs are in `data/measure-candidates/2026-10-04/`, the start-date
  directory spanning 4–5 October. Seven boundary/integrity tests are in
  `tests/test_measure_candidate_schema.py`. These are unregistered audit
  materials; source bytes and calibration readings must remain traceable. The
  later calibration diagnostic references immutable snapshots of its inputs.

- Respiration calibration, frozen: `src/orthopolity/cost_calibration.py`,
  `experiments/run_ghedini_cost_calibration.py`,
  `configs/ghedini_cost_calibration_2026-10-05.json`, and
  `data/ghedini-cost-calibration/2026-10-05/`. Fits, held-out forecasts and
  moment sensitivities are in `results/ghedini-cost-calibration/`. Live-source
  hashes and software versions must match for exact replay. Numerical fitting
  uses Python 3.11.6, NumPy 2.3.5 and SciPy 1.16.3; post-analysis figures use
  Matplotlib 3.10.7. Registration's own audit recomputes the numerical outputs;
  repeat registration is idempotent. Fourteen synthetic numerical/protocol
  tests cover the new analysis and leakage boundary. No community reader is
  part of this workflow.

- Chemostat sources and study: `experiments/fetch_chemostat_sources.py`,
  `experiments/run_chemostat_response.py`, `src/orthopolity/chemostat_response.py`,
  `src/orthopolity/gated_xlsx.py`, configuration plus amendments 1–2, and
  outputs in `data/chemostat-*/` and `results/chemostat-response/`. Frozen:
  evaluation and audit refuse changed source bytes.
- *Dunaliella* sources and study: `experiments/fetch_dunaliella_sources.py`,
  `experiments/run_dunaliella_size_budget.py`, `src/orthopolity/size_budget.py`,
  `src/orthopolity/rdata_reader.py`, and protocol, partition and amendment in
  `configs/dunaliella_size_budget_2026-10-02*.json`. Outputs are in
  `data/dunaliella-*/` and `results/dunaliella-size-budget/`. Frozen in the
  same way.
- Cost study, frozen: `experiments/run_archived_cost_transfer.py`,
  `src/orthopolity/archived_cost_transfer.py` and its outputs.
- Plant study, frozen: `experiments/fetch_plant_sources.py`,
  `experiments/run_plant_biomass_profile.py`, `src/orthopolity/plant_profiles.py`,
  `src/orthopolity/plant_observation.py`, protocol plus amendment, exact
  `data/plant-sources/` bytes and `data/plant-biomass-profile/` forecasts,
  calibration and membership. Results in `results/plant-biomass-profile/`.
  The separate figure manifest is a post-hoc presentation archive.
- Post-hoc report scripts (`experiments/report_*.py`) read retained outputs
  only and refuse to overwrite changed bytes.
- Registration of all four: `experiments/register_available_data.py`
  (`make available-data-registry PY=python3.11`). It is idempotent; add later
  studies to `STUDIES` without changing existing entries.
- New candidate metadata: `experiments/fetch_neutrality_metadata.py` has
  separate acquire/verify stages and a fixed metadata-only URL allowlist.
  Source files, receipts and the plant exposure record are under
  `data/neutrality-audit/2026-10-03/`; this is not a registered result.
- Completed law-route metadata gate: `experiments/fetch_law_observation_metadata.py`
  has fixed allowlisted acquisition and default offline verification. Six source
  files and receipts are in `data/law-route/2026-10-04/metadata/`. Reports:
  `docs/plankton-observation-gate.md`, `docs/malaspina-observation-gate.md` and
  `docs/bloofinz-observation-gate.md`. These are unregistered audit materials.
- Analytic reference-measure comparison: `src/orthopolity/measure_intervention.py`,
  `experiments/illustrate_measure_intervention.py`, and
  `tests/test_measure_intervention.py`. The runner prints deterministic examples
  without reading data, generating random samples or modifying the run registry.

## Checkpoint log

- 2 October 2026: created this handoff before acquisition/analysis. The user
  explicitly requested a document that serves as repository truth across sessions.
- Acquisition checkpoint: Dryad API metadata retained with expected checksums,
  but API downloads returned 401 and public download links returned 403. These
  attempts are logged. Figshare methods supplement was acquired (32 pages).
  The author-owned public Zenodo software deposit contains a full ~98.7 MB
  source bundle; acquisition/extraction completed through that mirror, with
  the published MD5 verified.
  Mirror provenance will be explicit and no unverified Dryad byte equivalence
  claimed. This access issue does not require new measurements.
- Measurement-method checkpoint: the published supplement independently
  confirms chemical C/N assays in separate preliminary monocultures and
  CASY counts/size measurements for per-cell normalization. They are observed
  cellular stocks, not imposed geometry or minimum physiological requirements.
  Their transfer into grazed communities remains an assumption. Original workbook bytes from the author mirror are now ready for analysis.
  Main records span 24 vessels; all have a pulse-time baseline. The main
  post-pulse numeric outcomes have not been analysed. The separate quota
  calibration has 20 serial observations, without replicate identifiers, and
  was collected later than the main series; physiology transfer is assumed.

- Cost-study checkpoint: local protocol freeze at 14:29:40 UTC preceded original
  CSV retrieval at 14:30:01–14:30:03 UTC. This Git checkpoint follows acquisition
  and precedes quota parsing/fitting. Do not describe it as a pre-acquisition
  Git commit. Source MD5 matched the provider; seven method tests pass.
- Session 2 checkpoint (new coding session, same day): registry audit passed,
  265 tests passed, chemostat `verify`/`audit` replays were byte-identical.
  Retained chemostat sources committed except the two large ignored binaries.
  Next: execute the frozen cost study, then implement and freeze the chemostat
  forecasts.
- Cost-study result checkpoint: calibration froze coefficients and 30 conditional
  predictions at 15:00:10 UTC (commit `a697be6`, pushed before evaluation).
  Evaluation started at 15:00:43 UTC; the offline audit replay matched.
  Held-out mean absolute log error: C, fixed cubic 0.133 best; N, strain mean
  0.207 best (cubic 0.221); P, strain mean 0.147 best (cubic 0.226). Strain
  temperature trends were worst for every element. Registered with 484 registry
  file references.
- Chemostat protocol checkpoint: amendment 1 (`a67c6a3`, 15:11:23 UTC) fixed the
  implementation and added the two-budget cost-ratio model before any
  main-workbook outcome was decoded. Synthetic tests then showed that the rule
  saturates. Amendment 2 (`92d239d`, 15:26:19 UTC, with the gated runner and
  tests) retained its capacity bound and a nitrogen-budget diagnostic.
- Chemostat freeze checkpoint: forecasts frozen at 15:26:34 UTC and pushed in
  `180dc6d` at 15:26:45 UTC. The reader matched 2,960 permitted cells against
  the openpyxl audit copies, and 120 held-out post-pulse rows stayed gated.
  Development diagnostics before evaluation: the fitted two-budget strength was
  zero on most days, and Chlamydomonas lowest growth held in 2 of 12
  development vessels.
- Chemostat evaluation checkpoint: evaluation started at 15:27:47 UTC, and the
  offline audit replay matched. Held-out reader cross-check: 480 cells. Results
  and verdicts are as stated in *Current state*. Post-hoc noise floor: 0.117 TV
  between consecutive pre-pulse samples; 0.164 from the day-0 composition.
  Registered with 514 file references, linked to `restrictions-2026-10-01`.
- *Dunaliella* checkpoints. Sources came from Dryad's Zenodo copy, whose MD5
  equals Dryad's digest. Commits:
  - `78a14cc` (16:06:23 UTC): partition declared; only controls inspectable.
  - `1eaa72d` (16:10:56): protocol frozen before decoding selected lineages.
  - `e6216f7`: runner and leakage tests.
  - `f3fd250`: factor-8 cell-volume amendment.
  - `74c229f`: forecasts retained (frozen 20:55:22; evaluation 20:55:46).

  Offline audit replay matched. Registered with 539 file references.
- Manuscript checkpoint. `docs/paper.md` revised (`31b2f84`) with a new
  Section 5, Figure 2 (*Dunaliella*), and an updated abstract, discussion,
  conclusion and references. PDF rebuilt (`d5d6ee1`, 15 pages, no LaTeX
  warnings); a second rebuild was byte-identical.
- 3 October 2026, session continuation. Checkout matched `05f2b4f` and was
  clean. All 295 tests passed and registry verification retained 21 studies /
  539 file references. Dataset screening identified directly harvested plant
  masses and chemically assayed plankton sieve fractions; methods, exclusions,
  proposed transfer design and seven metadata receipts are in
  [the audit](next-dataset-audit.md). The plant CSV header inspection exposed
  raw rows on CR-only line endings; retrieval stopped, no scoring occurred,
  and the incident was reported at 08:03:16 UTC (exact request time unknown).
  Future plant work must disclose retrospective raw-outcome exposure. Next:
  implement the plant protocol and observation calibration before formal
  scoring; preserve unused plankton outcomes for a separate frozen study.
- Plant execution checkpoint, 3 October. Protocol `6a2d2b3` precedes retained
  source acquisition; implementation/amendment `7cad34e` precedes formal
  calibration and fitting. Forecasts/calibration frozen at 21:34:45 UTC and
  pushed in `1258e80` before evaluation at 21:35:21 UTC. All five comparisons,
  missingness/tails and generated census diagnostics are retained. Registered
  as record 22 with 571 file references. Exact offline audit, figure byte
  reproduction and isolated missing-manifest recovery pass; 317 tests pass.
  Paper Section 5.4 and Figure 3 report the mixed stock/count comparison and
  unresolved expected neutrality. The revised PDF is 17 pages; all pages were
  visually checked, with no LaTeX warnings or overfull boxes. Table cells emit
  underfull-spacing diagnostics without clipping. A forced rebuild reproduces
  identical PDF bytes. Prior raw exposure remains part of every
  interpretation. Next: investigate the plankton observation design without
  decoding its outcome table, or address an explicitly discriminating methods
  comparison; do not modify any registered plant outputs.
- Law-route checkpoint, 4 October: proposal `7a8ee6f` preceded this methods
  gate. PANGAEA XML/KML agree on 43 station labels and coordinates; the six-page
  CSIC methods chapter documents class filtration and a possible background
  pathway, without demonstrating contamination. BCO-DMO processing confirms
  shared Cycle/gear/day-night/class chemistry and different depth supports.
  Six source files verify by checksum. The current two-archive ecological test
  is not justified; no forecasts were frozen and no raw N stocks were acquired
  or scored. The reopening criteria are evidence-based and do not require
  independent chemical assays on every tow. The manuscript and all registered
  studies remain unchanged. All 321 tests pass; offline verification retains
  22 registry records and 571 file references.
- Reference-measure design checkpoint, 4 October: continued after the archive
  gate, without opening its outcomes. Derived the exact power-cost equivalence
  and additive-cost discrimination, including budget-independent pairwise
  response contrasts and exact bin integrals. Independent mathematical review
  checked the proof, dimensional consistency, limits and causal qualifications.
  The software compares analytic forecasts with direct quadrature and checks
  invariance under bin merging and unit changes. A worked example changes the
  smaller-bin resource prediction from shared 50% at baseline to 50% versus
  25.96% after overhead. This is a conditional mathematical distinction, with
  no newly established natural regime or empirical support. The manuscript
  and registered records remain unchanged. All 331 tests pass, the illustrative
  table reproduces exactly, and the registry verifies 22 records / 571 file
  references. The response contrast also holds for a general increasing cost
  curve under a size-independent physical cost addition; the power baseline
  supplies initial observational equivalence.
- Candidate/calibration checkpoint, 5 October: source inventory completed in
  `8e209fa`, with 231 signed/missing independent-assay readings and real
  community-specific size headers. The frozen calibration protocol, source
  snapshots and synthetic tests were committed in `d49f0e6` before the first
  real-data fit. It fails the specified additive-family gate without opening
  numerical community outcomes. The primary weighting gives effectively
  identical power/additive forecasts; the alternative weighting gives interior
  gains but fails robust cross-weight separation. Exact numerical replay and
  PNG reproduction pass; registered as record 23 with 587 references. All 352
  tests pass. The report and scientific assessment retain the negative
  qualification; no conclusion changes in the manuscript. Future work must
  supply additional independent calibration/observation evidence or a
  substantively different, independently valid prediction. This route is not
  improved by selecting the favorable weighting after results.
