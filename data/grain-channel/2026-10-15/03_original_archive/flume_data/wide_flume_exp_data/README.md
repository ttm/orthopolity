# wide_flume_exp_data — new 5 cm flume experiments (this study)

Bed load sediment transport experiments conducted for *"Generalizing sediment transport experiments from narrow flumes to wider channels"* (Deal et al.) in a 5 cm wide flume at the River Dynamics Laboratory, Simon Fraser University. The name "wide flume" is relative to the narrower flume used in Deal et al. (2023, Nature; see `../Deal_2023_grain_params/`). **This folder is the primary public release of this data.**

Two granular materials were used, identified throughout by the codes `gb` (spherical glass beads) and `ng` (natural gravel). Run IDs follow `gb_5_01` = material, flume width (5 cm), run number.

## Contents and provenance

```
flume_experiment_data/          <- the transport experiments
├── IMG_6750.jpeg               <- photo of the experimental setup
├── gb_exps/  (and ng_exps/, same layout)
│   ├── gb_exp_data.ipynb       <- raw per-run measurements (entered in-notebook) + processing
│   ├── feeder_calib.tsv        <- sediment feeder calibration measurements
│   ├── gb_feeder_calib.ipynb   <- processes feeder calibration -> gb_feeder_calib.csv
│   ├── gb_feeder_calib.csv     <- feeder rate calibration used in gb_exp_data.ipynb
│   ├── gb_5_data.csv           <- OUTPUT: run summary table (read by the paper's analysis pipeline)
│   └── velocity_data/               <- LDV velocity profiles + transport videos; SEE CAVEATS BELOW
│       ├── gb_5_01.mp4 ...          <- GoPro video of steady-state transport, one per run, named
│       │                               by run ID (gb_5_01–gb_5_04, ng_5_01/02/04/05)
│       └── Narrow_Flume_Gb_5_01/ ... (one folder per run)
│           ├── *.csv                <- velocity time series, one file per traverse position
│           │                           (per-channel time + velocity, units in header; the
│           │                           "Y Axis Position" column records the traverse coordinate);
│           │                           *_Coincident.csv = coincidence-paired samples (for
│           │                           Reynolds stress estimation)
│           ├── *.set                <- instrument settings (plain text, laser-Doppler calibration)
│           └── *.PNG                <- screenshot of acquisition software settings
└── material_props/             <- properties of the two granular materials
    ├── 1_var_density.csv        <- grain density            ┐
    ├── 2_var_shape.csv          <- grain axes A/B/C, CSF    │ analysis-ready property tables
    ├── 3_var_ARS.csv            <- angle of repose          │ (read by the paper's pipeline;
    ├── 4_var_settling_velocities.csv  <- measured settling  │  also copied to 02_data/source_data
    ├── 5_var_VES_settling_velocity.csv <- VES sphere settling┘  with the _WF suffix)
    ├── 3_calc_ARS_ng.ipynb      <- computes 3_var_ARS.csv from AoR photos
    ├── 4_calc_settling_velocities.py / .ipynb <- computes 4_var from settling videos
    └── observations/            <- raw observations behind the property tables
        ├── 4_data_settling_velocities/  (settling videos, tracked gravel_centroids.csv,
        │                                 terminal_settling_tracks_ng.pdf)
        └── 5_data_friction_angle/AoR_ng/  (angle-of-repose photos + AoR.py analysis script)
```

## Processing chain (raw → published)

1. Raw run measurements (slopes, depths, sediment masses, feeder settings) are recorded in `gb_exp_data.ipynb` / `ng_exp_data.ipynb`, combined with the feeder calibration, and written to `gb_5_data.csv` / `ng_5_data.csv`.
2. Raw material observations (videos, photos) in `material_props/observations/` are processed by the numbered `*_calc_*` scripts into the numbered `*_var_*.csv` property tables. The natural gravel (ng) properties were re-measured for this study; all calculations use the same methods/scripts as in `../Deal_2023_grain_params/1_grain_properties/` (which is why calc scripts 1, 2, and 5 are not duplicated in this folder).
3. `gb_5_data.csv`, `ng_5_data.csv`, and the five `*_var_*.csv` tables are the inputs read by the paper's analysis pipeline (`../../data_analysis_for_paper.ipynb`), which merges them into the published dataset `02_data/deal_dataset_S3.csv`.

## Units and conventions

- `water_slope` / `bed_slope` in the run summary CSVs are in **degrees**; the merged datasets use gradients (m/m).
- Column names prefixed with `d` are 1-sigma uncertainties.
- Velocity file suffixes `X0, X1, ...` are position labels from the acquisition sequence; the physical traverse coordinate of each file is recorded in its "Y Axis Position" column (millimeters, instrument traverse datum — not referenced to the bed).
- Full column definitions: see `02_data/source_data/data_dictionary_source_data.csv` at the repository top level.

## Velocity data: scope and caveats — unvetted, use at your own risk

The velocity measurements were made with a laser Doppler velocimeter. Profiles were taken at mid-width (the channel centerline), with the instrument traversed vertically; each file is one traverse position. Channel 1 is the streamwise component; channel 2 is the cross-stream component.

Be aware:

1. These measurements were **not used in the associated article** (and not for any identified problem with them — they simply were not analyzed) and have therefore **not been vetted by the authors**. They are provided as-is, in the interest of completeness.
2. The instrument traversed vertically while the flume — and even more so the transport surface — was sloped, so the traverse axis is not bed-normal. The bed and water surface slopes are given in the run summary tables (`gb_5_data.csv` / `ng_5_data.csv`), so the geometry can be reconstructed.

The CSV exports contain the complete usable data.

## Transport videos

Each `velocity_data/` folder also contains a short GoPro video of bed load transport at steady state for that run (`<run>.mp4`, e.g. `gb_5_01.mp4`), filmed through the sidewall of the 5 cm "wide" channel. Videos are provided for runs `gb_5_01`–`gb_5_04` and `ng_5_01`, `ng_5_02`, `ng_5_04`, `ng_5_05`. They are illustrative only (re-encoded to HEVC/H.265 to reduce size) and were not used in any quantitative analysis.

## Known issues

The velocity profile files for position X0 of runs Ng_5_01 and Ng_5_02 were lost (empty files, removed from the dataset). All other positions for those runs are unaffected.

The per-run processed LDV profile summaries (`<run>_LDA_data_processed.csv`, written by the last cell of `gb_exps/gb_exp_data.ipynb` and `ng_exps/ng_exp_data.ipynb`) were empty — header only, because the LDV profiles were never processed end-to-end — and have been removed from the dataset. Re-running those notebook cells would regenerate them.
