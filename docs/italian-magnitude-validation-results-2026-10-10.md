# Italian test stops at the magnitude-validation gate

**The registered magnitude estimator fails the necessary synthetic check.**
Of 56 required scenarios, 45 fail at least one frozen criterion. This includes
30 of 32 noiseless converted-magnitude scenarios, so the finding does not depend
on the assumed Gaussian measurement errors. No real Italian sequence, Mc, b,
D2 or regression has been calculated. Neither physical prediction is favoured.

The [protocol](italian-magnitude-validation-protocol-2026-10-10.md) and implementation
were committed at `ab14b6b`. A sequence-input unit-test fix was committed at
`42a79c9`, before the ensemble ran; it did not change the design or thresholds.
The [configuration](../configs/italian_magnitude_validation_2026-10-10.json)
requires bias ≤0.05 in absolute value, at least 90% coverage of diagnostic
nominal 95% intervals, and at least 95% eligibility in every required cell.
Failure explicitly stops this bounded Italian attempt before real fitting.

## What was tested

There are 400 independent repetitions of 7,000 events in each of 72 cells:
two true b-values, four lower magnitude supports and nine observation models.
Each eligible sample receives the original MAXC+0.2 and Aki–Utsu calculation,
with 500 conditional bootstrap resamples. All 28,800 samples pass the minimum
200-event population gate; the failures concern bias and uncertainty calibration.

The true b-values 1 and 1.5 distinguish the magnitude marginals of the proposed
**log-orthopolic** rupture-territory relation b=D2/2 and the b=1 alternative
on ideal planar/volumetric supports. This checks the magnitude component, not
the full geometry, sequence selection or Deming-regression decision.

The [HORUS paper](https://doi.org/10.1785/0220200148), Tables 7 and 9, supplies
the ML/Md conversion coefficients and ML scatter scales. Single-source scenarios
isolate their effects: simulate true exponential magnitudes, convert to the
source scale, optionally add Gaussian error, round the source to 0.1, convert
to Mw proxy and round to 0.01, then apply the registered 0.1 rounding. The normal
distribution, hard lower support and homogeneous source populations are explicit
simulation assumptions. We have not fitted their frequencies or detection law
to the Italian catalogue, reconstructed all HORUS averaging/switching rules,
or established that every real mixture has the simulated biases.

| Observation model | Cells passing / 8 | Mean-bias range | Coverage range |
|---|---:|---:|---:|
| Direct rounded Mw control | 7 | −0.017 to −0.003 | 88.3–95.5% |
| ML before 2011, no scatter | 1 | −0.342 to +0.067 | 0–94.5% |
| ML from 2011, no scatter | 1 | −0.216 to +0.035 | 0–90.8% |
| Md before April 2013, no scatter | 0 | −0.304 to +0.377 | 0–32.8% |
| Md from April 2013, no scatter | 0 | +0.035 to +0.347 | 0–45.8% |
| Earlier ML with source scatter 0.18 | 0 | −0.114 to +0.028 | 1.3–89.0% |
| Later ML with source scatter 0.16 | 2 | −0.067 to +0.037 | 22.5–95.0% |

The two additional shared-calibration-slope sensitivities are outside the gate;
their 16 cells remain in the output. The full
[cell table](../results/italian-magnitude-validation-2026-10-10/cells.csv) and
[summary](../results/italian-magnitude-validation-2026-10-10/summary.json)
include Monte Carlo errors, Wilson coverage intervals, every failure and the
independent population calculation. A single near-threshold control failure
could be sensitive to Monte Carlo variation; the large proxy failures are
not an inference from that borderline control.

![Bias and interval coverage in every simulated scenario](../results/italian-magnitude-validation-2026-10-10/validation.png)

## Why rounding matters

In the earlier ML conversion, a source grid 1.6, 1.7, 1.8 produces proxy
hundredths 1.54, 1.65, 1.75. Under the declared NumPy rounding, the registered
tenths are 1.5, 1.6, 1.8: **the 1.7 class is missing**. With true b=1.5 and
lower Mw support 1.5, the population MAXC+0.2 is 1.7. Events first appear in
the 1.8 bin, while the estimator subtracts `1.7−0.05` from their mean.

The resulting average b is **1.15785**, with Monte Carlo SE 0.00071; an
independent integration over source-bin probabilities gives **1.15791**.
None of its 400 diagnostic intervals covers 1.5. For the later ML conversion,
true b=1.5 above support 2.0 gives mean **1.28430**, compared with the population
limit **1.28507**, again with zero coverage. The largest positive nominal bias
is an earlier-Md case: mean **1.87694** for true b=1.5.

Even the direct control has the small known finite-bin approximation error:
for a complete 0.1 lattice, the population limit of the implemented correction
is `2*tanh(b*0.1*ln(10)/2)/(0.1*ln(10))`, or **1.48526** when b=1.5.
This remains a magnitude-estimator issue, not an observed earthquake result.

Some population-mode bins nearly tie. The sampled MAXC can then change between
repetitions, so an ensemble mean need not equal the single population-mode
limit. Mode gaps are retained explicitly; no mismatching cells are discarded.

## What a repair would need

For noiseless, singly converted complete tails, an exact geometric likelihood
on the **original source bins** recovers b in the independent population
calculation. Its simulated point estimates also recover the nominal value.
This diagnoses the source of the problem; it is not a registered replacement.
With measurement error near a lower detection boundary, even that diagnostic
can remain biased (one earlier-ML b=1.5 scenario gives about 1.390).

A future attempt would need a likelihood that represents source-specific bins,
calibration, detection and source switching/averaging, plus uncertainty shared
by all events using a calibration. A deliberately narrower homogeneous cohort
is another design option, but would need fresh validation and unchanged
population/resolution gates. Neither option has been tested on real responses.

HORUS equation 4 also illustrates within-bin jitter using b=1. The retained
`_o` input files avoid this extra assumption. Table 9's post-2011 ML covariance,
as printed, violates the covariance bound for its two printed standard errors:
`0.0011 > 0.065*0.016`. We have neither diagnosed the cause nor repaired it.
The two marginal slope perturbations are sensitivities, not a joint calibration
uncertainty calculation. These issues strengthen the need for an observation
model; the noiseless failures already establish the present stop decision.

## Reproduction and verification

```bash
# Choose a new output root if this directory already holds a completed run.
make italian-magnitude-validation PY=python3.11
make registry-verify PY=python3.11
```

The driver needs NumPy, pandas and SciPy, with Matplotlib for the plot. It reads
the fixed design and hashes the retained methods PDF; it never reads real
earthquake rows. Default outputs go to `build/reproductions`, and the simulation
refuses to overwrite a populated output directory.

The [verification](../results/italian-magnitude-validation-2026-10-10/verification.json)
checks method/artifact hashes, independently recomputes decisions from the
compressed repetition table using the standard-library CSV reader, and
reconstructs one sample per cell for comparison with the unchanged original
runner. All 72 point estimates and completeness calculations agree; literal
event-resampling bootstrap SEs agree within Monte Carlo variation. Unit tests
also compare multinomial-bootstrap SEs with the analytic delta approximation
and integrated grid estimates with exact exponential-tail predictions.

The run is recorded as **simulation**, without adding a real b/D2 comparison.
The Southern California six-sequence eligibility finding, the Italian source
crosswalk and every earlier empirical result remain intact. The manuscript now
incorporates the completed geometry tests and these seismic limitations. Further
catalogue acquisition is not the immediate remedy for the identified problem.
