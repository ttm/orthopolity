# Available data for the next storage intervention

25 October 2026. **Two additional public archives are now downloaded and
checksum-verified.** They support physical response studies but do not supply
the closed capacity-versus-coupling experiment specified in the
[new design](storage-intervention-design-2026-10-25.md). No numerical experimental
values were converted or reported, and no empirical verdict was added.

This is a bounded source qualification. Availability, a known physical model
and eligibility for this particular prediction are separate questions.
Physical storage weights would be required; neither log-orthopolic nor
linear-orthopolic size allocation is tested by these archives.

## A 144-node electrical network with component changes

[Wang, Price, Zhang and Chong (2020)](https://doi.org/10.1038/s41467-020-15940-3)
describe an actual circuit implementation of a four-dimensional topological
insulator. Its [DR-NTU dataset](https://doi.org/10.21979/N9/KXL3TD), version 2,
is accessible through the public Dataverse API even though the browser landing
page returned a bot challenge.

- Original `data_codes.tar.xz`: **439,088 bytes**, publisher MD5
  `bbb17f2a2bb8a65ec2270ca999227e69`, matched after download.
- The graph has 144 sites. Grounding components are changed through the model
  parameter m; this parameter is not a mechanical mass. Nominal elementary
  components, their combinations and graph-generating source code are given.
- The archive contains **366 experimental NPY arrays**: 324 complex spectra
  of shape (81,), 40 spatial groups of shape (36,), and two combined spatial
  profiles of shape (144,). These are header counts, not numerical observations
  used in a calculation.
- Different byte sizes initially suggested shorter spectra. Header inspection
  resolves that concern: every spectrum has 81 entries. Different header
  lengths account for the apparent discrepancy. File size is not row count.

The acquisition code sweeps 77–160 kHz and drops the first three points,
consistent with the plotting code's 81 frequencies at 80–160 kHz. It converts
two measured amplitudes and their phase difference to complex impedance using
a nominal 1,000-ohm reference resistor. Only processed impedances are retained
in `data_exp`; the original amplitude/phase arrays named in the acquisition
script are absent from this archive. Code was read, not executed.

The methods describe component tolerances of 10% and resistance values based
on manufacturer models/data sheets, rather than independent measurements of
every assembled component. Interconnect resistance is explicitly unmodeled.
The simulation's coupling resistance scaling also deserves clarification:
its base inductance is 2 mH and `linkR=24.00001` is scaled relative to that
base, whereas the article describes 24 ohms per 1 mH inductor. Grounding
uses a different 48-ohm base. Do not silently select one implementation after
inspecting targets. A nominal model could still be tested under a fixed,
explicit component interpretation; its envelope would not become a measured
instrument-error distribution.

**Decision:** retain as an available driven-network intervention, with useful
topology and nominal components. It does not supply closed endpoint stocks,
independently assayed storage curves or experiment-specific uncertainty for
the prioritized allocation intervention. A separate nominal circuit protocol
would need to resolve observation conventions and component mapping first.
Published spatial-response and transition findings are already known; this
would be a retrospective comparison with locally withheld arrays.

## Full-scale wall: complete sensor map and separate calibration description

[Veit and Johra's public data](https://doi.org/10.5281/zenodo.8204755) provide
seven steady and four dynamic wall experiments. The original `dataset.zip`
has **2,070,317 bytes**, publisher MD5
`2542d5c27fbb494bd834025c7f28e839`, matched after download.
Unlike the previously audited GEOFIT archive, this source has an explicit
channel-to-position map in [Technical Report 317](https://doi.org/10.54337/aau544775163).
[Technical Report 304](https://doi.org/10.54337/aau488363266) documents
construction, materials, sensors, calibration and operating conditions.

Header and row-width inspection finds:

| Cases | Tables | Rows per table | Columns |
| --- | ---: | ---: | ---: |
| Steady state | 7 | 181 | Time plus 135 sensors |
| Dynamic | 4 | 1,440 | Time plus 45 sensors |

Steady data cover 15 wall positions, each with nine depths a–i. Dynamic data
cover positions 1, 4, 7, 10 and 13. The depth map starts at the hot surface:
−0.100, 0, 0.069, 0.125, 0.182, 0.239, 0.296, 0.374 and 0.474 m.
The interior five sensors are c–g; b and h measure wall surfaces and a/i
the adjacent air. Report 317 states calibrated temperature accuracy ±0.15°C.
That is a source-reported bound, not a newly verified noise covariance or
an assumption that averaging removes systematic error.

Report 304 lists conductivity, density and specific heat for wood-fiber
insulation, construction wood and OSB. These are useful material inputs but
are not an independent storage-curve assay of the exact assembled wall. The
wall has wooden separators, asymmetric plate thicknesses and possible
spatially heterogeneous insulation. A bowed temperature profile alone cannot
uniquely identify advection rather than material/boundary heterogeneity.

Report 317 broadly describes files as the last three hours at 60-second
resolution. The steady row counts agree with inclusive three-hour sampling;
the dynamic tables have 1,440 rows. Their actual time values remain unopened,
so any later dynamic protocol must resolve the time convention rather than
repeat the three-hour statement for every file.

The later [primary article](https://doi.org/10.1016/j.enbuild.2025.116646)
already reports convection and increased heat transfer. Its qualitative
conclusions and aggregate claim of an increase up to 90% are exposed. Its
described simulation introduces a volume force and internal barrier; that
does not automatically provide an independently predicted advective extension.
No temperatures or fitted simulation outputs from the archive were inspected.

**Decision:** useful for a separately specified conduction/boundary diagnostic,
now with an actual sensor map. It changes thermal forcing in an open system;
it is not a fixed-budget storage or coupling intervention. Before a future
prediction, fix the material and boundary model, treatment of spatial
heterogeneity, calibration/position uncertainty and dynamic-time mapping.
Do not label a residual as independently established convection or treat
source-calibrated transport as an unused prediction.

## Eight dummy-circuit controls are an observation intervention

The [Gonzalez, Toledo and Miranda preprint](https://arxiv.org/html/2609.04252v1#S2.SS5)
and [release commit 243b9fb](https://github.com/davidalejandromiranda/electrochemical-cell-nonclassical-correlations/tree/243b9fb718061a01cde87ba877e55783fa09e322)
resolve the wiring of a lead from the previous audit. Eight controls vary
resistors or series-RC loads **between the counter-electrode lead and the
reference tap**, outside the sensed reference-to-working-electrode dummy.
The measured storage object therefore stays the same. Ideal feedback predicts
unchanged impedance, the same prediction as a persistence baseline.

The methods name the PGSTAT204/FRA32M and nominal components, but do not supply
independently measured dummy tolerances or the acquisition settings needed
to apply the manufacturer's conditional accuracy specification. The code's
101/990-ohm semicircle reference has no verified metrological provenance in
the inspected documentation. Its origin is unresolved, not presumed fitted.
This can support an instrument-invariance diagnostic, but is not the requested
change to measured network storage. Its numerical workbooks remain unopened.

## Retention, boundaries and next action

`data/physics-candidates/2026-10-25/storage/` retains four unchanged originals
(two metadata records and two archives), two derived inventories and an
acquisition receipt with URLs, sizes and SHA-256 hashes. The two wall-methods
PDFs remain in ignored `build/`: their repository notices restrict further
redistribution, so only their URLs and hashes are committed. Original data
licenses are preserved separately in `data/NOTICE.md`.

`experiments/audit_storage_sources.py` verifies all six retained hashes and
reproduces both inventories. It reads NPY headers without array payloads;
thermal cells are tokenized only to count rows/columns, never numerically
converted or reported. Possession of a source archive is not global blinding.
Published summaries, methods and acquisition/simulation code were exposed.

The next priority is the [closed storage intervention](storage-intervention-design-2026-10-25.md):
independent complete storage curves, known budget, observed endpoint stocks
and a separate coupling control. The accessible wall and circuit archives
remain concrete alternatives for narrower conditional response studies. This
audit does not claim that suitable allocation data do not exist, and it adds
no empirical registry result.
