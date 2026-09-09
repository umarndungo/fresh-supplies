import { apiClient } from "@/lib/api/client";
import { API_ENDPOINTS } from "@/lib/api/endpoints";
import type {
  SpoilageRequest,
  SuspicionOut,
  MarketRecommendationRequest,
  MarketRecommendationOut,
  EvaluationSummary,
  RiskTier,
} from "@/types/ml.types";

// The /ml endpoints (unlike the rest of the API) return the payload bare, not
// wrapped in { data: ... } - confirmed by backend/tests/test_ml_api.py.
export async function predictSpoilageRequest(payload: SpoilageRequest): Promise<SuspicionOut> {
  const { data } = await apiClient.post<SuspicionOut>(API_ENDPOINTS.ml.predictSpoilage, payload);
  return {
    ...data,
    risk_tier: normalizeRiskTier(data.risk_tier),
  };
}

export async function recommendMarketRequest(payload: MarketRecommendationRequest): Promise<MarketRecommendationOut[]> {
  const { data } = await apiClient.post<MarketRecommendationOut[]>(API_ENDPOINTS.ml.recommendMarket, payload);
  return data;
}

export async function fetchEvaluationSummaryRequest(): Promise<EvaluationSummary> {
  const { data } = await apiClient.get<EvaluationSummary>(API_ENDPOINTS.ml.evaluationSummary);
  return data;
}

function normalizeRiskTier(value: string): RiskTier {
  if (value === "FRESH") return "Fresh";
  if (value === "AT_RISK") return "At-Risk";
  if (value === "CRITICAL") return "Critical";
  return value as RiskTier;
}