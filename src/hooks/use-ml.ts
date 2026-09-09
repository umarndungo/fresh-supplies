"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { toast } from "sonner";
import {
  fetchEvaluationSummaryRequest,
  predictSpoilageRequest,
  recommendMarketRequest,
} from "@/lib/api/ml.api";
import { ApiError } from "@/lib/api/api-error";
import type {
  EvaluationSummary,
  SpoilageRequest,
  SuspicionOut,
  MarketRecommendationRequest,
  MarketRecommendationOut,
} from "@/types/ml.types";

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

export function useEvaluationSummary() {
  return useQuery<EvaluationSummary, ApiError>({
    queryKey: ["ml", "evaluation-summary"],
    queryFn: fetchEvaluationSummaryRequest,
    staleTime: 5 * 60 * 1000,
  });
}