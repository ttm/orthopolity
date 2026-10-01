# Primary sources for the model-compatibility experiments

Reviewed 1 October 2026. This catalogue records model-specific predictions and
resource interpretations for the simulation work. Mathematical compatibility
with a resource representation and empirical adequacy as a model of Nature are
different questions. The cited papers do not validate Orthopolity.

For a count density $n(k)=dN/dk$ and mean resource cost $q(k)$, resource per
logarithmic interval is $O(k)=kq(k)n(k)$. Thus a tail $n(k)\propto k^{-\gamma}$
has constant $O$ when $q(k)\propto k^{\gamma-1}$. This accounting implication
is our comparison rule; the physical meaning and independent specification of
$q$ determine the scientific strength of each interpretation. Counts per
discrete class, densities per linear interval, and densities per logarithmic
interval must retain their distinct conventions.

## 1. Growth with preferential attachment

- Barabási, A.-L. and Albert, R. (1999), **Emergence of scaling in random
  networks**, *Science* 286, 509–512.
  [Primary author manuscript](https://arxiv.org/abs/cond-mat/9910332);
  [published paper](https://doi.org/10.1126/science.286.5439.509).
- Dorogovtsev, S. N., Mendes, J. F. F. and Samukhin, A. N. (2000),
  **Structure of growing networks with preferential linking**, *Physical
  Review Letters* 85, 4633–4636. The author manuscript has the earlier title
  *Structure of Growing Networks: Exact Solution of the Barabási–Albert's Model*.
  [Primary manuscript](https://arxiv.org/abs/cond-mat/0004434);
  [published paper](https://doi.org/10.1103/PhysRevLett.85.4633).

Linear attachment with $m$ new links per node gives the asymptotic degree
exponent $\gamma=3$. Equation 11 of the second manuscript supplies the
limiting degree distribution

$$P(k)=\frac{2m(m+1)}{k(k+1)(k+2)},\qquad k\ge m.$$

This is a large-network limit, not the exact histogram of a finite generated
simple graph. Seed effects, integer degrees, prohibited duplicate edges, and
the upper cutoff matter for finite simulations.

An independently defined candidate resource is the number of **wedges**, or
unordered length-two paths centered at a node: $q(k)=\binom{k}{2}$.
Our deduction from the cited distribution is

$$kq(k)P(k)=m(m+1)\frac{k(k-1)}{(k+1)(k+2)}
\longrightarrow m(m+1).$$

Consequently wedge resource is asymptotically equal per logarithmic degree
interval. Degree itself, interpreted as incident edge ends, instead gives
$k^2P(k)\propto k^{-1}$. Wedges are a real combinatorial observable; they are
not a conserved budget in the attachment rule. This establishes a resource
representation compatible with the tail, not a demonstration that equal wedge
allocation causes preferential attachment.

## 2. Independent-edge random graphs

- Gilbert, E. N. (1959), **Random graphs**, *Annals of Mathematical Statistics*
  30, 1141–1144.
  [Published paper](https://doi.org/10.1214/aoms/1177706098);
  [primary-paper scan](https://www.stat.cmu.edu/~brian/780/bibliography/09%20Other%20Models/Gilbert%20-%201959%20-%20Random%20graphs.pdf).
- Erdős, P. and Rényi, A. (1959), **On random graphs. I**, *Publicationes
  Mathematicae Debrecen* 6, 290–297.
  [Publisher record](https://publi.math.unideb.hu/paper/2769).

For independent-edge $G(n,p)$, a vertex degree has the exact binomial law
$P(k)=\binom{n-1}{k}p^k(1-p)^{n-1-k}$. It approaches a Poisson distribution
when $(n-1)p$ stays finite as $n$ increases. The historical fixed-edge model
and independent-edge model are distinct, although both are often called
Erdős–Rényi graphs. The simulation should state which it implements.

This is a comparison with a concentrated degree distribution. Uniform
probability for each potential edge does not imply equal resource per degree
class. A finite run can have an approximately straight segment on a log-log
plot without having an asymptotic power-law degree distribution.

## 3. Conservative pair exchange

- Drăgulescu, A. and Yakovenko, V. M. (2000), **Statistical mechanics of money**,
  *European Physical Journal B* 17, 723–729.
  [Primary manuscript](https://arxiv.org/abs/cond-mat/0001432);
  [author-hosted published paper](https://physics.umd.edu/~yakovenk/papers/EPJB-17-723-2000.pdf).

The paper investigates exponential stationary distributions for specified
conservative exchange processes, and also discusses dynamics where that result
fails. Conservation alone does not guarantee an exponential distribution.

For the particular simulation that chooses a pair and uniformly splits its
combined nonnegative wealth, the stationary distribution is uniform on the
fixed-total simplex. Its one-agent marginal, derived from the simplex volume,
is

$$p_N(w)=\frac{N-1}{W}\left(1-\frac{w}{W}\right)^{N-2},
\qquad 0\le w\le W,$$

where $W$ is total wealth. With $\bar w=W/N$ fixed, this approaches
$p(w)=\bar w^{-1}e^{-w/\bar w}$. The simplex expression is a calculation for
this particular uniformly redistributing update, not a claim that every money
model in the source uses that update.

The physical stock resource is $q(w)=w$. Its resource profile per log wealth
is $w^2p(w)$, with a maximum at $2\bar w$ in the large-$N$ limit. A conserved
total and a stationary state therefore coexist with a non-flat stock profile.

## 4. Multiplicative growth with a lower boundary

- Sornette, D. and Cont, R. (1997), **Convergent multiplicative processes
  repelled from zero: power laws and truncated power laws**, *Journal de
  Physique I* 7, 431–444.
  [Primary manuscript](https://arxiv.org/abs/cond-mat/9609074).

A convergent multiplicative process maintained away from zero has, under the
paper's regularity conditions, a stationary upper tail
$p(w)\propto w^{-(1+\kappa)}$. The positive tail exponent solves
$E[A^{\kappa}]=1$, where $A$ is the multiplier. It depends on the multiplier
distribution. For $\ln A\sim N(\mu,\sigma^2)$ with $\mu<0$, solving that
equation gives $\kappa=-2\mu/\sigma^2$.

The update $w_{t+1}=\max(w_{\min},A_tw_t)$ can have an atom at its floor;
the predicted power describes its upper tail, not necessarily its entire
stationary profile. For stock $q(w)=w$, resource per log wealth scales as
$w^{1-\kappa}$ and is asymptotically constant only when $\kappa=1$.
The weight $w^{\kappa}$ gives a constant tail resource representation for all
these exponents, but identifying it as a physical resource requires separate
support.

## 5. Dependence of simultaneous resource extremes

- Ledford, A. W. and Tawn, J. A. (1996), **Statistics for near independence in
  multivariate extreme values**, *Biometrika* 83, 169–187.
  [Published paper](https://doi.org/10.1093/biomet/83.1.169).

The paper supplies a framework for joint-tail dependence beyond a binary
independent/dependent distinction. The suite's two elementary endpoints can
be calculated directly. For independent Pareto resources with
$P(X_i>x)=x^{-\kappa_i}$, $x\ge1$,

$$P(X_1>x,\ldots,X_d>x)=x^{-\sum_i\kappa_i}.$$

For fully aligned resources $X_i=U^{-1/\kappa_i}$ with one common uniform
$U$, that joint probability is $x^{-\max_i\kappa_i}$. Equal marginal exponents
therefore produce a joint exponent $d\kappa$ under independence and $\kappa$
under complete alignment. These are simultaneous-exceedance predictions;
they are not automatically the exponent of additive cost, multiplied cost,
or an object-abundance density.

## 6. Equal radial throughput

- Poynting, J. H. (1884), **On the transfer of energy in the electromagnetic
  field**, *Philosophical Transactions of the Royal Society of London* 175,
  343–361.
  [Published paper](https://doi.org/10.1098/rstl.1884.0016);
  [transcription and original scan](https://en.wikisource.org/wiki/Index:PoyntingTransfer.djvu).

Electromagnetic energy conservation supplies the basis for the ideal
light-source comparison. Our elementary specialization to steady isotropic
outgoing power $L$ in a transparent three-dimensional medium is

$$E(r)=\frac{L}{4\pi r^2},\qquad
\int_{S_r}\mathbf S\cdot\mathbf n\,dA=L.$$

This is genuine equal throughput across enclosing spheres, and its exponent
reflects the growth of their area. The same radiation crosses successive
spheres; these are nested surfaces, not disjoint stocks. For radial propagation
at speed $c$, energy in a shell is $dU=L\,dr/c$, so energy per logarithmic
radius is $Lr/c$. Absorption or a time-dependent source changes the comparison.
The ideal sphere calculation is a conservation and geometry identity, not an
independent confirmation of an abundance law.

## 7. Optional phenomenological extensions

### Saving-dependent exchange

- Chakraborti, A. and Chakrabarti, B. K. (2000), **Statistical mechanics of
  money: how saving propensity affects its distribution**, *European Physical
  Journal B* 17, 167–170.
  [Primary manuscript](https://arxiv.org/abs/cond-mat/0004256);
  [published paper](https://doi.org/10.1007/s100510070173).
- Patriarca, M., Chakraborti, A. and Kaski, K. (2004), **Statistical model with
  a standard Gamma distribution**, *Physical Review E* 70, 016104.
  [Primary manuscript](https://arxiv.org/abs/cond-mat/0402200);
  [published paper](https://doi.org/10.1103/PhysRevE.70.016104).
- Chatterjee, A., Chakrabarti, B. K. and Manna, S. S. (2004), **Pareto law in a
  kinetic model of market with random saving propensity**, *Physica A* 335,
  155–163.
  [Primary manuscript](https://arxiv.org/abs/cond-mat/0301289);
  [published paper](https://doi.org/10.1016/j.physa.2003.11.014).

Common saving propensity changes the stationary wealth distribution away from
the no-saving exponential. The Gamma fit with shape
$a=(1+2\lambda)/(1-\lambda)$ is a useful approximation, not an exact
stationary-distribution theorem for every nonzero saving propensity. The
2004 paper explicitly offers an effective gas-dimension interpretation, making
it a close comparison for the proposed dimensionality program.

Quenched heterogeneous saving propensities can instead yield a Pareto upper
tail with density exponent near 2 in the reported model. Finite populations,
the largest saving propensity, equilibration, and the propensity distribution
affect the observable tail. For money as resource, a density exponent near 2
corresponds to near-equal money per logarithmic wealth interval. These are
specific idealized exchange models; their applicability to real economies
requires independent empirical assessment.

### Latent-variable Zipf mechanisms

- Aitchison, L., Corradi, N. and Latham, P. E. (2016), **Zipf's law arises
  naturally when there are underlying, unobserved variables**, *PLOS
  Computational Biology* 12, e1005110.
  [Published primary paper](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1005110).

The paper explains how mixing distributions through latent variables can
produce a broad range of observation probabilities and approximate Zipf
scaling, even when the conditional models do not have that scaling. It also
gives applicability diagnostics and examples where the explanation fails.
Its mathematical energy $-\ln P(x)$ is surprisal; interpreting it as a
physical cost requires an additional mapping.

Zipf probability $P_r\propto r^{-1}$ allocates approximately equal probability
mass per logarithmic **rank** interval. Rank is an ordering coordinate, not
automatically resource amount. This offers a second mechanism compatible with
an equal-share representation, without asserting one microscopic origin for
all compatible mechanisms.

## 8. Interpreting the comparisons

An outcome-defined class of power laws with their reciprocal resource weights
is mathematically legitimate and can organize different models. Simulation
can check the representation and reveal where a predeclared physical or
combinatorial resource matches it. If the weight is chosen from the observed
exponent afterward, successful flattening verifies the representation; it
cannot independently identify the resource or its causal role.

Here “cosmological” may be used in the broad philosophical sense of a principle
proposed to govern Nature. The conventional cosmological claim is more specific:
it would require predictions about declared astronomical
observables across specified scales and epochs. Neither interpretation makes
these simulated examples new empirical observations of natural systems.
