# Fragmentation: three public archives and the stopping decision

Started 28 October; completed 29 October 2026. **None of the three inspected
archives meets the independently qualified complete-budget requirement.**
The agreed search limit is reached. No numerical experimental worksheet outcomes
were decoded, no empirical fragmentation run was added, and no weaker conditional
analysis was substituted for the proposed absolute-allocation test.

The intended distinction is conservation versus allocation. Independently fixed
mass, objects and reference measure must precede outcomes. Equal mass per
logarithmic fragment mass is a **log-orthopolic** hypothesis. Sieve data can
instead test physical mass per logarithmic sieve diameter, also log-orthopolic,
but these are not interchangeable without a justified mass-size relation.
Neither is linear-orthopolic allocation. Whole experimental runs, not sibling
fragments, would be the units for inference about an ensemble mean.

## 1. Fragmenting rockfalls and rockslides: underlying distributions absent

Lin et al.'s [latest archive, Zenodo 3692315](https://zenodo.org/records/3692315),
version 2, supersedes the initially identified 3685912. The 71,452-byte workbook
matches the provider checksum. Its two sheets contain deposit parameters
(A1:P14) and velocity magnitudes (A1:AB302), not per-fragment masses or complete
class-mass distributions.

The [primary methods](https://doi.org/10.1029/2019JB019296) describe manual
fragment measurements and weighing, avoiding sieving-induced breakage. Those
distributions are absent from the inspected workbook. Videos and deposit surface
models cannot establish buried fragments and fines without a new observation
model; they were not downloaded. The methods also acknowledge an arbitrary
comminution cutoff. Nominal parent dimensions/density do not supply a measured
per-run budget ledger here.

**Decision:** fails outcome completeness. No distribution was reconstructed
from the published breakage summaries.

## 2. Dynamic rock fragmentation: useful spectra, unqualified budget

[Rae et al. (2020)](https://doi.org/10.1029/2020JE006561), *Dynamic Compressive
Strength and Fragmentation in Felsic Crystalline Rocks*, supplies two small
workbooks in [Zenodo 3987223](https://zenodo.org/records/3987223). Both provider
checksums match. [Author-hosted methods](https://viveins.github.io/publications/pdf/J7-2020.pdf)
describe the material characterization and loading experiments.

The dynamic table has 60 design rows: 16 granite, 19 parallel gneiss and 25
perpendicular gneiss. These are design counts, not a claim that all experiments
fragmented or have usable outcomes. Eight sieve-percentage fields cover six
bounded intervals with edges 0.2, 0.4, 0.63, 1, 2, 6.3 and 16 mm, plus open
tails. The quasistatic table has 17 mechanical-summary records and no fragment
allocation columns, so it cannot calibrate a quasistatic-to-dynamic spectrum
transfer.

The original specimen mass is explicitly calculated from geometry and separately
characterized density. This can be a legitimate independent measurement route,
but its geometric/density error and the weighing uncertainty are not qualified
here. Recovery is calculated relative to that estimate. The sieve percentages'
initial-versus-recovered-mass denominator remains unresolved from the inspected
headers and methods. No numerical closure calculation was used to choose one.

**Decision:** fails the original complete-budget qualification. A separate
nominal-budget sensitivity study could be designed, with missing mass allocated
adversarially and a fixed denominator rule. That would be a conditional boundary
test, not the independent absolute forecast proposed here. The source-supported
mass-weighted Weibull model is a possible rival, but its transfer rule would
also have to be fixed before calibration.

## 3. Rock chips under pressure: collected mass is not removed mass

The [Scientific Data descriptor](https://doi.org/10.1038/s41597-024-03419-5)
and [Figshare version 2](https://doi.org/10.6084/m9.figshare.25102847.v2)
describe pressure and cutting-depth interventions. A public 1.28 GB ZIP holds
images and workbooks; a separate small README archive documents them.

Selective retrieval obtains the final 65,536 ZIP bytes, including its directory
and the unchanged 11,808-byte `Sieving.xlsx`. This avoids downloading the images.
The sheet has nine mass classes, including open tails below 2.36 and above
53 mm, seven bounded intervals, and a total collected weight. Its schema is
A1:L28. The methods describe careful collection but acknowledge possible fine
powder loss without a quantitative bound. No independently measured mass removed
from the parent was established. The whole block's mass is not the chip budget.

**Decision:** recovered-chip profiles are available; the complete removed-mass
budget and observation-error bounds are not qualified. Repeated caliper
measurements in the source validate chip dimensions, not collection completeness
or the accuracy of sieve masses. No numerical mass cells or images were decoded.

## What is retained, and what the article gains

[Source receipts](../data/fragmentation-candidates/2026-10-28/source-receipt.json)
and [schemas](../data/fragmentation-candidates/2026-10-28/workbook-schemas.json)
retain four workbooks, provider metadata and relevant inspection records.
All three archives declare CC BY 4.0; attribution is in [data/NOTICE.md](../data/NOTICE.md).
For Figshare, the README checksum and extracted member CRC are verified. The
full large ZIP was not downloaded, so its provider MD5 is not independently
verified. The methods PDFs stay in ignored `build/`.

`make fragmentation-sources` checks 13 retained files, provider checksums,
the partial ZIP extraction and all workbook schemas without numeric outcome
decoding. Worksheet names are resolved by relationship IDs, not archive order.
Published methods, model descriptions and aggregate results were exposed,
including Rae's recovery range and strain-rate trends. This was local numerical
withholding, not global blinding or an external preregistration.

Instead of relaxing the gate, the article adds the independently specified
uniform-cut model in **supporting S3.8**. It conserves mass exactly while
predicting a nonuniform expected mass allocation across logarithmic fragment
mass intervals. The standard random-spacing distribution is credited to
[Rao and Sobel (1980)](https://doi.org/10.1016/0047-259X(80)90073-1).
This is an analytic applicability boundary, not a fit to these rocks or new
empirical evidence. It also distinguishes exchangeable fragment labels from
size classes: the former have equal expected mass, the latter do not.

The companion missing-mass formulas quantify how much unseen material could
restore a declared plateau. They cannot supply an unmeasured budget or an
unspecified stochastic error model. `make fragmentation-boundary` verifies the
fixed example by exact arithmetic and quadrature, and the completion bounds
against independent linear programs. The [analytic record](../results/fragmentation-boundary-2026-10-28/analytic.json)
contains no experimental observations. Registry remains **46 / 1,168**.

This round is closed at three archive families. Reopening a candidate requires
new independent budget/observation information, rather than reinterpretation of
its current limitations. The next editorial task is to make the article's
established conditional mechanisms, independent empirical predictions and
applicability boundaries easy to distinguish; another open-ended source search
is not the default next step.
