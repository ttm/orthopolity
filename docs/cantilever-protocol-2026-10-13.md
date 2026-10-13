# Heated-cantilever transfer: local analysis freeze

**13 October 2026.** Retrospective archival prediction, not a blinded experiment
or an external preregistration. The published qualitative outcomes, including
problematic modes, were known before this protocol. Numerical damping and
fluctuation responses have not been examined at this freeze. Predictor-only
inspection is recorded in `data/cantilever/2026-10-13/predictor-audit.json`.
The design and code must be committed before fitting; computed forecasts must
be committed separately before evaluating numerical fluctuation outcomes.

## Question and reference measure

Can a low-temperature damping curve predict both high-temperature damping and
mode energy, without fitting that energy? The finite reference measure counts
the specified mechanical modes; the resource is mean harmonic energy, with
potential energy per coordinate `k_B T_fluc/2`. At equilibrium the modal means
are equal. Out of equilibrium, a spatial temperature field and local dissipation
can produce unequal means. This is neither a linear-size nor a log-size density.

The known extended fluctuation-dissipation relation supplies this physical
realization. Orthopolity alone does not derive it. The test asks whether a
specified constraint model enables an independently fixed forward prediction;
it does not establish universality or rediscover equipartition. Equilibrium
normalization already assumes equipartition and cannot be scored as evidence.

## Sources and conventions fixed before responses

Fontana and Bellon (2023), *Physical Review E* **107**, 034118,
[article](https://arxiv.org/html/2208.08356v2),
[DOI](https://doi.org/10.1103/PhysRevE.107.034118), and the
[versioned CC BY 4.0 archive](https://zenodo.org/records/7640708)
(DOI 10.5281/zenodo.7640708). Retain and checksum `data.mat`, `plots.m`,
`Functions.zip`, the metadata and article. Credit the original authors.
Never execute publisher scripts or use `TTHEO` as input or validation oracle.

Use all eleven published cases: C30 flexural 1–5 and torsional 1; C30C flexural
1–4 and torsional 1. C30C is the coated C30 preparation, not an independent
replicate. Retain C30 flexural 3 and C30C torsional 1 despite known difficulties.
Exclude C100 because global damping alone cannot identify whether its loss is
at the clamp or uniformly distributed. Extra unplotted archive columns are not
part of this cohort. No mode is selected from its numerical agreement.

**Pre-response temperature discrepancy.** Article section II.5 states a 295 K
base. The plotting script uses 300 K, and `2*TAVG-TMAX` is 300 K throughout C30
and C30C except the first C30C row (299.141 K). Primary: use the archive's
300 K convention and impose the declared linear profile
`T(z)=T0+Delta*z`, `Delta=2*(TAVG-T0)`. This preserves TAVG exactly, rather
than silently mixing conflicting columns. Retain archived TMAX in the audit.
A fixed 295 K sensitivity uses the same observed arrays unchanged; it is a
baseline sensitivity, **not a recalibration** of fluctuation temperatures.
Their raw normalization is unavailable. Neither convention is selected by fit.

## Split, estimator and physical gates

Order each preparation's common conditions by `AVG_TAVG`, never by a response.
The lowest `ceil(2N/3)` conditions calibrate: C30 rows 1–8; C30C rows 1–5.
Predict C30 rows 9–11 and C30C rows 6–7 for every mode. There are 28 potential
mode-condition targets (6×3 + 5×2). A tie crossing the split or invalid/negative
heating predictors stops execution. Reduced arrays have no heater-group or ramp
identifiers; no independent replicate or prospective intervention claim follows
from row withholding. No target is an equilibrium anchor: all TAVG exceed 300 K.

Normalize the squared strain profile on `z in [0,1]` to rho, with moments
`mu_r=integral z^r rho(z) dz`, r=0..3. Use clamped-free Euler–Bernoulli curvature
for flexure and `rho=2*cos((m-1/2)*pi*z)^2` for torsion. Evaluate by 256-point
Gauss–Legendre quadrature and validate synthetic cases before fitting real data.

Assume local loss `A+B*Delta*z+C*Delta^2*z^2`. Fit global damping only to
`Phi=a+b*Delta+c*Delta^2` using inverse reported variance weights, with a scaled
quadratic design. Recover `A=a`, `B=b/mu1`, `C=c/mu2`. Require at least four
finite calibration observations, positive loss and positive reported error,
three distinct temperatures and full rank. Missing/nonfinite loss or error
entries are recorded and omitted; finite nonpositive values fail the case.
Record missing rows, rank, conditioning and calibration residuals. No uncertainty
floor, degree selection, data-driven trimming or constrained refit is allowed.

Predict using the **fitted**, never the heldout observed, damping denominator:

```
Tpred = T0 + Delta * (a*mu1 + b*Delta*mu2/mu1 + c*Delta^2*mu3/mu2)
                    / (a + b*Delta + c*Delta^2).
```

Require nonnegative local loss over `0 <= t <= max(Delta)` of the entire
calibration-plus-target domain. Check quadratic endpoints and any interior
minimum analytically, with a relative numerical tolerance of 1e-10. Require
positive global predicted damping throughout that domain. The resulting
weighted temperature must lie between T0 and T0+Delta (roundoff tolerance only).
An inadmissible fit remains a failure of this specified model. Preserve its
algebraic output for audit, but do not treat it as a qualified thermal prediction.
Do not clip local loss or reject observed fluctuations outside the envelope.

Primary data are as archived. A prespecified publisher-mask sensitivity removes
C30C flexural-4 calibration row 1, matching `plots.m`; its reason is unspecified.
Target membership does not change. The other publisher mask concerns an excluded
torsional column. A secondary analysis uses all damping rows with T0=300 K,
then scores the same hot targets. This is cross-observable replication, **not**
heldout damping prediction; its damping residuals are in-sample diagnostics.
No full factorial search or post-result selection among these four analyses.

## Scoring and interpretation

At identical target rows compare with three fixed alternatives: spatial mean
TAVG, cold-clamp T0, and uniform local loss `T0+Delta*mu1`. The last isolates the
added value of inferring temperature-dependent loss over mode geometry alone.
The TAVG comparator is a proxy, not an equilibrium theorem under a gradient.

Report physical admissibility /11 modes, scored /28 targets, per-mode damping
absolute relative error and fluctuation MAE in kelvin. Preserve raw observations,
reported errors, predictions and comparator differences. Temperature scores use
finite observations, irrespective of their magnitude. Relative damping errors
require positive observed loss. Average condition errors within mode, modes
within preparation, then the two preparation means with equal weight. Comparator
scores on admissible modes use exactly the same rows; also report comparator
scores across all finite targets. A missing preparation makes any remaining
mean a subset diagnostic, not a two-preparation score.

No binary significance claim or arbitrary accuracy threshold is introduced.
An advantage requires lower error against each comparator **and** coverage
accounting; survivor-only improvement is not overall predictive success.
Good damping with bad thermal prediction challenges the assumed spatial loss
inversion; bad damping or negative local loss defeats this quadratic transfer
before fluctuation outcomes are interpreted. It does not refute general local
thermal physics or establish a different post hoc mechanism.

The archive contains reduced figure data. Damping, frequency thermometry and
fluctuation amplitudes share spectral fits; baseline normalization and drift
can correlate errors across conditions and modes. Condition on measured TAVG;
retain its errors, but claim no full propagated interval or independent-error
p-value without joint covariance. The 295 K sensitivity does not resolve the
underlying normalization discrepancy.

## Reproduction and sequence

1. Verify acquisition; commit this protocol, config, predictor audit, module,
   runner and synthetic tests. Record the full commit in each execution receipt.
2. `PYTHONPATH=src python experiments/run_cantilever.py --stage predict
   --freeze-commit FREEZE --output results/cantilever-forecast-2026-10-13`.
   Commit its two JSON files before fluctuation evaluation.
3. Run `--stage evaluate --freeze-commit FREEZE --prediction-commit FORECAST
   --predictions results/cantilever-forecast-2026-10-13/predictions.json
   --output results/cantilever-transfer-2026-10-13`.
4. Independently verify with adaptive spatial integration and a separate weighted
   solver; write results, limitations and source credit; append the run registry.
   Preserve all earlier records. Update status/article/support and run checks.

Exploratory follow-ups, if warranted by failure, require a new labelled protocol;
no changes to this frozen analysis are justified by inconvenient outcomes.
