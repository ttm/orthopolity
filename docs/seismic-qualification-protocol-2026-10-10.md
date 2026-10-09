# Qualification of published earthquake sequences

This local execution supplement completes the source and cluster choices left
open in the [original registration](../configs/prereg_2026-10-08_volumetric_seismicity.json).
Its hypotheses remain b=D2/2 versus b=1. The territory reading allocates resource
per **d ln rupture length**; its conversion to b assumes the stated
moment–magnitude and rupture-length relations. This supplement must be committed
before real completeness thresholds or scaling-range eligibility are calculated.
It does not replace the original registration or declare new positive evidence.

The source acquisition began on 9 October; this execution freeze is dated
10 October 2026 (Europe/Rome). One source record has minute=60; it is retained
with a validity flag because this stage uses published membership, not event
time. No timestamp is invented.

## Source and fixed membership

Use the author-hosted
[Zaliapin–Ben-Zion clustered catalogue](https://zaliapin.github.io/pubs/ZBZ_JGR2020_data.txt)
and its [description](https://zaliapin.github.io/pubs/ZBZ_JGR2020_data_description.txt):
1981–2018, preferred magnitude ≥2.0, with the published largest-event index as
cluster ID. Structural inspection before freezing found 123,275 unique events,
26,137 clusters, and 40 clusters with at least 200 raw events. No actual Mc, b,
D2 or regression has been calculated. The publication is
[Zaliapin and Ben-Zion (2020), doi:10.1029/2018JB017120](https://doi.org/10.1029/2018JB017120).
The file description's reference year says 2019; retain those source bytes and
use the final publication's 2020 citation in reports.

Join exact SCSN event IDs to the **same 1981–2018 relocated source named by the
authors**, `hs_1981_all_comb_K4_A.cat_so_SCSN_v01`, to obtain location errors.
All published events must match, and latitude, longitude, depth and magnitude
must agree within half their last printed decimal. Stop on missing IDs,
duplicates or larger discrepancies. Preserve published coordinates/magnitudes.
The newly acquired 1981–2025 catalogue is retained separately for future work;
its newer coordinates are not substituted into this cohort.

The clustering algorithm uses magnitude as well as time and distance. Its
labels are externally fixed before our outcome fitting, **not statistically
independent of magnitude**. Neither waveform relocation components nor source
processing boxes are promoted to physical seismic sequences. No clusters are
split, joined or tuned to reach the required count.

## Quality and uncertainty conventions

Keep cross-correlation locations (`ct`) and earthquake event types `le` or
`eq`. The [SCEDC definitions](https://scedc.caltech.edu/eq-catalogs/catalog-search-help.html)
identify `eq` as an earthquake within or near the authoritative region; the
older format uses `le` for local earthquakes. Retain a ledger of all exclusions.
Require both absolute horizontal and depth errors to be finite, >0 and <99 km.
Zero or very large placeholder values do not establish useful precision.
Relative errors are retained as source fields but not substituted for absolute
precision between waveform components.

Use sqrt(EH²+EZ²) as the declared conservative location-error proxy. This is
not a full covariance model. Common translation errors can cancel within a
relocation component; therefore absolute-error qualification can be conservative.
Record how many composite `(processing box, waveform cluster)` groups occur
in each complete sequence, and their largest fraction, without changing the
error rule after observing eligibility.

The source magnitude is the preferred catalogue value. It is not uniformly Mw,
and this old file has no magnitude-type field. The
[SCSN catalogue account](https://scedc.caltech.edu/about/BSSA_2010_Hutton_SCSN_cat.pdf)
describes magnitude history and local/ moment-magnitude distinctions. No
empirical exponent fit here would directly validate the moment-based conversion
without an independently justified magnitude calibration.

## Registered gates, evaluated in order

1. Preserve every published cluster in the ledger. Fewer than 200 raw or
   quality-retained events is an immediate necessary-condition failure; there
   is no need to fit Mc for a group that cannot possibly qualify.
2. For remaining groups, apply the original rounded MAXC+0.2 rule, bounded
   below by the publisher's magnitude floor 2.0. Select events at or above Mc
   using the original numerical tolerance; require at least 200.
3. Sort the decimal-string event IDs lexicographically. Use original local coordinates (111.195 km per degree,
   cosine of the mean latitude, depth in km). Cap at 3,000 hypocentres using a
   cluster-specific stream `SeedSequence([202610092, cluster_id])`. Record the
   sampled IDs. The median location error uses **all complete events**, as in
   the original script, not only the cap sample.
4. Apply Amendment 1 unchanged: positive pair distances; lower radius is the
   larger of the 200th closest pair and three median location errors; upper is
   one tenth of the 90th-percentile pair distance. Require a factor-three span.
   Degenerate coordinates and invalid error values fail explicitly, without
   NaN falling through to an artificially zero error floor.
5. Report an error-free geometric upper bound on the span as a **diagnostic
   only**. It cannot qualify a sequence or justify a hypothesis fit.
6. If fewer than ten groups pass, stop before b or D2 and record the registered
   comparison as inconclusive from insufficient qualified clusters. This cannot
   favour either hypothesis. Otherwise freeze the response-execution wrapper,
   fit the original estimators, and retain the original minimum D2 range 0.5
   and regression decision rules.

The rough 1,000-event planar / 3,000-event volumetric requirements found in prior
simulations are not hard new eligibility thresholds. The exact registered gates
decide. No relaxed errors, alternative clusters or smaller completeness cuts
will be selected to obtain a desired number of qualifying groups.

## Reproducibility

The acquisition manifest pins complete source bytes and hashes. Source files
stay local and can be restored from publisher URLs. Commit this protocol,
config, parsers, qualification code and synthetic checks before execution.
Retain the event selection table, all cluster rejection reasons, chosen cap
IDs, error/range diagnostics, provenance, source verification and runtime.
Append the actual-data qualification result to the immutable registry, without
overwriting any existing analysis. Missing coverage or insufficient resolution
is a design finding, not an exponent result.
