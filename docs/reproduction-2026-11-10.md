# Full replay and manuscript evidence review

10 November 2026. Work on `main`, starting from **1704e495e14260a43fd27b2655f18dc79dad40fc**.
The complete `make all` target now passes in the existing Python 3.11 environment.
This record distinguishes numerical replay from byte identity; no frozen scientific
input, analysis, forecast, result or registry entry was replaced.

## BioMe replay-policy amendment

The [26 October failure](reproduction-2026-10-26.md) was reproduced before repair.
The frozen diagnostic at `59bd2b7` regenerates with **16,274 differing floating
values**, maximum absolute difference **2.2737367544323206e-13**, and unchanged
structure, metadata and types. The independent verifier still passes all
**26,799 comparisons**, with maximum absolute difference **4.547473508864641e-13**.
Its report differs from the archived report only in the hash binding it to the
regenerated diagnostic. The inventory and PNG reproduce byte-for-byte.

The observed differences are consistent with floating-point implementation
variation. This run used Python **3.11.6**, NumPy **2.3.5**, SciPy **1.17.0**,
Matplotlib **3.10.8**, and arm64 macOS with NumPy's Accelerate backend. No controlled
backend comparison was performed, so a particular library is not established
as the cause.

The new [replay checker](../experiments/check_biome_replay.py) is separate from
the frozen analysis and its independent verifier. It compares **26,404 computed
floating results** using the verifier's existing `math.isclose` tolerances:
relative **1e-11**, absolute **1e-10**, with the maximum of the two bounds.
It requires exact JSON structure and types, counts, missing values, flags,
text, time coordinates, pore labels, source inventory, reference measure and
freeze metadata. Nonfinite values and duplicate JSON fields are rejected.
Each verification report must pass, keep the original tolerances, and carry
the SHA-256 of its own diagnostic. All other report fields are exact except
its computed maximum numerical error, which uses the same numerical comparison.

The Makefile runs the original diagnostic and independent verifier before the
new comparison. It retains exact-byte checks for the inventory and figure.
`replay-comparison.json` records both hashes, numerical differences and separate
byte-equality flags. Here both JSON byte-equality flags are **false**: this is
successful numerical replay, not restoration of the original byte-level claim.

This is an explicitly retrospective amendment to the replay policy described
in the frozen protocol. It changes neither that historical protocol nor the
original empirical decision rules. BioMe remains source qualification with
unresolved physical measurement limitations, using physical chamber volume,
**neither log-orthopolic nor linear-orthopolic size allocation**.

| Diagnostic | SHA-256 |
| --- | --- |
| Retained | `97e421f857a51b01bb28df30e3b97fb6a282137ced9d30efdc69e045422b13e6` |
| Regenerated | `1ed322e5fea8d41d62c1b1345d2739dd708373fd159e352c27f71f444e79429d` |

Nine new synthetic regression tests exercise accepted roundoff, strict design
metadata, type/count/null preservation, missing fields, nonfinite and substantive
changes, hash mismatches, changed verifier policy/success, duplicate keys, and
the maximum-versus-sum tolerance distinction. An independent code review found
no substantive issue and separately reran the nine tests successfully.

## Completed verification

```sh
PATH=/usr/bin:/bin:/usr/sbin:/sbin:$PATH MPLCONFIGDIR=build/matplotlib \
  make all PY=build/main-venv-2026-10-09/bin/python \
  STUDY_OUTPUT_ROOT=build/reproductions-2026-11-10

PATH=/usr/bin:/bin:/usr/sbin:/sbin:$PATH \
  make registry-verify PY=build/main-venv-2026-10-09/bin/python
```

- Full `make all` exits successfully, including frozen-source checks,
  **711 Python tests**, **27 JavaScript model tests**, both browser-script
  syntax checks, legacy analyses, topology/storage qualifications, BioMe,
  circuit and wall transfers, fragmentation checks and whole-object assembly.
- Registry verification passes with **46 runs / 1,168 file references**.
- BioMe inventory/PNG, circuit and wall artifacts, and whole-object forecast,
  independent audit, simulation verification and both figure formats satisfy
  their retained byte comparisons.
- The full test log retains pre-existing `ResourceWarning` messages about
  unclosed CSV reads in the phosphorus verifier; no test fails. Frozen verifier
  code was not edited as part of this repair.

`make all` covers its declared target graph; later studies also retain separate
named replay targets. The registry audit verifies all retained referenced bytes
and lineage, not a new empirical run of every registered study.

Legacy regeneration changed four JSON files only in floating values:

| File | Differing floats | Maximum absolute difference |
| --- | ---: | ---: |
| `aftershock_productivity.json` | 28 | 4.187520874499029e-8 |
| `gibrat.json` | 5 | 2.220446049250313e-16 |
| `gof.json` | 4 | 1.1102230246251565e-16 |
| `independent.json` | 22 | 2.0816681711721685e-17 |

There are no structural, type, integer, Boolean, string or other nonnumeric
changes in those JSON files. Their regenerated copies, associated changed
figures, complete binary diff and hash/numerical audit are retained under
`build/regeneration-noise-2026-11-10/`. All eight changed legacy result artifacts
were restored to their starting bytes. The final scientific result/input
directories have no diff.

Logs are retained in `build/make-all-2026-11-10.log`,
`build/biome-replay-before-2026-11-10.log`,
`build/biome-replay-after-2026-11-10.log`, and
`build/registry-verify-2026-11-10.log`. The new BioMe audit is at
`build/reproductions-2026-11-10/biome-stock/replay-comparison.json`.

## Manuscript and scientific outcome

The [claim-to-evidence review](manuscript-evidence-review-2026-11-10.md)
checks main and supporting claims against retained studies, including stronger
comparators and failed predictions. Corrections identify the runtime comparator
as linear cost, narrow the Dunaliella ranking and raw-OD statements, and update
the supplement's synthesis and registry guide for later transfers. The title,
general-law ambition, reference measures and all frozen numerical findings remain.

The [storage readiness decision](storage-intervention-readiness-2026-11-10.md)
specifies independent inputs, target partition, divergent forecasts, uncertainty
and qualification requirements, and precise source-reopening conditions. No
retained archive supplies the complete closed storage intervention and coupling
control. Its empirical test remains unrun; the review adds no new observations
or confirmations and does not reopen the completed bounded searches.

Both manuscripts were reviewed from the working tree, then rebuilt with the
manuscript sources fixed at commit **632f869**, using the Makefile's
last-source-commit timestamps:

```sh
PATH=/usr/bin:/bin:/usr/sbin:/sbin:$PATH \
  make -W docs/paper.md -W docs/supporting-material.md paper \
  PY=build/main-venv-2026-10-09/bin/python
```

The final **12-page article and 74-page supplement** are byte-identical across
two forced builds from **632f869**, with no TeX warnings or overfull/underfull boxes in either
pass. All pages were visually reviewed through contact sheets; changed main
page 8 and supporting pages 1, 31–33, 35 and 50 were inspected at full size, along
with the corrected figures S9, S14 and S15 on pages 42, 57 and 59. Every one
of the 20 supplement figures now has its caption on the same page as its
image. No clipped or overlapping content, blank pages or page-flow defect
remains. Text-bound checks find no out-of-page spans. The repeated final build
matches the committed-source PDF hashes. Raster comparisons of all 86 pages
find no pixel differences between these PDFs and the visually inspected
working-tree PDFs; the source-commit timestamp change preserves the layout.

| PDF | SHA-256 |
| --- | --- |
| `docs/paper.pdf` | `a5174b2df6a2ccce077be0746af0a418e4fc831d01fafe095317cff38d753798` |
| `docs/supporting-material.pdf` | `e8c3a2b92e6c0f639bd893e3f005d6ffbfe15434310f84ad63987ad407267d04` |

Reviewed PDF images and working-tree build records are in
`build/review-pdf-qa-2026-11-10/final/`; the committed-source byte/pixel checks
are in `build/review-pdf-qa-2026-11-10/committed-first-build.json` and
`committed-second-build.json`. Build logs are
`build/paper-committed-build-2026-11-10.log` and
`build/paper-committed-rebuild-2026-11-10.log`. Seven manuscript-converter tests and
the terminology test pass after the source corrections; a separate check
covers terminology in the new untracked files. All **435 local links** in
the eight changed/new Markdown documents resolve, and `git diff --check`
passes. These checks do not refresh external source URLs or licensing terms.
