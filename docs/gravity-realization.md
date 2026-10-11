# Newtonian gravity: source accounting, angular allocation and shell energy

10 October 2026. This supporting derivation develops the manuscript's
general-law programme through an established physical example. It separates
the exact gravitational relations from their interpretation as allocation,
and complements [electromagnetic transport](physical-realizations.md).
No new observations or empirical fits are reported.

## Fixed-source field relation

Consider Newtonian gravity in Euclidean three-dimensional space, with a
stationary, nonnegative mass density of finite total mass. The potential
satisfies

$$\mathbf g=-\nabla\Phi,\qquad \nabla^2\Phi=4\pi G\rho.$$

Here $\mathbf g$ is acceleration, not an energy current. These are the
standard Newtonian equations; their regime is weak gravity and slow matter
motion, rather than arbitrary relativistic dynamics. See
[Tong, *General Relativity*, introduction](https://www.damtp.cam.ac.uk/user/tong/gr/grhtml/S0.html)
and [Section 5.1.2](https://www.damtp.cam.ac.uk/user/tong/gr/grhtml/S5.html).

Our boundary accounting follows directly by the divergence theorem. For a
closed surface $S=\partial V$, with outward unit normal $\mathbf n$,

$$\Psi(S)=-\int_S\mathbf g\cdot\mathbf n\,dA
=4\pi G\int_V\rho\,dV=4\pi G M_{\rm enc}.$$

The inward field flux $\Psi$ has units $\mathrm{m^3\,s^{-2}}$.
Dividing by $4\pi G$ reconstructs the enclosed mass. Every complete surface
enclosing the same source and no additional mass gives the same value.
This equality across surfaces is a spatial field constraint. It is not a
claim that mass or energy flows through those surfaces.

The nested enclosed volumes represent the same source repeatedly. Although
their boundaries can be geometrically disjoint, the reconstructed masses
cannot be summed as independent source stocks. For two nested surfaces,

$$\Psi(S_2)-\Psi(S_1)=4\pi G M_{V_2\setminus V_1}.$$

Additional intervening mass changes the equality by an independently
specified amount. External sources contribute zero net flux through a
closed surface but can change its local field.

## Spherical symmetry identifies the comparison measure

For an isolated spherical source of radius $r_0$ and mass $M$, on
$r_0<r\le R$,

$$\mathbf g(r)=-\frac{GM}{r^2}\widehat{\mathbf r},\qquad
d\Psi=\frac{GM}{r^2}dA=GM\,d\Omega.$$

Spherical symmetry makes the inward field flux equal per solid angle
$d\Omega$, at every exterior radius. Equal-area patches on any one sphere
also carry equal flux, while flux per unit area decreases as $r^{-2}$.
The reference measure for the angular equality is $d\Omega$; it is neither
linear-orthopolic nor log-orthopolic allocation over radius. There is no
radial object-abundance density in this calculation.

This supplies a precise connection to the manuscript: a fixed source has
the same complete boundary representation at each radius, while its field
concentration per area falls as the available area increases. Calling this
an orthopolic realization is an interpretation of the specified source/field
accounting. The Poisson equation and spherical symmetry supply the physics;
the interpretation does not independently derive Newton's force law or
the abundance of gravitating bodies.

Inside a spherical distributed source the same calculation instead gives
$|\mathbf g(r)|=GM(<r)/r^2$. For uniform density $\rho_0$ this is
$4\pi G\rho_0r/3$: acceleration grows linearly. For a nonspherical source,
the surface integral remains exact, but local radial and tangential fields
need not follow the spherical profile. Thus a measured nonuniform field
requires the actual source geometry, rather than an arbitrary correction
chosen from its residuals.

## Disjoint shell energy is a different quantity

For an isolated, sufficiently regular continuous source with finite
self-energy and $\Phi\to0$ at infinity, integration by parts gives

$$U=\frac12\int\rho\Phi\,d^3x
=-\frac{1}{8\pi G}\int|\nabla\Phi|^2\,d^3x.$$

The conventional field representation therefore assigns density
$u_g=-|\mathbf g|^2/(8\pi G)$. Its integral is negative gravitational
binding energy, relative to assembly from infinite separation. This
representation and its exterior spherical contribution are discussed by
[Chao (2014), Appendix](https://doi.org/10.1093/gji/ggu301).
The shell calculation below uses that specified representation; spatial
localization is not a unique independently measured gravitational energy
stock. In particular, the matter-based and field-based expressions above
agree globally under the boundary conditions, not region by region.

For an exterior shell $r_0<a<b\le R$, direct integration gives

$$U_{[a,b]}=-\frac{GM^2}{2}\left(\frac1a-\frac1b\right),
\qquad \frac{dU}{dr}=-\frac{GM^2}{2r^2},
\qquad \frac{dU}{d\ln r}=-\frac{GM^2}{2r}.$$

Neither equal radial widths nor equal logarithmic widths contain equal
field-representation energies. If the positive weight $dB_g=-dU$ is
defined, it is uniform in inverse-radius width $d\mu=dr/r^2$.
That coordinate identity is not an independently selected radial
allocation law. The weight is a binding-energy magnitude, not an available
positive fuel budget. Extending a point-source expression to $r=0$ gives a
divergence; the exterior lower boundary must be retained. The source's
interior energy requires its density profile.

## Constraints, motion and the scope of the realization

A supported object illustrates how a force persists without its free-motion
signature. With upward coordinate $z$ and approximately constant $g$,
$m\ddot z=-mg+F_{\rm support}$. A support force $mg$ holds the object at
rest. After release with initial velocity $v_0$, its trajectory is
$z(t)=z_0+v_0t-gt^2/2$ until another interaction intervenes. These outcomes
follow from specified forces and initial conditions. They motivate testing
constraints by their predicted response, but do not demonstrate a resource
equalizer hidden in an unrelated abundance distribution.

The established result is equal complete source accounting and, under
spherical symmetry, equal field flux per solid angle. Disjoint shell
energy has the different profile derived above. Both fit an allocation
discussion only with their quantity, measure and assumptions retained.
Newtonian static equations supply no finite-speed recovery law for a change
in the source; gravitational radiation and strong-field situations require
a relativistic treatment. The general-law ambition concerns whether this
explicit organization extends usefully across physical systems, with new
consequences beyond these already established equations.
