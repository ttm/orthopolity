# Chemostat capacity follow-up: frozen diagnostic design

Design initiated 10 October 2026; completed 11 October 2026, before executing
this follow-up on the retained real observations. The UTC clock read
`2026-10-11 14:17:56 UTC` during completion. The actual freeze is the Git commit
containing this protocol, configuration, module, runner and synthetic tests;
the execution receipt must identify that commit. The filename retains the
start date. No claim of an earlier execution freeze is made.

This is a **retrospective conditional diagnostic** of the failed
[chemostat response model](chemostat-response.md), not a new blinded
confirmation. All source outcomes, the published article and the earlier
analysis have already been inspected. The original forecasts, scoring rules
and results remain unchanged.

## Question and bounded scope

Can the two-resource allocation family accommodate the recorded early change
in nitrogen composition if resource prices may change freely at both times
and the separately assayed preliminary cultures supply time-varying quotas?
The purpose is to distinguish a failure caused merely by the earlier chosen
price path from a capacity limitation of the whole conditional model family.

Only exact observations at days 1, 2 and 3 after the pulse are evaluated,
against exact day 0. These are the only post-pulse days with contemporaneous
preliminary quota observations. There is no interpolation, quota extrapolation,
new response fit, inferred mixture or search over evaluation windows.

The primary comparison uses the twelve previously held-out polyculture
vessels and changing preliminary densities. The twelve monoculture vessels
are a separately reported secondary comparison. Repeating the same days with
fixed pre-pulse densities provides a diagnostic reference. All comparisons are
descriptive; day-vessel observations are not independent experiments.

## Sources, measurements and exposure

The source is Wojcik et al.,
[doi:10.1098/rspb.2025.1969](https://doi.org/10.1098/rspb.2025.1969), with the
author-owned [Zenodo data deposit](https://doi.org/10.5281/zenodo.14773023).
The [source audit](chemostat-source-audit.md) records acquisition, source
checksums, assay methods and known limitations. This follow-up uses three
already retained JSON inputs whose exact hashes and sizes are fixed in
[the configuration](../configs/chemostat_capacity_followup_2026-10-10.json):

- Preliminary stoichiometry: four species at days −4, 0, 1, 2 and 3, twenty
  records, with chemically assayed C and N per cell and measured cell volume.
- Earlier development records: 336 decoded main-experiment records, including
  the polyculture baselines; no-herbivore rows in this file are not used.
- Earlier evaluation records: 120 additional main-experiment records.

Combining the latter two must yield 456 distinct source rows and twelve
vessels in each category. Duplicate source rows, duplicate vessel times or
conflicting metadata abort execution. Missing or invalid baseline/target
volumes, negative volumes and zero total volume produce an unscored ledger
entry; no substitute baseline or pseudocount is allowed. All 144 planned
vessel/day/mode entries are retained.

The species order is Cryptomonas (`Cr`), Chlamydomonas (`Ca`), Monoraphidium
(`Mo`) and Chlorella (`Co`). Main observations distinguish Cr and Ca but pool
Mo and Co. The primary measured quantity is group biovolume. Nitrogen stocks
are reconstructed using the preliminary densities, and remain proxies for
main-vessel stocks. Density units are pmol per cubic micrometre; multiplying
by biovolume in cubic micrometres per mL yields pmol/mL, equivalently nmol/L.
Only normalized shares enter the capacity comparison.

Baseline N and C densities are separate species medians of quota divided by
cell volume at days −4 and 0, matching the earlier calibration convention.
The changing-density analysis uses the exact corresponding species quota
divided by volume at each target day. The fixed-density reference retains the
baseline values throughout. All twenty preliminary rows must be positive,
finite and unique for their specified species/day; otherwise execution stops.

The preliminary cultures are separate semi-continuous monocultures, not
chemical assays of the evaluated mixed vessels. They share light and
temperature conditions but differ in renewal and grazing. Their quota changes
therefore define a measured, externally specified sensitivity scenario. They
are not an envelope proven to contain mixed-vessel physiology. The archive
does not identify replicate-level assay errors; no uncertainty interval is
invented. Rounded quota resolution is likewise not represented as a calibrated
measurement-error distribution.

## Model family and analytic bound

Let V_j(t) denote group biovolume, and let rho_Nj(t), rho_Cj(t) denote positive
N and C densities. The family under examination is

$$V_j(t)=c_t\frac{w_j}{a_t\rho_{Nj}(t)+b_t\rho_{Cj}(t)},$$

with time-invariant nonnegative opportunity weights w_j, an arbitrary common
normalization c_t, and nonnegative prices a_t,b_t that are not both zero.
The units of the prices absorb the distinction between the two elemental
amounts. No actual environmental prices or budgets are estimated here.
Both baseline prices and post-pulse prices are unrestricted. A zero baseline
weight stays zero under this model.

Write r_j(t)=rho_Cj(t)/rho_Nj(t), and let p_j(t) be normalized nitrogen stock.
Eliminating w_j gives

$$p_j(t)=\frac{p_j(0)f_j}{\sum_l p_l(0)f_l},\qquad
f_j=\frac{a_0+b_0r_j(0)}{a_t+b_tr_j(t)}.$$

For each distinct pair i,j and any prices,

$$\frac{f_i}{f_j}\le
\max\left(1,\frac{r_i(0)}{r_j(0)}\right)
\max\left(1,\frac{r_j(t)}{r_i(t)}\right).$$

For ratio intervals, replace numerator ratios by their upper endpoints and
denominators by their lower endpoints. Let K be the maximum of these
pairwise bounds and 1. The total-variation distance then obeys

$$\operatorname{TV}(p(t),p(0))\le
U=\frac{\sqrt K-1}{\sqrt K+1}.$$

Proof: an event of baseline probability x can have its odds multiplied by
at most K under positive reweighting. Its probability gain is at most
Kx/(1+(K−1)x)−x. Maximizing over x gives U, attained at
x=1/(1+sqrt(K)). TV is the maximum probability difference over events.
The bound is sharp over unrestricted starting distributions, but can be
conservative for the observed starting profile and linked mixture choices.
It is an upper bound on possible movement, not a fitted closest model.

## Unknown pooled composition and numerical certification

For any Mo/Co biovolume fraction, pooled elemental density is the
biovolume-weighted average of the constituent densities. Its C:N ratio is
total C divided by total N, lying between the constituent ratios; it is not
the arithmetic average of those ratios. The theoretical bound maximizes over
that full ratio interval independently at baseline and target.

At each observation, the two pure-species conversions delimit a line segment
of possible normalized three-group nitrogen shares. All intermediate volume
mixtures occur somewhere on that share segment. Its position parameter is
not the original biovolume fraction. Baseline and target mixtures are allowed
to differ arbitrarily.

The minimum observed departure is the minimum TV between the two segments.
A linear program supplies a minimizing pair and a dual vector z with
absolute components at most 1/2. If their difference is d+uA+vB for
u,v in [0,1], then

$$L=z\cdot d+\min(0,z\cdot A)+\min(0,z\cdot B)$$

is a valid lower bound on the minimum TV. The stored dual vector is clipped
to its feasible box, L is recomputed directly, and a 1e−12 floating-point
guard is subtracted before truncating at zero. The code checks agreement of
the feasible primal witness and dual lower bound within 1e−8. Solver failure
or a larger gap aborts execution. The maximum observed TV occurs at one of
the four endpoint pairs and is recorded separately.

The decision is **conditional bound exceeded** only when L−U is greater than
1e−8. Otherwise the bound is **not exceeded**. A non-exceedance does not
establish that any common prices or fixed weights actually reproduce the
observations. Independently maximizing the theoretical bound and minimizing
the observed distance relaxes their shared mixture constraints, which makes
exceedance conservative within the stated point-measurement assumptions.

Pooling preserves the family when the aggregate opportunity weight is fixed:
a_t N_pool+b_t C_pool=c_t sum(w_species). Changing the allocation of weights
inside the pool need not violate this relation if their sum remains fixed.
Changing aggregate opportunities, for example through differential grazing or
population dynamics, is outside the tested fixed-weight family.

## Interpretation, verification and execution

An exceedance rules out the conjunction of the specified two-resource family,
fixed aggregate opportunities and transferred quota values for the recorded
points. It does not separately identify which assumption failed, establish
main-vessel physiology, reject orthopolity generally, or constitute a
population-level statistical rejection. Lack of exceedance supplies no
positive model-validation verdict. This finite-group diagnostic states no
log-orthopolic or linear-orthopolic size-spectrum claim.

Synthetic checks precede the real-data run: zero movement with identical
class ratios, sharp two-point bounds, randomized price/interval cases,
correct pooled ratios and share segments, interior and disjoint minima,
explicit dual feasibility, source-calibration mapping, invalid inputs and
missingness retention. No real chemostat response is a test fixture.

After the root agent commits all five design/source files, run:

```sh
PYTHONPATH=src build/main-venv-2026-10-09/bin/python experiments/run_chemostat_capacity.py \
  --freeze-commit FROZEN_COMMIT \
  --output results/chemostat-capacity-followup-2026-10-10
```

The runner compares every executed source byte with the declared Git commit,
checks input hashes and refuses an existing output directory. Retain the
complete ledger, bounds, quota calibration, summary and execution receipt.
The latter records the actual UTC execution time, environment, source hashes
and freeze commit. A separate verification should recompute the segment
minimum without relying on the same optimization algorithm. Preserve both
conditional exceedances and non-exceedances, and retain the earlier twelve-day
forecast failure without changing its interpretation or score.
