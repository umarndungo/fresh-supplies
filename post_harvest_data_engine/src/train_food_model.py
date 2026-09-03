"""
Retrain the post-harvest spoilage model on the FOOD grouping, enriched with
market pricing, and emit a scored dataset coupling spoilage probability with
the recommended (highest-price) market for every shipment.

Outputs (data/processed/food/):
  - food_predictive_models.joblib   (trained model + feature metadata)
  - food_scored.csv                 (shipments + spoilage_prob + risk_tier)
"""

from pathlib import Path
import math

import joblib
import pandas as pd

from src.grouping import PROCESSED_DIR
from src.predictive_models import PredictiveModels, _build_realistic_spoilage


def haversine_km(lat1, lon1, lat2, lon2):
    """Great-circle distance between two lat/lon points in kilometres."""
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def engineer_food_features(df):
    """Adds market distance + thermal exposure so the model couples route risk
    to destination."""
    df = _build_realistic_spoilage(df.copy())

    # Distance from shipment location to its best (highest-price) market
    has_coords = {"latitude", "longitude", "best_market_lat", "best_market_lon"}.issubset(df.columns)
    df["Distance_To_Market_Km"] = 0.0
    if has_coords:
        df["Distance_To_Market_Km"] = df.apply(
            lambda r: haversine_km(
                r["latitude"], r["longitude"], r["best_market_lat"], r["best_market_lon"]
            ),
            axis=1,
        )
    return df


def train_food_model():
    food_dir = PROCESSED_DIR / "food"
    src = food_dir / "food_market_annotated.csv"
    if not src.exists():
        raise FileNotFoundError(f"Missing FOOD market-annotated dataset: {src}")

    df = pd.read_csv(src)
    df = engineer_food_features(df)

    pm = PredictiveModels()
    X, y = pm.prepare_features(df)
    pm.train_and_evaluate(X, y)
    pm.get_feature_importance()

    # Score every shipment
    proba = pm.predict_proba(X)
    pred, _, tiers = pm.predict(X, threshold=0.5)
    df["spoilage_prob"] = proba
    df["spoilage_prediction"] = pred
    df["risk_tier"] = tiers

    model_out = food_dir / "food_predictive_models.joblib"
    scored_out = food_dir / "food_scored.csv"
    joblib.dump(
        {"model": pm, "feature_names": pm.feature_names},
        model_out,
    )

    # Standalone inference bundle for the FastAPI backend: a pure scikit-learn
    # RandomForestClassifier (no xgboost/imblearn/shap deps) so the API can
    # unpickle it without the heavy data-engine stack.
    from sklearn.ensemble import RandomForestClassifier

    rf_clf = RandomForestClassifier(
        n_estimators=200, max_depth=12, random_state=pm.random_state, n_jobs=-1
    )
    rf_clf.fit(X, y)
    inference_out = food_dir / "food_model_inference.joblib"
    joblib.dump(
        {"classifier": rf_clf, "feature_names": pm.feature_names, "model_name": "rf"},
        inference_out,
    )
    print(f"[Train] Saved standalone sklearn inference bundle -> {inference_out}")

    df.to_csv(scored_out, index=False)

    print(f"[Train] Saved model -> {model_out}")
    print(f"[Train] Saved scored FOOD dataset -> {scored_out}")
    print(f"[Train] Spoiled rate: {int(y.sum())}/{len(y)} ({y.mean()*100:.1f}%)")
    return pm, df


if __name__ == "__main__":
    train_food_model()
