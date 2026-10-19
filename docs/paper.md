# Orthopolity: a general law of resource allocation

**Capacity, physical realizations, and effective-resource inference**

> Research manuscript, revised 19 October 2026. Detailed derivations, complete
> comparisons and analysis histories are retained in the [supporting material](supporting-material.md).
> Empirical studies include exploration, locally frozen forecasts and retrospective
> reanalyses; none is externally preregistered. Authorship and submission declarations
> require agreement before submission.

## Abstract

Orthopolity states a general law of resource allocation: Nature tends to distribute
resources equally among concentrations of those resources. We develop its mathematical
content, establish exact realizations under specified physical conditions, and examine
its predictive reach in models and data. Finite resource capacity bounds incidence;
complete partitions give an exact inverse relation between count and mean resource.
Allocation among coexisting classes requires additional conditions, including an
independently defined comparison measure. Symmetric resource exchange supplies one
mechanism, while gravity, radiating waves and thermal modes clarify which geometric,
transport or statistical equality is present. Absorption, quantization and cell-cycle
variation supply independently specified departures. The framework also supports inverse
inference: restricted combinations of measured resource requirements produce identifiable
predictions across environments. Tests show accurate allocation forecasts in an engineered
system, pure-to-mixture chemical competition, approximate budget closure across
separately grown algal cultures, and speech-duration gains from independently
estimated contextual information. A conditional redistribution bound
shows why changing resource prices alone cannot explain one biological failure.
Other forecasts fail, and some natural
catalogues cannot support the intended test after observation and estimator checks.
These outcomes distinguish an established conditional relation, a physically explained
departure and an unresolved failure. The contribution is a common account of resource
incidence and allocation that makes those distinctions operational and connects them to
further predictions. Establishing its general physical reach requires both successful
transfers and explicit boundaries; failure is retained as information about the model
and its domain.

## 1. The law and the scientific task

**Nature tends to distribute resources equally among concentrations of those resources.**
This is the general-law statement of orthopolity. The article seeks to establish its
physical content through exact ideal systems, realizations in known laws, mechanisms
for real systems, and empirical predictions. It follows the accounts of Fabbri and
Oliveira Jr. (2017) and Fabbri (2024), while distinguishing the claims that their
shared intuition can support.

A box of volume $B$ accommodates $B/q$ equal smaller boxes of volume $q$ when
they tile it completely. At every complete level of a nested subdivision, more units
mean less resource per unit and the same total resource. A mixed population presents
an additional question: how much of the total is assigned to each coexisting size
class? Conservation answers the first accounting question but does not settle the
second allocation question. Their connection, and the conditions needed to make it,
are central to the law's application.

An equal allocation can appear unequal when expressed per a different coordinate,
when the relevant resource combines several requirements, or when another process
changes its distribution. Equal power through enclosing surfaces accompanies
inverse-square radiative flux density. Equal classical energy per mode accompanies
a spectrum increasing with mode density. These examples require explicit objects,
resources and measures; an exponent by itself does not identify the equality.
Ecological size-spectrum work provides an important precedent for making these
choices physical (Sheldon et al., 1972; Gaedke, 1993; Hatton et al., 2021).

The law's scientific value also concerns departures. A standing tree experiences
gravity while other forces support it; the absence of downward motion does not
identify which forces act. Likewise, unequal observed allocation can coexist with
an equalizing process. Establishing that explanation requires independent information
about the processes and a prediction of their combined effect. A fitted residual
called a constraint supplies neither. Some departures will instead expose a failed
resource choice, an inapplicable mechanism or a limitation of the allocation relation
in the claimed domain.

The paper therefore develops three connected contributions: a precise account of
capacity and allocation; a way to infer restricted effective resources and predict
across conditions; and comparisons that preserve both successful forecasts and
failures. Additivity, reversible dynamics, equipartition and the statistical tools
have established foundations. The contribution concerns their physical organization,
the consequences that can be transferred between settings, and the limits revealed
by testing them. [Supporting material](supporting-material.md) retains the detailed
proofs, secondary examples, complete comparisons and source qualifications.

## 2. Capacity, allocation and inference

### 2.1 An exact resource-incidence core

Let $\nu$ be a nonnegative additive resource measure on a system $\Omega$,
with finite budget $B=\nu(\Omega)>0$. For disjoint units $A_i$ with requirements
$q_i=\nu(A_i)$, finite additivity gives

$$N_{\ge t}=\#\{i:q_i\ge t\}\le B/t,\qquad t>0.$$

Indeed, $tN_{\ge t}\le\sum_{q_i\ge t}q_i\le B$. This is a capacity bound;
attaining it requires feasibility and use of the relevant budget.

For a nonempty finite description at level $j$, define its count $N_j$, mean
resource $\bar q_j$, and multiplicity $m_j(x)=\sum_i\mathbf1_{A_{ji}}(x)$.
Integration gives

$$N_j\bar q_j=\int_\Omega m_j\,d\nu=B\gamma_j,\qquad
\gamma_j=\frac{1}{B}\int_\Omega m_j\,d\nu.$$

Every complete partition has $\gamma_j=1$ and therefore
$N_j\bar q_j=B$. The inverse count--mean-resource relation holds exactly even
for unequal units and nested levels. Incomplete disjoint coverage has $\gamma_j<1$;
overlap can give $\gamma_j>1$. Independently measured coverage consequently
predicts a correction to the inverse relation.

A complete level accounts for the whole resource once. Several levels describe
that same budget repeatedly; their totals are not independent allocations. For
coexisting disjoint classes, fractions $f_j$ instead give
$N_j\bar q_j=Bf_j$ with $\sum_jf_j\le1$. Equal class allocations require
equal fractions, which is an additional physical statement. These elementary
results establish the exact core and identify where an allocation law adds content
([supporting derivation](resource-capacity.md)).

### 2.2 The allocation relation and its measure

Let $k$ denote size on a declared finite domain and let $\mu$ be the reference
measure of the classes being compared. If $n_\mu=dN/d\mu$ and
$\bar q(k)=E[q\mid k]$ is the arithmetic mean additive resource per object,
then resource density obeys

$$\mathcal O_\mu(k)=\frac{dR}{d\mu}=\bar q(k)n_\mu(k). \tag{1}$$

Neutral orthopolic allocation relative to $\mu$ has

$$\mathcal O_\mu(k)=C>0,\qquad n_\mu(k)=\frac{C}{\bar q(k)}. \tag{2}$$

This concerns an allocation density, an expectation or a time average as specified
by the system. Those interpretations are not interchangeable. Resource-weighted
sampling gives a uniform size distribution under (2), while sampling objects
uniformly gives an inverse-cost distribution. Stocks, accumulated requirements and
throughputs must also be distinguished before applying the relation.

The reference measure is physical input. If $\bar q(k)\propto k^d$, equal
resource per $d\ln k$ gives the **log-orthopolic** count density
$dN/dk\propto k^{-(d+1)}$. Equal resource per $dk$ instead gives the
**linear-orthopolic** density $dN/dk\propto k^{-d}$. A change of coordinate
carries a Jacobian and need not preserve a visually flat plot. Choosing the measure
after seeing an abundance profile can manufacture equality, so an empirical claim
must justify that choice independently.

One sufficient allocation condition is exchangeability of resource shares among
$K$ fixed equally weighted classes, with fixed total $R$. Symmetry gives
$E[R_i]=R/K$ and, for fixed positive cost $q_i$, $E[N_i]=R/(Kq_i)$.
Conservation alone does not imply this symmetry. Nor does equal expectation imply
equal snapshots: placing the entire resource in one randomly chosen class has
symmetric expectations and unequal realizations. The observation model must
represent this distinction.

### 2.3 Effective resources, constraints and transferable predictions

Objects can require several resources. With independently fixed reference quantities
$s_\ell$, write

$$Q_i=Q_0F(q_{i1}/s_1,\ldots,q_{im}/s_m;z_i,\theta),\qquad
\bar q_{\mathrm{eff}}(k)=E[Q_i\mid k].$$

The total $\sum_iQ_i$ is additive over the declared object partition, but a
nonlinear $F$ need not preserve that total when objects are split or merged.
Proportional subdivision requires degree-one homogeneity for invariance. If all
nonnegative constituent vectors and their subdivisions are admissible, invariance
under every heterogeneous subdivision forces a finite nonnegative $F$, with
$F(0)=0$, to be a nonnegative linear form.
Nonlinear effective resources therefore need a specified physical partition or
restricted composition domain. With heterogeneous objects, averaging follows
composition: $E[F(X,Y)]$ generally differs from $F(E[X],E[Y])$.

Several constituent budgets also remain several constraints unless a physical model
justifies reducing them. Feasibility can require $\sum_iN_iq_{\ell i}\le B_\ell$
for each constituent. A specified optimization problem may provide scarcity-weighted
effective costs, while a separately supported identical population has capacity
$\min_\ell B_\ell/q_\ell$. Neither scalarization nor capacity alone fixes
allocation among competing types (Boyd and Vandenberghe, 2004).

Write a constrained allocation as

$$\bar q_{\mathrm{eff}}(k)n_\mu(k)=C a(k),\qquad a(k)>0. \tag{3}$$

A mechanism or independent measurement must determine $a$ for a forward prediction.
Inversion identifies $\bar q_{\mathrm{eff}}/a=C/n_\mu$, up to scale. Thus
abundance contains information about an effective resource, but cannot by itself
separate that resource from an unrestricted constraint. Multiplying both by the
same positive function leaves the prediction unchanged.

Restrictions shared across environments make the inverse use predictive. Consider
the composition $Q=Q_0\prod_{\ell=1}^mX_\ell^{\theta_\ell}$. Suppose independently
measured constituent requirements scale as $X_{s\ell}\propto k^{D_{s\ell}}$, and a known allocation
factor is $a_s\propto k^{-v_s}$. Under logarithmic allocation, a count density
$k^{-(1+\alpha_s)}$ implies

$$b=D\theta,\qquad b_s=\alpha_s-v_s. \tag{4}$$

This requires deterministic class requirements, or size-independent residual
moments after combining heterogeneous constituents. For unrestricted coefficients,
full column rank identifies the shared composition; otherwise only some
combinations may be identified. A new constituent row has a unique forecast when
it lies in the row space of the calibration design. Every left-null vector gives
a parameter-free consequence $\ell^\top b=0$.

For example, calibration rows $(1,1)$ and $(1,2)$ identify a two-resource
composition. A new row $(2,1)$ then predicts $b_3=3b_1-b_2$ before the third
abundance slope is measured. Uncertainty and near-collinear constituent scalings
determine whether that forecast is useful. The
[identification study](inverse-resources.md) verifies these standard inverse-problem
calculations synthetically; it does not count constructed data as natural evidence.
Inverse optimization and inverse statistical mechanics provide related precedents
(Keshavarz et al., 2011; Habeck, 2014). Here the scientific content lies in the
specified resource family and its transferred physical predictions.

## 3. Ideal mechanisms and physical realizations

### 3.1 Equalization, a constraint and its removal

Consider fixed classes with positive reference widths $w_i$, fixed costs $q_i$,
and resource stocks $R_i$ totaling $B$. Symmetric conductances
$g_{ij}=g_{ji}\ge0$ on a connected graph give the exchange current

$$J^0_{ij}=g_{ij}\left(\frac{R_i}{w_i}-\frac{R_j}{w_j}\right).$$

The resulting dynamics conserve resource and relax to
$R_i^0=Bw_i/\sum_jw_j$, hence $N_i^0=R_i^0/q_i$. This mechanism selects
equal resource per the declared measure. It establishes the neutral relation
within its specified model class.

A fixed class preference $V_i$ changes the transition rate from $i$ to $j$ to
$(g_{ij}/w_i)\exp[\max(V_i-V_j,0)]$. Detailed balance then gives

$$R_i^V=\frac{Bw_i e^{-V_i}}{\sum_jw_j e^{-V_j}}.$$

The added rates balance the neutral current at constrained equilibrium. Removing
the preference preserves the current state and predicts relaxation toward the
neutral allocation. The generator's spectral gap supplies a convergence bound;
disconnected components equalize only within their separately conserved budgets.
These are established reversible-chain tools applied to resource classes (Levin
and Peres, 2017).

This construction shows how an active equalizing process can have an unequal
outcome. Identifying that decomposition in a natural system requires evidence
about its kinetics or response to intervention; a stationary profile alone is
insufficient.

![Equalization, a specified constraint, and recovery](../results/class-exchange-presentation/class-exchange.png)

*Figure 1. Resource exchange on fixed logarithmic size classes. The model predicts
neutral allocation, a nonuniform constrained equilibrium and recovery after release.
The detailed model, spectral bounds and finite-packet simulations are in the
[supporting material](supporting-material.md) and [model report](class-exchange.md).*

### 3.2 Gravity and radiating waves: what geometry preserves

For a Newtonian gravitational field $\mathbf g$, the Poisson equation
(Chao, 2014) gives the integral relation
$\oint_S\mathbf g\cdot\mathbf n\,dA=-4\pi GM_{\mathrm{enc}}$.
Every enclosing surface outside a fixed isolated source has the same inward
field flux. Spherical symmetry additionally gives $|\mathbf g|=GM/r^2$:
the conserved enclosed-source quantity is distributed over an area growing
as $r^2$. Inward flux per solid angle is $d\Psi/d\Omega=GM$, an explicit
angular equality. This is a geometric realization with specified symmetry. The field
flux is not an energy throughput, and nested surfaces are not independent
mass or energy shares. Distributed sources change $M_{\mathrm{enc}}(r)$;
nonspherical sources need not give uniform local fields. The
[gravity derivation](gravity-realization.md) states the resource interpretation,
energy-accounting limits and departures.

For radiation, Poynting's balance gives a physical energy throughput. In steady
transparent transport outside a source, the enclosing-surface power is
$P(r)=L$; isotropic emission gives flux density $L/(4\pi r^2)$. With outgoing
radial propagation at speed $c$, disjoint shell stocks instead satisfy
$dU=(L/c)dr$. Equal radial thicknesses hold equal energy. Equal logarithmic
radial intervals have $dU/d\ln r=Lr/c$, so they do not have equal stocks.
The geometry identifies which comparison realizes equality.

An independently specified absorbing medium gives

$$P(r)=L\exp\left[-\int_{r_0}^{r}\kappa(s)\,ds\right].$$

It predicts the departure from constant radiative throughput and accounts for
energy deposited in matter. If absorption is removed while the source continues,
the response travels outward and the transparent profile returns by
$(r-r_0)/c$. The [transport derivation](physical-realizations.md) gives the full
space-time response and its assumptions (Poynting, 1884; Haus and Melcher, 1989;
Condon and Ransom, 2016). Neither the gravitational nor radiative inverse-square
law alone determines the abundance of objects at different sizes.

### 3.3 Thermal modes: a derived limitation of neutral allocation

A finite set of classical harmonic modes in canonical equilibrium has mean
energy $k_BT$ per mode. Counting modes is the independently defined measure;
instantaneous mode energies can fluctuate. For electromagnetic excitation energy
above the ground state, quantization gives instead

$$\bar\epsilon_\nu=\frac{h\nu}{e^{h\nu/(k_BT)}-1}
=k_BT\frac{x}{e^x-1},\qquad x=\frac{h\nu}{k_BT}.$$

The classical plateau is approached for $x\ll1$ and suppressed for $x\gg1$.
The departure follows from the allowed states before a spectrum is observed.
Mode density $8\pi\nu^2/c^3$ then gives Planck's spectrum. Equal energy per
mode is therefore different from equal energy per frequency interval (Planck,
1901; Tong, n.d.).

Our [FIRAS calculation](thermal-radiation.md) expresses the published microwave
background spectrum as excitation energy per mode. Its 43 channels span
$x=1.199$--$11.262$, illustrating quantum suppression rather than the classical
plateau. The distributed product already contains a fitted blackbody template;
this calculation preserves established observational evidence and its correlated
errors, without claiming a new independent confirmation (Fixsen et al., 1996).
The full derivation and spectrum are retained in the supporting material.

A nonequilibrium test asks more: can independently fitted damping predict mode
energy under a temperature gradient? Using Fontana and Bellon's (2023) cantilever
archive, we fixed a quadratic local-loss model on colder conditions and sealed
hot-condition forecasts before evaluating fluctuations. Ten of eleven mode fits
have nonnegative inferred local loss. On their 26 targets, mean absolute error
is 74.0 K, versus 78.9 K for uniform local loss on the same modes. Individual
transfers range from close agreement to large errors; one fit requires negative
local dissipation. Thus measured global damping does not by itself identify an
adequate spatial energy weighting. The retrospective design, calibration
conventions, all failures and a source point hidden by the plotting range are
reported in supporting section S5.13. Equilibrium normalization was inherited,
so this is not a new test of equipartition.

### 3.4 Cell growth and division: a measurable constraint envelope

Let additive cell mass $x$ grow as $\dot x=gx$, with common deterministic $g$,
conservative symmetric binary division and no death. In a balanced asynchronous
population with a stationary lineage of physiologically equivalent daughters,
established growth-fragmentation theory gives
$p_L(x)=xp_P(x)/E_P[x]$ (Genthon, 2022). For lineage birth mass $B$ and division
mass $D$, stationarity requires $D\overset d=2B$. The fraction of cycles crossing
size $x$ is

$$H(x)=P(B\le x<D)=F_B(x)-F_B(x/2),$$

and the population law becomes

$$p_P(x)=\frac{2H(x)}{E[B^{-1}]x^2},\qquad
\frac{x^2p_P(x)}{E_P[x]}=\frac{H(x)}{\ln2}.$$

The right-hand side is the normalized mass allocation per logarithmic size.
Where every cycle crosses an interval, $H=1$ and allocation is log-orthopolic.
Fixed birth mass $b$ gives the inverse-square density $2b/x^2$ on $[b,2b)$;
variable birth masses can remove any exact plateau. Independently measured
birth events predict that envelope. Growth noise, asymmetric division or
physiological lineage selection require a different observation model.
This provides both a realizable ideal relation and a specified route to its
failure under changed assumptions ([derivation](cell-division.md)).

## 4. What the empirical comparisons establish

### 4.1 Predictions and comparisons

A test specifies its objects, measure, costs, constraints and observation model
before predicting an additional observable. Independent calibration is distinct
from an identity evaluated on the same data. The [run registry](run-registry.md)
preserves inputs, forecasts, comparators and outcomes. Supporting material
discloses prior access to published summaries or raw outcomes; freezing a later
analysis does not erase that exposure.

| Evidence | Established outcome | Scope or unresolved limitation |
|---|---|---|
| Runtime resource competition | Calibrated costs predict allocation and a thread-count intervention | One engineered mechanism |
| Size-selected algal cultures | Equal-biovolume forecasts transfer across selection treatments | Separate populations; binding resource unmeasured |
| Language transfers | Entropy predicts speech; symbolic costs transfer across genres | Known capacity account; physical cost and neutrality unidentified |
| Bacterial transfers | Population means and independent burden assays inform forecasts | Variability and fitted workload correction fail |
| Cantilever energy transfer | Some damping-to-energy forecasts transfer | Small average gain; spatial-loss and observation failures remain |
| Chemical / sediment constraints | Independent inputs improve transfer forecasts | Established rivals perform similarly or better; finite-accuracy limits |
| Chemostat nutrient pulse | Frozen two-budget reweighting fails | Constraint response needs explanation |
| Flare and lake geometry | Predicted exponents excluded or equivalence unresolved | Measurement and dependence affect interpretation |
| Seismicity | Qualification or estimator prerequisites fail | No real b--dimension comparison established |

*Table 1. Different studies answer different questions. Detailed results, all rival
forecasts and observation limitations are retained in supporting material.*

### 4.2 An allocation mechanism with an intervention

In a Python runtime whose global interpreter lock serializes execution, worker
threads running matrix kernels of five sizes compete for one execution resource.
Independent calibration gives cost degrees 1.870 and 2.686 for two kernels.
The complete mean-cost curves predict CPU and job profiles before 16 allocation
trials: maximum CPU-share errors are 0.0035--0.0063 and job-share total-variation
errors are 0.0021--0.0124. Replacing the largest-class thread with a second
smallest-class thread produces the predicted allocation change within 0.0078.
A unit-cost alternative has job-share errors of 0.126--0.273
([intervention report](dimensionality-intervention.md)).

The system supplies competition and the intervention changes the independently
counted opportunities. This is stronger evidence about allocation than assigning
quotas and checking their cost. It demonstrates one physical implementation
of a conditional resource law; it does not establish the same mechanism in nature.

### 4.3 Biological closure, predicted means and failed responses

In separately regrown *Dunaliella* cultures (Malerba et al., 2018), large- and
small-selected treatments differ
10.4-fold in mean cell volume but only 2.5% in geometric mean total biovolume;
control capacity is 18--21% higher. Frozen equal-biovolume forecasts have
held-out errors of 0.124 and 0.179 log units, outperforming fitted size and
equal-count alternatives. This is approximate budget closure across separate
cultures; a limiting resource and allocation among coexisting classes remain
unmeasured (supporting S5.3).

The cell-cycle mechanism predicts separate *E. coli* batch-culture means
more accurately than lineage sampling (Gangan and Athale, 2017): errors
are 2.72% and 0.447%, but variability is overpredicted and the joint criterion
fails. Rounded summaries, length as a mass proxy and unverified physiological
equivalence limit the transfer; supporting S5.6 retains all comparisons.

A nutrient-pulse forecast fails in twelve held-out chemostat polycultures:
frozen C:N reweighting permits at most 0.05--0.12 total variation, versus
observed maxima of 0.29--0.49 over days 0--12. Direction is correct in only
four vessels. No forecast improves appreciably on persistence; no vessel meets
the recovery criterion (Wojcik et al., 2025; supporting S5.3).

A retrospective follow-up allows arbitrary nonnegative C:N prices, preliminary
quota changes and all pooled-species mixtures. Redistribution still exceeds
the bound in 17/36 comparisons across eight vessels. Under transferred quotas
and fixed opportunities, price adjustment alone cannot explain the failure.
Separate-culture quotas do not establish mixed-vessel physiology, and assay
uncertainty is unavailable. A revised explanation must change physiology,
opportunities or the specified relation (supporting S5.10).

A subsequent [independent-assay pilot](paired-phosphorus-results-2026-10-12.md)
also fails: one eligible test culture has 34.9 million cells/mL, versus 5.55
million predicted from fixed phosphorus quota and 4.24 million from an independent
X-ray quota. Measurement independence does not guarantee compatible inputs
(supporting S5.11). A [field audit](field-resources-results-2026-10-12.md)
passes all 18 primary carbon/nitrogen partial-stock checks, but incomplete group
coverage and undefined allocation opportunities still prevent an allocation
test (supporting S5.12).

After calibration on twelve initiation variants, a separate protein-expression
assay predicts ten new-protein cell responses (Borkowski et al., 2018). Under
counting measure balanced over seven gene families, fitted reciprocal workload
MAE is 0.10184 versus 0.09464 for direct transfer. The fitted correction fails
both accuracy and advantage criteria. Direct transfer fixes the same model's
environment factor at 1; neither identifies absolute resource cost
(supporting S5.16).

### 4.4 Information costs and language transfer

Independent written-corpus entropy predicts pause-filtered speech duration
through $\widehat D=NS\,ID/C$, where $NS$ counts canonical syllables and $ID$
measures within-word conditional information (Coupé et al., 2019). Seven
Indo-European languages calibrate $C=40.40$ bits/s; sealed forecasts predict
ten languages from eight other families. Under counting measure balanced over
families, languages, speakers and available texts, language log MAE
is 0.0741: 52.0% below constant syllabic rate, 48.8% below unigram information,
21.5% below a fitted exponent and 27.4% below same-text duration. All frozen
criteria pass. Individual errors can cancel within a language; Thai's discrepancy
slightly exceeds a factor of 1.20. This transfers an established capacity
account, without identifying metabolic cost or neutral word allocation
(supporting S5.17).

For written word types, a symbolic cost $Q_w=L_w^{\theta_L}P_w^{\theta_P}$ under
counting measure gives $p(w)\propto1/Q_w$, with letter count $L$ and dictionary
phoneme count $P$. The fixed composite improves held-out genres over letter
power, but lexical frequencies predict better.
Cost shares remain nonuniform, and these symbols do not measure acoustic energy.
Supporting S5.5 retains all comparisons, including the contextual motivation
of Piantadosi et al. (2011).

### 4.5 Geometric predictions and observation limits

Locally registered tests compare consequences fixed before outcome fitting.
Aftershock productivity gives a primary exponent 0.63 with 95% interval
$[0.51,0.71]$, excluding both rupture-area and moment predictions, 1 and 1.5.
Changing to rupture-length counting windows gives 0.90, $[0.76,0.97]$.
The substantial window dependence qualifies the interpretation. Flare ribbon
area gives density exponent 3.163, $[2.962,3.457]$, excluding predictions 2
and $7/3$. Both registrations call these outcomes inconclusive because their
rules do not choose either candidate; exclusion of the individual predictions
is retained ([test ledger](preregistered-tests.md)).

Global lake radii initially give survival exponent 1.930 and iid equivalence
to 2. Replacing the global projection with physical local geometry gives 1.859,
with basin-bootstrap interval $[1.785,1.924]$. Exact 2 is excluded under that
analysis, but the interval overlaps the frozen equivalence band $[1.9,2.1]$.
The original positive iid conclusion does not survive this geometry correction.
Two local projections agree; topology, completeness and classification still
limit a physical explanation ([follow-up](lake-metric-followup-results-2026-10-09.md)).

The earthquake b--hypocentre-dimension comparison stops earlier. Southern
California provides six sequences passing population and resolution gates,
below the required ten. Italian CLASS/HORUS provides many calibrated proxies,
but a frozen magnitude-estimator check fails in 45 of 56 required synthetic
scenarios, including 30 of 32 noiseless converted-magnitude cases. Conversion
can leave gaps that invalidate a uniform-bin correction. Neither attempt
produces a real b--dimension hypothesis comparison. These are eligibility and
measurement findings, not physical evidence against either relation.

### 4.6 Independent constraints in chemical and sediment transport

For CO2 and CH4 on reference zeolite RM8850, we calibrated a shared-capacity
Langmuir model from pure gases and sealed predictions before evaluating 45
mixture conditions at three temperatures (Wedler et al., 2024). Counting measure
over species and vacancies defines the comparison; calibrated binding affinities
and reservoir fugacities specify the unequal allocation. Capacity is effective
within each temperature. Balanced component MAE is 0.247 mmol/g, versus 0.620
when competition is omitted: a 60% improvement. All temperatures pass the frozen
tolerance, defined relative to maximum pure loading. Established IAST gives
0.243 mmol/g, so no predictive advantage over adsorption theory is demonstrated.
Only 39/90 component predictions lie within reported observation uncertainties;
calibration-range extrapolations also remain. This supports transferable
constraints at finite accuracy, with the retrospective chronology, established
mechanisms and complete diagnostics in supporting section S5.14.

A retrospective sediment transfer calibrates 19 narrow-channel sphere runs
and predicts nine wider-channel runs using separate grain assays (Deal et al.,
2026). Measured shape reduces balanced flux error by 42.6% versus unit shape;
the fuller wall correction reduces it by 77.2% versus hydraulic radius.
The declared accuracy tolerance is permissive, low-flux errors exceed fourfold,
and separate old-material fits predict better. This tests a constitutive
constraint transfer under material-balanced counting measure, not neutral
log-/linear-orthopolic size allocation. One target was exposed before freezing
forecasts; complete comparisons and limitations are in supporting S5.15.

## 5. Learning from validity, departures and failure

A general law earns scientific content through its domains, consequences and
limits. Orthopolity is exact for complete resource hierarchies and is realized
by the specified exchange and physical models. Its broader empirical reach
requires determining when comparable concentrations receive comparable resource,
which effective resource is relevant, and what modifies that allocation.

Three kinds of finding should remain distinguishable. First, a metric or sampling
change can alter the apparent distribution without changing the physical system:
radial power and flux density, mode energy and spectral radiance, or lineage
and population sampling are examples. The correction is justified independently
of the desired result. Second, a physical constraint can produce a predicted
non-neutral profile: measured absorption, quantum level spacing, birth-cycle
crossings and pure-calibrated adsorption affinities supply such explanations.
Third, a specified resource model can fail
its own forecast. The chemostat reweighting, bacterial variability and cantilever
spatial-loss errors remain failures until a revised explanation succeeds on additional evidence.

Observed inequality is therefore not by itself a diagnosis. Conversely, an
arbitrary choice of resource, measure or constraint can make any positive profile
satisfy an allocation identity. Such a construction does not establish a physical
law. An application must state which inputs were independently known, what was
learned from calibration, what transfers unchanged and what observation would
contradict the specified model.

An unavailable test cannot decide between physical resource models; a qualified
forecast that fails should narrow the claimed domain or challenge its assumptions.
The next comparisons should change independently specified requirements or
constraints so that rival explanations predict different relaxation rates,
allocation profiles or cross-environment contrasts such as (4). A success supports
the specified relation; a failure can identify a missing interaction or a boundary.

## 6. Contribution and conclusion

Orthopolity links resource concentration, incidence and allocation as a general
law. Finite capacity and complete accounting establish its exact core; specified
symmetries and dynamics realize its allocation extension. Known physical laws
clarify which equalities hold and how independently specified constraints alter
the observable profile. Restricted inverse inference then makes abundance
informative through predictions that transfer between environments.

The empirical results establish useful conditional successes, failed forecasts
and observation boundaries. They do not yet demonstrate a common neutral regime
across the natural populations examined. This limits the present evidence for
universal physical reach while preserving the ambition to establish the law.
The strongest further contribution will be a resource explanation that predicts
both where the relation holds and how a specified change makes it depart or fail.

## Data and code availability

The repository retains source notices, fixed configurations, forecasts, algorithms
and outputs. The [supporting material](supporting-material.md) contains the moved
technical detail, full evidence comparisons and a map to study-specific reports.
The [run registry](run-registry.md) distinguishes empirical measurements, retrospective
analyses and simulations; earlier failed results are preserved. Source-specific
licences and conditions are in [data/NOTICE.md](../data/NOTICE.md).

The make all target verifies the original frozen inputs, runs the tests and
regenerates the original analysis suite. Later studies have separate offline
reproduction targets documented in their reports. The make paper target builds
this article and its supporting PDF; registry-verify checks retained study
references. Published FIRAS reconstruction and bacterial figure summaries are
identified as such, and neither is presented as a new raw-data experiment.
The supplied 2017 manuscript was inspected privately and is not redistributed.

## References

Bishop, C. J., and Peres, Y. (2017). *Fractals in Probability and Analysis*.
Cambridge University Press. Section 1.1.
<https://www.math.stonybrook.edu/~bishop/fractalbook.pdf>.

Borkowski, O., Bricio, C., Murgiano, M., Rothschild-Mancinelli, B., Stan, G.-B.,
and Ellis, T. (2018). Cell-free prediction of protein expression costs for growing
cells. *Nature Communications*, 9, 1457. <https://doi.org/10.1038/s41467-018-03970-x>.

Boyd, S., and Vandenberghe, L. (2004). *Convex Optimization*. Cambridge University Press.
Sections 4.7 and 5.6. <https://web.stanford.edu/~boyd/cvxbook/>.

Chao, B. F. (2014). On the gravitational energy associated with Earth's changing
oblateness. *Geophysical Journal International*, 199(2), 800–804.
<https://doi.org/10.1093/gji/ggu301>.

Condon, J. J., and Ransom, S. M. (2016). *Essential Radio Astronomy*.
Princeton University Press. Chapter 2, radiation and absorption.
<https://www.cv.nrao.edu/~sransom/web/Ch2.html>.

Coupé, C., Oh, Y. M., Dediu, D., and Pellegrino, F. (2019). Different languages,
similar encoding efficiency: Comparable information rates across the human
communicative niche. *Science Advances*, 5, eaaw2594.
<https://doi.org/10.1126/sciadv.aaw2594>.

Deal, E., et al. (2026). Generalizing sediment transport experiments from narrow
flumes to wider channels. *Journal of Geophysical Research: Earth Surface*, 131.
<https://doi.org/10.1029/2025JF008712>. Data: <https://doi.org/10.20383/103.01325>.

Fabbri, R., and Oliveira Jr., O. N. (2017). *A simple model that explains why inequality
is ubiquitous*. Supplied manuscript dated 17 March 2017, 13 pp.; publication status unverified.

Fabbri, R. (2024). The Orthopolity cosmological principle and the Natural distribution law.
Author's essay, 14 August. <https://ttm.github.io/2024/08/14/power.html>.

Fixsen, D. J., Cheng, E. S., Gales, J. M., Mather, J. C., Shafer, R. A., and Wright,
E. L. (1996). The cosmic microwave background spectrum from the full COBE FIRAS data set.
*The Astrophysical Journal*, 473, 576. <https://doi.org/10.1086/178173>.
Source article: <https://arxiv.org/abs/astro-ph/9605054>.

Gaedke, U. (1993). Ecosystem analysis based on biomass size distributions: A case study
of a plankton community in a large lake. *Limnology and Oceanography*, 38, 112–127.
<https://doi.org/10.4319/lo.1993.38.1.0112>.

Gangan, M. S., and Athale, C. A. (2017). Threshold effect of growth rate on
population variability of *Escherichia coli* cell lengths.
*Royal Society Open Science*, 4, 160417. <https://doi.org/10.1098/rsos.160417>.

Fontana, A., and Bellon, L. (2023). Linking fluctuation and dissipation in spatially
extended out-of-equilibrium systems. *Physical Review E*, **107**, 034118.
<https://doi.org/10.1103/PhysRevE.107.034118>. Data:
<https://doi.org/10.5281/zenodo.7640708>.

Genthon, A. (2022). Analytical cell size distribution: lineage-population bias
and parameter inference. *Journal of the Royal Society Interface*, 19, 20220405.
<https://doi.org/10.1098/rsif.2022.0405>. Revised exposition:
<https://arxiv.org/abs/2206.06146v2>.

Hatton, I. A., Heneghan, R. F., Bar-On, Y. M., and Galbraith, E. D. (2021). The global
ocean size spectrum from bacteria to whales. *Science Advances*, 7, eabh3732.
<https://doi.org/10.1126/sciadv.abh3732>.

Habeck, M. (2014). Bayesian approach to inverse statistical mechanics.
*Physical Review E*, 89, 052113. <https://doi.org/10.1103/PhysRevE.89.052113>.

Haus, H. A., and Melcher, J. R. (1989). *Electromagnetic Fields and Energy*.
Prentice-Hall. Section 11.2, Poynting's theorem.
<https://web.mit.edu/6.013_book/www/chapter11/11.2.html>.

Keshavarz, A., Wang, Y., and Boyd, S. (2011). Imputing a Convex Objective Function.
*Proceedings IEEE Multi-Conference on Systems and Control*, 613–619.
<https://stanford.edu/~boyd/papers/imputed_objective.html>.

Levin, D. A., and Peres, Y. (2017). *Markov Chains and Mixing Times*, second edition,
with contributions by E. L. Wilmer. American Mathematical Society.
<https://pages.uoregon.edu/dlevin/MARKOV/mcmt2e.pdf>.

Lolli, B., Randazzo, D., Vannucci, G., and Gasperini, P. (2020). The Homogenized
Instrumental Seismic Catalog (HORUS) of Italy from 1960 to Present.
*Seismological Research Letters*. <https://doi.org/10.1785/0220200148>.

Malerba, M. E., Palacios, M. M., and Marshall, D. J. (2018). Do larger individuals cope with
resource fluctuations better? An artificial selection approach. *Proceedings of the Royal
Society B*, 285, 20181347. <https://doi.org/10.1098/rspb.2018.1347>. Data:
<https://doi.org/10.5061/dryad.4mh47r7>.

Piantadosi, S. T., Tily, H., and Gibson, E. (2011). Word lengths are optimized for
efficient communication. *Proceedings of the National Academy of Sciences*,
108(9), 3526–3529. <https://doi.org/10.1073/pnas.1012551108>.

Planck, M. (1901). Ueber das Gesetz der Energieverteilung im Normalspectrum.
*Annalen der Physik*, 309, 553--563. <https://doi.org/10.1002/andp.19013090310>.

Poynting, J. H. (1884). On the transfer of energy in the electromagnetic field.
*Philosophical Transactions of the Royal Society of London*, 175, 343–361.
<https://doi.org/10.1098/rstl.1884.0016>.

Sheldon, R. W., Prakash, A., and Sutcliffe, W. H., Jr. (1972). The size distribution of
particles in the ocean. *Limnology and Oceanography*, 17, 327–340.
<https://doi.org/10.4319/lo.1972.17.3.0327>.

Tao, T. (2011). *An Introduction to Measure Theory*. Graduate Studies in
Mathematics, 126. American Mathematical Society. Exercise 1.4.34.
<https://terrytao.wordpress.com/wp-content/uploads/2012/12/gsm-126-tao5-measure-book.pdf>.

Tong, D. (n.d.). *Statistical Physics*. University of Cambridge Part II Mathematical
Tripos lecture notes, Sections 1.3, 2.2.1 and 3.2. Accessed 6 October 2026.
<https://davidtong.org/pdfs/teaching/statistical-physics/statphys.pdf>.

Wedler, C., Ferre, A., Azzan, H., Danaci, D., Petit, C., and Pini, R. (2024).
Binary adsorption equilibria of three CO2+CH4 mixtures on NIST reference zeolite Y
(RM 8850) at temperatures from 298 to 353 K and pressures up to 3 MPa.
*Journal of Chemical & Engineering Data*, 69, 4216--4229.
<https://doi.org/10.1021/acs.jced.4c00358>.

Wojcik, L. A. M., Pfennig, A., Flamm, S., Klauschies, T., Rosenbaum, B., Weithoff, G., and
Gaedke, U. (2025). Top-down control and species composition influence nonlinearly the
short-term response of experimental food webs to a nutrient pulse perturbation. *Proceedings
of the Royal Society B*. <https://doi.org/10.1098/rspb.2025.1969>. Data:
<https://doi.org/10.5061/dryad.51c59zwj5>.
