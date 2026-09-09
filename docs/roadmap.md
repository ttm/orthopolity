# Roadmap

Open work, in priority order. Completed items stay listed with their commit so the record of what
was tried is visible alongside what is left.

## Open

### R4 — Extend coverage beyond freshwater fish
**Data. THE top priority, and currently blocked by an external outage.**

This is the only genuine out-of-sample test of the replication prohibition, which R7 has now
sharpened from a universal τ ≈ 0.257 to class-specific values: **τ ≈ 0.23 for freshwater, ≈ 0.38 for
marine**. It would also supply the fixed-taxon span variation that R5 needs.

**Access attempted 2026-09-09; every route exhausted.** Recorded so the search is not repeated:

| Route | Result |
|---|---|
| Zenodo records 11050013 / 11983391, API and web | HTTP 504 — and the Zenodo *homepage* is 504 too, so it is a full outage, not a bad identifier |
| `pssdb.net` portal (up, HTTP 200) | Product pages for every version link only back to Zenodo DOIs |
| NOAA COPEPOD, `copepodproject.org` | Link circularly back to `pssdb.net` |
| IFREMER Archimer `doc/00898/101001` | Article PDFs plus Zenodo DOIs; no data |
| `jessluo/PSSdb` on GitHub | **Checked exhaustively:** both branches (`main`, `v1.2`), the `v2024-04` release tag (0 assets), every file type without an extension filter, and commit history. The only data-shaped files are project metadata and standardiser configs — `project_list_all.xlsx`, `Data_source_table_PSSdb.xlsx`, taxonomy and elemental-quota tables. No NBSS slopes anywhere. The repository is the pipeline that *produces* the products; the products themselves go to Zenodo. |
| Wayback Machine | Record page and `Documentation_PSSdb_v2024-04.pdf` archived, but `PSSdb-BULK__v2024-04.zip` was never captured (CDX empty, direct fetch 404) |

The file to retrieve when Zenodo recovers is **`PSSdb-BULK__v2024-04.zip`**, whose Product 1b holds
the NBSS slope, intercept and R² per 1°×1° monthly cell — exactly the quantity needed.

Regenerating the products from the pipeline is not a realistic substitute: it pulls from three live
platforms (EcoTaxa, EcoPart and instrument-specific IFCB dashboards), needs credentials for some of
them, and processes ~92,000 IFCB samples, ~3,000 UVP profiles and ~2,400 scans. Waiting for Zenodo
is cheaper than reproducing 98,000 sample ingests to obtain a published table.

**A partial substitute was run and it failed** ([evidence.md §6.10](evidence.md)): across the three
published conventions in GLOSSAQUA, whose study sets are disjoint, freshwater τ varies by a factor
of two and two of three have E[s] ≠ 0. Method and study population are perfectly confounded there,
so it neither refutes the hypothesis nor supports it. **Diagnosed** ([evidence.md
§6.11](evidence.md)): the discrepancy is a labelling defect in the database, verified against
Perkins et al. (2018), whose reported quantity is the M–N slope rather than a normalised spectrum.
The subset is excluded as unusable. The prohibition remains genuinely untested.

GLOSSAQUA is 87% freshwater and 80% fish, so the strata that would test generality hardest are the
smallest. PSSdb (Dugenne et al. 2024) is the obvious next source; its Zenodo record was unreachable
when last tried.

### R5 — Resolve the span/taxon confound
**Blocked on power, not method. Attempted; see [evidence.md §6.9](evidence.md).**

Tested within taxon and nothing reached significance, with signs disagreeing: Fish ρ = −0.500
(p = 0.39, 5 studies), Macroinvertebrate ρ = −0.211 (p = 0.79, 4), Zooplankton ρ = +0.400
(p = 0.60, 4). That is a power failure rather than a null result. Needs studies that vary span at
fixed taxon — which is what R4 would supply.

*Original framing:*

Wider-spanning studies sit closer to −1 (study-level ρ = −0.549, p = 0.028, n = 16), but span is
partly a proxy for taxon. Stratifying span within taxon would separate the two.

**Runnable now, but underpowered.** Three taxa have at least four studies *and* genuine span
variation within them — Fish (5 studies, 0.9–3.0 decades), Macroinvertebrate (4, 3.0–5.3) and
Zooplankton (4, 2.6–9.9). That is enough to attempt the stratification and not enough to settle it
at four or five study blocks per taxon. Worth running for the honest answer, which may well be
"cannot separate at this sample size" — itself worth recording rather than leaving the confound
unexamined.

### R6 — Better-constrained ocean data
**Data.** No ocean verdict is possible while 21 of 23 bins have departures smaller than the
published reconstruction uncertainty ([evidence.md §5](evidence.md)).

## Done

| Item | Commit |
|---|---|
| Concept restated falsifiably; (O)/(S) separated; content condition | `1df6951` |
| External assessment merged; log-bin convention corrected | `ffb105d` |
| Pilot lab ported out of `.private/`; everything reproduces | `0f7420e` |
| CSN goodness-of-fit and equivalence testing | `fd5def1` |
| Independent tests preregistered before computing | `6df364f` |
| Preregistered tests run: ensemble yes, individual systems no | `a0c9973` |
| Ensemble result attacked from three directions and survived | `d57a707` |
| Meta-analysis estimators moved into tested `src/meta.py`; span test; §5.1 theory | `ab218dd` |
| **R1** — (O-ensemble) formalised, latent-shape test, quantitative prohibitions | `1494a89` |
| **R2** — discrete Gutenberg–Richter goodness of fit; GR *not* ruled out at M ≥ 5.5 | `1098b7c` |
| **R3** — packaging (`pyproject.toml`) and one-command reproduction (`Makefile`) | `1098b7c` |
| Stale post-R1–R3 claims corrected; invalid earthquake lognormal comparison withdrawn | `aa45046` |
| **R7** — heavy tail is largely a class mixture; Gaussian adequate within freshwater | `6ee43fc` |
| Failed replication diagnosed as a database labelling defect (Perkins verified) | `9138a49` |
| **R8** — conventions of Arranz (2022) and Gaedke (1993) confirmed from the papers | `a3914ab` |
| **R9** — dispersion decomposed: ~92% between ecosystems, ≤8% temporal | `eca3855` |
| Manuscript drafted ([docs/paper.md](paper.md)) | *this commit* |


### R10 — A study with many sites *and* repeat visits
**Data. The clean version of R9.**

R9 bounds the temporal component using two different studies in two different ecosystems, which
requires assuming Lake Constance's temporal variability represents Ontario lakes. A single study
measuring many sites with repeat visits and reported errors would give a real partition instead of
bounds. Nothing in the primary subset is large enough: the two with both levels have n = 27 and
n = 24. This is a data requirement, not a method one.

### R11 — Finish the manuscript
**Writing. [docs/paper.md](paper.md) is a complete draft; these remain.**

- Format references for the target venue and verify every one against the original.
- Decide authorship, funding and acknowledgements.
- Produce figures: the four existing PNGs cover the analyses but were made as diagnostics, not as
  publication figures.
- Choose the venue. The draft is orthopolity-led, which suits PLOS ONE (negative results welcome) or
  Physica A. Methods in Ecology and Evolution would need the §4.6 label finding moved to the front.
- Consider extracting §4.6 as a short note *after* the main paper appears, citing it. Splitting it
  out beforehand would be salami-slicing: one dataset, one codebase, one set of 1,300 spectra.
