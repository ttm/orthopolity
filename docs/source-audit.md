# Source and revision audit

Reviewed 9 September 2026. This records direct comparison with the two requested sources
and the reasons for changing the repository's earlier conclusions. It accompanies the
[revised manuscript](paper.md).

## Sources actually inspected

- Renato Fabbri and Osvaldo N. Oliveira Jr., *A simple model that explains why inequality is
  ubiquitous*, manuscript dated 17 March 2017, 13 pages. Supplied as
  .private/originalArticle/essay.pdf. All pages were text-extracted; mathematical pages 4,
  7, and 12 were rendered, with pages 7 and 12 visually checked. Publication status is unverified.
  The private document has not been changed or copied into the public repository.
- Renato Fabbri, [The Orthopolity cosmological principle and the Natural distribution law](https://ttm.github.io/2024/08/14/power.html),
  dated 14 August 2024. The public essay was read directly.
- Existing code, frozen datasets, configurations, results, and local Git history.
  Literature verification is recorded in [references.md](references.md).

The linked Zenodo record is not assumed to be byte-identical to the supplied 2017 manuscript.
Authorship, funding, and acknowledgements in that manuscript do not automatically carry over
to a new article.

## 1. What survives from the original idea

Equal resource per declared class implies fewer objects in classes with higher mean resource
cost. This is exact accounting. Its converse is also exact when the resource is specified
independently. It is useful for explaining the difference between object sampling and
resource-weighted sampling.

This insight belongs in a scientific synthesis with credit to established size-spectrum
literature. The additional claim that real systems generally allocate resource this way
requires empirical evidence or a dynamical argument.

## 2. Corrections to the 2017 manuscript

| Location | Problem | Correction or scope |
|---|---|---|
| Proposition 1, pp. 3–4; explicit uniform density, p. 7 | Equal allocation across wealth values is presented as almost unavoidable and as conservation | It is an allocation assumption beyond conservation. Specify linear, logarithmic, or discrete classes. |
| Definition of wealth and dimensionality argument, pp. 3–7 | $k$ alternates between resource amount and a coordinate whose resource cost is $k^\alpha$ | Use separate symbols $k$ and $q(k)$. The power-cost model needs justification. |
| Corollary 1, pp. 3–4 | Incomparable resource units are taken to justify multiplying inputs | Dimensional incompatibility of a sum does not make a product the correct resource. Define its physical meaning and additivity. |
| Corollary 2, p. 4 | Uniform allocation is said to produce an equilibrium and make deviations transient | No dynamics, stability proof, or relaxation evidence is supplied. The algebra establishes neither. |
| Corollaries 3–6, pp. 4–5 | Upper cutoff and normalization/resource constants are equated | Probability normalization, population size, total resource, and resource per class have different meanings and units. None generally fixes the upper cutoff. |
| Independent-input argument, pp. 6–7 | Number of independent inputs is used to explain the tail exponent | A product distribution requires integration and support constraints. Independent Pareto inputs supply a counterexample with a logarithmic correction. |
| Boxes, p. 7 | Capacity for hypothetical small cubes is treated as abundance of actual mixed objects | The existence/counting process and competition or overlap must be modelled separately. |
| Networks, p. 8 | Degree/resource algebra is treated as a reason for a generic exponent near 2 | For an undirected network $\sum_i k_i=2E$ fixes a total degree, not the degree distribution. |
| Wealth, pp. 9–11 | Departures from power laws are asserted to require work or be transient | No causal economic model or thermodynamic definition of work supports this. Cross-sectional accounting does not imply either assertion. |
| Conclusions, p. 11 | Time arrow, thermodynamic analogy, and dark-sector speculation | No corresponding physical model or quantitative prediction is supplied. These do not enter the revised scientific claim. |

### Probability formulas in the appendix

For $f(k)=Ck^{-\alpha}$ on $0<a\le k\le b<\infty$, normalization fixes

$$C=\begin{cases}
(1-\alpha)/(b^{1-\alpha}-a^{1-\alpha}),&\alpha\ne1,\\
1/\ln(b/a),&\alpha=1.
\end{cases}$$

Thus the normalized family has three free parameters, not four independent ones. A lower
boundary at zero cannot be used for the usual positive exponents without checking integrability.

The final equality for the bounded median in equation A3 (p. 12) has a subtraction where
there should be an addition:

$$m=\left(\frac{a^{1-\alpha}+b^{1-\alpha}}{2}\right)^{1/(1-\alpha)}
\quad(\alpha\ne1),\qquad m=\sqrt{ab}\quad(\alpha=1).$$

The first expression for variance on that page is the second moment, missing subtraction
of the squared mean. The last expression supplies it. A form that handles all special cases is

$$E[K^r]=\begin{cases}
C(b^{r+1-\alpha}-a^{r+1-\alpha})/(r+1-\alpha),&\alpha\ne r+1,\\
C\ln(b/a),&\alpha=r+1,
\end{cases}
\qquad \operatorname{Var}(K)=E[K^2]-E[K]^2.$$

The unbounded-tail thresholds stated there are correct when $a>0$: normalization requires
$\alpha>1$, a finite mean $\alpha>2$, and finite variance $\alpha>3$.
These singular cases do not imply that empirical exponents must lie between 1.5 and 3.

## 3. Corrections to the 2024 essay

Its uniform-allocation intuition is retained, with the measure explicit. Two algebraic
statements need correction: multiplying a decreasing class probability by population size
does not reverse the exponent's sign, and uniform class resource requires multiplying
probability by *positive* resource cost, not inverse cost. An expected count is not itself
a probability. For continuous variables the statement must specify a density and measure.

The cycle-count and wave-speed identities do not establish a distribution of observed
objects. Psychophysical response curves and rank-frequency relations also need their own
sampling definitions. Sums do not become normally distributed without the assumptions and
centering/scaling required by a suitable central limit theorem. An unspecified correction
function cannot make a universal hypothesis falsifiable.

These points concern the specific equations and uses of probability, rather than the value
of asking how resource allocation relates to abundance.

## 4. Corrections to the repository's previous interpretation

| Previous claim | Revised assessment |
|---|---|
| Logarithmic classes merely clarify the original uniform law | Linear and logarithmic classes are different hypotheses, with density exponents differing by one. |
| The accounting equivalence is new or individual variability unstudied | Sheldon, Gaedke, Arranz, and others supply substantial prior art. |
| Blind, preregistered cross-domain experiment | Git records a local plan before a later analysis commit. It cannot independently verify blinding, public timing, or first inspection. |
| Equipartition holds in the expected aquatic spectrum | A median slope near −1 establishes neither a population mean nor a flat mean resource spectrum. |
| 7.8% of ecosystems are individually equivalent | This is a historical fraction of point slopes within metadata-derived tolerances, with no individual uncertainty or profile test. |
| Dispersion predicts the pass rate within 1–2% | The original calculation compared latent and observed quantities on different samples and ignored errors. Corrected matched checks do not reproduce that agreement. |
| AIC selection establishes Gaussian adequacy within habitat | AIC ranks the compared models; it is not an absolute fit test or proof of class homogeneity. |
| Two resources provide a decisive ensemble test | The claimed correlation restriction requires constant resource-exponent differences and holds without equipartition. |
| No more than 8% of variance is temporal | Comparing different studies and populations provides no such bound. |
| Reproducing published SD independently corroborates latent dispersion | It reuses the same underlying data and is an extraction check. |
| A label discrepancy explains every secondary failure | One documented mismatch does not establish the cause of all disagreements. |
| Homogeneity necessarily contradicts this allocation principle | No general incompatibility has been derived; the problem is the absence of a cosmological model and evidence. |

The code audit also corrected dropped zero-resource bins in flatness checks, centre-to-centre
rather than edge-to-edge domain widths, subrange normalization, missing likelihood Jacobians,
zero Monte Carlo probabilities, and inaccurate numerical integration of narrow measurement errors.
Regression tests accompany substantive numerical changes.

## 5. Newly identified metadata problem

All 377 primary-subset records from StudyID_07 (Gaedke) report minimum mass $2\times10^{-8}$
and maximum $2\times10^{27}$ in pg C, with 33 size classes. Those bounds span 35 decades;
the upper value corresponds to $2\times10^{12}$ kg of carbon per object. It is not a plausible
plankton body mass. This is a metadata inconsistency, not an observed extraordinary organism.

The slope values are retained for location summaries, but the range is not repaired by
guessing an exponent or converting log bases. Span-dependent diagnostics exclude these
records explicitly, and the historical primary tolerance output is retained alongside an
exclusion sensitivity. The source's actual range requires a documented record-level correction
before those tolerances can be restored. Other records have not thereby been validated.

## 6. Does orthopolity deserve a scientific document?

**Yes, as a limited critical synthesis or research note.** The useful contributions are a
clear allocation-versus-counting interpretation, explicit reference measures, counterexamples
to stronger deductions, and inspectable analyses showing how a plausible hypothesis can fail
or remain unresolved.

**The original universal-law paper is not defensible as written.** Conservation does not yield
the allocation assumption, the dimensionality argument does not establish generic exponents,
and the observational examples do not support the cosmological or social conclusions.
The revised article states those limits rather than promoting an unverified weaker principle
as a confirmed discovery.
