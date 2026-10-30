# Normal aggregation and natural allocation: verification record

30 October 2026. Source commit **91476d3** adds the author's normal/natural
argument to main section 5, supporting S3.9 and the glossary. It distinguishes
Gaussian aggregation under central-limit conditions from neutral resource
allocation under an independently specified measure. Title and general-law
ambition remain unchanged. No empirical dataset, forecast or registry entry
was added; the analytic fragmentation boundary remains visible.

## Scientific and repository checks

- Independent review checked central-limit assumptions, inverse-resource
  normalization, reference measures, candle sampling transformations and
  harmonic-mode coexistence. Corrections specify harmonic rather than general
  thermal coordinates, density exponents relative to linear size, positive
  variables for logarithms and the necessary parameter domains.
- For ideal flux I=A/r^2, six numerical integrations check normalized intensity
  densities and their means against direct radius integrations. Cases use
  (A,a,b)=(1,1,4), (2.5,0.3,2), (0.04,2,7), each under uniform-radius and
  uniform-volume sampling. Maximum absolute discrepancy is **8.88e-16**.
  These are mathematical checks, not empirical observations.
- With Python 3.11, `make test registry-verify` passes **692 tests** and
  verifies **46 runs / 1,168 references**. The terminology check passes again
  after the final scientific edits. Relative links in all changed source
  documents and `git diff --check` pass.
- Full `make all` was not rerun. The older BioMe exact-byte comparison
  limitation remains unresolved, as recorded on [26 October](reproduction-2026-10-26.md).
  No historical analysis artifacts were regenerated or changed.

Run the repository checks with:

```sh
PATH=/usr/bin:/bin:/usr/sbin:/sbin:$PATH make test registry-verify \
  PY=build/main-venv-2026-10-09/bin/python
```

For the analytic sampling checks, uniform sampling in dimension d=1 or 3 gives
p_r(r)=d r^(d-1)/(b^d-a^d), and transforming I=A/r^2 gives
p_I(I)=d A^(d/2) I^(-1-d/2)/[2(b^d-a^d)] on [A/b^2,A/a^2].
Integrating p_I must give one; integrating I p_I must equal the integral of
(A/r^2) p_r over [a,b]. The six cases above were checked with SciPy quadrature;
an independent reviewer also verified the formulas and these identities.

## Manuscripts

Both manuscripts were forcibly rebuilt twice from **91476d3**, using the
existing Makefile's last-source-commit timestamps:

```sh
PATH=/usr/bin:/bin:/usr/sbin:/sbin:$PATH make \
  -W docs/paper.md -W docs/supporting-material.md paper \
  PY=build/main-venv-2026-10-09/bin/python
```

The **12-page main article and 70-page supplement** are byte-identical across
both builds. Neither TeX pass reports overfull/underfull boxes or warnings.
All-page contact sheets and full-size main page 10 and supporting pages 24--26
were visually inspected. New equations, terminology, page transitions and
references are legible without clipping or overlap; the second-build hashes
match the inspected PDFs.

| PDF | SHA-256 |
|---|---|
| `docs/paper.pdf` | `c200a1635719cd3c230c541b15a44fa68118888b74f5a4446bfc00f27e6ffb41` |
| `docs/supporting-material.pdf` | `15b8ea31e225711b66db08efd09e0392e202557b808bee6e4ad38bd6a4095aa7` |

The revision improves the explanation of conditional mechanisms and their
overlap. It does not establish that power laws dominate nature, that most raw
observations are Gaussian, or that household inventories satisfy orthopolity.
