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

## 7. Identification and transfer across environments

Fix the logarithmic comparison measure, a common size coordinate $k/k_0$,
the object partition, positive dimensionless constituents $X_\ell$, and a
product family

$$Q=Q_0\prod_{\ell=1}^m X_\ell^{\theta_\ell},\qquad
X_{s\ell}(k)=A_{s\ell}(k/k_0)^{D_{s\ell}},\qquad
a_s(k)=e^{-V_s(k)}=(k/k_0)^{-v_s}.$$

The constituent exponents $D_{s\ell}$ and allocation slopes $v_s$ are
independently specified for each environment $s$. Composition exponents
$\theta$ are shared across environments. The initial result assumes
deterministic class requirements and unrestricted real $\theta$; constraints
on these parameters require the modification below. Environment-specific
positive amplitudes $A_{s\ell}$ and allocation totals affect normalization,
not the slope. Under these assumptions, $n_{\log,s}=C_sa_s/q_{\mathrm{eff},s}$
and $dN_s/dk\propto k^{-(1+\alpha_s)}$ imply

$$b=D\theta,\qquad b_s=\alpha_s-v_s.$$

For an unbounded Pareto tail with $\alpha_s>0$, $\alpha_s$ is also the
survival exponent. On a bounded domain, the exact assertion is about the
density exponent. The amplitudes and slopes do not fix the absolute resource
scale $Q_0$; an independent anchor remains necessary.

**Conditional identification result.** Let $D$ be a fixed $n\times m$ matrix
and $D^+$ its Moore--Penrose inverse. There is an exact compatible composition
if and only if $b\in\operatorname{col}(D)$. When compatible, all solutions
are

$$\theta=D^+b+z,\qquad z\in\ker D.$$

The unrestricted composition is unique if and only if $\operatorname{rank}(D)=m$.
A target environment with constituent row $d_*$ has a unique corrected-slope
prediction if and only if $d_*\in\operatorname{row}(D)$. This can hold even
when the individual components remain unidentified. If $w^\top D=d_*$,
the prediction is $b_*=w^\top b$ and $\alpha_*=w^\top b+v_*$.

**Proof.** Compatibility is exactly membership in the column space. The
Moore--Penrose solution satisfies $DD^+b=b$ for such $b$, and two solutions
differ exactly by a vector in $\ker D$. Their target predictions differ by
$d_*z$. This vanishes for every kernel vector exactly when $d_*$ belongs to
its orthogonal complement, the row space. For unrestricted parameters,
$\ker D=\{0\}$ is equivalent to full column rank. These are standard linear
inverse-problem facts applied to the specified allocation model.

If physical admissibility requires $\theta\in\Theta$, the identified set is
$(D^+b+\ker D)\cap\Theta$. A singleton identifies the composition even if
$D$ lacks full column rank. A target is identified when it is constant on
this intersection; the unrestricted row-space condition remains sufficient
but need not be necessary. The supplied implementation reports unrestricted
identification and does not silently impose positivity or choose a
minimum-norm coefficient vector as the physical answer.

**Parameter-free consequences.** Every left-null vector $\ell$, with
$\ell^\top D=0$, gives

$$\ell^\top b=0.$$

Conversely, satisfying a basis of these $n-\operatorname{rank}(D)$ contrasts
is equivalent to compatibility. This follows because the column space is the
orthogonal complement of $\ker D^\top$. Two calibration environments with
$D_1=(1,1)$, $D_2=(1,2)$ and corrected slopes $(1.5,2)$ identify
$\theta=(1,1/2)$, hence $Q=Q_0X\sqrt Y$. The third constituent row
$D_3=(2,1)=3D_1-D_2$ supplies

$$b_3=3b_1-b_2=2.5,\qquad
\alpha_3=3(\alpha_1-v_1)-(\alpha_2-v_2)+v_3.$$

The third slope must be withheld from composition fitting to serve as this
forecast. In contrast, a two-environment square invertible design fits every
pair of slopes exactly and supplies no remaining compatibility contrast.
For the deficient design with rows $(1,1),(2,2)$, the compatible coefficients
$(1,1/2)$ and $(1/4,5/4)$ give identical slopes $(1.5,3)$. The target row
$(3,3)$ is nevertheless identified at $4.5$; the target $(1,0)$ is not.

**Heterogeneity boundary.** For random within-class constituents,
$q_{\mathrm{eff},s}=Q_0E[\prod X_\ell^{\theta_\ell}\mid k,s]$.
Section 5 gives the additional slope $d\ln M_s(k;\theta)/d\ln k$.
The linear result remains valid if the relevant product moment is independent
of size for the admissible candidates, or its slope is independently known
and included in the correction. If that slope depends on unknown $\theta$,
the inverse problem is generally nonlinear. Marginal constituent means alone
do not justify dropping this term.

## 8. Precision, observation models, and explanatory predictions

Suppose corrected estimated slopes obey
$\widehat b=D\theta+\varepsilon$ with $E[\varepsilon]=0$ and known
positive-definite covariance $\Sigma_b$. For full column rank, generalized
least squares gives

$$\widehat\theta=H\widehat b,\qquad
H=(D^\top\Sigma_b^{-1}D)^{-1}D^\top\Sigma_b^{-1},\qquad
\operatorname{Cov}(\widehat\theta)=(D^\top\Sigma_b^{-1}D)^{-1}.$$

Indeed, minimizing the weighted quadratic gives the normal equations,
$HD=I$ establishes unbiasedness, and multiplying $H\Sigma_bH^\top$ gives
the covariance. The implementation uses whitening and singular-value
decomposition rather than forming these normal-equation inverses.
For a row-space target under deficient rank, minimizing $w^\top\Sigma_bw$
subject to $w^\top D=d_*$ gives the minimum-variance linear unbiased target
estimator. It does not assign unique physical values to unidentified components.

For fixed contrast rows $L$, the contrast estimate and covariance are
$L\widehat b$ and $L\Sigma_bL^\top$. For a calibration-based prediction of
one held-out environment, let $c=(-w^\top,1)^\top$ and retain the covariance
of all corrected slopes, including the held-out estimate. Then

$$r=\widehat b_*-w^\top\widehat b_{\mathrm{cal}},\qquad
\operatorname{Var}(r)=c^\top\Sigma_{\mathrm{joint}}c
=\Sigma_{**}+w^\top\Sigma_{\mathrm{cal}}w
-2w^\top\Sigma_{\mathrm{cal},*}.$$

This variance includes error in both the predicted mean and the held-out
observation. With centered jointly Gaussian errors and fixed weights,
$r/\sqrt{\operatorname{Var}(r)}$ is standard normal under the shared model.
Marginal Gaussian slope errors alone do not establish this joint statement.
The weights used here minimize calibration target-estimation variance;
they are fixed without reading held-out abundance. They are not claimed to
minimize the residual variance over all predictors exploiting correlated
held-out errors. The synthetic study uses an invertible two-row calibration
design, for which the unbiased weights are unique.

Exact known offsets change the mean only. If allocation slopes are estimated,
then with $C_{\alpha v}=\operatorname{Cov}(\widehat\alpha,\widehat v)$,

$$\Sigma_b=\Sigma_\alpha+\Sigma_v-C_{\alpha v}-C_{\alpha v}^\top.$$

An admissible joint covariance and possible offset bias must be addressed;
uncertain offsets cannot be made exact by labeling them constraints. The
implementation checks the joint covariance before applying this expression.

**Conditioning.** With fixed full-column-rank $D$, ordinary least squares and
an arbitrary slope perturbation $e$ give

$$\widehat\theta-\theta=D^+e,\qquad
\|\widehat\theta-\theta\|_2\le
\frac{\|e\|_2}{\sigma_{\min}(D)}.$$

The bound is the operator norm of $D^+$; equality is attainable along the
weakest left singular direction. For $D=((1,1),(1,1+10^{-4}))$,
$e=(0,10^{-3})$ changes the recovered coefficients by $(-10,10)$, even
though the matrix has full rank. Thus numerical rank, precision, and physical
identifiability are different issues. Generalized least squares has the same
bound in whitened coordinates. Numerical rank here uses a declared relative
singular-value tolerance, not a claim that smaller physical effects vanish.

Measurement error in $D$ is a separate problem. One deterministic extension
illustrates its importance: if $\widehat D=D+E$ and
$\|E\|_2<\sigma_{\min}(D)$, then

$$\|\widehat D^+(D\theta+e)-\theta\|_2
\le\frac{\|e\|_2+\|E\|_2\|\theta\|_2}
{\sigma_{\min}(D)-\|E\|_2}.$$

To obtain it, use $\widehat D^+\widehat D=I$ to write the error as
$\widehat D^+(e-E\theta)$ and bound
$\sigma_{\min}(\widehat D)\ge\sigma_{\min}(D)-\|E\|_2$ directly from
the minimum over unit vectors. This bound is conditional on unknown true
quantities; it is not a practical confidence interval by itself. Jointly
measured constituent and abundance data require an errors-in-variables or
joint observation model. The present synthetic calculation holds $D$ exact.

**From calibration to explanation.** Record the measure, support, constraints,
constituent scales, parameter family, and environment split before inspecting
held-out abundance. Infer slopes with an explicit sampling model and integrated
bin probabilities where needed. Propagate uncertainty, within-class variation,
and dependence between environments. Preserve separate constituent budgets.
Then measure the implied effective cost or predict another environment with
the same composition. A violation identifies incompatibility among these
declared assumptions; it does not by itself distinguish a changed resource
combination from an incorrect constraint, constituent measurement, or sampling
model. Diagnose those possibilities with independent information.

Defining $q_{\mathrm{eff}}=Ca/n_\mu$ from a profile makes its allocation
relation hold identically. This is useful inverse reconstruction, but fitting
that same profile is not an additional validation. Selection among multiple
resource families must also be confined to calibration or reported explicitly
as exploratory; a held-out profile cannot both select a family and validate
its frozen forecast. Independent constituent information and successful
transferred predictions supply the additional explanatory content.

The [reproducible inverse-resource demonstration](inverse-resources.md)
checks exact recovery, partial identification, correlated-noise uncertainty,
near-collinearity, and a deliberately changed held-out composition. Its
synthetic outcomes verify the consequences of the assumed model; they add no
natural observations. The linear-algebra results are standard mathematical
tools, and originality is sought in the allocation formulation and the
resource-specific predictions it makes possible.
