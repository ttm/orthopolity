# Orthopolity: definitions and limits

This is a reconstruction of the idea, not a claim that the source essays already supplied
these distinctions. [The source audit](source-audit.md) identifies where the reconstruction
changes the original statements. The [manuscript](paper.md) gives the full argument.

## 1. Specify what is equal

For object size $k$ on a declared domain $D$, choose a reference measure $\mu$ and an additive
per-object resource $q$. Write $n_\mu=dN/d\mu$ and $\bar q(k)=E[q\mid k]$. Then

$$\mathcal O_\mu(k)=\frac{dR}{d\mu}=\bar q(k)n_\mu(k).$$

The arithmetic mean is required because total resource is count times arithmetic mean.
Log-resource regression generally targets a different conditional quantity; retransformation
requires an error model. Resources need not be dynamically conserved for their totals to
be additive. Currency, energy, biomass, and person-hours cannot be combined without a
defined resource model and compatible units.

**Orthopolity relative to $\mu$** is the hypothesis $\mathcal O_\mu(k)=C>0$ on $D$.
It is equivalent to inverse mean-cost abundance. For positive finite
$Z=\int_D1/\bar q\,d\mu$, object density is $p_N=1/(Z\bar q)$ and resource-weighted
size density is uniform with respect to $\mu$. This equivalence is not a generative mechanism.

## 2. Linear and logarithmic allocation differ

With $\bar q(k)=q_0(k/k_0)^d$:

| Reference measure | Equipartition implies |
|---|---|
| Counting measure on predefined discrete classes | Expected count of class $j$ proportional to $1/\bar q_j$ |
| Linear size $dk$ | $dN/dk\propto k^{-d}$ |
| Log size $d\ln(k/k_0)=dk/k$ | $dN/dk\propto k^{-(d+1)}$ |

The 2017 manuscript explicitly writes a uniform density over a linear interval of wealth.
Replacing it by logarithmic intervals is a different hypothesis. Ecology supplies a strong
reason to examine the log version, but conservation does not select it.

For $q=k=m$, logarithmic biomass allocation predicts:

| Quantity | Predicted slope or exponent |
|---|---|
| Abundance per log mass | slope −1 |
| Abundance density per unit mass | slope −2 |
| Biomass per log mass | slope 0 |
| Biomass per unit mass (normalized biomass spectrum) | slope −1 |
| Survival probability, away from a remote upper cutoff | exponent 1 |
| Rank-size, away from cutoffs | exponent 1 |

These are representations of the same log-allocation model, not interchangeable observed
slope labels. On finite support $[a,b]$, with $d>0$,

$$P(K\ge k)=\frac{k^{-d}-b^{-d}}{a^{-d}-b^{-d}}.$$

The cutoff term matters. Equal nonzero resource per log interval on an unbounded domain
has infinite total resource, even when the count density normalizes.

Changing measurement units or logarithm base preserves flatness. A power reparameterization
$z=(k/k_0)^c$ with fixed $c>0$ also does, up to a constant. Arbitrary transformations do not.
Selecting the coordinate or measure to flatten the observed data defeats a test.

## 3. The hypothesis needs independent content

For any positive $n_\mu$, one can choose $\bar q=C/n_\mu$. This proves that resource
definition must precede, or be independently justified from, the abundance being explained.

The exact case $q=k=m$ is informative: mean resource is fixed by definition and cannot be
adjusted to fit abundance. When fluence is modelled from peak irradiance, the cost exponent
is estimated and adds another assumption. An exponent gap then tests the joint model;
it does not uniquely identify which assumption failed.

Counts of cubes that *could* fit in a room are capacities, not observations of coexisting
objects. Oscillation frequency is cycles per time, not a probability of observing wavelengths.
A deterministic power response, such as a psychophysical law, is not a size distribution.

## 4. Neither conservation nor uniformity of ignorance derives it

A finite budget fixes $\int_D\mathcal O_\mu\,d\mu$, not its shape. All normalized
$\mathcal O(u)\propto e^{\beta u}$ on a bounded log-domain can have the same budget.

Maximum entropy over equally weighted discrete object classes, with a fixed mean resource,
gives $p_j\propto e^{-\lambda q_j}$. Other constraints or reference measures can give other
distributions. There is no measure-free uniform distribution.

Orthopolity alone also permits non-power abundance. For $\bar q(k)=q_0e^{k/k_0}$,
logarithmic allocation gives $dN/d\ln k\propto e^{-k/k_0}$ and
$dN/dk\propto e^{-k/k_0}/k$. Calling both an exponential distribution would omit the Jacobian.

In geometric examples, $d$ can be a dimension. In general it is a scaling exponent.
Products of deterministic power cost factors have exponents that add under their specified
common coordinate. Products of independent random quantities need not have summed tail
exponents. Two independent unit-scale Pareto variables with exponent $h+1$ have product
density $h^2z^{-h-1}\ln z$ for $z\ge1$.

## 5. Stocks, event totals, and fluxes

A biomass spectrum describes standing resource. Summed event fluence describes an accumulated
quantity during an observation window. A flux through size classes describes transfer.
They have different physical units and interpretations. Constant flux does not imply
constant standing stock per scale, and neither follows from the accounting identity.

## 6. Individual flatness and ensemble statements

For $\mathcal O_i(u)=A_i e^{\beta_i u}$, the following are distinct:

- A system is flat: $\beta_i=0$, together with absence of curvature.
- Mean slopes are zero: $E[\beta_i]=0$.
- Median slopes are zero.
- Mean resource spectrum is flat: $E[\mathcal O_i(u)]$ is constant.

For common $A_i=A$ and Gaussian zero-centred slopes,

$$E[\mathcal O_i(u)]=Ae^{\tau^2u^2/2}.$$

Even equal-total normalized spectra with opposite slopes average to a nonconstant cosh
profile on a symmetric domain. Therefore the earlier claim that orthopolity “holds in the
mean” does not follow from the observed median slope near −1.

Mean and variance do not imply Gaussian shape. Choosing a Gaussian is an extra assumption.
A fitted dispersion and a matching in-sample fraction do not independently validate it.
Observed pass-rate predictions must include observation errors, fitted location, and the
same sample and tolerances used for the observed rate.

For two resources in a single system,

$$\frac{\mathcal O_1(k)}{\mathcal O_2(k)}
=\frac{\bar q_1(k)}{\bar q_2(k)}.$$

Both can be flat only if their mean-cost ratio is constant. Across systems the slope
difference equals the cost-exponent difference. Equal variances and perfect correlation
require that difference to be system-invariant and nonzero slope variance; they are not
general consequences of ensemble equipartition.

## 7. What a credible test records

Define the system population, objects, resource, coordinate, reference measure, domain,
exposure or sampling weights, missing-data policy, and scientific tolerance. Report the
resource profile with uncertainty as well as any fitted slope. Preserve empty classes.
Distinguish resource-mean modelling error from allocation error.

A factor-$F$ endpoint drift for a power-shaped spectrum on log-width $L$ means
$|\beta|\le\ln(F)/L$. A pointwise band $\phi\in[1/F,F]$ is a separate criterion.
Its simultaneous uncertainty cannot be inferred from a slope interval or from pointwise
overlap alone. Failing an equivalence test is not itself evidence of a nonzero effect.
