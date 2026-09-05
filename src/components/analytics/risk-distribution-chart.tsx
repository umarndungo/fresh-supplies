"use client";

import { useMemo } from "react";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Shipment } from "@/types/shipment.types";
import { getRiskTierFromProbability } from "@/components/shipments/risk-tier-badge";

interface RiskDistributionDataPoint {
  tier: "Fresh" | "At-Risk" | "Critical";
  count: number;
  percentage: number;
}

const TIER_COLORS: Record<string, string> = {
  Fresh: "hsl(var(--success))",
  "At-Risk": "hsl(var(--warning))",
  Critical: "hsl(var(--destructive))",
};

const TIER_LABELS: Record<string, string> = {
  Fresh: "Fresh (<33%)",
  "At-Risk": "At-Risk (33-66%)",
  Critical: "Critical (>66%)",
};

function processRiskDistributionData(shipments: Shipment[]): RiskDistributionDataPoint[] {
  const tierCounts: Record<string, number> = {
    Fresh: 0,
    "At-Risk": 0,
    Critical: 0,
  };

  let totalWithPrediction = 0;

  shipments.forEach((shipment) => {
    let tier: "Fresh" | "At-Risk" | "Critical" | null = null;

    if (shipment.riskTier) {
      tier = shipment.riskTier;
    } else if (shipment.spoilageProbability !== undefined) {
      tier = getRiskTierFromProbability(shipment.spoilageProbability);
    }

    if (tier && (tier === "Fresh" || tier === "At-Risk" || tier === "Critical")) {
      tierCounts[tier] = (tierCounts[tier] ?? 0) + 1;
      totalWithPrediction += 1;
    }
  });

  return (["Fresh", "At-Risk", "Critical"] as const).map((tier) => ({
    tier,
    count: tierCounts[tier] ?? 0,
    percentage: totalWithPrediction > 0 ? ((tierCounts[tier] ?? 0) / totalWithPrediction) * 100 : 0,
  }));
}

export function RiskDistributionChart({ shipments }: { shipments: Shipment[] }) {
  const data = useMemo(() => processRiskDistributionData(shipments), [shipments]);
  const totalWithPrediction = data.reduce((sum: number, d) => sum + (d.count ?? 0), 0);

  if (totalWithPrediction === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Risk Tier Distribution</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64 flex items-center justify-center text-muted-foreground">
            No spoilage prediction data available
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Risk Tier Distribution</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-64 flex flex-col">
          <div className="flex-1">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={2}
                  dataKey="count"
                  nameKey="tier"
                  label={({ name, percent }) => {
                    const tierName = String(name);
                    const p = percent ?? 0;
                    return `${TIER_LABELS[tierName]} ${(p * 100).toFixed(1)}%`;
                  }}
                  labelLine={false}
                >
                  {data.map((entry, index: number) => (
                    <Cell key={`cell-${index}`} fill={TIER_COLORS[entry.tier]} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value, name) => {
                    const val = (value as number) ?? 0;
                    const tierName = String(name);
                    return [val.toString(), `${TIER_LABELS[tierName]}: ${val} shipments`];
                  }}
                />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex justify-center gap-6 mt-4 text-sm">
            {data.map((entry) => (
              <div key={entry.tier} className="flex items-center gap-1.5">
                <span
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: TIER_COLORS[entry.tier] }}
                />
                <span>{TIER_LABELS[entry.tier]}: {entry.count}</span>
              </div>
            ))}
          </div>
        </div>
        <p className="text-xs text-muted-foreground mt-2">
          {totalWithPrediction} of {shipments.length} shipments have predictions. Threshold: {">15% = spoiled"}.
        </p>
      </CardContent>
    </Card>
  );
}