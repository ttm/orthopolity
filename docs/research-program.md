# Establishing orthopolity: a research programme

Prepared 8 October 2026 for the authors. It answers a narrower question than the
[manuscript](paper.md): in what form could orthopolity be established as a property of real
systems, what is already published, and which tests would decide it. The programme was drafted,
then reviewed by an adversarial referee pass and a citation check; their corrections are
incorporated. Literature statements were checked against abstracts and search extracts, not full
texts. Items marked *(verify)* need a primary-text check before citation.

## Summary

- **What can be established.** In systems where an additive resource is carried through log
  size by scale-indifferent dynamics (relative growth independent of size) and conserved along
  the way, the stationary allocation approaches equal resource per logarithmic size interval.
  The approach is quantitative: $\zeta-1\approx1/(m\,\tau_{\rm res})$, the reciprocal of the
  number of e-folds of size a resource unit climbs before it leaves. Orthopolity is the
  long-residence limit of this class, as equipartition is the equilibrium limit of a thermal
  system. This makes "nature does not care about concentration" precise and turns "deviations
  are constraints" into predictions from measured rates.
- **What cannot.** Orthopolity as a general property of all real systems. With the resource
  fixed in advance, event catalogues and cascades are mostly top-heavy (seismic moment
  $\zeta\approx0.63$–$0.67$, flare energy 0.5–0.8, wildfire area 0.3–0.75), and several stocks
  formed by other mechanisms are far from 1 (galaxy stellar mass 0.47, tree biomass 0.38, the
  stellar IMF 1.35 and 0.3). These are not small deviations awaiting a constraint term; other
  mechanisms predict them.
- **Novelty.** The mechanism and its exponent equation are published (Reed 2001; Reed and Hughes
  2002; Gabaix 1999; Saichev, Malevergne and Sornette 2010). A strong paper's contribution would
  be a pre-registered, multi-domain, out-of-sample test that measured rates predict $\zeta$,
  including systems where $\zeta\ne1$ is predicted. Realistic venues are a Registered Report in
  Royal Society Open Science or Physical Review E; a general-science journal only if the test
  succeeds across several domains.

## 1. The claim in a testable form

For objects holding an additive resource $q$, logarithmic orthopolity states that the
**resource-weighted distribution of log size is uniform**. With the resource itself as the size
coordinate, this is Zipf's law with survival exponent $\zeta_q=1$ (density exponent 2): equal
total resource in every factor-of-ten class. It is the marginal case between bottom-heavy
($\zeta>1$) and top-heavy ($\zeta<1$) allocations, and the only power law in which neither
cutoff dominates the total.

**Vacuity lemma.** For any power law $dN/dk\propto k^{-\alpha}$, the weight $q\propto k^{\alpha-1}$
is exactly orthopolitic. "Orthopolity holds for some resource" is therefore empty. The
repository's earthquake catalogue shows this concretely: one fit, $b=0.998$ [0.973, 1.024], gives
$\zeta=0.666$ for seismic moment and $\zeta=0.998$ for rupture area converted by self-similar
scaling ([resource_choice.json](../results/resource_choice.json)). Choosing a resource after
seeing the data can produce orthopolity anywhere.

**Resource rule**, frozen and published before any test system's size distribution is examined:

1. *Unit.* Defined by a published operational algorithm that uses no size statistics (a legal
   enterprise, a tagged tree, an algorithmically delineated urban centre). Alternative definitions
   are pre-registered sensitivity analyses, reported and never selected; the exponent depends on
   the definition (administrative US places $\zeta\approx1.4$, clustered "natural" cities
   $\approx1$; Rozenfeld et al. 2011).
2. *Resource.* Additive, held by units, with a budget that can be closed from panel data:
   incumbent growth + entry − exit ± measured transfers. Not admissible as the primary resource:
   quantities converted from another variable through an assumed scaling (magnitude to rupture
   area, peak flux to fluence), instrument-band fractions of energy, degrees or counts of distinct
   partners, nested quantities such as drainage area.
3. *Multiplicity.* If several resources qualify (firm employment, assets, revenue), each gets its
   own measured rates and prediction, and every failure counts. The claim is
   $\zeta_{\rm obs}(q)=\zeta_{\rm pred}(q)$ for every admissible $q$, never "$\zeta=1$ for some $q$".
4. *Coordinate and range.* The coordinate is the resource itself, measure $d\ln q$. The lower
   bound of the fit is set by the theory (the entry scale), not by minimizing a KS distance; the
   choice of lower cutoff alone moves published exponents by 0.3–0.9 for fires and wealth.
5. *Event catalogues.* The resource is the budgeted released quantity (seismic moment, radiated
   or magnetic energy).

Under this rule the repository's two most favourable cases are inadmissible as evidence. Rupture
area is a converted proxy, chosen after the energy result, and anticipated by Aki's $b=D/2$
(1981). GOES fluence is a band-limited proxy, and the direct fit depends on background handling
($\alpha=2.13$ raw, 1.90 approximately subtracted). Both stay in the record as demonstrations of
why the rule is needed.

## 2. The mechanism: conservative, scale-indifferent transport

**Transport identity.** Let $u=\ln(S/s_e)$, with $s_e$ the size at which units enter, and let
$B(u)$ be resource per unit $u$. At stationarity $B=F/v$: resource flux through $u$ divided by
the log-speed at which resource moves. Hence

$$\zeta-1=-\frac{d\ln B}{du}=-\frac{d\ln F}{du}+\frac{d\ln v}{du}\quad(+\text{ a diffusive term}).$$

$B$ is flat on an interval iff (i) the flux is conserved there (no net local creation or loss)
and (ii) the log-speed is scale-invariant (Gibrat's law). Condition (ii) is the precise content
of "nature does not care about concentration"; condition (i) is the content of conservation.
Additive rather than multiplicative indifference gives an exponential distribution instead
(Drăgulescu and Yakovenko 2000). The same closure gives the known non-unit exponents as measured
gradients: Kolmogorov turbulence ($kE(k)\propto k^{-2/3}$), the Dohnanyi cascade (log-speed
$\propto m^{-1/6}$, so $\zeta=5/6$), source-driven coagulation ($\zeta=(1+\nu)/2$), size spectra
(biomass per log mass $\propto m^{n-q}$). Each piece is known in its own field; stating them as
one deviation formula may be new *(verify)*.

**Exact result for Gibrat stocks.** Incumbents grow as geometric Brownian motion with drift
$\mu$ and variance rate $\sigma^2$ (relative to entrants), exit at hazard $h$, and entry grows at
rate $\nu$. The tail exponent is the positive root of
$(\sigma^2/2)\zeta^2+(\mu-\sigma^2/2)\zeta-(h+\nu)=0$ (Reed 2001; Reed and Hughes 2002; Saichev,
Malevergne and Sornette 2010), equivalently

$$(\zeta-1)\left(\mu+\tfrac{\sigma^2}{2}\zeta\right)=\phi,\qquad \phi=h+\nu-\mu .$$

**Budget identity.** The total obeys $dQ/dt=(\mu-h)Q+J_R$, with $J_R$ the entry flux. A
stationary total relative to the entry flow then forces $\phi=J_R/Q$, the inverse residence
time of a resource unit, $1/\tau_{\rm res}$. Positive entry therefore gives $\phi>0$ and
$\zeta>1$ strictly. To first order,

$$\zeta-1\approx\frac{\phi}{m}=\frac{1}{m\,\tau_{\rm res}},\qquad m=\mu+\frac{\sigma^2}{2},$$

where $m$ is the resource-weighted log-growth rate. **Orthopolity is the limit approached as
$m\tau_{\rm res}\to\infty$**: resource that stays long enough to spread over many e-folds of
size ends up equally distributed across them, with a small, predicted, bottom-heavy excess.
$\zeta<1$ requires incumbents to outgrow turnover ($\phi<0$); the normalized total is then not
stationary and the largest units dominate (condensation; Bouchaud and Mézard 2000). Special
cases: a reflecting floor at fixed mean gives $\zeta=1/(1-s_{\min}/\bar s)$ (an identity for a
Pareto tail; Levy and Solomon 1996; Rozenfeld et al. 2011); Kesten processes give $\zeta=1$ iff
$E[A]=1$ (Kesten 1973; Goldie 1991); Simon's model gives $\zeta=1/(1-\alpha)$.

`gibrat_zeta` in [src/orthopolity.py](../src/orthopolity.py) implements the exponent equation,
with tests. [run_gibrat.py](../experiments/run_gibrat.py) simulates a population from empty: the
tail exponent follows the law from $\zeta=0.81$ at $\phi=-0.02$ to 1.60 at $\phi=0.05$, with
$0.988\pm0.010$ at $\phi=0$, and the entry-flux share $J_R/Q$ converges to $\phi$ where the
total has relaxed (0.0498 at $\phi=0.05$) ([gibrat.json](../results/gibrat.json)).

**Measured deviations within and near the class.**

| Constraint | Predicted deviation | Source |
|---|---|---|
| Entry flux, finite residence | $(\zeta-1)(\mu+\sigma^2\zeta/2)=J_R/Q$ | Reed 2001; Saichev et al. 2010 |
| Size-dependent growth or volatility | local $\zeta(S)=1-2\mu(S)/\sigma^2(S)+d\ln\sigma^2/d\ln S$ | Gabaix 1999; Ioannides and Overman 2003 *(verify printed form)* |
| Finite age $T$ | flat only up to $u\approx mT$; beyond it $B$ collapses | Gabaix, Lasry, Lions and Moll 2016 (in spirit) |
| Trophic losses (food webs) | biomass slope $(1-n)+\ln TE/\ln PPMR$ | Jennings and Mackinson 2003; Mehner et al. 2018 |
| Encounter vs metabolic scaling | biomass slope $n-q$ | Andersen and Beyer 2006; Hartvig et al. 2011 |
| Rupture width saturation | rupture-area $\zeta_A=4b/3$ above about M 6.7 | Hanks and Bakun 2002 |
| Differential stress | $b\approx1.23-0.0012\,\Delta\sigma$ [MPa] | Scholz 2015 (empirical calibration) |

Two cautions. Size-dependent rates can fit any stationary distribution through the local
formula, so systems that need it test "stationary Markov dynamics", not orthopolity, and must be
scored separately. And observing $\zeta\approx1$ does not identify the mechanism: broad
lognormals are locally flat in resource near their resource-weighted mode (Montroll and
Shlesinger 1982; Perline 2005), and sample-space-reducing processes, latent-variable mixtures and
young high-noise Gibrat systems also give $\zeta\approx1$ (Corominas-Murtra et al. 2015;
Malevergne et al. 2013).

## 3. Where orthopolity is not expected

Other mechanisms predict their own exponents. Reporting them as "constrained orthopolity" would
make the claim unfalsifiable; stating them sharpens it.

| Class | Mechanism | Predicted $\zeta$ of the resource |
|---|---|---|
| Collisional fragmentation | Dohnanyi constant-mass-flux cascade | 5/6 (Dohnanyi computed 0.837); $5/(6+s)$ with strength scaling $s$ |
| Source-driven coagulation | Smoluchowski, kernel homogeneity $\nu$ | $(1+\nu)/2$; orthopolity only at $\nu=1$ |
| Mean-field avalanches | Critical branching, depinning | moment 1/2 |
| Lakes | Critical percolation of topography | 96/91 ≈ 1.055 (area); observed 1.14 |
| Size-structured food webs, forests | log-speed $\propto S^{n-1}$, size-dependent mortality | set by physiology and demography |
| Additive exchange | Conserved random transfers | exponential, no power law |

## 4. Evidence map

A 49-system compilation of published exponents ([zeta-compilation.md](zeta-compilation.md);
provisional, one value per system, several datasets reused):

| Class | Typical $\zeta$ | Examples |
|---|---|---|
| Stocks with proportional growth | 0.9–1.1, about half within ±0.1 of 1 | US firms 1.06; US metro areas 1.005; natural cities ≈1; ocean biomass 1.04 |
| Stocks from other mechanisms | 0.3–1.4 | trees 0.38; galaxy stellar mass 0.47; IMF 1.35 and 0.3; lakes 1.14 |
| Events and cascades | median ≈0.8, mostly below 1 | seismic moment 0.63–0.68; cyclone dissipation 0–0.25; wildfire 0.3–0.75; flare energy 0.5–0.8 |
| Degrees and counts (not resources) | median ≈1.4 | excluded |

Clauset, Shalizi and Newman (2009), the least selected source, does not centre on 1; its
converted median is about 1.3, though several rows in the compilation were taken from memory and
await checking. Even the favoured class has clear exceptions: administrative US places
$1.4\pm0.1$, Forbes wealth 1.1–1.5, mutual funds with lognormal tails. Firm and city growth also
violate Gibrat in the variance (Amaral et al. 1997; Rozenfeld et al. 2008), so near-Zipf tails
there appear despite a failure of the stated mechanism, and require compensating terms the theory
must predict.

The repository's own fits ([resource_choice.json](../results/resource_choice.json)):

| System | Quantity | Estimate | Status under the resource rule |
|---|---|---|---|
| USGS earthquakes 2010–2024, M ≥ 5.5 | seismic moment | $\zeta=0.666$ [0.649, 0.683] | admissible; top-heavy |
| same | rupture area, converted | $\zeta=0.998$ [0.973, 1.024] | inadmissible proxy; anticipated by Aki 1981 |
| same, M ≥ 6.7 | rupture area, width-saturated scaling | $\zeta=1.36$ [1.29, 1.44] | illustrates a constraint-predicted shift |
| GOES flares 2022–2024 | end fluence, raw / background-subtracted | $\alpha=2.13$ [2.03, 2.22] / 1.90 [1.82, 1.99] | band-limited proxy; energy exponents in the literature are 1.5–1.8 |
| Hatton et al. ocean reconstruction | biomass | $\zeta\approx1.04$ | admissible, but predicted ≈1.05 by existing size-spectrum theory |

## 5. Prior art and what would be new

Nearly every theoretical component is published, and a paper presenting them as discoveries
would be rejected.

- **Exponent equation and ζ = 1 limit:** Reed 2001; Reed and Hughes 2002 (who already argue this
  "killed exponential growth" mechanism explains power laws across domains); Saichev, Malevergne
  and Sornette 2010; Malevergne, Saichev and Sornette 2013 (who call Zipf's law the signature of
  the long-term optimal allocation of resources); Gabaix 1999; Luttmer 2007; Levy and Solomon
  1996; Malcai, Biham and Solomon 1999; Blank and Solomon 2000; Beare and Toda 2022 (general
  exponent theory with resets and type switching).
- **Zero-parameter tests in single domains:** Zhang and Sornette 2011 ($\zeta=0.75\pm0.05$
  predicted and observed); Hisano, Sornette and Mizuno 2011.
- **Domain criteria:** Sheldon et al. 1972 and size-spectrum theory; Hudson 1991 ($\alpha=2$,
  observed energy index ≈1.8); Aki 1981; Junge aerosols; pink noise.
- **Cross-domain geometric claim:** Aschwanden's scale-free probability conjecture (2014;
  Aschwanden and Scholkmann 2025 preprint, 64 distributions). In this notation it is logarithmic
  orthopolity in area for three dimensions.
- **Maximum entropy and invariance:** Jaynes 1968; Frank 2009, 2016, 2019; Visser 2013;
  Pueyo et al. 2007; Harte 2011. None selects $\zeta=1$ without an added constraint.
- **Closest ecological statement:** Schwamborn 2025 (arXiv:2509.00023, not peer reviewed), which
  treats a slope near −1 as a constant across systems with stress-driven departures.

Not found in searches, and candidate contributions once full texts are checked:

1. The resource-variable formulation with the resource rule, closing the resource, coordinate and
   cutoff loopholes together.
2. The cohort–age equivalence: flat resource per log size iff equal expected resource per unit
   age, which gives a test from age data without fitting a tail.
3. The transport identity $B=F/v$ as one deviation formula across Gibrat stocks, cascades,
   coagulation and size spectra.
4. The first pre-registered, multi-domain, out-of-sample test of the exponent equation, scored
   against strong nulls and including a domain where $\zeta<1$ is predicted.

## 6. Decisive tests

All are frozen and registered before outcome data are examined, preferably as Stage 1 of a
Registered Report.

**T1 — out-of-sample prediction across domains (central).** For each system, estimate $\mu$,
$\sigma^2$, $h$, $\nu$ and the entry scale from panel records in an earlier window, then predict
$\zeta$ and the slope of $B(u)$ for a later cross-section. Requirements from the referee review:

- *Nulls that remove the accounting component.* Because $\phi=J_R/Q$ uses the cross-section, the
  prediction must beat both persistence (each system's own earlier $\zeta$) and a moment null
  ($\zeta$ from the earlier mean-to-entry-size ratio). Incremental skill over the moment null is
  the headline result.
- *Dynamical content beyond accounting.* Estimate rates on a subpopulation disjoint from the
  tested cross-section, or predict transients (front position after a founding epoch,
  relaxation after a documented shock).
- *Estimation.* Truncated-Pareto likelihood between the entry scale and the finite-age front
  (Aban, Meerschaert and Panorska 2006); block bootstrap for common shocks; joint bootstrap of
  $(\phi,m,\zeta)$, since the same top units dominate all three.
- *Power.* Separating an exponential $B(u)$ from a broad lognormal needs about $10^4$ tail units
  per system (simulated power 0.14 at 1,600, 0.85 at 16,000). A calibration regression needs at
  least about 15 systems with a spread in $\phi/m$ of at least 0.2. Below these thresholds the
  study is declared uninformative in advance.

Candidate data, with known weaknesses stated in advance: US Census Business Dynamics Statistics
(public tables are binned, with an open top class); multitemporal urban-centre delineations with
independent censuses, mergers treated as a coagulation term; and repeated forest censuses (Barro
Colorado Island, 8 censuses 1982–2015), where Gibrat fails and demographic rates must predict a
top-heavy biomass distribution. A prospective test on a system with a public data feed is the
only fully blind option.

**T2 — sign and residence-time rule.** From documented dynamics only, coded blind to exponents by
two coders with reported agreement, classify systems drawn from a predefined frame (for example,
every dataset in Clauset et al. 2009 and the MetaZipf compilation with unit-level panels).
Predict: stationary stocks with entry have $\zeta>1$, approaching 1 as $m\tau_{\rm res}$ grows;
$\zeta<1$ occurs only in non-stationary stocks or other classes.

**T3 — geophysics, as an out-of-class control.** With measured rupture areas from a finite-fault
database, test $\zeta_A=b$ below and $4b/3$ above width saturation, and stress-dependent $b$
against an independent stress model. This tests scaling relations, not orthopolity.

**T4 — ecology.** Compare predictions with $\lambda=2+q-n$ and the $TE$/$PPMR$ relation on systems
where those quantities are measured; tolerances must be smaller than the differences between
models (about 0.05 in slope).

## 7. Falsification criteria

- The calibration regression of $(\zeta_{\rm obs}-1)$ on $(\zeta_{\rm pred}-1)$ has a slope whose
  95% interval excludes 1, or an intercept whose interval excludes 0.
- Out-of-sample skill over the persistence or moment null is not positive.
- A gated, relaxed system with large measured $m\tau_{\rm res}$ has $\zeta$ clearly away from 1.
- $\zeta\approx1$ is as frequent among systems with short residence as among those with long
  residence (the mechanism is not what selects $\zeta=1$).
- An admissible resource fails while another resource in the same system passes; both are reported.
- Fewer than a pre-registered fraction of candidate systems pass the gates. This limits the scope
  statement rather than falsifying the theorem, and gate failures never count as support.

## 8. Recommended paper

*Working titles:* "Equal resource per scale as the long-residence limit of proportional growth";
"Orthopolity: when scale-free transport allocates equal resource per logarithmic size, and why it
usually does not."

1. Accounting identity, measure dependence, vacuity lemma, resource rule.
2. Transport identity and the Gibrat-stock exponent equation, fully attributed; budget identity
   and $\zeta-1\approx1/(m\tau_{\rm res})$; simulation checks.
3. Class map: where orthopolity is and is not predicted.
4. Pre-registered T1 and T2; out-of-class controls; the repository's proxies as a loophole
   demonstration in supplementary material.
5. Failures reported with the same prominence as successes.

Sequence: theory note and protocol as a preprint and Registered Report Stage 1; analyses on frozen
predictions; prospective follow-up. Royal Society Open Science (Registered Report) or Physical
Review E are realistic. A general-science journal is plausible only if T1 succeeds in at least
three domains with positive skill over the nulls and a data collapse that includes a predicted
$\zeta<1$ case.

**Keep from the repository:** the accounting and measure sections of the manuscript, the vacuity
argument, the reproducibility infrastructure, the Gibrat code and simulation, and the earthquake
and flare pipelines as out-of-class controls. **Drop from the main argument:** cosmological,
social and "natural law" claims; the 2017 linear-allocation version (one sentence suffices);
rupture area and fluence as support; the GLOSSAQUA compatibility fractions and ensemble analyses,
which rest on defective metadata and cannot test a mechanism; maximum-entropy "derivations";
resource-weighted Benford tests, which are correct but have about $1/M^2$ of the information of a
slope fit over $M$ decades; "friction" without a formula.

## Sources

Full citations are in [references.md](references.md).
