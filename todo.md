# AgriYield Predictor — current status and remaining work (2026-10-19)

## Completed in this follow-up

- Verified APY season labels against official Tamil Nadu DES reports: Autumn = Kar/Kuruvai/Sornavari, Winter = Samba/Thaladi/Pishanam, Summer = Navarai/Kodai. State area and production totals match exactly for 2020-21 through 2022-23. Historical Kharif remains an unmapped category.
- Added canonical season encoding to models and prediction/scenario/explainability inputs; same-season yield history and baselines now use matching seasons.
- Expanded the unified table to 1,174 records and 1,169 non-null yield targets; retrained all 14 supported app models. Earlier models and result batches were retained.
- Downloaded the official DES 2023-24 and 2024-25 reports and extracted 228 district-season rows (222 positive targets) into a separate holdout CSV. No holdout targets were added to training.
- Corrected six official-report spelling variants and evaluated all 222 positive holdout rows. RF: MAE 0.397 t/ha, RMSE 0.522, R² -0.043. XGBoost: MAE 0.411, RMSE 0.521, R² -0.040. Historical district-season baseline MAE 0.433. Results are in `data/processed/official_holdout_20261019T095931.jsonl`.
- The pre-existing chronological CV batch `20261018T191913` / `20261018191913` remains preserved. The completed season-aware expanding-window CV batch `20261019T092852` contains 26 rows. Best pooled temporal result: `soil_weather_rich_history` + XGBoost, R² 0.393 and MAE 0.524 t/ha (23 folds); fold wins over district-mean baseline: 15/23. This is a research candidate, not a production selection.
- A refreshed spatial-validation run was started on the 1,174-row cohort and safely interrupted during richer-weather evaluation after 7 configurations completed. Its append-only partial artifact is `data/processed/spatial_validation_20261019T102542.jsonl`; it has no completion record and must not be presented as a complete batch. Completed RF pooled spatial R² values: soil 0.132, weather 0.240, satellite 0.183 (4 folds only), soil+weather 0.213, soil+satellite 0.189 (4 folds), weather+satellite 0.271 (4 folds), soil+weather+satellite 0.259 (4 folds). History configurations were explicitly skipped. No Python validation process is currently running.

## Next steps

1. Resume spatial validation selectively for `weather_rich_only`, `weather_rich_history` (expected skip), and `soil_weather_rich_history` (expected skip) only if the district CV method can correctly represent the history features; otherwise develop a separate history-aware spatial split design. Keep this separate from the interrupted artifact; never append to or overwrite it.
2. Inspect the 26 CV result rows, fold distributions, and district-season errors, especially 2024-25 Samba/Thaladi, and reconcile seasonal validation coverage.
3. Obtain provenance and historical yield-basis documentation for the uploaded APY source and verified rice-area masks with explicit licenses. Build validated season-specific crop-stage weather/satellite inputs and availability cutoffs before forecasting claims.
4. Do not select a production model yet. Temporal CV scores are moderate and the untouched two-year official holdout has negative R²; present current models as exploratory.

## Limitations that still need data or calendar work

- Kharif through 2016-17 has no verified mapping to the modern three season groups. Keep it distinct.
- Weather and Sentinel features are still fixed Aug 1–Sep 30 values. For each source season, build verified district crop-stage windows and define the intended forecast cutoff so only information available by that date is used.
- The same annual fixed-window weather/satellite values are repeated across multiple seasonal target rows. Current satellite row coverage therefore overstates independent season-specific coverage; it is not 39% crop-stage coverage.
- Sentinel coverage remains sparse (v2 has values on 172/765 pre-expansion district-year rows) and has no rice-specific mask. Obtain a clearly licensed Tamil Nadu rice-area mask, then aggregate imagery over rice areas and report coverage by district/year/season.
- The official 2023-25 holdout contains yield targets only; no matching future-year weather or satellite features are available in a verified season-aligned form. It validates the soil/season baseline and models, not weather/satellite configurations.
- The originally uploaded APY CSV still lacks its source URL and full historical yield-basis metadata. Newer DES reports specify rice-equivalent production, but that alone does not prove every historic observation's provenance.

## Reproducibility and product readiness

- Record source release, license, retrieval date, and extraction script for every new feature/target dataset.
- Preserve the original CV batch and earlier spatial JSONL artifacts. The new official report PDFs and extracted CSV are additive under `data/raw/`.
- Review prediction/report/CSV exports after retraining; keep retrospective estimates and hypothetical scenarios labeled separately from forecasts.
- Do not present any model as a reliable pre-harvest forecast until crop-stage features and an intended forecast date are implemented and independently validated.
