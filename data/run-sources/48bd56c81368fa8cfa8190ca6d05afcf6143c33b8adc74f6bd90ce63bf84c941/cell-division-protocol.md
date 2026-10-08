# Bacterial growth and division: published-summary transfer protocol

Run `cell-division-summary-2026-10-08`; protocol fixed 8 October 2026 before
reading the numerical annotations of Gangan and Athale (2017), Figure 1.
This is a retrospective comparison: the source's qualitative results and
birth/division measurements were already read. The local freeze is an integrity
record, not external preregistration or evidence of global blinding.

## Inputs and separation

Calibration is the arithmetic mean and variance of fitted lognormal birth
lengths in Figure 2b,d, for LB and M9+succinate. Independently fitted division
lengths (2c,e) diagnose the symmetric stationary assumption and supply a
declared sensitivity. Target endpoints are fitted mean and CV=sqrt(variance)/mean
of separate mid-log batch snapshots, Figure 1b, in those same two media.
No mutants, drug-treated cultures, microcolonies, or other media enter the test.
Printed four-decimal means/variances are transcribed, with image hashes and
panel identifiers; do not substitute arithmetic sample moments from prose.

The public Dryad workbook download returned HTTP 403 from both API and
HTML-linked endpoints. Metadata were retained; no workbook rows were decoded.
The official Figshare supplement was inspected for table structure but contains
no calibration/target moment table. Official NCBI figure images supply the
actual numerical inputs. This is a summary-level analysis, not a raw-data fit.

## Fixed models and endpoints

Assume a stationary chronological birth size B with the source-fitted lognormal
law, common noiseless exponential growth, exactly symmetric conservative
division, comparable lineage physiology, and an asynchronous balanced population.
Use H(x)=F_B(x)-F_B(x/2). The population prediction is proportional to H(x)/x^2;
the chronological lineage comparator is proportional to H(x)/x. Their moments
are evaluated analytically, with no population-fitted scale or shape.

Retain four forecasts: birth-calibrated population (primary); birth-calibrated
lineage (sampling comparator); population with fixed birth size equal to the
calibration mean (zero birth variability); and population calibrated using
division/2 (sensitivity, not a replacement if it performs better).

Score mean and CV separately by absolute log(predicted/observed), in each
medium. The primary population forecast improves on the lineage comparator
only if both errors are smaller in that medium. Do not combine endpoints or
select a winner across media. Report all predictions and results. Rounded
fitted summaries do not support sampling confidence intervals or a calibrated
hypothesis test; cell counts are provenance, not independent-replicate counts.
Display model profiles as predictions, without describing fitted target
lognormals as empirical histograms. No profile goodness-of-fit claim is made.

Before target retrieval, archive configuration, protocol, algorithms, tests,
calibration source hashes and numerical predictions in a local freeze. Verify
them before scoring. Evaluation may add plots and a provenance record but
cannot overwrite the freeze or modify forecasts.

## Applicability and interpretation

The two independent event fits need not obey D=2B. Report division/(2 birth)
mean ratio and division/birth CV ratio before evaluating the target; do not
clip negative differences of incompatible fitted CDFs. Birth-only forecasts
are coherent conditional models, not evidence that equal division holds.
Common exponential growth, identical old-pole physiology, uncensored stationary
event sampling, and device-to-batch comparability are not established by these
summaries. Known growth heterogeneity is a material limitation. Fixed cells
and living cells also have different acquisition procedures.

The theory concerns additive size (e.g. mass). Measured length is a proxy:
even at constant diameter d, spherocylinder volume is proportional to L-d/3,
not precisely L. Do not claim independently measured biomass allocation.
A successful summary forecast would be a limited transfer result; failure
rejects this complete length-proxy transfer model without identifying which
assumption failed. Neither result establishes or refutes a universal law.

The size tilt and inverse-square limit are prior growth-fragmentation theory
(Genthon, 2022). The proposed contribution is their explicit resource-allocation
interpretation and comparison using independent experimental summaries.
