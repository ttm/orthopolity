# Third-party data notice

`data/raw/` contains **unmodified third-party source files**, redistributed here so that the
analyses in [`results/`](../results/) reproduce offline. They are inputs, not products of this
project. Full citations are in [`SOURCES.md`](SOURCES.md); byte integrity is fixed by
[`snapshot_checksums.json`](snapshot_checksums.json) and verified by
[`experiments/fetch_data.py`](../experiments/fetch_data.py).

| File(s) | Origin | Redistribution basis |
|---|---|---|
| `noaa_2022.csv`, `noaa_2023.csv`, `noaa_2024.csv`, `noaa_metadata.json` | NOAA NCEI, GOES L2 XRS flare report, v1.0.1 | NOAA metadata states these data may be redistributed and used without restriction. |
| `usgs_2010_2024.csv` | USGS FDSN Event Web Service / ComCat | Work of the U.S. Geological Survey; U.S. federal government material, public domain. |
| `GLOSSAQUA_Size.txt`, `GLOSSAQUA_Sample.txt`, `GLOSSAQUA_DataSource.txt` | Ersoy et al. (2025), *Ecology* 106, e70050 — repository `zeynepersoy/GLOSSAQUA_dataset` | **MIT licence**, Copyright (c) 2023 Zeynep Ersoy. Redistribution permitted; the licence text is preserved upstream and attribution is retained here. |
| `sheldon_summary_biomass_top200_table_long.csv`, `sheldon_summary_biomass_allwater_table_long.csv`, `sheldon_group_standard_errors.csv` | Hatton, Heneghan, Bar-On & Galbraith (2021), *Science Advances* 7, eabh3732 — authors' public repository `ryanheneghan/sheldon_revisited` at commit `d8af6567`, archived at [10.5281/zenodo.5520055](https://doi.org/10.5281/zenodo.5520055) | Included by decision of this repository's author, 2026-09-09. See the note below for what was and was not verified. |

### On the Hatton et al. files

Three small derived summary tables (9.5 KB, 9.5 KB and 295 bytes), redistributed unmodified and with
attribution, from a published open-access article whose authors make them public themselves.
Inclusion is the decision of this repository's author.

What was checked, and what it showed:

- The authors' GitHub repository declares **no licence** — the GitHub API reports none, and there is
  no `LICENSE` file at the pinned commit `d8af6567`.
- **Crossref records no licence** for the article DOI `10.1126/sciadv.abh3732`.
- The **Zenodo archive could not be reached** (HTTP 504) at the time of checking, so any licence
  recorded there remains unverified.

So this is not a case of a licence permitting redistribution; it is a case of no licence being
stated anywhere reachable. That is common for academic data repositories and does not by itself
imply a restriction, but it is recorded here rather than glossed, because a journal or an
institutional review may ask.

If that position ever needs reversing, delete the three files. **Nothing breaks:**
`experiments/fetch_data.py` retrieves them from the authors' repository at the pinned commit and
verifies the checksums, so only *offline* reproduction of the ocean analyses is affected.

No new licence to any third-party material is granted by this repository. Original rights and
attribution are retained by their holders. Code, documentation and analysis outputs authored here
are separate from these inputs.
