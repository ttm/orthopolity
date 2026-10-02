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

- Branch: `py314-and-package-names`. Protocol checkpoint `bc57364` follows the
  available-data roadmap `ca0c683` and the last completed study `ec5f078`.
- Registry: 18 executed/incomplete historical records, 464 retained references.
  Complete suite at the start of session 2: 265 passing tests. New protocols and
  original inputs are retained; neither new study has been numerically fitted,
  evaluated or registered.
- Metadata screening ranks Dryad `10.5061/dryad.51c59zwj5` first: separate
  preliminary algal C/N and cell-volume records plus 24 nutrient-pulsed vessels.
- The main series resolves three algal groups: Cryptomonas, Chlamydomonas, and
  pooled Monoraphidium/Chlorella. Pool uncertainty must remain explicit.
- Supplied posterior nitrogen trajectories and full-data fitted interaction
  summaries are not independently measured inputs. The first endpoint is a
  finite-group resource-stock response, not a broad power-law exponent.

## Active work and checkpoint sequence

1. Retrieve versioned source metadata, README, original workbooks and published
   measurement methods; preserve bytes and acquisition receipts/checksums.
2. Audit schemas, assay methods, missingness, units, pooled groups and actual
   replicate structure. Inspect separate calibration records first. Keep whole
   community vessels together in development/evaluation membership.
3. Specify a feasible forecast using the measurements actually available,
   compare independent-cost/reference and development-only dynamic forecasts
   with persistence/mean-response rivals, and freeze all choices before reading
   held-out post-pulse values. Acquisition of a bundle is not outcome blinding.
4. Evaluate held-out resource composition, absolute stocks and return toward
   baseline separately; use calibrated uncertainty only when justified. Missing
   resource states narrow the claim rather than becoming invented measurements.
5. Register executed evidence with immutable inputs, algorithms, predictions,
   outcomes and limits. Update this file after each material checkpoint.
6. Audit complementary existing cost-scaling/recovery datasets; do not transplant
   quotas between different organisms as though they were one population.

## Candidate sources

- [Chemostat Dryad record](https://datadryad.org/dataset/doi:10.5061/dryad.51c59zwj5)
  and [published supplement](https://doi.org/10.6084/m9.figshare.c.8172360).
- [BCO-DMO 926311](https://www.bco-dmo.org/dataset/926311/description): independent
  Synechococcus C/N/P cost measurements; separate cost-transfer study only.
- [Dunaliella recovery publication](https://pubmed.ncbi.nlm.nih.gov/30068687/)
  and [data DOI](https://doi.org/10.5061/dryad.4mh47r7): existing deprivation and
  replenishment; resource costs and replication require file audit.

## Resume commands and immediate next action

```bash
git status --short --branch
PYTHONPATH=src python3.11 experiments/register_runs.py --verify
```

Read this document, the current source-audit report and frozen manifests before
changing code or interpreting outputs. Immediate next action at this checkpoint:
implement/freeze the finite-group response study before evaluation extraction;
resume the complementary cost study from its locally frozen protocol.
No prediction freeze or validation result exists yet for this candidate.

## Current files and ownership boundaries

- Source acquisition: `experiments/fetch_chemostat_sources.py`,
  `data/chemostat-sources/2026-10-02/`; completed audit report at
  `docs/chemostat-source-audit.md`. Git omits only the 98.7 MB Zenodo bundle
  and its extracted 94.8 MB `.RData`. Restore both by checksum with
  `make restore-chemostat-bundle PY=python3.11`.
- Response mathematics in development: `src/orthopolity/chemostat_response.py`
  and `tests/test_chemostat_response.py`. Primary design uses additive changes
  in resource shares, explicit simplex projection, and a separate stock-total
  response. Comparators: persistence, development-vessel mean response,
  preliminary no-herbivore response, equal stock across the three measured groups.
  Equal group stock is a comparator, not logarithmic neutrality.
- Response configuration now exists at
  `configs/chemostat_response_2026-10-02.json`: development monoculture-rotifer
  vessels versus evaluation polyculture-rotifer vessels; nitrogen primary,
  carbon sensitivity; pre-pulse median quota/volume calibration; pooled lower,
  midpoint and upper conversions; whole-vessel descriptive scores. These choices
  precede inspection of main held-out post-pulse numerical responses. Final
  schema/availability checks may still require an explicitly logged amendment
  before prediction freeze; no frozen prediction exists yet.
- Complementary archived cost study: `experiments/run_archived_cost_transfer.py`,
  `src/orthopolity/archived_cost_transfer.py`, corresponding config/tests,
  `data/archived-cost-transfer/2026-10-02/` and `results/archived-cost-transfer/`.
  Metadata-only protocol: train cultures at 16/18/20/22°C and evaluate 25/27°C;
  C/N/P quotas in fmol/cell; forecasts conditional on measured cell diameter.
  No quota transfer into other taxa or community neutrality claim.

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
