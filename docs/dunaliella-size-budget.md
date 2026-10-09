# Size-selected lineages under one budget

Status on 2 October 2026: complete and registered as
`dunaliella-size-budget-2026-10-02`. The study reanalyses the published
measurements of Malerba, Palacios and Marshall
([doi:10.1098/rspb.2018.1347](https://doi.org/10.1098/rspb.2018.1347); data
[doi:10.5061/dryad.4mh47r7](https://doi.org/10.5061/dryad.4mh47r7)). No new
observations were collected.

**Result in brief.** The lineages share one medium, so each well holds the same
budget. Across a 10.4-fold range of mean cell volume, carrying capacity in
total biovolume is the same to within 3%. Cell number at capacity therefore
falls as about $V^{-1.02}$. A frozen *equal-biovolume* forecast, cost dimension
$d=1$, predicted each held-out selection treatment with a typical error of
13–20%. It outperformed both a fitted size law and an equal-cell-number law.
Regrowth after deprivation restored capacity only approximately. Phosphorus
deprivation left a size-dependent overshoot that no frozen model predicted in
both folds.

## Question

Suppose one budget $R$ supports $N$ cells, each costing $q(V)=cV^d$. Then
$N=R/q(V)$, and the total biovolume reached is $NV\propto V^{1-d}$. The study asks:

1. **Size law.** In one shared medium, does carrying capacity follow a single
   law $\log K=a+(1-d)\log V$, so that a law fitted on two selection treatments
   predicts the third?
2. **Restoration.** After a week of N or P deprivation, does regrowth in the
   same medium restore each lineage's replete capacity?

The lineages grew separately, so this is not a coexisting size spectrum and
cannot test logarithmic neutrality. The archive has no nutrient quotas, so $d$
is fitted on development lineages or assigned across taxa, never measured. The
resource binding at capacity was not measured.

## Data and measurement chain

- **Lineages:** 30 *Dunaliella tertiolecta* lineages after about 280
  generations of artificial selection: 10 small-selected, 10 control and 10
  large-selected.
- **Growth assay:** each lineage was regrown for 12 days in standard F/2 (the
  authors' Fig. 3) after one of three pre-trial histories: replete, N-deplete
  or P-deplete. Each lineage-history has three replicate wells on separate
  plates. Optical density at 750 nm was read daily.
- **Outcome:** `BiovolUL` is the authors' calibrated total biovolume. For
  control rows, $\sqrt{\text{biovolume}}$ is exactly linear in manually
  blank-corrected OD. The calibration used nine separate cultures counted by
  haemocytometer. Raw OD is a pre-declared sensitivity analysis. `CellsUL` is an
  exact function of biovolume, so it is excluded.
- **Size coordinate:** mean microscopy cell volume, $(\pi/6)LW^2$ from at least
  200 cells per lineage and history.
- **Excluded assay:** the 72-hour media assay. In its P-free and full media,
  controls were still growing at 72 hours.

Dryad refused unauthenticated downloads, with HTTP 401 and 403 responses that
are logged. The 4.8 MB code-and-data bundle came from Dryad's Zenodo copy
(record 4990483). Its MD5 equals the digest Dryad publishes, so the bytes are
Dryad's. The 806 MB photo archive was not retrieved. The R workspaces are read
by a dependency-free reader, `src/orthopolity/rdata_reader.py`, which decodes
numeric vectors only on request, row by row.

**Source erratum.** The archive's two cell-size summaries share every shape
column, but their volumes differ by exactly 8 on all 89 rows. The per-cell
table computes $(4\pi/3)LW^2$, treating full axes as semi-axes. The study uses
the correct $(\pi/6)LW^2$ copy, which the authors' demographic analysis also
uses ([amendment 1](../configs/dunaliella_size_budget_2026-10-02_amendment-1.json)).
A uniform factor shifts every log volume equally, so no forecast or score can
change.

## Protocol and chronology

| Step | Commit | UTC, 2 October 2026 |
|---|---|---|
| Sources retained; partition declared | `78a14cc` | 16:06:23 |
| [Protocol](../configs/dunaliella_size_budget_2026-10-02.json) frozen | `1eaa72d` | 16:10:56 |
| Runner and leakage tests | `e6216f7` | 20:53:08 |
| Volume-factor amendment | `f3fd250` | 20:55:04 |
| Forecasts retained | `74c229f` | 20:55:22 |
| Evaluation started | — | 20:55:46 |

The [partition](../configs/dunaliella_size_budget_2026-10-02_partition.json)
allowed only control lineages to be inspected before the protocol was frozen.
Control lineages are development data in both folds. Small- and large-selected
outcomes were not decoded until after commit `1eaa72d`.

The folds are cross-fitted:

- **Fold A** develops on small and control lineages and predicts large ones.
- **Fold B** develops on control and large lineages and predicts small ones.

So one fold's held-out values are the other fold's development data. Each
retained forecast depends on held-out lineages only through their cell
volumes. A test confirms this: scrambling every held-out outcome leaves that
fold's forecasts unchanged. Anchored restoration forecasts apply frozen
development offsets to each lineage's observed replete capacity at evaluation.

Model A "outperforms" model B only if it meets both conditions:

- its mean absolute log error is at least 0.05 lower in both folds;
- it has the lower error for a strict majority of held-out lineages in each
  fold.

Control inspection set that scale: plate-to-plate SD of 0.093 log units, and
replete between-lineage SD of 0.20.

## Results

### Size law across selection treatments (replete history)

Held-out mean absolute log error of carrying capacity:

| Model | Large held out, biovolume | Small held out, biovolume | Large held out, OD | Small held out, OD |
|---|---:|---:|---:|---:|
| Equal biovolume ($d=1$) | **0.124** | 0.179 | **0.065** | **0.094** |
| Assigned carbon exponent ($d=0.91$) | 0.281 | **0.175** | 0.229 | 0.121 |
| Fitted size law | 0.626 | 0.259 | 0.329 | 0.136 |
| Assigned nitrogen exponent ($d=0.80$) | 0.509 | 0.274 | 0.457 | 0.278 |
| Equal cell number ($d=0$) | 2.078 | 1.480 | 2.026 | 1.513 |

The assigned exponents are the pooled carbon and nitrogen cost degrees of the
[archived *Synechococcus* study](archived-cost-transfer.md), converted to
volume ($D/3$). They are labelled cross-taxon hypotheses.

Frozen verdicts, calibrated biovolume:

- equal biovolume outperforms the fitted size law: 0.50 and 0.08 lower; the fitted law is lower in 0 and 3 of 10 lineages;
- equal biovolume outperforms the assigned nitrogen exponent;
- the assigned carbon exponent outperforms the fitted size law;
- the fitted size law outperforms equal cell number;
- the assigned carbon exponent and equal biovolume are not distinguished.

On raw OD, every difference keeps its direction. Two verdicts narrow to "not
distinguished": equal biovolume and the assigned carbon exponent, each against
the fitted law. Their fold B gaps (0.042 and 0.015) fall under the 0.05 margin.

The fitted law extrapolated badly because the folds disagree.

- Small and control lineages give a slope of +0.26 ($d=0.74$).
- Control and large lineages give −0.12 ($d=1.12$).

Controls sit slightly above both extremes: mean log capacity 11.89, against
11.72 for small and 11.70 for large. Fitting a line within either half of the
range then mispredicts the other extreme.

Across all 30 lineages (a post-hoc description), the slope is −0.023 and the
implied cost dimension is $d=1.02$; the OD gives $d=1.01$. Large lineages have
10.4 times the cell volume of small ones, reach 0.975 times their biovolume and
hold 0.093 times as many cells.

![Carrying capacity, cell number, frozen errors and restoration](../results/dunaliella-size-budget/size-budget.png)

### Restoration after deprivation

Mean change in log capacity relative to the replete history (biovolume; OD in
parentheses):

| Treatment | After N deprivation | After P deprivation |
|---|---:|---:|
| Small-selected | −0.12 (−0.06) | +0.01 (+0.01) |
| Control | −0.04 (−0.02) | +0.31 (+0.16) |
| Large-selected | −0.07 (−0.04) | +0.25 (+0.13) |

After N deprivation, capacity returned to within about 0.1 log units of
replete. After P deprivation, control and large lineages overshot by 25–31%,
while small lineages did not.

Errors of the restoration models in each fold:

| Model | Fold A (large held out) | Fold B (small held out) |
|---|---:|---:|
| Full restoration | 0.178 | **0.126** |
| History offset | **0.090** | 0.181 |
| Within-history mean | **0.090** | 0.262 |
| Within-history size law | 0.530 | 0.624 |

Full restoration and the history offset are not distinguished, because the
folds favour opposite models. The development offset, learned partly from
lineages that overshoot, transfers to large lineages but not to small ones.
The within-history mean outperforms the within-history size law.

## What this establishes

- **Equal resource, unequal abundance.** In one shared medium, cell number at
  capacity is inversely proportional to cell volume across a 10-fold range.
  This is the simplest budget-closure form, with the budget denominated in
  biovolume. Abundance here tracks one geometric cost, $d\approx1$.
- **A pre-frozen equal-biovolume forecast transfers to unseen selection
  treatments.** Fitting $d$ within part of the size range does worse, because
  a modest hump at intermediate size dominates short extrapolations.
- **Cost exponents can transfer across taxa only partly.** The *Synechococcus*
  carbon exponent ($d=0.91$) is as good as $d=1$ here. Its nitrogen exponent
  ($d=0.80$) is not.
- **Restoration depends on the restriction.** Regrowth after N deprivation
  nearly restores capacity. After P deprivation, a size-dependent overshoot
  persists for at least 12 days. Restoration toward the replete profile is
  therefore not guaranteed by restoring the medium.

This is not a neutrality test across coexisting size classes. It identifies no
binding resource and measures no quota. The results are point errors over 10
held-out lineages per fold, from one published experiment, with no intervals.
Published summaries, including the abstract's description of storage and
recovery, had been read before the analysis.

## Replay and files

```bash
make dunaliella-sources PY=python3.11           # verify retained bytes; header-only schema
make dunaliella-size-budget PY=python3.11       # offline audit: replays forecasts and evaluation
make dunaliella-size-budget-report PY=python3.11
```

- Sources: `experiments/fetch_dunaliella_sources.py` and
  `data/dunaliella-sources/2026-10-02/`.
- Configuration: `configs/dunaliella_size_budget_2026-10-02*.json` (protocol,
  partition, amendment).
- Frozen analysis: `experiments/run_dunaliella_size_budget.py`,
  `src/orthopolity/size_budget.py` and `src/orthopolity/rdata_reader.py`.
- Forecasts and capacities: `data/dunaliella-size-budget/2026-10-02/`.
- Report, post-hoc diagnostics and figure: `results/dunaliella-size-budget/`.
- Registry lineage links this study to `archived-cost-transfer-2026-10-02`,
  for the assigned exponents, and to `restrictions-2026-10-01`.
