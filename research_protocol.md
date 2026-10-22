# Research Protocol and Results

## 1. Question

Can district-level soil, weather and Sentinel-2 vegetation features predict Tamil Nadu's rice yield within
verified APY seasonal groups better than simple historical baselines?

**Answer from this study: not reliably.** No combination clearly and consistently beat the baseline under
cross-validation. This is a negative result, reported as such, and it should not be read as evidence that these
modalities are useless. Section 7 explains why the design may be the limiting factor.

## 2. Target and unit of analysis

- Target: `yield_value` from the imported district-year rice-yield data, in Tonnes/Hectare. Tamil Nadu DES's
  Statistical Handbook labels the crop "Paddy (Rice)" and says production is reported "in terms of Rice" for
  2021-22. That supports a rice-equivalent interpretation for that publication, but does not establish the
  definition or conversion used for every year in the imported dataset. See the [official handbook](https://www.des.tn.gov.in/sites/default/files/2024-11/04%20agriculture.pdf), pp. 108-109.
- Unit of analysis: one district × agricultural year × source season. From 2017-18, the source labels Autumn,
  Winter and Summer are crosswalked to DES groups Kar/Kuruvai/Sornavari, Samba/Thaladi/Pishanam, and
  Navarai/Kodai respectively. These mappings match official state area and production totals exactly in
  2020-21 through 2022-23. Historical Kharif remains a separate legacy category. TNAU documents differing local
  sowing calendars, which the current feature windows still do not model. See [DES reports](https://des.tn.gov.in/en/node/18)
  and [TNAU rice seasons](https://agritech.tnau.ac.in/agriculture/agri_seasonandvarieties_rice.html).
- 765 rows, 38 districts, start years 1998–2022. Training aborts if more than one yield unit is present.
- In the uploaded APY file, the 760 positive-yield main-season rows agree with production divided by area to within
  0.0005 tonnes/hectare; five zero-yield rows lack supporting positive production and are now excluded from
  rebuilt training targets pending source verification.

## 3. Features and the seven configurations

| Group | Columns |
|---|---|
| Soil (6) | soil_phh2o, soil_soc, soil_nitrogen, soil_sand, soil_silt, soil_clay (mean of 0-5, 5-15, 15-30 cm; constant per district) |
| Weather (6) | mean T2M, T2M_MAX, T2M_MIN, RH2M, solar radiation; total rainfall; all over 1 Aug – 30 Sep |
| Satellite (2) | NDVI and EVI, fixed 1 Aug – 30 Sep window. Historical v1 results used a 10 km buffer and allowed invalid/unclassified SCL classes through the mask. The v2 extractor now uses matched district polygons where the local geoBoundaries file has an exact name match and excludes invalid/unclassified SCL classes; it still has no paddy-specific mask. Existing database values and results remain v1 until extraction and dataset rebuilding are deliberately run. |

Configurations: soil_only, weather_only, satellite_only, soil_weather, soil_satellite, weather_satellite,
soil_weather_satellite. A row is used by a configuration only if all of that configuration's features are present
(so satellite configurations use far fewer rows). **A one-hot encoding of district is added to every
configuration**, including weather_only and satellite_only.

## 4. Models and preprocessing

- Random Forest: 200 trees, max_depth 5, min_samples_leaf 5, seed 42.
- XGBoost: 200 estimators, max_depth 3, learning_rate 0.05, min_child_weight 5, subsample 0.8,
  colsample_bytree 0.8, seed 42.
- Missing feature values: median imputation, fitted on training rows only.
- Metrics: MAE, RMSE, R². R² is left undefined when fewer than two test rows exist.

## 5. Evaluation design

- **Leakage control.** Rows are never shuffled. Training years always precede test years (a unit test checks this),
  and imputation statistics come from training rows only (also unit-tested).
- **Single chronological split.** The last 20% of available years (rounded) are the test set. For the three
  configurations without satellite data that is 2018–2022 (593 train / 172 test rows). For satellite
  configurations only 2022 is available as a test year (118 train / 37 test rows) — too thin to trust on its own.
- **Expanding-window cross-validation.** For each year after the first three, train on all earlier years and test
  on that year. 22 folds for non-satellite configurations; 4 folds (test years 2019–2022) for satellite
  configurations. Reported both pooled (all fold predictions together) and as the mean of per-fold R².
- **Baseline.** For each test row, the mean yield of that district across the training years (overall training
  mean if the district is unseen). It is scored under the same cross-validation.
- **Tuning.** Current training selects a small fixed candidate set using expanding splits contained entirely within
  the outer training years. The single-split test years are excluded from this selection.
- **Spatial evaluation.** Leave-districts-out code is available and keeps every row from a held-out district out of
  training. This is a separate geographic-transfer estimate, not a future-year forecast. Its scores have not yet
  been run and stored for this database refresh.
- **Error bands.** Trained models can store a 90th percentile of rolling-origin absolute errors from training years.
  It is a descriptive historical error band, not a calibrated prediction interval or coverage guarantee.

## 6. Results

Results below are copied from the console output of `scripts/run_all_experiments.py` (single split) and
`scripts/run_cross_validation.py` (cross-validation). Single-split runs are stored in MySQL; the cross-validation
results are not, so re-run the script to reproduce them.

### 6.1 Single chronological split

| Configuration | Model | Train/Test | Test years | MAE | RMSE | R² | Baseline R² |
|---|---|---|---|---|---|---|---|
| soil_only | RF | 593/172 | 2018-2022 | 0.555 | 0.765 | 0.330 | 0.334 |
| soil_only | XGB | 593/172 | 2018-2022 | 0.558 | 0.774 | 0.314 | 0.334 |
| weather_only | RF | 593/172 | 2018-2022 | 0.518 | 0.769 | 0.323 | 0.334 |
| weather_only | XGB | 593/172 | 2018-2022 | 0.527 | 0.781 | 0.302 | 0.334 |
| soil_weather | RF | 593/172 | 2018-2022 | 0.529 | 0.758 | 0.343 | 0.334 |
| soil_weather | XGB | 593/172 | 2018-2022 | 0.537 | 0.801 | 0.266 | 0.334 |
| satellite_only | RF | 118/37 | 2022 | 0.592 | 0.794 | -0.162 | 0.223 |
| satellite_only | XGB | 118/37 | 2022 | 0.626 | 0.809 | -0.204 | 0.223 |
| soil_satellite | RF | 118/37 | 2022 | 0.430 | 0.582 | 0.376 | 0.223 |
| soil_satellite | XGB | 118/37 | 2022 | 0.543 | 0.764 | -0.074 | 0.223 |
| weather_satellite | RF | 118/37 | 2022 | 0.493 | 0.628 | 0.273 | 0.223 |
| weather_satellite | XGB | 118/37 | 2022 | 0.551 | 0.760 | -0.065 | 0.223 |
| soil_weather_satellite | RF | 118/37 | 2022 | 0.456 | 0.580 | 0.380 | 0.223 |
| soil_weather_satellite | XGB | 118/37 | 2022 | 0.556 | 0.747 | -0.029 | 0.223 |

### 6.2 Expanding-window cross-validation

| Configuration | Model | Folds | Pooled MAE | Pooled R² | Mean fold R² | Std of fold R² | Baseline mean fold R² |
|---|---|---|---|---|---|---|---|
| soil_only | RF | 22 | 0.673 | 0.343 | 0.033 | 1.095 | -0.020 |
| soil_only | XGB | 22 | 0.677 | 0.334 | 0.010 | 1.125 | -0.020 |
| weather_only | RF | 22 | 0.725 | 0.248 | -0.138 | 1.165 | -0.020 |
| weather_only | XGB | 22 | 0.716 | 0.269 | -0.106 | 1.150 | -0.020 |
| soil_weather | RF | 22 | 0.684 | 0.318 | -0.023 | 1.167 | -0.020 |
| soil_weather | XGB | 22 | 0.694 | 0.296 | -0.074 | 1.234 | -0.020 |
| satellite_only | RF | 4 | 0.769 | -0.491 | -0.614 | 0.314 | -0.053 |
| satellite_only | XGB | 4 | 0.754 | -0.454 | -0.570 | 0.360 | -0.053 |
| soil_satellite | RF | 4 | 0.632 | -0.043 | -0.098 | 0.400 | -0.053 |
| soil_satellite | XGB | 4 | 0.655 | -0.082 | -0.180 | 0.108 | -0.053 |
| weather_satellite | RF | 4 | 0.644 | -0.077 | -0.159 | 0.409 | -0.053 |
| weather_satellite | XGB | 4 | 0.707 | -0.236 | -0.381 | 0.511 | -0.053 |
| soil_weather_satellite | RF | 4 | 0.610 | 0.029 | -0.046 | 0.334 | -0.053 |
| soil_weather_satellite | XGB | 4 | 0.648 | -0.008 | -0.135 | 0.358 | -0.053 |

Per-fold results for the satellite configurations (test years 2019–2022) vary widely. For example
soil_weather_satellite RF scored R² of -0.098, -0.544, 0.077 and 0.380 in 2019, 2020, 2021 and 2022.

## 7. Interpretation — what can and cannot be concluded

Supported by the numbers:

1. Mean fold R² is at most 0.033 for all 14 combinations and negative for 12. Only soil_only (RF and XGB) and
   soil_weather_satellite (RF) exceed the baseline's mean fold R², and the last by 0.007, which is far inside the
   fold-to-fold noise.
2. The single-split result for soil_weather_satellite RF (R² 0.380, 2022 only) is not robust. The same model
   averages -0.046 across its four cross-validation years. A single test year is not a reliable estimate.
3. Fold R² varies enormously (standard deviation above 1.0 for the 22-fold configurations), so differences of a
   few hundredths between configurations are not meaningful and no ranking among them should be claimed.
4. XGBoost never outperformed Random Forest on mean fold R².

Not supported, and not claimed:

- **That soil explains yield.** Soil features are constant within a district, so they cannot explain year-to-year
  change, and every configuration already includes district identity. soil_only's small edge is better read as a
  proxy for district-level differences.
- **That weather or satellite data are uninformative in general.** They are uninformative *as aggregated here*.
  Hypotheses that were not tested: the fixed Aug–Sep window misses the real growing period; one mean/sum hides
  timing and extremes; satellite values are not paddy-specific; satellite sample sizes are tiny.
- **Pooled R² beating the baseline.** The baseline's pooled R² is computed by the code but was not printed, so
  the pooled column in 6.2 has nothing to be compared against.
- Any forecasting ability, any prediction intervals, or any causal reading of SHAP values. SHAP output in the app
  describes what each fitted model relies on.

## 8. Limitations and disclosed weaknesses

1. Historical settings were adjusted after looking at 2018–2022 results, so the old score tables are not an
   untouched final evaluation. Current training code now selects from a small candidate set using expanding
   validation splits inside the training years. An independent final assessment still needs newer yield years.
2. Fixed 1 Aug – 30 Sep window; no verified crop calendar; therefore no valid pre-harvest forecast (the
   aggregates run to 30 September, inside the growing season).
3. Weather and soil still sample district centroids (soil for three districts uses documented offset points).
   Satellite v2 uses district polygons where available, but does not yet use paddy-area weighting or a
   rice-specific mask. Historical v1 scores used the 10 km buffer and older SCL mask; do not attribute those
   scores to v2 extraction.
4. The historical v1 snapshot had satellite coverage of 156 of 765 rows (20.4%). The refreshed v2 snapshot
   (Section 12) has 172 of 765 rows (22.5%), still a smaller and more recent population than non-satellite
   configurations. Satellite-inclusive scores are not directly comparable with the rest.
5. Season labels and rice basis remain only partly verified. The official handbook documents paddy production in
   terms of rice for 2021-22, while TNAU shows multiple local rice seasons; neither source verifies how each APY
   record maps to a particular local season.
6. Small data: 765 rows, 38 districts, 25 years; six newer districts have only a few years.
7. The historical results below compare against district mean only. The current code also scores last-year yield,
   recent-three-year mean, and district trend baselines, so those historical results do not represent the latest
   baseline comparison.
8. Spatial validation has now been run for supported configurations (see Section 12), but its output was printed
   only to the command session and is not stored as a database batch. Current models can show an empirical
   rolling-origin error band; it is descriptive and not a coverage guarantee under temporal or spatial shift.
9. The app's model list and evaluation report retain older development runs as well as the latest retrained runs;
   consult the current database records rather than assuming the earlier run IDs are newest.
10. Reproducibility depends on provider APIs returning the same data later; caches are not in the repository.

## 9. Suggested next steps (ordered by expected value)

1. The uploaded APY CSV passes unit consistency, duplicate-key, and yield=production/area arithmetic checks.
   Its 2017-18 onward season mapping has now been checked against official DES state area and production totals
   for three overlapping years. Kharif through 2016-17 remains unmapped. DES reports describe production in
   terms of rice for the new holdout years; original CSV source URL and full historical basis metadata are still
   missing.
2. Earth Engine authentication, pilot extraction, full v2 refresh, and unified dataset rebuild are complete. The
   remaining satellite work is to improve crop-calendar alignment and obtain a licensed rice-area mask.
3. Replace the fixed window with crop-calendar-aligned, multi-date weather and satellite features; add a licensed
   rice-area mask and paddy-area-weighted aggregation when suitable data are available.
4. Review the refreshed temporal CV batch and preserve spatial results in a durable artifact; obtain newer
   independent yield years for a final temporal holdout. Four history-based baselines and nested time-based tuning
   are implemented; Sections 6–7 and the prior Section 11 snapshot predate the v2 refresh and target cleanup.

## 10. Reproducibility

Seed 42 everywhere. Versions are pinned loosely in `requirements.txt`; no lock file or root README is currently
present. Synthetic data appears only in unit tests and never in any result above.

## 11. Previous evaluation snapshot (2026-10-18; superseded by Section 12)

After five unsupported zero-yield targets were excluded from the unified training targets, all 14 production
model/algorithm runs and all 26 cross-validation combinations were regenerated. The historical score tables in
Sections 6–7 remain an earlier snapshot. The primary-config summary below selects the algorithm with the highest
mean fold R² for each configuration; "wins" compares its fold R² with the strongest history baseline on those same
folds.

| Production configuration | Folds | Selected algorithm | Mean fold R² | Median fold R² | Strongest baseline median R² | Folds won |
|---|---:|---|---:|---:|---:|---:|
| soil_only | 22 | XGBoost | 0.082 | 0.324 | 0.334 (district mean) | 14/22 |
| weather_only | 22 | XGBoost | -0.058 | 0.267 | 0.334 (district mean) | 6/22 |
| satellite_only | 4 | XGBoost | -1.049 | -0.718 | -0.333 (recent mean 3) | 0/4 |
| soil_weather | 22 | Random Forest | 0.010 | 0.316 | 0.334 (district mean) | 7/22 |
| soil_satellite | 4 | Random Forest | -0.438 | -0.227 | -0.333 (recent mean 3) | 2/4 |
| weather_satellite | 4 | Random Forest | -0.266 | 0.025 | -0.333 (recent mean 3) | 2/4 |
| soil_weather_satellite | 4 | Random Forest | -0.122 | 0.124 | -0.333 (recent mean 3) | 2/4 |

This was the pre-v2 satellite and earlier target-cleanup snapshot. Its satellite scores and dataset coverage are
historical and are superseded by Section 12. The research-only weather-rich/history scores remain retrospective,
not pre-harvest forecasts. Do not treat this table as the latest evaluation.

## 12. Current v2 refresh and validation handoff (2026-10-19)

The current database uses satellite DatasetVersion id 5, `Sentinel-2-NDVI-EVI-peak-monsoon-v2`. Earth Engine
authentication and the one-district pilot succeeded. The full 2016–2022 extraction inserted 377 satellite rows;
73 district-years had no cloud-free imagery. The rebuilt unified table has 765 rows, of which 172 (22.5%) have
satellite features. The builder selects one global satellite release, so it does not mix v1 and v2 values by
district-year.

All 14 production model/algorithm holdout runs were retrained. These one-split scores are descriptive and do not
select a production model. For non-satellite configurations, train/test sizes are 591/169 and test years are
2018–2022. For satellite configurations, sizes are 126/37 and all test observations are from 2022.

| Configuration | Algorithm | Test MAE | Test RMSE | Test R² | Baseline R² | Test N |
|---|---|---:|---:|---:|---:|---:|
| soil_only | Random Forest | 0.486 | 0.594 | 0.460 | 0.451 | 169 |
| soil_only | XGBoost | 0.491 | 0.602 | 0.446 | 0.451 | 169 |
| weather_only | Random Forest | 0.462 | 0.612 | 0.427 | 0.451 | 169 |
| weather_only | XGBoost | 0.458 | 0.595 | 0.458 | 0.451 | 169 |
| satellite_only | Random Forest | 0.541 | 0.761 | -0.065 | 0.377 | 37 |
| satellite_only | XGBoost | 0.508 | 0.666 | 0.183 | 0.377 | 37 |
| soil_weather | Random Forest | 0.469 | 0.597 | 0.455 | 0.451 | 169 |
| soil_weather | XGBoost | 0.461 | 0.598 | 0.453 | 0.451 | 169 |
| soil_satellite | Random Forest | 0.420 | 0.560 | 0.423 | 0.377 | 37 |
| soil_satellite | XGBoost | 0.418 | 0.544 | 0.455 | 0.377 | 37 |
| weather_satellite | Random Forest | 0.452 | 0.575 | 0.391 | 0.377 | 37 |
| weather_satellite | XGBoost | 0.418 | 0.546 | 0.450 | 0.377 | 37 |
| soil_weather_satellite | Random Forest | 0.431 | 0.553 | 0.437 | 0.377 | 37 |
| soil_weather_satellite | XGBoost | 0.402 | 0.508 | 0.525 | 0.377 | 37 |

The refreshed expanding-window temporal validation completed and stored all 26 results for 13 configurations × 2
algorithms in batch `20261018T191913` (compact timestamp `20261018191913`). I read those existing rows from the
database on 2026-10-19; no validation was rerun. The best baseline column selects, per configuration, the
baseline with the highest median fold R². “Wins” compares each model's fold R² against that same baseline in
matching years. Satellite configurations have only four folds (2019–2022); the others have 22 folds (2001–2022).

| Configuration | Algorithm | Folds | Pooled MAE | Pooled R² | Mean fold R² | Median fold R² | Best baseline (median R²) | Wins |
|---|---|---:|---:|---:|---:|---:|---|---:|
| history_only | Random Forest | 22 | 0.639 | 0.335 | 0.108 | 0.295 | district mean (0.334) | 10/22 |
| history_only | XGBoost | 22 | 0.626 | 0.365 | 0.118 | 0.328 | district mean (0.334) | 12/22 |
| satellite_only | Random Forest | 4 | 0.664 | -0.536 | -0.986 | -0.604 | last year (-0.393) | 1/4 |
| satellite_only | XGBoost | 4 | 0.682 | -0.660 | -1.275 | -0.749 | last year (-0.393) | 0/4 |
| soil_only | Random Forest | 22 | 0.643 | 0.376 | 0.073 | 0.340 | district mean (0.334) | 10/22 |
| soil_only | XGBoost | 22 | 0.641 | 0.382 | 0.082 | 0.324 | district mean (0.334) | 14/22 |
| soil_satellite | Random Forest | 4 | 0.552 | -0.075 | -0.465 | -0.078 | last year (-0.393) | 1/4 |
| soil_satellite | XGBoost | 4 | 0.577 | -0.164 | -0.491 | -0.494 | last year (-0.393) | 1/4 |
| soil_weather | Random Forest | 22 | 0.658 | 0.339 | 0.010 | 0.316 | district mean (0.334) | 7/22 |
| soil_weather | XGBoost | 22 | 0.655 | 0.340 | -0.001 | 0.331 | district mean (0.334) | 9/22 |
| soil_weather_history | Random Forest | 22 | 0.614 | 0.377 | 0.141 | 0.449 | district mean (0.334) | 13/22 |
| soil_weather_history | XGBoost | 22 | 0.602 | 0.394 | 0.148 | 0.427 | district mean (0.334) | 14/22 |
| soil_weather_rich_history | Random Forest | 22 | 0.609 | 0.387 | 0.186 | 0.451 | district mean (0.334) | 11/22 |
| soil_weather_rich_history | XGBoost | 22 | 0.598 | 0.416 | 0.211 | 0.485 | district mean (0.334) | 13/22 |
| soil_weather_satellite | Random Forest | 4 | 0.495 | 0.140 | 0.053 | 0.284 | last year (-0.393) | 2/4 |
| soil_weather_satellite | XGBoost | 4 | 0.499 | 0.109 | 0.015 | 0.174 | last year (-0.393) | 2/4 |
| soil_weather_satellite_history | Random Forest | 4 | 0.484 | 0.183 | 0.111 | 0.196 | last year (-0.393) | 2/4 |
| soil_weather_satellite_history | XGBoost | 4 | 0.513 | -0.009 | -0.048 | -0.033 | last year (-0.393) | 2/4 |
| weather_only | Random Forest | 22 | 0.700 | 0.270 | -0.109 | 0.211 | district mean (0.334) | 7/22 |
| weather_only | XGBoost | 22 | 0.680 | 0.312 | -0.058 | 0.267 | district mean (0.334) | 6/22 |
| weather_rich_history | Random Forest | 22 | 0.611 | 0.382 | 0.178 | 0.402 | district mean (0.334) | 10/22 |
| weather_rich_history | XGBoost | 22 | 0.594 | 0.419 | 0.218 | 0.435 | district mean (0.334) | 13/22 |
| weather_rich_only | Random Forest | 22 | 0.700 | 0.275 | -0.093 | 0.235 | district mean (0.334) | 8/22 |
| weather_rich_only | XGBoost | 22 | 0.683 | 0.307 | -0.040 | 0.343 | district mean (0.334) | 8/22 |
| weather_satellite | Random Forest | 4 | 0.523 | 0.054 | -0.028 | 0.248 | last year (-0.393) | 2/4 |
| weather_satellite | XGBoost | 4 | 0.554 | -0.063 | -0.185 | 0.017 | last year (-0.393) | 2/4 |

The highest mean fold R² among production configurations is soil-only XGBoost (0.082), while soil-only Random
Forest has a slightly higher median fold R² (0.340). No single production configuration is consistently strong.
The top research mean is weather-rich-history XGBoost (0.218), followed by soil-weather-rich-history XGBoost
(0.211); these use past yields and/or weather through Dec–Jan and are retrospective associations, not valid
pre-harvest candidates. Satellite-only CV is weak; satellite-inclusive results have only four recent folds and
must not be treated as evidence of general improvement. Do not select a production model from this batch alone.

The 5-fold leave-districts-out Random Forest run completed for supported configurations below. It trains on all
observed years in non-held-out districts; this is a spatial transfer estimate, not a future-year holdout. These
Random Forest results were printed in the command session and captured here. A later XGBoost batch is saved as
JSONL at `data/processed/spatial_validation_20261019T083838.jsonl`; the artifact has a completion record for all
eight supported configurations and five explicit history-feature skips.

| Configuration | Algorithm | Spatial pooled MAE | Spatial pooled R² | Global-mean MAE | Global-mean R² |
|---|---|---:|---:|---:|---:|
| soil_only | Random Forest | 0.752 | 0.089 | 0.782 | -0.025 |
| weather_only | Random Forest | 0.696 | 0.195 | 0.782 | -0.025 |
| satellite_only | Random Forest | 0.673 | -0.049 | 0.664 | -0.021 |
| soil_weather | Random Forest | 0.700 | 0.205 | 0.782 | -0.025 |
| soil_satellite | Random Forest | 0.598 | 0.124 | 0.664 | -0.021 |
| weather_satellite | Random Forest | 0.584 | 0.214 | 0.664 | -0.021 |
| soil_weather_satellite | Random Forest | 0.576 | 0.224 | 0.664 | -0.021 |
| weather_rich_only | Random Forest | 0.672 | 0.233 | 0.782 | -0.025 |

| Configuration | Algorithm | Spatial pooled MAE | Spatial pooled R² | Global-mean MAE | Global-mean R² |
|---|---|---:|---:|---:|---:|
| soil_only | XGBoost | 0.735 | 0.137 | 0.782 | -0.025 |
| weather_only | XGBoost | 0.688 | 0.220 | 0.782 | -0.025 |
| satellite_only | XGBoost | 0.658 | -0.035 | 0.664 | -0.021 |
| soil_weather | XGBoost | 0.688 | 0.238 | 0.782 | -0.025 |
| soil_satellite | XGBoost | 0.639 | 0.024 | 0.664 | -0.021 |
| weather_satellite | XGBoost | 0.595 | 0.154 | 0.664 | -0.021 |
| soil_weather_satellite | XGBoost | 0.575 | 0.252 | 0.664 | -0.021 |
| weather_rich_only | XGBoost | 0.661 | 0.255 | 0.782 | -0.025 |

History-only, soil-weather-history, soil-weather-satellite-history, weather-rich-history, and
soil-weather-rich-history were skipped because district-holdout code does not support yield-history features.
These spatial results should not be compared directly with the stored temporal CV summary or the single holdout.

The XGBoost spatial run produced the best pooled spatial R² among these supported configurations (0.255 for
weather-rich-only, 0.252 for soil-weather-satellite), but these pooled transfer scores are not temporal forecasts
and satellite coverage is restricted. This does not establish a production winner. The spatial script now writes
each result to a unique, incrementally flushed JSONL artifact and refuses to overwrite an existing file.

Historical next-step note, superseded below: the newer official yield years, modern season crosswalk, and yield
basis have since been addressed as documented in Section 13. Crop-calendar-aligned weather/satellite features,
a licensed rice mask, and updated spatial validation remain open. Do not select a production model from a
single-split or pooled spatial score.

## 13. Season-aware refresh and untouched official holdout (2026-10-19)

The APY-to-DES season crosswalk was verified by exact state-level area and production sums for the three years
available in both sources: 2020-21, 2021-22 and 2022-23. Autumn maps to Kar/Kuruvai/Sornavari; Winter maps to
Samba/Thaladi/Pishanam; Summer maps to Navarai/Kodai. Kharif remains separate. Feature encoding canonicalizes
these modern categories while preserving raw labels on observations. Same-season lags and baselines no longer
combine a district's different seasons.

The official DES 2023-24 and 2024-25 district yield tables were extracted to a separate raw CSV and held out
entirely from model fitting/tuning. Units are kg/ha; DES states that paddy production is in terms of rice. Six
zero/no-report cells were excluded. With documented spellings mapped to the existing district records, all 222
positive district-season outcomes were scored on soil, district and season only; future-year weather/satellite
inputs were not available in a verified season-aligned form.

| Algorithm | N | MAE (t rice/ha) | RMSE | R² | Historical district-season baseline MAE |
|---|---:|---:|---:|---:|---:|
| Random Forest | 222 | 0.397 | 0.522 | -0.043 | 0.433 |
| XGBoost | 222 | 0.411 | 0.521 | -0.040 | 0.433 |

Both reduce MAE slightly versus the historical district-season baseline, while R² remains negative. This is a
two-year holdout and does not establish reliable forecasting. Results and row-level predictions are stored in
`data/processed/official_holdout_20261019T095931.jsonl`. The first run with 186 rows was superseded for coverage
by this corrected 222-row alias-mapped run; both artifacts are retained. Fourteen app models were retrained with
season categories. The season-aware expanding-window CV batch `20261019T092852` completed with 26 rows. Its
best pooled temporal result was soil + rich weather + season-aware history with XGBoost (R² 0.393, MAE
0.524 t/ha, 23 folds; 15 folds beat the district-mean baseline). This remains exploratory; the earlier batch
`20261018T191913` is preserved and must be distinguished from it.

Remaining design limits: fixed Aug-Sep weather/Sentinel values are repeated across each year's seasonal rows;
Sentinel coverage is sparse and the measurement is not rice-masked; source Kharif has no verified map into the
modern three groups; no crop-stage forecast cutoff or season-specific district calendar is implemented; the new
official holdout has no matched future weather/satellite inputs. A fresh random-forest spatial validation on
the refreshed cohort is only partial: `data/processed/spatial_validation_20261019T102542.jsonl` contains seven
completed configurations and three expected history skips, but no completion record because richer-weather
evaluation was interrupted. Its results are not a complete spatial batch. Keep the product labeled exploratory;
do not select a production model from pooled temporal or partial spatial scores.
