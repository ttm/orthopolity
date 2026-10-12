# Independent phosphorus measurements: a small conditional prediction pilot

**Local design freeze, 12 October 2026, before opening numerical cell counts,
bulk phosphorus, single-cell quotas or volumes.** Source selection, identifier
inspection and missingness inspection preceded this design. This is not a
prospective experiment or externally registered study. Commit this protocol,
configuration, retained inputs, implementation and synthetic checks before the
response calculation. The execution record identifies that commit.

## Question and scientific scope

Can a phosphorus quota measured by an independent single-cell method improve
a conditional cell-count prediction when the phosphorus environment changes?
An abundance-derived quota cannot answer that question: substituting
`quota = bulk phosphorus / cell count` into `count = bulk phosphorus / quota`
returns the original count by construction. Here X-ray microanalysis (XRMA)
provides the quota, colorimetry measures bulk phosphorus, and a Coulter Counter
measures abundance. Their independent measurement procedures permit a real
comparison, although biological and systematic measurement errors remain.

This tests transfer of resource accounting, **not equal resource allocation**.
The reference measure counts individual cells in a monoculture; no log-size
measure, neutral species opportunities, inverse-square law or equilibrium
allocation across classes is being tested. Bulk phosphorus is a measured
current stock, not an independently controlled usable supply or a carrying
capacity. A successful conditional prediction would establish neither a
future abundance forecast nor the general law. It would show how an
independently assayed cost changes a specific prediction. It cannot explain
the earlier mixed-species chemostat failures retrospectively.

## Sources and prior exposure

Filella, Duhamel and Diaz's [BCO-DMO 1005084](https://www.bco-dmo.org/dataset/1005084)
contains cell counts and bulk phosphorus from Synechococcus WH8102 cultures.
Filella, Duhamel, Segura-Noguera and Diaz's
[BCO-DMO 1005186](https://www.bco-dmo.org/dataset/1005186) contains single-cell
XRMA assays. Both are CC BY 4.0 and described as parts of the same experiment.
The downloaded live metadata mark both validated; version dates are
13 and 18 August 2026. The earlier web-search cache described the XRMA version
as unvalidated and dated 14 August; the retained live page governs this audit.
The acquisition receipt preserves requested/final URLs, timestamps and SHA256
hashes. XRMA cells were washed and dried before analysis, and measured against
elemental calibration standards. This preparation can introduce method effects.

Metadata already exposed the three phosphorus treatments, different associated
dilution rates, repeated samples from three bottles per treatment, the methods,
and culture biovolume constants (0.844, 0.845 and 0.436 cubic micrometres for low,
mid and high phosphorus). Those culture constants are not used in this pilot;
the size comparator uses independently imaged XRMA cells. No raw numerical
response or quota was printed or summarized before the freeze. The raw bytes
were downloaded and parsed to inspect identifiers, missingness, and whether
duplicate records differ, so this is not an inaccessible or cryptographically
sealed holdout. Published metadata and the search process were not blinded.

The source inspection found 51 bulk rows and 397 single-cell rows in 12 samples.
Cell IDs normally encode EFB1/high, EFB2/mid, EFB3/low, day and bottle; this
convention is inferred from concordant source labels, not independently
confirmed by the authors. One nominal high-P sample has EFB2 IDs throughout,
and another row disagrees in day/bottle. Two cell IDs are nonunique with
different measured records. Missing phosphorus assays are particularly common
in low-P samples. None of these issues is silently corrected.

## Eligibility fixed from identifiers and missingness

Match exact treatment, day and bottle across archives, normalizing only the
documented treatment spelling (`Low P` versus `Low-P`, etc.). Require one bulk
match, at least 20 single-cell rows, **no missing single-cell phosphorus**,
no nonunique cell ID, and agreement between all ID prefixes and explicit fields.
Quarantine the whole sample if any identity condition fails. No incomplete
sample is rescued by averaging detected cells: missing values might be related
to phosphorus content. Missing or nonpositive required numerical inputs after
unblinding cause the pilot to stop, not a switch of sample or model.

These gates leave exactly **High-P/day 1/bottle c (35 cells)** and
**Low-P/day 2/bottle b (33 cells)**. All ten other samples remain in the audit
ledger; their abundance/chemistry values are not analysed. One culture calibrates
and **one different culture** tests the transfer. The 33 test cells are samples
for a mean quota, not 33 independent population responses. Completeness
selection is nonrandom and prevents generalizing to the phosphorus treatments.

## Frozen predictions

For each eligible sample, use the arithmetic mean phosphorus quota `q` in
fg/cell and arithmetic mean imaged volume `v` in cubic micrometres. Let `Q` be
bulk total particulate phosphorus in micromoles/litre, and `N` cells/millilitre.
The raw accounting prediction is

`N_raw = 10^6 × 30.973761998 × Q / q`.

This assumes assayed particles are represented by the counted cells and the
XRMA sample mean represents their mean quota. Extra particulate material,
sampling bias or preparation loss can defeat closure. Report the raw ratio
`N_raw / N` for both cultures; do not fit away an observed closure discrepancy.

Use High-P/day 1/c as the only calibration culture (subscript 0). For the
Low-P/day 2/b target (subscript 1), make three calibrated predictions:

1. Fixed cost: `Nhat_1 = N_0 (Q_1 / Q_0)`.
2. Constant phosphorus density in cell volume:
   `Nhat_1 = N_0 (Q_1 / Q_0) (v_0 / v_1)`.
3. Independently measured cost:
   `Nhat_1 = N_0 (Q_1 / Q_0) (q_0 / q_1)`.

All predictions share the same initial count and bulk-stock change. The third
model incorporates current independently measured physiology, so it has an
additional measured input, not an additional parameter fitted to the target
count. A fixed cross-method calibration factor learned in the initial culture
is assumed transferable. Also report the uncalibrated predictions as above.
No target count, bulk-derived per-cell quota, biochemical pool fraction,
fitted resource price, treatment-specific rescaling or feed-minus-SRP proxy
enters a prediction.

## Reporting and decision limits

Report each predicted/observed ratio and absolute log error, whether the measured
quota improves on fixed quota, and whether each ratio lies in [0.8, 1.25]. This
factor-1.25 margin is a declared pilot accuracy target, not a confidence level,
equivalence test or a theory-derived tolerance. Report failures equally.
No bootstrap interval, p-value, treatment effect or population verdict is
claimed: one independent test culture and undocumented assay errors do not
support those inferences. Different treatment dilution rates also prevent
isolating phosphorus supply as a causal intervention.

Before real evaluation, synthetic checks must show inverse response to a changed
quota, correct unit conversions, unchanged predictions when the target count is
unavailable, and quarantine of missing or ambiguous samples. After evaluation,
recompute all predictions directly from the eligible source rows using an
independent short calculation; retain its maximum discrepancy. Keep all earlier
35 registry entries unchanged and append this pilot with its limited scope.

## Reproduction

```sh
PYTHONPATH=src build/main-venv-2026-10-09/bin/python -m unittest discover -s tests -p test_paired_phosphorus.py -v
build/main-venv-2026-10-09/bin/python experiments/fetch_paired_phosphorus.py --stage verify
PYTHONPATH=src build/main-venv-2026-10-09/bin/python experiments/run_paired_phosphorus.py --output build/reproductions/paired-phosphorus
```

The runner requires its sources to be committed and the input hashes to match.
Use an empty output directory. Acquisition is separately available with
`experiments/fetch_paired_phosphorus.py --stage acquire`; it reuses and verifies
existing snapshots rather than replacing them with a newer source version.
