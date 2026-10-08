# Notes for contributors and assistants

- Terminology follows [docs/glossary.md](docs/glossary.md). The adjective is **orthopolic**;
  `tests/test_terminology.py` fails if the incorrect form appears elsewhere.
- Always state the reference measure (log-orthopolic or linear-orthopolic); the same exponent
  implies different resources under the two.
- `make all` verifies frozen inputs, runs the tests and regenerates every analysis.
