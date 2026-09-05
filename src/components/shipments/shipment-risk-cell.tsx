"use client";

import { useEffect, useState } from "react";
import { Skeleton } from "@/components/ui/skeleton";
import { RiskTierBadge, type RiskTier, getRiskTierFromProbability } from "@/components/shipments/risk-tier-badge";
import { usePredictSpoilage } from "@/hooks/use-ml";
import type { Shipment } from "@/types/shipment.types";

interface ShipmentRiskCellProps {
  shipment: Shipment;
}

function buildSpoilageRequest(shipment: Shipment) {
  return {
    crop_type: shipment.produceType,
    latitude: shipment.latitude ?? -1.2921,
    longitude: shipment.longitude ?? 36.8219,
    Temperature_C: shipment.temperatureC ?? 25,
    Transit_Duration_Hr: shipment.transitDurationHr ?? 4,
    Pressure_PSI: shipment.pressurePsi ?? 30,
    baseline_loss_pct: shipment.baselineLossPct ?? 10,
    quantity_kg: shipment.quantityKg ?? 100,
  };
}

export function ShipmentRiskCell({ shipment }: ShipmentRiskCellProps) {
  const [riskTier, setRiskTier] = useState<RiskTier | null>(shipment.riskTier ?? null);
  const [probability, setProbability] = useState<number | null>(shipment.spoilageProbability ?? null);
  const [isLoading, setIsLoading] = useState(!shipment.riskTier && !shipment.spoilageProbability);
  const [error, setError] = useState(false);

  const predictSpoilage = usePredictSpoilage();

  useEffect(() => {
    if (shipment.riskTier !== undefined && shipment.spoilageProbability !== undefined) {
      setRiskTier(shipment.riskTier);
      setProbability(shipment.spoilageProbability);
      setIsLoading(false);
      return;
    }

    if (!shipment.latitude && !shipment.longitude) {
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(false);

    predictSpoilage.mutate(buildSpoilageRequest(shipment), {
      onSuccess: (result) => {
        setRiskTier(result.risk_tier);
        setProbability(result.spoilage_probability);
        setIsLoading(false);
      },
      onError: () => {
        setError(true);
        setIsLoading(false);
      },
    });
  }, [shipment.id, shipment.latitude, shipment.longitude, predictSpoilage]);

  if (isLoading) {
    return <Skeleton className="h-5 w-20" />;
  }

  if (error || riskTier === null) {
    return <span className="text-muted-foreground text-sm">—</span>;
  }

  return <RiskTierBadge tier={riskTier} showProbability probability={probability ?? undefined} />;
}