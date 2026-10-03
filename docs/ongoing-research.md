# Ongoing research: resume here

Last updated: 3 October 2026. This is the mutable handoff document for ongoing
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
  available-data studies are complete and registered. Registry: 22 records, 571
  retained file references. All 317 tests pass. Run the suite with
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

## Next actions, in priority order

1. **Audit the plankton observation design before a separate outcome freeze.** PANGAEA 816451
   has chemical stocks in common-net 200–500, 500–1000 and 1000–2000 µm
   fractions. Prefer nitrogen; audit sampling/volume normalization and stock
   uncertainty before interpreting net catches as water-column allocation.
   Exclude the different-net small fraction and the ambiguously bounded tail.
   Freeze before decoding any numerical plankton outcome. No measured
   opportunity budgets or individual quotas are supplied by this source. Decide
   whether independent samples and observation metadata can identify an expected
   allocation target. If not, retain a descriptive audit without claiming a law test.
2. **Resolve scope or method novelty.** Before adding further examples, declare
   independently observable eligibility for a neutral regime or identify a
   methods comparison that changes a substantive inference. Preserve the plant
   finite-census/dependence findings as calibrated synthetic diagnostics rather
   than fitting them to provide an ecological verdict.
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
make archived-cost-transfer chemostat-response dunaliella-size-budget PY=python3.11   # offline audits
make plant-sources plant-biomass-profile PY=python3.11
```

A clone lacks the 98.7 MB chemostat bundle. These audits do not need it.
Run `make restore-chemostat-bundle PY=python3.11` only to replay the chemostat
source audit.

## Current files and ownership boundaries

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
