# Chemistry prediction design review — 13 October 2026

Advisory source and design review, before any local numerical chemistry response
analysis. This is not a registration or a completed empirical test. It complements
the source audit and should not determine a cohort by published success. Searches
exposed publication abstracts, some search-result numerical summaries, and known
qualitative outcomes; a subsequent archival analysis cannot be described as blind.
No candidate numerical data files were opened or fitted for this review.

## Recommendation: pure-gas calibration to mixed-gas adsorption

The strongest immediate design is a fixed shared-site model calibrated using
single-component measurements, followed by a forecast of every eligible measured
mixture component. It has a physical finite resource, an intervention that changes
competition, and a clear failure condition. The model and measurements must have
the same material preparation, temperature, uptake convention and pressure units.
Mixture compositions must describe the equilibrated gas reservoir, or the model
must solve an independently specified finite-reservoir mass balance.

For one site occupied per molecule, let the resource be the number of accessible
sites per mass of adsorbent, with common capacity $Q_s$. The reference measure is
**counting measure over species and the vacancy state**, not a size coordinate.
The equal-allocation baseline is the discrete counterpart of linear-orthopolic
allocation on equally weighted classes. It is not log-orthopolic. With independent
site binding and ideal reservoir activities, competitive Langmuir gives

$$Q_i=Q_s\frac{b_i p_i}{1+\sum_jb_jp_j},\qquad
Q_\mathrm{vac}=Q_s\frac{1}{1+\sum_jb_jp_j}.$$

Each occupied site has the same resource cost. The independently calibrated
constraint/opportunity factor is $a_i=b_i p_i$; equal occupied shares occur when
those products are equal. Equal partial pressures alone do not justify equal
allocation. Neither $1/b_i$ nor $\exp(\Delta G_i/RT)$ should be relabelled an
additive physical resource merely to obtain inverse-cost form.

The relevant empirical tests are joint transfer of the common capacity and the
relative affinities. A useful additional prediction is the **composition at which
the two species have equal uptake**, $p_1/p_2=b_2/b_1$, provided the archived
composition sweep brackets that point. This ratio prediction eliminates $Q_s$;
it does not constitute an independent dataset when derived from the same mixture
measurements as the absolute-uptake test.

Freeze these comparisons before opening mixture uptake values:

- Primary: jointly fit pure curves to one positive $Q_s$ and one positive $b_i$
  per species, then predict all eligible mixture loadings and their ratios.
- Competition ablation: evaluate each fitted pure isotherm independently at its
  partial pressure. It intentionally lacks the shared denominator; it establishes
  whether including competition helps on the same observations.
- Established benchmark: IAST from the same pure curves, with interpolation and
  extrapolation rules fixed in advance. When all curves are Langmuir with the same
  capacity, IAST and competitive Langmuir coincide, so they are then a numerical
  verification rather than two competing physical predictions.
- Optional thermodynamic benchmark: IAST from a predeclared richer pure-curve
  family, provided that model is selected on pure data only. This tests whether
  the restrictive one-site representation loses transferable information.

Different species-specific fitted saturation capacities in an extended Langmuir
formula do not provide the same shared-site account. Equal saturation capacities
are a thermodynamic consistency condition for that simple mixing rule. A primary
modelling study explicitly enforces this condition in its dual-site formulation
([Charalambous et al., 2023](https://pubs.rsc.org/en/content/articlehtml/2023/ee/d3ee00858d)).
Unequal molecular footprints require a different independently specified model;
do not infer footprints from mixture residuals and call the prediction successful.

Pure curves with no measurable saturation may identify only the product $Q_s b_i$.
Treat that as an identifiability limitation before forecasting, not a license to
choose a convenient capacity. Report all prespecified material/mode exclusions.
Do not silently change excess uptake to absolute uptake at appreciable pressure.
Breakthrough outlet composition is not an equilibrium loading unless dead volume,
dispersion, flow and mass-transfer effects are independently addressed.

Measured mixture sources include
[Bazan et al. (2008)](https://journals.sagepub.com/doi/10.1260/026361708787548783)
and a [MOF-5 binary/ternary benchmark](https://www.sciencedirect.com/science/article/pii/S1383586617315563).
These are source leads, not certified locally available numerical archives in
this review. Their abstracts already disclose comparisons with IAST. In contrast,
the mixture outputs of the
[2026 queryable MOF database](https://pubs.acs.org/doi/10.1021/acs.langmuir.5c03717)
are predominantly computed with IAST from pure inputs. Testing IAST against those
outputs would validate software, not an empirical prediction. Source-level labels
must separate experimental, GCMC and IAST-generated records.

**Interpretation:** a successful transfer demonstrates that a fixed physical
capacity plus independently calibrated affinities predicts competition. It is
known adsorption physics, not a new derivation of Langmuir or evidence that
conservation alone determines allocation. Its value to the article is an explicit,
testable instance of constrained allocation and an identifiable failure of a
specific site model when the forecast misses.

## Second design: independent conversion to polymer length distribution

This has a particularly clear resource: monomer units incorporated in each chain.
Use counting measure over integer chain lengths $n$ (the discrete
linear-orthopolic comparison); one chain has cost $q_n=n$ monomer units. For an
ideal balanced, bifunctional, linear step-growth reaction without rings, the
independently measured reacted-functional-group fraction $p$ predicts

$$\frac{N_n}{N_0}=(1-p)^2p^{n-1},\qquad
\frac{nN_n}{N_0}=n(1-p)^2p^{n-1},\qquad n\ge1.$$

The second expression is the resource fraction at each integer chain length;
its sum is one. Relative to extant chain count, the number fraction is
$(1-p)p^{n-1}$. These normalizations must not be confused. On logarithmic size
intervals the resource density acquires a further factor of $n$ in a continuum
approximation; neither measure produces neutral flat allocation in general.
The mechanism is the classical
[Flory distribution](https://doi.org/10.1021/ja01301a016), not an inferred power law.

The independent input should be functional-group conversion from NMR/FTIR or a
separate chemical assay; feed stoichiometry and any monofunctional chain stoppers
must also be specified. Monomer disappearance alone is not automatically the
functional-group conversion needed by this formula. **Never obtain $p$ from
the mean of the same target chain-length distribution.**

An accessible source lead is the University of York's
[2016 polycondensation archive](https://doi.org/10.15124/49496b1b-9109-46bb-8175-6d8455ffc964),
whose institutional metadata advertises a `Data_management.zip` with GPC and NMR
raw data and a naming guide. The
[primary paper](https://doi.org/10.3390/molecules21091245) describes crude aliquots
measured by both techniques. Qualification remains necessary: GPC was calibrated
with linear polystyrene standards, so the apparent polyester molecular weights
are not automatically absolute chain lengths. Sample matching, functional-group
conversion, unequal stoichiometry, cyclic products, detector response and retained
monomer all require resolution before choosing a target. The full raw archive
has not been acquired in this review.

The most informative target is the entire independently calibrated distribution,
or a predefined tail mass fraction together with its mean and dispersity. Compare
the Flory forecast with a predeclared neutral resource allocation on a fixed
finite observable domain, accounting for instrument censoring. Do not select the
domain from the observed tail. A more elaborate kinetic model requires independent
rate information; fitting chain-specific reactivity or cyclization from the target
distribution forfeits that forecast.

This would primarily show **when neutral allocation does not follow even from
equal microscopic reactivity**, and whether a known kinetic constraint predicts
the departure. It should not be advertised as confirmation of neutral allocation.
That contrast is scientifically useful to the general-law programme because it
specifies which additional equalizing mechanism is missing.

## Molecular populations and other chemical laws: lower priority

Canonical populations have $N_j\propto g_j\exp[-E_j/(k_BT)]$, with temperature
measured independently and state degeneracy explicitly included in the reference
measure. Boltzmann weights are known statistical mechanics. Energy per quantum
state is not equal, and replacing the physical energy by an exponential cost
manufactures an inverse relation rather than measuring a resource.

There is an accessible
[INPTDAT molecular-plasma archive](https://www.inptdat.de/dataset/precision-spectroscopy-non-thermal-molecular-plasmas-using-mid-infrared-optical-frequency)
with spectra and rotational populations, but its own study diagnoses nonthermal
populations through fitted rotational temperatures. The independent thermometer
and state-independent observation calibration needed here have not been
established. Published nonthermal behavior was exposed in the metadata search.
It is currently a source for an attribution/example audit, not the strongest next
independent temperature-to-population test.

The same discipline applies to chemical partitioning and electrochemical laws:
equal chemical potentials are not equal additive resource amounts; activity
coefficients or equilibrium constants fitted from the target cannot supply an
independent correction. Prefer the adsorption intervention over another elegant
identity unless a separate calibration and a genuinely unused response are both
available.
