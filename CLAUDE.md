# Notes for contributors and assistants

- **Start with [docs/status.md](docs/status.md):** the authors' intent, history, results, current
  assessment and prioritized next steps. Update it at the end of any session that changes them.
- Terminology follows [docs/glossary.md](docs/glossary.md). The adjective is **orthopolic**;
  `tests/test_terminology.py` fails if the incorrect form appears elsewhere.
- Always state the reference measure (log-orthopolic or linear-orthopolic); the same exponent
  implies different resources under the two.
- Keep exploration and confirmation separate: a resource reading chosen after seeing an exponent is
  a hypothesis; it counts as evidence only with inputs fixed in advance and a second prediction
  that passes.
- Work on `main` (authorized by the lead author, 8 October 2026).
- `make all` verifies frozen inputs, runs the tests and regenerates every analysis. Results were
  committed under Python 3.11; do not commit floating-point noise from other versions.
