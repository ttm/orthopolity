# Project status and handoff

Last updated 11 October 2026. **Read this first in a new session.** It records what the authors
intend, what has been done and found, the current assessment, and the next steps, with pointers
to the files that hold the details.

**Unified main, 9 October:** at the user's request, `py314-and-package-names`
was merged with the current `origin/main`, preserving both histories and using
the package layout for all runners. The suite now passes **500 tests**; the
registry verifies **35 runs and 853 file references**, including the Italian simulation
and retrospective chemostat diagnosis. The broader programme and subsequent
studies are in [research-brief.md](research-brief.md) and
[ongoing-research.md](ongoing-research.md).
The [flare-ribbon test has now run](flare-ribbons-run-2026-10-09.md):
α = 3.163 [2.962, 3.457], registered verdict inconclusive, both predictions
excluded under the implemented uncertainty model. The full HydroLAKES archive
has now been analysed. [Lake results](lake-gyration-results-2026-10-09.md):
global ζ = 1.930 passes the original iid equivalence rule, but spatial
equivalence is not established; UK ζ = 1.441 triggers its departure rule,
while its spatial interval still includes 2.
The [local-geometry and catchment follow-up](lake-metric-followup-results-2026-10-09.md)
now gives ζ=1.859, iid [1.844,1.874], basin [1.785,1.924]. The original iid
equivalence disappears. Exact 2 is excluded under these resampling assumptions,
but the basin interval overlaps [1.9,2.1], so the follow-up rule is inconclusive.

The [seismic qualification](seismic-qualification-results-2026-10-10.md) is complete:
full catalogues and published memberships were acquired, then source/quality
choices were frozen at `6ae7a8c`. The sequence count falls 40→28→16→6 through
raw, quality, completeness and resolution gates. The minimum is ten; no b or
D2 was fitted. This is an eligibility limitation and does not favour either
hypothesis. Data access is no longer the barrier for this cohort.

The [next-source audit](seismic-candidate-audit-2026-10-10.md) acquired full CLASS,
HORUS and Northern California catalogues. CLASS/HORUS provides 295,193
unambiguous location/magnitude-provenance links; 347 ambiguous CLASS rows are
quarantined. Only 699 matched events have direct moment-tensor provenance
(at most three disjoint 200-event groups), so proxy calibration is necessary.
Four timestamp discrepancies were checked against INGV; official times agree
with HORUS. No physical clusters, completeness or response fits were calculated
for these new sources. The source audit leaves the 33-run registry unchanged.

The [Italian magnitude validation](italian-magnitude-validation-results-2026-10-10.md)
has now run under a design committed before the ensemble. It fails in 45 of 56
required synthetic scenarios, including 30 of 32 noiseless proxy cases. Empty
converted-magnitude bins can invalidate the registered uniform-bin correction;
exact source-bin integration confirms the large biases. The stop rule ends this
bounded Italian attempt before real sequence construction or Mc/b/D2 fitting.
This is a simulation finding, not a physical hypothesis test. The manuscript
now integrates the geometry outcomes, seismic eligibility and estimator limits.

## 1. What the authors intend

**10–11 October clarification and completion:** retain the exact title
*Orthopolity: a general law of resource allocation*, the general-law claim and
the ambition to establish it. Make the mathematical core, ideal mechanisms,
gravity/radiation, models and empirical consequences clear; move detailed
material to a companion document. Explain independently specified resource,
metric or constraint effects, and investigate actual failures. Further empirical
work is authorized. The [reorganized article](paper.md),
[supporting material](supporting-material.md), and [revision map](manuscript-revision-2026-10-11.md)
implement this instruction. `make paper` now builds both PDFs.

The [new chemostat diagnosis](chemostat-capacity-followup-results-2026-10-11.md)
finds that **8/12 primary vessels** exceed a conservative two-resource
redistribution bound even with arbitrary nonnegative prices, measured
preliminary quota changes and every pooled-species mixture: **17/36** day/vessel
comparisons. Independent geometric verification reproduces all 144 entries.
This excludes fixed opportunities, the allocation family and transferred
point quotas jointly; it does not establish main-vessel physiology or a
statistical rejection. All outcomes were previously exposed, and the new
protocol freeze at `13374c5` is a retrospective diagnostic freeze. The earlier
forecast remains unsuccessful.

Positions stated by the lead author (Renato Fabbri), on behalf of himself and more senior
co-authors, in the 8 October 2026 session:

- **Orthopolity is true and general.** "Nature doesn't care about resources or their
  concentration, yielding that the more units concentrate resources, the less abundant they are."
  Departures, which are observed constantly, are imposed by the constraints real systems have.
- **Goal of the paper:** establish orthopolity as a general property of real systems. The authors,
  as physicists, regard it as a natural law; it may be better stated as a mathematical property.
- **Exponents need not be 1.** For example, $p(k)\propto k^{-3}$ means the underlying resource is
  related to $k$ in three dimensions, or to the 3.
- **Reading the resource after seeing the data is a strength.** The medium a system lives in can be
  interpreted as a resource, which can yield insight and powerful ways to treat the system.
- **Proposed programme:** take many natural laws and data sets that follow power laws, read each
  exponent as a "final resource" combining simpler resources, and look for regularities.
- **Terminology:** the adjective is *orthopolic* ([glossary.md](glossary.md)).
- **Workflow:** work directly on `main` (authorized 8 October 2026; the earlier branch
  `claude/modest-archimedes-mcgs34` is merged).

The assistant's assessments in this session repeatedly found weaker evidence than the authors'
position assumes. Both views are recorded below so that a later session neither overclaims nor
discards the authors' programme.

## 2. History

| Date | Work | Outcome |
|---|---|---|
| 9 Sep 2026 | Pilot analyses (earthquakes, flares, ocean, GLOSSAQUA), source audit, critical manuscript | [paper.md](paper.md): orthopolity as a conditional hypothesis; no natural law established |
| 8 Oct 2026 | First assessment | Rigorous and reproducible, but weak as a contribution: no live claim refuted, known results, physics tests repeat textbook criteria |
| 8 Oct 2026 | Research programme with adversarial review | [research-program.md](research-program.md): orthopolity as the long-residence limit of proportional growth; resource rule; pre-registered tests |
| 8 Oct 2026 | Glossary and terminology test | [glossary.md](glossary.md), `tests/test_terminology.py` |
| 8 Oct 2026 | Resource catalogue of 59 power laws | [resource-catalogue.md](resource-catalogue.md): a few rules, exponents as dimension counts under the log measure |
| 8–9 Oct 2026 | Four locally registered tests | [preregistered-tests.md](preregistered-tests.md): aftershock and flare runs inconclusive; global lake conditional equivalence; seismicity awaits qualified clusters |
| 9 Oct 2026 | Merge development branch into main and run lake continuation | Both histories preserved; global and separately frozen UK analyses completed; 430 tests and 31 registry entries verified |
| 9 Oct 2026 | Local lake geometry and hydrological uncertainty follow-up | 1.43M polygons processed; ζ=1.859, basin [1.785,1.924]; declared equivalence unestablished; 442 tests and 32 registry entries verified |
| 10 Oct 2026 | Frozen Southern California sequence qualification | 123,275 published events joined to original relocations; 6 eligible sequences versus minimum 10; no b/D2 fitting; 464 tests and 33 registry entries verified |
| 10 Oct 2026 | Italian calibration crosswalk and Northern California source audit | Three complete new sources; 295,193 unambiguous CLASS/HORUS links; direct-Mw-only route insufficient; identity issues retained; 473 tests pass |
| 10 Oct 2026 | Italian synthetic magnitude gate | 45/56 required scenarios fail; no real Italian b/D2 fit; 480 tests, 34 registry records |
| 10–11 Oct 2026 | Main article/support reorganization and chemostat failure diagnosis | Title/general-law ambition retained; technical details preserved; arbitrary C:N prices insufficient in 8/12 vessels under transferred quotas; 500 tests, 35 records |

## 3. Results to carry forward

**Definitions.** Log-orthopolic: equal resource per $d\ln k$; with resource $\propto k^d$, density
exponent $\alpha=d+1$. Linear-orthopolic: $\alpha=d$. Always state the measure.

**Mathematics** (known results, attributed in the documents):

- Vacuity: any power law is orthopolic for some resource ($q\propto k^{\alpha-1}$), so evidence
  comes only from resources identified independently.
- Proportional growth with entry and exit: $(\zeta-1)(\mu+\sigma^2\zeta/2)=\phi$, and in a
  stationary system $\phi=J_R/Q>0$, so $\zeta-1\approx1/(m\tau_{\rm res})$. Equal resource per log
  size is the long-residence limit (Reed 2001; Saichev, Malevergne and Sornette 2010).
- Catalogue rules: territory $\alpha=1+d_s/D_k$; transport $\alpha=1+w+z-d_F$; coordinate change
  $\alpha=1+\zeta/c$; martingale $\alpha=1+1/c$; proportional growth $\alpha\to2$; rate ratios.

**Empirical results in this repository:**

| Result | Value | File |
|---|---|---|
| USGS earthquakes, b (M ≥ 5.5) | 0.998 [0.973, 1.024] | `results/results.json` |
| Seismic moment, ζ | 0.666 [0.649, 0.683] (top-heavy) | `results/resource_choice.json` |
| Rupture area (converted proxy), ζ | 0.998; 1.36 [1.29, 1.44] above M 6.7 | `results/resource_choice.json` |
| GOES flare fluence, α | 2.13 [2.03, 2.22] raw; 1.90 [1.82, 1.99] background-subtracted | `results/resource_choice.json` |
| Ocean biomass spectrum | ζ ≈ 1.04 (Hatton et al. 2021) | `results/independent.json` |
| GLOSSAQUA median NBSS slope | −1.015, study-block interval [−1.100, −0.990]; equivalence not established | `results/independent.json` |
| Gibrat simulation | ζ follows the law; 0.988 ± 0.010 at φ = 0 | `results/gibrat.json` |
| Rule cases | 17 of 25 within the observed range | `results/resource_catalogue.json` |
| Catalogue grades (59) | 23 derived, 15 motivated, 18 suggestive, 3 numerology or none | `results/resource_catalogue.json` |
| Chance match, quarters at ±0.1 | 90% of exponents in [1, 4.5] | `results/resource_catalogue.json` |
| Aftershock productivity (pre-registered) | α = 0.63 [0.51, 0.71]; 0.90 [0.76, 0.97] with rupture-length windows; area (1.0) and moment (1.5) both excluded | `results/aftershock_productivity.json` |

Literature compilation of 49 exponents: [zeta-compilation.md](zeta-compilation.md). Stocks that
grow proportionally sit near ζ = 1; event catalogues and cascades mostly below 1.

| New continuation | Value | File |
|---|---|---|
| Flare ribbon area, density α | 3.163 [2.962, 3.457], both proposed exponents excluded | `results/flare-ribbons-2026-10-09/result.json` |
| Global lake radius, survival ζ | 1.930; iid [1.919, 1.941], Country [1.595, 2.030] | `results/lake-gyration-2026-10-09/result.json` |
| UK lake radius, survival ζ | 1.441; iid [1.191, 1.714], grid [1.166, 2.009] | `results/uk-lake-gyration-2026-10-09/result.json` |
| Global local-geometry radius, survival ζ | 1.859; iid [1.844,1.874], matched basin [1.785,1.924] | `results/lake-metric-followup-2026-10-09/result.json` |
| Southern California b/D2 eligibility | 6 sequences pass, minimum 10; no fitted response or hypothesis preference | `results/seismic-qualification-2026-10-10/result.json` |
| Italian magnitude prerequisite (simulation) | 45/56 required scenarios fail; real Italian sequence/response fitting not run | `results/italian-magnitude-validation-2026-10-10/summary.json` |

## 4. Current assessment

The unified repository contains mathematical foundations, explicit mechanisms,
resource-transfer applications and negative or qualified empirical comparisons.
The [research brief](research-brief.md) explains the general-law programme;
[ongoing research](ongoing-research.md) connects its broader studies.

- Catalogue matches alone do not identify resources or independently establish
  a law; several listed exponents remain unverified.
- Aftershock and flare registered decision rules are inconclusive. Their primary
  intervals exclude both specified rival readings under the implemented analyses.
- Global lake ζ is practically equivalent to 2 under its declared iid margin,
  but Country uncertainty does not establish equivalence and the basin interval
  is absent from that original analysis. The literal script's positive verdict
  remains recorded. Its local-geometry follow-up moves ζ to 1.859 and removes
  iid equivalence. The basin interval excludes exact 2 but overlaps the margin,
  so the follow-up is inconclusive under its frozen rule. LAEA and geodesic
  AEQD agree; 379 invalid selected polygons, 31 unmatched outlets and an iid
  goodness-of-fit diagnostic (p=0.014) prevent a fully qualified positive claim.
- The separately frozen UK replication triggers its either-interval departure
  rule, but its spatial interval includes 2. It is not a robust spatial rejection.
- The seismic source/quality supplement fails the minimum-ten eligibility gate.
  Location errors reduce 16 sufficiently populated sequences to six with a usable
  distance span. The error proxy can be conservative; unknown covariance,
  magnitude-dependent memberships and nonuniform magnitude scales limit a future
  physical comparison. Neither prediction has been tested on this real cohort.
- The manuscript has been substantially developed on the merged branch; the
  earlier claim that it still has only September's framing is superseded.
- The Italian proxy route fails a necessary synthetic magnitude-estimator gate.
  This does not reject either b/D2 relation. A source-bin likelihood helps in
  noiseless single-source simulations but remains unvalidated for detection,
  measurement errors and shared calibration uncertainty. No automatic estimator
  replacement or real-data rerun is pending.

## 5. Next steps, in priority order

1. **Turn a failure explanation into a new prediction.** The chemostat bound
   rules out price adjustment alone under the recorded assumptions. Seek
   elemental quotas measured in the same mixed vessels and information about
   changing grazing/opportunities. A new model must predict an independent
   trajectory or intervention; transferred preliminary assays are not a proven
   physiology envelope. Alternatively, identify an independently eligible natural
   allocation regime with measured resources and a calibrated observation design.
   The current retrospective result must not be promoted to blind confirmation.
2. **Resolve the seismic observation model before another real test.** Both the
   six-sequence Southern California eligibility finding and the failed Italian
   synthetic prerequisite are complete and retained. A new design would need
   source-aware bins, detection and shared calibration uncertainty, or a narrower
   independently justified homogeneous cohort. Validate it before freezing
   physical sequence/event/identity conventions and running qualification. Direct
   moment estimates alone cannot supply ten groups in the present crosswalk.
   Do not relax gates or promote the noiseless grid diagnostic automatically.
   The required D2 contrast remains unassessed; more data hosts are not the
   immediate remedy. See [validation results](italian-magnitude-validation-results-2026-10-10.md).
3. **Explain the lake departure with independently justified inputs.** Physical
   geometry and hydrological uncertainty have now been evaluated. Source
   topology, mapping completeness and classification remain unresolved. The
   declared Lake_type1 point sensitivity is already known (ζ=1.975); it cannot
   be promoted to a new blind confirmatory test. Preserve all completed outputs.
4. **Follow up aftershocks** with finite-fault rupture windows under a new protocol,
   disclosing the earlier result. Wildfire allocation is another available-data
   route requiring a separate resource and held-out prediction design.
5. **Review the shortened article and supporting material together.** Main
   Sections 2–3 develop the exact and physical content; Section 4 assesses
   predictions, including the new diagnosis; Section 5 distinguishes explanations
   from failures. Full comparisons and derivations remain in S1–S5. The
   [revision map](manuscript-revision-2026-10-11.md) resolves historical section
   numbers and records interpretation corrections. Preserve the general-law
   claim and scope-specific evidence; build both PDFs after manuscript changes.
6. **Submission work:** reconcile attribution, data notices, authorship and venue
   requirements recorded in the broader handoff and roadmap.

## 6. Conventions and environment

- Terminology and measures: [CLAUDE.md](../CLAUDE.md), [glossary.md](glossary.md).
- Evidence standard: an exponent match counts only if the resource and inputs were fixed before the
  exponent was examined and the reading passes a second, different prediction. Grades:
  derived, motivated, suggestive, numerology. Source tags in documents: verified, repository result,
  own derivation, unverified.
- `make install` then `make all` (about 4 minutes) verifies frozen inputs, runs 500 tests and
  regenerates every analysis. The September results were produced with Python 3.11; results
  added on 8–9 October (Gibrat, resource choice, catalogue, aftershocks) with Python 3.13 and the
  pinned packages. Other versions change the older files by at most about $4\times10^{-8}$
  relative. Do not commit such noise; restore those files with `git checkout -- <file>`.
- Raw inputs in `data/raw` are frozen and checksummed; analyses never download.
- The registering session had restricted source access. The 9 October local
  continuation acquired full public datasets using approved network access;
  acquisition receipts distinguish full files, samples and metadata-only reads.
- `make seismic-qualification` reproduces eligibility to `build/reproductions`;
  `make restore-seismic-sources` restores missing raw catalogues by checksum.
  The full registered b/D2 response calculation was not run because only six
  sequences pass. No outcome-dependent estimator or threshold adjustment is pending.
- `make seismic-candidate-audit` reproduces the Italian source crosswalk and
  Northern California inventory without fitting. `make restore-seismic-candidates`
  restores exact raw inputs; later changes at the rolling HORUS URL fail hashes.
- `make italian-magnitude-validation` reproduces the 72-cell synthetic check to
  an empty output directory under `build/reproductions`. It refuses to overwrite
  completed runs. No real earthquake rows enter this calculation.
- `make chemostat-capacity` reproduces the completed conditional diagnosis,
  verifies it independently, and renders its figure in an unused build directory.
  The new source/protocol freeze is `13374c5`; no network access is required.

## 7. Document map

| Status | Documents |
|---|---|
| Current | this file; [preregistered-tests.md](preregistered-tests.md); [glossary.md](glossary.md); [research-program.md](research-program.md); [resource-catalogue.md](resource-catalogue.md); [zeta-compilation.md](zeta-compilation.md); [references.md](references.md); [concept.md](concept.md) |
| Evidence and audit history | [evidence.md](evidence.md); [source-audit.md](source-audit.md); [lake results](lake-gyration-results-2026-10-09.md) |
| Latest lake follow-up | [metric/basin results](lake-metric-followup-results-2026-10-09.md); [frozen protocol](lake-metric-followup-protocol-2026-10-09.md); [basin sources](hydrobasins-source-2026-10-09.md) |
| Latest seismic qualification | [results](seismic-qualification-results-2026-10-10.md); [frozen supplement](seismic-qualification-protocol-2026-10-10.md); `results/seismic-qualification-2026-10-10/` |
| Next seismic inputs | [source/calibration audit](seismic-candidate-audit-2026-10-10.md); `data/seismic-candidates/2026-10-10/` |
| Italian magnitude prerequisite | [failed validation](italian-magnitude-validation-results-2026-10-10.md); [frozen design](italian-magnitude-validation-protocol-2026-10-10.md); `results/italian-magnitude-validation-2026-10-10/` |
| Unified manuscript and programme | [paper.md](paper.md) and `paper.pdf`; [supporting-material.md](supporting-material.md) and `supporting-material.pdf`; [revision map](manuscript-revision-2026-10-11.md); [research-brief.md](research-brief.md); [ongoing-research.md](ongoing-research.md) |
| Chemostat failure diagnosis | [result](chemostat-capacity-followup-results-2026-10-11.md); [frozen protocol](chemostat-capacity-followup-protocol-2026-10-10.md); `results/chemostat-capacity-followup-2026-10-10/` |
| Still applicable scope limits | [not-worth-pursuing.md](not-worth-pursuing.md) (cosmological, social and normative claims) |
| Raw provenance | [archive/2026-10-08/](archive/2026-10-08/README.md): full research dossiers, paper design (resource rule, gates, candidate datasets, falsification criteria), hostile referee report, fact-check, and the complete catalogue workflow output |
