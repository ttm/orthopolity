# BioMe dye stocks: fixed diagnostic before numerical access

23 October 2026. This is a **source-qualification diagnostic**, not a new
confirmatory law test or the missing pair-to-network experiment. The
[author archive](https://github.com/segrelab/co_culture_device/tree/c9f6321c4a9dc70bfe6b9553dbecb17b5c228983)
contains isolated pairs, separate optical standards and no-pore controls.
The question is whether observed chamber totals can support independent
connector-capacity qualification. Physical volume defines the reference
measure, neither log-orthopolic nor linear-orthopolic size allocation.

## What is already exposed

The [article](https://doi.org/10.1128/msystems.00017-21) reports different
donor- and recipient-derived rates and suggests settling or sequestration.
That qualitative result is known. Methods, script text, workbook labels and
acquisition settings have been read, but numerical calibration and response
cells have not been decoded. The files are already downloaded. This is a
local retrospective freeze, not global blindness or external preregistration.

Both deposited MATLAB scripts assign `m_BP = (uM_PR/1000)*vol` after computing
the correct separate `uM_BP`. Thus their bromocresol-purple mass calculations
use the 478 nm readings and phenol-red conversion, although the intended
reading is 490 nm with its own standard curve. These are distinct wells at
the wrong wavelength, not copies of the phenol-red wells. Preserve the
original scripts and implement the documented measurement independently.
This code finding alone does not establish which version generated the
published figures or the size of any numerical error.

## Source mapping fixed before decoding

Retain original bytes and SHA-256 receipts in
`data/physics-candidates/2026-10-23/biome/`. Repository commit:
`c9f6321c4a9dc70bfe6b9553dbecb17b5c228983`.

Both workbooks use sheet `Plate 1 - Sheet1`, columns D:BK ordered A1:A10,
B1:B10, through F1:F10. Plate rows A:C contain phenol red; D:F contain
bromocresol purple. Each row is one replicate. Neighboring plate columns
1/2, 3/4, 5/6, 7/8 and 9/10 are donor/recipient pairs, respectively for
no pores, 0.03, 0.1, 0.2 and 0.4 micrometre pores.

| File | 478 nm block | 490 nm block | Design |
| --- | --- | --- | --- |
| `optical-calibration.xlsx` | D28:BK52 | D57:BK81 | 25 readings at 15-minute spacing, 0–6 h; columns have 450, 400, …, 0 micromolar standards |
| `dye-diffusion.xlsx` | D28:BK316 | D321:BK609 | 289 readings at 15-minute spacing, 0–72 h; nominal donor 400 micromolar, recipient water |

Use only each dye's matching wavelength and plate rows. All wells nominally
contain 250 microlitres. Thus each pair starts with 100 nmol. All 30 pairs
(six no-pore controls and 24 porous pairs) are retained. Standards were
acquired in November 2019, after the October diffusion run; they are separate
measurements, not chronological prior calibration. Recorded instrument
settings specify 30 degrees C and no shaking step. Well mixing is therefore
unverified. Actual loading-to-first-reading delay is unrecorded.
The file's time column includes the instrument's initial read delay, unlike
the source scripts' zero-based clock. Retain that offset in the inventory;
plots and the final-hour window use elapsed time since each wavelength's
first reading. This is not an estimate of elapsed time since physical loading.

## Fixed calculations

1. Average all 25 readings for each standard well. Fit absorbance
   `A = intercept + slope * C` by ordinary least squares to the 30 well
   means per dye, with an intercept and equal well weights. Invert this
   calibration for concentration. Do not pool wavelengths, force a zero
   intercept, exclude early readings, or truncate negative estimates.
   Report slope, intercept, concentration-equivalent RMSE, maximum absolute
   leave-one-concentration-out prediction error, and maximum temporal
   deviation from a well's mean. These are diagnostics, not 750 independent
   standard replicates. A nonpositive slope stops the numerical report.
2. For every pair and time, calculate measured recovery relative to nominal
   initial stock, `R = (C_left + C_right)/400`. Also report `R(t)/R(0)`.
   A nonpositive denominator is an error, not a replacement with zero.
3. Independently calculate a same-row control ratio directly in absorbance:
   `P = (A_left + A_right - 2*A_water_control) /
        (A_dye_control - A_water_control)`.
   Report `P(t)/P(0)`. This cancels a shared affine optical drift **only if**
   the no-pore dye and water controls retain their specified concentrations
   and optical response is shared across that row. It also masks physical
   losses shared with the no-pore controls. It is not an absolute stock assay.
   Any nonpositive control contrast or initial P stops this ratio report.
4. Summarize the first reading and the mean of the final five readings
   (71–72 h). Report each replicate, then the mean and range across the
   three replicates for each dye/pore condition. Plot all time points.
   For the no-pore controls also report donor and recipient concentration
   changes, so a constant pair total cannot hide apparent crossover.
5. Do not fit exchange rates, connector capacities, loss models, optical
   drift corrections, or selected time windows to these outcomes. No
   p-values, pass/fail threshold, empirical registry entry or network
   validation is produced. Shared wells, standards and same-plate conditions
   preclude treating time points as independent experimental replicates.

The ideal zero-storage, closed, well-mixed pair predicts constant total.
Departures diagnose a problem with that joint model **and its measurement
assumptions**. They do not identify the location, reversibility or amount of
hidden storage. Even apparent constancy cannot exclude a store initially at
the common concentration, as the [counterexample](topology-storage-2026-10-23.md)
shows. Neither fit quality nor nominal pore volume identifies a chemical
partition/adsorption capacity. The archive has no separate connector-loading
or recovery measurement, and no interconnected network response.

## Verification and release sequence

Before numerical decoding: verify original hashes and header mapping, test
the implementation on synthetic dyes with distinct optical slopes, offsets
and wavelength signals, including shared optical drift and genuine stock
loss. Commit and push this protocol, implementation and source inventory.
Only then run the diagnostic. Independently decode all used numerical cells
with a second library, verify the linear calibration by covariance formulas,
check the stock and control summaries, and replay outputs byte-for-byte.
Retain all findings, including unusable controls. Update status and the source
qualification note; do not rescue a failed qualification by selecting a dye
or pore group after inspection.
