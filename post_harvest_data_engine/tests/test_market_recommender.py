"""Market pricing + recommender tests.

These guard the revenue-ranking logic used by the /ml/recommend-market endpoint
and the pipeline's best_market column: prices are sane, ranking is descending by
revenue retained, and the model-coupled recommender returns finite, sorted
results.
"""

import pandas as pd
import joblib
import numpy as np

from src.crops import CROP_NAMES
from src.market_pricing import generate_market_prices, rank_markets
from src.optimization import (
    estimate_revenue_retained,
    recommend_market_for_shipment,
    recommend_market_destinations,
    build_friction_score,
)

FOOD_DIR = "data/processed/food"
MARKETS_N = 10


def test_market_prices_cover_all_crops():
    prices = generate_market_prices()
    assert set(prices["crop"]) == set(CROP_NAMES)
    assert prices["market_id"].nunique() >= MARKETS_N
    assert (prices["price_per_kg"] > 0).all()


def test_rank_markets_sorted_desc_by_revenue():
    prices = generate_market_prices()
    ranked = rank_markets("Tomatoes", prices, spoilage_pct=10.0, top_n=5)
    assert len(ranked) == 5
    assert list(ranked["revenue_retained"]) == sorted(
        ranked["revenue_retained"], reverse=True
    )


def test_saved_market_prices_all_crops_and_markets():
    saved = pd.read_csv(f"{FOOD_DIR}/market_prices.csv")
    assert set(saved["crop"]) == set(CROP_NAMES)
    assert saved["market_id"].nunique() >= MARKETS_N


def test_revenue_retained_monotonic_and_nonnegative():
    a = estimate_revenue_retained(100.0, 60.0, 0.0)   # no spoilage
    b = estimate_revenue_retained(100.0, 60.0, 25.0)  # some spoilage
    c = estimate_revenue_retained(100.0, 60.0, 99.0)  # nearly all lost
    assert a >= b >= c >= 0.0


def test_friction_score_finite_monotonic():
    short = build_friction_score(10.0, 2.0, 1.0, 22.0)
    long = build_friction_score(100.0, 20.0, 5.0, 35.0)
    assert np.isfinite(short) and np.isfinite(long)
    assert long > short


def test_recommend_market_destinations_ranks_top_n():
    graph = {
        "edges": [
            {"from": "origin", "to": "m1", "distance_km": 10, "transit_hours": 2, "temp_c": 22, "spoilage_risk": 1},
            {"from": "origin", "to": "m2", "distance_km": 90, "transit_hours": 15, "temp_c": 34, "spoilage_risk": 6},
            {"from": "origin", "to": "m3", "distance_km": 40, "transit_hours": 6, "temp_c": 28, "spoilage_risk": 3},
        ]
    }
    prices_lookup = {"m1": 100.0, "m2": 40.0, "m3": 70.0}
    out = recommend_market_destinations(
        graph, "origin", prices_lookup=prices_lookup, top_n=2
    )
    assert len(out) == 2
    revs = [r["revenue_retained_per_100kg"] for r in out]
    assert revs == sorted(revs, reverse=True)


def test_recommend_market_for_shipment_real_model():
    """End-to-end: trained model + saved market prices yield a sane ranking."""
    bundle = joblib.load(f"{FOOD_DIR}/food_predictive_models.joblib")
    prices = pd.read_csv(f"{FOOD_DIR}/market_prices.csv")

    shipment = {
        "crop_type": "Tomatoes",
        "latitude": -1.29,
        "longitude": 36.82,
        "Temperature_C": 30.0,
        "Shift": "Afternoon",
        "Pressure_PSI": 30.0,
        "Transit_Duration_Hr": 8.0,
        "quantity_kg": 100.0,
    }
    out = recommend_market_for_shipment(shipment, bundle, prices, top_n=5)
    assert len(out) == 5
    assert all(r["revenue_retained"] > 0 for r in out)
    assert all(np.isfinite(r["revenue_retained"]) for r in out)
    assert all(0.0 <= r["spoilage_prob"] <= 1.0 for r in out)
    revs = [r["revenue_retained"] for r in out]
    assert revs == sorted(revs, reverse=True)
    assert all(r["market_id"] for r in out)
