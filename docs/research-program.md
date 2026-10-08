# Establishing orthopolity: a research programme

Prepared 8 October 2026 for the authors. It answers a narrower question than the
[manuscript](paper.md): what form of the claim could be established as a general property of
real systems, what has already been published, and which tests would decide it. Literature
statements were checked from search extracts and abstracts; full texts could not be opened from
this environment. Items marked *(verify)* need a primary-text check before citation.

## 1. The claim in a form that can be tested

For objects holding an additive resource $q$, logarithmic orthopolity states that the
**resource-weighted distribution of log size is uniform**. If the resource itself is the size
coordinate, this is Zipf's law with survival exponent $\zeta_q=1$ (density exponent 2): equal
total resource in every factor-of-ten class. It is the marginal case between bottom-heavy
($\zeta>1$, small objects hold most resource) and top-heavy ($\zeta<1$, large objects hold most)
allocations, and the only power law for which neither cutoff dominates the total.

One restriction comes first. **For any power law $dN/dk\propto k^{-\alpha}$, the weight
$q\propto k^{\alpha-1}$ is exactly orthopolitic.** "Orthopolity holds for some resource" is
therefore empty. The repository's own earthquake catalogue shows the problem concretely: the same
fit, $b=0.998$ [0.973, 1.024], gives $\zeta=0.666$ for seismic moment and $\zeta=0.998$ for
rupture area under self-similar scaling ([resource_choice.json](../results/resource_choice.json)).
The resource must be fixed by a rule stated before the data are examined.

**Proposed rule.** The resource is the additive quantity whose per-object changes are
proportional to the amount held, measured as growth rates of identifiable objects. This rule is
checkable in advance from panel data, and it connects the claim to a mechanism (§2). Event
catalogues, which have no persistent holders, need a separate rule and are a separate class (§3).

## 2. The mechanism: scale-indifferent dynamics of a conserved resource

"Nature does not care about concentration" has a precise dynamical counterpart: **Gibrat's law**,
under which an object's relative growth is independent of its size. Two exact results then make
orthopolity a stationary state rather than an assumption.

- **Kesten–Goldie.** For $X_{t+1}=A_tX_t+B_t$ with $E[\ln A]<0$, the stationary tail is
  $P(X>x)\sim x^{-\zeta}$ with $E[A^\zeta]=1$. Hence $\zeta=1$ exactly when $E[A]=1$, that is,
  when proportional changes conserve the resource on average (Kesten 1973; Goldie 1991).
- **Entry and exit.** With geometric Brownian growth (drift $g$, variance rate $\sigma^2$, both
  relative to entrants), exit hazard $h$ and entry growing at rate $d$, the tail exponent solves
  $(\sigma^2/2)\zeta^2+(g-\sigma^2/2)\zeta-(d+h)=0$ (Reed 2001; Saichev, Malevergne and Sornette
  2010). Rearranged,

  $$(\zeta-1)\left(g+\tfrac{\sigma^2}{2}\zeta\right)=\phi,\qquad \phi=d+h-g,$$

  where $\phi$ is the share of the normalized total injected by entrants per unit time.
  **Orthopolity holds iff $\phi=0$.** Injection at the small end ($\phi>0$) makes the
  allocation bottom-heavy; incumbents outgrowing turnover ($\phi<0$) makes it top-heavy and
  non-stationary in the mean.

The function `gibrat_zeta` implements this law with tests, and
[run_gibrat.py](../experiments/run_gibrat.py) checks it with a population simulated from empty:
the tail exponent follows the law from $\zeta=0.81$ at $\phi=-0.02$ to $1.60$ at $\phi=0.05$,
with $0.988\pm0.010$ at $\phi=0$ ([gibrat.json](../results/gibrat.json)).

This gives the paper the structure physicists expect of a law with corrections. Orthopolity is
the ideal limit; each constraint enters as a measurable term:

| Constraint | Deviation it predicts | Source |
|---|---|---|
| Entry or a floor injects a share $\phi$ | $(\zeta-1)(g+\sigma^2\zeta/2)=\phi$; reflecting floor: $\zeta=1/(1-s_{\min}/\bar s)$ | Gabaix 1999; Malevergne et al. 2013 |
| Size-dependent growth or volatility | local $\zeta(S)=1-2\mu(S)/\sigma^2(S)+d\ln\sigma^2/d\ln S$ | Gabaix 1999 *(verify sign)*; Ioannides and Overman 2003 |
| Finite system | Upper cutoff where the total is reached | — |
| Trophic losses (ecology) | biomass slope $=1/4+\ln TE/\ln PPMR$ | Jennings and Mackinson 2003; Mehner et al. 2018 |
| Encounter vs metabolic scaling (ecology) | biomass slope $=n-q$ | Andersen and Beyer 2006; Hartvig et al. 2011 |
| Rupture width saturates (earthquakes) | rupture-area $\zeta_A=4b/3$ above about M 6.7 | Hanks and Bakun 2002 |
| Differential stress (earthquakes) | $b\approx1.23-0.0012\,\Delta\sigma$ [MPa] | Scholz 2015 |

The weakness to address: $\zeta=1$ is a knife-edge in these models. A 3% mean imbalance in a
Kesten process moves $\zeta$ from 1 to about 1.7 or 0.3. The paper must explain why real systems
sit near $\phi=0$. Candidate arguments exist — normalization by a conserved total (Gabaix),
balanced or maximum sustainable growth (Malevergne et al. 2013) — and must be stated and tested,
not assumed.

## 3. Where orthopolity is not expected

Other mechanisms have their own exponents. Treating them as confirmations or as "constrained
orthopolity" would make the claim unfalsifiable; stating them explicitly sharpens it.

| Class | Mechanism | Predicted $\zeta$ of the resource |
|---|---|---|
| Collisional fragmentation | Dohnanyi constant-mass-flux cascade | 5/6 (mass); $5/(6+s)$ with strength scaling $s$ |
| Source-driven coagulation | Smoluchowski, kernel homogeneity $\nu$ | $(1+\nu)/2$ |
| Mean-field avalanches | Critical branching / depinning | moment $1/2$; area $3/4$ |
| Lakes | Critical percolation of topography | 96/91 ≈ 1.055 (area) |
| Fractal-diffusive SOC | Aschwanden | energy 2/3 |

## 4. Evidence map

A 49-system compilation of published exponents
([zeta-compilation.md](zeta-compilation.md)) gives a class-dependent picture:

| Class | Typical $\zeta$ | Within ±0.1 of 1 | Examples |
|---|---|---|---|
| Stocks with proportional growth | 0.9–1.1 | about half | US firms 1.06; US metro areas 1.005; natural cities ≈1; ocean biomass 1.04; aquatic spectra 1.015 |
| Stocks from other mechanisms | 0.3–1.4 | few | trees 0.38; galaxy stellar mass 0.47; IMF 1.35 / 0.3; lakes 1.14 |
| Events and cascades | median ≈0.8 | few | seismic moment 0.63–0.68; cyclone dissipation 0–0.25; wildfire 0.3–0.75; flare energy 0.5–0.8 |
| Degrees and counts (not resources) | median ≈1.4 | — | excluded |

The least selected compilation, Clauset, Shalizi and Newman (2009), has a median near 1.3 and
does not centre on 1. Stocks with proportional growth are the class where orthopolity is close,
and that is the class the mechanism of §2 covers. Even there are clear exceptions: administrative
US places $1.4\pm0.1$, Forbes wealth 1.1–1.5, mutual funds without a power-law tail. Each
exception is a test of the deviation law, not a reason to discard it.

The repository's own direct fits:

| System | Resource | Estimate | Reading |
|---|---|---|---|
| USGS earthquakes 2010–2024 | rupture area (self-similar) | $\zeta=0.998$ [0.973, 1.024] | orthopolitic; post hoc resource |
| same | rupture area, M ≥ 6.7 (width saturation) | $\zeta=1.36$ [1.29, 1.44] | departure in the direction the constraint predicts |
| same | seismic moment | $\zeta=0.666$ [0.649, 0.683] | top-heavy |
| GOES flares 2022–2024 | end fluence, as supplied | $\alpha=2.13$ [2.03, 2.22] | near 2, excludes it |
| same | end fluence minus background (approximate) | $\alpha=1.90$ [1.82, 1.99] | near 2, excludes it |
| Hatton et al. ocean reconstruction | biomass | $\zeta\approx1.04$ | near 1; predicted ≈1.05 by $\lambda=2+q-n$ |

## 5. Prior art and what would be new

Most components are published. A paper presenting them as discoveries would be rejected.

- **ζ = 1 from proportional growth with conservation:** Levy and Solomon 1996; Gabaix 1999;
  Malcai, Biham and Solomon 1999; Saichev, Malevergne and Sornette 2010; Malevergne et al. 2013,
  who already describe Zipf's law as "the signature of the long-term optimal allocation of
  resources".
- **Zero-parameter predicted deviations, single domains:** Zhang and Sornette 2011 (social groups,
  $\zeta=0.75$ predicted and observed); Hisano, Sornette and Mizuno 2011 (product markets).
- **Domain-specific equal-per-log criteria:** Sheldon et al. 1972 and size-spectrum theory;
  Hudson 1991 ($\alpha=2$ for flares); Aki 1981 ($b=D/2$, rupture area); Junge aerosols; pink noise.
- **Cross-domain geometric claim:** Aschwanden's scale-free probability conjecture
  ($N(L)\propto L^{-d}$; Aschwanden and Scholkmann 2025 compare 64 distributions). In this
  repository's notation it is linear orthopolity in volume, equivalently logarithmic orthopolity
  in area for $d=3$.
- **Maximum entropy and invariance:** Jaynes 1968; Frank 2009, 2016, 2019; Visser 2013;
  Pueyo et al. 2007; Harte 2011, whose METE gives $\varepsilon^{-2}$ only within a window.
- **Closest ecological statement:** Schwamborn 2025 (arXiv:2509.00023, not peer reviewed) calls
  slope −1 an equilibrium constant with stress-driven deviations.

What searches did not find, and could be the contribution:

1. One resource-weighted criterion applied across stocks and events, with the vacuity lemma and an
   a priori resource rule.
2. The deviation law in injection-share form, $(\zeta-1)(g+\sigma^2\zeta/2)=\phi$, used as a
   single cross-domain prediction with independently measured $\phi$, $g$, $\sigma^2$.
3. A sign rule tested as a prediction: stationary conserved stocks with entry at the small end
   have $\zeta\ge1$; $\zeta<1$ requires incumbent growth exceeding turnover or a different class.
4. An explicit partition into classes where orthopolity is and is not predicted (§3).

## 6. Decisive tests

Each should be registered publicly, with code frozen, before the outcome data are examined.

**T1 — zero-parameter prediction across domains (the central test).** In at least three domains
with object-level panel data, estimate $g$, $\sigma^2$, $h$, $d$ (and their size dependence)
from growth, entry and exit records alone. Predict $\zeta$, then compare with an independently
fitted tail (Clauset–Shalizi–Newman estimator with lognormal comparison). Candidate data: US
Census Business Dynamics Statistics or Compustat (firms); natural-city populations from census
series (Rozenfeld et al. 2011); repeated forest censuses such as ForestGEO, where Gibrat fails and
the local deviation formula must predict the observed top-heavy tree-biomass distribution. Success
criterion: predicted and observed $\zeta$ agree within their joint uncertainty in every domain,
and the prediction beats a fitted-$\zeta$ null on held-out years.

**T2 — sign rule.** Classify systems as stationary conserved stocks, growing stocks, events, or
cascades from their dynamics alone, blind to exponents, then test whether the first class has
$\zeta\ge1$ and clusters at 1 more tightly than the others.

**T3 — constraint-predicted deviations in geophysics.** With measured rupture areas from a
finite-fault database (e.g. SRCMOD), test $\zeta_A=b$ for small and moderate events and
$\zeta_A=4b/3$ above width saturation. Test stress-dependent $b$ against an independent stress
model rather than faulting style.

**T4 — ecology.** Compare orthopolity-plus-constraint predictions with the established
$\lambda=2+q-n$ and $TE$/$PPMR$ models on systems with measured transfer efficiency and
predator–prey mass ratio. The tolerance must be smaller than the difference between those models
(about 0.05 in slope).

## 7. Falsification criteria

The general claim fails if any of the following holds:

- In T1, measured growth, entry and exit rates fail to predict $\zeta$ in two or more domains, or
  a stationary conserved stock has $\phi\approx0$ measured but $\zeta$ clearly away from 1.
- In T2, stationary conserved stocks do not cluster nearer $\zeta=1$ than the other classes.
- The a priori resource rule selects a quantity whose $\zeta$ is far from 1 in a system the
  programme classifies as in scope.

## 8. Recommended paper

*Working title:* "Equal resource per scale as the stationary state of scale-indifferent allocation."

1. Definition, vacuity lemma, resource rule.
2. Theorem: Kesten–Goldie criterion and the deviation law, with full attribution; simulation check.
3. Classes where the law does and does not apply.
4. Pre-registered T1 across three domains; T2 meta-analysis; repository case studies as
   illustrations, labelled post hoc.
5. Explicit list of failures.

A paper with T1 succeeding in several domains is a candidate for a general-science journal; the
theory plus T2 alone fits Physical Review E or Journal of the Royal Society Interface. Without T1
the novelty over Malevergne, Saichev and Sornette is thin.

**Drop:** cosmological and social-normative claims; energy as the earthquake resource except as a
reported failure; "friction" or "constraint" terms without a formula and measured inputs; pooling
events with stocks as confirmations.

## Appendix A. Sources

Full citations for the works named above are recorded in [references.md](references.md).
