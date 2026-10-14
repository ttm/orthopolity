# Chemistry source qualification — 13 October 2026

## Selected source and exposure

Wedler et al. (2024), *Binary Adsorption Equilibria of Three CO2+CH4 Mixtures
on a Reference Zeolite Y at Temperatures from 298 to 353 K and Pressures up
to 3 MPa*, J. Chem. Eng. Data 69, 4216–4229,
[doi:10.1021/acs.jced.4c00358](https://doi.org/10.1021/acs.jced.4c00358).
The [versioned author archive](https://zenodo.org/records/17604326),
doi:10.5281/zenodo.17604326, was published 13 November 2025 under CC BY 4.0.
All thirteen publisher files are retained, including the workbook, although
the analysis uses the twelve AIF text files. Full article XML and gas-property
documentation are retained separately with acquisition receipts, SHA-256 and
publisher MD5 checksums. `experiments/fetch_adsorption.py --stage verify`
checks the exact sources offline.

The metadata search exposed the abstract's claim that a pure-calibrated
statistical model predicted mixtures well, and search-result uncertainty
examples. The publication's qualitative conclusions are known. Before the
design freeze we inspected methods, headers, pressure/composition arrays,
temperature matching and uncertainty-column identity, but did not fit pure
uptake or inspect the numerical mixture uptake arrays. This is a locally
frozen retrospective forecast audit, not a blind or prospective experiment.
Downloading an intact file is not withholding access; the runner enforces
column selection and commits forecasts before numerical target evaluation.

## Eligibility and conventions

- Binderless RM8850 zeolite Na-Y; vacuum activation 633 K for 16 h. Unary and
  binary measurements use the same reference material and gravimetric method,
  but different sample masses. Binary runs require gas circulation/mixing.
- Amounts are **absolute** uptake, mmol per gram of adsorbent. The source
  converts excess to absolute using independently measured micropore volume
  0.358 ± 0.003 cm³/g and gas density. We use the published absolute values;
  we do not fit an adsorbed-volume correction from mixture outcomes.
- Predictors are total pressure in MPa and **equilibrium**, not feed, gas
  composition. Composition is derived from density using GERG-2008/REFPROP;
  component uptake is obtained by mass balance. Composition and component
  errors are therefore related. No joint covariance or independent replicate
  structure is available for population inference.
- All pure files have 12 observations. Pure temperatures: 298, 333, 353,
  393 K. Binary temperatures: 298 (18 rows), 313 (9), 333 (18), 353 (9).
  The fixed intersection gives **72 calibration observations and 45 mixture
  conditions / 90 component targets**. Exclude 313 and 393 K from this
  within-temperature transfer; no temperature interpolation is introduced.
- Nominal AIF temperatures are used throughout; the paper gives measured
  temperatures differing by at most 0.05 K. The predictor audit retains those
  measured temperatures. Each temperature contains three feed-composition
  sweeps, preserved in source order (6, 6 and 3 pressures per sweep).
- A preliminary count of XML rows was misleading: Table 7's `tbody` has 65
  rows, of which eleven are empty separators. Its 54 numerical rows match all
  archive pressures and equilibrium compositions exactly. There is no missing
  mixture cohort. Numerical response equality is checked only at evaluation.
- AIF mixture uncertainties match the paper's **Monte Carlo** columns exactly,
  not its GUM columns. The Table 7 caption says “Standard”, while its footnote
  specifies coverage factor 2 for both methods. We retain U as reported, use
  U/2 only for pure-fit weights, and describe error-bar agreement without a
  calibrated coverage claim. The pure files' uncertainty convention is also
  checked against Tables 5 and 6 at calibration.

## Physical scope and competing explanations

The source establishes common pore/cage volume, not identical one-molecule
binding sites. Its cage model uses 958.2 Å³ cages and very similar van der Waals
covolumes (70.9 Å³ CO2; 71.0 Å³ CH4), but species-effective excluded volumes
and adsorption energies can differ. A common-capacity Langmuir model is
therefore a restrictive, testable approximation. Capacity fitted separately
at each temperature is an **effective within-temperature capacity**, not an
independently measured site count or evidence of temperature-invariant sites.

The source's statistical cage model is established adsorption physics; its
published parameter tables and mixture fits are not calibration inputs here.
The chosen benchmark is classical IAST with separately fitted pure Langmuir
curves. No species-specific capacity is inserted into an inconsistent
shared-denominator formula and described as one conserved site resource.

Peng–Robinson gas fugacity uses independently tabulated CO2 and CH4 critical
constants from the retained [CoolProp CO2](https://coolprop.org/fluid_properties/fluids/CarbonDioxide.html)
and [CH4](https://coolprop.org/fluid_properties/fluids/Methane.html) documentation.
The fixed binary interaction coefficient is zero, a declared approximation.
The retained IDAES rendered table has an apparent alpha-function typo;
the [official version 2.13.0 implementation](https://raw.githubusercontent.com/IDAES/idaes-pse/2.13.0/idaes/models/properties/modular_properties/eos/ceos.py)
confirms the standard square-root reduced-temperature formula and mixture
fugacity expression. An independent Gibbs-derivative implementation checks
our code. An ideal-gas sensitivity recalibrates and forecasts end to end.

## Alternative chemistry routes

The [design review](chemistry-design-review-2026-10-13.md) records adsorption,
step-growth polymer distributions and molecular populations. A Donnan-voltage
archive (doi:10.1038/s41467-022-33592-3) is accessible, but its absolute voltage
reference is extrapolated from the same response curve; voltage differences
would require a distinct design. Donnan-dialysis data
(doi:10.4121/9629d894-4b39-4e4a-adb6-1c17eeff82c3.v1) require reconciliation
with a flow-rate corrigendum and separation of fitted transport coefficients
from predictions. They remain leads, not completed tests. Adsorption was
selected for accessible separate calibration and competition measurements,
not because its locally evaluated outcomes were favorable.
