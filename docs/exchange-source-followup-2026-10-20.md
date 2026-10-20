# Exchange sources: a usable pair archive, and a narrower transfer

20 October 2026. This follows the [first source audit](equalization-source-audit-2026-10-19.md).
**A public archive now supports developing a two-compartment transfer test.**
It does not supply the five-compartment topology intervention. No calibration
or target response values have been numerically inspected or fitted, and no
new empirical test is registered. Known publication summaries remain exposed.

## The original droplet candidate: public inventory checked

The [ACS Figshare DOI inventory](https://api.figshare.com/v2/articles?resource_doi=10.1021%2Facs.analchem.0c04939)
lists four version-1 supplements for Bachler et al. (2021). The separately hosted
[BioStudies inventory](https://www.ebi.ac.uk/biostudies/api/v1/studies/S-EPMC8014892)
agrees:

| File | Bytes | Public record |
| --- | ---: | --- |
| `ac0c04939_si_001.pdf` | 741,729 | [14219948](https://api.figshare.com/v2/articles/14219948) |
| `ac0c04939_si_002.avi` | 17,623,958 | [14219951](https://api.figshare.com/v2/articles/14219951) |
| `ac0c04939_si_003.avi` | 16,935,712 | [14219954](https://api.figshare.com/v2/articles/14219954) |
| `ac0c04939_si_004.avi` | 4,628,714 | [14219957](https://api.figshare.com/v2/articles/14219957) |

The videos describe spotting, splitting and aspiration. These inventories do
not identify raw fluorescence/geometry time series. The
[ETH thesis record](https://www.research-collection.ethz.ch/entities/publication/dded41e0-59e8-45a8-a176-e6bcfede279f)
lists a thesis PDF and abstract; [DOI metadata](https://api.datacite.org/dois/10.3929/ethz-b-000454797)
has no related dataset identifier. The ETH bundle API returned 429 to a
read-only source audit, so that underlying inventory was not exhaustively
checked. None of these supplements was downloaded. This is a bounded search
finding, not proof that raw data do not exist elsewhere.

The [observation correction](exchange-observability-2026-10-20.md) is essential:
an initially empty acceptor gaining solute rules out loss alone under a valid
observation model. The outstanding issue is quantitatively transferring rates
and verifying stock recovery, not denying transport.

## Available alternative: independently sampled membrane pairs

Benstead, Politi, Bergsman and Pozzo (2026), *An automated sampling workflow for
parallel long-term membrane diffusion cell testing*,
[article](https://doi.org/10.1039/D5DD00523J),
[Zenodo data](https://zenodo.org/records/17238337),
[pinned repository](https://github.com/pozzo-research-group/OT2-ADT/tree/12be95974a58e1971483823948eff8802e06b729).

The 52,182-byte experimental ZIP is retained unchanged. Its MD5
`92c9c740602a1f274a2e4550ca98409d` matches Zenodo. It contains 25 dated sample
files and 25 UV calibration files. Despite their `metadata.csv` suffix, sample
files contain **response values**; they must not be opened as unrestricted
metadata. Record and figure-crosswalk files also mix design fields with fitted
transport coefficients.

The design-only inventory selects matching acid-orange/PEG25-on-PES runs:

| Property | Proposed calibration | Proposed withheld response |
| --- | --- | --- |
| Date and sampling | 5 May 2025, automated | 3 June 2025, manual |
| New membrane identities | S1–S4 | S5–S8 |
| Volume per chamber | 11 mL | 11 mL |
| Recorded contact radius | 0.81 cm | 0.81 cm |
| Times, hours | 0, 6, …, 66 | 0, 4, 21.3, 24, 27.5, 45.6, 48, 69.6 |
| Chamber observations | 96 | 64 |
| Optical calibration rows | 5 | 5 |

All eight chamber sequences in each run have the listed number of samples.
Only design fields, filenames, headers and calibration row counts were exposed.
The inventory and its response-field exclusion check reproduce with
`experiments/audit_membrane_exchange_inputs.py`.

**Observation audit.** The source code retains raw and blank-subtracted
absorbance. It estimates the calibration slope and intercept, but converts
sample absorbance using the slope alone. It does not impose a constant total.
Its comparison plot divides by initial donor concentration, a fixed baseline.
Freeze the blank/intercept treatment before response access; do not silently
copy the source's concentration columns. These findings come from the retained
[analysis code](https://zenodo.org/records/17238337/files/ADT_OT2_Analysis.py?download=1),
which was inspected but not executed. Notebook outputs remain uninspected.

The article describes experiment-day optical standards from a separate vial,
20 µL withdrawals from each chamber, tenfold sample dilution and 20 µL water
replacement. Four-pair collection takes about ten minutes, sequentially; exact
chamber timestamps are not established. Stirring rates vary and are unmeasured.
Post-experiment thickness enters the published diffusivity. These limitations
must remain in a transfer analysis. [Methods](https://doi.org/10.1039/D5DD00523J)

CSV thickness labels conflict (`Membrane (um)` versus `Membrane_cm` for the
same 0.11/0.12 entries). Notebook inputs instead specify 110/120 µm for the
automated cohort. The recorded radius also differs slightly from the nominal
16 mm diameter in the methods. Do not repair these by fitting target responses.
**Use effective conductance directly**, without claiming a thickness-based
permeability or diffusivity forecast. New-membrane variation remains part of
the transfer uncertainty.

## Concrete next test, with a changed scope

Use the earlier four pairs to estimate a shared distribution of effective
conductance, then predict both chamber concentrations for the four later
pairs. The resource is dissolved dye amount; chamber volumes supply the
reference measure. Equal volumes also permit ordinary counting. This is
**neither log-orthopolic nor linear-orthopolic size allocation**.

For constant equal chamber volume $V$ between collections,

$$\dot C_D=-(g/V)(C_D-C_A),\qquad
  \dot C_A=(g/V)(C_D-C_A).$$

Under an explicitly simultaneous withdrawal/replacement approximation,
each collection multiplies both stocks by

$$f=1-\frac{0.020\;\mathrm{mL}}{11\;\mathrm{mL}}=\frac{549}{550}.$$

Thus the known sampling schedule predicts total-stock depletion, while $g$
predicts the contrast decay. Just before sample $j$, with $j$ prior collections
and nominal initial concentrations $(C_0,0)$, the two predictions are

$$C_{D,A}(t_j)=\frac{C_0 f^j}{2}
                 [1\mathbin{\pm}e^{-2gt_j/V}].$$

This is our conditional model derivation, not a finding in the data. A source
run's measured initial condition may replace the nominal initial condition
only under a rule fixed before target access. In that case eight target-run
baseline values become inputs, leaving **56 later chamber responses** for
withheld scoring; the full run contains 64. Shared baseline and calibration
uncertainty must be propagated, without silently clipping negative inferred
concentrations. Sequential collection needs a
timing sensitivity or an explicit event model; it must not be represented as
exact simultaneous sampling. Loss to membranes, evaporation, chemical changes
or changing detector response could still violate the proposed model, and both
chambers provide a diagnostic of those failures without enforced conservation.

**Stock recovery needs its own check.** Persistence, finite exchange and
instantaneous mixing can all share the same sampling-depleted total prediction.
For chamber prediction errors $e_D,e_A$,

$$e_D^2+e_A^2=\tfrac12[(e_D+e_A)^2+(e_D-e_A)^2].$$

The common total error then cancels from a squared-error ranking of those
models. Winning that comparison can establish better contrast kinetics while
stock recovery remains wrong. Score the total and contrast separately, with
shared optical/baseline covariance; do not interpret a kinetic win as verified
conservation. Five optical calibration rows leave only three residual degrees
of freedom for an affine fit and do not independently test time drift, matrix
effects or pipetting errors.

Before fitting: freeze the input whitelist and chronology; the observation
calibration and initial-condition rules; the physical and optical qualification
gates; fitting and uncertainty treatment; comparisons and decision tolerances;
and synthetic checks that recover exchange and reveal incompatible losses.
Then calibrate on the earlier run, independently verify and commit forecasts,
and only then decode the later response columns. Keep all four target pairs;
do not reproduce source outlier exclusions without a separately frozen rule.

This would test **effective kinetics across independent pairs and collection
procedures**, not the factor-5.236 topology prediction, a geometry-derived
conductance, or a mechanism unique to orthopolity. Only four calibration and
four target membranes limit any population-level inference. Each procedure
occurs on just one run/day, so procedure and batch effects are confounded;
success would not establish equivalence of manual and automated methods.
The archive clears
the availability and measurement-identity stage; numerical optical adequacy
and physical-model qualification have not yet been tested.

## Other checked leads and exposure

[Sun et al. (2024)](https://doi.org/10.1038/s41467-024-45214-1) supply a public
source workbook and observe dye exchange in partially fused pairs. Their
larger transport channels use imposed pumping; fixed-position fluorescence
does not directly identify whole-compartment stocks. The workbook was not
requested, and a compatible closed pair-to-network target was not established.

[Bachler et al. (2020)](https://doi.org/10.1038/s42003-020-01489-w) normalize
fluorescence to the initial donor, rather than each frame's total. Their
reported data availability is author request; no public raw archive was
identified in this audit. The methods and Sun article XML are retained.

The thermal lead [Funayama et al. (2026)](https://doi.org/10.1038/s42005-026-02763-9)
lists [source data](https://doi.org/10.6084/m9.figshare.32788554), but the audit
did not retrieve or qualify it. This remains a lead, not a second ready test.

Published droplet outcomes, membrane diffusivity aggregates and the four
published automated-cohort diffusivities were exposed. Notebook prose included
illustrative numerical formatting examples; outputs and selected-cohort
absorbance/concentration values were not viewed. No global blindness is claimed.
The raw membrane ZIP and source notebook are now acquired, so the accurate
statement is **numerical responses uninspected**, not "no response files
downloaded." Acquisition receipts preserve that distinction. This work changes
source qualification and analytic design, not the 43-run registry or article
PDFs.
