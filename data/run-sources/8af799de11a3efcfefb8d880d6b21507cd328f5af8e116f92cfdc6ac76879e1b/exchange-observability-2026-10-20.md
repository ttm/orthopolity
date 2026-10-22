# What normalized exchange measurements can establish

20 October 2026. This is a qualification of the
[19 October exchange design](equalization-release-design-2026-10-19.md), not an
empirical result or a registered study. The earlier counterexample is valid for
its **positive initial stocks**. It does not show that losses can reproduce
solute appearing in a genuinely empty compartment. That distinction matters
for the droplet experiments, whose preparation specifies unloaded acceptors.

The resource is solute amount in disjoint compartments. Compartment volumes
define the reference weights for concentration equalization; equal volumes
also permit ordinary counting measure. This is **neither log-orthopolic nor
linear-orthopolic size allocation**. The following observation bounds apply
to stock shares irrespective of those volume weights.

## Influx and conservative exchange are different claims

Write total stock as $S(t)>0$, shares as $p_i(t)=R_i(t)/S(t)$, and retained
fraction as $q(t)=S(t)/S(0)$. Under a loss-only explanation, each compartment's
stock is nonincreasing. Consequently,

$$q(t)p_i(t)\le p_i(0)\quad\text{for every }i.$$

An exactly empty compartment remains empty under loss alone. Thus a verified
zero-to-positive stock share establishes influx or production, even if total
retention was not measured. Identifying *intercompartment exchange* additionally
requires excluding production and outside inputs. Optical background, detector
cross-talk, changing fluorescence yield and a detection limit must be addressed
before interpreting a signal increase as increased solute amount. An unloaded
preparation is useful evidence, but not an exact measurement of zero.

This does not establish conservation, the exchange route, or a kinetic rate.
Common fractional losses remain invisible in normalized shares. Differential
losses can distort an actual exchange trajectory even when they cannot explain
the initial appearance of solute. Pair-to-chain transfer still requires
compatible independently specified geometry, observation response and kinetics.

## A sharp endpoint test using total retention

For exact endpoint shares, define

$$a(t)=\min_{i:p_i(t)>0}\frac{p_i(0)}{p_i(t)}.$$

The loss-only explanation requires $q(t)\le a(t)\le1$. Hence the **minimum
total loss needed to reproduce those endpoints** is $1-a(t)$. For positive
endpoint shares and $a(t)>0$ the bound is sharp: set final stocks to $a(t)S(0)p_i(t)$;
each is at most its initial stock. Monotone stock interpolation realizes the
endpoints with losses only. It need not reproduce the intervening share path.
If $a(t)=0$ because a previously empty compartment becomes positive, no
positive-total loss-only realization exists.

A conservative criterion with measurement bounds is

$$q_{\mathrm{lower}}(t)\,p_{i,\mathrm{lower}}(t)
  >p_{i,\mathrm{upper}}(0).$$

This certifies a net stock increase in compartment $i$. The bounds must cover
joint measurement uncertainty; nominal separate confidence intervals cannot
silently be called a joint confidence statement. Neither fitting total loss
from the target shares nor imposing a constant total during normalization
supplies the needed independent retention bound.

For the earlier example $p_1(t)=1/2-e^{-2t}/4$,
$p_2(t)=1/2+e^{-2t}/4$, the sharp retention ceiling is

$$a(t)=\frac1{2-e^{-2t}}.$$

At $t=1$, losses of at least **46.37%** are needed to explain the endpoints
without influx. The earlier constructed example lost 86.47%; it demonstrated
possibility, not minimal loss. An independent retention lower bound above
53.63% would rule out *all* loss-only explanations of these exact endpoints.
These numbers describe an analytic example, not measured droplet losses.

## More observations can strengthen the test

For strictly positive shares observed at times $t_0<\cdots<t_m$, set

$$a_r=\min_i\frac{p_i(t_{r-1})}{p_i(t_r)},\qquad
q_{\max}(t_m)=\prod_{r=1}^{m}a_r.$$

Each step requires $q_r\le a_r q_{r-1}$, with $q_0=1$. Taking equality at
every step attains the largest possible final retention; the resulting stock
sequence is nonincreasing in every coordinate. Piecewise exponential decay of
each stock gives a loss-only realization at all sampled times with finite
nonnegative rates. This is a test of the **sampled path**, not proof of an
unobserved continuous trajectory between samples.

For example, shares $(0.2,0.8)\to(0.8,0.2)\to(0.2,0.8)$ return to their
initial values. Their endpoints alone require no loss, whereas reproducing all
three observations without influx requires at least **93.75% loss**. Independent
retention information can therefore distinguish mechanisms even without a
complete set of absolute compartment trajectories.

Support expansion (a zero becoming positive) makes positive-total loss-only
realization impossible. A positive stock becoming exactly zero requires an
infinite integrated fractional loss rate, though a general nonnegative loss
flux can deplete it. The finite-rate construction above deliberately assumes
strictly positive shares.

For a positive continuously differentiable share path, the analogous sharp
envelope is

$$q_{\max}(t)=\exp\left[-\int_0^t
     \max_i\frac{\dot p_i(s)}{p_i(s)}\,ds\right].$$

To prove it, write $h=-\dot q/q$. Nonincreasing stocks require
$h\ge\dot p_i/p_i$ for every compartment. Their weighted mean is zero, so
the maximum is nonnegative. Choosing $h=\max_i\dot p_i/p_i$ attains the bound,
with nonnegative loss rates $\ell_i=h-\dot p_i/p_i$. This is an elementary
identifiability result, not a claim of a new physical law. Numerical derivatives
of noisy observations should not be inserted into this formula without a
separately justified observation model.

## Consequence for source qualification

The [Bachler et al. methods](https://doi.org/10.1021/acs.analchem.0c04939)
specify fluorophore-free acceptors. This makes the blanket suggestion that
losses alone could explain their entire donor-to-acceptor experiment too broad.
We have not independently validated their optical baseline or raw observations.
The unresolved task is **quantitative kinetic transfer**, rather than proving
that no transport took place. Source-specific losses and signal calibration
still matter to that task.

A source can now qualify a test rejecting loss alone with reliable stock shares and an
independent total-retention bound, without measuring every absolute stock.
That narrower test must be labelled as such; it does not replace the full
pair-to-network forecast. This refinement avoids rejecting useful measurements
merely because they are normalized.

`experiments/check_exchange_observability.py` checks the discrete formula
against independently formulated linear programs, checks the continuous
example by quadrature and loss-rate integration, and exercises zero-support
and uncertain-retention cases. These are analytic verification examples, with
no experimental response inputs, empirical verdict or new registry entry.
