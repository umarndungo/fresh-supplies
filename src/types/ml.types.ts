export type RiskTier = "Fresh" | "At-Risk" | "Critical";

export interface SpoilageRequest {
  crop_type: string;
  latitude: number;
  longitude: number;
  Temperature_C: number;
  Transit_Duration_Hr: number;
  Pressure_PSI: number;
  baseline_loss_pct: number;
  quantity_kg: number;
}

export interface MarketRecommendationRequest extends SpoilageRequest {
  top_n: number;
}

export interface SuspicionOut {
  spoilage_probability: number;
  risk_tier: RiskTier;
  spoil_prediction: boolean;
}

export interface MarketRecommendationOut {
  market_id: string;
  market_name: string;
  region: string;
  distance_km: number;
  price_per_kg: number;
  spoilage_probability: number;
  revenue_retained: number;
}