# Thermal radiation: equal energy per mode and its quantum limit

6 October 2026. This worked example connects orthopolity to classical
equipartition, quantum statistical mechanics and the observed cosmic microwave
background (CMB) spectrum. The resource is **thermal electromagnetic excitation
energy** and the primary comparison units are independently defined field
modes. It establishes a classical equality and a quantitative quantum
departure. Frequency intervals contain different numbers of modes, so a
non-flat spectrum need not mean unequal energy per mode.

The derivation is established physics, organized around the repository's
[allocation formulation](concept.md). It does not derive a new physical law.
The empirical component below is a re-expression of an official calibrated
FIRAS product with explicit provenance; it is not an independent reduction of
the mission observations. The [retrospective analysis specification](thermal-radiation-protocol.md)
declares all 43 rows, the fixed reference temperature, transformations and
limits of inference. The published conclusions and data product were known
before that specification was written.

## 1. Classical equality among declared modes

Take a finite set of $M$ nonzero-frequency electromagnetic normal modes in a
cavity. A polarization and its wave vector together identify a mode. In
canonical equilibrium at $T>0$, write its classical Hamiltonian as

$$H=\sum_{j=1}^{M}H_j,\qquad
H_j=\frac{P_j^2}{2m_j}+\frac{m_j\omega_j^2 Q_j^2}{2}.$$

$Q_j,P_j$ are mode coordinates, $m_j>0$ sets their normalization, and
$\omega_j=2\pi\nu_j>0$. Integrating over the full coordinate and momentum
axes, with $a_*>0$ a fixed reference action that makes $Z_j$ dimensionless,

$$Z_j^{\mathrm{cl}}=\frac{1}{a_*}\int_{\mathbb R^2}
e^{-\beta H_j}\,dQ_j\,dP_j
=\frac{2\pi}{a_*\beta\omega_j},
\qquad\beta=(k_BT)^{-1}.$$

Consequently

$$\langle H_j\rangle=-\partial_\beta\ln Z_j^{\mathrm{cl}}
=\beta^{-1}=k_BT.$$

Each of the two quadratic terms contributes $k_BT/2$. The frequency and the
coordinate normalization cancel from the mean. This is the canonical
equipartition theorem specialized to harmonic modes; its statistical and
oscillator foundations are given in [Tong, classical statistical physics,
Sections 2.2.1 and 2.4](https://davidtong.org/pdfs/teaching/statistical-physics/statphys.pdf).

The allocation measure is counting measure on these modes. A class containing
$M_i$ modes has expected energy $M_i k_BT$ and weight $w_i=M_i$. Equal
expected resource per reference weight follows without redefining the
resource from an observed spectrum. Individual instantaneous mode energies
fluctuate; equipartition asserts equality of equilibrium means. Canonical
equilibrium requires a justified preparation or thermal coupling: uncoupled
Hamiltonian oscillators do not thermalize one another merely because their
Hamiltonian has this form. The partition-function calculation supplies no
relaxation time. See [Tong, canonical ensemble and fluctuations](https://davidtong.org/pdfs/teaching/statistical-physics/statphys.pdf).

## 2. The quantum constraint specifies the departure

A quantum electromagnetic mode has energies
$E_{j,n}=h\nu_j(n+1/2)$, $n=0,1,\ldots$. For thermal radiative allocation
use the excitation above its ground state, $\epsilon_{j,n}=nh\nu_j$.
This excludes the temperature-independent zero-point term $h\nu_j/2$;
including that term defines a different resource.

At equilibrium with photon absorption and emission, photon number is not
fixed and the photon chemical potential is zero. For one mode, let
$x_j=\beta h\nu_j$. Its excitation partition function, occupation
probability and mean excitation are

$$Z_j=\sum_{n=0}^{\infty}e^{-nx_j}=\frac{1}{1-e^{-x_j}},
\qquad p_j(n)=(1-e^{-x_j})e^{-nx_j},$$

$$\bar n_j=\frac{1}{e^{x_j}-1},\qquad
\bar\epsilon_j=h\nu_j\bar n_j
=k_BT f(x_j),\qquad f(x)=\frac{x}{e^x-1}.$$

The geometric sum is finite for every $x_j>0$. This modern mode-occupation
derivation and the zero-chemical-potential condition are described in
[Tong, quantum gases, Section 3.2](https://davidtong.org/pdfs/teaching/statistical-physics/statphys.pdf).
The historical quantization and radiation law are due to
[Planck (1901), *Ueber das Gesetz der Energieverteilung im Normalspectrum*](https://doi.org/10.1002/andp.19013090310)
([accessible translation](https://www.informationphilosopher.com/solutions/scientists/planck/Planck_1901a.pdf));
the modern photon calculation should not be attributed verbatim to the
historical paper.

For $x>0$, $0<f(x)<1$ and

$$f'(x)=\frac{e^x(1-x)-1}{(e^x-1)^2}<0.$$

Indeed the numerator is zero at $x=0$ and its derivative is $-xe^x<0$.
The limiting behavior is

$$f(x)=1-\frac{x}{2}+\frac{x^2}{12}+O(x^4)
\quad(x\to0),\qquad f(x)\sim xe^{-x}\quad(x\to\infty).$$

The specified constraint is the level spacing $h\nu$ relative to thermal
energy $k_BT$. At fixed temperature, high-frequency modes have a small
probability of being excited. Lowering frequency or raising temperature
recovers the classical **relative** equality as $h\nu/(k_BT)\to0$. There is
no sharp frequency cutoff: every finite-frequency mode has positive mean
occupation at $T>0$.

This quantum restriction changes the allowed energy states. The calculation
does not contain an unchanged classical equalizing drift opposed by a second
force. That dynamical decomposition was established for the
[class-exchange model](class-exchange.md), whereas the result here is a
statistical equilibrium law with a controlled classical limit. The relevant
physical distinction is explicit, so both examples can contribute to the
programme without claiming identical mechanisms.

## 3. Counting modes gives the Planck spectrum

For a large three-dimensional vacuum cavity of volume $V$, periodic boundary
conditions give one wave-vector state per volume $(2\pi)^3/V$ in wave-vector
space. A spherical layer has volume $4\pi k^2dk$ and two transverse
polarizations. With $k=2\pi\nu/c$,

$$dM=2\frac{V}{(2\pi)^3}4\pi k^2dk
=\frac{8\pi V\nu^2}{c^3}d\nu.$$

This is a continuum density of modes, valid when the chosen spectral interval
contains many cavity modes. Exact finite-cavity boundary spectra, dispersion
and restricted geometries can change the mode density. The weight is derived
from the field and geometry before any allocation is inspected.

Multiplying the mode density by the mean thermal energy gives

$$u_\nu(T)=\frac{1}{V}\frac{dU}{d\nu}
=\frac{8\pi h\nu^3}{c^3}\frac{1}{e^{h\nu/(k_BT)}-1}.$$

For isotropic radiation, $u_\nu=4\pi B_\nu/c$, so the specific intensity is

$$B_\nu(T)=\frac{2h\nu^3}{c^2}\frac{1}{e^{h\nu/(k_BT)}-1}.$$

Here $u_\nu$ has units J m⁻³ Hz⁻¹ and $B_\nu$ has units
W m⁻² Hz⁻¹ sr⁻¹. These are energy density and spectral radiance, respectively;
the net flux of a perfectly isotropic field is zero. The relation between
mode energy, Rayleigh–Jeans and Planck radiance is worked out in
[Condon and Ransom, Section 2.5, especially equations 2.85–2.88](https://www.cv.nrao.edu/~sransom/web/Ch2.html).

| Comparison measure | Classical mean allocation | Quantum mean allocation |
|---|---|---|
| One electromagnetic mode | $k_BT$ | $k_BT f(h\nu/k_BT)$ |
| Unit frequency and unit volume, $d\nu$ | $8\pi k_BT\nu^2/c^3$ | $u_\nu(T)$ |
| Unit logarithmic frequency and unit volume, $d\ln\nu$ | $8\pi k_BT\nu^3/c^3$ | $\nu u_\nu(T)$ |

Thus classical equality among modes already permits non-flat frequency and
log-frequency spectra. Quantum occupation changes their shape further. If
photons are counted as objects, their resource per object is $q(\nu)=h\nu$;
mean photon number **per mode** tends to $k_BT/(h\nu)$ in the classical
regime. Multiplication by the independent mode density is still required to
obtain photon abundance per frequency interval.

Over a finite classical mode set the total expected energy is $Mk_BT$.
Extending the classical continuum spectrum to arbitrarily large $\nu$ makes
$\int_0^\infty u_\nu^{\mathrm{cl}}d\nu$ diverge. Quantum suppression gives
the finite value

$$\frac{U}{V}=\frac{8\pi(k_BT)^4}{h^3c^3}
\int_0^\infty\frac{x^3}{e^x-1}dx
=\frac{8\pi^5 k_B^4}{15h^3c^3}T^4.$$

The mode equality is therefore an exact classical result and an approximate
quantum result on a declared regime. It is not a statement that all thermal
spectra or all spectral bins receive equal energy.

## 4. What FIRAS measured and what the distributed table contains

FIRAS compared sky radiation against onboard blackbody references. Absolute
calibration used an external calibrator, while the observing configuration
operated close to a differential null. The analysis separated a monopole,
dipole and Galactic components from calibrated sky spectra; subsequent fits
also treated residual Galactic contamination. These processing steps are
part of the measurement, not new operations performed here. The primary
account is [Fixsen et al. (1996), Sections 2–6 and Table 4](https://arxiv.org/pdf/astro-ph/9605054).

NASA's [monopole product description](https://lambda.gsfc.nasa.gov/product/cobe/firas_monopole_spect.html)
states that the distributed spectrum is the sum of a **2.725 K Planck
template and the published 1996 residuals**. The residuals came from an
earlier fitted temperature and Galactic correction; the 2.725 K reference
reflects later calibration work. Consequently the tabulated monopole and
residual are related products, not two independent measurements. The
[download page](https://lambda.gsfc.nasa.gov/product/cobe/firas_monopole_get.html)
links the [version 1 text table](https://lambda.gsfc.nasa.gov/data/cobe/firas/monopole_spec/firas_monopole_spec_v1.txt),
which has 43 rows and these columns:

| Column | Meaning | Published units |
|---|---|---|
| 1 | Spectral coordinate, wavenumber $\tilde\nu$ | cm⁻¹ |
| 2 | Constructed monopole spectral radiance | MJy/sr |
| 3 | Published residual spectral radiance | kJy/sr |
| 4 | Published one-sigma spectral uncertainty | kJy/sr |
| 5 | Modeled Galactic spectrum at the poles | kJy/sr |

The [source manifest and receipts](../data/thermal-radiation/2026-10-06/sources.json)
retain source bytes, checksums and acquisition times. The download listing
gives a delivery date of 1 March 2003, while the file header labels its initial
release May 2005. Preserve that metadata discrepancy rather than inventing a
single release date. The linked NASA description cites Fixsen and Mather
(2002), Mather et al. (1999) and Fixsen et al. (1996) as the relevant analyses.

The source convention is spectral radiance **per Hz**, even though the
horizontal coordinate is given in cm⁻¹. Convert the coordinate using
$\nu=100c\tilde\nu$ with $c$ in m/s. The radiance factors are

$$1\ \mathrm{MJy/sr}=10^{-20}\ \mathrm{W\,m^{-2}\,Hz^{-1}\,sr^{-1}},
\qquad
1\ \mathrm{kJy/sr}=10^{-23}\ \mathrm{W\,m^{-2}\,Hz^{-1}\,sr^{-1}}.$$

An extra Jacobian is needed only if converting the spectral **density** to a
different coordinate, not when relabeling its horizontal axis. Column 5 is
context for foreground modeling; subtracting it again from the supplied
monopole would change the defined data product.

The CMB need not currently exchange energy with a cavity wall to retain a
Planck form. Collisionless redshifting preserves a Planck occupation spectrum
when frequency and temperature both scale inversely with the cosmological
scale factor. The relevant comparison is therefore with a thermal spectrum
preserved from earlier conditions, not an assertion of current equilibrium
with surrounding matter. See [Condon and Ransom, Section 2.6.2](https://www.cv.nrao.edu/~sransom/web/Ch2.html).

## 5. Observation model and descriptive comparison

Fix the reference temperature at the product's $T_0=2.725$ K when displaying
its documented construction. At each tabulated frequency, the inferred mean
thermal energy per mode is

$$\widehat\epsilon_\nu
=\frac{u_\nu}{(1/V)dM/d\nu}
=\frac{c^2 I_\nu}{2\nu^2},\qquad
\frac{\widehat\epsilon_\nu}{k_BT_0}
\longleftrightarrow f\!\left(\frac{h\nu}{k_BT_0}\right).$$

This transformation uses independently established geometry and photon
energy; it does not choose a cost function to flatten the data. Nevertheless,
the distributed monopole already contains a Planck template. Agreement of
the transformed column 2 with $f$ is a visualization of the published result,
not an independent validation of the model.

Use the supplied residual column directly for residual diagnostics.
Recomputing residuals from rounded radiance and wavenumber columns can add
rounding and reconstruction differences. Audit any discrepancy explicitly;
its cause is not established merely by observing that published columns are
rounded. Plot residuals with the supplied
marginal one-sigma errors in their native kJy/sr units, and report descriptive
residual amplitudes relative to the tabulated peak radiance. A diagonal
inverse-variance weighted RMS,

$$\mathrm{WRMS}
=\sqrt{\frac{\sum_i r_i^2/\sigma_i^2}{\sum_i1/\sigma_i^2}},$$

is a defined descriptive summary even when errors are correlated; it is not
by itself a significance test. State the point set, weight convention and
peak normalization. Show the classical Rayleigh–Jeans curve and the quantum
curve at the same reference temperature, with a separate theoretical
low-$x$ panel. The FIRAS interval is not a measurement of the
$h\nu\ll k_BT$ limit.

Correlations are documented and approximately reconstructible. Fixsen et al.
(1996), Section 3.3, supplies 43 lag coefficients $Q_\ell$, with
$Q_0=1$, $Q_1=0.176$ and $Q_2=-0.203$, for the spectral spacing
$0.4538$ cm⁻¹. Together with Table 4 uncertainties they specify

$$C_{ij}=\sigma_i\sigma_jQ_{|i-j|}.$$

Use channel-index separation for this sequence; rounding the published
wavenumbers does not alter their order. With $C$ expressed in
$(\mathrm{kJy/sr})^2$, the covariance of normalized mode-energy residuals is
$C^{\mathrm{mode}}=ACA$, where $A$ is diagonal and

$$A_{ii}=\frac{10^{-23}c^2}{2\nu_i^2k_BT_0}.$$

This propagates the quoted spectral covariance under the declared linear
conversion, without adding temperature or calibration uncertainty. If a quadratic residual diagnostic
$r^TC^{-1}r$ is computed, label it as a reconstruction using the approximate
published statistical covariance. It is not automatically a new chi-square
test with 43 independent observations: the residuals already follow
temperature and foreground fitting, and absolute calibration and foreground
systematics require the original analysis. The authors' quoted uncertainties
and their original fit conclusions retain their published interpretation.

A fresh temperature estimate, a new spectral-distortion bound or model
selection claim would require the corresponding calibration, band response,
nuisance parameters and covariance propagation. No such claim is needed for
this milestone. A later temperature determination, such as
[Fixsen (2009)](https://doi.org/10.1088/0004-637X/707/2/916), should not replace
$T_0$ inside this product's construction without explaining the resulting
reference change.

## 6. Numerical demonstration and retained results

Run `thermal-radiation-2026-10-06` retains all 43 source rows, the original
five columns and their converted quantities. The temperature is the product's
2.725 K reference and all physical constants take their
[exact SI values](https://www.bipm.org/en/measurement-units/si-defining-constants).
No parameter is fitted, no row is selected after inspection, and no new
observations are collected. The [analysis specification](thermal-radiation-protocol.md)
records the retrospective scope and prior team-level source-table exposure.

| Quantity | Retained result |
|---|---|
| Frequency interval | 68.0529--639.4573 GHz |
| $x=h\nu/(k_BT_0)$ interval | 1.19854--11.26206 |
| Inferred $\widehat\epsilon/(k_BT_0)$ range | 0.000132119--0.517685 |
| Predicted $f(x)$ range on these channels | 0.000144735--0.517667 |
| Minimum eigenvalue of the correlation matrix | 0.0723600 |
| Published-residual quadratic $r^TC^{-1}r$ | 49.77414 |
| Diagonal inverse-variance weighted residual RMS | 18.89628 kJy/sr |
| Peak tabulated monopole | 383.478 MJy/sr |
| Weighted residual RMS / tabulated peak | 49.27605 ppm |
| Reconstruction discrepancy range | -0.126547--7.597571 kJy/sr |

The discrepancy is defined as
$I_{\mathrm{posted}}-[B_\nu(T_0)+r_{\mathrm{published}}]$ in common radiance
units, evaluated at the displayed source frequencies. Its cause remains
unassigned. The original fitted residuals are used for both residual summaries.
The quadratic form uses the approximate covariance prescription and does not
reproduce the original paper's full-analysis statistic of 46 for 40 degrees of
freedom. The RMS uses the explicitly defined diagonal weights above, even
though channels are correlated; neither number is presented as a new test.

The full 43-by-43 covariance and its propagation to normalized mode energy are
retained. The largest relative mismatch between propagated marginal variances
and squared converted marginal errors is $4.44\times10^{-16}$, numerical
roundoff. Temperature uncertainty and additional calibration or foreground
uncertainty are not added by this linear conversion; the observed product
retains the scope of the published analysis.

![Thermal mode energy and FIRAS comparison](../results/thermal-radiation/thermal-radiation.png)

The theoretical panel shows the classical plateau and quantum suppression.
The FIRAS panels show the reconstructed product, the same spectrum divided by
the independent mode density, and the original residuals with marginal
one-sigma errors. The channels do not reach the classical $x\ll1$ regime.
The plotted agreement in the middle panels inherits the Planck template in
the supplied product; the residuals and original measurement paper carry the
observational content.

Reproduce the calculation offline:

```bash
make thermal-radiation PY=python3.11
make thermal-radiation-registry PY=python3.11
make registry-verify PY=python3.11
```

The first command verifies four downloaded sources and writes a reproduction
under `build/reproductions/thermal-radiation/`. It preserves the retained
`results/thermal-radiation/` directory. The second command archives/checks the
retained study without rerunning it. Source acquisition is separately explicit
through `experiments/fetch_thermal_radiation.py --fetch`; normal analysis never
uses the network.

The [summary](../results/thermal-radiation/summary.json),
[transformed rows](../results/thermal-radiation/spectrum.csv),
[covariance entries](../results/thermal-radiation/covariances.csv),
[theoretical curve](../results/thermal-radiation/theory.csv),
[vector figure](../results/thermal-radiation/thermal-radiation.svg), and
[execution provenance](../results/thermal-radiation/provenance.json) retain
the results and their exact inputs. Numerical checks include direct geometric
partition sums, classical and Wien limits, the Stefan--Boltzmann integral,
source-tampering rejection, all-row preservation, and independent covariance
conversion checks.

## 7. What this contributes

Thermal radiation supplies an exact equality among classical mode means, a
quantitatively specified quantum departure, and a limiting regime in which
relative equality returns. Independent counting of modes explains why even
the classical neutral allocation does not look flat per unit frequency.
FIRAS then supplies a published physical observation of the quantum spectral
form, with its calibrated residuals available for transparent re-expression.

The example advances the principle through specified resources, units,
measures and conditions. Its non-flat spectral shape is explained by mode
degeneracy and quantum occupation. The mode statistics and the observational
comparison establish that result under their stated assumptions; extensions
to other resources and systems require their own derivations.
