# Whole-object assembly: when inverse-resource means emerge

Started 31 October 2026; forecast frozen 1 November 2026. This constructed model fills a stated gap in the
[class-resource exchange model](class-exchange.md): actual integer objects now
assemble and break apart, with every event conserving the material budget.
The rates are specified before deriving the stationary law. A second mechanism
uses the same objects, budget and reaction network but different rate dependence.
No empirical dataset is used. Simulation will check the implementation of the
analytic predictions; it cannot independently confirm the general law in nature.

The stationary-distribution tools are established, including both the mass-action
and non-mass-action results of Anderson, Craciun and Kurtz (2010), Theorems 4.1
and 6.1. The contribution here is their explicit application to orthopolic
allocation, its finite-budget correction, a rate intervention and the distinction
between equal means and unequal snapshots. The proof below uses detailed balance
directly rather than claiming a new general reaction-network theorem.

## Objects, resource and comparison measure

An object contains 1, 2 or 4 monomer units. All three kinds, including free
monomers, are counted. Their nonnegative integer counts satisfy

$$n_1+2n_2+4n_4=B,\qquad R=(n_1,2n_2,4n_4).$$

The resource is material mass in monomer units, not energy, molecule count or
an inferred effective cost. The population is closed to these units; the model
does not assert energy conservation or describe the surrounding thermal bath.
The only reactions are

$$2X_1\rightleftarrows X_2,\qquad 2X_2\rightleftarrows X_4.$$

Binary assembly fixes the available masses before any outcome. Compare bins
centered on 1, 2 and 4 with boundaries $2^{-1/2},2^{1/2},2^{3/2},2^{5/2}$.
All have width $\ln2$: equal expected class mass is **log-orthopolic in physical
object mass**. Equal resource per linear mass width would instead assign shares
$(1,2,4)/7$ to those same bins. Neither measure is selected from the resulting
abundance. The log measure is a declared comparison across binary hierarchy
levels, not a consequence of conservation. Three discrete masses do not
establish a continuous power-law density.

The observable is the stationary expectation $E[R_i]/B$, equivalently a
long-time mean in this finite irreducible chain. Expected counts are also
reported. Normalizing expected counts describes a population pooled over
replicates; it need not equal the mean of within-snapshot normalized counts.

## Two independently specified rate rules

Let $a_j,b_j>0$ be association and breakup constants for reaction $j=1,2$.
Unavailable reactions have rate zero.

**Constant feasible-channel rates:** association has rate $a_j$ when at least
two reactants exist, and breakup has rate $b_j$ when its parent exists. Adding
more eligible objects creates no additional processing channels. This is an
idealization of saturated processing in both directions, not ordinary
well-mixed pair encounters. Its physical application would require independent
evidence for these rate rules.

**Mass-action rates:** association has rate $a_j n_j(n_j-1)$ and breakup has
rate $b_j n_{2j}$. The convention is the falling factorial, with no division by
two. Using unordered pairs requires doubling the corresponding association
constant to represent the same process. Rate constants absorb the fixed-volume
and time units; equality of their numerical values is part of this constructed
case, not a claim that different chemical constants share physical units.

Both rules operate on exactly the same finite state space. Successive breakup
of tetramers and then dimers reaches $(B,0,0)$ from every state. Every transition
is reversible, so all feasible configurations communicate and the stationary
law is unique.

Write $r=a_1/b_1$ and $\rho=a_2/b_2$. Reaction-wise detailed balance gives

$$\pi_{\rm channel}(n)\propto r^{n_2+2n_4}\rho^{n_4},\qquad
\pi_{\rm mass}(n)\propto
\frac{r^{n_2+2n_4}\rho^{n_4}}{n_1!n_2!n_4!},$$

in each case restricted to the exact budget. For the first reaction the
channel-weight ratio is $r$; the factorial-weight ratio additionally supplies
$n_1(n_1-1)/(n_2+1)$. For the second, the corresponding ratios are $\rho$ and
$\rho n_2(n_2-1)/(n_4+1)$. These match the opposing rate ratios, proving both
stationary laws. Their normalization is a finite sum. Product-form parameters
are not generally the conditioned mean counts.

## Equal resource in the mean, with an exact finite-budget correction

Set every constant to one. Constant feasible-channel rates make the law
uniform over **count configurations**, not over labeled microscopic
arrangements or object sizes. For $B=4m$, fixing $n_4=j$ leaves
$2(m-j)+1$ configurations, so their total is $(m+1)^2$. Direct summation gives

$$E[n_4]=\frac{m(2m+1)}{6(m+1)},\qquad
E[n_2]=m-E[n_4],\qquad E[n_1]=2E[n_2].$$

Consequently,

$$\frac{E[R_1]}B=\frac{E[R_2]}B=\frac13+\frac{1}{12(m+1)},\qquad
\frac{E[R_4]}B=\frac13-\frac{1}{6(m+1)}.$$

Log-orthopolic equality therefore emerges in stationary means as the budget
grows with these three classes fixed. Its finite departure is predicted, not
fitted. Expected counts satisfy $E[n_i]\sim B/(3q_i)$ for $q=(1,2,4)$:
their relative error vanishes, not generally their absolute difference.

This does **not** make snapshots equal. Normalized resource vectors approach
the uniform distribution on the simplex, or Dirichlet$(1,1,1)$, by the ordinary
lattice-to-volume limit (Beck and Robins, 2015). Its density is two on
$s_1,s_2\ge0$, $s_1+s_2\le1$, with $s_4=1-s_1-s_2$. Thus

$$\operatorname{Var}(R_i/B)\longrightarrow1/18,\qquad
\operatorname{Cov}(R_i/B,R_j/B)\longrightarrow-1/36\quad(i\ne j).$$

Relative fluctuations persist as the number of objects increases. Gaussian
limits apply to suitable independent-replicate or mixing time averages, not
automatically to a single high-budget configuration. This differs from the
independent resource-packet model's shrinking share covariance. The order of
limits matters: first take equilibrium for each finite budget, then increase
the budget; no uniform bound on relaxation time is asserted.

## Same budget, different mechanisms, and a frozen intervention

Fix $B=24$, giving 49 configurations. Compare the two rate rules with every
constant one. Then double only tetramer association, so $\rho$ changes from
one to two while $r=1$. The exact stationary forecasts, computed by rational
enumeration before stochastic simulation, are:

| Mechanism | Baseline mean mass shares | After doubling tetramer association |
|---|---|---|
| Constant feasible channels | (0.345238, 0.345238, 0.309524) | (0.171662, 0.171662, 0.656676) |
| Mass action | (0.055882, 0.182557, 0.761562) | (0.044436, 0.132949, 0.822616) |

For constant channels the fractions are exactly $(29/84,29/84,13/42)$ and
$(63/367,63/367,241/367)$. The mass-action result strongly departs from equal
log-class resource despite identical conservation, object costs and allowed
reactions. It is a boundary of this allocation premise, not evidence that
conservation failed. Common numerical rate constants do not imply common
physical kinetics.

A separate control multiplies **all** biased channel rates by three. It leaves
the stationary law unchanged and predicts the full time rescaling
$p_3(t)=p_1(3t)$. Changing only one forward/backward ratio instead changes
allocation, as the table predicts.

The [configuration](../configs/whole_object_2026-10-31.json) fixes all rates,
budgets, observation time, seeds and verification tolerances. The
[driver](../experiments/run_whole_object.py) has separate forecast and verification
stages. Forecasts include exact stationary means and covariances, plus the
complete finite-time distribution from the master equation. The verification
stage uses event-by-event Gillespie paths. Matrix evolution and simulation use
different numerical algorithms but share the propensity routine; their agreement
alone cannot detect a common rate-specification error. A separate scalar-rate
audit reconstructs the generators and checks the forecasts without importing
either model implementation.
The retained [independent audit](../results/whole-object-assembly-2026-10-31/forecast-audit.json)
checks 18,547 scalar quantities within 1.21e-13 before study simulations.

All five scenarios start from independently sampled baseline stationary
configurations for their respective mechanism, with the specified intervention
at time zero. Observe 4,096 independent trajectories per scenario at time five.
This is a finite-time prediction, not an assumption that time five is equilibrium.
The mean-share tolerance is fixed by Hoeffding's inequality and a union bound
over 15 bounded share means, with total error probability at most 0.001:

$$\epsilon=\sqrt{\frac{\ln(2\cdot15/0.001)}{2\cdot4096}}.$$

Class means within a realization are dependent; the bound requires independence
across trajectories only. Whole-state total variation is reported descriptively.
All case results are retained even if a frozen statistical bound fails.
An independent linear stationary solve, edge detailed balance, exact budget
conservation and clock rescaling also check the formulas. The forecast and
implementation are to be committed and pushed before these study simulations. This
ordering is a computational audit, not empirical preregistration or independent
natural-system evidence.

## Interpretation and next empirical requirement

The sufficient mechanism is now concrete: symmetric feasible state-to-state
assembly/breakup rates, a connected closed budget class and a large budget
relative to fixed object requirements yield inverse-cost expected abundance
under the declared logarithmic classes. Conservation alone remains insufficient.
Rate multiplicity changes the stationary law; finite budgets change mean shares;
snapshot fluctuations remain large even when the means become equal.

A public empirical source would need independently observed assembly and
breakup propensities, a complete material budget, object counts and a separate
rate intervention. The first question is whether those measured kinetics support
either model, not whether a fitted abundance curve looks like a power law.
No new broad dataset search or laboratory work is assumed here.

## References

Anderson, D. F., Craciun, G., and Kurtz, T. G. (2010). Product-form stationary
distributions for deficiency zero chemical reaction networks. *Bulletin of
Mathematical Biology*, 72, 1947--1970.
<https://doi.org/10.1007/s11538-010-9517-4>.
Author manuscript: <https://arxiv.org/abs/0803.3042>.

Beck, M., and Robins, S. (2015). *Computing the Continuous Discretely*, second
edition. Springer. Author-corrected text:
<https://matthbeck.github.io/papers/ccdnew.pdf>.
