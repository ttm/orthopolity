# Chemostat failure diagnosis: unrestricted resource prices remain insufficient

11 October 2026. Retrospective analysis of previously inspected published
observations; no new measurements or independent confirmatory outcome.
The [design and algorithms](chemostat-capacity-followup-protocol-2026-10-10.md)
were frozen at `13374c5` before this calculation. The filename of the run
retains its 10 October initiation date. The actual execution receipt records
11 October. All earlier forecasts and results remain unchanged.

**Result:** with measured preliminary quota changes, **8 of 12 polyculture
vessels** exceed the maximum redistribution allowed by the tested model family
at least once during days 1–3. There are **17 exceedances among 36 vessel/day
comparisons**. Allowing every mixture of the pooled algal species and arbitrary
nonnegative carbon and nitrogen prices does not accommodate those points.
This excludes a conjunction of assumptions: fixed aggregate opportunities,
two-resource proportional allocation and transfer of the preliminary quotas.
It does not determine which assumption fails.

## What this adds to the earlier failure

The [original study](chemostat-response.md) found that a particular frozen
cost-ratio forecast failed to predict the twelve-day response of held-out
polycultures. Its maximum attainable redistribution was 0.05–0.12 total
variation (TV), below observed per-vessel maxima of 0.29–0.49. Those maxima
were not matched-time predictions. The present follow-up broadens the allowed
family and addresses a possible explanation: perhaps a different path of
resource prices or a changing C:N ratio would suffice.

Let group biovolume obey

$$V_j(t)=c_t\frac{w_j}{a_t\rho_{Nj}(t)+b_t\rho_{Cj}(t)},$$

where the nonnegative group opportunities $w_j$ stay fixed, positive elemental
densities may change, and prices $a_t,b_t\ge0$ are otherwise unrestricted
(not both zero). For normalized nitrogen stocks, writing
$r_j(t)=\rho_{Cj}(t)/\rho_{Nj}(t)$ eliminates both opportunities and the
common normalization:

$$p_j(t)\propto p_j(0)\frac{a_0+b_0r_j(0)}{a_t+b_tr_j(t)}.$$

Every pairwise ratio of these multipliers is bounded by the observed C:N
ratio ranges. If their span is at most $K$, positive reweighting implies

$$\operatorname{TV}(p(t),p(0))\le\frac{\sqrt K-1}{\sqrt K+1}.$$

This is a bound over all baseline shares and prices, not a newly fitted
forecast. Its derivation and assumptions are in the protocol. The finite-group
comparison uses nitrogen shares across three algal groups; it is not a test
of a logarithmic or linear size spectrum.

## Measurements, mixture uncertainty and complete outcomes

The source is Wojcik et al. (2025),
[published study](https://doi.org/10.1098/rspb.2025.1969), with its
[author data deposit](https://doi.org/10.5281/zenodo.14773023).
Twenty preliminary records provide chemically measured nitrogen and carbon
per cell and cell volumes for four species at days −4, 0, 1, 2 and 3.
The main experiment provides 456 retained observations in 24 vessels.
The primary twelve vessels have multiple rotifer species; the secondary twelve
have a single rotifer species. Both contain the algal food community.

Cryptomonas and Chlamydomonas are observed separately, while Monoraphidium and
Chlorella are pooled. All possible mixtures of the latter two are allowed,
independently at baseline and target. Their resource shares trace line segments
in the three-group probability simplex. The observed lower envelope is the
minimum TV between the two segments. An explicit feasible dual certificate
bounds that minimum from below; exceedance requires this lower bound to be
above the theoretical upper bound by more than $10^{-8}$.

The primary mode uses exact measured quota changes at days 1–3; the reference
mode keeps pre-pulse densities fixed. No extrapolation or interpolation was
used. All 144 planned vessel/day/mode entries were usable and retained.

| Quota scenario | Vessels | Day 1 exceedances | Day 2 | Day 3 | All comparisons | Vessels exceeding at least once |
|---|---|---:|---:|---:|---:|---:|
| Measured changes (primary) | Polycultures | 5/12 | 5/12 | 7/12 | 17/36 | 8/12 |
| Fixed pre-pulse | Polycultures | 3/12 | 5/12 | 7/12 | 15/36 | 8/12 |
| Measured changes | Monocultures | 7/12 | 1/12 | 1/12 | 9/36 | 8/12 |
| Fixed pre-pulse | Monocultures | 6/12 | 0/12 | 0/12 | 6/36 | 6/12 |

With changing quotas the TV upper bounds are 0.190065, 0.174899 and 0.154853
on days 1, 2 and 3. Fixed quotas give 0.154853 on each day. Primary vessels
1, 2, 5, 7, 8, 9, 11 and 12 exceed a bound at least once. Non-exceedance
does not establish that the model can reproduce a vessel's trajectory:
the bound is a conservative necessary condition, not a sufficiency test.

![Complete primary cohort, both quota scenarios](../results/chemostat-capacity-followup-2026-10-10/capacity.png)

*Each vertical range covers the minimum and maximum observed TV over all pooled
mixtures for one vessel. The lower dot is the minimum. Dashed lines give the
model family's upper bound. Ranges are not confidence intervals. Within each
day, vessels are ordered 1–12 from left to right. Red means every admitted
mixture exceeds the bound.*

## Scientific interpretation and next discriminating observation

The larger family still fails for recorded points. Price adjustment alone is
therefore insufficient **under the transferred quota values and fixed
opportunities**. This is useful information beyond the failure of one selected
price path. Similar resource ratios limit how much any such reweighting can
move composition.

The quota transfer is a substantive limitation. Preliminary semi-continuous
monocultures do not directly measure physiology in the grazing chemostats.
Their changes define a measured sensitivity scenario, not a demonstrated
envelope of main-vessel values. Assay-error distributions and replicate-level
quota uncertainties are unavailable. Repeated vessel/day comparisons are
dependent. Consequently no population-level p-value, confidence claim or
statistical rejection is made; counting 17 comparisons does not create
17 independent experiments.

The conditional result directs the next study. Measure elemental quotas in
the same mixed vessels and quantify grazing or other processes that change
group opportunities. A revised allocation or dynamical model should then
predict an independent intervention or trajectory before observing it. The
present data do not identify an omitted resource or prove that changing
opportunities explains the failure. They identify what must be measured to
distinguish that explanation from failure of the proposed relation in this
setting. The original forecast remains unsuccessful.

## Verification and reproduction

Ten synthetic tests preceded execution. The separate verifier imports neither
the analysis module nor an LP solver: it enumerates vertices of the piecewise
linear distance geometry, enumerates extreme prices, and rebuilds quota
conversions and shares from the retained input rows. Across all 144 entries,
the largest difference from the LP minimum is $5.6\times10^{-17}$.
It also checks feasible dual bounds, row identities, source hashes, frozen
code and every summary count. Three additional analytic cases exercise the
independent verifier.

The [retained run](../results/chemostat-capacity-followup-2026-10-10/summary.json)
contains the full ledger, bounds, quota conversion, execution receipt and
verification. To reproduce to an unused directory:

```sh
PYTHONPATH=src python experiments/run_chemostat_capacity.py \
  --freeze-commit 13374c5 --output build/reproductions/chemostat-capacity
PYTHONPATH=src python experiments/verify_chemostat_capacity.py \
  --directory build/reproductions/chemostat-capacity
MPLCONFIGDIR=build/matplotlib python experiments/plot_chemostat_capacity.py \
  --directory build/reproductions/chemostat-capacity
```

The runner refuses an existing output directory or any changed frozen source
or input. Analysis values are deterministic; execution receipts record the
actual run time. No network access is required.
