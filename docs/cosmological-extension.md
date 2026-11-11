# Orthopolity and cosmic structure

**Exploratory cosmological extension, revised 11 November 2026.** This appendix develops
a specific conjecture from the proposed natural law in the [main article](paper.md).
Its mathematical implications are derived below; its astronomical examples are
interpretations of published results. No new catalogue analysis or empirical
confirmation is reported.

## 1. The cosmological conjecture

**We conjecture that gravitational assembly produces finite regimes of
approximately equal matter allocation per logarithmic host-mass interval.**
The substantive physical proposal is that these regimes arise when material
current and residence time per logarithmic interval become approximately
independent of host mass.
This is a proposed **log-orthopolic cosmological principle**. Its domain must
be located from independently specified dynamics and observational eligibility,
so finding a convenient straight segment in a mass function cannot establish it.

Here "cosmological" concerns the assembly and distribution of cosmic structure.
The standard cosmological principle concerns approximate spatial homogeneity
and isotropy on very large scales: sameness across locations and directions
([ESA, Planck and the cosmic microwave background](https://www.esa.int/Science_Exploration/Space_Science/Planck/Planck_and_the_cosmic_microwave_background)).
Our conjecture concerns allocation across object masses; that spatial symmetry
does not determine a mass spectrum.
The allocation constant $C$ below is set by the selected inventory and mass
range. It is not identified with the cosmological constant $\Lambda$, which
enters the gravitational description of vacuum energy
([Carroll, 2001](https://arxiv.org/abs/astro-ph/0004075)).

## 2. Stars, galaxies and the question to test

Consider a fixed stellar inventory at one epoch. Assign each included star to
exactly one galaxy, and let $\bar k$ be the average number of included stars per
galaxy. Then

$$N_{\rm galaxies}\,\bar k=N_{\rm stars}.$$

Every complete grouping of that same inventory obeys this identity. It is the
exact accounting content of the framework, with a predefined grouping measure;
it is neither a log-orthopolic nor a linear-orthopolic size-allocation test.
Different galaxy-size distributions can have the same total. Diffuse stars
must be included as an explicit additional component or excluded from the
declared inventory. Stellar birth and death also prevent this snapshot identity
from implying conservation of stellar number through time.

The distributional question is sharper. Let $k$ denote stars per galaxy and
$\phi(k)=dN_{\rm galaxies}/dk$ a smooth richness density over a declared range.
The number of stars per logarithmic richness interval is

$$\frac{dN_{\rm stars}}{d\ln k}=k^2\phi(k).$$

**Log-orthopolic allocation predicts $k^2\phi(k)=C$: each decade of galaxy
richness contains the same total number of stars.** Moving to a decade with
ten times richer galaxies gives ten times fewer galaxies. The corresponding
linear-orthopolic prediction would instead be $k\phi(k)=C$; it expresses equal
stars per unit richness, a different physical hypothesis.

Galaxy stellar mass offers an observationally accessible analogue. Turning
stellar mass into star number additionally requires an independently justified
mean stellar mass for each population. A stellar mass function therefore does
not directly measure the richness distribution above.

For either stellar mass or halo mass, define
$n(M,t)=dN/(dV_c\,dM)$ in comoving volume $V_c$ at epoch $t$. Choose one resource
and one object definition. The mass density per logarithmic interval is

$$r(M,t)=\frac{d\rho}{d\ln M}=M^2n(M,t).$$

Log-orthopolic mass allocation has $r=C$ and $n=C/M^2$. Over a finite interval
$I=[M_{\min},M_{\max}]$, its normalization is fixed:

$$\rho_I=C\ln\!\left(\frac{M_{\max}}{M_{\min}}\right).$$

This cannot extend over arbitrarily many decades at fixed positive $C$ and
finite mass density. Both bounds, the epoch window, completeness and mass
estimator belong to the hypothesis. A host and its subhalos must not contribute
the same material twice: use disjoint hosts, an exclusive material assignment,
or a separately declared subhalo population with its own budget.

## 3. Published signs and departures

For $n(M)\propto M^{-\alpha}$, our conversion gives
$r(M)\propto M^{2-\alpha}$. Thus $\alpha=2$ is neutral in mass under the
logarithmic measure; a nearby exponent gives a tilted resource profile. The
following readings were made after seeing the published exponents and remain
exploratory. Their domains and resource definitions are different.

| Population and published result | Log-orthopolic mass reading |
|---|---|
| COSMOS2015 galaxies near $z=5$: low-mass Schechter slope $-2.11_{-0.13}^{+0.30}$. | The fitted low-mass component has $r\propto M^{-0.11}$, compatible with neutrality within the quoted uncertainty. The inferred slope depends on the observational error model used in correcting Eddington bias. [Davidzon et al. (2017)](https://arxiv.org/abs/1701.02734). |
| Aquarius dark-matter subhalos: simulated $dN/dM\propto M^{-1.9}$ over resolved ranges. | $r\propto M^{0.1}$ is close to flat per decade but differs systematically over a wide range. This is a simulation result, with stripping and subhalo selection relevant to interpretation. [Springel et al. (2008), Section 3.1](https://arxiv.org/html/0809.0898v1). |
| GAMA nearby galaxies, $z<0.06$: double Schechter fit with low-mass exponent $-1.47$. | Where that component dominates well below the cutoff, $r\propto M^{0.53}$. The full mass function includes a second component and an exponential cutoff; it is not neutral mass allocation. [Baldry et al. (2012)](https://arxiv.org/abs/1111.5707). |
| Stellar initial mass function: adopted high-mass exponent approximately $-2.3$ in Kroupa's Galactic-field description. | The corresponding birth-mass allocation has $r\propto M^{-0.3}$, with slope changes at lower masses. Birth masses of individual stars are a different population from total stellar masses of galaxies. [Kroupa (2001), Section 2](https://arxiv.org/html/astro-ph/0009005v2). |

The early-to-late galaxy contrast suggests a useful question: can independently
measured assembly, star formation and loss processes predict the change in
resource profile? The table itself cannot identify such a mechanism. Replacing
physical mass by a power of mass chosen to flatten each row would only construct
a new resource hypothesis.

## 4. A conditional mechanism with a further prediction

Equal current through size classes does not by itself imply equal stored mass.
The amount present also depends on how long material stays in each class.
To make that distinction explicit, track fixed mass elements by their host-mass
coordinate $x=\ln(M/M_0)$, where $M_0$ is a fixed reference mass. The assigned
resource must equal the catalogue mass of each host for $r=M^2n$ to hold;
tracking only a tracer subset would require its own resource per host. In a
local transport approximation, let $r(x,t)$ be the mass density per $dx$,
$J(x,t)$ its current, and $s(x,t)$ its source or loss density:

$$\partial_t r+\partial_x J=s,\qquad J=v(x,t)r(x,t).$$

Here $v$ is the material-weighted drift in log host mass. In a stationary,
source-free interior, $J$ is constant in $x$. If $v=v_0>0$ is also independent
of $x$, then

$$r=\frac{J}{v_0}=C,\qquad n(M)=\frac{J}{v_0M^2}.$$

This is an exact conditional derivation within the transport model. It describes
throughflow maintained at the interval boundaries. Its cosmological hypothesis
is that gravitational assembly supplies those conditions over a finite regime.
Tracking material matters: a continuity equation for halo counts would miss
the mass reassigned by mergers. Large merger jumps can invalidate the local
approximation, diffusion requires an additional flux term, and accretion from
an untracked diffuse component introduces sources. These effects require a
justified transport model before applying the stationary result. Applying it
to galaxy stellar mass additionally requires the effects of star formation
and stellar mass loss to be specified independently.

The same model gives a prediction beyond matching an exponent. Independently
specified positive currents $J_i$ and drifts $v_i$ in two eligible environments
predict, for $0<a<b$ within the second environment's declared mass interval,

$$\frac{C_2}{C_1}=\frac{J_2/v_2}{J_1/v_1},\qquad
\frac{N_{[a,b],2}}{V_{c,2}}=\frac{J_2}{v_2}
\left(\frac1a-\frac1b\right).$$

The target is the second environment's abundance, including its normalization.
Estimating $J_2$ as $v_2r_2$ from that target would make the test circular.
Independent development data or a separately calibrated dynamical model must
supply the inputs before the target mass function is examined. With variable
$v(x)$, the stationary prediction becomes $r(x)=J/v(x)$, providing a specified
departure that can also fail.

## 5. What would advance the conjecture

Self-similarity alone does not establish the needed residence times. Scale-free
cosmological simulations retain power-spectrum dependence in fitted halo mass
functions ([Bagla, Khandai and Kulkarni, 2010](https://arxiv.org/abs/0908.2702));
calibrated halo mass functions also vary with epoch and mass definition
([Tinker et al., 2008](https://arxiv.org/abs/0803.2706)). These are substantive
comparators for any proposed cosmic mechanism.

A next test would fix the resource, disjoint population, mass range, epoch,
observation model and independent transport inputs before predicting a held-out
abundance or its change. Established mass-function and assembly models should
make predictions for the same target. Agreement shared by those models would
support a common orthopolic interpretation; a distinctive contribution requires
a successful additional prediction or an independently useful reduction of the
inputs. Public simulations can first test the transport approximation, while
observational confirmation requires a separately qualified astronomical sample.
No such test is claimed here. The appendix establishes a concrete cosmological
question, conditional mathematical consequences and a route by which the
conjecture could succeed or fail.
