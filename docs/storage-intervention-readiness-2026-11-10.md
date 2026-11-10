# Storage intervention: readiness decision and next admissible action

10 November 2026. **The design is ready for dataset qualification; an empirical
run is not yet qualified.** None of the public sources qualified in the
repository supplies the independent storage measurements, closed budget,
capacity intervention and separate coupling control required together. This
review converts the [25 October design](storage-intervention-design-2026-10-25.md)
and [28 October prediction specification](allocation-prediction-specification-2026-10-28.md)
into an acquisition and release decision. It adds no observations, numerical
target access, fitted model, empirical registry entry or evidence of the law.

The assessment uses retained source audits, not a fresh survey of worldwide
data availability. Their bounded searches remain closed. No author contact,
new experiment or acquisition of an already disqualified target is proposed;
the author's existing-public-data-only constraint remains in force.

## What would actually be predicted

The concrete example is a connected set of communicating vessels. Resource is
liquid volume, with identical liquid density and a common height/pressure
reference. The independently measured storage function is
\(R_i=F_i(h_i)\). Connector volumes belong in the complete resource inventory,
or their omission must have an independent bound. Gravitational energy is
dissipated and is not the conserved resource in this test.

Fix the reference weights before target access, for example
\(w_i=F_i(h_{\rm ref})\) at a declared physical reference height, separately
accounting for the documented intervention. This is discrete allocation by
physical storage weights, **neither log-orthopolic nor linear-orthopolic size
allocation**. Changing the weights to match the final stocks would remove the
test.

The existing design has two different unused observables to seek in an archive:

| Intervention | Independently fixed inputs | Prediction to seal before target release |
| --- | --- | --- |
| Change one complete storage curve at fixed total volume | Pre/post geometry or storage assays, full budget, reference datum and connected passive links | Solve \(\sum_i F_i(H)=B\); predict **every absolute stock** \(R_i^*=F_i(H)\), and the common potential \(H\) |
| Change coupling while preserving storage and total volume | Separate matched control, unchanged storage curves and budget, no new hidden store or disconnected component | The complete endpoint vector is unchanged; a uniform conductance multiplier changes only the clock if the kinetic assumptions also qualify |

An endpoint forecast does not require fitting a coupling rate. Any additional
trajectory forecast requires separately measured kinetics and its own frozen
observation times; a successful endpoint cannot retrospectively qualify them.

The storage intervention is the primary allocation comparison. The separate
coupling control checks the claimed distinction between storage and exchange
speed; its endpoint invariance alone does not distinguish the storage models.
Previously exposed wall temperatures, BioMe stock traces and membrane-pair
outcomes cannot serve as new unused targets.

## Competing predictions and the scope of a success

The physically strongest comparator is ordinary hydrostatics/conservative
network theory with the **same independently measured full storage curves**.
It gives the same endpoint equation as the proposed constrained-allocation
account. The two labels therefore cannot be distinguished by this experiment.
A successful prediction would establish a scoped transfer and its constitutive
boundary, not a unique advantage over that established theory.

The useful divergent comparison is with the baseline fixed-weight prediction
\(R_i^*=B w_i/\sum_j w_j\), or a local linear storage approximation fixed
without targets. Include persistence as a simple additional comparator, not as
the strongest physical rival. If the independently assayed curves are
proportional, the full-curve and fixed-weight forecasts agree for every budget;
such a cohort cannot answer the intended discrimination question.

The constructed example already demonstrates the required contrast. After
doubling the first store at budget 3, weights \((2,1,1)\) give the fixed-weight
forecast \((1.5,0.75,0.75)\). The independently stipulated nonlinear third store
instead gives \((1.444240,0.722120,0.833640)\). The maximum stock separation is
0.083640 resource units, or **2.7880% of the independent budget**. Two equal
simultaneous error radii smaller than 1.3940% of that budget would be disjoint
in this maximum-coordinate metric. This is an analytic illustration, not a
measured uncertainty, a power estimate or an empirical acceptance threshold.

## Minimum public-data package

A candidate can be reopened only when a specifically identified public file
or deposition adds independent measurement information relevant to a failed
gate. A new URL for the same outcomes, a fitted simulator or more final curves
does not meet that condition. The first deliverable for an eligible lead is a
file-level manifest with persistent identifiers, versions, hashes, licenses,
experimental-unit keys and the following access partition:

| Partition | Minimum contents | What it identifies |
| --- | --- | --- |
| Source metadata and methods | Full intervention map, instrument channels, units, resource boundary, acquisition order and independent replicate identities | Whether the physical comparison exists and which records belong together |
| Independent storage and observation calibration | Complete pre/post \(F_i\) curves over the target operating interval; common zero datum; sensor calibration, uncertainty and shared-error information | Finite allocation forecasts and a valid mapping from readings to stocks |
| Independent initial inventory and controls | Total stock prepared before release; connector/dead-volume storage; leakage, sampling and evaporation controls | Absolute budget, closure and whether the coupling control changes storage |
| Prediction inputs | Fixed class inclusion, reference weights, intervention identities and allowed operating range; separate kinetics only if used | A forecast that does not depend on target allocations |
| Withheld targets | Complete absolute endpoint stocks and potential readings for both interventions, endpoint timing and all replicates | A separate whole-vector evaluation, without selecting convenient classes or runs |

Input and target files may reside in the same public archive, but numerical
target payloads remain unopened until the protocol, implementation and forecasts
have been frozen. Record any earlier exposure to captions, published summaries
or aggregate results; local withholding is not global blinding.

Prefer endpoint stocks recovered or measured independently of the predictor's
storage assay. If stocks are calculated from the same \(F_i\) curves used in
the prediction, retain the shared calibration covariance and identify which
observable remains independent (for example, final potential). The derived
stock relation itself is not separate corroboration of those curves.

## Release gates and stopping rule

The following are sequential qualification decisions, not permission prompts.
They must be satisfied by source evidence before numerical targets are released.

1. **Physical cohort:** identify a capacity change and a separate coupling-only
   control with matched resource definitions, complete class coverage and known
   intervention order. Reject driven throughflow or active feedback as a
   substitute for the specified closed comparison.
2. **Input identification:** demonstrate independent complete storage curves,
   initial inventory, reference datum and observation calibration, with units
   and uncertainty. A single nominal component value, small-signal slope or
   target-fitted curve is insufficient.
3. **Closure and hidden storage:** bound all omitted stores and losses, and
   establish that the coupling intervention preserves capacity and connectivity.
   Where connector storage is not independently measured, require the separate
   common-mode calibration in the [storage qualification](topology-storage-2026-10-23.md).
   A conserved observed chamber sum or a good pair fit does not clear this gate.
4. **Discrimination:** propagate joint independent-input uncertainty through the
   scalar budget root and observation model. Require useful separation of the
   full-curve and prespecified fixed-weight/local forecasts, including shared
   calibration errors. Specify replication and demonstrate power under an
   error model supported by the source; the illustrative 1.3940% figure above
   cannot be substituted for that exercise.
5. **Frozen evaluation:** fix one whole-vector statistic, a numerical practical
   tolerance and its simultaneous uncertainty calibration, endpoint rule,
   treatment of failures and all comparator predictions before target access.
   A suitable default statistic is
   \(D=\max_i|R_i^{\rm obs}-R_i^{\rm pred}|/B_{\rm ref}\), where
   \(B_{\rm ref}\) is the independently measured preparation budget, not a sum
   reconstructed from the target. This compares absolute stocks on a fixed
   scale; it does not renormalize observed stocks to conceal losses. Select
   actual thresholds from independent calibration and practical requirements,
   then assess power before release.
6. **Forecast release and evaluation:** freeze and push the dataset-specific
   protocol and verified implementation before calibration, then freeze and
   push numerical forecasts before releasing targets, following the existing
   [prediction specification](allocation-prediction-specification-2026-10-28.md).
   Report absolute accuracy separately from improvement over comparators and
   retain every included replicate and failed qualification.

Stop the candidate at the first missing necessary gate. Do not compensate by
fitting the missing input from the outcome, dropping inconvenient classes,
widening an acceptance threshold or replacing the intended intervention with
another available response. A failed measurement gate leaves the empirical
test unqualified; a gate-qualified outcome outside the frozen acceptance
region rejects the scoped forecast. A new post-outcome explanation requires
new independent inputs and a different unused prediction.

## Existing sources: decision and precise reopening condition

| Retained source | Current reason it cannot supply this test | Independent information needed to reopen it |
| --- | --- | --- |
| [BioMe pairs](biome-stock-audit-results-2026-10-23.md) | No-pore controls have 8.22–32.30% apparent stock loss; connector loading/recovery is not independently identified; no matched network intervention | Separate stable stock calibration over the full run, connector loading/recovery and complete matched intervention records. Repairing numerical replay does not repair these physical gaps |
| [Membrane-pair transfer](membrane-exchange-results-2026-10-22.md) | A completed pair-transfer result, not the required capacity/coupling cohort; its targets are exposed | A distinct public intervention cohort with independent storage, full stocks and controls |
| [144-node circuit](storage-source-audit-2026-10-25.md) | Driven impedance data, nominal components and missing original amplitude/phase measurements; no closed endpoint inventory | Independently measured assembled storage/observation inputs and closed redistribution records, not another nominal impedance fit |
| [Wall archive](storage-source-audit-2026-10-25.md) | Open thermal forcing; no fixed-budget storage intervention; the later [steady transfer](hotbox-transfer-results-2026-10-26.md) is already complete | A separate closed storage-change/control cohort and assembled storage assays. The four unopened dynamic files do not acquire those properties merely by remaining unopened |
| [Droplet/network leads](topology-source-audit-2026-10-23.md) | Matched pair/network whole-stock calibration is unidentified, or pumping/osmotic mechanics changes the model | A specific deposited raw-stock/geometry and independent calibration package covering the intended closed interventions |
| [Optical final allocations](physics-allocation-source-audit-2026-10-28.md) | Independent measured initial invariants, active-mode coverage and their covariance were not qualified; this is also a different physical test | A distinct identified deposition of those initial inputs plus unused final allocations under a separately specified optical protocol |

There is currently no identified package in the repository that clears gates
1–3 together, so neither a data-specific tolerance nor a powered empirical
forecast can honestly be frozen. **The next admissible empirical action is a
metadata-first qualification of one specifically identified new input package.**
Until that trigger exists, keep the storage test unrun and advance the
manuscript/reproducibility work. Repeating the completed source searches or
generating another constructed trajectory would not fill this evidence gap.

## Checks for this readiness review

The source decisions above were checked against the linked retained audits and
completed results. The example's nonlinear root and complete stock vector were
recomputed by scalar bisection independently of the production solver; the
budget is 3 to floating-point precision, and the derived normalized separation
is 0.0278800910752. No empirical observations were decoded, no old gate was
relaxed, and no source-availability claim beyond the audited records is made.
