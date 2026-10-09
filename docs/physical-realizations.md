# A worked physical realization: radial electromagnetic transport

5 October 2026. This derivation extends the [existing radiation example](model-sources.md#6-equal-radial-throughput)
into a neutral prediction, a specified medium constraint, and a predicted
response when that constraint is removed. It supplies one physical realization
for the [research programme](research-brief.md), followed by a map of the
retained empirical cases. The calculations below specialize established energy
conservation and radiation transport equations; they introduce no new physical
law and change no registered study result.

## 1. What is shared, and what is compared?

Consider a source enclosed by a sphere of radius $r_0>0$, with outward emitted
power $L$. Compare spherical surfaces $S_r$ outside that source, within a
finite domain $r_0\le r\le R$. The transported resource is electromagnetic
energy; its rate of transfer across a sphere is

$$P(r,t)=\int_{S_r}\mathbf S\cdot\mathbf n\,dA,$$

where $\mathbf S$ is the Poynting vector, $P$ has units W, and $\mathbf n$ is
the outward radial normal. The proposed equality in this comparison is
$P(r)=L$: every enclosing surface receives the same **throughput**. Successive
surfaces count the passage of the same energy. Their powers are not additive
shares of a finite resource stock.

For the local intensity and shell-stock calculations, additionally assume
outgoing radial propagation at a constant speed $c$, with isotropic,
cycle-averaged or ensemble-averaged emission. This is a radiation-zone,
ray-transport idealization outside the near field. There is no incoming
radiation, scattering or secondary emission in the modeled component. One may
use a fixed frequency band, or a grey coefficient over a declared spectrum;
frequency-dependent absorption requires separate spectral equations.

## 2. Conservation gives equal throughput

In the microscopic Maxwell description, with charge currents represented
explicitly, electromagnetic energy obeys

$$\partial_t u+\nabla\cdot\mathbf S=-\mathbf J\cdot\mathbf E,
\qquad
u=\frac{\epsilon_0|\mathbf E|^2}{2}
 +\frac{|\mathbf B|^2}{2\mu_0},
\qquad
\mathbf S=\frac{\mathbf E\times\mathbf B}{\mu_0}.$$

This is Poynting's energy balance, derived from Maxwell's equations. Its
historical source is [Poynting (1884)](https://doi.org/10.1098/rstl.1884.0016)
([accessible transcription linked to original pages](https://en.wikisource.org/wiki/On_the_Transfer_of_Energy_in_the_Electromagnetic_Field));
a modern derivation is [Haus and Melcher, Section 11.2](https://web.mit.edu/6.013_book/www/chapter11/11.2.html).

Integrating over the volume between two spheres gives

$$\frac{dU_{[r_1,r_2]}}{dt}+P(r_2,t)-P(r_1,t)
=-Q_{[r_1,r_2]}(t),$$

where $U$ is field energy in that volume and $Q$ is power transferred from
the field to matter there. The sign of the inner-sphere contribution is
negative because the shell's outward normal points inward on its inner face.
For steady or period-averaged stationary transport through a transparent,
source-free shell, both the accumulation term and $Q$ vanish. Hence

$$P(r_2)=P(r_1)=L.$$

This equality needs no angular isotropy. Isotropy is needed for the stronger
pointwise statement that the radial energy-flux density $F$ is the same at
every location on a sphere. Under that added assumption,

$$F(r)=\frac{P(r)}{4\pi r^2}=\frac{L}{4\pi r^2}.$$

Without isotropy, this expression remains the **sphere-averaged radial flux
density**, while local values can depend on direction. In particular,
conservation does not make an anisotropic emitter isotropic. $F$ has units
W/m² and is not the specific intensity per solid angle used in radiative
transfer notation; the distinction is explained in [Condon and Ransom,
Section 2.1](https://www.cv.nrao.edu/~sransom/web/Ch2.html).

We have obtained equal total passage at every radius together with an unequal
local concentration of the flow. The inverse-square factor describes how the
same power crosses larger areas; it does not contradict the throughput
equality.

## 3. A prescribed medium produces a quantitative departure

Let an absorbing medium have a nonnegative, independently specified absorption
coefficient $\kappa(r)$, with units m⁻¹. In the radial transport approximation,
absorption deposits power density $\kappa F$ in the medium. Thus the power
removed in a shell of thickness $dr$ is $\kappa(r)P(r)dr$, giving

$$\frac{dP}{dr}=-\kappa(r)P(r),\qquad P(r_0)=L.$$

This is an effective model for absorption with fixed propagation speed. It
does not substitute the vacuum expression for $u$ into a general dispersive
material, whose energy storage and transport require additional constitutive
information.

The absorption rule and its exponential solution are standard radiative
transfer results; see [Condon and Ransom, Section 2.2.1, equations 2.19–2.24](https://www.cv.nrao.edu/~sransom/web/Ch2.html).
Applying them to this spherical comparison yields

$$P(r)=L e^{-\tau(r)},\qquad
\tau(r)=\int_{r_0}^{r}\kappa(s)\,ds,
\qquad
F(r)=\frac{L e^{-\tau(r)}}{4\pi r^2}.$$

The source power, radius and absorption coefficient are inputs. The unequal
profile follows from them. Its lost radiative power is accounted for exactly:

$$L-P(r)=\int_{r_0}^{r}\kappa(s)P(s)\,ds.$$

Absorbed energy enters matter; the modeled radiation component has an open
budget. A steady material state requires heat removal or another compensating
transfer. Re-emission into the observed component would need a source term,
and scattering would need an angular transport model. Neither is silently
counted as pure absorption here.

For a concrete constraint, prescribe a layer $a<r<b$ with
$r_0<a<b<R$, constant $\kappa_0$, and transparent surroundings:

$$\frac{P(r)}{L}=
\begin{cases}
1,&r\le a,\\
e^{-\kappa_0(r-a)},&a<r<b,\\
e^{-\kappa_0(b-a)},&r\ge b.
\end{cases}$$

If $\kappa_0(b-a)=\ln2$, every sphere outside the layer carries half the
source power. Outside the layer the lower throughput is again constant.
Changing the layer's independently measured optical depth predicts a ratio
$P_{\mathrm{out}}/P_{\mathrm{in}}=e^{-\kappa_0(b-a)}$, without fitting the
downstream allocation profile.

## 4. Removing the constraint predicts a causal recovery

The stationary formula does not specify how quickly the transparent profile
returns. Under the declared radial propagation assumption, $F=cu$. Define
energy per unit radial distance and the associated power by

$$e(r,t)=4\pi r^2u(r,t),\qquad P(r,t)=c e(r,t).$$

The shell balance becomes

$$\partial_t e+\partial_r(c e)=-c\kappa(r,t)e,
\qquad c e(r_0,t)=L(t).$$

Here $e$ has units J/m, so every term in the transport equation has units
W/m. Along a characteristic $dr/dt=c$, one has
$de/dt=-c\kappa e$. The boundary-supplied solution is therefore

$$P(r,t)=L\!\left(t-\frac{r-r_0}{c}\right)
\exp\!\left[-\int_{r_0}^{r}
\kappa\!\left(s,t-\frac{r-s}{c}\right)ds\right].$$

This expression applies when the backward characteristic reaches the supplied
boundary history; earlier characteristics require initial data. The optical
depth is evaluated along the actual travel path in space and time, rather
than at one simultaneous snapshot of the medium.

For an exact clearing experiment, take a constant source $L$, an initially
stationary absorbing profile $\kappa_{\mathrm{old}}(r)$, and prescribe
$\kappa(r,t)=0$ everywhere in the domain for $t\ge0$. This is an idealized
change of the coefficient that adds no radiation to the modeled component.
The characteristic solution reduces, for $t\ge0$, to

$$P(r,t)=L\exp\!\left[-\int_{r_0}^{\max\{r_0,r-ct\}}
\kappa_{\mathrm{old}}(s)\,ds\right].$$

It agrees with the old stationary profile at $t=0$, increases monotonically,
and equals $L$ once $t\ge(r-r_0)/c$. Thus the entire finite domain recovers
by $(R-r_0)/c$. For the isolated layer above, a downstream sphere $r\ge b$
starts responding at $(r-b)/c$ and fully recovers at $(r-a)/c$. These are
travel times, not a diffusive relaxation time or a recovery of already
absorbed energy. Radiation present after clearing carries the change outward.

This worked example makes the constraint explanation predictive: it specifies
the constrained profile, its dependence on an external coefficient, and the
response to removing that coefficient while the source continues operating.

## 5. Throughput and disjoint stocks give different equalities

The same model also defines a genuine stock in each **disjoint shell**. In
the transparent stationary case,

$$dU=e(r)dr=\frac{L}{c}dr,
\qquad
U_{[a,b]}=\frac{L}{c}(b-a).$$

Disjoint shells of equal radial thickness therefore hold equal energy. The
comparison measure is explicitly $dr$. Equal logarithmic intervals instead
have

$$\frac{dU}{d\ln r}=\frac{Lr}{c},$$

which increases with radius. Local energy density is $u=L/(4\pi c r^2)$;
equal volume elements at different radii do not contain equal energy. With
absorption, $dU/dr=L e^{-\tau(r)}/c$ and the unequal shell stocks follow
from the same medium coefficient. All stock statements here concern a finite
radial domain; an eternally driven stationary field over unbounded space
would have infinite total shell energy.

These results demonstrate a physical allocation relation with a declared
measure and an explained departure. They do not identify radial shells with
size classes of organisms, or infer abundance exponents from an inverse-square
flux. Equality among size classes requires its own governing dynamics. Nor
does this derivation establish that orthopolity derives Newtonian gravity:
an inverse-square field, a transported power and a stored energy are distinct
quantities requiring distinct physical arguments.

## 6. Where the retained empirical cases enter

The existing reports address different predictions. Their meanings can be
placed alongside this worked example without treating every observed
non-flat profile as a test of one universal, unconstrained template.

| Case and declared comparison | Retained result | Contribution and remaining constraint explanation |
|---|---|---|
| [Size-selected *Dunaliella*](dunaliella-size-budget.md): biovolume capacity across separately grown lineages in the same medium | Equal-biovolume forecasts transferred across selection treatments; small- and large-selected means differed by about 3% despite a 10.4-fold cell-volume difference. P deprivation produced size-dependent overshoot. | Positive budget-closure and inverse-cost-abundance example across replicate cultures. The binding nutrient and cell quotas were not measured; it is not equality among coexisting size classes. Medium restoration alone did not erase history effects. |
| [Chemostat pulse response](chemostat-response.md): resource composition across algal groups in perturbed food webs | The specified two-budget rule failed effect-size, direction and forecast comparisons; its maximum shift was smaller than the observed shift in every held-out vessel. No held-out vessel met the recovery endpoint within 12 days. | Negative result for that quantitative response model. Grazing, variable quotas and batch/history differences are identified conditions, but their mention does not supply a successful replacement explanation. Equilibrium size-class neutrality was not the tested proposition. |
| [Plant census](plant-biomass-profile.md): measured dry mass in eight half-decade size bins | Realized profiles were uneven; the best transferred mass template varied by plot. Logarithmic neutrality had mean mass TV 0.493, versus 0.470 for the fitted Pareto template. | Direct disjoint-stock observations with mixed template performance. Finite-count normalization and dependence can produce uneven censuses under equal expected stocks, but the ecological observation model is unresolved; these simulations do not explain the actual plant profiles. |
| [Ocean reconstruction](evidence.md#3-ocean-reconstruction): modeled biomass per decade of body mass | The selected upper-ocean plateau had a maximum/minimum ratio 1.7, versus 38.8 across all 23 bins; the plateau selection was post hoc and full-profile equivalence was not established. | Suggestive broad size-class pattern with clear domain and depth dependence. A model-assisted reconstruction does not independently identify the processes causing the departures. |
| [Aquatic study transfer](aquatic-study-transfer.md): published normalized-biomass slopes, whose neutral target is −1 | The fixed −1 center outscored a learned center in 6/8 primary held-out studies, but nominal 95% coverage was about 67%; relative advantage was concentrated in two studies. | Useful relative prediction of a slope center with poor absolute calibration. Full resource profiles, observation conventions and source uncertainties are needed to explain individual departures or establish practical equality. |

For radiation, absorption is an **explicitly modeled and quantitatively
resolved** constraint. In the biological studies, some conditions are measured
and some mechanisms remain candidates. Retaining that distinction permits
productive work on the investigators' central claim: observed distributions
reflect both the proposed allocation tendency and the system in which it acts.
A standing tree or intercepted apple motivates separating contributions from
outcomes; the scientific counterpart is a combined equation that predicts the
outcome and its response to changing the constraint. The radiation calculation
provides that complete sequence for one declared physical comparison.
