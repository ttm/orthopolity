# Deal_2023_grain_params — raw data from Deal et al. (2023, Nature)

Raw and processed experimental data from **Deal, E., Venditti, J.G., Benavides, S.J., Bradley, R., Zhang, Q., Kamrin, K., & Perron, J.T. (2023). Grain shape effects in bed load sediment transport. *Nature* 613, 298–302. https://doi.org/10.1038/s41586-022-05564-6**



Granular material codes used throughout: `gb` = glass beads, `ng` = natural gravel, `pg` = pea gravel, `mb` = marble chips, `jo` = "Joel's" gravel, `mk` = "Michael's" gravel, `sf` = shell fragments, `dn` = dragon glass, `oc` = faceted ellipsoids, `ls` = rectangular prisms, `gg` = rounded chips, `tg` = tempered glass. Experiment IDs follow `gb_s1_e1` = material, series 1, experiment 1.

## Contents and provenance

The three numbered folders reflect the processing order:

```
1_grain_properties/             <- granular material property measurements
├── table_aux.csv               <- auxiliary property table (additional materials: tg, sf, ng2–ng5)
├── main_granular_materials/    <- materials used in the main experiments
│   ├── 1_calc_density.py  -> 1_var_density.csv      (grain density, mass, volume)
│   ├── 2_calc_shape.py    -> 2_var_shape.csv        (axes A/B/C, VES diameter, Corey shape factor)
│   ├── 3_calc_friction_angle.py -> 3_var_ARS.csv    (angle of repose)
│   ├── 4_calc_settling_velocities.py -> 4_var_settling_velocities.csv (measured settling, drag coeff.)
│   ├── 5_calc_VES_settling_velocity.py -> 5_var_VES_settling_velocity.csv (Dietrich-curve VES sphere settling)
│   ├── Grain_size_dists.png
│   └── observations/           <- raw observations each calc script reads
│       ├── 2_data_shape/                (3D grain scan data: Metrics_HR_*.npy + format docx)
│       ├── 4_data_settling_velocities/  (per-material settling measurements + per-grain processing codes)
│       ├── 5_data_friction_angle/       (AoR photo series: series_6, series_6_clean + official AoR csvs)
│       └── 6_circularity/               (circularity.py + grain outline images)
└── extended_methods_granular_materials/ <- additional materials measured in 2022 (extended data)
    ├── 1–5_calc_*_2022.py -> 1–5_var_*_2022.csv     (same pipeline as above, 2022 campaign)
    ├── mu_c_star_2022.py                             (computes mu* and C* for these materials)
    └── observations/  (grain photos, density/volume spreadsheets, 2022 Taylor shape data,
                        AOR photos by material, settling videos by date/material)

2_exp_raw_data/                 <- raw transport experiment data
├── raw_exp_data.py             <- THE official raw dataset: per-run dicts of all measurements
│                                  (bed slope [per mille], water temps, pump frequency, timed
│                                  sediment masses, depths along flume, etc.). Data unchanged
│                                  since collection; refactored into this form 10.2020.
├── raw_exp_data.txt            <- same data as JSON (machine-readable mirror)
├── image_slope_measurements/   <- compressed image data (.dgz) for image-based bed slope measurements
└── image_slope_meas.csv        <- OUTPUT: bed slopes (Sb ± dSb) per experiment from image analysis

3_exp_meta_data/
└── exp_data.txt                <- OUTPUT: merged per-experiment table (CSV format despite .txt)
                                   combining raw experiment data with grain properties. This is
                                   the processed dataset released with the Nature paper, and the
                                   file read by this repository's analysis pipeline.
```

## Processing chain (raw → published)

1. Property observations (`1_grain_properties/*/observations/`) → numbered `*_calc_*.py` scripts → numbered `*_var_*.csv` property tables.
2. Raw experiment logs (`2_exp_raw_data/raw_exp_data.py`) + image-based slope measurements (`image_slope_meas.csv`) + property tables → `3_exp_meta_data/exp_data.txt`.
3. `exp_data.txt` and the `main_granular_materials` property tables are read by `../../data_analysis_for_paper.ipynb` and merged into the published dataset `02_data/deal_dataset_S3.csv`.

## Units and conventions

- `bed_slope` in `raw_exp_data.py` is in **per mille**; masses in grams, depths/distances in cm, temperatures in °C (units are commented inline in the file).
- Property tables and `exp_data.txt` are in SI units; angles in degrees.
- Column names prefixed with `d` are 1-sigma uncertainties.
- Full column definitions: see `02_data/source_data/data_dictionary_source_data.csv` at the repository top level.

