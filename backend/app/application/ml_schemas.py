from typing import Optional

from pydantic import BaseModel, Field


class SpoilageRequest(BaseModel):
    crop_type: str = Field(..., description="Crop name, e.g. Avocados")
    latitude: float = Field(..., description="Shipment origin latitude")
    longitude: float = Field(..., description="Shipment origin longitude")
    Temperature_C: float = Field(25.0, ge=-20, le=60)
    Transit_Duration_Hr: float = Field(4.0, ge=0, le=120)
    Pressure_PSI: float = Field(30.0)
    baseline_loss_pct: float = Field(10.0, ge=0, le=100)
    quantity_kg: float = Field(100.0, gt=0)


class MarketRecommendationRequest(SpoilageRequest):
    top_n: int = Field(5, ge=1, le=20)


class SuspicionOut(BaseModel):
    spoilage_probability: float
    risk_tier: str
    spoil_prediction: bool


class MarketRecommendationOut(BaseModel):
    market_id: str
    market_name: str
    region: str
    distance_km: float
    price_per_kg: float
    spoilage_probability: float
    revenue_retained: float
