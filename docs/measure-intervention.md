# A cost change that distinguishes two allocation postulates

4 October 2026. This is a mathematical design note with deterministic worked
examples. It supplies no new empirical evidence and is not a frozen study.
The [plankton observation gate](plankton-observation-gate.md) remains closed.

**Main result:** equal resource per logarithmic size and equal resource per
logarithmic cost are observationally equivalent under a power cost law. A
physical additive cost breaks that equivalence. Relative to the shared baseline,
the two postulates predict abundance responses with log slopes −1 and −2
against the independently measured cost multiplier. This gives a concrete
discriminating prediction beyond another baseline power-law fit.

## When the hypotheses coincide

Fix a size domain $[a,b]$, $0<a<b$, and a positive, continuously differentiable
cost $q(k)$ with $q'(k)>0$. Costs are deterministic in this model. Let $B>0$ be
total expected allocated resource on that domain, $u=\ln(k/k_0)$,
$L=\ln(b/a)$, $H=\ln[q(b)/q(a)]$, and
$D_q(k)=d\ln q/d\ln k$. Compare two physical postulates:

$$S:\quad \frac{dE[R]}{du}=\frac B L,
\qquad
Q:\quad \frac{dE[R]}{d\ln q}=\frac B H.$$

The size reference stays fixed under a cost change in S. Q uses the logarithm
of the **current physical cost**. Changing variables in Q gives

$$\frac{dE[R_Q]}{du}=\frac B H D_q(k),\qquad
\frac{dE[R_Q]/du}{dE[R_S]/du}=\frac{L D_q(k)}H.$$

Consequently the complete resource profiles, and their count profiles after
division by the same $q(k)$, coincide if and only if $D_q$ is constant. Integrating
that condition gives $q(k)=A(k/k_0)^d$, $A,d>0$, on the declared band. Under the
power law, $H=dL$. A power-cost baseline therefore cannot identify which of
these two reference measures describes allocation, even with perfect observations.
Equality of a few bin totals is a weaker condition than equality of full profiles.

These are different hypotheses, not two descriptions of one distribution.
Expressing S in cost coordinates preserves its measure and yields
$dE[R_S]/d\ln q=B/(L D_q)$, generally nonconstant. Requiring uniformity again
changes the allocation postulate. Reference measures and transformation-based
indifference have established precedent in [Jaynes (1968)](https://bayes.wustl.edu/etj/articles/prior.pdf);
that argument does not establish a physical symmetry in nature.

## The discriminating cost change

Use an independently calibrated family

$$q_c(k)=q_0\{v(k)+c\},\qquad v(k)=(k/k_0)^d,
\qquad q_0,k_0,d>0,\quad c\ge0.$$

Here $q_0c$ is a physical per-object overhead in the same resource units as
$q_0v$. It is not a change of units or an offset added to the recorded variable.
Write $H_c=\ln[(v(b)+c)/(v(a)+c)]$. Expected counts per log size are

$$\nu_{S,c}(k)=\frac{B_c}{Lq_0(v+c)},\qquad
\nu_{Q,c}(k)=\frac{B_c d v}{q_0 H_c(v+c)^2}.$$

Both equal $B_0/(Lq_0v)$ at $c=0$. Define the measured cost multiplier
$h(k)=q_c(k)/q_{c=0}(k)=1+c/v(k)$. Then

$$\frac{\nu_{S,c}}{\nu_0}=\frac{B_c}{B_0}h^{-1},
\qquad
\frac{\nu_{Q,c}}{\nu_0}=\frac{B_c}{B_0}\frac{dL}{H_c}h^{-2}.$$

Thus the log response has slope −1 under S and −2 under Q. The total allocated
resource may change: its ratio affects only the intercept. Ratios of responses
at two sizes remove that intercept. These statements require the same size
domain, cost coefficient and degree, with the stated additive intervention.
They concern pointwise expected densities, not arbitrary regressions on noisy
counts or finite-bin averages.

The response exponents extend beyond a power baseline. For any fixed increasing
baseline $q_{\mathrm{base}}(k)$, a size-independent physical addition $\delta$
gives $q_{\mathrm{after}}=q_{\mathrm{base}}+\delta$ and leaves $q'(k)$ unchanged.
Since Q predicts $\nu_Q=(B/H)kq'(k)/q(k)^2$, its response is
$(B_{\mathrm{after}}/B_{\mathrm{before}})(H_{\mathrm{before}}/H_{\mathrm{after}})h^{-2}$,
while S's response remains $(B_{\mathrm{after}}/B_{\mathrm{before}})h^{-1}$.
The power baseline is useful because it makes the two initial profiles identical;
it is not necessary for this response contrast.

For $c>0$, S predicts a decreasing count density throughout the band. Q's count
density increases until $v=c$ and decreases afterward, so it has an interior
peak if $v(a)<c<v(b)$. Q's resource density increases with size, while S's
resource density is constant. Both rivals must be allowed to fail empirically.

## Exact forecasts for observed bins

For a bin $[\ell,r]$, put $v_\ell=v(\ell)$ and $v_r=v(r)$. The resource totals are

$$R_S[\ell,r]=B\frac{\ln(r/\ell)}L,\qquad
R_Q[\ell,r]=B\frac{\ln[(v_r+c)/(v_\ell+c)]}{H_c}.$$

For $c>0$, the count totals are

$$N_S[\ell,r]=\frac{B}{Lq_0dc}
\ln\left(1+\frac{c(v_r-v_\ell)}{v_\ell(v_r+c)}\right),$$

$$N_Q[\ell,r]=\frac{B}{q_0H_c}
\left(\frac1{v_\ell+c}-\frac1{v_r+c}\right).$$

At $c=0$, both reduce to
$B(1/v_\ell-1/v_r)/(Lq_0d)$. Summing adjacent bins gives the forecast for their
union. Dividing a bin's resource by its midpoint cost would introduce an
approximation. Resetting all bin weights to equal shares after arbitrary
regrouping would change the hypothesis.

The [calculator](../src/orthopolity/measure_intervention.py) evaluates these
integrals using stable expressions near $c=0$ and at large overhead. Its
[tests](../tests/test_measure_intervention.py) compare with independent numerical
quadrature and check baseline equality, additivity, unit changes and limiting
profiles. These are checks of mathematical calculations, not scientific validations.

The worked example fixes $k\in[1,10]$, two equal log-size bins split at
$\sqrt{10}$, $d=2$, $q_0=k_0=1$ and $B=1000$. All parameters are illustrative;
none is estimated from an ecological archive. Reproduce the table with:

```bash
make measure-intervention PY=python3.11
```

| Overhead c | Small-bin resource S / Q | Small-bin counts S / Q | Total expected count S / Q |
|---|---|---|---|
| 0 | 50.00% / 50.00% | 90.91% / 90.91% | 214.976 / 214.976 |
| 10 | 50.00% / 25.96% | 74.04% / 50.00% | 50.000 / 35.533 |
| 1000 | 50.00% / 9.49% | 50.85% / 9.90% | 0.980 / 0.953 |

The percentages describe the share of expected resource or expected count in
the smaller bin, not an average of normalized individual censuses. At $c=10$,
the predicted resource share differs by about 24 percentage points. This is
an algebraic separation between the models, not a power calculation for a
particular observation design.

With equal $B$ and any finite $c>0$, $N_Q<N_S$: Q shifts resource toward larger
sizes, where inverse cost is smaller. At very large $c$, both total counts
approach $B/(q_0c)$, yet their normalized bin profiles remain different. S's
count and resource shares tend to log-size widths divided by $L$; Q's tend to
$(v_r-v_\ell)/(v(b)-v(a))$. Total abundance alone can therefore lose discrimination
even while profiles differ. Large overhead also compresses the log-cost span,
making independent cost calibration especially demanding.

## What an empirical test would still need

The exchangeability postulate does not show that a natural system remains
eligible after an overhead change. A causal test must declare observable
admission conditions and the assumed stability of the allocation rule before
evaluation. Restricting the test afterward to communities that match either
forecast would make it circular. This design establishes conditional predictions;
it does not supply the missing natural-regime rule or justify an intervention
that changes growth, mortality, access or other resources in unspecified ways.

Cost calibration must independently determine $q(k)$ and its uncertainty over
the full retained domain. A bulk ratio $R_j/N_j$ is an abundance-weighted class
mean; it does not determine costs at bin boundaries. Choosing cost proportional
to inverse evaluated abundance would manufacture agreement. Estimating costs
from evaluated stock/count pairs also forfeits an independent cost forecast.
If costs vary at fixed size,
a reference based on $\ln E[q\mid k]$ is a different hypothesis from neutrality
in actual individual log costs; the latter needs joint size–cost information.

The observation design must distinguish the predicted profiles after propagating
cost uncertainty, class recovery and biological dependence. Neither postulate
implies Poisson counts, multinomial sampling or an effective sample size.
Available resource equals allocated $B$ only with a separately justified
exhaustion condition. Normalized expected-stock profiles eliminate unknown $B$;
averaging normalized catches generally changes the target.

This note extends the repository's measure-dependence argument into an explicit
design consequence. It uses elementary change of variables and integration;
no priority claim is made for a new mathematical theorem. Existing allocation
models also need separate support for their objectives, as illustrated by
[Kelly, Maulloo and Tan (1998)](https://www.statslab.cam.ac.uk/~fpk1/rate.html)
and the repository's [two-budget comparison](restriction-study.md). The new
question here is which physical reference measure, if either, survives a
separately measured cost change. The current empirical records do not resolve it.
