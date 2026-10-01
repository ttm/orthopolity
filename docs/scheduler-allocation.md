# A gated experiment on CPU allocation

1 October 2026. This protocol moves from assigned feasibility quotas toward
observed allocation by an existing OS scheduler. The controller declares
runnable opportunities and a common observation window; it does not assign
CPU budgets or implement the allocation rule. The experiment remains a test of
one engineered system under a specified policy.

## Why the measurement was not run here

The inspection reports 10 logical CPUs, no inherited affinity restriction, and
no visible CPU quota on this Darwin host. The bounded protocol permits one
controller and at most three workers. It therefore does not establish the CPU
scarcity required for its allocation hypotheses. External load could create
contention, but unknown background load is not a declared capacity restriction.

The [hardware gate](../results/scheduler-allocation/hardware-gate.json) rejected
actual allocation measurement. No calibration or allocation trials were run
for this study. The [conditional simulations](../results/scheduler-allocation/conditional-design.json)
are generated examples of the competing assumptions, with their own retained
configuration, algorithm and seed. They are not scheduler observations.

## Fixed resources and opportunity measure

Each single-thread worker repeatedly performs a deterministic pure-Python dense
matrix product at side length 16, 32 or 64, with an independent matrix-vector
consistency check. The workload makes no BLAS calls. Fixed logarithmic bin edges
give all three classes width $\log 2$.

The primary resource is directly measured worker user plus system CPU seconds
in the common observation window, classified by size. It includes completed
work, CPU used by a censored partial job, and loop overhead. CPU used by the
controller and unrelated processes lies outside this worker-resource total.
Separately measured mean CPU per completed job supplies a secondary
reconstruction from job counts; that reconstruction does not replace measured
allocation or invent a completed job for censored work.

The opportunity measure is the number of continuously runnable, equal-priority
workers in each class. Baseline counts are $(1,1,1)$; the restriction intervention
changes them to $(2,1,0)$ while retaining total worker count three. It is an
intervention on available classes/opportunities, not a reduction of total CPU
capacity. Removing the largest class tests the complete predicted response of
the two remaining classes.

## Competing prospective predictions

Let $w_i$ be declared worker counts and $q_i$ independently calibrated CPU
seconds per completed job. The class CPU-share predictions are:

| Hypothesis | Class CPU share | Baseline with illustrative $q\propto(1,8,64)$ | Restricted classes |
|---|---|---|---|
| Equal CPU per runnable process | $w_i/\sum_jw_j$ | $(1/3,1/3,1/3)$ | $(2/3,1/3,0)$ |
| Equal completed-job service per worker | $w_iq_i/\sum_jw_jq_j$ | $(1,8,64)/73$ | $(1/5,4/5,0)$ |
| Equal CPU per active class | $1/\#\{j:w_j>0\}$ for active classes | $(1/3,1/3,1/3)$ | $(1/2,1/2,0)$ |

Baseline cannot distinguish equal process shares from equal active-class
shares. The intervention can. Equal process shares and equal thread shares
remain indistinguishable because every worker has one workload thread.

The simulated costs $(0.00025,0.002,0.016)$ CPU seconds are declared examples,
not measured calibration. Five hundred multinomial replicates of 3,000 resource
quanta per condition and hypothesis illustrate generated variability. Their
95th-percentile error is not an empirical confidence interval or an acceptance
tolerance. A separate deterministic demand-limited comparator uses duty caps
and equal-weight water filling; continuously runnable trials do not test that
sleeping-worker extension.

## Eligibility and collection on another host

Every condition must have more continuously runnable workers than an
independently visible CPU bound no greater than two. The gate inspects logical
CPU count, inherited affinity where available, and Linux cgroup v1/v2 limits,
including visible ancestors. Unreadable limits are disclosed. A quota-only
qualification also requires zero positive burst allowance and a quota period
at most one tenth of the trial length. Ordinary inherited scheduler policy is
required; children must share the same inherited priority and policy. The
program changes no priority, affinity or cgroup configuration.

On an eligible host, the driver collects 12 fresh-child calibration blocks,
three jobs per size in each block. It freezes all share predictions from these
costs before measuring allocation. Three randomized three-second trials per
condition then start workers against common monotonic-clock deadlines. Raw CPU
accounting, job counts, child constraints, timing lags and the frozen-plan hash
are retained. Starts/stops more than 0.05 seconds late are flagged; all trials
are reported rather than selectively retained. There is no guaranteed interval
coverage or significance threshold attached to these short trials.

Reproduce the retained gate/design without overwriting its bytes:

~~~bash
make scheduler-allocation PY=python3.11
~~~

Collect a new run on independently eligible hardware using new directories:

~~~bash
PYTHONPATH=src python3.11 experiments/run_scheduler_allocation.py \
  --stage all --directory data/scheduler-allocation/NEW-ID \
  --output results/scheduler-allocation-NEW-ID
~~~

The gate is checked again before actual collection and in each child. A retained
inspection is not used to authorize measurements on a changed host. Existing
actual records cannot be overwritten; an interrupted actual study requires a
separate run and retention of its incomplete records. Completed actual runs
must be registered explicitly using the [run-registry schema](run-registry.md).

## Relation to dimensionality and the article

In the baseline, equal CPU per worker would yield equal CPU per fixed logarithmic
size class. If independently measured cost scaled as $q(k)\propto k^d$, completed
job abundance per logarithmic class would approximately scale as $k^{-d}$ under
negligible overhead and censoring. This is a conditional consequence to check,
not a power-law fit to three classes or a geometric-dimension estimate.

The intervention supplies a stronger distinction than a compatible baseline
slope: it predicts a particular unequal resource profile from known opportunity
counts. Agreement would support that policy-specific allocation model. It
would not establish a universal selection of neutral resource allocation by
Nature. Independently defined natural systems and restriction interventions
remain necessary for that broader scientific claim.
