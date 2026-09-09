# Orthopolity

A critical investigation of the idea that equal resource allocation can produce unequal
object abundance. The starting points are [Fabbri's 2024 essay](https://ttm.github.io/2024/08/14/power.html)
and the supplied 2017 manuscript by Renato Fabbri and Osvaldo N. Oliveira Jr.

**Assessment:** the idea merits a scientific document as a precise synthesis and reproducible
test of a conditional hypothesis. The current evidence does not establish a new natural law,
a cosmological principle, or equal resource allocation in an average ecosystem.

The revised [scientific manuscript](docs/paper.md) is the main document.

## What the hypothesis says

Choose the objects, an additive resource $q$, a size coordinate $k$, an observation domain,
and a reference measure for the size classes. Equal resource per logarithmic interval means

$$\frac{dR}{d\ln k}=\bar q(k)\frac{dN}{d\ln k}=C.$$

With $\bar q(k)\propto k^d$, this implies a count density $dN/dk\propto k^{-(d+1)}$.
Equal resource per *linear* interval instead implies $dN/dk\propto k^{-d}$.
The difference is substantive: the original essay's uniform allocation does not uniquely
select the logarithmic version used in the ecological analyses.

Conservation alone gives neither hypothesis. A fitted inverse-cost relation does not
explain why a system allocates resources that way. The [concept note](docs/concept.md)
states the assumptions and counterexamples.

## What the evidence supports

| Source | Finding | Interpretation |
|---|---|---|
| USGS earthquakes | $b=0.998$ versus 1.5 required by the selected energy proxy | Disagreement with that proxy version; not a direct radiated-energy test |
| NOAA solar flares | Predicted exponent 1.858 versus estimated 2.239 on the selected range | Disagreement with the joint resource-scaling and allocation model |
| Published ocean reconstruction | Broad plateau with substantial shape and reconstruction uncertainty | Re-expression of existing evidence; no independent confirmation |
| GLOSSAQUA aquatic spectra | Median normalized biomass slope −1.015, study-block departure interval [−0.100, 0.010] | Location near −1; planned equivalence not established |

The aquatic dataset contains 1,300 estimates from 16 study identifiers, with 78% of estimates
from two studies. Reported-slope tolerance fractions are point-estimate diagnostics, not
fractions of statistically equivalent ecosystems. Known invalid size bounds affect 377
records; corrected sensitivities are reported explicitly.

The earlier claims of a verified ensemble principle, near-perfect failure-rate prediction,
Gaussian adequacy, a decisive two-resource ensemble test, and an 8% temporal-variance bound
have been withdrawn. Mean-zero slopes do not imply a flat mean resource spectrum.
See [the evidence ledger](docs/evidence.md) and [revision audit](docs/source-audit.md).

## Reproduce

Python 3.11 or later is required. A virtual environment keeps dependencies isolated:

~~~bash
python3 -m venv .venv
. .venv/bin/activate
make install
make all
~~~

The pinned analysis dependencies are in [requirements.txt](requirements.txt).
To use an existing interpreter, pass its path, for example:

~~~bash
make all PY=/path/to/python
~~~

The pipeline verifies frozen input checksums, runs the test suite, and regenerates analyses.
Data verification is offline; restoring missing snapshots is an explicit separate action:

~~~bash
make data
make restore-data
~~~

The manuscript typesets to PDF with a TeX installation providing `pdflatex`; no Pandoc is
needed, since `tools/md2tex.py` converts the Markdown subset the manuscript uses:

~~~bash
make paper
~~~

This writes [docs/paper.pdf](docs/paper.pdf), which is committed for convenience; regenerate
it whenever the manuscript changes, so the tracked PDF matches its Markdown source.

Results contain estimated quantities, diagnostic plots, and declared limitations. Successful
reproduction verifies computation from the frozen inputs; it does not validate sampling
assumptions, data labels, novelty, or the physical hypothesis. The historical analysis plan
is preserved in [configs/prereg_2026-09-09.json](configs/prereg_2026-09-09.json);
Git records commit order, not independently verified blinding or external preregistration.

## Repository guide

| Path | Purpose |
|---|---|
| [docs/paper.md](docs/paper.md) | Scientific manuscript: formulation, methods, results, limitations, references |
| [docs/source-audit.md](docs/source-audit.md) | Direct assessment of the original PDF and blog, and corrections to this repository |
| [docs/concept.md](docs/concept.md) | Definitions, reference measures, exponent conversions, and ensemble counterexample |
| [docs/evidence.md](docs/evidence.md) | Numerical provenance and current interpretations |
| [docs/value.md](docs/value.md) / [docs/criticism.md](docs/criticism.md) | Reasons to pursue a limited study and limits on its contribution |
| [docs/not-worth-pursuing.md](docs/not-worth-pursuing.md) | Claims and directions the present evidence does not justify |
| [docs/roadmap.md](docs/roadmap.md) | Remaining scientific and submission work |
| [docs/references.md](docs/references.md) | Annotated literature and primary sources |
| [src/](src/) / [tests/](tests/) | Accounting, distribution fitting, equivalence diagnostics, meta-analysis, and regression checks |
| [experiments/](experiments/) / [results/](results/) | Reproducible analyses and outputs |
| [data/SOURCES.md](data/SOURCES.md) / [data/NOTICE.md](data/NOTICE.md) | Input provenance and source-specific notices |
| [tools/explore.py](tools/explore.py) | Optional inspection and sonification aid; not empirical evidence |

The supplied private manuscript is not redistributed. The earlier wording and results remain
available in Git history; the current documents supersede their interpretation.
