# Hidden link storage: identical pairs, different network predictions

23 October 2026. **A perfect pair fit and conserved observed stock do not
establish that the links have negligible capacity.** An omitted link store can
be invisible in pair calibration yet change a five-chamber relaxation time by
58.34%. This is an exact constructed counterexample to an inadequately qualified
reduced model, not an empirical failure of orthopolity or of conservative
exchange on the complete system. It refines the
[19 October prediction](equalization-release-design-2026-10-19.md) before any
network target access. No observed outcome selected the example.

Reference weights are physical capacities: solute volume, heat capacity, or
electrical capacitance. Concentration, temperature relative to a fixed reference,
or voltage is resource divided by capacity. This is **neither log-orthopolic
nor linear-orthopolic size allocation**. The calculations below use nonnegative
concentrations and conserve resource over chambers **and** links.

## A link that the usual pair calibration cannot measure

Two well-mixed chambers have equal capacity $w>0$. Their connector contains a
well-mixed store with capacity $c>0$, with conductance $h>0$ to each chamber.
Writing chamber concentrations as $x_1,x_2$ and connector concentration as $y$,

$$w\dot x_1=h(y-x_1),\qquad
  c\dot y=h(x_1+x_2-2y),\qquad
  w\dot x_2=h(y-x_2).$$

The full resource is $B=w(x_1+x_2)+cy$. Set
$x_1(0)=a$, $x_2(0)=b$ and $y(0)=(a+b)/2=\mu$. Then

$$y(t)=\mu,\qquad
  x_{1,2}(t)=\mu\mathbin{\pm}\frac{a-b}{2}e^{-ht/w}.$$

Every positive $c$ gives exactly the same two measured trajectories, conserved
observed chamber total $w(a+b)$, and endpoint $\mu$. The pair contrast rate is
$\lambda_-=h/w$. A zero-storage reduction would infer effective direct-link
conductance $g=h/2$ and fit perfectly. The full budget $B=(2w+c)\mu$ differs
across capacities: the ambiguity is an unmeasured physical store, not identical
independently known whole-system inventories. For arbitrary connector initial
conditions the contrast still has rate $h/w$, but the chamber sum can reveal
the missing capacity.

## Why the five-chamber prediction changes

Connect five identical chambers in a path, using four of these identical link
stores. In concentration coordinates $z$ ordered chamber/link/chamber,

$$W\dot z=-hL_9z,\qquad
  W=\operatorname{diag}(w,c,w,c,w,c,w,c,w).$$

Here $L_9$ is the unit path Laplacian. If $c/w\to0$, eliminating the massless
links gives a five-node path with conductance $h/2$, recovering

$$\frac{\tau_5}{\tau_{\mathrm{pair}}}=3+\sqrt5=5.236068.$$

If $c=w$, the complete system is a homogeneous nine-node path. Its slow rate
is $2(h/w)[1-\cos(\pi/9)]$, so

$$\frac{\tau_5}{\tau_{\mathrm{pair}}}
 =\frac{1}{2[1-\cos(\pi/9)]}=8.290859.$$

The same pair calibration now leads to a slow time 58.34% greater than the
zero-storage forecast. Both systems remain connected, symmetric and conservative.

This difference need not be exposed by a drifting chamber total or a changed
endpoint. Use chamber concentrations
$\mu+(A,0,0,0,-A)$ and connector concentrations
$\mu+(A/2,0,0,-A/2)$ initially, with $\mu\ge |A|>0$.
Reflection-odd deviations remain odd. The observed chamber stock stays exactly
$5w\mu$, every chamber tends to $\mu$, and the slow odd mode is excited and
visible in endpoint concentrations. The full budget is $(5w+4c)\mu$.
Alternatively, loading one end chamber and leaving all other stores empty
excites the slow mode but also produces observable transfer into the links.
The ratio concerns the slow mode, not an arbitrary threshold time.

## Quantitative qualification with independently bounded capacity

Let $r=c/w$ and write the slow rate as $(h/w)s_1(r)$. The smallest positive root
of

$$r^2s^4-(3r^2+4r)s^3+(2r^2+9r+4)s^2-(4r+6)s+1=0$$

is $s_1(r)$, and the time ratio is $1/s_1(r)$. The quartic follows by restricting
the nine-node weighted path to reflection-odd modes, whose central chamber is
zero relative to equilibrium. A weighted path's first nonconstant mode has one
sign change and is odd, so this root is the full spectral gap.

| Independently specified $c/w$ | Five-chamber / pair slow time |
| ---: | ---: |
| 0 (massless-link limit) | 5.236068 |
| 0.01 | 5.264516 |
| 0.05 | 5.378923 |
| 0.10 | 5.523257 |
| 0.50 | 6.720962 |
| 1.00 | 8.290859 |
| 2.00 | 11.549905 |
| 10.00 | 38.612125 |

Increasing $c$ enlarges $W$ at fixed Laplacian. The generalized eigenvalue
min–max principle makes ordered relaxation rates nonincreasing; the slow time
increases here. Independent bounds on $c/w$ therefore bound the forecast.
For illustration, limiting the slow-time increase relative to the massless-link
prediction to 5% requires $c/w\le0.0912414$ in **this specific model**. This is
not a universal geometric threshold, an experimental confidence interval, or a
registered accuracy gate. Distributed connectors, partition coefficients,
adsorption, unequal links and external losses require their own model and bounds.

## A separate pair measurement can resolve the ambiguity

Excite the pair's common mode as well as its contrast. With $S=x_1+x_2$,

$$\frac{d}{dt}(S-2y)=-h\left(\frac1w+\frac2c\right)(S-2y),
  \qquad\lambda_+=\frac hw+\frac{2h}{c}.$$

Thus independently measured mode rates give

$$\frac cw=\frac{2}{\lambda_+/\lambda_- -1}.$$

For example, prepare both chambers at concentration one and the connector at
zero. Every $c$ then has the same known full budget $2w$, and

$$S(t)=\frac4{2+r}+\frac{2r}{2+r}
             e^{-(h/w)(1+2/r)t}.$$

The sum's endpoint also gives $r=4/S(\infty)-2$. Small $r$ makes the common
mode both fast and low-amplitude, demanding adequate time resolution and optical
precision. Unknown external losses, gain drift or an uncertain connector initial
condition can confound this measurement. Those controls must be qualified
independently; the new network response must not be used to estimate $c$.

The revised route is concrete: fix the resource and reference measure; measure
or bound connector storage independently; qualify both pair modes where needed;
then seal the complete network forecast before observing its transient. A failed
five-node forecast with unqualified connector storage would diagnose a reduction
problem, not distinguish a failure of the full equalization mechanism.

## Verification and scope

`make topology-design PY=build/main-venv-2026-10-09/bin/python` verifies retained
source hashes and the three analytic design checks. The new checker compares
generalized eigenvalues with the independently reduced quartic, closed pair and
common-mode formulas, and direct edge-flux ODE integration for seven fixed
capacity ratios. The ODE check uses Radau because small connector capacities
introduce stiff fast modes. An unconstrained explicit solver initially failed
the cross-check; reducing its step size also resolves the discrepancy.
Spectral and nonsymmetric matrix-exponential propagation agreed independently.
No tolerance was relaxed to accept the failed calculation.

The [source audit](topology-source-audit-2026-10-23.md) records accessible but
ineligible datasets and remaining leads. None of these analytic constructions
adds an empirical result, changes an existing frozen result, or uniquely
identifies orthopolity over ordinary diffusion/circuit theory.
