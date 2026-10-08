# Project status and handoff

Last updated 8 October 2026. **Read this first in a new session.** It records what the authors
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

Literature compilation of 49 exponents: [zeta-compilation.md](zeta-compilation.md). Stocks that
grow proportionally sit near ζ = 1; event catalogues and cascades mostly below 1.

## 4. Current assessment

Rigor and reproducibility are strong. As a scientific contribution the work is a promising
framework and agenda, not yet a result:

- The mechanisms and most rules are published (proportional growth; hyperscaling and box counting;
  Kolmogorov-type flux closures). The new element is the unifying reading and its classification.
- Agreement in the catalogue mostly restates known derivations; new readings in biology and social
  systems grade suggestive; 25 of 59 exponents are unverified.
- No pre-registered test has been run. The decisive evidence would be predictions fixed before the
  data, with rivals, passing in several systems.
- The only manuscript, [paper.md](paper.md), still has the critical framing of September and does
  not reflect the authors' direction or the catalogue.

## 5. Next steps, in priority order

1. **Verify the catalogue.** Check the 25 unverified and 6 corrected exponents in
   [configs/resource_catalogue.json](../configs/resource_catalogue.json) against primary sources,
   update the `exponent_check` fields, and rerun `make catalogue`. Full-text priority checks are
   also needed for Reed and Hughes 2002, Saichev et al. 2010, Aschwanden 2014 and 2025, Frank 2016
   and 2019, and Gabaix 1999 before any novelty statement.
2. **Pre-register two or three discriminating predictions** from
   [resource-catalogue.md](resource-catalogue.md#predictions-to-test-before-looking), freezing the
   resource, measure, inputs, estimator and rival prediction in `configs/prereg_<date>.json` and
   committing it before downloading outcome data. Candidates, with data to confirm:
   - *Solar flare ribbon areas*: log-orthopolic area predicts α = 2, the scale-free probability
     conjecture 7/3. A ribbon database exists (Kazachenko et al. 2017, about 3,000 flares; verify
     access, and whether its area distribution is already published, which would weaken the test).
   - *Lake radius of gyration*: $N(>L)\propto L^{-2}$ independent of fractal dimension, from
     HydroLAKES polygons (verify licence).
   - *Seismicity in volumetric support*: territory in 3D predicts b = 1.5 from an independently
     measured hypocentre dimension. Prior art is mixed (Aki 1981 b = D/2; Hirata 1989 found a
     negative correlation), and high b in volcanic swarms is already reported, so define the support
     dimension before looking.
   - *Aftershock productivity versus rupture area*, from a full-magnitude ComCat download.
3. **Agree the paper's framing with the authors.** Options: (a) a synthesis paper presenting the
   orthopolic reading, the rules, the chance baseline and the predictions; (b) a Registered Report
   of the multi-domain test in [research-program.md](research-program.md); (c) (a) followed by (b).
   Avoid presenting post hoc readings as confirmation; keep exploration and confirmation separate.
4. **Rewrite the manuscript** for the chosen framing, keeping the accounting and measure sections of
   [paper.md](paper.md) and the reproducibility material; regenerate `docs/paper.pdf` with
   `make paper`.
5. **Submission requirements** still open from [roadmap.md](roadmap.md): authorship and
   declarations, data notices and licences (GLOSSAQUA licence conflict), venue formatting.

## 6. Conventions and environment

- Terminology and measures: [CLAUDE.md](../CLAUDE.md), [glossary.md](glossary.md).
- Evidence standard: an exponent match counts only if the resource and inputs were fixed before the
  exponent was examined and the reading passes a second, different prediction. Grades:
  derived, motivated, suggestive, numerology. Source tags in documents: verified, repository result,
  own derivation, unverified.
- `make install` then `make all` (about 3 minutes) verifies frozen inputs, runs 89 tests and
  regenerates every analysis. Committed results were produced with Python 3.11; other versions
  change them by at most about $4\times10^{-8}$ relative. Do not commit such noise; restore with
  `git checkout -- results/`.
- Raw inputs in `data/raw` are frozen and checksummed; analyses never download.
- In cloud sessions, web search is limited (about 200 queries per turn, shared by subagents) and
  full-text fetches from arXiv, DOI and PMC hosts were blocked. Verification relied on abstracts and
  search extracts; record that in any value's check field.

## 7. Document map

| Status | Documents |
|---|---|
| Current | this file; [glossary.md](glossary.md); [research-program.md](research-program.md); [resource-catalogue.md](resource-catalogue.md); [zeta-compilation.md](zeta-compilation.md); [references.md](references.md); [concept.md](concept.md) |
| Accurate for the September analyses | [evidence.md](evidence.md); [source-audit.md](source-audit.md) |
| Earlier framing, to be revised | [paper.md](paper.md) and `paper.pdf`; [value.md](value.md); [criticism.md](criticism.md); [roadmap.md](roadmap.md) (next steps now here) |
| Still applicable scope limits | [not-worth-pursuing.md](not-worth-pursuing.md) (cosmological, social and normative claims) |
| Raw provenance | [archive/2026-10-08/](archive/2026-10-08/README.md): full research dossiers, paper design (resource rule, gates, candidate datasets, falsification criteria), hostile referee report, fact-check, and the complete catalogue workflow output |
