# Validation of the public wall transfer and revised supplement

26 October 2026. The wall-transfer source/result commit is **942f5b6**.
The forecast design **a18fbec** and numerical forecast **0db6966** were pushed
before target interior release. The new result is fully reproduced; one older
byte-level check prevents calling the complete `make all` run successful here.

## Passed

- **692 tests**, including 12 synthetic tests for the new transfer, target
  access partition, qualification, bounds, competing corrections and independent
  verifier. No experimental target data enter those synthetic tests.
- `make hotbox-transfer`: forecast, independent arithmetic verification, input
  source audit, complete result and result source audit reproduce byte-for-byte.
- `make rlc-boundary`: the preceding circuit study also reproduces byte-for-byte.
- Registry audit: **46 runs / 1,168 references**, with earlier entries preserved.
- Supplement: **67 pages**, no LaTeX warnings or out-of-page text; all page
  contact sheets and the changed section/reference pages visually inspected.
  Two forced builds are byte-identical, SHA-256
  `0a047abca34684c50fbf4b70579e883f0df4a5485ef902b3fb22a21510374b83`.
- The **12-page main article** remains byte-identical, SHA-256
  `975836de0941df45363d090cb1f32f2ff5011148d6633345e5fa8c9fcb7aeb93`.

## Full replay limitation

`make all` passes the complete test suite and reaches the older BioMe diagnostic
comparison, where `cmp` reports different JSON bytes. Recursive comparison finds
**16,274 numerical differences**, maximum **2.2737367544323206e−13**, and no
structural, boolean, string or other nonnumeric changes. These are consistent
with floating-point differences on the current arm64 machine using the project's
Python 3.11 environment; no historical result is changed to make the check pass.

The BioMe independent verifier also passes on the newly generated diagnostic:
**26,799 numerical comparisons**, maximum **4.55e−13**, within its existing
tolerances. The old exact-byte check remains strict and remains a failure on
this execution environment. The circuit and new thermal targets after that
point in the Makefile were therefore run separately and passed.

Historical regenerated JSON/plot differences were restored from the committed
versions. Their diagnostic patch and full logs remain in ignored `build/`:
`hotbox-make-all-2026-10-26.log`, `hotbox-prior-replay-differences.json`,
`hotbox-prior-biome-verification.json`, `hotbox-regeneration-noise-2026-10-26.patch`,
`hotbox-replay-2026-10-26.log` and `hotbox-prior-rlc-replay-2026-10-26.log`.
PDF checks are in `build/hotbox-pdf-qa-2026-10-26/`.

Use the project Python and working system Git on this machine:

```sh
PATH=/usr/bin:/bin:/usr/sbin:/sbin:$PATH MPLCONFIGDIR=build/matplotlib \
  make hotbox-transfer PY=build/main-venv-2026-10-09/bin/python
```

The default `/usr/local/bin/git` cannot execute on this machine; `/usr/bin/git`
works. This is an environment issue, not a reason to alter frozen study inputs.
