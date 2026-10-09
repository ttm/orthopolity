# Predictive claims and identification

1 October 2026. This ledger separates established mathematics, what the present
constructed benchmarks check, and what an independent experiment could establish.
It accompanies the [resource-dimensionality benchmark](resource-dimensionality.md)
and [empirical protocol](empirical-protocol.md); it does not report new observations
or establish priority for a forecasting method.

## Claim ledger

| Claim | What already establishes it | What would add scientific evidence |
|---|---|---|
| A count exponent equals a resource-cost dimension under equal allocation per log size. | The accounting identity $\alpha-1=D_q-\beta$, with independently declared cost $q$, coordinate, and allocation measure. | Independently calibrated costs and measured resource profiles; a prospective prediction of when $\beta=0$ occurs. The identity alone supplies no selection mechanism. |
| Dependence changes joint-feasibility dimension even with fixed marginal capacities. | Existing multivariate probability and copula tail theory; the repository gives concrete forward calculations. | A useful application or a new mathematical result beyond those known models. Reproducing their exponents is a compatibility check. |
| Capacities predict a constructed bottleneck distribution. | $K=\min_a X_a$ implies $S(k)=P(X_1\ge k,\ldots,X_m\ge k)$ by definition. | Separate training and validation can establish estimator accuracy and numerical reliability, including unknown-family and misspecification cases. This does not independently test that a real system realizes the minimum. |
| Capacities predict observed realizable sizes. | A bottleneck mechanism is an additional empirical hypothesis. Capacity gives an upper bound unless full realization is justified. | Calibrate costs separately, freeze a capacity-only forecast, then measure operational or physical outcomes and intervention responses independently. Compare missing-resource, undersaturation, and stochastic-completion alternatives. |
| Budgets predict allocation across classes. | Proportional fairness and entropy optimization give conditional predictions once their objective, reference measure, and constraints are imposed. | Hold the objective and resource definitions fixed; measure budgets and predict full profiles and intervention ratios. Distinguish a fixed total from an upper bound that may be slack. |
| Nature selects resource neutrality. | Neither successful bottleneck prediction nor an imposed neutral optimization objective establishes this. | Independently define eligible conditions and test whether measured cost and feasibility dimensions match, with the finite-band correction below, and whether the predicted allocation is actually realized. A broader principle needs repeated successful transfer across independently chosen systems. |

The prior mathematical boundaries are concrete. [Fung and Seneta (2011)](https://www.sciencedirect.com/science/article/abs/pii/S0167715211002057)
establish regular variation and tail-dependence decay for the bivariate normal
copula. A limiting index does not replace the finite survival curve used for
forecasting here. [Demarta and McNeil (2005), author manuscript](https://www.planchet.net/EXT/ISFA/1226.nsf/0/303eb11b4d617b79c1257b0800744575/$FILE/t%20copula%20demarta%20mcneil.pdf)
give Gaussian/Student comparisons, joint exceedance probabilities, and inference
for Student copula parameters. [Kelly, Maulloo and Tan (1998)](https://web.stanford.edu/class/cs244/papers/ShadowPricesFairnessStability.pdf)
give weighted logarithmic utility, resource constraints, shadow-price solutions,
and associated allocation dynamics. Consequently, fitting a Student parameter
or deriving $N_j=w_j/\sum_a\lambda_a q_{aj}$ is not by itself a new contribution.
An application or improved forecast procedure still requires comparison with
the relevant existing methods before a novelty claim.

## What capacity data identify

Keep aligned resource vectors, not only marginal histograms or ordinary
correlations. Gaussian and Student copulas share
$\tau=2\arcsin(\rho)/\pi$, while Student tail dependence also depends on degrees
of freedom $\nu$. Thus Kendall's tau cannot identify $\nu$, choose these families,
or identify their different limiting feasibility dimensions. Full-vector
likelihood or pseudo-likelihood can estimate additional parameters under a
specified family; Demarta and McNeil describe both joint estimation and estimation
of $\nu$ after a rank-based correlation fit. That conditional identifiability does
not imply enough finite-sample information to distinguish large $\nu$ from a
Gaussian copula. Evaluate that distinction using capacity-only held-out records.

Observed minima alone identify only the joint survival along the threshold path
$(q_1(k),\ldots,q_m(k))$ in budget space, rather than the complete dependence law.
Unpaired marginal records do not identify that survival. A changed cost curve or
unequal-resource intervention can move to another path; retain paired budgets and
calibration coverage for the new thresholds. The asymptotic index is a different
target from a finite-band forecast: many distributions can agree on an observed
bounded range and differ beyond it. A ceiling supplies an atom and cannot identify
the unobserved uncapped tail without extra assumptions.

Generated outcomes $K=\min X_a$ allow a genuine statistical generalization test
when training and validation samples are independent. The construction fixes the
mechanism, so its scientific inference remains about estimation and prediction
within that mechanism. A separately executed workload with measured success can
test the mechanism operationally. Experimentally assigned budgets do not, by
themselves, demonstrate spontaneous neutral allocation.

## Actionable benchmark and sampling decisions

1. Separate cost calibration, capacity training/model selection, and outcome
   validation. Select copula family, marginal models, degrees of freedom,
   thresholds, and loss weights without validation sizes. Evaluate known-family,
   unknown-family, and misspecified-family cases separately; include independence
   and single-resource forecasts with the same measured marginals. A nonparametric
   joint-survival forecast is a useful within-support comparator.
2. Declare instrument limits and the forecast domain before viewing outcomes.
   At threshold $k$, $M$ independent capacity records supply an expected $Mp(k)$
   joint exceedances. The binomial relative standard error is
   $\sqrt{(1-p)/(Mp)}$; roughly 25 exceedances give 20% relative standard error
   when $p$ is small. For four independent unit-Pareto capacities, $p(10)=10^{-4}$:
   16,000 training records yield only 1.6 expected events, and 60,000 validation
   opportunities yield six. A good parametric forecast there uses model
   extrapolation; it is not a precise direct measurement of a tail dimension.
   Choose sample size and supported thresholds against specified alternatives,
   rather than interpreting a visually straight tail as sufficient information.
3. Preserve failures, paired measurements, search boundaries, and censoring.
   Distinguish clipping from conditioning on falling below a cutoff. A clipped
   value is a tied boundary observation, not an exact uncapped value. Repeated
   sizes within one search and tasks within a dependent batch are not additional
   independent opportunities.
4. Use outer simulation replicates that redo calibration, capacity fitting, model
   selection, and validation. Assess prediction error and interval coverage under
   changed margins, dependence, caps, hidden bottlenecks, and stochastic completion.
   Validation-only run quantiles omit uncertainty in fitted resources and costs.
   For actual data, resample the independent opportunity or batch and repeat the
   fitted stages, subject to the observation design.
5. Score the frozen full survival and intervention predictions. Threshold Brier
   scores or other declared probability scores can expose poor calibration;
   separately report tail-bin counts and uncertainty so central accuracy cannot
   conceal rare-event errors. Threshold indicators and bins from the same
   opportunity are dependent. Use a whole-profile diagnostic or simultaneous
   uncertainty for a claim about neutrality across a band.

These are design recommendations, not achieved statistical guarantees. In
particular, nonparametric prediction outside observed support needs assumptions.

## A falsifiable neutrality-selection test

Fix the size coordinate and an independently meaningful additive resource cost
$q(k)$. Estimate $D_q=d\log q/d\log k$ from separate calibration. Estimate the
joint availability law without abundance data and freeze its size prediction.
First test that prediction on independently observed sizes. Then audit the
actual primary resource per log interval $O(k)=kq(k)n(k)$ on a declared band.

For differentiable survival and positive
$\kappa(k)=-d\log S/d\log k$, exact accounting gives

$$
\frac{d\log O}{d\log k}
=D_q(k)-\kappa(k)+\frac{d\log\kappa(k)}{d\log k}.
$$

The familiar $\kappa=D_q$ condition applies to pure survival powers, or an
appropriate regular asymptotic regime. It is insufficient for exact finite-band
neutrality when $\kappa$ changes. Test the full resource profile, preferably using
integrated bin predictions rather than noisy numerical derivatives. Where a cap
applies, report its endpoint mass separately and make no uncapped asymptotic
inference from it.

The countermonotone endpoint makes the correction tangible. For fixed unit-Pareto
margins, $X_1=1/U$, $X_2=1/(1-U)$ with uniform $U$ gives
$S(k)=2/k-1$ on $1\le k\le2$, $f(k)=2/k^2$, and exactly flat $k\,k\,f(k)=2$
for the linear resource $q(k)=k$. Nevertheless,
$\kappa(k)=2/(2-k)$ varies. The Gaussian endpoint copulas and diagonal derivative
are given by [Meyer (2009), equations (2.2)–(2.4) and (3.19)–(3.21)](https://arxiv.org/pdf/0912.2816).
That derivative also yields the familiar Gaussian diagonal index
$2/(1+\rho)$ for $-1<\rho<1$: negative dependence can make it exceed the number
of inputs. Neither index is automatically a resource-cost dimension.

A selection claim needs independently stated admission conditions and an
intervention prediction: for example, a declared relaxation of an auxiliary
restriction restores a specified neutral profile under a frozen allocation
model. Include conditions predicted to remain non-neutral. The relevant result
would be reproducible selection of neutrality under those conditions, rather
than the fact that some parameter setting admits $\kappa=D_q$. Successful
feasibility forecasts with $\kappa\ne D_q$ support the feasibility mechanism and
provide a direct non-neutral case for that audited resource.

## Why unrestricted post-fit constraints cannot test the principle

For any positive observed class allocation $N_j$ and fixed positive weights $w_j$,
one can define $q_j^{\rm eff}=w_j/N_j$ and obtain
$q_j^{\rm eff}N_j=w_j$. Choosing a resource metric this way explains no independent
observation. Similarly, a freely chosen constraint or reference measure for each
observed profile can reproduce the desired optimum without forecasting another
condition. Such representations may guide exploration; they cannot distinguish
the proposed principle from its alternatives.

Prespecified measured costs and budgets avoid this problem. The PF priced cost
$q_j^{\rm eff}=\sum_a\lambda_a q_{aj}$ is predictive when the objective and weights
are frozen and multipliers follow from independent budgets. Its effective
dimension is conditional on that objective and priced resource measure. Testing
the resulting profile does not automatically establish neutrality of each
physical resource, nor show that Nature generally chooses that objective.

The strongest next claim available is consequently a prospective, independently
calibrated resource forecast with documented performance under interventions.
Whether that becomes an original contribution depends on its new method,
application, or explanatory evidence relative to prior work. Establishing a
general neutrality-selection principle requires the additional tests above.
