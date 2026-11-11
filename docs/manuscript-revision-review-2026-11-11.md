# Review of the natural-law and cosmological revision

11 November 2026. Implements the author-approved
[roadmap](manuscript-roadmap-2026-11-10.md), starting from `3bb224d`.
This review extends the [10 November empirical claim map](manuscript-evidence-review-2026-11-10.md).
It does not replace any retained forecast, result or failure.

## What changed and why

The main article now states the **proposed natural law** directly and leads
with a finite log-orthopolic picture. Count times mean cost gives class resource;
only then do densities, reference measures and inverse inference enter. The
accounting proof is shorter in the main article and remains complete in S1.
Section 4 now emphasizes what each comparison establishes, with complete numbers
and competing predictions retained in S5. No study verdict changes.

The orthopolic umbrella distinguishes exact accounting, neutral mechanisms,
independently predicted constraints and exploratory resource interpretations.
Gaussian aggregation remains complementary; mode coordinates and mean energy
illustrate coexistence under mode-counting measure, neither size measure.

Supporting S6 and the companion [cosmic report](cosmological-extension.md)
develop a new theoretical conjecture. This revision adds literature interpretation
and conditional model consequences, not a newly executed empirical study.

## New claim map

| Claim | Basis and reference measure | Status and boundary |
|---|---|---|
| The main statement is a proposed natural law | General physical claim with independently specified comparison measure | Exact realizations support particular conditions; universality remains proposed |
| Four classes hold equal resource with unequal counts | Finite log-orthopolic grid; sizes/costs 1,2,4,8 and counts 8,4,2,1 | Exact illustration: each product 8, total 32; no empirical inputs |
| Power-law cost cancels inverse-cost frequency | Density relative to the declared measure; normalized density uses a rescaled constant | Log-orthopolic linear-size exponent is cost exponent plus one; linear-orthopolic exponent equals cost exponent |
| Complete inventories give an unavoidable inverse count--mean relation | Nonnegative additive resource; complete partition, neither size-allocation measure | Conservation alone does not specify shares among coexisting classes |
| A cosmic stellar inventory differs from a richness distribution | Predefined galaxy grouping versus log-orthopolic stellar-number allocation | The inventory identity does not imply the separate prediction k² phi(k)=C |
| Neutral mass allocation predicts a mass-function exponent of minus two | Mass resource and logarithmic mass intervals in a finite, disjoint inventory at a specified epoch and volume | Conditional equation; stellar mass is not a direct stellar count |
| Published cosmic distributions supply signs and departures | COSMOS2015, GAMA, stellar birth masses and Aquarius simulations; logarithmic mass measure | Retrospective interpretations of published slopes, with uncertainties, cutoffs and population differences retained |
| Constant mass current and constant drift produce neutral stored mass | Stationary source-free local transport in log host mass; full declared host mass is tracked | Exact within the model; merger jumps, diffuse sources, diffusion and stellar evolution can invalidate the assumptions |
| Independent current and drift predict a second environment's abundance | Positive current/drift and finite mass interval, with comoving-volume convention | Proposed amplitude/count transfer; inputs derived from the target profile would be circular |

The new sources are linked in S6 and listed in the supplement and reference
catalogue. The standard spatial cosmological principle and cosmological constant
Lambda are explicitly distinguished from the allocation conjecture.

## Review and verification

Independent conceptual review checked the change-of-measure factor, normalized
density constant, inverse-resource transfer equation, additive-resource premise,
cosmic residence-time interpretation, tracer/host-mass distinction and amplitude
prediction. The recommended precision changes were incorporated. Primary-source
review checked the published astronomical slopes and their qualifications.

The explanatory renderer uses no empirical inputs. Its integer arithmetic and
equal logarithmic spacing were checked independently; PNG and SVG are identical
across three renders in the existing Python 3.11 environment.

The condensed-study review also restored job **shares** (rather than an absolute
job-count claim), the membrane error denominator, and the chemostat bound's
fixed-opportunity premise. Five references no longer cited in the shortened
main text remain in the supporting bibliography.

Verification completed:

- Eight tests pass: `python -m unittest tests.test_md2tex tests.test_terminology`.
  The separate document check includes new untracked Markdown and checks links,
  anchors and paired display delimiters.
- `make registry-verify` passes **46 runs / 1,168 references**. No registry entry
  was added; frozen data, configuration, source snapshots and numerical results
  are unchanged. Supporting S1--S5 compare byte-for-byte with baseline; S6
  matches the companion cosmic report after its heading renumbering.
- `make -B paper PY=build/main-venv-2026-10-09/bin/python` succeeds twice with
  identical PDFs and no TeX warnings, overfull or underfull boxes in either
  pass of the repeat build. Main is **13 pages**, supporting is **77 pages**.
- All 90 pages were inspected through rendered contact sheets; the new
  illustration, main equations and revised comparisons, and cosmic pages
  71--73 received full-size inspection. All 22 figures have their captions on
  the image page. There are no blank pages or out-of-page text spans.
- `git diff --check` passes. The successful 10 November full `make all` remains
  the baseline; it was not rerun for this editorial/theoretical revision.

The builds use the Makefile's fixed timestamps from the last committed source;
these hashes describe the current working-tree PDFs. Committing manuscript
sources will change the timestamp basis for a subsequent rebuild.

| Artifact | SHA-256 |
|---|---|
| `docs/paper.pdf` | `ede91ba0b1b677d99b89eb98f5dffac1c59741cdfebce31c5e0d857b47ee5523` |
| `docs/supporting-material.pdf` | `84fdf152607b3e19e7b9bc46b5cfe2c19bd6ec6979b341f645840a283c01006e` |

Build logs are `build/law-cosmos-paper-final-2026-11-11.log` and
`build/law-cosmos-paper-repeat-2026-11-11.log`. Raster review, bounds/caption
checks and repeat hashes are in `build/law-cosmos-pdf-qa-2026-11-11/`.
The source/link check is `build/law-cosmos-doc-check-2026-11-11.json`;
registry output is `build/law-cosmos-registry-2026-11-11.log`. These scratch
artifacts document this local verification; the manuscript, retained figure
source and standard Make targets are the reproducible deliverables.

## Remaining scientific step

Qualify one public source with independent transport or assembly inputs and a
separate abundance target before freezing a cosmic test. The current literature
examples have already been seen and cannot become blind confirmation. Existing
source-qualification stops remain in force; author declarations, permissions
and venue work from the preceding review remain separate submission tasks.
