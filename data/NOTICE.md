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
| `sheldon_summary_biomass_top200_table_long.csv` | Hatton, Heneghan, Bar-On & Galbraith (2021), *Science Advances* 7, eabh3732 — authors' public repository `ryanheneghan/sheldon_revisited` at commit `d8af6567`, archived at [10.5281/zenodo.5520055](https://doi.org/10.5281/zenodo.5520055) | ⚠️ **Verify before publication.** A 9 KB derived summary table from an open-access article, redistributed with attribution. The specific licence on the authors' archive has not been confirmed by this project. |

**On the third row:** if the licence turns out to disallow redistribution, delete that one file.
Nothing breaks — `experiments/fetch_data.py` retrieves it from the authors' repository at the pinned
commit and verifies the checksum, so only offline reproduction of the ocean re-expression is
affected.

No new licence to any third-party material is granted by this repository. Original rights and
attribution are retained by their holders. Code, documentation and analysis outputs authored here
are separate from these inputs.
