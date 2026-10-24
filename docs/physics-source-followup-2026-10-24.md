# Independent physical predictions: fresh source qualification

24 October 2026. This follows the [network source follow-up](network-source-followup-2026-10-23.md)
and completed [BioMe stock diagnostic](biome-stock-audit-results-2026-10-23.md).
A new heat-transfer archive supplies actual temperatures and separate material
assays. **It remains unqualified for a spatial forecast because the available
sensor channels have no verified coordinate crosswalk.** This is a bounded
source audit, not a new empirical result or proof that suitable data do not exist.
The electrical search also found a smaller, independently specified circuit
that supports the [separate boundary-test protocol](rlc-boundary-protocol-2026-10-24.md).

For a thermal field the resource would be stored heat relative to a fixed
reference, with measure `rho * cp * dV`. This is **neither log-orthopolic nor
linear-orthopolic size allocation**. A controlled heater makes this an open
system; boundary flux and electrical input belong in the balance. It would be
a separate continuum prediction, not the closed pair-to-five-node test.

## GEOFIT: useful independent inputs, incomplete observation mapping

[Kling et al. (2022)](https://doi.org/10.3390/pr10050959) describe a heating
helix in sand or soil inside a climate-controlled container. The
[public data record](https://zenodo.org/records/7436705) supplies two HDF5 files
and a material-property workbook. The
[primary methods PDF](https://zenodo.org/records/7436458) is accessible.

| File | Bytes | Publisher MD5 |
| --- | ---: | --- |
| `Experiment_data_M24_Sand.h5` | 240,189,640 | `88507dfc20d8e4f4facc90280121517e` |
| `Experiment_data_M31_Humus.h5` | 311,025,352 | `051449661e9c440cf5857d8d733e69c2` |
| `Experimental_material_properties.xlsx` | 851,330 | `cde0ea9ee9b8d9691cae80fe501b0328` |

The relevant independence is substantive: conductivity and specific heat come
from separate heat-flow-meter and step-heating assays of material samples,
with moisture assessed by drying. The article describes samples before and
after the experiments; it does not establish which assay should be assigned
to each run. Electrical power was monitored separately. Numerical material
cells have not been decoded.

Methods and apparatus drawings specify a one-metre heating helix, 0.35 m in
diameter with 0.1 m pitch, in a rectangular container. Published conditions
include 10 W/m nominal heating and a 10°C climate setting. The original
experiment uses both resistance probes and distributed fibre-optic sensing
(DTS), including a cable near the container wall. These details offer a
possible independent diffusion forecast once input and observation mappings
are fixed.

### What the downloaded file actually contains

The complete Sand HDF5 matches its publisher checksum. Inspection was limited
to object names, shapes, types, attribute names and three string-only column
label datasets. **No numerical index, time, power, initial-temperature or
response values were read.**

There is one pandas table, `M24_10dC_10W`, with **652,664 rows and 45 columns**:

- `X_Value`;
- `T01`–`T24`, `T25_core`, `T26_cc`, `T27_lab`;
- `MA1`–`MA4`, `MB1`–`MB4`, `MC1`–`MC4`;
- `-`, `kWh`, `W`, `Comment`, `Time`.

Forty-four columns share a float64 block; `Time` occupies an int64 block. There
is **no explicit DTS coordinate/temperature object or wall-DTS history** in
this file. The paper's unnumbered apparatus drawings cannot establish the
mapping from `T01`–`T24` to physical positions. Labels such as `T25_core` are
not sufficient to assign exact coordinates. `T26_cc` and `T27_lab` likewise
need documented meanings before use as boundary inputs.

The material workbook has sheets `Material Parameters` and `Tabelle1`.
String-label inspection finds density, heat capacity, conductivity, units,
run identifiers, dates, geometry and source-power descriptors, but no sensor
channel crosswalk. The numerical cells remain unread. The second
[conference-data archive](https://zenodo.org/records/7437077) lists the same
three files under slightly different names with **identical checksums**;
it adds no missing observations or mapping.

### Gate before any target access

A usable design must fix:

1. The channel-to-coordinate crosswalk, heater position and geometry, and the
   meaning and units of the input/time channels.
2. Material assay-to-run matching, including moisture, density and how
   uncertainty and temperature dependence enter the prediction.
3. Initial-field and boundary treatment, including which independently
   selected measurements are inputs and which interior readings are targets.
4. An error bound for any omitted heater/support storage, moisture transport
   or container boundary influence.

An early-time forecast could limit sensitivity to uncertain distant boundaries.
Its time window must follow from independent diffusivity, geometry and a
specified error bound before reading the responses. It cannot repair an
unverified sensor map. Do not select channel positions, boundary corrections
or effective conductivity by matching the temperature curves.

## Bounded search for the missing map

The [project deliverables pages](https://geofit-project.eu/publications-and-results/project-deliverables/)
identify a public **D3.6 Model Environment for Different Types of Novel Ground
Heat Exchangers**. The complete 29-page PDF was retrieved. Its text supplies
model coordinates, but no experimental channel crosswalk was found.

[CORDIS](https://cordis.europa.eu/project/id/792210/results) also lists two
performance reports. Their public download redirects returned **HDS-010
technical errors**. The retained files are explicitly named `.html`; they
are error/redirect receipts, not retrieved report PDFs.

[Dörr's 2020 primary thesis landing page](https://pure.unileoben.ac.at/en/publications/cfd-analysis-of-ground-source-heat-exchangers/)
links a potentially useful full text, but both web and direct retrieval returned
403. Its abstract describes a smaller Thermo-Pipe experiment as well as the
large apparatus. That is a lead, not a verified coordinate source or another
available raw dataset. Kling's 2020 experimental thesis is cited in project
materials; a public full text was not located in this pass.

Stop this source before numerical access. Reopen it when an actual coordinate
crosswalk or equivalent primary documentation becomes available; another
successful curve fit would not resolve this qualification.

## Other new thermal leads

| Source | Availability and design | Remaining qualification |
| --- | --- | --- |
| [Aalborg guarded-hotbox wall](https://zenodo.org/records/8204755), [methods](https://doi.org/10.54337/aau488363266) | Public `dataset.zip`, 2,070,317 bytes; seven steady and four dynamic experiments; calibrated temperature sensors | Designed to study internal convection in porous insulation. Pure conduction, independent material inputs and full observation mapping are not yet qualified. ZIP not downloaded. |
| [Dowling Lab TCLab examples](https://colab.research.google.com/github/dowlinglab/pyomo-doe/blob/main/notebooks/tclab_model.ipynb) | Separate two-heater step and sine CSVs are linked; actual hardware measurements described | Potential separate-forcing transfer. Board identity, independent calibration and environmental/sensor parameters need fixing. [Manufacturer modeling](https://apmonitor.com/pdc/index.php/Main/TCLabHigherOrder) fits several parameters to the temperatures; nominal heat capacity alone does not supply an independent complete model. CSVs not downloaded. |
| [Tomanek and Stutts rod experiments](https://doi.org/10.1016/j.dib.2021.107632) | Raw temperature data and [analysis code](https://zenodo.org/records/5683312) described | Source estimates conductivity and convection/boundary parameters from the same response. A separate-condition transfer would require a new fixed design; no response file decoded. |
| [Heated cable bundles](https://data.mendeley.com/datasets/9y8fjy2vwt/2) | Electrical inputs, surface temperatures and a PSpice thermal model for bundles of different sizes | The effective-conductivity model was developed using these measurements. Independent component calibration and a withheld cohort remain unidentified. |
| [Battery thermal characterization](https://github.com/Battery-Intelligence-Lab/battery-thermal-characterisation) | Real thermal-camera experiments and code | Effective conductivity is obtained by inverse modeling of the temperature response; it is not automatically an independent predictor. |

A [heat-pipe identification dataset](https://huggingface.co/datasets/cetiennec/heat-pipe-model-identification)
explicitly contains simulated trajectories. The
[Grey-brick building collection](https://doi.org/10.5281/zenodo.7180260) supplies
fitted RC models. Neither substitutes for independently characterized physical
network observations. Previously excluded archives were not rerun.

## Retention, exposure and reproducibility

Thirteen unchanged public metadata/methods files are retained in
`data/physics-candidates/2026-10-24/thermal/`, including the complete methods
and model PDFs and the material workbook. `acquisition.json` records URLs,
byte counts and SHA-256 hashes. It distinguishes the two valid PDFs from four
HTML redirect/error receipts. Two derived JSON files retain the Sand schema
and column names. The 240 MB Sand HDF5 stays in ignored `build/`; its download
URL, publisher MD5, independently computed SHA-256 and scratch path are in
the receipt. The Humus HDF5 was not downloaded.

Published prose, methods, design settings, unnumbered apparatus drawings,
qualitative results and some aggregate comparison summaries were exposed.
The paper's reported material contrast and failure to reach a stationary
state were known. Some teaching-data values appeared in an unrelated search
snippet; that source was not selected. No raw GEOFIT numerical material,
input or response arrays were decoded, and no calibration or target fit was
run. Possession of the complete files is not a claim of global blindness.
This thermal source audit changes neither the empirical registry nor the manuscripts.

## Electrical and tracer alternatives

| Source | Available information | Decision |
| --- | --- | --- |
| [Danzer, Plank and Rüther (2024), ELSA](https://doi.org/10.1016/j.xcrp.2024.102091); [data](https://doi.org/10.5281/zenodo.10794584) | Small original JSON and MAT impedance files from a fabricated parallel RLC circuit; nominal L/C tolerances and separate multimeter resistance in supplementary Table S3 | Selected for a component forecast and a boundary of collocated passive RC exchange. It is a driven one-port circuit, not the closed five-node topology intervention. Source resistance units conflict; protocol fixes a primary reading and sensitivity before response access. |
| [Pfeiffer et al. (2022), CapClamp](https://doi.org/10.7554/eLife.75517); [software](https://doi.org/10.5281/zenodo.5553946) | Actual hardware RC validation and neuronal experiments with active feedback implementing apparent capacitance changes | A possible controlled open-system transfer, but the controller deliberately implements the target law, and biological offline capacitance corrections depend on response fits. Not selected for the present independent passive-state test. |
| [Visentini et al., millifluidic tracer mixing](https://doi.org/10.1007/s11242-021-01607-0) | Real stopped-flow diffusion with independent optical standards and known geometry; methods cite Zenodo 4066432 | Both the Zenodo API and DataCite record returned 404 for the cited identifier. No substitute raw archive was located in the bounded pass. No image or numerical tracer response was downloaded. |

The ELSA metadata, complete supplement and both original response files are
retained with hashes in `data/physics-candidates/2026-10-24/rlc/`. All published
Table S3 fit aggregates are known. An initial schema reader printed the first
string-encoded complex observation; that row is excluded from primary scoring
before any other numerical responses are opened. The corrected inventory
emits no string content. The protocol records this exposure, the distinction
between conditional component envelopes and measurement uncertainty, and the
forecast-sealing sequence. A successful electrical comparison would qualify
a restricted mechanism and its extension, not establish a new general law
from one circuit.
