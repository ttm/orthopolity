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

- Branch: `py314-and-package-names`, pushed to `origin`. Both studies of this
  checkpoint are complete and registered. Registry: 20 records, 514 retained
  file references. Suite: 283 passing tests (`make test PY=python3.11`).
- [Archived cost transfer](archived-cost-transfer.md) (`archived-cost-transfer-2026-10-02`):
  a size-geometric carbon cost predicts held-out 25°C Synechococcus quotas best
  (mean absolute log error 0.133); strain identity predicts N and P better than
  cell size; extrapolated temperature trends are worst throughout.
- [Chemostat response](chemostat-response.md) (`chemostat-resource-response-2026-10-02`):
  negative. No frozen forecast beat persistence on the twelve held-out
  polyculture vessels (nitrogen midpoint time-weighted TV: development response
  0.243, persistence 0.247; not distinguished). The two-budget cost-ratio rule
  failed on score, size and direction. Its capacity of 0.05–0.12 TV fell below
  every observed departure (0.29–0.49), and its ordinal prediction held in 4 of
  12 vessels, the chance count. All twelve held-out vessels are right-censored
  for recovery to baseline by day 12.
- Erratum retained, not corrected in frozen code: the chemostat freeze field
  `baseline_algal_nitrogen_umol_per_l` holds nmol/L. Corrected values are in
  `results/chemostat-response/posthoc-diagnostics.json`. No score uses the field.

## Next actions, in priority order

1. **Audit the next available dataset for direct resource stocks.** The
   chemostat study's main limit was a transferred, not measured, resource
   proxy. Begin with the [Dunaliella recovery records](https://doi.org/10.5061/dryad.4mh47r7)
   (deprivation and replenishment). Follow the same sequence: retain bytes and
   receipts; audit methods and replication from metadata; freeze a protocol;
   then forecast, evaluate and register. Declare a multi-sample baseline and the
   grazer/forcing structure in advance.
2. **Search for systems where recovery can resolve.** Longer post-perturbation
   windows are needed than the 12 days here, ideally with stocks measured in the
   evaluated units.
3. **Decide with the user whether to integrate these results into
   `docs/paper.md`.** The manuscript does not yet cite the 2 October validation
   round or the two available-data studies. The scientific assessment and
   roadmap now summarize them.
4. Keep every failed forecast. A corrective or extended analysis gets a new run
   identifier and its own frozen protocol. Never edit a registered one.

## Resume commands

```bash
git status --short --branch
PYTHONPATH=src python3.11 experiments/register_runs.py --verify
make archived-cost-transfer chemostat-response PY=python3.11   # offline audits
```

A clone lacks the 98.7 MB chemostat bundle. The audits above do not need it.
Run `make restore-chemostat-bundle PY=python3.11` only to replay the source
acquisition audit.

## Current files and ownership boundaries

- Chemostat sources: `experiments/fetch_chemostat_sources.py`,
  `data/chemostat-sources/2026-10-02/` and the
  [source audit](chemostat-source-audit.md). Git omits only the Zenodo bundle
  and its extracted `.RData`, both restorable by checksum
  (`experiments/restore_chemostat_bundle.py`).
- Chemostat study, frozen: `experiments/run_chemostat_response.py`,
  `src/orthopolity/chemostat_response.py`, `src/orthopolity/gated_xlsx.py`,
  configuration plus amendments 1–2 in `configs/`, and outputs in
  `data/chemostat-response/2026-10-02/` and `results/chemostat-response/`.
  Do not edit these files: evaluation and audit refuse changed source bytes.
  The post-hoc report `experiments/report_chemostat_response.py` reads
  retained outputs only.
- Cost study, frozen: `experiments/run_archived_cost_transfer.py`,
  `src/orthopolity/archived_cost_transfer.py`, its config, and outputs in
  `data/archived-cost-transfer/2026-10-02/` and `results/archived-cost-transfer/`.
- Registration of both: `experiments/register_available_data.py`
  (`make available-data-registry PY=python3.11`). It is idempotent; add later
  studies to its `STUDIES` table without changing existing entries.

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
