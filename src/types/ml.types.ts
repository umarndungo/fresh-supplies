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

export interface EvaluationModelMetrics {
  rmse?: number;
  mae?: number;
  r2?: number;
  roc_auc?: number;
}

export interface RouteEvaluationSummary {
  transit_time_reduction_pct: number;
  spoilage_reduction_pct: number;
  revenue_retention_change_pct: number;
}

export interface EvaluationSummary {
  data_source: "synthetic" | "real" | string;
  field_validated: boolean;
  classification: Record<string, EvaluationModelMetrics>;
  regression: Record<string, EvaluationModelMetrics>;
  best_classification_model: string | null;
  best_regression_model: string | null;
  route_evaluation: RouteEvaluationSummary;
  limitations: string[];
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