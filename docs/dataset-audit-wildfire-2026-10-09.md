# Wildfire data for a new test, 9 October 2026

The [US Forest Service FPA FOD service](https://apps.fs.usda.gov/arcx/rest/services/EDW/EDW_FireOccurrenceCurrentEdition_01/MapServer)
is accessible. It identifies its current release as Seventh Edition,
FPA_FOD_20260615, covering 1992–2024 and approximately 2.66 million records.
The [data layer](https://apps.fs.usda.gov/arcx/rest/services/EDW/EDW_FireOccurrenceCurrentEdition_01/MapServer/0)
supplies fire size, discovery time, location, cause and source identifiers.
It supports pagination, with a maximum of 2,000 records per request. Freeze
downloaded bytes and cite the edition because the current endpoint can change.

An actual 243,261-byte JSON response containing **1,000 unique records** has
been retained, together with service metadata and a
[`receipt`](../data/dataset-audit/2026-10-09/wildfire/receipt.json). The query
selects `fire_year = 2020`, ordered by `fod_id ASC`. It deliberately stops at
1,000 records and reports `exceededTransferLimit=true`. This is an access and
schema check, **not** a complete year or a representative analysis sample.
All sampled records have size, discovery date and location; 108 lack containment
dates. No distributions or hypothesis outcomes were calculated.

## Proposed scientific use — not registered or run

A conditional area-resource hypothesis gives

\[
A\frac{dN}{d\ln A}=C
\quad\Longrightarrow\quad
\frac{dN}{dA}\propto A^{-2}.
\]

This supplies a candidate density exponent of 2 for burned area, once the
population, observation period and log-area comparison are defined. Its physical
allocation premise needs justification: recurrent fires are not simultaneous,
disjoint territorial holdings, and burned area does not directly measure energy
or consumed fuel. A fitted exponent alone cannot identify the resource.

A useful new protocol would choose complete regional/year extracts, fix a
reporting/completeness rule, calibrate on earlier years and evaluate withheld
years. Verify the edition's `fire_size` units against its attribute documentation
before setting numerical thresholds. Compare the fixed area-resource model with fitted power-law, truncated
power-law and lognormal alternatives, preserving a goodness-of-fit gate and
regional/year dependence. Fire suppression, weather, changing reporting and
finite burnable area are substantive constraints. A second prediction could
test transfer of normalized area allocation across years; direct area–length
geometry requires linked perimeters, since this source supplies points.

Choose the cohorts and thresholds before fitting, and record that the 1,000-row
sample has already been opened. This document proposes a design, not a completed
registration or evidence for the area hypothesis.

## WUMI fallback: metadata accessible, files blocked here

[WUMI2 on Dryad](https://datadryad.org/dataset/doi:10.5061/dryad.sf7m0cg72)
advertises a compact 3.61 MB event table with 21,693 western-US fires from
1984–2020. Metadata was acquired, but API file downloads returned HTTP 401 and
public file links returned HTTP 403 in this session. It is therefore not counted
as payload-verified. FPA FOD's successful public API request is the practical
new-domain route established here.
