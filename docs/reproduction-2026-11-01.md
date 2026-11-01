# Whole-object assembly: verification and manuscript record

1 November 2026. Forecast commit **895e774** was pushed before the five
study-budget Gillespie scenarios. Integration commit **d0b9cdf** adds all
results, the analytic figure and main 3.1/supporting S3.10. The model conserves
integer material through assembly and breakup of masses 1, 2 and 4.
Its comparison is **log-orthopolic in physical object mass**, using fixed
equal-width logarithmic bins. No empirical data or registry entries are added.

## Numerical and repository verification

Using Python 3.11 from `build/main-venv-2026-10-09/bin/python`:

```sh
PATH=/usr/bin:/bin:/usr/sbin:/sbin:$PATH make test registry-verify \
  PY=build/main-venv-2026-10-09/bin/python
PATH=/usr/bin:/bin:/usr/sbin:/sbin:$PATH make whole-object-assembly \
  PY=build/main-venv-2026-10-09/bin/python
```

- **702 unit tests pass**, including ten small independently solvable kinetic
  tests. The terminology check passes again after staging the integration.
- Registry remains **46 runs / 1,168 references**; all references verify.
- Analytic forecasts use exact rational stationary weights. A separate script
  imports neither the kinetic model nor the forecast driver and reconstructs
  scalar reaction rates, state enumeration, SVD stationary solutions, transient
  probabilities, moments, conservation, finite-budget formulas and clock scaling.
  All **18,547 comparisons** pass within **1.21e-13**, below tolerance 1e-11.
- The simulation stage checks **20,480 independent trajectories and 894,172
  integer-conserving jumps**. All five frozen scenarios pass the simultaneous
  mean bound. Maximum mean-share error **0.00380162** is below **0.03547417**;
  the Hoeffding union bound covers 15 means with family error at most 0.001.
  Whole-state total variation is retained as a descriptive diagnostic.
- The independent stationary linear solve agrees within **1.67e-15**;
  detailed-balance error is at most **5.56e-17**. Both clock identities have
  zero residual in the retained computations. Finite-time intervention checks
  use transient predictions, not the new stationary distribution.
- Forecast, independent-audit and simulation JSON replay byte-for-byte, as do
  the analytic PNG and SVG. Configuration and model/driver source hashes are
  embedded in the forecasts and checked before simulation.
- Relative links, sequential supporting figure captions S1--S20 and
  `git diff --check` pass. Pre-existing untracked files remain untouched.

The matrix and Gillespie algorithms share a propensity function; their agreement
alone is not an independent rate-model check. The separate scalar-rate audit
supplies that check. Independent scientific and code reviews preceded forecast
freezing; the final prose retains the distinction between finite-budget means,
large-budget asymptotics, persistent snapshot variance and empirical evidence.

Full `make all` was not rerun. Its older BioMe numerical byte-comparison
limitation remains unresolved, as documented in the
[26 October record](reproduction-2026-10-26.md). The new offline target is included
in `make all` and was run separately. Historical analysis artifacts were not
regenerated or changed.

## Manuscripts

Both PDFs were forcibly built twice from source commit **d0b9cdf**, using the
Makefile's last-source-commit timestamps:

```sh
PATH=/usr/bin:/bin:/usr/sbin:/sbin:$PATH make \
  -W docs/paper.md -W docs/supporting-material.md paper \
  PY=build/main-venv-2026-10-09/bin/python
```

The **12-page main article and 72-page supplement** are byte-identical across
both builds, with no warnings or overfull/underfull boxes in either TeX pass.
All-page contact sheets, full-size main pages 4--5, supporting pages 26--28
and the standalone analytic figure were visually inspected. Equations, table,
figure labels, captions and page transitions are legible without clipping or
overlap. Second-build hashes match the inspected PDFs.

| PDF | SHA-256 |
|---|---|
| `docs/paper.pdf` | `64c29153a826f541984a8717053a7d7c26b056f2e0c6690200a2c36d07b163b3` |
| `docs/supporting-material.pdf` | `9eb983cb110a180c6590cde00c115be48d6a80d089d8b8f02800c8f9c835be61` |

The title and general-law ambition remain unchanged. The advance is a specified
whole-object mechanism, its rate-change forecast and kinetic/snapshot boundaries,
using established stationary-distribution theory. It is not a new empirical
confirmation or a claim that ordinary mass action generally yields orthopolity.
