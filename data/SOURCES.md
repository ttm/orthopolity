# Source data

1. NOAA NCEI, *L2 XRS flare report*, science-quality composite, annual files for
   2022, 2023 and 2024, version 1.0.1. [Source directory](https://data.ngdc.noaa.gov/platforms/solar-space-observing-satellites/goes/multi/l2/data/xrsf-l2-flrpt_science/csv/).
   Metadata and original fields are preserved. NOAA's metadata states that
   these data may be redistributed and used without restriction. Irradiance
   is W/m², integrated irradiance is J/m². End fluence has missing values.
2. USGS, *FDSN Event Web Service / ComCat*, worldwide earthquakes from
   2010-01-01 through 2024-12-31, minimum reported magnitude 5.5.
   [API documentation](https://earthquake.usgs.gov/fdsnws/event/1/).
   The query URL is in `experiments/fetch_data.py`. Moment magnitudes are
   filtered during analysis, not in the raw download. The energy proxy is an
   analysis transformation, not a USGS observed field.
3. Hatton, Heneghan, Bar-On and Galbraith (2021), *The global ocean size spectrum
   from bacteria to whales*, Science Advances 7, eabh3732.
   [Article](https://doi.org/10.1126/sciadv.abh3732),
   [associated archive](https://doi.org/10.5281/zenodo.5520055),
   [authors' repository](https://github.com/ryanheneghan/sheldon_revisited).
   The included 253-row table is the authors' output for reconstructed upper-200-m
   biomass by group and mass bin. It is not individual-organism raw data.
   Attribution and original third-party rights are retained; no new license
   to third-party materials is granted by this package.

4. Hatton et al. (2021), full-water-column companion table
   (`summary_biomass_table_long.csv`) and per-group uncertainty factors
   (`group_standard_errors.csv`), from the same repository and commit as (3).
   Note: the column named `log10_Standard_Error` does **not** contain a log10
   standard error. It is a multiplicative factor f, with the published 95%
   interval being exactly [estimate/f, estimate*f]; verified for all 253 rows.
5. Ersoy, Z., et al. (2025), *GLOSSAQUA: A global dataset of size spectra across
   aquatic ecosystems*, Ecology 106, e70050.
   [Repository](https://github.com/zeynepersoy/GLOSSAQUA_dataset), MIT licence,
   Copyright (c) 2023 Zeynep Ersoy. Files `GLOSSAQUA_Size.txt`,
   `GLOSSAQUA_Sample.txt`, `GLOSSAQUA_DataSource.txt`. These are R
   `write.table` output: space-separated, quoted, UTF-8. (The data dictionary in
   the same repository is UTF-16; the data files are not.) `GLOSSAQUA_Size.txt`
   holds published size-spectrum *fit parameters* per sample, not individual
   organism measurements. Pinned to HEAD, as upstream publishes no tags.

All source files are preserved byte-for-byte and hashed. New views, estimates,
figures and audio are analysis outputs and are labeled separately.
