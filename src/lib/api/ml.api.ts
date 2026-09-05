import { apiClient } from "@/lib/api/client";
import { API_ENDPOINTS } from "@/lib/api/endpoints";
import type { ApiSuccessResponse } from "@/types/api.types";
import type { SpoilageRequest, SuspicionOut, MarketRecommendationRequest, MarketRecommendationOut } from "@/types/ml.types";

export async function predictSpoilageRequest(payload: SpoilageRequest): Promise<SuspicionOut> {
  const { data } = await apiClient.post<ApiSuccessResponse<SuspicionOut>>(API_ENDPOINTS.ml.predictSpoilage, payload);
  return data.data;
}

export async function recommendMarketRequest(payload: MarketRecommendationRequest): Promise<MarketRecommendationOut[]> {
  const { data } = await apiClient.post<ApiSuccessResponse<MarketRecommendationOut[]>>(API_ENDPOINTS.ml.recommendMarket, payload);
  return data.data;
}