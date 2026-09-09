# Evidence ledger

This is the current interpretation of the frozen data and regenerated analyses, superseding
earlier “ensemble confirmed” language. The [manuscript](paper.md) is the narrative account;
the [audit](source-audit.md) records why conclusions changed.

## Reproduction and scope

Run make install and make all from the repository root, as described in the
[README](../README.md). Inputs are checked against
[data/snapshot_checksums.json](../data/snapshot_checksums.json). No empirical analysis
downloads data. Successful execution is a computational check, not a validation of the
data's units, labels, sampling model, or scientific interpretation.

The pilot is exploratory. The historical aquatic/ocean plan in
[configs/prereg_2026-09-09.json](../configs/prereg_2026-09-09.json) appears in local commit
6df364f before the implementation/results commit a0c9973. Raw slopes were already in the
plan commit. Blinding and registration timing are not independently verified by this history.
The file is preserved as a historical record, including statements the present audit cannot
verify. The revised analyses disclose retrospective corrections and sensitivities.

## 1. Earthquake energy proxy

Source: USGS ComCat, 2010–2024, minimum queried magnitude 5.5.
The 7,174 retrieved events yield 6,639 retained moment-magnitude-family records. Magnitudes
are rounded to a 0.1 grid for the Gutenberg–Richter fit.

| Threshold | Retained events | Estimated $b$ |
|---|---:|---:|
| 5.5 | 6,639 | 0.998 |
| 6.0 | 2,076 | 0.984 |
| 6.5 | 679 | 0.977 |

With proxy $E\propto10^{\gamma M}$ and $N(\ge M)\propto10^{-bM}$, resource per log
energy scales as $E^{1-b/\gamma}$. Equipartition requires $b=\gamma$.
At the primary threshold, the year-block 95% interval is [0.973, 1.024], far from the
chosen $\gamma=1.5$. Conversion exponent 1.44 leaves the discrepancy.

The discrete geometric test gives KS ≈ 0.0077 and a refitted bootstrap probability
≈ 0.26. It does not reject the fitted model under its independent-event working assumptions.
It does not prove a perfect power law. The former continuous-reference test and continuous
lognormal comparison are excluded because their calibration ignored ties.

This is evidence against the *specified energy-proxy allocation*. It is not a direct test of
measured radiated energy. Event-specific efficiency, magnitude-method variation, catalogue
completeness, and dependence are not resolved. No discrete lognormal comparison was run.

Provenance: [results.json](../results/results.json), usgs.cases;
[gof.json](../results/gof.json), usgs.discrete.

## 2. Solar flares

Source: NOAA GOES XRS science-quality reports, 2022–2024; 10,501 retained catalogue events.
Resource: end fluence as supplied in J/m², without background subtraction. Coordinate:
peak irradiance in W/m². The primary domain is $[10^{-5},10^{-3}]$.

| Quantity | Estimate | Pilot 95% interval |
|---|---:|---|
| Arithmetic mean resource exponent, trained on 2022 | 0.858 | [0.697, 1.054] |
| Implied density exponent | 1.858 | [1.697, 2.054] |
| Density exponent on paired 2023–2024 events | 2.239 | [2.085, 2.399] |
| Observed minus implied exponent | 0.382 | [0.125, 0.620] |

There are 1,168 paired evaluation events. The 1,306 in-domain evaluation events with peak
irradiance give a density exponent of 2.274, KS ≈ 0.032, and bootstrap probability ≈ 0.02.
The power-law family is inadequate under this working test. Likelihood alternatives are
descriptive when dependence or boundary-limit model overlap invalidates nominal Vuong
calibration. The stretched-exponential comparison was corrected because the old stored fit
and evaluated density used different effective scales.

Rise-phase fluence yields a gap of 0.411 [0.208, 0.604]. It has no missing values in the
selected domain but is a different resource; it cannot establish absence of primary
missingness bias. Lower cutoffs $10^{-6}$, $5\times10^{-6}$, $10^{-5}$, and
$3\times10^{-5}$ yield gaps −0.480, 0.191, 0.382, and 0.960.

The gap concerns the joint allocation, cost-scaling, distribution, and temporal-transfer
assumptions. The temporal split does not make the exploratory domain choice prospective.
The resource is band-limited fluence, not total flare energy. Month-block intervals do not
cover calibration, completeness, or all temporal dependence. Bootstrap spectra with empty
bins prevent a valid log-slope interval; the corrected pipeline reports that limitation
instead of dropping those replicates.

Provenance: [results.json](../results/results.json), noaa.cases;
[gof.json](../results/gof.json), noaa.

## 3. Ocean reconstruction

Source: Hatton et al. (2021), author-produced biomass summaries. This is a re-expression of
a published model-assisted reconstruction, not an independent organism census or replication.

| Domain | Maximum/minimum biomass ratio |
|---|---:|
| Upper 200 m, all 23 bins | 38.8 |
| Upper 200 m, selected 16-bin plateau | 1.7 |
| Full water column, same plateau bins | 4.3 |

The 23 one-decade bins have 22 decades between centres and 23 between outer edges. Plateau
centres extend from log10 mass −10.5 to 4.5, spanning 15 decades; the bin edges span 16.
Slope tolerances now use the edges. Each selected subrange is normalized to its own total
and width. The plateau is post hoc.

Published bounds equal estimate divided and multiplied by the reported group factor.
The uncertainty model draws each positive group/bin estimate lognormally, using log standard
deviation ln(f)/1.96, then sums groups and normalizes each simulated profile. This treats
the published point as a lognormal median. Error independence across groups and bins is
unverified. Alternative correlations could change conclusions.

At factor 1.25, 2 of 23 upper-ocean and 3 of 23 full-column pointwise intervals lie entirely
outside the tolerance band. These counts are not simultaneous tests. Intervals overlapping
the band can also admit substantial non-flatness. Neither “most bins are equal” nor “the
departures are absent” follows. The complete profile does not establish equivalence under
the supplied uncertainty model. The upper-ocean full-range slope is −0.0392 with propagated
90% interval approximately [−0.058, −0.026], outside the slope tolerance of 0.00421.
That model therefore indicates a systematic gradient; overlapping individual bin intervals
do not eliminate information in the whole profile.

Provenance: [independent.json](../results/independent.json), ocean_top200 and ocean_allwater;
[results.json](../results/results.json), ocean.

## 4. Aquatic slope summaries and invalid ranges

Source: GLOSSAQUA. The primary normalized-biomass subset contains 1,300 slopes from 16 study
identifiers. Prediction for biomass per unit mass is −1.

| Location summary | Value |
|---|---|
| Pooled median slope | −1.015 |
| Departure from prediction | −0.015 |
| Study-block 95% departure interval | [−0.100, 0.010] |
| Historical factor-1.25 median slope tolerance | 0.0317 |
| Historical factor-2 median slope tolerance | 0.0984 |
| Historical joint verdict | Not supported |

The median interval is not wholly inside either tolerance band. It does not establish
equivalence. A median is not an expected value, and mean slopes would not identify mean
resource occupancy either.

The recomputed point-slope fractions within tolerance are approximately 7.85% at factor 1.25
and 24.23% at factor 2 under inclusive boundary counting. **These are historical descriptive outputs with known-invalid range
metadata**, not estimated fractions of truly flat ecosystems. Individual errors and
within-spectrum curvature are not included. Two studies contribute 1,016 slopes, 78% of
the primary subset.

### Known-invalid bounds

All 377 StudyID_07 records have reported bounds $2\times10^{-8}$ to $2\times10^{27}$
pg C and 33 size classes. This is a 35-decade range with an upper mass of $2\times10^{12}$
kg C, unsuitable as a plankton body-mass domain. The original raw file and slope values are
preserved; no replacement bounds are guessed.

The explicit sensitivity excluding those records from range-dependent assessment contains
923 slopes from 15 studies. About **9.32%** meet the factor-1.25 point tolerance and **28.93%**
meet factor 2. Exclusion addresses one known defect; it is not a validation of every remaining
range. The primary location summary still retains all 1,300 slopes because it does not use
the size limits quantitatively.

Inclusive tolerance comparisons allow relative floating-point error of $10^{-12}$ at the
boundary. The exact counts and both historical and sensitivity outputs are in
[independent.json](../results/independent.json), glossaqua.subsets.

## 5. What the ensemble diagnostics do and do not show

The subset with usable reported errors has 747 slopes. Their error-aware likelihood fits
are descriptive because within-study dependence, method bias, and uncertainty calibration
are unresolved. A random-effects $I^2$ statistic is not a measured causal fraction of variance
attributable to ecology.

The corrected pass comparison uses the same 747 observations, their individual tolerances,
their error variances, and the fitted model location:

| Factor | Observed point-slope fraction | Gaussian fitted prediction | Student fitted prediction |
|---|---:|---:|---:|
| 1.25 | 0.0696 | 0.0890 | 0.0938 |
| 2 | 0.2436 | 0.2684 | 0.2820 |

These are internal checks with fitted parameters, not out-of-sample predictions.
The earlier near-perfect match used a latent probability, ignored observation errors,
assumed a zero location, and compared different samples. That claim is withdrawn.

Corrected convolution uses full-support adaptive integration rather than a coarse latent
grid. Narrow reported errors no longer interact with grid spacing to produce a misleading
likelihood. Student t remains the lowest-AIC candidate in the pooled comparison, but AIC
does not establish absolute adequacy. The corrected illustrative habitat mixture gives
standardized-residual excess kurtosis around 0.558 versus the observed 1.132. It does not
identify a unique explanation of the pooled shape.

Excluding the known-invalid span metadata changes the study-level association of span with
absolute departure to Spearman rho ≈ −0.453, p ≈ 0.090, n = 15. The former significant
association is not retained. Nonsignificance does not prove no association or establish low
power as its cause. Stratification is exploratory.

Provenance: [ensemble.json](../results/ensemble.json), [strata.json](../results/strata.json).

## 6. Variance and convention audits

Arranz's 639 lake estimates have raw SD ≈ 0.279 and descriptive error-adjusted dispersion
≈ 0.235. Gaedke's 377 records have raw slope SD ≈ 0.067 and lack reported standard errors.
Those are different populations, taxa, designs, and uncertainty models. Their variance ratio
does not bound the temporal share of aquatic variation. Cross-sectional samples confound
persistent site differences with occasion effects; repeated records need not represent
identical independent temporal observations. Small joint fits are available as exploratory
outputs, not validation of a universal decomposition.

Comparing a reconstructed Arranz SD with the source's published SD checks extraction from
the same underlying observations. It is not independent corroboration of a latent variance.

Perkins et al. (2018) uses log-bin counts, illustrating a documented mismatch with the
database's normalized-abundance category. This does not prove that every secondary discrepancy
is a labelling error or that the primary subset is entirely clean. Choosing conventions by
proximity to a predicted exponent would bias agreement. Whole-spectrum reanalysis and a
source-by-source convention audit remain preferable to pooling labels.

Provenance: [variance.json](../results/variance.json), [references.md](references.md).

## 7. Current conclusion

The physical examples disagree with particular, explicitly defined versions of logarithmic
resource allocation. The ecological data offer a familiar near-−1 location and unresolved
allocation claims. They do not establish a universal principle or a confirmed ensemble law.

The contribution retained in the manuscript is the explicit accounting formulation, its
dependence on the reference measure, counterexamples to stronger deductions, and a transparent
assessment of what these data permit.
