# Project status — 2026-10-19

## Completed refresh

- Earth Engine authentication succeeded. The single-district pilot ran successfully, then the full 2016–2022 extraction completed.
- Satellite dataset version: `Sentinel-2-NDVI-EVI-peak-monsoon-v2` (DatasetVersion id 5), using matched district polygons where available and stricter Sentinel-2 SCL masking. Extraction inserted 377 feature rows; 73 district-years had no cloud-free imagery.
- The unified training table was rebuilt against v2 only, avoiding a mix of satellite extractor versions across district-years: 765 rows total, 760 valid targets refreshed, five suspect targets excluded, and 172/765 rows (22.5%) with satellite features.
- All 14 configured production model/algorithm runs were retrained. The chronological expanding-window validation batch `20261018T191913` (compact timestamp `20261018191913`) was read back from the database and confirmed to contain 26 rows (13 configurations × 2 algorithms).
- Temporal CV summary: the highest mean fold R² among production configurations is 0.082 (soil-only XGBoost, 22 folds); soil-only Random Forest has the highest production median fold R² at 0.340. The research-only weather-rich-history XGBoost mean fold R² is 0.218, but it is retrospective and not a valid pre-harvest model. Satellite-only mean fold R² is negative and satellite configurations have only four recent folds. Full metrics are in Section 12 of `research_protocol.md`.
- Spatial results are separate 5-fold leave-districts-out transfer estimates. The earlier Random Forest results are documented here; the new XGBoost results are preserved in `data/processed/spatial_validation_20261019T083838.jsonl`. No model has been selected for production.

## Latest single-holdout results (descriptive, not model selection)

These are chronological holdout scores from the retrained runs. The satellite-feature configurations have 126 training and 37 test rows, all from 2022; their scores are not directly comparable with the full-data configurations (591/169 train/test rows, 2018–2022).

| Configuration / algorithm | Test N, years | MAE | RMSE | R² | Baseline R² |
|---|---:|---:|---:|---:|---:|
| soil_only / random_forest | 169, 2018–2022 | 0.486 | 0.594 | 0.460 | 0.451 |
| soil_only / xgboost | 169, 2018–2022 | 0.491 | 0.602 | 0.446 | 0.451 |
| weather_only / random_forest | 169, 2018–2022 | 0.462 | 0.612 | 0.427 | 0.451 |
| weather_only / xgboost | 169, 2018–2022 | 0.458 | 0.595 | 0.458 | 0.451 |
| satellite_only / random_forest | 37, 2022 | 0.541 | 0.761 | -0.065 | 0.377 |
| satellite_only / xgboost | 37, 2022 | 0.508 | 0.666 | 0.183 | 0.377 |
| soil_weather / random_forest | 169, 2018–2022 | 0.469 | 0.597 | 0.455 | 0.451 |
| soil_weather / xgboost | 169, 2018–2022 | 0.461 | 0.598 | 0.453 | 0.451 |
| soil_satellite / random_forest | 37, 2022 | 0.420 | 0.560 | 0.423 | 0.377 |
| soil_satellite / xgboost | 37, 2022 | 0.418 | 0.544 | 0.455 | 0.377 |
| weather_satellite / random_forest | 37, 2022 | 0.452 | 0.575 | 0.391 | 0.377 |
| weather_satellite / xgboost | 37, 2022 | 0.418 | 0.546 | 0.450 | 0.377 |
| soil_weather_satellite / random_forest | 37, 2022 | 0.431 | 0.553 | 0.437 | 0.377 |
| soil_weather_satellite / xgboost | 37, 2022 | 0.402 | 0.508 | 0.525 | 0.377 |

Do not select a production model from this holdout table. The 0.525 satellite-inclusive result uses only 37 test records in one year; consult the stored chronological folds and geographic validation first.

## Spatial validation state

The 5-fold leave-districts-out runs completed for the supported configurations. The Random Forest summary from the earlier run is recorded here. XGBoost results are also saved incrementally in `data/processed/spatial_validation_20261019T083838.jsonl`; the artifact has a completion record for eight configurations and five skips. This JSONL file is a local processed-data artifact, not a database batch. No Python process is currently running.

| Configuration / algorithm | Pooled MAE | Pooled R² | Global-mean baseline MAE | Global-mean baseline R² |
|---|---:|---:|---:|---:|
| soil_only / random_forest | 0.752 | 0.089 | 0.782 | -0.025 |
| weather_only / random_forest | 0.696 | 0.195 | 0.782 | -0.025 |
| satellite_only / random_forest | 0.673 | -0.049 | 0.664 | -0.021 |
| soil_weather / random_forest | 0.700 | 0.205 | 0.782 | -0.025 |
| soil_satellite / random_forest | 0.598 | 0.124 | 0.664 | -0.021 |
| weather_satellite / random_forest | 0.584 | 0.214 | 0.664 | -0.021 |
| soil_weather_satellite / random_forest | 0.576 | 0.224 | 0.664 | -0.021 |
| weather_rich_only / random_forest | 0.672 | 0.233 | 0.782 | -0.025 |

| Configuration / algorithm | Pooled MAE | Pooled R² | Global-mean baseline MAE | Global-mean baseline R² |
|---|---:|---:|---:|---:|
| soil_only / xgboost | 0.735 | 0.137 | 0.782 | -0.025 |
| weather_only / xgboost | 0.688 | 0.220 | 0.782 | -0.025 |
| satellite_only / xgboost | 0.658 | -0.035 | 0.664 | -0.021 |
| soil_weather / xgboost | 0.688 | 0.238 | 0.782 | -0.025 |
| soil_satellite / xgboost | 0.639 | 0.024 | 0.664 | -0.021 |
| weather_satellite / xgboost | 0.595 | 0.154 | 0.664 | -0.021 |
| soil_weather_satellite / xgboost | 0.575 | 0.252 | 0.664 | -0.021 |
| weather_rich_only / xgboost | 0.661 | 0.255 | 0.782 | -0.025 |

History-based configurations were skipped because the spatial-validation implementation does not support yield-history features. These spatial scores and the stored temporal CV scores answer different questions and must remain separate. Spatial validation trains on all observed years in non-held-out districts, so it is not a future-year test.

## Earlier handoff snapshot (superseded by the follow-up below)

1. Inspect fold-level spatial patterns in `data/processed/spatial_validation_20261019T083838.jsonl`; pooled leave-districts-out scores are transfer estimates, not future-year performance.
2. Obtain newer independent yield years for a final untouched temporal assessment. No production model is selected.
3. The original APY CSV audit confirms 1,376 rows, consistent Hectare/Tonnes/Tonnes-per-Hectare units, no duplicate district-year-season-crop rows, and zero yield-vs-production/area discrepancies among rows with production. It does **not** establish whether “Rice” is paddy or milled-rice yield, or map pre-2017 Kharif to post-2017 Autumn/Summer/Winter crop calendars. The builder now states this limitation accurately and continues its existing Kharif/Winter selection; no unsupported season mapping was applied.
4. Satellite v2 remains sparse (22.5% row coverage), fixed to Aug 1–Sep 30, and not paddy-specific. Find licensed rice-area masks and verified crop calendars before engineering crop-stage features.
5. Rich-weather research configurations include weather through Dec–Jan and are retrospective, not pre-harvest forecasts. They are not wired into the prediction form.
6. Review errors by district/year and large misses; verify report/export behavior; restore data-source and reproducible setup documentation.

At the time of this earlier handoff, no runs were pending. The repository has no `.git` directory in this workspace, so a Git working-tree check could not establish a complete changed-file list. Existing validation batches and source observations were preserved; the later dated follow-up below records additive official report files and updated training records.

## Follow-up source audit — 2026-10-19

The staged source file `instance/uploads/8fdabefe80694e8baf27e9dea98e0444_tamil_nadu_rice_apy.csv` was audited read-only. Its seasons are Kharif (1998-99–2016-17), then Autumn, Summer, and Winter (2017-18–2022-23), plus a 1997-98 Whole Year series and Total rows. The importer excludes Total rows. All 1,376 rows have one consistent unit tuple; there are no duplicate district/year/season/crop keys, and all rows with production satisfy yield = production / area within 0.001. Ten rows have missing production. The later official-report crosswalk resolves modern season equivalence for 2020-21 through 2022-23 and confirms rice-equivalent units in newer reports; the original CSV's URL and full historical metadata remain unavailable.

The builder documentation initially corrected the false claim that Kharif was simply relabeled Winter. The subsequent section records the season-aware implementation, expanded refresh, retraining, and official holdout work completed after this audit.

## Season-aware refresh and official holdout — 2026-10-19

The official DES Season and Crop Reports are linked from the [Tamil Nadu DES report catalog](https://des.tn.gov.in/en/node/18). Their state-level 2020-21, 2021-22, and 2022-23 area and production totals exactly verify the CSV crosswalk:

| APY CSV source label | DES rice season group | Verification |
|---|---|---|
| Autumn | Kar / Kuruvai / Sornavari | Area and production match exactly in all three overlapping years |
| Winter | Samba / Thaladi / Pishanam | Area and production match exactly in all three overlapping years |
| Summer | Navarai / Kodai | Area and production match exactly in all three overlapping years |
| Kharif (through 2016-17) | Unmapped legacy category | Kept as a separate category; no verified mapping to the three later groups |

The DES reports state that paddy production is reported in terms of rice and give district-season yield rates in kg/ha. That supports the unit/basis for the new reports; the original CSV still lacks a source URL and full historical metadata. The official 2023-24 and 2024-25 PDFs and an extracted 228-row CSV are saved additively under `data/raw/`. Six zero/no-report yield cells are excluded; 222 positive district-season targets remain.

The builder now includes all non-Total source seasons. The ML pipeline encodes canonical season groups, computes yield lags and historical baselines within the same canonical season, and prediction/scenario forms ask for a season. Source labels remain preserved in the database. The database now has 1,174 unified rows and 1,169 non-null yield targets (the 11 suspect observations remain without targets). Fourteen supported models were retrained and stored as new artifacts/records. The previous models and CV batch `20261018T191913` / `20261018191913` were preserved.

An untouched official two-year temporal holdout for 2023-24 and 2024-25 used soil, district and season only, because post-2022 crop-calendar-aligned weather and satellite features are not available. All 222 positive rows were evaluated after applying six documented DES-to-source spelling aliases. Results in `data/processed/official_holdout_20261019T095931.jsonl`:

| Model | MAE (t rice/ha) | RMSE | R² | Historical district-season baseline MAE |
|---|---:|---:|---:|---:|
| Random Forest | 0.397 | 0.522 | -0.043 | 0.433 |
| XGBoost | 0.411 | 0.521 | -0.040 | 0.433 |

Both models modestly reduce MAE versus the historical baseline, but negative R² means neither explains the holdout's overall variance. These results do not establish reliable forecasting or justify production selection. The earlier first holdout artifact had 36 unmatched rows; the corrected artifact maps all six district spelling variants and is the one to use.

The expanding-window temporal CV for the changed season-aware pipeline completed in batch `20261019T092852` with 26 rows; details are in the dated follow-up below and `todo.md`. The earlier batch `20261018T191913` remains unchanged. A fresh spatial run on the expanded cohort is only partial: see the latest handoff below. Do not present it as complete.

## Handoff — 2026-10-19 after season-aware validation refresh

- Database cohort: 1,174 unified records; 1,169 non-null yield targets. Satellite source version: `Sentinel-2-NDVI-EVI-peak-monsoon-v2` (DatasetVersion id 5).
- Season-aware expanding-window CV batch `20261019T092852`: 26 saved configuration/algorithm rows. Best pooled result was soil + rich weather + season-aware history with XGBoost: pooled R² 0.393, MAE 0.524 t/ha, 23 folds, 15/23 folds beating the district-mean baseline. This is temporal cross-validation, not the untouched 2023-25 holdout, and is not enough to select a production model.
- Untouched official 2023-24/2024-25 holdout remains unchanged: 222 positive targets; RF R² -0.043 / MAE 0.397, XGBoost R² -0.040 / MAE 0.411, baseline MAE 0.433. Holdout only covers soil, district, season.
- Refreshed spatial run artifact `data/processed/spatial_validation_20261019T102542.jsonl` has 7 completed Random Forest modality results and 3 history-related skips, but was interrupted during the richer-weather configuration. It has **no run_complete record** and is a partial artifact. Previous spatial result artifact `spatial_validation_20261019T083838.jsonl` remains preserved for its older cohort.
- The refreshed spatial artifact’s completed pooled RF R²: soil 0.132; weather 0.240; satellite 0.183 (4 folds); soil+weather 0.213; soil+satellite 0.189 (4 folds); weather+satellite 0.271 (4 folds); soil+weather+satellite 0.259 (4 folds). History features are unsupported by district holdout and were skipped. These scores are spatial transfer estimates, not forecasts.
- No Python run remains active. Existing batches, datasets, models, logs, and result files were preserved; the interrupted JSONL is additive and must not be overwritten. Workspace has no `.git` directory, so Git cannot report a changed-file inventory.

### Next steps

1. Read the stored 26-row CV batch and inspect fold-level distributions/error slices; compare it separately against the official holdout and spatial validation.
2. If resuming spatial work, use a new timestamped output. Run `weather_rich_only` only if needed; do not attempt history configurations until a valid unseen-district history feature design exists. Do not mark the partial artifact complete.
3. Obtain original APY provenance/yield basis, a licensed rice extent mask, and verified season/crop-stage calendars. Rebuild weather and satellite features by forecast cutoff and season; the current fixed Aug-Sep repeated values cannot validate seasonal pre-harvest forecasting.
4. Add matched official weather/satellite coverage for years reserved for independent holdout, then evaluate once without tuning on holdout labels. Do not choose a production model until that evidence exists.

Important limitations still open: satellite and fixed-window weather values are annual Aug-Sep measurements repeated across multiple season rows, not season-specific crop-stage inputs; satellite coverage remains sparse and not rice-masked; the old Kharif category has no verified modern counterpart; official 2023-25 holdout contains yield targets but not matched future weather/satellite inputs; the two-year holdout does not establish long-run reliability. No production model is selected.

## Execution addendum — 2026-10-19 (forecast cutoff, crop mask pilot, and verification)

### Current code and data changes
- Added a soil-only pre-season prediction path. It rejects target years at or before the current year/latest historical year and excludes year-specific weather, satellite imagery, and yield-history features, so it is a pre-season estimate rather than a forecast informed by in-season observations. Prediction outputs record their `preseason` mode. The form now examples `2027-2028` to match the validator on the current date (Oct 19, 2026).
- Added optional ESA WorldCover 2021 v200 generic cropland masking to the Sentinel-2 extractor. A one-district Thanjavur pilot completed for 2022 and inserted two indices (NDVI and EVI); it is marked `partial_test`, and the unified builder excludes partial-test versions. Existing satellite releases and old results were retained.
- The mask is generic cropland class 40, not rice-specific. In the updated extraction, valid-pixel count is the number of 20 m region pixels with both NDVI and EVI unmasked after cloud and cropland masking; its denominator is all 20 m pixels in the district geometry. It does not establish rice-specific coverage. No rice-specific external mask was integrated because the discovered candidate has a non-commercial/no-derivatives license that is not suitable for unrestricted derivative integration.
- Added source notes and a small calendar reference table. The Tamil Nadu sources provide stage windows for selected districts/seasons; complete, consistent district-by-season sow/harvest dates are still unavailable. Do not fill gaps by interpolation without documenting assumptions.

### Verified results and artifacts
- Repeated official 2023-24/2024-25 holdout artifact: `data/processed/official_holdout_20261019T111633.jsonl`, 222 targets. RF MAE 0.3973 t/ha, RMSE 0.5216, R² -0.0425; XGBoost MAE 0.4111, RMSE 0.5208, R² about -0.040; district-season baseline MAE 0.4330. Both model R² values remain negative. This target-only holdout does not compare weather/satellite inputs.
- Completed spatial transfer artifacts: `data/processed/spatial_validation_20261019T111749.jsonl` (RF) and `data/processed/spatial_validation_20261019T111852.jsonl` (XGBoost), five district holdout folds each. RF soil-only pooled R² 0.132, MAE 0.613; XGBoost soil-only pooled R² 0.186, MAE 0.595; district baseline pooled R² 0.056, MAE 0.625. These are spatial transfer tests over observed years, not forward-in-time forecasts.
- Earlier temporal CV batch `20261019T092852` and preserved chronological batch `20261018191913` remain historical. Do not equate their retrospective/weather-rich results with pre-season or independent holdout performance.
- Earth Engine auth and public WorldCover collection access succeeded in the prior check; the later pytest collection check could not refresh OAuth because external DNS/network was unavailable. The one-district extraction had succeeded. Do not interpret the pytest transport failure as proof the account credentials are invalid.

### Test state and pending tasks
- Focused tests run: `.venv\\Scripts\\python.exe -m pytest tests/test_preseason_prediction.py tests/test_history.py tests/test_training_logic.py tests/test_leakage_prevention.py tests/test_satellite_cache_key.py -q` — 19 passed.
- Full pytest collection is not cleanly runnable in the current sandbox: `scripts/test_earth_engine.py` authenticates and queries EE at import time (external network blocked); app tests require local MySQL at `localhost:3306` (socket access denied). `tests/test_crop_calendar.py` is currently untracked and directly queries the production database; it also failed under the same local MySQL restriction. Do not run that file against the production database as a test.
- No new model experiment or full satellite extraction was run in this verification pass. The checked output files exist with non-zero sizes. No Python processes were running at the workspace check.
- Final verification update: `.venv\\Scripts\\python.exe -m pytest tests -q` completed with **71 passed in 24.39s** when local MySQL access was approved. The prior unfiltered `pytest -q` attempt failed at collection because it also imported `scripts/test_earth_engine.py`, a live integration script; the project test directory is the appropriate suite. The standalone integration check then succeeded: `scripts/test_earth_engine.py` initialized project `agriyield-predictor-510308` and found 24 Sentinel-2 images over the central Tamil Nadu point in Jan 2023.
- The workspace has an existing Git recovery checkpoint `affcba4` and only the currently reported working changes; inspect `git status` before resuming. Existing artifacts were not deleted or rewritten in this pass.

### Exact next steps
1. Review the working tree; determine the origin and purpose of untracked `tests/test_crop_calendar.py`. Keep it from querying production DB, and relocate any intended migration check into an isolated test fixture before including it in the suite.
2. On the user's machine with MySQL service running, run the normal app suite using the isolated `agriyield_predictor_test` database. Keep EE connectivity as a separately invoked integration check, not a pytest import side effect.
3. Implement a matched satellite ablation: pair baseline and satellite rows on identical district-season-year keys, use identical expanding temporal folds and only pre-cutoff imagery, and report matched sample counts, coverage, RF/XGBoost plus regularized linear baseline. Do not compare current unmatched satellite folds as evidence of satellite benefit.
4. Verify the APY original source URL and exact yield-series definition from source metadata before changing provenance labels. Current official handbook evidence supports describing Tamil Nadu DES values as rice-equivalent, but the uploaded APY file's exact source chain is not fully established.
5. Add district-season-year aligned crop-stage features only after verifying calendar coverage and imagery availability cutoffs. Continue to report the 2023-25 holdout separately and do not select a production model from preliminary scores.

## Matched satellite ablation and extraction audit — 2026-10-19

### Preservation and target provenance
- Recovery commit remains `affcba4`; working changes and timestamped artifacts are additive. Read-only database check found the preserved 26-row historical CV batch stored as `20261018T191913` (the compact ID `20261018191913` is the same timestamp); no records were changed. The latest season-aware batch `20261019T092852` also remains present.
- The staged APY CSV is `instance/uploads/8fdabefe80694e8baf27e9dea98e0444_tamil_nadu_rice_apy.csv`, 169,747 bytes, local modified date 2026-09-30. Audit SHA-256: `E6D2FBA680CB3D5D6140515A2D0D9CE571F4B5B952A563EBD25448B627876550` (a local integrity fingerprint, not an upstream checksum).
- Database DatasetVersion 1 stores source name `TN DES Rice Crop`, original filename `tamil_nadu_rice_apy.csv`, 1,376 rows, but has no source URL or checksum. All 1,180 imported yield observations have `source_url = NULL`. The schema, fields and numeric checks strongly match the DES APY series and official state aggregates for the 2020-21–2022-23 overlap match exactly; however, the exact downloaded resource/file chain is not proven. The local rows say `Tonnes/Hectare`. Tamil Nadu DES publications define paddy in terms of rice for their covered report years, but that does not independently establish the measurement basis for every older row in this upload. Do not relabel or rescale historical values pending source confirmation.
- Importer drops `Total` aggregate rows, stores the provided yield/area/production without unit conversion, flags missing/suspect/mismatched records, and records the DatasetVersion URL (null here). Model preprocessing canonicalizes modern Autumn/Winter/Summer season labels based on the verified DES crosswalk; legacy Kharif remains separate. The standalone official 2023-25 evaluation’s target basis is rice-equivalent tonnes/ha, supported by the DES report footnote, and it has matching `Tonnes/Hectare` units.

### Reproduced official holdout and diagnosis
- Recomputed saved per-row predictions in `data/processed/official_holdout_20261019T111633.jsonl`; no refit or tuning against this holdout occurred. All three model/baseline evaluations use the same 222 targets, 38 districts, and 2023-24 plus 2024-25 years. Target missingness among scored records is zero; the 222 records are positive targets after the six documented no-report/zero cells were excluded.
- Target distribution: mean 3.660, SD 0.512, median 3.7585, range 1.766–4.988 t rice-equivalent/ha. Model RMSE is approximately the full target SD, explaining the slightly negative R². RF errors are especially large for Thoothukkudi 2023-24 Samba (−2.173 t/ha signed actual-minus-predicted) and Ramanathapuram 2024-25 Navarai (+1.594); XGBoost’s largest miss is Thoothukkudi 2023-24 Samba (−2.114). Model MAE is below the district-season baseline, but both R² values remain negative.

| Same 222-row official holdout | R² | MAE (t/ha) | RMSE (t/ha) |
|---|---:|---:|---:|
| District-season historical mean baseline | -0.0917 | 0.4330 | 0.5337 |
| Random Forest | -0.0425 | 0.3973 | 0.5216 |
| XGBoost | -0.0396 | 0.4111 | 0.5208 |

### Matched temporal feature ablation
- Reproducible command: `.venv\\Scripts\\python.exe scripts\\run_matched_satellite_ablation.py`.
- New append-only artifact: `data/processed/matched_satellite_ablation_20261019T134505521937Z.jsonl`. It uses exactly 440 district-season-year rows matched one-to-one across the current soil+weather and soil+weather+satellite frames, 38 districts, 168 district-years, years 2016–2022, and common yield units. This is 37.6% of the 1,169-row soil+weather cohort. Satellite values are repeated across seasons within a district-year; 440 seasonal rows therefore are not 440 independent satellite observations.
- A fixed three-year warmup gives four identical outer test folds (2019, 2020, 2021, 2022): test n = 76, 82, 103, 108 (369 pooled scored rows); train n = 71, 147, 229, 332. The heldout years cover 130 distinct district-years. RF/XGBoost candidates and Ridge alpha `[0.1, 1, 10, 100]` were selected only inside each outer training window. Preprocessing for Ridge (median imputation, scaling, district/season one-hot encoding) is fit inside training folds. The same district-season baseline and records are used for every modality.

| Features | Model | Pooled R² | MAE | RMSE | Same-fold district-season baseline R² / MAE / RMSE |
|---|---|---:|---:|---:|---|
| Soil + weather | RF | 0.1676 | 0.3948 | 0.5317 | 0.1587 / 0.4014 / 0.5345 |
| Soil + weather + satellite | RF | 0.1682 | 0.3908 | 0.5315 | 0.1587 / 0.4014 / 0.5345 |
| Soil + weather | XGBoost | 0.2638 | 0.3762 | 0.5000 | 0.1587 / 0.4014 / 0.5345 |
| Soil + weather + satellite | XGBoost | 0.2534 | 0.3745 | 0.5035 | 0.1587 / 0.4014 / 0.5345 |
| Soil + weather | Ridge | -0.5061 | 0.5002 | 0.7151 | 0.1587 / 0.4014 / 0.5345 |
| Soil + weather + satellite | Ridge | -0.4806 | 0.4899 | 0.7091 | 0.1587 / 0.4014 / 0.5345 |
| Satellite only | RF | 0.0740 | 0.4064 | 0.5607 | 0.1587 / 0.4014 / 0.5345 |
| Satellite only | XGBoost | -0.1372 | 0.4580 | 0.6214 | 0.1587 / 0.4014 / 0.5345 |
| Satellite only | Ridge | 0.1403 | 0.4198 | 0.5403 | 0.1587 / 0.4014 / 0.5345 |

Satellite effects are small and inconsistent: RF gains 0.0006 pooled R²; XGBoost loses 0.0104 pooled R² despite a 0.0018 MAE decrease. Satellite-only does not beat the baseline on any pooled metric. The 2019 RF/XGBoost satellite gains do not persist uniformly through 2020–22. Ridge does not beat the baseline; its large negative pooled R² is driven by the small 2019 training cohort (71 rows with district/season categories). No model is selected. These retrospective results use August–September inputs and cannot establish pre-sowing or pre-harvest forecast performance.

### Satellite pipeline verification and fix
- Official Earth Engine documentation says `filterDate` includes its start and excludes its end. The previous `2022-09-30` end therefore omitted all of September 30. The extractor now passes `10-01` as the exclusive end to represent Aug 1 through Sep 30 inclusively. New release labels distinguish this corrected window (`...-v3`, WorldCover path `...-cropland-v2`) and old dataset IDs/caches are unchanged.
- Added explicit valid and total 20 m pixel counts. A one-district Thanjavur live EE check (2024-08-01 to 2024-10-01 exclusive; WorldCover v200 class 40; S2 SR Harmonized; SCL classes 4–6 retained, including water) returned 24 scenes, NDVI 0.46578, EVI 0.31585, 4,563,091 valid joint-index pixels / 8,775,828 district pixels (51.996%). This validated the live formulas/mask/reduction path and cache response. The cache file is `data/external/satellite_cache/b1122214a3b1898b3ed980523beffc3a.json`. No satellite rows were inserted, no unified dataset was rebuilt, and no production DB refresh occurred.
- WorldCover is a 2021, 10 m generic land-cover classification and class 40 means cropland, not rice. The mask does not establish which pixels are paddy or whether rice rotations match the target year. The value is diagnostic only.
- The unified builder joins satellite by district and agricultural start year, then copies that same annual fixed-window measurement to each yield season in that district-year. Thus current satellite rows are not season-specific. Weather uses the same Aug 1–Sep 30 target-start-year window. This feature design remains retrospective for many season prediction dates.

### Verification and pending work
- Full project test directory after changes: `.venv\\Scripts\\python.exe -m pytest tests -q` — **75 passed in 27.40s**. `git diff --check` passed. The standalone EE test worked in the current environment; its Google project/auth result remains private in the user environment, not written to configuration.
- The earlier Git state had uncommitted changes in `PROJECT_STATUS.md`, the pre-season form/test, plus an untracked `tests/test_crop_calendar.py`; additional changes from this pass include the matched evaluation script/tests, corrected date-window/pixel-count code/tests, and the prediction module wording. Check `git status` before any commit. No running Python process was left.
- The test suite uses the isolated test DB fixtures; `tests/test_crop_calendar.py` is still untracked and directly reads `alembic_version` from the configured DB. It made no writes during the passing run. Move its migration-graph assertion to an isolated test before relying on it in future environments.
- Highest-value next action: obtain/record an authoritative APY download and historical yield-basis metadata; then acquire season-resolved satellite and weather inputs available by a defined forecast cutoff. Re-evaluate with matched expanding temporal folds and a newly reserved independent year. Keep the 2023-25 holdout untouched and do not select a model based on this ablation.

### Follow-up provenance capture change
- Future confirmed uploads now store a SHA-256 hash in `DatasetVersion.checksum_sha256`; the APY importer copies the input CSV's `id` into `YieldObservation.source_record_id` when present. No existing upload, observation, dataset version, or database value was backfilled or changed.
- A read-only query confirmed APY DatasetVersion 1 has `source_url = NULL`, `checksum_sha256 = NULL`, original filename `tamil_nadu_rice_apy.csv`, and 1,376 source rows; all 1,180 existing yield observations have null source URLs and source record IDs. This confirms that exact original-file provenance cannot be reconstructed from the stored database records alone. Local staged-file checksum is recorded above only as an audit fingerprint.
- Provenance unit tests passed. After this follow-up, `.venv\\Scripts\\python.exe -m pytest tests -q` completed with **77 passed in 27.02s**; relevant changed Python files also passed `py_compile`.

## Experimental Sentinel-2 processing pass — 2026-10-19

- Added an isolated processing path, `scl-index-timeseries-v3`: NDVI, EVI, and NDMI; SCL cloud/shadow masking happens before same-day composites; cache keys include processing version; outputs include central/p90/peak summaries, distinct dates, valid observation fractions and 20 m area/pixel coverage. Fewer than three distinct acquisition days is marked `insufficient_dates`. The optional generic crop mask applies consistently to all summaries and observation counts. New future ingestion releases use separate version labels. Historical database rows, official holdout and experiment batches were not altered.
- The v3 cache-only Thanjavur pilot completed with 24 scenes/10 daily composites. Unmasked/masked medians: NDVI 0.51328/0.46714, EVI 0.36079/0.31647, NDMI 0.09902/0.07970. Class-40 area 1,784.88 km² / full 3,428.10 km² (52.07%); valid area 1,782.26 km². Valid count 4,563,091/8,775,828 (52.00% of full district; 99.85% of mask area); at least three valid dates cover 48.68% of full area. Cache reuse succeeded for both masks. Artifact: `data/processed/satellite_timeseries_pilot_thanjavur_2024_20261019T143541Z.json`. No MySQL connection/write or unified refresh.
- The v1 and v2 artifacts/caches remain preserved and excluded from analysis (v1 mask omission; v2 cloud-mask ordering). v3 is the valid pilot output. No yield ablation was run: one district-year is far too small and the fixed window is not season/cutoff-aligned.
- Coverage interpretation: pixel counts use the nominal 20 m reduction grid; `valid_pixel_pct` is a 0–100 percentage of the full polygon; the two observation coverage fields are proportions [0,1] of the full polygon after the optional mask; area fields are m². The v3 mask result's 52.00% is full-polygon coverage and about 99.85% of the 2021 generic cropland mask. `partial` is full-polygon coverage status, not a failed request. WorldCover class 40 is not a rice mask.
- Ingestion now retains any available NDVI/EVI/NDMI summary rather than dropping the district-year solely because NDVI is null; a local regression test covers this edge case. **At the time of this entry**, the unified builder and model schema did not yet consume v3. See the later V3 feature schema integration addendum below.
- Rice mask source review: SARice/Open-SARice-10 is South Asia-wide, 2021, 10 m EPSG:4326, with single/double/triple cropping classes; India raster is about 800 MB. The paper states CC BY-NC-ND 4.0 but the data record does not clearly state separate raster terms. Integration is pending rights clarification. SICKLE offers 2018–Mar 2021 plot-season data, including 351 rice samples in 145 plots across four Cauvery Delta districts; its public page links data but license terms need direct confirmation. Neither dataset was downloaded or integrated.
- Existing mask limitation stands: WorldCover 2021 class 40 is generic cropland and static. No verified complete district-season calendar exists, so Aug-Sep remains a retrospective processing window; no pre-season/in-season prediction claim or satellite-based model improvement is justified.
- Rice-mask sources: SARice/Open-SARice-10 offers 2021, 10 m South Asia coverage and single/double/triple rice-frequency classes, but the paper states CC BY-NC-ND and the separate raster license is unclear. SICKLE has plot-season data for 2018–Mar 2021, including 351 paddy samples in 145 plots across four Cauvery Delta districts; reuse terms need confirmation. Neither was integrated. The mask in this pilot is generic WorldCover class 40 and static 2021.
- No comparable yield-model ablation was run: one district-year, annual Aug-Sep features and no verified season/cutoff alignment cannot establish predictive value. No production model selected. Weather/satellite features remain retrospective until crop-season windows and forecast availability are defensible.
- Verification: targeted satellite tests 5 passed; full test suite excluding pre-existing `tests/test_crop_calendar.py` (which directly queries configured production DB) passed 78 tests. Python compilation and app factory import passed. The full unfiltered suite was attempted but failed because sandbox networking blocked localhost MySQL; the isolated relevant suite completed after allowing test DB access. Next: verify extraction output, then gather matched season-aware data at scale only after a documented cutoff/calendar and license check. No statewide extraction yet.

## V3 feature schema integration — 2026-10-19

- Added a distinct v3 feature family to the unified builder and model configuration: the exact unmasked release label `Sentinel-2-NDVI-EVI-NDMI-timeseries-v3` is selected, and v1/v2 legacy features remain in their original columns/configurations. The generic WorldCover v3 release is not implicitly substituted or mixed.
- V3 fields now cover NDVI/EVI/NDMI median, p90 and peak; source scene and distinct-day counts; full-district valid-pixel percent; observed-pixel and >=3-observation fractions; and an explicit `satellite_v3_has_data` missingness flag. Missing optional values remain null. Training fold preprocessing uses training-only median imputation and keeps all-empty v3 columns for shape stability.
- The builder joins v3 on district + agricultural year + the extractor's `aug-sep-fixed-window` label. This is one annual window and is copied to each source-season yield row; it is not a season-specific feature. A v3 cutoff guard marks it unavailable before Oct 1 of the target start year. The live pre-season workflow remains soil-only, so these retrospective features are not used for a pre-season forecast.
- Added migration `a71f2d9c4e10`; it has **not** been applied. MySQL was not modified and unified data was not rebuilt. The current completed pilot is only JSON/cache; no v3 rows exist in the unified training table from that artifact. Thus code now supports v3 consumption after migration and an explicitly approved feature build, but v3 is **not currently consumed by trained models**.
- The v3 ingestion maps coverage and observation metadata to stable `SatelliteFeature.index_name` values in addition to indices. Extraction itself was not run. The official holdout, database, all satellite artifacts, and experiment batches were left untouched.
- Forecast window supported by the current evidence: v3's fixed retrospective Aug 1–Sep 30 window is only available after that window ends (exclusive end Oct 1). No fully verified district-by-season planting calendar is wired into the model; no season-specific timing claim is made.
- Pending safe activation: first review/apply the additive migration on the intended database backup, then explicitly import/refresh v3-derived features into a separately versioned unified dataset. Do this only after confirming the saved extraction/source-row representation, since the existing Thanjavur pilot JSON is not automatically imported. Next run local schema/model-loader checks, then a matched temporal ablation against the legacy non-satellite baseline; keep official holdout untouched.

## Controlled v3 research collection pre-flight and bounded job — 2026-10-19

- Read-only pre-flight used the local APY upload (`instance/uploads/8fdabefe80694e8baf27e9dea98e0444_tamil_nadu_rice_apy.csv`): 1,376 source rows, 38 district names, 26 agricultural years (1997-98 through 2022-23), and 799 distinct district-year pairs after excluding `Total` (771 after also excluding `Whole Year`). A conservative Sentinel-2 SR Harmonized period is 2017-2022: the official Earth Engine catalog starts the collection on 2017-03-28. This is 208 source district-year pairs across all 38 districts, unchanged after excluding aggregate labels. No exact current unmasked-v3 cache keys existed for those 208 jobs; the saved Thanjavur 2024 pilot is outside the APY period. All 38 candidate district geometries resolve locally. ESA confirms Sentinel-2A launched in 2015 and Sentinel-2B in 2017; the collection availability start, rather than satellite launch date, sets the conservative 2017 lower bound.
- The configured target is local MySQL `localhost:3306/agriyield_predictor`; no credentials were printed and no connection/write was made. The migration remains unapplied. For later database work, first use a unique timestamped `mysqldump --single-transaction --routines --triggers --events --hex-blob` backup with password prompting or a protected MySQL login path, verify nonzero size and restore into an isolated database; do not redirect credentials into command text.
- Existing DB-fetch script has no retry policy and writes satellite rows to MySQL; it was not used. The v3 extractor uses a processing-version/mask/geometry/date-aware cache and makes multiple Earth Engine evaluations per district-year (image count, timestamps, index summaries, pixel/area counts, observation coverage); 208 misses therefore imply 208 district-year jobs and many remote reductions. Statewide extraction remains paused.
- Added `scripts/collect_satellite_research_batch.py`, an explicitly bounded, append-only JSON collector that validates result fields, reuses the shared cache, requires a local polygon, and never writes MySQL or unified data. One job was authorized and run: Thanjavur 2022-23, unmasked SCL v3, 2022-08-01 inclusive to 2022-10-01 exclusive. Successful artifact: `data/processed/research_satellite_v3/v3_2022_thanjavur_20261019T154542912076Z.json`; cache: `data/external/satellite_cache/cce8ad79c088e5265096374e5b6321f6.json`.
- Result status was `partial` relative to the full district polygon: 23 scenes, 13 distinct daily composites, NDVI 0.55535, EVI 0.39255, NDMI 0.16531; p90 NDVI/EVI/NDMI 0.62378/0.45117/0.23127; per-pixel seasonal peak means 0.62422/0.45162/0.23180. Valid 20 m pixels: 8,712,900 / 8,775,828 (99.283%); at-least-three-observation coverage 0.63453 of the full region. No cropland/rice mask was used. The output records both source year label `2022-2023` and compact database join key `2022-23`.
- Two failed attempts were preserved as separate artifacts: first found the source-vs-database year-label mismatch before Earth Engine; the corrected sandbox attempt failed OAuth DNS resolution. The final network-enabled run succeeded; it did not reuse cache, and the new v3 cache was created. Database, unified training records, official 2023-24/2024-25 holdout and earlier pilot artifacts were not touched.
- Validation of the new batch collector and v3/cache/window helpers: Python compilation passed and 12 focused tests passed. Do not run the full suite as-is for this batch: its shared MySQL fixture creates/drops database tables, while this task explicitly left the database untouched. `git diff --check` passed with line-ending warnings only.
- Next step requires explicit approval: define and review a resumable statewide execution budget/checkpoint cadence and decide whether the 208-job (2017-22) set is acceptable. Then run only bounded batches into the research artifact directory, review every partial/no-data/failure status, and do not apply migration/rebuild unified records until collection coverage and backup/restore are reviewed. These fixed Aug-Sep values remain retrospective and repeated across seasons; they do not establish forecast-safe timing or model improvement.

## First five-job research batch — 2026-10-19

- Updated the bounded collector with explicit batches capped at five jobs, a mutable atomic manifest checkpoint, immutable per-attempt job JSON files, completed-artifact discovery (including `partial` and `no_data`), per-job runtime/scene/day/index/coverage/cache/error fields, and one attempt per job per invocation. `--resume MANIFEST` is the explicit retry path; completed job outputs are skipped, failed artifacts remain, and the batch stops on the first failure. A focused test verifies that the saved Thanjavur 2022-23 partial artifact is found and therefore not repeated.
- Ran only Ariyalur, Cuddalore, Nagapattinam, Thiruvarur, and Ramanathapuram for 2022-23. Batch manifest: `data/processed/research_satellite_v3/batches/batch_20261019T155445472686Z/manifest.json`. Five immutable job artifacts and their cache keys are listed there. No job reused a cache; each created a v3 cache. No Earth Engine error occurred.
- Outcomes: 5 partial, 0 full-success, 0 no-data, 0 failed. Aggregate extractor runtime was 302.522 s; wall time from manifest creation to completion was about 302.7 s. Scenes/day counts/valid coverage: Ariyalur 16/11/99.891%; Cuddalore 20/11/98.992%; Nagapattinam 6/5/97.140%; Thiruvarur 6/5/98.191%; Ramanathapuram 21/10/99.407%. Each valid-pixel percentage is of the full district geometry. At-least-three-observation fractions were 0.95859, 0.85235, 0.14811, 0.27079, and 0.67002 respectively. All are unmasked SCL v3, fixed Aug-Sep 2022 windows, not rice-specific and not season/cutoff-aligned.
- `Thanjavur 2022-23` was recognized from its saved artifact and excluded from this batch. Within the stated 208-job 2017-22 set, six jobs now have saved results (the prior Thanjavur job plus these five), leaving an estimated 202 uncached jobs. This remains a request-count estimate; per-job Earth Engine calls and quota are variable.
- Tests/compilation after collector changes: 15 focused tests passed; `py_compile` passed; `git diff --check` passed with existing line-ending warnings. No MySQL connection/write, migration, unified rebuild, model training, or official holdout access occurred.
- Stop here pending user approval. Before another batch, review the five outputs and approve the next bounded job list. No statewide extraction or migration has started.

## V3 research-only integration and matched temporal comparison — 2026-10-20

- Added `scripts/run_v3_satellite_research_ablation.py` to join saved, version-checked v3 district-year artifacts to the existing soil+weather yield cohort without importing them into MySQL. It ignores failed/no-data results, rejects non-v3 releases and unexpected date windows, preserves optional missing indices as missing, and explicitly labels the Aug-Sep data retrospective and shared across seasons. Added `tests/test_v3_research_ablation.py` for release filtering, optional missing values, seasonal joins and duplicate-key rejection.
- The read-only MySQL check confirmed `agriyield_predictor` has 1,169 non-null yield rows, but the unified table currently has 26 columns and no v3 columns; migration `a71f2d9c4e10` remains unapplied. The research script therefore selects only legacy soil/weather/target columns and does not use the ORM's v3 fields. No migration, DB write, unified rebuild, production retraining or official-holdout access occurred.
- At evaluation time there were 97 usable v3 district-years across 37 districts and 2017–2022. Joining against the six-year soil+weather cohort yielded 269 district-season-year rows (46.4% of its 580 rows). The expanding temporal evaluation used three identical test folds (2020 n=33, 2021 n=47, 2022 n=99; 179 pooled scored rows). The paired non-satellite and v3 models used the same rows and fold boundaries; RF/XGBoost hyperparameters were selected only within each outer training window. The district-season baseline was identical in each pair.

| Features / model | Pooled R² | MAE (t/ha) | RMSE (t/ha) |
|---|---:|---:|---:|
| Soil + weather, RF | 0.1478 | 0.3950 | 0.5370 |
| Soil + weather + v3, RF | 0.1470 | 0.3913 | 0.5372 |
| Soil + weather, XGBoost | 0.1342 | 0.4097 | 0.5412 |
| Soil + weather + v3, XGBoost | 0.1496 | 0.3907 | 0.5364 |
| Same-fold district-season baseline | 0.0955 | 0.4159 | 0.5532 |

- Effect is small and inconsistent. RF v3 lowered MAE by 0.0037 t/ha but slightly lowered R² and slightly increased RMSE; XGBoost v3 improved pooled R² by 0.0154, MAE by 0.0191 t/ha and RMSE by 0.0048 t/ha. Both v3 and non-v3 still had negative R² in the 2020 fold; only three test years and 179 rows are available. This is preliminary retrospective evidence, not proof of statewide or forecast accuracy improvement and not grounds for production model selection.
- Append-only research outputs: `data/processed/v3_research_matched_dataset_20261019T190940576965Z.csv` (269 rows) and `data/processed/v3_research_ablation_20261019T190940576965Z.jsonl` (metadata, paired fold metrics and completion record). These preserve v3 release/window metadata and do not include the official 2023-25 holdout.
- Verification: `.venv\\Scripts\\python.exe -m pytest tests\\test_v3_research_ablation.py tests\\test_satellite_v3_integration.py tests\\test_matched_satellite_ablation.py -q --basetemp=data\\processed\\pytest_v3_research_tmp_20261020` — 8 passed; new script passed `py_compile`; `git diff --check` passed with existing line-ending warnings. Default pytest temp creation was blocked outside the workspace; rerunning with an in-workspace basetemp passed.
- Next: keep v3 as a research-only dataset, complete the remaining bounded collection batches, inspect missing/no-data coverage, then rerun the same paired temporal experiment with an adequately broader cohort. Season-specific calendars and forecast-cutoff-valid imagery remain unresolved; the present August-September composite must not be treated as a pre-season feature. Apply the migration/import path only after separate review and approval.

## Season-aware feature feasibility check — 2026-10-20

- Re-inspected the current prediction path and local `data/raw/tamil_nadu_rice_calendar_reference.csv`. The operational pre-season estimate is soil-only plus district and selected season; current-year weather, satellite and yield history are excluded. It rejects target agricultural start years not later than the current year or latest training year. The page advises submitting before sowing, but calendar-date eligibility is explicitly not enforced.
- No new weather or satellite crop-stage feature was added. The local TNAU statewide entries mostly provide sowing months only (or variety duration), not complete district-specific growth/harvest stages. The detailed Villupuram calendar has sow/growth/harvest month ranges for Sornavari, Samba and Navarai but has no publication date in the local reference and cannot be mapped uniquely to the model's merged categories: `Autumn` maps to Kar/Kuruvai/Sornavari and `Winter` to Samba/Thaladi/Pishanam. Thiruchirappalli/Perambalur entries provide broad season periods only, not stage windows. The remaining district-season dates are unknown; no missing months were inferred.
- The v3 satellite values now saved locally are fixed Aug 1–Sep 30 district-year composites copied across source seasons. They cannot be split into season-specific image periods after extraction. Using these as distinct seasonal or pre-season features would be temporally misleading. A matched season-aware experiment is therefore unsupported by the current feature artifacts; no accuracy claim or model comparison was made in this pass.
- Safe next improvement requires an authoritative, dated district × source-season calendar with a verified source-season crosswalk, plus historical weather and satellite summaries computed within that calendar and a declared forecast cutoff. Until then, keep the soil-only pre-season workflow and label the missing calendar-date enforcement as a limitation; treat weather/satellite v3 as retrospective only.
- Verification only: `.venv\\Scripts\\python.exe -m pytest tests\\test_preseason_prediction.py tests\\test_leakage_prevention.py tests\\test_satellite_v3_integration.py tests\\test_satellite_window.py -q --basetemp=data\\processed\\pytest_season_cutoff_tmp_20261020` — 10 passed. Python compilation passed for the season, prediction and v3 helper modules; `git diff --check` passed with existing line-ending warnings. No full-suite run, network search, Earth Engine extraction, MySQL connection/write, production refresh, or holdout access was performed.

## Forecast calendar status and cutoff signaling — 2026-10-20

- Added `app/services/ml/forecast_calendar.py` with conservative evidence classification and an exact-date cutoff boundary helper. The local reference CSV has traceable TNAU/TN AGRIS month windows, but these are not year-scoped exact dates and the detailed Villupuram crop seasons do not map uniquely to the APY model's merged season labels. Therefore no current district/model-season receives a verified cutoff; its forecast calendar assessment is `unknown` with no cutoff date.
- The soil-only pre-season path now stores and returns calendar status/date/reason. The UI explicitly warns that sowing-cutoff validation is unsupported, so the estimate may be after sowing. Existing soil-only inputs remain unchanged; current-season weather, satellite and historical yield are not introduced. Prediction dates are not rejected where calendar evidence is unknown.
- Added focused tests for verified/inferred/unknown evidence, exact cutoff boundary, missing/unsupported dates, and the observation-date cutoff predicate. No season-aware model features or accuracy claims were added.
- Source/evidence gap: obtain a dated official district × exact source-season calendar with explicit validity years and an unambiguous crosswalk to APY season labels. Then define a prediction date and test cutoff enforcement before adding crop-stage features.
- Verification for this pass: 8 focused tests passed (`test_preseason_prediction.py` and `test_leakage_prevention.py`); Python compilation passed for the changed Python modules/tests; `git diff --check` passed with existing line-ending warnings. No network, Earth Engine, MySQL, model training, or official holdout access.

## V3 schema deployment for analytics compatibility — 2026-10-20

- Applied reviewed additive migration `a71f2d9c4e10` to configured MySQL `agriyield_predictor` after confirming the database was at parent revision `4a1a8172253b` and creating a non-empty timestamped `mysqldump` backup at `data/backups/agriyield_predictor_pre_v3_migration_20261019T200535Z.sql` (352,337,620 bytes; dump header verified).
- Post-migration Alembic revision is `a71f2d9c4e10` (head). Read-only schema inspection confirmed the expected v3 columns exist on `unified_training_records`. A GET to the running local `/analytics/` endpoint returned HTTP 200 without a debug traceback.
- The migration adds nullable v3 feature columns and a default-false `satellite_v3_has_data`; it does not import research artifacts, rebuild unified rows, train models, or establish production satellite-feature usage. Existing data/model results were preserved.

## Final data diagnosis and submission verification — 2026-10-20

- Added `data/processed/final_data_diagnosis_20261020T111500Z.md` and read-only staged CSV audit `data/processed/yield_data_audit_20261020T110500Z.json`. The staged 1,376-row CSV has 38 districts, 26 years, one unit tuple, no duplicate district-year-season keys, 10 missing production values, and 14 zero yields. Production/area agrees with the supplied yield within 0.0005 t/ha for all 1,366 comparable rows. These checks do not authenticate the source or historical paddy/rice basis.
- Official documentation establishes rice-equivalent reporting for specific DES handbook years and broad/historical season timing, but not a full provenance chain for this exact CSV or year-applicable district-season cutoff. The target basis and forecast issuance cutoff remain unresolved; output stays explicitly exploratory.
- Read-only production checks found 1,174 unified rows, zero V3 DatasetVersions/features/unified rows/models. The 29 saved research manifests represent 145/208 planned keys (97 partial, 48 no_data, 63 unrepresented). V3 remains research-only; no extraction/import/training was performed.
- Prediction and analytics returned HTTP 200. A no-write pre-season POST rendered the future-year estimate and unknown-calendar warning; ORM persistence was intercepted. No production record was added.
- Fixed test hygiene: `tests/test_crop_calendar.py` no longer queries the default application database; it validates the migration graph offline. Added `scripts/audit_yield_dataset.py` and focused audit tests.
- Verification: full suite `pytest tests -q --basetemp=tmp\pytest_data_diagnosis_20261020` — 102 passed; focused tests — 12 passed; Python compilation and `git diff --check` passed (existing LF/CRLF warnings only). Official holdout was not opened, and no migration, production refresh, model training, or Earth Engine extraction ran.

## Research-grade improvement and modern-season benchmark — 2026-10-22

- Reconciled `data/processed/evaluation_target_cohort_comparison_20261021T030000.md`: production/official-holdout fitting cohorts and seasonal `run_001` include literal Kharif/Whole Year along with modern seasons, but preserve labels; this is potential mixed target granularity, not a literal Kharif-to-Winter relabel. `run_004` and the new feature benchmark use only modern Autumn/Summer/Winter. Earlier `run_001` test years were later used as official-holdout training/tuning history, so they are not globally untouched. The official 2023–25 cohort remains excluded from new selection.
- Added the isolated modern-season feature benchmark protocol/configuration/runner and tests under `data/processed/experiments/modern_season_feature_benchmark_v1/`. The first attempt failed closed because frozen zero-excluded fit counts were one row low; it was preserved without metrics. Corrected v2 completed in `run_20261021T182916Z` after fixing expected counts. Source hash matched; 589 source candidates reconciled to 583 complete exact feature rows; six unmatched Chennai zero-yield rows were logged; three matched zeros were retained in inclusive sensitivity. No official-holdout file access or DB writes occurred.
- Pooled OOF Ridge + history results: inclusive N=321 MAE 0.3659/RMSE 0.4903/R² 0.3948; zero-excluded N=320 MAE 0.3567/RMSE 0.4850/R² 0.3302. This beat the strongest simple previous-year district-season baseline on pooled MAE/RMSE in both arms, but did not win every fold. Soil/weather additions did not consistently help. Findings remain exploratory retrospective source-year evidence; no production model was selected.
- Reconciled cache audit: NASA POWER and SoilGrids point data exist but lack verified season/boundary/cutoff alignment. Satellite remains partial (145 represented job keys, 63 unrepresented, 97 partial, 48 no-data) with an unverified shared Aug–Sep window. No data were downloaded.
- Narrowed source and code comments to avoid asserting a universally verified historical rice/paddy basis or a Kharif/Winter merge. Updated source-overview limitations. No production model, data, DB record, cache, manifest or deployment setting was changed.
- Verification: focused benchmark tests 4 passed; full project suite `.venv\Scripts\python.exe -m pytest -q` — 108 passed in 41.25 seconds using isolated `agriyield_predictor_test`; `git diff --check` passed with line-ending warnings. A live browser/cold-start walk-through was not performed.
- Full evidence, requirement status, output inventory and next blockers: `data/processed/full_research_improvement_20261022T000500.md`.

## Target regime and prior-yield history reconciliation — 2026-10-22

- Added authoritative context from the Government of India MoSPI AISR 2017-18 report: Tamil Nadu introduced Kharif/Rabi season concepts from agricultural year 2017-18 and data were presented season-wise instead of whole-year. This supports an annual/whole-year interpretation of the candidate’s single pre-2017 Kharif rows, but the note is not a data dictionary for this exact APY extract. National DES documentation defines crop year as July–June; candidate-specific year interpretation and historical yield basis/vintage remain to be confirmed.
- Audited prior-yield feature timing and found a v2 benchmark mismatch: history was built from feature-matched rows before sensitivity filtering, so zero-excluded fits still received prior zero targets and source targets without environmental rows were absent from history. Added a separate frozen source-history reconciliation experiment at `data/processed/experiments/source_history_reconciliation_v1/`; original v2 outputs were preserved.
- Corrected fixed Ridge/source-history pooled OOF metrics on identical rows: inclusive N=321 MAE/RMSE/R²=0.3750/0.5141/0.3345; zero-excluded N=320 =0.3604/0.4899/0.3166. Both beat their same-row previous-year district-season baselines on pooled MAE/RMSE, but not in every fold. No model selection or production integration.
- Updated `history.py` documentation to distinguish earlier-label ordering from real publication-time availability. Added a regression test for a missing intervening source year. Source release/vintage dates and target revisions are still unavailable, so prior-yield features remain retrospective-only.
- Focused history tests: 12 passed. Full project suite: 111 passed in 36.17 seconds using isolated `agriyield_predictor_test`. Full report: `data/processed/research_continuation_20261022T001500.md`.
