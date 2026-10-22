# Membrane exchange: kinetics transfer, empirical interpolation remains competitive

**The fixed exchange forecast transfers to four later membrane pairs, but does
not outperform every declared alternative.** Its mean absolute contrast error
is **0.042285 of initial total concentration**, versus 0.547178 for persistence,
0.462221 for immediate mixing and **0.041383 for empirical interpolation**.
Thus exchange improves the two limiting models by 92.27% and 90.85%, but is
2.18% worse than the empirical trajectory forecast. No target rate was fitted.

The separate target stock test gives **F(28,3)=2.03717, p=0.30855**. This is
compatibility with the declared physical, sampling and optical-error model,
not proof of conservation. Observed total recovery relative to sampling-adjusted
initial stock ranges from **94.82% to 106.51%**.

## What was fixed, and when

The [source audit](exchange-source-followup-2026-10-20.md) identified the
[Benstead et al. public archive](https://zenodo.org/records/17238337), associated
with [their membrane workflow article](https://doi.org/10.1039/D5DD00523J).
The retained original ZIP matches the publisher's MD5 and the pinned SHA-256.
We use four automated acid-orange/PEG25-on-PES pairs from 5 May 2025 (96
chamber measurements) to predict four manual pairs from 3 June (56 later
chamber measurements), conditional on their eight measured time-zero inputs.
All membranes remain included. Published aggregate diffusivities and qualitative
method comparisons were already known; this is a locally frozen retrospective
comparison, not a blind replication or external preregistration.

- **55b3970:** protocol, configuration, qualification code, independent verifier
  and synthetic tests committed and pushed before numerical optical standards,
  selected earlier trajectories or target baselines were read.
- **8c7f60a:** passing qualification and remaining fixed forecast/scoring
  implementation committed before target access.
- **68694fd:** predictions and independent verification committed and pushed
  before the first numerical access to all 56 later responses on 22 October.

The [protocol](membrane-exchange-protocol-2026-10-20.md) retains its original
rules. Data access receipts accompany the qualification, forecasts and results.
No gate, benchmark, source split or kinetic parameter was adjusted after
observing the target trajectories.

The resource is dissolved dye amount and the reference measure is compartment
volume. Equal 11 mL chambers also permit ordinary counting. **Neither
log-orthopolic nor linear-orthopolic size allocation is tested.** Ordinary
diffusion predicts the same kinetics. This is not the proposed five-compartment
network intervention or a unique orthopolity mechanism.

## Qualification and uncertainty

Each run's five optical standards fit raw absorbance A=aC+b, with a retained
intercept and no second blank subtraction. Chamber concentration is 10(A-b)/a.
The assumed raw errors are independent Gaussian with the same variance across
standards and chamber samples within each run. Nominal standard concentrations
are treated as exact. Five standards do not establish linearity, equal variance,
absence of matrix effects, temporal stability or accurate pipetting.

Both slopes have positive 99% lower confidence endpoints; all baseline gates
pass. Earlier and later optical residual SDs are 0.017386 and 0.012915
absorbance, respectively. Only three residual degrees of freedom determine the
noise estimates. Earlier contrast fits have much smaller residual sums of
squares than their acceptance thresholds; non-rejection should not be read as
a precise demonstration of the physical/observation assumptions.

Each previous 20 microlitre withdrawal and water replacement depletes an 11 mL
chamber by f=549/550. Sampling is approximated as simultaneous and observations
as immediately before removal. Each pair's earlier raw contrast fits
Delta*f^j*exp(-2*g*t/11), profiling its initial amplitude. The intercept cancels
from the contrast, and the amplitude absorbs the optical slope.

| Earlier pair | Effective conductance (mL/h) | Whole 99% accepted interval (mL/h) |
| --- | ---: | ---: |
| S1 | 0.180520 | [0.098482, 0.297112] |
| S2 | 0.161034 | [0.086965, 0.261356] |
| S3 | 0.159083 | [0.085715, 0.258219] |
| S4 | 0.131292 | [0.067724, 0.211934] |

All four intervals are nonempty and exclude zero and infinite rates. They
invert the absolute residual F(11,3) test, not an approximate RSS-increment
interval. The separate 44-residual earlier stock test gives F=0.266883,
p=0.982436. It includes correlated baseline and shared optical-intercept errors.
All mandatory qualification gates pass, authorizing the planned transfer.

![Earlier kinetics, total recovery and rate uncertainty](../results/membrane-exchange-qualification-2026-10-20/qualification.png)

The point kernel averages the four fitted exponentials. It does not
exponentiate the average rate. Target amplitudes use only the measured baselines.
The forecast archive retains the full 56-by-56 conditional covariance matrix
from the shared slope/intercept and eight baseline readings. Conditional
concentration SDs range from **8.09 to 11.78 micromolar**. The separate rate
sets give broad kernel envelopes; at 69.6 h the point kernel is 0.13890 and
the envelope is [0.04161,0.34568]. These are not prediction intervals for a
new membrane. The declared +/-10 minute elapsed-time sensitivity changes any
chamber point forecast by at most **1.803 micromolar**; it is not a rigorous
bound for unrecorded sequential collection times or temporary volumes.

The optical standards span 0--80 micromolar in diluted aliquots. All eight
target baseline estimates are slightly outside that support. Recipient
baselines are negative (-6.16 to -7.66 micromolar chamber estimates) and remain
unclipped, consistent with the predeclared observation-compatibility gate.
Seven earlier readings are substantively outside support; the literal frozen
output counts eight because one mathematically boundary-valued estimate is
80.00000000000001. This floating-point flag does not affect any decision.
All 56 later measurements lie within calibration support.

## Complete target comparison

Errors below normalize each contrast by its pair's measured initial total
concentration, then average equally over seven times and four pairs. They are
not percentages of the instantaneous contrast, which becomes small as mixing
proceeds. The empirical benchmark interpolates the mean earlier sampling-adjusted
contrast, holding its final value constant beyond 66 h. It uses no target fit.

| Target pair | Exchange | Persistence | Instant mixing | Empirical trajectory |
| --- | ---: | ---: | ---: | ---: |
| S5 | 0.049057 | 0.518199 | 0.491243 | 0.047292 |
| S6 | 0.064851 | 0.502337 | 0.506983 | 0.063086 |
| S7 | 0.044069 | 0.610383 | 0.397382 | 0.045832 |
| S8 | 0.011163 | 0.557795 | 0.453277 | 0.009322 |
| Equal-pair mean | **0.042285** | **0.547178** | **0.462221** | **0.041383** |

Exchange beats each limiting model in all four pairs, and empirical
interpolation in one. The all-benchmark advantage fails at the frozen zero
improvement boundary. The empirical advantage is small in absolute terms
(0.000902 of initial total), but no equivalence margin was registered and none
is introduced afterward. Four favourable pair signs alone would yield a
one-sided sign-test probability of 1/16; no population significance is claimed.
The largest individual exchange contrast error is 0.090677 of initial total.

![All later-pair forecasts and separately observed stock recovery](../results/membrane-exchange-transfer-2026-10-22/transfer.png)

Average joint chamber absolute error is 0.023254 of initial total for exchange,
versus 0.022843 for the empirical alternative. Average normalized total-stock
absolute error is 0.021982 for all four forecasts: they share the same depleted
baseline total, so the kinetic ranking cannot establish conservation.

| Target pair | Minimum total recovery | Maximum total recovery |
| --- | ---: | ---: |
| S5 | 99.81% | 104.43% |
| S6 | 98.63% | 104.58% |
| S7 | 94.82% | 106.51% |
| S8 | 98.82% | 105.40% |

The total-stock statistic F=2.03717 is below its frozen 1% critical value
26.53118. Its non-rejection (p=0.30855) depends on the noise assumptions above;
there is no claim of exact recovery. Volume changes, matrix effects, evaporation,
unmeasured stirring and temporal optical drift are not separately identified.
Date, membrane batch and manual/automated procedure change together. Conflicting
source thickness units and post-experiment thickness measurements are avoided
by transferring effective conductance without claiming an independently known
permeability or diffusivity.

## Scientific contribution and next prediction

This result adds a real cross-cohort kinetic forecast to the framework's ideal
exchange construction. The same measured initial conditions and sampling rule
predict substantially better than either frozen or immediate allocation.
The full trajectory also makes the model's time dependence observable without
fitting a target rate. That is a conditional empirical transfer.

It does not establish a predictive advantage over the earlier empirical
trajectory, distinguish orthopolity from ordinary diffusion, or identify a
universal neutral size allocation. Stock compatibility and the kinetic ranking
remain separate observations. A useful next advance is the already derived
pair-to-network topology intervention with independently known geometry and
absolute-stock controls, where the graph predicts a new relaxation pattern.
Another fit to these exposed targets would not supply that evidence.

## Verification and reproduction

Qualification checks **2,854 numerical quantities** independently using optical
centered sums, 80-digit polynomial root isolation, an original-observation
error map and explicit sampling-event ODE integration. Maximum discrepancy is
5.85e-12. Transfer verification checks **5,184 quantities before release** and
**7,496 afterward**, maximum discrepancy **4.37e-11**, using an independent
mixing formula, ODE solution, complex-step derivatives and a separately assembled
69-observation error map for the 28 target stock residuals. A separate CSV
decoder also matches all 56 released absorbances, eight target baselines and
five optical-standard records exactly to the original archived cells, without
importing the production reader. Numerical agreement does not validate the
physical assumptions.

The [qualification](../results/membrane-exchange-qualification-2026-10-20/qualification.json),
[sealed forecasts](../results/membrane-exchange-forecast-2026-10-22/predictions.json),
[complete result](../results/membrane-exchange-transfer-2026-10-22/result.json)
and [independent verification](../results/membrane-exchange-transfer-2026-10-22/verification.json)
retain every selected value, prediction, uncertainty and score.

Reproduce all deterministic artifacts offline in a new directory:

```sh
make membrane-exchange PY=build/main-venv-2026-10-09/bin/python STUDY_OUTPUT_ROOT=build/membrane-replay-new
```

The reproduction compares JSON and figures byte-for-byte. Execution timestamps
record each actual run and are not expected to match. The append-only registry
retains the preceding 43 study entries unchanged and records this complete
qualification/transfer as one actual-measurement study. Main section 4.6 and
supporting S5.18 retain the result and its failed all-benchmark advantage.
