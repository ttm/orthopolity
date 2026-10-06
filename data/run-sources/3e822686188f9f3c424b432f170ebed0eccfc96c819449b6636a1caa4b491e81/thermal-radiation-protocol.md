# Thermal radiation: retrospective analysis specification

6 October 2026. This is a descriptive calculation on an established physical
example and a published observational product. Published conclusions and NASA's
product construction were read before this specification. It is neither a new
blind test nor an externally preregistered study.
During the primary-source review, a team member also read the complete table
and calculated residual summaries before the raw-byte download. This exposure
is retained; the specification makes no unseen-outcome claim.

## Physical quantities and comparison

The resource is thermal electromagnetic energy above the vacuum contribution.
The elementary concentrations are normal modes, including polarization. In
classical canonical equilibrium each harmonic mode has mean energy $k_BT$.
For a quantized mode with zero photon chemical potential, the corresponding
mean is $h\nu/(\exp(h\nu/k_BT)-1)$. The predicted ratio is
$f(x)=x/(e^x-1)$, $x=h\nu/(k_BT)$. Mode counting supplies the independent
reference measure $dM/V=8\pi\nu^2d\nu/c^3$; equal energy per mode does not mean
equal energy per frequency interval. The quantum state structure changes the
classical premise and does not itself prove an additive classical equalizing
current persists underneath the quantum equilibrium.

The analysis will calculate the limiting forms, exact Planck and Rayleigh--Jeans
spectra, and transformation of spectral intensity to energy per mode. Constants
$h$, $k_B$, and $c$ take their exact SI values. No physical coefficient will be
fitted to the observed spectral shape.

## Observational product and fixed choices

Use NASA LAMBDA's complete `firas_monopole_spec_v1.txt` product, all 43 rows.
Retain exact input bytes, retrieval receipts, product description, and the
Fixsen et al. (1996) source article. Its reported spectrum is constructed by
adding the published fitted residuals to a 2.725 K blackbody. Use that declared
temperature; do not re-estimate it and call it independent validation. Preserve
the original residuals, marginal one-sigma errors, and modeled Galaxy columns.
The Galaxy column is ancillary and must not be subtracted a second time.

Convert the wavenumber coordinate from inverse centimetres to hertz, while
retaining the intensity's per-hertz units. Compare $I_\nu/B_\nu^{RJ}$ with
$f(x)$ and show the original residuals with their marginal errors. Show the
classical limiting regime in a theoretical panel; do not imply the FIRAS
frequencies empirically reach $x\ll1$.

Audit the posted reconstruction against modern exact-constant Planck values,
retaining rounding or construction discrepancies explicitly. Original published
residuals remain the residual diagnostic; subtracting a newly evaluated curve
from a rounded reconstructed intensity is a different calculation.

Fixsen et al. (1996), Section 3.3, supplies an approximate frequency covariance
through a correlation sequence. If its coefficients can be verified, retain a
traceable transcription, check positive definiteness, propagate the covariance
through the mode-energy conversion, and report the residual quadratic form as a
descriptive reproduction diagnostic. The residuals already follow temperature
and foreground fitting. Do not treat rows as independent observations, report
a new goodness-of-fit probability, or infer a new temperature uncertainty.
The original analysis's calibration and foreground treatment are inherited;
this work does not reprocess interferograms or reproduce the full sky fit.

## Outputs and interpretation

Retain transformed rows, theoretical curves, numerical summary, a figure,
configuration and source/output SHA-256 provenance. Reproduction is offline;
network acquisition is a separate explicit action. Archive the completed study
without modifying earlier registered runs.

This example establishes a standard physical equality, its quantitative quantum
departure, and a reproducible connection to an existing measured spectrum.
The posted reconstructed blackbody shape is not independent new evidence for
Planck's law or for universal orthopolity. The observational evidence is the
published calibrated FIRAS measurement and analysis, cited with its assumptions.

## Sources

- [NASA LAMBDA product description](https://lambda.gsfc.nasa.gov/product/cobe/firas_monopole_spect.html).
- [NASA LAMBDA download page](https://lambda.gsfc.nasa.gov/product/cobe/firas_monopole_get.html).
- [Fixsen et al. (1996), source article](https://arxiv.org/abs/astro-ph/9605054).
