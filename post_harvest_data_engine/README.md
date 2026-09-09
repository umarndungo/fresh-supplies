# Fresh Supplies Data Engine

The data engine builds the agricultural supply-chain analytics used by Fresh
Supplies. It combines local FAOSTAT baselines with deterministic synthetic
telemetry, engineers thermal and route-risk features, trains spoilage models,
and ranks market destinations by expected revenue retained.

## Setup

```bash
cd post_harvest_data_engine
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Run the pipeline

```bash
.venv/bin/python main.py
```

The pipeline writes grouped datasets under `data/processed/`. Telemetry includes
temperature, humidity, rainfall intensity, GPS, speed, route distance, stopover
duration, transit duration, and vehicle category.

## Train models

```bash
.venv/bin/python -m src.train_food_model
```

This trains the classification models and writes:

- `data/processed/food/food_predictive_models.joblib`
- `data/processed/food/food_model_inference.joblib`
- `data/processed/food/food_scored.csv`
- `data/processed/food/food_regression_metrics.json`

The classification path reports ROC-AUC for Random Forest and XGBoost. The
continuous-loss path compares linear regression, Random Forest regression, and
XGBoost regression using RMSE, MAE, and R².

## Test

```bash
.venv/bin/pytest -q
```

The suite covers model leakage, artifact compatibility, crop coverage, market
ranking, route comparison, climate/logistics schema, and FreshOps operational
reports.

## Dashboard

```bash
.venv/bin/streamlit run explainer_dashboard.py
```

The `6 · Evaluation` view shows continuous regression metrics and a deterministic
baseline-versus-spoilage-aware route comparison.

## Interpretation and limitations

- The generated telemetry and market prices are synthetic and deterministic.
- The spoilage target is a realistic simulated target, not observed arrival-loss
	ground truth.
- The route benchmark demonstrates scoring logic; it does not prove a 15–25%
	transport reduction on real operations.
- CHIRTS raster support exists for heat-risk sampling, but CHIRPS rainfall and
	ERA5 daily data are not yet an end-to-end production ingestion source.
- Model artifacts are currently overwritten on retraining; versioned artifact
	storage remains future work.
