# Ongoing research: resume here

Last updated: 2 October 2026. This is the mutable handoff document for ongoing
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

- Branch: `py314-and-package-names`, pushed to `origin`. All three
  available-data studies are complete and registered. Registry: 21 records, 539
  retained file references. Run the suite with `make test PY=python3.11`.
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

## Next actions, in priority order

1. **Audit the next dataset.** Look for coexisting size classes with directly
   measured resource stocks: only such records can test neutrality itself.
   Follow the same discipline: retain bytes and receipts, declare the partition
   from metadata, freeze the protocol before decoding held-out outcomes,
   register, and keep every failure.
2. **Manuscript.** [`docs/paper.md`](paper.md) now reports the frozen-forecast
   tests in Section 5 (commits `31b2f84`, `d5d6ee1`). Revise it again only when
   a new registered study changes a conclusion. Rebuild with `make paper`, which
   needs TeX; the PDF is byte-reproducible from the manuscript's commit date.
3. Never edit a registered study. A corrective analysis gets a new run
   identifier and its own frozen protocol.

## Resume commands

```bash
git status --short --branch
PYTHONPATH=src python3.11 experiments/register_runs.py --verify
make archived-cost-transfer chemostat-response dunaliella-size-budget PY=python3.11   # offline audits
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
- Post-hoc report scripts (`experiments/report_*.py`) read retained outputs
  only and refuse to overwrite changed bytes.
- Registration of all three: `experiments/register_available_data.py`
  (`make available-data-registry PY=python3.11`). It is idempotent; add later
  studies to `STUDIES` without changing existing entries.

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
