# Effective resources, nonlinear composition, and inverse inference

This note develops the composite-resource formulation of the proposed general
orthopolity law. A system can allocate an operative combination of resources,
with its form determined by the medium, constituent interactions, and available
processes. The forward theory predicts abundance from that effective resource
and its constraints. The inverse theory uses abundance to identify candidate
effective costs and then confronts them with constituent measurements and
interventions. The notation extends [the mathematical formulation](paper.md)
and the [class-exchange demonstration](class-exchange.md).

## 1. Nonlinear composition within objects, additivity across objects

For object $j$, record a vector $\mathbf q_j=(q_{1j},\ldots,q_{mj})$ of
constituent resources in their own units. Choose fixed positive reference
scales $s_\ell$ in those same units, and let $z_{\ell j}=q_{\ell j}/s_\ell$.
A candidate effective resource is

$$Q_j=Q_0 F(\mathbf z_j;\eta_j,\theta),\qquad
Q_{\mathrm{total}}=\sum_jQ_j,\qquad Q_0>0.$$

Here $Q_0$ sets the effective-resource unit, $\eta_j$ describes the declared
environment, and $\theta$ contains constitutive parameters. The scales,
environmental variables, functional form, and parameter-estimation procedure
are specified explicitly. The scales cannot be chosen separately in each
observed abundance bin to manufacture equalization. Unit changes leave each
$q_\ell/s_\ell$ unchanged when $s_\ell$ is converted consistently.

The function $F$ may be nonlinear: for positive inputs, examples include
$\prod_\ell z_\ell^{\omega_\ell}$ and
$(\sum_\ell\beta_\ell z_\ell^p)^{1/p}$, with nonnegative weights and $p>0$.
These are candidate constitutive forms. Dimensional consistency alone does
not establish that either is the quantity redistributed by a physical system.
An effective cost needs a physical process, measured response, or specified
optimization model that makes its combination operationally meaningful.

The distinction in the first equation is essential: $F$ combines constituents
**within an object**, whereas different objects contribute by summation.
Generally $\sum_jF(\mathbf z_j)\ne F(\sum_j\mathbf z_j)$. If pair or collective
interactions carry additional resource, those terms must be included explicitly
or assigned to objects by a declared accounting convention without double
counting. Additivity of the complete resource is then an additional modeling
property, not a consequence of writing down $F$.

The object partition is itself physical input. With $F(X,Y)=XY$, one object
holding $(X,Y)=(1,1)$ contributes $Q_0$. Replacing it by two objects each
holding $(1/2,1/2)$ preserves both constituent totals but gives only $Q_0/2$.
Thus nonlinear composition can depend on actual assembly or fragmentation;
arbitrary regrouping of the same observations cannot be treated as invariant.

## 2. Class means and the surviving constituent budgets

Fix the positive size coordinate $k$, finite domain $D$, and reference measure
$\mu$. Let $n_\mu(k)=dN/d\mu$ be population abundance, and define

$$q_{\mathrm{eff}}(k)=E[Q\mid k]
=Q_0E[F(\mathbf q/\mathbf s;\eta,\theta)\mid k]>0,
\qquad \frac{dQ_{\mathrm{total}}}{d\mu}
=q_{\mathrm{eff}}(k)n_\mu(k).$$

The expectation averages objects conditional on size, including constituent
variation, dependence, and environmental heterogeneity within that class.
Replacing it by $Q_0F(E[\mathbf q\mid k]/\mathbf s;\eta,\theta)$ generally
changes the quantity. For fixed $\eta,\theta$ and convex $F$, Jensen's inequality
gives $E[F(\mathbf z)\mid k]\ge F(E[\mathbf z\mid k])$; a concave $F$ reverses
the inequality. This established averaging result is presented in
[Boyd and Vandenberghe's convex-function lectures, slide 3.14](https://stanford.edu/~boyd/cvxbook/bv_cvxslides.pdf).

Every constituent retains its own accounting:

$$R_\ell=\sum_jq_{\ell j}
=\int_D\bar q_\ell(k)n_\mu(k)\,d\mu(k),\qquad
\bar q_\ell(k)=E[q_\ell\mid k].$$

The physical model must still impose its separate equalities, capacity bounds,
sources, sinks, and exchanges for these $R_\ell$. A scalar effective resource
does not erase a vector constraint. Simultaneous neutrality of all constituents
would require $\bar q_\ell(k)/\bar q_r(k)$ to be independent of $k$ wherever
both are positive; this is a stronger condition than neutrality of one composite.

A weighted linear cost can arise from the multipliers of a specified constrained
optimization problem, with units that convert the constituent constraints into
objective units. Scalarization and the local sensitivity interpretation of dual
multipliers are standard results; their assumptions and meanings are developed in
[Boyd and Vandenberghe, *Convex Optimization*, Sections 4.7 and 5.6](https://www.stanford.edu/~boyd/cvxbook/bv_cvxbook.pdf).
Such weights depend on that problem and its environment. General nonlinear $F$
needs its own constitutive justification; it does not follow from linear
scalarization alone.

Additivity and conservation also differ. Even if every $R_\ell$ is conserved,
$Q_{\mathrm{total}}$ need not be. For example, redistributing one constituent
from dimensionless object holdings $(1,3)$ to $(2,2)$ conserves their sum, but
$F(z)=z^2$ changes the effective total from $10Q_0$ to $8Q_0$. For differentiable
$F$, a fixed population, and fixed $Q_0,\mathbf s,\theta$, its balance is instead

$$\dot Q_{\mathrm{total}}=Q_0\sum_j
\left[\sum_\ell\frac{\partial F_j}{\partial z_\ell}
\frac{\dot q_{\ell j}}{s_\ell}
+\nabla_\eta F_j\mathbin{\cdot}\dot\eta_j\right].$$

Births, losses, or changing constitutive parameters require their corresponding
terms. Applying the conservative class-exchange model to $Q$ therefore requires
a mechanism that conserves this particular effective quantity.

## 3. Forward allocation under a declared constraint

Let $a(k)>0$ describe the constrained allocation profile on the accessible
domain, with $a(k)=1$ in the neutral case. It is supplied by the mechanism or
independent constraint measurements. For example, the class-exchange model has
$a(k)=e^{-V(k)}$ on its discrete classes. The forward relation is

$$q_{\mathrm{eff}}(k)n_\mu(k)=C a(k),\qquad
n_\mu(k)=\frac{C a(k)}{q_{\mathrm{eff}}(k)},\qquad C>0.$$

All integrals below are assumed finite. If the total effective resource is
known, $C=Q_{\mathrm{total}}/\int_Da\,d\mu$; if total abundance is known instead,
$C=N/\int_D(a/q_{\mathrm{eff}})\,d\mu$. Separate constituent capacities still
require, for example,

$$C\int_D\frac{a(k)\bar q_\ell(k)}{q_{\mathrm{eff}}(k)}\,d\mu(k)
\le B_\ell\quad\text{for each constrained constituent }\ell.$$

Equality replaces the inequality for a closed, fully accounted constituent
stock. Choosing a composite does not guarantee these conditions. Their failure
identifies a missing constraint or an unsuitable effective-resource mechanism.

For a finite class $B\subset D$, the population relations are integrals:

$$N_B=C\int_B\frac{a}{q_{\mathrm{eff}}}\,d\mu,\qquad
Q_B=C\int_Ba\,d\mu,\qquad
\bar Q_B=\frac{Q_B}{N_B}
=\frac{\int_Ba\,d\mu}{\int_B(a/q_{\mathrm{eff}})\,d\mu}.$$

Thus the appropriate finite-bin effective cost is an abundance-weighted class
mean, equivalently the displayed harmonic mean with weights $a\,d\mu$. A
midpoint cost times the count is an approximation unless costs are constant
within the bin. For an actual finite sample, $Q_B^{\mathrm{obs}}=
N_B^{\mathrm{obs}}\bar Q_B^{\mathrm{obs}}$ is an exact accounting identity,
but random observed counts need not equal population expectations. Empty sample
bins do not justify inferring infinite physical cost by taking their reciprocal.

## 4. What the inverse direction identifies

For positive population densities at $k$ and a reference point $k_*$,

$$\frac{q_{\mathrm{eff}}(k)/a(k)}
{q_{\mathrm{eff}}(k_*)/a(k_*)}
=\frac{n_\mu(k_*)}{n_\mu(k)}.$$

The abundance shape identifies $q_{\mathrm{eff}}/a$ up to scale under the
allocation relation. A known $a$ then identifies relative effective costs.
An independent effective-resource total or cost calibration can fix the scale.
If $a$ is unknown, replacing both $q_{\mathrm{eff}}$ and $a$ by their product
with any positive function leaves the abundance unchanged. Even with known
$a$, many constituent combinations and joint distributions can share the same
conditional mean $q_{\mathrm{eff}}$: abundance alone does not identify them.

For logarithmic size, $d\mu=d\ln(k/k_0)=dk/k$. If the object probability density
with respect to $dk$ satisfies $f(k)\propto k^{-(1+\alpha)}$ on the declared
domain, then

$$n_{\log}(k)=Nkf(k)\propto k^{-\alpha},\qquad
\frac{q_{\mathrm{eff}}(k)}{a(k)}\propto k^\alpha.$$

Hence $d\ln q_{\mathrm{eff}}/d\ln k=\alpha+d\ln a/d\ln k$ when these
derivatives exist. The observed exponent constrains an effective cost relative
to the imposed allocation profile; identifying a constituent requires more
information than identifying this ratio.

## 5. Product composites and conditional scaling

For deterministic constituent curves $q_\ell(k)/s_\ell=b_\ell(k/k_0)^{d_\ell}$
and $F(\mathbf z)=\prod_\ell z_\ell^{\omega_\ell}$, direct substitution gives

$$q_{\mathrm{eff}}(k)=Q_0\prod_\ell b_\ell^{\omega_\ell}
(k/k_0)^{d_{\mathrm{eff}}},\qquad
d_{\mathrm{eff}}=\sum_\ell\omega_\ell d_\ell.$$

More generally, let $q_\ell/s_\ell=b_\ell(k/k_0)^{d_\ell}Y_\ell$ within each
class. Its effective cost includes
$M(k)=E[\prod_\ell Y_\ell^{\omega_\ell}\mid k]$, assumed finite and positive,
so its log slope is $\sum_\ell\omega_\ell d_\ell+d\ln M/d\ln k$. Correlations
and changes in within-class heterogeneity can therefore change the prediction.
These are conditional scaling statements along a common size coordinate.
They are not rules for adding the distributional tail exponents of products
of random variables.

## 6. An algebraic inverse-recovery example

Take the neutral logarithmic model with a fixed $\gamma>0$ and

$$q_{\mathrm{eff}}(k)=Q_0[A+B(k/k_0)^\gamma],\qquad A>0,\ B\ge0,
\qquad \frac{dN}{dk}=\frac{C}{kq_{\mathrm{eff}}(k)}.$$

The capital coefficients avoid confusing the baseline $A$ with the constraint
profile $a(k)$. Write $z_i=(k_i/k_0)^\gamma$ and
$r=n_{\log}(k_1)/n_{\log}(k_2)$ for $k_2>k_1$. Then

$$r=\frac{1+(B/A)z_2}{1+(B/A)z_1},\qquad
\frac BA=\frac{r-1}{z_2-rz_1}.$$

For finite $B/A$, the allowed ratio satisfies $1\le r<z_2/z_1$.
As an exact toy instance, $A=2$, $B=3$, $\gamma=2$, and $k/k_0=1,2,4$ give
$q_{\mathrm{eff}}/Q_0=5,14,50$ and
$n_{\log}=(C/Q_0)(1/5,1/14,1/50)$. The first two classes give $r=14/5$,
and the inverse formula recovers $B/A=(14/5-1)/(4-14/5)=3/2$.
The third class supplies a predicted ratio under the same parameters.

This is algebraic recovery in a constructed model, not an empirical finding.
The ratio does not fix $Q_0A$ separately from $C$. Unknown $\gamma$ requires
additional information; near the regime dominated entirely by $Bz$, recovering
the baseline is poorly conditioned because the denominator approaches zero.
For finite bins, use the integrated count prediction from Section 3 rather
than treating bin averages as these pointwise values.

## 7. Identifying a nonlinear combination across environments

Consider $Q=Q_0X^aY^b$, where $X,Y$ are dimensionless constituent quantities
normalized by fixed physical scales. Here $a,b$ are composition exponents,
while the allocation profile in environment $s$ is written $a_s(k)$.
Assume the same exponents apply across environments, with independently known
deterministic relations

$$X_s(k)=A_{1s}(k/k_0)^{d_{1s}},\qquad
Y_s(k)=A_{2s}(k/k_0)^{d_{2s}},\qquad
V_s(k)=v_s\ln(k/k_0),\qquad a_s(k)=e^{-V_s(k)}.$$

The forward logarithmic abundance has exponent
$\alpha_s=ad_{1s}+bd_{2s}+v_s$. Equivalently, a density
$f_s(k)\propto k^{-(1+\alpha_s)}$ implies

$$\alpha_s-v_s=ad_{1s}+bd_{2s}.$$

For an untruncated Pareto tail with $\alpha_s>0$, $\alpha_s$ is also its
survival exponent; on a bounded domain the exact statement concerns the
density exponent. Two independently characterized environments with
$(d_{11},d_{21})=(1,1)$, $(d_{12},d_{22})=(1,2)$ and corrected slopes
$\alpha_1-v_1=1.5$, $\alpha_2-v_2=2$ give $a+b=1.5$ and $a+2b=2$.
Thus $a=1$, $b=1/2$: the inverse candidate is $Q=Q_0X\sqrt Y$.
A third environment with $(d_{13},d_{23})=(2,1)$ predicts
$\alpha_3=2.5+v_3$ without changing the composition exponents.

This is a constructed identification and prediction example. Its uniqueness
requires the constituent-exponent matrix to have full column rank, known
constraint slopes, and shared composition parameters. Proportional exponent
rows would identify only one combination of $a,b$. With heterogeneous objects,
the relevant quantity is $Q_0E[X^aY^b\mid k,s]$; class-dependent fluctuations
add the correction in Section 5 and must be identified separately. Slopes
alone leave $Q_0$ undetermined; an absolute resource or cost anchor is needed.

## 8. Turning inverse candidates into explanatory results

Inverse inference is useful for discovering which resource combinations to
measure and which interventions distinguish them. Record the fixed measure,
domain, constraints, constituent scales, and candidate family first. Estimate
the remaining parameters with an explicit observation model, preserving
uncertainty, within-class variation, and separate constituent budgets. Then
measure the implied effective cost or predict another profile or controlled
environmental change with the same constitutive specification.

Defining $q_{\mathrm{eff}}=Ca/n_\mu$ from a profile makes its allocation relation
hold identically. That step is an inverse reconstruction, so evaluating the
same profile is not an additional validation of the inferred resource.
Independent constituent information and successful transferred or intervention
predictions give the composite proposal explanatory content.
