# Fresh network sources and the BioMe qualification

23–24 October 2026. The preceding
[audit](topology-source-audit-2026-10-23.md) is preserved. This follow-up sought
new sources rather than repeatedly reopening excluded archives. It found an
accessible raw-pair dataset, completed a fixed stock diagnostic, and clarified
established prior art. **A matched network forecast remains unqualified.**
This is a bounded search, not proof that suitable public data do not exist.

## The usable archive and the limitation it actually tests

[Jo et al. (2023), BioMe](https://doi.org/10.1128/msystems.00017-21), provides
raw dye measurements, independent optical standards, no-pore controls and
fabrication drawings in a
[public repository](https://github.com/segrelab/co_culture_device/tree/c9f6321c4a9dc70bfe6b9553dbecb17b5c228983).
It implements 30 isolated pairs, not a multiwell network. The
[fixed diagnostic](biome-stock-audit-results-2026-10-23.md) retains all pairs
and uses the correct dye-specific optical channels, correcting a misassignment
in the two deposited scripts without changing those originals.
Apparent no-pore stock loss and unstable control normalization prevent an
independent connector-capacity interpretation. This is useful measurement
qualification, not the originally sought topology intervention.

## Other new sources

| Source | What is available | Qualification finding |
| --- | --- | --- |
| [Ponce and Cordero (2020), microfluidic Voronoi networks](https://doi.org/10.1103/PhysRevE.101.023110); [primary preprint](https://arxiv.org/html/1903.07681v2) | Methods and separate free-diffusion calibration; fluorescence recovery in fabricated networks | A promising continuum-network alternative. Raw geometry, bleaching masks, reference images and complete recovery records were not located. Network-fitted effective diffusivity is not an independent input. Observation bleaching requires explicit controls. |
| [Camacho, Edwards and Engheta (2020), modulated capacitive network](https://doi.org/10.1038/s41467-020-17550-5) | Actual switched-capacitor experiment; primary XML and BioStudies inventory list two PDFs and two GIFs | The experimental left end is attached to a voltage source; it is an open, time-varying system. No raw node table or independent component-calibration archive was identified; code is on request. Time modulation alone would not disprove charge conservation: the appropriate equation is for charge `Q=C(t)V`, with boundary injection included. |
| [ASEN 3802 metal-rod conduction archive](https://github.com/TariqSawaqed1/Heat-Conduction-Aerospace-Lab/tree/aba5a8c3c1d52fb879710cdddcfb23d29b079f03) | Five real heated-rod cases, eight thermocouples, nominal material properties and heating power | An open heat-equation candidate, not closed redistribution. The source fits the boundary intercept to target steady-state data. Independent boundary/sensor characterization remains unidentified. Raw time series were not decoded. |
| [Schanke et al. (2022), protocell nanotubes](https://doi.org/10.1039/D2NR02290G) | Methods, supplementary material and movie listed | Branched geometry and losses/bleaching; tube dimensions inferred from transport. No complete independent geometry plus raw stock archive identified. |
| [Santoso et al. (2026), physics-based toolbox](https://doi.org/10.1038/s42005-026-02590-y) | Public simulation toolbox and measured precipitation geometry | Concentration fields are simulated virtual probes; these do not supply measured conservative network relaxation. |
| [Nebuloni et al. (2024), fluid-wall gradients](https://pmc.ncbi.nlm.nih.gov/articles/PMC11189932/) | Primary methods and profiles | Continuously fed laminar streams and steady gradients, requiring an open transport design. |
| [Baranger et al. (2020), individual hyphae](https://pmc.ncbi.nlm.nih.gov/articles/PMC7481688/); [Dryad](https://doi.org/10.5061/dryad.76hdr7ss1) | Article and public data identifier | Cell-free dye control is perfused; convection accompanies diffusion. |
| [Williams et al. (2022), active-particle confinement](https://pmc.ncbi.nlm.nih.gov/articles/PMC9378696/); [Zenodo](https://doi.org/10.5281/zenodo.6866462) | Public article, data and code identifier | Active algae drive particle motion; the passive control has no appreciable filling over its observation window. |

These exclusions are relative to the specific closed pair-to-network design.
Driven systems can test different predictions with separately fixed boundary
fluxes, capacities and observation models. They should not be relabeled as
closed conservative experiments. For charge, heat or solute stocks the relevant
reference weights are physical capacitance, heat capacity or accessible volume,
neither log-orthopolic nor linear-orthopolic size allocation.

## Prior art and what the construction adds

[Lizana and Konkoli (2005)](https://doi.org/10.1103/PhysRevE.72.026305) already
derive memory equations for diffusion between reservoirs connected by tubes,
including finite tube storage and limits of well-mixed reservoir approximations.
Their [primary preprint](https://arxiv.org/abs/cond-mat/0503273) is retained
with a hash in the BioMe acquisition receipt. It studies theory and numerical
examples; it is not a new empirical dataset.

The [specific counterexample](topology-storage-2026-10-23.md) gives identical
pair observations with different subsequent network relaxation and identifies
a calibration that can distinguish the hidden capacities. Its value here is
the sharp prediction/identifiability check. It does not establish discovery of
diffusion memory or a unique mechanism beyond established transport theory.
Supporting S5.19 now attributes that prior work explicitly.

## Exposure and stopping rule

Published descriptions, figures' textual captions and numerical summaries
were exposed for these sources. Examples include the Voronoi diffusivity
summaries, the capacitive voltage enhancement, and active/passive transport
comparisons. No new raw response arrays except the BioMe cells were decoded.
BioMe access followed pushed design `43b1bd2` and pre-access amendment
`59bd2b7`; it remains a retrospective source diagnostic with known qualitative
publication outcomes. No new empirical registry record is added.

Do not repeat these searches without new metadata or released files. Reopen
BioMe only for an explicitly exploratory reanalysis or with independent
optical/loss and connector-loading information. A future topology test needs
actual node stocks, matched link characterization and initial conditions,
plus independently bounded connector storage. Prioritize archives with those
measurements over another successful fit of normalized curves.
