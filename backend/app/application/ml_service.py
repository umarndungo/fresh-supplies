"""Machine Learning inference service.

Loads the trained spoilage model + market pricing from the data engine's FOOD
grouping and exposes predictions and market recommendations. Kept deliberately
light: it only depends on joblib/pandas/numpy/sklearn and the saved artifacts.
"""

from functools import lru_cache
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from app.core.config import settings


class MLServiceError(Exception):
    pass


def load_evaluation_summary() -> dict:
    """Load synthetic model metrics and the deterministic route benchmark."""
    model_path = Path(settings.ML_MODEL_PATH)
    metrics_path = model_path.parent / "food_regression_metrics.json"
    if not metrics_path.exists():
        raise MLServiceError(
            f"Evaluation metrics not found at {metrics_path.resolve()}. "
            "Run post_harvest_data_engine train_food_model first."
        )

    regression = json.loads(metrics_path.read_text())
    classification_path = model_path.parent / "food_classification_metrics.json"
    if not classification_path.exists():
        raise MLServiceError(
            f"Classification metrics not found at {classification_path.resolve()}. "
            "Run post_harvest_data_engine train_food_model first."
        )
    classification = json.loads(classification_path.read_text())
    classification = {
        name: {"roc_auc": round(float(metrics["roc_auc"]), 4)}
        for name, metrics in classification.items()
    }

    # Deterministic demonstration: static shortest-time route versus the
    # spoilage-aware route used by the data engine's evaluation benchmark.
    baseline_hours = 4.0
    optimized_hours = 8.0
    baseline_spoilage = 24.0
    optimized_spoilage = 2.0
    baseline_revenue = 100.0 * 60.0 * (1.0 - baseline_spoilage / 100.0)
    optimized_revenue = 100.0 * 60.0 * (1.0 - optimized_spoilage / 100.0)

    return {
        "data_source": "synthetic",
        "field_validated": False,
        "classification": classification,
        "regression": {
            name: {metric: round(float(value), 4) for metric, value in metrics.items()}
            for name, metrics in regression.items()
        },
        "best_classification_model": (
            max(classification, key=lambda name: classification[name]["roc_auc"])
            if classification else None
        ),
        "best_regression_model": min(
            regression, key=lambda name: regression[name]["rmse"]
        ) if regression else None,
        "route_evaluation": {
            "transit_time_reduction_pct": round(
                (baseline_hours - optimized_hours) / baseline_hours * 100.0, 4
            ),
            "spoilage_reduction_pct": round(
                baseline_spoilage - optimized_spoilage, 4
            ),
            "revenue_retention_change_pct": round(
                (optimized_revenue - baseline_revenue) / baseline_revenue * 100.0,
                4,
            ),
        },
        "limitations": [
            "Metrics are based on synthetic data.",
            "Results are not field validated.",
            "Route improvements are a deterministic benchmark, not observed operations.",
        ],
    }


@lru_cache
def load_model_bundle() -> dict:
    """Loads the saved standalone inference bundle (sklearn classifier + features)."""
    path = Path(settings.ML_MODEL_PATH)
    if not path.exists():
        raise MLServiceError(
            f"Model artifacts not found at {path.resolve()}. "
            "Run post_harvest_data_engine train_food_model first."
        )
    try:
        return joblib.load(path)
    except Exception as exc:
        raise MLServiceError(
            "The ML inference artifact could not be loaded. "
            "Rebuild the backend with the pinned ML dependencies and refresh the "
            "Git LFS artifact."
        ) from exc


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


def _normalize_crop(name: str) -> str:
    """Lowercases and strips a trailing plural 's' for tolerant matching."""
    name = name.strip().lower()
    return name[:-1] if name.endswith("s") else name


def _match_crop(crop: str, available_crops: list[str]) -> str | None:
    """Finds the canonical crop name in the price table.

    The price table stores plural display names (e.g. "Bananas", "Mangoes")
    while shipment produce types are user-entered ("Banana", "Bananas", ...).
    Match case- and plural-insensitively, then fall back to fuzzy matching for
    typos so /ml/recommend-market does not 422 on legitimate crops.
    """
    import difflib

    target = _normalize_crop(crop)
    for name in available_crops:
        if _normalize_crop(name) == target:
            return name
    close = difflib.get_close_matches(target, [_normalize_crop(n) for n in available_crops], n=1, cutoff=0.6)
    if close:
        for name in available_crops:
            if _normalize_crop(name) == close[0]:
                return name
    return None


def recommend_market(shipment: dict, top_n: int = 5) -> list:
    """Ranks markets for a shipment by revenue retained (spoilage x price)."""
    bundle = load_model_bundle()
    model = bundle["classifier"]
    feature_names = bundle["feature_names"]
    prices = load_market_prices()

    crop = shipment.get("crop_type")
    matched_crop = _match_crop(crop, prices["crop"].unique().tolist()) if crop else None
    if matched_crop is None:
        raise MLServiceError(f"No market prices found for crop: {crop}")

    crop_prices = prices[prices["crop"] == matched_crop]

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
