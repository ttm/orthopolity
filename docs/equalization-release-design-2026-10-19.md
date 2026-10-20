# Next prediction: transfer exchange kinetics, and distinguish exchange from loss

19 October 2026. **Design derivation and source qualification, not an executed
empirical test or a preregistration.** The first cross-domain forecast programme
is complete. Its next step should connect the [equalizing mechanism](class-exchange.md)
to measured exchange between independently defined resource classes. This note
specifies a prediction and an observation ambiguity that a usable dataset must
resolve. The accompanying [source audit](equalization-source-audit-2026-10-19.md)
finds accessible candidates, but none yet qualifies the complete test.

**20 October qualification:** the positive-stock loss counterexample below
does not cover an initially empty acceptor becoming occupied. The
[observation note](exchange-observability-2026-10-20.md) distinguishes evidence
of influx from conservative kinetic transfer and derives sharp retention
bounds for rejecting loss-only explanations.

The mathematical statements below are elementary consequences of the existing
linear exchange model, not claims of new spectral theory. They add a concrete
experimental design to the general-law programme. Ordinary diffusion makes the
same predictions in its domain; a successful test would establish that physical
realization and its transfer, not uniquely identify a new universal mechanism.

## The physical comparison must come first

Let disjoint compartments have resource stocks $R_i$, independently known
positive reference weights $w_i$, and symmetric exchange conductances $g_{ij}$.
The model is

$$\dot R_i=-\sum_jg_{ij}(R_i/w_i-R_j/w_j),\qquad B=\sum_iR_i.$$

In a molecular transport experiment, $R_i$ can be solute amount and $w_i$
compartment volume, so $R_i/w_i$ is concentration. For a membrane with
independently calibrated permeability $P$ and area $A$, $g=PA$ has units of
volume/time. Uniform concentration then means equal solute per volume, not
equal solute per unequal compartment. Equal-volume compartments also supply
an ordinary counting measure.

This spatial measure is **neither log-orthopolic nor linear-orthopolic size
allocation**. Those readings require size classes and their respective
$d\ln k$ or $dk$ widths. A successful compartment experiment cannot silently
establish either size-distribution claim. Nor does a spatial compartment become
a size class merely because its volume is known.

The resource, volumes, topology and observation response must be fixed without
using the target allocation to choose them. Calibrating conductance on a
separate two-compartment experiment is legitimate; estimating it anew from the
target network would discard the proposed transfer.

## Two predictions from the same calibration

For two compartments with one conductance $g$, define
$\delta=R_1/w_1-R_2/w_2$. After a constraint is removed and exchange is the
only process,

$$\delta(t)=\delta(0)e^{-\lambda_2t},\qquad
\lambda_2=g(1/w_1+1/w_2),$$

$$R_1(t)=\frac{Bw_1}{w_1+w_2}+
\left(R_1(0)-\frac{Bw_1}{w_1+w_2}\right)e^{-\lambda_2t}.$$

This predicts both the final allocation and its rate of approach. If a separate
intervention multiplies $g$ by a known factor $c>0$, the endpoint is unchanged
and the relaxation rate multiplies by $c$. A change of volume instead changes
both endpoint and rate. Neither follows from conservation alone.

A more discriminating topology transfer uses a pair to calibrate a **five-node
linear chain**. Assume identical compartment weights $w$, identical edge
conductances $g$, no end leakage and no additional connections. If $L_5$ is
the unit-conductance path Laplacian, the entire withheld trajectory is

$$R(t)=\exp[-(g/w)L_5t]R(0).$$

The path eigenvalues are $2[1-\cos(j\pi/5)]$, $j=0,\ldots,4$. Thus the
slowest nonconstant mode has rate
$\lambda_5=2(g/w)[1-\cos(\pi/5)]$, while the equal-volume pair has
$\lambda_2=2g/w$. Their exponential time constants obey

$$\frac{\tau_5}{\tau_2}
=\frac{1}{1-\cos(\pi/5)}=3+\sqrt5\simeq5.23607.$$

**No kinetic parameter is fitted to the five-compartment response.** The final
shares are $1/5$ and the full curve is fixed by the pair calibration and
measured initial condition. The factor 5.236 applies to the slowest mode, not
an arbitrary threshold time for "reaching equilibrium." That mode must be
excited by the initial condition and observed by the measurement; loading one
end compartment and measuring all five satisfies this requirement.

If volumes or membrane areas differ, use their measured values in
$-L_gW^{-1}$ and predict the resulting spectrum. Do not retain the simple ratio
or adjust geometry to reproduce a measured relaxation time. Uncertainty in
pair calibration, geometry, timing and optical response must enter the target
forecast before the target curves are decoded.

## Why positive normalized shares need not establish exchange by themselves

Suppose unobserved loss rates $\ell_i(t)\ge0$ accompany exchange:

$$\dot R=-L_gW^{-1}R-\operatorname{diag}(\ell)R.$$

Set $S=\sum_iR_i$, $p_i=R_i/S$, and
$\bar\ell=\sum_i\ell_ip_i$. Since exchange conserves total resource,

$$\dot p=-L_gW^{-1}p+
\operatorname{diag}(\bar\ell\mathbf1-\ell)p.$$

A **common fractional loss** $\ell_i(t)=\ell(t)$ cancels exactly. Therefore
normalization is not automatically invalid: under independently justified
common loss and compatible observation gains, relative shares still obey the
exchange equation. Normalization neither creates equality nor validates those
assumptions. Unequal losses leave a term that can masquerade as redistribution.

An exact counterexample makes the issue concrete. In dimensionless model time,
unit-weight compartments exchanging at $g=1$, with initial shares $(1/4,3/4)$,
have the conserved-resource path

$$p_1(t)=\tfrac12-\tfrac14e^{-2t},\qquad
p_2(t)=\tfrac12+\tfrac14e^{-2t}.$$

Now define another system with **no exchange**:

$$\widetilde R_i(t)=e^{-2t}p_i(t),\qquad
\ell_i(t)=2-\dot p_i(t)/p_i(t).$$

Both loss rates are nonnegative for $t\ge0$, and
$\dot{\widetilde R}_i=-\ell_i\widetilde R_i\le0$. Nevertheless,
$\widetilde R_i/\sum_j\widetilde R_j=p_i(t)$: its normalized trajectories
are identical to genuine equalization at every time. At $t=1$, only
$e^{-2}\simeq0.1353$ of the original total remains. An absolute stock or
flux measurement distinguishes the systems immediately; normalized shares do
not. This is a constructed identifiability counterexample, not a finding that
any particular experiment suffered these losses.

This example starts with both compartments occupied. A verified zero-to-positive
stock change rules out loss alone; normalized observations can establish that
narrower fact under a valid observation model. They still do not establish
conservation or transferable rates. See the dated qualification above.

## What qualifies an empirical run

Before freezing a numerical test, the archive must support:

1. **Objects and measure:** disjoint compartments or modes with independently
   justified weights; measured resource stocks rather than an arbitrary signal
   called a resource.
2. **Transferable kinetics:** separate conductance calibration and compatible
   chemistry, geometry and boundary conditions in the target. Pair and chain
   pH or membrane composition cannot be changed without an independent correction.
3. **Intervention and observables:** an identified constraint change or topology
   change, measured initial conditions and enough observations to resolve the
   predicted modes. A steady endpoint alone does not identify the kinetics.
4. **Observation and loss controls:** absolute measurements or independent
   evidence that loss and detection gains preserve the declared shares. A
   constant total imposed during preprocessing cannot verify conservation.
5. **An informative comparison:** persistence, instantaneous mixing and any
   source-supported loss/partition alternatives, with tolerances based on
   measurement uncertainty and scientific relevance. If ordinary diffusion
   coincides with the orthopolity realization, report that equivalence openly.

Then freeze the full prediction, train only on the designated calibration,
verify and commit forecasts, and evaluate a separate response. Known published
results stay disclosed. If the source fails a gate, stop before fitting; the
failure is design qualification, not evidence against the law.

## Calculation checks

`build/main-venv-2026-10-09/bin/python experiments/check_equalization_design.py`
checks the closed-form ratio against independent numerical eigenvalues,
compares a matrix-exponential trajectory with direct integration of edge
balances, and verifies the loss-only counterexample's nonnegative losses and
identical normalized path. On Python 3.11 the two trajectory calculations differ
by less than $9\times10^{-13}$; the normalized counterexample agrees within
$2\times10^{-16}$. These are checks of analytic examples, with no real data,
randomized study, empirical decision or new run-registry entry.
