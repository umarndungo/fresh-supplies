"""Machine Learning inference service.

Loads the trained spoilage model + market pricing from the data engine's FOOD
grouping and exposes predictions and market recommendations. Kept deliberately
light: it only depends on joblib/pandas/numpy/sklearn and the saved artifacts.
"""

from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from app.core.config import settings


class MLServiceError(Exception):
    pass


@lru_cache
def load_model_bundle() -> dict:
    """Loads the saved standalone inference bundle (sklearn classifier + features)."""
    path = Path(settings.ML_MODEL_PATH)
    if not path.exists():
        raise MLServiceError(
            f"Model artifacts not found at {path.resolve()}. "
            "Run post_harvest_data_engine train_food_model first."
        )
    return joblib.load(path)


@lru_cache
def load_market_prices() -> pd.DataFrame:
    """Loads the market prices table (price per crop per market)."""
    path = Path(settings.ML_MARKET_PRICES_PATH)
    if not path.exists():
        raise MLServiceError(f"Market prices not found at {path.resolve()}.")
    return pd.read_csv(path)


def _feature_vector(feature_names, shipment: dict, distance_km: float, price: float) -> np.ndarray:
    thermal = max(0.0, shipment.get("Temperature_C", 25.0) - 25.0) * shipment.get(
        "Transit_Duration_Hr", 4.0
    )
    idx = {name: i for i, name in enumerate(feature_names)}
    vec = np.zeros(len(feature_names))
    mapping = {
        "Temperature_C": shipment.get("Temperature_C", 25.0),
        "Pressure_PSI": shipment.get("Pressure_PSI", 30.0),
        "Transit_Duration_Hr": shipment.get("Transit_Duration_Hr", 4.0),
        "baseline_loss_pct": shipment.get("baseline_loss_pct", 10.0),
        "Thermal_Heat_Exposure": thermal,
        "Distance_To_Market_Km": distance_km,
        "price_per_kg": price,
    }
    for name, value in mapping.items():
        if name in idx:
            vec[idx[name]] = value
    return vec


def predict_spoilage(shipment: dict) -> dict:
    """Predicts spoilage probability and risk tier for a single shipment."""
    bundle = load_model_bundle()
    model = bundle["classifier"]
    feature_names = bundle["feature_names"]

    distance_km = shipment.get("Distance_To_Market_Km", 40.0)
    price = shipment.get("price_per_kg", 100.0)
    vec = _feature_vector(feature_names, shipment, distance_km, price)
    frame = pd.DataFrame([vec], columns=feature_names)

    proba = float(model.predict_proba(frame)[0][1])
    tier = "CRITICAL" if proba >= 0.6 else ("AT_RISK" if proba >= 0.35 else "FRESH")
    return {
        "spoilage_probability": round(proba, 4),
        "risk_tier": tier,
        "spoil_prediction": bool(proba >= 0.5),
    }


def recommend_market(shipment: dict, top_n: int = 5) -> list:
    """Ranks markets for a shipment by revenue retained (spoilage x price)."""
    bundle = load_model_bundle()
    model = bundle["classifier"]
    feature_names = bundle["feature_names"]
    prices = load_market_prices()

    crop = shipment.get("crop_type")
    crop_prices = prices[prices["crop"] == crop]
    if crop_prices.empty:
        raise MLServiceError(f"No market prices found for crop: {crop}")

    quantity_kg = float(shipment.get("quantity_kg", 100.0))
    rankings = []
    for _, mkt in crop_prices.iterrows():
        distance_km = _haversine(
            shipment["latitude"], shipment["longitude"], mkt["market_lat"], mkt["market_lon"]
        )
        vec = _feature_vector(
            feature_names, shipment, distance_km, mkt["price_per_kg"]
        )
        frame = pd.DataFrame([vec], columns=feature_names)
        proba = float(model.predict_proba(frame)[0][1])
        revenue = quantity_kg * mkt["price_per_kg"] * (1.0 - proba)
        rankings.append(
            {
                "market_id": mkt["market_id"],
                "market_name": mkt["market_name"],
                "region": mkt["region"],
                "distance_km": round(distance_km, 1),
                "price_per_kg": mkt["price_per_kg"],
                "spoilage_probability": round(proba, 3),
                "revenue_retained": round(revenue, 2),
            }
        )

    rankings.sort(key=lambda r: r["revenue_retained"], reverse=True)
    return rankings[:top_n]


def _haversine(lat1, lon1, lat2, lon2) -> float:
    import math

    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))
