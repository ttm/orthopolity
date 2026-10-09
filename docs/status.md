# Project status and handoff

Last updated 9 October 2026. **Read this first in a new session.** It records what the authors
intend, what has been done and found, the current assessment, and the next steps, with pointers
to the files that hold the details.

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
| 8–9 Oct 2026 | Four pre-registered tests ("go for them", lead author) | [preregistered-tests.md](preregistered-tests.md): aftershock test run (inconclusive; moment reading excluded); three tests ready to run where their data are reachable |

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

## 4. Current assessment

Rigor and reproducibility are strong. As a scientific contribution the work is a promising
framework and agenda, not yet a result:

- The mechanisms and most rules are published (proportional growth; hyperscaling and box counting;
  Kolmogorov-type flux closures). The new element is the unifying reading and its classification.
- Agreement in the catalogue mostly restates known derivations; new readings in biology and social
  systems grade suggestive; 25 of 59 exponents are unverified.
- One pre-registered test has been run (aftershock productivity). Its registered verdict is
  inconclusive: it excludes the seismic-moment reading, and also, narrowly, the self-similar area
  reading, with a strong dependence on the aftershock window. Three further tests are registered
  and validated but await data. The decisive evidence would still be predictions fixed before
  the data, with rivals, passing in several systems.
- The only manuscript, [paper.md](paper.md), still has the critical framing of September and does
  not reflect the authors' direction or the catalogue.

## 5. Next steps, in priority order

1. **Run the three registered tests** where their data are reachable (this cloud session could
   reach only GitHub and PyPI). Step-by-step instructions, including what to record before running,
   are in [preregistered-tests.md](preregistered-tests.md):
   - flare ribbon areas (RibbonDB): α = 2 against 7/3;
   - lake radius of gyration (HydroLAKES): ζ_R = 2;
   - b against hypocentre dimension (relocated regional catalogue with clusters): b = D2/2 against 1.

   Do not change hypotheses, estimators or decision rules; any change before data access goes in
   an `amendments` entry with its reason, as done for the lake and volumetric tests.
2. **Follow up the aftershock test** with windows from finite-fault rupture extents, registered anew
   and disclosing the present result; it is then a replication, not a blind test.
3. **Verify the catalogue.** Check the 25 unverified and 6 corrected exponents in
   [configs/resource_catalogue.json](../configs/resource_catalogue.json) against primary sources,
   update `exponent_check`, and rerun `make catalogue`. Full-text priority checks are needed for
   Reed and Hughes 2002, Saichev et al. 2010, Aschwanden 2014 and 2025, Frank 2016 and 2019, and
   Gabaix 1999 before any novelty statement.
4. **Agree the paper's framing with the authors**, in light of the test outcomes: (a) a synthesis
   paper presenting the orthopolic reading, rules, chance baseline, predictions and test results;
   (b) a Registered Report of the multi-domain growth test in
   [research-program.md](research-program.md); (c) (a) followed by (b). Keep exploration and
   confirmation separate.
5. **Rewrite the manuscript** for the chosen framing, keeping the accounting and measure sections of
   [paper.md](paper.md); regenerate `docs/paper.pdf` with `make paper`.
6. **Submission requirements** still open from [roadmap.md](roadmap.md): authorship and
   declarations, data notices and licences (GLOSSAQUA licence conflict), venue formatting.

## 6. Conventions and environment

- Terminology and measures: [CLAUDE.md](../CLAUDE.md), [glossary.md](glossary.md).
- Evidence standard: an exponent match counts only if the resource and inputs were fixed before the
  exponent was examined and the reading passes a second, different prediction. Grades:
  derived, motivated, suggestive, numerology. Source tags in documents: verified, repository result,
  own derivation, unverified.
- `make install` then `make all` (about 4 minutes) verifies frozen inputs, runs 96 tests and
  regenerates every analysis. The September results were produced with Python 3.11; results
  added on 8–9 October (Gibrat, resource choice, catalogue, aftershocks) with Python 3.13 and the
  pinned packages. Other versions change the older files by at most about $4\times10^{-8}$
  relative. Do not commit such noise; restore those files with `git checkout -- <file>`.
- Raw inputs in `data/raw` are frozen and checksummed; analyses never download.
- In cloud sessions, web search is limited (about 200 queries per turn, shared by subagents) and
  full-text fetches from arXiv, DOI and PMC hosts were blocked. Verification relied on abstracts and
  search extracts; record that in any value's check field.

## 7. Document map

| Status | Documents |
|---|---|
| Current | this file; [preregistered-tests.md](preregistered-tests.md); [glossary.md](glossary.md); [research-program.md](research-program.md); [resource-catalogue.md](resource-catalogue.md); [zeta-compilation.md](zeta-compilation.md); [references.md](references.md); [concept.md](concept.md) |
| Accurate for the September analyses | [evidence.md](evidence.md); [source-audit.md](source-audit.md) |
| Earlier framing, to be revised | [paper.md](paper.md) and `paper.pdf`; [value.md](value.md); [criticism.md](criticism.md); [roadmap.md](roadmap.md) (next steps now here) |
| Still applicable scope limits | [not-worth-pursuing.md](not-worth-pursuing.md) (cosmological, social and normative claims) |
| Raw provenance | [archive/2026-10-08/](archive/2026-10-08/README.md): full research dossiers, paper design (resource rule, gates, candidate datasets, falsification criteria), hostile referee report, fact-check, and the complete catalogue workflow output |
