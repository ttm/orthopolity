# Independent component forecast and a boundary of symmetric exchange

Drafted 24 October; finalized 25 October 2026. **Retrospective prediction
protocol, frozen before the 80
unexposed numerical impedance observations.** This tests the applicability of
the article's first-order symmetric exchange mechanism to a driven electrical
port. It does not test a size spectrum, the closed five-node topology forecast,
or a unique general-law mechanism. Capacitance is the physical reference weight
for charge increments; magnetic storage adds a different state. This is neither
log-orthopolic nor linear-orthopolic size allocation.

## Independent inputs and prior exposure

Danzer, Plank and Rüther's [public archive](https://doi.org/10.5281/zenodo.10794584)
contains an actual circuit: a capacitor in parallel with a series resistor and
inductor. The [paper](https://doi.org/10.1016/j.xcrp.2024.102091), supplementary
Table S3, gives `C = 2.2 µF ±10%`, `L = 5 mH ±1%`, and `R ≈ 9.7 Ω`, the last
explicitly measured with a multimeter. These are the fixed forecast inputs.
Table S2 and the archive description instead print `9.7 mΩ` and a generic
±10% component tolerance. Choose the component-specific Table S3 before target
access; retain the conflicting resistance as a fixed sensitivity scenario.
The resistance has no reported uncertainty. All tolerance intervals below
are conditional scenario envelopes, **not confidence intervals or complete
measurement-error bounds**.

Published fitted values `R=9.67 Ω`, `L=4.83 mH`, `C=2.20 µF`, and the qualitative
resonant response were already exposed. None is a forecast input. The fitted
inductance is outside the printed ±1% nominal tolerance; do not widen it after
seeing the data. Local freezing is not global blinding or external registration.
The other two fitted Table S3 columns were also exposed: ELSA order 36 gives
`8.49 Ω, 4.95 mH, 2.55 µF`, and order 3 gives `9.55 Ω, 4.9 mH, 2.27 µF`.

The two original response files are downloaded and their publisher MD5 hashes
verified. A schema reader discarded JSON numeric tokens but inadvertently
printed the first complex **string** from `z`: `0.1028511-7.564268i`.
Exclude zero-based row 0 from the primary evaluation, fixing this exclusion now;
retain it in a separately labelled all-row descriptive report. All other 80
numerical impedances remain unread. The corrected schema reader emits only
types/lengths, including for strings. Frequency values are allowed forecast
inputs; impedance strings and numeric fields are not. MAT header inspection
failed on the source's MATLAB object; no MAT response was decoded.

## A model-class prediction with no fit

For a passive resistor-capacitor network, let `C` be a positive semidefinite
capacitance matrix, `G` a symmetric positive semidefinite conductance matrix,
and `b` a real current-injection port. Voltage is measured at that same port:

$$Z(\omega)=b^T(G+i\omega C)^{-1}b.$$

For `v=(G+iωC)^{-1}b`, conjugating `v* b` gives

$$\operatorname{Im}Z=-\omega v^*Cv\leq0\quad(\omega>0).$$

If both matrices share a nullspace, restrict to its orthogonal complement and
require `b` orthogonal to it. Singular `G` alone is harmless. The claim requires
collocated input/output; it does not apply to arbitrary transfer functions.
Adding any number of positive capacitors or resistors cannot produce positive
imaginary driving-point impedance under the `exp(iωt)` convention. This is an
elementary passive-circuit identity, not a new network theorem.

The independently specified RLC circuit instead predicts

$$Z=\frac{R+i\omega L}{1-\omega^2LC+i\omega CR},\qquad
f_\times=\frac{1}{2\pi}\sqrt{\frac1{LC}-\frac{R^2}{L^2}}.$$

Its imaginary part is positive below this crossing and negative above it.
Calculate the crossing range over the stated `L,C` box at fixed `R=9.7 Ω`.
Also calculate the union of the two printed resistance scenarios. Monotonicity
over this small box makes the extrema occur at corners; verify it analytically
and numerically before release. Frequencies strictly below the lower bound or
above the upper bound get a separated sign prediction. Those within the range
are unclassified, not discarded from the full-curve error score.

The extended state equations are `C Vdot = Iin - IL`,
`L ILdot = V - R IL`. Their energy
`E=(C V²+L IL²)/2` satisfies `Edot=V Iin-R IL²`. Charge increments and energy
are not interchangeable resources. The experiment is driven, and energy is
dissipated in the resistor. Inertial storage can violate a first-order exchange
description without violating complete energy accounting or the conditional
allocation law.

## Frozen evaluation

1. Decode only frequency inputs; require 81 finite, positive, distinct values
   spanning the documented 100 Hz–10 kHz range within 1%. Preserve row indices,
   sort ascending only for quadrature and crossover brackets. Compute and
   commit every nominal complex forecast and both sign classifications before
   decoding the remaining impedances. No rate, gain, offset, component value,
   time scale or frequency shift is fitted.
2. Primary evaluation uses all 80 unexposed rows, without clipping, smoothing
   or a fitted crossover. Count agreements for both separated sign predictions,
   list every adjacent observed sign-changing bracket and any exact zeros,
   and report whether there is exactly one positive-to-negative crossing whose
   bracket intersects the conditional Table S3 range. Multiple crossings or
   missing coverage fail that descriptive rule. Report unit-scenario sensitivity
   identically. A bracket overlap is compatibility at sampled resolution,
   not an estimate of a continuous crossing with a confidence interval.
3. Let normalized trapezoid weights in `log(f)` be `w`. Report nominal complex
   error `sqrt(sum(w*|Zpred-Zobs|²)/sum(w*|Zobs|²))`. For every passive RC network,
   an optimistic lower bound on that same error is
   `sqrt(sum(w*max(Im Zobs,0)²)/sum(w*|Zobs|²))`: even an arbitrary value in the
   lower half-plane cannot remove the positive imaginary residual. If the
   nominal RLC error is smaller, report that it beats this lower bound for the
   whole collocated passive RC class on the released observations. Also report
   the fixed alternative-resistance curve error. Do not fit an RC benchmark.
4. Report the fraction/count of positive imaginary responses and their magnitudes.
   The frequency points are observations of **one circuit**, not independent
   experimental replicates. There is no raw instrument error model or repeat
   cohort, so no p-value, population confidence interval or noise-qualified
   statistical rejection is justified. The fixed sign/crossing/error rules are
   deterministic descriptive comparisons. Preserve failures as well as passes.
5. Decode all redundant JSON representations after release. Check `omega=2πf`,
   `z_real+i*z_imag=z`, modulus and phase (radians or degrees must be identified
   from the source format, never by changing signs to make a model agree).
   Stop on an unexplained encoding inconsistency. Retain original bytes.
   Independently verify the forecast via the two-state linear equations,
   crossover via admittance roots, and weighted errors without runner imports.

## Execution sequence

Before response access, test the implementation with synthetic RC and RLC
spectra, altered crossing signs, noncollocated counterexamples, source-string
sentinels, and a shared-nullspace RC network. Commit and push the protocol,
config, implementation and source receipts. Generate forecasts using only
frequencies, independently verify them, then commit and push forecast bytes.
Only then evaluate the 80 unexposed responses. Archive the result and independent
verification in the run registry as a locally frozen reanalysis of actual
measurements, with the exposed first row and published fitted values explicit.
Update the article only with the resulting qualified conclusion.
