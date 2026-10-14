# Broader natural-system source audit — 14 October 2026

Physics and chemistry transfers are complete. This audit follows the author's
requested move to broader natural phenomena. Reachability alone is insufficient:
an archive must separate predictors from the response, support an unused
prediction, and discriminate physically different explanations.

## Selected for design qualification: aeolian sand transport

Martin and Kok (2017), *Wind-invariant saltation heights imply linear scaling
of aeolian saltation flux with shear stress*, Science Advances 3, e1602569,
[doi:10.1126/sciadv.1602569](https://doi.org/10.1126/sciadv.1602569), supplies
separate wind and sand measurements at three field sites. The public
[unbinned archive](https://zenodo.org/records/291798), doi:10.5281/zenodo.291798,
is a **69,336-byte workbook**, CC BY 4.0. The original bytes, publisher record,
full paper XML, acquisition receipts and checksums are retained under
`data/saltation/2026-10-14/`. Publisher MD5 and local SHA-256 are checked offline.
The dataset and methods are reachable; no author contact or private access is
needed. The workbook is retained intact and is not rewritten.

Schema and predictor audit: Notes plus Jericoacoara, RanchoGuadalupe and Oceano
worksheets. All data sheets contain Date, StartTime, EndTime, friction velocity,
stress, direction, stability, saltation height, integrated flux, detection
frequency and associated uncertainties. Notes identifies stress in Pa, height
in m and integrated flux in g/m/s. There are 30, 19 and 299 source intervals,
respectively, on four, two and twenty recorded dates. These include inactive
and incomplete periods; the paper's three, two and twelve active-transport
days therefore describe a different cohort.

Wind comes from sonic-anemometer Reynolds stress. Sand flux uses laser counts
calibrated by sand traps, with exponential fits over height. Integrated flux
and saltation height share that profile fit; they are not independently assayed
responses. Sub-2-cm transport, trap efficiency, spatial sampling and hourly
calibration shared by half-hour intervals limit interpretation. We do not use
heldout height to predict flux from the same fit and call that independent.

The published linear/3/2 comparison, approximate 50% flux variation within
stress bins and qualitative preference for linear scaling are known. Numeric
workbook response arrays have not been inspected. A text-only schema inspection
did reveal NaN locations; subsequent extraction is hard-limited to columns A:I.
The published binned archive (Zenodo 291799) is not an input: its excess-stress
normalization uses a threshold estimated from flux. Source download and local
column withholding do not make this a blind study.

The [frozen qualification](saltation-qualification-protocol-2026-10-14.md)
uses the actual wind support to test selection of two known constitutive laws
in simulated worlds. It is a prerequisite to any new real response fit. Neither
log-orthopolic nor linear-orthopolic size allocation is measured: wind stress
changes an input budget, and transport depends on momentum transfer and grain
trajectories. A positive result would support a bounded transport transfer,
not neutral allocation across coexisting size classes. Its scientific value
must be judged against that limited claim.

## Other reachable leads

- **Catchment water balance:** [CAMELS-GB v1](https://doi.org/10.5285/8344e4f3-d2ea-44f5-8afa-86d2987543a9)
  has daily meteorology and discharge for 671 catchments, 1970–2015, under the
  Open Government Licence; source methods are
  [Coxon et al. (2020)](https://essd.copernicus.org/articles/12/2459/2020/).
  Its Penman–Monteith reference-grass potential evaporation uses meteorology,
  offering a cleaner input than catchment-calibrated evaporation products.
  The metadata page was reached, but the full archive has not been downloaded
  in this audit. A water/energy-limited runoff forecast needs independent
  choices for storage, groundwater exchange, human abstraction and period
  aggregation. Do not use runoff-calibrated aridity as an independent resource.
- **Gravel/sand transition experiments:**
  [Zenodo 6261166](https://zenodo.org/records/6261166) lists small original
  workbooks on washload deposition and grain-size gaps. It may support a
  controlled transport comparison if input size fractions, hydraulics and
  output sampling are independently measured. Metadata reached; no response
  files analyzed or design frozen.
- **Bimodal sediment erosion:**
  [PANGAEA 901393](https://doi.org/10.1594/PANGAEA.901393) accompanies
  [Staudt et al. (2019)](https://doi.org/10.1002/esp.4559), with controlled
  mixtures and flow velocities. Mobility, hiding/exposure and bed opportunity
  measures need qualification before predicting grain-specific incidence.
  This remains a lead, not a completed download or test.

The next useful natural-system comparison should measure grain incidence and
particle velocity or collision cost separately, or otherwise supply independently
specified competing resource costs. Repeating a familiar exponent fit adds
less than forecasting a tradeoff across conditions from those measurements.
