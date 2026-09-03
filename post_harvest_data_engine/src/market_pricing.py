"""
Market pricing & destination intelligence for the FOOD grouping.

Produces a market destinations table (East African markets with coordinates)
and current wholesale prices per crop, then ranks markets by revenue retained
(= quantity x price x (1 - spoilage%)) so stakeholders know where to sell.

Prices are synthetic (real public sources do not cover the horticulture crops
in our FOOD grouping) but calibrated to realistic Kenyan wholesale levels.
"""

from pathlib import Path

import numpy as np
import pandas as pd

# East African marketplace destinations with approximate coordinates (Kenya focus).
MARKET_DESTINATIONS = [
    # (market_id, name, lat, lon, region)
    ("MKT_NAI", "Nairobi Gikomba Market", -1.2864, 36.8300, "Nairobi"),
    ("MKT_NKU", "Nakuru Wakulima Market", -0.3031, 36.0800, "Nakuru"),
    ("MKT_KIS", "Kisumu Open Air Market", -0.0917, 34.7680, "Kisumu"),
    ("MKT_MOM", "Mombasa Kongowea Market", -4.0435, 39.6682, "Mombasa"),
    ("MKT_ELD", "Eldoret Market", 0.5143, 35.2698, "Uasin Gishu"),
    ("MKT_THK", "Thika Market", -1.0333, 37.0693, "Kiambu"),
    ("MKT_KSM-K", "Kakamega Municipal Market", 0.2833, 34.7500, "Kakamega"),
    ("MKT_MER", "Meru Market", 0.0500, 37.6500, "Meru"),
    ("MKT_NKR-NSR", "Naivasha Market", -0.7172, 36.4312, "Naivasha"),
    ("MKT_BOM", "Bomet Market", -0.7800, 35.3400, "Bomet"),
]

# Base wholesale prices (KES per kg) per FOOD crop, from the single source of
# truth (config/crops.yaml). Higher margin crops fetch more.
from src.crops import CROP_BASE_PRICE_KES  # noqa: E402 (canonical prices)

# Regional price variation multipliers (%), simulating scarcity/premiums by market.
REGION_VARIATION = {
    "Nairobi": 1.12,
    "Mombasa": 1.08,
    "Nakuru": 1.02,
    "Kisumu": 1.00,
    "Uasin Gishu": 0.98,
    "Kiambu": 1.05,
    "Kakamega": 0.97,
    "Meru": 0.95,
    "Naivasha": 1.00,
    "Bomet": 0.96,
}


def _normalise_crop(crop: str) -> str:
    """Maps a crop name to the canonical key used in price tables."""
    return str(crop).strip()


def generate_market_destinations() -> pd.DataFrame:
    """Returns the market destinations table (id, name, lat, lon, region)."""
    return pd.DataFrame(
        MARKET_DESTINATIONS,
        columns=["market_id", "market_name", "market_lat", "market_lon", "region"],
    )


def generate_market_prices(crops: list[str] | None = None) -> pd.DataFrame:
    """Returns current wholesale price (KES/kg) per crop per market.

    Columns: market_id, market_name, region, crop, price_per_kg, market_lat, market_lon.
    """
    np.random.seed(7)
    if crops is None:
        crops = list(CROP_BASE_PRICE_KES.keys())
    crops = [_normalise_crop(c) for c in crops]

    destinations = generate_market_destinations()
    rows = []
    for _, mkt in destinations.iterrows():
        mult = REGION_VARIATION.get(mkt["region"], 1.0)
        for crop in crops:
            base = CROP_BASE_PRICE_KES.get(crop, 60.0)
            # deterministic-ish per-crop jitter + regional multiplier
            jitter = np.random.uniform(-0.08, 0.08)
            price = max(10.0, round(base * mult * (1 + jitter), 2))
            rows.append(
                {
                    "market_id": mkt["market_id"],
                    "market_name": mkt["market_name"],
                    "region": mkt["region"],
                    "market_lat": mkt["market_lat"],
                    "market_lon": mkt["market_lon"],
                    "crop": crop,
                    "price_per_kg": price,
                }
            )
    return pd.DataFrame(rows)


def attach_market_prices(
    shipments: pd.DataFrame,
    prices: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Joins market price info onto a shipment dataset (rows = shipments).

    For each shipment's crop, attaches the best available market price and the
    recommended (highest-price) market id for that crop.

    Returns a copy of shipments with columns:
      price_per_kg, best_market_id, best_market_name, best_market_region,
      best_market_price, best_market_lat, best_market_lon, revenue_per_100kg
    """
    if prices is None:
        prices = generate_market_prices()

    result = shipments.copy()
    if "crop_type" not in result.columns:
        raise ValueError("shipments must contain a 'crop_type' column")

    # recommended (best-price) market per crop
    best = (
        prices.loc[prices.groupby("crop")["price_per_kg"].idxmax()]
        .set_index("crop")
    )
    result["price_per_kg"] = result["crop_type"].map(
        dict(zip(prices["crop"], prices["price_per_kg"]))
    )
    result["best_market_id"] = result["crop_type"].map(best["market_id"].to_dict())
    result["best_market_name"] = result["crop_type"].map(best["market_name"].to_dict())
    result["best_market_region"] = result["crop_type"].map(best["region"].to_dict())
    result["best_market_price"] = result["crop_type"].map(best["price_per_kg"].to_dict())
    result["best_market_lat"] = result["crop_type"].map(best["market_lat"].to_dict())
    result["best_market_lon"] = result["crop_type"].map(best["market_lon"].to_dict())
    result["revenue_per_100kg"] = result["best_market_price"] * 100.0
    return result


def rank_markets(
    crop: str,
    prices: pd.DataFrame | None = None,
    spoilage_pct: float = 10.0,
    quantity_kg: float = 100.0,
    top_n: int = 5,
) -> pd.DataFrame:
    """Ranks markets for a given crop by revenue retained.

    revenue_retained = quantity x price x (1 - spoilage%)
    """
    if prices is None:
        prices = generate_market_prices()

    crop_prices = prices[prices["crop"] == _normalise_crop(crop)].copy()
    if crop_prices.empty:
        return pd.DataFrame()

    crop_prices["revenue_retained"] = (
        quantity_kg * crop_prices["price_per_kg"] * (1.0 - spoilage_pct / 100.0)
    )
    crop_prices["spoilage_pct"] = spoilage_pct
    crop_prices = crop_prices.sort_values("revenue_retained", ascending=False).head(top_n)
    return crop_prices[
        [
            "market_id", "market_name", "region", "price_per_kg",
            "spoilage_pct", "revenue_retained",
        ]
    ].reset_index(drop=True)


def write_market_outputs(
    food_merged: pd.DataFrame,
    food_dir: Path,
) -> None:
    """Writes market destinations, prices, and annotated FOOD shipments to disk."""
    destinations = generate_market_destinations()
    prices = generate_market_prices()

    food_dir.mkdir(parents=True, exist_ok=True)
    destinations.to_csv(food_dir / "market_destinations.csv", index=False)
    prices.to_csv(food_dir / "market_prices.csv", index=False)

    annotated = attach_market_prices(food_merged, prices)
    annotated.to_csv(food_dir / "food_market_annotated.csv", index=False)
    print(f"[Market] wrote market_destinations.csv, market_prices.csv, food_market_annotated.csv -> {food_dir}")
    return annotated


if __name__ == "__main__":
    prices = generate_market_prices()
    print(prices.head(12).to_string(index=False))
    print()
    print("=== Market ranking for Tomatoes (10% spoilage) ===")
    print(rank_markets("Tomatoes", prices).to_string(index=False))
