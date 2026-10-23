# Network transfer: public sources and qualification limits

23 October 2026, including searches begun on 22 October. This follows the
[19 October design](equalization-release-design-2026-10-19.md) and
[completed membrane-pair transfer](membrane-exchange-results-2026-10-22.md).
**No newly inspected source qualifies the proposed closed pair-to-network
forecast.** Some data are accessible; independent calibration and the right
observable remain missing. This is a bounded source audit, not evidence that
no suitable public data exist and not a 45th empirical study.

The intended resource is solute amount, heat stored relative to a fixed
reference, or electrical charge. Reference weights are independently measured
volumes, heat capacities or capacitances, respectively: **neither log-orthopolic
nor linear-orthopolic size allocation**. Electrical field energy is dissipated
in resistive equalization; it cannot replace charge as the conserved resource.

## Reachable data do not automatically provide an independent prediction

| Source | Public availability | Qualification finding |
| --- | --- | --- |
| [Funayama et al., nanoscale thermal diffusion (2026)](https://doi.org/10.1038/s42005-026-02763-9) | [Figshare 32788554](https://api.figshare.com/v2/articles/32788554), two files | Conductivity is fitted to the experimental network decay; large end reservoirs remove heat from the observed lattice. |
| [Hu et al., passive aluminum lattice (2022)](https://doi.org/10.1002/adma.202202257) | Publisher lists fitted-generator ZIP; raw data on request | Generator inferred from the network response itself; no separate pair calibration located; environmental cooling present. |
| [Xu et al., spatiotemporal thermal lattices (2022)](https://doi.org/10.1038/s41567-021-01493-9) | Four publisher source workbooks listed | Motor-driven fluid advection, rather than the specified passive symmetric exchange experiment. |
| [Temporal anti-parity–time symmetry (2026 issue)](https://doi.org/10.1038/s41567-025-03129-8) | Ten source workbooks listed | Actively switched material properties and rotating rings; requires a separately specified driven transport model. |
| [Localized and delocalized topological modes of heat (2024)](https://doi.org/10.1073/pnas.2408843121) | Primary XML lists a supplement and three movies | Feedback-controlled thermoelectric elements, water sinks and periodic forcing implement an active analog. |
| [Supercapacitor dynamics (2026)](https://doi.org/10.1080/19397038.2026.2720202) | [Zenodo 18979232](https://zenodo.org/api/records/18979232), two workbooks | Terminal discharge of a 20-cell module; no individual-node redistribution or independent topology switch identified. |
| [Bachler et al., microdroplet membranes (2021)](https://doi.org/10.1021/acs.analchem.0c04939) | Existing supplement inventory; ETH bundle listing now reachable | Still closest physical design; raw matched pair/chain stock measurements remain unidentified. |
| [Sun et al., reconfigurable droplets (2024)](https://doi.org/10.1038/s41467-024-45214-1) | Source workbook listed | Documented linear/Y networks are pumped; pair profiles do not establish calibrated whole-compartment stocks. |
| [Valet et al., nanopore diffusion (2019)](https://doi.org/10.1103/PhysRevLett.123.088101) | Article and [preprint](https://arxiv.org/abs/1902.04912) | Relevant linear droplet arrays; no public raw archive plus matched pair calibration identified. |
| [Fica et al., interconnected bilayer emulsions (2026)](https://doi.org/10.1038/s41563-026-02679-3) | Texas raw-data DOI; public simulation archive metadata | Osmotic folding changes geometry and couples transport to mechanics; the fixed-volume chain design does not apply directly. |

### Nanoscale archive: accessible, but the calibration is target-derived

The [Figshare inventory](https://api.figshare.com/v2/articles/32788554) identifies
version 1, CC BY 4.0, with `Analysis for Fig1-3-4.ipynb` (202,981 bytes,
MD5 `986ab8448aec1b2f0fc378fbd84774fa`) and `Figure2.xlsx` (49,052 bytes,
MD5 `406a004907460af541b61bd7f73638d1`). Neither file was downloaded or decoded.
The accepted manuscript's Methods 4.1 describes varying thermal conductivity
until simulated and experimental decay agree. The modeled silicon ends act as
large thermal reservoirs; Methods 4.2 documents fabricated geometry. Geometry
alone therefore does not make the reported conductivity an independent input.
This stops the proposed test before numerical access. It does not contradict
the source's stated effective-model purpose.

### Passive thermal and electrical alternatives

Hu's article describes a measured 24-by-24 generator extracted from temperature
trajectories. Its 6.1 kB
[supplementary ZIP](https://advanced.onlinelibrary.wiley.com/action/downloadSupplement?doi=10.1002%2Fadma.202202257&file=adma202202257-sup-0002-SuppMat.zip)
returned HTTP 403; members were not inspected. A fitted generator is not a
substitute for unseen raw responses. Published convection and outcome summaries
were exposed, including fitted edge rates 0.52/0.91 per minute.

The supercapacitor inventory supplies constant-power and constant-current
workbooks (15,601 and 16,570 bytes; respective MD5s
`6653b564714fd06fb3ce4ab41a40fb9c` and
`94fba64c7e3683336bd4096dd22c6cbe`). They were not decoded. Equivalent internal
branches fitted to terminal measurements do not independently determine stocks
in physical nodes. The PNAS thermal array similarly has real measurements,
but programmed heating/cooling supplies its couplings and an external budget.
These sources could support other questions after a new design.

### Droplet follow-up and remaining accessibility leads

The [ETH thesis bundle listing](https://www.research-collection.ethz.ch/server/api/core/items/dded41e0-59e8-45a8-a176-e6bcfede279f/bundles)
now returns 200 and identifies ORIGINAL bundle
`a340f000-3ad9-41a2-95ad-ece4fb12c49d`. Its
[bitstream inventory](https://www.research-collection.ethz.ch/server/api/core/bundles/a340f000-3ad9-41a2-95ad-ece4fb12c49d/bitstreams)
returned 429, including one bounded retry. The previous ACS/BioStudies inventory
and observation concerns remain as recorded in the
[20 October audit](exchange-source-followup-2026-10-20.md).

Sun's methods use fixed-position fluorescence and pair line profiles. Larger
linear/Y channels use syringe pumps at 2.0 mL/h; the three-color mixing example
uses different dyes. These do not establish matched closed same-solute
pair/network trajectories. A workbook inventory attempt failed DNS; it was
not retried after the design mismatch was established.

Fica's [Texas raw-data identifier](https://doi.org/10.18738/T8/BPHF34) is a concrete
availability lead; the repository metadata API returned 403 here.
[Zenodo 20414671](https://zenodo.org/api/records/20414671) identifies a
24,045,464-byte simulation-code ZIP, not a replacement for experimental data.
No ZIP was downloaded. Folding by osmotic water exchange requires evolving
volumes, chemical potentials and mechanical constraints to be specified before
an independent prediction. A [packing archive](https://doi.org/10.5061/dryad.k0p2ngf4z)
offers images and segmented networks, but no relaxation series was identified.
The [Haylock bilayer study](https://doi.org/10.1038/s42004-020-0322-1) measures
driven channel current; it does not supply conserved compartment stocks.

## What the search changes in the design

Apparent adjacency and successful pair fits do not suffice: connecting rods,
membranes or fluid channels may themselves hold resource. Related thermal work
already shows limits of reducing extended fields to simple site couplings
([Liu et al., 2026](https://doi.org/10.1103/jprj-749c)). Our separate
[analytic storage counterexample](topology-storage-2026-10-23.md) gives identical
pair observations and conserved chamber totals but different network rates.
It adds a concrete pre-target check: independently bound connector capacity,
or excite the pair's common mode to estimate it before forecasting the network.
This is a qualification refinement, not a newly observed violation of the law.

Prioritize the still-closest matched droplet design if raw stocks/geometry become
publicly reachable. Otherwise require an archive with independent component
characterization, matched passive links, known initial states and resolved
network transients. Do not fit the target generator, relabel a driven transport
example as closed exchange, or spend another round reopening these same
ineligible leads without new information.

## Exposure and reproducibility

Eleven unchanged public metadata/methods files and their SHA-256 receipts are
retained in `data/physics-candidates/2026-10-23/topology/`. Replay the offline
audit with `python experiments/audit_topology_sources.py`. Published prose,
abstracts, methods, captions and numerical summaries were exposed. No response
workbook, notebook output, image pixels, movie, or raw experimental trajectory
was decoded; no calibration or target fit was run. Complete article files can
contain outcomes, so possession of these files is not a claim of global blindness.
The DataCite droplet-network query returned 34 metadata records. Searches also
covered RC redistribution, passive thermal lattices, exact droplet titles and
public repository identifiers. Article PDFs and the 44-study registry remain
unchanged by this source audit itself.
