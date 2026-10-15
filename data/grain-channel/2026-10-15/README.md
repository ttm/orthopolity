# Flume sediment transport experiments and river channel data for testing sidewall corrections in narrow flumes

## General information

**Dataset DOI:** https://doi.org/10.20383/103.01325 (Federated Research Data Repository)

**Dataset authors:**
- Eric Deal (eric_deal@sfu.ca) — Simon Fraser University — ORCID: 0000-0003-0945-9160
- Kyle Kusack — Simon Fraser University — ORCID: 0009-0001-3048-0661
- Jeremy G. Venditti — Simon Fraser University — ORCID: 0000-0002-2876-4251

**Long-term point of contact:** Prof. Jeremy G. Venditti, Simon Fraser University

**Associated article:** Deal, E., Perron, J.T., Kusack, K., Benavides, S.J., Bradley, R., Zhang, Q., Kamrin, K., & Venditti, J.G. — *Generalizing sediment transport experiments from narrow flumes to wider channels* [TODO: add journal + article DOI on acceptance, and ask FRDR curator to add it as a related identifier]

**Related datasets:**
- Deal, E. (2021). Downstream Hydraulic Geometry Data Compilation, HydroShare, http://www.hydroshare.org/resource/0629ffb81fdb40aa9e6be42cc11918ca
- Deal, E. et al. (2023). Grain shape effects in bed load sediment transport, *Nature* 613, 298–302, https://doi.org/10.1038/s41586-022-05564-6 (source of the `Deal_2023_grain_params` experiments)

**License:** Creative Commons Attribution 4.0 (CC-BY 4.0)

**Date of data collection:** 2018–2025. **Location:** River Dynamics Laboratory, Simon Fraser University, Burnaby, BC, Canada (new flume experiments); remaining data compiled from published literature (sources cited in data dictionaries and in the article).

## Dataset description

This dataset contains laboratory flume experiment data and compiled river channel data used to test whether sidewall correction methods for estimating bed shear stress can be generalized to very narrow flumes (width/depth aspect ratios between 0.1 and 1).

It includes:

1. **New bed load sediment transport experiments** conducted in a narrow (5 cm wide) flume at Simon Fraser University using spherical glass beads (gb) and natural gravel (ng), including flow and transport measurements (depth, slope, discharge, sediment flux) and velocity profile measurements.
2. **Granular material property measurements** for the experimental sediments: grain density, grain shape (long/intermediate/short axes, Corey shape factor), angle of repose, and settling velocities, with raw observations (photos, videos) from which these were derived.
3. **Raw experimental data from Deal et al. (2023)**, the grain shape study whose experiments are re-analyzed with sidewall corrections in the associated article.
4. **Literature compilations of flume experiments**: Gilbert (1914) as compiled by Brownlie (1981); Meyer-Peter & Müller (1948) as compiled by Smart (1983); Song (1994) as compiled by Guo (2015); Williams (1970).
5. **A compilation of river hydraulic geometry data** (width, depth, velocity, slope, discharge, grain size) spanning steep coarse bedrock rivers to large fine-grained alluvial rivers.
6. **Analysis code**: Jupyter notebooks that reproduce every figure and analysis in the associated article, plus standalone "calculator" notebooks and a spreadsheet implementing the sidewall and grain shape corrections discussed in the article so that others can apply them to their own data.

**Methods summary:** Bed load transport experiments were run at constant discharge with sediment recirculation/feed. Flow depth was measured at six consistent stations along the flume using rulers fixed to the flume sidewall; water surface slope was derived from the known flume slope and the change in flow depth along the flume at those stations (the same method as in Deal et al., 2023). Velocity profiles were measured at the channel centerline with a laser Doppler velocimeter; these measurements were not used in the article and carry caveats (see the wide_flume_exp_data README). Settling velocities were measured by video analysis of grains settling in a water column. Angle of repose was measured from imaged grain piles. Full methods are described in the associated article and its supporting information.

## Folder structure

```
data_repository/
├── README.md                  <- this file
├── 01_code/                   <- analysis code (start here to reproduce the paper)
│   ├── analyses_figures_deal_2026.ipynb       <- reproduces all figures/analyses in the article from 02_data
│   ├── calculator_sidewall_correction_python_notebook_deal_2026.ipynb
│   ├── calculator_sidewall_correction_protected_spreadsheet_deal_2026.xlsx
│   ├── calculator_grain_shape_correction_python_notebook_deal_2026.ipynb
│   ├── calculator_grain_shape_deal_2026.xlsx
│   └── requirements.txt
├── 02_data/                   <- analysis-ready datasets (with data dictionaries)
│   ├── deal_dataset_S1.csv    <- new narrow-flume transport experiments (summary)
│   ├── deal_dataset_S2.csv    <- granular material properties (summary)
│   ├── deal_dataset_S3.csv    <- full merged flume compilation used in the analysis (418 experiments)
│   ├── deal_dataset_S4.csv    <- river hydraulic geometry compilation (simplified)
│   ├── data_dictionary_deal_datasets.csv
│   └── source_data/           <- flat, renamed copies of the key source tables in 03_original_archive
│       └── data_dictionary_source_data.csv
└── 03_original_archive/       <- original data and file structure, preserved exactly as generated
    ├── data_analysis_for_paper.ipynb  <- original full analysis pipeline (runs in place, in this folder)
    ├── flume_data/
    │   ├── Brownlie_1981_Gilbert_1914.csv, Smart_1983_MPM_1948.csv,
    │   │   Guo_2015_Song_1994.csv, Williams_1970.csv   <- literature compilations
    │   ├── wide_flume_exp_data/       <- new 5 cm flume experiments (this study); see its README.md
    │   │   ├── flume_experiment_data/{gb,ng}_exps/     <- run summaries, raw velocity profiles,
    │   │   │                                              and a transport video per run
    │   │   └── material_props/                          <- material properties + raw observations
    │   └── Deal_2023_grain_params/    <- raw data from Deal et al. (2023, Nature) — first public
    │       │                             release of this raw data; see its README.md
    │       ├── 1_grain_properties/    <- grain property tables + raw observations (photos, videos)
    │       ├── 2_exp_raw_data/        <- raw experiment data, incl. image-based slope measurements
    │       └── 3_exp_meta_data/       <- per-experiment metadata table (exp_data.txt)
    └── river_data/                    <- hydraulic geometry compilation + per-source cleaned tables
        └── readme.md                  <- detailed documentation of the river compilation
```

### Two ways to use this dataset

- **To reproduce the article:** run `01_code/analyses_figures_deal_2026.ipynb` from inside `01_code/`. It reads only the four `deal_dataset_S*.csv` files in `02_data/` and requires only numpy, pandas, scipy, and matplotlib (see `requirements.txt`). 
- **To reuse the underlying data:** `02_data/source_data/` contains clean, flat copies of the key source tables. `03_original_archive/` preserves the complete original data — including raw observations (videos, photos, velocity profiles) — in the file structure in which it was generated and processed over the course of the project. The original analysis pipeline `data_analysis_for_paper.ipynb` runs unchanged from within `03_original_archive/` and documents exactly how the archive files were processed into the analysis datasets.

## Naming conventions

- **Granular material codes** (used as row indices and in folder names): `gb` = glass beads (spheres), `ng` = natural gravel, `pg` = pea gravel, `mb` = marble chips, `jo` = "Joel's" gravel, `mk` = "Michael's" gravel, `sf` = shell fragments, `dn` = dragon glass, `oc` = faceted ellipsoids, `ls` = rectangular prisms, `gg` = rounded chips, `tg` = tempered glass.
- **Experiment run IDs:** `gb_5_01` = material `gb`, 5 cm flume, run 01. Deal et al. (2023) runs use `gb_s1_e1` = material, series 1, experiment 1.
- **`_WF` suffix** (in `02_data/source_data/`): material properties measured for the wide flume (this study's experiments), as opposed to the Deal et al. (2023) measurements.
- **`d` prefix** on column names: 1-sigma uncertainty of the corresponding column (e.g. `dgrain_mass` is the uncertainty of `grain_mass`).
- **Numbered prefixes** (`1_`, `2_`, ...): processing order within a folder.

## File formats

- `.csv` / `.txt` / `.tsv` — plain-text tables (note `exp_data.txt` and `raw_exp_data.txt` are comma-separated). 
- `.ipynb` — Jupyter/Python 3 notebooks.
- `.xlsx` — Excel spreadsheets (the sidewall calculator is sheet-protected to prevent accidental edits to formulas; the protection passwords are provided directly in the spreadsheets).
- `.set` — plain-text instrument settings from the TSI laser Doppler velocimeter used for velocity measurements. The velocity data itself is provided as plain-text CSV time series (per-channel time + velocity with units in the header, plus `_Coincident.csv` versions for Reynolds stress estimation). **These velocity measurements were not used in the associated article** The processed run summaries are in `gb_5_data.csv` / `ng_5_data.csv`.
- `.mp4` / `.jpg` / `.JPG` / `.HEIC` / `.png` — raw observation videos and photos (settling velocity videos, angle-of-repose images, grain photos), plus per-run GoPro videos of steady-state bed load transport in the wide-channel experiments (`{gb,ng}_exps/velocity_data/<run>.mp4`, re-encoded to HEVC/H.265; illustrative only, not used in the analysis). JPEG copies are provided alongside each HEIC photo for long-term accessibility.

## Known issues

- In `03_original_archive/flume_data/wide_flume_exp_data/flume_experiment_data/ng_exps/velocity_data/`, the velocity profile files for position X0 of runs Ng_5_01 and Ng_5_02 (`Ng_5_01_X 0.dat`, `Ng_5_02_X0.dat`) were lost (the files were empty and could not be recovered) and have been removed from the dataset. The remaining profile positions for these runs are unaffected.

## Data dictionaries

- `02_data/data_dictionary_deal_datasets.csv` — column definitions for `deal_dataset_S1–S4.csv`
- `02_data/source_data/data_dictionary_source_data.csv` — column definitions for all source tables
- `03_original_archive/river_data/readme.md` — detailed documentation of the river hydraulic geometry compilation

## How to cite

Deal, E., Kusack, K., & Venditti, J.G. (2026). Flume sediment transport experiments and river channel data for testing sidewall corrections in narrow flumes. Federated Research Data Repository. https://doi.org/10.20383/103.01325
