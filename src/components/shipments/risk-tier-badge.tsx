import { Badge } from "@/components/ui/badge";
import type { RiskTier } from "@/types/ml.types";

export type { RiskTier };

const RISK_TIER_CONFIG: Record<RiskTier, { label: string; variant: "default" | "secondary" | "warning" | "destructive" }> = {
  Fresh: { label: "Fresh", variant: "default" },
  "At-Risk": { label: "At-Risk", variant: "warning" },
  Critical: { label: "Critical", variant: "destructive" },
};

export function RiskTierBadge({ tier, showProbability, probability }: { tier: RiskTier; showProbability?: boolean; probability?: number }) {
  const config = RISK_TIER_CONFIG[tier];
  return (
    <Badge variant={config.variant} className="capitalize">
      {config.label}
      {showProbability && probability !== undefined && (
        <span className="ml-1 text-xs opacity-80">({(probability * 100).toFixed(0)}%)</span>
      )}
    </Badge>
  );
}

export function getRiskTierFromProbability(probability: number): RiskTier {
  if (probability < 0.33) return "Fresh";
  if (probability < 0.66) return "At-Risk";
  return "Critical";
}