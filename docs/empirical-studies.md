# Supporting empirical methods and exploratory results

This supplement retains the detailed methods, results, sensitivities and source
limitations moved from Sections 3–5 of the manuscript on 7 October 2026.
The main article now summarizes these studies so that the allocation law,
mechanisms and inverse predictions remain central. No analysis, retained
numerical result or registered output was changed by this editorial move.
The section labels below preserve their earlier correspondence; references to
Section 2 refer to the [main manuscript](paper.md). Full bibliographic entries
are in that manuscript and the linked study reports.

## 3. Data and methods

### 3.1 Sources and scope

| Data source | Analysed material | Resource and size coordinate |
|---|---|---|
| NOAA GOES XRS flare reports, 2022–2024 | 10,501 catalogue events; 1,168 paired events in the primary evaluation domain | End fluence in J/m²; peak irradiance in W/m² |
| USGS ComCat, 2010–2024 | 6,639 events after retaining moment-magnitude types and rounding to 0.1 at threshold 5.5 | Magnitude-derived energy proxy as both resource and coordinate |
| Hatton et al. (2021) | 23 one-decade biomass bins, upper 200 m and full water column | Body mass for both |
| GLOSSAQUA (Ersoy et al., 2025) | 1,300 normalized biomass-spectrum estimates from 16 study identifiers | Body mass for both |

These are four data sources; the two ocean domains are related reconstructions. GLOSSAQUA
contains published estimates rather than organism-level observations. Study identifiers do
not guarantee independent authors, methods, sites, or measurement errors. The sources are
convenience cases for evaluating a hypothesis, not a representative sample of natural systems.
Input bytes are fixed by SHA-256 manifests; provenance and source notices accompany the data.

### 3.2 Analysis-plan provenance

The pilot configuration explicitly labels itself exploratory. The subsequent aquatic/ocean
plan is retained as [prereg_2026-09-09.json](../configs/prereg_2026-09-09.json). In local
history, commit 6df364f contains the plan and raw slope data, preceding analysis commit
a0c9973. This records an order of commits. It does not establish an immutable public
registration, independently verified blinding, or when values were first viewed.
Statements of blinding in the historical file are author reports. The current corrections
are retrospective, and the later ensemble, stratification, and variance analyses are
exploratory. No claim of confirmatory preregistration is needed for the descriptive and
mathematical results here.

### 3.3 Accounting and uncertainty

For bins $B_j$ of logarithmic width $w_j$, compute
$\widehat{\mathcal O}_j=\sum_{i\in B_j}q_i/w_j$ and
$\widehat C=\sum_j\sum_{i\in B_j}q_i/\sum_j w_j$. The normalized profile
$\phi_j=\widehat{\mathcal O}_j/\widehat C$ has width-weighted mean one by construction.
This is not evidence of flatness. Empty bins remain in the profile, the final boundary is
included, and missing resources require an explicit exclusion policy.

A factor-$F$ endpoint drift across log-domain width $L$ corresponds, for a power-shaped
spectrum, to slope tolerance $c=\ln(F)/L$. This differs from requiring every
$\phi_j\in[1/F,F]$: the latter permits a maximum-to-minimum ratio of $F^2$. Both slope
and profile deviations matter. A slope equivalence interval combined with a point-estimate
profile screen is not full simultaneous equivalence; that would require uncertainty for
the whole profile. Failure to establish equivalence is not, by itself, evidence of a
nonzero departure.

For flares, the arithmetic mean resource exponent is fitted by Gamma quasi-likelihood on
2022 data, with bounded count-density fitting on 2023–2024 over $[10^{-5},10^{-3}]$ W/m².
Log-resource least squares would target a different conditional quantity unless an appropriate
retransformation were justified. Pilot intervals use 600 calendar-month block resamples for
flares and calendar-year blocks for earthquakes. These do not capture all dependence or
selection bias. The temporal split separates estimation samples but does not make the
exploratory domain choice a prospective prediction.

Power-law diagnostics use maximum likelihood and a refitted parametric-bootstrap KS
statistic on declared support, following the approach of Clauset et al. (2009). The
rounded earthquake magnitudes are tested on their integer grid: for
$K=(M-M_0)/\Delta$, $P(K=k)=(1-r)r^k$ with $r=10^{-b\Delta}$. Continuous-reference KS
calibration is unsuitable for these ties. Parametric-bootstrap probabilities remain
conditional on an independent-event working model; catalogue clustering is a limitation.

### 3.4 Aquatic estimates and reconstruction uncertainty

The primary GLOSSAQUA subset requires body mass on the size axis, finite slopes and positive
ordered size limits, and the normalized biomass-spectrum convention. For biomass per unit
linear mass $B(m)\propto m^t$, equal biomass per log mass requires $t=-1$. We examine
$\beta=t+1$ and each estimate's reported size span. The historical plan uses $F=1.25$
and $F=2$, a 2,000-replicate study-block bootstrap for the pooled median, and a joint
criterion involving its interval and the fraction of slopes inside their tolerances.
That fraction ignores individual slope uncertainty and must not be interpreted as formal
individual equivalence. Slope summaries cannot detect within-spectrum curvature. A post-audit
sensitivity explicitly excludes StudyID_07 from range-dependent assessment because its
reported bounds are physically implausible; no replacement bounds are imputed (§4.4).

For the ocean reconstruction, 20,000 simulated profiles propagate reported multiplicative
uncertainty factors using lognormal draws centred on the published log estimates, with
log-scale standard deviation $\ln(f)/1.96$. The published bounds match estimate divided
and multiplied by $f$. Independent errors across groups and bins are a working assumption,
not a property established by those bounds. The reconstruction is not a sample of independent
organisms, and its plateau was selected after inspecting the upper-ocean estimates.

Exploratory random-effects and latent-distribution fits use reported errors where available.
Intervals converted to standard errors assume their advertised coverage and approximate
normality. Size-spectrum estimators can have biased estimates and miscalibrated intervals
(Edwards et al., 2017, 2020). Repeated spectra within studies and estimated error variances
further limit inference; independence-based pooled intervals are not primary evidence
of a population mean.

## 4. Results

### 4.1 Earthquakes contradict the specified energy-proxy allocation

Gutenberg–Richter scaling $N(\ge M)\propto10^{-bM}$ and proxy
$E\propto10^{\gamma M}$ give resource per log energy proportional to
$E^{1-b/\gamma}$. Flatness therefore requires $b=\gamma$. At threshold 5.5, the fitted
$b=0.998$ has year-block 95% interval [0.973, 1.024], far below the chosen $\gamma=1.5$.
Thresholds 6.0 and 6.5 give 0.984 and 0.977. Using conversion exponent 1.44 also leaves a
substantial discrepancy.

At threshold 5.5 the discrete KS statistic is approximately 0.0077, with a parametric-bootstrap
probability about 0.26. This is non-rejection of the fitted geometric model, not proof that
the model is exact. A power-like tail can thus coexist with a resource-proxy allocation that
disagrees with $O_{\log}$. No discrete lognormal comparison was conducted. Magnitude-derived
energy is not independently measured radiated energy; the finding is restricted to the
specified proxy and catalogue, without declustering or a regional completeness model.

### 4.2 Flares disagree with the joint prediction on the selected domain

The fitted resource exponent is $d=0.858$ with 95% interval [0.697, 1.054]. The implied
density exponent is 1.858, compared with 2.239 [2.085, 2.399] in the paired evaluation
sample. The estimated gap is 0.382 [0.125, 0.620]. A rise-phase fluence sensitivity gives
gap 0.411 [0.208, 0.604]. This alternate resource has no missing values in the domain,
but does not prove the primary end-fluence analysis free of missingness bias.

For all 1,306 in-domain evaluation events, peak irradiance has fitted exponent 2.274 and
KS statistic about 0.032; its bootstrap probability is about 0.02. The power law is
therefore inadequate under this working test. Its likelihood cannot clearly distinguish
it from the fitted lognormal. Exponent mismatch tests the conjunction of equipartition,
power-shaped mean cost, transfer between years, and the count model; it cannot isolate
equipartition from all those assumptions.

The gaps at four lower cutoffs are −0.480, 0.191, 0.382, and 0.960. This substantial
sensitivity discourages treating one selected range as a universal scaling regime.
Fluence is instrument-band irradiance integrated over an event, not total flare energy.

### 4.3 The ocean reconstruction is compatible with a broad, uneven plateau

The upper-ocean summary reproduces the published abundance slope at approximately −1.039.
Its maximum-to-minimum biomass ratio is 38.8 across all 23 bins, and 1.7 within the selected
plateau of 16 bins. The corresponding full-water-column plateau ratio is 4.3. The 23
one-decade bins span 23 decades between outer edges; their centres are 22 decades apart.
Similarly, the plateau covers 16 decades between edges and 15 between centres.

Under the stated uncertainty propagation, only 2 of 23 upper-ocean bin intervals lie
wholly outside the factor-1.25 band; the corresponding full-column count is 3. These are
pointwise intervals without multiplicity adjustment. The remaining intervals can include
both near-flat and materially non-flat values, so their overlap with the band establishes
neither equality nor absence of departures. Correlated reconstruction errors and post hoc
range selection further limit the assessment. These results re-express Hatton et al.'s
reconstruction; they do not independently replicate it.

The full upper-ocean range has a fitted biomass log-slope of −0.0392 and a propagated
90% interval approximately [−0.058, −0.026], outside the factor-1.25 slope tolerance
of 0.00421. Thus the assumed uncertainty model indicates a systematic gradient even
though most individual bin intervals overlap the pointwise band. Pointwise overlap
does not make the whole-profile question uninformative; its interpretation remains
conditional on the reconstruction error model.

### 4.4 Aquatic slopes are close in location, without established equivalence

Among 1,300 normalized biomass spectra from 16 study identifiers, the pooled median slope
is −1.015. The study-block 95% interval for its departure from −1 is [−0.100, 0.010].
The median slope tolerance is 0.0317 at $F=1.25$ and 0.0984 at $F=2$. This interval is
not wholly within either band. Under the historical joint criteria, the result is
**not supported**.

The reported-slope fractions inside their individual drift tolerances are 0.07846
($F=1.25$) and 0.24231 ($F=2$), counting boundary cases inclusively. These are descriptive compatibility fractions. Their
complements are not estimates of the fraction of true spectra violating equipartition,
because measurement error and within-spectrum shape are not accounted for.

These historical fractions also depend on a metadata defect: all 377 StudyID_07 records
report bounds of $2\times10^{-8}$ to $2\times10^{27}$ pg C, a 35-decade range with a
physically implausible upper body mass of $2\times10^{12}$ kg C. Excluding those records
from this range-dependent calculation leaves 923 slopes from 15 studies. Their point-slope
compatibility fractions are 9.32% at $F=1.25$ and 28.93% at $F=2$. The source-derived
replacement bounds are unknown; the original slopes remain in the location summary.
The remaining records also require a methods and units audit. Consequently neither version
of the pass fraction should be treated as a validated estimate of ecological prevalence.

Two studies supply 1,016 of the 1,300 estimates, approximately 78%. A central estimate
near −1 is worth investigating, but it neither establishes a mean of −1 in a defined
population nor establishes equal average biomass occupancy. The stronger ensemble
interpretation fails on both statistical and mathematical grounds (main manuscript §2.6).

### 4.5 Exploratory diagnostics identify further limits

Latent-shape fits and random-effects summaries describe appreciable variation in the
error-reporting subset. Their fitted dispersion includes ecological differences, study
methods, and potentially unmodelled dependence. An $I^2$ estimate is not a measured
fraction of variance caused by ecosystem differences. AIC rankings among Gaussian,
Laplace, and Student families do not establish adequacy or identify ecological classes.
Error-aware, matched-sample pass fractions are internal model checks, not independent
predictions of individual failure.

The cross-study comparison of 639 lake-fish estimates with 377 records associated with
Gaedke's Lake Constance study does not partition spatial and temporal variance. Different
taxa, sampling designs, fitting methods, and measurement uncertainties prevent treating
their variance ratio as a bound on one population. Reproducing Arranz et al.'s reported
summary statistics from the same underlying observations checks extraction, not independent
replication of a dispersion parameter.

Exponent metadata also need source verification. Counts in equal-log bins and abundance
divided by linear bin width have slopes differing by one under power scaling. The
Perkins et al. (2018) count-bin method illustrates why a database category alone may not
identify the estimand. Choosing a mapping because it makes a slope closer to −1 or −2
would bias the test. Secondary conventions remain sensitivity analyses; a complete
study-level methods audit is needed before pooling them. Checks of two dominant primary
studies do not validate every record in the primary subset.


## Supporting detail for the frozen-forecast studies

The following detailed accounts preserve the earlier manuscript text; the main
article retains the principal outcomes and figures in a shorter account.

## 5. Frozen-forecast tests

The analyses of Section 4 assess data that had already been inspected. We therefore added tests
in which the resource, its cost law, the forecasts and the decision rules are fixed before the
evaluated outcomes are decoded, and in which whole units are held out: launches, a calendar year,
vessels and selection treatments. Each executed study retains its inputs, frozen protocol,
archived algorithms, forecasts and results in an append-only [run registry](run-registry.md).
Three kinds of evidence are kept separate: measurements on engineered systems, an unused
observation period of a natural catalogue, and published biological experiments reanalysed
retrospectively. Published summaries of those experiments had been read, so their reanalyses
are retrospective validations, not blinded tests. A further plant study uses fixed scoring
and a development-only geographic split after accidental raw outcome exposure. Its freeze
cannot establish that those outcomes were unseen.

### 5.1 Controlled allocation measurements

In a controlled workload experiment, separately measured memory and CPU costs of matrix tasks
predicted completion profiles under assigned quota pairs within four tolerances frozen before
672 validation tasks ([workload pilot](workload-pilot.md)). A fresh launch exposed a transfer
boundary: the original forecast failed its unchanged tolerance in two of four conditions, and
local recalibration recovered one ([workload transfer](workload-transfer.md)). The quotas were
acceptance criteria, so these tests concern the transfer of cost models, not allocation.

An allocation test requires the system, not the experimenter, to divide a resource. In a Python
runtime whose global interpreter lock serializes execution, worker threads running matrix
kernels of five sizes competed for one execution resource
([dimensionality intervention](dimensionality-intervention.md)). Separate calibration gave CPU
cost degrees 1.870 and 2.686 for the two kernels. The calibrated mean-cost curves predicted
complete CPU and job profiles before 16 allocation trials, with maximum CPU-share errors of
0.0035–0.0063 and job-share total-variation errors of 0.0021–0.0124. Replacing the
largest-class thread with a second smallest-class thread produced the predicted CPU-share change
within 0.0078. A unit-cost alternative had count errors of 0.126–0.273. This success concerns
one engineered allocation mechanism; it identifies no geometric dimension and no tendency of
natural systems.

### 5.2 Calibrated decisions and an unused observation period

Complete-profile equivalence decisions were calibrated on 180,000 independently generated
datasets in 90 conditions ([profile calibration](profile-calibration.md)). Simultaneous bands
met the declared gate for dense, bounded, independent blocks at 48 blocks, with minimum coverage
93.95%, but failed at 12 and 24 blocks. With twelve serially dependent blocks, wrong-departure
rates reached 43.75%. These failures define observation designs for which no neutrality verdict
is available, whatever a nominal interval suggests.

For solar flares, measured rise-phase fluence costs, six logarithmic classes, three forecasts,
a tolerance and an application gate were committed before the 2025 NOAA records were acquired
([solar validation](solar-validation.md)). Of 3,277 events, 356 met the domain rules.
Logarithmic neutrality predicted the class counts much better than linear neutrality, with
count total variation 0.125 against 0.573; historical counts did better still, at 0.022. The
point profile departed from the $\ln 1.5$ margin, but the calibrated decision remained
unresolved, as declared before acquisition, and the instrument mix changed between periods.

### 5.3 Published biological measurements

| Study | Held out | Resource and cost | Frozen comparison | Outcome |
|---|---|---|---|---|
| *Synechococcus* quotas (Harcourt et al., 2024) | Ten cultures at 25 °C | C, N and P per cell against measured diameter | Fixed cube, free power, strain means, temperature trends | Fixed cube best for C; strain means best for N and P |
| Size-selected *Dunaliella* (Malerba et al., 2018) | Each selection treatment | Biovolume at carrying capacity in one shared medium | Equal biovolume ($d=1$), fitted size law, assigned exponents, equal cell number | Equal biovolume best; cells at capacity scale as $V^{-1.02}$ |
| Food-web chemostats (Wojcik et al., 2025) | Twelve polyculture vessels | Algal N stock: biovolume times separately assayed N per volume | Persistence, development response, no-herbivore response, equal stock, two-budget cost ratio | No model beat persistence; the cost-ratio rule failed |
| Harvested plants (Dillon et al., 2019) | Five Colorado plots; prior raw exposure | Direct aboveground dry mass; $q(m)=m$ by definition | Log and linear neutrality, Ohio histogram, bounded Pareto and Weibull | Pareto best for biomass; trained models better for counts; ecological neutrality unresolved |

Published elemental quotas of four *Synechococcus* strains tested whether a size-based cost
transfers to an unused temperature ([cost transfer](archived-cost-transfer.md)). Trained on
16–22 °C cultures, a cubic diameter law with one fitted intercept predicted held-out 25 °C
carbon quotas within a typical factor of 1.14. For nitrogen and phosphorus, strain means beat
both size laws, and a fitted exponent never beat the fixed cube. Extrapolated temperature trends
were worst for every element. A cost calibration can therefore transfer for one resource while
failing as a size law for another resource in the same cells.

The accounting identity behind orthopolity, $N\,q(V)=R$, predicts how abundance scales with
per-object cost when a budget is shared. Thirty *Dunaliella tertiolecta* lineages, artificially
selected for about 280 generations into small, control and large classes, were regrown
separately in one F/2 medium after replete, N-deprived or P-deprived histories
([size budget](dunaliella-size-budget.md)). The protocol was committed before any small- or
large-selected outcome was decoded; each held-out selection treatment was then predicted from
the other two. Across a 10.4-fold range of mean cell volume, replete carrying capacity in total
biovolume was constant to within 3%, so cell number at capacity scaled as $V^{-1.02}$
(Figure 4). The frozen equal-biovolume law ($d=1$) had held-out errors of 0.124 and 0.179 log
units. It outperformed a size law fitted within part of the range, whose fitted cost dimension
was 0.74 in one fold and 1.12 in the other, and an equal-cell-number law, with errors of
1.48–2.08. A carbon cost degree assigned from the *Synechococcus* study ($d=0.91$) performed
comparably; its nitrogen degree ($d=0.80$) did not. Regrowth after N deprivation nearly
restored capacity, whereas P deprivation left an overshoot of 25–31% in control and large
lineages but not in small ones. Restoring the medium therefore did not guarantee a return to the
replete profile.

In 24 food-web chemostats, a nitrogen pulse redistributed algal resource composition
([chemostat response](chemostat-response.md)). Pre-pulse N and C per cell volume from separate
monocultures converted three algal groups' biovolumes into resource stocks. Forecasts for twelve
held-out polyculture vessels were frozen before their post-pulse values were decoded. The pulse
moved resource composition by 0.25 total variation on average, about 1.5 times the pre-pulse
variation around baseline, yet no forecast improved appreciably on persistence: 0.243 for the
development response against 0.247. A two-budget allocation rule, in which a binding secondary
carbon budget reweights each group's share by its measured C:N ratio, failed on three counts. Its
attainable redistribution, 0.05–0.12, was below every observed departure, 0.29–0.49. Its
predicted direction held in 4 of 12 vessels, the chance count. It did not beat persistence. No
held-out vessel recovered its pre-pulse composition within 12 days.

![Size-selected Dunaliella lineages regrown in one shared medium](../results/dunaliella-size-budget/size-budget.png)

*Figure 4. Size-selected Dunaliella lineages regrown in one shared medium, from the data of
Malerba et al. (2018). (a) Replete carrying capacity in total biovolume against mean cell
volume, with the two cross-fitted size laws and the equal-biovolume law. (b) Implied cell
number at capacity. (c) Held-out errors of the frozen forecasts. (d) Capacity after N or P
deprivation against replete capacity. Generated from retained outputs by
[report_dunaliella_size_budget.py](../experiments/report_dunaliella_size_budget.py).*

### 5.4 Directly weighed coexisting plant stocks

Ten harvested herbaceous plots provide direct aboveground dry masses for coexisting ramets
or stem clusters (Dillon et al., 2019; [plant study](plant-biomass-profile.md)). Forest and
desert allometric masses are excluded. Five Ohio plots supply development fits; five Colorado
plots supply evaluation. The protocol, algorithms and forecasts were committed before formal
scoring, but raw rows had already been exposed during source inspection. This is a retrospective
transfer comparison. It identifies neither a limiting nutrient nor an opportunity budget;
$q(m)=m$ defines the measured stock rather than testing an independent cost law.

The frozen domain is 0.01–100 g, split into eight half-decade bins with empty classes retained.
The upper bound depends only on Ohio masses. Thirty missing mass records, 144 subthreshold
ramets and one above-domain ramet remain in the evaluation membership ledger. The latter
weighs 112.55 g and accounts for 24.50% of one plot's known biomass. In-domain mass coverage
is 75.48% there and 99.89–99.97% in the other four plots. Scores therefore describe the
declared domain; the excluded mass and unknown missing mass cannot be silently absorbed.

The primary score is equal-plot mean total variation between realized normalized biomass
and each expected-stock or empirical template. Bounded Pareto scores 0.470, logarithmic
neutrality 0.493, linear neutrality 0.507, the development histogram 0.510 and bounded
Weibull 0.531 (Figure 5). Pareto beats logarithmic neutrality in three of five plots;
large opposing plot differences leave a mean improvement of only 0.023. Count profiles
provide a different comparison: the development histogram, Pareto and Weibull score
0.260–0.271, versus 0.412 for linear and 0.495 for logarithmic neutrality. Their binned
count log losses are about 1.83, versus 2.08 and 2.42. These are point discrepancies,
without a calibrated ecological superiority or equivalence verdict. They also do not
contradict the original study's superior within-site Weibull fits: the models here transfer
across locales and share a development-fixed domain.

Synthetic calibration fixes census size and draws masses from $m^{-2}$ on the same domain,
so each bin has equal expected biomass before measurement rounding. At 160 independent ramets, mean realized stock TV
is 0.441 and every simulated census has an empty bin. The largest bin's average normalized
share is 3.13%, although its normalized expected stock is 12.50%. At 1,280 ramets these
values are 0.244, 87.2% and 9.12%. Thus
$E[R_i/\sum_jR_j]$ differs from $E[R_i]/\sum_jE[R_j]$. A separately generated iid 95% TV
envelope has exceedance rates 6.2% and 5.2%, but repeating masses in blocks of twenty raises
these to 97.8% and 99.9%. This stress test is not an ecological dependence model. Field
dependence, inclusion and independent regional replication remain unidentified, so the
ecological neutrality decision is unresolved. An uneven small census alone cannot settle
a claim about expected allocation.

![Plant biomass transfer and finite-census normalization](../results/plant-biomass-profile/mass-profile.png)

*Figure 5. Directly weighed plant profiles and synthetic observation limits. (a) Equal-plot
mean Colorado biomass shares and transferred stock templates. (b) Count shares and retained
count forecasts. (c) Each plot's biomass discrepancy and the five means. (d) Mean normalized
census shares under iid logarithmic neutrality, compared with normalized expected stocks.
All panels read retained outputs; [report_plant_biomass_profile.py](../experiments/report_plant_biomass_profile.py)
performs presentation only. Prior raw exposure and excluded biomass are retained.*
