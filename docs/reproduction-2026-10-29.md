# Fragmentation boundary: verification record

29 October 2026. Source commit **dcb4ca3** closes the three-archive search and
adds the analytic uniform-cut boundary to main section 5/supporting S3.8.
No numerical experimental worksheet outcomes were decoded and no empirical
registry entry was added. The generated uniform cuts are mathematical checks.

## Source and mathematical checks

Using Python 3.11 from `build/main-venv-2026-10-09/bin/python`:

```sh
PATH=/usr/bin:/bin:/usr/sbin:/sbin:$PATH make test registry-verify \
  fragmentation-sources fragmentation-boundary \
  PY=build/main-venv-2026-10-09/bin/python
```

- **692 unit tests pass**; the terminology check also passes after staging the
  new files. Local documentation links and `git diff --check` pass.
- Registry verifies **46 runs / 1,168 references**, with prior entries unchanged.
- Source replay verifies **13 retained files**, four provider checksums, four
  workbooks/five sheet schemas and a CRC-checked member from a 282-entry ZIP
  directory. The complete large Figshare archive hash is not independently verified.
- The analytic check covers 12 quadrature cases, exact rational arithmetic,
  4,096 generated mass-conserving partitions, 60 independent LP cases for each
  completion formula and 11 invalid-input checks. Maximum normalized quadrature
  error is **1.11e-16**; missing-mass and TV comparisons agree within
  **5.68e-14** and **1.11e-16**. Its JSON replays byte-for-byte against
  `results/fragmentation-boundary-2026-10-28/analytic.json`.
- Independent mathematical and source/provenance reviews found no remaining
  blockers. The ensemble normalization, positive-mass domain and original
  budget qualification are explicit.

Full `make all` was not rerun. Its previously documented older BioMe exact-byte
comparison limitation remains unresolved; see the [26 October record](reproduction-2026-10-26.md).
New targets are included in `make all` and were executed separately. Historical
analysis artifacts were not regenerated or changed.

## Manuscripts

Both manuscripts were forcibly rebuilt twice from **dcb4ca3**, using their last
source-commit timestamps via the existing Makefile:

```sh
PATH=/usr/bin:/bin:/usr/sbin:/sbin:$PATH make \
  -W docs/paper.md -W docs/supporting-material.md paper \
  PY=build/main-venv-2026-10-09/bin/python
```

Both builds have identical bytes and no overfull/underfull boxes or TeX warnings.
The main article remains **12 pages** after condensing the discussion; the
supplement is **69 pages**. All-page contact sheets and full-size main page 10
and supporting pages 23--24 were visually inspected. Equations, the new table,
page breaks, figures and references are legible without clipping or overlap.
The second-build hashes match those of the inspected PDFs.

| PDF | SHA-256 |
|---|---|
| `docs/paper.pdf` | `64da5a61853adfb287acf380fd74d5ba5a3d906524a932694c2b3f11b2097adc` |
| `docs/supporting-material.pdf` | `e998cdb234c1a8953ed2c3bb0ea85e3ad32a583528ce8bf838d7dbe2175f9156` |

The title and general-law ambition are preserved. The new contribution is a
specified analytic applicability boundary, not empirical establishment of a
common log-orthopolic regime in the audited rock experiments.
