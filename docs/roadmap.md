# Roadmap

Open work, in priority order. Completed items stay listed with their commit so the record of what
was tried is visible alongside what is left.

## Open

### R7 — Is the heavy tail a mixture over classes?
**Analysis. Follows directly from [evidence.md §6.5](evidence.md).**

The latent slope distribution is heavier-tailed than the maximum-entropy two-moment form
(Student t with ν = 8 beats Gaussian by ΔAIC = −7.4; excess kurtosis +1.13). The natural
explanation is that pooling freshwater with marine, and fish with plankton, mixes subgroups with
different τ — and a mixture of Gaussians with unequal variances is heavy-tailed. Estimating τ
separately per stratum tests this. If it holds, τ is confirmed as a *class* property and the
heavy tail stops being an anomaly; if a single stratum is still heavy-tailed, there is real
structure beyond two moments to explain.

### R2 — Discrete goodness-of-fit for the earthquake catalogue
**Code. Closes a flagged placeholder.**

The continuous KS test is invalid on magnitudes rounded to 0.1 — the energy proxy takes 32 distinct
values across 6,639 events, and the ties inflate the statistic on their own
([evidence.md §4](evidence.md)). The Clauset–Shalizi–Newman discrete procedure is needed before
that row is a result rather than a placeholder. Until then it must not be cited as evidence.

### R3 — Packaging and one-command reproduction
**Code. Housekeeping; a precondition for anyone else using this.**

Currently four scripts run by hand with `PYTHONPATH=src`. Needs a `pyproject.toml`, an importable
package, and a single entry point that runs fetch → tests → all analyses. Note that JOSS requires
more than six months of public development history, so a software paper stays out of scope for now
([not-worth-pursuing.md B3](not-worth-pursuing.md)).

### R4 — Extend coverage beyond freshwater fish
**Data. Determines how far the one positive result generalises.**

GLOSSAQUA is 87% freshwater and 80% fish, so the strata that would test generality hardest are the
smallest. PSSdb (Dugenne et al. 2024) is the obvious next source; its Zenodo record was unreachable
when last tried.

### R5 — Resolve the span/taxon confound
**Analysis. Follows directly from [evidence.md §6.4](evidence.md).**

Wider-spanning studies sit closer to −1 (study-level ρ = −0.549, p = 0.028, n = 16), but span is
partly a proxy for taxon. Stratifying span within taxon, or finding studies that vary span at fixed
taxon, would separate the two.

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
| **R1** — (O-ensemble) formalised, latent-shape test, quantitative prohibitions | *this commit* |
