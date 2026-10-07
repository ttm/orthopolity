# Contribution and its established foundations

This targeted comparison supports the general-law manuscript. It is not an
exhaustive priority search. Orthopolity is proposed as a general natural law;
the comparisons below locate the specific mathematical, physical, and
inferential claims without attributing established results to this proposal.

## What is proposed

The central proposal is that Nature tends to distribute resources equally
among concentrations of those resources. Its operational formulation specifies
the physical objects, comparison measure, effective resource, and constraints.
For abundance density $n_\mu$, a conditional mean resource $\bar q$, and a
positive constraint profile $a$, the working relation is

$$\bar q(k)n_\mu(k)=C a(k).$$

The scientific programme connects three uses of this statement: deriving
allocation from mechanisms, predicting abundance from independently specified
resource requirements, and inferring effective resource combinations whose
predictions can subsequently be tested. The substantive claim concerns where
this relation and its dynamical extensions describe natural systems. Algebraic
inversion alone does not establish that scope.

## Closest foundations and the required distinction

| Established work | What it supplies | What this manuscript develops |
|---|---|---|
| Resource-weighted distributions and ecological size spectra | Allocation identities, inverse-cost abundance conditional on equality, and observed biomass patterns | Explicit resource, measure, constraint and observation definitions across applications; the proposal of a general allocation tendency |
| Reversible transport and statistical mechanics | Detailed balance, convergence, classical equipartition and quantum occupancy | Worked realizations of equality, constrained outcomes and recovery, with the physical comparison measure identified in each case |
| Inverse optimization | Inference of objectives from choices across conditions under a restricted model family | Inference of candidate effective resource requirements from allocation profiles, followed by predictions with a shared composition rule |
| Inverse statistical mechanics | Inference of interactions from ensemble observations | An allocation-level inverse problem that can be formulated before a complete microscopic interaction model is available; its resource/constraint ambiguity remains explicit |
| Linear inverse problems | Rank, null spaces, conditioning and covariance propagation | Conditional identification and parameter-free transfer relations for resource-composition models; no claim that the underlying linear algebra is new |
| Linguistic abbreviation and communication efficiency | Relationships among word frequency, length, context and communicative cost | A declared resource-allocation interpretation and a frozen comparison of candidate symbolic costs across text genres |

[Keshavarz, Wang and Boyd (2011)](https://stanford.edu/~boyd/papers/imputed_objective.html)
infer a parameterized convex objective from optimal or nearly optimal decisions
and prior assumptions. Their work already establishes the legitimacy of learning
an unobserved governing quantity from observed outcomes. The orthopolity inverse
problem should therefore be evaluated by its allocation assumptions and the
predictions that its inferred resources produce, rather than by claiming the
general idea of inverse inference.

[Habeck (2014)](https://doi.org/10.1103/PhysRevE.89.052113) develops Bayesian
inference of particle interactions from ensemble properties. The orthopolity
formulation instead starts with an effective allocation relation. A future
microscopic explanation could connect the two levels; the present work does
not derive a unique interaction potential from abundance.

Indeed, a deterministic product-resource model under a fixed measure has

$$p_\theta(k)=\frac{1}{Z_s(\theta)}
\exp\!\left(\ln a_s(k)-\sum_\ell\theta_\ell\ln X_{s\ell}(k)\right).$$

This is an exponential-family model, with log constituent requirements as
sufficient statistics and $a_s\,d\mu$ as its reference measure. Its normalized
likelihood and fitting machinery are established statistical tools. The
resource interpretation and the shared-parameter predictions across environments
are the application-specific content. For heterogeneous objects the denominator
contains $E[\prod X_\ell^{\theta_\ell}\mid k,s]$, which need not retain this
simple exponential-family form.

[Piantadosi, Tily and Gibson (2011)](https://doi.org/10.1073/pnas.1012551108)
compare frequency and contextual information as predictors of word length.
Such models are important alternatives to a length-only resource account.
Rank-frequency Zipf scaling, abbreviation, and equal expenditure of letters
are distinct statements. The [linguistic application](linguistic-resources.md)
defines their accounting separately.

## Where a further scientific increment can be demonstrated

For a prespecified product resource with shared exponents $\theta$, independently
characterized constituent scalings produce $b=D\theta$, where $b$ contains
constraint-corrected abundance slopes. Rank specifies what is identified;
left-null contrasts specify restrictions across environments; conditioning
specifies how uncertainty is amplified. These are applications of standard
linear algebra to the resource model. Their empirical value is realized when
constituent information and calibration environments determine a prediction
that is then evaluated elsewhere without changing the composition, measure or
constraint rule.

A successful prediction supports the specified resource model within its
tested domain. A poor prediction retains information about its limitations.
Neither outcome automatically determines the status of the unrestricted
general-law proposal. Identifying a previously omitted constraint requires
additional evidence or a subsequent test, rather than renaming the residual.

The contribution should therefore be judged on the coherence and reach of the
general-law proposal, the explanatory connections that its worked realizations
establish, and the predictive usefulness of its inferred effective resources.
The current paper distinguishes these claims from its established foundations.

## References

- Keshavarz, A., Wang, Y., and Boyd, S. (2011). Imputing a Convex Objective
  Function. *Proceedings IEEE Multi-Conference on Systems and Control*, 613–619.
  [Author's publication page](https://stanford.edu/~boyd/papers/imputed_objective.html).
- Habeck, M. (2014). Bayesian approach to inverse statistical mechanics.
  *Physical Review E* **89**, 052113.
  [doi:10.1103/PhysRevE.89.052113](https://doi.org/10.1103/PhysRevE.89.052113).
- Piantadosi, S. T., Tily, H., and Gibson, E. (2011). Word lengths are optimized
  for efficient communication. *Proceedings of the National Academy of Sciences*
  **108**(9), 3526–3529.
  [doi:10.1073/pnas.1012551108](https://doi.org/10.1073/pnas.1012551108).
