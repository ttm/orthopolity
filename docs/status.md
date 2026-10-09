# Project status and handoff

Last updated 9 October 2026. **Read this first in a new session.** It records what the authors
intend, what has been done and found, the current assessment, and the next steps, with pointers
to the files that hold the details.

**Unified main, 9 October:** at the user's request, `py314-and-package-names`
was merged with the current `origin/main`, preserving both histories and using
the package layout for all runners. The merged suite passes 430 tests; the
31-run registry verifies all 751 file references. The broader programme and subsequent
studies are in [research-brief.md](research-brief.md) and
[ongoing-research.md](ongoing-research.md).
The [flare-ribbon test has now run](flare-ribbons-run-2026-10-09.md):
α = 3.163 [2.962, 3.457], registered verdict inconclusive, both predictions
excluded under the implemented uncertainty model. The full HydroLAKES archive
has now been analysed. [Lake results](lake-gyration-results-2026-10-09.md):
global ζ = 1.930 passes the original iid equivalence rule, but spatial
equivalence is not established; UK ζ = 1.441 triggers its departure rule,
while its spatial interval still includes 2.

## 1. What the authors intend

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
  is absent. The literal script's positive verdict remains qualified.
- The separately frozen UK replication triggers its either-interval departure
  rule, but its spatial interval includes 2. It is not a robust spatial rejection.
- The manuscript has been substantially developed on the merged branch; the
  earlier claim that it still has only September's framing is superseded.

## 5. Next steps, in priority order

1. **Resolve the global lake observation model.** Declare a follow-up for physical
   distance, complete polygon geometry, distribution adequacy and hydrological
   dependence before further fitting. Preserve the completed original result.
2. **Qualify the remaining seismicity test.** Relocated catalogues are downloaded;
   freeze quality/magnitude filters and physical clusters before b or D2 fits.
   Require ten eligible clusters and sufficient dimension contrast. See
   [available data](accessible-datasets-2026-10-09.md).
3. **Follow up aftershocks** with finite-fault rupture windows under a new protocol,
   disclosing the earlier result. Wildfire allocation is another available-data
   route requiring a separate resource and held-out prediction design.
4. **Synthesize the paper and verify the catalogue.** Incorporate both branches'
   scoped findings and retain the distinction between derivations, conditional
   exponent agreement and empirical resource identification. Regenerate the PDF
   whenever the manuscript changes.
5. **Submission work:** reconcile attribution, data notices, authorship and venue
   requirements recorded in the broader handoff and roadmap.

## 6. Conventions and environment

- Terminology and measures: [CLAUDE.md](../CLAUDE.md), [glossary.md](glossary.md).
- Evidence standard: an exponent match counts only if the resource and inputs were fixed before the
  exponent was examined and the reading passes a second, different prediction. Grades:
  derived, motivated, suggestive, numerology. Source tags in documents: verified, repository result,
  own derivation, unverified.
- `make install` then `make all` (about 4 minutes) verifies frozen inputs, runs 430 tests and
  regenerates every analysis. The September results were produced with Python 3.11; results
  added on 8–9 October (Gibrat, resource choice, catalogue, aftershocks) with Python 3.13 and the
  pinned packages. Other versions change the older files by at most about $4\times10^{-8}$
  relative. Do not commit such noise; restore those files with `git checkout -- <file>`.
- Raw inputs in `data/raw` are frozen and checksummed; analyses never download.
- The registering session had restricted source access. The 9 October local
  continuation acquired full public datasets using approved network access;
  acquisition receipts distinguish full files, samples and metadata-only reads.

## 7. Document map

| Status | Documents |
|---|---|
| Current | this file; [preregistered-tests.md](preregistered-tests.md); [glossary.md](glossary.md); [research-program.md](research-program.md); [resource-catalogue.md](resource-catalogue.md); [zeta-compilation.md](zeta-compilation.md); [references.md](references.md); [concept.md](concept.md) |
| Evidence and audit history | [evidence.md](evidence.md); [source-audit.md](source-audit.md); [lake results](lake-gyration-results-2026-10-09.md) |
| Unified manuscript and programme | [paper.md](paper.md) and `paper.pdf`; [research-brief.md](research-brief.md); [ongoing-research.md](ongoing-research.md) |
| Still applicable scope limits | [not-worth-pursuing.md](not-worth-pursuing.md) (cosmological, social and normative claims) |
| Raw provenance | [archive/2026-10-08/](archive/2026-10-08/README.md): full research dossiers, paper design (resource rule, gates, candidate datasets, falsification criteria), hostile referee report, fact-check, and the complete catalogue workflow output |
