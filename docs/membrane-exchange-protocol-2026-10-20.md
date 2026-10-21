# Frozen protocol: independent membrane-pair exchange transfer

Drafted 20 October; frozen 21 October 2026 before numerical source access.
Locally frozen retrospective test of Benstead et al. (2026),
DOI [10.1039/D5DD00523J](https://doi.org/10.1039/D5DD00523J), using the
[qualified public archive](exchange-source-followup-2026-10-20.md). Published
aggregate outcomes and four calibration diffusivities are known. No selected
raw absorbance, optical-standard values or source notebook outputs have been
inspected at protocol preparation. This is not a globally blind experiment.

The resource is dissolved dye amount and the reference measure is chamber
volume. Equal 11 mL chambers also permit ordinary counting. This is **neither
log-orthopolic nor linear-orthopolic size allocation**. The test transfers
effective kinetics between two cohorts; ordinary diffusion makes the same
prediction. It does not test the five-node topology factor or identify a unique
orthopolity mechanism. Procedure, date and new membranes change together.

## Source, split and access order

`configs/membrane_exchange_2026-10-20.json` pins the original ZIP SHA-256 and
all numerical constants. Archive names ending in `metadata.csv` contain
outcomes and must not be inspected as unrestricted metadata.

1. Commit this protocol, configuration, gated reader, qualification code,
   independent verifier and synthetic tests before reading any numerical
   optical standards or selected sample absorbances.
2. Release both runs' five optical calibration rows, all 96 observations from
   automated run **20250505**, and only the **eight time-zero observations**
   from manual run **20250603**. The latter are forecast inputs, not targets.
   Retain all four membranes in each cohort, with source identities S1–S4 and
   S5–S8. Do not inherit response-based outlier exclusions.
3. Execute the qualification below. If any mandatory gate fails, retain and
   independently verify the stopped result. **Do not decode the 56 later
   manual-run absorbances, fit a correction, or change the gate to continue.**
   A follow-up would need an explicitly dated new design and exposure record.
4. If qualification passes, generate and independently verify the forecasts
   and uncertainty diagnostics below. Commit their exact bytes before opening
   the 56 later observations. Any remaining implementation work must follow
   these fixed rules and be committed before target access.
5. Evaluate all seven positive-time observations in both chambers of all four
   target pairs. Keep failed predictions and stock discrepancies in the report.

Read only raw `Abs_raw`, standard `C_uM`, and declared identity/time fields.
Source-derived concentrations, blank-corrected `Abs`, fitted transport
coefficients and post-experiment thickness are not inputs. Mislabelled geometry
is not repaired from response data. The source reader checks the complete fixed
identity/time grid and source hash. Evaluation requires an explicit gate and a
committed, replay-verified forecast file.

## Optical calibration and baseline qualification

For each run separately, fit raw absorbance $A=aC+b+\epsilon$ by ordinary
least squares to its five distinct prepared concentrations. Use the full affine
calibration, including its intercept. Do not subtract another blank. Let
$X=(C,1)$, $H=(X^TX)^{-1}$ and $s^2=\mathrm{SSE}/3$.
The covariance of $(\hat a,\hat b)$ is $s^2H$; report it rather than treating
slope and intercept as independent. Convert chamber readings as
$C_{\rm chamber}=10(A-\hat b)/\hat a$.

Stop if calibration is singular, its residual variance is numerically zero,
or the lower endpoint of the
two-sided 99% Student-$t_3$ slope interval is not positive. Zero residual
variance is unresolved observation uncertainty, not perfect measurement.
Numerical zero means $\mathrm{SSE}\le100\epsilon^2\max(1,\sum A_i^2)$,
where $\epsilon$ is double-precision machine epsilon; this is a rounding
check, not an assumed physical noise floor.
Report the concentration support, residuals and extrapolation without adding
an unregistered goodness-of-fit cutoff. Five standards do not establish
linearity outside their support, temporal stability or matrix equivalence.

For all eight pairs, baseline raw contrast $A_D-A_A$ and corrected total
$A_D+A_A-2\hat b$ must be positive. Individual baseline estimates may be
negative because of noise; do not clip them. Stop if any of the 16 corrected
baseline readings is below
$-t_{1-0.01/16,3}s\sqrt{1+H_{bb}}$. This is a separate observation-compatibility
gate with a Bonferroni family bound, not an estimate that the true stock is
negative. Preserve the measured values and their shared calibration covariance.

## Sampling and effective-rate model

Primary calculation approximates paired sampling and replacement as
simultaneous, with constant volume $V=11$ mL between collections. Each prior
collection multiplies both chamber stocks by $f=1-0.02/11=549/550$.
Observations are immediately before collection: index $j$ has $j$ prior
collections, including time-zero removal when $j>0$.

For conductance $g$ in mL/h, the contrast rate is $\lambda=2g/V$. Fit each
calibration pair's raw difference $d_j=A_{D,j}-A_{A,j}$ with

$$d_j=\Delta\,\phi_j(z)+\eta_j,\qquad
\phi_j(z)=f^jz^{t_j/6},\qquad z=e^{-6\lambda}\in[0,1],$$

with $\phi_0=1$, including at $z=0$. Persistence is $z=1$ and immediate
mixing after baseline is $z=0$. For each $z$, profile the nuisance initial
amplitude $\hat\Delta(z)=\phi^Td/(\phi^T\phi)$ and calculate RSS. Minimize
RSS over the full closed interval, including both endpoints. The primary
implementation uses a 4,097-point grid and refines every detected local minimum;
the independent verifier checks the full polynomial problem for the equally
spaced calibration times. Retain disconnected accepted sets if present.
The confidence-set search includes refined minima so narrow intervals are not
discarded solely because no grid point falls inside them.

At each fixed true $z$, under the stated observation model,

$$\frac{\mathrm{RSS}(z)}{2(n-1)s^2}\sim F_{n-1,3},\qquad n=12.$$

Use its 99% inversion set, **not** a profile-RSS-increment approximation.
Every calibrator must have a nonempty set excluding both endpoints and a
positive fitted amplitude. Otherwise its finite rate is unresolved or the
exponential model is incompatible: stop before target release. Report whole
accepted intervals, their transformed rate/conductance bounds and endpoint
tests. Do not impose an arbitrary maximum rate or acceptable interval width.

Profiling calibration amplitudes uses all earlier observations. Target
amplitudes instead come only from their eight measured baselines. This
distinction is intentional. Raw contrasts cancel the optical intercept;
the unknown contrast amplitude absorbs the slope, so rate fitting needs no
concentration conversion. Do not add calibration-coefficient errors to these
raw contrasts.

## Independent stock-recovery gate

For the 44 positive-time calibration totals define

$$r_{kj}=(A_D+A_A)_{kj}-f^j(A_D+A_A)_{k0}
                     -2(1-f^j)\hat b.$$

Let $B_{(k,j),k}=f^j$ and other entries of that row be zero, and
$u_{kj}=1-f^j$. The covariance divided by $\sigma^2$ is

$$Q=2I+2BB^T+4H_{bb}uu^T.$$

It includes shared baseline errors and the shared optical intercept. Under
the joint model,

$$F_{\rm stock}=\frac{r^TQ^{-1}r}{m s^2}\sim F_{m,3},\qquad m=44.$$

Stop if its upper-tail probability is below 0.01. Report the total trajectory,
pairwise discrepancies and statistic even when a rate gate fails. Four 99%
rate sets and this 1% stock test have at least 95% joint coverage/non-rejection
under the full assumed model by a union bound; this is not a power guarantee
or a guarantee for the separate optical/baseline gates.

The finite-sample statements assume known nominal standard concentrations and
independent homoscedastic Gaussian raw-absorbance errors shared by standards
and samples within each run. They omit uncertain pipetting, matrix effects,
evaporation, unmeasured stirring and drift. A rejection identifies an
incompatibility of **that joint physical/measurement/sampling model**, not
the chemical cause, and not a rejection of the general law.

## Forecasts and comparisons, conditional on qualification

The point forecast uses the arithmetic mean of the four fitted exponential
kernels, $K(t)=\frac14\sum_k e^{-\hat\lambda_k t}$; it does not exponentiate
the mean rate. For target pair baseline total $T_0=C_{D0}+C_{A0}$ and contrast
$D_0=C_{D0}-C_{A0}$,

$$\widehat C_{D,A}(t_j)=\frac{f^j}{2}[T_0\mathbin{\pm}K(t_j)D_0].$$

Generate deterministic kernel envelopes over the four full 99% accepted rate
sets. Propagate the target run's shared affine-calibration covariance and
independent baseline reading errors by the Jacobian of the formula, preserving
covariance between chambers and times. Report pointwise conditional optical
uncertainty separately from rate-set and between-calibrator sensitivity. These
are not population prediction intervals for new membranes. Do not discard
boundary or incompatible uncertainty scenarios to tighten the result.

Compare three predeclared kernels: persistence $K=1$, instantaneous mixing
$K=0$ at positive times, and an empirical kernel formed by averaging the four
earlier $d_j/(d_0f^j)$ trajectories, linearly interpolating in time and holding
the last value constant beyond 66 h. Do not clip that empirical kernel.
All comparators share the sampling-depleted baseline total.

Primary score is absolute contrast error divided by each target pair's initial
corrected total, averaged equally over seven later times and then four pairs.
Report each pair, each comparator and absolute/relative differences; a positive
estimated improvement has boundary zero. No arbitrary engineering accuracy
cutoff or population-significance claim is introduced. Four favourable paired
signs alone yield only a one-sided sign-test probability of 1/16.

Separately apply the stock test to the 28 target follow-up totals with that
run's optical calibration, and report normalized total and joint chamber
errors. Kinetic superiority cannot verify stock recovery: a common total
error cancels from squared-error rankings of these kernels. Non-rejection of
the stock test is compatibility under the stated noise model, not proof of
conservation.

Sequential collection differs from the primary approximation. Report rate
forecast changes when elapsed times shift by $\pm10$ minutes (clamped at zero)
without fitting shifts to data. This is a declared timing sensitivity scale,
not a rigorous bound on the unrecorded timing or temporary-volume changes.
If qualification stops, retain this limitation without decoding targets to
rescue it. Procedure and batch remain confounded, and four membranes per run
cannot establish equivalence of collection methods.
