"use client";

import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import { predictSpoilageRequest, recommendMarketRequest } from "@/lib/api/ml.api";
import { ApiError } from "@/lib/api/api-error";
import type { SpoilageRequest, SuspicionOut, MarketRecommendationRequest, MarketRecommendationOut } from "@/types/ml.types";

export function usePredictSpoilage() {
  return useMutation<SuspicionOut, ApiError, SpoilageRequest>({
    mutationFn: (payload: SpoilageRequest) => predictSpoilageRequest(payload),
    onError: (error) => {
      toast.error(error instanceof ApiError ? error.message : "Unable to predict spoilage.");
    },
  });
}

export function useRecommendMarket() {
  return useMutation<MarketRecommendationOut[], ApiError, MarketRecommendationRequest>({
    mutationFn: (payload: MarketRecommendationRequest) => recommendMarketRequest(payload),
    onError: (error) => {
      toast.error(error instanceof ApiError ? error.message : "Unable to get market recommendations.");
    },
  });
}