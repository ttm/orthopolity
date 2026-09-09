# References

Works the other documents depend on, grouped by their role in the argument. Core size-spectrum
citations, dataset provenance and statistical-method references were checked against publisher
pages, author repositories or original papers on 2026-09-09. This is a focused source audit, not a
systematic literature review or proof of novelty; the broader background list remains a reading
list. The manuscript should cite only sources supporting claims it actually retains.

## The closest prior art — equipartition of a measured resource

Equal biomass across logarithmic mass classes and variation among individual communities were
studied well before this project. Re-expressing those results is a useful benchmark, but cannot
establish either priority for the identity or independent confirmation of it.

- **Sheldon, R. W., Prakash, A., & Sutcliffe, W. H., Jr. (1972).** The size distribution of
  particles in the ocean. *Limnology and Oceanography* 17(3), 327–340.
  [Publisher](https://doi.org/10.4319/lo.1972.17.3.0327). The original ocean-size-spectrum
  hypothesis; observed spectra also varied geographically and with depth.
- **Gaedke, U. (1993).** Ecosystem analysis based on biomass size distributions: A case study
  of a plankton community in a large lake. *Limnology and Oceanography* 38(1), 112–127.
  [Publisher](https://doi.org/10.4319/lo.1993.38.1.0112). Explicitly relates a flat Sheldon
  biomass spectrum to a normalized biomass slope of −1 and studies seasonal variation.
- **Arranz, I., Fournier, B., Lester, N. P., Shuter, B. J., & Peres-Neto, P. R. (2022).**
  Species compositions mediate biomass conservation: The case of lake fish communities.
  *Ecology* 103(3), e3608. [Publisher](https://doi.org/10.1002/ecy.3608);
  [author data archive](https://doi.org/10.5281/zenodo.5775491). Tests environmental and
  community-composition explanations across more than 600 Canadian lake fish communities.
  Consequently, this repository cannot claim to introduce testing at the individual-system level.
- **Perkins, D. M., et al. (2018).** Bending the rules: exploitation of allochthonous resources
  by a top-predator modifies size-abundance scaling in stream food webs. *Ecology Letters*
  21(12), **1771–1780**. [Publisher](https://doi.org/10.1111/ele.13147);
  [author manuscript](https://pure.roehampton.ac.uk/ws/files/1018876/Perkins_et_al._ELE_revised_submission_FINAL_.pdf).
  Its Methods use abundance in logarithmic mass bins without linear-bin-width normalization.
  This supports a specific mismatch with the GLOSSAQUA label, not a reconstruction of every
  other study's convention from its observed exponent. The former manuscript's page 1721 was wrong.
- **Hatton, I. A., Heneghan, R. F., Bar-On, Y. M., & Galbraith, E. D. (2021).** The global ocean
  size spectrum from bacteria to whales. *Science Advances* 7, eabh3732.
  [Article](https://doi.org/10.1126/sciadv.abh3732) — Reconstruction of ocean biomass per
  logarithmic body-mass class. Data archive:
  <https://doi.org/10.5281/zenodo.5520055>; authors' repository `ryanheneghan/sheldon_revisited`.
- **Cuesta, J. A., Delius, G. W., & Law, R. (2018).** Sheldon spectrum and the plankton paradox:
  two sides of the same coin — a trait-based plankton size-spectrum model. *Journal of Mathematical
  Biology* 76, 67–96. [Publisher](https://doi.org/10.1007/s00285-017-1132-7);
  [author preprint](https://arxiv.org/abs/1607.04158). A mechanistic plankton model linking
  allometric rates, species coexistence and the Sheldon spectrum.
- **Damuth, J. (1981).** Population density and body size in mammals. *Nature* 290, 699–700. —
  The original size–density power law, $N \propto M^{-3/4}$. This concerns species-population
  density versus characteristic body mass, not abundance pooled into community mass bins.
- **Nee, S., Read, A. F., Greenwood, J. J. D., & Harvey, P. H. (1991).** The relationship between
  abundance and body size in British birds. *Nature* 351, 312–313. — Coins "energetic equivalence
  rule". Note: a species-population relation, not community abundance per log size bin.
- **Isaac, N. J. B., Storch, D., & Carbone, C. (2013).** The paradox of energy equivalence.
  *Global Ecology and Biogeography* 22, 1–5. — Where and why it fails.
- **West, G. B., Brown, J. H., & Enquist, B. J. (1997).** A general model for the origin of
  allometric scaling laws in biology. *Science* 276, 122–126. — An exponent predicted rather than
  fitted: the standard to match.

## Scale invariance, dimension, and the geometric argument

- **Mandelbrot, B. B. (1982).** *The Fractal Geometry of Nature.* W. H. Freeman. — Box-counting
  dimension; $N(l) \propto l^{-D}$ is the essay's boxes argument.
- **Mandelbrot, B. (1953).** An informational theory of the statistical structure of language. —
  Origin of the Zipf–Mandelbrot form referenced in the essay.

## Why conservation and symmetry do not select equal allocation

- **Sreenivasan, K. R. (1995).** On the universality of the Kolmogorov constant. *Physics of Fluids*
  7, 2778–2784. — Inertial-range spectrum. Constant energy *flux* coexists with occupancy
  $\propto k^{-2/3}$: the stock/flux counterexample.
- **Jaynes, E. T. (1957).** Information theory and statistical mechanics. *Physical Review* 106,
  620–630.
- **Frank, S. A. (2009).** The common patterns of nature. *Journal of Evolutionary Biology* 22,
  1563–1585. — Distributions from constraints and invariances rather than mechanisms. The closest
  methodological sibling.
- **Visser, M. (2013).** Zipf's law, power laws and maximum entropy. *New Journal of Physics* 15,
  043021. <https://arxiv.org/abs/1212.5567> — Power laws from a constraint on
  $\langle \ln x \rangle$; constraining an additive mean instead gives an exponential.
- **Drăgulescu, A., & Yakovenko, V. M. (2000).** Statistical mechanics of money. *European Physical
  Journal B* 17, 723–729. <https://arxiv.org/abs/cond-mat/0001432> — Conserved quantity, exponential
  rather than power-law outcome.

## Generating mechanisms — the alternatives orthopolity would displace

- **Newman, M. E. J. (2005).** Power laws, Pareto distributions and Zipf's law. *Contemporary
  Physics* 46(5), 323–351. — The standard survey; the single most useful orientation document.
- **Mitzenmacher, M. (2004).** A brief history of generative models for power law and lognormal
  distributions. *Internet Mathematics* 1(2), 226–251.
- **Simon, H. A. (1955).** On a class of skew distribution functions. *Biometrika* 42, 425–440.
- **Yule, G. U. (1925).** A mathematical theory of evolution. *Phil. Trans. R. Soc. B* 213, 21–87.
- **Barabási, A.-L., & Albert, R. (1999).** Emergence of scaling in random networks. *Science* 286,
  509–512.
- **Zipf, G. K. (1949).** *Human Behavior and the Principle of Least Effort.* Addison-Wesley.

## Statistical methodology — non-negotiable for any empirical claim

- **Edwards, A. M., Robinson, J. P. W., Plank, M. J., Baum, J. K., & Blanchard, J. L. (2017).**
  Testing and recommending methods for fitting size spectra to data. *Methods in Ecology and
  Evolution* 8, 57–67. [Publisher](https://doi.org/10.1111/2041-210X.12641);
  [authors' reproducible code](https://github.com/andrew-edwards/fitting-size-spectra).
  Compares fitting methods and interval coverage. Reported regression errors cannot automatically
  be treated as calibrated measurement errors in a meta-analysis.
- **Edwards, A. M., Robinson, J. P. W., Blanchard, J. L., Baum, J. K., & Plank, M. J. (2020).**
  Accounting for the bin structure of data removes bias when fitting size spectra.
  *Marine Ecology Progress Series* 636, 19–33. [Publisher](https://doi.org/10.3354/meps13230).
  Shows that fitting methods and bin structure can change inferred trends. The warning about
  incompatible size-spectrum estimates therefore has substantial methodological prior art.
- **Clauset, A., Shalizi, C. R., & Newman, M. E. J. (2009).** Power-law distributions in empirical
  data. *SIAM Review* 51(4), 661–703. [Publisher](https://doi.org/10.1137/070710111);
  [author preprint](https://arxiv.org/abs/0706.1062). Basis for this project's likelihood fits,
  goodness-of-fit bootstraps and alternative comparisons. A non-rejection is not proof of a power
  law, and those tests do not themselves test resource equipartition.
- **Alstott, J., Bullmore, E., & Plenz, D. (2014).** powerlaw: a Python package for analysis of
  heavy-tailed distributions. *PLoS ONE* 9(1), e85777.
- **Stumpf, M. P. H., & Porter, M. A. (2012).** Critical truths about power laws. *Science* 335,
  665–666.
- **Broido, A. D., & Clauset, A. (2019).** Scale-free networks are rare. *Nature Communications* 10,
  1017.
- **Callaghan, C. T., et al. (2023).** Unveiling global species abundance distributions. *Nature
  Ecology & Evolution* 7, 1600–1609. — Poisson log-normal preferred in 38 of 39 classes. Not itself
  a test against every power-law model, and occurrence counts are not resource measurements.

## Data sources for the empirical tests

- **NOAA NCEI.** L2 XRS flare report, science-quality composite, 2022–2024, v1.0.1.
  <https://data.ngdc.noaa.gov/platforms/solar-space-observing-satellites/goes/multi/l2/data/xrsf-l2-flrpt_science/csv/>
- **USGS.** FDSN Event Web Service / ComCat. <https://earthquake.usgs.gov/fdsnws/event/1/>
- **USGS Earthquake Hazards Program.** Earthquake Magnitude, Energy Release, and Shaking Intensity.
  — Source of the $\log_{10}E = 5.24 + 1.44 M_w$ conversion.
- **Sakurai, T. (2022).** Probability Distribution Functions of Solar and Stellar Flares.
  <https://arxiv.org/abs/2212.02678> — Distinguishes pure-power, tapered and gamma-form fits; none
  should be promoted into a universal exponent of total flare energy.
- **Dugenne, M., et al. (2024).** First release of the Pelagic Size Structure database. *Earth System
  Science Data* 16, 2971–2999. — Highest-value next ecological test.
- **Ersoy, Z., et al. (2025).** GLOSSAQUA: a global dataset of size spectra across aquatic
  ecosystems. *Ecology* 106(3), e70050. [Publisher](https://doi.org/10.1002/ecy.70050);
  [archived v1.0.0](https://zenodo.org/records/14701391);
  [authors' repository](https://github.com/zeynepersoy/GLOSSAQUA_dataset).
  Compiles published and contributed slope estimates, not a uniform sample of independently
  measured communities. The original release reports 8,459 slopes from 127 sources; the precise
  subset and version used here must be stated separately. Authors explicitly note variation in
  extraction and fitting procedures. Publisher supporting metadata specifies CC-BY-NC-SA 4.0,
  while the GitHub repository and Zenodo record display MIT; see the source-specific notice in
  [data/NOTICE.md](../data/NOTICE.md), rather than treating all releases as unambiguously MIT.

## Structure that a resource model must explain

- **Kelvin, L. S., et al. (2014).** Galaxy And Mass Assembly (GAMA): stellar mass functions by
  Hubble type. *MNRAS* 444, 1647–1655. — Double-Schechter form with characteristic mass and
  exponential cutoff. Curvature to be explained, not called friction.

## Cosmology — why the "third cosmological principle" framing fails

- **Sylos Labini, F., Montuori, M., & Pietronero, L. (1998).** Scale-invariance of galaxy
  clustering. *Physics Reports* 293, 61–226.
- **Hogg, D. W., et al. (2005).** Cosmic homogeneity demonstrated with luminous red galaxies.
  *Astrophysical Journal* 624, 54–58.
- **Scrimgeour, M. I., et al. (2012).** The WiggleZ Dark Energy Survey: the transition to large-scale
  cosmic homogeneity. *MNRAS* 425, 116–134.
- **Jacobson, T. (1995).** Thermodynamics of spacetime: the Einstein equation of state. *Physical
  Review Letters* 75, 1260–1263. — Context for thermodynamic gravity, not support for orthopolity.
- **Carroll, S. M. (2001).** The cosmological constant. *Living Reviews in Relativity* 4, 1.

## Other domains and deprioritised directions

- **Gabaix, X. (1999).** Zipf's law for cities: an explanation. *Quarterly Journal of Economics*
  114(3), 739–767.
- **Gabaix, X. (2009).** Power laws in economics and finance. *Annual Review of Economics* 1, 255–293.
- **Stevens, S. S. (1957).** On the psychophysical law. *Psychological Review* 64(3), 153–181. —
  Cited in the essay; see [concept.md §11](concept.md) for why it does not belong.
- **Landauer, R. (1961).** Irreversibility and heat generation in the computing process. *IBM Journal
  of Research and Development* 5, 183–191. — See [not-worth-pursuing.md B5](not-worth-pursuing.md).
- **Enge, K., et al. (2024).** Open your ears and take a look: a state-of-the-art report on the
  integration of sonification and visualization. *Computer Graphics Forum* 43(3).
  <https://arxiv.org/abs/2402.16558> — See [not-worth-pursuing.md B1](not-worth-pursuing.md).

## Primary sources for this repository

- **Fabbri, R. (2024).** The Orthopolity cosmological principle and the Natural distribution law.
  [Author's essay](https://ttm.github.io/2024/08/14/power.html). Motivation and a source for the
  original claim, not independent scientific evidence. Its discrete-class accounting does not
  uniquely select logarithmic rather than linear classes in a continuous formulation.
- **Fabbri, R., & Oliveira, O. N., Jr. (2017).** A simple model that explains why inequality is
  ubiquitous. Manuscript dated 17 March 2017, supplied privately as `essay.pdf`. Discussed as an
  antecedent to the 2024 essay; no publication or peer-review status is inferred from the local file.
- **Fabbri, R.** Earlier related work. <https://zenodo.org/records/3973549>
- **Private assessment and pilot lab**, supplied by the author, September 2026. Findings seeded
  the repository analysis. This is project provenance, not an independent replication or a
  peer-reviewed source.

## Publication venues assessed

- **Physical Review E** — scope: <https://journals.aps.org/pre/about>
- **PLOS ONE** — criteria including negative results:
  <https://journals.plos.org/plosone/s/criteria-for-publication>
- **Journal of Open Source Software** — requires >6 months public development history:
  <https://joss.readthedocs.io/en/latest/submitting.html>
