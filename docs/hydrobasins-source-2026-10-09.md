# HydroBASINS source acquisition, 9 October 2026

All nine **standard level-3 v1.c** archives were downloaded from the official
HydroSHEDS host: Africa, Arctic, Asia, Australia, Europe, Greenland, North
America, South America and Siberia. Total: **25,305,725 bytes**, **292 polygon
features**. These are complete files, not samples. The retained
[manifest](../data/hydrobasins/2026-10-09/acquisition.json) records each URL,
SHA256, byte count, ZIP members/CRCs, feature count and DBF schema. HTTP headers
are retained alongside the unchanged archives; ZIP integrity checks pass.

The [publisher](https://www.hydrosheds.org/products/hydrobasins) offers global
watershed boundaries in 12 nested levels. Its
[technical documentation](https://data.hydrosheds.org/file/technical-documentation/HydroBASINS_TechDoc_v1c.pdf)
describes level 3 as manually grouped major drainage regions; these are not
uniformly sized independent experimental units. Boundaries derive from
15-arcsecond data, with coarser source elevation information north of 60°N.
Standard basin polygons extend through lakes and do not themselves define lake
outlines. The CRS is geographic WGS84.

Use `HYBAS_ID` for block identity and source HydroLAKES outlet coordinates for
the spatial join. Inspection before new lake outcomes found 209 GEOS-invalid
basin polygons, chiefly self-touching grid rings. The
[frozen follow-up](lake-metric-followup-protocol-2026-10-09.md) declares the
overlay repair and date-line convention; no lake outline is repaired.

Attribution: **Lehner, B. and Grill, G. (2013), Global river hydrography and
network routing: baseline data and new approaches to study the world's large
river systems, Hydrological Processes 27(15), 2171–2186,
[doi:10.1002/hyp.9740](https://doi.org/10.1002/hyp.9740).** HydroBASINS was
developed on behalf of WWF with partner support. It uses the HydroSHEDS license
agreement linked by the publisher, rather than HydroLAKES' CC BY 4.0 label.
Each original ZIP includes the technical documentation and attribution notice.
Source ZIPs remain local and ignored by git; a fresh checkout restores them
directly from the publisher with `experiments/fetch_hydrobasins.py --restore`.
The repository retains receipts and derived analytical results, not a mirror of
the stand-alone basin product. The applicable
[license agreement](https://data.hydrosheds.org/file/technical-documentation/HydroSHEDS_TechDoc_v1_4.pdf)
is in Appendix A of the current HydroSHEDS technical documentation.
