# Cosmic mechanism audit: when does material transport imply neutrality?

11 November 2026. Development-stage audit of the
[cosmological extension](cosmological-extension.md). This document uses primary
literature and mathematical derivation; it does not fit a catalogue, inspect a
held-out abundance target or execute a cosmic empirical test. Every size-allocation
statement below concerns **log-orthopolic physical mass allocation**, not
linear-orthopolic allocation and not a resource power selected to flatten data.

**Decision:** the stationary transport derivation is correct conditionally.
Gravitational assembly, self-similarity and ordinary halo growth rates do not by
themselves establish its conditions. A public-data development diagnostic can
qualify the material mapping, locality, sources and stationarity. A frozen
abundance test is premature until those gates and independent prediction inputs
pass. This is an eligibility finding, not an empirical rejection of the conjecture.

## 1. What the proposed mechanism actually assumes

Fix one cosmology, comoving volume convention, epoch window, disjoint host
definition and finite mass interval. Let $x=\ln(M/M_0)$ and
$n(M,t)=dN/(dV_c\,dM)$. If the tracked material accounts for the declared mass
of each host, then

$$r(x,t)=M^2n(M,t).$$

With material current $J$, source/loss density $s$ and a local advective
closure $J=vr$, continuity gives

$$\partial_t r+\partial_xJ=s.$$

Stationarity and no interior sources make $J$ independent of $x$. A positive
drift $v=v_0$ independent of $x$ then gives $r=J/v_0=C$ and $n=C/M^2$.
The residence time per equal logarithmic width $\Delta x$ is $\Delta x/v_0$.
Boundary inflow and outflow maintain this throughflow. A closed finite inventory
moving only toward greater masses cannot sustain it indefinitely without a
boundary supply or recycling mechanism.

The model's three separate requirements are therefore **constant current,
constant residence time per logarithmic interval, and a valid local transport
description**. No cosmological argument in the existing appendix has yet shown
that all three hold for an independently selected population and interval.

## 2. A quantitative approximate-neutrality gate

For differentiable positive $r,v,J$ with $J=vr$, direct differentiation gives

$$\partial_x\ln r
=\frac{s-\partial_t r}{J}-\partial_x\ln v.$$

If, throughout an interval of logarithmic width $L$,

$$\frac{|s|}{J}\le\epsilon_s,\qquad
\frac{|\partial_t r|}{J}\le\epsilon_t,\qquad
|\partial_x\ln v|\le\epsilon_v,$$

then integration yields the sufficient bound

$$\left|\ln\frac{r(x)}{r(y)}\right|
\le(\epsilon_s+\epsilon_t+\epsilon_v)|x-y|,\qquad
\frac{\sup r}{\inf r}\le
e^{(\epsilon_s+\epsilon_t+\epsilon_v)L}.$$

These are our mathematical consequences, not a fitted cosmological result.
They show why a small slope difference can matter across many decades. For
illustration, to guarantee a maximum-to-minimum ratio at most 1.20 across two
decades using this bound, the sum must be no larger than
$\ln(1.20)/\ln(100)\simeq0.0396$. This number illustrates the calculation; it
is not a frozen empirical tolerance. The condition is sufficient, not necessary:
source, time and drift contributions can cancel.

If additional transport has flux $K$, so $J=vr+K$, the exact relation becomes

$$\partial_x\ln r
=\frac{s-\partial_t r-\partial_xK}{J-K}-\partial_x\ln v,
\qquad J-K=vr>0.$$

Local diffusion can enter through $K$; large jumps may require an explicitly
nonlocal current. Declaring $K$ negligible needs an independent error bound.
Estimating all terms and the target $r$ from the same snapshots can diagnose
the closure, but does not independently confirm its abundance forecast.

## 3. Halo histories are not automatically material trajectories

For an ideal merger $M+\xi M\longrightarrow(1+\xi)M$, material in the main
progenitor moves by $\Delta x=\ln(1+\xi)$, whereas material in the secondary
moves by $\Delta x=\ln[(1+\xi)/\xi]$. Even a minor merger can therefore combine
a short main-branch step with a long jump of incoming material. This exact
kinematic example prevents using a small main-branch increment as the sole
locality criterion. All material transfers, losses and unresolved components
matter to the mass-weighted current.

Fakhouri, Ma and Boylan-Kolchin (2010, Sections 2.3 and 3.2) define their
growth rate from a descendant and its most massive progenitor; at fixed
redshift their fitted mean scales as $\langle\dot M\rangle\propto M^{1.1}$.
They also distinguish halo mass conventions and diffuse contributions.
These are simulation-derived growth statistics, not a direct measurement of
the local material drift required here.
[Primary paper](https://arxiv.org/html/1001.2304v2).

As a **constructed sensitivity**, identifying $v$ with
$\langle\dot M\rangle/M$ would give $v\propto M^{0.1}$ and, under the additional
stationary source-free closure, $r\propto M^{-0.1}$ and $n\propto M^{-2.1}$.
Across two decades the high-mass/low-mass resource ratio would be
$100^{-0.1}\simeq0.631$, or a maximum/minimum ratio of about 1.585.
This is not a valid cosmic forecast without establishing the identification;
it shows that even this familiar near-linear growth formula does not impose
constant residence time.

Mass-definition evolution is another gate. Diemer, More and Kravtsov (2013)
show that an evolving spherical-overdensity boundary can change catalogue halo
mass even for a stationary physical density profile. Such pseudo-evolution
must be represented in the catalogue-to-material mapping; it cannot silently
be called physical inflow. An exclusive particle-membership mass and a
spherical-overdensity mass also cannot be interchanged in calibration and target.
[Primary paper](https://arxiv.org/abs/1207.0816).

## 4. Self-similarity does not force an exponent of two

An independently specified scale-free power spectrum provides a useful analytic
comparator. Write its spectral index as $n_s$ to distinguish it from number
density, with $P(\kappa)\propto\kappa^{n_s}$ and $-3<n_s<1$. For spherical
top-hat smoothing, $\sigma(M)\propto M^{-\beta}$ with
$\beta=(n_s+3)/6$. Define $\nu=\delta_c/[D(t)\sigma(M)]$.
The Press--Schechter form gives

$$n_{\rm PS}(M,t)=\sqrt{\frac2\pi}\frac{\bar\rho}{M^2}
\beta\nu e^{-\nu^2/2},\qquad
r_{\rm PS}=\sqrt{\frac2\pi}\bar\rho\beta\nu e^{-\nu^2/2}.$$

These standard ingredients appear in Bagla, Khandai and Kulkarni (2010,
equations 1, 2, 4 and 7). Their simulation study also finds dependence on
the initial power spectrum despite self-similar evolution.
[Primary paper](https://arxiv.org/pdf/0908.2702).

Our differentiation yields

$$\frac{d\ln r_{\rm PS}}{d\ln M}=\beta(1-\nu^2),\qquad
\alpha_{\rm PS}\equiv-\frac{d\ln n_{\rm PS}}{d\ln M}
=2-\beta+\beta\nu^2.$$

For example, $n_s=-2$ gives $\beta=1/6$ and low-$\nu$ density exponent
$\alpha\simeq11/6$, with resource rising as $M^{1/6}$. This supplies a
counterexample to inferring exact log-orthopolic mass allocation from
self-similarity alone. It does not contradict the transport theorem under
that theorem's stronger conditions. The formal $n_s\to-3$ limit needs its
own cutoff/variance treatment; it cannot justify an exact universal plateau.

## 5. What makes the second prediction independent

A boundary current $J_{\rm in}$ and an independently calibrated drift profile
give the stationary source-free forecast

$$\widehat n(M)=\frac{J_{\rm in}}{v(\ln(M/M_0))M^2},\qquad
\widehat{N}_{[a,b]}/V_c=
\int_a^b\frac{J_{\rm in}}{v(\ln(M/M_0))M^2}\,dM.$$

Constant $v$ recovers the appendix's amplitude and count prediction. A useful
validation design freezes how development histories determine the inputs,
then predicts a separate population or realization. Boundary flux can be an
allowed measured input in a conditional forecast; if it uses the same system
as the target, its selection and uncertainty dependence must be declared.
The target's occupancy cannot determine $J$ through $J=vr$, determine a fitted
$v=J/r$, or choose the mass interval after seeing which portion is flat.

Multiple descendants drawn from the same initial realization are not independent
cosmic replicates. A separate realization, appropriate spatial blocking or a
validated shared-error model is needed. A forecast across epochs additionally
needs evidence that calibration and target share the specified transport law;
an expanding universe does not supply stationary comoving mass spectra by default.

## 6. Comparators, contribution and gate decision

The transport equation is conventional conservation. Its neutral solution is
not a new gravitational law derived independently of the allocation premise.
The possible contribution is a successful reduction of assembly information to
an independently predictive resource allocation, with explicit domain and
failure bounds. Existing models that imply the same forecast belong under an
orthopolic interpretation; matching them cannot uniquely favor the framework.

Use a mass-definition-compatible conventional halo mass function as a rival,
fixed from external/development inputs. Press--Schechter supplies an analytic
baseline; a calibrated model is a stronger comparator in its valid domain.
Tinker et al. (2008) provide spherical-overdensity fits and explicitly report
epoch- and mass-definition-dependent departures from universality. Those fits
cannot be applied directly to an incompatible exclusive-membership catalogue.
[Primary paper](https://arxiv.org/abs/0803.2706).

| Gate | Current assessment | Required development evidence |
|---|---|---|
| Mathematical implication | Pass, conditional | Positive local drift/current and finite declared interval; formulas above |
| Resource and host definition | Unqualified | Full disjoint material assignment matching the mass coordinate, including diffuse/lost components and boundary conventions |
| Locality and residual flux | Unqualified | Material transitions and temporal-resolution checks; bounds on omitted long jumps or diffusion |
| Stationarity and sources | Unqualified | Independent development bounds tight enough for the declared interval and tolerance |
| Independent normalization | Unqualified | A reproducible input/target split that does not infer current or drift from target occupancy |
| Competing prediction | Specifiable, not executed | Fixed compatible established model plus direct-transfer baseline, with an observation/error model |

Proceed with bounded public-source qualification and a development diagnostic.
Do not promote a main-branch growth fit or an observed near-minus-two slope
to a ready abundance test. Failure of one gate should identify the needed
repair or close that particular source/model route, preserving the conjecture's
explicit status and the recorded negative finding.
