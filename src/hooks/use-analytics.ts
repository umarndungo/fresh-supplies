"use client";

import { useQuery } from "@tanstack/react-query";
import { recommendMarketRequest } from "@/lib/api/ml.api";
import type { Shipment } from "@/types/shipment.types";
import type { MarketRecommendationOut } from "@/types/ml.types";

function buildMarketRequest(shipment: Shipment) {
  return {
    crop_type: shipment.produceType,
    latitude: shipment.latitude ?? -1.2921,
    longitude: shipment.longitude ?? 36.8219,
    Temperature_C: shipment.temperatureC ?? 25,
    Transit_Duration_Hr: shipment.transitDurationHr ?? 4,
    Pressure_PSI: shipment.pressurePsi ?? 30,
    baseline_loss_pct: shipment.baselineLossPct ?? 10,
    quantity_kg: shipment.quantityKg ?? 100,
    top_n: 1,
  };
}

export function useAllMarketRecommendations(shipments: Shipment[]) {
  const shipmentsWithLocation = shipments.filter((s) => s.latitude && s.longitude);

  return useQuery({
    queryKey: ["market-recommendations", shipmentsWithLocation.map((s) => s.id).join(",")],
    queryFn: async () => {
      const results: Record<string, MarketRecommendationOut[]> = {};
      await Promise.all(
        shipmentsWithLocation.map(async (shipment) => {
          try {
            const recommendations = await recommendMarketRequest(buildMarketRequest(shipment));
            results[shipment.id] = recommendations;
          } catch {
            results[shipment.id] = [];
          }
        })
      );
      return results;
    },
    enabled: shipmentsWithLocation.length > 0,
    staleTime: 5 * 60 * 1000,
  });
}