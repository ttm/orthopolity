# New seismic inputs: Italy has a usable calibration link, not yet a qualified test

Three more complete public sources have been downloaded and verified. The most
promising route combines Italian CLASS locations with HORUS magnitude calibration:
**295,193 records have unambiguous matching IDs and magnitude-provenance records**.
This supplies information missing from the earlier Southern California cohort,
but it does not yet establish ten qualifying physical sequences. No completeness
threshold, b-value, D2, regression or hypothesis verdict was calculated.

| Source | Full file acquired | Source audit |
|---|---:|---|
| CLASS 1.0, Italy, 1981–2018 | 21,979,365-byte gzip | 422,557 location records with quality classes, formal location errors and magnitude types |
| HORUS, Italy, snapshot acquired 10 October 2026 | 61,118,210-byte ZIP | 532,037 catalogue rows; 523,241 provenance rows; original-input and randomized-input variants supplied |
| NCAeqDD v202112.1, Northern California, 1984–2021 | 26,082,007-byte gzip | 879,626 unique event IDs; relative error ellipses; publisher identifies magnitudes as ML |

Exact URLs, SHA256 and byte counts are in the
[source manifest](../data/seismic-candidates/2026-10-10/acquisition.json).
All five HORUS ZIP members have separate uncompressed hashes and CRC checks in
[the member receipt](../data/seismic-candidates/2026-10-10/horus-members.json).
Large raw downloads remain local and ignored by Git. The original six-sequence
[Southern California qualification](seismic-qualification-results-2026-10-10.md)
remains unchanged.

## Why the Italian pairing is useful

[CLASS](https://ingv.github.io/class/locations/) supplies probabilistic absolute
locations, horizontal and vertical errors derived from a 68% error ellipsoid,
quality categories, magnitude types and an INGV event identifier when available.
It is not simply a list of high-precision relative locations.
[HORUS](https://horus.bo.ingv.it/) supplies a published homogenization to moment
magnitude, with uncertainty and source provenance. Its calibration was developed
independently of this b/D2 test, but converted magnitudes remain proxies rather
than direct moment measurements. Both sources identify CC BY 4.0 terms.

The audit uses the publisher's **`_o` original-input files**. The
[retained README](../data/seismic-candidates/2026-10-10/metadata/HORUS-README.txt)
states that the default variant adds random decimal jitter to ML/Md before
conversion. Original-input does not mean unconverted: `_o` still contains direct
or proxy Mw values. No synthetic jitter, new calibration coefficient, magnitude
rounding or response estimate has been introduced by this audit.

The exact-ID crosswalk retains every CLASS row and records:

| Identity/provenance status | Rows |
|---|---:|
| Unambiguous CLASS, HORUS catalogue and HORUS provenance match | **295,193** |
| Missing positive INGV ID | 79,568 |
| Ambiguous CLASS identifiers, quarantined | 347 |
| No unambiguous HORUS catalogue match | 47,449 |

Of the matched rows, **699** have direct moment-tensor provenance, **294,484**
have proxy provenance, and **10** have no final magnitude provenance label.
There are 243,550 matched records in source quality categories A/B with positive
finite error fields. This is an availability description, not a frozen analysis
cohort: earthquake classification, magnitude completeness, identity anomalies,
physical sequence membership and measurable distance ranges still matter.

Direct moment measurements alone cannot meet the original minimum. Even before
quality or completeness cuts, 699 observations can populate at most
`floor(699 / 200) = 3` disjoint groups of the required minimum size. This is an
upper bound, not three identified sequences. A viable Italian comparison must
therefore validate how calibrated proxies and their uncertainties affect the
registered estimator and decision rule.

## Problems caught before fitting

**Identifiers are not all unique.** There are 43 rows with repeated `id_class`
and 334 with repeated positive `id_ingv`; these overlap, leaving 347 quarantined
rows. Some repeated CLASS IDs have different alternate INGV IDs. The join never
uses `keep first`, matches missing/zero IDs, or expands an ambiguous join into
multiple observations. The
[collision ledger](../data/seismic-candidates/2026-10-10/audit/class-identifier-collisions.csv)
preserves every affected source row.

**Four matching IDs have origin times differing by more than a minute.** One
differs by about a day. All four were queried against the current official INGV
event service; its times agree with HORUS, and one is classified as a quarry
blast. The [lookup receipts](../data/seismic-candidates/2026-10-10/identity-lookups.json)
and [discrepancy table](../data/seismic-candidates/2026-10-10/audit/class-horus-time-discrepancies.csv)
retain the evidence. Source records are not silently corrected. A future
time-based clustering procedure must declare which time source it uses and how
it handles uncertain matches. Ordinary relocation-induced time shifts are also
retained; the median absolute CLASS/HORUS difference is 0.454 seconds.

**Quality documentation has a contradictory field description.** The observed
numeric ranges are A below 0.25, B from 0.25 to below 0.5, C from 0.5 to below
0.75, D from 0.75 to 1, and E without a numeric value. This agrees with the
publisher's narrative but reverses its separate `qmd_num` field description.
The audit preserves the letter category and numeric value; it does not select
a numerical quality cutoff from the conflicting description.

**Magnitude conversion needs an observation model.** In 656 matched rows, the
catalogue Mw differs from the provenance table's value by more than half of
0.01 magnitude; the largest difference is about 0.0148. These differences are
retained, not harmonized. A converted and rounded ML/Md mixture is not
automatically equivalent to independently measured Mw with uniform 0.1 bins.
The original Aki–Utsu correction and conditional bootstrap need simulation under
the actual transformation and uncertainty before treating their intervals as
calibrated. Merely rounding the proxy column to 0.1 would not establish this.

**Event classification is incomplete historically.** Among the matched records,
1,230 have HORUS's non-earthquake flag. That flag is documented only from May
2012 onward. An earlier blank cannot be interpreted as a verified earthquake.
No event-type filter has been frozen for a new response calculation.

## Northern California and other routes

Northern California is available in full, with 868,195 rows having positive
finite values in all three published relative-error fields. The remaining
11,431 have at least one unavailable/nonpositive value. Its 28,707 negative
depths are retained: the publisher explicitly references depth to the geoid,
so a negative depth is not by itself a corrupt location. The
[publisher README](https://nocaldd.ldeo.columbia.edu/catalog/README) specifies
95% relative-location errors and NCSN ML magnitudes. Those errors cannot be
inserted unchanged as absolute one-sigma uncertainties. No physical-sequence
labels or independent Mw calibration have been established here for this file.

Two other sources were screened from primary documentation without treating
metadata as a downloaded analysis cohort. The
[2026 consistent New Zealand catalogue](https://zenodo.org/records/18820779)
describes 407,553 reassessed events, but its files are restricted. Japan's
[JUICE catalogue](https://www.hinet.bosai.go.jp/topics/JUICE/?LANG=en) is publicly
offered, but warns of independently relocated grids and possible offsets at
their boundaries; grid membership alone would not supply physical sequences.
The [GCCEL methods](https://seismo.com/gccel/) describe calibrated clusters of
up to about 200 selected events, intended for accurate reference locations.
That selection does not establish a complete frequency–magnitude population.

## Reproduction and next experiment

```bash
make restore-seismic-candidates PY=python3.11  # only if pinned raw sources are absent
make seismic-candidate-audit PY=python3.11
make registry-verify PY=python3.11
```

The audit is offline and writes to `build/reproductions/seismic-candidates`.
Restoration refuses changed bytes. HORUS has a rolling URL, so a future publisher
revision must not silently replace this snapshot. The
[compressed crosswalk](../data/seismic-candidates/2026-10-10/audit/class-horus-crosswalk.csv.gz),
[counts](../data/seismic-candidates/2026-10-10/audit/audit.json) and
[independent verification](../data/seismic-candidates/2026-10-10/audit/verification.json)
are retained. Verification uses Python's CSV reader separately from the pandas
join to check all 422,557 CLASS rows, the magnitude provenance, all Northern
California row counts and the four official timestamp lookups. The suite passes
**473 tests**. This source audit adds no hypothesis-comparison registry entry;
the existing 33 runs remain intact.

The recommended next experiment uses CLASS/HORUS, subject to three steps:

1. Freeze a physical sequence definition and event/identity policy. No published
   membership table suitable for this merged cohort was established in this
   search. Nearest-neighbour clustering is allowed by the original registration,
   but its magnitude dependence and fixed parameters must be explicit. Arbitrary
   spatial cells or relocation components must not be presented as independent
   sequences.
2. Validate the converted-magnitude estimator with the published calibration,
   rounding and uncertainty model in both synthetic hypothesis worlds. Any change
   to the registered estimator requires a dated amendment before real fitting.
3. Apply the original population and resolution gates, then require ten usable
   sequences and the declared dimension contrast before a hypothesis comparison.

The physical target remains **log-orthopolic** allocation per logarithmic rupture
length, b=D2/2 versus b=1. These new inputs make a better documented test possible;
the audit itself supplies no evidence for either relation.
