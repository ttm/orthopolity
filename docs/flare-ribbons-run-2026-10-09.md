# Registered flare-ribbon analysis, 9 October 2026

**The original flare test has now run. Its registered verdict is inconclusive:
the area interval excludes both proposed exponents.** Data access, which blocked
the earlier session, succeeded here.

| Variable | Density exponent α | 95% bootstrap interval | Selected tail / input rows | Script's GOF p |
|---|---:|---:|---:|---:|
| Ribbon area, primary | 3.16265 | [2.96239, 3.45746] | 565 / 3,137 | 0.79242 |
| Reconnection flux, secondary | 3.12002 | [2.56987, 3.38417] | 346 / 3,137 | 0.49102 |

Neither interval contains 2 or 7/3. The rule assigns *inconclusive* whenever
both values are excluded. This is a failure of both candidate predictions
under the implemented analysis, not evidence that either resource reading
has been established. The script's likelihood comparisons do not distinguish
its fitted power law from its fitted lognormal (p = 0.799 and 0.917).

The selected area threshold is 3.87652 × 10^18 cm²; the flux threshold is
3.118 × 10^21 Mx. These are density exponents, not survival exponents.

## What was preserved

The handoff supplied by the user matches Git commit
`f84667064f0477325ab05b3689c36d7a0b7a8c23`, available in the local `origin/main`
reference. The working branch is `py314-and-package-names`, whose research
documents differ. No branch was switched or merged. Exact copies of the original
runner, statistical module, registration and requirements were retained under
[`results/flare-ribbons-2026-10-09/implementation/`](../results/flare-ribbons-2026-10-09/implementation/).

The [RibbonDB v1.0 CSV](https://solarmuri.ssl.berkeley.edu/~kazachenko/RibbonDB/ribbondb_v1.0.csv)
was downloaded as original bytes. See the [source audit](dataset-audit-flare-2026-10-09.md)
for methods, fields and acquisition receipts. All 3,137 rows remain in the
primary analysis, including two exact duplicate event pairs. The literal input
column names retain their leading spaces. No thresholds, hypotheses, estimators,
random seeds or decision rules were changed.

The unchanged script used 2,000 resamples with threshold reselection for each
exponent interval and 500 parametric resamples for each goodness-of-fit diagnostic,
with seed 20261008. Runtime: Python 3.11.6, NumPy 2.3.5, pandas 2.2.3 and
SciPy 1.17.0. The numerical library versions match the recovered pinned versions;
the original session used a different Python version. Execution took 31.7 seconds.

Before execution, the [exposure record](../results/flare-ribbons-2026-10-09/before-run.json)
recorded data inspection, duplicates, source hashes and published information
encountered during the search. The source-audit agent had read a published
reconnection-flux/energy frequency exponent of 1.6, but no published ribbon-area
index was located or read. This is a continuation of a locally registered
analysis, not a claim of external preregistration or complete blinding.

## Interpretation limits

The original implementation uses an unbounded, threshold-selected power law for
α, but computes goodness of fit on a bounded interval ending at the observed
sample maximum, holding the selected threshold fixed. Thus its displayed GOF
p-value is not a calibrated test of the entire primary selection-and-fit
procedure. This discrepancy was recorded before the run and left unchanged.
The result above reports the registered implementation, not an endorsement
of that diagnostic as a definitive distribution test.

The iid bootstrap also omits dependence among repeated flares in the same active
region and retains two duplicate event pairs. The intervals are conditional on
that implementation. GOES-class selection, tail selection and finite active-region
size can affect the observed distribution. These are possible explanations to
test, not explanations established by this result.

Finally, area alone does not measure a fractal dimension. The two predictions
also assume a shared linear-size distribution, and the catalogue lacks independent
linear extent or spatial masks. Neither this failure nor a hypothetical exponent
match would isolate the geometry without a second measurement.

## Artifacts and reproduction

- [Numerical result](../results/flare-ribbons-2026-10-09/result.json).
- [Exact command, runtime and result hash](../results/flare-ribbons-2026-10-09/execution.json).
- [Independent MLE and source-byte checks](../results/flare-ribbons-2026-10-09/verification.json).

From the repository root, using an environment with the numerical versions above:

```sh
mkdir -p build/reproductions/flare-ribbons-2026-10-09
python results/flare-ribbons-2026-10-09/implementation/experiments/run_flare_ribbons.py \
  --input data/dataset-audit/2026-10-09/flare/ribbondb_v1.0.csv \
  --column ' S_RBN [cm^2]' --secondary ' PHI_RBN [Mx]' \
  --output build/reproductions/flare-ribbons-2026-10-09/result.json
```

The independent audit reproduced both point estimates directly from raw values
and verified every retained implementation file against its Git source. The
existing full-project test suite was not rerun: production code was unchanged.
